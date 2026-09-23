"""本地分钟线语料库：每个交易日收盘后把新浪 1 分钟 K 线永久落库。

新浪 stock_zh_a_minute 只滚动保留约 9 个交易日——不每天入库，历史分钟数据就
永远丢失。本模块按日累积全宇宙标的的语料（用户指令：建立本地化运算能力，
2026-09-21），为分钟级特征工程/盘中策略/执行验证提供不随时间蒸发的本地资产。

存储：data/minute_store/minute_YYYYMMDD.csv（每交易日一文件，幂等可重跑）。
"""
from __future__ import annotations

import datetime as dt
import logging
import os

import pandas as pd

from .config import DATA_DIR, AppConfig, ensure_dirs
from .verify import download_minute

log = logging.getLogger("quant.minute")

STORE_DIR = os.path.join(DATA_DIR, "minute_store")


def _stored_days() -> list[str]:
    try:
        return sorted(f[len("minute_"):-len(".csv")] for f in os.listdir(STORE_DIR)
                      if f.startswith("minute_") and f.endswith(".csv"))
    except FileNotFoundError:
        return []


def collect(cfg: AppConfig, codes: list[str], force: bool = False) -> dict:
    """抓取滚动窗口分钟线并按日落库（已有该日文件的跳过=幂等）。

    socket 全局超时 20s：akshare 内部 requests 不带超时，新浪连接一挂就是
    永久卡死（2026-09-21 01:25 实测第47只标的挂起7分钟）——设默认超时后
    单次请求最多 20s，_retry_call 才有机会重试或跳过。
    """
    import socket
    socket.setdefaulttimeout(20)
    ensure_dirs()
    os.makedirs(STORE_DIR, exist_ok=True)
    frames = download_minute(codes)  # 内部当日缓存：一天内多次调用不重复抓
    by_day: dict[str, list[pd.DataFrame]] = {}
    for code, df in frames.items():
        if df is None or not len(df):
            continue
        g = df.copy()
        g["code"] = code
        for day, part in g.groupby(g["day"].dt.strftime("%Y%m%d")):
            by_day.setdefault(day, []).append(part)
    saved: list[str] = []
    for day, parts in sorted(by_day.items()):
        path = os.path.join(STORE_DIR, f"minute_{day}.csv")
        day_df = pd.concat(parts, ignore_index=True)
        cols = [c for c in ("code", "day", "open", "high", "low", "close", "volume", "amount")
                if c in day_df.columns]
        if os.path.exists(path) and not force:
            # 已有日文件：覆盖率达60%视为完整跳过；部分日（新浪夜间空负载等）
            # 与新抓取合并补全——滚动窗口约9个交易日，次日仍能兜住缺口。
            try:
                old = pd.read_csv(path, dtype={"code": str})
                if old["code"].nunique() >= 0.6 * len(codes):
                    continue
                merged = (pd.concat([old[cols], day_df[cols]], ignore_index=True)
                          .drop_duplicates(subset=["code", "day"], keep="last"))
                merged.to_csv(path, index=False)
                saved.append(day)
                continue
            except Exception:  # noqa: BLE001
                log.debug("部分日合并失败 %s，覆盖重写", day)
        day_df[cols].to_csv(path, index=False)
        saved.append(day)
    result = {"days": sorted(by_day), "saved": saved, "n_codes": len(frames)}
    if saved:
        log.info("【本地语料】分钟线入库 %d 个交易日（%s ~ %s）| 本批 %d 标的",
                 len(saved), saved[0], saved[-1], len(frames))
    else:
        log.debug("分钟语料无新增（已入库或无数据）")
    return result


def maybe_collect(cfg: AppConfig, panel, force: bool = False) -> dict:
    """盘后自动入库：已有最新交易日的语料即跳过（auto 守护每日调用）。"""
    have = _stored_days()
    last_trade = pd.Timestamp(panel.dates[-1]).strftime("%Y%m%d")
    if not force and have and max(have) >= last_trade:
        return {"skipped": True, "days": len(have), "latest": max(have)}
    return collect(cfg, list(panel.codes), force=force)


def load_day(day: str) -> pd.DataFrame | None:
    """读取某交易日的全宇宙分钟线（语料消费接口）。"""
    path = os.path.join(STORE_DIR,
                        f"minute_{day.replace('-', '').replace('/', '')}.csv")
    if not os.path.exists(path):
        return None
    return pd.read_csv(path, parse_dates=["day"])


def status() -> dict:
    days = _stored_days()
    total_mb = 0.0
    if days:
        total_mb = sum(os.path.getsize(os.path.join(STORE_DIR, f"minute_{d}.csv"))
                       for d in days) / 1e6
    return {"days": len(days),
            "span": f"{days[0]}~{days[-1]}" if days else "—",
            "size_mb": round(total_mb, 1),
            "dir": STORE_DIR}


def capability_inventory(cfg: AppConfig) -> list[str]:
    """本地算力资产盘点（用户指令：建立本地能力——让积累可见）。"""
    from .config import resolve_workers
    lines = []
    try:
        w = resolve_workers(cfg)
        lines.append(f"CPU 并行评估: {w} 进程")
    except Exception:  # noqa: BLE001
        pass
    try:
        import torch  # noqa: F401
        if torch.cuda.is_available():
            lines.append(f"GPU: {torch.cuda.get_device_name(0)}")
    except Exception:  # noqa: BLE001
        lines.append("GPU: 不可用（CPU 模式）")
    try:
        cache_path = os.path.join(DATA_DIR, "eval_cache.db")
        if os.path.exists(cache_path):
            import sqlite3
            with sqlite3.connect(cache_path) as con:
                n = con.execute("SELECT COUNT(*) FROM eval_cache").fetchone()[0]
            lines.append(f"评估缓存: {n:,} 条（{os.path.getsize(cache_path) / 1e6:.0f} MB）")
    except Exception:  # noqa: BLE001
        pass
    st = status()
    lines.append(f"分钟语料: {st['days']} 个交易日（{st['span']}，{st['size_mb']} MB）")
    try:
        import glob as _glob
        csvs = _glob.glob(os.path.join(DATA_DIR, "daily", "*.csv"))
        lines.append(f"日线语料: {len(csvs)} 只标的本地CSV")
    except Exception:  # noqa: BLE001
        pass
    return lines
