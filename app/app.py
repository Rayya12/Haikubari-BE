from fastapi import FastAPI
from app.controller.authController import router as auth_router
from app.model.db import get_async_session
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from app.model.db import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def read_root():
    return {"Hello": "World"}


app.include_router(auth_router)




