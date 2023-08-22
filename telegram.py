from typing import Any

import requests
from singleton.singleton import ThreadSafeSingleton

from properties import properties
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
