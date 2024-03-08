import asyncio
import copy
import json
import os
import textwrap
import traceback
from _decimal import Decimal
from decimal import DecimalException
from logging import DEBUG, INFO
from typing import Any

import yaml
from dotmap import DotMap

from core.decorators import log_class_exceptions
from core.properties import properties
from core.types import SystemStatus
from core.utils import deep_merge
from core.utils import dump
from hummingbot.gateway import Gateway
from hummingbot.strategies.pure_market_making.v_1_0_0.worker import Worker
from hummingbot.strategies.strategy_base import StrategyBase
from hummingbot.strategies.worker_base import WorkerBase
from hummingbot.constants import DECIMAL_ZERO, alignment_column, DEFAULT_PRECISION
from hummingbot.utils import format_currency, format_line, format_percentage


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
			self._workers_balances = DotMap()

			self.log(INFO, "start")

			super().__init__()

			self._configuration: DotMap[str, Any]
			self._database_path: str
			self._reload_configuration()

			self._is_busy: bool = False
			self._can_run: bool = True
			self._first_time = True
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

		self._database_path = os.path.join(root_path, "resources", "databases", self.ID, self.VERSION, "supervisor.json")

		self._tick_interval = self._configuration.strategy.tick_interval
		self._run_only_once = self._configuration.strategy.run_only_once

		self.log(INFO, "end")

	def get_status(self) -> DotMap[str, Any]:
		status = DotMap({})

		status.initialized = self._initialized

		status.status = SystemStatus.STARTING
		if not self._can_run and self._tasks.on_tick is None:
			status.status = SystemStatus.STOPPED
		elif not self._can_run and self._tasks.on_tick is not None:
			status.status = SystemStatus.STOPPING
		if self._can_run and self._tasks.on_tick is not None:
			status.status = SystemStatus.RUNNING

		for (task_name, task) in self._tasks.items():
			status.tasks[task_name] = SystemStatus.RUNNING if task is not None else SystemStatus.STOPPED

		for worker_id in self._configuration.workers.keys():
			status.workers[worker_id] = self._workers[worker_id].get_status()

		return status

	async def initialize(self):
		try:
			self.log(INFO, "start")
			self.telegram_log(INFO, "initializing...")

			self._initialized = False

			self._load_state()

			self.clock.start()
			self._refresh_timestamp = self.clock.now()
			(self._refresh_timestamp, self._events.on_tick) = self.clock.register(self._refresh_timestamp)

			coroutines = []
			for worker_id in self._configuration.workers.keys():
				worker = Worker(self, worker_id)
				self._workers[worker_id] = worker
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

					self._is_busy = True

					self._reload_configuration()

					self._print_summary_and_save_state()

					waiting_time = self._calculate_waiting_time(self._tick_interval)

					self._refresh_timestamp = waiting_time + self.clock.now()
					(self._refresh_timestamp, self._events.on_tick) = self.clock.register(self._refresh_timestamp)
					self._is_busy = False

					self.log(INFO, "loop - end")

					if self._run_only_once:
						await self.stop()

						return

					self._first_time = False

					self.log(INFO, f"loop - sleeping for {waiting_time}...")
					await asyncio.sleep(waiting_time)
					self.log(INFO, "loop - awaken")
				except asyncio.exceptions.CancelledError:
					return
				except Exception as exception:
					self.ignore_exception(exception)
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

	def _get_summary(self) -> str:
		summary = ""

		workers_initialized = True
		for worker in self._workers.values():
			if not worker.state.wallet.current_value:
				workers_initialized = False

		if not workers_initialized:
			return

		active_workers = []
		stopped_workers = []
		allowed_workers = []

		for (worker_id, worker) in self._workers.items():
			allowed_workers.append(worker._client_id)
			if self._tasks.workers.get(worker_id) and worker.get_status().status == "running":
				active_workers.append(worker_id)
			else:
				stopped_workers.append(worker_id)

		self.state.wallets.initial_value = DECIMAL_ZERO
		self.state.wallets.previous_value = DECIMAL_ZERO
		self.state.wallets.current_value = DECIMAL_ZERO
		self.state.wallets.previous_initial_pnl = DECIMAL_ZERO
		self.state.wallets.current_initial_pnl = DECIMAL_ZERO
		self.state.wallets.current_previous_pnl = DECIMAL_ZERO
		self.state.wallets.current_initial_pnl_in_usd = DECIMAL_ZERO

		self.state.balances.total.free = DECIMAL_ZERO
		self.state.balances.total.lockedInOrders = DECIMAL_ZERO
		self.state.balances.total.unsettled = DECIMAL_ZERO
		self.state.balances.total.total = DECIMAL_ZERO

		workers_summary = ""
		for worker_id in active_workers:
			worker = self._workers[worker_id]

			self.state.wallets.initial_value += worker.state.wallet.initial_value
			self.state.wallets.previous_value += worker.state.wallet.previous_value
			self.state.wallets.current_value += worker.state.wallet.current_value

			workers_summary += textwrap.dedent(
				f"""\n\
							{worker_id}:
					{format_line("  %: ", format_percentage(worker.state.wallet.current_initial_pnl, 3), alignment_column + 0)}
					{format_line("  $: ", format_currency(worker.state.wallet.current_initial_pnl_in_usd, 4), alignment_column + 1)}\
				"""
			)

			self.state.balances.total.free += worker.state.balances.total.free
			self.state.balances.total.lockedInOrders += worker.state.balances.total.lockedInOrders
			self.state.balances.total.unsettled += worker.state.balances.total.unsettled
			self.state.balances.total.total += worker.state.balances.total.total

		if self.state.wallets.initial_value <= 0:
			return

		self.state.wallets.previous_initial_pnl = Decimal(round(
			100 * ((self.state.wallets.previous_value / self.state.wallets.initial_value) - 1),
			DEFAULT_PRECISION
		))
		self.state.wallets.current_initial_pnl = Decimal(round(
			100 * ((self.state.wallets.current_value / self.state.wallets.initial_value) - 1),
			DEFAULT_PRECISION
		))
		self.state.wallets.current_previous_pnl = Decimal(round(
			100 * ((self.state.wallets.current_value / self.state.wallets.previous_value) - 1),
			DEFAULT_PRECISION
		))
		self.state.wallets.current_initial_pnl_in_usd = Decimal(round(
			self.state.wallets.current_value - self.state.wallets.initial_value,
			DEFAULT_PRECISION
		))

		summary += textwrap.dedent(
			f"""\n\n\
				<b>Supervisor</b>
				 Id: {self._client_id}
				
				<b>Workers</b>
				 Allowed: {allowed_workers}
				 Active:	{active_workers}
				 Stopped:	{stopped_workers}
				
				<b>PnL (in USD)</b>:
				 <b>GLOBAL</b>:
				{format_line("  <b>%</b>: ", format_percentage(self.state.wallets.current_initial_pnl, 3), alignment_column + 6)}
				{format_line("  <b>$</b>: ", format_currency(self.state.wallets.current_initial_pnl_in_usd, 4), alignment_column + 7)}\
			"""
		)

		if workers_summary:
			summary += f"""\n Workers:{workers_summary}"""

		summary += textwrap.dedent(
			f"""\n\n\
				<b>Wallets (in USD)</b>:
				{format_line(" Wo:", format_currency(self.state.wallets.initial_value, 4))}
				{format_line(" Wp:", format_currency(self.state.wallets.previous_value, 4))}
				{format_line(" Wc:", format_currency(self.state.wallets.current_value, 4))}
				{format_line(" Wc/Wo:", (format_percentage(self.state.wallets.current_initial_pnl, 3)), alignment_column - 1)}
				{format_line(" Wc/Wp:", format_percentage(self.state.wallets.current_previous_pnl, 3), alignment_column - 1)}
				
				<b>Balances (in USD)</b>:
				{format_line(f" Free:", format_currency(self.state.balances.total.free, 4))}
				{format_line(f" Orders:", format_currency(self.state.balances.total.lockedInOrders, 4))}
				{format_line(f" Unsettled:", format_currency(self.state.balances.total.unsettled, 4))}
				{format_line(f" Total:", format_currency(self.state.balances.total.total, 4))}
				
				<b>Settings</b>:
				 Tick Interval: {self._tick_interval}
				 Run Only Once: {self._run_only_once}\
			"""
		)

		return summary

	def _get_new_state(self) -> DotMap[str, Any]:
		return DotMap({
				"configurations": {
					"tick_interval": None,
					"run_only_once": None
				},
				"active_workers": [],
				"balances": DotMap({
					"total": {
						"free": DECIMAL_ZERO,
						"lockedInOrders": DECIMAL_ZERO,
						"unsettled": DECIMAL_ZERO,
						"total": DECIMAL_ZERO,
					}
				}, _dynamic=False),
				"wallets": {
					"initial_value": DECIMAL_ZERO,
					"previous_value": DECIMAL_ZERO,
					"current_value": DECIMAL_ZERO,
					"previous_initial_pnl": DECIMAL_ZERO,
					"current_initial_pnl": DECIMAL_ZERO,
					"current_previous_pnl": DECIMAL_ZERO,
					"current_initial_pnl_in_usd": DECIMAL_ZERO,
				},
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