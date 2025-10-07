import os

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

from dotenv import load_dotenv

load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_PORT=587,
    MAIL_SERVER=os.getenv("MAIL_HOST"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    MAIL_FROM=os.getenv("MAIL_SENDER")
)

async def send_verification_email(email: str, link: str):
    message = MessageSchema(
        subject="Подтверждение регистрации",
        recipients=[email],
        body=f"Перейдите по ссылке, чтобы подтвердить: {link}",
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message)
