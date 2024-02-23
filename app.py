import threading

from pathlib import Path

import asyncio
import atexit
import logging
import os
import signal
import ssl
from json import JSONDecodeError
from typing import Any, Dict

import nest_asyncio
import uvicorn
from dotmap import DotMap
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.requests import Request

from core.constants import constants
from core.properties import properties
from core.types import HttpMethod

nest_asyncio.apply()
root_path = Path(os.path.dirname(__file__)).absolute().as_posix()
debug = properties.get_or_default('server.debug', True)
app = FastAPI(debug=debug, root_path=root_path)
properties.load(app)
# Needs to come after properties loading
from core.logger import logger
from core.telegram.telegram import telegram
from core import controller
from hummingbot.router import router
from hummingbot.strategies.strategy_base import StrategyBase

tasks: DotMap[str, asyncio.Task] = DotMap({
})

processes: DotMap[str, StrategyBase] = DotMap({
})


@app.get("/service/status")
async def status(request: Request) -> Dict[str, Any]:
	try:
		body = await request.json()
	except JSONDecodeError:
		body = {}

	return (await controller.service_status(body)).toDict()


@app.post("/service/start")
async def start(request: Request) -> Dict[str, Any]:
	try:
		body = await request.json()
	except JSONDecodeError:
		body = {}

	body = DotMap(body, _dynamic=False)

	return await controller.service_start(body)


@app.post("/service/stop")
async def stop(request: Request) -> Dict[str, Any]:
	try:
		body = await request.json()
	except JSONDecodeError:
		body = {}

	body = DotMap(body, _dynamic=False)

	return await controller.service_stop(body)


@app.get("/strategy/status")
async def strategy_status(request: Request) -> Dict[str, Any]:
	try:
		body = await request.json()
	except JSONDecodeError:
		body = {}

	return await controller.strategy_status(body)


@app.post("/strategy/start")
async def strategy_start(request: Request) -> Dict[str, Any]:
	try:
		body = await request.json()
	except JSONDecodeError:
		body = {}

	return await controller.strategy_start(body)


@app.post("/strategy/stop")
async def strategy_stop(request: Request) -> Dict[str, Any]:
	try:
		body = await request.json()
	except JSONDecodeError:
		body = {}

	return await controller.strategy_stop(body)


@app.get("/strategy/worker/status")
async def strategy_worker_status(request: Request) -> Dict[str, Any]:
	try:
		body = await request.json()
	except JSONDecodeError:
		body = {}

	return await controller.strategy_worker_status(body)


@app.post("/strategy/worker/start")
async def strategy_worker_start(request: Request) -> Dict[str, Any]:
	try:
		body = await request.json()
	except JSONDecodeError:
		body = {}

	return await controller.strategy_worker_start(body)


@app.post("/strategy/worker/stop")
async def strategy_worker_stop(request: Request) -> Dict[str, Any]:
	try:
		body = await request.json()
	except JSONDecodeError:
		body = {}

	return await controller.strategy_worker_stop(body)

@app.get("/")
@app.post("/")
@app.put("/")
@app.delete("/")
@app.patch("/")
@app.head("/")
@app.options("/")
@app.get("/{subpath:path}")
@app.post("/{subpath:path}")
@app.post("/{subpath:path}")
@app.put("/{subpath:path}")
@app.delete("/{subpath:path}")
@app.patch("/{subpath:path}")
@app.head("/{subpath:path}")
@app.options("/{subpath:path}")
async def root(request: Request, subpath=''):
	parameters = dict(request.query_params)
	try:
		body = await request.json()
	except:
		body = {}
	# headers = dict(request.headers)

	method = HttpMethod[request.method.upper()]

	response = await router(
		method=method,
		url=subpath,
		parameters=parameters,
		body=body,
		certificates=None
	)

	try:
		return JSONResponse(response.toDict())
	except:
		return response


async def start_api():
	signal.signal(signal.SIGTERM, shutdown)
	signal.signal(signal.SIGINT, shutdown)

	logger.log(logging.INFO, f'Environment: {properties.get("environment")}')

	host = os.environ.get("HOST", properties.get('server.host'))
	port = int(os.environ.get("PORT", properties.get('server.port')))
	environment = properties.get_or_default('server.environment', constants.environments.production)
	server_private_key_password = os.environ.get("PASSWORD", properties.get("hummingbot.gateway.certificates.server_private_key_password"))

	os.environ['ENV'] = environment

	path_prefix = properties.get_or_default(
		"hummingbot.gateway.certificates.path.base.absolute",
		os.path.join(properties.get("root_path"), properties.get("hummingbot.gateway.certificates.path.base.relative")),
	)
	certificates = DotMap({
		"server_private_key_password": server_private_key_password,
		"server_certificate": os.path.abspath(f"""{path_prefix}/{properties.get("hummingbot.gateway.certificates.path.server_certificate")}"""),
		"server_private_key": os.path.abspath(f"""{path_prefix}/{properties.get("hummingbot.gateway.certificates.path.server_private_key")}"""),
		"certificate_authority_certificate": os.path.abspath(f"""{path_prefix}/{properties.get("hummingbot.gateway.certificates.path.certificate_authority_certificate")}""")
	}, _dynamic=False)

	config = uvicorn.Config(
		"app:app",
		host=host,
		port=port,
		log_level=logging.DEBUG,
		#reload=debug,
		# app_dir=os.path.dirname(__file__),
		ssl_certfile=certificates.server_certificate,
		ssl_keyfile=certificates.server_private_key,
		ssl_keyfile_password=certificates.server_private_key_password,
		ssl_ca_certs=certificates.certificate_authority_certificate,
		ssl_cert_reqs=ssl.CERT_REQUIRED
	)
	server = uvicorn.Server(config)
	await server.serve()


async def main():
	loop = asyncio.get_event_loop()

	tasks.telegram = loop.create_task(telegram.start_command_listener())
	tasks.api = loop.create_task(start_api())

	await asyncio.gather(*[tasks.telegram, tasks.api])


def after_startup():
	pass

	# url = f"""{properties.get("server.base_url")}/service/status"""
	# payload = {
	# }
	#
	# return print(requests.post(url, json=payload))

	# asyncio.get_event_loop().run_until_complete(controller.service_status(DotMap({})))


async def startup():
	threading.Timer(1, after_startup).start()


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


app.add_event_handler("startup", startup)
app.add_event_handler("shutdown", shutdown)


if __name__ == '__main__':
	try:
		loop = asyncio.get_event_loop()
		loop.run_until_complete(main())
	finally:
		shutdown_helper()
