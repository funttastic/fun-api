import asyncio
import hashlib
import math
import random
import json
from enum import Enum
import time
from _decimal import Decimal
from array import array
from datetime import datetime
from typing import Any, List, Union, Optional, Dict

import jsonpickle
import numpy as np
from dotmap import DotMap

from hummingbot.constants import VWAP_THRESHOLD, DECIMAL_ZERO


alignment_column = 12

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


def current_timestamp() -> float:
	return time.time()


def generate_hash(input: Any) -> str:
	return generate_hashes([input])[0]


def generate_hashes(inputs: List[Any]) -> List[str]:
	hashes = []
	salt = datetime.now()

	for input in inputs:
		serialized = jsonpickle.encode(input, unpicklable=True)
		hasher = hashlib.md5()
		target = f"{salt}{serialized}".encode("utf-8")
		hasher.update(target)
		hash = hasher.hexdigest()

		hashes.append(hash)

	return hashes


def convert_hb_trading_pair_to_market_name(trading_pair: str) -> str:
	return trading_pair.replace("-", "/")


def convert_market_name_to_hb_trading_pair(market_name: str) -> str:
	return market_name.replace("/", "-")


def parse_order_book(orderbook: DotMap[str, Any]) -> List[
	Union[List[DotMap[str, Any]], List[DotMap[str, Any]]]]:
	bids_list = []
	asks_list = []

	bids: DotMap[str, Any] = orderbook.bids
	asks: DotMap[str, Any] = orderbook.asks

	for value in bids.values():
		bids_list.append(DotMap({'price': value.price, 'amount': value.amount}, _dynamic=False))

	for value in asks.values():
		asks_list.append(DotMap({'price': value.price, 'amount': value.amount}, _dynamic=False))

	bids_list.sort(key=lambda x: x['price'], reverse=True)
	asks_list.sort(key=lambda x: x['price'], reverse=False)

	return [bids_list, asks_list]


def split_percentage(bids: [DotMap[str, Any]], asks: [DotMap[str, Any]]) -> List[Any]:
	asks = asks[:math.ceil((VWAP_THRESHOLD / 100) * len(asks))]
	bids = bids[:math.ceil((VWAP_THRESHOLD / 100) * len(bids))]

	return [bids, asks]


def compute_volume_weighted_average_price(book: [DotMap[str, Any]]) -> np.array:
	prices = [float(order['price']) for order in book]
	amounts = [float(order['amount']) for order in book]

	prices = np.array(prices)
	amounts = np.array(amounts)

	vwap = (np.cumsum(amounts * prices) / np.cumsum(amounts))

	return vwap


def remove_outliers(order_book: [DotMap[str, Any]], side: OrderSide) -> [DotMap[str, Any]]:
	prices = [order['price'] for order in order_book]

	q75, q25 = np.percentile(prices, [75, 25])

	# https://www.askpython.com/python/examples/detection-removal-outliers-in-python
	# intr_qr = q75-q25
	# max_threshold = q75+(1.5*intr_qr)
	# min_threshold = q75-(1.5*intr_qr) # Error: Sometimes this function assigns negative value for min

	max_threshold = q75 * 1.5
	min_threshold = q25 * 0.5

	orders = []
	if side == OrderSide.SELL:
		orders = [order for order in order_book if order['price'] < max_threshold]
	elif side == OrderSide.BUY:
		orders = [order for order in order_book if order['price'] > min_threshold]

	return orders


def calculate_middle_price(
	bids: [DotMap[str, Any]],
	asks: [DotMap[str, Any]],
	strategy: MiddlePriceStrategy
) -> Decimal:
	if strategy == MiddlePriceStrategy.SAP:
		bid_prices = [float(item['price']) for item in bids]
		ask_prices = [float(item['price']) for item in asks]

		best_ask_price = 0
		best_bid_price = 0

		if len(ask_prices) > 0:
			best_ask_price = min(ask_prices)

		if len(bid_prices) > 0:
			best_bid_price = max(bid_prices)

		return Decimal((best_ask_price + best_bid_price) / 2.0)
	elif strategy == MiddlePriceStrategy.WAP:
		bid_prices = [float(item['price']) for item in bids]
		ask_prices = [float(item['price']) for item in asks]

		best_ask_price = 0
		best_ask_volume = 0
		best_bid_price = 0
		best_bid_amount = 0

		if len(ask_prices) > 0:
			best_ask_idx = ask_prices.index(min(ask_prices))
			best_ask_price = float(asks[best_ask_idx]['price'])
			best_ask_volume = float(asks[best_ask_idx]['amount'])

		if len(bid_prices) > 0:
			best_bid_idx = bid_prices.index(max(bid_prices))
			best_bid_price = float(bids[best_bid_idx]['price'])
			best_bid_amount = float(bids[best_bid_idx]['amount'])

		if best_ask_volume + best_bid_amount > 0:
			return Decimal(
				(best_ask_price * best_ask_volume + best_bid_price * best_bid_amount)
				/ (best_ask_volume + best_bid_amount)
			)
		else:
			return DECIMAL_ZERO
	elif strategy == MiddlePriceStrategy.VWAP:
		bids, asks = split_percentage(bids, asks)

		if len(bids) > 0:
			bids = remove_outliers(bids, OrderSide.BUY)

		if len(asks) > 0:
			asks = remove_outliers(asks, OrderSide.SELL)

		book = [*bids, *asks]

		if len(book) > 0:
			vwap = compute_volume_weighted_average_price(book)

			return Decimal(vwap[-1])
		else:
			return DECIMAL_ZERO
	else:
		raise ValueError(f'Unrecognized mid price strategy "{strategy}".')


