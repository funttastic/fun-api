from hummingbot.strategies.base import Base


class WorkerBase(Base):

	def __init__(self):
		self.id: str
