import logging
import logging.handlers
import os
from datetime import datetime

from openai import OpenAI
from config import (
    MAIL_USER,
    MAIL_APP_PASSWORD,
    MAIL_FROM,
    MAIL_TO,
    LOG_DIR
)

# Настройка логирования
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Получаем текущую дату в формате YYYY-MM-DD
current_date = datetime.now().strftime("%Y-%m-%d")

logging.basicConfig(
    filename=os.path.join(LOG_DIR, f"chatgpt_bot_{current_date}.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
)

# Настройка обработчика для отправки критических сообщений по электронной почте
mail_handler = logging.handlers.SMTPHandler(
    mailhost=("smtp.gmail.com", 587),
    fromaddr=MAIL_FROM,
    toaddrs=[MAIL_TO],
    subject="Критическое сообщение журнала",
    credentials=(MAIL_USER, MAIL_APP_PASSWORD),
    secure=(),
)
mail_handler.setLevel(logging.CRITICAL)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
mail_handler.setFormatter(formatter)

# Добавление обработчика к логгеру
logging.getLogger().addHandler(mail_handler)