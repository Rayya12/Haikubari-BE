from imagekitio import ImageKit
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.users import current_verified_user
from app.model.db import get_async_session
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter(prefix="/imagekit",tags=["imagekit"])

@router.get("/auth")
async def imagekit_auth(session:AsyncSession = Depends(get_async_session),user=Depends(current_verified_user)):
    imagekit = ImageKit(
        private_key= os.getenv("IMAGE_KIT_PRIVATE_KEY"),
        public_key = os.getenv("IMAGE_KIT_PUBLIC_KEY"),
        url_endpoint = os.getenv("IMAGE_KIT_URL_ENDPOINT")
    )
    
    auth = imagekit.get_authentication_parameters()
    
    return {
        **auth,
        "folder" : f"/{user.id}"
    }
    