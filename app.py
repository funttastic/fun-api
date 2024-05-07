from json import JSONDecodeError

import asyncio
import atexit
import datetime
import json
import logging
import nest_asyncio
import os
import signal
import ssl
import threading
import uvicorn
from dotmap import DotMap
from fastapi import FastAPI, WebSocket, HTTPException, Response
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from pathlib import Path
from pydantic import BaseModel
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED
from typing import Any, Dict

from core.constants import constants
from core.properties import properties
from core.router.hummingbot_client import hummingbot_client_router
from core.router.hummingbot_gateway import hummingbot_gateway_router
from core.system import execute
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
from hummingbot.strategies.strategy_base import StrategyBase

tasks: DotMap[str, asyncio.Task] = DotMap({
})

processes: DotMap[str, StrategyBase] = DotMap({
})

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

unauthorized_exception = HTTPException(
	status_code=HTTP_401_UNAUTHORIZED,
	detail="Unauthorized",
	headers={"WWW-Authenticate": "Bearer"},
)


class Credentials(BaseModel):
	username: str
	password: str


async def authenticate(username: str, password: str):
	try:
		if properties.get_or_default("server.authentication.enforce", True):
			result = DotMap(
				json.loads(
					str(
						await execute(
							str(properties.get("system.commands.authenticate")).format(
								username=username, password=password
							)

						)
					)
				),
				_dynamic=False
			)

			properties.set("admin.username", result.username)

			return result
		else:
			return DotMap({"username": username, "password": password}, _dynamic=False)
	except Exception as exception:
		return False


def create_jwt_token(data: dict, expires_delta: datetime.timedelta):
	to_encode = data.copy()
	expiration_datetime = datetime.datetime.now(datetime.UTC) + expires_delta
	to_encode.update({"exp": expiration_datetime})
	encoded_jwt = jwt.encode(to_encode, properties.get("admin.password"), algorithm=constants.authentication.jwt.algorithm)

	return encoded_jwt


async def validate_token(request: Request | WebSocket) -> bool:
	try:
		token = request.cookies.get("access_token")

		if token:
			token = token.removeprefix("Bearer ")
		else:
			authorization = request.headers.get("Authorization")
			if not authorization:
				return False

			token = str(authorization).strip().removeprefix("Bearer ")

		if not token:
			return False

		payload = jwt.decode(token, properties.get("admin.password"), algorithms=[constants.authentication.jwt.algorithm])
		if not payload:
			return False

		token_expiration_timestamp = payload.get("exp")
		token_expiration_datetime = datetime.datetime.fromtimestamp(token_expiration_timestamp, datetime.UTC)
		if not token_expiration_datetime:
			return False

		if datetime.datetime.now(datetime.UTC) > token_expiration_datetime:
			return False

		return True
	except Exception as exception:
		return False


async def validate_certificate(request: Request | WebSocket) -> bool:
	try:
		provided_certificate = request.headers.get("X-SSL-Cert-Subject")
		client_verify = request.headers.get("X-SSL-Client-Verify")
		client_s_dn = request.headers.get("X-SSL-Client-S-DN")

		if not provided_certificate and not client_verify and not client_s_dn:
			return False

		if client_verify != "SUCCESS":
			return False

		certificate_authority_certificate = properties.get("hummingbot.gateway.certificates.certificate.certificate_authority_certificate")
		client_certificate = properties.get("hummingbot.gateway.certificates.certificate.client_certificate")

		now = datetime.datetime.now(datetime.UTC)
		if client_certificate.not_valid_before > now or client_certificate.not_valid_after < now:
			return False

		if client_certificate.issuer != certificate_authority_certificate.subject:
			return False

		if client_certificate.subject.rfc4514_string() != provided_certificate:
			return False

		return True
	except Exception as exception:
		return False


async def validate_request_token(request: Request):
	return await validate_token(request)


async def validate_websocket_token(websocket: WebSocket):
	try:
		if not await validate_token(websocket):
			await websocket.close(code=1008)

			return False
	except Exception as e:
		await websocket.close(code=1008)

		return False

	return True


