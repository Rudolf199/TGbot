import asyncio
# import datetime
import json
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.markdown import hbold, hlink
from aiogram.dispatcher.filters import Text
from config import BOT_TOKEN, admin_id
from news import check_news_update


bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


async def send_to_admin(*args):
    await bot.send_message(chat_id=admin_id, text="Бот запущен")


"""@dp.message_handler()
async def echo(message: Message):
    text = f"Привет, ты написал: {message.text}"
    await message.reply(text=text)"""

@dp.message_handler(commands="start")
async def start(message: types.Message):
    start_buttons = ["Все новости", "Последние 5 новостей", "Свежие новости"]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)
    await message.answer("Лента новостей", reply_markup=keyboard)

@dp.message_handler(commands="stop")
async def stop(message: types.Message):
    start_buttons = ["Все новости", "Последние 5 новостей", "Свежие новости"]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=False)
    await message.answer("Пока!", reply_markup=keyboard)

@dp.message_handler(Text(equals="Все новости"))
async def get_all_news(message: types.Message):
    with open("news_dict.json") as file:
        news_dict = json.load(file)

    for k, v in sorted(news_dict.items()):
        news = f"{hbold(v['article_desc'])}\n" \
               f"{hlink(v['article_title'], v['article_url'])}"
        await message.answer(news)

@dp.message_handler(Text(equals="Последние 5 новостей"))
async def get_last_five_news(message: types.Message):
    with open("news_dict.json") as file:
        news_dict = json.load(file)

    for k, v in sorted(news_dict.items())[-5:]:
        news = f"{hbold(v['article_desc'])}\n" \
               f"{hlink(v['article_title'], v['article_url'])}"
        await message.answer(news)


@dp.message_handler(Text(equals="Свежие новости"))
async def get_fresh_news(message: types.Message):
    fresh_news = check_news_update()

    if len(fresh_news) >= 1:
        for k, v in sorted(fresh_news.items()):
            news = f"{hbold(v['article_desc'])}\n" \
                   f"{hlink(v['article_title'], v['article_url'])}"
            await message.answer(news)
    else:
        await message.answer("Пока нет свежих новостей...")

"""async def news_every_minute():
    while True:
        fresh_news = check_news_update()
        if len(fresh_news) >= 1:
            for k, v in sorted(fresh_news.items()):
                news = f"{hbold(v['article_desc'])}\n" \
                       f"{hlink(v['article_title'], v['article_url'])}"

                # get your id @userinfobot
                await bot.send_message(admin_id, news, disable_notification=True)

        else:
            await bot.send_message(admin_id, "Пока нет свежих новостей...", disable_notification=True)

        await asyncio.sleep(40)"""


if __name__ == '__main__':
    # loop = asyncio.get_event_loop()
    # loop.create_task(news_every_minute())
    executor.start_polling(dp, on_startup=send_to_admin)