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
    msg["Subject"] = "俳句張りのOTPコード"
    msg.set_content(
        f"あなたのOTPは: {otp_code}\n"
        f"このOTPは {int(os.getenv('OTP_TTL_SECONDS','600'))//60}分以内で使えます.\n"
        f"もし、このOTPを申し込まない場合、無視してください."
    )

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service.users().messages().send(userId="me", body={"raw": raw}).execute()


def send_token(to_email,token:str):
    service = _gmail_service()
    
    msg = EmailMessage()
    msg["to"] = to_email
    msg["From"] = os.getenv("GMAIL_SENDER")
    msg["Subject"] = "パスワード忘れ確認"
    
    msg.set_content(
        f"俳句張りでパスワードをお忘れ場合、このOTPを入力してください：\n"
        f"{token}\n"
        f"もし、パスワードが大丈夫だとしたら、このメールを無視してください."
    )
    
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service.users().messages().send(userId="me", body={"raw": raw}).execute()