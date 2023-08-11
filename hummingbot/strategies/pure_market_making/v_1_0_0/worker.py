import asyncio
import copy
import math
import traceback
from decimal import Decimal
from logging import DEBUG, INFO, WARNING
from os import path
from pathlib import Path
from typing import Any, List, Union

import numpy as np
from dotmap import DotMap

from hummingbot.constants import DECIMAL_NAN
from hummingbot.constants import KUJIRA_NATIVE_TOKEN, DECIMAL_ZERO, VWAP_THRESHOLD, \
	FLOAT_ZERO, FLOAT_INFINITY
from hummingbot.gateway import Gateway
from hummingbot.strategies.worker_base import WorkerBase
from hummingbot.types import OrderSide, OrderType, Order, OrderStatus, \
	MiddlePriceStrategy, PriceStrategy
from utils import dump


class Worker(WorkerBase):

	def __init__(self, parent, configuration):
		try:
			self._parent = parent
			self.id = f"""{self._parent.id}:worker:{configuration.id}"""
			self.logger_prefix = self.id

			self.log(INFO, "start")

			super().__init__()

			self._can_run: bool = True
			self._script_name = path.basename(Path(__file__))
			self._configuration = DotMap(configuration, _dynamic=False)
			self._wallet_address = None
			self._quote_token_name = None
			self._base_token_name = None
			self._is_busy: bool = False
			self._refresh_timestamp: int = 0
			self._market: DotMap[str, Any]
			self._balances: DotMap[str, Any] = DotMap({}, _dynamic=False)
			self._tickers: DotMap[str, Any]
			self._currently_tracked_orders_ids: [str] = []
			self._tracked_orders_ids: [str] = []
			self._open_orders: DotMap[str, Any]
			self._filled_orders: DotMap[str, Any]
			self._tasks: DotMap[str, asyncio.Task] = DotMap({
				"on_tick": None,
				"markets": None,
				"order_books": None,
				"tickers": None,
				"orders": None,
				"balances": None,
			}, _dynamic=False)
			self._events: DotMap[str, asyncio.Event] = DotMap({
				"on_tick": None,
			}, _dynamic=False)
		finally:
			self.log(INFO, "end")

	# noinspection PyAttributeOutsideInit
	async def initialize(self):
		try:
			self.log(INFO, "start")

			self.initialized = False

			self.clock.start()
			self._refresh_timestamp = self.clock.now()
			(self._refresh_timestamp, self._events.on_tick) = self.clock.register(self._refresh_timestamp)

			self._market_name = self._configuration.market

			self._wallet_address = self._configuration.wallet

			self._market = await self._get_market()

			self._base_token = self._market.baseToken
			self._quote_token = self._market.quoteToken

			self._base_token_name = self._market.baseToken.name
			self._quote_token_name = self._market.quoteToken.name

			if self._configuration.strategy.cancel_all_orders_on_start:
				try:
					await self._cancel_all_orders()
				except Exception as exception:
					self.ignore_exception(exception)

			if self._configuration.strategy.withdraw_market_on_start:
				try:
					await self._market_withdraw()
				except Exception as exception:
					self.ignore_exception(exception)

			waiting_time = self._calculate_waiting_time(self._configuration.strategy.tick_interval)
			self.log(DEBUG, f"""Waiting for {waiting_time}s.""")
			self._refresh_timestamp = waiting_time + self.clock.now()

			self.initialized = True
			self._can_run = True
		except Exception as exception:
			self.ignore_exception(exception)

			await self.exit()
		finally:
			self.log(INFO, "end")

	async def start(self):
		self.log(INFO, "start")

		await self.initialize()

		self._tasks.on_tick = asyncio.create_task(self.on_tick())

		self.log(INFO, "end")

	async def stop(self):
		try:
			self.log(INFO, "start")

			self._can_run = False

			try:
				if self._tasks.on_tick:
					self._tasks.on_tick.cancel()
					await self._tasks.on_tick
			except asyncio.exceptions.CancelledError:
				pass
			except Exception as exception:
				self.ignore_exception(exception)

			if self._configuration.strategy.cancel_all_orders_on_stop:
				try:
					await self._cancel_all_orders()
				except Exception as exception:
					self.ignore_exception(exception)

			if self._configuration.strategy.withdraw_market_on_stop:
				try:
					await self._market_withdraw()
				except Exception as exception:
					self.ignore_exception(exception)
		finally:
			await self.exit()

			self.log(INFO, "end")

	async def exit(self):
		self.log(INFO, "start")
		self.log(INFO, "end")

	async def on_tick(self):
		try:
			self.log(INFO, "start")

			while self._can_run:
				try:
					self.log(INFO, "loop - waiting")

					await self._events.on_tick.wait()

					self.log(INFO, "loop - start")

					self._is_busy = True

					if self._configuration.strategy.withdraw_market_on_tick:
						try:
							await self._market_withdraw()
						except Exception as exception:
							self.ignore_exception(exception)

					open_orders = await self._get_open_orders(use_cache=False)
					await self._get_filled_orders(use_cache=False)
					await self._get_balances(use_cache=False)

					open_orders_ids = list(open_orders.keys())
					await self._cancel_currently_untracked_orders(open_orders_ids)

					proposed_orders: List[Order] = await self._create_proposal()
					candidate_orders: List[Order] = await self._adjust_proposal_to_budget(proposed_orders)

					await self._replace_orders(candidate_orders)
				except Exception as exception:
					self.ignore_exception(exception)
				finally:
					waiting_time = self._calculate_waiting_time(self._configuration.strategy.tick_interval)

					self._refresh_timestamp = waiting_time + self.clock.now()
					(self._refresh_timestamp, self._events.on_tick) = self.clock.register(self._refresh_timestamp)
					self._is_busy = False

					self.log(INFO, "loop - end")

					if self._configuration.strategy.run_only_once:
						await self.stop()

					self.log(INFO, f"loop - sleeping for {waiting_time}...")
					await asyncio.sleep(waiting_time)
					self.log(INFO, "loop - awaken")
		finally:
			self.log(INFO, "end")

	async def _create_proposal(self) -> List[Order]:
		try:
			self.log(INFO, "start")

			order_book = await self._get_order_book()
			bids, asks = self._parse_order_book(order_book)

			ticker_price = await self._get_market_price()
			try:
				last_filled_order_price = await self._get_last_filled_order_price()
			except Exception as exception:
				self.ignore_exception(exception)

				last_filled_order_price = DECIMAL_ZERO

			price_strategy = PriceStrategy[self._configuration.strategy.get("price_strategy", PriceStrategy.TICKER.name)]
			if price_strategy == PriceStrategy.TICKER:
				used_price = ticker_price
			elif price_strategy == PriceStrategy.MIDDLE:
				middle_price_strategy = MiddlePriceStrategy[self._configuration.strategy.get("middle_price_strategy", MiddlePriceStrategy.SAP.name)]

				used_price = await self._get_market_middle_price(
					bids,
					asks,
					middle_price_strategy
				)
			elif price_strategy == PriceStrategy.LAST_FILL:
				used_price = last_filled_order_price
			else:
				raise ValueError("""Invalid "strategy.middle_price_strategy" configuration value.""")

			if used_price is None or used_price <= DECIMAL_ZERO:
				raise ValueError(f"Invalid price: {used_price}")

			minimum_price_increment = Decimal(self._market.minimumPriceIncrement)
			minimum_order_size = Decimal(self._market.minimumOrderSize)

			client_id = 1
			proposal = []

			bid_orders = []
			for index, layer in enumerate(self._configuration.strategy.layers, start=1):
				best_ask = Decimal(next(iter(asks), {"price": FLOAT_INFINITY}).price)
				bid_quantity = int(layer.bid.quantity)
				bid_spread_percentage = Decimal(layer.bid.spread_percentage)
				bid_market_price = ((100 - bid_spread_percentage) / 100) * min(used_price, best_ask)
				bid_max_liquidity_in_dollars = Decimal(layer.bid.max_liquidity_in_dollars)
				bid_size = bid_max_liquidity_in_dollars / bid_market_price / bid_quantity if bid_quantity > 0 else 0

				if bid_market_price < minimum_price_increment:
					self.log(WARNING, f"""Skipping orders placement from layer {index}, bid price too low:\n\n{'{:^30}'.format(round(bid_market_price, 6))}""")
				elif bid_size < minimum_order_size:
					self.log(WARNING, f"""Skipping orders placement from layer {index}, bid size too low:\n\n{'{:^30}'.format(round(bid_size, 9))}""")
				else:
					for i in range(bid_quantity):
						bid_order = Order()
						bid_order.client_id = str(client_id)
						bid_order.market_name = self._market_name
						bid_order.type = OrderType.LIMIT
						bid_order.side = OrderSide.BUY
						bid_order.amount = bid_size
						bid_order.price = bid_market_price

						bid_orders.append(bid_order)

						client_id += 1

			ask_orders = []
			for index, layer in enumerate(self._configuration.strategy.layers, start=1):
				best_bid = Decimal(next(iter(bids), {"price": FLOAT_ZERO}).price)
				ask_quantity = int(layer.ask.quantity)
				ask_spread_percentage = Decimal(layer.ask.spread_percentage)
				ask_market_price = ((100 + ask_spread_percentage) / 100) * max(used_price, best_bid)
				ask_max_liquidity_in_dollars = Decimal(layer.ask.max_liquidity_in_dollars)
				ask_size = ask_max_liquidity_in_dollars / ask_market_price / ask_quantity if ask_quantity > 0 else 0

				if ask_market_price < minimum_price_increment:
					self.log(WARNING, f"""Skipping orders placement from layer {index}, ask price too low:\n\n{'{:^30}'.format(round(ask_market_price, 9))}""", True)
				elif ask_size < minimum_order_size:
					self.log(WARNING, f"""Skipping orders placement from layer {index}, ask size too low:\n\n{'{:^30}'.format(round(ask_size, 9))}""", True)
				else:
					for i in range(ask_quantity):
						ask_order = Order()
						ask_order.client_id = str(client_id)
						ask_order.market_name = self._market_name
						ask_order.type = OrderType.LIMIT
						ask_order.side = OrderSide.SELL
						ask_order.amount = ask_size
						ask_order.price = ask_market_price

						ask_orders.append(ask_order)

						client_id += 1

			proposal = [*proposal, *bid_orders, *ask_orders]

			self.log(DEBUG, f"""proposal:\n{dump(proposal)}""")

			return proposal
		finally:
			self.log(INFO, "end")

	async def _adjust_proposal_to_budget(self, candidate_proposal: List[Order]) -> List[Order]:
		try:
			self.log(INFO, "start")

			adjusted_proposal: List[Order] = []

			balances = await self._get_balances()
			base_balance = Decimal(balances.tokens[self._base_token.id].free)
			quote_balance = Decimal(balances.tokens[self._quote_token.id].free)
			current_base_balance = base_balance
			current_quote_balance = quote_balance

			for order in candidate_proposal:
				if order.side == OrderSide.BUY:
					if current_quote_balance > order.amount:
						current_quote_balance -= order.amount
						adjusted_proposal.append(order)
					else:
						continue
				elif order.side == OrderSide.SELL:
					if current_base_balance > order.amount:
						current_base_balance -= order.amount
						adjusted_proposal.append(order)
					else:
						continue
				else:
					raise ValueError(f"""Unrecognized order size "{order.side}".""")

			self.log(DEBUG, f"""adjusted_proposal:\n{dump(adjusted_proposal)}""")

			return adjusted_proposal
		finally:
			self.log(INFO, "end")

	async def _get_base_ticker_price(self) -> Decimal:
		try:
			self.log(INFO, "start")

			return Decimal((await self._get_ticker(use_cache=False)).price)
		finally:
			self.log(INFO, "end")

	async def _get_last_filled_order_price(self) -> Decimal:
		try:
			self.log(INFO, "start")

			last_filled_order = await self._get_last_filled_order()

			if last_filled_order:
				return Decimal(last_filled_order.price)
			else:
				return DECIMAL_NAN
		finally:
			self.log(INFO, "end")

	async def _get_market_price(self) -> Decimal:
		return await self._get_base_ticker_price()

	async def _get_market_middle_price(self, bids, asks, strategy: MiddlePriceStrategy = None) -> Decimal:
		try:
			self.log(INFO, "start")

			if strategy:
				return self._calculate_middle_price(bids, asks, strategy)

			try:
				return self._calculate_middle_price(bids, asks, MiddlePriceStrategy.VWAP)
			except (Exception,):
				try:
					return self._calculate_middle_price(bids, asks, MiddlePriceStrategy.WAP)
				except (Exception,):
					try:
						return self._calculate_middle_price(bids, asks, MiddlePriceStrategy.SAP)
					except (Exception,):
						return await self._get_market_price()
		finally:
			self.log(INFO, "end")

	async def _get_base_balance(self) -> Decimal:
		try:
			self.log(INFO, "start")

			base_balance = Decimal((await self._get_balances())[self._base_token.id].free)

			return base_balance
		finally:
			self.log(INFO, "end")

	async def _get_quote_balance(self) -> Decimal:
		try:
			self.log(INFO, "start")

			quote_balance = Decimal((await self._get_balances())[self._quote_token.id].free)

			return quote_balance
		finally:
			self.log(INFO, "start")

	async def _get_balances(self, use_cache: bool = True) -> DotMap[str, Any]:
		try:
			self.log(INFO, "start")

			response = None
			try:
				request = {
					"chain": self._configuration.chain,
					"network": self._configuration.network,
					"connector": self._configuration.connector,
					"ownerAddress": self._wallet_address,
					"tokenIds": [KUJIRA_NATIVE_TOKEN.id, self._base_token.id, self._quote_token.id]
				}

				self.log(DEBUG, f"""gateway.kujira_get_balances: request:\n{dump(request)}""")

				if use_cache and self._balances is not None:
					response = self._balances
				else:
					response = await Gateway.kujira_get_balances(request)

					self._balances = DotMap(copy.deepcopy(response), _dynamic=False)

					self._balances.total.free = Decimal(self._balances.total.free)
					self._balances.total.lockedInOrders = Decimal(self._balances.total.lockedInOrders)
					self._balances.total.unsettled = Decimal(self._balances.total.unsettled)

					for (token, balance) in DotMap(response.tokens).items():
						balance.free = Decimal(balance.free)
						balance.lockedInOrders = Decimal(balance.lockedInOrders)
						balance.unsettled = Decimal(balance.unsettled)

				return response
			except Exception as exception:
				response = traceback.format_exc()

				raise exception
			finally:
				self.log(DEBUG, f"""gateway.kujira_get_balances: response:\n{dump(response)}""")
		finally:
			self.log(INFO, "end")

	async def _get_market(self):
		try:
			self.log(INFO, "start")

			request = None
			response = None
			try:
				request = {
					"chain": self._configuration.chain,
					"network": self._configuration.network,
					"connector": self._configuration.connector,
					"name": self._market_name
				}

				self.log(DEBUG, f"""gateway.kujira_get_market: request:\n{dump(request)}""")

				response = await Gateway.kujira_get_market(request)

				return response
			except Exception as exception:
				response = traceback.format_exc()

				raise exception
			finally:
				self.log(DEBUG, f"""gateway.kujira_get_market: response:\n{dump(response)}""")
		finally:
			self.log(INFO, "end")

	async def _get_order_book(self):
		try:
			self.log(INFO, "start")

			request = None
			response = None
			try:
				request = {
					"chain": self._configuration.chain,
					"network": self._configuration.network,
					"connector": self._configuration.connector,
					"marketId": self._market.id
				}

				self.log(DEBUG, f"""gateway.kujira_get_order_books: request:\n{dump(request)}""")

				response = await Gateway.kujira_get_order_book(request)

				return response
			except Exception as exception:
				response = traceback.format_exc()

				raise exception
			finally:
				self.log(DEBUG, f"""gateway.kujira_get_order_books: response:\n{dump(response)}""")
		finally:
			self.log(INFO, "end")

	async def _get_ticker(self, use_cache: bool = True) -> DotMap[str, Any]:
		try:
			self.log(INFO, "start")

			request = None
			response = None
			try:
				request = {
					"chain": self._configuration.chain,
					"network": self._configuration.network,
					"connector": self._configuration.connector,
					"marketId": self._market.id
				}

				self.log(DEBUG, f"""gateway.kujira_get_ticker: request:\n{dump(request)}""")

				if use_cache and self._tickers is not None:
					response = self._tickers
				else:
					response = await Gateway.kujira_get_ticker(request)

					self._tickers = response

				return response
			except Exception as exception:
				response = exception

				raise exception
			finally:
				self.log(DEBUG, f"""gateway.kujira_get_ticker: response:\n{dump(response)}""")

		finally:
			self.log(INFO, "end")

	async def _get_open_orders(self, use_cache: bool = True) -> DotMap[str, Any]:
		try:
			self.log(INFO, "start")

			request = None
			response = None
			try:
				request = {
					"chain": self._configuration.chain,
					"network": self._configuration.network,
					"connector": self._configuration.connector,
					"marketId": self._market.id,
					"ownerAddress": self._wallet_address,
					"status": OrderStatus.OPEN.value[0]
				}

				self.log(DEBUG, f"""gateway.kujira_get_open_orders: request:\n{dump(request)}""")

				if use_cache and self._open_orders is not None:
					response = self._open_orders
				else:
					response = await Gateway.kujira_get_orders(request)
					self._open_orders = response

				return response
			except Exception as exception:
				response = traceback.format_exc()

				raise exception
			finally:
				self.log(DEBUG, f"""gateway.kujira_get_open_orders: response:\n{dump(response)}""")
		finally:
			self.log(INFO, "end")

	async def _get_last_filled_order(self) -> DotMap[str, Any]:
		try:
			self.log(INFO, "start")

			filled_orders = await self._get_filled_orders()

			if len((filled_orders or {})):
				last_filled_order = list(DotMap(filled_orders).values())[0]
			else:
				last_filled_order = None

			return last_filled_order
		finally:
			self.log(INFO, "end")

	async def _get_filled_orders(self, use_cache: bool = True) -> DotMap[str, Any]:
		try:
			self.log(INFO, "start")

			request = None
			response = None
			try:
				request = {
					"chain": self._configuration.chain,
					"network": self._configuration.network,
					"connector": self._configuration.connector,
					"marketId": self._market.id,
					"ownerAddress": self._wallet_address,
					"status": OrderStatus.FILLED.value[0]
				}

				self.log(DEBUG, f"""gateway.kujira_get_filled_orders: request:\n{dump(request)}""")

				if use_cache and self._filled_orders is not None:
					response = self._filled_orders
				else:
					response = await Gateway.kujira_get_orders(request)
					self._filled_orders = response

				return response
			except Exception as exception:
				response = traceback.format_exc()

				raise exception
			finally:
				self.log(DEBUG, f"""gateway.kujira_get_filled_orders: response:\n{dump(response)}""")

		finally:
			self.log(INFO, "end")

	async def _replace_orders(self, proposal: List[Order]) -> DotMap[str, Any]:
		try:
			self.log(INFO, "start")

			response = None
			try:
				orders = []
				for candidate in proposal:
					order_type = OrderType[self._configuration.strategy.get("kujira_order_type", OrderType.LIMIT.name)]

					orders.append({
						"clientId": candidate.client_id,
						"marketId": self._market.id,
						"ownerAddress": self._wallet_address,
						"side": candidate.side.value[0],
						"price": str(candidate.price),
						"amount": str(candidate.amount),
						"type": order_type.value[0],
					})

				request = {
					"chain": self._configuration.chain,
					"network": self._configuration.network,
					"connector": self._configuration.connector,
					"orders": orders
				}

				self.log(DEBUG, f"""gateway.kujira_post_orders: request:\n{dump(request)}""")

				if len(orders):
					response = await Gateway.kujira_post_orders(request)

					self._currently_tracked_orders_ids = list(response.keys())
					self._tracked_orders_ids.extend(self._currently_tracked_orders_ids)
				else:
					self.log(WARNING, "No order was defined for placement/replacement. Skipping.", True)
					response = []

				return response
			except Exception as exception:
				response = traceback.format_exc()

				raise exception
			finally:
				self.log(DEBUG, f"""gateway.kujira_post_orders: response:\n{dump(response)}""")
		finally:
			self.log(INFO, "end")

	async def _cancel_currently_untracked_orders(self, open_orders_ids: List[str]):
		try:
			self.log(INFO, "start")

			request = None
			response = None
			try:
				untracked_orders_ids = list(
					set(self._tracked_orders_ids).intersection(set(open_orders_ids)) - set(self._currently_tracked_orders_ids))

				if len(untracked_orders_ids) > 0:
					request = {
						"chain": self._configuration.chain,
						"network": self._configuration.network,
						"connector": self._configuration.connector,
						"ids": untracked_orders_ids,
						"marketId": self._market.id,
						"ownerAddress": self._wallet_address,
					}

					self.log(DEBUG, f"""gateway.kujira_delete_orders: request:\n{dump(request)}""")

					response = await Gateway.kujira_delete_orders(request)
				else:
					self.log(DEBUG, "No order needed to be canceled.")
					response = {}

				return response
			except Exception as exception:
				response = traceback.format_exc()

				raise exception
			finally:
				self.log(DEBUG, f"""gateway.kujira_delete_orders: response:\n{dump(response)}""")
		finally:
			self.log(INFO, "end")

	async def _cancel_all_orders(self):
		try:
			self.log(INFO, "start")

			request = None
			response = None
			try:
				request = {
					"chain": self._configuration.chain,
					"network": self._configuration.network,
					"connector": self._configuration.connector,
					"marketId": self._market.id,
					"ownerAddress": self._wallet_address,
				}

				self.log(DEBUG, f"""gateway.clob_delete_orders: request:\n{dump(request)}""")

				response = await Gateway.kujira_delete_orders_all(request)
			except Exception as exception:
				response = traceback.format_exc()

				raise exception
			finally:
				self.log(DEBUG, f"""gateway.clob_delete_orders: response:\n{dump(response)}""")
		finally:
			self.log(INFO, "end")

	async def _market_withdraw(self):
		try:
			self.log(INFO, "start")

			response = None
			try:
				request = {
					"chain": self._configuration.chain,
					"network": self._configuration.network,
					"connector": self._configuration.connector,
					"marketId": self._market.id,
					"ownerAddress": self._wallet_address,
				}

				self.log(DEBUG, f"""gateway.kujira_post_market_withdraw: request:\n{dump(request)}""")

				response = await Gateway.kujira_post_market_withdraw(request)
			except Exception as exception:
				response = traceback.format_exc()

				raise exception
			finally:
				self.log(DEBUG, f"""gateway.kujira_post_market_withdraw: response:\n{dump(response)}""")
		finally:
			self.log(INFO, "end")

	async def _get_remaining_orders_ids(self, candidate_orders, created_orders) -> List[str]:
		self.log(INFO, "end")

		try:
			candidate_orders_client_ids = [order.client_id for order in candidate_orders] if len(candidate_orders) else []
			created_orders_client_ids = [order.clientId for order in created_orders.values()] if len(
				created_orders) else []
			remaining_orders_client_ids = list(set(candidate_orders_client_ids) - set(created_orders_client_ids))
			remaining_orders_ids = list(
				filter(lambda order: (order.clientId in remaining_orders_client_ids), created_orders.values()))

			self.log(DEBUG, f"""remaining_orders_ids:\n{dump(remaining_orders_ids)}""")

			return remaining_orders_ids
		finally:
			self.log(INFO, "end")

	async def _get_duplicated_orders_ids(self) -> List[str]:
		self.log(INFO, "start")

		try:
			open_orders = (await self._get_open_orders()).values()

			open_orders_map = {}
			duplicated_orders_ids = []

			for open_order in open_orders:
				if open_order.clientId == "0":  # Avoid touching manually created orders.
					continue
				elif open_order.clientId not in open_orders_map:
					open_orders_map[open_order.clientId] = [open_order]
				else:
					open_orders_map[open_order.clientId].append(open_order)

			for orders in open_orders_map.values():
				orders.sort(key=lambda order: order.id)

				duplicated_orders_ids = [
					*duplicated_orders_ids,
					*[order.id for order in orders[:-1]]
				]

			self.log(DEBUG, f"""duplicated_orders_ids:\n{dump(duplicated_orders_ids)}""")

			return duplicated_orders_ids
		finally:
			self.log(INFO, "end")

	# noinspection PyMethodMayBeStatic
	def _parse_order_book(self, orderbook: DotMap[str, Any]) -> List[Union[List[DotMap[str, Any]], List[DotMap[str, Any]]]]:
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

	@staticmethod
	def _split_percentage(bids: [DotMap[str, Any]], asks: [DotMap[str, Any]]) -> List[Any]:
		asks = asks[:math.ceil((VWAP_THRESHOLD / 100) * len(asks))]
		bids = bids[:math.ceil((VWAP_THRESHOLD / 100) * len(bids))]

		return [bids, asks]

	# noinspection PyMethodMayBeStatic
	def _compute_volume_weighted_average_price(self, book: [DotMap[str, Any]]) -> np.array:
		prices = [float(order['price']) for order in book]
		amounts = [float(order['amount']) for order in book]

		prices = np.array(prices)
		amounts = np.array(amounts)

		vwap = (np.cumsum(amounts * prices) / np.cumsum(amounts))

		return vwap

	# noinspection PyMethodMayBeStatic
	def _remove_outliers(self, order_book: [DotMap[str, Any]], side: OrderSide) -> [DotMap[str, Any]]:
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

	def _calculate_middle_price(
		self,
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
			bids, asks = self._split_percentage(bids, asks)

			if len(bids) > 0:
				bids = self._remove_outliers(bids, OrderSide.BUY)

			if len(asks) > 0:
				asks = self._remove_outliers(asks, OrderSide.SELL)

			book = [*bids, *asks]

			if len(book) > 0:
				vwap = self._compute_volume_weighted_average_price(book)

				return Decimal(vwap[-1])
			else:
				return DECIMAL_ZERO
		else:
			raise ValueError(f'Unrecognized mid price strategy "{strategy}".')
