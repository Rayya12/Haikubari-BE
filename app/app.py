from fastapi import FastAPI
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.model.db import get_async_session

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}



@app.get("/health/db")
async def health_db(session: AsyncSession = Depends(get_async_session)):
    value = (await session.execute(text("SELECT 1"))).scalar()
    return {"db": "ok", "select_1": value}
