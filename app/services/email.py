import logging
from pathlib import Path

from fastapi import BackgroundTasks
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from app.core.settings import settings

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / settings.email.templates_dir

class EmailService:
    def __init__(self, background_tasks: BackgroundTasks):
        self._background_tasks = background_tasks

        self._conf = ConnectionConfig(
            MAIL_USERNAME=settings.email.username,
            MAIL_PASSWORD=settings.email.password,
            MAIL_FROM=settings.email.username,
            MAIL_PORT=settings.email.port,
            MAIL_SERVER=settings.email.server,
            MAIL_FROM_NAME=settings.email.title,
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            TEMPLATE_FOLDER=str(TEMPLATES_DIR),
            USE_CREDENTIALS=True,
        )
        self._fast_mail = FastMail(self._conf)

    async def send_email(
        self,
        email_to: str,
        subject: str,
        template_name: str,
        template_body: dict,
    ) -> None:
        message = MessageSchema(
            subject=subject,
            recipients=[email_to],
            template_body=template_body,
            subtype=MessageType.html,
        )

        self._background_tasks.add_task(
            self._fast_mail.send_message,
            message,
            template_name=template_name,
        )

    async def send_verification_email(
        self,
        email_to: str,
        verification_code: str,
        verification_link: str,
    ) -> None:
        await self.send_email(
            email_to=email_to,
            subject=f'Подтверждение аккаунта - {settings.email.title}',
            template_name='verify_account.html',
            template_body={
                'title': settings.email.title,
                'verification_code': verification_code,
                'verification_link': verification_link,
            },
        )

    async def send_change_password_email(
        self,
        email_to: str,
        reset_code: str,
        reset_link: str,
    ) -> None:
        await self.send_email(
            email_to=email_to,
            subject=f'Сброс пароля - {settings.email.title}',
            template_name='change_password.html',
            template_body={
                'title': settings.email.title,
                'reset_code': reset_code,
                'reset_link': reset_link,
            },
        )
