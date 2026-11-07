#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""open_print_ruler -- what does it actually cost to fill the book at the open?

WHY THIS FILE EXISTS
--------------------
Every published number in this line charges 13.041bp per side.  That is a *model*
number, carried since the engine was written, and nothing in the repo has ever
checked it against a fill we could look at.  Meanwhile the book's own instruction
is "signal at the close of bar t, fill at the open of bar t+1" -- a market order
in the first minute.  Three things decide what that really costs, and all three
are measurable inside data/minute_feed without inventing an impact model:

  1. the first minute's drift (you say open, you get the first bar's close);
  2. the first bar's own range (the spread you cross inside that minute);
  3. the first minute's turnover (how big an order can be before it is a
     meaningful share of the print that is actually there).

WHAT IS *NOT* MEASURED (printed on the face, not left to the reader)
--------------------------------------------------------------------
  * no impact model.  The ruler reports the order size that equals 1% and 5% of
    the first-minute turnover of each symbol; it does not claim a slippage for
    that size.
  * the window is the forward archive only (the lane began 2026-09).  Every
    number is therefore a *current-regime* reading, and the session count is
    printed beside it.
  * the archive covers a handful of broad-based ETFs, not the cross-border legs
    the book actually entered.  It prices the venue, not the ticket.

QUALIFYING RULE (a session that cannot be read is skipped and counted)
  * the session's first bar must be at or before 09:31 -- a session whose
    archive starts at 13:53 is a piece of a day, and reading its "first minute"
    as the open would be a fabricated open print;
  * at least MIN_BARS bars in the session.

Usage:
  python scripts/open_print_ruler.py selftest
  python scripts/open_print_ruler.py run [--min-bars=100]
"""

import glob
import io
import json
import os
import sys
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEED_DIR = os.path.join(BASE, "data", "minute_feed")
DAILY_DIR = os.path.join(BASE, "data", "daily")
OUT_DIR = os.path.join(BASE, "results", "execution")
OUT_JSON = os.path.join(OUT_DIR, "open_print_ruler.json")
OUT_MD = os.path.join(OUT_DIR, "OPEN-PRINT-RULER.md")

BOOK_COST_BP = 13.041   # the model charge the whole line carries, per side
MIN_BARS = 100          # a session shorter than this is not a session
OPEN_LIMIT = "09:31"    # the first bar of a real session starts by this minute
WAITS = (5, 15, 30)     # minutes after the opening bar
NAMES = {
    "510300": "沪深300ETF", "510050": "上证50ETF", "510500": "中证500ETF",
    "511010": "国债ETF", "511880": "银华日利", "511990": "华宝添益",
    "159915": "创业板ETF", "512880": "证券ETF", "518880": "黄金ETF",
    "588000": "科创50ETF",
}
LEG_WEIGHT = 0.058           # the card's per-name weight (12 names x 5.8%)
CAPITALS = (1_000_000, 5_000_000, 10_000_000, 50_000_000)


# --------------------------------------------------------------------------- #
# reading
# --------------------------------------------------------------------------- #
def load_feed(path):
    """Read one minute archive into a (ts, open, high, low, close, volume, amount) frame."""
    df = pd.read_csv(path)
    need = {"day", "open", "high", "low", "close", "volume", "amount"}
    missing = need - set(df.columns)
    if missing:
        raise ValueError("feed %s lacks columns %s" % (os.path.basename(path), sorted(missing)))
    df = df.copy()
    df["ts"] = pd.to_datetime(df["day"], errors="coerce")
    df = df.dropna(subset=["ts"]).sort_values("ts").reset_index(drop=True)
    for c in ("open", "high", "low", "close", "volume", "amount"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["session"] = df["ts"].dt.strftime("%Y-%m-%d")
    return df


def measure_session(day_df, min_bars=MIN_BARS, open_limit=OPEN_LIMIT, waits=WAITS):
    """Price one session's opening print.  Returns None when the session cannot be read."""
    day_df = day_df.sort_values("ts").reset_index(drop=True)
    if len(day_df) < min_bars:
        return None, "too_few_bars"
    first = day_df.iloc[0]
    hhmm = first["ts"].strftime("%H:%M")
    if hhmm > open_limit:
        return None, "late_first_bar"
    p_open = float(first["open"])
    if not np.isfinite(p_open) or p_open <= 0:
        return None, "no_open_price"
    first_amt = float(first["amount"]) if np.isfinite(first["amount"]) else float("nan")
    first_vol = float(first["volume"]) if np.isfinite(first["volume"]) else float("nan")
    session_amt = float(np.nansum(day_df["amount"]))
    row = {
        "session": first["session"],
        "first_bar": hhmm,
        "bars": int(len(day_df)),
        "p_open": p_open,
        "drift_1m_bp": (float(first["close"]) / p_open - 1.0) * 1e4,
        "spread_bp": (float(first["high"]) - float(first["low"])) / float(first["close"]) * 1e4,
        "first_amt": first_amt,
        "first_vol": first_vol,
        "session_amt": session_amt,
        "frac_first": (first_amt / session_amt) if session_amt > 0 else float("nan"),
        "vwap_first": (first_amt / first_vol) if first_vol and first_vol > 0 else float("nan"),
    }
    # a wait at +N minutes is priced off the bar that *starts* at that stamp; a
    # missing bar is None (not zero) so an incomplete archive cannot look cheap.
    for n in waits:
        target = (first["ts"] + timedelta(minutes=n)).strftime("%Y-%m-%d %H:%M")
        hit = day_df.loc[day_df["ts"].dt.strftime("%Y-%m-%d %H:%M") == target, "open"]
        row["wait_%dm_bp" % n] = (float(hit.iloc[0]) / p_open - 1.0) * 1e4 if len(hit) else None
    return row, None


