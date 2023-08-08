import asyncio
import hashlib
import jsonpickle
import time
import traceback
from datetime import datetime
from typing import Any, List


def current_timestamp() -> int:
	return int(time.time() * 1000)


def generate_hash(input: Any) -> str:
	return generate_hashes([input])[0]


def generate_hashes(inputs: List[Any]) -> List[str]:
	hashes = []
	salt = datetime.now()

	for input in inputs:
		serialized = jsonpickle.encode(input, unpicklable=True)
		hasher = hashlib.md5()
		target = f"{salt}{serialized}".encode("utf-8")
		hasher.update(target)
		hash = hasher.hexdigest()

		hashes.append(hash)

	return hashes


def convert_hb_trading_pair_to_market_name(trading_pair: str) -> str:
	return trading_pair.replace("-", "/")


def convert_market_name_to_hb_trading_pair(market_name: str) -> str:
	return market_name.replace("/", "-")


def automatic_retry_with_timeout(retries=1, delay=0, timeout=None):
	def decorator(func):
		async def wrapper(*args, **kwargs):
			errors = []
			number_of_retries = range(retries)
			for i in range(retries):
				try:
					result = await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
					return result
				except Exception as exception:
					if i == number_of_retries:
						error = traceback.format_exception(exception)
					else:
						error = str(exception)

					errors.append(''.join(error))

					await asyncio.sleep(delay)

			error_message = f"Function failed after {retries} attempts. Here are the errors:\n" + "\n".join(errors)

			raise Exception(error_message)
		return wrapper
	return decorator
