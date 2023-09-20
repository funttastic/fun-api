import os
from sqlalchemy import (
    create_engine,
    Column,
    BigInteger,
    String,
    Text,
    DECIMAL,
    JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

working_directory = os.path.dirname(
    os.path.dirname(os.path.realpath(__file__))
)
# os.chdir(working_directory)


ClientBase = declarative_base()


class Order(ClientBase):
    __tablename__ = "Order"

    exchange_id = Column(String(32), primary_key=True, nullable=False)
    price = Column(DECIMAL(6), nullable=False)
    amount = Column(DECIMAL(6), nullable=False)
    order_type = Column(Text, nullable=False)
    market_name = Column(String(32), nullable=False)
    market_id = Column(Text, nullable=False)
    base_symbol = Column(String(32), nullable=False)
    quote_symbol = Column(String(32), nullable=False)
    base_id = Column(Text, nullable=False)
    quote_id = Column(Text, nullable=False)
    current_status = Column(Text, nullable=False)
    creation_timestamp = Column(BigInteger, nullable=False)
    transaction_response_body = Column(JSON, nullable=False)


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

    def create_session(self, _db_path: str, _db_name: str):
        db_session = None
        try:
            os.makedirs(_db_path, exist_ok=True)
            url = f"{self._RDBMS}:///{_db_path}/{_db_name}"
            db_engine = create_engine(url)
            ClientBase.metadata.create_all(db_engine)
            db_session = sessionmaker(bind=db_engine)()
        except Exception as e:
            raise f"An error occurred during database session creation: {e}"
        finally:
            return db_session


if __name__ == '__main__':

    strategy_name = "pure_market_making"
    strategy_id = "01"
    strategy_version = "1.0.0"
    worker_id = "01"

    manipulator = DataBaseManipulator()
    db_path, db_name = manipulator.create_db_path(
        strategy_name,
        strategy_version,
        worker_id
    )
    session = manipulator.create_session(db_path, db_name)
    session.close()
