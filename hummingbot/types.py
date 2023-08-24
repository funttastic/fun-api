import asyncio
import json
from _decimal import Decimal
from enum import Enum
from typing import Optional, Any, Dict

from core.utils import dump


class OrderStatus(Enum):
	OPEN = "OPEN",
	CANCELLED = "CANCELLED",
	PARTIALLY_FILLED = "PARTIALLY_FILLED",
	FILLED = "FILLED",
	CREATION_PENDING = "CREATION_PENDING",
	CANCELLATION_PENDING = "CANCELLATION_PENDING",
	UNKNOWN = "UNKNOWN"

	@staticmethod
	def from_name(name: str):
		if name == "OPEN":
			return OrderStatus.OPEN
		elif name == "CANCELLED":
			return OrderStatus.CANCELLED
		elif name == "PARTIALLY_FILLED":
			return OrderStatus.PARTIALLY_FILLED
		elif name == "FILLED":
			return OrderStatus.FILLED
		elif name == "CREATION_PENDING":
			return OrderStatus.CREATION_PENDING
		elif name == "CANCELLATION_PENDING":
			return OrderStatus.CANCELLATION_PENDING
		else:
			raise ValueError(f"Unknown order status: {name}")


class OrderType(Enum):
	MARKET = 'MARKET',
	LIMIT = 'LIMIT',
	IOC = 'IOC',  # Immediate or Cancel
	POST_ONLY = 'POST_ONLY',

	@staticmethod
	def from_name(name: str):
		if name == "MARKET":
			return OrderType.MARKET
		elif name == "LIMIT":
			return OrderType.LIMIT
		elif name == "IOC":
			return OrderType.IOC
		elif name == "POST_ONLY":
			return OrderType.POST_ONLY
		else:
			raise ValueError(f"Unknown order type: {name}")


class OrderSide(Enum):
	BUY = 'BUY',
	SELL = 'SELL',

	@staticmethod
	def from_name(name: str):
		if name == "BUY":
			return OrderSide.BUY
		elif name == "SELL":
			return OrderSide.SELL
		else:
			raise ValueError(f"Unknown order side: {name}")


class TickerSource(Enum):
	ORDER_BOOK_SAP = "orderBookSimpleAveragePrice",
	ORDER_BOOK_WAP = "orderBookWeightedAveragePrice",
	ORDER_BOOK_VWAP = "orderBookVolumeWeightedAveragePrice",
	LAST_FILLED_ORDER = "lastFilledOrder",
	NOMICS = "nomics"


class PriceStrategy(Enum):
	MIDDLE = 'MIDDLE',
	TICKER = 'TICKER',
	LAST_FILL = 'LAST_FILL'


class MiddlePriceStrategy(Enum):
	SAP = 'SIMPLE_AVERAGE_PRICE',
	WAP = 'WEIGHTED_AVERAGE_PRICE',
	VWAP = 'VOLUME_WEIGHTED_AVERAGE_PRICE'


class Order:
	def __init__(self) -> None:
		super().__init__()

	id: Optional[str]
	client_id: Optional[str]
	market_name: Optional[str]
	market_id: Optional[str]
	market: Optional[Any]
	owner_address: str
	payer_address: Optional[str]
	price: Optional[Decimal]
	amount: Decimal
	side: OrderSide
	status: OrderStatus
	type: OrderType
	fee: Decimal
	creation_timestamp: Optional[int]
	filling_timestamp: Optional[int]
	hashes: Optional[Dict[str, str]]

	def __str__(self):
		def decoder(target):
			if isinstance(target, Decimal):
				return str(target)
			raise TypeError

		dictionary = json.dumps(self.__dict__, default=decoder)

		return dump(dictionary)


class AsyncLock:
	def __init__(self):
		self._lock = asyncio.Lock()

	async def __aenter__(self):
		await self._lock.acquire()
		return self

	async def __aexit__(self, exc_type, exc_value, traceback):
		self._lock.release()
