from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker


class UploadResponse(BaseModel):
    batch_id: str
    message: str
    record_count: int

class MatchResult(BaseModel):
    internal_id: str
    bank_id: str
    confidence_score: float
    status: str  
    reasons: List[str]


Base = declarative_base()

class Batch(Base):
    __tablename__ = "batches"
    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    total_records = Column(Integer)
    status = Column(String, default="PENDING") 

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(String, index=True)
    source = Column(String) 
    txn_date = Column(DateTime)
    amount = Column(Float)
    description = Column(String)
    reference_id = Column(String)
    matched = Column(Boolean, default=False)
    match_details = Column(JSON, nullable=True) 


DATABASE_URL = "sqlite+aiosqlite:///./reconciliation.db"
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)