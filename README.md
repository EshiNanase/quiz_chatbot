# History Quiz Bot

Bots for testing knowledge of history events

Examples:
Telegram: https://t.me/quizer_1337_bot
VKontakte: https://vk.com/public218965946

## Prerequisites

Virtual environment needs to be:

```
python==3.10
```
## Installing

First, you need to clone the code:

```
git clone https://github.com/EshiNanase/quiz_chatbot
```
Second, you need to install requirements.txt:

```
pip install -r requirements.txt
```
Third, you need to create redis database following these instructions:
```
https://app.redislabs.com/
```
## Environment variables

The code needs .env file with such environment variables as:

```
TELEGRAM_TOKEN = token of your Telegram bot, text https://t.me/BotFather to create one
TELEGRAM_CHAT_ID = needed for logger you can find it here https://t.me/userinfobot
VK_TOKEN = token of your VK group, follow these instructions to create https://habr.com/ru/company/vk/blog/570486/
REDIS_HOST = host of you redis db, you'll get it once you create redis db
REDIS_PORT = port of you redis db, you'll get it once you create redis db
REDIS_PASSWORD = password of you redis db, you need to create redis db and remember the password
PATH_TXT = path for your questions file, should be in txt with architecture like this: question---answer\n
```
## Running

The code should be ran in cmd like so:

```
python telegram_bot.py & python vk_bot.py
```