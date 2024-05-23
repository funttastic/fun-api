import inspect
from abc import ABC
from decimal import Decimal
from typing import Any

from hummingbot.clock import Clock
from hummingbot.constants import DECIMAL_ZERO, DECIMAL_NAN, INT_ZERO, FLOAT_ZERO


class Base(ABC):

	id = ""

	clock: Clock = Clock.instance()

	def log(self, level: int, message: str = "", object: Any = None):
		# noinspection PyUnresolvedReferences
		from core.logger import logger
		logger.log(level=level, prefix=self.id, message=message, object=object, frame=inspect.currentframe().f_back.f_back)

	def telegram_log(self, level: int, message: str = "", object: Any = None):
		# noinspection PyUnresolvedReferences
		from core.telegram.telegram import telegram
		telegram.log(level=level, prefix=self.id, message=message, object=object)

	def ignore_exception(self, exception: Exception):
		# noinspection PyUnresolvedReferences
		from core.logger import logger
		logger.ignore_exception(prefix=self.id, exception=exception, frame=inspect.currentframe().f_back.f_back)

	# noinspection PyMethodMayBeStatic
	def safe_division(self, dividend: Decimal | int | float, divisor: Decimal | int | float):
		if divisor == INT_ZERO or divisor == FLOAT_ZERO or divisor == DECIMAL_ZERO:
			return DECIMAL_NAN
		else:
			return dividend / divisor
