import asyncio
from dotmap import DotMap
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


async def strategy_status(options: DotMap[str, Any]) -> Dict[str, Any]:
	options = sanitize_options(options)

	try:
		if processes.get(options.full_id):
			return processes[options.full_id].get_status()
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
