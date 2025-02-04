#  It essentially maps (state, action) pairs to their (next_state, reward) result,
#  with the state being the current stock price

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime
import sys
import time


from src.Loader import load_to_memory, get_date_before


def print_stats(model, value, t):
    value = np.array(value).flatten()
    t.add_row(
        [
            str(model),
            "%.2f" % np.mean(value),
            "%.2f" % np.amax(value),
            "%.2f" % np.amin(value),
            "%.2f" % np.std(value),
            # TODO: more information
        ]
    )

    return {
        "mean": np.mean(value),
        "max": np.amax(value),
        "min": np.amin(value),
        "std": np.std(value),
        # TODO: more information
    }


def plot_conf_interval(name, cum_returns):
    """NB. cum_returns must be 2-dim"""
    # Mean
    M = np.mean(np.array(cum_returns), axis=0)
    # std dev
    S = np.std(np.array(cum_returns), axis=0)
    # upper and lower limit of confidence intervals
    LL = M - 0.95 * S
    UL = M + 0.95 * S

    plt.figure(figsize=(20, 5))
    plt.xlabel("Trading Instant (h)")
    plt.ylabel(name)
    plt.legend(["Cumulative Averadge Return (%)"], loc="upper left")
    plt.grid(True)
    plt.ylim(-5, 15)
    plt.plot(range(len(M)), M, linewidth=2)  # mean curve.
    plt.fill_between(range(len(M)), LL, UL, color="b", alpha=0.2)  # std curves.
    plt.show()

    plt.savefig()


def plot_multiple_conf_interval(names, cum_returns_list):
    """NB. cum_returns[i] must be 2-dim"""
    i = 1

    for cr in cum_returns_list:
        plt.subplot(len(cum_returns_list), 2, i)
        # Mean
        M = np.mean(np.array(cr), axis=0)
        # std dev
        S = np.std(np.array(cr), axis=0)
        # upper and lower limit of confidence intervals
        LL = M - 0.95 * S
        UL = M + 0.95 * S

        plt.xlabel("Trading Instant (h)")
        plt.ylabel(names[i - 1])
        plt.title("Cumulative Averadge Return (%)")
        plt.grid(True)
        plt.plot(range(len(M)), M, linewidth=2)  # mean curve.
        plt.fill_between(range(len(M)), LL, UL, color="b", alpha=0.2)  # std curves.
        i += 1

    plt.show()


def split_raw_to_timerange():
    # TODO: it can be data kitchen
    if False:
        df = pd.read_csv(path + "one_minute.csv")
        dfs_to_concat = []
        for count in range(0, len(df) - 300, 300):
            five_minute_interval = df.iloc[count : count + 300]
            aggregated_data = pd.DataFrame(
                {
                    "Open": [five_minute_interval["Open"].iloc[0]],
                    "High": [five_minute_interval["High"].max()],
                    "Low": [five_minute_interval["Low"].min()],
                    "Close": [five_minute_interval["Close"].iloc[-1]],
                }
            )
            dfs_to_concat.append(aggregated_data)
        df_five_minute_aggregated = pd.concat(dfs_to_concat, ignore_index=True)
        df_five_minute_aggregated.to_csv(
            path + "five_minute_aggregated_dataset.csv", index=False
        )
        df = df_five_minute_aggregated
        del df_five_minute_aggregated
        print(f"Shape for range {timerange} of aggregated dataset:", df.shape)
    if False:
        df = pd.read_csv(path + "one_minute.csv")
        dfs_to_concat = []

        for count in range(0, len(df) - 60, 60):
            hour_interval = df.iloc[count : count + 60]
            aggregated_data = pd.DataFrame(
                {
                    "Open": [hour_interval["Open"].iloc[0]],
                    "High": [hour_interval["High"].max()],
                    "Low": [hour_interval["Low"].min()],
                    "Close": [hour_interval["Close"].iloc[-1]],
                }
            )
            dfs_to_concat.append(aggregated_data)

        df_hourly_aggregated = pd.concat(dfs_to_concat, ignore_index=True)
        df_hourly_aggregated.to_csv(path + "hourly_aggregated_dataset.csv", index=False)
        df = df_hourly_aggregated
        del df_hourly_aggregated
        print(f"Shape for range {timerange} of aggregated dataset:", df.shape)
    raise Exception("NOT IMPLEMENTED YET!")


