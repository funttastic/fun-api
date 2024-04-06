import json
import os
from typing import Any

import requests
from dotmap import DotMap

from core.properties import properties
from core.types import HttpMethod


async def hummingbot_client_router(
	method: HttpMethod = HttpMethod.GET,
	host: str = None,
	port: int = None,
	url: str = None,
	headers: Any = None,
	paths: dict[str, Any] = None,
	parameters: dict[str, Any] = None,
	body: dict[str, Any] = None,
	certificates: DotMap[str, str] = None
) -> DotMap[str, Any] | Any:
	raise NotImplemented()
