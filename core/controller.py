import json

import asyncio
from dotmap import DotMap

from core.constants import constants
from core.properties import properties
from core.system import execute
from core.types import SystemStatus
from hummingbot.strategies.strategy_base import StrategyBase
from hummingbot.strategies.types import Strategy
from typing import Any, Dict

tasks: DotMap[str, asyncio.Task] = DotMap({
})

processes: DotMap[str, StrategyBase] = DotMap({
})


def sanitize_options(options: DotMap[str, Any]) -> DotMap[str, Any]:
	default_strategy = Strategy.get_default()

	output = DotMap({
		"strategy": options.get("strategy", default_strategy.ID),
		"version": options.get("version", default_strategy.VERSION),
		"id": options.get("id", "01"),
		"worker_id": options.get("worker_id", options.get("workerId", None)),
	})

	output.full_id = f"""{output.strategy}:{output.version}:{output.id}"""
	output.class_reference = Strategy.from_id_and_version(output.strategy, output.version).value

	output._dynamic = False

	return output


async def continuously_solve_status():
	while True:
		current = properties.set("status", DotMap({}))
		system = DotMap(json.loads(await execute(constants.system.commands.status)))
		final = DotMap({})

		properties.set("status", final)

		await asyncio.sleep(constants.status.delay)


async def status(_options: DotMap[str, Any]) -> Dict[str, Any]:
	try:
		# return DotMap(json.loads(await execute(constants.system.commands.status)))
		return properties.get_or_default("status", DotMap({}))
	except Exception as exception:
		raise exception


async def start(options: DotMap[str, Any]):
	try:
		if properties.get_or_default(f"status.{options.id}", SystemStatus.UNKNOWN) == SystemStatus.STOPPED:
			properties.set(f"status.{options.id}", SystemStatus.STARTING)

			await execute(constants.system.commands.start[options.id])

			properties.set(f"status.{options.id}", SystemStatus.IDLE)

			return {
				"message": f"{options.id} has started."
			}
		else:
			return {
				"message": f"{options.id} is already running."
			}
	except Exception as exception:
		raise exception


async def stop(options: DotMap[str, Any]):
	try:
		if properties.get_or_default(f"status.{options.id}", SystemStatus.UNKNOWN) in [SystemStatus.STARTING, SystemStatus.IDLE, SystemStatus.RUNNING]:
			properties.set(f"status.{options.id}", SystemStatus.STOPPING)

			await execute(constants.system.commands.stop[options.id])

			properties.set(f"status.{options.id}", SystemStatus.STOPPED)

			return {
				"message": f"{options.id} has stopped."
			}
		else:
			return {
				"message": f"{options.id} is not running."
			}
	except Exception as exception:
		raise exception


async def strategy_status(options: DotMap[str, Any]) -> Dict[str, Any]:
	options = sanitize_options(options)

	try:
		if processes.get(options.full_id):
			return processes[options.full_id].get_status().toDict()
		else:
			return {
				"message": "Process not running"
			}
	except Exception as exception:
		if tasks.get(options.full_id):
			tasks[options.full_id].start.cancel()
			await tasks[options.full_id].start
		processes[options.full_id] = None
		tasks[options.full_id].start = None

		raise exception


async def strategy_start(options: DotMap[str, Any]) -> Dict[str, Any]:
	options = sanitize_options(options)

	try:
		if not processes.get(options.full_id):
			processes[options.full_id] = options.class_reference(options.id)
			tasks[options.full_id].start = asyncio.create_task(processes[options.full_id].start())

			return {
				"message": "Starting..."
			}
		else:
			return {
				"message": "Already running"
			}
	except Exception as exception:
		if tasks.get(options.full_id):
			tasks[options.full_id].start.cancel()
			await tasks[options.full_id].start
		processes[options.full_id] = None
		tasks[options.full_id].start = None

		raise exception


async def strategy_stop(options: DotMap[str, Any]):
	options = sanitize_options(options)

	try:
		if processes.get(options.full_id):
			tasks[options.full_id].start.cancel()
			tasks[options.full_id].stop = asyncio.create_task(processes[options.full_id].stop())

			return {
				"message": "Stopping..."
			}
		else:
			return {
				"message": "Process not running"
			}
	except Exception as exception:
		if tasks.get(options.full_id):
			tasks[options.full_id].start.cancel()
			await tasks[options.full_id].start

		raise exception
	finally:
		processes[options.full_id] = None
		tasks[options.full_id].start = None

async def strategy_worker_start(options: DotMap[str, Any]) -> Dict[str, Any]:
	options = sanitize_options(options)

	try:
		if processes.get(options.full_id):
			asyncio.create_task(processes[options.full_id].start_worker(options.worker_id))

			return {
				"message": f"Starting worker {options.worker_id} ..."
			}
		else:
			return {
				"message": f"Supervisor {options.full_id} is not running"
			}
	except Exception as exception:
		raise exception

async def strategy_worker_stop(options: DotMap[str, Any]) -> Dict[str, Any]:
	options = sanitize_options(options)

	try:
		if processes.get(options.full_id):
			asyncio.create_task(processes[options.full_id].stop_worker(options.worker_id))

			return {
				"message": f"Stopping worker {options.worker_id} ..."
			}
		else:
			return {
				"message": f"Supervisor {options.full_id} is not running"
			}
	except Exception as exception:
		raise exception

async def strategy_worker_status(options: DotMap[str, Any]) -> Dict[str, Any]:
	options = sanitize_options(options)

	try:
		if processes.get(options.full_id):
			status = DotMap({})
			status.supervisor_id = options.full_id
			status.update(processes[options.full_id].worker_status(options.worker_id))

			return status.toDict()

		else:
			return {
				"message": f"Supervisor {options.full_id} is not running"
			}

	except Exception as exception:
		raise exception
