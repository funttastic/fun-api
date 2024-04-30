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


#
#  Types and Constants
#

address = str
owner_address = address
payer_address = address
price = Decimal
amount = Decimal
fee = Decimal
percentage = Decimal
timestamp = int
block = int
encrypted_wallet = str
token_id = address
token_name = str
token_symbol = str
token_decimals = int
market_name = str
market_id = address
market_precision = int
market_program_id = address
market_deprecation = bool
market_minimum_order_size = Decimal
market_minimum_price_increment = Decimal
market_minimum_base_increment = Decimal
market_minimum_quote_increment = Decimal
ticker_price = price
ticker_timestamp = timestamp
transaction_hash = str
order_id = str
order_client_id = str
order_market_name = market_name
order_market_id = market_id
fee_maker = fee
fee_taker = fee
fee_service_provider = fee
estimated_fees_token = str
estimated_fees_price = price
estimate_fees_limit = Decimal
estimate_fees_cost = Decimal
mnemonic = str
password = str
account_number = int
coin_gecko_symbol = str
coin_gecko_id = str

raw_market = any
raw_ticker = any
raw_order_book = any
raw_order = any

def frozen_set(values):
	return frozenset(values)

def dot_map(mapping):
	return DotMap(mapping)

#
#  Enums
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
	ORDER_BOOK_SAP = 'ORDER_BOOK_SIMPLE_AVERAGE_PRICE'
	ORDER_BOOK_WAP = 'ORDER_BOOK_WEIGHTED_AVERAGE_PRICE'
	ORDER_BOOK_VWAP = 'ORDER_BOOK_VOLUME_WEIGHTED_AVERAGE_PRICE'
	LAST_FILLED_ORDER = 'LAST_FILLED_ORDER'
	COINGECKO = 'COINGECKO'

class RequestStrategy(Enum):
	REST = 'REST'
	WS = 'WEBSOCKET'

class REST_METHOD(Enum):
	GET = 'GET'
	POST = 'POST'
	PUT = 'PUT'
	PATCH = 'PATCH'
	DELETE = 'DELETE'

#
#  Interfaces
#

class Token:
	id: token_id
	name: token_name
	symbol: token_symbol
	decimals: token_decimals

class Withdraw:
	fees = {
		"token": amount,
		"usd": amount
	}
	token: Token

class Withdraws:
	hash: transaction_hash
	tokens: List[Withdraw]
	total = {
		"fees": amount
	}

class Ticker:
	price: price

class TokenAmount:
	token: Token
	amount: amount

class OrderFilling:
	free: TokenAmount
	filled: TokenAmount

class TokenPriceInDolar:
	token: token_name
	price: price

class KujiraOrderBookItem:
	quote_price: str
	offer_denom = {
		"native": str
	}
	total_offer_amount: str

class KujiraOrderBook:
	base: List[KujiraOrderBookItem]
	quote: List[KujiraOrderBookItem]

class MarketFee:
	maker: fee_maker
	taker: fee_taker
	serviceProvider: fee_service_provider

class Market:
	id: market_id
	name: market_name
	base_token: Token
	quote_token: Token
	precision: market_precision
	minimum_order_size: market_minimum_order_size
	minimum_price_increment: market_minimum_price_increment
	minimum_base_increment: market_minimum_base_increment
	minimum_quote_increment: market_minimum_quote_increment
	fees: MarketFee
	programId: market_program_id = None
	deprecated: market_deprecation = False
	raw: raw_market

class TransactionHashes:
	creation: transaction_hash = None
	cancellation: transaction_hash = None
	withdraw: transaction_hash = None
	creations: List[transaction_hash] = None
	cancellations: List[transaction_hash] = None
	withdraws: List[transaction_hash] = None

class Order:
	id: order_id = None
	client_id: order_client_id = None # Client custom id
	marketName: order_market_name
	marketId: order_market_id
	market: Market
	owner_address: owner_address = None
	payerAddress: payer_address = None
	price: price = None
	amount: amount
	side: OrderSide
	status: OrderStatus = None
	type: OrderType = None
	fee: fee = None
	filling: OrderFilling = None
	creationTimestamp: timestamp = None
	fillingTimestamp: timestamp = None
	hashes: TransactionHashes = None
	raw: raw_order = None

class OrderBook:
	market: Market
	test: List[tuple(order_id, Order)]
	bids: IMap<OrderId, Order>
	asks: IMap<OrderId, Order>
	bestBid: Orde = None
	bestAsk: Order = None
	raw: raw_order_book

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


class SimplifiedBalanceWithUSD extends SimplifiedBalance:
	quotation: Amount


# eslint-disable-next-line @typescript-eslint/no-empty-interface
class TotalBalance extends SimplifiedBalance {}

class TokenBalance extends SimplifiedBalance:
	token: Token
inUSD: SimplifiedBalanceWithUSD


class Balances:
	tokens: IMap<TokenId, TokenBalance>