async def validate(target: Request | WebSocket) -> Request:
	try:
		if properties.get_or_default("server.authentication.require.token", True):
			if isinstance(target, Request):
				if not await validate_request_token(target):
					raise unauthorized_exception
			elif isinstance(target, WebSocket):
				if not await validate_websocket_token(target):
					raise unauthorized_exception
			else:
				raise unauthorized_exception

		# TODO In order to make this validation to work, a reverse proxy must be configured to forward some headers as well.
		# if properties.get_or_default("server.authentication.require.certificate", True):
		# 	if not validate_certificate(target):
		# 		raise unauthorized_exception

		return target
	except Exception as exception:
		raise unauthorized_exception


@app.post("/auth/signUp")
async def auth_sign_up(_request: Request, response: Response):
	raise NotImplemented


@app.post("/auth/signIn")
async def auth_sign_in(request: Credentials, response: Response):
	credentials = await authenticate(request.username, request.password)

	if not credentials:
		raise unauthorized_exception

	token_expiration_delta = datetime.timedelta(minutes=constants.authentication.jwt.token.expiration)
	token = create_jwt_token(
		data={"sub": credentials.username}, expires_delta=token_expiration_delta
	)

	response.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True, secure=True, samesite="lax", max_age=60 * 60 * 1000, path="/", domain="localhost")

	return {"token": token, "type": constants.authentication.jwt.token.type}


@app.post("/auth/signOut")
async def auth_sign_out(_request: Request, response: Response):
	response.delete_cookie(key="access_token")

	return {"message": "Cookie successfully deleted."}


@app.post("/auth/refresh")
async def auth_refresh(request: Request, response: Response):
	await validate(request)

	token_expiration_delta = datetime.timedelta(minutes=constants.authentication.jwt.token.expiration)
	token = create_jwt_token(
		data={"sub": properties.get("admin.username")}, expires_delta=token_expiration_delta
	)

	response.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True, secure=True, samesite="lax", max_age=60 * 60 * 1000, path="/", domain="localhost")

	return {"token": token, "type": constants.authentication.jwt.token.type}


@app.get("/service/status")
async def service_status(request: Request) -> Dict[str, Any]:
	await validate(request)

	try:
		body = await request.json()
	except JSONDecodeError:
		body = {}

	return DotMap(await controller.service_status(body)).toDict()


@app.post("/service/start")
async def service_start(request: Request) -> Dict[str, Any]:
	await validate(request)

	try:
		body = await request.json()
	except JSONDecodeError:
		body = {}

	body = DotMap(body, _dynamic=False)

	return await controller.service_start(body)


@app.post("/service/stop")
async def service_stop(request: Request) -> Dict[str, Any]:
	await validate(request)

	try:
		body = await request.json()
	except JSONDecodeError:
		body = {}

	body = DotMap(body, _dynamic=False)

	return await controller.service_stop(body)


@app.get("/strategy/status")
async def strategy_status(request: Request) -> Dict[str, Any]:
	await validate(request)

	try:
		body = await request.json()
	except JSONDecodeError:
		body = {}

	return await controller.strategy_status(body)


@app.post("/strategy/start")
async def strategy_start(request: Request) -> Dict[str, Any]:
	await validate(request)

	try:
		body = await request.json()
	except JSONDecodeError:
		body = {}

	return await controller.strategy_start(body)


@app.post("/strategy/stop")
async def strategy_stop(request: Request) -> Dict[str, Any]:
	await validate(request)

	try:
		body = await request.json()
	except JSONDecodeError:
		body = {}

	return await controller.strategy_stop(body)


@app.get("/strategy/worker/status")
async def strategy_worker_status(request: Request) -> Dict[str, Any]:
	await validate(request)

	try:
		body = await request.json()
	except JSONDecodeError:
		body = {}

	return await controller.strategy_worker_status(body)


