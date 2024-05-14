class HummingbotBaseException(Exception):
	"""Base exception for Hummingbot."""




class MarketNameOrIdNotProvidedError(HummingbotBaseException):
	"""Exception raised when a market name or id is not provided."""


	def __init__(self, message="Market name or id not provided"):
		super().__init__(message)




class MarketNotFoundError(HummingbotBaseException):
	"""Exception raised when a market is not found."""


	def __init__(self, message="Market not found"):
		super().__init__(message)




class OrderBookNotFoundError(HummingbotBaseException):
	"""Exception raised when an order book is not found."""


	def __init__(self, message="Order book not found"):
		super().__init__(message)




class TokenNotFoundError(HummingbotBaseException):
	"""Exception raised when a token is not found."""


	def __init__(self, message="Token not found"):
		super().__init__(message)




class TokenIdentifierNotProvidedError(HummingbotBaseException):
	"""Exception raised when a token identifier is not provided."""


	def __init__(self, message="No token identifiers provided."):
		super().__init__(message)




class TickerNotFoundError(HummingbotBaseException):
	"""Exception raised when a ticker is not found."""


	def __init__(self, message="Ticker not found"):
		super().__init__(message)




class TickerIdentifierNotProvidedError(HummingbotBaseException):
	"""Exception raised when a ticker identifier is not provided."""


	def __init__(self, message="Ticker identifier not provided"):
		super().__init__(message)

