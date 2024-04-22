from abc import ABC, abstractmethod

from typing import Any

from dotmap import DotMap


class BasicConnectorBase(ABC):

	# noinspection PyUnusedLocal
	def __init__(self, options: DotMap[str, Any] = None):
		pass


class RESTConnectorBase(BasicConnectorBase, ABC):

	# noinspection PyUnusedLocal
	def __init__(self, options: DotMap[str, Any] = None):
		super().__init__(options)

	@abstractmethod
	async def initialize(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def get_current_block(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def get_block(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def get_blocks(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def get_transaction(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def get_transactions(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def get_token(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def get_tokens(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def get_all_tokens(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def get_market(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def get_markets(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def get_all_markets(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def get_order_book(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def get_order_books(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def get_all_order_books(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def get_ticker(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def get_tickers(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def get_all_tickers(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def get_balance(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def get_balances(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def get_all_balances(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def get_order(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def get_orders(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def get_all_open_orders(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def get_all_filled_orders(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def get_all_orders(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def place_order(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def place_orders(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	async def replace_order(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	async def replace_orders(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def cancel_order(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def cancel_orders(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def cancel_all_orders(self, options: DotMap[str, Any] = None):
		raise NotImplemented()


class WebSocketConnectorBase(BasicConnectorBase):

	# noinspection PyUnusedLocal
	def __init__(self, options: DotMap[str, Any] = None):
		super().__init__(options)

	@abstractmethod
	async def initialize(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def watch_order_book(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def watch_order_books(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def watch_all_order_books(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def watch_ticker(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def watch_tickers(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def watch_all_tickers(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def watch_balance(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def watch_balances(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def watch_all_balances(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def watch_order(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def watch_orders(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def watch_all_open_orders(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def watch_all_filled_orders(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def watch_all_orders(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def create_order(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def create_orders(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def cancel_order(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def cancel_orders(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def cancel_all_orders(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def watch_indicator(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def watch_indicators(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def watch_all_indicators(self, options: DotMap[str, Any] = None):
		raise NotImplemented()


class ConnectorBase(BasicConnectorBase, ABC):

	# noinspection PyUnusedLocal
	def __init__(self, options: DotMap[str, Any] = None):
		super().__init__(options)

		self.rest = None
		self.websocket = None

	@abstractmethod
	async def initialize(self, options: DotMap[str, Any] = None):
		self.rest = await self.initialize_rest_connector(options)
		self.websocket = await self.initialize_websocket_connector(options)

	@abstractmethod
	async def initialize_rest_connector(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def initialize_websocket_connector(self, options: DotMap[str, Any] = None):
		raise NotImplemented()