@app.post("/strategy/worker/start")
async def strategy_worker_start(request: Request) -> Dict[str, Any]:
	await validate(request)

	try:
		body = await request.json()
	except JSONDecodeError:
		body = {}

	return await controller.strategy_worker_start(body)


@app.post("/strategy/worker/stop")
async def strategy_worker_stop(request: Request) -> Dict[str, Any]:
	await validate(request)

	try:
		body = await request.json()
	except JSONDecodeError:
		body = {}

	return await controller.strategy_worker_stop(body)

@app.get("/hummingbot/gateway/")
@app.post("/hummingbot/gateway/")
@app.put("/hummingbot/gateway/")
@app.delete("/hummingbot/gateway/")
@app.patch("/hummingbot/gateway/")
@app.head("/hummingbot/gateway/")
@app.options("/hummingbot/gateway/")
@app.get("/hummingbot/gateway/{subpath:path}")
@app.post("/hummingbot/gateway/{subpath:path}")
@app.post("/hummingbot/gateway/{subpath:path}")
@app.put("/hummingbot/gateway/{subpath:path}")
@app.delete("/hummingbot/gateway/{subpath:path}")
@app.patch("/hummingbot/gateway/{subpath:path}")
@app.head("/hummingbot/gateway/{subpath:path}")
@app.options("/hummingbot/gateway/{subpath:path}")
async def hummingbot_gateway(request: Request, subpath=''):
	await validate(request)

	paths = DotMap(request.path_params, _dynamic=False)
	parameters = DotMap(request.query_params, _dynamic=False)
	try:
		body = DotMap(await request.json(), _dynamic=False)
	except:
		body = DotMap({}, _dynamic=False)
	headers = DotMap(request.headers.raw, _dynamic=False)

	method = HttpMethod[request.method.upper()]

	response = await hummingbot_gateway_router(
		method=method,
		url=subpath,
		paths=paths,
		parameters=parameters,
		headers=headers,
		body=body,
		certificates=None
	)

	try:
		if response is not None:
			subpath = request.path_params['subpath']

			if subpath == "wallet/add":
				publickey = response["address"]
				chain = body['chain']

				controller.update_gateway_connections({"chain": chain, "network": body["network"], "publickey": publickey, "subpath": subpath})
			elif subpath == "wallet/remove":
				publickey = body["address"]
				chain = body['chain']

				controller.update_gateway_connections({"chain": chain, "address": publickey, "subpath": subpath})

			if not response:
				response = DotMap({}, _dynamic=False)

			return JSONResponse(response.toDict())
		else:
			return {}
	except Exception as exception:
		raise exception


@app.get("/hummingbot/client/")
@app.post("/hummingbot/client/")
@app.put("/hummingbot/client/")
@app.delete("/hummingbot/client/")
@app.patch("/hummingbot/client/")
@app.head("/hummingbot/client/")
@app.options("/hummingbot/client/")
@app.get("/hummingbot/client/{subpath:path}")
@app.post("/hummingbot/client/{subpath:path}")
@app.post("/hummingbot/client/{subpath:path}")
@app.put("/hummingbot/client/{subpath:path}")
@app.delete("/hummingbot/client/{subpath:path}")
@app.patch("/hummingbot/client/{subpath:path}")
@app.head("/hummingbot/client/{subpath:path}")
@app.options("/hummingbot/client/{subpath:path}")
async def hummingbot_client(request: Request, subpath=''):
	await validate(request)

	paths = DotMap(request.path_params)
	parameters = DotMap(request.query_params)
	try:
		body = DotMap(await request.json())
	except:
		body = DotMap({})
	headers = DotMap(request.headers.raw)

	method = HttpMethod[request.method.upper()]

	response = await hummingbot_client_router(
		method=method,
		url=subpath,
		paths=paths,
		parameters=parameters,
		headers=headers,
		body=body,
		certificates=None
	)

	return JSONResponse(response.toDict())


