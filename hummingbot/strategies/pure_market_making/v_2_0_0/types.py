from dotmap import DotMap
from decimal import Decimal
from typing import Any, List, Dict, Optional, Callable, Union
from enum import Enum
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

KujiraOrder = Any
KujiraEvent = Any
KujiraEventAttribute = Any

FunctionType = Callable[..., Any]
AsyncFunctionType = Callable[..., Any]

Map = DotMap

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

Mnemonic = str
Password = str
AccountNumber = int

CoinGeckoSymbol = str
CoinGeckoId = str

ChainName = str
ConnectorName = str
NetworkName = str
Latency = int
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
	tokens: Map[TokenId, Withdraw]
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


class OrderBook:
	market: Market
	bids: Map[OrderId, 'Order']
	asks: Map[OrderId, 'Order']
	best_bid: 'Order'
	best_ask: 'Order'
	raw: Any


class Ticker:
	market: Market
	price: TickerPrice
	timestamp: TickerTimestamp
	tokens: ConnectorTicker


class SimplifiedBalance:
	free: Amount
	locked_in_orders: Amount
	unsettled: Amount
	total: Amount


class SimplifiedBalanceWithUSD(SimplifiedBalance):
	quotation: Amount


class TotalBalance(SimplifiedBalance):
	pass


class TokenBalance(SimplifiedBalance):
	token: Token
	in_usd: SimplifiedBalanceWithUSD


class Balances:
	tokens: Map[TokenId, TokenBalance]
	total: TotalBalance


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
	connector_order: ConnectorOrder


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
	service_provider: FeeServiceProvider


class EstimatedFees:
	token: EstimatedFeesToken
	price: EstimatedFeesPrice
	limit: EstimateFeesLimit
	cost: EstimateFeesCost


class Transaction:
	hash: TransactionHash
	block_number: Block
	gas_used: int
	gas_wanted: int
	code: int
	data: Any


class BasicWallet:
	mnemonic: Mnemonic
	account_number: AccountNumber
	public_key: Address


class KujiraWalletArtifacts:
	public_key: Address
	account_data: Any
	account_number: AccountNumber
	direct_secp256k1_hd_wallet: Any
	signing_stargate_client: Any
	signing_cosm_wasm_client: Any
	fin_clients: Map[MarketId, Any]


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


RestGetTransactionsResponse = Map[TransactionHash, Transaction]


class RestGetTokenRequest:
	id: Optional[TokenId]
	name: Optional[TokenName]
	symbol: Optional[TokenSymbol]


class RestGetTokenResponse(Token):
	pass


class RestGetTokensRequest:
	ids: Optional[List[TokenId]]
	names: Optional[List[TokenName]]
	symbols: Optional[List[TokenSymbol]]


class RestGetTokensResponse(Map[TokenId, Token]):
	pass


class RestGetAllTokensRequest:
	pass


class RestGetAllTokensResponse(Map[TokenId, Token]):
	pass


class RestGetMarketRequest:
	id: Optional[MarketId]
	name: Optional[MarketName]


class RestGetMarketResponse(Market):
	pass


class RestGetMarketsRequest:
	ids: Optional[List[MarketId]]
	names: Optional[List[MarketName]]


class RestGetMarketsResponse(Map[MarketId, Market]):
	pass


class RestGetAllMarketsRequest(RestGetMarketsRequest):
	pass


class RestGetAllMarketsResponse(Map[MarketId, Market]):
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


class RestGetAllOrderBooksRequest(RestGetOrderBooksRequest):
	pass


class RestGetAllOrderBooksResponse(Map[MarketId, OrderBook]):
	pass


class RestGetTickerRequest:
	market_id: Optional[MarketId]
	market_name: Optional[MarketName]


class RestGetTickerResponse(Ticker):
	pass


class RestGetTickersRequest:
	market_ids: Optional[List[MarketId]]
	market_names: Optional[List[MarketName]]


class RestGetTickersResponse(Map[MarketId, Ticker]):
	pass


class RestGetAllTickersRequest(RestGetTickersRequest):
	pass


class RestGetAllTickersResponse(Map[MarketId, Ticker]):
	pass


class RestGetBalanceRequest:
	token_id: TokenId
	token_symbol: TokenSymbol
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


class RestGetAllBalancesResponse(Balances):
	pass


class RestGetOrderRequest:
	id: OrderId
	market_id: Optional[MarketId]
	market_name: Optional[MarketName]
	market_ids: Optional[List[MarketId]]
	market_names: Optional[List[MarketName]]
	owner_address: OrderOwnerAddress
	status: Optional[OrderStatus]
	statuses: Optional[List[OrderStatus]]


class RestGetOrderResponse(Map[OwnerAddress, Map[OrderId, Order]]):
	pass


