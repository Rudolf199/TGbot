import asyncio
import datetime
import json
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.markdown import hbold, hunderline, hcode, hlink
from aiogram.dispatcher.filters import Text
from config import token, user_id
from news import check_news_update
from sqlighter import SQLighter


bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)
db = SQLighter('database.db')
# start_buttons = ["📰 Все новости", "⬅ Последние 5 новостей", "🍅🗞️Свежие новости"]
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
    # keyboard.add(*start_buttons)

    await message.answer("Лента новостей", reply_markup=start_buttons)

@dp.message_handler(Text(equals="✔ Подписаться"))
async def subscribe(message: types.Message):
    if not db.subscriber_exists(message.from_user.id):
        # если юзера нет в базе, добавляем его
        db.add_subscriber(message.from_user.id)
    else:
        # если он есть, то просто обновляем ему статус
        db.update_subscription(message.from_user.id, True)

    await message.answer("Вы подписались на рассылку 📧")

@dp.message_handler(Text(equals="❌ Отписаться"))
async def subscribe(message: types.Message):
    if not db.subscriber_exists(message.from_user.id):
        # если юзера нет в базе, добавляем его с неактивной подпиской, запоминаем его
        db.add_subscriber(message.from_user.id, False)
        await message.answer("Вы не подписаны 🤨")
    else:
        # если он есть, то просто обновляем ему статус
        db.update_subscription(message.from_user.id, False)
        await message.answer("Вы отписались от рассылки👋")

    # await message.answer("Вы подписались на рассылку 📧")


"""@dp.message_handler(commands="start")
async def start(message: types.Message):
    start_buttons = ["Все новости", "Последние 5 новостей", "Свежие новости"]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)

    await message.answer("Лента новостей", reply_markup=keyboard)"""

@dp.message_handler(Text(equals="📰 Все новости"))
async def get_all_news(message: types.Message):
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


@dp.message_handler(Text(equals="⬅ Последние 5 новостей"))
async def get_last_five_news(message: types.Message):
    with open("news_dict.json", encoding='utf-8') as file:
        news_dict = json.load(file)

    for k, v in sorted(news_dict.items())[-5:]:
        news = f"{hbold(datetime.datetime.fromtimestamp(v['article_date_timestamp']))}\n" \
               f"{hlink(v['article_title'], v['article_url'])}"

        await message.answer(news)


@dp.message_handler(Text(equals="🍅🗞️Свежие новости"))
async def get_fresh_news(message: types.Message):
    fresh_news = check_news_update()

    if len(fresh_news) >= 1:
        for k, v in sorted(fresh_news.items()):
            news = f"{hbold(datetime.datetime.fromtimestamp(v['article_date_timestamp']))}\n" \
                   f"{hlink(v['article_title'], v['article_url'])}"

            await message.answer(news)

    else:
        await message.answer("Пока нет свежих новостей...")


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