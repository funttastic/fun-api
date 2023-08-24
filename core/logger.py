import inspect
import logging
import traceback
from pathlib import Path
from singleton.singleton import ThreadSafeSingleton
from typing import Any

from core.telegram import telegram
from core.utils import dump
from core.properties import properties


@ThreadSafeSingleton
class Logger(object):

	def __init__(self):
		self.level = properties.get('logging.level')
		self.telegram_level: bool = properties.get('telegram.level')
		self.use_telegram: bool = properties.get('logging.use_telegram')

		directory = properties.get('logging.directory')
		Path(directory).mkdir(parents=True, exist_ok=True)

		filename = properties.get('logging.filename')

		format = properties.get('logging.format')

		logging.basicConfig(
			level=self.level,
			format=format,
			handlers=[
				logging.StreamHandler(),
				logging.FileHandler(f'{directory}/{filename}', mode='a')
			]
		)

	def log(self, level: int, message: str = "", object: Any = None, prefix: str = "", frame: Any = None):
		if not frame:
			frame = inspect.currentframe().f_back

		filename = frame.f_code.co_filename.removeprefix(f"""{properties.get("root_path")}/""")
		line_number = frame.f_lineno
		function_name = frame.f_code.co_name

		if object:
			message = f'{message}:\n{dump(object)}'

		message = f"{prefix} {filename}:{line_number} {function_name}: {message}"

		logging.log(level, message)

		if self.use_telegram and level >= self.level and level >= self.telegram_level:
			telegram.send(message)

	def ignore_exception(self, exception: Exception, prefix: str = "", frame=inspect.currentframe().f_back):
		formatted_exception = traceback.format_exception(type(exception), exception, exception.__traceback__)
		formatted_exception = "\n".join(formatted_exception)

		message = f"""Ignored exception: {type(exception).__name__} {str(exception)}:\n{formatted_exception}"""

		self.log(logging.WARNING, prefix=prefix, message=message, frame=frame)


logger = Logger.instance()
