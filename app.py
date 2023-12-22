import asyncio
import atexit
import os
import base64
import sys
import re
import logging
from getpass import getpass
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

from core import controller
from core.constants import constants
from core.properties import properties
from core.types import HttpMethod
from core.encrypt import *
from hummingbot.router import router
from hummingbot.strategies.strategy_base import StrategyBase

nest_asyncio.apply()
root_path = os.path.dirname(__file__)
debug = properties.get_or_default('server.debug', True)
app = FastAPI(debug=debug, root_path=root_path)
properties.load(app)
# Needs to come after properties loading
from core.logger import logger
from core.telegram.telegram import telegram

tasks: DotMap[str, asyncio.Task] = DotMap({
})

processes: DotMap[str, StrategyBase] = DotMap({
})


@app.post("/strategy/start")
async def strategy_start(request: Request) -> Dict[str, Any]:
	try:
		body = await request.json()
	except JSONDecodeError:
		body = {}

	return await controller.strategy_start(body)


@app.post("/strategy/status")
async def strategy_status(request: Request) -> Dict[str, Any]:
	try:
		body = await request.json()
	except JSONDecodeError:
		body = {}

	return await controller.strategy_status(body)


@app.post("/strategy/stop")
async def strategy_stop(request: Request) -> Dict[str, Any]:
	try:
		body = await request.json()
	except JSONDecodeError:
		body = {}

	return await controller.strategy_stop(body)


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


@app.post("/strategy/worker/status")
async def strategy_worker_status(request: Request) -> Dict[str, Any]:
	try:
		body = await request.json()
	except JSONDecodeError:
		body = {}

	return await controller.strategy_worker_status(body)

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

	return JSONResponse((await router(
		method=method,
		url=subpath,
		parameters=parameters,
		body=body,
		certificates=None
	)).toDict())


async def start_api(password):
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

	if authenticate(password):
		print("")

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
	else:
		exit(0)


def get_password():
	passphrase_minimal_length = 4
	max_attempts = 5

	for attempt in range(max_attempts):
		passphrase = getpass(f"   New passphrase [Attempt {attempt+1}/{max_attempts}]: ")

		if len(passphrase) < passphrase_minimal_length:

			print(f"\n   [!] The passphrase must have at least {passphrase_minimal_length} digits. Please try again.\n")

			if attempt == max_attempts - 1:
				print("\n   [!] You have reached the maximum number of attempts. Please try again later.\n")
				exit(0)
		else:
			for confirmation_attempt in range(max_attempts):

				confirm_passphrase = getpass(f"\n   Confirm your passphrase [Attempt {confirmation_attempt+1}/{max_attempts}]: ")

				if passphrase == confirm_passphrase:
					return passphrase

				elif confirmation_attempt == max_attempts - 1:
					print("\n   [!] The passwords do not match, check if everything is ok with your keyboard...\n")

					exit(0)
				else:
					print("\n   [!] The passwords provided are different. Please try again.")


def authenticate(password):
	server_private_key_password_hash = os.environ.get("PASSWORD_HASH", properties.get("hummingbot.gateway.certificates.server_private_key_password_hash"))

	if server_private_key_password_hash == '<password_hash>' or len(
			server_private_key_password_hash
	) == 0 or server_private_key_password_hash is None or re.fullmatch(r"^\s*$", server_private_key_password_hash):

		os.system('cls' if os.name == 'nt' else 'clear')

		print("\n   ===============     AUTHENTICATION - FUNTTASTIC HUMMINGBOT CLIENT     ===============\n")

		print("   This is the first time you will start the server. Please define a passphrase.\n")

		if len(password) > 0:
			new_passphrase = password
		else:
			new_passphrase = get_password()

		hashed_passphrase = generate_passphrase_hash(new_passphrase)

		properties.set("hummingbot.gateway.certificates.server_private_key_password_hash", hashed_passphrase)

		return True
	else:
		i = 0
		while True:
			if i == 0:
				os.system('cls' if os.name == 'nt' else 'clear')
				print("\n   ===============     AUTHENTICATION - FUNTTASTIC HUMMINGBOT CLIENT     ===============\n")

			if len(password) > 0:
				provided_passphrase = password
			else:
				provided_passphrase = getpass(f"   Enter your password to access [Attempt {i+1}/3]: ")

			passphrase_to_binary = base64.b64decode(server_private_key_password_hash)
			correct = verify_passphrase(passphrase_to_binary, provided_passphrase)

			if correct:
				os.system('cls' if os.name == 'nt' else 'clear')
				print("\n   Access granted.")
				return True
			else:
				print("\n   Incorrect password. Please try again.\n")

			i += 1
			if i >= 3:
				print("\n   Access denied. Incorrect password.\n   You have exhausted your 3 consecutive attempts.\n")
				return False


async def main(argv):
	password = argv[1] if len(argv) > 1 else ""

	loop = asyncio.get_event_loop()

	tasks.telegram = loop.create_task(telegram.start_command_listener())
	tasks.api = loop.create_task(start_api(password))

	await asyncio.gather(*[tasks.telegram, tasks.api])


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
		loop = asyncio.get_event_loop()
		loop.run_until_complete(main(sys.argv))
	finally:
		shutdown_helper()
