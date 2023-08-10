import time
from abc import abstractmethod
from typing import Any, Dict

from hummingbot.strategies.base import Base
from hummingbot.utils import current_timestamp


class StrategyBase(Base):

	ID: str
	VERSION: str
	TITLE: str

	def __init__(self):
		self.id: str

	@abstractmethod
	def get_status(self) -> Dict[str, Any]:
		pass

	@staticmethod
	def _calculate_waiting_time(number: int) -> int:
		current_timestamp_in_milliseconds = current_timestamp()

		result = int(number - (current_timestamp_in_milliseconds % number))

		if result == 0:
			result = number

		return result