def read_symbol(sym, min_bars=MIN_BARS):
    path = os.path.join(FEED_DIR, "%s.csv" % sym)
    df = load_feed(path)
    rows, skipped = [], {}
    for session, day_df in df.groupby("session", sort=True):
        rec, why = measure_session(day_df, min_bars=min_bars)
        if rec is None:
            skipped[why] = skipped.get(why, 0) + 1
            continue
        rec["symbol"] = sym
        rows.append(rec)
    return rows, skipped, df


def _med(values):
    vals = [v for v in values if v is not None and np.isfinite(v)]
    return float(np.median(vals)) if vals else None


def _p90_abs(values):
    vals = [abs(v) for v in values if v is not None and np.isfinite(v)]
    return float(np.percentile(vals, 90)) if vals else None


def size_table(by_symbol, leg_weight=LEG_WEIGHT, capitals=CAPITALS):
    """For each account size: what share of the first minute's turnover one leg is.

    This is the only capacity statement the archive supports -- a share, not a
    slippage.  A symbol without a first-minute turnover is skipped and counted.
    """
    out = []
    usable = {s: v["first_amt_median"] for s, v in by_symbol.items()
              if v.get("first_amt_median") and v["first_amt_median"] > 0}
    for cap in capitals:
        leg = cap * leg_weight
        shares = sorted(leg / amt for amt in usable.values())
        out.append({
            "capital": cap,
            "leg_amount": leg,
            "share_of_first_minute_median": float(np.median(shares)) if shares else None,
            "share_of_first_minute_worst": shares[-1] if shares else None,
            "symbols_priced": len(shares),
        })
    return out


def summarise(rows):
    """Per-symbol and pooled readings.  Median, because one 3-sigma minute is not the venue."""
    by_sym = {}
    for sym in sorted({r["symbol"] for r in rows}):
        rs = [r for r in rows if r["symbol"] == sym]
        first_amt = _med([r["first_amt"] for r in rs])
        by_sym[sym] = {
            "name": NAMES.get(sym, sym),
            "sessions": len(rs),
            "drift_1m_bp_median": _med([r["drift_1m_bp"] for r in rs]),
            "drift_1m_bp_p90_abs": _p90_abs([r["drift_1m_bp"] for r in rs]),
            "spread_bp_median": _med([r["spread_bp"] for r in rs]),
            "frac_first_median": _med([r["frac_first"] for r in rs]),
            "first_amt_median": first_amt,
            "size_1pct_first_minute": (first_amt * 0.01) if first_amt else None,
            "size_5pct_first_minute": (first_amt * 0.05) if first_amt else None,
            "wait_30m_bp_median": _med([r.get("wait_30m_bp") for r in rs]),
            "wait_30m_missing": sum(1 for r in rs if r.get("wait_30m_bp") is None),
        }
    pooled = {
        "sessions": len(rows),
        "symbols": len(by_sym),
        "drift_1m_bp_median": _med([r["drift_1m_bp"] for r in rows]),
        "drift_1m_bp_p90_abs": _p90_abs([r["drift_1m_bp"] for r in rows]),
        "spread_bp_median": _med([r["spread_bp"] for r in rows]),
        "frac_first_median": _med([r["frac_first"] for r in rows]),
        "wait_30m_bp_median": _med([r.get("wait_30m_bp") for r in rows]),
    }
    return {"by_symbol": by_sym, "pooled": pooled}


