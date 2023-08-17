import inspect
from abc import ABC
from typing import Any

from hummingbot.clock import Clock


class Base(ABC):

	logger_prefix = ""

	clock: Clock = Clock.instance()

	def log(self, level: int, message: str = "", object: Any = None):
		# noinspection PyUnresolvedReferences
		from logger import logger
		logger.log(level=level, prefix=self.logger_prefix, message=message, object=object, frame=inspect.currentframe().f_back.f_back)

	def ignore_exception(self, exception: Exception):
		# noinspection PyUnresolvedReferences
		from logger import logger
		logger.ignore_exception(prefix=self.logger_prefix, exception=exception, frame=inspect.currentframe().f_back.f_back)
