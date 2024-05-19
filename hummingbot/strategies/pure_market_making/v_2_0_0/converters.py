from dotmap import DotMap
from typing import Dict, Union, Tuple, Any, Optional
from hummingbot.strategies.pure_market_making.v_2_0_0.types import (
	Market,
	MarketFee,
	Token,
	Ticker,
	Order,
	OrderStatus,
	OrderType,
)


from pprint import pprint
from hummingbot.strategies.pure_market_making.v_2_0_0._exceptions import (
	MarketNameOrIdNotProvidedError,
	MarketNotFoundError,
	TokenNotFoundError,
	TokenIdentifierNotProvidedError,
	TickerNotFoundError,
	TickerIdentifierNotProvidedError
)




def convert_ccxt_token_to_token(currency_data: Dict[str, Any]) -> Token:
	currency_data = DotMap(currency_data)
	return Token(
		id=currency_data.id,
		name=currency_data.name,
		symbol=currency_data.code,
		decimals=currency_data.precision,
		raw=currency_data.info
	)




def convert_ccxt_market_to_market(raw_market_data: dict, raw_currencies_data: dict) -> Market:
	raw_currencies_data = DotMap(raw_currencies_data)
	raw_market_data = DotMap(raw_market_data)


	market: Market = Market(
		id=raw_market_data.id,
		name=raw_market_data.symbol,
		base_token=convert_ccxt_token_to_token(raw_currencies_data[raw_market_data.base]),
		quote_token=convert_ccxt_token_to_token(raw_currencies_data[raw_market_data.quote]),


		precision=raw_market_data.precision.price,
		minimum_order_size=raw_market_data.limits.market.min,
		minimum_price_increment=raw_market_data.precision.price,
		minimum_base_amount_increment=raw_market_data.precision.base,
		minimum_quote_amount_increment=raw_market_data.precision.quote,


		fees=MarketFee(
			maker=raw_market_data.maker,
			taker=raw_market_data.taker
		),
		raw=raw_market_data.info
	)


	return market




def get_token_by_id_name_or_symbol(
	currencies: Dict[str, Any],
	*,
	token_id: Optional[str] = None,
	token_name: Optional[str] = None,
	token_symbol: Optional[str] = None
) -> dict:


	if not (token_name or token_id or token_symbol):
		raise TokenIdentifierNotProvidedError()
	try:
		token = None
		if token_id:
			token = convert_ccxt_token_to_token(currencies[token_id])
		elif token_name:
			token = next(
				convert_ccxt_token_to_token(currencies[token_key])
				for token_key, token_value in currencies.items()
				if token_value["name"] == token_name
			)
		elif token_symbol:
			token = next(
				convert_ccxt_token_to_token(currencies[token_key])
				for token_key, token_value in currencies.items()
				if token_value["code"] == token_symbol
			)
	except (KeyError, StopIteration) as e:
		raise TokenNotFoundError(f"Token <{token_id or token_name or token_symbol}> not found") from e


	return token




def filter_tokens_by_ids_or_names_or_symbols(
	currencies: Dict[str, Any],
	*,
	token_ids: Optional[str] = None,
	token_names: Optional[str] = None,
	token_symbols: Optional[str] = None
) -> Any:


	if not (token_names or token_ids or token_symbols):
		return currencies


	tokens = {}


	if token_ids:
		for token_id in token_ids:
			tokens[token_id] = currencies[token_id]


	elif token_names:
		token_names_copy = set(token_names[:])
		for token_key, token_value in currencies.items():
			if len(token_names_copy) == 0: break
			if token_value.name in token_names_copy:
				tokens[token_key] = token_value
				token_names_copy.remove(token_value.name)


	elif token_symbols:
		token_symbols_copy = set(token_symbols[:])
		for token_key, token_value in currencies.items():
			if len(token_symbols_copy) == 0: break
			if token_value.name in token_symbols_copy:
				tokens[token_key] = token_value
				token_symbols_copy.remove(token_value.name)


	return tokens




def convert_ccxt_tokens_to_tokens(currency_data: Dict[str, dict]):
	token_data = {}
	for token_key, token_value in currency_data.items():
		token_data[token_key] = convert_ccxt_token_to_token(token_value)


	return token_data




def get_market_data_by_id_or_name(
	markets_data: Dict[str, Dict],
	*,
	market_id: str = None,
	market_name: str = None
) -> Dict:
	if not (market_id or market_name):
		raise MarketNameOrIdNotProvidedError()
	market = None


	try:
		if market_id:
			market = markets_data[market_id]


		elif market_name:
			market = next(
				_market_value
				for _market_id, _market_value in markets_data.items()
				if _market_value.name == market_name
			)


	except (KeyError, StopIteration) as e:
		if isinstance(e, KeyError):
			raise MarketNotFoundError(f"Market <{market_id or market_name}> not found") from e
		else:
			raise MarketNotFoundError(f"Market with name '{market_name}' not found") from e


	return market




def filter_markets_data_by_names_or_ids(
	markets_data: DotMap,
	*,
	market_names: Tuple[str, ...] = (),
	market_ids: Tuple[str, ...] = ()
) -> Dict[str, DotMap]:
	filtered_markets = {}


	if not (market_names or market_ids):
		return markets_data.toDict()


	try:
		if market_ids:
			filtered_markets = {market_id: markets_data[market_id] for market_id in market_ids}


		elif market_names:
			# create a temporary holder to iterate by, so it doesn't go through the entire currencies data
			market_names_counter = set(market_names[:])
			for market_id, market in markets_data.items():
				if len(market_names_counter) == 0: break  # if an empty tuple is provided, save us the stress


				market_name = market.get("name")


				if market_name in market_names:
					filtered_markets[market_id] = market
					market_names_counter.remove(market_name)


		if not filtered_markets:
			raise MarketNotFoundError("No markets found with the provided names or ids")


	except KeyError as e:
		raise MarketNotFoundError(f"Market <{e.args[0]}> not found") from e


	return filtered_markets




