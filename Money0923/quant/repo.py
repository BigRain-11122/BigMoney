"""国债逆回购现金管理（GC001 / 沪市204001）——用户指令 2026-09-22：
"现金可以加入国债逆回购赚取隔夜收益"。

机制（沪深现行规则，2026-09-22 数据实测）：
- 1000元起、1000整数倍；年化利率以"卖出价"成交，价格即年化%（GC001最小变动0.005）
- 计息按资金实际占款天数：T日尾盘借出 → 资金T+1交易日开市前归还（可用可取）
  → 与本系统日频节奏天然契合：收盘决策→次日开盘执行，现金隔夜无冲突
- 占款天数 = T 至下一交易日间的自然日数（周五=3天，节假日前更长）
- 利息 = 金额 × 年化% × 占款天数 / 365（沪市计息基准365天）
- 佣金 = 金额 × 0.00001（十万分之一），一次性收取
- 风险 ≈ 0：交易所质押 + 中国结算担保交收

三端一致（防"模拟盘比回测虚胖"的口径分裂）：
- paper：收盘结算后按各分仓现金借出，次日会话开始前归还本息（真实节奏）
- backtest / futures_backtest：每日收盘现金按当日204001真实历史收盘利率隔夜计息
  （选才管道必须知道"现金不是死钱"，否则系统性低估防御型策略）
- live：QMT实盘接入时按同参数下单204001卖出（当前 mode=paper 惰性）

数据源：腾讯 stock_zh_a_hist_tx(sh204001) 日K（2015→今实测全史覆盖，close=年化%）；
实时利率用 qt.gtimg.cn/q=sh204001 轻量报价（收盘结算时取当日真实成交利率）。
"""
from __future__ import annotations

import datetime as dt
import logging
import os
import socket

import pandas as pd

from .config import DATA_DIR, AppConfig

log = logging.getLogger("quant.repo")

_REPO_FILE = os.path.join(DATA_DIR, "repo_daily.csv")
_symbol = "204001"
_rmap_cache: dict | None = None
_rmap_mtime: float = -1.0


# ---------------------------------------------------------------- 数据
def update_repo_daily(force: bool = False) -> int:
    """日更204001历史利率缓存（追加式；当日已更新则跳过——与期货日更同节奏）。"""
    if not force and os.path.exists(_REPO_FILE) and _fresh_today(_REPO_FILE):
        return -1
    import akshare as ak
    socket.setdefaulttimeout(20)  # akshare无内置超时是系统级风险（2026-09-21教训）
    df = ak.stock_zh_a_hist_tx(symbol="sh204001")            # 全史一次拉齐
    if df is None or len(df) == 0:
        return 0
    df = df[["date", "close"]].rename(columns={"close": "rate"})
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    df["rate"] = pd.to_numeric(df["rate"], errors="coerce")
    df = df.dropna(subset=["rate"])
    df = df.drop_duplicates("date", keep="last").sort_values("date")
    os.makedirs(DATA_DIR, exist_ok=True)
    df.to_csv(_REPO_FILE, index=False)
    global _rmap_cache
    _rmap_cache = None
    return len(df)


def _fresh_today(path: str) -> bool:
    try:
        return os.path.getmtime(path) >= _today_start_ts()
    except OSError:
        return False


def _today_start_ts() -> float:
    d = dt.date.today()
    return dt.datetime(d.year, d.month, d.day).timestamp()


def load_rate_map() -> dict[str, float]:
    """date("YYYY-MM-DD") -> 当日GC001收盘年化%。进程内mtime缓存；缺失返回空dict。"""
    global _rmap_cache, _rmap_mtime
    try:
        mtime = os.path.getmtime(_REPO_FILE)
    except OSError:
        return {}
    if _rmap_cache is not None and mtime == _rmap_mtime:
        return _rmap_cache
    try:
        df = pd.read_csv(_REPO_FILE, dtype={"date": str, "rate": float})
        _rmap_cache = dict(zip(df["date"], df["rate"]))
        _rmap_mtime = mtime
    except Exception:  # noqa: BLE001
        return {}
    return _rmap_cache


