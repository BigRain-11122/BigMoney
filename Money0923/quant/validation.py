"""数据真实性校验闸：任何数据未经校验不得进入进化/回测/实盘决策（防"数据幻觉"）。

三道防线：
1. **涨跌停限制数据驱动推断**：观察样本内相邻交易日最大真实波幅推断该标的的真实限制
   （如创业板ETF 20%，规则表错标 10% 会把真实行情误判为异常）——推断结果持久化，
   回测/模拟盘撮合的涨跌停拒单规则同源使用。
2. **ETF份额折算/分红缺口修复**：不复权ETF数据在拆分/折算日出现物理不可能跳空
   （如 1拆3 = -66.7%假崩盘）→ 按比率反向回溯调整历史K线，恢复连续的真实收益序列，
   修复写回缓存并留痕。
3. **股票坏数据剔除**：相邻交易日波幅超出(推断)限制×1.3+2% 的物理不可能跳变
   = 复权缺口/坏K线，整只剔除出面板（宁可不交易，不喂假数据）。

其余校验：OHLC 逻辑矛盾、缺失率>40%、样本量<min_bars。
全部结果写 data/validation_report.json，日报与周度复盘自动披露。
"""
from __future__ import annotations

import datetime as dt
import json
import logging
import os

import numpy as np
import pandas as pd

from . import clock
from .config import DATA_DIR
from .data import is_etf, limit_up_pct

log = logging.getLogger("quant.validation")

REPORT_FILE = os.path.join(DATA_DIR, "validation_report.json")
INFERRED_LIMITS_FILE = os.path.join(DATA_DIR, "inferred_limits.json")

# 缓存模块级推断结果（避免回测热路径反复读盘）
_inferred_cache: dict[str, float] | None = None


def load_inferred_limits() -> dict[str, float]:
    """数据推断的真实涨跌幅限制（如创业板ETF=20%）。"""
    global _inferred_cache
    if _inferred_cache is None:
        try:
            with open(INFERRED_LIMITS_FILE, encoding="utf-8") as f:
                _inferred_cache = {str(k): float(v) for k, v in json.load(f).items()}
        except Exception:  # noqa: BLE001
            _inferred_cache = {}
    return _inferred_cache


def effective_limit(code: str) -> float:
    """推断值优先（来自真实数据观察），规则表兜底。"""
    inferred = load_inferred_limits().get(code)
    if inferred and inferred > limit_up_pct(code):
        return inferred
    return limit_up_pct(code)


def _adjacent_mask(dates: pd.DatetimeIndex) -> np.ndarray:
    """相邻交易日掩码：跨停牌/长假跳空是合法的，不在涨跌停校验范围。"""
    cal = clock.trade_dates()
    pos = cal.searchsorted(dates.to_numpy())
    adj = np.zeros(len(dates), dtype=bool)
    adj[1:] = (pos[1:] - pos[:-1]) == 1
    return adj


def infer_limit_from_data(code: str, df: pd.DataFrame) -> float:
    """观察相邻交易日最大波幅：>11% 即为 20% 限制品种（创业板ETF/双创等）。"""
    if len(df) < 3:
        return 0.0
    ret = df["close"].pct_change().abs().to_numpy()
    try:
        adj = _adjacent_mask(df.index)
        obs = float(np.nanmax(ret * adj)) if adj.any() else 0.0
    except Exception:  # noqa: BLE001 日历不可用则保守用全样本
        obs = float(np.nanmax(ret[1:])) if len(ret) > 1 else 0.0
    return 0.20 if obs > 0.11 else 0.0


def _new_stock_grace(pos_n: int, grace: int = 5) -> np.ndarray:
    """新股上市前5个交易日无涨跌幅限制（实测：603376/-20.9%、301632/+28.2%、
    603248/-29.3% 均为上市第2日真实行情）——序列前 grace 根K线豁免跳变判定。"""
    mask = np.ones(pos_n, dtype=bool)
    mask[:grace] = False
    return mask


