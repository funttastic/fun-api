from abc import ABC, abstractmethod

from dotmap import DotMap

from hummingbot.strategies.pure_market_making.v_2_0_0.types import *


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
	async def get_current_block(self, request: RestGetCurrentBlockRequest = None) -> RestGetCurrentBlockResponse:
		raise NotImplemented()

	@abstractmethod
	async def get_block(self, request: RestGetBlockRequest = None) -> RestGetBlockResponse:
		raise NotImplemented()

	@abstractmethod
	async def get_blocks(self, request: RestGetBlocksRequest = None) -> RestGetBlocksResponse:
		raise NotImplemented()

	@abstractmethod
	async def get_transaction(self, request: RestGetTransactionRequest = None) -> RestGetTransactionResponse:
		raise NotImplemented()

	@abstractmethod
	async def get_transactions(self, request: RestGetTransactionsRequest = None) -> RestGetTransactionsResponse:
		raise NotImplemented()

	@abstractmethod
	async def get_token(self, request: RestGetTokenRequest = None) -> RestGetTokenResponse:
		raise NotImplemented()

	@abstractmethod
	async def get_tokens(self, request: RestGetTokensRequest = None) -> RestGetTokensResponse:
		raise NotImplemented()

	@abstractmethod
	async def get_all_tokens(self, request: RestGetAllTokensRequest = None) -> RestGetAllTokensResponse:
		raise NotImplemented()

	@abstractmethod
	async def get_market(self, request: RestGetMarketRequest = None) -> RestGetMarketResponse:
		raise NotImplemented()

	@abstractmethod
	async def get_markets(self, request: RestGetMarketsRequest = None) -> RestGetMarketsResponse:
		raise NotImplemented()

	@abstractmethod
	async def get_all_markets(self, request: RestGetAllMarketsRequest = None) -> RestGetAllMarketsResponse:
		raise NotImplemented()

	@abstractmethod
	async def get_order_book(self, request: RestGetOrderBookRequest = None) -> RestGetOrderBookResponse:
		raise NotImplemented()

	@abstractmethod
	async def get_order_books(self, request: RestGetOrderBooksRequest = None) -> RestGetOrderBooksResponse:
		raise NotImplemented()

	@abstractmethod
	async def get_all_order_books(self, request: RestGetAllOrderBooksRequest = None) -> RestGetAllOrderBooksResponse:
		raise NotImplemented()

	@abstractmethod
	async def get_ticker(self, request: RestGetTickerRequest = None) -> RestGetTickerResponse:
		raise NotImplemented()

	@abstractmethod
	async def get_tickers(self, request: RestGetTickersRequest = None) -> RestGetTickersResponse:
		raise NotImplemented()

	@abstractmethod
	async def get_all_tickers(self, request: RestGetAllTickersRequest = None) -> RestGetAllTickersResponse:
		raise NotImplemented()

	@abstractmethod
	async def get_balance(self, request: RestGetBalanceRequest = None) -> RestGetBalanceResponse:
		raise NotImplemented()

	@abstractmethod
	async def get_balances(self, request: RestGetBalancesRequest = None) -> RestGetBalancesResponse:
		raise NotImplemented()

	@abstractmethod
	async def get_all_balances(self, request: RestGetAllBalancesRequest = None) -> RestGetAllBalancesResponse:
		raise NotImplemented()

	@abstractmethod
	async def get_order(self, request: RestGetOrderRequest = None) -> RestGetOrderResponse:
		raise NotImplemented()

	@abstractmethod
	async def get_orders(self, request: RestGetOrdersRequest = None) -> RestGetOrdersResponse:
		raise NotImplemented()

	@abstractmethod
	async def get_all_open_orders(self, request: RestGetAllOpenOrdersRequest = None) -> RestGetAllOpenOrdersResponse:
		raise NotImplemented()

	@abstractmethod
	async def get_all_filled_orders(self, request: RestGetAllFilledOrdersRequest = None) -> RestGetAllFilledOrdersResponse:
		raise NotImplemented()

	@abstractmethod
	async def get_all_orders(self, request: RestGetAllOrdersRequest = None) -> RestGetAllOrdersResponse:
		raise NotImplemented()

	@abstractmethod
	async def place_order(self, request: RestPlaceOrderRequest = None) -> RestPlaceOrderResponse:
		raise NotImplemented()

	@abstractmethod
	async def place_orders(self, request: RestPlaceOrdersRequest = None) -> RestPlaceOrdersResponse:
		raise NotImplemented()

	async def replace_order(self, request: RestReplaceOrderRequest = None) -> RestReplaceOrderResponse:
		raise NotImplemented()

	async def replace_orders(self, request: RestReplaceOrdersRequest = None) -> RestReplaceOrdersResponse:
		raise NotImplemented()

	@abstractmethod
	async def cancel_order(self, request: RestCancelOrderRequest = None) -> RestCancelOrderResponse:
		raise NotImplemented()

	@abstractmethod
	async def cancel_orders(self, request: RestCancelOrdersRequest = None) -> RestCancelOrdersResponse:
		raise NotImplemented()

	@abstractmethod
	async def cancel_all_orders(self, request: RestCancelAllOrdersRequest = None) -> RestCancelAllOrdersResponse:
		raise NotImplemented()

	@abstractmethod
	async def market_withdraw(self, request: RestMarketWithdrawRequest = None) -> RestMarketWithdrawResponse:
		raise NotImplemented()

	@abstractmethod
	async def markets_withdraws(self, request: RestMarketsWithdrawsRequest = None) -> RestMarketsWithdrawsResponse:
		raise NotImplemented()

	@abstractmethod
	async def all_markets_withdraws(self, request: RestAllMarketsWithdrawsRequest = None) -> RestAllMarketsWithdrawsResponse:
		raise NotImplemented()