class RestGetOrdersRequest:
	ids: Optional[List[OrderId]]
	market_id: Optional[MarketId]
	market_name: Optional[MarketName]
	market_ids: Optional[List[MarketId]]
	market_names: Optional[List[MarketName]]
	owner_address: Optional[OrderOwnerAddress]
	owner_addresses: Optional[List[OrderOwnerAddress]]
	status: Optional[OrderStatus]
	statuses: Optional[List[OrderStatus]]


class RestGetOrdersResponse(Map[OwnerAddress, Map[OrderId, Order]]):
	pass


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
	client_id: Optional[OrderClientId]
	market_id: Optional[MarketId]
	market_name: Optional[MarketName]
	owner_address: Optional[OrderOwnerAddress]
	side: OrderSide
	price: OrderPrice
	amount: OrderAmount
	type: OrderType
	payer_address: Optional[OrderPayerAddress]
	replace_if_exists: Optional[bool]
	wait_until_included_in_block: Optional[bool]


class RestPlaceOrderResponse(Order):
	pass


class RestPlaceOrdersRequest:
	owner_address: Optional[OrderOwnerAddress]
	orders: List[RestPlaceOrderRequest]
	wait_until_included_in_block: Optional[bool]
	replace_if_exists: Optional[bool]


class RestPlaceOrdersResponse(Map[OrderId, Order]):
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
	client_id: Optional[OrderClientId]
	owner_address: OrderOwnerAddress
	market_id: Optional[MarketId]
	market_name: Optional[MarketName]


class RestCancelOrderResponse(Map[OwnerAddress, Map[OrderId, Order]]):
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


RestCancelOrdersResponse = Map[OwnerAddress, Map[OrderId, Order]]


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


RestMarketWithdrawResponse = Map[OwnerAddress, Withdraws]


class RestMarketsWithdrawsRequest:
	market_ids: Optional[List[MarketId]]
	market_names: Optional[List[MarketName]]
	owner_address: Optional[OrderOwnerAddress]
	owner_addresses: Optional[List[OrderOwnerAddress]]


RestMarketsWithdrawsFundsResponse = Map[OwnerAddress, Map[MarketId, Withdraws]]


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
	hourly_funding_rate_cap: str
	hourly_interest_rate: str
	next_funding_timestamp: Timestamp
	funding_interval: int


@dataclass
class PerpetualMarketFunding:
	cumulative_funding: str
	cumulative_price: str
	last_timestamp: Timestamp


@dataclass
class TokenMeta:
	pass


@dataclass
class BaseDerivativeMarket:
	oracle_type: str
	market_id: str
	market_status: str
	ticker: str
	quote_denom: str
	maker_fee_rate: str
	quote_token: Optional[TokenMeta]
	taker_fee_rate: str
	service_provider_fee: str
	min_price_tick_size: Optional[Union[int, str]]
	min_quantity_tick_size: Optional[Union[int, str]]


@dataclass
class PerpetualMarket(BaseDerivativeMarket):
	initial_margin_ratio: str
	maintenance_margin_ratio: str
	is_perpetual: bool
	oracle_base: str
	oracle_quote: str
	oracle_scale_factor: int
	perpetual_market_info: Optional[PerpetualMarketInfo]
	perpetual_market_funding: Optional[PerpetualMarketFunding]


@dataclass
class PriceLevel:
	price: str
	quantity: str
	timestamp: Timestamp


@dataclass
class InjectiveOrderBook:
	buys: List[PriceLevel]
	sells: List[PriceLevel]


class TradeDirection(Enum):
	BUY = "buy"
	SELL = "sell"
	LOG = "long"
	SHORT = "short"


class TradeExecutionType(Enum):
	MARKET = "market"
	LIMIT_FILL = "limitFill"
	LIMIT_MATCH_RESTING_ORDER = "limitMatchRestingOrder"
	LIMIT_MATCH_NEW_ORDER = "limitMatchNewOrder"


class TradeExecutionSide(Enum):
	MAKER = "maker"
	TAKER = "taker"


@dataclass
class FundingPayment:
	market_id: str
	sub_account_id: str
	amount: str
	timestamp: Timestamp


@dataclass
class Position:
	market_id: str
	sub_account_id: str
	direction: TradeDirection
	quantity: str
	entry_price: str
	margin: str
	liquidation_price: str
	mark_price: str
	ticker: str
	aggregate_reduce_only_quantity: str
	updated_at: Timestamp


@dataclass
class PositionDelta:
	trade_direction: TradeDirection
	execution_price: str
	execution_quantity: str
	execution_margin: str


@dataclass
class DerivativeTrade(PositionDelta):
	order_hash: str
	sub_account_id: str
	trade_id: str
	market_id: str
	executed_at: Timestamp
	trade_execution_type: TradeExecutionType
	execution_side: TradeExecutionSide
	fee: str
	fee_recipient: str
	is_liquidation: bool
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


CLOBMarkets = Map[str, any]


@dataclass
class ClobMarketsRequest(NetworkSelectionRequest):
	market: Optional[MarketName]


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
	order_book: InjectiveOrderBook


