#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""etf_premium_face -- what the book pays over NAV to get filled (execution face).

WHY THIS FILE EXISTS
--------------------
The live ETF book holds cross-border legs (513100, 513690, 159501, 159577) whose
price is not pinned to NAV the way a domestic ETF's is: QDII quotas, trading-hour
mismatch and a capped subscription channel let the same basket trade several
percent above or below its own IOPV.  Every one of those percent is paid by the
buyer on entry -- the research record says which basket to hold, and this face
says whether *today* is a day you can actually get into it without handing the
market a slice of the edge.

    for each leg the ticket wants to buy, how far is the price from its IOPV,
    and how much CNY does that premium/discount mean on this ticket's size?

WHAT IT IS NOT
--------------
It is a snapshot face, not a backtest: one print of the ETF spot board, read at
whatever moment the command runs.  IOPV itself is a real-time *estimate* of the
basket (it is not the fund's published NAV), the spot board is intraday until
the close, and no price here is used to change a holding.  The book's rule is
price-based; this face only prices the *entry friction* that rule cannot see.

MODES
-----
  fetch     pull the ETF spot board once, write the snapshot to
            data/etf_premium/snap/<session>.csv, and render the face.
  render    render the face from the newest local snapshot (no network).
  selftest  offline legs over synthetic boards (the gate's own contract).

Bands (frozen): |premium| <= 0.30% is "at par"; <= 1.00% is "watch"; above that
is "stretched" -- a stretched cross-border leg is the case this face exists for.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP_DIR = os.path.join(ROOT, "data", "etf_premium", "snap")
OUT_DIR = os.path.join(ROOT, "results", "etf_premium")
TICKET_DIR = os.path.join(ROOT, "results", "etf_book_order")


def ticket_path():
    """The newest ORDER ticket (the book's own sheet), never the -card twin.

    r1398: the path used to be pinned to one session. On a daily chain that is a
    silent staleness bug -- the face would keep pricing the entry into a book the
    ticket no longer describes, and nothing would say so.
    """
    try:
        names = os.listdir(TICKET_DIR)
    except OSError:
        return None
    cands = [n for n in names
             if n.startswith("TICKET-") and n.endswith(".json") and not n.endswith("-card.json")]
    if not cands:
        return None
    return os.path.join(TICKET_DIR, sorted(cands)[-1])


TICKET_PATH = ticket_path() or os.path.join(TICKET_DIR, "TICKET-2026-11-06.json")

# Frozen bands, percent of IOPV.
PAR_BP = 0.30
WATCH_BP = 1.00
# Cross-section liquidity floor (CNY of session turnover) for the dispersion read.
MIN_AMOUNT = 20_000_000.0
# Execution hurdle: above this many CNY of over-NAV on one ticket the face says so
# out loud. Below it the cost is inside the book's own 8bp/side assumption and a
# warning line would be noise on every quiet day.
OVER_HURDLE_CNY = 500.0

# ---------------------------------------------------------- daily-chain gate
# The face is a SESSION snapshot, so it belongs on the daily chain (S6), not on a
# hand-run. A chain leg that runs every cycle needs three things the hand-run did
# not: it must not photograph an INTRADAY board and call it the close, it must not
# re-pull a session it already captured, and it must not hammer the source after a
# failure. `gate()` is that contract, and it is injectable so the selftest can
# exercise every branch without touching the real calendar or the real snapshots.
GATE_PATH = os.path.join(OUT_DIR, "_fetch_gate.json")
CLOSE_CUTOFF = (15, 30)
RETRY_BACKOFF_MIN = 30

REQUIRED = ["代码", "名称", "最新价", "IOPV实时估值", "成交额", "数据日期"]
# The board publishes a DISCOUNT rate, not a premium: 159981 at price 1.801 over
# IOPV 1.806 prints 基金折价率 = 0.28 -- the number is POSITIVE for a *discount*.
# Reading that column as a premium would invert every band this face prints, so
# it is only a cross-check: the premium is always recomputed from price/IOPV and
# a disagreement between the two is counted and disclosed.
DISCOUNT_COLS = ["基金折价率", "基金折溢价率"]
CROSS_CHECK_TOL_PP = 0.10


def _num(s):
    return pd.to_numeric(s, errors="coerce")


def normalize_spot(df: pd.DataFrame) -> pd.DataFrame:
    """Spot board -> one row per ETF with a numeric premium, NaN kept as NaN.

    A row with no IOPV has NO premium (that is a fact about the row, not a
    zero); the same for a row with no price.  Never fill either with 0.
    """
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError("shape drift: missing columns %s" % ", ".join(missing))
    out = pd.DataFrame({
        "code": df["代码"].astype(str).str.zfill(6),
        "name": df["名称"].astype(str),
        "price": _num(df["最新价"]),
        "iopv": _num(df["IOPV实时估值"]),
        "amount": _num(df["成交额"]),
        "session": df["数据日期"].astype(str),
    })
    both = out["price"].gt(0) & out["iopv"].gt(0)
    out["premium_pct"] = np.nan
    out.loc[both, "premium_pct"] = (out.loc[both, "price"] / out.loc[both, "iopv"] - 1.0) * 100.0

    pub_col = next((c for c in DISCOUNT_COLS if c in df.columns), None)
    if pub_col is not None:
        published = _num(df[pub_col])          # discount: + means below IOPV
        implied = -published                    # what it would mean as a premium
        gap = (out["premium_pct"] - implied).abs()
        out["cross_check_pp"] = gap.round(4)
        out["cross_check_bad"] = gap.gt(CROSS_CHECK_TOL_PP) & out["premium_pct"].notna()
    else:
        out["cross_check_pp"] = np.nan
        out["cross_check_bad"] = False
    return out.reset_index(drop=True)


def normalize_nav_board(df: pd.DataFrame, session: str) -> set:
    """Fund NAV board -> the codes that published a unit NAV ON `session`.

    The board's columns are dated ('2026-11-06-单位净值'); a QDII fund prints
    '---' because its NAV arrives at T+n.  Membership in this set is exactly
    'the IOPV can be checked against a published NAV for this session'.
    """
    code_col = df.columns[0]
    date_cols = [c for c in df.columns if str(c).startswith(session) and "单位净值" in str(c)]
    if not date_cols:
        return set()
    col = date_cols[0]
    ok = set()
    for _, r in df.iterrows():
        v = str(r.get(col, "")).strip()
        if v in ("", "---", "nan", "None", "--"):
            continue
        try:
            float(v)
        except ValueError:
            continue
        ok.add(str(r[code_col]).strip().zfill(6))
    return ok


def band(premium_pct: float) -> str:
    if premium_pct is None or not np.isfinite(premium_pct):
        return "unknown"
    a = abs(premium_pct)
    if a <= PAR_BP:
        return "at-par"
    if a <= WATCH_BP:
        return "watch"
    return "stretched"


def leg_face(ticket: dict, spot: pd.DataFrame, nav_ok=None) -> list[dict]:
    """One row per ordered leg.  A leg the board does not carry is MISSING:
    its premium is None, and the face prints it as unknown rather than free.

    nav_ok = the set of funds that published a SAME-DAY unit NAV.  A QDII /
    cross-border fund publishes its NAV at T+n, so its IOPV is the only number
    on the board and that number is built from a basket whose home market has
    not printed yet -- such a leg is 'unverified', never priced.  Passing None
    disables the distinction (there is then no second source to appeal to).
    """
    by_code = spot.set_index("code")
    rows = []
    for leg in ticket.get("order", []):
        code = str(leg.get("symbol", "")).zfill(6)
        amount = float(leg.get("amount") or 0.0)
        if code in by_code.index:
            r = by_code.loc[code]
            if isinstance(r, pd.DataFrame):
                r = r.iloc[0]
            prem = float(r["premium_pct"]) if np.isfinite(r["premium_pct"]) else None
            unverified = nav_ok is not None and code not in nav_ok
            rows.append({
                "symbol": code,
                "name": str(r["name"]),
                "class": leg.get("class", ""),
                "amount_cny": round(amount, 2),
                "premium_pct": None if prem is None else round(prem, 4),
                "band": "unverified" if unverified else band(prem),
                "trust": "iopv-only" if unverified else "iopv+same-day-nav",
                "over_nav_cny": None if (prem is None or unverified) else round(amount * prem / 100.0, 2),
                "iopv": None if not np.isfinite(r["iopv"]) else round(float(r["iopv"]), 4),
                "price": None if not np.isfinite(r["price"]) else round(float(r["price"]), 4),
            })
        else:
            rows.append({
                "symbol": code,
                "name": "",
                "class": leg.get("class", ""),
                "amount_cny": round(amount, 2),
                "premium_pct": None,
                "band": "missing",
                "trust": "no-quote",
                "over_nav_cny": None,
                "iopv": None,
                "price": None,
            })
    return rows


def dispersion(spot: pd.DataFrame, min_amount: float = MIN_AMOUNT, nav_ok=None) -> dict:
    liq = spot[(spot["amount"] >= min_amount) & spot["premium_pct"].notna()]
    if nav_ok is not None:
        liq = liq[liq["code"].isin(nav_ok)]
    if liq.empty:
        return {"n": 0, "note": "no liquid ETF carries a premium reading today"}
    p = liq["premium_pct"]
    top = liq.sort_values("premium_pct", ascending=False).head(5)
    bot = liq.sort_values("premium_pct").head(5)
    return {
        "n": int(len(liq)),
        "amount_floor_cny": min_amount,
        "median_pct": round(float(p.median()), 4),
        "p10_pct": round(float(p.quantile(0.10)), 4),
        "p90_pct": round(float(p.quantile(0.90)), 4),
        "share_at_par": round(float((p.abs() <= PAR_BP).mean()), 4),
        "share_stretched": round(float((p.abs() > WATCH_BP).mean()), 4),
        "top_premium": [{"symbol": r.code, "name": r["name"], "pct": round(float(r.premium_pct), 4)}
                        for _, r in top.iterrows()],
        "top_discount": [{"symbol": r.code, "name": r["name"], "pct": round(float(r.premium_pct), 4)}
                         for _, r in bot.iterrows()],
    }


def render_md(face: dict) -> str:
    L = []
    L.append("# 执行溢价面 · %s" % face["session"])
    L.append("")
    src = face["source"]
    L.append("快照口径：ETF 现货板一次读取（%s），IOPV=实时估值不是公布净值；"
             "读数随盘中变动，收盘后才等于当日最终值。" % src.get("fetched_at", ""))
    L.append("")
    legs = face["legs"]
    if legs:
        L.append("## 本单入场摩擦（书要买的每一腿）")
        L.append("")
        L.append("| 代码 | 名称 | 类别 | 计划金额 | IOPV 溢价% | 档位 | 相对净值多付(CNY) |")
        L.append("|---|---|---|---|---|---|---|")
        for r in legs:
            prem = "—" if r["premium_pct"] is None else "%+.3f" % r["premium_pct"]
            over = "—" if r["over_nav_cny"] is None else format(r["over_nav_cny"], "+,.0f")
            L.append("| %s | %s | %s | %s | %s | %s | %s |" % (
                r["symbol"], r["name"] or "(板面未列)", r["class"],
                format(r["amount_cny"], ",.0f"),
                prem, r["band"], over))
        L.append("")
        tot = sum(r["over_nav_cny"] for r in legs if r["over_nav_cny"] is not None)
        known = sum(r["amount_cny"] for r in legs if r["over_nav_cny"] is not None)
        unk = [r["symbol"] for r in legs if r["over_nav_cny"] is None]
        L.append("**合计：在已知 %s 的计划金额上，相对净值 %s 元**（正数=买入即在溢价上多付）。"
                 % (format(known, ",.0f"), format(tot, "+,.0f")))
        if unk:
            L.append("")
            L.append("未定价腿：%s（板面没有它的读数，或它没有当日公布净值可对——按「不知道」记，不按 0 记）。"
                     % "、".join(unk))
        L.append("")
        oh = face.get("over_hurdle") or {}
        if oh:
            if oh.get("breached"):
                L.append("**执行闸：本单可核对腿合计多付 %s 元 > 阈值 %s 元"
                         "（占可核对计划金额的 %.4f%%）——买进即先把这笔交给溢价；"
                         "可等溢价回落、或换贴水腿。**"
                         % (format(oh["total_over_nav_cny"], ",.0f"),
                            format(oh["hurdle_cny"], ",.0f"),
                            oh.get("share_of_plan_pct") or 0.0))
            else:
                L.append("执行闸：可核对腿合计多付 %s 元，未超阈值 %s 元，不提示。"
                         % (format(oh.get("total_over_nav_cny") or 0.0, ",.0f"),
                            format(oh.get("hurdle_cny") or 0.0, ",.0f")))
            L.append("")
    disp = face["dispersion"]
    L.append("## 全市场溢价分布（只用当日有公布净值的 %d 只，成交额 ≥ %s）"
             % (disp.get("n", 0), format(MIN_AMOUNT, ",.0f")))
    L.append("")
    if disp.get("n"):
        L.append("- 中位 %+.3f%%，p10 %+.3f%%，p90 %+.3f%%" % (
            disp["median_pct"], disp["p10_pct"], disp["p90_pct"]))
        L.append("- 贴水/溢价在 ±%.2f%% 以内的占 %.1f%%，偏离超过 %.2f%% 的占 %.1f%%" % (
            PAR_BP, disp["share_at_par"] * 100, WATCH_BP, disp["share_stretched"] * 100))
        L.append("- 溢价最高：" + "、".join("%s %s %+.2f%%" % (t["symbol"], t["name"], t["pct"])
                                           for t in disp["top_premium"]))
        L.append("- 折价最深：" + "、".join("%s %s %+.2f%%" % (t["symbol"], t["name"], t["pct"])
                                           for t in disp["top_discount"]))
    else:
        L.append("- %s" % disp.get("note", ""))
    L.append("")
    cc = face.get("cross_check") or {}
    if cc:
        L.append("## 口径核对：板面「折价率」列 vs 用 价格/IOPV 重算")
        L.append("")
        L.append("- 可比 %d 行，分歧 %d 行（阈值 %.2f 个百分点）——**板面那一列是折价率，符号与溢价相反**，"
                 "本面一律用价格/IOPV 重算，分歧只数不平均。" % (
                     cc.get("compared_rows", 0), cc.get("disagreeing_rows", 0), cc.get("tolerance_pp", 0)))
        L.append("")
    L.append("## 诚实边界")
    L.append("")
    for c in face["caveats"]:
        L.append("- %s" % c)
    L.append("")
    return "\n".join(L)


def build_face(spot: pd.DataFrame, ticket: dict, fetched_at: str, nav_ok=None) -> dict:
    sessions = sorted(set(spot["session"].dropna()))
    session = sessions[-1] if sessions else "unknown"
    bad = int(spot["cross_check_bad"].sum()) if "cross_check_bad" in spot.columns else 0
    checked = int(spot["cross_check_pp"].notna().sum()) if "cross_check_pp" in spot.columns else 0
    # The book's ticket nests its legs under "ticket"; a bare order list is also
    # accepted so this face can be pointed at any ticket-shaped file.
    inner = ticket.get("ticket") if isinstance(ticket.get("ticket"), dict) else ticket
    legs = leg_face(inner, spot, nav_ok)
    # The hurdle is summed over PRICED legs only: an unverified leg has no CNY figure
    # and is excluded rather than counted as zero, so a ticket made mostly of unverified
    # cross-border legs cannot look cheap.
    priced = [r for r in legs if r["over_nav_cny"] is not None]
    tot = sum(r["over_nav_cny"] for r in priced)
    known = sum(r["amount_cny"] for r in priced)
    over_hurdle = {
        "hurdle_cny": OVER_HURDLE_CNY,
        "total_over_nav_cny": round(tot, 2),
        "priced_amount_cny": round(known, 2),
        "share_of_plan_pct": round(100.0 * tot / known, 4) if known else None,
        "breached": bool(tot > OVER_HURDLE_CNY),
        "basis": "sum over priced legs only; unverified legs carry no CNY figure and are excluded, never counted as zero",
    }
    return {
        "artifact": "etf_premium_face",
        "machine": "bm-c",
        "session": session,
        "source": {"view": "ETF spot board (eastmoney via akshare fund_etf_spot_em)",
                   "fetched_at": fetched_at,
                   "rows": int(len(spot)),
                   "nav_board": "same-day unit NAV board (fund_etf_fund_daily_em) used as the second source" if nav_ok is not None else "not read -- every premium is IOPV-only"},
        "cross_check": {"basis": "premium recomputed from price/IOPV; the board's own 折价率 column is only compared",
                        "compared_rows": checked,
                        "disagreeing_rows": bad,
                        "tolerance_pp": CROSS_CHECK_TOL_PP},
        "ticket": {"path": os.path.relpath(TICKET_PATH, ROOT).replace("\\", "/"),
                   "bar": inner.get("book_decided_at") or ticket.get("book_decided_at") or ticket.get("evidence_cutoff")},
        "bands": {"par_pct": PAR_BP, "watch_pct": WATCH_BP},
        "legs": legs,
        "priced_legs": sum(1 for r in legs if r["over_nav_cny"] is not None),
        "unverified_legs": sum(1 for r in legs if r["band"] == "unverified"),
        "over_hurdle": over_hurdle,
        "dispersion": dispersion(spot, nav_ok=nav_ok),
        "caveats": [
            "IOPV is a real-time estimate of the basket, not the fund's published NAV; a premium measured against it inherits that error.",
            "the spot board publishes 折价率 (discount), the opposite sign of a premium -- this face recomputes from price/IOPV and reports any disagreement instead of choosing a side.",
            "a cross-border leg publishes its NAV at T+n, so on the session itself its IOPV cannot be checked against anything. Those legs are marked unverified and carry NO CNY figure: an IOPV that has drifted from the basket looks exactly like a real premium from one snapshot.",
            "the board is read at one moment: before the close these numbers move, and cross-border legs are the ones that move most (their underlying trades in another timezone).",
            "a positive premium is a cost only to a buyer; it is income to a seller. This face says nothing about which side the book will be on tomorrow.",
            "no historical premium series is long enough to build a percentile gate from: this face runs once per session on the daily chain from 2026-11-06, so a 'is today's premium high for this leg' reading has to wait for the series to accumulate.",
        ],
    }


def _snap_path(session: str) -> str:
    return os.path.join(SNAP_DIR, "%s.csv" % session)


def _read_gate():
    try:
        with open(GATE_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _write_gate(d):
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = GATE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    os.replace(tmp, GATE_PATH)


def _trading_days():
    """The official calendar, or None. None means 'unreadable', never 'holiday'."""
    try:
        if ROOT not in sys.path:
            sys.path.insert(0, ROOT)
        from scripts import exchange_calendar_audit as CA
        return CA.load_calendar()
    except Exception:  # noqa: BLE001 -- see docstring: unreadable is not a verdict
        return None


_AUTO = object()   # sentinel: "read the calendar yourself"; an explicit None is 'unreadable'


def gate(now=None, force=False, days=_AUTO, snap_exists=None, gate_state=None):
    """May `fetch` hit the source right now? -> (run, session, reason).

    Every input is injectable so the selftest can drive the clock, the calendar and
    the on-disk state explicitly instead of depending on the day it runs. `days` is
    _AUTO by default (read the file), None passes through as 'calendar unreadable'.
    """
    import datetime as _dt
    now = now or _dt.datetime.now()
    today = now.date().isoformat()
    if force:
        return True, today, "forced"
    if days is _AUTO:
        days = _trading_days()
    if days is None:
        return False, today, "official calendar unreadable -- refusing to guess a session"
    if today not in days:
        return False, today, "not a trading session (%s)" % today
    if (now.hour, now.minute) < CLOSE_CUTOFF:
        return False, today, "before the 15:30 close -- an intraday board is not the session"
    if snap_exists is None:
        snap_exists = os.path.exists(_snap_path(today)) and os.path.getsize(_snap_path(today)) > 0
    if snap_exists:
        return False, today, "session %s already captured" % today
    g = gate_state if gate_state is not None else _read_gate()
    ts = g.get("last_fail_ts")
    if g.get("last_fail_session") == today and ts:
        try:
            age = (now - _dt.datetime.fromisoformat(ts)).total_seconds() / 60.0
        except (TypeError, ValueError):
            age = None
        if age is not None and age < RETRY_BACKOFF_MIN:
            return False, today, "backoff %.0f/%.0f min after a failed attempt" % (age, RETRY_BACKOFF_MIN)
    return True, today, "armed"


def board_gap(now=None, days=_AUTO, snap_dir=None):
    """Which trading sessions the IOPV board holds, and which are gone for good.

    The board is a REALTIME print: `fetch` reads the session's spot board after the
    close and files it under that session. A session with no file is therefore not
    "late" -- re-running the lane tomorrow photographs tomorrow, not yesterday. That
    makes this the one face in the chain whose holes do not heal, which is why a
    consumer has to be told the hole instead of assuming a merely old file (contrast
    the daily bar panels: any later run backfills them).

    Coverage starts at the first board on disk -- sessions before it are NOT counted
    as holes, because nothing ever claimed to cover them. An unreadable calendar
    returns `missing=None` (unknown), never an empty list.
    """
    import datetime as _dt
    now = now or _dt.datetime.now()
    today = now.date().isoformat()
    if days is _AUTO:
        days = _trading_days()
    snap_dir = snap_dir or SNAP_DIR
    present = []
    try:
        names = os.listdir(snap_dir)
    except OSError:
        names = []
    for fn in names:
        if not fn.endswith(".csv"):
            continue
        stem = fn[:-4]
        try:
            _dt.date.fromisoformat(stem)
        except ValueError:
            continue
        try:
            if os.path.getsize(os.path.join(snap_dir, fn)) <= 0:
                continue
        except OSError:
            continue
        present.append(stem)
    present = sorted(set(present))
    before_close = (now.hour, now.minute) < CLOSE_CUTOFF
    out = {"status": "ok", "boards_present": present, "n_boards": len(present),
           "first_board": present[0] if present else None,
           "last_board": present[-1] if present else None,
           "coverage_starts": present[0] if present else None,
           "sessions_expected": [], "missing": [], "n_missing": 0,
           "recoverable": False,
           "why_unrecoverable": "the board is a realtime print taken after the close, so a "
                                "rerun photographs the session it runs in, not the one it missed",
           "next_capture_session": None, "next_capture_after": None,
           "clock": now.isoformat(timespec="minutes")}
    if days is None:
        out["status"] = "unreadable_calendar"
        out["sessions_expected"] = None
        out["missing"] = None
        out["n_missing"] = None
        out["next_capture_session"] = today
        out["next_capture_after"] = "15:30" if before_close else None
        return out
    days = set(days)
    closable = [d for d in days if d < today or (d == today and not before_close)]
    last_closable = max(closable) if closable else None
    if present and last_closable:
        expected = sorted(d for d in days if present[0] <= d <= last_closable)
        have = set(present)
        out["sessions_expected"] = expected
        out["missing"] = [d for d in expected if d not in have]
        out["n_missing"] = len(out["missing"])
    if today in days and before_close:
        out["next_capture_session"] = today
        out["next_capture_after"] = "15:30"
    elif today in days and today not in set(present):
        out["next_capture_session"] = today
    else:
        later = sorted(d for d in days if d > today)
        out["next_capture_session"] = later[0] if later else None
        out["next_capture_after"] = "15:30"
    return out


def do_fetch(force=False) -> int:
    import time as _t
    run, today, why = gate(force=force)
    if not run:
        print("fetch: no-op -- %s" % why)
        return 0
    try:
        import akshare as ak
        df = ak.fund_etf_spot_em()
    except Exception as e:  # noqa: BLE001 -- source failure is a reading, not a crash
        print("source failure: %s: %s" % (type(e).__name__, e))
        g = _read_gate()
        g.update({"last_fail_session": today,
                  "last_fail_ts": _t.strftime("%Y-%m-%dT%H:%M:%S"),
                  "last_fail_reason": "%s: %s" % (type(e).__name__, e)})
        _write_gate(g)
        return 2
    try:
        spot = normalize_spot(df)
    except ValueError as e:
        print(str(e))
        return 3
    session = sorted(set(spot["session"].dropna()))[-1]
    if session < today:
        # The board has not rolled to today's close yet: writing this snapshot under
        # today's name would freeze yesterday's tape as today's session.
        print("fetch: no-op -- board still reports %s, not %s" % (session, today))
        return 0
    os.makedirs(SNAP_DIR, exist_ok=True)
    path = _snap_path(session)
    tmp = path + ".tmp"
    spot.to_csv(tmp, index=False, encoding="utf-8")
    os.replace(tmp, path)
    print("snapshot: %s (%d rows, session %s)" % (os.path.relpath(path, ROOT), len(spot), session))
    nav_ok = fetch_nav_ok(session)
    _save_nav_ok(session, nav_ok)
    g = _read_gate()
    g.pop("last_fail_session", None)
    g.pop("last_fail_ts", None)
    g.pop("last_fail_reason", None)
    g["last_ok_session"] = session
    g["last_ok_ts"] = _t.strftime("%Y-%m-%dT%H:%M:%S")
    _write_gate(g)
    return _render(spot, _t.strftime("%Y-%m-%dT%H:%M:%S%z"), nav_ok)


def fetch_nav_ok(session: str):
    """Second source: which funds published a unit NAV on `session`.

    Failure to read it is not a reason to invent a number -- it downgrades the
    whole face to IOPV-only (nav_ok=None), which the face then says out loud.
    """
    try:
        import akshare as ak
        df = ak.fund_etf_fund_daily_em()
    except Exception as e:  # noqa: BLE001
        print("nav board unavailable (%s: %s) -- every premium is IOPV-only" % (type(e).__name__, e))
        return None
    ok = normalize_nav_board(df, session)
    if not ok:
        print("nav board carries no %s unit NAV -- every premium is IOPV-only" % session)
        return None
    print("nav board: %d funds published a unit NAV for %s" % (len(ok), session))
    return ok


def _nav_ok_path(session: str) -> str:
    return os.path.join(SNAP_DIR, "%s.navok.json" % session)


def _save_nav_ok(session: str, ok) -> None:
    with open(_nav_ok_path(session), "w", encoding="utf-8") as f:
        json.dump({"session": session, "codes": sorted(ok) if ok else None}, f, ensure_ascii=False)


def _cached_nav_ok(session: str):
    p = _nav_ok_path(session)
    if not os.path.exists(p):
        return None
    try:
        with open(p, encoding="utf-8") as f:
            codes = json.load(f).get("codes")
    except (OSError, ValueError):
        return None
    return set(codes) if codes else None


def _load_snapshot() -> pd.DataFrame | None:
    if not os.path.isdir(SNAP_DIR):
        return None
    files = sorted(f for f in os.listdir(SNAP_DIR) if f.endswith(".csv"))
    if not files:
        return None
    return pd.read_csv(os.path.join(SNAP_DIR, files[-1]), dtype={"code": str, "session": str},
                       keep_default_na=True).assign(code=lambda d: d["code"].str.zfill(6))


def _render(spot: pd.DataFrame, fetched_at: str, nav_ok=None) -> int:
    try:
        with open(TICKET_PATH, encoding="utf-8") as f:
            ticket = json.load(f)
    except (OSError, ValueError) as e:
        print("ticket unreadable: %s" % e)
        return 2
    face = build_face(spot, ticket, fetched_at, nav_ok)
    os.makedirs(OUT_DIR, exist_ok=True)
    js = os.path.join(OUT_DIR, "PREMIUM-%s.json" % face["session"])
    md = os.path.join(OUT_DIR, "PREMIUM-%s.md" % face["session"])
    with open(js, "w", encoding="utf-8") as f:
        json.dump(face, f, ensure_ascii=False, indent=1)
    with open(md, "w", encoding="utf-8") as f:
        f.write(render_md(face))
    print("face: %s" % os.path.relpath(md, ROOT).replace("\\", "/"))
    for r in face["legs"]:
        prem = "unknown" if r["premium_pct"] is None else "%+.3f%%" % r["premium_pct"]
        print("  %s %-14s %10s %8s  %s" % (r["symbol"], r["name"][:12], format(r["amount_cny"], ",.0f"), prem, r["band"]))
    return 0


def _published_fetched_at(session: str):
    """Keep the original capture stamp when re-rendering a published session.

    A re-render after a code change (a new section, a new field) must not rewrite the
    provenance of a snapshot that was taken at a different moment -- 'local:<day>' is
    the fallback for a session that was never fetched by this tool.
    """
    p = os.path.join(OUT_DIR, "PREMIUM-%s.json" % session)
    try:
        with open(p, encoding="utf-8") as f:
            return (json.load(f).get("source") or {}).get("fetched_at")
    except (OSError, ValueError):
        return None


def do_render() -> int:
    spot = _load_snapshot()
    if spot is None:
        print("no local snapshot; run `fetch` first")
        return 2
    session = str(spot["session"].dropna().iloc[-1])
    print("rendering from local snapshot %s (no network)" % session)
    return _render(spot, _published_fetched_at(session) or "local:%s" % session,
                   _cached_nav_ok(session))


# ---------------------------------------------------------------- selftest

def selftest() -> int:
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    def board(rows, disc=None):
        df = pd.DataFrame(rows, columns=REQUIRED)
        if disc is not None:
            df["基金折价率"] = disc
        return df

    # L1 premium sign: price above IOPV is a positive premium.
    b = board([["510300", "沪深300ETF", 4.04, 4.00, 9e8, "2026-11-06"]])
    s = normalize_spot(b)
    leg("L1 price above IOPV reads as a positive premium", abs(s.loc[0, "premium_pct"] - 1.0) < 1e-9)

    # L2 a row with no IOPV has no premium -- NaN, never 0.
    b = board([["510300", "x", 4.04, np.nan, 9e8, "2026-11-06"]])
    s = normalize_spot(b)
    leg("L2 no IOPV -> NaN premium (not zero)", np.isnan(s.loc[0, "premium_pct"]))

    # L3 THE inversion leg: the board publishes a DISCOUNT rate, so a printed
    # +0.28 beside price 1.801 / IOPV 1.806 (a real 159981 row) is a DISCOUNT.
    # A reader that trusted the column would call it a premium and flip the band.
    b = board([["159981", "能源化工ETF建信", 1.801, 1.806, 1.4e9, "2026-11-06"]], disc=[0.28])
    s = normalize_spot(b)
    leg("L3 published 折价率 +0.28 reads as a -0.28% premium (never +0.28)",
        -0.35 < s.loc[0, "premium_pct"] < -0.20 and band(float(s.loc[0, "premium_pct"])) == "at-par")

    # L4 shape gate rejects a board missing a column.
    bad = pd.DataFrame([["510300", "x"]], columns=["代码", "名称"])
    try:
        normalize_spot(bad)
        ok = False
    except ValueError:
        ok = True
    leg("L4 shape drift (missing column) raises instead of guessing", ok)

    # L5 band edges.
    leg("L5 bands: 0.30 at-par / 1.00 watch / above stretched",
        band(0.30) == "at-par" and band(-0.99) == "watch" and band(1.01) == "stretched"
        and band(None) == "unknown")

    # L6 a leg the board does not carry is MISSING, not free.
    s = normalize_spot(board([["510300", "沪深300ETF", 4.04, 4.00, 9e8, "2026-11-06"]]))
    rows = leg_face({"order": [{"symbol": "513100", "amount": 100000.0, "class": "crossborder"}]}, s)
    leg("L6 unknown leg -> band=missing and no CNY figure", rows[0]["band"] == "missing"
        and rows[0]["over_nav_cny"] is None and rows[0]["premium_pct"] is None)

    # L7 CNY figure is signed against the ticket size.
    rows = leg_face({"order": [{"symbol": "510300", "amount": 100000.0, "class": "equity"}]}, s)
    leg("L7 over-NAV CNY scales with the ticket and keeps the sign",
        abs(rows[0]["over_nav_cny"] - 1000.0) < 1e-6)

    # L8 dispersion ignores names below the liquidity floor.
    b = board([["510300", "big", 4.04, 4.00, 9e8, "2026-11-06"],
               ["159999", "thin", 1.5, 1.4, 1e6, "2026-11-06"]])
    d = dispersion(normalize_spot(b))
    leg("L8 illiquid names stay out of the cross-section", d["n"] == 1 and d["median_pct"] == 1.0)

    # L9 top premium / top discount are opposite ends of the same set.
    b = board([["510300", "a", 4.04, 4.0, 9e8, "2026-11-06"],
               ["510050", "b", 2.0, 2.1, 9e8, "2026-11-06"],
               ["510500", "c", 6.0, 6.0, 9e8, "2026-11-06"]])
    d = dispersion(normalize_spot(b))
    leg("L9 extremes come from opposite sorts",
        d["top_premium"][0]["symbol"] == "510300" and d["top_discount"][0]["symbol"] == "510050")

    # L10 the renderer never crashes on an empty ticket and still prints its header.
    face = build_face(s, {"order": []}, "t:0")
    md = render_md(face)
    leg("L10 empty ticket still renders a one-pager", md.startswith("# 执行溢价面") and "诚实边界" in md)

    # L11 determinism: same board in -> same bytes out (no wall clock inside).
    f1 = build_face(s, {"order": []}, "t:0")
    f2 = build_face(s.copy(), {"order": []}, "t:0")
    leg("L11 face is deterministic for the same board", json.dumps(f1, sort_keys=True) == json.dumps(f2, sort_keys=True))

    # L12 a row whose IOPV is <= 0 must not produce a premium (guard division by zero).
    b = board([["510300", "x", 4.04, 0.0, 9e8, "2026-11-06"]])
    s2 = normalize_spot(b)
    leg("L12 IOPV<=0 -> NaN, no division", np.isnan(s2.loc[0, "premium_pct"]))

    # L13 cross-check counts a disagreement instead of silently preferring a side.
    b = board([["510300", "x", 4.04, 4.00, 9e8, "2026-11-06"]], disc=[1.0])
    s2 = normalize_spot(b)
    leg("L13 a board that disagrees with price/IOPV is counted, not averaged",
        bool(s2.loc[0, "cross_check_bad"]) and abs(s2.loc[0, "premium_pct"] - 1.0) < 1e-9)

    # L14 the table path itself renders (L10 only proves the empty case): a face
    # with one priced leg and one missing leg must print both rows.
    face = build_face(s, {"order": [{"symbol": "510300", "amount": 100000.0, "class": "equity"},
                                    {"symbol": "513100", "amount": 50000.0, "class": "crossborder"}]}, "t:0")
    md = render_md(face)
    leg("L14 ticket table renders priced and missing legs",
        "510300" in md and "513100" in md and "未定价腿" in md)

    # L15 the NAV board's dated column decides membership: '---' is NOT a NAV.
    nb = pd.DataFrame([["510300", "沪深300ETF", "4.1312", "4.12"],
                       ["513100", "纳指ETF国泰", "---", "---"]],
                      columns=["基金代码", "基金简称", "2026-11-06-单位净值", "2026-11-05-单位净值"])
    ok_set = normalize_nav_board(nb, "2026-11-06")
    leg("L15 NAV board: a fund that printed '---' is not 'has a NAV'",
        ok_set == {"510300"} and normalize_nav_board(nb, "2026-11-07") == set())

    # L16 with the second source in hand, an uncheckable leg is UNVERIFIED:
    # it keeps its raw IOPV reading but must not be priced in CNY.
    s3 = normalize_spot(board([["513100", "纳指ETF国泰", 2.158, 1.7797, 4e8, "2026-11-06"],
                               ["510300", "沪深300ETF", 4.124, 4.1349, 9e8, "2026-11-06"]]))
    rows = leg_face({"order": [{"symbol": "513100", "amount": 90000.0, "class": "crossborder"},
                               {"symbol": "510300", "amount": 90000.0, "class": "equity"}]}, s3, {"510300"})
    leg("L16 unverifiable leg is unverified, not 'stretched' and not priced",
        rows[0]["band"] == "unverified" and rows[0]["over_nav_cny"] is None
        and abs(rows[0]["premium_pct"] - 21.2564) < 1e-3
        and rows[1]["band"] != "unverified" and rows[1]["over_nav_cny"] is not None)

    # ---- the daily-chain gate (r1398). This face moved from a hand-run to an S6
    # leg, so the gate is now load-bearing: a wrong branch either photographs an
    # intraday board as the close, or re-pulls a captured session every cycle.
    import datetime as _dt
    DAYS = {"2026-11-06", "2026-11-09"}
    after_open = _dt.datetime(2026, 11, 9, 15, 45)
    before_close = _dt.datetime(2026, 11, 9, 11, 0)

    # L17 a non-trading day never fires.
    r = gate(now=_dt.datetime(2026, 11, 7, 16, 0), days=DAYS, snap_exists=False, gate_state={})
    leg("L17 weekend is a no-op, not an empty snapshot",
        r[0] is False and "not a trading session" in r[2])

    # L18 the close is the boundary: 11:00 is refused, 15:45 runs, --force overrides.
    r_before = gate(now=before_close, days=DAYS, snap_exists=False, gate_state={})
    r_after = gate(now=after_open, days=DAYS, snap_exists=False, gate_state={})
    r_forced = gate(now=before_close, force=True, days=DAYS, snap_exists=False, gate_state={})
    leg("L18 before 15:30 refused, after it armed, --force overrides the clock",
        r_before[0] is False and "before the 15:30 close" in r_before[2]
        and r_after[0] is True and r_forced[0] is True)

    # L19 a captured session is not re-pulled (the chain runs many times a day).
    r = gate(now=after_open, days=DAYS, snap_exists=True, gate_state={})
    leg("L19 an already captured session is a no-op",
        r[0] is False and "already captured" in r[2])

    # L20 a failed attempt backs the source off for 30 minutes, then re-arms.
    fail_state = {"last_fail_session": "2026-11-09", "last_fail_ts": "2026-11-09T15:40:00"}
    r_soon = gate(now=_dt.datetime(2026, 11, 9, 15, 50), days=DAYS, snap_exists=False,
                  gate_state=fail_state)
    r_late = gate(now=_dt.datetime(2026, 11, 9, 16, 20), days=DAYS, snap_exists=False,
                  gate_state=fail_state)
    leg("L20 30-minute backoff after a failure, and only for the same session",
        r_soon[0] is False and "backoff" in r_soon[2] and r_late[0] is True
        and gate(now=after_open, days=DAYS, snap_exists=False,
                 gate_state={"last_fail_session": "2026-11-06",
                             "last_fail_ts": "2026-11-06T15:40:00"})[0] is True)

    # L21 an unreadable calendar is NOT a holiday: refusing to run is the honest
    # branch, because guessing gives us a snapshot with a name we invented.
    r = gate(now=after_open, days=None, snap_exists=False, gate_state={})
    leg("L21 unreadable calendar refuses instead of guessing a session",
        r[0] is False and "unreadable" in r[2] and gate(now=after_open, force=True)[0] is True)

    # L22 a board still carrying an older session must not be filed under today.
    # (The branch lives in do_fetch, so this leg pins the comparison itself.)
    leg("L22 a stale board day sorts below today and is skipped",
        "2026-11-06" < "2026-11-09" and not ("2026-11-07" >= "2026-11-09"))

    # L23 the hurdle sums PRICED legs only. One leg at +1% on 1,000,000 = +10,000 CNY
    # breaches; the same ticket with an unverified leg of equal size does NOT get to
    # count that leg as zero-and-therefore-cheap -- the priced basis is unchanged.
    s4 = normalize_spot(board([["510300", "沪深300ETF", 4.04, 4.00, 9e8, "2026-11-06"],
                               ["513100", "纳指ETF国泰", 2.158, 1.7797, 4e8, "2026-11-06"]]))
    f_hit = build_face(s4, {"order": [{"symbol": "510300", "amount": 1_000_000.0, "class": "equity"}]}, "t:0")
    f_mixed = build_face(s4, {"order": [{"symbol": "510300", "amount": 1_000_000.0, "class": "equity"},
                                        {"symbol": "513100", "amount": 1_000_000.0, "class": "crossborder"}]},
                         "t:0", {"510300"})
    leg("L23 hurdle sums priced legs only and never counts unverified as zero",
        f_hit["over_hurdle"]["breached"] is True
        and abs(f_hit["over_hurdle"]["total_over_nav_cny"] - 10_000.0) < 1e-6
        and f_mixed["over_hurdle"]["total_over_nav_cny"] == 10_000.0
        and f_mixed["over_hurdle"]["priced_amount_cny"] == 1_000_000.0
        and f_mixed["unverified_legs"] == 1)

    # L24 a small premium on a small ticket is under the hurdle and says so, in the
    # renderer, not only in the JSON (the operator reads the page, not the file).
    f_low = build_face(normalize_spot(board([["510300", "x", 4.005, 4.00, 9e8, "2026-11-06"]])),
                       {"order": [{"symbol": "510300", "amount": 10_000.0, "class": "equity"}]}, "t:0")
    md = render_md(f_low)
    leg("L24 under the hurdle the page prints the figure instead of a warning",
        f_low["over_hurdle"]["breached"] is False and abs(f_low["over_hurdle"]["total_over_nav_cny"] - 12.5) < 1e-6
        and "执行闸" in md and "不提示" in md)

    # ---- board gaps (r1505). This board is the one face in the chain whose holes
    # cannot be healed by running the lane again, so naming them is load-bearing.
    import tempfile
    tmp = tempfile.mkdtemp(prefix="epf_gap_")
    for d in ("2026-11-05", "2026-11-06"):
        with open(os.path.join(tmp, "%s.csv" % d), "w", encoding="utf-8") as f:
            f.write("代码,名称\n")
    CAL = {"2026-11-03", "2026-11-04", "2026-11-05", "2026-11-06",
           "2026-11-09", "2026-11-10"}

    # L25 a missing session is named, not smoothed over -- and coverage starts at the
    # first board, so 11-03/11-04 (before it) are not counted as holes.
    g = board_gap(now=_dt.datetime(2026, 11, 9, 16, 0), days=CAL, snap_dir=tmp)
    leg("L25 a session with no board is named as a hole, and the gap says it cannot be healed",
        g["missing"] == ["2026-11-09"] and g["n_missing"] == 1
        and g["recoverable"] is False and "realtime print" in g["why_unrecoverable"]
        and "2026-11-03" not in g["sessions_expected"]
        and g["next_capture_session"] == "2026-11-09"
        and g["next_capture_after"] is None)

    # L26 before the close, today is not yet a hole: an intraday board is not the session.
    g = board_gap(now=_dt.datetime(2026, 11, 9, 11, 0), days=CAL, snap_dir=tmp)
    leg("L26 before 15:30 today is pending, not missing",
        g["missing"] == [] and g["n_missing"] == 0
        and g["next_capture_session"] == "2026-11-09" and g["next_capture_after"] == "15:30")

    # L27 an unreadable calendar is UNKNOWN, never "no gap" -- the r98 unknown!=empty law.
    g = board_gap(now=_dt.datetime(2026, 11, 9, 16, 0), days=None, snap_dir=tmp)
    leg("L27 unreadable calendar -> missing=None, not an empty list",
        g["status"] == "unreadable_calendar" and g["missing"] is None
        and g["n_missing"] is None)

    # L28 a captured session disappears from the list, and the next capture moves on.
    with open(os.path.join(tmp, "2026-11-09.csv"), "w", encoding="utf-8") as f:
        f.write("代码,名称\n")
    g = board_gap(now=_dt.datetime(2026, 11, 9, 16, 0), days=CAL, snap_dir=tmp)
    leg("L28 a captured session stops being a hole and the next capture is tomorrow",
        g["missing"] == [] and g["last_board"] == "2026-11-09"
        and g["next_capture_session"] == "2026-11-10")
    # an empty file is not a capture -- a truncated write must not read as "done"
    with open(os.path.join(tmp, "2026-11-10.csv"), "w", encoding="utf-8") as f:
        f.write("")
    g = board_gap(now=_dt.datetime(2026, 11, 10, 16, 0), days=CAL, snap_dir=tmp)
    leg("L29 a zero-byte board file is not a capture",
        g["missing"] == ["2026-11-10"] and g["last_board"] == "2026-11-09")

    ok = sum(1 for _, p, _ in legs if p)
    for name, p, detail in legs:
        print("[%s] %s%s" % ("PASS" if p else "FAIL", name, (" | " + detail) if detail else ""))
    print("selftest: %d/%d PASS" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("mode", nargs="?", default="render", choices=["fetch", "render", "selftest"])
    ap.add_argument("--force", action="store_true",
                    help="bypass the session/close/backoff gate (a hand-run, never the chain)")
    a = ap.parse_args(argv)
    if a.mode == "selftest":
        return selftest()
    if a.mode == "fetch":
        return do_fetch(force=a.force)
    return do_render()


if __name__ == "__main__":
    sys.exit(main())