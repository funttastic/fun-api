import ccxt.async_support as ccxt
from ccxt.async_support.base.exchange import Exchange as WebSocketExchange
from ccxt.base.exchange import Exchange as RESTExchange
from dotmap import DotMap
from typing import Any, Optional

from core.decorators import log_class_exceptions
from core.utils import deep_merge
from hummingbot.strategies.pure_market_making.v_2_0_0.connectors.base import ConnectorBase, RESTConnectorBase, \
	WebSocketConnectorBase
from hummingbot.strategies.pure_market_making.v_2_0_0.connectors.ccxt.convertors import CCXTConvertors
from hummingbot.strategies.pure_market_making.v_2_0_0.types import WsCancelAllOrdersRequest, WsCancelAllOrdersResponse, \
	WsMarketWithdrawRequest, WsMarketWithdrawResponse, WsMarketsWithdrawsRequest, WsMarketsWithdrawsFundsResponse, \
	WsAllMarketsWithdrawsRequest, WsAllMarketsWithdrawsResponse, WsWatchIndicatorRequest, WsWatchIndicatorResponse, \
	WsWatchIndicatorsRequest, WsWatchIndicatorsResponse, WsWatchAllIndicatorsRequest, WsWatchAllIndicatorsResponse, \
	WsCancelOrdersResponse, WsCancelOrdersRequest, WsCancelOrderResponse, WsCancelOrderRequest, WsCreateOrdersRequest, \
	WsCreateOrdersResponse, WsCreateOrderResponse, WsCreateOrderRequest, WsWatchAllOrdersRequest, \
	WsWatchAllOrdersResponse, WsWatchOrderBookRequest, WsWatchOrderBookResponse, WsWatchOrderBooksRequest, \
	WsWatchOrderBooksResponse, WsWatchAllOrderBooksRequest, WsWatchAllOrderBooksResponse, WsWatchTickerRequest, \
	WsWatchTickerResponse, WsWatchTickersRequest, WsWatchTickersResponse, WsWatchAllTickersRequest, \
	WsWatchAllTickersResponse, WsWatchBalanceRequest, WsWatchBalanceResponse, WsWatchBalancesRequest, \
	WsWatchBalancesResponse, WsWatchAllBalancesRequest, WsWatchAllBalancesResponse, WsWatchOrderResponse, \
	WsWatchOrderRequest, WsWatchOrdersRequest, WsWatchOrdersResponse, WsWatchAllOpenOrdersRequest, \
	WsWatchAllOpenOrdersResponse, WsWatchAllFilledOrdersRequest, WsWatchAllFilledOrdersResponse, \
	RestAllMarketsWithdrawsResponse, RestAllMarketsWithdrawsRequest, RestMarketsWithdrawsResponse, \
	RestMarketsWithdrawsRequest, RestMarketWithdrawResponse, RestMarketWithdrawRequest, RestCancelAllOrdersResponse, \
	RestCancelAllOrdersRequest, RestCancelOrdersResponse, RestCancelOrdersRequest, RestGetOrderRequest, \
	RestCancelOrderResponse, RestCancelOrderRequest, RestPlaceOrdersResponse, RestPlaceOrdersRequest, \
	RestGetMarketRequest, RestPlaceOrderResponse, RestPlaceOrderRequest, RestGetAllOrdersRequest, \
	RestGetAllFilledOrdersResponse, RestGetAllFilledOrdersRequest, RestGetAllOpenOrdersResponse, \
	RestGetAllOpenOrdersRequest, RestGetOrdersResponse, RestGetOrdersRequest, RestGetOrderResponse, \
	RestGetAllBalancesResponse, RestGetAllBalancesRequest, RestGetBalancesResponse, RestGetBalancesRequest, \
	RestGetBalanceResponse, RestGetBalanceRequest, RestGetAllTickersResponse, RestGetAllTickersRequest, \
	RestGetTickersResponse, RestGetTickersRequest, RestGetTickerResponse, RestGetTickerRequest, \
	RestGetAllOrderBooksResponse, RestGetAllOrderBooksRequest, RestGetOrderBooksResponse, RestGetOrderBooksRequest, \
	RestGetOrderBookResponse, RestGetOrderBookRequest, RestGetAllMarketsResponse, RestGetAllMarketsRequest, \
	RestGetAllOrdersResponse, RestGetMarketsResponse, RestGetMarketsRequest, RestGetMarketResponse, \
	RestGetAllTokensResponse, RestGetAllTokensRequest, RestGetTokensResponse, RestGetTokensRequest, \
	RestGetTokenResponse, RestGetTokenRequest, RestGetTransactionsResponse, RestGetTransactionsRequest, \
	RestGetTransactionResponse, RestGetTransactionRequest, RestGetBlocksResponse, RestGetBlocksRequest, \
	RestGetBlockResponse, RestGetBlockRequest, RestGetCurrentBlockResponse, RestGetCurrentBlockRequest


