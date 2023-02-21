import logging
import re
import redis as r
import telegram
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from functools import partial
import os
import dotenv
from logger import ChatbotLogsHandler

from quiz_base import send_question, read_data


logger = logging.getLogger(__file__)
QUESTION, ANSWER = range(2)


def start(update: Update, context: CallbackContext) -> None:
    score = 0
    context.user_data['score'] = score

    keyboard = [['Новый вопрос', 'Сдаться'],
                ['Мой счет']]

    reply_markup = telegram.ReplyKeyboardMarkup(keyboard=keyboard)
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Привет, я бот для викторины\!',
        reply_markup=reply_markup,
    )

    return QUESTION
    

def new_question(update: Update, context: CallbackContext, data, redis) -> None:
    question = send_question(data)
    redis.set(update.message.from_user['id'], question)
    update.message.reply_text(question)

    return ANSWER


def check_answer(update: Update, context: CallbackContext, data, redis) -> None:
    question = redis.get(update.message.from_user['id']).decode('utf-8', 'ignore')

    answer_long = ''.join([letter for letter in data[question] if letter != '[' and letter != ']'])
    answer_short = re.sub("[\(\[].*?[\)\]]", "", data[question])

    if answer_long.lower() == update.message.text.lower() or answer_short.lower() == update.message.text.lower():

        context.user_data['score'] += 1
        update.message.reply_text('Правильно, жми Новый вопрос для нового вопроса')
        return QUESTION
    else:
        update.message.reply_text('Неправильно, дружок')
        return ANSWER


def concede(update: Update, context: CallbackContext, data, redis) -> None:

    question = redis.get(update.message.from_user['id']).decode('utf-8', 'ignore')
    answer = ''.join([letter for letter in data[question] if letter != '[' and letter != ']'])
    update.message.reply_text(answer)

    question = send_question(data)
    redis.set(update.message.from_user['id'], question)
    update.message.reply_text(question)                                          

    return ANSWER


def show_score(update: Update, context: CallbackContext) -> None:
    score = context.user_data['score']
    update.message.reply_text(score)


def cancel(update: Update, context: CallbackContext,):
    update.message.reply_text('Ну покедова штоли', reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def main() -> None:
    dotenv.load_dotenv()

    telegram_chat_id = os.environ['TELEGRAM_CHAT_ID']
    telegram_token = os.environ['TELEGRAM_TOKEN']
    redis_host = os.environ['REDIS_HOST']
    redis_port = int(os.environ['REDIS_PORT'])
    redis_password = os.environ['REDIS_PASSWORD']

    logging.basicConfig(level=logging.WARNING)
    logger.addHandler(ChatbotLogsHandler(telegram_chat_id, telegram_token))

    redis = r.Redis(host=redis_host, port=redis_port, password=redis_password)

    data = read_data()
    new_question_data = partial(new_question, data=data, redis=redis)
    check_answer_data = partial(check_answer, data=data, redis=redis)
    concede_data = partial(concede, data=data, redis=redis)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            QUESTION: [MessageHandler(Filters.regex('Новый вопрос'), new_question_data),
                       MessageHandler(Filters.regex('Мой счет'), show_score)],
            ANSWER: [MessageHandler(Filters.regex('Сдаться'), concede_data),
                     MessageHandler(Filters.regex('Мой счет'), show_score),
                     MessageHandler(Filters.text & ~Filters.command, check_answer_data),
                     ],
            
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    updater = Updater(telegram_token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
