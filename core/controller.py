import asyncio
import json
import os
from dotmap import DotMap
from typing import Dict, AsyncGenerator, Any, List

from core.constants import constants, chains_connector_specification
from core.logger import logger
from core.properties import properties
from core.system import execute, execute_continuously
from core.types import SystemStatus
from core.utils import deep_merge

from hummingbot.strategies.strategy_base import StrategyBase
from hummingbot.strategies.types import Strategy

tasks: DotMap[str, asyncio.Task] = DotMap({
})
tasks._dynamic=True

processes: DotMap[str, StrategyBase] = DotMap({
})
processes._dynamic=True


def sanitize_options(options: DotMap[str, Any]) -> DotMap[str, Any]:
	default_strategy = Strategy.get_default()

	output = DotMap({
		"strategy": options.get("strategy", default_strategy.ID),
		"version": options.get("version", default_strategy.VERSION),
		"id": options.get("id", "01"),
		"worker_id": options.get("worker_id", options.get("workerId", None)),
	})

	output.full_id = f"""{output.strategy}:{output.version}:{output.id}"""
	output.class_reference = Strategy.from_id_and_version(output.strategy, output.version).value

	output._dynamic = False

	return output


async def continuously_solve_services_status():
	while True:
		try:
			system = DotMap(json.loads(await execute(properties.get("system.commands.status"))), _dynamic=False)
			for (key, value) in system.items():
				if key == constants.id:
					try:
						status = DotMap(await strategy_status(DotMap({})), _dynamic=False)

						if status.get("message") == "Process not running":
							system[key] = SystemStatus.STOPPED
						else:
							system[key] = DotMap(status, _dynamic=False).status
					except Exception as exception:
						system[key] = SystemStatus.UNKNOWN
				else:
					system[key] = SystemStatus.get_by_id(value)

			current = properties.get_or_default("services.status.current", constants.services.status.default)
			final = deep_merge(current, system)

			properties.set("services.status.current", final)

			await asyncio.sleep(constants.services.status.delay / 1000.0)
		except Exception as exception:
			logger.ignore_exception(exception)

			pass


async def service_status(_options: DotMap[str, Any]) -> Dict[str, Any]:
	try:
		if not tasks[constants.services.status.task]:
			tasks[constants.services.status.task].start = asyncio.create_task(continuously_solve_services_status())

		return properties.get_or_default("services.status.current", constants.services.status.default)
	except Exception as exception:
		raise exception


async def service_start(options: DotMap[str, Any]):
	try:
		if properties.get_or_default(f"services.status.current.{options.id}", SystemStatus.UNKNOWN) in [SystemStatus.STOPPED, SystemStatus.UNKNOWN]:
			properties.set(f"services.status.current.{options.id}", SystemStatus.STARTING)

			if options.id == constants.id:
				await strategy_start(DotMap({}))
			else:
				await execute(str(properties.get(f"system.commands.start.{options.id}")).format(
					username=properties.get("admin.username"), password=properties.get("admin.password")
				))

			properties.set(f"services.status.current.{options.id}", SystemStatus.RUNNING)

			return {
				"message": f"""Service "{options.id}" has started."""
			}
		else:
			return {
				"message": f"""Service "{options.id}" is already running."""
			}
	except Exception as exception:
		raise exception


async def service_stop(options: DotMap[str, Any]):
	try:
		if properties.get_or_default(f"services.status.current.{options.id}", SystemStatus.UNKNOWN) in [SystemStatus.STARTING, SystemStatus.IDLE, SystemStatus.RUNNING]:
			properties.set(f"services.status.current.{options.id}", SystemStatus.STOPPING)

			if options.id == constants.id:
				await strategy_stop(DotMap({}))
			else:
				await execute(properties.get(f"system.commands.stop.{options.id}"))

			properties.set(f"services.status.current.{options.id}", SystemStatus.STOPPED)

			return {
				"message": f"""Service "{options.id}" has stopped."""
			}
		else:
			return {
				"message": f"""Service "{options.id}" is not running."""
			}
	except Exception as exception:
		raise exception


