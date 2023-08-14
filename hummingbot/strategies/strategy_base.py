from abc import abstractmethod
from typing import Any, Dict

from hummingbot.strategies.base import Base


class StrategyBase(Base):

	ID: str
	VERSION: str
	TITLE: str
	CATEGORY: str

	def __init__(self):
		self.id: str

	@abstractmethod
	def get_status(self) -> Dict[str, Any]:
		pass

	def _calculate_waiting_time(self, number: int) -> int:
		current_timestamp_in_milliseconds = self.clock.now()

		result = int(number - (current_timestamp_in_milliseconds % number))

		if result == 0:
			result = number

		return result
