from enum import Enum

from hummingbot.strategies.pure_market_making.v_1_0_0.supervisor import Supervisor as PureMarketMaking_1_0_0


class Strategy(Enum):
	PURE_MARKET_MAKING_1_0_0 = PureMarketMaking_1_0_0

	@staticmethod
	def from_id_and_version(id: str, version: str):
		for strategy in Strategy.__members__.values():
			if strategy.value.ID == id and strategy.value.VERSION == version:
				return strategy
