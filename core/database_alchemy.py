import os
from decimal import Decimal
from sqlalchemy import (
    create_engine,
    Column,
    BigInteger,
    String,
    Text,
    DECIMAL,
    JSON,
    ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session

working_directory = os.path.dirname(
    os.path.dirname(os.path.realpath(__file__))
)
# os.chdir(working_directory)


ClientBase = declarative_base()


class Owner(ClientBase):
    __tablename__ = "Owner"

    owner_address = Column(Text, primary_key=True, nullable=False)
    orders = relationship('Order', backref='Owner')


class Order(ClientBase):
    __tablename__ = "Order"

    exchange_order_id = Column(String(32), primary_key=True, nullable=False)
    price = Column(DECIMAL(6), nullable=False)
    amount = Column(DECIMAL(6), nullable=False)
    order_type = Column(Text, nullable=False)
    market_name = Column(String(32), nullable=False)
    market_id = Column(Text, nullable=False)
    base_token_symbol = Column(String(32), nullable=False)
    quote_token_symbol = Column(String(32), nullable=False)
    base_token_id = Column(Text, nullable=False)
    quote_token_id = Column(Text, nullable=False)
    current_status = Column(Text, nullable=False)
    creation_timestamp = Column(BigInteger, nullable=False)
    cancellation_timestamp = Column(BigInteger)
    transaction_response_body = Column(JSON)
    owner_address = Column(Text, ForeignKey('Owner.owner_address'))


class DataBaseManipulator:
    _root_path = str
    _RDBMS = "sqlite"

    def __init__(self):
        self._root_path = working_directory

    def create_db_path(
            self,
            _strategy_name: str,
            _strategy_version: str,
            _worker_id: str
    ):
        file_name = f"{_strategy_name.lower()}_{_strategy_version.replace('.', '_')}_worker_{_worker_id}.db"
        _db_path = f"{self._root_path}/resources/databases/{_strategy_name}/{_strategy_version}/"

        return _db_path, file_name

    def get_session_creator(self, _db_path: str, _db_name: str):
        session_creator = None
        try:
            os.makedirs(_db_path, exist_ok=True)
            url = f"{self._RDBMS}:///{_db_path}/{_db_name}"
            db_engine = create_engine(url)
            ClientBase.metadata.create_all(db_engine)
            session_creator = scoped_session(sessionmaker(bind=db_engine))
        except Exception as e:
            raise f"An error occurred during database session creation: {e}"
        finally:
            return session_creator


if __name__ == '__main__':

    strategy_name = "pure_market_making"
    strategy_version = "1.0.0"
    worker_id = "01"

    manipulator = DataBaseManipulator()
    db_path, db_name = manipulator.create_db_path(
        strategy_name,
        strategy_version,
        worker_id
    )
    session = manipulator.get_session_creator(db_path, db_name)

    creation_order_json_body = {
        "id": "1387375",
        "marketName": "KUJI/USK",
        "marketId": "kujira193dzcmy7lwuj4eda3zpwwt9ejal00xva0vawcvhgsyyp5cfh6jyq66wfrf",
        "market": {
            "id": "kujira193dzcmy7lwuj4eda3zpwwt9ejal00xva0vawcvhgsyyp5cfh6jyq66wfrf",
            "name": "KUJI/USK",
            "baseToken": {
                "id": "ukuji",
                "name": "KUJI",
                "symbol": "KUJI",
                "decimals": 6
            },
            "quoteToken": {
                "id": "factory/kujira1qk00h5atutpsv900x202pxx42npjr9thg58dnqpa72f2p7m2luase444a7/uusk",
                "name": "USK",
                "symbol": "USK",
                "decimals": 6
            },
            "precision": 3,
            "minimumOrderSize": "0.001",
            "minimumPriceIncrement": "0.001",
            "minimumBaseAmountIncrement": "0.001",
            "minimumQuoteAmountIncrement": "0.001",
            "fees": {
                "maker": "0.075",
                "taker": "0.15",
                "serviceProvider": "0"
            },
            "deprecated": False,
            "connectorMarket": {
                "address": "kujira193dzcmy7lwuj4eda3zpwwt9ejal00xva0vawcvhgsyyp5cfh6jyq66wfrf",
                "denoms": [
                    {
                        "reference": "ukuji",
                        "decimals": 6,
                        "symbol": "KUJI"
                    },
                    {
                        "reference": "factory/kujira1qk00h5atutpsv900x202pxx42npjr9thg58dnqpa72f2p7m2luase444a7/uusk",
                        "decimals": 6,
                        "symbol": "USK"
                    }
                ],
                "precision": {
                    "decimal_places": 3
                },
                "decimalDelta": 0,
                "multiswap": True,
                "pool": "kujira1g9xcvvh48jlckgzw8ajl6dkvhsuqgsx2g8u3v0a6fx69h7f8hffqaqu36t",
                "calc": "kujira1e6fjnq7q20sh9cca76wdkfg69esha5zn53jjewrtjgm4nktk824stzyysu"
            }
        },
        "ownerAddress": "kujira1ga9qk68ne00wfflv7y2v92epaajt59e554uulc",
        "payerAddress": "kujira1ga9qk68ne00wfflv7y2v92epaajt59e554uulc",
        "price": "0.001",
        "amount": "0.1",
        "side": "BUY",
        "status": "OPEN",
        "type": "LIMIT",
        "fee": "0.00033",
        "hashes": {
            "creation": "908800826D48782041DACD6C96ADA5D296B31374EB236E9136BB4450910D366B"
        }
    }

    owner = Owner(owner_address=creation_order_json_body["ownerAddress"])

    order = Order(
        exchange_order_id=creation_order_json_body["id"],
        price=Decimal(creation_order_json_body["price"]),
        amount=Decimal(creation_order_json_body["amount"]),
        order_type=creation_order_json_body["type"],
        market_name=creation_order_json_body["marketName"],
        market_id=creation_order_json_body["marketId"],
        base_token_symbol=creation_order_json_body["market"]["baseToken"]["symbol"],
        quote_token_symbol=creation_order_json_body["market"]["quoteToken"]["symbol"],
        base_token_id=creation_order_json_body["market"]["baseToken"]["id"],
        quote_token_id=creation_order_json_body["market"]["quoteToken"]["id"],
        current_status=creation_order_json_body["status"],
        creation_timestamp=creation_order_json_body["hashes"]["creation"],
        transaction_response_body=creation_order_json_body,
        owner_address=creation_order_json_body["ownerAddress"]
    )

    session.add(owner)
    session.add(order)
    session.commit()

    owner_records = session.query(Owner).all()

    cancellation_order_json_body = {
        "id": "1387375",
        "marketName": "KUJI/USK",
        "marketId": "kujira193dzcmy7lwuj4eda3zpwwt9ejal00xva0vawcvhgsyyp5cfh6jyq66wfrf",
        "market": {
            "id": "kujira193dzcmy7lwuj4eda3zpwwt9ejal00xva0vawcvhgsyyp5cfh6jyq66wfrf",
            "name": "KUJI/USK",
            "baseToken": {
                "id": "ukuji",
                "name": "KUJI",
                "symbol": "KUJI",
                "decimals": 6
            },
            "quoteToken": {
                "id": "factory/kujira1qk00h5atutpsv900x202pxx42npjr9thg58dnqpa72f2p7m2luase444a7/uusk",
                "name": "USK",
                "symbol": "USK",
                "decimals": 6
            },
            "precision": 3,
            "minimumOrderSize": "0.001",
            "minimumPriceIncrement": "0.001",
            "minimumBaseAmountIncrement": "0.001",
            "minimumQuoteAmountIncrement": "0.001",
            "fees": {
                "maker": "0.075",
                "taker": "0.15",
                "serviceProvider": "0"
            },
            "deprecated": False,
            "connectorMarket": {
                "address": "kujira193dzcmy7lwuj4eda3zpwwt9ejal00xva0vawcvhgsyyp5cfh6jyq66wfrf",
                "denoms": [
                    {
                        "reference": "ukuji",
                        "decimals": 6,
                        "symbol": "KUJI"
                    },
                    {
                        "reference": "factory/kujira1qk00h5atutpsv900x202pxx42npjr9thg58dnqpa72f2p7m2luase444a7/uusk",
                        "decimals": 6,
                        "symbol": "USK"
                    }
                ],
                "precision": {
                    "decimal_places": 3
                },
                "decimalDelta": 0,
                "multiswap": True,
                "pool": "kujira1g9xcvvh48jlckgzw8ajl6dkvhsuqgsx2g8u3v0a6fx69h7f8hffqaqu36t",
                "calc": "kujira1e6fjnq7q20sh9cca76wdkfg69esha5zn53jjewrtjgm4nktk824stzyysu"
            }
        },
        "ownerAddress": "kujira1ga9qk68ne00wfflv7y2v92epaajt59e554uulc",
        "payerAddress": "kujira1ga9qk68ne00wfflv7y2v92epaajt59e554uulc",
        "status": "CANCELLED",
        "type": "LIMIT",
        "fee": "0.000325",
        "hashes": {
            "cancellation": "818EE194C59B9CF5DD2CB2BCC85AEC794F6FD18963DDE6EDC1DF245615871B9D"
        }
    }

    order_status_update = session.query(Order).filter_by(exchange_order_id=creation_order_json_body["id"]).first()

    if order_status_update:
        order_status_update.current_status = cancellation_order_json_body["status"]
        order_status_update.cancellation_timestamp = cancellation_order_json_body["hashes"]["cancellation"]
        order_status_update.transaction_response_body = cancellation_order_json_body
        session.commit()
    else:
        print("Owner not found")

    owner_records = session.query(Owner).all()

    session.close()
