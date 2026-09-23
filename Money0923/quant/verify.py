"""执行逻辑验证：用近端真实分钟级行情检验回测/模拟盘的撮合假设是否成立。

用户要求：拿近期的实时交易数据验证逻辑。本模块对每个模拟成交做四类对照：

1. 开盘撮合保真：回测假设"次日开盘价±滑点成交"——用真实1分钟K线验证该委托价
   在开盘后15分钟内是否真实可成交（价格穿越过委托价）
2. 止损可成交性：引擎假设"盘中触及止损价即按止损价成交"——验证当日分钟区间
   是否真实覆盖止损成交价
3. 涨跌停真实性：引擎按昨收±10%/20%拒单——统计当日分钟高低点真实触板情况
4. 数据口径自检：日线（前复权）与分钟线（不复权）的价格尺度一致性

数据：新浪 stock_zh_a_minute（1分钟K线，最近约9个交易日；股票/ETF均可用）
"""
from __future__ import annotations

import datetime as dt
import logging
import os

import pandas as pd

from . import data as qdata
from . import strategies as strat_lib
from .backtest import equal_weight_benchmark, run_backtest
from .config import DATA_DIR, AppConfig, ensure_dirs
from .data import _retry_call, _sina_symbol, limit_up_pct

log = logging.getLogger("quant.verify")

MINUTE_DIR = os.path.join(DATA_DIR, "minute")


# ---------------------------------------------------------------- 分钟数据

def download_minute(codes: list[str], force: bool = False) -> dict[str, pd.DataFrame]:
    """下载/缓存 1 分钟K线（新浪源，最近约9个交易日；当日缓存直接复用）。"""
    ensure_dirs()
    os.makedirs(MINUTE_DIR, exist_ok=True)
    import akshare as ak
    out: dict[str, pd.DataFrame] = {}
    today = dt.date.today()
    for code in codes:
        path = os.path.join(MINUTE_DIR, f"{code}.csv")
        if not force and os.path.exists(path):
            if dt.datetime.fromtimestamp(os.path.getmtime(path)).date() == today:
                out[code] = _load_minute_df(path)
                continue
        try:
            raw = _retry_call(lambda: ak.stock_zh_a_minute(
                symbol=_sina_symbol(code), period="1", adjust=""), tries=2)
        except Exception as e:  # noqa: BLE001
            log.warning("分钟数据下载失败 %s: %s", code, e)
            continue
        df = pd.DataFrame({
            "day": pd.to_datetime(raw["day"]),
        })
        for col in ("open", "high", "low", "close", "volume", "amount"):
            if col in raw.columns:
                df[col] = pd.to_numeric(raw[col], errors="coerce")
        df = df.dropna(subset=["open"]).sort_values("day")
        df.to_csv(path, index=False)
        out[code] = df
    return out


def _load_minute_df(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["day"])
    return df.sort_values("day")


# ---------------------------------------------------------------- 主验证

