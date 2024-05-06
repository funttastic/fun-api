from dotmap import DotMap
from collections import namedtuple
from decimal import Decimal
from typing import Any, List, Dict, Optional, Callable, Tuple, TypeVar, Union
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

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

KujiraOrder = Any
KujiraEvent = Any
KujiraEventAttribute = Any

FunctionType = Callable[..., Any]
AsyncFunctionType = Callable[..., Any]

IList = list
ISet = set
IMap = Dict

BasicKujiraToken = Any
BasicKujiraMarket = Any
KujiraWithdraw = Any

Address = str
OwnerAddress = Address
PayerAddress = Address
Price = Decimal
Amount = Decimal
Fee = Decimal
Percentage = Decimal
Timestamp = int
Block = int
EncryptedWallet = str

ConnectorMarket = Any
ConnectorTicker = Any
ConnectorOrderBook = Any
ConnectorOrder = Any

TokenId = Address
TokenName = str
TokenSymbol = str
TokenDecimals = int

MarketName = str
MarketId = Address
MarketPrecision = int
MarketProgramId = Address
MarketDeprecation = bool
MarketMinimumOrderSize = Decimal
MarketMinimumPriceIncrement = Decimal
MarketMinimumBaseIncrement = Decimal
MarketMinimumQuoteIncrement = Decimal

TickerPrice = Price
TickerTimestamp = Timestamp

TransactionHash = str

OrderId = str
OrderClientId = str
OrderMarketName = MarketName
OrderMarketId = MarketId
OrderMarket = 'Market'
OrderOwnerAddress = OwnerAddress
OrderPayerAddress = PayerAddress
OrderPrice = Price
OrderAmount = Amount
OrderFee = Fee
OrderCreationTimestamp = Timestamp
OrderFillingTimestamp = Timestamp
OrderTransactionHashes = 'TransactionHashes'

FeeMaker = Fee
FeeTaker = Fee
FeeServiceProvider = Fee

EstimatedFeesToken = str
EstimatedFeesPrice = Price
EstimateFeesLimit = Decimal
EstimateFeesCost = Decimal

Mnemonic = str
Password = str
AccountNumber = int

CoinGeckoSymbol = str
CoinGeckoId = str

ChainName = str
ConnectorName = str
NetworkName = str
Latency = int
Leverage = int
Limit = int


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
	LIMIT_MAKER = "LIMIT_MAKER"
	IOC = 'IOC'  # Immediate or Cancel
	POST_ONLY = 'POST_ONLY'


class TickerSource(Enum):
	ORDER_BOOK_SAP = 'orderBookSimpleAveragePrice'
	ORDER_BOOK_WAP = 'orderBookWeightedAveragePrice'
	ORDER_BOOK_VWAP = 'orderBookVolumeWeightedAveragePrice'
	LAST_FILLED_ORDER = 'lastFilledOrder'
	COINGECKO = 'coinGecko'


class ConvertOrderType(Enum):
	GET_ORDERS = 'getOrders'
	PLACE_ORDERS = 'placeOrders'
	CANCELLED_ORDERS = 'cancelledOrders'


class RequestStrategy(Enum):
	RESTful = 'RESTful'
	Controller = 'Controller'


class RESTfulMethod(Enum):
	GET = 'GET'
	POST = 'POST'
	PUT = 'PUT'
	PATCH = 'PATCH'
	DELETE = 'DELETE'


#
# Interfaces and Classes
#

class Withdraw:
	fees: Dict[str, Amount]
	token: 'Token'


class Withdraws:
	hash: TransactionHash
	tokens: IMap[TokenId, Withdraw]
	total: Dict[str, Amount]


class KujiraTicker:
	price: Price


class TokenAmount:
	token: 'Token'
	amount: Amount


class OrderFilling:
	free: TokenAmount
	filled: TokenAmount


class TokenPriceInDolar:
	token: TokenName
	price: Price


class KujiraOrderBookItem:
	quote_price: str
	offer_denom: Dict[str, str]
	total_offer_amount: str


class KujiraOrderBook:
	base: List[KujiraOrderBookItem]
	quote: List[KujiraOrderBookItem]


class Token:
	id: TokenId
	name: TokenName
	symbol: TokenSymbol
	decimals: TokenDecimals
	raw: Any


