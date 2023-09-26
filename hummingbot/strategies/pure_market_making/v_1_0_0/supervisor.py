import asyncio
import copy
import os
import traceback
from _decimal import Decimal
from logging import DEBUG, INFO
from typing import Any

import yaml
from dotmap import DotMap

from core.decorators import log_class_exceptions
from core.properties import properties
from core.utils import deep_merge
from core.utils import dump
from core.database_alchemy import DataBaseManipulator
from hummingbot.gateway import Gateway
from hummingbot.strategies.pure_market_making.v_1_0_0.worker import Worker
from hummingbot.strategies.strategy_base import StrategyBase
from hummingbot.strategies.worker_base import WorkerBase


@log_class_exceptions
class Supervisor(StrategyBase):

	ID = "pure_market_making"
	SHORT_ID = "pmm"
	VERSION = "1.0.0"
	TITLE = "Pure Market Making"
	CATEGORY = "supervisor"

	def __init__(self, client_id):
		try:
			self._client_id = client_id
			self.base_id = f"""{self.SHORT_ID}:{self.VERSION}:{self._client_id}"""
			self.id = f"""{self.base_id}:{self.CATEGORY}"""

			self.log(INFO, "start")

			super().__init__()

			self._reload_configuration()
			self._database_manipulator = DataBaseManipulator()

			self._is_busy: bool = False
			self._can_run: bool = True
			self._refresh_timestamp: int = 0

			self._workers: DotMap[str, WorkerBase] = DotMap({})
			self._database_session = None

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

	def _reload_configuration(self):
		self.log(INFO, "start")

		root_path = properties.get('app_root_path')
		base_path = os.path.join(root_path, "resources", "strategies", self.ID, self.VERSION)

		configuration = {}

		with open(os.path.join(base_path, f"{self.CATEGORY}.yml"), 'r') as stream:
			target = yaml.safe_load(stream) or {}
			configuration = deep_merge(copy.deepcopy(configuration), target)

		with open(os.path.join(base_path, "common.yml"), 'r') as stream:
			target = yaml.safe_load(stream) or {}
			configuration = deep_merge(copy.deepcopy(configuration), target)

		with open(os.path.join(base_path, "workers", "common.yml"), 'r') as stream:
			configuration_worker_common = yaml.safe_load(stream) or {}

		workers_ids = copy.deepcopy(configuration["workers"])
		configuration["workers"] = {}

		for worker_id in workers_ids:
			with open(os.path.join(base_path, "workers", f"{worker_id}.yml"), 'r') as stream:
				target = yaml.safe_load(stream) or {}
				configuration_worker = deep_merge(copy.deepcopy(configuration_worker_common), target)

				configuration["workers"][worker_id] = copy.deepcopy(configuration_worker)

		self._configuration = DotMap(configuration, _dynamic=False)

		self.log(INFO, "end")

	def get_status(self) -> DotMap[str, Any]:
		status = DotMap({})

		status.initialized = self._initialized
		if not self._can_run and self._tasks.on_tick is None:
			status.status = "stopped"
		elif not self._can_run and self._tasks.on_tick is not None:
			status.status = "stopping..."
		if self._can_run and self._tasks.on_tick is not None:
			status.status = "running"

		for (task_name, task) in self._tasks.items():
			status.tasks[task_name] = "running" if task is not None else "stopped"

		for worker_id in self._configuration.workers.keys():
			status.workers[worker_id] = self._workers[worker_id].get_status()

		return status

	async def initialize(self):
		try:
			self.log(INFO, "start")
			self.telegram_log(INFO, "initializing...")

			self._initialized = False

			self.clock.start()
			self._refresh_timestamp = self.clock.now()
			(self._refresh_timestamp, self._events.on_tick) = self.clock.register(self._refresh_timestamp)

			self._initialize_databases()

			coroutines = []
			for worker_id in self._configuration.workers.keys():
				self._workers[worker_id] = Worker(self, worker_id, self._database_session)
				self._tasks.workers[worker_id] = asyncio.create_task(self._workers[worker_id].start())
				coroutines.append(self._tasks.workers[worker_id])

			await asyncio.gather(*coroutines, return_exceptions=True)

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

			try:
				coroutines = [self.stop_worker(worker_id) for worker_id in self._configuration.workers.keys()]
				await asyncio.gather(*coroutines)
			except asyncio.exceptions.CancelledError:
				pass
			except Exception as exception:
				self.ignore_exception(exception)
		finally:
			await self.exit()

			self.telegram_log(INFO, "stopped.")
			self.log(INFO, "end")

	async def start_worker(self, worker_id: str):
		self.log(INFO, "start")
		try:
			if not self._tasks.workers.get(worker_id):
				if not self._workers.get(worker_id):
					self._workers[worker_id] = Worker(self, worker_id)

				self._tasks.workers[worker_id] = asyncio.create_task(self._workers[worker_id].start())
				await self._tasks.workers[worker_id]

			else:
				self.log(INFO, f"Worker {worker_id} is already running")
		finally:
			self.log(INFO, "end")

	async def stop_worker(self, worker_id: str):
		self.log(INFO, "start")
		try:
			if self._tasks.workers.get(worker_id):
				await self._workers[worker_id].stop()
				self._tasks.workers[worker_id].cancel()
				# await self._tasks.workers[worker_id]
				self._tasks.workers[worker_id] = None
			else:
				self.log(INFO, f"Worker {worker_id} is not running")
		finally:
			self.log(INFO, "end")

	def worker_status(self, worker_id: str) -> DotMap[str, Any]:
		self.log(INFO, "start")
		try:
			status = DotMap({})
			if self._tasks.workers.get(worker_id):
				status.id = worker_id
				status.update(self._workers[worker_id].get_status())
			else:
				self.log(INFO, f"Worker {worker_id} is not running")
				status["message"] = f"Worker {worker_id} is not running"

			status._dynamic = False

			return status
		finally:
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

					self._reload_configuration()

					self._is_busy = True
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

	def _initialize_databases(self):
		for worker in self._configuration.workers.keys():
			db_path, file_name = self._database_manipulator.create_db_path(
				_strategy_name=self.ID,
				_strategy_version=self.VERSION,
				_worker_id=worker
			)
			self._database_session = self._database_manipulator.get_session_creator(db_path, file_name)
