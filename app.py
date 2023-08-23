import asyncio
import atexit
import logging
import os
import signal
import ssl
from typing import Any, Dict

import nest_asyncio
import uvicorn
from dotmap import DotMap
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.requests import Request

from constants import constants
from hummingbot.router import router
from hummingbot.strategies.strategy_base import StrategyBase
from hummingbot.strategies.types import Strategy
from properties import properties
from utils import HttpMethod

nest_asyncio.apply()
root_path = os.path.dirname(__file__)
debug = properties.get_or_default('server.debug', True)
app = FastAPI(debug=debug, root_path=root_path)
properties.load(app)
# Needs to come after properties loading
from logger import logger

tasks: DotMap[str, asyncio.Task] = DotMap({
})

processes: DotMap[str, StrategyBase] = DotMap({
})


@app.get("/")
@app.post("/")
@app.put("/")
@app.delete("/")
@app.patch("/")
@app.head("/")
@app.options("/")
@app.get("/{subpath}")
@app.post("/{subpath}")
@app.put("/{subpath}")
@app.delete("/{subpath}")
@app.patch("/{subpath}")
@app.head("/{subpath}")
@app.options("/{subpath}")
async def root(request: Request, subpath=''):
	parameters = dict(request.query_params)
	try:
		body = await request.json()
	except:
		body = {}
	# headers = dict(request.headers)

	method = HttpMethod[request.method.upper()]

	return JSONResponse((await router(
		method=method,
		url=subpath,
		parameters=parameters,
		body=body,
		certificates=None
	)).toDict())


@app.post("/strategy/start")
async def strategy_start(request: Request) -> Dict[str, Any]:
	body = await request.json()

	strategy = body["strategy"]
	version = body["version"]
	id = body["id"]

	full_id = f"""{strategy}:{version}:{id}"""

	try:
		import hummingbot.strategies.pure_market_making.v_1_0_0.supervisor
		import hummingbot.strategies.pure_market_making.v_1_0_0.worker

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


@app.post("/strategy/status")
async def strategy_status(request: Request) -> Dict[str, Any]:
	body = await request.json()

	strategy = body["strategy"]
	version = body["version"]
	id = body["id"]

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


@app.post("/strategy/stop")
async def strategy_stop(request: Request) -> Dict[str, Any]:
	body = await request.json()

	strategy = body["strategy"]
	version = body["version"]
	id = body["id"]

	full_id = f"""{strategy}:{version}:{id}"""

	try:
		if processes.get(full_id):
			tasks[full_id].start.cancel()
			tasks[full_id].stop = asyncio.create_task(processes[full_id].stop())
			await tasks[full_id].stop

			return {
				"message": "Successfully stopped"
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


def start():
	signal.signal(signal.SIGTERM, shutdown)
	signal.signal(signal.SIGINT, shutdown)

	logger.log(logging.INFO, f'Environment: {properties.get("environment")}')

	host = properties.get('server.host')
	port = properties.get('server.port')
	environment = properties.get_or_default('server.environment', constants.environments.production)

	os.environ['ENV'] = environment

	path_prefix = properties.get_or_default(
		"hummingbot.gateway.certificates.path.base.absolute",
		os.path.join(properties.get("root_path"), properties.get("hummingbot.gateway.certificates.path.base.relative")),
	)
	certificates = DotMap({
		"server_private_key_password": properties.get("hummingbot.gateway.certificates.server_private_key_password"),
		"server_certificate": os.path.abspath(f"""{path_prefix}/{properties.get("hummingbot.gateway.certificates.path.server_certificate")}"""),
		"server_private_key": os.path.abspath(f"""{path_prefix}/{properties.get("hummingbot.gateway.certificates.path.server_private_key")}"""),
		"certificate_authority_certificate": os.path.abspath(f"""{path_prefix}/{properties.get("hummingbot.gateway.certificates.path.certificate_authority_certificate")}""")
	}, _dynamic=False)

	uvicorn.run(
		"app:app",
		host=host,
		port=port,
		log_level=logging.DEBUG,
		# reload=debug,
		app_dir=os.path.dirname(__file__),
		ssl_certfile=certificates.server_certificate,
		ssl_keyfile=certificates.server_private_key,
		ssl_keyfile_password=certificates.server_private_key_password,
		ssl_ca_certs=certificates.certificate_authority_certificate,
		ssl_cert_reqs=ssl.CERT_REQUIRED
	)


# noinspection PyUnusedLocal
def shutdown(*args):
	for task in tasks.values():
		if task:
			try:
				task.cancel()
			except Exception as exception:
				pass


@atexit.register
def shutdown_helper():
	shutdown()
	asyncio.get_event_loop().close()


if __name__ == '__main__':
	try:
		start()
	finally:
		shutdown_helper()
