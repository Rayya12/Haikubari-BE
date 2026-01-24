import os, secrets, hmac, hashlib
from datetime import datetime, timedelta, timezone
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.model.db import OTP
import dotenv

dotenv.load_dotenv()

OTP_TTL_SECONDS = int(os.getenv("OTP_TTL_SECONDS", "600"))
OTP_PEPPER = os.getenv("OTP_PEPPER", os.getenv("SECRET", "change-me"))  # minimal pakai SECRET

def generate_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"

def _now():
    return datetime.now(timezone.utc)

def otp_digest(user_id: str, otp_code: str) -> str:
    # ikat ke user_id biar OTP gak bisa dipakai lintas user
    msg = f"{user_id}:{otp_code}".encode()
    key = OTP_PEPPER.encode()
    return hmac.new(key, msg, hashlib.sha256).hexdigest()

async def create_otp_for_user(session: AsyncSession, user_id, otp_code: str) -> OTP:
    now = _now()

    # 1 user 1 OTP aktif
    await session.execute(delete(OTP).where(OTP.user_id == user_id))

    rec = OTP(
        user_id=user_id,
        code=otp_digest(str(user_id), otp_code),   # simpan digest, bukan OTP asli
        expired_at=now + timedelta(seconds=OTP_TTL_SECONDS),
    )
    session.add(rec)
    await session.commit()
    await session.refresh(rec)
    return rec

async def verify_otp_for_user(session: AsyncSession, user_id, otp_code: str) -> bool:
    now = _now()

    rec = (await session.execute(select(OTP).where(OTP.user_id == user_id))).scalars().first()
    if not rec:
        return False
    if rec.expired_at < now:
        return False

    expected = otp_digest(str(user_id), otp_code)
    if not hmac.compare_digest(rec.code, expected):
        return False

    # karena model belum punya used_at → delete setelah sukses
    await session.delete(rec)
    await session.commit()
    return True
