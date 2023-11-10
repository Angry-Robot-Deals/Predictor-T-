import asyncio
from concurrent import futures
import os
from concurrent.futures import ThreadPoolExecutor
from src.Config import settings
from pprint import pprint
from queue import Queue
import logging

from rich.logging import RichHandler
from rich.console import Console

from src.ui.fullscreen import demo

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler()],
)
console = Console()

# main is:
# for each trading / training / testing period do:
# 0. init data and current metrics
# 1. train in memory out train model
# 2. test in memory out test model
# 3. hypertune in memory out tuned model
# 4. demo in model out demo results
# 5. trade in model out trade results


class Tradee:
    def __init__(self, symbol) -> None:
        from agent import RlEcAg_Predictor

        TENSORBOARD_LOGS_DIR = os.getenv("TENSORBOARD_LOGS")
        SAVED_MODEL_FILEPATH = os.getenv("TORCH_MODEL_FILEPATH")
        TRAIN_DATA_FILEPATH = os.getenv("TRAIN_FILEPATH")

        TRADING_PERIOD = 600
        TRAIN_EPOCHS = 20000
        TRAIN_DAYS = 365

        TEST_SIMULATIONS = 1000
        TEST_APPROVE_ACCURACY = 0.6

        DEMO_PRELOAD_DAYS = 0  # 0 - current last 1000 candles
        DEMO_ITERATIONS = 100
        DEMO_CLIENTS = 1

        SYMBOL = "BTC/USDT"
        TIMEFRAME = "1m"
        EXCHANGE = "binance"

        self.symbol = symbol

        # self.price_predictor = RlEcAg_Predictor(
        #     demo=True,
        #     symbol=symbol
        #     )

    def test(self, **kwargs):
        console.log("symbol:", kwargs.get("target"))
        console.log("test")
        # if current metrics is ok go to next step
        return {"step": "test", "state": "done", "target": kwargs.get("target"), "symbol": self.symbol}

    def train(self, **kwargs):
        console.log("train")
        if settings.optimisation:
            return self.hypertune(**kwargs)
        return {"step": "train", "state": "done", "target": kwargs.get("target"), "symbol": self.symbol}

    def hypertune(self, **kwargs):
        console.log("hypertune")
        return {"step": "tune", "state": "done", "target": kwargs.get("target"), "symbol": self.symbol}

    def eval(self, **kwargs):
        console.log("eval")
        return {"step": "eval", "state": "done", "target": kwargs.get("target"), "symbol": self.symbol}

    def demo(self, **kwargs):
        console.log("demo")
        # self.price_predictor.trade_demo()
        return {"step": "demo", "state": "done", "target": kwargs.get("target"), "symbol": self.symbol}

    def process_handler(self):
        print(self.__dict__)
        tested = self.test()
        console.log(str(tested))
        trained = self.train()
        console.log(str(trained))
        evaluated = self.eval()
        console.log(str(evaluated))
        demostrated = self.demo()
        console.log(str(demostrated))


def proceed_tradee(symbol):
    console.log(symbol)
    tradee = Tradee(symbol)
    tradee.process_handler()

def main():
    pprint(settings.__dict__)

    free_processors_count = int(os.cpu_count() / 4)
    max_threads = free_processors_count
    console.log("free processors count:", int(free_processors_count))    

    # start new process
    # Создаем ThreadPoolExecutor с ограничением по количеству потоков
    with ThreadPoolExecutor(max_workers=3) as executor:
        executor.map(proceed_tradee, settings.scope)


    

    # TODO: ui
    # demo(
    #     cosole=console,
    #     # all graphs in ui with layout
    # )


if __name__ == "__main__":
    main()