@app.websocket("/ws/log")
async def websocket_log(websocket: WebSocket):
	await websocket.accept()

	await validate(websocket)

	try:
		while True:
			id = await websocket.receive_text()

			async for message in controller.websocket_log(DotMap({"id": id})):
				await websocket.send_text(message)
	except Exception as exception:
		raise exception


async def start_api():
	signal.signal(signal.SIGTERM, shutdown)
	signal.signal(signal.SIGINT, shutdown)

	logger.log(logging.INFO, f'Environment: {properties.get("environment")}')

	host = os.environ.get("HOST", properties.get('server.host'))
	port = int(os.environ.get("PORT", properties.get('server.port')))
	environment = properties.get_or_default('server.environment', constants.environments.production)

	os.environ['ENV'] = environment

	path_prefix = properties.get_or_default(
		"hummingbot.gateway.certificates.path.base.absolute",
		os.path.join(properties.get("root_path"), properties.get("hummingbot.gateway.certificates.path.base.relative")),
	)

	properties.set("hummingbot.gateway.certificates.path.certificate_authority_certificate", os.path.abspath(os.path.join(path_prefix, properties.get("hummingbot.gateway.certificates.path.certificate_authority_certificate"))))
	properties.set("hummingbot.gateway.certificates.path.certificate_authority_private_key", os.path.abspath(os.path.join(path_prefix, properties.get("hummingbot.gateway.certificates.path.certificate_authority_private_key"))))
	properties.set("hummingbot.gateway.certificates.path.client_certificate", os.path.abspath(os.path.join(path_prefix, properties.get("hummingbot.gateway.certificates.path.client_certificate"))))
	properties.set("hummingbot.gateway.certificates.path.client_certificate_signing_request", os.path.abspath(os.path.join(path_prefix, properties.get("hummingbot.gateway.certificates.path.client_certificate_signing_request"))))
	properties.set("hummingbot.gateway.certificates.path.client_private_key", os.path.abspath(os.path.join(path_prefix, properties.get("hummingbot.gateway.certificates.path.client_private_key"))))
	properties.set("hummingbot.gateway.certificates.path.server_certificate", os.path.abspath(os.path.join(path_prefix, properties.get("hummingbot.gateway.certificates.path.server_certificate"))))
	properties.set("hummingbot.gateway.certificates.path.server_certificate_signing_request", os.path.abspath(os.path.join(path_prefix, properties.get("hummingbot.gateway.certificates.path.server_certificate_signing_request"))))
	properties.set("hummingbot.gateway.certificates.path.server_private_key", os.path.abspath(os.path.join(path_prefix, properties.get("hummingbot.gateway.certificates.path.server_private_key"))))

	properties.set("admin.password", os.environ.get("PASSWORD", properties.get("hummingbot.gateway.certificates.server_private_key_password")))

	certificates = DotMap({
		"server_private_key_password": properties.get("admin.password"),
		"server_certificate": properties.get("hummingbot.gateway.certificates.path.server_certificate"),
		"server_private_key": properties.get("hummingbot.gateway.certificates.path.server_private_key"),
		"certificate_authority_certificate": properties.get("hummingbot.gateway.certificates.path.certificate_authority_certificate")
	}, _dynamic=False)

	key = "hummingbot.gateway.certificates.path.certificate_authority_certificate"
	with open(properties.get(key), "rb") as file:
		content = file.read()
		properties.set(key, content)

	key = "hummingbot.gateway.certificates.path.client_certificate"
	with open(properties.get(key), "rb") as file:
		content = file.read()
		properties.set(key, content)

	if properties.get_or_default("server.authentication.require.certificate", True):
		certificate_requirement = ssl.CERT_REQUIRED
	else:
		certificate_requirement = ssl.CERT_OPTIONAL

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
		ssl_cert_reqs=certificate_requirement
	)
	server = uvicorn.Server(config)

	await server.serve()

	if environment == constants.environments.development:
		import pydevd_pycharm
		pydevd_pycharm.settrace('localhost', port=30001, stdoutToServer=True, stderrToServer=True, suspend=False)


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
