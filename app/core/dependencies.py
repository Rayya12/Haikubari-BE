# app/core/dependencies.py

from fastapi import Depends, HTTPException, status
from app.model.db import User
from app.users import current_user

async def current_active_watcher(
    user: User = Depends(current_user)
):
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"ユーザーのステータスはただいま{user.status}です、お詳しいことはアドミンに申し込んでください"
        )
    return user