def load_data(filepath=None, timerange=None):
    print(f"Processing `minutes?` to {timerange} from {filepath}")
    if os.path.isfile(filepath):
        df = pd.read_csv(filepath)
        print("Shape of aggregated dataset:", df.shape)
    else:
        raise Exception(f"{filepath} ???? Not found!")
        raise Exception(f"{filepath} ???? Not found!")

    return df


def load_data_ram(days=0, symbol="BTC/USDT", timeframe="1m", exchange="binance"):
    date_one_day_ago = get_date_before(days)
    try:
        # 1
        data, last_tick = load_to_memory(
            exchange_id=exchange,
            max_retries=100,
            symbol=symbol,
            timeframe=timeframe,
            since=date_one_day_ago,
            limit=1000,
        )
    except Exception as E:
        # TODO: fix it more enterpriseble
        try:
            # 2
            data, last_tick = load_to_memory(
                exchange_id=exchange,
                max_retries=100,
                symbol=symbol,
                timeframe=timeframe,
                since=date_one_day_ago,
                limit=1000,
            )
        except Exception as E:
            # TODO: fix it more enterpriseble
            print(E)
            # 3
            data, last_tick = load_to_memory(
                exchange_id=exchange,
                max_retries=100,
                symbol=symbol,
                timeframe=timeframe,
                since=date_one_day_ago,
                limit=1000,
            )
            pass

    # Convert milliseconds timestamp to seconds
    timestamp_seconds = last_tick / 1000

    # Convert to a datetime object
    datetime_obj = datetime.datetime.utcfromtimestamp(timestamp_seconds)

    # Format the datetime object as a string
    formatted_time = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")

    print(
        f"{symbol}",
        "Last server tick",
        formatted_time,
        "with `Close` price",
        data.iloc[-1, :]["Close"],
    )

    return data, last_tick


def clean_loader():
    sys.stdout.write("\r")
    sys.stdout.flush()


def show_loader():
    # Define a list of rotating characters
    loader_chars = ["-", "\\", "|", "/"]

    # Initialize the index of the current character
    char_index = 0

    for _ in range(len(loader_chars)):
        # Print the current character without a newline
        sys.stdout.write("\r" + loader_chars[char_index])
        sys.stdout.flush()

        # Sleep for a short time to control the animation speed
        time.sleep(0.1)

        # Move to the next character
        char_index = (char_index + 1) % len(loader_chars)


def demo_wait_tick(last_tick):
    # Get the current timestamp in seconds
    current_timestamp = time.time()
    time.sleep(0.1)

    # Convert the given timestamp (last_tick) to seconds
    timestamp_seconds = last_tick / 1000

    # Convert to a datetime object
    last_tick_datetime = datetime.datetime.utcfromtimestamp(timestamp_seconds)
    current_datetime = datetime.datetime.utcfromtimestamp(current_timestamp)

    # Format the datetime objects as strings
    formatted_last_tick = last_tick_datetime.strftime("%Y-%m-%d %H:%M")
    formatted_current = current_datetime.strftime("%Y-%m-%d %H:%M")

    is_need_wait = formatted_last_tick == formatted_current
    return is_need_wait


def print_action(act: int, agent_positions: list = []):
    if act == 0:
        print("Stay...")
    if act == 1:
        print("Buy...")
    if act == 2 and len(agent_positions) > 0:
        print("Sell...")
    else:
        pass


async def send_signal(**kwargs):
    print(str(kwargs))


async def send_profit(**kwargs):
    print(str(kwargs))


def check_model_state(symbol, settings=None):
    import json
    from datetime import datetime, timedelta
    import pytz

    lock_file = settings.lock

    def read_json_file(file_path):
        with open(file_path, 'r') as file:
            json_object = json.load(file)
        return json_object
    
    locks = read_json_file(lock_file)
    task_state = locks.get(symbol)
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