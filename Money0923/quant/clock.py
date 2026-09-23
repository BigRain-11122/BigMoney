"""交易日历与开市时段判断（本机时区即北京时间 Asia/Shanghai）。

日历来自 akshare tool_trade_date_hist_sina（覆盖当年及次年部分），本地缓存，
临近日历末尾自动刷新；网络异常时退回缓存。
"""
from __future__ import annotations

import datetime as dt
import os

import pandas as pd

from .config import DATA_DIR, ensure_dirs

_CAL_FILE = os.path.join(DATA_DIR, "trade_dates.csv")
_CAL: pd.DatetimeIndex | None = None

SESSION_AM = (dt.time(9, 30), dt.time(11, 30))
SESSION_PM = (dt.time(13, 0), dt.time(15, 0))
ORDER_WINDOW = (dt.time(9, 25), dt.time(14, 50))  # 实盘/模拟盘允许发单窗口


def _load_calendar() -> pd.DatetimeIndex:
    global _CAL
    if _CAL is not None:
        return _CAL
    ensure_dirs()
    need_fetch = True
    if os.path.exists(_CAL_FILE):
        try:
            cached = pd.DatetimeIndex(pd.read_csv(_CAL_FILE, parse_dates=["trade_date"])["trade_date"])
            # 日历已覆盖到 30 天后 → 缓存仍有效
            if len(cached) and cached.max() >= pd.Timestamp(dt.date.today() + dt.timedelta(days=30)):
                need_fetch = False
        except Exception:
            need_fetch = True
    if need_fetch:
        try:
            import akshare as ak
            df = ak.tool_trade_date_hist_sina()
            pd.DataFrame({"trade_date": pd.to_datetime(df["trade_date"])}).to_csv(_CAL_FILE, index=False)
        except Exception:
            if not os.path.exists(_CAL_FILE):
                raise
            # 网络失败但有缓存：继续用缓存
    _CAL = pd.DatetimeIndex(pd.read_csv(_CAL_FILE, parse_dates=["trade_date"])["trade_date"])
    return _CAL


def trade_dates() -> pd.DatetimeIndex:
    return _load_calendar()


def is_trade_date(day: dt.date | None = None) -> bool:
    day = day or dt.date.today()
    return pd.Timestamp(day) in _load_calendar()


def last_trade_date(day: dt.date | None = None) -> dt.date:
    """≤ day 的最近交易日（day 为交易日时返回自身）。"""
    day = day or dt.date.today()
    ts = pd.Timestamp(day)
    cal = _load_calendar()
    idx = cal.searchsorted(ts, side="right") - 1
    if idx < 0:
        raise ValueError(f"交易日历不含 {day} 之前的日期")
    return cal[idx].date()


def next_trade_date(day: dt.date | None = None) -> dt.date:
    """> day 的下一个交易日。"""
    day = day or dt.date.today()
    ts = pd.Timestamp(day)
    cal = _load_calendar()
    idx = cal.searchsorted(ts, side="right")
    if idx >= len(cal):
        raise ValueError(f"交易日历未覆盖 {day} 之后，请联网刷新日历")
    return cal[idx].date()


def _in_window(now: dt.datetime, window: tuple[dt.time, dt.time]) -> bool:
    return window[0] <= now.time() <= window[1]


def in_session(now: dt.datetime | None = None) -> bool:
    """当前是否处于连续竞价时段（9:30-11:30 / 13:00-15:00）。"""
    now = now or dt.datetime.now()
    if not is_trade_date(now.date()):
        return False
    return _in_window(now, SESSION_AM) or _in_window(now, SESSION_PM)


def in_order_window(now: dt.datetime | None = None) -> bool:
    now = now or dt.datetime.now()
    if not is_trade_date(now.date()):
        return False
    return _in_window(now, ORDER_WINDOW)


def seconds_until(target: dt.datetime, now: dt.datetime | None = None) -> float:
    now = now or dt.datetime.now()
    return max(0.0, (target - now).total_seconds())
