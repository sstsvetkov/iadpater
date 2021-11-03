"""
This bot is created for the demonstration of a usage of regular keyboards.
"""

import logging

from aiogram import Bot, Dispatcher, executor, types

# Configure logging
from settings import TG_NOTIFICATIONS_TOKEN
from queries import get_receiver, update_receiver

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Initialize bot and dispatcher
bot = Bot(token=TG_NOTIFICATIONS_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands="start")
async def start_cmd_handler(message: types.Message):
    keyboard_markup = types.InlineKeyboardMarkup(row_width=3)
    keyboard_markup.row(
        types.InlineKeyboardButton(text="Включить уведомления", callback_data="1"),
        types.InlineKeyboardButton(text="Выключить уведомления", callback_data="2"),
    )
    receiver = await get_receiver(tg_dialog_id=message.from_user.id)
    if receiver and receiver["send_notifications"]:
        msg = "Уведомления включены"
    else:
        msg = "Уведомления выключены"
    await message.reply(msg, reply_markup=keyboard_markup)


@dp.callback_query_handler(lambda c: c.data)
async def process_callback(callback_query: types.CallbackQuery):
    data = callback_query.data
    keyboard_markup = types.InlineKeyboardMarkup(row_width=3)
    keyboard_markup.row(
        types.InlineKeyboardButton(text="Включить уведомления", callback_data="1"),
        types.InlineKeyboardButton(text="Выключить уведомления", callback_data="2"),
    )
    if data == "1":
        await update_receiver(
            tg_dialog_id=callback_query.from_user.id, send_notifications=True
        )
        await bot.edit_message_text(
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            text="Уведомления включены",
            reply_markup=keyboard_markup,
        )
    if data == "2":
        await update_receiver(
            tg_dialog_id=callback_query.from_user.id, send_notifications=False
        )
        await bot.edit_message_text(
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            text="Уведомления выключены",
            reply_markup=keyboard_markup,
        )


def main():
    executor.start_polling(dp, skip_updates=True)


if __name__ == "__main__":
    main()
