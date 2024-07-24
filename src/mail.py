import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime

from config import (
    MAIL_USER,
    MAIL_APP_PASSWORD,
    MAIL_FROM,
    MAIL_TO,
)


def send_email(
    subject,
    body,
    to_email,
    from_email,
    smtp_server,
    smtp_port,
    smtp_user,
    smtp_password,
    attachment_path=None,
):
    # Создание сообщения
    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject

    # Добавление тела письма
    msg.attach(MIMEText(body, "plain"))

    # Добавление вложения
    if attachment_path:
        attachment = open(attachment_path, "rb")
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={os.path.basename(attachment_path)}",
        )
        msg.attach(part)

    # Настройка сервера
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_user, smtp_password)

    # Отправка письма
    text = msg.as_string()
    server.sendmail(from_email, to_email, text)
    server.quit()


if __name__ == "__main__":
    # Настройки
    TO_EMAIL = MAIL_TO
    FROM_EMAIL = MAIL_FROM
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SMTP_USER = MAIL_USER
    SMTP_PASSWORD = MAIL_APP_PASSWORD
    ATTACHMENT_PATH = "logs/chatgpt_bot_2024-07-21.log"
    SUBJECT = f"Ежедневный отчет за {datetime.now().strftime('%Y-%m-%d')}"
    BODY = "Добрый день,\n\nПожалуйста, найдите приложенный ежедневный отчет.\n\nС уважением,\nВаша команда"

    send_email(
        SUBJECT,
        BODY,
        TO_EMAIL,
        FROM_EMAIL,
        SMTP_SERVER,
        SMTP_PORT,
        SMTP_USER,
        SMTP_PASSWORD,
        ATTACHMENT_PATH,
    )