class ClobGetOrderRequest(ClobOrderbookRequest):
	address: Optional[Address]
	order_id: OrderId


class ClobGetOrderResponse:
	network: str
	timestamp: int
	latency: int
	orders: List[Map[str, str]] = []


@dataclass
class CreateOrderParam:
	price: str
	amount: str
	order_type: OrderType
	side: OrderSide
	market: MarketName
	client_order_id: Optional[OrderClientId]


class ClobPostOrderRequest(NetworkSelectionRequest, CreateOrderParam):
	address: Address


@dataclass
class ClobDeleteOrderRequestExtract:
	market: MarketName
	order_id: OrderId


@dataclass
class ClobBatchUpdateRequest(NetworkSelectionRequest):
	address: Address
	create_order_params: Optional[List[CreateOrderParam]]
	cancel_order_params: Optional[List[ClobDeleteOrderRequestExtract]]


@dataclass
class ClobPostOrderResponse:
	network: str
	timestamp: int
	latency: int
	txHash: str
	client_order_id: Optional[Union[str, List[str]]]


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
	order_id: Optional[OrderId]
	direction: Optional[str]  # 'buy', 'sell', 'long', 'short'
	order_types: Optional[str]  # string like 'buy,sell,stop_buy,stop_sell,take_buy,take_sell,buy_po,sell_po'
	limit: Optional[Limit]  # 1 or greater, otherwise it gets all orders


class PerpClobGetOrderResponse:
	network: NetworkName
	timestamp: Timestamp
	latency: Latency
	orders: List[Dict[str, str]] = []


@dataclass
class CreatePerpOrderParam:
	price: str
	amount: str
	order_type: OrderType
	side: OrderSide
	market: MarketName
	leverage: int


@dataclass
class PerpClobPostOrderRequest(NetworkSelectionRequest, CreatePerpOrderParam):
	address: Address


PerpClobPostOrderResponse = ClobPostOrderResponse


@dataclass
class PerpClobDeleteOrderRequest(NetworkSelectionRequest):
	market: MarketName
	address: Address
	order_id: OrderId


PerpClobDeleteOrderResponse = PerpClobPostOrderResponse


@dataclass
class PerpClobBatchUpdateRequest(NetworkSelectionRequest):
	address: Address
	create_order_params: Optional[List[CreatePerpOrderParam]]
	cancel_order_params: Optional[List[ClobDeleteOrderRequestExtract]]


PerpClobBatchUpdateResponse = ClobPostOrderResponse


@dataclass
class PerpClobFundingInfoRequest(NetworkSelectionRequest):
	market: MarketName


@dataclass
class FundingInfo:
	market_id: MarketId
	index_price: str
	mark_price: str
	funding_rate: str
	next_funding_timestamp: Timestamp


@dataclass
class PerpClobFundingInfoResponse:
	network: NetworkName
	timestamp: Timestamp
	latency: Latency
	funding_info: FundingInfo


@dataclass
class PerpClobGetLastTradePriceRequest(NetworkSelectionRequest):
	market: MarketName


@dataclass
class PerpClobGetLastTradePriceResponse:
	network: NetworkName
	timestamp: Timestamp
	latency: Latency
	last_trade_price: str


@dataclass
class PerpClobGetTradesRequest(NetworkSelectionRequest):
	market: MarketName
	address: Address
	order_id: OrderId


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
	funding_payments: List[FundingPayment]


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
	gas_price: int
	gas_price_token: str
	gas_limit: int
	gas_cost: int


class LatencyData:
	endpoint: str
	latency: Latency
	latest_block_time: Any


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
	symbols: Optional[List[TokenSymbol]]


class GetTokenSymbolsToTokenIdsMapResponse(Map[TokenSymbol, TokenId]):
	pass


class GetKujiraTokenSymbolsToCoinGeckoTokenIdsMapResponse(Map[TokenSymbol, Union[CoinGeckoId, None]]):
	pass


class GetWalletArtifactsRequest:
	owner_address: OwnerAddress


class GetWalletArtifactsResponse(KujiraWalletArtifacts):
	pass


class TransferFromToRequest:
	from_: Any
	to: OwnerAddress
	amount: OrderAmount
	token_id: Optional[TokenId]
	token_symbol: Optional[TokenSymbol]


TransferFromToResponse = TransactionHash


class GetWalletPublicKeyRequest:
	mnemonic: Mnemonic
	account_number: AccountNumber


GetWalletPublicKeyResponse = Address


class GetWalletsPublicKeysRequest:
	pass


GetWalletsPublicKeysResponse = List[Address]


class EncryptWalletRequest:
	wallet: BasicWallet


EncryptWalletResponse = EncryptedWallet


class DecryptWalletRequest:
	account_address: OwnerAddress


DecryptWalletResponse = BasicWallet


RequestWrapper = Union[Any, Any]
