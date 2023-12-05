import os
import logging
from concurrent.futures import ThreadPoolExecutor

from rich.logging import RichHandler
from rich.console import Console

from src.Config import settings
from src.ui.fullscreen import demo
from src.tools.utils import check_model_state
from agent import RlEcAg_Predictor

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler()],
)
console = Console()

# main is - not it is agent, it is multiagent:
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
        # agent
        self.symbol = symbol
        self.price_predictor = None
        self.wallet = None

    def test(self, **kwargs):
        console.log("test")
        console.log("symbol:", kwargs.get("target"))

        self.price_predictor.trade_train_test()

        # if current metrics is ok go to next step
        return {
            "step": "test",
            "state": "done",
            "target": kwargs.get("target"),
            "symbol": self.symbol,
        }

    def train(self, **kwargs):
        console.log("train")

        self.price_predictor.trade_train_test()

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
        TENSORBOARD_LOGS_DIR = os.getenv("TENSORBOARD_LOGS")
        SAVED_MODEL_FILEPATH = os.getenv("TORCH_MODEL_FILEPATH")
        TRAIN_DATA_FILEPATH = os.getenv("TRAIN_FILEPATH")

        TRADING_PERIOD = 600
        TRAIN_EPOCHS = 100
        TRAIN_DAYS = 365

        TEST_SIMULATIONS = 1000
        TEST_APPROVE_ACCURACY = 0.6

        DEMO_PRELOAD_DAYS = 0  # 0 - current last 1000 candles
        DEMO_ITERATIONS = 100
        DEMO_CLIENTS = 1

        SYMBOL = self.symbol
        TIMEFRAME = "1m"
        EXCHANGE = "binance"

        console.log("hypertune with https://ax.dev/")
        return {
            "step": "tune",
            "state": "done",
            "target": kwargs.get("target"),
            "symbol": self.symbol,
        }

    def eval(self, **kwargs):
        console.log("eval not ready yet, to do it with https://ax.dev/")
        return {
            "step": "eval",
            "state": "done",
            "target": kwargs.get("target"),
            "symbol": self.symbol,
        }

    def flow_demo(self, **kwargs):
        console.log(f"Trade Flow:")
        console.log(f"demo: {self.symbol}")
        self.price_predictor.agent_demo()
        return {
            "step": "demo",
            "state": "done",
            "target": kwargs.get("target"),
            "symbol": self.symbol,
        }

    def process_handler(self):
        # TODO use for all process: 1) train all, valid all, test all, and tune all
        run, exist, tuned = check_model_state(self.symbol, settings=settings)

        # tuned - is already tuned
        if run:
            # run - is in trade now
            console.log(
                f"{self.symbol}: return is online now and not ready for restart. only force restart it."
            )
            return

        # information
        console.log(f"{self.symbol}: ready for processing.")

        # exist - is already ready for rl
        if not exist:
            self.price_predictor = RlEcAg_Predictor(demo=False, symbol=self.symbol)
            trained = self.train()
            console.log(str(trained))
            tested = self.test()
            console.log(str(tested))
            console.log(f"{self.symbol}: test done. ready for tune.")
            exist = True

        # exist - is already trained
        if not tuned:
            self.price_predictor = RlEcAg_Predictor(demo=False, symbol=self.symbol)
            evaluated = self.eval()
            console.log(str(evaluated))
            console.log("{self.symbol}: eval done. ready for demo.")
            tuned = True

        # allready read for demo trade
        if exist and tuned:
            self.price_predictor = RlEcAg_Predictor(demo=True, symbol=self.symbol)
            demostrated = self.flow_demo()
            console.log(str(demostrated))


def proceed_tradee(symbol):
    console.log(symbol)
    tradee = Tradee(symbol)
    tradee.process_handler()


def main():
    free_processors_count = int(os.cpu_count() / 2)
    max_threads = free_processors_count
    console.log("free processors count:", int(free_processors_count))
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        executor.map(proceed_tradee, settings.scope)


if __name__ == "__main__":
    try:
        main()
    except Exception as E:
        console.log(E)