@log_class_exceptions
class CCXTConnector(ConnectorBase):

	def __init__(self, options: DotMap[str, Any] = None):
		super().__init__(options)

		# noinspection PyTypeChecker
		self.rest: CCXTRESTConnector = None
		# noinspection PyTypeChecker
		self.websocket: CCXTWebSocketConnector = None

		# noinspection PyTypeChecker
		self._configuration: DotMap[str, Any] = None

	async def initialize(self, options: DotMap[str, Any] = None):
		self._configuration = options

		options = DotMap({
			"id": self._configuration.ccxt.exchange.id,
			"environment": self._configuration.ccxt.exchange.environment,
		})

		await self.initialize_rest_connector(
			DotMap(
				deep_merge(
					options.toDict(),
					self._configuration.ccxt.exchange.rest.toDict()
				),
				_dynamic=False
			)
		)
		await self.initialize_websocket_connector(
			DotMap(
				deep_merge(
					options.toDict(),
					self._configuration.ccxt.exchange.websocket.toDict()
				),
				_dynamic=False
			)
		)

	async def initialize_rest_connector(self, options: DotMap[str, Any] = None):
		self.rest: CCXTRESTConnector = CCXTRESTConnector()
		await self.rest.initialize(options)

	async def initialize_websocket_connector(self, options: DotMap[str, Any] = None):
		self.websocket: CCXTWebSocketConnector = CCXTWebSocketConnector()
		await self.rest.initialize(options)


