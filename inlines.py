from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import channel_url

channel_sub_bn = InlineKeyboardButton(text="Подписка↗", url=channel_url)
channel_sub_done = InlineKeyboardButton(text="Подписался⇙", callback_data="subchanneldone")

check_sub_menu = InlineKeyboardMarkup(row_width=1)
check_sub_menu.insert(channel_sub_bn)
check_sub_menu.insert(channel_sub_done)

