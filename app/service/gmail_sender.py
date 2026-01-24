import os, base64
from email.message import EmailMessage
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import dotenv


dotenv.load_dotenv()

def _gmail_service():
    rt = os.getenv("GMAIL_REFRESH_TOKEN")
    cid = os.getenv("GMAIL_CLIENT_ID")
    cs = os.getenv("GMAIL_CLIENT_SECRET")

    creds = Credentials(
        token=None,
        refresh_token=rt,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=cid,
        client_secret=cs,
        scopes= ["https://www.googleapis.com/auth/gmail.send"],
    )
    return build("gmail", "v1", credentials=creds)

def send_otp_email(to_email: str, otp_code: str):
    service = _gmail_service()

    msg = EmailMessage()
    msg["To"] = to_email
    msg["From"] = os.getenv("GMAIL_SENDER")
    msg["Subject"] = "Kode OTP Haikubari"
    msg.set_content(
        f"Kode OTP kamu: {otp_code}\n"
        f"Berlaku {int(os.getenv('OTP_TTL_SECONDS','600'))//60} menit.\n"
        f"Kalau kamu tidak merasa minta OTP, abaikan email ini."
    )

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service.users().messages().send(userId="me", body={"raw": raw}).execute()
