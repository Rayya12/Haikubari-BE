from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,delete

from app.database.db import get_async_session
from app.model.user import User
from app.service.otp_service import generate_otp, create_otp_for_user, verify_otp_for_user
from app.service.gmail_sender import send_otp_email

from app.users import fastapi_users  # file users.py kamu
current_user = fastapi_users.current_user(active=True)

router = APIRouter(prefix="/auth/otp", tags=["auth"])

class OTPRequestBody(BaseModel):
    email: EmailStr
    

class OTPVerifyBody(BaseModel):
    code: str
    
class OTPRetryBody(BaseModel):
    email: EmailStr
    username:str

@router.post("/request")
async def request_otp(body: OTPRequestBody, session: AsyncSession = Depends(get_async_session)):
    # cari user by email
    user = (await session.execute(select(User).where(User.email == body.email))).scalars().first()

    # anti user-enumeration: selalu balikin ok
    if not user:
        return {"ok": True}

    otp = generate_otp()
    await create_otp_for_user(session,user.id, otp)

    try:
        send_otp_email(user.email, otp)
    except Exception:
        # jangan bocorin detail error ke client
        pass

    return {"ok": True}

@router.post("/verify")
async def verify_otp(
    body: OTPVerifyBody,
    user=Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    ok = await verify_otp_for_user(session, user.id, body.code)
    if not ok:
        raise HTTPException(status_code=400, detail="OTP salah atau sudah kedaluwarsa")

    # tandain verified
    user.is_verified = True
    session.add(user)
    await session.commit()

    return {"ok": True, "is_verified": True}

@router.delete("/check")
async def check(body : OTPRetryBody,session:AsyncSession = Depends(get_async_session)):
    result1 = await session.execute(select(User).where(User.email == body.email))
    
    user1 = result1.scalar_one_or_none()
   
    if not user1:
        raise HTTPException(status_code=404,detail="User not Found")

    if user1.is_verified == True:
        raise HTTPException(status_code=400,detail="Bad Request")
    
    await session.delete(user1)
    await session.commit()
        
    return {"ok":True}

    
   
    
    