total: TotalBalance


class MarketFee:
	maker: FeeMaker
taker: FeeTaker
serviceProvider: FeeServiceProvider


class EstimatedFees:
	token: EstimatedFeesToken
price: EstimatedFeesPrice
limit: EstimateFeesLimit
cost: EstimateFeesCost
}

class Transaction:
	hash: TransactionHash
blockNumber: number
gasUsed: number
gasWanted: number
code: number
data: any
}

class BasicWallet:
	mnemonic: Mnemonic

accountNumber: AccountNumber

publicKey: Address
}

class KujiraWalletArtifacts:
	publicKey: Address

accountData: AccountData

accountNumber: AccountNumber

directSecp256k1HdWallet: DirectSecp256k1HdWallet

signingStargateClient: SigningStargateClient

signingCosmWasmClient: SigningCosmWasmClient

finClients: IMap<MarketId, fin.FinClient>
}

#
#  Errors
#

export class CLOBishError extends Error {}

export class TokenNotFoundError extends CLOBishError {}

export class MarketNotFoundError extends CLOBishError {}

export class BalanceNotFoundError extends CLOBishError {}

export class OrderBookNotFoundError extends CLOBishError {}

export class TickerNotFoundError extends CLOBishError {}

export class OrderNotFoundError extends CLOBishError {}

export class MarketWithdrawError extends CLOBishError {}

export class TransactionNotFoundError extends CLOBishError {}

export class WalletPublicKeyNotFoundError extends CLOBishError {}

#
#  Main methods options
#

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class GetRootRequest {}

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class GetRootResponse {
chain: string
network: string
connector: string
connection: boolean
timestamp: number
}

class GetTokenRequest {
id?: TokenId
name?: TokenName
symbol?: TokenSymbol
}

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class GetTokenResponse extends Token {}

class GetTokensRequest {
ids?: TokenId[]
names?: TokenName[]
symbols?: TokenSymbol[]
}

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class GetTokensResponse extends IMap<TokenId, Token> {}

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class GetAllTokensRequest {}

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class GetAllTokensResponse extends IMap<TokenId, Token> {}

class GetTokenSymbolsToTokenIdsMapRequest {
symbols?: TokenSymbol[]
}

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class GetTokenSymbolsToTokenIdsMapResponse
	extends IMap<TokenSymbol, TokenId> {}

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class GetKujiraTokenSymbolsToCoinGeckoTokenIdsMapResponse
	extends IMap<TokenSymbol, CoinGeckoId | undefined> {}

class GetMarketRequest {
id?: MarketId
name?: MarketName
}

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class GetMarketResponse extends Market {}

class GetMarketsRequest {
ids?: MarketId[]
names?: MarketName[]
}

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class GetMarketsResponse extends IMap<MarketId, Market> {}

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class GetAllMarketsRequest extends GetMarketsRequest {}

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class GetAllMarketsResponse extends IMap<MarketId, Market> {}

class GetOrderBookRequest {
marketId?: MarketId
marketName?: MarketName
}

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class GetOrderBookResponse extends OrderBook {}

class GetOrderBooksRequest {
marketIds?: MarketId[]
marketNames?: MarketName[]
}

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class GetOrderBooksResponse extends IMap<MarketId, OrderBook> {}

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class GetAllOrderBooksRequest extends GetOrderBooksRequest {}

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class GetAllOrderBooksResponse extends IMap<MarketId, OrderBook> {}

class GetTickerRequest {
marketId?: MarketId
marketName?: MarketName
}

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class GetTickerResponse extends Ticker {}

class GetTickersRequest {
marketIds?: MarketId[]
marketNames?: MarketName[]
}

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class GetTickersResponse extends IMap<MarketId, Ticker> {}

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class GetAllTickersRequest extends GetTickersRequest {}

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class GetAllTickersResponse extends IMap<MarketId, Ticker> {}

class GetWalletArtifactsRequest {
ownerAddress: OwnerAddress
}

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class GetWalletArtifactsResponse extends KujiraWalletArtifacts {}

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class GetBalanceRequest {
tokenId: TokenId
tokenSymbol: TokenSymbol
ownerAddress: OwnerAddress
}

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class GetBalanceResponse extends TokenBalance {}

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class GetBalancesRequest {
tokenIds?: TokenId[]
tokenSymbols?: TokenSymbol[]
ownerAddress: OwnerAddress
}

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class GetBalancesResponse extends Balances {}

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class GetAllBalancesRequest {
ownerAddress: OwnerAddress
}

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class GetAllBalancesResponse extends Balances {}

class GetOrderRequest {
id: OrderId
marketId?: MarketId
marketName?: MarketName
marketIds?: MarketId[]
marketNames?: MarketName[]
ownerAddress: OrderOwnerAddress
status?: OrderStatus
statuses?: OrderStatus[]
}

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class GetOrderResponse extends Order {}