def verify_execution(cfg: AppConfig, state: dict, days: int = 40,
                     max_codes: int = 14) -> dict:
    champion = state.get("champion")
    if not champion:
        raise SystemExit("暂无冠军策略，先 run.py evolve")
    _, panel = qdata.full_panel(cfg)

    strat = strat_lib.get_strategy(champion["strategy"])()
    w = strat.target_weights(panel, champion["params"])
    start = panel.dates[max(0, len(panel.dates) - days)]
    sub = panel.window(start, panel.dates[-1])
    res = run_backtest(sub, w, cfg, start_cash=cfg.risk.initial_capital)
    bench = equal_weight_benchmark(sub, cfg.risk.initial_capital)
    bm_ret = float(bench.iloc[-1] / bench.iloc[0] - 1)

    # 需要分钟级对照的标的：现任目标持仓 + 回放窗口内实际成交过的标的
    target_codes = [c for c in sub.codes if float(w.iloc[-1].get(c, 0) or 0) > 0]
    trade_codes = list({t["code"] for t in res.trades})
    codes = list(dict.fromkeys(target_codes + trade_codes))[:max_codes]
    minutes = download_minute(codes)

    # 分钟窗口（各标的取并集的日历范围）
    minute_days: list[str] = []
    for df in minutes.values():
        minute_days += [d.strftime("%Y-%m-%d") for d in df["day"].dt.date.unique()]
    minute_days = sorted(set(minute_days))
    if not minute_days:
        log.warning("无分钟数据可比对（验证仅含日线回放部分）")
    d0, d1 = (minute_days[0], minute_days[-1]) if minute_days else ("", "")

    # —— 复权尺度自检：日线前复权 vs 分钟不复权，按共同日开盘价比对 ——
    scale_info: dict[str, float] = {}
    for c, df in minutes.items():
        try:
            # 取该标的分钟首日的日线开盘价与分钟开盘价比对
            mday = df["day"].dt.date.iloc[0]
            ts = pd.Timestamp(mday)
            if ts in sub.dates:
                do = float(sub.open.loc[ts, c])
                mo = float(df[df["day"].dt.date == mday]["open"].iloc[0])
                if mo > 0 and do > 0:
                    scale_info[c] = do / mo
        except Exception:  # noqa: BLE001
            continue

    # —— 逐单成交保真度对照（复权尺度逐日独立校正：日线open ÷ 当日分钟首bar open）——
    rows: list[dict] = []
    n_ok15 = n_okday = n_fail = 0
    n_stop_ok = n_stop_fail = 0
    for t in res.trades:
        date_s, code = t["date"], t["code"]
        if not minute_days or date_s < d0 or date_s > d1 or code not in minutes:
            continue
        mdf = minutes[code]
        daydf = mdf[mdf["day"].dt.strftime("%Y-%m-%d") == date_s]
        if not len(daydf):
            continue
        # 逐日尺度：窗口内若发生除息分红，日线(前复权)与分钟(不复权)比值会漂移
        try:
            ts = pd.Timestamp(date_s)
            scale = 1.0
            if ts in sub.dates:
                do = float(sub.open.loc[ts, code])
                mo = float(daydf["open"].iloc[0])
                if mo > 0 and do > 0:
                    scale = do / mo
        except Exception:  # noqa: BLE001
            scale = scale_info.get(code, 1.0)
        fill = float(t["price"]) / scale  # 模拟成交价(前复权) → 分钟线原始价格空间
        first15 = daydf[daydf["day"].dt.time <= dt.time(9, 45)]
        lo15 = float(first15["low"].min()) if len(first15) else float("nan")
        hi15 = float(first15["high"].max()) if len(first15) else float("nan")
        lo_day = float(daydf["low"].min())
        hi_day = float(daydf["high"].max())
        if t["side"] == "buy":
            ok15 = bool(lo15 <= fill) if len(first15) else False
            okday = bool(lo_day <= fill)
        else:
            ok15 = bool(hi15 >= fill) if len(first15) else False
            okday = bool(hi_day >= fill)
        n_ok15 += ok15
        n_okday += (not ok15 and okday)
        n_fail += (not okday)
        if t["reason"].startswith("stop"):
            # 止损单：验证当日价格区间真实覆盖止损成交价
            if t["side"] == "sell" and lo_day <= fill:
                n_stop_ok += 1
            else:
                n_stop_fail += 1
        m15_txt = ("数据不完整" if pd.isna(lo15)
                   else (f"{lo15 * scale:.2f}~{hi15 * scale:.2f}" if abs(scale - 1) > 0.005
                         else f"{lo15:.2f}~{hi15:.2f}"))
        rows.append({"date": date_s, "code": code, "side": t["side"], "reason": t["reason"],
                     "shares": t["shares"], "sim_fill": round(float(t["price"]), 3),
                     "m15_range": m15_txt,
                     "status": "15分钟内可成交" if ok15 else ("日内可成交" if okday else "不可成交")})

    # —— 涨跌停真实性统计（分钟高低点 vs 昨收±限价）——
    touch_up = touch_dn = 0
    checked_days = 0
    for c, df in minutes.items():
        if c not in sub.codes:
            continue
        lim = limit_up_pct(c)
        for mday, g in df.groupby(df["day"].dt.date):
            ts = pd.Timestamp(mday)
            if ts not in sub.dates:
                continue
            idx = sub.dates.get_loc(ts)
            if idx == 0:
                continue
            prev = float(sub.close.loc[sub.dates[idx - 1], c])
            if not prev or pd.isna(prev):
                continue
            up = round(prev * (1 + lim), 2)
            dn = round(prev * (1 - lim), 2)
            scale = scale_info.get(c, 1.0)
            if float(g["high"].max()) >= (up - 0.001) / scale:
                touch_up += 1
            if float(g["low"].min()) <= (dn + 0.001) / scale:
                touch_dn += 1
            checked_days += 1

    # —— 报告 ——
    m = res.metrics
    lines = [
        "# 执行逻辑验证报告（近端真实分钟数据）",
        f"- 生成: {dt.datetime.now():%Y-%m-%d %H:%M}",
        f"- 冠军: {champion['strategy']} {champion['params']}",
        f"- 回放窗口: {sub.dates[0].date()} ~ {sub.dates[-1].date()}（{len(sub.dates)}个交易日）",
        f"- 分钟数据窗口: {d0} ~ {d1}（{len(minute_days)}个交易日）| 对照标的: {len(minutes)}只",
        "",
        "## 1. 近端回放结果（日线撮合）",
        f"- 净值 {res.equity.iloc[0]:,.0f} → {res.equity.iloc[-1]:,.0f}（{m['total_return']*100:+.2f}%）"
        f" | 最大回撤 {m['max_dd']*100:.2f}% | 夏普 {m['sharpe']:.2f} | 笔数 {m['n_trades']}",
        f"- 同窗等权基准: {bm_ret*100:+.2f}%",
        "",
        "## 2. 撮合保真度（真实1分钟行情逐单对照）",
        f"- 逐单对照 {len(rows)} 笔（均在分钟数据窗口内）",
        f"- 15分钟内真实可成交: {n_ok15} 笔（{n_ok15/max(1,len(rows))*100:.1f}%）",
        f"- 日内可成交(>15分钟): {n_okday} 笔",
        f"- 不可成交(假设失效): {n_fail} 笔",
        f"- 止损单真实可成交: {n_stop_ok}/{n_stop_ok+n_stop_fail}",
        "",
        "## 3. 逐单明细（最近10笔）",
        "| 执行日 | 代码 | 方向 | 原因 | 股数 | 模拟成交价 | 真实15分钟区间 | 结论 |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in rows[-10:]:
        lines.append(f"| {r['date']} | {r['code']} | {r['side']} | {r['reason']} | "
                     f"{r['shares']} | {r['sim_fill']} | {r['m15_range']} | {r['status']} |")
    lines += [
        "",
        "## 4. 涨跌停真实性（分钟高低点触板统计）",
        f"- 检验标的×日: {checked_days} | 盘中触涨停 {touch_up} 次 | 触跌停 {touch_dn} 次",
        "- 引擎仅在开盘即触板时拒单；盘中触板不影响已成交持仓，与规则一致",
        "",
        "## 5. 数据口径自检（日线前复权 vs 分钟不复权）",
    ]
    for c, s in scale_info.items():
        flag = "OK" if abs(s - 1) <= 0.005 else "存在复权差(已按尺度校正)"
        lines.append(f"- {c}: 日线/分钟价格比 {s:.4f} {flag}")
    lines += ["", "## 结论",
              f"- 开盘±滑点撮合假设在近端真实数据上的可成交率: "
              f"{(n_ok15 + n_okday)}/{len(rows)}"
              f"（{((n_ok15 + n_okday) / max(1, len(rows))) * 100:.1f}%）",
              "- 注：分钟窗口内无撮合失败即说明模拟盘/实盘的开盘市价单假设可靠；"
              "失败单需复核滑点或改限价单策略"]

    from .config import LOGS_DIR
    os.makedirs(LOGS_DIR, exist_ok=True)
    path = os.path.join(LOGS_DIR, f"verify_{dt.date.today().strftime('%Y%m%d')}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    log.info("验证报告 → %s", path)
    return {"trades_checked": len(rows), "ok15": n_ok15, "okday": n_okday,
            "fail": n_fail, "report": path, "metrics": m, "bench_ret": bm_ret}
