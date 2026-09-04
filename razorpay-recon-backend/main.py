from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import uuid
import asyncio
import io
from contextlib import asynccontextmanager

from models import init_db, UploadResponse, Batch, AsyncSessionLocal
from engine import ReconciliationEngine
from pydantic import BaseModel
from typing import List, Dict, Any
from agent_engine import get_agent_response
from catalog import CATALOG


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass # Handle disconnected clients gracefully

manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="Razorpay Reconciliation Engine", lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Restrict to your Vercel/Netlify URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


batch_store = {} 


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:

            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.post("/upload", response_model=UploadResponse)
async def upload_dataset(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")
    
    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))
    
    
    required_cols = {'date', 'amount', 'description'}
    if not required_cols.issubset(df.columns):
        raise HTTPException(status_code=400, detail=f"CSV must contain columns: {required_cols}")
    
    df['date'] = pd.to_datetime(df['date'])
    
    batch_id = str(uuid.uuid4())
    batch_store[batch_id] = df
    
    return UploadResponse(
        batch_id=batch_id,
        message="Dataset uploaded successfully.",
        record_count=len(df)
    )

async def run_reconciliation(batch_id: str, internal_df: pd.DataFrame, bank_df: pd.DataFrame):
    """Background task to run the engine and stream updates."""
    engine = ReconciliationEngine(internal_df, bank_df)
    
    async def send_progress(message: str):
        await manager.broadcast({
            "type": "progress",
            "batch_id": batch_id,
            "message": message
        })

    results = await engine.process(send_progress)
    
    
    matched = sum(1 for r in results if r['status'] == 'MATCHED')
    exceptions = sum(1 for r in results if r['status'] == 'EXCEPTION')
    match_rate = (matched / len(results)) * 100 if results else 0

    
    await manager.broadcast({
        "type": "complete",
        "batch_id": batch_id,
        "metrics": {
            "total_records": len(results),
            "matched": matched,
            "exceptions": exceptions,
            "match_rate": round(match_rate, 2)
        },
        "results": results
    })

@app.post("/process/{batch_id}")
async def process_reconciliation(batch_id: str, background_tasks: BackgroundTasks):
    if batch_id not in batch_store:
        raise HTTPException(status_code=404, detail="Batch ID not found.")
    
    df = batch_store[batch_id]
    
    
    internal_df = df.iloc[:len(df)//2].copy().reset_index(drop=True)
    bank_df = df.iloc[len(df)//2:].copy().reset_index(drop=True)
    
    
    bank_df.loc[::3, 'description'] = bank_df.loc[::3, 'description'].apply(lambda x: f"PGWY {x}" if isinstance(x, str) else x)
    
    
    background_tasks.add_task(run_reconciliation, batch_id, internal_df, bank_df)
    
    return {"message": "Processing started. Listen to WebSocket for updates."}

@app.get("/results/{batch_id}")
async def get_results(batch_id: str):
    
    return {"message": "Use WebSocket for real-time results, or check dashboard state."}



class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    
    history = [{"role": msg.role, "content": msg.content} for msg in request.history]
    
    response_text = get_agent_response(request.message, history)
    
    return {"reply": response_text}

@app.get("/catalog/ai-readable")
async def ai_readable_catalog():
    """Endpoint for AI buyers to scrape the catalog in a structured format."""
    return {
        "store_name": "Razorpay Hacker Store",
        "currency": "INR",
        "description": "Welcome to our store. We sell developer merchandise.",
        "products": CATALOG
    }


import os
from fastapi.staticfiles import StaticFiles

frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "razorpay-recon-frontend", "dist"))

if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")