def format_line(left, right, column=alignment_column, align: str = "right"):
	right = str(right) if str(right).startswith("-") else f" {str(right)}"

	if align == "left":
		return f"""<code>{left}{" " * (column - len(left))}{right}</code>"""
	elif align == "right":
		return f"""<code>{left}{" " * (alignment_column + column - len(left) - len(right))}{right}</code>"""
	else:
		raise ValueError(f"""Align option "{align}" not recognized.""")


def format_currency(target: Decimal, precision: int) -> str:
	return ("{:0,." + str(precision) + "f}").format(round(target, precision))


def format_percentage(target: Decimal, precision: int = 2) -> str:
	decimal_near_zero = Decimal("0E-2")

	value = round(target, precision)
	if math.isclose(value, DECIMAL_ZERO, rel_tol=decimal_near_zero, abs_tol=decimal_near_zero):
		return "⚪ {:.{}f}%".format(math.fabs(value), precision)
	elif target < 0:
		return "🔴 {:.{}f}%".format(value, precision)
	else:
		return "🟢 {:.{}f}%".format(value, precision)


def format_lines(groups: List[List[str]], align: str = "right") -> str:
	lines: array[str] = [""] * len(groups[0])
	for items in groups:
		length = len(max(items, key=lambda i: len(i)))

		for index, item in enumerate(items):
			if align == "left":
				lines[index] += f"""{item}{" " * (length - len(item))} """
			elif align == "right":
				lines[index] += f"""{" " * (length - len(item))}{item} """
			else:
				raise ValueError(f"""Align option "{align}" not recognized.""")

	for line in range(len(lines)):
		lines[line] = f"""<code>{lines[line].rstrip(" ")}</code>"""

	return "\n".join(lines)


def is_int(value: int) -> bool:
	return isinstance(value, int)


def is_float(value: float) -> bool:
	return isinstance(value, float)


def is_list_of_floats(items: List[any]) -> bool:
	for item in items:
		if not is_float(item):
			return False

	return True


def is_number(value: any) -> bool:
	return isinstance(value, (int, float))


def is_list_of_numbers(items: List[any]) -> bool:
	for item in items:
		if not is_number(item):
			return False

	return True


def is_list(value: any) -> bool:
	return type(value) is list


def is_valid_interval(interval: List) -> bool:
	return interval is not None \
		and len(interval) == 2 \
		and is_number(interval[0]) \
		and is_number(interval[1]) \
		and interval[0] <= interval[1]


def is_valid_non_negative_interval(interval: List) -> bool:
	return interval is not None \
		and len(interval) == 2 \
		and is_number(interval[0]) \
		and is_number(interval[1]) \
		and interval[0] >= 0 \
		and interval[1] >= 0 \
		and interval[0] <= interval[1]


def get_int_or_random_int_in_interval(target: any) -> int:
	return int(get_float_or_random_float_in_interval(target))


def get_float_or_random_float_in_interval(target: any) -> float:
	if is_number(target):
		return target
	elif is_valid_interval(target):
		return random.uniform(target[0], target[1])
	else:
		raise ValueError(f"Invalid number or interval: {target}")


def get_random_choice(items: List[any]) -> any:
	chosen = random.randint(0, len(items) - 1)

	return items[chosen]


def calculate_waiting_time(number: int) -> int:
	current_timestamp_in_milliseconds = int(time.time() * 1000)
	result = number - (current_timestamp_in_milliseconds % number)

	return result


def redefine_precision(number: Decimal, decimal_place: int) -> str:
	integer_part = int(number)
	length_integer_part = len(str(integer_part))
	precision = decimal_place
	if length_integer_part == 1:
		return ("{:0,." + str(precision) + "f}").format(round(number, precision))
	elif length_integer_part <= 3:
		precision -= (length_integer_part - 1)
		return ("{:0,." + str(precision) + "f}").format(round(number, precision))
	elif length_integer_part == 4:
		precision -= length_integer_part
		return ("{:0,." + str(precision) + "f}").format(number).replace(",", "")
	else:
		return "{:.1e}".format(number)
