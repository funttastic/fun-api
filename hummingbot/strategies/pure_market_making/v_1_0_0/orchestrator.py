import asyncio
import copy
import os
import traceback
from _decimal import Decimal
from logging import DEBUG, INFO
from typing import Dict, Any

import yaml
from dotmap import DotMap

from hummingbot.gateway import Gateway
from hummingbot.strategies.pure_market_making.v_1_0_0.worker import Worker
from hummingbot.strategies.strategy_base import StrategyBase
from hummingbot.strategies.worker_base import WorkerBase
from properties import properties
from utils import deep_merge
from utils import dump


class PureMarketMaking_1_0_0(StrategyBase):

	ID = "pure_market_making"
	SHORT_ID = "pmm"
	VERSION = "1.0.0"
	TITLE = "Pure Market Making"

	def __init__(self, client_id):
		try:
			self._client_id = client_id
			self.id = f"""{self.SHORT_ID}:{self.VERSION}:{self._client_id}"""
			self.logger_prefix = f"""{self.id}:orchestrator"""

			self.log(INFO, "start")

			super().__init__()

			self._load_configuration()

			self._is_busy: bool = False
			self._can_run: bool = True
			self._refresh_timestamp: int = 0

			self._workers: DotMap[str, WorkerBase] = DotMap({})

			self._tasks: DotMap[str, asyncio.Task] = DotMap({
				"on_tick": None,
				"workers": {
				}
			}, _dynamic=False)

			self._events: DotMap[str, asyncio.Event] = DotMap({
				"on_tick": None,
			}, _dynamic=False)

			self._initialized = False
		finally:
			self.log(INFO, "end")

	def _load_configuration(self):
		self.log(INFO, "start")

		root_path = properties.get('app_root_path')
		base_path = os.path.join(root_path, "resources", "strategies", self.ID, self.VERSION)

		configuration = {}

		with open(os.path.join(base_path, "main.yml"), 'r') as stream:
			target = yaml.safe_load(stream) or {}
			configuration = deep_merge(copy.deepcopy(configuration), target)

		with open(os.path.join(base_path, "common.yml"), 'r') as stream:
			target = yaml.safe_load(stream) or {}
			configuration = deep_merge(copy.deepcopy(configuration), target)

		with open(os.path.join(base_path, "workers", "common.yml"), 'r') as stream:
				worker_common = yaml.safe_load(stream) or {}

		workers_ids = copy.deepcopy(configuration["workers"])
		configuration["workers"] = {}

		for worker_id in workers_ids:
			with open(os.path.join(base_path, "workers", f"{worker_id}.yml"), 'r') as stream:
				target = yaml.safe_load(stream) or {}
				worker = deep_merge(copy.deepcopy(worker_common), target)

				configuration["workers"][worker_id] = copy.deepcopy(worker)

		self._configuration = DotMap(configuration, _dynamic=False)

		self.log(INFO, "end")

	def get_status(self) -> Dict[str, Any]:
		return {}

	async def initialize(self):
		try:
			self.log(INFO, "start")

			self._initialized = False

			self.clock.start()
			self._refresh_timestamp = self.clock.now()
			(self._refresh_timestamp, self._events.on_tick) = self.clock.register(self._refresh_timestamp)

			for worker_id, worker_configuration in self._configuration.workers.items():
				self._workers[worker_id] = Worker(self, worker_configuration)
				self._tasks.workers[worker_id] = asyncio.create_task(self._workers[worker_id].start())

			self._initialized = True
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

			try:
				coroutines = [self.stop_worker(worker_id) for worker_id in self._configuration.workers.keys()]
				await asyncio.gather(*coroutines)
			except asyncio.exceptions.CancelledError:
				pass
			except Exception as exception:
				self.ignore_exception(exception)
		finally:
			await self.exit()

			self.log(INFO, "end")

	async def stop_worker(self, worker_id: str):
		self.log(INFO, "start")

		if self._tasks.workers[worker_id]:
			await self._workers[worker_id].stop()
			self._tasks.workers[worker_id].cancel()
			# await self._tasks.workers[worker_id]
			self._tasks.workers[worker_id] = None

		self.log(INFO, "end")

	async def exit(self):
		self.log(INFO, "start")
		self.log(INFO, "end")

	async def on_tick(self):
		try:
			self.log(INFO, "start")

			while self._can_run:
				self.log(INFO, "loop - waiting")

				await self._events.on_tick.wait()

				try:
					self.log(INFO, "loop - start")

					self._is_busy = True
				except Exception as exception:
					self.ignore_exception(exception)
				finally:
					waiting_time = self._calculate_waiting_time(self._configuration.strategy.tick_interval)

					# noinspection PyAttributeOutsideInit
					self._refresh_timestamp = waiting_time + self.clock.now()
					(self._refresh_timestamp, self._events.on_tick) = self.clock.register(self._refresh_timestamp)
					self._is_busy = False

					self.log(INFO, "loop - end")

					if self._configuration.strategy.run_only_once:
						await self.stop()

						return

					self.log(INFO, f"loop - sleeping for {waiting_time}...")
					await asyncio.sleep(waiting_time)
					self.log(INFO, "loop - awaken")
		finally:
			self.log(INFO, "end")

	async def get_statistics(self) -> DotMap[str, Any]:
		balances = await self._get_balances(False)

		return balances

	async def _get_wallets(self) -> [str]:
		wallets = []

		for worker_id in self._configuration.workers.keys():
				wallets.append(self._workers[worker_id]._configuration.wallet)

		return wallets

	async def _get_balances(self, use_cache: bool = True) -> DotMap[str, Any]:
		try:
			self.log(INFO, "start")

			response = None
			try:
				request = {
					"chain": self._configuration.chain,
					"network": self._configuration.network,
					"connector": self._configuration.connector,
					"ownerAddresses": self._get_wallets(),
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

					for (wallet, tokens) in DotMap(response.tokens).items():
						for (token, balance) in tokens.items():
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