from fastapi import APIRouter, Depends,HTTPException,Query
from app.users import current_verified_user
from app.schema.ReviewSchema import createReview
from sqlalchemy.ext.asyncio import AsyncSession
from app.model.db import get_async_session,Review
from sqlalchemy import select


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
    
@router.get("/{id}")
async def getReviewbyId(id:str,user = Depends(current_verified_user),session:AsyncSession=Depends(get_async_session),sort:str = Query("created_at",regex="^(created_at|likes)$")):
    if not (user.role == "common"):
        raise HTTPException(status_code=403,detail="普通しか使いません")
    
    result = await session.execute(select(Review).where(Review.haiku_id == id))
    data = result.scalars().all()
    
    return {
        "reviews" : data
    }





    
    
    
    
    
    
