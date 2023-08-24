from __future__ import annotations

from typing import Any, Dict

from dotmap import DotMap

from hummingbot.constants import NUMBER_OF_RETRIES, DELAY_BETWEEN_RETRIES, TIMEOUT
from hummingbot.router import router
from core.decorators import automatic_retry_with_timeout
from core.types import HttpMethod


class Gateway:

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_root(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return DotMap(await router(
			method=HttpMethod.GET,
			url='kujira',
			body=body,
			), _dynamic=False)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_token(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return DotMap(await router(
			method=HttpMethod.GET,
			url='kujira/token',
			body=body,
			), _dynamic=False)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_tokens(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return DotMap(await router(
			method=HttpMethod.GET,
			url='kujira/tokens',
			body=body,
			), _dynamic=False)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_tokens_all(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return DotMap(await router(
			method=HttpMethod.GET,
			url='kujira/tokens/all',
			body=body,
		), _dynamic=False)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_market(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return DotMap(await router(
			method=HttpMethod.GET,
			url='kujira/market',
			body=body,
		), _dynamic=False)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_markets(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return DotMap(await router(
			method=HttpMethod.GET,
			url='kujira/markets',
			body=body,
		), _dynamic=False)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_markets_all(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return DotMap(await router(
			method=HttpMethod.GET,
			url='kujira/markets/all',
			body=body,
		), _dynamic=False)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_order_book(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return DotMap(await router(
			method=HttpMethod.GET,
			url='kujira/orderBook',
			body=body,
		), _dynamic=False)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_order_books(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return DotMap(await router(
			method=HttpMethod.GET,
			url='kujira/orderBooks',
			body=body,
		), _dynamic=False)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_order_books_all(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return DotMap(await router(
			method=HttpMethod.GET,
			url='kujira/orderBooks/all',
			body=body,
		), _dynamic=False)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_ticker(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return DotMap(await router(
			method=HttpMethod.GET,
			url='kujira/ticker',
			body=body,
		), _dynamic=False)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_tickers(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return DotMap(await router(
			method=HttpMethod.GET,
			url='kujira/tickers',
			body=body,
		), _dynamic=False)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_tickers_all(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return DotMap(await router(
			method=HttpMethod.GET,
			url='kujira/tickers/all',
			body=body,
		), _dynamic=False)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_balance(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return DotMap(await router(
			method=HttpMethod.GET,
			url='kujira/balance',
			body=body,
		), _dynamic=False)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_balances(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return DotMap(await router(
			method=HttpMethod.GET,
			url='kujira/balances',
			body=body,
		), _dynamic=False)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_balances_all(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return DotMap(await router(
			method=HttpMethod.GET,
			url='kujira/balances/all',
			body=body,
		), _dynamic=False)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_order(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return DotMap(await router(
			method=HttpMethod.GET,
			url='kujira/order',
			body=body,
		), _dynamic=False)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_orders(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return DotMap(await router(
			method=HttpMethod.GET,
			url='kujira/orders',
			body=body,
		), _dynamic=False)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_post_order(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return DotMap(await router(
			method=HttpMethod.POST,
			url='kujira/order',
			body=body,
		), _dynamic=False)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_post_orders(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return DotMap(await router(
			method=HttpMethod.POST,
			url='kujira/orders',
			body=body,
		), _dynamic=False)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_delete_order(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return DotMap(await router(
			method=HttpMethod.DELETE,
			url='kujira/order',
			body=body,
		), _dynamic=False)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_delete_orders(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return DotMap(await router(
			method=HttpMethod.DELETE,
			url='kujira/orders',
			body=body,
		), _dynamic=False)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_delete_orders_all(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return DotMap(await router(
			method=HttpMethod.DELETE,
			url='kujira/orders/all',
			body=body,
		), _dynamic=False)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_post_market_withdraw(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return DotMap(await router(
			method=HttpMethod.POST,
			url='kujira/market/withdraw',
			body=body,
		), _dynamic=False)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_post_market_withdraws(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return DotMap(await router(
			method=HttpMethod.POST,
			url='kujira/market/withdraws',
			body=body,
		), _dynamic=False)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_post_market_withdraws_all(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return DotMap(await router(
			method=HttpMethod.POST,
			url='kujira/market/withdraws/all',
			body=body,
		), _dynamic=False)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_transaction(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return DotMap(await router(
			method=HttpMethod.GET,
			url='kujira/transaction',
			body=body,
		), _dynamic=False)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_transactions(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return DotMap(await router(
			method=HttpMethod.GET,
			url='kujira/transactions',
			body=body,
		), _dynamic=False)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_wallet_public_key(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return DotMap(await router(
			method=HttpMethod.GET,
			url='kujira/wallet/publicKey',
			body=body,
		), _dynamic=False)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_wallet_public_keys(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return DotMap(await router(
			method=HttpMethod.GET,
			url='kujira/wallet/publicKeys',
			body=body,
		), _dynamic=False)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_block_current(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return DotMap(await router(
			method=HttpMethod.GET,
			url='kujira/block/current',
			body=body,
		), _dynamic=False)

	@staticmethod
	@automatic_retry_with_timeout(retries=NUMBER_OF_RETRIES, delay=DELAY_BETWEEN_RETRIES, timeout=TIMEOUT)
	async def kujira_get_fees_estimated(
		body: Dict[str, Any] | DotMap[str, Any]
	) -> DotMap[str, Any]:
		return DotMap(await router(
			method=HttpMethod.GET,
			url='kujira/fees/estimated',
			body=body,
		), _dynamic=False)