class Market:
	id: MarketId
	name: MarketName
	baseToken: Token
	quoteToken: Token
	precision: MarketPrecision
	minimumOrderSize: MarketMinimumOrderSize
	minimumPriceIncrement: MarketMinimumPriceIncrement
	minimumBaseAmountIncrement: MarketMinimumBaseIncrement
	minimumQuoteAmountIncrement: MarketMinimumQuoteIncrement
	fees: 'MarketFee'
	programId: MarketProgramId
	deprecated: MarketDeprecation
	raw: Any


class OrderBook:
	market: Market
	bids: IMap[OrderId, 'Order']
	asks: IMap[OrderId, 'Order']
	bestBid: 'Order'
	bestAsk: 'Order'
	raw: Any


class Ticker:
	market: Market
	price: TickerPrice
	timestamp: TickerTimestamp
	tokens: ConnectorTicker


class SimplifiedBalance:
	free: Amount
	lockedInOrders: Amount
	unsettled: Amount
	total: Amount


class SimplifiedBalanceWithUSD(SimplifiedBalance):
	quotation: Amount


class TotalBalance(SimplifiedBalance):
	pass


class TokenBalance(SimplifiedBalance):
	token: Token
	inUSD: SimplifiedBalanceWithUSD


class Balances:
	tokens: IMap[TokenId, TokenBalance]
	total: TotalBalance


class Order:
	id: OrderId
	clientId: OrderClientId
	marketName: OrderMarketName
	marketId: OrderMarketId
	market: OrderMarket
	ownerAddress: OrderOwnerAddress
	payerAddress: OrderPayerAddress
	price: OrderPrice
	amount: OrderAmount
	side: OrderSide
	status: OrderStatus
	type: OrderType
	fee: OrderFee
	filling: OrderFilling
	creationTimestamp: OrderCreationTimestamp
	fillingTimestamp: OrderFillingTimestamp
	hashes: OrderTransactionHashes
	connectorOrder: ConnectorOrder


class TransactionHashes:
	creation: TransactionHash
	cancellation: TransactionHash
	withdraw: TransactionHash
	creations: List[TransactionHash]
	cancellations: List[TransactionHash]
	withdraws: List[TransactionHash]


class MarketFee:
	maker: FeeMaker
	taker: FeeTaker
	serviceProvider: FeeServiceProvider


class EstimatedFees:
	token: EstimatedFeesToken
	price: EstimatedFeesPrice
	limit: EstimateFeesLimit
	cost: EstimateFeesCost


class Transaction:
	hash: TransactionHash
	blockNumber: Block
	gasUsed: int
	gasWanted: int
	code: int
	data: Any


class BasicWallet:
	mnemonic: Mnemonic
	accountNumber: AccountNumber
	publicKey: Address


class KujiraWalletArtifacts:
	publicKey: Address
	accountData: Any
	accountNumber: AccountNumber
	directSecp256k1HdWallet: Any
	signingStargateClient: Any
	signingCosmWasmClient: Any
	finClients: IMap[MarketId, Any]


#
# Errors
#

class CLOBishError(Exception):
	pass


class TokenNotFoundError(CLOBishError):
	pass


class MarketNotFoundError(CLOBishError):
	pass


class BalanceNotFoundError(CLOBishError):
	pass


class OrderBookNotFoundError(CLOBishError):
	pass


class TickerNotFoundError(CLOBishError):
	pass


class OrderNotFoundError(CLOBishError):
	pass


class MarketWithdrawError(CLOBishError):
	pass


class TransactionNotFoundError(CLOBishError):
	pass


class WalletPublicKeyNotFoundError(CLOBishError):
	pass


#
# Main Rest Methods Interfaces
#


class RestGetCurrentBlockRequest:
	pass


class RestGetCurrentBlockResponse:
	pass


class RestGetBlockRequest:
	pass


class RestGetBlockResponse:
	pass


class RestGetBlocksRequest:
	pass


class RestGetBlocksResponse:
	pass


class RestGetTransactionRequest:
	hash: TransactionHash


class RestGetTransactionResponse:
	pass


class RestGetTransactionsRequest:
	hashes: List[TransactionHash]


RestGetTransactionsResponse = IMap[TransactionHash, Transaction]


class RestGetTokenRequest:
	id: TokenId = None
	name: TokenName = None
	symbol: TokenSymbol = None


