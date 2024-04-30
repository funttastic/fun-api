from dotmap import DotMap
from collections import namedtuple
from decimal import Decimal
from typing import Any, List, Optional
from enum import Enum

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


from dotmap import DotMap
from enum import Enum
from decimal import Decimal
from typing import Any, Callable, Dict, List, Tuple, TypeVar, Union

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
	connectorMarket: ConnectorMarket

class OrderBook:
	market: Market
	bids: IMap[OrderId, 'Order']
	asks: IMap[OrderId, 'Order']
	bestBid: 'Order'
	bestAsk: 'Order'
	connectorOrderBook: ConnectorOrderBook

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
# Main methods options
#

class GetRootRequest:
	pass

class GetRootResponse:
	chain: str
	network: str
	connector: str
	connection: bool
	timestamp: Timestamp

class GetTokenRequest:
	id: TokenId = None
	name: TokenName = None
	symbol: TokenSymbol = None

class GetTokenResponse(Token):
	pass

class GetTokensRequest:
	ids: List[TokenId] = None
	names: List[TokenName] = None
	symbols: List[TokenSymbol] = None

class GetTokensResponse(IMap[TokenId, Token]):
	pass

class GetAllTokensRequest:
	pass

class GetAllTokensResponse(IMap[TokenId, Token]):
	pass

class GetTokenSymbolsToTokenIdsMapRequest:
	symbols: List[TokenSymbol] = None

class GetTokenSymbolsToTokenIdsMapResponse(IMap[TokenSymbol, TokenId]):
	pass

class GetKujiraTokenSymbolsToCoinGeckoTokenIdsMapResponse(IMap[TokenSymbol, Union[CoinGeckoId, None]]):
	pass

class GetMarketRequest:
	id: MarketId = None
	name: MarketName = None

class GetMarketResponse(Market):
	pass

class GetMarketsRequest:
	ids: List[MarketId] = None
	names: List[MarketName] = None

class GetMarketsResponse(IMap[MarketId, Market]):
	pass

class GetAllMarketsRequest(GetMarketsRequest):
	pass

class GetAllMarketsResponse(IMap[MarketId, Market]):
	pass

class GetOrderBookRequest:
	marketId: MarketId = None
	marketName: MarketName = None

class GetOrderBookResponse(OrderBook):
	pass

class GetOrderBooksRequest:
	marketIds: List[MarketId] = None
	marketNames: List[MarketName] = None

class GetOrderBooksResponse(IMap[MarketId, OrderBook]):
	pass

class GetAllOrderBooksRequest(GetOrderBooksRequest):
	pass

class GetAllOrderBooksResponse(IMap[MarketId, OrderBook]):
	pass

class GetTickerRequest:
	marketId: MarketId = None
	marketName: MarketName = None

class GetTickerResponse(Ticker):
	pass

class GetTickersRequest:
	marketIds: List[MarketId] = None
	marketNames: List[MarketName] = None

class GetTickersResponse(IMap[MarketId, Ticker]):
	pass

class GetAllTickersRequest(GetTickersRequest):
	pass

class GetAllTickersResponse(IMap[MarketId, Ticker]):
	pass

class GetWalletArtifactsRequest:
	ownerAddress: OwnerAddress

class GetWalletArtifactsResponse(KujiraWalletArtifacts):
	pass

class GetBalanceRequest:
	tokenId: TokenId
	tokenSymbol: TokenSymbol
	ownerAddress: OwnerAddress

class GetBalanceResponse(TokenBalance):
	pass

class GetBalancesRequest:
	tokenIds: List[TokenId] = None
	tokenSymbols: List[TokenSymbol] = None
	ownerAddress: OwnerAddress

class GetBalancesResponse(Balances):
	pass

class GetAllBalancesRequest:
	ownerAddress: OwnerAddress

class GetAllBalancesResponse(Balances):
	pass

