import asyncio
import inspect
import logging
import traceback
from datetime import datetime
from enum import Enum
from functools import reduce, wraps
from typing import Any

import jsonpickle
from dateutil.relativedelta import relativedelta
from deepmerge import always_merger
from dotmap import DotMap


def human_readable(delta):
	attributes = ['years', 'months', 'days', 'hours', 'minutes', 'seconds', 'microseconds']

	return ', '.join([
		(f'{getattr(delta, attribute)} {attribute}' if getattr(delta, attribute) > 0 else attribute[:-1])\
		for attribute in attributes if getattr(delta, attribute)
	])


def elapsed_time(start_time, end_time):
	start = datetime.fromtimestamp(start_time)
	end = datetime.fromtimestamp(end_time)
	delta = relativedelta(end, start)

	return human_readable(delta)


def safe_deep_get(self, keys, default=None):
	return reduce(
		lambda dictionary, key:
			dictionary.get(key, default) if isinstance(dictionary, dict)
			else default, keys.split("."), self
	)


def deep_merge(base, next):
	return always_merger.merge(base, next)


def dump(target: Any):
	try:
		if isinstance(target, str):
			return target

		if isinstance(target, DotMap):
			target = target.toDict()

		return jsonpickle.encode(target, unpicklable=True, indent=2)
	except (Exception,):
		return target


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


def log_function_call(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		from core.logger import logger

		frame = inspect.currentframe().f_back

		# fully_qualified_name = f"{func.__module__}.{func.__qualname__}"
		fully_qualified_name = func.__qualname__

		logger.log(logging.DEBUG, f"{fully_qualified_name} input", {"args": args, "kwargs": kwargs}, frame=frame)

		try:
			output = func(*args, **kwargs)

			logger.log(logging.DEBUG, f"{fully_qualified_name} output", output, frame=frame)
			return output
		except Exception as exception:
			logger.log(logging.DEBUG, f"{fully_qualified_name} exception", exception, frame=frame)

			raise

	return wrapper


def log_function_exception(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		from core.logger import logger

		frame = inspect.currentframe().f_back
		fully_qualified_name = func.__qualname__

		try:
			return func(*args, **kwargs)
		except Exception as exception:
			formatted_exception = traceback.format_exception(type(exception), exception, exception.__traceback__)
			formatted_exception = "\n".join(formatted_exception)

			logger.log(logging.DEBUG, f"{fully_qualified_name} input", {"args": args, "kwargs": kwargs}, frame=frame)
			logger.log(logging.DEBUG, f"{fully_qualified_name} exception", formatted_exception, frame=frame)
			raise

	return wrapper


def log_class_exceptions(cls):
	for name, method in inspect.getmembers(cls, inspect.isfunction):
		setattr(cls, name, log_function_exception(method))

	return cls


class HttpMethod(Enum):
	GET = 'get'
	POST = 'post'
	PUT = 'put'
	DELETE = 'delete'
	PATCH = 'patch'
	HEAD = 'head'
	OPTIONS = 'options'
