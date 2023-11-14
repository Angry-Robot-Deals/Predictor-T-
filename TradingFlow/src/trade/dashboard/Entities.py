from datetime import datetime
import os
from sqlalchemy import Column, Integer, String, Float, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base

try:
    from src.trade.dashboard.connection import engine
except ImportError:
    try:
        from connection import engine
    except ImportError:
        print("Failed to import the 'engine' object from the connection module.")

Base = declarative_base()


class Balance(Base):
    __tablename__ = "balances"
    __table_args__ = {"schema": "ml"}

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(Float, index=True)
    profit = Column(Float)
    volume = Column(Float)


class Signal(Base):
    __tablename__ = "signals"
    __table_args__ = {"schema": "ml"}

    # todo: action with state
    id = Column(DateTime, primary_key=True, index=True)
    name = Column(String, index=True)


class ComulativeReturn(Base):
    __tablename__ = "cumulative_return"
    __table_args__ = {"schema": "ml"}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)


class Item(Base):
    __tablename__ = "items"
    __table_args__ = {"schema": "ml"}

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(Float)
    name = Column(String, index=True)
    side = Column(Integer)
    true = Column(Integer)
    price = Column(Float)
    positions = Column(JSON)
    vector = Column(JSON)


class Stats(Base):
    __tablename__ = "stats"
    __table_args__ = {"schema": "ml"}

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(Float, default=datetime.now().timestamp())
    name = Column(String, index=True)
    means = Column(JSON)
    profit_usdt = Column(Float)
    volume = Column(Float)
    positions = Column(JSON)


if False:
    recreate = os.getenv("RECREATE_DB", False)
    if recreate:
        Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
