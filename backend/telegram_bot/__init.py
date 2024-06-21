from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters

from config import Config

def start(update: Update, context: CallbackContext):
    update.message.reply_text('Hello! I am your task review bot.')

def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    update.message.reply_text(f'You said: {text}')

def main():
    TOKEN = Config.TELEGRAM_BOT_TOKEN
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
