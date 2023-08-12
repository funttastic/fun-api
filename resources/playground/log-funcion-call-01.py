import os

import nest_asyncio
from fastapi import FastAPI

from properties import properties

nest_asyncio.apply()
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.join(__file__))))
debug = properties.get_or_default('server.debug', False)
app = FastAPI(debug=debug, root_path=root_path)
properties.load(app)

from hummingbot.utils import log_function_call


class Test:

	@staticmethod
	@log_function_call
	def test_function(a, b, c=5):
		return a + b + c

	@staticmethod
	@log_function_call
	def test_exception(a, b):
		return a / b


if __name__ == "__main__":
	Test.test_function(1, 2, c=3) # Deverá imprimir os argumentos e o resultado (6)
	Test.test_exception(10, 0) # Deverá imprimir os argumentos e a exceção
