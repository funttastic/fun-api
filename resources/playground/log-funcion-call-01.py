import os

import nest_asyncio
from fastapi import FastAPI

from core.properties import properties

nest_asyncio.apply()
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.join(__file__))))
debug = properties.get_or_default('server.debug', False)
app = FastAPI(debug=debug, root_path=root_path)
properties.load(app)

from hummingbot.utils import log_function_call, log_function_exception, log_class_exceptions


@log_class_exceptions
class Test_1:

	@staticmethod
	@log_function_call
	def test_function_1(a, b, c=5):
		return a + b + c

	@staticmethod
	@log_function_call
	def test_exception_1(a, b):
		return a / b

	@staticmethod
	@log_function_exception
	def test_function_2(a, b, c=5):
		return a + b + c

	@staticmethod
	@log_function_exception
	def test_exception_2(a, b):
		return a / b


@log_class_exceptions
class Test_2:

	@staticmethod
	def test_function_1(a, b, c=5):
		return a + b + c

	@staticmethod
	def test_exception_1(a, b):
		return a / b

	@staticmethod
	def test_function_2(a, b, c=5):
		return a + b + c

	@staticmethod
	def test_exception_2(a, b):
		return a / b

if __name__ == "__main__":
	# Test_1.test_function_1(1, 2, c=3)
	# Test_1.test_exception_1(10, 0)
	# Test_1.test_function_2(1, 2, c=3)
	# Test_1.test_exception_2(10, 0)

	Test_2.test_function_1(1, 2, c=3)
	Test_2.test_exception_1(10, 0)
	# Test_2.test_function_2(1, 2, c=3)
	# Test_2.test_exception_2(10, 0)
