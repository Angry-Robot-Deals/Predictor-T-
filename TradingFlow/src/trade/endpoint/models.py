import os

from sqlalchemy import Boolean, Column, Enum, Integer, String
from sqlalchemy import create_engine

from .database import Base
from .schemas import Roles


class UserModel(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "ml"}

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=False, index=True)
    username = Column(String, unique=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=False)
    role = Column(Enum(Roles), default="user")


def create_all():
    # Create all tables in the database
    import dotenv
    dotenv.load_dotenv("../.env")
    SQLALCHEMY_DATABASE_URL = os.getenv("SERVICE_DATABASE_URL")
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    Base.metadata.create_all(engine)