async def strategy_status(options: DotMap[str, Any]) -> Dict[str, Any]:
	options = sanitize_options(options)

	try:
		if processes.get(options.full_id):
			return processes[options.full_id].get_status().toDict()
		else:
			return {
				"message": "Process not running"
			}
	except Exception as exception:
		if tasks.get(options.full_id):
			tasks[options.full_id].start.cancel()
			await tasks[options.full_id].start
		processes[options.full_id] = None
		tasks[options.full_id].start = None

		raise exception


async def strategy_start(options: DotMap[str, Any]) -> Dict[str, Any]:
	options = sanitize_options(options)

	try:
		if not processes.get(options.full_id):
			processes[options.full_id] = options.class_reference(options.id)
			tasks[options.full_id].start = asyncio.create_task(processes[options.full_id].start())

			return {
				"message": "Starting..."
			}
		else:
			return {
				"message": "Already running"
			}
	except Exception as exception:
		if tasks.get(options.full_id):
			tasks[options.full_id].start.cancel()
			await tasks[options.full_id].start
		processes[options.full_id] = None
		tasks[options.full_id].start = None

		raise exception


async def strategy_stop(options: DotMap[str, Any]):
	options = sanitize_options(options)

	try:
		if processes.get(options.full_id):
			tasks[options.full_id].start.cancel()
			tasks[options.full_id].stop = asyncio.create_task(processes[options.full_id].stop())

			return {
				"message": "Stopping..."
			}
		else:
			return {
				"message": "Process not running"
			}
	except Exception as exception:
		if tasks.get(options.full_id):
			tasks[options.full_id].start.cancel()
			await tasks[options.full_id].start

		raise exception
	finally:
		processes[options.full_id] = None
		tasks[options.full_id].start = None


async def strategy_worker_start(options: DotMap[str, Any]) -> Dict[str, Any]:
	options = sanitize_options(options)

	try:
		if processes.get(options.full_id):
			asyncio.create_task(processes[options.full_id].start_worker(options.worker_id))

			return {
				"message": f"Starting worker {options.worker_id} ..."
			}
		else:
			return {
				"message": f"Supervisor {options.full_id} is not running"
			}
	except Exception as exception:
		raise exception


async def strategy_worker_stop(options: DotMap[str, Any]) -> Dict[str, Any]:
	options = sanitize_options(options)

	try:
		if processes.get(options.full_id):
			asyncio.create_task(processes[options.full_id].stop_worker(options.worker_id))

			return {
				"message": f"Stopping worker {options.worker_id} ..."
			}
		else:
			return {
				"message": f"Supervisor {options.full_id} is not running"
			}
	except Exception as exception:
		raise exception


async def strategy_worker_status(options: DotMap[str, Any]) -> Dict[str, Any]:
	options = sanitize_options(options)

	try:
		if processes.get(options.full_id):
			status = DotMap({})
			status.supervisor_id = options.full_id
			status.update(processes[options.full_id].worker_status(options.worker_id))

			return status.toDict()

		else:
			return {
				"message": f"Supervisor {options.full_id} is not running"
			}

	except Exception as exception:
		raise exception


async def websocket_log(options: Any) -> AsyncGenerator[str, None]:
	command = str(properties.get(f"system.commands.log.{options.id}"))

	async for line in execute_continuously(command):
		yield line
		await asyncio.sleep(0.1)


