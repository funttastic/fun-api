from dataclasses import dataclass

from decimal import Decimal
from dotmap import DotMap as Map
from enum import Enum
from typing import Any, List, Optional, Union

from hummingbot.strategies.pure_market_making.v_2_0_0.workers.ccxt.ccxt import CCXTWorker
from hummingbot.strategies.pure_market_making.v_2_0_0.workers.hb_client.hb_client import HBClientWorker
from hummingbot.strategies.pure_market_making.v_2_0_0.workers.hb_gateway.clob import HBGatewayCLOBWorker
from hummingbot.strategies.pure_market_making.v_2_0_0.workers.hb_gateway.kujira import HBGatewayKujiraWorker


class WorkerType(Enum):
	CCXT = ("ccxt", "CCXT", "CCXT.", CCXTWorker)
	HBGatewayCLOB = ("hb-gateway.clob", "Hummingbot Gateway - CLOB", "Hummingbot Gateway - CLOB.", HBGatewayCLOBWorker)
	HBGatewayKujira = ("hb-gateway.kujira", "Hummingbot Gateway - Kujira", "Hummingbot Gateway - Kujira.", HBGatewayKujiraWorker)
	HBClient = ("hb-client", "Hummingbot Client", "Hummingbot Client.", HBClientWorker)

	def __init__(self, id: str, title: str, description: str, class_: Any):
		self.id = id
		self.title = title
		self.description = description
		self.class_ = class_

	@staticmethod
	def get_by_id(id_: str):
		for item in WorkerType:
			if item.id == id_:
				return item

		raise ValueError(f"""Worker type with id "{id_}" not found.""")

#
# Types and Constants
#

Address = str
OwnerAddress = Address
PayerAddress = Address
Price = Decimal
Amount = Decimal
Fee = Decimal
Percentage = Decimal
Timestamp = int
Mnemonic = str
Password = str
AccountNumber = int

BlockNumber = int

TransactionHash = str

TokenId = Address
TokenName = str
TokenSymbol = str
TokenDecimals = int

MarketId = Address
MarketName = str
MarketPrecision = int
MarketProgramId = Address
MarketDeprecation = bool
MarketMinimumOrderSize = Decimal
MarketMinimumPriceIncrement = Decimal
MarketMinimumBaseIncrement = Decimal
MarketMinimumQuoteIncrement = Decimal

TickerPrice = Price
TickerTimestamp = Timestamp

OrderId = str
OrderClientId = str
OrderMarketName = MarketName
OrderMarketId = MarketId
OrderOwnerAddress = OwnerAddress
OrderPayerAddress = PayerAddress
OrderPrice = Price
OrderAmount = Amount
OrderFee = Fee
OrderCreationTimestamp = Timestamp
OrderFillingTimestamp = Timestamp

FeeMaker = Fee
FeeTaker = Fee
FeeServiceProvider = Fee

EstimatedFeesToken = str
EstimatedFeesPrice = Price
EstimateFeesLimit = Decimal
EstimateFeesCost = Decimal

ChainName = str
NetworkName = str
ConnectorName = str
ConnectorStatus = str


#
# Enums
#

class OrderSide(Enum):
	BUY = 'BUY'
	SELL = 'SELL'


class OrderStatus(Enum):
	OPEN = 'OPEN'
	CANCELLED = 'CANCELLED'
	PARTIALLY_FILLED = 'PARTIALLY_FILLED'
	FILLED = 'FILLED'
	CREATION_PENDING = 'CREATION_PENDING'
	CANCELLATION_PENDING = 'CANCELLATION_PENDING'
	UNKNOWN = 'UNKNOWN'


class OrderType(Enum):
	MARKET = 'MARKET'
	LIMIT = 'LIMIT'
	POST_ONLY = 'POST_ONLY'  # A limit order which cannot be filled while posting
	LIMIT_MAKER = "LIMIT_MAKER"  # A limit order which can be partially filled (not completely) while posting
	IMMEDIATE_OR_CANCEL = 'IMMEDIATE_OR_CANCEL'  # A limit order that must be filled immediately or cancelled


class TickerSource(Enum):
	ORDER_BOOK_SAP = 'ORDER_BOOK_SIMPLE_AVERAGE_PRICE'
	ORDER_BOOK_WAP = 'ORDER_BOOK_WEIGHTED_AVERAGE_PRICE'
	ORDER_BOOK_VWAP = 'ORDER_BOOK_VOLUME_WEIGHTED_AVERAGE_PRICE'
	LAST_FILLED_ORDER = 'LAST_FILLED_ORDER'
	EXTERNAL_API = 'EXTERNAL_API'


