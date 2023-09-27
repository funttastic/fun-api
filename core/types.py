from enum import Enum
from core.constants import DB_MAXIMUM_FILLED_ORDERS, DB_MAXIMUM_CANCELLED_ORDERS


class HttpMethod(Enum):
	GET = 'get'
	POST = 'post'
	PUT = 'put'
	DELETE = 'delete'
	PATCH = 'patch'
	HEAD = 'head'
	OPTIONS = 'options'


class MaximumOrdersInDBForOrderStatus(Enum):
	FILLED = DB_MAXIMUM_FILLED_ORDERS
	CANCELLED = DB_MAXIMUM_CANCELLED_ORDERS