def spot_repo_rate() -> float | None:
    """实时GC001年化%（腾讯轻量报价专用通道——spot_quotes_light按首位路由错市场）。"""
    import requests
    try:
        r = requests.get("http://qt.gtimg.cn/q=sh204001", timeout=8)
        r.encoding = "gbk"
        for seg in r.text.split(";"):
            if "~" not in seg:
                continue
            p = seg.split("~")
            if len(p) > 4 and p[2].zfill(6) == _symbol and p[3]:
                v = float(p[3])
                if 0.0 < v < 100.0:      # 年化%物理界内（历史极值~50%）
                    return v
    except Exception:  # noqa: BLE001
        pass
    return None


# ---------------------------------------------------------------- 计息数学
def lend_days(d: dt.date) -> int:
    """占款天数 = 当日 → 下一交易日的自然日数（周五=3，节假日前更长）。"""
    from . import clock
    try:
        nxt = clock.next_trade_date(d)
        return max(1, (nxt - d).days)
    except Exception:  # noqa: BLE001
        return 1


def lend_amount(cash: float, min_lend: float = 1000.0) -> float:
    """可借金额 = 1000元整数倍（沪市门槛1000起，1000整数倍）。"""
    amt = float(cash) // min_lend * min_lend
    return amt if amt >= min_lend else 0.0


def interest(amount: float, rate_pct: float, days: int, cfg: AppConfig) -> float:
    """毛利息 = 金额×年化%×占款天数/365（沪市计息基准）。"""
    basis = int(getattr(cfg.risk, "repo_year_basis", 365))
    return amount * float(rate_pct) / 100.0 * days / basis


def fee(amount: float, cfg: AppConfig) -> float:
    """佣金 = 成交金额×十万分之一（现行规则，一次性收取）。"""
    return amount * float(getattr(cfg.risk, "repo_fee_rate", 0.00001))


def net_interest(amount: float, rate_pct: float, days: int, cfg: AppConfig) -> float:
    return interest(amount, rate_pct, days, cfg) - fee(amount, cfg)


# ---------------------------------------------------------------- 回测端：逐日现金计息
def overnight_cash_yield(dates: list[str], cfg: AppConfig) -> list[float] | None:
    """回测引擎用：返回与dates同长的"当日收盘现金单位隔夜净收益率"数组。
    rate取当日204001收盘年化%，days按日历算占款；数据缺失日期用保守默认利率。
    repo_enabled=False 或无历史数据时返回 None（引擎跳过，现金收益=0，诚实留痕）。"""
    if not getattr(cfg.risk, "repo_enabled", False):
        return None
    rmap = load_rate_map()
    if not rmap:
        return None
    default_rate = float(getattr(cfg.risk, "repo_default_rate", 1.8))
    out: list[float] = []
    for i, dstr in enumerate(dates):
        rate = float(rmap.get(dstr, default_rate))
        if i + 1 < len(dates):
            try:
                d0 = dt.date.fromisoformat(dstr)
                d1 = dt.date.fromisoformat(dates[i + 1])
                days = max(1, (d1 - d0).days)
            except ValueError:
                days = 1
        else:
            days = 1
        out.append(net_interest(1.0, rate, days, cfg))   # 单位现金的净收益率
    return out


