import asyncio
import json
import os
from dotmap import DotMap
from typing import Any, Dict, List, AsyncGenerator

from core.constants import constants, chains_connector_spec
from core.logger import logger
from core.properties import properties
from core.system import execute, execute_continuously
from core.types import SystemStatus
from core.utils import deep_merge
from hummingbot.strategies.strategy_base import StrategyBase
from hummingbot.strategies.types import Strategy

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


async def continuously_solve_services_status():
	while True:
		try:
			system = DotMap(json.loads(await execute(properties.get("system.commands.status"))), _dynamic=False)
			for (key, value) in system.items():
				if key == constants.id:
					try:
						status = DotMap(await strategy_status(DotMap({})), _dynamic=False)

						if status.get("message") == "Process not running":
							system[key] = SystemStatus.STOPPED
						else:
							system[key] = DotMap(status, _dynamic=False).status
					except Exception as exception:
						system[key] = SystemStatus.UNKNOWN
				else:
					system[key] = SystemStatus.get_by_id(value)

			current = properties.get_or_default("services.status.current", constants.services.status.default)
			final = deep_merge(current, system)

			properties.set("services.status.current", final)

			await asyncio.sleep(constants.services.status.delay / 1000.0)
		except Exception as exception:
			logger.ignore_exception(exception)

			pass


async def service_status(_options: DotMap[str, Any]) -> Dict[str, Any]:
	try:
		if not tasks[constants.services.status.task]:
			tasks[constants.services.status.task].start = asyncio.create_task(continuously_solve_services_status())

		return properties.get_or_default("services.status.current", constants.services.status.default)
	except Exception as exception:
		raise exception


async def service_start(options: DotMap[str, Any]):
	try:
		if properties.get_or_default(f"services.status.current.{options.id}", SystemStatus.UNKNOWN) in [SystemStatus.STOPPED, SystemStatus.UNKNOWN]:
			properties.set(f"services.status.current.{options.id}", SystemStatus.STARTING)

			if options.id == constants.id:
				await strategy_start(DotMap({}))
			else:
				await execute(str(properties.get(f"system.commands.start.{options.id}")).format(
					username=properties.get("admin.username"), password=properties.get("admin.password")
				))

			properties.set(f"services.status.current.{options.id}", SystemStatus.RUNNING)

			return {
				"message": f"""Service "{options.id}" has started."""
			}
		else:
			return {
				"message": f"""Service "{options.id}" is already running."""
			}
	except Exception as exception:
		raise exception


async def service_stop(options: DotMap[str, Any]):
	try:
		if properties.get_or_default(f"services.status.current.{options.id}", SystemStatus.UNKNOWN) in [SystemStatus.STARTING, SystemStatus.IDLE, SystemStatus.RUNNING]:
			properties.set(f"services.status.current.{options.id}", SystemStatus.STOPPING)

			if options.id == constants.id:
				await strategy_stop(DotMap({}))
			else:
				await execute(properties.get(f"system.commands.stop.{options.id}"))

			properties.set(f"services.status.current.{options.id}", SystemStatus.STOPPED)

			return {
				"message": f"""Service "{options.id}" has stopped."""
			}
		else:
			return {
				"message": f"""Service "{options.id}" is not running."""
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


async def websocket_log(options: Any) -> AsyncGenerator[str, None]:
	command = str(properties.get(f"system.commands.log.{options.id}"))

	async for line in execute_continuously(command):
		yield line
		await asyncio.sleep(0.1)


def update_gateway_connections(params: Any):
	absolute_file_path = os.path.expanduser(str(properties.get("hummingbot.client.gateway_connections.file_path")))

	# Opening and loading file
	if os.path.exists(absolute_file_path):
		with open(absolute_file_path) as connections_file:
			try:
				connectors_conf: List[Dict[str, str]] = json.load(connections_file)
			except json.JSONDecodeError:
				connectors_conf: List[Dict[str, str]] = []
	else:
		connectors_conf: List[Dict[str, str]] = []

	connector_name = chains_connector_spec[params["chain"].upper()]["CONNECTOR"].value
	chain = params["chain"]

	if params["subpath"] == "wallet/add":
		network = params["network"]

		new_connector_spec: Dict[str, str] = {
			"connector": connector_name,
			"chain": chain,
			"network": network,
			"trading_type": chains_connector_spec[params["chain"].upper()]["TRADING_TYPE"].value,
			"chain_type": chains_connector_spec[params["chain"].upper()]["CHAIN_TYPE"].value,
			"wallet_address": params["publickey"],
			"additional_spenders": chains_connector_spec[params["chain"].upper()]["ADDITIONAL_SPENDERS"].value,
			"additional_prompt_values": chains_connector_spec[params["chain"].upper()]["ADDITIONAL_PROMPT_VALUES"].value
		}

		updated: bool = False

		for i, c in enumerate(connectors_conf):
			if c["connector"] == connector_name and c["chain"] == chain and c["network"] == network:
				connectors_conf[i] = new_connector_spec
				updated = True
				break

		if updated is False:
			connectors_conf.append(new_connector_spec)

	elif params["subpath"] == "wallet/remove":
		connectors_conf = [c for c in connectors_conf if not (c["chain"] == chain and c["wallet_address"] == params["address"])]

	# Saving file
	with open(absolute_file_path, "w") as connections_file:
		json.dump(connectors_conf, connections_file)
