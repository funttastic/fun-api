import copy
from logging import INFO

from ccxt.base.exchange import Exchange
from dotmap import DotMap
from typing import Any

import ccxt

from core.decorators import log_class_exceptions
from core.utils import deep_merge
from hummingbot.strategies.pure_market_making.v_2_0_0.workers.base import WorkerBase


@log_class_exceptions
class CCXTWorker(WorkerBase):

	async def initialize(self):
		try:
			exchange_class = getattr(ccxt, self._configuration.ccxt.exchange.id)
			constructor: DotMap[str, Any] = self._configuration.ccxt.exchange.constructor

			self.exchange: Exchange = exchange_class(constructor.toDict())

			self.exchange.options = deep_merge(
				self.exchange.options,
				self._configuration.ccxt.exchange.options
			)

			if self._configuration.ccxt.exchange.environment != "production":
				self.exchange.set_sandbox_mode(True)

			await super().initialize()

			self._can_run = False  # TODO revert to True when the implementation is ready!!!
		except Exception as exception:
			self.ignore_exception(exception)

			raise exception
		finally:
			self.telegram_log(INFO, "initialized.")
			self.log(INFO, "end")