class WebSocketConnectorBase(BasicConnectorBase):

	# noinspection PyUnusedLocal
	def __init__(self, options: DotMap[str, Any] = None):
		super().__init__(options)

	@abstractmethod
	async def initialize(self, options: DotMap[str, Any] = None):
		raise NotImplemented()

	@abstractmethod
	async def watch_order_book(self, request: WsWatchOrderBookRequest = None) -> Optional[WsWatchOrderBookResponse]:
		raise NotImplemented()

	@abstractmethod
	async def watch_order_books(self, request: WsWatchOrderBooksRequest = None) -> Optional[WsWatchOrderBooksResponse]:
		raise NotImplemented()

	@abstractmethod
	async def watch_all_order_books(self, request: WsWatchAllOrderBooksRequest = None) -> Optional[WsWatchAllOrderBooksResponse]:
		raise NotImplemented()

	@abstractmethod
	async def watch_ticker(self, request: WsWatchTickerRequest = None) -> Optional[WsWatchTickerResponse]:
		raise NotImplemented()

	@abstractmethod
	async def watch_tickers(self, request: WsWatchTickersRequest = None) -> Optional[WsWatchTickersResponse]:
		raise NotImplemented()

	@abstractmethod
	async def watch_all_tickers(self, request: WsWatchAllTickersRequest = None) -> Optional[WsWatchAllTickersResponse]:
		raise NotImplemented()

	@abstractmethod
	async def watch_balance(self, request: WsWatchBalanceRequest = None) -> Optional[WsWatchBalanceResponse]:
		raise NotImplemented()

	@abstractmethod
	async def watch_balances(self, request: WsWatchBalancesRequest = None) -> Optional[WsWatchBalancesResponse]:
		raise NotImplemented()

	@abstractmethod
	async def watch_all_balances(self, request: WsWatchAllBalancesRequest = None) -> Optional[WsWatchAllBalancesResponse]:
		raise NotImplemented()

	@abstractmethod
	async def watch_order(self, request: WsWatchOrderRequest = None) -> Optional[WsWatchOrderResponse]:
		raise NotImplemented()

	@abstractmethod
	async def watch_orders(self, request: WsWatchOrdersRequest = None) -> Optional[WsWatchOrdersResponse]:
		raise NotImplemented()

	@abstractmethod
	async def watch_all_open_orders(self, request: WsWatchAllOpenOrdersRequest = None) -> Optional[WsWatchAllOpenOrdersResponse]:
		raise NotImplemented()

	@abstractmethod
	async def watch_all_filled_orders(self, request: WsWatchAllFilledOrdersRequest = None) -> Optional[WsWatchAllFilledOrdersResponse]:
		raise NotImplemented()

	@abstractmethod
	async def watch_all_orders(self, request: WsWatchAllOrdersRequest = None) -> Optional[WsWatchAllOrdersResponse]:
		raise NotImplemented()

	@abstractmethod
	async def create_order(self, request: WsCreateOrderRequest = None) -> Optional[WsCreateOrderResponse]:
		raise NotImplemented()

	@abstractmethod
	async def create_orders(self, request: WsCreateOrdersRequest = None) -> Optional[WsCreateOrdersResponse]:
		raise NotImplemented()

	@abstractmethod
	async def cancel_order(self, request: WsCancelOrderRequest = None) -> Optional[WsCancelOrderResponse]:
		raise NotImplemented()

	@abstractmethod
	async def cancel_orders(self, request: WsCancelOrdersRequest = None) -> Optional[WsCancelOrdersResponse]:
		raise NotImplemented()

	@abstractmethod
	async def cancel_all_orders(self, request: WsCancelAllOrdersRequest = None) -> Optional[WsCancelAllOrdersResponse]:
		raise NotImplemented()

	@abstractmethod
	async def market_withdraw(self, request: WsMarketWithdrawRequest = None) -> Optional[WsMarketWithdrawResponse]:
		raise NotImplemented()

	@abstractmethod
	async def markets_withdraws(self, request: WsMarketsWithdrawsRequest = None) -> Optional[WsMarketsWithdrawsFundsResponse]:
		raise NotImplemented()

	@abstractmethod
	async def all_markets_withdraws(self, request: WsAllMarketsWithdrawsRequest = None) -> Optional[WsAllMarketsWithdrawsResponse]:
		raise NotImplemented()

	@abstractmethod
	async def watch_indicator(self, request: WsWatchIndicatorRequest = None) -> Optional[WsWatchIndicatorResponse]:
		raise NotImplemented()

	@abstractmethod
	async def watch_indicators(self, request: WsWatchIndicatorsRequest = None) -> Optional[WsWatchIndicatorsResponse]:
		raise NotImplemented()

	@abstractmethod
	async def watch_all_indicators(self, request: WsWatchAllIndicatorsRequest = None) -> Optional[WsWatchAllIndicatorsResponse]:
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
