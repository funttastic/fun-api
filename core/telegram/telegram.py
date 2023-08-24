from typing import Any

import requests
from singleton.singleton import ThreadSafeSingleton
# noinspection PyUnresolvedReferences
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler

from core.properties import properties
from core.utils import dump
# noinspection PyUnresolvedReferences
from telegram import Update


@ThreadSafeSingleton
class Telegram(object):

	def __init__(self):
		self.url: str = properties.get("telegram.url")
		self.token: str = properties.get("telegram.token")
		self.chat_id: str = properties.get("telegram.chat_id")
		self.parse_mode: str = properties.get("telegram.parse_mode")
		self.final_url: str = self.url.replace("{token}", self.token)
		self.level: bool = properties.get('telegram.level')
		self.enabled: bool = properties.get('telegram.enabled')
		self.listen_commands: bool = properties.get('telegram.listen_commands')

	async def start_command_listener(self):
		if not self.enabled or not self.listen_commands:
			return

		application = ApplicationBuilder().token(self.token).build()

		from core.telegram.commands import Command

		for command in Command:
			application.add_handler(command.handler)

		application.run_polling()

	def send(self, text):
		if not self.enabled:
			return

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
