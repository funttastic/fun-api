import json
import os
from typing import Any

import requests
from dotmap import DotMap

from core.properties import properties
from core.types import HttpMethod


async def hummingbot_gateway_router(
	method: HttpMethod = HttpMethod.GET,
	host: str = None,
	port: int = None,
	url: str = None,
	headers: Any = None,
	paths: DotMap[str, Any] = None,
	parameters: DotMap[str, Any] = None,
	body: DotMap[str, Any] = None,
	certificates: DotMap[str, str] = None
) -> DotMap[str, Any] | Any:
	if not host:
		host = properties.get("hummingbot.gateway.host")

	if not port:
		port = properties.get("hummingbot.gateway.port")

	if not url:
		url = "/"

	if not url.startswith("/"):
		url = f"/{url}"

	if url.startswith("/hummingbot/gateway/"):
		url = url.replace("/hummingbot/gateway/", "/")

	final_url = f"""{host}:{port}{url}"""

	if not headers:
		headers = DotMap({
			"Content-Type": "application/json"
		}, _dynamic=False)

	if not certificates:
		path_prefix = properties.get_or_default(
			"hummingbot.gateway.certificates.path.base.absolute",
			os.path.join(properties.get("root_path"), properties.get("hummingbot.gateway.certificates.path.base.relative")),
		)
		certificates = DotMap({
			"client_certificate": os.path.abspath(f"""{path_prefix}/{properties.get("hummingbot.gateway.certificates.path.client_certificate")}"""),
			"client_private_key": os.path.abspath(f"""{path_prefix}/{properties.get("hummingbot.gateway.certificates.path.client_private_key")}"""),
			"certificate_authority_certificate": os.path.abspath(f"""{path_prefix}/{properties.get("hummingbot.gateway.certificates.path.certificate_authority_certificate")}""")
		}, _dynamic=False)

	if body is not None:
		payload = DotMap(body, _dynamic=False).toDict()
		payload = json.dumps(payload).encode('utf-8')
	else:
		payload = None

	if headers is not None:
		headers = DotMap(headers, _dynamic=False).toDict()

	if parameters is not None:
		parameters = DotMap(parameters, _dynamic=False).toDict()

	request = {
		"url": final_url,
		"headers": headers,
		"params": parameters,
		"data": payload,
		"cert": (certificates.client_certificate, certificates.client_private_key),
		"verify": certificates.certificate_authority_certificate,
		"timeout": 60
	}

	response = getattr(requests, method.value)(**request)

	try:
		result = DotMap(response.json(), _dynamic=False)
	except:
		result = response.text

	if result and "httpErrorCode" in result:
		raise RuntimeError(
f"""\
Message: {result.message}
Error code: {result.errorCode}
Http error code: {result.httpErrorCode}
Stacktrace:\n\t{result.stack}\
"""
		)

	return result
