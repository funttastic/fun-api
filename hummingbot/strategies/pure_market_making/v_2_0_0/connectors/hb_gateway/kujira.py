from dotmap import DotMap
from typing import Any

from core.decorators import log_class_exceptions
from core.utils import deep_merge
from hummingbot.hummingbot_gateway import HummingbotGateway
from hummingbot.strategies.pure_market_making.v_2_0_0.connectors.base import ConnectorBase, RESTConnectorBase, \
	WebSocketConnectorBase
from hummingbot.strategies.pure_market_making.v_2_0_0.types import *


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

	async def get_current_block(self, request: RestGetCurrentBlockRequest = None) -> RestGetCurrentBlockResponse:
		parameters = request

		response = HummingbotGateway.kujira_get_block_current(parameters)

		output = response

		return output

	async def get_block(self, request: RestGetBlockRequest = None) -> RestGetBlockResponse:
		pass

	async def get_blocks(self, request: RestGetBlocksRequest = None) -> RestGetBlocksResponse:
		pass

	async def get_transaction(self, request: RestGetTransactionRequest = None) -> RestGetTransactionResponse:
		parameters = request

		response = HummingbotGateway.kujira_get_transaction(parameters)

		output = response

		return output

	async def get_transactions(self, request: RestGetTransactionsRequest = None) -> RestGetTransactionsResponse:
		parameters = request

		response = HummingbotGateway.kujira_get_transactions(parameters)

		output = response

		return output

	async def get_token(self, request: RestGetTokenRequest = None) -> RestGetTokenResponse:
		parameters = request

		response = HummingbotGateway.kujira_get_token(parameters)

		output = response

		return output

	async def get_tokens(self, request: RestGetTokensRequest = None) -> RestGetTokensResponse:
		parameters = request

		response = HummingbotGateway.kujira_get_tokens(parameters)

		output = response

		return output

	async def get_all_tokens(self, request: RestGetAllTokensRequest = None) -> RestGetAllTokensResponse:
		parameters = request

		response = HummingbotGateway.kujira_get_tokens_all(parameters)

		output = response

		return output

	async def get_market(self, request: RestGetMarketRequest = None) -> RestGetMarketResponse:
		parameters = request

		response = HummingbotGateway.kujira_get_market(parameters)

		output = response

		return output

	async def get_markets(self, request: RestGetMarketsRequest = None) -> RestGetMarketsResponse:
		parameters = request

		response = HummingbotGateway.kujira_get_markets(parameters)

		output = response

		return output

	async def get_all_markets(self, request: RestGetAllMarketsRequest = None) -> RestGetAllMarketsResponse:
		parameters = request

		response = HummingbotGateway.kujira_get_markets(parameters)

		output = response

		return output

	async def get_order_book(self, request: RestGetOrderBookRequest = None) -> RestGetOrderBookResponse:
		parameters = request

		response = HummingbotGateway.kujira_get_order_book(parameters)

		output = response

		return output

	async def get_order_books(self, request: RestGetOrderBooksRequest = None) -> RestGetOrderBooksResponse:
		parameters = request

		response = HummingbotGateway.kujira_get_order_books(parameters)

		output = response

		return output

	async def get_all_order_books(self, request: RestGetAllOrderBooksRequest = None) -> RestGetAllOrderBooksResponse:
		parameters = request

		response = HummingbotGateway.kujira_get_order_books_all(parameters)

		output = response

		return output

	async def get_ticker(self, request: RestGetTickerRequest = None) -> RestGetTickerResponse:
		parameters = request

		response = HummingbotGateway.kujira_get_ticker(parameters)

		output = response

		return output

	async def get_tickers(self, request: RestGetTickersRequest = None) -> RestGetTickersResponse:
		parameters = request

		response = HummingbotGateway.kujira_get_tickers(parameters)

		output = response

		return output

	async def get_all_tickers(self, request: RestGetAllTickersRequest = None) -> RestGetAllTickersResponse:
		parameters = request

		response = HummingbotGateway.kujira_get_tickers_all(parameters)

		output = response

		return output

	async def get_balance(self, request: RestGetBalanceRequest = None) -> RestGetBalanceResponse:
		parameters = request

		response = HummingbotGateway.kujira_get_balance(parameters)

		output = response

		return output

	async def get_balances(self, request: RestGetBalancesRequest = None) -> RestGetBalancesResponse:
		parameters = request

		response = HummingbotGateway.kujira_get_balances(parameters)

		output = response

		return output

	async def get_all_balances(self, request: RestGetAllBalancesRequest = None) -> RestGetAllBalancesResponse:
		parameters = request

		response = HummingbotGateway.kujira_get_balances_all(parameters)

		output = response

		return output

	async def get_order(self, request: RestGetOrderRequest = None) -> RestGetOrderResponse:
		parameters = request

		response = HummingbotGateway.kujira_get_order(parameters)

		output = response

		return output

	async def get_orders(self, request: RestGetOrdersRequest = None) -> RestGetOrdersResponse:
		parameters = request

		response = HummingbotGateway.kujira_get_orders(parameters)

		output = response

		return output

	async def get_all_open_orders(self, request: RestGetAllOpenOrdersRequest = None) -> RestGetAllOpenOrdersResponse:
		parameters = request

		response = HummingbotGateway.kujira_get_orders(parameters)

		output = response

		return output

	async def get_all_filled_orders(self, request: RestGetAllFilledOrdersRequest = None) -> RestGetAllFilledOrdersResponse:
		parameters = request

		response = HummingbotGateway.kujira_get_orders(parameters)

		output = response

		return output

	async def get_all_orders(self, request: RestGetAllOrdersRequest = None) -> RestGetAllOrdersResponse:
		pass

	async def place_order(self, request: RestPlaceOrderRequest = None) -> RestPlaceOrderResponse:
		parameters = request

		response = HummingbotGateway.kujira_post_order(parameters)

		output = response

		return output

	async def place_orders(self, request: RestPlaceOrdersRequest = None) -> RestPlaceOrdersResponse:
		parameters = request

		response = HummingbotGateway.kujira_post_orders(parameters)

		output = response

		return output

	async def cancel_order(self, request: RestCancelOrderRequest = None) -> RestCancelOrderResponse:
		parameters = request

		response = HummingbotGateway.kujira_delete_order(parameters)

		output = response

		return output

	async def cancel_orders(self, request: RestCancelOrdersRequest = None) -> RestCancelOrdersResponse:
		parameters = request

		response = HummingbotGateway.kujira_delete_orders(parameters)

		output = response

		return output

	async def cancel_all_orders(self, request: RestCancelAllOrdersRequest = None) -> RestCancelAllOrdersResponse:
		parameters = request

		response = HummingbotGateway.kujira_delete_orders_all(parameters)

		output = response

		return output

	async def market_withdraw(self, request: RestMarketWithdrawRequest = None) -> RestMarketWithdrawResponse:
		pass

	async def markets_withdraws(self, request: RestMarketsWithdrawsRequest = None) -> RestMarketsWithdrawsFundsResponse:
		pass

	async def all_markets_withdraws(self, request: RestAllMarketsWithdrawsRequest = None) -> RestAllMarketsWithdrawsResponse:
		pass


