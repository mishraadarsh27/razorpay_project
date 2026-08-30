from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import uuid
import asyncio
import io
from contextlib import asynccontextmanager

from models import init_db, UploadResponse, Batch, AsyncSessionLocal
from engine import ReconciliationEngine

# --- WebSocket Connection Manager ---
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

# --- FastAPI App ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="Razorpay Reconciliation Engine", lifespan=lifespan)

# Allow frontend (React) to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Restrict to your Vercel/Netlify URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for DataFrames (Use Redis/S3 in production)
batch_store = {} 

# --- WebSocket Endpoint ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, listen for pings or commands from frontend
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# --- API Endpoints ---
@app.post("/upload", response_model=UploadResponse)
async def upload_dataset(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")
    
    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))
    
    # Basic validation
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
    
    # Calculate final metrics
    matched = sum(1 for r in results if r['status'] == 'MATCHED')
    exceptions = sum(1 for r in results if r['status'] == 'EXCEPTION')
    match_rate = (matched / len(results)) * 100 if results else 0

    # Broadcast final results
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
    
    # For this demo, we split the uploaded CSV into two mock datasets 
    # (Internal Ledger and Bank Statement) with slight variations to simulate real data.
    # In production, you would upload TWO files or fetch from DBs.
    internal_df = df.iloc[:len(df)//2].copy().reset_index(drop=True)
    bank_df = df.iloc[len(df)//2:].copy().reset_index(drop=True)
    
    # Introduce slight noise to bank_df to test fuzzy matching
    bank_df.loc[::3, 'description'] = bank_df.loc[::3, 'description'].apply(lambda x: f"PGWY {x}" if isinstance(x, str) else x)
    
    # Run in background so the API responds immediately
    background_tasks.add_task(run_reconciliation, batch_id, internal_df, bank_df)
    
    return {"message": "Processing started. Listen to WebSocket for updates."}

@app.get("/results/{batch_id}")
async def get_results(batch_id: str):
    # Fallback endpoint if WebSocket drops, frontend can poll this
    return {"message": "Use WebSocket for real-time results, or check dashboard state."}