def _repair_etf_discontinuity(code: str, df: pd.DataFrame, limit: float) -> pd.DataFrame:
    """修复ETF不复权序列的份额折算/大额分红跳空：按比率回溯调整事件前历史。

    检出条件：相邻交易日收益超出 limit×1.3+2%（物理不可能）；前5根K线豁免
    （新上市ETF初期波动合法，不做修复假设）。
    比率 = 事件日收盘 / 前收 —— 对 1拆3 型折算即 1/3，恢复真实连续收益。
    """
    thr = limit * 1.3 + 0.02
    ret = df["close"].pct_change()
    try:
        adj = _adjacent_mask(df.index)
    except Exception:  # noqa: BLE001
        adj = np.ones(len(df), dtype=bool)
    bad = (ret.abs() > thr) & adj & _new_stock_grace(len(df))
    if not bad.any():
        return df
    df = df.copy()
    for i in np.nonzero(bad.to_numpy())[0]:
        prev_close = float(df["close"].iloc[i - 1])
        cur_close = float(df["close"].iloc[i])
        ratio = cur_close / prev_close
        # 企业行为比率判定：拆分/合并的比率必然远离涨跌停边界——
        # 真实跌停最多 -20%（ratio≥0.8）、真实涨停最多 +20%（ratio≤1.2），
        # 故仅 ratio<0.75（拆分/大额折算）或 >1.35（份额合并）才认定为企业行为。
        # 边界附近（0.75~1.35）的跳空不修复：20%限制品种的合法涨跌停不受污染，
        # 留给限制推断与剔除逻辑诚实处理。
        if not (0 < ratio < 0.75 or ratio > 1.35):
            continue
        event_date = df.index[i]
        for col in ("open", "high", "low", "close"):
            df.loc[df.index < event_date, col] = df.loc[df.index < event_date, col] * ratio
        log.warning("【数据修复】%s 检出份额折算/合并跳空 @%s（表面%.1f%%）→ 历史K线按 %.4f 回溯调整",
                    code, event_date.date(), (ratio - 1) * 100, ratio)
    return df