class RESTfulMethod(Enum):
	GET = 'GET'
	POST = 'POST'
	PUT = 'PUT'
	PATCH = 'PATCH'
	DELETE = 'DELETE'
	HEAD = 'HEAD'
	OPTIONS = 'OPTIONS'


#
# Interfaces and Classes
#

Block = Map[str, Any]


@dataclass
class Transaction:
	hash: TransactionHash
	block_number: BlockNumber
	block: Block
	gas_used: int
	gas_wanted: int
	code: int
	data: Any
	raw: Any


@dataclass
class Token:
	id: TokenId
	name: TokenName
	symbol: TokenSymbol
	decimals: TokenDecimals
	raw: Any


@dataclass
class MarketFee:
	maker: FeeMaker
	taker: FeeTaker
	service_provider: FeeServiceProvider


@dataclass
class Market:
	id: MarketId
	name: MarketName
	base_token: Token
	quote_token: Token
	precision: MarketPrecision
	minimum_order_size: MarketMinimumOrderSize
	minimum_price_increment: MarketMinimumPriceIncrement
	minimum_base_amount_increment: MarketMinimumBaseIncrement
	minimum_quote_amount_increment: MarketMinimumQuoteIncrement
	fees: 'MarketFee'
	program_id: MarketProgramId
	deprecated: MarketDeprecation
	raw: Any


@dataclass
class OrderBook:
	market: Market
	bids: Map[OrderId, 'Order']
	asks: Map[OrderId, 'Order']
	best_bid: 'Order'
	best_ask: 'Order'
	raw: Any


@dataclass
class Ticker:
	market: Market
	price: TickerPrice
	timestamp: TickerTimestamp
	raw: Any


@dataclass
class TokenAndAmount:
	token: 'Token'
	amount: Amount


@dataclass
class OrderFilling:
	free: TokenAndAmount
	filled: TokenAndAmount


@dataclass
class BaseBalance:
	free: Amount
	locked_in_orders: Amount
	unsettled: Amount
	total: Amount


@dataclass
class BaseBalanceWithQuotation(BaseBalance):
	quotation: Amount


@dataclass
class TotalBalance(BaseBalance):
	pass


@dataclass
class BaseTokenBalance:
	token: BaseBalance
	usd: BaseBalanceWithQuotation
	native_token: BaseBalanceWithQuotation


@dataclass
class TokenBalance:
	token: Token
	balances: BaseTokenBalance


@dataclass
class Balances:
	tokens: Map[TokenId, TokenBalance]
	total: TotalBalance


@dataclass
class Order:
	id: OrderId
	client_id: OrderClientId
	market_name: OrderMarketName
	market_id: OrderMarketId
	market: Market
	owner_address: OrderOwnerAddress
	payer_address: OrderPayerAddress
	price: OrderPrice
	amount: OrderAmount
	side: OrderSide
	status: OrderStatus
	type: OrderType
	fee: OrderFee
	filling: OrderFilling
	creation_timestamp: OrderCreationTimestamp
	filling_timestamp: OrderFillingTimestamp
	hashes: 'TransactionHashes'
	raw: Any


@dataclass
class TransactionHashes:
	creation: Optional[TransactionHash]
	cancellation: Optional[TransactionHash]
	withdraw: Optional[TransactionHash]
	creations: Optional[List[TransactionHash]]
	cancellations: Optional[List[TransactionHash]]
	withdraws: Optional[List[TransactionHash]]


@dataclass
class WithdrawItem:
	fees: Map[str, Amount]
	token: 'Token'


@dataclass
class Withdraw:
	hash: TransactionHash
	tokens: Map[TokenId, WithdrawItem]
	total: Map[str, Amount]
	raw: Any


@dataclass
class EstimatedFees:
	token: EstimatedFeesToken
	price: EstimatedFeesPrice
	limit: EstimateFeesLimit
	cost: EstimateFeesCost


#
# Errors
#

class BaseError(Exception):
	pass


class TransactionNotFoundError(BaseError):
	pass


class TokenNotFoundError(BaseError):
	pass


class MarketNotFoundError(BaseError):
	pass


class OrderBookNotFoundError(BaseError):
	pass


