from decimal import Decimal
from dotmap import DotMap as Map
from enum import Enum
from typing import Any, List, Optional, Union, Tuple, Literal
from dataclasses import dataclass
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


TickerId = str  # I created this to identify tickers
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


OrderSide = Literal["buy", "sell"]


#
# Enums
#


class StringEnum(str, Enum):
	def __new__(cls, value, description=''):
		obj = str.__new__(cls, value)
		obj._value_ = value
		obj.description = description
		return obj


class OrderStatus(StringEnum):
	OPEN = 'OPEN'
	CANCELED = 'CANCELED'  # renamed from CANCELLED
	PARTIALLY_FILLED = 'PARTIALLY_FILLED'
	FILLED = 'FILLED'
	CREATION_PENDING = 'CREATION_PENDING'
	CANCELLATION_PENDING = 'CANCELLATION_PENDING'
	UNKNOWN = 'UNKNOWN'
	CLOSED = 'CLOSED' # QUESTION:  added this to replace FILLED, is this accepted?


class OrderType(StringEnum):
	MARKET = "MARKET"
	LIMIT = "LIMIT"
	POST_ONLY = "POST_ONLY", "A limit order which cannot be filled while posting"
	LIMIT_MAKER = "LIMIT_MAKER", "A limit order which can be partially filled (not completely) while posting"
	IMMEDIATE_OR_CANCEL = "IMMEDIATE_OR_CANCEL", "A limit order that must be filled immediately or cancelled"


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
	service_provider: Optional[FeeServiceProvider] = None


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
	fees: MarketFee
	raw: Any
	program_id: Optional[MarketProgramId] = None
	deprecated: Optional[MarketDeprecation] = None


class TokenAndAmount:
	token: Token
	amount: Amount


class OrderFilling:
	free: TokenAndAmount
	filled: TokenAndAmount


class TransactionHashes:
	creation: Optional[TransactionHash]
	cancellation: Optional[TransactionHash]
	withdraw: Optional[TransactionHash]
	creations: Optional[List[TransactionHash]]
	cancellations: Optional[List[TransactionHash]]
	withdraws: Optional[List[TransactionHash]]


@dataclass
class Order:
	id: OrderId
	client_id: OrderClientId
	market_name: OrderMarketName
	market_id: OrderMarketId
	market: Market
	price: OrderPrice
	amount: OrderAmount
	side: OrderSide
	status: OrderStatus
	type: OrderType
	fee: OrderFee
	creation_timestamp: OrderCreationTimestamp
	raw: Any
	filling_timestamp: Optional[OrderFillingTimestamp] = None


class OldOrder:  # REFACTOR: REMOVE THIS
	id: OrderId
	client_id: OrderClientId
	market_name: OrderMarketName
	market_id: OrderMarketId
	market: Market
	#  These four are not available, how can I derive them?
	owner_address: OrderOwnerAddress
	payer_address: OrderPayerAddress
	filling: OrderFilling
	hashes: TransactionHashes
	######################


	price: OrderPrice
	amount: OrderAmount
	side: OrderSide
	status: OrderStatus
	type: OrderType
	fee: OrderFee
	creation_timestamp: OrderCreationTimestamp
	filling_timestamp: OrderFillingTimestamp
	raw: Any


@dataclass
class OrderBook:
	market: Market
	bids: List[Tuple[Price, Amount]]
	asks: List[Tuple[Price, Amount]]
	best_bid: Tuple[Price, Amount]
	best_ask: Tuple[Price, Amount]
	raw: Any


class OldOrderBook:  # The Old OrderBook
	market: Market
	bids: Map[OrderId, 'Order']
	asks: Map[OrderId, 'Order']
	best_bid: 'Order'
	best_ask: Order
	raw: Any


class Ticker(Map):
	symbol: TickerId
	market: Market
	price: TickerPrice  # Question: IS TICKER PRICE NOT (bid + ask)/2
	timestamp: TickerTimestamp
	raw: Any


class BaseBalance:
	free: Amount
	locked_in_orders: Amount
	unsettled: Amount
	total: Amount


class BaseBalanceWithQuotation(BaseBalance):
	quotation: Amount


class TotalBalance(BaseBalance):
	pass


class BaseTokenBalance:
	token: BaseBalance
	usd: BaseBalanceWithQuotation
	native_token: BaseBalanceWithQuotation


class TokenBalance:
	token: Token
	balances: BaseTokenBalance


class Balances:
	tokens: Map[TokenId, TokenBalance]
	total: TotalBalance


class WithdrawItem:
	fees: Map[str, Amount]
	token: 'Token'


class Withdraw:
	hash: TransactionHash
	tokens: Map[TokenId, WithdrawItem]
	total: Map[str, Amount]
	raw: Any


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


class RestGetRootRequest:
	pass


class RestGetRootResponse:
	chain: ChainName
	network: NetworkName
	connector: ConnectorName
	status: ConnectorStatus
	timestamp: Timestamp


class RestGetCurrentBlockRequest:
	pass


class RestGetCurrentBlockResponse:
	number: BlockNumber
	block: Block
	raw: Any


