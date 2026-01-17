from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text,select
from app.model.db import get_async_session
from app.schema.registerform import RegisterForm
from app.model.db import User

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register_user(form: RegisterForm, session: AsyncSession = Depends(get_async_session)):
    
    form_data = form.model_dump()
    username = form_data.get("username")
    
    
    
    email = form_data.get("email")
    password = form_data.get("password")
    role = form_data.get("role")
    photo_url = form_data.get("photo_url")
    file_name = form_data.get("file_name")
    file_type = form_data.get("file_type")
    bio = form_data.get("bio")
    age = form_data.get("age")
    address = form_data.get("address")
    
    
    
    
    
    # You can access form_data['username'], form_data['email'], etc.
    