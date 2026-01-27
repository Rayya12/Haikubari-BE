from fastapi import APIRouter, Depends, HTTPException
from app.users import current_verified_user
from app.schema.haikuSchema import HaikuPost
from app.model.db import Haiku, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession



router = APIRouter(prefix="/haiku", tags=["haiku"])

@router.post("/create")
async def createHaiku(haiku:HaikuPost,user=Depends(current_verified_user),session: AsyncSession = Depends(get_async_session)):
    new_haiku = Haiku(**haiku.model_dump(), user_id=user.id)
    session.add(new_haiku)
    await session.commit()
    await session.refresh(new_haiku)
    return {
        "ok":True,
        "haiku":new_haiku
    }