class TickerNotFoundError(BaseError):
	pass


class BalanceNotFoundError(BaseError):
	pass


class OrderNotFoundError(BaseError):
	pass


class WithdrawError(BaseError):
	pass


#
# Main Rest Methods Interfaces
#

@dataclass
class RestGetRootRequest:
	pass


@dataclass
class RestGetRootResponse:
	chain: ChainName
	network: NetworkName
	connector: ConnectorName
	status: ConnectorStatus
	timestamp: Timestamp


@dataclass
class RestGetCurrentBlockRequest:
	pass


@dataclass
class RestGetCurrentBlockResponse:
	number: BlockNumber
	block: Block
	raw: Any


@dataclass
class RestGetBlockRequest:
	number: BlockNumber


@dataclass
class RestGetBlockResponse:
	number: BlockNumber
	block: Block
	raw: Any


@dataclass
class RestGetBlocksRequest:
	numbers: List[BlockNumber]


@dataclass
class RestGetBlocksResponse(Map[BlockNumber, Block]):
	pass


@dataclass
class RestGetTransactionRequest:
	hash: TransactionHash


@dataclass
class RestGetTransactionResponse(Transaction):
	pass


@dataclass
class RestGetTransactionsRequest:
	hashes: List[TransactionHash]


@dataclass
class RestGetTransactionsResponse(Map[TransactionHash, Transaction]):
	pass


@dataclass
class RestGetTokenRequest:
	id: Optional[TokenId]
	name: Optional[TokenName]
	symbol: Optional[TokenSymbol]


@dataclass
class RestGetTokenResponse(Token):
	pass


@dataclass
class RestGetTokensRequest:
	ids: Optional[List[TokenId]]
	names: Optional[List[TokenName]]
	symbols: Optional[List[TokenSymbol]]


@dataclass
class RestGetTokensResponse(Map[TokenId, Token]):
	pass


@dataclass
class RestGetAllTokensRequest:
	pass


@dataclass
class RestGetAllTokensResponse(RestGetTokensResponse):
	pass


@dataclass
class RestGetMarketRequest:
	id: Optional[MarketId]
	name: Optional[MarketName]


@dataclass
class RestGetMarketResponse(Market):
	pass


@dataclass
class RestGetMarketsRequest:
	ids: Optional[List[MarketId]]
	names: Optional[List[MarketName]]


@dataclass
class RestGetMarketsResponse(Map[MarketId, Market]):
	pass


@dataclass
class RestGetAllMarketsRequest:
	pass


@dataclass
class RestGetAllMarketsResponse(RestGetMarketsResponse):
	pass


@dataclass
class RestGetOrderBookRequest:
	market_id: Optional[MarketId]
	market_name: Optional[MarketName]


@dataclass
class RestGetOrderBookResponse(OrderBook):
	pass


@dataclass
class RestGetOrderBooksRequest:
	market_ids: Optional[List[MarketId]]
	market_names: Optional[List[MarketName]]


@dataclass
class RestGetOrderBooksResponse(Map[MarketId, OrderBook]):
	pass


@dataclass
class RestGetAllOrderBooksRequest:
	pass


@dataclass
class RestGetAllOrderBooksResponse(Map[MarketId, OrderBook]):
	pass


@dataclass
class RestGetTickerRequest:
	market_id: Optional[MarketId]
	market_name: Optional[MarketName]


@dataclass
class RestGetTickerResponse(Ticker):
	pass


@dataclass
class RestGetTickersRequest:
	market_ids: Optional[List[MarketId]]
	market_names: Optional[List[MarketName]]


@dataclass
class RestGetTickersResponse(Map[MarketId, Ticker]):
	pass


@dataclass
class RestGetAllTickersRequest:
	pass


@dataclass
class RestGetAllTickersResponse(RestGetTickersResponse):
	pass


@dataclass
class RestAddWalletRequest:
	mnemonic: Mnemonic
	account_number: Optional[AccountNumber]


RestAddWalletResponse = Address


@dataclass
class RestGetBalanceRequest:
	token_id: Optional[TokenId]
	token_symbol: Optional[TokenSymbol]
	owner_address: OwnerAddress


@dataclass
class RestGetBalanceResponse(TokenBalance):
	pass


@dataclass
class RestGetBalancesRequest:
	token_ids: Optional[List[TokenId]]
	token_symbols: Optional[List[TokenSymbol]]
	owner_address: OwnerAddress


