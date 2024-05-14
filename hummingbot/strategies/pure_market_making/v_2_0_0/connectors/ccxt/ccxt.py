from ccxt.async_support.base.exchange import Exchange as WebSocketExchange
from ccxt.base.exchange import Exchange as RESTExchange
import ccxt.async_support as ccxt
from core.decorators import log_class_exceptions
from core.utils import deep_merge
from hummingbot.strategies.pure_market_making.v_2_0_0.connectors.base import ConnectorBase, RESTConnectorBase, \
	WebSocketConnectorBase


# import the types
from . import *


# import the converters
from hummingbot.strategies.pure_market_making.v_2_0_0.converters import (
	convert_ccxt_tokens_to_tokens,
	convert_ccxt_tickers_to_tickers,
	convert_ccxt_markets_to_market,
	filter_markets_data_by_names_or_ids,
	get_market_data_by_id_or_name,
	get_token_by_id_name_or_symbol,
	filter_tokens_by_ids_or_names_or_symbols,
	filter_tickers_by_market_ids_or_market_names,
	get_ticker_by_market_name_or_market_id
)


from hummingbot.strategies.pure_market_making.v_2_0_0.utils import retry
from ccxt.base.errors import RequestTimeout as ExchangeRequestTimeout


from pprint import pprint




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


	async def __aenter__(self):
		await self.initialize()
		return self


	async def __aexit__(self, exc_type, exc, tb):
		await self.close()


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


	async def close(self):
		if self.rest: await self.rest.close()
		# if self.websocket: await self.websocket.close()




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


	async def close(self):
		# Close the exchange instance
		if self.exchange: await self.exchange.close()  # type: ignore


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
		token = get_token_by_id_name_or_symbol(
			currencies=self.exchange.currencies,
			token_id=request.id,
			token_name=request.name,
			token_symbol=request.symbol
		)


		return token


	async def get_tokens(self, request: RestGetTokensRequest = None) -> RestGetTokensResponse:
		currencies = await self.get_all_tokens()


		tokens = filter_tokens_by_ids_or_names_or_symbols(
			currencies,
			token_ids=request.ids,
			token_names=request.names,
			token_symbols=request.symbols
		)


		return tokens


	@retry(ExchangeRequestTimeout, tries=3)
	async def get_all_tokens(self, request: RestGetAllTokensRequest = None) -> RestGetAllTokensResponse:
		all_tokens = convert_ccxt_tokens_to_tokens(self.exchange.currencies)


		return all_tokens


	async def get_market(self, request: RestGetMarketRequest = None) -> RestGetMarketResponse:
		markets_data: RestGetAllMarketsResponse = await self.get_all_markets()
		currencies = self.exchange.currencies
		market = get_market_data_by_id_or_name(
			markets_data,
			currencies,
			market_name=request.name,
			market_id=request.id)


		return market


	async def get_markets(self, request: RestGetMarketsRequest = None) -> RestGetMarketsResponse:
		markets_data: RestGetAllMarketsResponse = await self.get_all_markets()
		markets = filter_markets_data_by_names_or_ids(markets_data, market_ids=request.ids, market_names=request.names)


		return markets


	@retry(ExchangeRequestTimeout, tries=3)
	async def get_all_markets(self, request: RestGetAllMarketsRequest = None) -> RestGetAllMarketsResponse:
		# TODO:
		#  1. Filter it by allowed and disallowed market(s)
		#  2. Add retry decorator (for network issues)


		markets: dict = self.exchange.markets
		currencies: dict = self.exchange.currencies
		all_markets = convert_ccxt_markets_to_market(markets, currencies)


		return all_markets.toDict()


	async def get_order_book(self, market_id: str = None, market_name: str = None) -> RestGetOrderBookResponse:
		if not (market_id or market_name):
			raise MarketNameOrIdNotProvidedError()
		elif market_id:
			order_book = self.exchange.fetch_order_book(market_id)
		elif market_name:
			order_book = self.exchange.fetch_order_book(market_name)
		else:
			raise OrderBookNotFoundError()


		return order_book


	async def get_order_books(self, market_ids: list = None, market_names: list = None) -> RestGetOrderBooksResponse:
		# use the market_ids or market_names provided to
		# call the get_order_book_method with each id, or name
		# store the order book in a list
		# return the dictionary of list of order books
		order_books = await self.get_all_order_books()
		pass


	async def get_all_order_books(self, request: RestGetAllOrderBooksRequest = None) -> RestGetAllOrderBooksResponse:
		# fetch all the markets data
		# get the ids of all the market data
		# use the ids to call get_order_books method
		symbol = "BNBUSD_240927"
		order_books = await self.exchange.fetch_orders(symbol=symbol)


		return order_books


	async def get_ticker(self, request: RestGetTickerRequest = None) -> RestGetTickerResponse:
		all_tickers = self.exchange.tickers
		ticker = get_ticker_by_market_name_or_market_id(
			all_tickers,
			market_id=request.market_id,
			market_name=request.market_name
		)


		return ticker


	async def get_tickers(self, request: RestGetTickersRequest = None) -> RestGetTickersResponse:
		all_tickers = await self.get_all_tickers()
		tickers = filter_tickers_by_market_ids_or_market_names(
			all_tickers,
			market_ids=request.market_ids,
			market_names=request.market_names)


		return tickers


	@retry(ExchangeRequestTimeout, tries=3)
	async def get_all_tickers(self, request: RestGetAllTickersRequest = None) -> RestGetAllTickersResponse:
		tickers_data = await self.exchange.fetch_tickers()
		markets = await self.get_all_markets()
		tickers = convert_ccxt_tickers_to_tickers(tickers_data, markets)


		return tickers


	async def get_balance(self, request: RestGetBalanceRequest = None) -> RestGetBalanceResponse:
		pass


	async def get_balances(self, request: RestGetBalancesRequest = None) -> RestGetBalancesResponse:
		pass


	async def get_all_balances(self, request: RestGetAllBalancesRequest = None) -> RestGetAllBalancesResponse:
		pass


	async def get_order(self, request: RestGetOrderRequest = None) -> RestGetOrderResponse:
		# TODO: FUNCTION 1
		order = self.exchange.fetch_orders()


		pass


	async def get_orders(self, request: RestGetOrdersRequest = None) -> RestGetOrdersResponse:
		# TODO: FUNCTION 2
		pass


	async def get_all_open_orders(self, request: RestGetAllOpenOrdersRequest = None) -> RestGetAllOpenOrdersResponse:
		pass


	async def get_all_filled_orders(self, request: RestGetAllFilledOrdersRequest = None) -> RestGetAllFilledOrdersResponse:
		pass


	async def get_all_orders(self, request: RestGetAllOrdersRequest = None) -> RestGetAllOrdersResponse:
		# TODO: FUNCTION 3
		pass


	async def place_order(self, request: RestPlaceOrderRequest = None) -> RestPlaceOrderResponse:
		# TODO: FUNCTION 4
		sl = self.exchange.create_order()
		pass


	async def place_orders(self, request: RestPlaceOrdersRequest = None) -> RestPlaceOrdersResponse:
		# TODO: FUNCTION 5
		pass


	async def cancel_order(self, request: RestCancelOrderRequest = None) -> RestCancelOrderResponse:
		# TODO: FUNCTION 6
		pass


	async def cancel_orders(self, request: RestCancelOrdersRequest = None) -> RestCancelOrdersResponse:
		pass


	async def cancel_all_orders(self, request: RestCancelAllOrdersRequest = None) -> RestCancelAllOrdersResponse:
		pass


	async def market_withdraw(self, request: RestMarketWithdrawRequest = None) -> RestMarketWithdrawResponse:
		pass


	async def markets_withdraws(self, request: RestMarketsWithdrawsRequest = None) -> RestMarketsWithdrawsResponse:
		pass


	async def all_markets_withdraws(self, request: RestAllMarketsWithdrawsRequest = None) -> RestAllMarketsWithdrawsResponse:
		pass




class CCXTWebSocketConnector(WebSocketConnectorBase):


	def __init__(self, options: DotMap[str, Any] = None):
		super().__init__(options)


		# noinspection PyTypeChecker
		self.exchange: WebSocketExchange = None


	async def initialize(self, options: DotMap[str, Any] = None):
		pass


	async def close(self):
		# Close the exchange instance
		if self.exchange: await self.exchange.close()  # type: ignore


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