class RestGetTokenResponse(Token):
	pass


class RestGetTokensRequest:
	ids: List[TokenId] = None
	names: List[TokenName] = None
	symbols: List[TokenSymbol] = None


class RestGetTokensResponse(IMap[TokenId, Token]):
	pass


class RestGetAllTokensRequest:
	pass


class RestGetAllTokensResponse(IMap[TokenId, Token]):
	pass


class RestGetMarketRequest:
	id: MarketId = None
	name: MarketName = None


class RestGetMarketResponse(Market):
	pass


class RestGetMarketsRequest:
	ids: List[MarketId] = None
	names: List[MarketName] = None


class RestGetMarketsResponse(IMap[MarketId, Market]):
	pass


class RestGetAllMarketsRequest(RestGetMarketsRequest):
	pass


class RestGetAllMarketsResponse(IMap[MarketId, Market]):
	pass


class RestGetOrderBookRequest:
	marketId: MarketId = None
	marketName: MarketName = None


class RestGetOrderBookResponse(OrderBook):
	pass


class RestGetOrderBooksRequest:
	marketIds: List[MarketId] = None
	marketNames: List[MarketName] = None


class RestGetOrderBooksResponse(IMap[MarketId, OrderBook]):
	pass


class RestGetAllOrderBooksRequest(RestGetOrderBooksRequest):
	pass


class RestGetAllOrderBooksResponse(IMap[MarketId, OrderBook]):
	pass


class RestGetTickerRequest:
	marketId: MarketId = None
	marketName: MarketName = None


class RestGetTickerResponse(Ticker):
	pass


class RestGetTickersRequest:
	marketIds: List[MarketId] = None
	marketNames: List[MarketName] = None


class RestGetTickersResponse(IMap[MarketId, Ticker]):
	pass


class RestGetAllTickersRequest(RestGetTickersRequest):
	pass


class RestGetAllTickersResponse(IMap[MarketId, Ticker]):
	pass


class RestGetBalanceRequest:
	tokenId: TokenId
	tokenSymbol: TokenSymbol
	ownerAddress: OwnerAddress


class RestGetBalanceResponse(TokenBalance):
	pass


class RestGetBalancesRequest:
	tokenIds: List[TokenId] = None
	tokenSymbols: List[TokenSymbol] = None
	ownerAddress: OwnerAddress


class RestGetBalancesResponse(Balances):
	pass


class RestGetAllBalancesRequest:
	ownerAddress: OwnerAddress


class RestGetAllBalancesResponse(Balances):
	pass


class RestGetOrderRequest:
	id: OrderId
	marketId: MarketId = None
	marketName: MarketName = None
	marketIds: List[MarketId] = None
	marketNames: List[MarketName] = None
	ownerAddress: OrderOwnerAddress
	status: OrderStatus = None
	statuses: List[OrderStatus] = None


class RestGetOrderResponse(Order):
	pass


class RestGetOrdersRequest:
	ids: List[OrderId] = None
	marketId: MarketId = None
	marketName: MarketName = None
	marketIds: List[MarketId] = None
	marketNames: List[MarketName] = None
	ownerAddress: OrderOwnerAddress = None
	ownerAddresses: List[OrderOwnerAddress] = None
	status: OrderStatus = None
	statuses: List[OrderStatus] = None

OrderMap = IMap[OrderId, Order]
OwnerOrderMap = IMap[OwnerAddress, OrderMap]
RestGetOrdersResponse = Union[OrderMap, OwnerOrderMap]

# class RestGetOrdersResponse(Union[IMap[OrderId, Order], IMap[OwnerAddress, IMap[OrderId, Order]]]):
# 	pass


class RestGetAllOpenOrdersRequest:
	pass


class RestGetAllOpenOrdersResponse:
	pass


class RestGetAllFilledOrdersRequest:
	pass


class RestGetAllFilledOrdersResponse:
	pass


class RestGetAllOrdersRequest:
	pass


class RestGetAllOrdersResponse:
	pass


class RestPlaceOrderRequest:
	clientId: OrderClientId = None
	marketId: MarketId = None
	marketName: MarketName = None
	ownerAddress: OrderOwnerAddress = None
	side: OrderSide
	price: OrderPrice
	amount: OrderAmount
	type: OrderType
	payerAddress: OrderPayerAddress = None
	replaceIfExists: bool = None
	waitUntilIncludedInBlock: bool = None


