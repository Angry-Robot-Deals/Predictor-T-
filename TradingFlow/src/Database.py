from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from databases import Database
from src.Config import NAME, PASS, HOST, PORT

import asyncio

from src.trade.dashboard.Entities import Item, Balance, Stats

# Замените строку подключения на свою базу данных.
DATABASE_URL = f"postgresql://{NAME}:{PASS}@{HOST}:{PORT}/{NAME}"
database = Database(DATABASE_URL)

# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Создание таблицы в базе данных (если её нет)
async def send_signal(**kwargs):
    await database.connect()
    await create_item(kwargs)
    await database.disconnect()


async def send_profit(**kwargs):
    await database.connect()
    await create_profit(kwargs)
    await database.disconnect()


async def save_iteration_stats(**kwargs):
    await database.connect()
    await create_stats(kwargs)
    await database.disconnect()


async def create_profit(item):
    async with database.transaction():
        query = Balance.__table__.insert().values(item)
        await database.execute(query)


async def create_item(item_name):
    async with database.transaction():
        query = Item.__table__.insert().values(item_name)
        await database.execute(query)


async def create_stats(item):
    async with database.transaction():
        query = Stats.__table__.insert().values(item)
        await database.execute(query)


async def main():
    await database.connect()

    while True:
        item_name = input("Введите имя записи для создания (или 'exit' для выхода): ")
        if item_name.lower() == "exit":
            break
        await create_item(item_name)

    await database.disconnect()


if __name__ == "__main__":
    # Запустить базу данных и выполнить операции в бесконечной петле
    asyncio.run(main())