def convert_ccxt_markets_to_market(ccxt_markets: dict, ccxt_currencies: dict):
	all_markets = DotMap()
	for market_key, market_value in ccxt_markets.items():
		try:
			market_value = DotMap(market_value)


			market_obj = Market(
				id=market_key,
				name=market_value.symbol,


				base_token=convert_ccxt_token_to_token(ccxt_currencies[market_value.base]),
				quote_token=convert_ccxt_token_to_token(ccxt_currencies[market_value.quote]),


				precision=market_value.precision.price,  # QUESTION: is this what is expected?
				minimum_order_size=market_value.limits.market.min,
				minimum_price_increment=market_value.precision.price,
				minimum_base_amount_increment=market_value.precision.base,
				minimum_quote_amount_increment=market_value.precision.quote,


				fees=MarketFee(
					maker=market_value.maker,
					taker=market_value.taker
				),
				raw=market_value.info
			)
			all_markets[market_obj.id] = market_obj
		except KeyError:
			# REMINDER: LOG THIS CASE TO FILE
			pass


	return all_markets




def convert_ccxt_ticker_to_ticker(ticker: dict, market: Market):
	ccxt_ticker = DotMap(ticker)
	ticker = Ticker(
		symbol=ccxt_ticker.symbol,
		market=market,
		price=ccxt_ticker.ask,
		timestamp=ccxt_ticker.timestamp,
		raw=ccxt_ticker.info
	)


	return ticker




def convert_ccxt_tickers_to_tickers(tickers: dict, markets: dict):
	all_tickers = {}
	for ticker_key, ticker_value in tickers.items():
		market = markets[ticker_key]
		all_tickers[ticker_key] = convert_ccxt_ticker_to_ticker(ticker=ticker_value, market=market)


	return all_tickers




def filter_tickers_by_market_ids_or_market_names(
	tickers: Dict[str, Any],
	*,
	market_ids: Optional[str] = None,
	market_names: Optional[str] = None,
) -> Any:


	if not (market_ids or market_names):
		return tickers


	ticker_data = {}
	try:


		if market_ids:
			for market_id in market_ids:
				ticker_data[market_id] = tickers[market_id]


		elif market_names:
			market_names_copy = set(market_names[:])
			for ticker_key, ticker_value in tickers.items():
				if len(market_names_copy) == 0: break
				if ticker_value.name in market_names_copy:
					ticker_data[ticker_key] = ticker_value
					market_names_copy.remove(ticker_value.name)


	except KeyError as e:
		raise TickerNotFoundError(f"Ticker <{e.args[0]}> not found.")


	return ticker_data




def get_ticker_by_market_name_or_market_id(
	tickers: Dict[str, Any],
	ccxt_markets: Dict[str, Any],
	ccxt_currencies,
	*,
	market_id: Optional[str] = None,
	market_name: Optional[str] = None,
) -> dict:
	if not (market_id or market_name):
		raise TickerIdentifierNotProvidedError()
	try:
		ticker = None
		if market_id:
			market = get_market_data_by_id_or_name(
				markets_data=ccxt_markets,
				market_id=market_id,
			)
			market = convert_ccxt_market_to_market(market, ccxt_currencies)
			ticker = convert_ccxt_ticker_to_ticker(tickers[market_id], market=market)


		elif market_name:
			market = get_market_data_by_id_or_name(
				markets_data=ccxt_markets,
				market_id=market_id,
			)
			market = convert_ccxt_market_to_market(market, ccxt_currencies)
			ticker = next(
				convert_ccxt_ticker_to_ticker(tickers[ticker_key], market=market)
				for ticker_key, ticker_value in tickers.items()
				if ticker_value["name"] == market_name
			)


	except (KeyError, StopIteration) as e:
		raise TickerNotFoundError(f"Ticker <{market_id or market_name}> not found") from e


	return ticker




def get_order_status(status):
	match str(status).casefold():
		case "closed":
			order_status = OrderStatus.FILLED
		case "open":
			order_status = OrderStatus.OPEN
		case "creation_pending":
			order_status = OrderStatus.CREATION_PENDING
		case "partially_filled":
			order_status = OrderStatus.PARTIALLY_FILLED
		case "cancellation_pending":
			order_status = OrderStatus.CREATION_PENDING
		case _:
			order_status = OrderStatus.UNKNOWN


	return order_status




def get_order_type(ccxt_order_type):
	match str(ccxt_order_type).casefold():
		case "MARKET":
			order_type = OrderType.MARKET
		case "LIMIT":
			order_type = OrderType.LIMIT
		case "POST_ONLY":
			order_type = OrderType.POST_ONLY
		case "LIMIT_MAKER":
			order_type = OrderType.LIMIT_MAKER
		case "IMMEDIATE_OR_CANCEL":
			order_type = OrderType.IMMEDIATE_OR_CANCEL
		case _:
			order_type = None


	return order_type




def convert_ccxt_order_response_to_response(ccxt_order, market) -> Order:
	ccxt_order = DotMap(ccxt_order)
	return Order(
		id=ccxt_order.id,
		client_id=ccxt_order.clientOrderId,
		market_name=market.name,
		market_id=market.id,
		market=market,
		price=ccxt_order.price,
		amount=ccxt_order.amount,
		side=ccxt_order.side,
		status=get_order_status(ccxt_order.status),
		type=get_order_type(ccxt_order.type),
		fee=ccxt_order.fee,
		creation_timestamp=ccxt_order.timestamp,
		raw=ccxt_order.info
	)