class CCXTRESTConnector(RESTConnectorBase):

	def __init__(self, options: DotMap[str, Any] = None):
		super().__init__(options)

		# noinspection PyTypeChecker
		self.exchange: RESTExchange = None

	async def initialize(self, options: DotMap[str, Any] = None):
		exchange_class = getattr(ccxt, options.id)
		constructor: DotMap[str, Any] = options.constructor

		self.exchange: RESTExchange = exchange_class(constructor.toDict())

		self.exchange.options = deep_merge(
			self.exchange.options,
			options.options
		)

		if options.environment != "production":
			self.exchange.set_sandbox_mode(True)

		await self.exchange.load_markets()

	async def get_current_block(self, request: RestGetCurrentBlockRequest = None) -> RestGetCurrentBlockResponse:
		input = CCXTConvertors.rest_get_current_block_request(request)

		output = await self.exchange.fetch_current_block(input)

		response = CCXTConvertors.rest_get_current_block_response(output)

		return response

	async def get_block(self, request: RestGetBlockRequest = None) -> RestGetBlockResponse:
		input = CCXTConvertors.rest_get_block_request(request)

		output = await self.exchange.fetch_block(input)

		response = CCXTConvertors.rest_get_block_response(output)

		return response

	async def get_blocks(self, request: RestGetBlocksRequest = None) -> RestGetBlocksResponse:
		input = CCXTConvertors.rest_get_blocks_request(request)

		output = await self.exchange.fetch_blocks(input)

		response = CCXTConvertors.rest_get_blocks_response(output)

		return response

	async def get_transaction(self, request: RestGetTransactionRequest = None) -> RestGetTransactionResponse:
		input = CCXTConvertors.rest_get_transaction_request(request)

		output = await self.exchange.fetch_transaction(input)

		response = CCXTConvertors.rest_get_transaction_response(output)

		return response

	async def get_transactions(self, request: RestGetTransactionsRequest = None) -> RestGetTransactionsResponse:
		input = CCXTConvertors.rest_get_transactions_request(request)

		output = await self.exchange.fetch_transactions(input)

		response = CCXTConvertors.rest_get_transactions_response(output)

		return response

	async def get_token(self, request: RestGetTokenRequest = None) -> RestGetTokenResponse:
		input = CCXTConvertors.rest_get_token_request(request)

		output = await self.exchange.fetch_token(input)

		response = CCXTConvertors.rest_get_token_response(output)

		return response

	async def get_tokens(self, request: RestGetTokensRequest = None) -> RestGetTokensResponse:
		input = CCXTConvertors.rest_get_tokens_request(request)

		output = await self.exchange.fetch_tokens(input)

		response = CCXTConvertors.rest_get_tokens_response(output)

		return response

	async def get_all_tokens(self, request: RestGetAllTokensRequest = None) -> RestGetAllTokensResponse:
		input = CCXTConvertors.rest_get_all_tokens_request(request)

		output = await self.exchange.fetch_all_tokens(input)

		response = CCXTConvertors.rest_get_all_tokens_response(output)

		return response

	async def get_market(self, request: RestGetMarketRequest = None) -> RestGetMarketResponse:
		input = CCXTConvertors.rest_get_market_request(request)

		output = await self.get_markets(input)

		response = CCXTConvertors.rest_get_market_response(output)

		return response

	async def get_markets(self, request: RestGetMarketsRequest = None) -> RestGetMarketsResponse:
		input = CCXTConvertors.rest_get_markets_request(request)

		all_markets = await self.get_all_markets(input)

		output = RestGetMarketsResponse()
		for market_id, market in all_markets.items():
			if market_id in request.ids:
				output[market_id] = market

		response = CCXTConvertors.rest_get_markets_response(output)

		return response

	async def get_all_markets(self, request: RestGetAllMarketsRequest = None) -> RestGetAllMarketsResponse:
		input = CCXTConvertors.rest_get_all_markets_request(request)

		output = await self.exchange.fetch_markets(input)

		response = CCXTConvertors.rest_get_all_markets_response(output)

		return response

	async def get_order_book(self, request: RestGetOrderBookRequest = None) -> RestGetOrderBookResponse:
		input = CCXTConvertors.rest_get_order_book_request(request)

		output = await self.exchange.fetch_order_book(input)

		response = CCXTConvertors.rest_get_order_book_response(output)

		return response

	async def get_order_books(self, request: RestGetOrderBooksRequest = None) -> RestGetOrderBooksResponse:
		input = CCXTConvertors.rest_get_order_books_request(request)

		output = await self.exchange.fetch_order_books(input)

		response = CCXTConvertors.rest_get_order_books_response(output)

		return response

	async def get_all_order_books(self, request: RestGetAllOrderBooksRequest = None) -> RestGetAllOrderBooksResponse:
		input = CCXTConvertors.rest_get_all_order_books_request(request)

		output = await self.exchange.fetch_all_order_books(input)

		response = CCXTConvertors.rest_get_all_order_books_response(output)

		return response

	async def get_ticker(self, request: RestGetTickerRequest = None) -> RestGetTickerResponse:
		input = CCXTConvertors.rest_get_ticker_request(request)

		output = await self.exchange.fetch_ticker(input)

		response = CCXTConvertors.rest_get_ticker_response(output)

		return response

	async def get_tickers(self, request: RestGetTickersRequest = None) -> RestGetTickersResponse:
		input = CCXTConvertors.rest_get_tickers_request(request)

		output = await self.exchange.fetch_tickers(input)

		response = CCXTConvertors.rest_get_tickers_response(output)

		return response

	async def get_all_tickers(self, request: RestGetAllTickersRequest = None) -> RestGetAllTickersResponse:
		input = CCXTConvertors.rest_get_all_tickers_request(request)

		output = await self.exchange.fetch_all_tickers(input)

		response = CCXTConvertors.rest_get_all_tickers_response(output)

		return response

	async def get_balance(self, request: RestGetBalanceRequest = None) -> RestGetBalanceResponse:
		input = CCXTConvertors.rest_get_balance_request(request)

		output = await self.exchange.fetch_balance(input)

		response = CCXTConvertors.rest_get_balance_response(output)

		return response

	async def get_balances(self, request: RestGetBalancesRequest = None) -> RestGetBalancesResponse:
		input = CCXTConvertors.rest_get_balances_request(request)

		output = await self.exchange.fetch_balances(input)

		response = CCXTConvertors.rest_get_balances_response(output)

		return response

	async def get_all_balances(self, request: RestGetAllBalancesRequest = None) -> RestGetAllBalancesResponse:
		input = CCXTConvertors.rest_get_all_balances_request(request)

		output = await self.exchange.fetch_balance(input)

		response = CCXTConvertors.rest_get_all_balances_response(output)

		return response

	async def get_order(self, request: RestGetOrderRequest = None) -> RestGetOrderResponse:
		input = CCXTConvertors.rest_get_order_request(request)

		output = await self.exchange.fetch_order(input)

		response = CCXTConvertors.rest_get_order_response(output)

		return response

	async def get_orders(self, request: RestGetOrdersRequest = None) -> RestGetOrdersResponse:
		input = CCXTConvertors.rest_get_orders_request(request)

		output = await self.exchange.fetch_orders(input)

		response = CCXTConvertors.rest_get_orders_response(output)

		return response

	async def get_all_open_orders(self, request: RestGetAllOpenOrdersRequest = None) -> RestGetAllOpenOrdersResponse:
		input = CCXTConvertors.rest_get_all_open_orders_request(request)

		output = await self.exchange.fetch_all_open_orders(input)

		response = CCXTConvertors.rest_get_all_open_orders_response(output)

		return response

	async def get_all_filled_orders(self, request: RestGetAllFilledOrdersRequest = None) -> RestGetAllFilledOrdersResponse:
		input = CCXTConvertors.rest_get_all_filled_orders_request(request)

		output = await self.exchange.fetch_all_filled_orders(input)

		response = CCXTConvertors.rest_get_all_filled_orders_response(output)

		return response

	async def get_all_orders(self, request: RestGetAllOrdersRequest = None) -> RestGetAllOrdersResponse:
		input = CCXTConvertors.rest_get_all_orders_request(request)

		output = await self.exchange.fetch_all_orders(input)

		response = CCXTConvertors.rest_get_all_orders_response(output)

		return response

	async def place_order(self, request: RestPlaceOrderRequest = None) -> RestPlaceOrderResponse:
		input = CCXTConvertors.rest_place_order_request(request)

		output = await self.exchange.create_order(input)

		response = CCXTConvertors.rest_place_order_response(output)

		return response

	async def place_orders(self, request: RestPlaceOrdersRequest = None) -> RestPlaceOrdersResponse:
		input = CCXTConvertors.rest_place_orders_request(request)

		output = await self.exchange.create_orders(input)

		response = CCXTConvertors.rest_place_orders_response(output)

		return response

	async def cancel_order(self, request: RestCancelOrderRequest = None) -> RestCancelOrderResponse:
		input = CCXTConvertors.rest_cancel_order_request(request)

		output = await self.exchange.cancel_order(input)

		response = CCXTConvertors.rest_cancel_order_response(output)

		return response

	async def cancel_orders(self, request: RestCancelOrdersRequest = None) -> RestCancelOrdersResponse:
		input = CCXTConvertors.rest_cancel_orders_request(request)

		output = await self.exchange.cancel_orders(input)

		response = CCXTConvertors.rest_cancel_orders_response(output)

		return response

	async def cancel_all_orders(self, request: RestCancelAllOrdersRequest = None) -> RestCancelAllOrdersResponse:
		input = CCXTConvertors.rest_cancel_all_orders_request(request)

		output = await self.exchange.cancel_all_orders(input)

		response = CCXTConvertors.rest_cancel_all_orders_response(output)

		return response

	async def market_withdraw(self, request: RestMarketWithdrawRequest = None) -> RestMarketWithdrawResponse:
		input = CCXTConvertors.rest_market_withdraw_request(request)

		output = await self.exchange.withdraw(input)

		response = CCXTConvertors.rest_market_withdraw_response(output)

		return response

	async def markets_withdraws(self, request: RestMarketsWithdrawsRequest = None) -> RestMarketsWithdrawsResponse:
		input = CCXTConvertors.rest_markets_withdraws_request(request)

		output = await self.exchange.withdraws(input)

		response = CCXTConvertors.rest_markets_withdraws_response(output)

		return response

	async def all_markets_withdraws(self, request: RestAllMarketsWithdrawsRequest = None) -> RestAllMarketsWithdrawsResponse:
		input = CCXTConvertors.rest_all_markets_withdraws_request(request)

		output = await self.exchange.all_withdraws(input)

		response = CCXTConvertors.rest_all_markets_withdraws_response(output)

		return response



