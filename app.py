import asyncio
import datetime
import json
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.markdown import hbold, hunderline, hcode, hlink
from aiogram.dispatcher.filters import Text
from config import token, user_id, chat_id, not_sub_message, channel_url
from inlines import check_sub_menu
from news import check_news_update
from sqlighter import DataBase
from config import db_uri
from config import user, port, password, database, host

bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)
db = DataBase(host=host, password=password, port=port, user=user, database=database)
# start_buttons = ["📰 Все новости", "⬅ Последние 5 новостей", "🍅🗞️Свежие новости"]

def check_sub_channel(chat_member):
    print(chat_member['status'], "\n")
    if chat_member['status'] != 'left':
        return True
    else:
        return False


@dp.message_handler(commands="start")
async def start(message: types.Message):
    # start_buttons = ["📰 Все новости", "⬅ Последние 5 новостей", "🍅🗞️Свежие новости"]
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
    """sub_button = types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(text="Подписка↗", url=channel_url)
            ],
        ],
        resize_keyboard=True)"""

    # keyboard.add(*start_buttons)
    if check_sub_channel(await bot.get_chat_member(chat_id=chat_id, user_id=message.from_user.id)):
        await message.answer("Лента новостей", reply_markup=start_buttons)
    else:
        await bot.send_message(message.from_user.id, not_sub_message, reply_markup=check_sub_menu)
        # await message.answer(not_sub_message)  # , reply_markup=sub_button)"""
    # await message.answer("Лента новостей", reply_markup=start_buttons)

@dp.message_handler(Text(equals="✔ Подписаться"))
async def subscribe(message: types.Message):
    if check_sub_channel(await bot.get_chat_member(chat_id=chat_id, user_id=message.from_user.id)):
        if not db.subscriber_exists(message.from_user.id):
            # если юзера нет в базе, добавляем его
            db.add_subscriber(message.from_user.id)
        else:
            await message.answer("wait...")
            # если он есть, то просто обновляем ему статус
            db.update_subscription(message.from_user.id, True)

        await message.answer("Вы подписались на рассылку 📧")
    else:
        await bot.send_message(message.from_user.id, not_sub_message, reply_markup=check_sub_menu)
        # await bot.send_message(message.from_user.id, not_sub_message, reply_markup=sub_button)
        # await message.answer(not_sub_message)  # , reply_markup=sub_button)

@dp.callback_query_handler(text="subchanneldone")
async def sub_channel_done(message: types.Message):
    await bot.delete_message(message.from_user.id, message.message.message_id)
    if check_sub_channel(await bot.get_chat_member(chat_id=chat_id, user_id=message.from_user.id)):
        await message.answer("Лента новостей", reply_markup=start_buttons)
    else:
        await bot.send_message(message.from_user.id, not_sub_message, reply_markup=check_sub_menu)


@dp.message_handler(Text(equals="❌ Отписаться"))
async def unsubscribe(message: types.Message):
    if check_sub_channel(await bot.get_chat_member(chat_id=chat_id, user_id=message.from_user.id)):
        if not db.subscriber_exists(message.from_user.id):
            # если юзера нет в базе, добавляем его с неактивной подпиской, запоминаем его
            db.add_subscriber(message.from_user.id, False)
            await message.answer("Вы не подписаны 🤨")
        else:
            # если он есть, то просто обновляем ему статус
            db.update_subscription(message.from_user.id, False)
            await message.answer("Вы отписались от рассылки👋")
    else:
        # await bot.send_message(message.from_user.id, not_sub_message, reply_markup=sub_button)
        await bot.send_message(message.from_user.id, not_sub_message, reply_markup=check_sub_menu)
        # await message.answer(not_sub_message) # , reply_markup=sub_button)
    # await message.answer("Вы подписались на рассылку 📧")

"""@dp.message_handler(Text(equals="Подписка↗"))
async def sub_channel(message: types.Message):
    pass"""