def update_gateway_connections(params: Any):
	absolute_configuration_path = os.path.expanduser(str(properties.get("hummingbot.client.configuration_path")))

	def load(path) -> List[Dict[str, str]]:
		if os.path.exists(path):
			with open(path) as target_file:
				try:
					file_content: List[Dict[str, str]] = json.load(target_file)

					return file_content
				except json.JSONDecodeError:
					return []
		return []

	def save(path, settings: List[Dict[str, str]]):
		with open(path, "w") as target_file:
			json.dump(settings, target_file)

	gateway_connections_absolute_file_path = (
		absolute_configuration_path + "gateway_connections.json"
		if absolute_configuration_path[-1] == "/"
		else absolute_configuration_path + "/gateway_connections.json"
	)
	gateway_connections_content = load(gateway_connections_absolute_file_path)

	gateway_networks_absolute_file_path = (
		absolute_configuration_path + "gateway_network.json"
		if absolute_configuration_path[-1] == "/"
		else absolute_configuration_path + "/gateway_network.json"
	)
	gateway_network_content = load(gateway_networks_absolute_file_path)

	connector_name = chains_connector_specification[params["chain"].upper()]["CONNECTOR"].value
	chain = params["chain"]

	if params["subpath"] == "wallet/add":
		# Updating gateway_connections.json
		new_connector_specification: List[Dict[str, str]] = []

		for network in chains_connector_specification[params["chain"].upper()]["NETWORK"].value:
			new_connector_specification.append({
				"connector": connector_name,
				"chain": chain,
				"network": network,
				"trading_type": chains_connector_specification[params["chain"].upper()]["TRADING_TYPE"].value,
				"chain_type": chains_connector_specification[params["chain"].upper()]["CHAIN_TYPE"].value,
				"wallet_address": params["publickey"],
				"additional_spenders": chains_connector_specification[params["chain"].upper()]["ADDITIONAL_SPENDERS"].value,
				"additional_prompt_values": chains_connector_specification[params["chain"].upper()]["ADDITIONAL_PROMPT_VALUES"].value
			})

		for spec in new_connector_specification:
			updated: bool = False
			network = spec["network"]

			for i, c in enumerate(gateway_connections_content):
				if c["connector"] == connector_name and c["chain"] == chain and c["network"] == network:
					gateway_connections_content[i] = spec
					updated = True
					break

			if updated is False:
				gateway_connections_content.append(spec)

		# Updating gateway_networks.json
		for chain_network in chains_connector_specification[params["chain"].upper()]["CHAIN_NETWORKS"].value:
			new_network_specification: Dict[str, str] = {
				"chain_network": chain_network,
			}

			updated: bool = False

			for i, c in enumerate(gateway_network_content):
				if c["chain_network"] == chain_network:
					gateway_network_content[i] = new_network_specification
					updated = True
					break

			if updated is False:
				gateway_network_content.append(new_network_specification)

		# Updating gateway_networks.json - Adding tokens to watch
		tokens = chains_connector_specification[params["chain"].upper()]["TOKENS"].value

		network_found = False

		for chain_network in chains_connector_specification[params["chain"].upper()]["CHAIN_NETWORKS"].value:
			for network in gateway_network_content:
				if network.get("chain_network") == chain_network:
					network['tokens'] = tokens
					network_found = True
					break
			if not network_found:
				new_network = {
					"chain_network": chain_network,
					"tokens": tokens
				}
				gateway_network_content.append(new_network)

	elif params["subpath"] == "wallet/remove":
		# Updating gateway_connections.json
		gateway_connections_content = [
			c for c in gateway_connections_content if not (
				c["chain"] == chain and c["wallet_address"] == params["address"]
			)
		]

		# Updating gateway_networks.json
		for chain_network in chains_connector_specification[params["chain"].upper()]["CHAIN_NETWORKS"].value:
			for i, c in enumerate(gateway_network_content):
				if c["chain_network"] == chain_network:
					gateway_network_content.remove(c)

	save(gateway_connections_absolute_file_path, gateway_connections_content)
	save(gateway_networks_absolute_file_path, gateway_network_content)


