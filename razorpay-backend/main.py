import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
from agent_engine import get_agent_response

app = FastAPI(title="Razorpay Storefront API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Message]] = []

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    history = [{"role": msg.role, "content": msg.content} for msg in request.history]
    response_text = get_agent_response(request.message, history)
    return {"reply": response_text}

frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "razorpay-frontend", "dist"))
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
