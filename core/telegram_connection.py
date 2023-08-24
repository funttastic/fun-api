from typing import Any

import requests
from singleton.singleton import ThreadSafeSingleton
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler

from core.controller import controller_strategy_stop, controller_strategy_start, controller_strategy_status
from core.properties import properties
from utils import dump


@ThreadSafeSingleton
class Telegram(object):

	def __init__(self):
		self.url: str = properties.get("telegram.url")
		self.token: str = properties.get("telegram.token")
		self.chat_id: str = properties.get("telegram.chat_id")
		self.parse_mode: str = properties.get("telegram.parse_mode")
		self.final_url: str = self.url.replace("{token}", self.token)
		self.level: bool = properties.get('telegram.level')

	def send(self, text):
		parameters = {
			"chat_id": self.chat_id,
			"parse_mode": self.parse_mode,
			"text": text
		}
		response = requests.get(url=self.final_url, params=parameters)

		return response.json()

	def log(self, level: int, message: str = "", object: Any = None, prefix: str = ""):
		if object:
			message = f'{message}:\n{dump(object)}'

		message = f"{prefix} {message}"

		if level >= self.level:
			telegram.send(message)


telegram = Telegram.instance()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
	chat_id = str(update.message.chat_id)
	if chat_id != telegram.chat_id:
		return

	if not context.args:
		telegram.send("You need to provide the strategy, version and id")
		return

	args = context.args[0].split(':')
	if len(args) != 3:
		telegram.send("You need to provide the strategy, version and id")
		return

	strategy = args[0]
	version = args[1]
	id = args[2]
	response = await controller_strategy_start(strategy, version, id)
	telegram.send(dump(response))


async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
	chat_id = str(update.message.chat_id)
	if chat_id != telegram.chat_id:
		return

	if not context.args:
		telegram.send("You need to provide the strategy, version and id")
		return

	args = context.args[0].split(':')
	if len(args) != 3:
		telegram.send("You need to provide the strategy, version and id")
		return

	strategy = args[0]
	version = args[1]
	id = args[2]
	response = await controller_strategy_stop(strategy, version, id)
	telegram.send(dump(response))


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
	chat_id = str(update.message.chat_id)
	if chat_id != telegram.chat_id:
		return

	if not context.args:
		telegram.send("You need to provide the strategy, version and id")
		return

	args = context.args[0].split(':')
	if len(args) != 3:
		telegram.send("You need to provide the strategy, version and id")
		return

	strategy = args[0]
	version = args[1]
	id = args[2]
	response = await controller_strategy_status(strategy, version, id)
	telegram.send(dump(response))


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
	chat_id = str(update.message.chat_id)
	if chat_id != telegram.chat_id:
		return

	telegram.send("Sorry, I didn't understand that command.")


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
	application.run_polling()