@dataclass
class RestGetBalancesResponse(Balances):
	pass


@dataclass
class RestGetAllBalancesRequest:
	owner_address: OwnerAddress


@dataclass
class RestGetAllBalancesResponse(RestGetBalancesResponse):
	pass


@dataclass
class RestGetOrderRequest:
	id: OrderId
	market_id: Optional[MarketId]
	market_name: Optional[MarketName]
	owner_address: Optional[OrderOwnerAddress]
	status: Optional[OrderStatus]


@dataclass
class RestGetOrderResponse(Order):
	pass


@dataclass
class RestGetOrdersRequest:
	ids: Optional[List[OrderId]]
	market_id: Optional[MarketId]
	market_ids: Optional[List[MarketId]]
	market_name: Optional[MarketName]
	market_names: Optional[List[MarketName]]
	owner_address: Optional[OrderOwnerAddress]
	owner_addresses: Optional[List[OrderOwnerAddress]]
	status: Optional[OrderStatus]
	statuses: Optional[List[OrderStatus]]


RestGetOrdersResponse = Union[Map[OrderId, Order], Map[OwnerAddress, Map[OrderId, Order]]]


@dataclass
class RestGetAllOpenOrdersRequest:
	pass


RestGetAllOpenOrdersResponse = RestGetOrdersResponse


@dataclass
class RestGetAllFilledOrdersRequest:
	pass


RestGetAllFilledOrdersResponse = RestGetOrdersResponse


@dataclass
class RestGetAllOrdersRequest:
	pass


RestGetAllOrdersResponse = RestGetOrdersResponse


@dataclass
class RestPlaceOrderRequest:
	client_id: Optional[OrderClientId]
	market_id: Optional[MarketId]
	market_name: Optional[MarketName]
	owner_address: Optional[OrderOwnerAddress]
	payer_address: Optional[OrderPayerAddress]
	side: OrderSide
	price: OrderPrice
	amount: OrderAmount
	type: OrderType
	replace_if_exists: Optional[bool]
	wait_until_included_in_block: Optional[bool]


@dataclass
class RestPlaceOrderResponse(Order):
	pass


@dataclass
class RestPlaceOrdersRequest:
	owner_address: Optional[OrderOwnerAddress]
	orders: List[RestPlaceOrderRequest]
	replace_if_exists: Optional[bool]
	wait_until_included_in_block: Optional[bool]


@dataclass
class RestPlaceOrdersResponse(Map[OrderId, Order]):
	pass


@dataclass
class RestReplaceOrderRequest(RestPlaceOrderRequest):
	id: OrderId


@dataclass
class RestReplaceOrderResponse(Order):
	pass


@dataclass
class RestReplaceOrdersRequest:
	owner_address: Optional[OrderOwnerAddress]
	orders: List[RestReplaceOrderRequest]


@dataclass
class RestReplaceOrdersResponse(Map[OrderId, Order]):
	pass


@dataclass
class RestCancelOrderRequest:
	id: Optional[OrderId]
	client_id: Optional[OrderClientId]
	owner_address: OrderOwnerAddress
	market_id: Optional[MarketId]
	market_name: Optional[MarketName]


@dataclass
class RestCancelOrderResponse(Order):
	pass


@dataclass
class RestCancelOrdersRequest:
	ids: List[OrderId]
	client_ids: Optional[List[OrderClientId]]
	market_id: Optional[MarketId]
	market_ids: Optional[List[MarketId]]
	market_name: Optional[MarketName]
	market_names: Optional[List[MarketName]]
	owner_address: Optional[OrderOwnerAddress]
	owner_addresses: Optional[List[OrderOwnerAddress]]


RestCancelOrdersResponse = Union[Map[OrderId, Order], Map[OwnerAddress, Map[OrderId, Order]]]


@dataclass
class RestCancelAllOrdersRequest:
	market_id: Optional[MarketId]
	market_name: Optional[MarketName]
	market_ids: Optional[List[MarketId]]
	market_names: Optional[List[MarketName]]
	owner_address: Optional[OrderOwnerAddress]
	owner_addresses: Optional[List[OrderOwnerAddress]]


RestCancelAllOrdersResponse = RestCancelOrdersResponse


@dataclass
class RestMarketWithdrawRequest:
	market_id: Optional[MarketId]
	market_name: Optional[MarketName]
	owner_address: Optional[OrderOwnerAddress]
	owner_addresses: Optional[List[OrderOwnerAddress]]