# ---------------------------------------------------------------- 模拟盘端：借出/归还
def paper_lend(state: dict, cfg: AppConfig, today: dt.date) -> list[dict]:
    """收盘结算后调用：各分仓现金按1000整数倍借出，双记账（仓内+总账）同步扣减。
    返回本次借出清单（含利率/天数/应收利息），并存入 state.repo_open。"""
    if not getattr(cfg.risk, "repo_enabled", False):
        return []
    rate = spot_repo_rate()
    if rate is None:
        rmap = load_rate_map()
        rate = float(rmap[max(rmap)]) if rmap else None   # 最后已知收盘利率
    if rate is None:
        rate = float(getattr(cfg.risk, "repo_default_rate", 1.8))
        log.info("【逆回购】实时利率缺失，用保守默认年化 %.2f%%", rate)
    days = lend_days(today)
    min_lend = float(getattr(cfg.risk, "repo_min_lend", 1000.0))
    opened: list[dict] = []
    sleeves = state.get("sleeves") or []
    ledgers: list[tuple[str, dict]] = []
    for sv in sleeves:                       # 分仓各自借出（利息归属清晰）
        ledgers.append((sv.get("id", "?"), sv))
    acc = state["account"]
    if not sleeves:                          # 无分仓结构：整账户现金借出
        ledgers.append(("", acc))
    for sid, ledger in ledgers:
        amt = lend_amount(float(ledger.get("cash", 0.0) or 0.0), min_lend)
        if amt < min_lend:
            continue
        rec = {"date": today.isoformat(), "sleeve": sid, "amount": round(amt, 2),
               "rate": round(rate, 3), "days": days,
               "interest": round(interest(amt, rate, days, cfg), 4),
               "fee": round(fee(amt, cfg), 4),
               "return_date": _next_trade_key(today)}
        # 双记账不变式：仓内现金与总账现金同步扣减
        ledger["cash"] = round(float(ledger.get("cash", 0.0) or 0.0) - amt, 2)
        acc["cash"] = round(float(acc.get("cash", 0.0) or 0.0) - amt, 2)
        opened.append(rec)
    if opened:
        state.setdefault("repo_open", []).extend(opened)
        state["repo_open"] = state["repo_open"][-20:]
    return opened


def paper_return(state: dict, today_key: str) -> list[dict]:
    """会话开始时调用：归还所有 return_date ≤ 今日 的逆回购本息（双记账同步加回）。
    GC001资金T+1开市前到账——次日开盘执行订单不受任何影响。"""
    acc = state["account"]
    sleeves = {sv.get("id"): sv for sv in (state.get("sleeves") or [])}
    still: list[dict] = []
    returned: list[dict] = []
    for rec in state.get("repo_open") or []:
        if str(rec.get("return_date", "99991231")) > today_key:
            still.append(rec)
            continue
        amt = float(rec.get("amount", 0.0))
        net = amt + float(rec.get("interest", 0.0)) - float(rec.get("fee", 0.0))
        sid = rec.get("sleeve", "")
        sv = sleeves.get(sid) if sid else None
        if sv is not None:
            sv["cash"] = round(float(sv.get("cash", 0.0) or 0.0) + net, 2)
            acc["cash"] = round(float(acc.get("cash", 0.0) or 0.0) + net, 2)
        else:
            acc["cash"] = round(float(acc.get("cash", 0.0) or 0.0) + net, 2)
        returned.append(rec)
    if returned:
        state["repo_open"] = still
        state.setdefault("repo_log", []).extend(returned)
        state["repo_log"] = state["repo_log"][-1000:]
    return returned


def open_principal(state: dict) -> float:
    """在途逆回购本金（account_equity 计入，防止隔夜读数把借出本金当浮亏）。"""
    return sum(float(r.get("amount", 0.0)) for r in state.get("repo_open") or [])


def total_interest_earned(state: dict) -> float:
    return sum(float(r.get("interest", 0.0)) - float(r.get("fee", 0.0))
               for r in state.get("repo_log") or [])


def _next_trade_key(d: dt.date) -> str:
    from . import clock
    try:
        return clock.next_trade_date(d).strftime("%Y%m%d")
    except Exception:  # noqa: BLE001
        return (d + dt.timedelta(days=1)).strftime("%Y%m%d")
