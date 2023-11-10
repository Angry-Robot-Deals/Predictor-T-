import os
from concurrent.futures import ThreadPoolExecutor
from src.Config import settings
from pprint import pprint
from queue import Queue
import logging

from rich.logging import RichHandler
from rich.console import Console
from rich.layout import Layout
from rich.align import Align
from rich import box
from rich.align import Align
from rich.console import Console, Group
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.table import Table

from src.ui.fullscreen import demo

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler()],
)
console = Console()

# main is:
# for each trading /training /testing period do:
# 0. init data and current metrics
# 1. train in memory out train model
# 2. test in memory out test model
# 3. hypertune in memory out tuned model
# 4. demo in model out demo results
# 5. trade in model out trade results


def process_handler(symbol):
    def test(**kwargs):
        console.log("symbol:", kwargs.get("target"))
        console.log("test")
        # if current metrics is ok go to next step
        return {"step": "test", "state": "done", "target": kwargs.get("target")}

    def train(**kwargs):
        console.log("train")
        if settings.optimisation:
            return hypertune(**kwargs)
        return {"step": "train", "state": "done", "target": kwargs.get("target")}

    def hypertune(**kwargs):
        console.log("hypertune")
        return {"step": "tune", "state": "done", "target": kwargs.get("target")}

    def eval(**kwargs):
        console.log("eval")
        return {"step": "eval", "state": "done", "target": kwargs.get("target")}

    def demo(**kwargs):
        console.log("demo")
        return {"step": "demo", "state": "done", "target": kwargs.get("target")}

    tested = test(target=symbol)
    console.log(tested)
    trained = train(target=symbol)
    console.log(trained)
    evaluated = eval(target=symbol)
    console.log(evaluated)
    demostrated = demo(target=symbol)
    console.log(demostrated)


def make_layout() -> Layout:
    """Define the layout."""
    layout = Layout(name="root")

    layout.split(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=7),
    )
    layout["main"].split_row(
        Layout(name="side"),
        Layout(name="body", minimum_size=60),
    )
    layout["side"].split(Layout(name="box1"), Layout(name="box2"))
    layout["body"].split(Layout(name="body1"), Layout(name="body2"))
    return layout


from time import sleep
from rich.live import Live



def main():
    pprint(settings.__dict__)

    free_processors_count = int(os.cpu_count() / 2)
    console.log("free processors count:", int(free_processors_count))
    process_queue = Queue(maxsize=10)

    # start new process
    # Создаем ThreadPoolExecutor с ограничением по количеству потоков
    max_threads = free_processors_count
    with ThreadPoolExecutor(max_threads) as executor:
        while process_queue.empty() is False:
            # Получаем процесс из очереди (блокирующий вызов)
            process = process_queue.get()
            # Запускаем обработку процесса в отдельном потоке
            executor.submit(process_handler, process)

    demo(
        cosole=console,
        # all graphs in ui with layout
    )


if __name__ == "__main__":
    main()
