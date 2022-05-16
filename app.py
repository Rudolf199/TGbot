import subprocess
import sys
import os

subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
print("Your bot token please: ")
os.environ['bottoken'] = input()
print("Your database host: ")
os.environ['dbhost'] = input()
print("Your db password: ")
os.environ['password'] = input()
print("Your db port: ")
os.environ['port'] = input()
print("Your db user: ")
os.environ['user'] = input()
print("your database: ")
os.environ['database'] = input()
print("Your channel url: ")
os.environ['channel'] = input()


import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.markdown import hbold, hlink
from aiogram.dispatcher.filters import Text
from src.config import token, chat_id, not_sub_message
from src.config import user, port, password, database, host
import datetime
import json
from src.inlines import check_sub_menu
from src.news import check_news_update
from src.sqlighter import DataBase


bot = Bot(token=os.environ['bottoken'], parse_mode=types.ParseMode.HTML)
# bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)
# db = DataBase(host=host, password=password, port=port, user=user, database=database)
db = DataBase(host=os.environ['dbhost'], password=os.environ['password'], port=os.environ['port'],
              user=os.environ['user'], database=os.environ['database'])

def check_sub_channel(chat_member):
    """проверяем подписан ли пользовтель на канал"""
    print(chat_member['status'], "\n")
    if chat_member['status'] != 'left':
        return True
    else:
        return False


@dp.message_handler(commands="start")
async def start(message: types.Message):
    """после команды "старт" запускается бот, и включается клавиатура с кнопками"""
    start_buttons = types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(text="📰 Все новости")
            ],
            [
                types.KeyboardButton(text="⬅ Последние 5 новостей"),
                types.KeyboardButton(text="🍅🗞️Свежие новости")
            ],
            [
                types.KeyboardButton(text="✔ Подписаться"),
                types.KeyboardButton(text="❌ Отписаться")
            ],
            ],
        resize_keyboard=True)
    await message.answer("Лента новостей", reply_markup=start_buttons)


@dp.message_handler(Text(equals="✔ Подписаться"))
async def subscribe(message: types.Message):
    """проверяем подписан ли пользователь на канал, и даем право на подписку на рассылку новостей в зависимости от этого"""
    if check_sub_channel(await bot.get_chat_member(chat_id=chat_id, user_id=message.from_user.id)):
        if not db.subscriber_exists(message.from_user.id):
            """если юзера нет в базе, добавляем его"""
            db.add_subscriber(message.from_user.id)
            await message.answer("you are in my database :)")
        else:
            await message.answer("wait...")
            """если он есть, то просто обновляем ему статус"""
            db.update_subscription(message.from_user.id, True)
        await message.answer("Вы подписались на рассылку 📧")
    else:
        await bot.send_message(message.from_user.id, not_sub_message, reply_markup=check_sub_menu)


@dp.callback_query_handler(text="subchanneldone")
async def sub_channel_done(message: types.Message):
    """после подписки пользовтель нажимает на кнопку "Подписался" и убирает инлайн кнопку"""
    await bot.delete_message(message.from_user.id, message.message.message_id)
    if check_sub_channel(await bot.get_chat_member(chat_id=chat_id, user_id=message.from_user.id)):
        await message.answer("Лента новостей", reply_markup=start_buttons)
    else:
        await bot.send_message(message.from_user.id, not_sub_message, reply_markup=check_sub_menu)


@dp.message_handler(Text(equals="❌ Отписаться"))
async def unsubscribe(message: types.Message):
    """то же самое, что и у кнопки подписаться"""
    if check_sub_channel(await bot.get_chat_member(chat_id=chat_id, user_id=message.from_user.id)):
        if not db.subscriber_exists(message.from_user.id):
            """если юзера нет в базе, добавляем его с неактивной подпиской, запоминаем его"""
            db.add_subscriber(message.from_user.id, False)
            await message.answer("Вы не подписаны 🤨")
        else:
            """если он есть, то просто обновляем ему статус"""
            db.update_subscription(message.from_user.id, False)
            await message.answer("Вы отписались от рассылки👋")
    else:
        await bot.send_message(message.from_user.id, not_sub_message, reply_markup=check_sub_menu)


@dp.message_handler(Text(equals="📰 Все новости"))
async def get_all_news(message: types.Message):
    """для обычных юзеров доступна кнопка "📰 Все новости", которая отправляет все новости"""
    with open("news_dict.json", encoding='utf-8') as file:
        news_dict = json.load(file)
    for k, v in sorted(news_dict.items()):
        news = f"{hbold(datetime.datetime.fromtimestamp(v['article_date_timestamp']))}\n" \
                f"{hlink(v['article_title'], v['article_url'])}"
        await message.answer(news)


@dp.message_handler(Text(equals="⬅ Последние 5 новостей"))
async def get_last_five_news(message: types.Message):
    """для подписчиков доступна кнопка "⬅ Последние 5 новостей", которая отправляет только последние 5 новостей"""
    if check_sub_channel(await bot.get_chat_member(chat_id=chat_id, user_id=message.from_user.id)):
        with open("news_dict.json", encoding='utf-8') as file:
            news_dict = json.load(file)
        for k, v in sorted(news_dict.items())[-5:]:
            news = f"{hbold(datetime.datetime.fromtimestamp(v['article_date_timestamp']))}\n" \
                   f"{hlink(v['article_title'], v['article_url'])}"
            await message.answer(news)
    else:
        await bot.send_message(message.from_user.id, not_sub_message, reply_markup=check_sub_menu)


@dp.message_handler(Text(equals="🍅🗞️Свежие новости"))
async def get_fresh_news(message: types.Message):
    """отправляет свежие новости"""
    fresh_news = check_news_update()
    if len(fresh_news) >= 1:
        for k, v in sorted(fresh_news.items()):
            news = f"{hbold(datetime.datetime.fromtimestamp(v['article_date_timestamp']))}\n" \
                   f"{hlink(v['article_title'], v['article_url'])}"
            await message.answer(news)
    else:
        await message.answer("Пока нет свежих новостей...")


async def news_every_minute():
    """рассылка свежих новостей всем подписчикам(рассылки)"""
    while True:
        fresh_news = check_news_update()
        """получаем список подписчиков"""
        subscribers = db.get_subscriptions()
        if len(fresh_news) >= 1:
            for k, v in sorted(fresh_news.items()):
                news = f"{hbold(datetime.datetime.fromtimestamp(v['article_date_timestamp']))}\n" \
                       f"{hlink(v['article_title'], v['article_url'])}"
                for s in subscribers:
                    """отправляем подписчикам"""
                    await bot.send_message(s[1], news, disable_notification=True)
        else:
            for s in subscribers:
                await bot.send_message(s[1], "Пока нет свежих новостей...", disable_notification=True)
        await asyncio.sleep(100)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(news_every_minute())
    executor.start_polling(dp)
