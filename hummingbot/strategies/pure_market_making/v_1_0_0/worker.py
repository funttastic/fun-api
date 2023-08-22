import asyncio
import copy
import math
import os
import textwrap
import traceback
from array import array
from decimal import Decimal
from logging import DEBUG, INFO, WARNING, CRITICAL
from typing import Any, List, Optional

import yaml
from dotmap import DotMap

from hummingbot.constants import DECIMAL_NAN, DEFAULT_PRECISION
from hummingbot.constants import KUJIRA_NATIVE_TOKEN, DECIMAL_ZERO, FLOAT_ZERO, FLOAT_INFINITY
from hummingbot.gateway import Gateway
from hummingbot.strategies.worker_base import WorkerBase
from hummingbot.utils import OrderSide, OrderType, Order, OrderStatus, \
	MiddlePriceStrategy, PriceStrategy
from hummingbot.utils import calculate_middle_price, format_currency, format_lines, format_line, format_percentage, \
	alignment_column, parse_order_book
from properties import properties
from utils import dump, deep_merge, log_class_exceptions


# @log_class_exceptions
class Worker(WorkerBase):
	CATEGORY = "worker"

	def __init__(self, parent: Any, client_id: str):
		try:
			self._parent = parent
			self._client_id = client_id

			self._configuration: DotMap[str, Any]
			self._reload_configuration()

			self.id = f"""{self._parent.base_id}:{self.CATEGORY}:{self._configuration.id}"""

			self.log(INFO, "start")

			super().__init__()

			self._can_run: bool = True
			self._is_busy: bool = False
			self._initialized = False
			self._first_time = True
			self._refresh_timestamp: int = 0
			self._wallet_address = None
			self._market: DotMap[str, Any]
			self._market_name = None
			self._base_token: DotMap[str, Any]
			self._quote_token: DotMap[str, Any]
			self._quote_token_name = None
			self._base_token_name = None
			self._tickers: DotMap[str, Any]
			self._balances: DotMap[str, Any] = DotMap({}, _dynamic=False)
			self._all_tracked_orders_ids: [str] = []
			self._currently_tracked_orders_ids: [str] = []
			self._open_orders: DotMap[str, Any]
			self._filled_orders: DotMap[str, Any]

			self._wallet_previous_value: Optional[float] = None
			self._token_previous_price: Optional[float] = None
			self._wallet_current_value: Optional[float] = None
			self._token_current_price: Optional[float] = None

			self._tasks: DotMap[str, asyncio.Task] = DotMap({
				"on_tick": None,
				"markets": None,
				"order_books": None,
				"tickers": None,
				"orders": None,
				"balances": None,
			}, _dynamic=False)

			self.summary: DotMap[str, Any] = DotMap({
				"configurations": {
					"order_type": str,
					"price_strategy": str,
					"middle_price_strategy": str,
					"use_adjusted_price": bool
				},
				"balance": {
					"wallet": {
						"base": DECIMAL_ZERO,
						"quote": DECIMAL_ZERO
					},
					"orders": {
						"quote": {
							"bids": DECIMAL_ZERO,
							"asks": DECIMAL_ZERO,
							"total": DECIMAL_ZERO,
						}
					}
				},
				"orders": {
					"replaced": DotMap({}, _dynamic=False),
					"canceled": DotMap({}, _dynamic=False),
				},
				"wallet": {
					"initial_value": DECIMAL_ZERO,
					"previous_value": DECIMAL_ZERO,
					"current_value": DECIMAL_ZERO,
					"current_initial_pnl": DECIMAL_ZERO,
					"current_previous_pnl": DECIMAL_ZERO,
				},
				"token": {
					"initial_price": DECIMAL_ZERO,
					"previous_price": DECIMAL_ZERO,
					"current_price": DECIMAL_ZERO,
					"current_initial_pnl": DECIMAL_ZERO,
					"current_previous_pnl": DECIMAL_ZERO,
				},
				"price": {
					"used_price": DECIMAL_ZERO,
					"ticker_price": DECIMAL_ZERO,
					"last_filled_order_price": DECIMAL_ZERO,
					"expected_price": DECIMAL_ZERO,
					"adjusted_market_price": DECIMAL_ZERO,
					"sap": DECIMAL_ZERO,
					"wap": DECIMAL_ZERO,
					"vwap": DECIMAL_ZERO,
				}
			}, _dynamic=False)

			self._events: DotMap[str, asyncio.Event] = DotMap({
				"on_tick": None,
			}, _dynamic=False)
		finally:
			self.log(INFO, "end")

	def _reload_configuration(self):
		self.log(INFO, "start")

		root_path = properties.get('app_root_path')
		base_path = os.path.join(root_path, "resources", "strategies", self._parent.ID, self._parent.VERSION)

		configuration = {}

		with open(os.path.join(base_path, "common.yml"), 'r') as stream:
			target = yaml.safe_load(stream) or {}
			configuration = deep_merge(copy.deepcopy(configuration), target)

		with open(os.path.join(base_path, "workers", "common.yml"), 'r') as stream:
			target = yaml.safe_load(stream) or {}
			configuration = deep_merge(copy.deepcopy(configuration), target)

		with open(os.path.join(base_path, "workers", f"{self._client_id}.yml"), 'r') as stream:
			target = yaml.safe_load(stream) or {}
			configuration = deep_merge(copy.deepcopy(configuration), target)

		self._configuration = DotMap(configuration, _dynamic=False)

		self.log(INFO, "end")

	async def initialize(self):
		try:
			self.log(INFO, "start")

			self._initialized = False

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

			self.clock.start()
			self._refresh_timestamp = self.clock.now()
			(self._refresh_timestamp, self._events.on_tick) = self.clock.register(self._refresh_timestamp)

			self._initialized = True
			self._can_run = True
		except Exception as exception:
			self.ignore_exception(exception)

			raise exception
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

			if self._initialized:
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

					self._reload_configuration()

					# noinspection PyTypedDict
					self.summary.orders.canceled = {}

					if self._configuration.strategy.withdraw_market_on_tick:
						try:
							await self._market_withdraw()
						except Exception as exception:
							self.ignore_exception(exception)

					await self._get_filled_orders(use_cache=False)
					await self._get_balances(use_cache=False)

					proposed_orders: List[Order] = await self._create_proposal()
					candidate_orders: List[Order] = await self._adjust_proposal_to_budget(proposed_orders)

					await self._replace_orders(candidate_orders)

					open_orders = await self._get_open_orders(use_cache=False)
					open_orders_ids = list(open_orders.keys())
					await self._cancel_currently_untracked_orders(open_orders_ids)

					balances = await self._get_balances(use_cache=False)

					self.summary.balance.wallet.base = Decimal(balances.tokens[self._base_token.id].total)
					self.summary.balance.wallet.quote = Decimal(balances.tokens[self._quote_token.id].total)

					if self._first_time is False:
						self._show_summary()

					self._first_time = False

					await self._should_stop_loss()
				except Exception as exception:
					self.ignore_exception(exception)
				finally:
					waiting_time = self._calculate_waiting_time(self._configuration.strategy.tick_interval)

					self._refresh_timestamp = waiting_time + self.clock.now()
					(self._refresh_timestamp, self._events.on_tick) = self.clock.register(self._refresh_timestamp)

					self.log(INFO, "loop - end")

					if self._configuration.strategy.run_only_once:
						await self.stop()

					self._is_busy = False

					self.log(INFO, f"loop - sleeping for {waiting_time}...")
					await asyncio.sleep(waiting_time)
					self.log(INFO, "loop - awaken")
		finally:
			self.log(INFO, "end")

	async def _create_proposal(self) -> List[Order]:
		try:
			self.log(INFO, "start")

			order_book = await self._get_order_book()
			bids, asks = parse_order_book(order_book)

			ticker_price = await self._get_market_price(use_cache=False)
			try:
				last_filled_order_price = await self._get_last_filled_order_price()
			except Exception as exception:
				self.ignore_exception(exception)

				last_filled_order_price = DECIMAL_ZERO

			self._price_strategy = PriceStrategy[self._configuration.strategy.get("price_strategy", PriceStrategy.TICKER.name)]
			if self._price_strategy == PriceStrategy.TICKER:
				self._used_price = ticker_price
			elif self._price_strategy == PriceStrategy.MIDDLE:
				self._middle_price_strategy = MiddlePriceStrategy[
					self._configuration.strategy.get("middle_price_strategy", MiddlePriceStrategy.SAP.name)
				]

				self._used_price = await self._get_market_middle_price(
					bids,
					asks,
					self._middle_price_strategy
				)
			elif self._price_strategy == PriceStrategy.LAST_FILL:
				self._used_price = last_filled_order_price
			else:
				raise ValueError("""Invalid "strategy.middle_price_strategy" configuration value.""")

			if self._used_price is None or self._used_price <= DECIMAL_ZERO:
				raise ValueError(f"Invalid price: {self._used_price}")

			self._order_type = OrderType[self._configuration.strategy.get("order_type", OrderType.LIMIT.name)]

			minimum_price_increment = Decimal(self._market.minimumPriceIncrement)
			minimum_order_size = Decimal(self._market.minimumOrderSize)

			client_id = 1
			proposal = []

			bid_orders = []
			for index, layer in enumerate(self._configuration.strategy.layers, start=1):
				best_ask = Decimal(next(iter(asks), {"price": FLOAT_INFINITY}).price)
				bid_quantity = int(layer.bid.quantity)
				bid_spread_percentage = Decimal(layer.bid.spread_percentage)
				bid_market_price = ((100 - bid_spread_percentage) / 100) * min(self._used_price, best_ask)
				bid_max_liquidity_in_dollars = Decimal(layer.bid.max_liquidity_in_dollars)
				bid_size = bid_max_liquidity_in_dollars / bid_market_price / bid_quantity if bid_quantity > 0 else 0

				if not (bid_quantity > 0):
					continue

				if bid_market_price < minimum_price_increment:
					self.log(WARNING, f"""Skipping orders placement from layer {index}, bid price too low:\n\n{'{:^30}'.format(round(bid_market_price, 6))}""")
				elif bid_size < minimum_order_size:
					self.log(WARNING, f"""Skipping orders placement from layer {index}, bid size too low:\n\n{'{:^30}'.format(round(bid_size, 9))}""")
				else:
					for i in range(bid_quantity):
						bid_order = Order()
						bid_order.client_id = str(client_id)
						bid_order.market_name = self._market_name
						bid_order.type = self._order_type
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
				ask_market_price = ((100 + ask_spread_percentage) / 100) * max(self._used_price, best_bid)
				ask_max_liquidity_in_dollars = Decimal(layer.ask.max_liquidity_in_dollars)
				ask_size = ask_max_liquidity_in_dollars / ask_market_price / ask_quantity if ask_quantity > 0 else 0

				if not (ask_quantity > 0):
					continue

				if ask_market_price < minimum_price_increment:
					self.log(WARNING, f"""Skipping orders placement from layer {index}, ask price too low:\n\n{'{:^30}'.format(round(ask_market_price, 9))}""", True)
				elif ask_size < minimum_order_size:
					self.log(WARNING, f"""Skipping orders placement from layer {index}, ask size too low:\n\n{'{:^30}'.format(round(ask_size, 9))}""", True)
				else:
					for i in range(ask_quantity):
						ask_order = Order()
						ask_order.client_id = str(client_id)
						ask_order.market_name = self._market_name
						ask_order.type = self._order_type
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

	async def _get_base_ticker_price(self, use_cache: bool = True) -> Decimal:
		try:
			self.log(INFO, "start")

			return Decimal((await self._get_ticker(use_cache=use_cache)).price)
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

	async def _get_market_price(self, use_cache: bool = True) -> Decimal:
		return await self._get_base_ticker_price(use_cache=use_cache)

	async def _get_market_middle_price(self, bids, asks, strategy: MiddlePriceStrategy = None) -> Decimal:
		try:
			self.log(INFO, "start")

			if strategy:
				return calculate_middle_price(bids, asks, strategy)

			try:
				return calculate_middle_price(bids, asks, MiddlePriceStrategy.VWAP)
			except (Exception,):
				try:
					return calculate_middle_price(bids, asks, MiddlePriceStrategy.WAP)
				except (Exception,):
					try:
						return calculate_middle_price(bids, asks, MiddlePriceStrategy.SAP)
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
					self._balances.total.total = Decimal(self._balances.total.total)

					for (token, balance) in DotMap(response.tokens).items():
						balance.free = Decimal(balance.free)
						balance.lockedInOrders = Decimal(balance.lockedInOrders)
						balance.unsettled = Decimal(balance.unsettled)
						balance.total = Decimal(balance.total)

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

			# request = None
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

			# request = None
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

			# request = None
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

			# request = None
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

			# request = None
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
					orders.append({
						"clientId": candidate.client_id,
						"marketId": self._market.id,
						"ownerAddress": self._wallet_address,
						"side": candidate.side.value[0],
						"price": str(candidate.price),
						"amount": str(candidate.amount),
						"type": self._order_type.value[0],
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
					self._all_tracked_orders_ids.extend(self._currently_tracked_orders_ids)
				else:
					self.log(WARNING, "No order was defined for placement/replacement. Skipping.", True)
					response = []

				return response
			except Exception as exception:
				response = traceback.format_exc()

				raise exception
			finally:
				self.summary.orders.replaced = response

				self.log(DEBUG, f"""gateway.kujira_post_orders: response:\n{dump(response)}""")
		finally:
			self.log(INFO, "end")

	async def _cancel_currently_untracked_orders(self, open_orders_ids: List[str]):
		try:
			self.log(INFO, "start")

			# request = None
			response = None
			try:
				untracked_orders_ids = list(
					set(self._all_tracked_orders_ids).intersection(set(open_orders_ids)) - set(
						self._currently_tracked_orders_ids))

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

					# noinspection PyTypedDict
					self.summary.orders.canceled = {**self.summary.orders.canceled, **response}

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

			# request = None
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

	async def _should_stop_loss(self):
		try:
			self.log(INFO, """start""")

			balances = await self._get_balances()

			if self.summary.wallet.initial_value == DECIMAL_ZERO:
				self.summary.token.initial_price = await self._get_market_price()
				self.summary.token.previous_price = self.summary.token.initial_price
				self.summary.token.current_price = self.summary.token.initial_price

				self.summary.wallet.initial_value = balances.total.total
				self.summary.wallet.previous_value = self.summary.wallet.initial_value
				self.summary.wallet.current_value = self.summary.wallet.initial_value
			else:
				max_wallet_loss_from_initial_value = round(self._configuration.strategy.kill_switch.max_wallet_loss_from_initial_value, 9)
				max_wallet_loss_from_previous_value = round(self._configuration.strategy.kill_switch.max_wallet_loss_from_previous_value, 9)
				max_wallet_loss_compared_to_token_variation = round(self._configuration.strategy.kill_switch.max_wallet_loss_compared_to_token_variation, 9)
				max_token_loss_from_initial = round(self._configuration.strategy.kill_switch.max_token_loss_from_initial, 9)

				self.summary.token.previous_price = self.summary.token.current_price
				self.summary.token.current_price = await self._get_market_price()

				open_orders_balance = await self._get_open_orders_balance()
				self.summary.balance.orders.base.bids = open_orders_balance.quote / self.summary.token.current_price
				self.summary.balance.orders.base.asks = open_orders_balance.base
				self.summary.balance.orders.base.total = self.summary.balance.orders.base.bids + self.summary.balance.orders.base.asks
				self.summary.balance.orders.quote.bids = open_orders_balance.quote
				self.summary.balance.orders.quote.asks = open_orders_balance.base * self.summary.token.current_price
				self.summary.balance.orders.quote.total = self.summary.balance.orders.quote.bids + self.summary.balance.orders.quote.asks

				self.summary.wallet.previous_value = self.summary.wallet.current_value
				self.summary.wallet.current_value = balances.total.total

				wallet_previous_initial_pnl = Decimal(round(
					100 * ((self.summary.wallet.previous_value / self.summary.wallet.initial_value) - 1),
					DEFAULT_PRECISION
				))
				wallet_current_initial_pnl = Decimal(round(
					100 * ((self.summary.wallet.current_value / self.summary.wallet.initial_value) - 1),
					DEFAULT_PRECISION
				))
				wallet_current_previous_pnl = Decimal(round(
					100 * ((self.summary.wallet.current_value / self.summary.wallet.previous_value) - 1),
					DEFAULT_PRECISION
				))
				token_previous_initial_pnl = Decimal(round(
					100 * ((self.summary.token.previous_price / self.summary.token.initial_price) - 1),
					DEFAULT_PRECISION
				))
				token_current_initial_pnl = Decimal(round(
					100 * ((self.summary.token.current_price / self.summary.token.initial_price) - 1),
					DEFAULT_PRECISION
				))
				token_current_previous_pnl = Decimal(round(
					100 * ((self.summary.token.current_price / self.summary.token.previous_price) - 1),
					DEFAULT_PRECISION
				))

				self.summary.wallet.previous_initial_pnl = wallet_previous_initial_pnl
				self.summary.wallet.current_initial_pnl = wallet_current_initial_pnl
				self.summary.wallet.current_previous_pnl = wallet_current_previous_pnl
				self.summary.token.previous_initial_pnl = token_previous_initial_pnl
				self.summary.token.current_initial_pnl = token_current_initial_pnl
				self.summary.token.current_previous_pnl = token_current_previous_pnl

				users = ', '.join(self._configuration.strategy.kill_switch.notify.telegram.users)

				if wallet_current_initial_pnl < 0:
					if self._configuration.strategy.kill_switch.max_wallet_loss_from_initial_value:
						if math.fabs(wallet_current_initial_pnl) >= math.fabs(max_wallet_loss_from_initial_value):
							self.log(CRITICAL, f"""The bot has been stopped because the wallet lost {-wallet_current_initial_pnl}%, which is at least {max_wallet_loss_from_initial_value}% distant from the wallet initial value.\n/cc {users}""")
							self.can_run = False

							await self.stop()

					if self._configuration.strategy.kill_switch.max_wallet_loss_from_previous_value:
						if math.fabs(wallet_current_previous_pnl) >= math.fabs(max_wallet_loss_from_previous_value):
							self.log(CRITICAL, f"""The bot has been stopped because the wallet lost {-wallet_current_previous_pnl}%, which is at least {max_wallet_loss_from_previous_value}% distant from the wallet previous value.\n/cc {users}""")
							self.can_run = False

							await self.stop()

					if self._configuration.strategy.kill_switch.max_wallet_loss_compared_to_token_variation:
						if math.fabs(wallet_current_initial_pnl - token_current_initial_pnl) >= math.fabs(max_wallet_loss_compared_to_token_variation):
							self.log(CRITICAL, f"""The bot has been stopped because the wallet lost {-wallet_current_initial_pnl}%, which is at least {max_wallet_loss_compared_to_token_variation}% distant from the token price variation ({token_current_initial_pnl}) from its initial price.\n/cc {users}""")
							self.can_run = False

							await self.stop()

				if token_current_initial_pnl < 0 and math.fabs(token_current_initial_pnl) >= math.fabs(max_token_loss_from_initial):
					self.log(CRITICAL, f"""The bot has been stopped because the token lost {-token_current_initial_pnl}%, which is at least {max_token_loss_from_initial}% distant from the token initial price.\n/cc {users}""")
					self.can_run = False

					await self.stop()
		finally:
			self.log(DEBUG, """end""")

	# noinspection DuplicatedCode
	def _show_summary(self):
		replaced_orders_summary = ""
		canceled_orders_summary = ""

		if self.summary.orders.replaced:
			orders: List[DotMap[str, Any]] = list(self.summary.orders.replaced.values())
			orders.sort(key=lambda item: item.id)

			groups: array[array[str]] = [[], [], [], [], [], [], [], []]
			for order in orders:
				groups[0].append(order.id)
				groups[1].append(str(order.side).lower())
				groups[2].append(str(order.type).lower())
				groups[3].append(format_currency(Decimal(order.amount), 3))
				groups[4].append(self._base_token.symbol)
				groups[5].append("by")
				groups[6].append(format_currency(Decimal(order.price), 3))
				groups[7].append(self._quote_token.symbol)

			replaced_orders_summary = format_lines(groups)

		if self.summary.orders.canceled:
			orders: List[DotMap[str, Any]] = list(self.summary.orders.canceled.values())
			# orders.sort(key=lambda item: item.price)

			groups: array[array[str]] = [[], [], []]
			for order in orders:
				groups[0].append(order.id)
				groups[1].append(str(order.type).lower())
				groups[2].append(order.marketName)

			canceled_orders_summary = format_lines(groups)

		self.log(
			INFO,
			textwrap.dedent(
				f"""\
					<b>Settings</b>:
					{format_line("OrderType: ", self._order_type)}<br>
					{format_line("PriceStrategy: ", self._price_strategy)}<br>
					{format_line("Mid$Strategy: ", self._middle_price_strategy)}<br>
					"""
			)
		)

		self.log(
			INFO,
			textwrap.dedent(
				f"""\
				
					<b>Market</b>: <b>{self._market.name}</b>
					<b>PnL</b>: {format_line("", format_percentage(self.summary.wallet.current_initial_pnl), alignment_column - 4)}
					<b>Balances</b>:
					{format_line(f"  {self._base_token['symbol']}:", format_currency(self.summary.balance.wallet.base, 4))}
					{format_line(f"  {self._quote_token['symbol']}:", format_currency(self.summary.balance.wallet.quote, 4))}
					<b>Orders (in {self._quote_token['symbol']})</b>:
					{format_line(f"  Bids:", format_currency(self.summary.balance.orders.quote.bids, 4))}
					{format_line(f"  Asks:", format_currency(self.summary.balance.orders.quote.asks, 4))}
					{format_line(f"  Total:", format_currency(self.summary.balance.orders.quote.total, 4))}
					<b>Orders</b>:
					{format_line(" Replaced:", str(len(self.summary.orders.replaced)))}
					{format_line(" Canceled:", str(len(self.summary.orders.canceled)))}
					<b>Wallet</b>:
					{format_line(" Wo:", format_currency(self.summary.wallet.initial_value, 4))}
					{format_line(" Wp:", format_currency(self.summary.wallet.previous_value, 4))}
					{format_line(" Wc:", format_currency(self.summary.wallet.current_value, 4))}
					{format_line(" Wc/Wo:", (format_percentage(self.summary.wallet.current_initial_pnl)))}
					{format_line(" Wc/Wp:", format_percentage(self.summary.wallet.current_previous_pnl))}
					<b>Token</b>:
					{format_line(" To:", format_currency(self.summary.token.initial_price, 6))}
					{format_line(" Tp:", format_currency(self.summary.token.previous_price, 6))}
					{format_line(" Tc:", format_currency(self.summary.token.current_price, 6))}
					{format_line(" Tc/To:", format_percentage(self.summary.token.current_initial_pnl))}
					{format_line(" Tc/Tp:", format_percentage(self.summary.token.current_previous_pnl))}
					<b>Price</b>:
					{format_line(" Used:", format_currency(self.summary.price.used_price, 6))}
					{format_line(" External:", format_currency(self.summary.price.ticker_price, 6))}
					{format_line(" Last fill:", format_currency(self.summary.price.last_filled_order_price, 6))}
					{format_line(" Expected:", format_currency(self.summary.price.expected_price, 6))}
					{format_line(" Adjusted:", format_currency(self.summary.price.adjusted_market_price, 6))}
					{format_line(" SAP:", format_currency(self.summary.price.sap, 6))}
					{format_line(" WAP:", format_currency(self.summary.price.wap, 6))}
					{format_line(" VWAP:", format_currency(self.summary.price.vwap, 6))}
					<b>Balance</b>:
					"""
			)
		)

		if replaced_orders_summary:
			self.log(
				INFO,
				f"""<b>Replaced Orders:</b>\n{replaced_orders_summary}"""
			)

		if canceled_orders_summary:
			self.log(
				INFO,
				f"""<b>Canceled Orders:</b>\n{canceled_orders_summary}"""
			)

	async def _get_open_orders_balance(self) -> DotMap[str, Decimal]:
		open_orders = await self._get_open_orders()
		open_orders_base_amount = DECIMAL_ZERO
		open_orders_quote_amount = DECIMAL_ZERO
		for order in open_orders.values():
			if order.side == OrderSide.SELL.name:
				open_orders_base_amount += Decimal(order.amount)
			if order.side == OrderSide.BUY.name:
				open_orders_quote_amount += Decimal(order.amount) * Decimal(order.price)

		open_orders_balance = DotMap()
		open_orders_balance.base = open_orders_base_amount
		open_orders_balance.quote = open_orders_quote_amount

		return open_orders_balance