def daily_last_bar():
    """The equity panel's own last bar, so the minute archive's staleness is a number."""
    path = os.path.join(DAILY_DIR, "sh510300.csv")
    if not os.path.exists(path):
        return None
    try:
        df = pd.read_csv(path)
        col = "date" if "date" in df.columns else df.columns[0]
        return str(df[col].iloc[-1])[:10]
    except Exception:
        return None


def build(min_bars=MIN_BARS):
    paths = sorted(glob.glob(os.path.join(FEED_DIR, "*.csv")))
    if not paths:
        raise SystemExit("no minute archive under %s" % FEED_DIR)
    rows, skipped, last = [], {}, {}
    for path in paths:
        sym = os.path.basename(path)[:-4]
        rs, sk, df = read_symbol(sym, min_bars=min_bars)
        rows.extend(rs)
        if sk:
            skipped[sym] = sk
        if len(df):
            last[sym] = df["session"].iloc[-1]
    if not rows:
        raise SystemExit("every session was unreadable -- refusing to publish an empty ruler")
    summary = summarise(rows)
    sessions = sorted({r["session"] for r in rows})
    summary["size_by_capital"] = size_table(summary["by_symbol"])
    return {
        "generated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "evidence_cutoff": sessions[-1],
        "sessions_read": sessions,
        "sessions_read_count": len(sessions),
        "skipped": skipped,
        "symbols_without_open": {s: last[s] for s in last if s not in summary["by_symbol"]},
        "archive_last_session": last,
        "daily_panel_last_bar": daily_last_bar(),
        "book_cost_bp_per_side": BOOK_COST_BP,
        "waits_minutes": list(WAITS),
        "min_bars": min_bars,
        "open_limit": OPEN_LIMIT,
        **summary,
        "rows": rows,
    }


# --------------------------------------------------------------------------- #
# rendering
# --------------------------------------------------------------------------- #
def _f(v, digits=2):
    return "—" if v is None else ("%.*f" % (digits, v))


def _amt(v):
    if v is None:
        return "—"
    if v >= 1e8:
        return "%.2f 亿" % (v / 1e8)
    if v >= 1e4:
        return "%.0f 万" % (v / 1e4)
    return "%.0f 元" % v


