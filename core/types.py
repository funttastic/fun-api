from enum import Enum


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


class WorkerType(Enum):
	CCXT = 'ccxt'
	HB_CLIENT = 'hb-client'
	HB_GATEWAY_CLOB = 'hb-gateway-clob'
	HB_GATEWAY_KUJIRA = 'hb-gateway-kujira'
