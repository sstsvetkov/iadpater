"""
This bot is created for the demonstration of a usage of regular keyboards.
"""

import logging

import asyncio
from aiogram import Bot, Dispatcher, executor, types

# Configure logging
from aiogram.utils.callback_data import CallbackData

from models import Database
from settings import TG_NOTIFICATIONS_TOKEN
from tg_bot.queries import get_receiver, update_receiver

# Initialize bot and dispatcher
# bot = Bot(token=TG_NOTIFICATIONS_TOKEN)
# dp = Dispatcher(bot)


# @dp.message_handler(commands=["start", "help"])
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


# @dp.callback_query_handler(lambda c: c.data)
async def process_callback(callback_query: types.CallbackQuery):
    data = callback_query.data
    keyboard_markup = types.InlineKeyboardMarkup(row_width=3)
    keyboard_markup.row(
        types.InlineKeyboardButton(text="Включить уведомления", callback_data="1"),
        types.InlineKeyboardButton(text="Выключить уведомления", callback_data="2"),
    )
    receiver = await get_receiver(tg_dialog_id=callback_query.message.chat.id)
    if data == "1":
        await update_receiver(
            tg_dialog_id=callback_query.message.chat.id, send_notifications=True
        )
        if receiver and receiver["send_notifications"] is False:
            await callback_query.bot.edit_message_text(
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,
                text="Уведомления включены",
                reply_markup=keyboard_markup,
            )
    if data == "2":
        await update_receiver(
            tg_dialog_id=callback_query.message.chat.id, send_notifications=False
        )
        if receiver and receiver["send_notifications"] is True:
            await callback_query.bot.edit_message_text(
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,
                text="Уведомления выключены",
                reply_markup=keyboard_markup,
            )


async def main():
    db = Database.get_connection_pool(new=True)

    bot = Bot(TG_NOTIFICATIONS_TOKEN, parse_mode="HTML")
    bot["db"] = db
    dp = Dispatcher(bot)

    dp.register_message_handler(start_cmd_handler, commands="start"),
    dp.register_message_handler(start_cmd_handler, commands="help")
    dp.register_callback_query_handler(process_callback)

    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()
    # try:
    #     loop = asyncio.new_event_loop()
    #     asyncio.set_event_loop(loop)
    #     executor.start_polling(dp, skip_updates=True)
    # except Exception:
    #     logging.exception("Error")


if __name__ == "__main__":
    main()