class RestGetBlockRequest:
	number: BlockNumber


class RestGetBlockResponse:
	number: BlockNumber
	block: Block
	raw: Any


class RestGetBlocksRequest:
	numbers: List[BlockNumber]


class RestGetBlocksResponse(Map[BlockNumber, Block]):
	pass


class RestGetTransactionRequest:
	hash: TransactionHash


class RestGetTransactionResponse(Transaction):
	pass


class RestGetTransactionsRequest:
	hashes: List[TransactionHash]


class RestGetTransactionsResponse(Map[TransactionHash, Transaction]):
	pass


@dataclass
class RestGetTokenRequest:
	id: Optional[TokenId] = None
	name: Optional[TokenName] = None
	symbol: Optional[TokenSymbol] = None


class RestGetTokenResponse(Token):
	pass


@dataclass
class RestGetTokensRequest:
	ids: Optional[Tuple[TokenId, ...]] = None
	names: Optional[Tuple[TokenName, ...]] = None
	symbols: Optional[Tuple[TokenSymbol, ...]] = None


@dataclass
class RestGetTokensResponse(Map[TokenId, Token]):
	pass


@dataclass
class RestGetAllTokensRequest:
	pass


class RestGetAllTokensResponse(RestGetTokensResponse):
	pass


@dataclass
class RestGetMarketRequest:
	id: Optional[MarketId] = None
	name: Optional[MarketName] = None


class RestGetMarketResponse(Market):
	pass


@dataclass
class RestGetMarketsRequest:
	ids: Optional[Tuple[MarketId, ...]] = None
	names: Optional[Tuple[MarketName, ...]] = None


class RestGetMarketsResponse(Map[MarketId, Market]):
	pass


class RestGetAllMarketsRequest:
	pass


class RestGetAllMarketsResponse(RestGetMarketsResponse):
	pass


class RestGetOrderBookRequest:
	market_id: Optional[MarketId]
	market_name: Optional[MarketName]


class RestGetOrderBookResponse(OrderBook):
	pass


class RestGetOrderBooksRequest:
	market_ids: Optional[List[MarketId]]
	market_names: Optional[List[MarketName]]


class RestGetOrderBooksResponse(Map[MarketId, OrderBook]):
	pass


class RestGetAllOrderBooksRequest:
	pass


class RestGetAllOrderBooksResponse(Map[MarketId, OrderBook]):
	pass


@dataclass
class RestGetTickerRequest:
	market_id: Optional[MarketId] = None
	market_name: Optional[MarketName] = None


# class RestGetTickerRequest(Map):
#
#   def __setattr__(self, key, value):
#      __allowed_keys = {'market_id', 'market_name'}
#      if key not in __allowed_keys:
#         raise AttributeError(f"'RestGetTickerRequest' object only allows attributes: {', '.join(__allowed_keys)}")
#      super().__setattr__(key, value)


class RestGetTickerResponse(Ticker): pass


@dataclass
class RestGetTickersRequest:
	market_ids: Optional[Tuple[MarketId, ...]] = None
	market_names: Optional[Tuple[MarketName, ...]] = None


class RestGetTickersResponse(Map[MarketId, Ticker]):
	pass


class RestGetAllTickersRequest:
	pass


class RestGetAllTickersResponse(RestGetTickersResponse):
	pass


class RestAddWalletRequest:
	mnemonic: Mnemonic
	account_number: Optional[AccountNumber]


RestAddWalletResponse = Address


class RestGetBalanceRequest:
	token_id: Optional[TokenId]
	token_symbol: Optional[TokenSymbol]
	owner_address: OwnerAddress


class RestGetBalanceResponse(TokenBalance):
	pass


class RestGetBalancesRequest:
	token_ids: Optional[List[TokenId]]
	token_symbols: Optional[List[TokenSymbol]]
	owner_address: OwnerAddress


class RestGetBalancesResponse(Balances):
	pass


class RestGetAllBalancesRequest:
	owner_address: OwnerAddress


class RestGetAllBalancesResponse(RestGetBalancesResponse):
	pass


class RestGetOrderRequest:
	id: OrderId
	market_id: Optional[MarketId]
	market_name: Optional[MarketName]
	owner_address: Optional[OrderOwnerAddress]
	status: Optional[OrderStatus]


class RestGetOrderResponse(Order):
	pass


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


class RestGetAllOpenOrdersRequest:
	pass


RestGetAllOpenOrdersResponse = RestGetOrdersResponse


class RestGetAllFilledOrdersRequest:
	pass


RestGetAllFilledOrdersResponse = RestGetOrdersResponse


class RestGetAllOrdersRequest:
	pass


RestGetAllOrdersResponse = RestGetOrdersResponse


@dataclass
class RestPlaceOrderRequest:
	order_side: OrderSide
	order_type: OrderType
	order_price: OrderPrice
	order_amount: OrderAmount
	market_id: Optional[MarketId] = None
	market_name: Optional[MarketName] = None


class OldRestPlaceOrderRequest:  # REFACTOR: REMOVE THIS
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
	wait_until_included_in_block: Optional[bool]  # SHOULD THIS BE REMOVED