class GetOrderRequest:
	id: OrderId
	marketId: MarketId = None
	marketName: MarketName = None
	marketIds: List[MarketId] = None
	marketNames: List[MarketName] = None
	ownerAddress: OrderOwnerAddress
	status: OrderStatus = None
	statuses: List[OrderStatus] = None

class GetOrderResponse(Order):
	pass

class GetOrdersRequest:
	ids: List[OrderId] = None
	marketId: MarketId = None
	marketName: MarketName = None
	marketIds: List[MarketId] = None
	marketNames: List[MarketName] = None
	ownerAddress: OrderOwnerAddress = None
	ownerAddresses: List[OrderOwnerAddress] = None
	status: OrderStatus = None
	statuses: List[OrderStatus] = None

GetOrdersResponse = Union[IMap[OrderId, Order], IMap[OwnerAddress, IMap[OrderId, Order]]]

class PlaceOrderRequest:
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

class PlaceOrderResponse(Order):
	pass

class PlaceOrdersRequest:
	ownerAddress: OrderOwnerAddress = None
	orders: List[PlaceOrderRequest]
	waitUntilIncludedInBlock: bool = None
	replaceIfExists: bool = None

class PlaceOrdersResponse(IMap[OrderId, Order]):
	pass

class CancelOrderRequest:
	id: OrderId
	clientId: OrderClientId = None
	ownerAddress: OrderOwnerAddress
	marketId: MarketId = None
	marketName: MarketName = None

class CancelOrderResponse(Order):
	pass

class CancelOrdersRequest:
	ids: List[OrderId]
	clientIds: List[OrderClientId] = None
	marketId: MarketId = None
	marketIds: List[MarketId] = None
	marketName: MarketName = None
	marketNames: List[MarketName] = None
	ownerAddress: OrderOwnerAddress = None
	ownerAddresses: List[OrderOwnerAddress] = None

CancelOrdersResponse = Union[IMap[OrderId, Order], IMap[OwnerAddress, IMap[OrderId, Order]]]

class CancelAllOrdersRequest:
	marketId: MarketId = None
	marketName: MarketName = None
	marketIds: List[MarketId] = None
	marketNames: List[MarketName] = None
	ownerAddress: OrderOwnerAddress = None
	ownerAddresses: List[OrderOwnerAddress] = None

CancelAllOrdersResponse = CancelOrdersResponse

class TransferFromToRequest:
	from_: Any
	to: OwnerAddress
	amount: OrderAmount
	tokenId: TokenId = None
	tokenSymbol: TokenSymbol = None

TransferFromToResponse = TransactionHash

class MarketWithdrawRequest:
	marketId: MarketId = None
	marketName: MarketName = None
	ownerAddress: OrderOwnerAddress = None
	ownerAddresses: List[OrderOwnerAddress] = None

MarketWithdrawResponse = Union[Withdraws, IMap[OwnerAddress, Withdraws]]

class MarketsWithdrawsRequest:
	marketIds: List[MarketId] = None
	marketNames: List[MarketName] = None
	ownerAddress: OrderOwnerAddress = None
	ownerAddresses: List[OrderOwnerAddress] = None

MarketsWithdrawsFundsResponse = Union[IMap[MarketId, Withdraws], IMap[OwnerAddress, IMap[MarketId, Withdraws]]]

class AllMarketsWithdrawsRequest(MarketsWithdrawsRequest):
	pass

AllMarketsWithdrawsResponse = MarketsWithdrawsFundsResponse

class GetCurrentBlockRequest:
	pass

GetCurrentBlockResponse = Block

class GetTransactionRequest:
	hash: TransactionHash

class GetTransactionResponse(Transaction):
	pass

class GetTransactionsRequest:
	hashes: List[TransactionHash]

GetTransactionsResponse = IMap[TransactionHash, Transaction]

class GetEstimatedFeesRequest:
	pass

class GetEstimatedFeesResponse(EstimatedFees):
	pass

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

RequestWrapper = Union[Any, Any]
