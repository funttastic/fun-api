from logging import DEBUG

import asyncio
import inspect
import logging
import traceback
from functools import wraps
from typing import Any


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


def log(level: int, message: str = "", object: Any = None):
	from core.logger import logger
	logger.log(level=level, message=message, object=object, frame=inspect.currentframe().f_back.f_back)


def sync_logged_method(method):

	@wraps(method)
	def wrapper(*args, **kwargs):
		log(DEBUG, f"""Starting {method.__name__}...""")
		try:
			result = method(*args, **kwargs)

			log(
				DEBUG,
				f"""Successfully executed {method.__name__}.""",
				# object={
				# 	"args": args,
				# 	"kwargs": kwargs,
				# 	"result": result
				# }
			)

			return result
		except Exception as exception:
			log(
				DEBUG,
				f"""Exception raised in {method.__name__}: {exception}.""",
				# object={
				# 	"args": args,
				# 	"kwargs": kwargs,
				# 	"exception": exception
				# }
			)

			raise

	return wrapper


def async_logged_method(method):
	@wraps(method)
	async def wrapper(*args, **kwargs):
		log(DEBUG, f"""Starting {method.__name__}...""")
		try:
			result = await method(*args, **kwargs)

			log(
				DEBUG,
				f"""Successfully executed {method.__name__}.""",
				# object={
				# 	"args": args,
				# 	"kwargs": kwargs,
				# 	"result": result
				# }
			)

			return result
		except Exception as exception:
			log(
				DEBUG,
				f"""Exception raised in {method.__name__}: {exception}.""",
				# object={
				# 	"args": args,
				# 	"kwargs": kwargs,
				# 	"exception": exception
				# }
			)

			raise

	return wrapper


def logged_class(cls):
	for attr, method in cls.__dict__.items():
		if callable(method):
			if asyncio.iscoroutinefunction(method):
				setattr(cls, attr, async_logged_method(method))
			else:
				setattr(cls, attr, sync_logged_method(method))

	return cls

