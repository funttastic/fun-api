import requests
from singleton.singleton import ThreadSafeSingleton
from controller import controller_strategy_stop, controller_strategy_start, controller_strategy_status
from utils import dump
from properties import properties

@ThreadSafeSingleton
class Telegram(object):

	def __init__(self):
		self.url: str = properties.get("telegram.url")
		self.token: str = properties.get("telegram.token")
		self.chat_id: str = properties.get("telegram.chat_id")
		self.parse_mode: str = properties.get("telegram.parse_mode")
		self.final_url: str = self.url.replace("{token}", self.token)

	def send(self, text):
		parameters = {
			"chat_id": self.chat_id,
			"parse_mode": self.parse_mode,
			"text": text
		}
		response = requests.get(url=self.final_url, params=parameters)

		return response.json()


telegram = Telegram.instance()

import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler

logging.basicConfig(
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
	level=logging.INFO
)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
	if not context.args:
		await context.bot.send_message(chat_id=update.effective_chat.id, text="You need to provide the strategy, version and id")
		return

	args = context.args[0].split(':')
	if len(args) != 3:
		await context.bot.send_message(chat_id=update.effective_chat.id, text="You need to provide the strategy, version and id")
		return

	strategy = args[0]
	version = args[1]
	id = args[2]
	response = await controller_strategy_start(strategy, version, id)
	await context.bot.send_message(chat_id=update.effective_chat.id, text=dump(response))

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
	if not context.args:
		await context.bot.send_message(chat_id=update.effective_chat.id, text="You need to provide the strategy, version and id")
		return

	args = context.args[0].split(':')
	if len(args) != 3:
		await context.bot.send_message(chat_id=update.effective_chat.id, text="You need to provide the strategy, version and id")
		return

	strategy = args[0]
	version = args[1]
	id = args[2]
	response = await controller_strategy_stop(strategy, version, id)
	await context.bot.send_message(chat_id=update.effective_chat.id, text=dump(response))

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
	if not context.args:
		await context.bot.send_message(chat_id=update.effective_chat.id, text="You need to provide the strategy, version and id")
		return

	args = context.args[0].split(':')
	if len(args) != 3:
		await context.bot.send_message(chat_id=update.effective_chat.id, text="You need to provide the strategy, version and id")
		return

	strategy = args[0]
	version = args[1]
	id = args[2]
	response = await controller_strategy_status(strategy, version, id)
	await context.bot.send_message(chat_id=update.effective_chat.id, text=dump(response))

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
	await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

async def start_telegram_bot():
	token: str = properties.get("telegram.token")
	application = ApplicationBuilder().token(token).build()
	start_handler = CommandHandler('start', start_command)
	stop_handler = CommandHandler('stop', stop_command)
	status_handler = CommandHandler('status', status_command)
	unknown_handler = MessageHandler(filters.COMMAND, unknown_command)

	application.add_handler(start_handler)
	application.add_handler(stop_handler)
	application.add_handler(status_handler)
	application.add_handler(unknown_handler)
	application.run_polling(timeout=20)
