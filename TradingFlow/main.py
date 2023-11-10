from concurrent import futures
import os
from concurrent.futures import ThreadPoolExecutor
from agent import RlEcAg_Predictor
from src.Config import settings
from pprint import pprint

import logging
from rich.logging import RichHandler
from rich.console import Console

from datetime import datetime, timedelta
import pytz

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
os.system("clear")

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

        # agent
        self.symbol = symbol
        self.price_predictor = None
        self.wallet = None


    def test(self, **kwargs):
        console.log("test")
        console.log("symbol:", kwargs.get("target"))
    
        # if current metrics is ok go to next step
        return {
            "step": "test",
            "state": "done",
            "target": kwargs.get("target"),
            "symbol": self.symbol,
        }

    def train(self, **kwargs):
        console.log("train")
        if settings.optimisation:
            return self.hypertune(**kwargs)
        
        return {
            "step": "train",
            "state": "done",
            "target": kwargs.get("target"),
            "symbol": self.symbol,
        }

    def hypertune(self, **kwargs):
        # https://ax.dev/
        console.log("hypertune with https://ax.dev/")
        return {
            "step": "tune",
            "state": "done",
            "target": kwargs.get("target"),
            "symbol": self.symbol,
        }

    def eval(self, **kwargs):
        console.log("eval")
        return {
            "step": "eval",
            "state": "done",
            "target": kwargs.get("target"),
            "symbol": self.symbol,
        }

    def flow_demo(self, **kwargs):
        console.log(f"demo: {self.symbol}")
        self.price_predictor.agent_demo()
        return {
            "step": "demo",
            "state": "done",
            "target": kwargs.get("target"),
            "symbol": self.symbol,
        }

    def process_handler(self):        
        print(self.__dict__)
        run, exist, fresh = self.check_model_state()
        # is fresh
        if run:
            console.log(f"{self.symbol}: return.")
            return
        
        console.log(f"{self.symbol}: proceed.")
        self.price_predictor = RlEcAg_Predictor(
                    demo=True,
                    symbol=self.symbol
                    )        
        
        if not exist:
            trained = self.train()
            console.log(str(trained))

            tested = self.test()
            console.log(str(tested))

        if not fresh:
            evaluated = self.eval()
            console.log(str(evaluated))

        demostrated = self.flow_demo()
        console.log(str(demostrated))

    def check_model_state(self):
        import json
        lock_file = settings.lock

        def read_json_file(file_path):
            with open(file_path, 'r') as file:
                json_object = json.load(file)
            return json_object
        
        locks = read_json_file(lock_file)
        task_state = locks.get(self.symbol)
        # is run
        run = task_state.get("run" or False)
        # is exist
        file_path = task_state.get("file_path" or None)
        exist = os.path.exists(file_path)
        # is fresh
        def check_updated_at(saved_at):
            current_datetime = datetime.now()
            thirty_days_before = current_datetime - timedelta(days=settings.FRESH_DAYS)   
            updated_at = datetime.fromisoformat(saved_at)
            timezone = pytz.timezone("UTC")  
            aware_datetime = thirty_days_before.replace(tzinfo=timezone)
            return aware_datetime < updated_at
        
        updated = task_state.get("updated_at")
        fresh = check_updated_at(updated)
        return run, exist, fresh


def proceed_tradee(symbol):
    console.log(symbol)
    tradee = Tradee(symbol)
    tradee.process_handler()


def main():
    pprint(settings.__dict__)

    free_processors_count = int(os.cpu_count() / 2)
    max_threads = free_processors_count
    console.log("free processors count:", int(free_processors_count))

    # start new process
    # Создаем ThreadPoolExecutor с ограничением по количеству потоков
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        executor.map(proceed_tradee, settings.scope)

    # TODO: ui
    # demo(
    #     cosole=console,
    #     # all graphs in ui with layout
    # )


if __name__ == "__main__":
    try:
        main()
    except Exception as E:
        console.log(E)
