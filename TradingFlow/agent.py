import os
import pandas as pd
import random
from datetime import datetime


from tensorboardX import SummaryWriter
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from prettytable import PrettyTable as PrettyTable

from src.Config import settings


from src.Agent import Agent
from src.Environment import Environment
from src.tools.utils import (
    load_data,
    print_stats,
    load_data_ram,
)
from dotenv import load_dotenv

if False:
    from src.Database import send_signal, send_profit
else:
    from src.tools.utils import send_signal, send_profit


# to yaml / .env config [w4]
docker = os.getenv("IN_DOCKER" or None)
if docker is None:
    load_dotenv()

TENSORBOARD_LOGS_DIR = os.getenv("TENSORBOARD_LOGS")
SAVED_MODEL_FILEPATH = os.getenv("TORCH_MODEL_FILEPATH")
TRAIN_DATA_FILEPATH = os.getenv("TRAIN_FILEPATH")

TRADING_PERIOD = 300
TRAIN_EPOCHS = 5
TRAIN_DAYS = 365

TEST_SIMULATIONS = 20
TEST_APPROVE_ACCURACY = 0.6

DEMO_PRELOAD_DAYS = 0  # 0 - current last 1000 candles
DEMO_ITERATIONS = TRADING_PERIOD
DEMO_CLIENTS = 1  # this needed for balancing

SYMBOL = "BTC/USDT"
TIMEFRAME = "1m"
EXCHANGE = "binance"