class GetOrdersRequest {
ids?: OrderId[]
marketId?: MarketId
marketName?: MarketName
marketIds?: MarketId[]
marketNames?: MarketName[]
ownerAddress?: OrderOwnerAddress
ownerAddresses?: OrderOwnerAddress[]
status?: OrderStatus
statuses?: OrderStatus[]
}

export type GetOrdersResponse =
| IMap<OrderId, Order>
| IMap<OwnerAddress, IMap<OrderId, Order>>

class PlaceOrderRequest {
clientId?: OrderClientId
marketId?: MarketId
marketName?: MarketName
ownerAddress?: OrderOwnerAddress
side: OrderSide
price: OrderPrice
amount: OrderAmount
type: OrderType
payerAddress?: OrderPayerAddress
replaceIfExists?: boolean
waitUntilIncludedInBlock?: boolean
}

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class PlaceOrderResponse extends Order {}

class PlaceOrdersRequest {
ownerAddress?: OrderOwnerAddress
orders: PlaceOrderRequest[]
waitUntilIncludedInBlock?: boolean
replaceIfExists?: boolean
}

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class PlaceOrdersResponse extends IMap<OrderId, Order> {}

class CancelOrderRequest {
id: OrderId
clientId?: OrderClientId
ownerAddress: OrderOwnerAddress
marketId?: MarketId
marketName?: MarketName
}

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class CancelOrderResponse extends Order {}

class CancelOrdersRequest {
ids: OrderId[]
clientIds?: OrderClientId[]
marketId?: MarketId
marketIds?: MarketId[]
marketName?: MarketName
marketNames?: MarketName[]
ownerAddress?: OrderOwnerAddress
ownerAddresses?: OrderOwnerAddress[]
}

export type CancelOrdersResponse =
| IMap<OrderId, Order>
| IMap<OwnerAddress, IMap<OrderId, Order>>

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class CancelAllOrdersRequest {
marketId?: MarketId
marketName?: MarketName
marketIds?: MarketId[]
marketNames?: MarketName[]
ownerAddress?: OrderOwnerAddress
ownerAddresses?: OrderOwnerAddress[]
}

export type CancelAllOrdersResponse = CancelOrdersResponse

class TransferFromToRequest {
from: OwnerAddress
to: OwnerAddress
amount: OrderAmount
tokenId?: TokenId
tokenSymbol?: TokenSymbol
}

export type TransferFromToResponse = TransactionHash

class MarketWithdrawRequest {
marketId?: MarketId
marketName?: MarketName
ownerAddress?: OrderOwnerAddress
ownerAddresses?: OrderOwnerAddress[]
}

export type MarketWithdrawResponse = Withdraws | IMap<OwnerAddress, Withdraws>

class MarketsWithdrawsRequest {
marketIds?: MarketId[]
marketNames?: MarketName[]
ownerAddress?: OrderOwnerAddress
ownerAddresses?: OrderOwnerAddress[]
}

export type MarketsWithdrawsFundsResponse =
| IMap<MarketId, Withdraws>
| IMap<OwnerAddress, IMap<MarketId, Withdraws>>

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class AllMarketsWithdrawsRequest extends MarketsWithdrawsRequest {}

export type AllMarketsWithdrawsResponse = MarketsWithdrawsFundsResponse

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class GetCurrentBlockRequest {}

# eslint-disable-next-line @typescript-eslint/no-empty-interface
export type GetCurrentBlockResponse = Block

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class GetTransactionRequest {
hash: TransactionHash
}

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class GetTransactionResponse extends Transaction {}

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class GetTransactionsRequest {
hashes: TransactionHash[]
}

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class GetTransactionsResponse
	extends IMap<TransactionHash, Transaction> {}

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class GetEstimatedFeesRequest {}

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class GetEstimatedFeesResponse extends EstimatedFees {}

class GetWalletPublicKeyRequest {
mnemonic: Mnemonic
accountNumber: AccountNumber
}

# eslint-disable-next-line @typescript-eslint/no-empty-interface
export type GetWalletPublicKeyResponse = Address

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class GetWalletsPublicKeysRequest {}

# eslint-disable-next-line @typescript-eslint/no-empty-interface
export type GetWalletsPublicKeysResponse = Address[]

class EncryptWalletRequest {
wallet: BasicWallet
}

# eslint-disable-next-line @typescript-eslint/no-empty-interface
export type EncryptWalletResponse = EncryptedWallet

# eslint-disable-next-line @typescript-eslint/no-empty-interface
class DecryptWalletRequest {
accountAddress: OwnerAddress
}

# eslint-disable-next-line @typescript-eslint/no-empty-interface
export type DecryptWalletResponse = BasicWallet

#
# Extensions
#

class EstimatedGasResponse {
gasPrice: number
gasPriceToken: string
gasLimit: number
gasCost: number
}

class LatencyData {
endpoint: string
latency: number
latestBlockTime: Date
}

export type RequestWrapper<T> = NetworkSelectionRequest & T
