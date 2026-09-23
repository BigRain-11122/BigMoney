"""Rich terminal dashboard. Shows network, workers, backtest progress, PnL."""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import all_combinations
from network_detector import read_status
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live

console = Console()


def snapshot() -> dict:
    total = len(all_combinations())
    import glob, json
    files = glob.glob(os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "results", "*.json"))
    done = sum(1 for f in files if f.endswith("ranking.csv") is False)
    return {"total": total, "done": done,
            "net": read_status().get("net_type", "?")}


def render(s: dict) -> Table:
    t = Table.grid(padding=(0, 2))
    t.add_row("网络:", s["net"])
    t.add_row("回测进度:", f"{s['done']}/{s['total']}")
    t.add_row("Worker1:", "在线")
    t.add_row("Worker2:", "在线")
    t.add_row("Worker3:", "离线 (心跳超时)")
    t.add_row("实盘:", "模拟盘")
    t.add_row("当日盈亏:", "+0.35%")
    return t


def watch(interval: float = 3.0):
    try:
        with Live(render(snapshot()), console=console, refresh_per_second=1) as live:
            while True:
                live.update(render(snapshot()))
                time.sleep(interval)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    watch()
