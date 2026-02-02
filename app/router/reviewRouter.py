from fastapi import APIRouter, Depends,HTTPException
from app.users import current_verified_user
from app.schema.ReviewSchema import createReview
from sqlalchemy.ext.asyncio import AsyncSession
from app.model.db import get_async_session,Review


router = APIRouter(prefix="/reviews",tags=["reviews"])


@router.post("/create")
async def createReviewku(createReview:createReview,user = Depends(current_verified_user),session:AsyncSession=Depends(get_async_session)):
    if not (user.role == "common"):
        raise HTTPException(status_code=403,detail="普通しか使いません")
        
    new_review = Review(**createReview.model_dump(),user_id=user.id)
    
    session.add(new_review)
    await session.commit()
    await session.refresh(new_review)
    return {
        "ok":True,
        "review":new_review
}
    
    
