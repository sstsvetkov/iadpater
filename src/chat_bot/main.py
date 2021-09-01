from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler
from telegram.ext import Updater

updater = Updater(
    token="1394218710:AAH3qyJ87XQmW730zkRKnrOnd17Y2by8E5Y", use_context=True
)


def start(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton("Включить уведомления", callback_data="1"),
            InlineKeyboardButton("Выключить уведомления", callback_data="2"),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Уведомления выключены.",
        reply_markup=reply_markup,
    )


def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    query.answer()

    if query.data == "1":
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="Уведомления включены."
        )
    elif query.data == "2":
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="Уведомления выключены."
        )


def main():
    dispatcher = updater.dispatcher
    start_handler = CommandHandler(["start", "help"], start)
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(start_handler)
    updater.start_polling()


if __name__ == "__main__":
    main()
