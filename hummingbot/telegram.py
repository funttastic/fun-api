import requests
from singleton.singleton import ThreadSafeSingleton

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
