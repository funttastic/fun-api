from dotmap import DotMap
from typing import Any

from core.decorators import log_class_exceptions
from core.utils import deep_merge
from hummingbot.gateway import Gateway
from hummingbot.strategies.pure_market_making.v_2_0_0.connectors.base import ConnectorBase, RESTConnectorBase, \
	WebSocketConnectorBase


@log_class_exceptions
class HummingbotGatewayKujiraConnector(ConnectorBase):

	def __init__(self, options: DotMap[str, Any] = None):
		super().__init__(options)

		# noinspection PyTypeChecker
		self.rest: HummingbotGatewayKujiraRESTConnector = None
		# noinspection PyTypeChecker
		self.websocket: HummingbotGatewayKujiraWebSocketConnector = None

		# noinspection PyTypeChecker
		self._configuration: DotMap[str, Any] = None

	async def initialize(self, options: DotMap[str, Any] = None):
		self._configuration = options

		options = DotMap({})

		await self.initialize_rest_connector(
			DotMap(
				deep_merge(
					options.toDict(),
					self._configuration.hb_gateway.exchange.rest.toDict()
				),
				_dynamic=False
			)
		)
		await self.initialize_websocket_connector(
			DotMap(
				deep_merge(
					options.toDict(),
					self._configuration.hb_gateway.exchange.websocket.toDict()
				),
				_dynamic=False
			)
		)

	async def initialize_rest_connector(self, options: DotMap[str, Any] = None):
		self.rest: HummingbotGatewayKujiraRESTConnector = HummingbotGatewayKujiraRESTConnector()
		await self.rest.initialize(options)

	async def initialize_websocket_connector(self, options: DotMap[str, Any] = None):
		self.websocket: HummingbotGatewayKujiraWebSocketConnector = HummingbotGatewayKujiraWebSocketConnector()
		await self.rest.initialize(options)


class HummingbotGatewayKujiraRESTConnector(RESTConnectorBase):

	def __init__(self, options: DotMap[str, Any] = None):
		super().__init__(options)

	async def initialize(self, options: DotMap[str, Any] = None):
		await super().initialize(options)

	async def get_current_block(self, options: DotMap[str, Any] = None):
		parameters = options

		response = Gateway.kujira_get_block_current(parameters)

		output = response

		return output

	async def get_block(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	async def get_blocks(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	async def get_transaction(self, options: DotMap[str, Any] = None):
		parameters = options

		response = Gateway.kujira_get_transaction(parameters)

		output = response

		return output

	async def get_transactions(self, options: DotMap[str, Any] = None):
		parameters = options

		response = Gateway.kujira_get_transactions(parameters)

		output = response

		return output

	async def get_token(self, options: DotMap[str, Any] = None):
		parameters = options

		response = Gateway.kujira_get_token(parameters)

		output = response

		return output

	async def get_tokens(self, options: DotMap[str, Any] = None):
		parameters = options

		response = Gateway.kujira_get_tokens(parameters)

		output = response

		return output

	async def get_all_tokens(self, options: DotMap[str, Any] = None):
		parameters = options

		response = Gateway.kujira_get_tokens_all(parameters)

		output = response

		return output

	async def get_market(self, options: DotMap[str, Any] = None):
		parameters = options

		response = Gateway.kujira_get_market(parameters)

		output = response

		return output

	async def get_markets(self, options: DotMap[str, Any] = None):
		parameters = options

		response = Gateway.kujira_get_markets(parameters)

		output = response

		return output

	async def get_all_markets(self, options: DotMap[str, Any] = None):
		parameters = options

		response = Gateway.kujira_get_markets(parameters)

		output = response

		return output

	async def get_order_book(self, options: DotMap[str, Any] = None):
		parameters = options

		response = Gateway.kujira_get_order_book(parameters)

		output = response

		return output

	async def get_order_books(self, options: DotMap[str, Any] = None):
		parameters = options

		response = Gateway.kujira_get_order_books(parameters)

		output = response

		return output

	async def get_all_order_books(self, options: DotMap[str, Any] = None):
		parameters = options

		response = Gateway.kujira_get_order_books_all(parameters)

		output = response

		return output

	async def get_ticker(self, options: DotMap[str, Any] = None):
		parameters = options

		response = Gateway.kujira_get_ticker(parameters)

		output = response

		return output

	async def get_tickers(self, options: DotMap[str, Any] = None):
		parameters = options

		response = Gateway.kujira_get_tickers(parameters)

		output = response

		return output

	async def get_all_tickers(self, options: DotMap[str, Any] = None):
		parameters = options

		response = Gateway.kujira_get_tickers_all(parameters)

		output = response

		return output

	async def get_balance(self, options: DotMap[str, Any] = None):
		parameters = options

		response = Gateway.kujira_get_balance(parameters)

		output = response

		return output

	async def get_balances(self, options: DotMap[str, Any] = None):
		parameters = options

		response = Gateway.kujira_get_balances(parameters)

		output = response

		return output

	async def get_all_balances(self, options: DotMap[str, Any] = None):
		parameters = options

		response = Gateway.kujira_get_balances_all(parameters)

		output = response

		return output

	async def get_order(self, options: DotMap[str, Any] = None):
		parameters = options

		response = Gateway.kujira_get_order(parameters)

		output = response

		return output

	async def get_orders(self, options: DotMap[str, Any] = None):
		parameters = options

		response = Gateway.kujira_get_orders(parameters)

		output = response

		return output

	async def get_all_open_orders(self, options: DotMap[str, Any] = None):
		parameters = options

		response = Gateway.kujira_get_orders(parameters)

		output = response

		return output

	async def get_all_filled_orders(self, options: DotMap[str, Any] = None):
		parameters = options

		response = Gateway.kujira_get_orders(parameters)

		output = response

		return output

	async def get_all_orders(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	async def place_order(self, options: DotMap[str, Any] = None):
		parameters = options

		response = Gateway.kujira_post_order(parameters)

		output = response

		return output

	async def place_orders(self, options: DotMap[str, Any] = None):
		parameters = options

		response = Gateway.kujira_post_orders(parameters)

		output = response

		return output

	async def cancel_order(self, options: DotMap[str, Any] = None):
		parameters = options

		response = Gateway.kujira_delete_order(parameters)

		output = response

		return output

	async def cancel_orders(self, options: DotMap[str, Any] = None):
		parameters = options

		response = Gateway.kujira_delete_orders(parameters)

		output = response

		return output

	async def cancel_all_orders(self, options: DotMap[str, Any] = None):
		parameters = options

		response = Gateway.kujira_delete_orders_all(parameters)

		output = response

		return output


class HummingbotGatewayKujiraWebSocketConnector(WebSocketConnectorBase):

	def __init__(self, options: DotMap[str, Any] = None):
		super().__init__(options)

	async def initialize(self, options: DotMap[str, Any] = None):
		await super().initialize(options)

	async def watch_order_book(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	async def watch_order_books(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	async def watch_all_order_books(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	async def watch_ticker(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	async def watch_tickers(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	async def watch_all_tickers(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	async def watch_balance(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	async def watch_balances(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	async def watch_all_balances(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	async def watch_order(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	async def watch_orders(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	async def watch_all_open_orders(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	async def watch_all_filled_orders(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	async def watch_all_orders(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	async def create_order(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	async def create_orders(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	async def cancel_order(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	async def cancel_orders(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	async def cancel_all_orders(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	async def watch_indicator(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	async def watch_indicators(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	async def watch_all_indicators(self, options: DotMap[str, Any] = None):
		raise NotImplemented()
