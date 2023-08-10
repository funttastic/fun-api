from hummingbot.strategies.base import Base
from hummingbot.utils import current_timestamp


class WorkerBase(Base):

	def __init__(self):
		self.id: str

	@staticmethod
	def _calculate_waiting_time(number: int) -> int:
		current_timestamp_in_milliseconds = current_timestamp()

		result = int(number - (current_timestamp_in_milliseconds % number))

		if result == 0:
			result = number

		return result
