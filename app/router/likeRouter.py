from fastapi import APIRouter,Depends,HTTPException
from app.model.db import get_async_session,Like
from sqlalchemy.ext.asyncio import AsyncSession
from app.users import current_verified_user
from sqlalchemy import select


router = APIRouter(prefix="/likes",tags=["likes"])

@router.get("/{id}")
async def isLikesFromUserForId(id: str,session:AsyncSession=Depends(get_async_session),user=Depends(current_verified_user)):
    
    if not (user.role == "common"):
        raise HTTPException(status_code=403,detail="まだログインしていない？")
    
    result = await session.execute(select(Like).where(Like.user_id == user.id, Like.haiku_id == id))
    isExist = result.scalar_one_or_none()
    
    if isExist:
        return {
            "ok" :True
        }
    else:
        raise HTTPException(status_code=404,detail="いいねデータが見つかりません")
    