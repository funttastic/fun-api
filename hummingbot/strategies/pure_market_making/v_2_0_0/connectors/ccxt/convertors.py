from dotmap import DotMap
from typing import Any

from singleton.singleton import ThreadSafeSingleton

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


CCXTRestGetAllMarketsRequest = Any
CCXTRestGetAllMarketsResponse = Any


class CCXTConvertors:

	@staticmethod
	def rest_cancel_all_orders_request(input: RestCancelAllOrdersRequest) -> Any:
		output = input
		return output

	@staticmethod
	def rest_cancel_all_orders_response(input: Any) -> RestCancelAllOrdersResponse:
		output = input
		return output

	@staticmethod
	def rest_cancel_order_request(input: RestCancelOrderRequest) -> Any:
		output = input
		return output

	@staticmethod
	def rest_cancel_order_response(input: Any) -> RestCancelOrderResponse:
		output = input
		return output

	@staticmethod
	def rest_cancel_orders_request(input: RestCancelOrdersRequest) -> Any:
		output = input
		return output

	@staticmethod
	def rest_cancel_orders_response(input: Any) -> RestCancelOrdersResponse:
		output = input
		return output

	@staticmethod
	def rest_get_all_balances_request(input: RestGetAllBalancesRequest) -> Any:
		output = input
		return output

	@staticmethod
	def rest_get_all_balances_response(input: Any) -> RestGetAllBalancesResponse:
		output = input
		return output

	@staticmethod
	def rest_get_all_filled_orders_request(input: RestGetAllFilledOrdersRequest) -> Any:
		output = input
		return output

	@staticmethod
	def rest_get_all_filled_orders_response(input: Any) -> RestGetAllFilledOrdersResponse:
		output = input
		return output

	@staticmethod
	def rest_get_all_markets_request(_input: RestGetAllMarketsRequest) -> CCXTRestGetAllMarketsRequest:
		return None

	@staticmethod
	def rest_get_all_markets_response(input: CCXTRestGetAllMarketsResponse) -> RestGetAllMarketsResponse:
		output = {}
		for item in input:
			output[item['symbol']] = item
		return output

	@staticmethod
	def rest_get_all_open_orders_request(input: RestGetAllOpenOrdersRequest) -> Any:
		output = input
		return output

	@staticmethod
	def rest_get_all_open_orders_response(input: Any) -> RestGetAllOpenOrdersResponse:
		output = input
		return output

	@staticmethod
	def rest_get_all_order_books_request(input: RestGetAllOrderBooksRequest) -> Any:
		output = input
		return output

	@staticmethod
	def rest_get_all_order_books_response(input: Any) -> RestGetAllOrderBooksResponse:
		output = input
		return output

	@staticmethod
	def rest_get_all_orders_request(input: RestGetAllOrdersRequest) -> Any:
		output = input
		return output

	@staticmethod
	def rest_get_all_orders_response(input: Any) -> RestGetAllOrdersResponse:
		output = input
		return output

	@staticmethod
	def rest_get_all_tickers_request(input: RestGetAllTickersRequest) -> Any:
		output = input
		return output

	@staticmethod
	def rest_get_all_tickers_response(input: Any) -> RestGetAllTickersResponse:
		output = input
		return output

	@staticmethod
	def rest_get_all_tokens_request(input: RestGetAllTokensRequest) -> Any:
		output = input
		return output

	@staticmethod
	def rest_get_all_tokens_response(input: Any) -> RestGetAllTokensResponse:
		output = input
		return output

	@staticmethod
	def rest_get_balances_request(input: RestGetBalancesRequest) -> Any:
		output = input
		return output

	@staticmethod
	def rest_get_balances_response(input: Any) -> RestGetBalancesResponse:
		output = input
		return output

	@staticmethod
	def rest_get_balance_request(input: RestGetBalanceRequest) -> Any:
		output = input
		return output

	@staticmethod
	def rest_get_balance_response(input: Any) -> RestGetBalanceResponse:
		output = input
		return output

	@staticmethod
	def rest_get_block_request(input: RestGetBlockRequest) -> Any:
		output = input
		return output

	@staticmethod
	def rest_get_block_response(input: Any) -> RestGetBlockResponse:
		output = input
		return output

	@staticmethod
	def rest_get_blocks_request(input: RestGetBlocksRequest) -> Any:
		output = input
		return output

	@staticmethod
	def rest_get_blocks_response(input: Any) -> RestGetBlocksResponse:
		output = input
		return output

	@staticmethod
	def rest_get_current_block_request(input: RestGetCurrentBlockRequest) -> Any:
		output = input
		return output

	@staticmethod
	def rest_get_current_block_response(input: Any) -> RestGetCurrentBlockResponse:
		output = input
		return output

	@staticmethod
	def rest_get_market_request(input: RestGetMarketRequest) -> Any:
		output = RestGetMarketsRequest(
			ids=[input.id],
			names=[input.name]
		)

		return output

	@staticmethod
	def rest_get_market_response(input: RestGetMarketsResponse) -> RestGetMarketResponse:
		output = next(iter(input.values()), None)

		return output

	@staticmethod
	def rest_get_markets_request(input: RestGetMarketsRequest) -> Any:
		output = input

		return output

	@staticmethod
	def rest_get_markets_response(input: Any) -> RestGetMarketsResponse:
		output = input.toDict()

		return output

	@staticmethod
	def rest_get_order_books_request(input: RestGetOrderBooksRequest) -> Any:
		output = input
		return output

	@staticmethod
	def rest_get_order_books_response(input: Any) -> RestGetOrderBooksResponse:
		output = input
		return output

	@staticmethod
	def rest_get_order_book_request(input: RestGetOrderBookRequest) -> Any:
		output = input
		return output

	@staticmethod
	def rest_get_order_book_response(input: Any) -> RestGetOrderBookResponse:
		output = input
		return output

	@staticmethod
	def rest_get_orders_request(input: RestGetOrdersRequest) -> Any:
		output = DotMap(
			symbol=input.market_id
		)

		return output

	@staticmethod
	def rest_get_orders_response(input: Any) -> RestGetOrdersResponse:
		output = DotMap(
			orders=input
		)
		return output.toDict()

	@staticmethod
	def rest_get_order_request(input: RestGetOrderRequest) -> Any:
		output = DotMap(
			id=input.id,
			symbol=input.market_id
		)

		return output

	@staticmethod
	def rest_get_order_response(input: Any) -> RestGetOrderResponse:
		output = input
		return output

	@staticmethod
	def rest_get_ticker_request(input: RestGetTickerRequest) -> Any:
		output = input
		return output

	@staticmethod
	def rest_get_ticker_response(input: Any) -> RestGetTickerResponse:
		output = input
		return output

	@staticmethod
	def rest_get_tickers_request(input: RestGetTickersRequest) -> Any:
		output = input
		return output

	@staticmethod
	def rest_get_tickers_response(input: Any) -> RestGetTickersResponse:
		output = input
		return output

	@staticmethod
	def rest_get_token_request(input: RestGetTokenRequest) -> Any:
		output = input
		return output

	@staticmethod
	def rest_get_token_response(input: Any) -> RestGetTokenResponse:
		output = input
		return output

	@staticmethod
	def rest_get_tokens_request(input: RestGetTokensRequest) -> Any:
		output = input
		return output

	@staticmethod
	def rest_get_tokens_response(input: Any) -> RestGetTokensResponse:
		output = input
		return output

	@staticmethod
	def rest_get_transaction_request(input: RestGetTransactionRequest) -> Any:
		output = input
		return output

	@staticmethod
	def rest_get_transaction_response(input: Any) -> RestGetTransactionResponse:
		output = input
		return output

	@staticmethod
	def rest_get_transactions_request(input: RestGetTransactionsRequest) -> Any:
		output = input
		return output

	@staticmethod
	def rest_get_transactions_response(input: Any) -> RestGetTransactionsResponse:
		output = input
		return output

	@staticmethod
	def rest_market_withdraw_request(input: RestMarketWithdrawRequest) -> Any:
		output = input
		return output

	@staticmethod
	def rest_market_withdraw_response(input: Any) -> RestMarketWithdrawResponse:
		output = input
		return output

	@staticmethod
	def rest_markets_withdraws_request(input: RestMarketsWithdrawsRequest) -> Any:
		output = input
		return output

	@staticmethod
	def rest_markets_withdraws_response(input: Any) -> RestMarketsWithdrawsResponse:
		output = input
		return output

	@staticmethod
	def rest_place_order_request(input: RestPlaceOrderRequest) -> Any:
		output = input
		return output

	@staticmethod
	def rest_place_order_response(input: Any) -> RestPlaceOrderResponse:
		output = input
		return output

	@staticmethod
	def rest_place_orders_request(input: RestPlaceOrdersRequest) -> Any:
		output = input
		return output

	@staticmethod
	def rest_place_orders_response(input: Any) -> RestPlaceOrdersResponse:
		output = input
		return output

	@staticmethod
	def ws_all_markets_withdraws_request(input: WsAllMarketsWithdrawsRequest) -> Any:
		output = input
		return output

	@staticmethod
	def ws_all_markets_withdraws_response(input: Any) -> WsAllMarketsWithdrawsResponse:
		output = input
		return output

	@staticmethod
	def ws_cancel_all_orders_request(input: WsCancelAllOrdersRequest) -> Any:
		output = input
		return output

	@staticmethod
	def ws_cancel_all_orders_response(input: Any) -> WsCancelAllOrdersResponse:
		output = input
		return output

	@staticmethod
	def ws_cancel_order_request(input: WsCancelOrderRequest) -> Any:
		output = input
		return output

	@staticmethod
	def ws_cancel_order_response(input: Any) -> WsCancelOrderResponse:
		output = input
		return output

	@staticmethod
	def ws_cancel_orders_request(input: WsCancelOrdersRequest) -> Any:
		output = input
		return output

	@staticmethod
	def ws_cancel_orders_response(input: Any) -> WsCancelOrdersResponse:
		output = input
		return output

	@staticmethod
	def ws_create_order_request(input: WsCreateOrderRequest) -> Any:
		output = input
		return output

	@staticmethod
	def ws_create_order_response(input: Any) -> WsCreateOrderResponse:
		output = input
		return output

	@staticmethod
	def ws_create_orders_request(input: WsCreateOrdersRequest) -> Any:
		output = input
		return output

	@staticmethod
	def ws_create_orders_response(input: Any) -> WsCreateOrdersResponse:
		output = input
		return output

	@staticmethod
	def ws_market_withdraw_request(input: WsMarketWithdrawRequest) -> Any:
		output = input
		return output

	@staticmethod
	def ws_market_withdraw_response(input: Any) -> WsMarketWithdrawResponse:
		output = input
		return output

	@staticmethod
	def ws_markets_withdraws_request(input: WsMarketsWithdrawsRequest) -> Any:
		output = input
		return output

	@staticmethod
	def ws_markets_withdraws_response(input: Any) -> WsMarketsWithdrawsFundsResponse:
		output = input
		return output

	@staticmethod
	def ws_watch_all_balances_request(input: WsWatchAllBalancesRequest) -> Any:
		output = input
		return output

	@staticmethod
	def ws_watch_all_balances_response(input: Any) -> WsWatchAllBalancesResponse:
		output = input
		return output

	@staticmethod
	def ws_watch_all_filled_orders_request(input: WsWatchAllFilledOrdersRequest) -> Any:
		output = input
		return output

	@staticmethod
	def ws_watch_all_filled_orders_response(input: Any) -> WsWatchAllFilledOrdersResponse:
		output = input
		return output

	@staticmethod
	def ws_watch_all_indicators_request(input: WsWatchAllIndicatorsRequest) -> Any:
		output = input
		return output

	@staticmethod
	def ws_watch_all_indicators_response(input: Any) -> WsWatchAllIndicatorsResponse:
		output = input
		return output

	@staticmethod
	def ws_watch_all_open_orders_request(input: WsWatchAllOpenOrdersRequest) -> Any:
		output = input
		return output

	@staticmethod
	def ws_watch_all_open_orders_response(input: Any) -> WsWatchAllOpenOrdersResponse:
		output = input
		return output

	@staticmethod
	def ws_watch_all_order_books_request(input: WsWatchAllOrderBooksRequest) -> Any:
		output = input
		return output

	@staticmethod
	def ws_watch_all_order_books_response(input: Any) -> WsWatchAllOrderBooksResponse:
		output = input
		return output

	@staticmethod
	def ws_watch_all_orders_request(input: WsWatchAllOrdersRequest) -> Any:
		output = input
		return output

	@staticmethod
	def ws_watch_all_orders_response(input: Any) -> WsWatchAllOrdersResponse:
		output = input
		return output

	@staticmethod
	def ws_watch_all_tickers_request(input: WsWatchAllTickersRequest) -> Any:
		output = input
		return output

	@staticmethod
	def ws_watch_all_tickers_response(input: Any) -> WsWatchAllTickersResponse:
		output = input
		return output

	@staticmethod
	def ws_watch_balance_request(input: WsWatchBalanceRequest) -> Any:
		output = input
		return output

	@staticmethod
	def ws_watch_balance_response(input: Any) -> WsWatchBalanceResponse:
		output = input
		return output

	@staticmethod
	def ws_watch_balances_request(input: WsWatchBalancesRequest) -> Any:
		output = input
		return output

	@staticmethod
	def ws_watch_balances_response(input: Any) -> WsWatchBalancesResponse:
		output = input
		return output

	@staticmethod
	def ws_watch_indicator_request(input: WsWatchIndicatorRequest) -> Any:
		output = input
		return output

	@staticmethod
	def ws_watch_indicator_response(input: Any) -> WsWatchIndicatorResponse:
		output = input
		return output

	@staticmethod
	def ws_watch_indicators_request(input: WsWatchIndicatorsRequest) -> Any:
		output = input
		return output

	@staticmethod
	def ws_watch_indicators_response(input: Any) -> WsWatchIndicatorsResponse:
		output = input
		return output

	@staticmethod
	def ws_watch_order_book_request(input: WsWatchOrderBookRequest) -> Any:
		output = input
		return output

	@staticmethod
	def ws_watch_order_book_response(input: Any) -> WsWatchOrderBookResponse:
		output = input
		return output

	@staticmethod
	def ws_watch_order_books_request(input: WsWatchOrderBooksRequest) -> Any:
		output = input
		return output

	@staticmethod
	def ws_watch_order_books_response(input: Any) -> WsWatchOrderBooksResponse:
		output = input
		return output

	@staticmethod
	def ws_watch_order_request(input: WsWatchOrderRequest) -> Any:
		output = input
		return output

	@staticmethod
	def ws_watch_order_response(input: Any) -> WsWatchOrderResponse:
		output = input
		return output

	@staticmethod
	def ws_watch_orders_request(input: WsWatchOrdersRequest) -> Any:
		output = input
		return output

	@staticmethod
	def ws_watch_orders_response(input: Any) -> WsWatchOrdersResponse:
		output = input
		return output

	@staticmethod
	def ws_watch_ticker_request(input: WsWatchTickerRequest) -> Any:
		output = input
		return output

	@staticmethod
	def ws_watch_ticker_response(input: Any) -> WsWatchTickerResponse:
		output = input
		return output

	@staticmethod
	def ws_watch_tickers_request(input: WsWatchTickersRequest) -> Any:
		output = input
		return output

	@staticmethod
	def ws_watch_tickers_response(input: Any) -> WsWatchTickersResponse:
		output = input
		return output
