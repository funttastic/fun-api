from core.decorators import log_class_exceptions
from core.utils import deep_merge
from hummingbot.hummingbot_gateway import HummingbotGateway
from hummingbot.strategies.pure_market_making.v_2_0_0.connectors.base import ConnectorBase, RESTConnectorBase, \
	WebSocketConnectorBase
from hummingbot.strategies.pure_market_making.v_2_0_0.types import *


@log_class_exceptions
class HummingbotGatewayCLOBConnector(ConnectorBase):

	def __init__(self, options: DotMap[str, Any] = None):
		super().__init__(options)

		# noinspection PyTypeChecker
		self.rest: HummingbotGatewayCLOBRESTConnector = None
		# noinspection PyTypeChecker
		self.websocket: HummingbotGatewayCLOBWebSocketConnector = None

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
		self.rest: HummingbotGatewayCLOBRESTConnector = HummingbotGatewayCLOBRESTConnector()
		await self.rest.initialize(options)

	async def initialize_websocket_connector(self, options: DotMap[str, Any] = None):
		self.websocket: HummingbotGatewayCLOBWebSocketConnector = HummingbotGatewayCLOBWebSocketConnector()
		await self.rest.initialize(options)


class HummingbotGatewayCLOBRESTConnector(RESTConnectorBase):

	def __init__(self, options: DotMap[str, Any] = None):
		super().__init__(options)

	async def initialize(self, options: DotMap[str, Any] = None):
		await super().initialize(options)

	async def get_current_block(self, request: RestGetCurrentBlockRequest = None) -> RestGetCurrentBlockResponse:
		pass

	async def get_block(self, request: RestGetBlockRequest = None) -> RestGetBlockResponse:
		pass

	async def get_blocks(self, request: RestGetBlocksRequest = None) -> RestGetBlocksResponse:
		pass

	async def get_transaction(self, request: RestGetTransactionRequest = None) -> RestGetTransactionResponse:
		pass

	async def get_transactions(self, request: RestGetTransactionsRequest = None) -> RestGetTransactionsResponse:
		pass

	async def get_token(self, request: RestGetTokenRequest = None) -> RestGetTokenResponse:
		pass

	async def get_tokens(self, request: RestGetTokensRequest = None) -> RestGetTokensResponse:
		pass

	async def get_all_tokens(self, request: RestGetAllTokensRequest = None) -> RestGetAllTokensResponse:
		pass

	async def get_market(self, request: RestGetMarketRequest = None) -> RestGetMarketsResponse:
		parameters = request

		result = HummingbotGateway.clob_get_markets(parameters)

		response = result

		return response

	async def get_markets(self, request: RestGetMarketsRequest = None) -> RestGetMarketsResponse:
		pass

	async def get_all_markets(self, request: RestGetAllMarketsRequest = None) -> RestGetAllMarketsResponse:
		pass

	async def get_order_book(self, request: RestGetOrderBookRequest = None) -> RestGetOrderBookResponse:
		pass

	async def get_order_books(self, request: RestGetOrderBooksRequest = None) -> RestGetOrderBooksResponse:
		pass

	async def get_all_order_books(self, request: RestGetAllOrderBooksRequest = None) -> RestGetAllOrderBooksResponse:
		pass

	async def get_ticker(self, request: RestGetTickerRequest = None) -> RestGetTickerResponse:
		pass

	async def get_tickers(self, request: RestGetTickersRequest = None) -> RestGetTickersResponse:
		pass

	async def get_all_tickers(self, request: RestGetAllTickersRequest = None) -> RestGetAllTickersResponse:
		pass

	async def get_balance(self, request: RestGetBalanceRequest = None) -> RestGetBalanceResponse:
		pass

	async def get_balances(self, request: RestGetBalancesRequest = None) -> RestGetBalancesResponse:
		pass

	async def get_all_balances(self, request: RestGetAllBalancesRequest = None) -> RestGetAllBalancesResponse:
		pass

	async def get_order(self, request: RestGetOrderRequest = None) -> RestGetOrderResponse:
		pass

	async def get_orders(self, request: RestGetOrdersRequest = None) -> RestGetOrdersResponse:
		pass

	async def get_all_open_orders(self, request: RestGetAllOpenOrdersRequest = None) -> RestGetAllOpenOrdersResponse:
		pass

	async def get_all_filled_orders(self, request: RestGetAllFilledOrdersRequest = None) -> RestGetAllFilledOrdersResponse:
		pass

	async def get_all_orders(self, request: RestGetAllOrdersRequest = None) -> RestGetAllOrdersResponse:
		pass

	async def place_order(self, request: RestPlaceOrderRequest = None) -> RestPlaceOrderResponse:
		pass

	async def place_orders(self, request: RestPlaceOrdersRequest = None) -> RestPlaceOrdersResponse:
		pass

	async def cancel_order(self, request: RestCancelOrderRequest = None) -> RestCancelOrderResponse:
		pass

	async def cancel_orders(self, request: RestCancelOrdersRequest = None) -> RestCancelOrdersResponse:
		pass

	async def cancel_all_orders(self, request: RestCancelAllOrdersRequest = None) -> RestCancelAllOrdersResponse:
		pass

	async def market_withdraw(self, request: RestMarketWithdrawRequest = None) -> RestMarketWithdrawResponse:
		pass

	async def markets_withdraws(self, request: RestMarketsWithdrawsRequest = None) -> RestMarketsWithdrawsFundsResponse:
		pass

	async def all_markets_withdraws(self, request: RestAllMarketsWithdrawsRequest = None) -> RestAllMarketsWithdrawsResponse:
		pass


class HummingbotGatewayCLOBWebSocketConnector(WebSocketConnectorBase):

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