class RestPlaceOrderResponse(Order):
	pass


class RestPlaceOrdersRequest:
	ownerAddress: OrderOwnerAddress = None
	orders: List[RestPlaceOrderRequest]
	waitUntilIncludedInBlock: bool = None
	replaceIfExists: bool = None


class RestPlaceOrdersResponse(IMap[OrderId, Order]):
	pass


class RestReplaceOrderRequest:
	pass


class RestReplaceOrderResponse(Order):
	pass


class RestReplaceOrdersRequest:
	pass


class RestReplaceOrdersResponse(Order):
	pass


class RestCancelOrderRequest:
	id: OrderId
	clientId: OrderClientId = None
	ownerAddress: OrderOwnerAddress
	marketId: MarketId = None
	marketName: MarketName = None


class RestCancelOrderResponse(Order):
	pass


class RestCancelOrdersRequest:
	ids: List[OrderId]
	clientIds: List[OrderClientId] = None
	marketId: MarketId = None
	marketIds: List[MarketId] = None
	marketName: MarketName = None
	marketNames: List[MarketName] = None
	ownerAddress: OrderOwnerAddress = None
	ownerAddresses: List[OrderOwnerAddress] = None


RestCancelOrdersResponse = Union[IMap[OrderId, Order], IMap[OwnerAddress, IMap[OrderId, Order]]]


class RestCancelAllOrdersRequest:
	marketId: MarketId = None
	marketName: MarketName = None
	marketIds: List[MarketId] = None
	marketNames: List[MarketName] = None
	ownerAddress: OrderOwnerAddress = None
	ownerAddresses: List[OrderOwnerAddress] = None


RestCancelAllOrdersResponse = RestCancelOrdersResponse


class RestMarketWithdrawRequest:
	marketId: MarketId = None
	marketName: MarketName = None
	ownerAddress: OrderOwnerAddress = None
	ownerAddresses: List[OrderOwnerAddress] = None


RestMarketWithdrawResponse = Union[Withdraws, IMap[OwnerAddress, Withdraws]]


class RestMarketsWithdrawsRequest:
	marketIds: List[MarketId] = None
	marketNames: List[MarketName] = None
	ownerAddress: OrderOwnerAddress = None
	ownerAddresses: List[OrderOwnerAddress] = None


RestMarketsWithdrawsFundsResponse = Union[IMap[MarketId, Withdraws], IMap[OwnerAddress, IMap[MarketId, Withdraws]]]


class RestAllMarketsWithdrawsRequest(RestMarketsWithdrawsRequest):
	pass


RestAllMarketsWithdrawsResponse = RestMarketsWithdrawsFundsResponse


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

#
# Injective Interfaces
#


@dataclass
class PerpetualMarketInfo:
	hourlyFundingRateCap: str
	hourlyInterestRate: str
	nextFundingTimestamp: int
	fundingInterval: int


@dataclass
class PerpetualMarketFunding:
	cumulativeFunding: str
	cumulativePrice: str
	lastTimestamp: int


@dataclass
class TokenMeta:
	pass


@dataclass
class BaseDerivativeMarket:
	oracleType: str
	marketId: str
	marketStatus: str
	ticker: str
	quoteDenom: str
	makerFeeRate: str
	quoteToken: Optional[TokenMeta]
	takerFeeRate: str
	serviceProviderFee: str
	minPriceTickSize: Optional[Union[int, str]]
	minQuantityTickSize: Optional[Union[int, str]]


@dataclass
class PerpetualMarket(BaseDerivativeMarket):
	initialMarginRatio: str
	maintenanceMarginRatio: str
	isPerpetual: bool
	oracleBase: str
	oracleQuote: str
	oracleScaleFactor: int
	perpetualMarketInfo: Optional[PerpetualMarketInfo] = None
	perpetualMarketFunding: Optional[PerpetualMarketFunding] = None


@dataclass
class PriceLevel:
	price: str
	quantity: str
	timestamp: Timestamp


@dataclass
class Orderbook:
	buys: IMap[str,PriceLevel]
	sells: IMap[str,PriceLevel]


class TradeDirection(Enum):
	Buy = "buy"
	Sell = "sell"
	Long = "long"
	Short = "short"


