from fastapi import APIRouter
from pydantic import EmailStr
import traceback

from app.service.gmail_sender import send_otp_email

router = APIRouter(prefix="/health", tags=["health"])

@router.post("/gmail")
def health_gmail(to: EmailStr):
    """
    Health check Gmail API by sending test email.
    Requires only gmail.send scope.
    """
    try:
        send_otp_email(to, "123456")
        return {
            "ok": True,
            "message": f"Test email sent to {to}"
        }
    except Exception as e:
        traceback.print_exc()
        return {
            "ok": False,
            "error": repr(e)
        }