async def test(options: DotMap[str, Any]) -> DotMap[str, Any]:
	from hummingbot.strategies.pure_market_making.v_2_0_0.types import (
		AccountNumber,
		Address,
		Amount,
		BalanceNotFoundError,
		Balances,
		BaseBalance,
		BaseBalanceWithQuotation,
		BaseError,
		BaseTokenBalance,
		Block,
		BlockNumber,
		ChainName,
		ConnectorName,
		ConnectorStatus,
		EstimatedFees,
		EstimatedFeesPrice,
		EstimatedFeesToken,
		EstimateFeesCost,
		EstimateFeesLimit,
		Fee,
		FeeMaker,
		FeeServiceProvider,
		FeeTaker,
		Market,
		MarketDeprecation,
		MarketFee,
		MarketId,
		MarketMinimumBaseIncrement,
		MarketMinimumOrderSize,
		MarketMinimumPriceIncrement,
		MarketMinimumQuoteIncrement,
		MarketName,
		MarketNotFoundError,
		MarketPrecision,
		MarketProgramId,
		Mnemonic,
		NetworkName,
		Order,
		OrderAmount,
		OrderBook,
		OrderBookNotFoundError,
		OrderClientId,
		OrderCreationTimestamp,
		OrderFee,
		OrderFilling,
		OrderFillingTimestamp,
		OrderId,
		OrderMarketId,
		OrderMarketName,
		OrderNotFoundError,
		OrderOwnerAddress,
		OrderPayerAddress,
		OrderPrice,
		OrderSide,
		OrderStatus,
		OrderType,
		OwnerAddress,
		Password,
		PayerAddress,
		Percentage,
		Price,
		RestAddWalletRequest,
		RestAddWalletResponse,
		RestAllMarketsWithdrawsRequest,
		RestAllMarketsWithdrawsResponse,
		RestCancelAllOrdersRequest,
		RestCancelAllOrdersResponse,
		RestCancelOrderRequest,
		RestCancelOrderResponse,
		RestCancelOrdersRequest,
		RestCancelOrdersResponse,
		RESTfulMethod,
		RestGetAllBalancesRequest,
		RestGetAllBalancesResponse,
		RestGetAllFilledOrdersRequest,
		RestGetAllFilledOrdersResponse,
		RestGetAllMarketsRequest,
		RestGetAllMarketsResponse,
		RestGetAllOpenOrdersRequest,
		RestGetAllOpenOrdersResponse,
		RestGetAllOrderBooksRequest,
		RestGetAllOrderBooksResponse,
		RestGetAllOrdersRequest,
		RestGetAllOrdersResponse,
		RestGetAllTickersRequest,
		RestGetAllTickersResponse,
		RestGetAllTokensRequest,
		RestGetAllTokensResponse,
		RestGetBalanceRequest,
		RestGetBalanceResponse,
		RestGetBalancesRequest,
		RestGetBalancesResponse,
		RestGetBlockRequest,
		RestGetBlockResponse,
		RestGetBlocksRequest,
		RestGetBlocksResponse,
		RestGetCurrentBlockRequest,
		RestGetCurrentBlockResponse,
		RestGetEstimatedFeesRequest,
		RestGetEstimatedFeesResponse,
		RestGetMarketRequest,
		RestGetMarketResponse,
		RestGetMarketsRequest,
		RestGetMarketsResponse,
		RestGetOrderBookRequest,
		RestGetOrderBookResponse,
		RestGetOrderBooksRequest,
		RestGetOrderBooksResponse,
		RestGetOrderRequest,
		RestGetOrderResponse,
		RestGetOrdersRequest,
		RestGetOrdersResponse,
		RestGetRootRequest,
		RestGetRootResponse,
		RestGetTickerRequest,
		RestGetTickerResponse,
		RestGetTickersRequest,
		RestGetTickersResponse,
		RestGetTokenRequest,
		RestGetTokenResponse,
		RestGetTokensRequest,
		RestGetTokensResponse,
		RestGetTransactionRequest,
		RestGetTransactionResponse,
		RestGetTransactionsRequest,
		RestGetTransactionsResponse,
		RestMarketsWithdrawsRequest,
		RestMarketsWithdrawsResponse,
		RestMarketWithdrawRequest,
		RestMarketWithdrawResponse,
		RestPlaceOrderRequest,
		RestPlaceOrderResponse,
		RestPlaceOrdersRequest,
		RestPlaceOrdersResponse,
		RestReplaceOrderRequest,
		RestReplaceOrderResponse,
		RestReplaceOrdersRequest,
		RestReplaceOrdersResponse,
		Ticker,
		TickerNotFoundError,
		TickerPrice,
		TickerSource,
		TickerTimestamp,
		Timestamp,
		Token,
		TokenAndAmount,
		TokenBalance,
		TokenDecimals,
		TokenId,
		TokenName,
		TokenNotFoundError,
		TokenSymbol,
		TotalBalance,
		Transaction,
		TransactionHash,
		TransactionHashes,
		TransactionNotFoundError,
		Withdraw,
		WithdrawError,
		WithdrawItem,
		WorkerType,
		WsAllMarketsWithdrawsRequest,
		WsAllMarketsWithdrawsResponse,
		WsCancelAllOrdersRequest,
		WsCancelAllOrdersResponse,
		WsCancelOrderRequest,
		WsCancelOrderResponse,
		WsCancelOrdersRequest,
		WsCancelOrdersResponse,
		WsCreateOrderRequest,
		WsCreateOrderResponse,
		WsCreateOrdersRequest,
		WsCreateOrdersResponse,
		WsMarketsWithdrawsFundsResponse,
		WsMarketsWithdrawsRequest,
		WsMarketWithdrawRequest,
		WsMarketWithdrawResponse,
		WsWatchAllBalancesRequest,
		WsWatchAllBalancesResponse,
		WsWatchAllFilledOrdersRequest,
		WsWatchAllFilledOrdersResponse,
		WsWatchAllIndicatorsRequest,
		WsWatchAllIndicatorsResponse,
		WsWatchAllOpenOrdersRequest,
		WsWatchAllOpenOrdersResponse,
		WsWatchAllOrderBooksRequest,
		WsWatchAllOrderBooksResponse,
		WsWatchAllOrdersRequest,
		WsWatchAllOrdersResponse,
		WsWatchAllTickersRequest,
		WsWatchAllTickersResponse,
		WsWatchBalanceRequest,
		WsWatchBalanceResponse,
		WsWatchBalancesRequest,
		WsWatchBalancesResponse,
		WsWatchIndicatorRequest,
		WsWatchIndicatorResponse,
		WsWatchIndicatorsRequest,
		WsWatchIndicatorsResponse,
		WsWatchOrderBookRequest,
		WsWatchOrderBookResponse,
		WsWatchOrderBooksRequest,
		WsWatchOrderBooksResponse,
		WsWatchOrderRequest,
		WsWatchOrderResponse,
		WsWatchOrdersRequest,
		WsWatchOrdersResponse,
		WsWatchTickerRequest,
		WsWatchTickerResponse,
		WsWatchTickersRequest,
		WsWatchTickersResponse
	)

	from decimal import Decimal

	from hummingbot.strategies.pure_market_making.v_2_0_0.connectors.ccxt.ccxt import CCXTConnector

	options = DotMap({
		"ccxt": {
			"exchange": {
				"id": os.environ.get("EXCHANGE_ID", "binance"),
				"environment": os.environ.get("EXCHANGE_ENVIRONMENT", "production"),
				"rest": {
					"constructor": {
						"apiKey": os.environ.get("EXCHANGE_API_KEY"),
						"secret": os.environ.get("EXCHANGE_API_SECRET"),
					},
					"options": {
						"subaccountId": os.environ.get("EXCHANGE_SUB_ACCOUNT_ID"),
					},
				},
				"websocket": {
					"constructor": {
						"apiKey": os.environ.get("EXCHANGE_API_KEY"),
						"secret": os.environ.get("EXCHANGE_API_SECRET"),
					},
					"options": {
						"subaccountId": os.environ.get("EXCHANGE_SUB_ACCOUNT_ID"),
					},
				}
			}
		}
	}, _dynamic=False)

	# market_id = RestGetMarketRequest(
	# 	id="ETH/BTC",
	# 	name=None,
	# )
	#
	# market_ids = RestGetMarketsRequest(
	# 	ids=("EOS/USDC", "ETH/BTC"),
	# 	names=None,
	# )
	#
	# market_names = RestGetMarketsRequest(
	# 	names=("BNB/USD", "ZRX/USDT:USDT", "ZRX/BNB")
	# )
	#
	# get_token_request = RestGetTokenRequest(
	# 	# symbol="ZIL",
	# 	id=None,
	# 	name=None,
	# 	symbol="BRL",
	# )
	#
	# get_tokens_request = RestGetTokensRequest(
	# 	# ids=("ZIL", "NEAR",),
	# 	ids=("TBTC", "BRL",),
	# 	names=None,
	# 	symbols=None,
	# )
	#
	# tickers_request = RestGetTickersRequest(
	# 	market_ids=("ZIL/USDT", "ZIL/TRY")
	# )
	# ticker_request = RestGetTickerRequest(
	# 	market_id="BTC/USDT"
	# )
	#
	# place_order_request = RestPlaceOrderRequest(
	# 	market_id="BTC/USDT",
	# 	order_side="sell",
	# 	order_type=OrderType.LIMIT,
	# 	order_amount=Decimal(0.0005),
	# 	order_price=Decimal(90000)
	# )
	#
	# place_orders_request = RestPlaceOrdersRequest(
	# 	orders=[
	# 		RestPlaceOrderRequest(
	# 			market_id="BTC/USDT",
	# 			order_side="buy",
	# 			order_type=OrderType.MARKET,
	# 			order_amount=Decimal(0.0009),
	# 			order_price=Decimal(7000)
	# 		),
	# 		RestPlaceOrderRequest(
	# 			market_id="BTC/USDT",
	# 			order_side="sell",
	# 			order_type=OrderType.LIMIT,
	# 			order_amount=Decimal(0.0005),
	# 			order_price=Decimal(90000)
	# 		)
	# 	]
	# )
	#
	# get_orders_request = RestGetOrdersRequest(
	# 	ids=None,
	# 	market_id="ETH/USDT",
	# 	market_ids=None,
	# 	market_name=None,
	# 	market_names=None,
	# 	owner_address=None,
	# 	owner_addresses=None,
	# 	status=None,
	# 	statuses=None,
	# )
	#
	# get_order_request = RestGetOrderRequest(
	# 	id="5707151",
	# 	market_id="ETH/USDT",
	# 	market_name=None,
	# 	owner_address=None,
	# 	status=None,
	# )
	# cancel_order_request = RestCancelOrderRequest(
	# 	id="5707151",
	# 	market_id="ETH/USDT"
	# )
	#
	# get_order_books_request = RestGetOrderBooksRequest(market_ids=["ETH/USDT", "BTC/USDT"])
	# get_order_book_request = RestGetOrderBookRequest(market_id="ETH/USDT")

	response: Any = None
	connector = CCXTConnector(options)
	await connector.initialize(options)

	# response = await connector.rest.get_all_markets()
	# response = await connector.rest.get_markets(market_ids)
	# response = await connector.rest.get_market(market_id)
	#
	# response = await connector.rest.get_all_tokens()
	# response = await connector.rest.get_tokens(get_tokens_request)
	# response = await connector.rest.get_token(get_token_request)

	# response = await connector.rest.get_all_order_books()
	# response = await connector.rest.get_order_books(get_order_books_request)
	# response = await connector.rest.get_order_book(get_order_book_request)

	# response = await connector.rest.get_all_tickers()
	# response = await connector.rest.get_tickers(tickers_request)
	# response = await connector.rest.get_ticker(ticker_request)

	# response = await connector.rest.place_order(place_order_request)
	# response = await connector.rest.place_orders(place_orders_request)

	# not implemented in ccxt exchange
	# response = await connector.rest.get_all_orders()
	#
	# response = await connector.rest.get_order(get_order_request)
	# response = await connector.rest.get_orders(get_orders_request)

	# response = await connector.rest.cancel_order(cancel_order_request)

	return response
