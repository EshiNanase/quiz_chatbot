from vk_api.longpoll import VkEventType, VkLongPoll
import os
import dotenv
import vk_api as vk
import logging
import time
import redis as r
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from quiz_base import read_data
import requests
import re
from logger import ChatbotLogsHandler
import random


logger = logging.getLogger(__file__)


def start(event, vk_api, keyboard, players):
    players[event.user_id] = 0
    vk_api.messages.send(
        user_id=event.user_id,
        keyboard=keyboard.get_keyboard(),
        message='Привет! Я викториновый бот, жми "Новый вопрос"',
        random_id=0,
    )
    return players


def new_question(event, vk_api, keyboard, data, redis) -> None:
    question = random.choice(list(data.keys()))
    redis.set(event.user_id, question)

    vk_api.messages.send(
        user_id=event.user_id,
        keyboard=keyboard.get_keyboard(),
        message=question,
        random_id=0,
    )


def check_answer(event, vk_api, keyboard, data, redis, players) -> None:
    question = redis.get(event.user_id).decode('utf-8', 'ignore')

    answer_long = ''.join([letter for letter in data[question] if letter != '[' and letter != ']'])
    answer_short = re.sub(r"[\(\[].*?[\)\]]", "", data[question])

    if answer_long.lower() == event.text.lower() or answer_short.lower() == event.text.lower():

        players[event.user_id] += 1

        vk_api.messages.send(
            user_id=event.user_id,
            keyboard=keyboard.get_keyboard(),
            message='Красавчик! Жми "Новый вопрос" и продолжай викторину',
            random_id=0,
        )
    else:
        vk_api.messages.send(
            user_id=event.user_id,
            keyboard=keyboard.get_keyboard(),
            message='Неправильно! Думай дальше',
            random_id=0,
        )

    return players


def send_answer(event, vk_api, keyboard, data, redis) -> None:
    question = redis.get(event.user_id).decode('utf-8', 'ignore')
    answer = ''.join([letter for letter in data[question] if letter != '[' and letter != ']'])
    vk_api.messages.send(
        user_id=event.user_id,
        keyboard=keyboard.get_keyboard(),
        message=answer,
        random_id=0,
    )

    question = random.choice(list(data.keys()))
    redis.set(event.user_id, question)

    vk_api.messages.send(
        user_id=event.user_id,
        keyboard=keyboard.get_keyboard(),
        message=question,
        random_id=0,
    )


def show_score(event, vk_api, keyboard, players):
    vk_api.messages.send(
        user_id=event.user_id,
        keyboard=keyboard.get_keyboard(),
        message=str(players[event.user_id]),
        random_id=0,
    )


def main() -> None:
    dotenv.load_dotenv()

    telegram_chat_id = os.environ['TELEGRAM_CHAT_ID']
    telegram_token = os.environ['TELEGRAM_TOKEN']
    vk_token = os.environ['VK_TOKEN']
    redis_host = os.environ['REDIS_HOST']
    redis_port = int(os.environ['REDIS_PORT'])
    redis_password = os.environ['REDIS_PASSWORD']

    logging.basicConfig(level=logging.WARNING)
    logger.addHandler(ChatbotLogsHandler(telegram_chat_id, telegram_token))

    redis = r.Redis(host=redis_host, port=redis_port, password=redis_password)

    data = read_data()

    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()

    keyboard = VkKeyboard(one_time=True)

    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Мой счет', color=VkKeyboardColor.PRIMARY)

    longpoll = VkLongPoll(vk_session)

    players = {}

    while True:
        try:
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    if event.text == 'Новый вопрос':
                        new_question(event=event, vk_api=vk_api, data=data, redis=redis, keyboard=keyboard)
                    elif event.text == 'Начать':
                        players = start(event=event, vk_api=vk_api, players=players, keyboard=keyboard)
                    elif event.text == 'Сдаться':
                        send_answer(event=event, vk_api=vk_api, data=data, redis=redis, keyboard=keyboard)
                    elif event.text == 'Мой счет':
                        show_score(event=event, vk_api=vk_api, keyboard=keyboard, players=players)
                    else:
                        players = check_answer(event=event, vk_api=vk_api, data=data, redis=redis, keyboard=keyboard, players=players)

        except requests.exceptions.ConnectionError as err:
            logger.warning('Боту прилетело:')
            logger.warning(err, exc_info=True)
            time.sleep(10)


if __name__ == '__main__':
    main()