class RestPlaceOrderResponse(Order):
	pass


@dataclass
class RestPlaceOrdersRequest:
	orders: List[RestPlaceOrderRequest]


class OldRestPlaceOrdersRequest:
	owner_address: Optional[OrderOwnerAddress]
	orders: List[RestPlaceOrderRequest]
	replace_if_exists: Optional[bool]
	wait_until_included_in_block: Optional[bool]


class RestPlaceOrdersResponse(Map[OrderId, Order]):
	pass


class RestReplaceOrderRequest(RestPlaceOrderRequest):
	id: OrderId


class RestReplaceOrderResponse(Order):
	pass


class RestReplaceOrdersRequest:
	owner_address: Optional[OrderOwnerAddress]
	orders: List[RestReplaceOrderRequest]


class RestReplaceOrdersResponse(Map[OrderId, Order]):
	pass


class RestCancelOrderRequest:
	id: OrderId
	market_id: Optional[MarketId] = None
	market_name: Optional[MarketName] = None


class RestCancelOrderResponse(Order):
	pass


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


class RestCancelAllOrdersRequest:
	market_id: Optional[MarketId]
	market_name: Optional[MarketName]
	market_ids: Optional[List[MarketId]]
	market_names: Optional[List[MarketName]]
	owner_address: Optional[OrderOwnerAddress]
	owner_addresses: Optional[List[OrderOwnerAddress]]


RestCancelAllOrdersResponse = RestCancelOrdersResponse


class RestMarketWithdrawRequest:
	market_id: Optional[MarketId]
	market_name: Optional[MarketName]
	owner_address: Optional[OrderOwnerAddress]
	owner_addresses: Optional[List[OrderOwnerAddress]]


RestMarketWithdrawResponse = Union[Map[MarketId, Withdraw], Map[OwnerAddress, Withdraw]]


class RestMarketsWithdrawsRequest:
	market_ids: Optional[List[MarketId]]
	market_names: Optional[List[MarketName]]
	owner_address: Optional[OrderOwnerAddress]
	owner_addresses: Optional[List[OrderOwnerAddress]]


RestMarketsWithdrawsResponse = Union[Map[MarketId, Withdraw], Map[OwnerAddress, Map[MarketId, Withdraw]]]


class RestAllMarketsWithdrawsRequest:
	pass


RestAllMarketsWithdrawsResponse = RestMarketsWithdrawsResponse


class RestGetEstimatedFeesRequest:
	pass


class RestGetEstimatedFeesResponse(EstimatedFees):
	pass


#
# Main WebSocket Methods Interfaces
#

class WsWatchOrderBookRequest:
	pass


class WsWatchOrderBookResponse:
	pass


class WsWatchOrderBooksRequest:
	pass


class WsWatchOrderBooksResponse:
	pass


class WsWatchAllOrderBooksRequest:
	pass


class WsWatchAllOrderBooksResponse:
	pass


class WsWatchTickerRequest:
	pass


class WsWatchTickerResponse:
	pass


class WsWatchTickersRequest:
	pass


class WsWatchTickersResponse:
	pass


class WsWatchAllTickersRequest:
	pass


class WsWatchAllTickersResponse:
	pass


class WsWatchBalanceRequest:
	pass


class WsWatchBalanceResponse:
	pass


class WsWatchBalancesRequest:
	pass


class WsWatchBalancesResponse:
	pass


class WsWatchAllBalancesRequest:
	pass


class WsWatchAllBalancesResponse:
	pass


class WsWatchOrderRequest:
	pass


class WsWatchOrderResponse:
	pass


class WsWatchOrdersRequest:
	pass


class WsWatchOrdersResponse:
	pass


class WsWatchAllOpenOrdersRequest:
	pass


class WsWatchAllOpenOrdersResponse:
	pass


class WsWatchAllFilledOrdersRequest:
	pass


class WsWatchAllFilledOrdersResponse:
	pass


class WsWatchAllOrdersRequest:
	pass


class WsWatchAllOrdersResponse:
	pass


class WsCreateOrderRequest:
	pass


class WsCreateOrderResponse:
	pass


class WsCreateOrdersRequest:
	pass


class WsCreateOrdersResponse:
	pass


class WsCancelOrderRequest:
	pass


class WsCancelOrderResponse:
	pass


class WsCancelOrdersRequest:
	pass


class WsCancelOrdersResponse:
	pass


class WsCancelAllOrdersRequest:
	pass


class WsCancelAllOrdersResponse:
	pass


class WsWatchIndicatorRequest:
	pass


class WsWatchIndicatorResponse:
	pass


class WsWatchIndicatorsRequest:
	pass


class WsWatchIndicatorsResponse:
	pass


class WsWatchAllIndicatorsRequest:
	pass


class WsWatchAllIndicatorsResponse:
	pass


class WsMarketWithdrawRequest:
	pass


class WsMarketWithdrawResponse:
	pass


class WsMarketsWithdrawsRequest:
	pass


class WsMarketsWithdrawsFundsResponse:
	pass


class WsAllMarketsWithdrawsRequest:
	pass


class WsAllMarketsWithdrawsResponse:
	pass