RestMarketWithdrawResponse = Union[Map[MarketId, Withdraw], Map[OwnerAddress, Withdraw]]


@dataclass
class RestMarketsWithdrawsRequest:
	market_ids: Optional[List[MarketId]]
	market_names: Optional[List[MarketName]]
	owner_address: Optional[OrderOwnerAddress]
	owner_addresses: Optional[List[OrderOwnerAddress]]


RestMarketsWithdrawsResponse = Union[Map[MarketId, Withdraw], Map[OwnerAddress, Map[MarketId, Withdraw]]]


@dataclass
class RestAllMarketsWithdrawsRequest:
	pass


RestAllMarketsWithdrawsResponse = RestMarketsWithdrawsResponse


@dataclass
class RestGetEstimatedFeesRequest:
	pass


@dataclass
class RestGetEstimatedFeesResponse(EstimatedFees):
	pass


#
# Main WebSocket Methods Interfaces
#


@dataclass
class WsWatchOrderBookRequest:
	pass


@dataclass
class WsWatchOrderBookResponse:
	pass


@dataclass
class WsWatchOrderBooksRequest:
	pass


@dataclass
class WsWatchOrderBooksResponse:
	pass


@dataclass
class WsWatchAllOrderBooksRequest:
	pass


@dataclass
class WsWatchAllOrderBooksResponse:
	pass


@dataclass
class WsWatchTickerRequest:
	pass


@dataclass
class WsWatchTickerResponse:
	pass


@dataclass
class WsWatchTickersRequest:
	pass


@dataclass
class WsWatchTickersResponse:
	pass


@dataclass
class WsWatchAllTickersRequest:
	pass


@dataclass
class WsWatchAllTickersResponse:
	pass


@dataclass
class WsWatchBalanceRequest:
	pass


@dataclass
class WsWatchBalanceResponse:
	pass


@dataclass
class WsWatchBalancesRequest:
	pass


@dataclass
class WsWatchBalancesResponse:
	pass


@dataclass
class WsWatchAllBalancesRequest:
	pass


@dataclass
class WsWatchAllBalancesResponse:
	pass


@dataclass
class WsWatchOrderRequest:
	pass


@dataclass
class WsWatchOrderResponse:
	pass


@dataclass
class WsWatchOrdersRequest:
	pass


@dataclass
class WsWatchOrdersResponse:
	pass


@dataclass
class WsWatchAllOpenOrdersRequest:
	pass


@dataclass
class WsWatchAllOpenOrdersResponse:
	pass


@dataclass
class WsWatchAllFilledOrdersRequest:
	pass


@dataclass
class WsWatchAllFilledOrdersResponse:
	pass


@dataclass
class WsWatchAllOrdersRequest:
	pass


@dataclass
class WsWatchAllOrdersResponse:
	pass


@dataclass
class WsCreateOrderRequest:
	pass


@dataclass
class WsCreateOrderResponse:
	pass


@dataclass
class WsCreateOrdersRequest:
	pass


@dataclass
class WsCreateOrdersResponse:
	pass


@dataclass
class WsCancelOrderRequest:
	pass


@dataclass
class WsCancelOrderResponse:
	pass


@dataclass
class WsCancelOrdersRequest:
	pass


@dataclass
class WsCancelOrdersResponse:
	pass


@dataclass
class WsCancelAllOrdersRequest:
	pass


@dataclass
class WsCancelAllOrdersResponse:
	pass


@dataclass
class WsWatchIndicatorRequest:
	pass


@dataclass
class WsWatchIndicatorResponse:
	pass


@dataclass
class WsWatchIndicatorsRequest:
	pass


@dataclass
class WsWatchIndicatorsResponse:
	pass


@dataclass
class WsWatchAllIndicatorsRequest:
	pass


@dataclass
class WsWatchAllIndicatorsResponse:
	pass


@dataclass
class WsMarketWithdrawRequest:
	pass


@dataclass
class WsMarketWithdrawResponse:
	pass


@dataclass
class WsMarketsWithdrawsRequest:
	pass


@dataclass
class WsMarketsWithdrawsFundsResponse:
	pass


@dataclass
class WsAllMarketsWithdrawsRequest:
	pass


@dataclass
class WsAllMarketsWithdrawsResponse:
	pass