class TradeExecutionType(Enum):
	Market = "market"
	LimitFill = "limitFill"
	LimitMatchRestingOrder = "limitMatchRestingOrder"
	LimitMatchNewOrder = "limitMatchNewOrder"


class TradeExecutionSide(Enum):
	Maker = "maker"
	Taker = "taker"


@dataclass
class FundingPayment:
	marketId: str
	subaccountId: str
	amount: str
	timestamp: int


@dataclass
class Position:
	marketId: str
	subaccountId: str
	direction: TradeDirection
	quantity: str
	entryPrice: str
	margin: str
	liquidationPrice: str
	markPrice: str
	ticker: str
	aggregateReduceOnlyQuantity: str
	updatedAt: int


@dataclass
class PositionDelta:
	tradeDirection: TradeDirection
	executionPrice: str
	executionQuantity: str
	executionMargin: str


@dataclass
class DerivativeTrade(PositionDelta):
	orderHash: str
	subaccountId: str
	tradeId: str
	marketId: str
	executedAt: int
	tradeExecutionType: TradeExecutionType
	executionSide: TradeExecutionSide
	fee: str
	feeRecipient: str
	isLiquidation: bool
	payout: str


#
# Gateway Common Interfaces
#


@dataclass
class NetworkSelectionRequest:
	chain = ChainName
	network = NetworkName
	connector = ConnectorName

#
# CLOB Interfaces
#


CLOBMarkets = IMap[str, any]


@dataclass
class ClobMarketsRequest(NetworkSelectionRequest):
	market: MarketName = None


@dataclass
class ClobMarketResponse:
	network: NetworkName
	timestamp: Timestamp
	latency: Latency
	markets: CLOBMarkets


ClobTickerRequest = ClobMarketsRequest
ClobTickerResponse = ClobMarketResponse


@dataclass
class ClobOrderbookRequest(ClobMarketsRequest):
	market: MarketName


@dataclass
class ClobOrderbookResponse:
	network: NetworkName
	timestamp: Timestamp
	latency: Latency
	orderbook: Orderbook


class ClobGetOrderRequest(ClobOrderbookRequest):
	address: Address = None
	orderId: OrderId


class ClobGetOrderResponse:
	network: str
	timestamp: int
	latency: int
	orders: List[IMap[str, str]] = []


@dataclass
class CreateOrderParam:
	price: str
	amount: str
	orderType: OrderType
	side: OrderSide
	market: MarketName
	clientOrderID: OrderClientId = None


class ClobPostOrderRequest(NetworkSelectionRequest, CreateOrderParam):
	address: Address


@dataclass
class ClobDeleteOrderRequestExtract:
	market: MarketName
	orderId: OrderId


@dataclass
class ClobBatchUpdateRequest(NetworkSelectionRequest):
	address: Address
	createOrderParams: List[CreateOrderParam] = None
	cancelOrderParams: List[ClobDeleteOrderRequestExtract] = None


@dataclass
class ClobPostOrderResponse:
	network: str
	timestamp: int
	latency: int
	txHash: str
	clientOrderID: Union[str, List[str]] = None


ClobDeleteOrderRequest = ClobGetOrderRequest
ClobDeleteOrderResponse = ClobPostOrderResponse

PerpClobMarketRequest = ClobMarketsRequest

PerpClobMarkets = Dict[str, PerpetualMarket]


@dataclass
class PerpClobMarketResponse:
	network: NetworkName
	timestamp: Timestamp
	latency: Latency
	markets: PerpClobMarkets


PerpClobTickerRequest = PerpClobMarketRequest
PerpClobTickerResponse = PerpClobMarketResponse

PerpClobOrderbookRequest = ClobOrderbookRequest
PerpClobOrderbookResponse = ClobOrderbookResponse


@dataclass
class PerpClobGetOrderRequest(NetworkSelectionRequest):
	market: MarketName
	address: Address
	orderId: OrderId = None
	direction: str = None  # 'buy', 'sell', 'long', 'short'
	orderTypes: str = None  # string like 'buy,sell,stop_buy,stop_sell,take_buy,take_sell,buy_po,sell_po'
	limit: Limit = None  # 1 or greater, otherwise it gets all orders


class PerpClobGetOrderResponse:
	network: NetworkName
	timestamp: Timestamp
	latency: Latency
	orders: List[Dict[str, str]] = []


