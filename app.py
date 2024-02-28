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
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from pathlib import Path
from pydantic import BaseModel
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED
from typing import Any, Dict, Optional

from core.constants import constants
from core.properties import properties
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
from hummingbot.router import router
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


class Token(BaseModel):
	token: str
	type: str


async def authenticate(username: str, password: str):
	try:
		if properties.get_or_default("server.enforce_authentication", True):
			return DotMap(
				json.loads(
					str(
						await execute(
							str(constants.system.commands.authenticate).format(
								username=username, password=password
							)

						)
					)
				),
				_dynamic=False
			)
		else:
			return DotMap({"username": username, "password": password}, _dynamic=False)
	except Exception as exception:
		return False


def create_jwt_token(data: dict, expires_delta: datetime.timedelta):
	to_encode = data.copy()
	expiration_datetime = datetime.datetime.now(datetime.UTC) + expires_delta
	to_encode.update({"exp": expiration_datetime})
	encoded_jwt = jwt.encode(to_encode, properties.get("password"), algorithm=constants.authentication.jwt.algorithm)

	return encoded_jwt


def validate_token(request: Request) -> bool:
	try:
		test = OAuth2PasswordBearer(tokenUrl="auth/login")(request)

		print(test)

		authorization = request.headers.get("Authorization")
		if not authorization:
			return False

		token = str(authorization).strip().removeprefix("Bearer ")
		if not token:
			return False

		payload = jwt.decode(token, properties.get("password"), algorithms=[constants.authentication.jwt.algorithm])
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


def validate_certificate(request: Request) -> bool:
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


def validate(request: Request) -> Request:
	try:
		if not validate_token(request) and not validate_certificate(request):
			raise unauthorized_exception

		return request
	except Exception as exception:
		raise unauthorized_exception


@app.post("/auth/login", response_model=Token)
async def auth_login(request: Credentials):
	credentials = await authenticate(request.username, request.password)

	if not credentials:
		raise unauthorized_exception

	token_expiration_delta = datetime.timedelta(minutes=constants.authentication.jwt.token.expiration)
	token = create_jwt_token(
		data={"sub": credentials.username}, expires_delta=token_expiration_delta
	)

	return {"token": token, "type": constants.authentication.jwt.token.type}


@app.get("/auth/token")
async def auth_token(request: Request):
	validate(request)
	
	return {"token": request.headers.get("Authorization").removeprefix("Bearer "), "type": constants.authentication.jwt.token.type}


@app.get("/service/status")
async def status(request: Request) -> Dict[str, Any]:
	validate(request)

	try:
		body = await request.json()
	except JSONDecodeError:
		body = {}

	return DotMap(await controller.service_status(body)).toDict()


@app.post("/service/start")
async def start(request: Request) -> Dict[str, Any]:
	validate(request)

	try:
		body = await request.json()
	except JSONDecodeError:
		body = {}

	body = DotMap(body, _dynamic=False)

	return await controller.service_start(body)


@app.post("/service/stop")
async def stop(request: Request) -> Dict[str, Any]:
	validate(request)

	try:
		body = await request.json()
	except JSONDecodeError:
		body = {}

	body = DotMap(body, _dynamic=False)

	return await controller.service_stop(body)


@app.get("/strategy/status")
async def strategy_status(request: Request) -> Dict[str, Any]:
	validate(request)

	try:
		body = await request.json()
	except JSONDecodeError:
		body = {}

	return await controller.strategy_status(body)


@app.post("/strategy/start")
async def strategy_start(request: Request) -> Dict[str, Any]:
	validate(request)

	try:
		body = await request.json()
	except JSONDecodeError:
		body = {}

	return await controller.strategy_start(body)


@app.post("/strategy/stop")
async def strategy_stop(request: Request) -> Dict[str, Any]:
	validate(request)

	try:
		body = await request.json()
	except JSONDecodeError:
		body = {}

	return await controller.strategy_stop(body)


@app.get("/strategy/worker/status")
async def strategy_worker_status(request: Request) -> Dict[str, Any]:
	validate(request)

	try:
		body = await request.json()
	except JSONDecodeError:
		body = {}

	return await controller.strategy_worker_status(body)


@app.post("/strategy/worker/start")
async def strategy_worker_start(request: Request) -> Dict[str, Any]:
	validate(request)

	try:
		body = await request.json()
	except JSONDecodeError:
		body = {}

	return await controller.strategy_worker_start(body)


@app.post("/strategy/worker/stop")
async def strategy_worker_stop(request: Request) -> Dict[str, Any]:
	validate(request)

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
async def root(request: Request, subpath='', token: str = Depends(oauth2_scheme)):
	validate(request)

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

	properties.set("password", os.environ.get("PASSWORD", properties.get("hummingbot.gateway.certificates.server_private_key_password")))

	certificates = DotMap({
		"server_private_key_password": properties.get("password"),
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