class CCXTWebSocketConnector(WebSocketConnectorBase):

	def __init__(self, options: DotMap[str, Any] = None):
		super().__init__(options)

		# noinspection PyTypeChecker
		self.exchange: WebSocketExchange = None

	async def initialize(self, options: DotMap[str, Any] = None):
		exchange_class = getattr(ccxt, options.id)
		constructor: DotMap[str, Any] = options.constructor

		self.exchange: WebSocketExchange = exchange_class(constructor.toDict())

		self.exchange.options = deep_merge(
			self.exchange.options,
			options.options
		)

		if options.environment != "production":
			self.exchange.set_sandbox_mode(True)

	async def watch_order_book(self, request: WsWatchOrderBookRequest = None) -> Optional[WsWatchOrderBookResponse]:
		input = CCXTConvertors.ws_watch_order_book_request(request)

		output = await self.exchange.watch_order_book(input)

		response = CCXTConvertors.ws_watch_order_book_response(output)

		return response

	async def watch_order_books(self, request: WsWatchOrderBooksRequest = None) -> Optional[WsWatchOrderBooksResponse]:
		input = CCXTConvertors.ws_watch_order_books_request(request)

		output = await self.exchange.watch_order_books(input)

		response = CCXTConvertors.ws_watch_order_books_response(output)

		return response

	async def watch_all_order_books(self, request: WsWatchAllOrderBooksRequest = None) -> Optional[WsWatchAllOrderBooksResponse]:
		input = CCXTConvertors.ws_watch_all_order_books_request(request)

		output = await self.exchange.watch_all_order_books(input)

		response = CCXTConvertors.ws_watch_all_order_books_response(output)

		return response

	async def watch_ticker(self, request: WsWatchTickerRequest = None) -> Optional[WsWatchTickerResponse]:
		input = CCXTConvertors.ws_watch_ticker_request(request)

		output = await self.exchange.watch_ticker(input)

		response = CCXTConvertors.ws_watch_ticker_response(output)

		return response

	async def watch_tickers(self, request: WsWatchTickersRequest = None) -> Optional[WsWatchTickersResponse]:
		input = CCXTConvertors.ws_watch_tickers_request(request)

		output = await self.exchange.watch_tickers(input)

		response = CCXTConvertors.ws_watch_tickers_response(output)

		return response

	async def watch_all_tickers(self, request: WsWatchAllTickersRequest = None) -> Optional[WsWatchAllTickersResponse]:
		input = CCXTConvertors.ws_watch_all_tickers_request(request)

		output = await self.exchange.watch_all_tickers(input)

		response = CCXTConvertors.ws_watch_all_tickers_response(output)

		return response

	async def watch_balance(self, request: WsWatchBalanceRequest = None) -> Optional[WsWatchBalanceResponse]:
		input = CCXTConvertors.ws_watch_balance_request(request)

		output = await self.exchange.watch_balance(input)

		response = CCXTConvertors.ws_watch_balance_response(output)

		return response

	async def watch_balances(self, request: WsWatchBalancesRequest = None) -> Optional[WsWatchBalancesResponse]:
		input = CCXTConvertors.ws_watch_balances_request(request)

		output = await self.exchange.watch_balances(input)

		response = CCXTConvertors.ws_watch_balances_response(output)

		return response

	async def watch_all_balances(self, request: WsWatchAllBalancesRequest = None) -> Optional[WsWatchAllBalancesResponse]:
		input = CCXTConvertors.ws_watch_all_balances_request(request)

		output = await self.exchange.watch_all_balances(input)

		response = CCXTConvertors.ws_watch_all_balances_response(output)

		return response

	async def watch_order(self, request: WsWatchOrderRequest = None) -> Optional[WsWatchOrderResponse]:
		input = CCXTConvertors.ws_watch_order_request(request)

		output = await self.exchange.watch_order(input)

		response = CCXTConvertors.ws_watch_order_response(output)

		return response

	async def watch_orders(self, request: WsWatchOrdersRequest = None) -> Optional[WsWatchOrdersResponse]:
		input = CCXTConvertors.ws_watch_orders_request(request)

		output = await self.exchange.watch_orders(input)

		response = CCXTConvertors.ws_watch_orders_response(output)

		return response

	async def watch_all_open_orders(self, request: WsWatchAllOpenOrdersRequest = None) -> Optional[WsWatchAllOpenOrdersResponse]:
		input = CCXTConvertors.ws_watch_all_open_orders_request(request)

		output = await self.exchange.watch_all_open_orders(input)

		response = CCXTConvertors.ws_watch_all_open_orders_response(output)

		return response

	async def watch_all_filled_orders(self, request: WsWatchAllFilledOrdersRequest = None) -> Optional[WsWatchAllFilledOrdersResponse]:
		input = CCXTConvertors.ws_watch_all_filled_orders_request(request)

		output = await self.exchange.watch_all_filled_orders(input)

		response = CCXTConvertors.ws_watch_all_filled_orders_response(output)

		return response

	async def watch_all_orders(self, request: WsWatchAllOrdersRequest = None) -> Optional[WsWatchAllOrdersResponse]:
		input = CCXTConvertors.ws_watch_all_orders_request(request)

		output = await self.exchange.watch_all_orders(input)

		response = CCXTConvertors.ws_watch_all_orders_response(output)

		return response

	async def create_order(self, request: WsCreateOrderRequest = None) -> Optional[WsCreateOrderResponse]:
		input = CCXTConvertors.ws_create_order_request(request)

		output = await self.exchange.create_order(input)

		response = CCXTConvertors.ws_create_order_response(output)

		return response

	async def create_orders(self, request: WsCreateOrdersRequest = None) -> Optional[WsCreateOrdersResponse]:
		input = CCXTConvertors.ws_create_orders_request(request)

		output = await self.exchange.create_orders(input)

		response = CCXTConvertors.ws_create_orders_response(output)

		return response

	async def cancel_order(self, request: WsCancelOrderRequest = None) -> Optional[WsCancelOrderResponse]:
		input = CCXTConvertors.ws_cancel_order_request(request)

		output = await self.exchange.cancel_order(input)

		response = CCXTConvertors.ws_cancel_order_response(output)

		return response

	async def cancel_orders(self, request: WsCancelOrdersRequest = None) -> Optional[WsCancelOrdersResponse]:
		input = CCXTConvertors.ws_cancel_orders_request(request)

		output = await self.exchange.cancel_orders(input)

		response = CCXTConvertors.ws_cancel_orders_response(output)

		return response

	async def cancel_all_orders(self, request: WsCancelAllOrdersRequest = None) -> Optional[WsCancelAllOrdersResponse]:
		input = CCXTConvertors.ws_cancel_all_orders_request(request)

		output = await self.exchange.cancel_all_orders(input)

		response = CCXTConvertors.ws_cancel_all_orders_response(output)

		return response

	async def market_withdraw(self, request: WsMarketWithdrawRequest = None) -> Optional[WsMarketWithdrawResponse]:
		input = CCXTConvertors.ws_market_withdraw_request(request)

		output = await self.exchange.withdraw(input)

		response = CCXTConvertors.ws_market_withdraw_response(output)

		return response

	async def markets_withdraws(self, request: WsMarketsWithdrawsRequest = None) -> Optional[WsMarketsWithdrawsFundsResponse]:
		input = CCXTConvertors.ws_markets_withdraws_request(request)

		output = await self.exchange.withdraws(input)

		response = CCXTConvertors.ws_markets_withdraws_response(output)

		return response

	async def all_markets_withdraws(self, request: WsAllMarketsWithdrawsRequest = None) -> Optional[WsAllMarketsWithdrawsResponse]:
		input = CCXTConvertors.ws_all_markets_withdraws_request(request)

		output = await self.exchange.all_withdraws(input)

		response = CCXTConvertors.ws_all_markets_withdraws_response(output)

		return response

	async def watch_indicator(self, request: WsWatchIndicatorRequest = None) -> Optional[WsWatchIndicatorResponse]:
		input = CCXTConvertors.ws_watch_indicator_request(request)

		output = await self.exchange.watch_indicator(input)

		response = CCXTConvertors.ws_watch_indicator_response(output)

		return response

	async def watch_indicators(self, request: WsWatchIndicatorsRequest = None) -> Optional[WsWatchIndicatorsResponse]:
		input = CCXTConvertors.ws_watch_indicators_request(request)

		output = await self.exchange.watch_indicators(input)

		response = CCXTConvertors.ws_watch_indicators_response(output)

		return response

	async def watch_all_indicators(self, request: WsWatchAllIndicatorsRequest = None) -> Optional[WsWatchAllIndicatorsResponse]:
		input = CCXTConvertors.ws_watch_all_indicators_request(request)

		output = await self.exchange.watch_all_indicators(input)

		response = CCXTConvertors.ws_watch_all_indicators_response(output)

		return response