def validate_frames(frames: dict[str, pd.DataFrame], min_bars: int = 120
                    ) -> tuple[dict[str, pd.DataFrame], dict]:
    report: dict = {
        "time": dt.datetime.now().isoformat(timespec="seconds"),
        "n_input": len(frames),
        "excluded": [],
        "repaired": [],
        "anomaly_bars": [],
        "inferred_20pct": [],
        "n_clean": 0,
    }
    clean: dict[str, pd.DataFrame] = {}
    inferred: dict[str, float] = {}

    for code, df in frames.items():
        if len(df) < min_bars:
            report["excluded"].append({"code": code, "reason": f"样本不足({len(df)}根<{min_bars})"})
            continue
        close = df["close"]
        if float(close.isna().mean()) > 0.40:
            report["excluded"].append({"code": code, "reason": f"收盘缺失率{close.isna().mean():.0%}"})
            continue

        # ① ETF 折算/分红缺口修复（先修复，修复后的序列才能用于后续判定）
        if is_etf(code):
            df = _repair_etf_discontinuity(code, df, limit_up_pct(code))
            if not df.equals(frames[code]):
                report["repaired"].append(code)

        # ② 涨跌停限制推断——仅限ETF（股票前缀规则可靠：00/60→10%，30/68→20%；
        #    新股前5日无限制的波动由豁免逻辑处理，不污染限制推断）
        limit = limit_up_pct(code)
        if is_etf(code):
            lim_data = infer_limit_from_data(code, df)
            if lim_data > limit:
                limit = lim_data
                inferred[code] = lim_data
                report["inferred_20pct"].append(code)

        # ③ OHLC 逻辑矛盾
        bad_ohlc = (
            (df["high"] < df[["open", "close"]].max(axis=1) - 1e-9)
            | (df["low"] > df[["open", "close"]].min(axis=1) + 1e-9)
            | (df["close"] <= 0)
        )

        # ④ 物理不可能跳变（用推断后的真实限制判定；跨停牌跳空与新股前5日豁免）
        ret = df["close"].pct_change()
        thr = limit * 1.3 + 0.02
        jump = ret.abs() > thr
        try:
            jump = jump & pd.Series(_adjacent_mask(df.index), index=df.index)
        except Exception:  # noqa: BLE001
            pass
        jump = jump & pd.Series(_new_stock_grace(len(df)), index=df.index)
        n_bad = int(bad_ohlc.sum())
        n_jump = int(jump.sum())
        if n_jump > 0:
            # 股票的物理不可能跳变 = 复权缺口/坏K线 → 整只剔除（修复须靠全量重拉）
            if not is_etf(code):
                for d in df.index[jump][:3]:
                    report["excluded"].append({"code": code, "reason":
                                               f"物理不可能跳变@{d.date()}({(float(df['close'].loc[d]) / float(df['close'].shift(1).loc[d]) - 1) * 100:+.1f}%)→疑复权缺口"})
                continue
            # ETF 修复后仍超限（向上跳空无企业行为对应）→ 剔除
            for d in df.index[jump][:3]:
                report["excluded"].append({"code": code, "reason": f"修复后仍异常跳变@{d.date()}"})
            continue
        if n_bad > 0:
            for d in df.index[bad_ohlc][:5]:
                report["anomaly_bars"].append({"code": code, "date": str(d.date()), "type": "ohlc"})
            report["anomaly_bars"] = report["anomaly_bars"][-60:]
        clean[code] = df

    report["n_clean"] = len(clean)
    # —— 污染清除联动（用户红线 2026-09-21"错误的训练数据及时清空，发现以后，
    #    不要污染我的模型"）：本次校验相对上次发现新修复/新剔除/新推断 = 新发现
    #    坏数据 → 升股票数据纪元，评估缓存分与联赛实战证据按事件类型清除。
    #    只比语义集合不看时间戳/计数；合成测试数据（<30只）不触发真实清除。
    if len(frames) >= 30:
        prev = load_last_report() or {}
        events = _discovery_diff(prev, report)
        if events:
            from .data import bump_data_epoch  # 惰性导入防 data↔validation 循环
            bump_data_epoch("stock", "校验发现数据修正：" + "；".join(events))
    # 持久化推断的涨跌停限制（回测/模拟盘撮合同源使用）
    if inferred:
        merged = load_inferred_limits()
        merged.update(inferred)
        global _inferred_cache
        _inferred_cache = merged
        tmp = INFERRED_LIMITS_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(merged, f, ensure_ascii=False, indent=1)
        os.replace(tmp, INFERRED_LIMITS_FILE)
    log.info("数据校验: 输入 %d → 通过 %d | 剔除 %d | 修复 %d | 推断20%%限制 %d | OHLC异常留痕 %d",
             report["n_input"], report["n_clean"], len(report["excluded"]),
             len(report["repaired"]), len(report["inferred_20pct"]),
             len(report["anomaly_bars"]))
    _save_report(report)
    return clean, report


def _discovery_diff(prev: dict, report: dict) -> list[str]:
    """本次校验相对上次的语义变化（新剔除/新修复/新推断）——发现坏数据的判据。

    纯函数（不碰文件）：①剔除集合 ②修复ETF集合 ③推断20%限制集合任一变化
    即视为"发现"。同集合纯增减照报，让清除原因可审计。"""
    def codes(rows) -> set:
        return {r["code"] for r in (rows or []) if isinstance(r, dict) and "code" in r}

    out: list[str] = []
    pe, ce = codes(prev.get("excluded")), codes(report.get("excluded"))
    if pe != ce:
        out.append(f"剔除{len(ce)}只（新增{sorted(ce - pe)[:5]}）")
    pr, cr = set(prev.get("repaired") or []), set(report.get("repaired") or [])
    if pr != cr:
        out.append(f"ETF修复新增{sorted(cr - pr)[:5]}")
    pi, ci = set(prev.get("inferred_20pct") or []), set(report.get("inferred_20pct") or [])
    if pi != ci:
        out.append(f"推断涨跌停新增{sorted(ci - pi)[:5]}")
    return out


def _save_report(report: dict) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp = REPORT_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
    os.replace(tmp, REPORT_FILE)


def load_last_report() -> dict | None:
    """最近一次校验报告（供复盘/日报披露）。"""
    try:
        with open(REPORT_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:  # noqa: BLE001
        return None
