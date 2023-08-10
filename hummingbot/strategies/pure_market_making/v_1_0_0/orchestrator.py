import traceback

from _decimal import Decimal
from logging import DEBUG, INFO

import asyncio
import copy
import os
import yaml
from dotmap import DotMap
from typing import Dict, Any

from hummingbot.gateway import Gateway
from hummingbot.strategies.pure_market_making.v_1_0_0.worker import Worker
from hummingbot.strategies.strategy_base import StrategyBase
from hummingbot.strategies.worker_base import WorkerBase
from hummingbot.utils import current_timestamp
from utils import dump
from properties import properties
from utils import deep_merge


class PureMarketMaking_1_0_0(StrategyBase):

	ID = "pure_market_making"
	VERSION = "1.0.0"
	TITLE = "Pure Market Making"

	def __init__(self, client_id):
		try:
			self._client_id = client_id
			self.id = f"""{self.ID}:{self.VERSION}:{self._client_id}"""
			self.logger_prefix = self.id

			self.log(DEBUG, "start")

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

			self._initialized = False
		finally:
			self.log(DEBUG, "end")

	def _load_configuration(self):
		self.log(DEBUG, "start")

		root_path = properties.get('app_root_path')
		base_path = os.path.join(root_path, "resources", "strategies", self.ID, self.VERSION)

		configuration = {}

		with open(os.path.join(base_path, "main.yml"), 'r') as stream:
			target = yaml.safe_load(stream) or {}
			configuration = deep_merge(configuration, target)

		with open(os.path.join(base_path, "common.yml"), 'r') as stream:
			target = yaml.safe_load(stream) or {}
			configuration = deep_merge(configuration, target)

		with open(os.path.join(base_path, "workers", "common.yml"), 'r') as stream:
				worker_common = yaml.safe_load(stream) or {}

		workers_ids = copy.copy(configuration["workers"])
		configuration["workers"] = {}

		for worker_id in workers_ids:
			with open(os.path.join(base_path, "workers", f"{worker_id}.yml"), 'r') as stream:
				target = yaml.safe_load(stream) or {}
				worker = deep_merge(worker_common, target)

				configuration["workers"][worker_id] = copy.deepcopy(worker)

		self._configuration = DotMap(configuration, _dynamic=False)

		self.log(DEBUG, "end")

	def get_status(self) -> Dict[str, Any]:
		return {}

	async def initialize(self):
		try:
			self.log(DEBUG, "start")

			self._initialized = False

			for worker_id, worker_configuration in self._configuration.workers.items():
				self._workers[worker_id] = Worker(self, worker_configuration)
				self._tasks.workers[worker_id] = asyncio.create_task(self._workers[worker_id].start())

			self._initialized = True
		except Exception as exception:
			self.ignore_exception(exception)

			await self.exit()
		finally:
			self.log(DEBUG, "end")

	async def start(self):
		self.log(INFO, "start")

		await self.initialize()

		while self._can_run:
			if (not self._is_busy) and (not self._can_run):
				await self.exit()

			now = current_timestamp()
			if self._is_busy or (self._refresh_timestamp > now):
				continue

			if self._tasks.on_tick is None:
				try:
					self._tasks.on_tick = asyncio.create_task(self.on_tick())
					await self._tasks.on_tick
				finally:
					self._tasks.on_tick = None

		self.log(INFO, "end")

	async def stop(self):
		try:
			self.log(INFO, "start")

			self._can_run = False

			try:
				if self._tasks.on_tick:
					self._tasks.on_tick.cancel()
					await self._tasks.on_tick
			except Exception as exception:
				self.ignore_exception(exception)

			try:
				coroutines = [self.stop_worker(worker_id) for worker_id in self._configuration.workers.keys()]
				await asyncio.gather(*coroutines)
			except Exception as exception:
				self.ignore_exception(exception)
		finally:
			await self.exit()

			self.log(INFO, "end")

	async def stop_worker(self, worker_id: str):
		self.log(DEBUG, "start")

		if self._tasks.workers[worker_id]:
			await self._workers[worker_id].stop()
			self._tasks.workers[worker_id].cancel()
			# await self._tasks.workers[worker_id]
			self._tasks.workers[worker_id] = None

		self.log(DEBUG, "end")

	async def exit(self):
		self.log(DEBUG, "start")
		self.log(DEBUG, "end")

	async def on_tick(self):
		try:
			self.log(INFO, "start")

			self._is_busy = True

		except Exception as exception:
			self.ignore_exception(exception)
		finally:
			waiting_time = self._calculate_waiting_time(self._configuration.strategy.tick_interval)

			# noinspection PyAttributeOutsideInit
			self._refresh_timestamp = waiting_time + current_timestamp()
			self._is_busy = False

			self.log(INFO, f"""Waiting for {waiting_time}s.""")

			self.log(INFO, "end")

			if self._configuration.strategy.run_only_once:
				await self.exit()

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
			self.log(DEBUG, "start")

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
			self.log(DEBUG, "end")