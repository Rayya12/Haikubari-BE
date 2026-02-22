from fastapi import APIRouter,Depends,HTTPException,status,Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.model.user import User
from app.database.db import get_async_session
from app.users import current_verified_user, current_active_user
from sqlalchemy import select
from app.schema.UserSchema import UserUpdate,ChangeStatus
from app.service.gmail_sender import send_status_change_announcement



router = APIRouter(prefix="/users",tags=["users"])


@router.get("/me")
async def getMe(session:AsyncSession = Depends(get_async_session),user = Depends(current_active_user)):
    
    response =  await session.execute(select(User).where(user.id == User.id))
    selected_user = response.scalars().one()
    
    if (not selected_user):
        raise HTTPException(status_code=404,detail="ユーザーが見つかりません")
    
    return {
        "username" : selected_user.username,
        "email": selected_user.email,
        "photo_url" : selected_user.photo_url,
        "file_name" : selected_user.file_name,
        "file_type" : selected_user.file_type,
        "bio": selected_user.bio,
        "age": selected_user.age,
        "address" : selected_user.address,
        "is_verified":selected_user.is_verified,
        "role" : selected_user.role,
        "status" : selected_user.status
    }
    
@router.patch("/me")
async def patchme(userUpdate:UserUpdate,session:AsyncSession = Depends(get_async_session),user= Depends(current_verified_user)):
    response = await session.execute(select(User).where(user.id == User.id))
    selected_user = response.scalars().one()
    
    if (not selected_user):
        raise HTTPException(status_code=404,detail="ユーザーが見つかりません")
    
    if userUpdate.username:
        selected_user.username = userUpdate.username
    
    if userUpdate.photo_url:
        selected_user.photo_url = userUpdate.photo_url
        
    if userUpdate.file_name:
        selected_user.file_name = userUpdate.file_name
    
    if userUpdate.file_type:    
        selected_user.file_type = userUpdate.file_type
        
    if userUpdate.bio:    
        selected_user.bio = userUpdate.bio
    
    if userUpdate.age:    
        selected_user.age = userUpdate.age
    
    if userUpdate.address:
        selected_user.address = userUpdate.address
        
    await session.commit()
    await session.refresh(selected_user)
    
    return selected_user

@router.get("/watchers")
async def getWatchers(q: str = Query(None,description="ユーサネームで探す"),session:AsyncSession = Depends(get_async_session),user = Depends(current_verified_user)):
    if (user.role != "admin"):
        raise HTTPException(status.HTTP_403_FORBIDDEN,detail="アドミンしかこの機能を使えません")
    
    
    
    conditions = [User.role == "watcher"]
    
    if q:
        conditions.append(User.username.ilike(f"%{q}%"))
    
    response = await session.execute(select(User).where(*conditions))
    watchers = response.scalars().all()
    
    return {
        "wachers" : watchers
    }
    
@router.patch("/watchers/changeStatus")
async def changeRoleWatcher(changeStatus:ChangeStatus,session: AsyncSession = Depends(get_async_session),user = Depends(current_verified_user)):
    if (user.role != "admin"):
        raise HTTPException(status.HTTP_403_FORBIDDEN,detail="アドミンしかこの機能を使えません")
    
    selected_watcher = await session.scalar(select(User).where(User.id == changeStatus.id,User.role == "watcher"))
    
    if (not selected_watcher):
        raise HTTPException(status.HTTP_404_NOT_FOUND,detail="ユーザーはいません")
    
    selected_watcher.status = changeStatus.status
    
    await session.commit()
    await session.refresh(selected_watcher)
    
    send_status_change_announcement(to_email=changeStatus.email, status=selected_watcher.status)
    
    return {
        "ok": True
    }
    
    
    
    
    
    