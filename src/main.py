import logging
import logging.handlers
import time
from datetime import datetime
import telebot
from telebot import types

import logger
from openai import OpenAI
from config import (
    API_TOKEN,
    API_KEY_PROXY,
)


client = OpenAI(
    api_key=API_KEY_PROXY,
)

bot = telebot.TeleBot(API_TOKEN)

# Словарь для хранения истории переписки для каждого пользователя
user_conversations = {}
# Словарь для хранения выбранной модели для каждого пользователя
user_models = {}


# Функция разбивает сообщение на части с максимальной длиной max_length для отправки в Telegram
def split_message(message, max_length):
    return [message[i : i + max_length] for i in range(0, len(message), max_length)]


# Функция для создания клавиатуры выбора модели
def create_model_keyboard():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
    btn_gpt3 = types.KeyboardButton("gpt-3.5-turbo-1106")
    btn_gpt4o = types.KeyboardButton("gpt-4o")
    btn_gpt4m = types.KeyboardButton("gpt-4o-mini")
    markup.row(btn_gpt3, btn_gpt4o, btn_gpt4m)
    return markup


# Функция для получения ответа от модели GPT
def get_gpt_response(user_id, user_input):
    if user_id not in user_conversations:
        user_conversations[user_id] = []

    conversation_history = user_conversations[user_id]
    conversation_history.append({"role": "system", "content": user_input})

    try:
        model = user_models.get(
            user_id, "gpt-3.5-turbo-1106"
        )  # По умолчанию используем gpt-3.5-turbo-1106
        response = client.chat.completions.create(
            model=model, messages=conversation_history
        )
        answer = response.choices[0].message.content
        # conversation_history.append({"role": "system", "content": ""})
        logging.info(f"Ответ для пользователя {user_id}, модель {model}: {answer}")
        return answer
    except Exception as e:
        logging.error(
            f"Ошибка при получении ответа от модели {model} для пользователя {user_id}: {str(e)}"
        )
        return f"Произошла ошибка при обращении к модели {model}. Пожалуйста, попробуйте позже."


# Обработчик стартового сообщения
@bot.message_handler(commands=["start"])
def handle_start(message):
    user_id = message.from_user.id
    bot.send_message(
        user_id,
        "Привет! Выберите модель, которую хотите использовать:",
        reply_markup=create_model_keyboard(),
    )


# Обработчик выбора модели
@bot.message_handler(
    func=lambda message: message.text in ["gpt-3.5-turbo-1106", "gpt-4o", "gpt-4o-mini"]
)
def handle_model_selection(message):
    user_id = message.from_user.id
    user_models[user_id] = message.text
    bot.send_message(
        user_id,
        f"Вы выбрали модель {message.text}. Теперь вы можете начать задавать вопросы.",
    )


# Обработчик остальных сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    user_input = message.text
    logging.info(f"Получено сообщение от пользователя {user_id}: {user_input}")

    if user_input.lower() == "exit":
        bot.reply_to(message, "Завершение чата. До свидания!")
        if user_id in user_conversations:
            del user_conversations[user_id]
        logging.info(f"Чат с пользователем {user_id} завершен")
        return

    if user_input.lower() == "сменить модель":
        bot.send_message(
            user_id,
            "Пожалуйста, выберите новую модель:",
            reply_markup=create_model_keyboard(),
        )
        return

    response = get_gpt_response(user_id, user_input)
    for part in split_message(response, 4096):
        bot.reply_to(message, part)


if __name__ == "__main__":
    logging.info("ChatGPT Bot запущен...")
    print("ChatGPT Bot запущен...")
    while True:
        try:
            bot.polling()
        except Exception as e:
            logging.critical(f"Критическая ошибка в работе бота: {str(e)}")
            time.sleep(5)
