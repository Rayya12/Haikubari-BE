# app/core/dependencies.py

from fastapi import Depends, HTTPException, status
from app.model.db import User
from app.users import current_user

async def current_active_watcher(
    user: User = Depends(current_user)
):
    if user.status != "accepted":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"ユーザーのステータスはただいま{str(user.status)[12:]}です、お詳しいことはアドミンに申し込んでください"
        )
    return user

async def current_active_admin(
    user: User = Depends(current_user)
):
    if user.status != "accepted":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"ユーザーのステータスはただいま{str(user.status)[12:]}です、お詳しいことはアドミンに申し込んでください"
        )
    return user