@dataclass
class CreatePerpOrderParam:
	price: str
	amount: str
	orderType: OrderType
	side: OrderSide
	market: MarketName
	leverage: Leverage


@dataclass
class PerpClobPostOrderRequest(NetworkSelectionRequest, CreatePerpOrderParam):
	address: Address


PerpClobPostOrderResponse = ClobPostOrderResponse


@dataclass
class PerpClobDeleteOrderRequest(NetworkSelectionRequest):
	market: MarketName
	address: Address
	orderId: OrderId


PerpClobDeleteOrderResponse = PerpClobPostOrderResponse


@dataclass
class PerpClobBatchUpdateRequest(NetworkSelectionRequest):
	address: Address
	createOrderParams: List[CreatePerpOrderParam] = None
	cancelOrderParams: List[ClobDeleteOrderRequestExtract] = None


PerpClobBatchUpdateResponse = ClobPostOrderResponse


@dataclass
class PerpClobFundingInfoRequest(NetworkSelectionRequest):
	market: MarketName


@dataclass
class FundingInfo:
	marketId: MarketId
	indexPrice: str
	markPrice: str
	fundingRate: str
	nextFundingTimestamp: Timestamp


@dataclass
class PerpClobFundingInfoResponse:
	network: NetworkName
	timestamp: Timestamp
	latency: Latency
	fundingInfo: FundingInfo


@dataclass
class PerpClobGetLastTradePriceRequest(NetworkSelectionRequest):
	market: str


@dataclass
class PerpClobGetLastTradePriceResponse:
	network: NetworkName
	timestamp: Timestamp
	latency: Latency
	lastTradePrice: str


@dataclass
class PerpClobGetTradesRequest(NetworkSelectionRequest):
	market: MarketName
	address: Address
	orderId: OrderId


@dataclass
class PerpClobGetTradesResponse:
	network: NetworkName
	timestamp: Timestamp
	latency: Latency
	trades: List[DerivativeTrade]


@dataclass
class PerpClobFundingPaymentsRequest(NetworkSelectionRequest):
	address: Address
	market: MarketName


@dataclass
class PerpClobFundingPaymentsResponse:
	network: NetworkName
	timestamp: Timestamp
	latency: Latency
	fundingPayments: List[FundingPayment]


@dataclass
class PerpClobPositionRequest(NetworkSelectionRequest):
	markets: List[MarketName]
	address: Address


@dataclass
class PerpClobPositionResponse:
	network: NetworkName
	timestamp: Timestamp
	latency: Latency
	positions: List[Position]


#
# Extensions
#


class EstimatedGasResponse:
	gasPrice: int
	gasPriceToken: str
	gasLimit: int
	gasCost: int


class LatencyData:
	endpoint: str
	latency: int
	latestBlockTime: Any


#
# Other interfaces
#


class GetRootRequest:
	pass


class GetRootResponse:
	chain: ConnectorName
	network: NetworkName
	connector: ConnectorName
	connection: bool
	timestamp: Timestamp


class GetTokenSymbolsToTokenIdsMapRequest:
	symbols: List[TokenSymbol] = None


class GetTokenSymbolsToTokenIdsMapResponse(IMap[TokenSymbol, TokenId]):
	pass


class GetKujiraTokenSymbolsToCoinGeckoTokenIdsMapResponse(IMap[TokenSymbol, Union[CoinGeckoId, None]]):
	pass


class GetWalletArtifactsRequest:
	ownerAddress: OwnerAddress


class GetWalletArtifactsResponse(KujiraWalletArtifacts):
	pass


class TransferFromToRequest:
	from_: Any
	to: OwnerAddress
	amount: OrderAmount
	tokenId: TokenId = None
	tokenSymbol: TokenSymbol = None


TransferFromToResponse = TransactionHash


class GetWalletPublicKeyRequest:
	mnemonic: Mnemonic
	accountNumber: AccountNumber


GetWalletPublicKeyResponse = Address


class GetWalletsPublicKeysRequest:
	pass


GetWalletsPublicKeysResponse = List[Address]


class EncryptWalletRequest:
	wallet: BasicWallet


EncryptWalletResponse = EncryptedWallet


class DecryptWalletRequest:
	accountAddress: OwnerAddress


DecryptWalletResponse = BasicWallet


RequestWrapper = Union[Any, Any]
