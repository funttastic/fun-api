from __future__ import annotations

from dotmap import DotMap
from typing import Any, Dict

from core.decorators import automatic_retry_with_timeout
from core.router.hummingbot_gateway import hummingbot_gateway_router
from core.types import HttpMethod
from hummingbot.constants import NUMBER_OF_RETRIES, DELAY_BETWEEN_RETRIES, TIMEOUT


class HummingbotGateway:

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_root(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return await hummingbot_gateway_router(
			method=HttpMethod.GET,
			url='kujira',
			body=body,
		)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_token(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return await hummingbot_gateway_router(
			method=HttpMethod.GET,
			url='kujira/token',
			body=body,
		)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_tokens(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return await hummingbot_gateway_router(
			method=HttpMethod.GET,
			url='kujira/tokens',
			body=body,
		)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_tokens_all(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return await hummingbot_gateway_router(
			method=HttpMethod.GET,
			url='kujira/tokens/all',
			body=body,
		)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_market(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return await hummingbot_gateway_router(
			method=HttpMethod.GET,
			url='kujira/market',
			body=body,
		)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_markets(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return await hummingbot_gateway_router(
			method=HttpMethod.GET,
			url='kujira/markets',
			body=body,
		)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_markets_all(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return await hummingbot_gateway_router(
			method=HttpMethod.GET,
			url='kujira/markets/all',
			body=body,
		)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_order_book(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return await hummingbot_gateway_router(
			method=HttpMethod.GET,
			url='kujira/orderBook',
			body=body,
		)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_order_books(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return await hummingbot_gateway_router(
			method=HttpMethod.GET,
			url='kujira/orderBooks',
			body=body,
		)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_order_books_all(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return await hummingbot_gateway_router(
			method=HttpMethod.GET,
			url='kujira/orderBooks/all',
			body=body,
		)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_ticker(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return await hummingbot_gateway_router(
			method=HttpMethod.GET,
			url='kujira/ticker',
			body=body,
		)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_tickers(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return await hummingbot_gateway_router(
			method=HttpMethod.GET,
			url='kujira/tickers',
			body=body,
		)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_tickers_all(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return await hummingbot_gateway_router(
			method=HttpMethod.GET,
			url='kujira/tickers/all',
			body=body,
		)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_balance(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return await hummingbot_gateway_router(
			method=HttpMethod.GET,
			url='kujira/balance',
			body=body,
		)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_balances(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return await hummingbot_gateway_router(
			method=HttpMethod.GET,
			url='kujira/balances',
			body=body,
		)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_balances_all(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return await hummingbot_gateway_router(
			method=HttpMethod.GET,
			url='kujira/balances/all',
			body=body,
		)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_order(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return await hummingbot_gateway_router(
			method=HttpMethod.GET,
			url='kujira/order',
			body=body,
		)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_orders(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return await hummingbot_gateway_router(
			method=HttpMethod.GET,
			url='kujira/orders',
			body=body,
		)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_post_order(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return await hummingbot_gateway_router(
			method=HttpMethod.POST,
			url='kujira/order',
			body=body,
		)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_post_orders(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return await hummingbot_gateway_router(
			method=HttpMethod.POST,
			url='kujira/orders',
			body=body,
		)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_delete_order(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return await hummingbot_gateway_router(
			method=HttpMethod.DELETE,
			url='kujira/order',
			body=body,
		)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_delete_orders(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return await hummingbot_gateway_router(
			method=HttpMethod.DELETE,
			url='kujira/orders',
			body=body,
		)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_delete_orders_all(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return await hummingbot_gateway_router(
			method=HttpMethod.DELETE,
			url='kujira/orders/all',
			body=body,
		)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_post_market_withdraw(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return await hummingbot_gateway_router(
			method=HttpMethod.POST,
			url='kujira/market/withdraw',
			body=body,
		)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_post_market_withdraws(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return await hummingbot_gateway_router(
			method=HttpMethod.POST,
			url='kujira/market/withdraws',
			body=body,
		)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_post_market_withdraws_all(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return await hummingbot_gateway_router(
			method=HttpMethod.POST,
			url='kujira/market/withdraws/all',
			body=body,
		)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_transaction(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return await hummingbot_gateway_router(
			method=HttpMethod.GET,
			url='kujira/transaction',
			body=body,
		)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_transactions(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return await hummingbot_gateway_router(
			method=HttpMethod.GET,
			url='kujira/transactions',
			body=body,
		)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_wallet_public_key(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return await hummingbot_gateway_router(
			method=HttpMethod.GET,
			url='kujira/wallet/publicKey',
			body=body,
		)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_wallet_public_keys(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return await hummingbot_gateway_router(
			method=HttpMethod.GET,
			url='kujira/wallet/publicKeys',
			body=body,
		)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_block_current(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return await hummingbot_gateway_router(
			method=HttpMethod.GET,
			url='kujira/block/current',
			body=body,
		)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_fees_estimated(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return await hummingbot_gateway_router(
			method=HttpMethod.GET,
			url='kujira/fees/estimated',
			body=body,
		)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def clob_get_markets(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return await hummingbot_gateway_router(
			method=HttpMethod.GET,
			url='clob/markets',
			body=body,
		)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def clob_get_orderbook(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return await hummingbot_gateway_router(
			method=HttpMethod.GET,
			url='clob/orderbook',
			body=body,
		)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def clob_get_ticker(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return await hummingbot_gateway_router(
			method=HttpMethod.GET,
			url='clob/ticker',
			body=body,
		)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def clob_get_orders(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return await hummingbot_gateway_router(
			method=HttpMethod.GET,
			url='clob/orders',
			body=body,
		)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def clob_post_orders(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		"""
			Although the function name is `clob_post_orders`, it is used to place a single order.
		"""
		return await hummingbot_gateway_router(
			method=HttpMethod.POST,
			url='clob/orders',
			body=body,
		)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def clob_delete_orders(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		"""
		Although the function name is `clob_delete_orders`, it is used to delete a single order.
		"""
		return await hummingbot_gateway_router(
			method=HttpMethod.DELETE,
			url='clob/orders',
			body=body,
		)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def clob_post_batch_orders(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return await hummingbot_gateway_router(
			method=HttpMethod.POST,
			url='clob/batchOrders',
			body=body,
		)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def clob_get_estimate_gas(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return await hummingbot_gateway_router(
			method=HttpMethod.GET,
			url='clob/estimateGas',
			body=body,
		)