@dp.message_handler(Text(equals="📰 Все новости"))
async def get_all_news(message: types.Message):
    if check_sub_channel(await bot.get_chat_member(chat_id=chat_id, user_id=message.from_user.id)):
        with open("news_dict.json", encoding='utf-8') as file:
            news_dict = json.load(file)

        for k, v in sorted(news_dict.items()):
            # news = f"<b>{datetime.datetime.fromtimestamp(v['article_date_timestamp'])}</b>\n" \
            #        f"<u>{v['article_title']}</u>\n" \
            #        f"<code>{v['article_desc']}</code>\n" \
            #        f"{v['article_url']}"
            # news = f"{hbold(datetime.datetime.fromtimestamp(v['article_date_timestamp']))}\n" \
            #        f"{hunderline(v['article_title'])}\n" \
            #        f"{hcode(v['article_desc'])}\n" \
            #        f"{hlink(v['article_title'], v['article_url'])}"
            news = f"{hbold(datetime.datetime.fromtimestamp(v['article_date_timestamp']))}\n" \
                   f"{hlink(v['article_title'], v['article_url'])}"

            await message.answer(news)
    else:
        # await bot.send_message(message.from_user.id, not_sub_message, reply_markup=sub_button)
        await bot.send_message(message.from_user.id, not_sub_message, reply_markup=check_sub_menu)
        # await message.answer(not_sub_message) # , reply_markup=sub_button)


@dp.message_handler(Text(equals="⬅ Последние 5 новостей"))
async def get_last_five_news(message: types.Message):
    if check_sub_channel(await bot.get_chat_member(chat_id=chat_id, user_id=message.from_user.id)):
        with open("news_dict.json", encoding='utf-8') as file:
            news_dict = json.load(file)

        for k, v in sorted(news_dict.items())[-5:]:
            news = f"{hbold(datetime.datetime.fromtimestamp(v['article_date_timestamp']))}\n" \
                   f"{hlink(v['article_title'], v['article_url'])}"

            await message.answer(news)
    else:
        # await bot.send_message(message.from_user.id, not_sub_message, reply_markup=sub_button)
        await bot.send_message(message.from_user.id, not_sub_message, reply_markup=check_sub_menu)
        # await message.answer(not_sub_message)  #, reply_markup=sub_button)


@dp.message_handler(Text(equals="🍅🗞️Свежие новости"))
async def get_fresh_news(message: types.Message):
    if check_sub_channel(await bot.get_chat_member(chat_id=chat_id, user_id=message.from_user.id)):
        fresh_news = check_news_update()

        if len(fresh_news) >= 1:
            for k, v in sorted(fresh_news.items()):
                news = f"{hbold(datetime.datetime.fromtimestamp(v['article_date_timestamp']))}\n" \
                       f"{hlink(v['article_title'], v['article_url'])}"

                await message.answer(news)

        else:
            await message.answer("Пока нет свежих новостей...")
    else:
        await bot.send_message(message.from_user.id, not_sub_message, reply_markup=check_sub_menu)
        # await bot.send_message(message.from_user.id, not_sub_message, reply_markup=sub_button, disable_notification=True)
        # await message.answer(not_sub_message)  # , reply_markup=sub_button)

async def news_every_minute():
    while True:
        fresh_news = check_news_update()
        # получаем список подписчиков
        subscribers = db.get_subscriptions()
        if len(fresh_news) >= 1:
            for k, v in sorted(fresh_news.items()):
                news = f"{hbold(datetime.datetime.fromtimestamp(v['article_date_timestamp']))}\n" \
                       f"{hlink(v['article_title'], v['article_url'])}"
                for s in subscribers:
                    # get your id @userinfobot
                    # отправляем подписчикам
                    await bot.send_message(s[1], news, disable_notification=True)
        else:
            for s in subscribers:
                await bot.send_message(s[1], "Пока нет свежих новостей...", disable_notification=True)

        await asyncio.sleep(1)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(news_every_minute())
    executor.start_polling(dp)