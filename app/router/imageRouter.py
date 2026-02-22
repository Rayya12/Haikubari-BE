from imagekitio import ImageKit
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.users import current_verified_user
from app.database.db import get_async_session
import os
from app.core.settings import settings

router = APIRouter(prefix="/imagekit",tags=["imagekit"])

@router.get("/auth")
async def imagekit_auth(session:AsyncSession = Depends(get_async_session),user=Depends(current_verified_user)):
    imagekit = ImageKit(
        private_key= settings.IMAGEKIT_PRIVAT_KEY
    )
    
    auth = imagekit.helper.get_authentication_parameters()
    
    return {
        **auth,
        "folder" : f"/{user.id}"
    }
    