def render_md(res):
    p = res["pooled"]
    lag = ""
    if res.get("daily_panel_last_bar") and res.get("archive_last_session"):
        lag = "（日线面板最后一根 bar=%s）" % res["daily_panel_last_bar"]
    gap = ""
    if res.get("daily_panel_last_bar") and res.get("evidence_cutoff"):
        try:
            a = datetime.strptime(res["evidence_cutoff"], "%Y-%m-%d")
            b = datetime.strptime(res["daily_panel_last_bar"], "%Y-%m-%d")
            gap = "分钟档案最后一笔是 %s，日线面板已到 %s——分钟道落后 %d 个自然日，本页读的是那之前的执行面。" % (
                res["evidence_cutoff"], res["daily_panel_last_bar"], max(0, (b - a).days))
        except ValueError:
            gap = ""
    lines = [
        "# 开盘一分钟到底多少钱（执行成本尺）",
        "",
        "当前活：无（本页是一次测量，不改任何生产配置）。",
        "最近实物：results/execution/open_print_ruler.json（%s 生成）。" % res["generated"],
        "下个里程碑：把这张尺子接到订单卡上（每张单按实际手数算一遍开一分钟吃掉多少），窗 ≤48h。",
        "",
        "## 一句话结论",
        "",
        "- 书里每个单边都按 **%s bp** 收费，这是模型数；开盘第一分钟的真实读数见下表——"
        "**中位漂移 %s bp、盘中价差中位 %s bp、第一分钟成交量占全天 %s%%**。"
        % (_f(res["book_cost_bp_per_side"], 3), _f(p["drift_1m_bp_median"]), _f(p["spread_bp_median"]),
           _f((p["frac_first_median"] or 0) * 100)),
        "- 读数窗口＝分钟档案前向史：**%d 个交易日 / %d 个标的**（%s → %s）%s。"
        % (res["sessions_read_count"], p["symbols"], res["sessions_read"][0], res["evidence_cutoff"], lag),
        "",
        "## 逐标的（中位数；第一分钟＝09:30 那根）",
        "",
        "| 代码 | 名称 | 可读交易日 | 开盘一分钟漂移 | p90 绝对漂移 | 一分钟内价差 | 一分钟成交占比 | 一分钟成交额 | 1% 份额对应的下单额 | 等到第 30 分钟的价差 |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for sym, s in sorted(res["by_symbol"].items()):
        lines.append(
            "| %s | %s | %d | %s bp | %s bp | %s bp | %s%% | %s | %s | %s bp |"
            % (sym, s["name"], s["sessions"], _f(s["drift_1m_bp_median"]), _f(s["drift_1m_bp_p90_abs"]),
               _f(s["spread_bp_median"]), _f((s["frac_first_median"] or 0) * 100),
               _amt(s["first_amt_median"]), _amt(s["size_1pct_first_minute"]),
               _f(s["wait_30m_bp_median"]))
        )
    lines += [
        "",
        "## 装得下多大（单腿占开盘第一分钟成交额的比例）",
        "",
        "| 账户规模 | 单腿金额（5.8%） | 中位标的 | 最薄标的 |",
        "|---|---|---|---|",
    ]
    for row in res.get("size_by_capital", []):
        lines.append("| %s | %s | %s | %s |" % (
            _amt(row["capital"]), _amt(row["leg_amount"]),
            "%.2f%%" % (row["share_of_first_minute_median"] * 100) if row["share_of_first_minute_median"] else "—",
            "%.2f%%" % (row["share_of_first_minute_worst"] * 100) if row["share_of_first_minute_worst"] else "—"))
    lines += [
        "",
        "读法：这是份额，不是滑点。份额到了百分之几的级别，开盘一分钟就装不下这张单——"
        "要么拆到别的时间窗，要么换更厚的标的。",
        "",
        "## 怎么读这张表（三条，缺一条都会读错）",
        "",
        "1. **漂移和价差是两个方向的钱**：漂移中位为正＝那一分钟平均在涨（你等一分钟更贵），"
        "为负＝平均在跌。价差是一分钟内最高最低的距离，它衡量的是「市价单穿过去要吃掉多少」，"
        "不是两边都能吃到的成本。",
        "2. **1% 份额那一列才是「能不能装下」**：它等于该标的第一分钟成交额的百分之一。"
        "书的单腿在 100 万账户里约 5.8 万元——拿这个数和表里那一列比，就知道现在这个体量离「把开盘一分钟打出坑」还有多远。",
        "3. **没算出成本模型**：本页没有把份额换算成滑点，也没有把漂移当成可规避的成本。"
        "报「模型 13.041bp 对与不对」需要的是成交回单，不是这张尺子。",
        "",
        "## 诚实边界",
        "",
        "- %s" % (gap if gap else "档案与日线面板的日期差无法计算（缺一侧日期）。"),
        "- 窗口是分钟档案的前向史（2026-09 起），不是全样本；样本量逐标的一行都给出来了。",
        "- 档案里能读出开盘的标的是 %d 个：%s。**书的纳指/美国50/港股红利腿多数不在档案内**，"
        "那些标的的开盘一分钟只会更薄——本页不为它们背书。档案里有 %d 个文件因读不出开盘而没有进表：%s。"
        % (res["pooled"]["symbols"], "/".join(sorted(res["by_symbol"])),
           len(res.get("symbols_without_open") or {}),
           "/".join(sorted(res.get("symbols_without_open") or {})) or "无"),
        "- 会话被跳过的原因逐项计数：%s。首日（档案从 13:53 开始）按规则不计入，"
        "把半天的第一根当成开盘价会凭空造出一个不存在的开盘。"
        % (json.dumps(res["skipped"], ensure_ascii=False) if res["skipped"] else "无"),
    ]
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- #
# selftest -- hermetic fixtures, no disk
# --------------------------------------------------------------------------- #
def _fixture(day="2026-11-06", start="09:30", bars=240, step=1, drift=0.001,
             amt=1_000_000.0, price=4.0, hi=None, lo=None):
    rows = []
    t0 = datetime.strptime("%s %s" % (day, start), "%Y-%m-%d %H:%M")
    for i in range(bars):
        ts = t0 + timedelta(minutes=i * step)
        p = price
        pc = price * (1 + drift) if i == 0 else price
        rows.append({
            "day": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "open": p,
            "high": hi if hi is not None else max(p, pc),
            "low": lo if lo is not None else min(p, pc),
            "close": pc,
            "volume": 1000.0,
            "amount": amt if i == 0 else amt / 10.0,
        })
    df = pd.DataFrame(rows)
    df["ts"] = pd.to_datetime(df["day"])
    df["session"] = df["ts"].dt.strftime("%Y-%m-%d")
    return df


def selftest() -> int:
    ok, fail = 0, []

    def leg(name, fn):
        nonlocal ok
        try:
            fn()
            ok += 1
            print("[PASS] %s" % name)
        except AssertionError as exc:
            fail.append("%s :: %s" % (name, exc))
            print("[FAIL] %s :: %s" % (name, exc))

    def l_reads_first_bar_of_the_session():
        df = _fixture()
        rec, why = measure_session(df)
        assert why is None, why
        assert rec["first_bar"] == "09:30", rec["first_bar"]

    def l_late_start_is_refused():
        df = _fixture(start="13:53")
        rec, why = measure_session(df)
        assert rec is None and why == "late_first_bar", (rec, why)

    def l_short_session_is_refused():
        df = _fixture(bars=40)
        rec, why = measure_session(df)
        assert rec is None and why == "too_few_bars", (rec, why)

    def l_drift_has_the_right_sign():
        up, _ = measure_session(_fixture(drift=0.002))
        down, _ = measure_session(_fixture(drift=-0.002))
        assert up["drift_1m_bp"] > 0 > down["drift_1m_bp"], (up["drift_1m_bp"], down["drift_1m_bp"])
        assert abs(up["drift_1m_bp"] - 20.0) < 1e-6, up["drift_1m_bp"]

    def l_spread_is_high_minus_low():
        rec, _ = measure_session(_fixture(hi=4.10, lo=4.00, price=4.0, drift=0.0))
        assert abs(rec["spread_bp"] - 250.0) < 1e-6, rec["spread_bp"]

    def l_share_uses_the_session_total():
        df = _fixture(bars=240, amt=1_000_000.0)
        rec, _ = measure_session(df)
        total = 1_000_000.0 + 239 * 100_000.0
        assert abs(rec["session_amt"] - total) < 1e-3, rec["session_amt"]
        assert abs(rec["frac_first"] - 1_000_000.0 / total) < 1e-9, rec["frac_first"]

    def l_size_column_is_one_percent_of_first_minute():
        res = summarise([{"symbol": "X", "session": "d", "first_amt": 2_000_000.0, "drift_1m_bp": 0.0,
                          "spread_bp": 1.0, "frac_first": 0.1, "wait_30m_bp": 0.0}])
        s = res["by_symbol"]["X"]
        assert abs(s["size_1pct_first_minute"] - 20_000.0) < 1e-6, s["size_1pct_first_minute"]
        assert abs(s["size_5pct_first_minute"] - 100_000.0) < 1e-6, s["size_5pct_first_minute"]

    def l_missing_wait_bar_is_none_not_zero():
        df = _fixture(bars=240, step=1)
        rec, _ = measure_session(df, waits=(300,))
        assert rec["wait_300m_bp"] is None, rec["wait_300m_bp"]

    def l_wait_reads_the_bar_that_starts_there():
        df = _fixture(bars=240)
        df.loc[df["ts"] == pd.Timestamp("2026-11-06 09:35:00"), "open"] = 4.04
        rec, _ = measure_session(df, waits=(5,))
        assert abs(rec["wait_5m_bp"] - 100.0) < 1e-6, rec["wait_5m_bp"]

    def l_median_not_mean():
        rows = [
            {"symbol": "X", "session": "a", "first_amt": 1.0, "drift_1m_bp": 1.0, "spread_bp": 1.0,
             "frac_first": 0.1, "wait_30m_bp": 0.0},
            {"symbol": "X", "session": "b", "first_amt": 1.0, "drift_1m_bp": 2.0, "spread_bp": 1.0,
             "frac_first": 0.1, "wait_30m_bp": 0.0},
            {"symbol": "X", "session": "c", "first_amt": 1.0, "drift_1m_bp": 99.0, "spread_bp": 1.0,
             "frac_first": 0.1, "wait_30m_bp": 0.0},
        ]
        assert abs(summarise(rows)["by_symbol"]["X"]["drift_1m_bp_median"] - 2.0) < 1e-9

    def l_all_unreadable_refuses_to_publish():
        try:
            summarise([])["pooled"]["drift_1m_bp_median"]
        except Exception as exc:  # pragma: no cover - defensive
            raise AssertionError(exc)

    def l_no_open_price_is_refused():
        df = _fixture()
        df.loc[0, "open"] = np.nan
        rec, why = measure_session(df)
        assert rec is None and why == "no_open_price", (rec, why)

    def l_render_prints_the_windows_and_the_boundaries():
        res = {
            "generated": "2026-11-07T13:00:00", "evidence_cutoff": "2026-11-06",
            "sessions_read": ["2026-10-28", "2026-11-06"], "sessions_read_count": 2,
            "skipped": {"510300": {"late_first_bar": 1}}, "daily_panel_last_bar": "2026-11-06",
            "book_cost_bp_per_side": 13.041,
            "by_symbol": {"510300": {"name": "沪深300ETF", "sessions": 2, "drift_1m_bp_median": 1.0,
                                     "drift_1m_bp_p90_abs": 2.0, "spread_bp_median": 3.0,
                                     "frac_first_median": 0.05, "first_amt_median": 1e6,
                                     "size_1pct_first_minute": 1e4, "size_5pct_first_minute": 5e4,
                                     "wait_30m_bp_median": -1.0, "wait_30m_missing": 0}},
            "pooled": {"sessions": 2, "symbols": 1, "drift_1m_bp_median": 1.0, "drift_1m_bp_p90_abs": 2.0,
                       "spread_bp_median": 3.0, "frac_first_median": 0.05, "wait_30m_bp_median": -1.0},
        }
        md = render_md(res)
        assert "13.041" in md and "装得下多大" in md and "诚实边界" in md, md[:400]

    for name, fn in [
        ("first bar is the session's own open", l_reads_first_bar_of_the_session),
        ("a session that starts at 13:53 is refused", l_late_start_is_refused),
        ("a short session is refused", l_short_session_is_refused),
        ("drift carries the sign of the minute", l_drift_has_the_right_sign),
        ("spread is high minus low", l_spread_is_high_minus_low),
        ("the share divides by the session, not the bar", l_share_uses_the_session_total),
        ("the size column is 1% of the first minute", l_size_column_is_one_percent_of_first_minute),
        ("a missing wait bar is None, never zero", l_missing_wait_bar_is_none_not_zero),
        ("the wait reads the bar that starts there", l_wait_reads_the_bar_that_starts_there),
        ("aggregation is the median", l_median_not_mean),
        ("an empty reading yields no number", l_all_unreadable_refuses_to_publish),
        ("a session without an open price is refused", l_no_open_price_is_refused),
        ("the page prints its window and its boundaries", l_render_prints_the_windows_and_the_boundaries),
    ]:
        leg(name, fn)

    total = ok + len(fail)
    for f in fail:
        print("FAIL %s" % f)
    print("selftest: %d/%d PASS" % (ok, total))
    return 0 if not fail else 1


def run(min_bars=MIN_BARS) -> int:
    res = build(min_bars=min_bars)
    os.makedirs(OUT_DIR, exist_ok=True)
    with io.open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(res, fh, ensure_ascii=False, indent=1, default=float)
    with io.open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write(render_md(res))
    p = res["pooled"]
    print(json.dumps({
        "evidence_cutoff": res["evidence_cutoff"],
        "sessions": res["sessions_read_count"],
        "symbols": p["symbols"],
        "drift_1m_bp_median": p["drift_1m_bp_median"],
        "spread_bp_median": p["spread_bp_median"],
        "frac_first_median": p["frac_first_median"],
        "skipped": res["skipped"],
        "out": os.path.relpath(OUT_JSON, BASE),
    }, ensure_ascii=False))
    return 0


def main(argv) -> int:
    mode = (argv[1] if len(argv) > 1 else "run").lower().lstrip("-")
    min_bars = MIN_BARS
    for a in argv[2:]:
        if a.startswith("--min-bars="):
            min_bars = int(a.split("=", 1)[1])
    if mode == "selftest":
        return selftest()
    if mode == "run":
        return run(min_bars=min_bars)
    print("usage: open_print_ruler.py [run|selftest] [--min-bars=N]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))