class HummingbotGatewayKujiraWebSocketConnector(WebSocketConnectorBase):

	def __init__(self, options: DotMap[str, Any] = None):
		super().__init__(options)

	async def initialize(self, options: DotMap[str, Any] = None):
		await super().initialize(options)

	async def watch_order_book(self, request: WsWatchOrderBookRequest = None) -> Optional[WsWatchOrderBookResponse]:
		pass

	async def watch_order_books(self, request: WsWatchOrderBooksRequest = None) -> Optional[WsWatchOrderBooksResponse]:
		pass

	async def watch_all_order_books(self, request: WsWatchAllOrderBooksRequest = None) -> Optional[WsWatchAllOrderBooksResponse]:
		pass

	async def watch_ticker(self, request: WsWatchTickerRequest = None) -> Optional[WsWatchTickerResponse]:
		pass

	async def watch_tickers(self, request: WsWatchTickersRequest = None) -> Optional[WsWatchTickersResponse]:
		pass

	async def watch_all_tickers(self, request: WsWatchAllTickersRequest = None) -> Optional[WsWatchAllTickersResponse]:
		pass

	async def watch_balance(self, request: WsWatchBalanceRequest = None) -> Optional[WsWatchBalanceResponse]:
		pass

	async def watch_balances(self, request: WsWatchBalancesRequest = None) -> Optional[WsWatchBalancesResponse]:
		pass

	async def watch_all_balances(self, request: WsWatchAllBalancesRequest = None) -> Optional[WsWatchAllBalancesResponse]:
		pass

	async def watch_order(self, request: WsWatchOrderRequest = None) -> Optional[WsWatchOrderResponse]:
		pass

	async def watch_orders(self, request: WsWatchOrdersRequest = None) -> Optional[WsWatchOrdersResponse]:
		pass

	async def watch_all_open_orders(self, request: WsWatchAllOpenOrdersRequest = None) -> Optional[WsWatchAllOpenOrdersResponse]:
		pass

	async def watch_all_filled_orders(self, request: WsWatchAllFilledOrdersRequest = None) -> Optional[WsWatchAllFilledOrdersResponse]:
		pass

	async def watch_all_orders(self, request: WsWatchAllOrdersRequest = None) -> Optional[WsWatchAllOrdersResponse]:
		pass

	async def create_order(self, request: WsCreateOrderRequest = None) -> Optional[WsCreateOrderResponse]:
		pass

	async def create_orders(self, request: WsCreateOrdersRequest = None) -> Optional[WsCreateOrdersResponse]:
		pass

	async def cancel_order(self, request: WsCancelOrderRequest = None) -> Optional[WsCancelOrderResponse]:
		pass

	async def cancel_orders(self, request: WsCancelOrdersRequest = None) -> Optional[WsCancelOrdersResponse]:
		pass

	async def cancel_all_orders(self, request: WsCancelAllOrdersRequest = None) -> Optional[WsCancelAllOrdersResponse]:
		pass

	async def market_withdraw(self, request: WsMarketWithdrawRequest = None) -> Optional[WsMarketWithdrawResponse]:
		pass

	async def markets_withdraws(self, request: WsMarketsWithdrawsRequest = None) -> Optional[WsMarketsWithdrawsFundsResponse]:
		pass

	async def all_markets_withdraws(self, request: WsAllMarketsWithdrawsRequest = None) -> Optional[WsAllMarketsWithdrawsResponse]:
		pass

	async def watch_indicator(self, request: WsWatchIndicatorRequest = None) -> Optional[WsWatchIndicatorResponse]:
		pass

	async def watch_indicators(self, request: WsWatchIndicatorsRequest = None) -> Optional[WsWatchIndicatorsResponse]:
		pass

	async def watch_all_indicators(self, request: WsWatchAllIndicatorsRequest = None) -> Optional[WsWatchAllIndicatorsResponse]:
		pass
