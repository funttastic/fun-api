import asyncio
import copy
import json
import os
import textwrap
import traceback
from array import array
from decimal import Decimal, DecimalException
from logging import DEBUG, INFO, WARNING, CRITICAL
from typing import Any, List, Optional

import yaml
from dotmap import DotMap

from core.decorators import log_class_exceptions
from core.properties import properties
from core.utils import dump, deep_merge
from hummingbot.constants import DECIMAL_NAN, DEFAULT_PRECISION, alignment_column
from hummingbot.constants import KUJIRA_NATIVE_TOKEN, DECIMAL_ZERO, FLOAT_ZERO, FLOAT_INFINITY
from hummingbot.gateway import Gateway
from hummingbot.strategies.worker_base import WorkerBase
from hummingbot.types import OrderStatus, OrderType, OrderSide, PriceStrategy, MiddlePriceStrategy, Order
from hummingbot.utils import calculate_middle_price, format_currency, format_lines, format_line, format_percentage, \
	parse_order_book


@log_class_exceptions
class Worker(WorkerBase):
	CATEGORY = "worker"

	def __init__(self, parent: Any, client_id: str):
		try:
			self._parent = parent
			self._client_id = client_id

			self._configuration: DotMap[str, Any]
			self._database_path: str
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

		self._database_path = os.path.join(root_path, "resources", "databases", self._parent.ID, self._parent.VERSION, "workers", f"{self._client_id}.json")

		self.log(INFO, "end")

	async def initialize(self):
		try:
			self.log(INFO, "start")
			self.telegram_log(INFO, "initializing...")

			self._initialized = False

			self._load_state()

			self._market_name = self._configuration.market

			self._wallet_address = self._configuration.wallet

			self._market = await self._get_market()

			self._base_token = self._market.baseToken
			self._quote_token = self._market.quoteToken

			self._base_token_name = self._market.baseToken.name
			self._quote_token_name = self._market.quoteToken.name

			if self._configuration.strategy.withdraw_market_on_start:
				try:
					await self._market_withdraw()
					await asyncio.sleep(self._configuration.strategy.sleep_time_after_withdraw)
				except Exception as exception:
					self.ignore_exception(exception)

			if self._configuration.strategy.cancel_all_orders_on_start:
				try:
					await self._cancel_all_orders()
					await asyncio.sleep(self._configuration.strategy.sleep_time_after_orders_cancellation)
				except Exception as exception:
					self.ignore_exception(exception)

			await self._get_balances(use_cache=False)

			self.clock.start()
			self._refresh_timestamp = self.clock.now()
			(self._refresh_timestamp, self._events.on_tick) = self.clock.register(self._refresh_timestamp)

			self._initialized = True
			self._can_run = True
		except Exception as exception:
			self.ignore_exception(exception)

			raise exception
		finally:
			self.telegram_log(INFO, "initialized.")
			self.log(INFO, "end")

	async def start(self):
		self.log(INFO, "start")

		await self.initialize()

		self._tasks.on_tick = asyncio.create_task(self.on_tick())

		self.log(INFO, "end")

	async def stop(self):
		try:
			self.log(INFO, "start")
			self.telegram_log(INFO, "stopping...")

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

			self.telegram_log(INFO, "stopped.")
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

					self.state.orders.new = DotMap({}, _dynamic=False)
					self.state.orders.untracked = DotMap({}, _dynamic=False)
					self.state.orders.canceled = DotMap({}, _dynamic=False)
					self.state.orders.filled = DotMap({}, _dynamic=False)

					await self._get_balances(use_cache=False)
					await self._get_market_price(use_cache=False)

					await self._should_stop_loss()

					await self._withdraw_from_market_if_necessary()
					await asyncio.sleep(self._configuration.strategy.sleep_time_after_withdraw)

					await self._get_filled_orders(use_cache=False)
					proposed_orders: List[Order] = await self._create_proposal()
					current_open_orders = await self._get_open_orders(use_cache=False)
					refined_proposal = await self._refine_proposal(current_open_orders, proposed_orders)

					await self._cancel_untracked_orders(refined_proposal.solution.orders.cancel, current_open_orders)
					await asyncio.sleep(self._configuration.strategy.sleep_time_after_orders_cancellation)

					await self._get_balances(use_cache=False)
					adjusted_orders_to_create = await self._adjust_proposal_to_budget(refined_proposal.solution.orders.create)
					await self._place_orders(adjusted_orders_to_create)
					self._currently_tracked_orders_ids.extend(list(refined_proposal.solution.meta.keep.keys()))
					await asyncio.sleep(self._configuration.strategy.sleep_time_after_orders_creation)

					current_open_orders = await self._get_open_orders(use_cache=False)
					self.state.orders.untracked = self._get_untracked_orders(current_open_orders)

					await self._get_balances(use_cache=False)
					self.state.balances = self._balances

					self._print_summary_and_save_state()

					self._first_time = False

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
				except asyncio.exceptions.CancelledError:
					return
				except Exception as exception:
					self.ignore_exception(exception)
		finally:
			self.log(INFO, "end")

	async def _withdraw_from_market_if_necessary(self):
		try:
			self.log(INFO, "start")

			if self._configuration.strategy.withdraw_market_on_tick:
				try:
					if self._configuration.strategy.minimize_fees_cost.active:
						if self._configuration.strategy.minimize_fees_cost.tolerance.withdraw.absolute:
							difference = Decimal(self._configuration.strategy.minimize_fees_cost.tolerance.withdraw.absolute)

							if self._balances.total.unsettled >= difference:
								await self._market_withdraw()

								return
						if self._configuration.strategy.minimize_fees_cost.tolerance.withdraw.percentage:
							percentage = Decimal(self._configuration.strategy.minimize_fees_cost.tolerance.withdraw.absolute)
							difference = percentage * self._balances.total.total / 100

							if self._balances.total.unsettled >= difference:
								await self._market_withdraw()

								return
					else:
						await self._market_withdraw()
				except Exception as exception:
					self.ignore_exception(exception)
		finally:
			self.log(INFO, "end")

	async def _create_proposal(self) -> List[Order]:
		try:
			self.log(INFO, "start")

			order_book = await self._get_order_book()
			bids, asks = parse_order_book(order_book)

			ticker_price = await self._get_market_price(use_cache=False)
			self.state.price.ticker_price = ticker_price

			try:
				last_filled_order_price = await self._get_last_filled_order_price()
			except Exception as exception:
				self.ignore_exception(exception)

				last_filled_order_price = DECIMAL_ZERO

			self.state.price.last_filled_order_price = last_filled_order_price

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

			self.state.price.used_price = self._used_price

			self._order_type = OrderType[self._configuration.strategy.get("order_type", OrderType.LIMIT.name)]

			minimum_price_increment = Decimal(self._market.minimumPriceIncrement)
			minimum_order_size = Decimal(self._market.minimumOrderSize)

			best_bid_price = Decimal(next(iter(bids), {"price": FLOAT_ZERO}).price)
			best_ask_price = Decimal(next(iter(asks), {"price": FLOAT_INFINITY}).price)

			client_id = 1
			proposal = []

			bid_orders = []
			for index, layer in enumerate(self._configuration.strategy.layers, start=1):
				if self._configuration.strategy.be_the_first:
					base_price = min(best_bid_price + minimum_price_increment, best_ask_price - minimum_price_increment)
				else:
					base_price = min(self._used_price, best_ask_price)

				quotation = (await self._get_balances()).tokens[self._quote_token.id].inUSD.quotation
				bid_quantity = int(layer.bid.quantity)
				bid_spread_percentage = Decimal(layer.bid.spread_percentage)
				bid_price = ((100 - bid_spread_percentage) / 100) * base_price
				bid_budget = Decimal(layer.bid.budget)
				bid_size = bid_budget / quotation / bid_quantity if bid_quantity > 0 else 0

				if not (bid_quantity > 0):
					continue

				if bid_price < minimum_price_increment:
					self.log(WARNING, f"""Skipping orders placement from layer {index}, bid price too low:\n\n{'{:^30}'.format(round(bid_price, 6))}""")
				elif bid_size < minimum_order_size:
					self.log(WARNING, f"""Skipping orders placement from layer {index}, bid size too low:\n\n{'{:^30}'.format(round(bid_size, 9))}""")
				else:
					for i in range(bid_quantity):
						bid_order = Order()
						bid_order.id = str(client_id)  # This is a temporary id
						bid_order.client_id = str(client_id)
						bid_order.market_name = self._market_name
						bid_order.type = self._order_type
						bid_order.side = OrderSide.BUY
						bid_order.amount = bid_size
						bid_order.price = bid_price

						bid_orders.append(bid_order)

						client_id += 1

			ask_orders = []
			for index, layer in enumerate(self._configuration.strategy.layers, start=1):
				if self._configuration.strategy.be_the_first:
					base_price = max(best_ask_price - minimum_price_increment, best_bid_price + minimum_price_increment)
				else:
					base_price = max(self._used_price, best_bid_price)

				quotation = (await self._get_balances()).tokens[self._base_token.id].inUSD.quotation
				ask_quantity = int(layer.ask.quantity)
				ask_spread_percentage = Decimal(layer.ask.spread_percentage)
				ask_price = ((100 + ask_spread_percentage) / 100) * base_price
				ask_budget = Decimal(layer.ask.budget)
				ask_size = ask_budget / quotation / ask_quantity if ask_quantity > 0 else 0

				if not (ask_quantity > 0):
					continue

				if ask_price < minimum_price_increment:
					self.log(WARNING, f"""Skipping orders placement from layer {index}, ask price too low:\n\n{'{:^30}'.format(round(ask_price, 9))}""", True)
				elif ask_size < minimum_order_size:
					self.log(WARNING, f"""Skipping orders placement from layer {index}, ask size too low:\n\n{'{:^30}'.format(round(ask_size, 9))}""", True)
				else:
					for i in range(ask_quantity):
						ask_order = Order()
						ask_order.id = str(client_id)  # This is a temporary id
						ask_order.client_id = str(client_id)
						ask_order.market_name = self._market_name
						ask_order.type = self._order_type
						ask_order.side = OrderSide.SELL
						ask_order.amount = ask_size
						ask_order.price = ask_price

						ask_orders.append(ask_order)

						client_id += 1

			proposal = [*proposal, *bid_orders, *ask_orders]

			self.log(DEBUG, f"""proposal:\n{dump(proposal)}""")

			return proposal
		finally:
			self.log(INFO, "end")

	async def _refine_proposal(self, current_orders: List[Order], proposed_orders: List[Order]) -> DotMap[str, Any]:
		try:
			self.log(INFO, "start")

			current_orders_buy = []
			current_orders_sell = []
			proposed_orders_buy = []
			proposed_orders_sell = []

			for order in current_orders.values():
				if order.side == OrderSide.BUY.name:
					current_orders_buy.append(order)
				else:
					current_orders_sell.append(order)

			for order in proposed_orders:
				if order.side == OrderSide.BUY:
					proposed_orders_buy.append(order)
				else:
					proposed_orders_sell.append(order)

			problem = DotMap({
				"tolerance": {
					"absolute": {
						"price": None,
						"amount": None,
					},
					"percentage": {
						"price": None,
						"amount": None,
					}
				},
				"orders": {
					"current": [current_orders_buy, current_orders_sell],
					"proposed": [proposed_orders_buy, proposed_orders_sell]
				}
			}, _dynamic=False)

			if self._configuration.strategy.minimize_fees_cost.active:
				problem.tolerance.absolute.price = Decimal(self._configuration.strategy.minimize_fees_cost.tolerance.orders.absolute.price)
				problem.tolerance.absolute.amount = Decimal(self._configuration.strategy.minimize_fees_cost.tolerance.orders.absolute.amount)
				problem.tolerance.percentage.price = Decimal(self._configuration.strategy.minimize_fees_cost.tolerance.orders.percentage.price)
				problem.tolerance.percentage.amount = Decimal(self._configuration.strategy.minimize_fees_cost.tolerance.orders.percentage.amount)

				output = await self._minimize_fees_cost(problem)
			else:
				output = DotMap({
					'problem': problem,
					'solution': {
						'orders': {
							'cancel': current_orders,
							'keep': [],
							'create': proposed_orders,
						},
						'meta': {
							'cancel': [order.id for order in current_orders],
							'keep': {},
							'create': [order.id for order in proposed_orders],
						}
					}
				}, _dynamic=False)

			return output
		finally:
			self.log(INFO, "end")

	async def _minimize_fees_cost(self, problem: DotMap[str, Any]) -> DotMap[str, Any]:
		try:
			self.log(INFO, "start")
			def calculate_tolerance(value, absolute_tolerance, percentage_tolerance):
				return max(absolute_tolerance, value * (percentage_tolerance / 100))

			[current_orders_buy, current_orders_sell] = problem.orders.current
			[proposed_orders_buy, proposed_orders_sell] = problem.orders.proposed

			cancel = []
			keep = []
			create = []
			keep_map = {}

			mapped_proposed = set()
			sides = [(current_orders_buy, proposed_orders_buy), (current_orders_sell, proposed_orders_sell)]
			for (current_orders, proposed_orders) in sides:
				for current_order in current_orders:
					matched = False
					for proposed_order in proposed_orders:
						if proposed_order.id in mapped_proposed:
							continue

						price_tolerance = calculate_tolerance(
							Decimal(current_order.price),
							problem.tolerance.absolute.price,
							problem.tolerance.percentage.price
						)

						amount_tolerance = calculate_tolerance(
							Decimal(current_order.amount),
							problem.tolerance.absolute.amount,
							problem.tolerance.percentage.amount
						)

						if (
							(abs(Decimal(current_order.price) - proposed_order.price) <= price_tolerance)
							and (abs(Decimal(current_order.amount) - proposed_order.amount) <= amount_tolerance)
						):
							keep.append(current_order)
							keep_map[current_order.id] = proposed_order.id
							mapped_proposed.add(proposed_order.id)
							matched = True
							break

					if not matched:
						cancel.append(current_order)
				for proposed_order in proposed_orders:
					if proposed_order.id not in mapped_proposed:
						create.append(proposed_order)

			solution = {
				'orders': {
					'cancel': cancel,
					'keep': keep,
					'create': create,
				},
				'meta': {
					'cancel': [order.id for order in cancel],
					'keep': keep_map,
					'create': [order.id for order in create],
				}
			}

			return DotMap({
				'problem': problem,
				'solution': solution
			}, _dynamic=False)
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

					for (token, balance) in self._balances.tokens.items():
						balance.free = Decimal(balance.free)
						balance.lockedInOrders = Decimal(balance.lockedInOrders)
						balance.unsettled = Decimal(balance.unsettled)
						balance.total = Decimal(balance.total)

						balance.inUSD.quotation = Decimal(balance.inUSD.quotation)
						balance.inUSD.free = Decimal(balance.inUSD.free)
						balance.inUSD.lockedInOrders = Decimal(balance.inUSD.lockedInOrders)
						balance.inUSD.unsettled = Decimal(balance.inUSD.unsettled)
						balance.inUSD.total = Decimal(balance.inUSD.total)

				return self._balances
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
					"statuses": [OrderStatus.OPEN.value[0], OrderStatus.PARTIALLY_FILLED.value[0]]
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

				self.state.orders.filled = response

				return response
			except Exception as exception:
				response = traceback.format_exc()

				raise exception
			finally:
				self.log(DEBUG, f"""gateway.kujira_get_filled_orders: response:\n{dump(response)}""")

		finally:
			self.log(INFO, "end")

	async def _place_orders(self, proposal: List[Order]) -> DotMap[str, Any]:
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

					if response:
						if not self._balances:
							await self._get_balances(use_cache=False)
						self._calculate_gas_sum(response, "creation")

				else:
					self.log(INFO, "No order was defined for placement/replacement. Skipping.", True)
					response = []

				self.state.orders.new = response

				return response
			except Exception as exception:
				response = traceback.format_exc()

				raise exception
			finally:
				self.log(DEBUG, f"""gateway.kujira_post_orders: response:\n{dump(response)}""")
		finally:
			self.log(INFO, "end")

	async def _cancel_untracked_orders(self, orders_to_cancel: List[DotMap[str, Any]], current_open_orders: DotMap[str, Any]):
		try:
			self.log(INFO, "start")

			# request = None
			response = None
			try:
				orders_to_cancel_ids = [order.id for order in orders_to_cancel]
				current_open_orders_ids = list(current_open_orders.keys())

				target_orders_ids = self._get_untracked_orders_ids(current_open_orders_ids, orders_to_cancel_ids)

				if len(target_orders_ids) > 0:
					request = {
						"chain": self._configuration.chain,
						"network": self._configuration.network,
						"connector": self._configuration.connector,
						"ids": target_orders_ids,
						"marketId": self._market.id,
						"ownerAddress": self._wallet_address,
					}

					self.log(DEBUG, f"""gateway.kujira_delete_orders: request:\n{dump(request)}""")

					response = await Gateway.kujira_delete_orders(request)

					if response:
						self._calculate_gas_sum(response, "cancellation")
				else:
					self.log(DEBUG, "No order needed to be canceled.")
					response = {}

				self.state.orders.canceled = response

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

				if response:
					if not self._balances:
						await self._get_balances(use_cache=False)
					self._calculate_gas_sum(response, "cancellation")
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

				if response:
					self._calculate_gas_sum(response, "withdrawing")
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

			if self._first_time:
				return

			balances = await self._get_balances()

			if self.state.wallet.initial_value == DECIMAL_ZERO:
				self.state.token.base.initial_price = await self._get_market_price()
				self.state.token.base.previous_price = self.state.token.base.initial_price
				self.state.token.base.current_price = self.state.token.base.initial_price

				self.state.wallet.initial_value = balances.total.total
				self.state.wallet.previous_value = self.state.wallet.initial_value
				self.state.wallet.current_value = self.state.wallet.initial_value
			else:
				max_wallet_loss_from_initial_value = round(self._configuration.strategy.kill_switch.max_wallet_loss_from_initial_value, 9)
				max_wallet_loss_from_previous_value = round(self._configuration.strategy.kill_switch.max_wallet_loss_from_previous_value, 9)
				max_wallet_loss_compared_to_token_variation = round(self._configuration.strategy.kill_switch.max_wallet_loss_compared_to_token_variation, 9)
				max_token_loss_from_initial = round(self._configuration.strategy.kill_switch.max_token_loss_from_initial, 9)

				self.state.token.base.previous_price = self.state.token.base.current_price
				self.state.token.base.current_price = await self._get_market_price()

				self.state.wallet.previous_value = self.state.wallet.current_value
				self.state.wallet.current_value = balances.total.total

				wallet_previous_initial_pnl = Decimal(round(
					100 * ((self.state.wallet.previous_value / self.state.wallet.initial_value) - 1),
					DEFAULT_PRECISION
				))
				wallet_current_initial_pnl_in_usd = Decimal(round(
					self.state.wallet.current_value - self.state.wallet.initial_value,
					DEFAULT_PRECISION
				))
				wallet_current_initial_pnl = Decimal(round(
					100 * ((self.state.wallet.current_value / self.state.wallet.initial_value) - 1),
					DEFAULT_PRECISION
				))
				wallet_current_previous_pnl = Decimal(round(
					100 * ((self.state.wallet.current_value / self.state.wallet.previous_value) - 1),
					DEFAULT_PRECISION
				))
				token_base_previous_initial_pnl = Decimal(round(
					100 * ((self.state.token.base.previous_price / self.state.token.base.initial_price) - 1),
					DEFAULT_PRECISION
				))
				token_base_current_initial_pnl = Decimal(round(
					100 * ((self.state.token.base.current_price / self.state.token.base.initial_price) - 1),
					DEFAULT_PRECISION
				))
				token_base_current_previous_pnl = Decimal(round(
					100 * ((self.state.token.base.current_price / self.state.token.base.previous_price) - 1),
					DEFAULT_PRECISION
				))

				wallet_current_initial_pnl_to_token_base_current_initial_pnl = Decimal(round(
					100 * ((wallet_current_initial_pnl / token_base_current_initial_pnl) - 1),
					DEFAULT_PRECISION
				))

				self.state.wallet.previous_initial_pnl = wallet_previous_initial_pnl
				self.state.wallet.current_initial_pnl = wallet_current_initial_pnl
				self.state.wallet.current_previous_pnl = wallet_current_previous_pnl

				self.state.wallet.current_initial_pnl_in_usd = wallet_current_initial_pnl_in_usd

				self.state.token.base.previous_initial_pnl = token_base_previous_initial_pnl
				self.state.token.base.current_initial_pnl = token_base_current_initial_pnl
				self.state.token.base.current_previous_pnl = token_base_current_previous_pnl

				users = ', '.join(self._configuration.strategy.kill_switch.notify.telegram.users)

				if self._configuration.strategy.kill_switch.max_wallet_loss_from_initial_value:
					if (
						wallet_current_initial_pnl < 0
						and wallet_current_initial_pnl <= -max_wallet_loss_from_initial_value
					):
						self.log(CRITICAL, f"""\n\nThe bot has been stopped because the wallet lost {format_percentage(wallet_current_initial_pnl, 3)}, which is at least {max_wallet_loss_from_initial_value}% distant from the wallet initial value.\n/cc {users}""")
						await self.stop()

						return

				if self._configuration.strategy.kill_switch.max_wallet_loss_from_previous_value:
					if (
						wallet_current_previous_pnl < 0
						and wallet_current_previous_pnl <= -max_wallet_loss_from_previous_value
					):
						self.log(CRITICAL, f"""\n\nThe bot has been stopped because the wallet lost {format_percentage(wallet_current_previous_pnl, 3)}, which is at least {max_wallet_loss_from_previous_value}% distant from the wallet previous value.\n/cc {users}""")
						await self.stop()

						return

				if self._configuration.strategy.kill_switch.max_wallet_loss_compared_to_token_variation:
					if (
						wallet_current_initial_pnl < 0
						and token_base_current_initial_pnl < 0
						and wallet_current_initial_pnl_to_token_base_current_initial_pnl < 0
						and wallet_current_initial_pnl_to_token_base_current_initial_pnl <= -max_wallet_loss_compared_to_token_variation
					):
						self.log(CRITICAL, f"""\n\nThe bot has been stopped because the wallet lost {format_percentage(wallet_current_initial_pnl, 3)}, which is at least {max_wallet_loss_compared_to_token_variation}% distant from the token price variation ({token_base_current_initial_pnl}) from its initial price.\n/cc {users}""")
						await self.stop()

						return

				if (
					token_base_current_initial_pnl < 0
					and token_base_current_initial_pnl <= -max_token_loss_from_initial
				):
					self.log(CRITICAL, f"""\n\nThe bot has been stopped because the token lost {format_percentage(token_base_current_initial_pnl, 3)}, which is at least {max_token_loss_from_initial}% distant from the token initial price.\n/cc {users}""")
					await self.stop()

					return
		finally:
			self.log(DEBUG, """end""")

	def get_status(self) -> DotMap[str, Any]:
		status = DotMap({})

		status.initialized = self._initialized

		if self._can_run:
			status.status = "running"
		else:
			status.status = "stopping"

		stopped = True
		for (task_name, task) in self._tasks.items():
			if task is not None:
				status.tasks[task_name] = "running"
				stopped = False
			else:
				status.tasks[task_name] = "stopped"

		if stopped:
			status.status = "stopped"

		status._dynamic = False

		return status

	# noinspection DuplicatedCode
	def _get_summary(self) -> str:
		summary = ""

		new_orders_summary = ""
		untracked_orders_summary = ""
		canceled_orders_summary = ""
		filled_orders_summary = ""

		if self.state.orders.new:
			orders: List[DotMap[str, Any]] = list(self.state.orders.new.values())
			orders.sort(key=lambda item: item.id)

			groups: array[array[str]] = [[], [], [], [], [], [], [], []]
			for order in orders:
				groups[0].append(order.id)
				groups[2].append(str(order.type).lower())
				groups[1].append(str(order.side).lower())
				groups[3].append(format_currency(Decimal(order.amount), 3))
				groups[4].append(self._base_token.symbol)
				groups[5].append("by")
				groups[6].append(format_currency(Decimal(order.price), 3))
				groups[7].append(self._quote_token.symbol)

			new_orders_summary = format_lines(groups)

		if self.state.orders.untracked:
			orders: List[DotMap[str, Any]] = list(self.state.orders.untracked.values())
			orders.sort(key=lambda item: item.id)

			groups: array[array[str]] = [[], [], [], [], [], [], [], []]
			for order in orders:
				groups[0].append(order.id)
				groups[2].append(str(order.type).lower())
				groups[1].append(str(order.side).lower())
				groups[3].append(format_currency(Decimal(order.amount), 3))
				groups[4].append(self._base_token.symbol)
				groups[5].append("by")
				groups[6].append(format_currency(Decimal(order.price), 3))
				groups[7].append(self._quote_token.symbol)

			untracked_orders_summary = format_lines(groups)

		if self.state.orders.canceled:
			orders: List[DotMap[str, Any]] = list(self.state.orders.canceled.values())
			# orders.sort(key=lambda item: item.price)

			groups: array[array[str]] = [[]]
			for order in orders:
				groups[0].append(order.id)
				# groups[1].append(str(order.type).lower())
				# groups[2].append(order.marketName)

			canceled_orders_summary = format_lines(groups)

		if self.state.orders.filled:
			orders: List[DotMap[str, Any]] = list(self.state.orders.filled.values())
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

			filled_orders_summary = format_lines(groups)

		summary += textwrap.dedent(
			f"""\n\n\
				<b>Worker</b>
				 Id: {self._client_id}
				 Network: {self._configuration.network}
				 Market: <b>{self._market.name}</b>
				 Wallet: ...{str(self._wallet_address)[-4:]}

				<b>PnL (in USD)</b>:
				{format_line(" <b>%</b>: ", format_percentage(self.state.wallet.current_initial_pnl, 3), alignment_column + 6)}
				{format_line(" <b>$</b>: ", format_currency(self.state.wallet.current_initial_pnl_in_usd, 4), alignment_column + 7)}
				
				<b>Balances (in USD)</b>:
				 <b>Total</b>:
				{format_line(f"  Free:", format_currency(self.state.balances.total.free, 4))}
				{format_line(f"  Orders:", format_currency(self.state.balances.total.lockedInOrders, 4))}
				{format_line(f"  Unsettled:", format_currency(self.state.balances.total.unsettled, 4))}
				{format_line(f"  Total:", format_currency(self.state.balances.total.total, 4))}
				 <b>Tokens</b>:
				  <b>{self._base_token.symbol}</b>:
				{format_line(f"   Price:", format_currency(self.state.balances.tokens[self._base_token.id].inUSD.quotation, 4))}
				{format_line(f"   Free:", format_currency(self.state.balances.tokens[self._base_token.id].inUSD.free, 4))}
				{format_line(f"   Sell Orders:", format_currency(self.state.balances.tokens[self._base_token.id].inUSD.lockedInOrders, 4))}
				{format_line(f"   Unsettled:", format_currency(self.state.balances.tokens[self._base_token.id].inUSD.unsettled, 4))}
				{format_line(f"   Total:", format_currency(self.state.balances.tokens[self._base_token.id].inUSD.total, 4))}
				  <b>{self._quote_token.symbol}</b>:
				{format_line(f"   Price:", format_currency(self.state.balances.tokens[self._quote_token.id].inUSD.quotation, 4))}
				{format_line(f"   Free:", format_currency(self.state.balances.tokens[self._quote_token.id].inUSD.free, 4))}
				{format_line(f"   Buy Orders:", format_currency(self.state.balances.tokens[self._quote_token.id].inUSD.lockedInOrders, 4))}
				{format_line(f"   Unsettled:", format_currency(self.state.balances.tokens[self._quote_token.id].inUSD.unsettled, 4))}
				{format_line(f"   Total:", format_currency(self.state.balances.tokens[self._quote_token.id].inUSD.total, 4))}
				
				<b>Wallet (in USD)</b>:
				{format_line(" Wo:", format_currency(self.state.wallet.initial_value, 4))}
				{format_line(" Wp:", format_currency(self.state.wallet.previous_value, 4))}
				{format_line(" Wc:", format_currency(self.state.wallet.current_value, 4))}
				{format_line(" Wc/Wo:", (format_percentage(self.state.wallet.current_initial_pnl, 3)), alignment_column - 1)}
				{format_line(" Wc/Wp:", format_percentage(self.state.wallet.current_previous_pnl, 3), alignment_column - 1)}
				
				<b>{self._base_token.symbol} (in {self._quote_token.symbol})</b>:
				{format_line(" Bo:", format_currency(self.state.token.base.initial_price, 4))}
				{format_line(" Bp:", format_currency(self.state.token.base.previous_price, 4))}
				{format_line(" Bc:", format_currency(self.state.token.base.current_price, 4))}
				{format_line(" Bc/Bo:", format_percentage(self.state.token.base.current_initial_pnl, 3), alignment_column - 1)}
				{format_line(" Bc/Bp:", format_percentage(self.state.token.base.current_previous_pnl, 3), alignment_column - 1)}
				
				<b>Price</b>:
				{format_line(" Used:", format_currency(self.state.price.used_price, 4))}
				{format_line(" Ticker:", format_currency(self.state.price.ticker_price, 4))}
				
				<b>Orders</b>:
				 <b>Quantity</b>:
				{format_line("  New:", str(len(self.state.orders.new)), alignment_column - 5)}
				{format_line("  Canceled:", str(len(self.state.orders.canceled)), alignment_column - 5)}
				
				<b>Fees</b>:
				{format_line(" Native Token:", self.state.gas_payed.token.symbol)}
				 <b>{self.state.gas_payed.token.symbol}</b>:
				{format_line("  Create:", format_currency(self.state.gas_payed.token_amounts.creation, 5))}
				{format_line("  Cancel:", format_currency(self.state.gas_payed.token_amounts.cancellation, 5))}
				<code>  Withdraw:</code>
				{format_line("   Native:", format_currency(self.state.gas_payed.token_amounts.withdrawing.native, 5))}
				{format_line("   Base:", format_currency(self.state.gas_payed.token_amounts.withdrawing.base, 5))}
				{format_line("   Quote:", format_currency(self.state.gas_payed.token_amounts.withdrawing.quote, 5))}
				{format_line("  Total:", format_currency(self.state.gas_payed.token_amounts.total, 5))}
				 <b>USD (~)</b>:
				{format_line("  Create:", format_currency(self.state.gas_payed.usd_amounts.creation, 5))}
				{format_line("  Cancel:", format_currency(self.state.gas_payed.usd_amounts.cancellation, 5))}
				<code>  Withdraw:</code>
				{format_line("   Base:", format_currency(self.state.gas_payed.usd_amounts.withdrawing.base, 5))}
				{format_line("   Quote:", format_currency(self.state.gas_payed.usd_amounts.withdrawing.quote, 5))}
				{format_line("   Total:", format_currency(self.state.gas_payed.usd_amounts.withdrawing.total, 5))}
				{format_line("  Total:", format_currency(self.state.gas_payed.usd_amounts.total, 5))}\
			"""
		)

		if new_orders_summary:
			summary += f"""\n<b> New:</b>\n{new_orders_summary}"""

		if untracked_orders_summary:
			summary += f"""\n<b> Untracked:</b>\n{untracked_orders_summary}"""

		if canceled_orders_summary:
			summary += f"""\n<b> Canceled:</b>\n{canceled_orders_summary}"""

		if filled_orders_summary:
			summary += f"""\n<b> Filled:</b>\n{filled_orders_summary}"""

		summary += textwrap.dedent(
			f"""\n\n\
				<b>Settings</b>:
				 TickInterval: {self._configuration.strategy.tick_interval}
				 OrderType: {self._order_type.name}
				 PriceStrategy: {self._price_strategy.name}
				 MiddlePriceStrategy: {self._middle_price_strategy.name}\
			"""
		)

		return summary
	
	def _hot_reload(self):
		import importlib
		module = importlib.reload(importlib.import_module(self.__module__))

		self.__class__ = getattr(module, self.__class__.__name__)

	def _calculate_gas_sum(self, response: Any, transaction_type: str):
		try:
			self.log(DEBUG, f"""start""")

			if not transaction_type == 'withdrawing':
				unique_transaction_hashes = {}
				sample_orders_for_each_transaction = {}

				for order_id, order in response.items():
					transaction_hash = order.hashes[transaction_type]
					if transaction_hash not in unique_transaction_hashes:
						unique_transaction_hashes[transaction_hash] = True
						sample_orders_for_each_transaction[order_id] = order

				for order in sample_orders_for_each_transaction.values():
					self.state.gas_payed.token_amounts[transaction_type] += Decimal(order.fee)
					self.state.gas_payed.token_amounts.total += Decimal(order.fee)
					values = [
						Decimal(self._balances.tokens[self.state.gas_payed.token.id].free),
						Decimal(self._balances.tokens[self.state.gas_payed.token.id].inUSD.free)
					]
					max_value = max(*values)
					min_value = min(*values)
					quotation = self._balances.tokens[self.state.gas_payed.token.id].inUSD.quotation

					factor = quotation if quotation else min_value / max_value

					self.state.gas_payed.usd_amounts[transaction_type] += Decimal(order.fee) * factor
					self.state.gas_payed.usd_amounts.total += Decimal(order.fee) * factor
			else:
				if self._base_token.id != KUJIRA_NATIVE_TOKEN.id and self._quote_token.id != KUJIRA_NATIVE_TOKEN.id:
					self.state.gas_payed.token_amounts[transaction_type].native += Decimal(response.tokens[KUJIRA_NATIVE_TOKEN.id].fees.token)
				if self._base_token.id in response.tokens:
					self.state.gas_payed.token_amounts[transaction_type].base += Decimal(response.tokens[self._base_token.id].fees.token)
					self.state.gas_payed.usd_amounts[transaction_type].base += Decimal(response.tokens[self._base_token.id].fees.USD)
				if self._quote_token.id in response.tokens:
					self.state.gas_payed.token_amounts[transaction_type].quote += Decimal(response.tokens[self._quote_token.id].fees.token)
					self.state.gas_payed.usd_amounts[transaction_type].quote += Decimal(response.tokens[self._quote_token.id].fees.USD)
				self.state.gas_payed.usd_amounts[transaction_type].total += Decimal(response.total.fees)
				self.state.gas_payed.usd_amounts.total += Decimal(response.total.fees)
		except Exception as exception:
			self.log(DEBUG, f"""An error occurred during tax sum calculation...""")
			raise exception
		finally:
			self.log(DEBUG, f"""end""")

	def _get_untracked_orders_ids(self, open_orders_ids: List[str], orders_to_cancel_ids: List[str]):
		currently_untracked_orders_ids = list(
			set(
				set(self._all_tracked_orders_ids).intersection(set(open_orders_ids))
				- set(self._currently_tracked_orders_ids)
			).union(orders_to_cancel_ids)
		)

		return currently_untracked_orders_ids

	def _get_untracked_orders(self, open_orders: DotMap[str, Any]):
		open_orders_ids = list(open_orders.keys())

		currently_untracked_orders_ids = self._get_untracked_orders_ids(open_orders_ids, [])

		currently_untracked_orders = DotMap({}, _dynamic=False)

		if len(currently_untracked_orders_ids) > 0:
			for order_id in currently_untracked_orders_ids:
				order = self._open_orders[order_id]
				currently_untracked_orders[order_id] = order

		return currently_untracked_orders

	def _get_new_state(self) -> DotMap[str, Any]:
		return DotMap({
				"configurations": {
					"order_type": None,
					"price_strategy": None,
					"middle_price_strategy": None,
					"use_adjusted_price": None
				},
				"balances": DotMap({}, _dynamic=False),
				"orders": {
					"new": DotMap({}, _dynamic=False),
					"open": DotMap({}, _dynamic=False),
					"canceled": DotMap({}, _dynamic=False),
					"filled": DotMap({}, _dynamic=False),
				},
				"gas_payed": {
					"token": KUJIRA_NATIVE_TOKEN,
					"token_amounts": {
						"creation": DECIMAL_ZERO,
						"cancellation": DECIMAL_ZERO,
						"withdrawing": {
							"native": DECIMAL_ZERO,
							"base": DECIMAL_ZERO,
							"quote": DECIMAL_ZERO
						},
						"total": DECIMAL_ZERO
					},
					"usd_amounts": {
						"creation": DECIMAL_ZERO,
						"cancellation": DECIMAL_ZERO,
						"withdrawing": {
							"base": DECIMAL_ZERO,
							"quote": DECIMAL_ZERO,
							"total": DECIMAL_ZERO
						},
						"total": DECIMAL_ZERO,
					}
				},
				"wallet": {
					"initial_value": DECIMAL_ZERO,
					"previous_value": DECIMAL_ZERO,
					"current_value": DECIMAL_ZERO,
					"previous_initial_pnl": DECIMAL_ZERO,
					"current_initial_pnl": DECIMAL_ZERO,
					"current_previous_pnl": DECIMAL_ZERO,
					"current_initial_pnl_in_usd": DECIMAL_ZERO,
				},
				"token": {
					"base": {
						"initial_price": DECIMAL_ZERO,
						"previous_price": DECIMAL_ZERO,
						"current_price": DECIMAL_ZERO,
						"previous_initial_pnl": DECIMAL_ZERO,
						"current_initial_pnl": DECIMAL_ZERO,
						"current_previous_pnl": DECIMAL_ZERO,
					},
				},
				"price": {
					"used_price": DECIMAL_ZERO,
					"ticker_price": DECIMAL_ZERO,
					"last_filled_order_price": DECIMAL_ZERO,
				}
			}, _dynamic=False)

	def _recreate_state(self):
		self.state = self._get_new_state()
		self._save_state()

	def _save_state(self):
		def handle_serialization(target):
			if isinstance(target, Decimal):
				return str(target)
			raise TypeError("Non serializable type: {}".format(type(target)))

		filepath = self._database_path
		dirpath = os.path.dirname(filepath)
		if not os.path.exists(dirpath):
			os.makedirs(dirpath, exist_ok=True)

		with open(filepath, "w+") as file:
			json.dump(self.state.toDict(), file, indent=2, default=handle_serialization)

	def _load_state(self):
		if self._configuration.state.recreate_on_start:
			self._recreate_state()
		else:
			filepath = self._database_path
			dirpath = os.path.dirname(filepath)
			if not os.path.exists(dirpath):
				os.makedirs(dirpath, exist_ok=True)

			with open(filepath, "a+") as file:
				file.seek(0)
				content = file.read()
				if not content or content == "":
					self._recreate_state()
				else:
					def handle_deserialization(target):
						for key, value in target.items():
							if isinstance(value, str):
								try:
									target[key] = Decimal(value)
								except DecimalException:
									pass
						return target

					self.state = DotMap(json.loads(content, object_hook=handle_deserialization), _dynamic=False)

	def _print_summary_and_save_state(self):
		summary = self._get_summary()

		if not summary or summary is None:
			summary = "Summary not ready."
		else:
			self._save_state()

		self.log(INFO, summary)
		self.telegram_log(INFO, summary)