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


@ThreadSafeSingleton
class CCXTConvertors(object):

	@staticmethod
	def rest_get_all_markets_request(input: RestGetAllMarketsRequest) -> CCXTRestGetAllMarketsRequest:
		output = input

		return output

	@staticmethod
	def rest_get_all_markets_response(input: CCXTRestGetAllMarketsResponse) -> RestGetAllMarketsResponse:
		output = input

		return output
