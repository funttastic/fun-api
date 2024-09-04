from enum import Enum
from dataclasses import dataclass
from dotmap import DotMap
from enum import Enum
from pydantic import BaseModel
from starlette.status import *
from typing import Any, Dict, Optional


class Environment(Enum):
	PRODUCTION = "production"
	STAGING = "staging"
	DEVELOPMENT = "development"

	@staticmethod
	def get_by_id(id_: str):
		for environment in Environment:
			if environment.value == id_.lower():
				return environment

		raise ValueError(f"""Environment with id "{id_}" not found.""")


class HttpMethod(Enum):
	GET = 'get'
	POST = 'post'
	PUT = 'put'
	DELETE = 'delete'
	PATCH = 'patch'
	HEAD = 'head'
	OPTIONS = 'options'


class SystemStatus(Enum):
	STOPPED = 'stopped'
	STARTING = 'starting'
	IDLE = 'idle'
	RUNNING = 'running'
	STOPPING = 'stopping'
	UNKNOWN = 'unknown'

	@staticmethod
	def get_by_id(id_: str):
		for status in SystemStatus:
			if status.value == id_:
				return status

		raise ValueError(f"""Status with id "{id_}" not found.""")

class Protocol(Enum):
	REST = "rest"
	WebSocket = "websocket"
	FIX = "fix"


class APIResponseStatus(Enum):
	SUCCESS = ("success", HTTP_200_OK)
	ATTRIBUTE_NOT_FOUND_ERROR = ("attribute_not_found_error", HTTP_404_NOT_FOUND)
	ATTRIBUTE_NOT_AVAILABLE_ERROR = ("attribute_not_available_error", HTTP_404_NOT_FOUND)
	EXCHANGE_NOT_AVAILABLE_ERROR = ("exchange_not_available_error", HTTP_401_UNAUTHORIZED)
	METHOD_EXECUTION_ERROR = ("method_execution_error", HTTP_400_BAD_REQUEST)
	EXPECTATION_FAILED_ERROR = ("expectation_failed_error", HTTP_417_EXPECTATION_FAILED)
	UNAUTHORIZED_ERROR = ("unauthorized_error", HTTP_401_UNAUTHORIZED)
	UNKNOWN_ERROR = ("unknown_error", HTTP_500_INTERNAL_SERVER_ERROR)

	def __init__(self, id: str, http_code: int):
		self.id = id
		self.http_code = http_code


class APIRequest:
	pass


class APIResponse(DotMap):
	title: str
	message: str
	status: APIResponseStatus
	result: Dict[str, Any] | Any


class Credentials(BaseModel):
	userTelegramId: str | int
	jwtToken: Optional[str] = None
	exchangeId: str
	exchangeEnvironment: Optional[str] = Environment.PRODUCTION.value
	exchangeProtocol: Optional[str] = Protocol.REST.value
	exchangeApiKey: str
	exchangeApiSecret: str
	exchangeOptions: Optional[dict[str, Any]] = None

	@property
	def id(self):
		return f"""{self.exchangeId}|{self.exchangeEnvironment}|{self.exchangeApiKey}"""
