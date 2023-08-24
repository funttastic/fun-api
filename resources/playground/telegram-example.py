# Documentation https://github.com/python-telegram-bot/python-telegram-bot/wiki/Extensions---Your-first-Bot
import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


# if you send a "/start" it will trigger the start function below
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

# if you send a "/caps word to capitalize" it will trigger the caps function below
async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_caps = ' '.join(context.args).upper()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)

# if you send a non especified command like "/ttt" it will trigger the unknow function below
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

if __name__ == '__main__':
    application = ApplicationBuilder().token('<token>').build()

    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo) # echo is not working
    caps_handler = CommandHandler('caps', caps)
    start_handler = CommandHandler('start', start)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    application.add_handler(echo_handler)
    application.add_handler(caps_handler)
    application.add_handler(start_handler)
    application.add_handler(unknown_handler)

    application.run_polling()
