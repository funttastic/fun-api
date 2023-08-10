from hummingbot.strategies.base import Base


class WorkerBase(Base):

	def __init__(self):
		self.id: str

	def _calculate_waiting_time(self, number: int) -> int:
		current_timestamp_in_milliseconds = self.clock.now()

		result = int(number - (current_timestamp_in_milliseconds % number))

		if result == 0:
			result = number

		return result
