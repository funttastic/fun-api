import asyncio
from dotmap import DotMap
from hummingbot.strategies.strategy_base import StrategyBase
from hummingbot.strategies.types import Strategy
from typing import Any, Dict

tasks: DotMap[str, asyncio.Task] = DotMap({
})

processes: DotMap[str, StrategyBase] = DotMap({
})


async def controller_strategy_start(strategy: str, version: str, id: str) -> Dict[str, Any]:
	full_id = f"""{strategy}:{version}:{id}"""

	try:
		class_reference = Strategy.from_id_and_version(strategy, version).value
		if not processes.get(full_id):
			processes[full_id] = class_reference(id)
			tasks[full_id].start = asyncio.create_task(processes[full_id].start())

			return {
				"message": "Successfully started"
			}
		else:
			return {
				"message": "Already running"
			}
	except Exception as exception:
		if tasks.get(full_id):
			tasks[full_id].start.cancel()
			await tasks[full_id].start
		processes[full_id] = None
		tasks[full_id].start = None

		raise exception


async def controller_strategy_status(strategy: str, version: str, id: str) -> Dict[str, Any]:
	full_id = f"""{strategy}:{version}:{id}"""

	try:
		if processes.get(full_id):
			return processes[full_id].get_status()
		else:
			return {
				"message": "Process not running"
			}
	except Exception as exception:
		if tasks.get(full_id):
			tasks[full_id].start.cancel()
			await tasks[full_id].start
		processes[full_id] = None
		tasks[full_id].start = None

		raise exception


async def controller_strategy_stop(strategy: str, version: str, id: str):
	full_id = f"""{strategy}:{version}:{id}"""

	try:
		if processes.get(full_id):
			tasks[full_id].start.cancel()
			tasks[full_id].stop = asyncio.create_task(processes[full_id].stop())
			# await tasks[full_id].stop

			return {
				"message": "Stopping..."
			}
		else:
			return {
				"message": "Process not running"
			}
	except Exception as exception:
		if tasks.get(full_id):
			tasks[full_id].start.cancel()
			await tasks[full_id].start

		raise exception
	finally:
		processes[full_id] = None
		tasks[full_id].start = None