class RlEcAg_Predictor:
    def __init__(self, demo: bool = False, **kwargs) -> None:
        if "symbol" in kwargs:
            global SYMBOL
            SYMBOL = kwargs.get("symbol")
            self.symbol = SYMBOL
        else:
            self.symbol = SYMBOL

        # demo trade
        self.demo = demo

        # agent
        self.double_dqn_agent = None

        # train & test params
        self.df = self.init_data(ticker=SYMBOL, timeframe=TIMEFRAME, exchange=EXCHANGE)
        self.index = random.randrange(len(self.df) - TRADING_PERIOD - 5)
        self.train_size = int(TRADING_PERIOD * 0.8)

        # enviroments & angets
        self.init_e_agent()
        self.profit_train_env = None
        self.profit_test_env = None

        # metrics
        self.profit_ddqn_return = []
        self.accuracy = []
        self.recall = []
        self.precision = []
        self.f1 = []

        # tensorboard
        self.writer = SummaryWriter(
            log_dir=TENSORBOARD_LOGS_DIR
        )  # You can customize the log directory

        print(self.__dict__)

        self.new_model_filepath = None

    def init_data(self, ticker, timeframe, exchange, remote=True) -> pd.DataFrame:
        # it can be replace for train data loader from open api or ccxt
        if not remote:
            # load from local file
            df, last_tick = load_data_ram(
                days=DEMO_PRELOAD_DAYS,
                symbol=ticker,
                timeframe=timeframe,
                exchange=exchange,
            )
        else:
            df, last_tick = load_data_ram(
                days=DEMO_PRELOAD_DAYS,
                symbol=ticker,
                timeframe=timeframe,
                exchange=exchange,
            )
        return df

    def init_e_agent(self) -> Agent:
        # hyperparams
        REPLAY_MEM_SIZE = 10000
        BATCH_SIZE = 40
        GAMMA = 0.98
        EPS_START = 1
        EPS_END = 0.12
        EPS_STEPS = 300
        LEARNING_RATE = 0.001
        INPUT_DIM = 24
        HIDDEN_DIM = 120
        ACTION_NUMBER = 3
        TARGET_UPDATE = 10

        self.double_dqn_agent = Agent(
            REPLAY_MEM_SIZE,
            BATCH_SIZE,
            GAMMA,
            EPS_START,
            EPS_END,
            EPS_STEPS,
            LEARNING_RATE,
            INPUT_DIM,
            HIDDEN_DIM,
            ACTION_NUMBER,
            TARGET_UPDATE,
            MODEL="ddqn",
            DOUBLE=True,
            symbol=self.symbol
        )
        if self.demo:
            self.remote = True
        else:
            self.remote = False

    def init_env(self) -> None:
        # try:
        model_filepath = os.getenv("TORCH_MODEL_FILEPATH")
        # except Exception as E:
        #     SAVED_MODEL_FILEPATH = os.getenv("TORCH_MODEL_FILEPATH")
        #     model_filepath = SAVED_MODEL_FILEPATH
        print(f"search model in {model_filepath}")
        def search_model(model_filepath) -> bool:
            for file in os.listdir(model_filepath):
                if self.symbol.replace('/', '_') in file:
                    return True
            return False
        
        Train = not os.path.isfile(path=model_filepath) # not search_model(model_filepath)       # 
        print("need train (pretrainded model not exist):", "yes" if Train else "no")

        # For not ready model
        if Train:
            self.profit_train_env = Environment(
                self.df[self.index : self.index + self.train_size],
                "profit",
                symbol=self.symbol,
                steps=DEMO_ITERATIONS,
            )
            self.double_dqn_agent_test, new_model_path = self.double_dqn_agent.train(
                env=self.profit_train_env,
                path=model_filepath,
                num_episodes=TRAIN_EPOCHS,
            )
            # TODO may be next time we can store images into tensorboard
            self.new_model_filepath = new_model_path

        # For ready model
        else:
            if not self.remote:
                SAVED_MODEL_FILEPATH = self.new_model_filepath if self.new_model_filepath is not None else SAVED_MODEL_FILEPATH

                # Profit ENV construction
                self.profit_test_env = Environment(
                    self.df[self.index + self.train_size : self.index + TRADING_PERIOD],
                    "profit",
                    symbol=self.symbol,
                )
                # Agent: Profit Double DQN
                self.double_dqn_agent_test, _, true_values = self.double_dqn_agent.test(
                    env_test=self.profit_test_env,
                    model_name="profit_reward_double_dqn_model",
                    path=model_filepath,
                )

    def loop(self, train_test=True):
        if train_test:
            Training = True
            while Training:
                # ENV EVOLUTION HERE
                self.init_env()
                self.profit_ddqn_return = []

                if self.profit_test_env is not None:
                    self.profit_test_env.reset()
                if self.profit_train_env is not None:
                    self.profit_train_env.reset()

                i = 0
                while i < TEST_SIMULATIONS:
                    # AGENT EVOLUTION HERE
                    index = random.randrange(len(self.df) - TRADING_PERIOD - 1)
                    profit_test_env = Environment(
                        self.df[index + self.train_size : index + TRADING_PERIOD],
                        "profit",
                        remote=False,
                        symbol=self.symbol,
                    )

                    SAVED_MODEL_FILEPATH = self.new_model_filepath if self.new_model_filepath is not None else SAVED_MODEL_FILEPATH

                    # Profit Double DQN
                    (
                        self.double_dqn_agent_test,
                        _,
                        true_values,
                    ) = self.double_dqn_agent.test(
                        profit_test_env,
                        # TODO fix
                        model_name="profit_reward_double_ddqn_model",
                        path=SAVED_MODEL_FILEPATH,
                    )

                    # Comulative return for parallel bots
                    self.profit_ddqn_return.append(profit_test_env.cumulative_return)
                    avg_mean = sum(self.profit_ddqn_return[i]) / len(
                        self.profit_ddqn_return[i]
                    )
                    if self.remote:
                        print(f"Reward for {i}", avg_mean)
                    profit_test_env.reset()
                    i += 1
                    self.writer.add_scalar("Agent_Test_End", avg_mean, i)

                    # Предположим, у вас есть список с истинными классами (1 - выигрыш, 0 - проигрыш)
                    # Предположим, у вас есть список с предсказанными классами (1 - предсказанный выигрыш, 0 - предсказанный проигрыш)
                    true_labels = true_values
                    profits_trues = [1 if x > 0 else 0 for x in true_values]
                    predicted_profits = [
                        1 if x > 0 else 0 for x in self.profit_ddqn_return[i - 1]
                    ]

                    # если правильное действие, то 1, если действие не правильное -1,
                    accuracy = accuracy_score(predicted_profits, profits_trues)
                    precision = precision_score(predicted_profits, profits_trues, zero_division=0)
                    recall = recall_score(predicted_profits, profits_trues, zero_division=0)
                    f1 = f1_score(predicted_profits, profits_trues, zero_division=0)

                    self.accuracy.append(accuracy)
                    self.precision.append(precision)
                    self.recall.append(recall)
                    self.f1.append(f1)

                    print("Accuracy:", accuracy)
                    print("Precision:", precision)
                    print("Recall:", recall)
                    print("F1_Score:", f1)

                # Reporting
                t = PrettyTable(
                    [
                        "Trading System",
                        "Avg_Return__p_",
                        "Max_Return__p_",
                        "Min_Return__p_",
                        "Std_Dev",
                    ]
                )

                print("\r\nIteration: ", i)
                print(f"{self.symbol} - tested.")
                to_tensorboard = print_stats(
                    "ProfitDDQN (stats)", self.profit_ddqn_return, t
                )
                print(t)

                ta = PrettyTable(
                    [
                        "Metrics",
                        "Avg_Accuracy__p_",
                        "Max_Accuracy__p_",
                        "Min_Accuracy__p_",
                        "Std_Dev.",
                    ]
                )
                to_tensorboard = print_stats("ProfitDDQN (accuracy)", self.accuracy, ta)
                print(ta)

                mean1 = to_tensorboard.get("mean")
                max1 = to_tensorboard.get("max")
                min1 = to_tensorboard.get("min")
                std1 = to_tensorboard.get("std")
                timestamp_now = datetime.now().timestamp()

                self.writer.add_scalar("Avg_Return__p_", mean1, timestamp_now)
                self.writer.add_scalar("Max_Return__p_", max1, timestamp_now)
                self.writer.add_scalar("Min_Return__p_", min1, timestamp_now)
                self.writer.add_scalar("Std_Dev", std1, timestamp_now)

                # plot_multiple_conf_interval()
                # os.remove(MODEL_FILEPATH)
                # while os.path.isfile(path=SAVED_MODEL_FILEPATH):
                #    pass

                Trained = True
                if Trained:
                    break
        else:
            Testing = True
            while Testing:
                self.init_env()
                self.profit_ddqn_return = []

                # load env data
                profit_demo_env = Environment(
                    self.df,
                    "profit",
                    remote=True,
                    send_profit_fn=send_profit,
                    symbol=self.symbol,
                    steps=DEMO_ITERATIONS,
                )

                SAVED_MODEL_FILEPATH = self.new_model_filepath if self.new_model_filepath is not None else SAVED_MODEL_FILEPATH


                (
                    self.double_dqn_agent_test,
                    _,
                    true_values,
                ) = self.double_dqn_agent.demo(
                    profit_demo_env,
                    model_name="profit_reward_double_dqn_model",
                    path=SAVED_MODEL_FILEPATH,
                    steps=DEMO_ITERATIONS,
                    fn_signal=send_signal,
                )

                print(profit_demo_env.cumulative_return)
                self.profit_ddqn_return.extend(profit_demo_env.cumulative_return)

                t = PrettyTable(
                    [
                        "Trading System",
                        "Avg_Return__p_",
                        "Max_Return__p_",
                        "Min_Return__p_",
                        "Std_Dev",
                    ]
                )

                to_tensorboard = print_stats(
                    "ProfitDDQN (stats)", self.profit_ddqn_return, t
                )
                print(t)
                quality = False
                if quality == "stop":
                    break

    def trade_train_test(self):
        self.loop(train_test=True)

    def agent_demo(self):
        # not work yet
        # self.loop(train_test=False)
        print("FIX DEMO: LOADING MODEL ISSUE!!!!")
        pass


if __name__ == "__main__":
    # init agent
    agent_predictions = RlEcAg_Predictor(demo=True)
    print(settings)
    # pipeline
    # agent_predictions.trade_train_test()
    # production
    agent_predictions.agent_demo()
