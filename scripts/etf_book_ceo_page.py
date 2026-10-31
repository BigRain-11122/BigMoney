"""ETF production book -> CEO one-page (docs/live_book/LIVE-BOOK-YYYYMMDD.md + .json).

Why this exists: the ETF book is the only money-making structure this company has
shown to work, but every face it publishes (ticket JSON, card JSON, registry JSON,
forward ledger) is machine-shaped. Nothing in the repo answers, in plain language,
"what do I buy today, with how much money, how am I doing, and when does it change".

Pure aggregation, zero new judgement:
  - order list / money split   <- results/etf_book_order/latest.json -> ticket file
  - backtest expectation band  <- results/etf_book_production/latest.json (card)
  - forward track vs inception <- results/etf_book_forward/LEDGER.json
  - next rebalance date        <- data/exchange_calendar.csv (official calendar)

Idempotent: same day -> same content; other days' pages are never touched.

Usage:
  python scripts/etf_book_ceo_page.py run
  python scripts/etf_book_ceo_page.py selftest
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "docs", "live_book")
TICKET_PTR = os.path.join(ROOT, "results", "etf_book_order", "latest.json")
CARD = os.path.join(ROOT, "results", "etf_book_production", "latest.json")
LEDGER = os.path.join(ROOT, "results", "etf_book_forward", "LEDGER.json")
CAL = os.path.join(ROOT, "data", "exchange_calendar.csv")
REGIME_PATH = os.path.join(ROOT, "results", "etf_book_return_regime.json")
BETS_JSON = os.path.join(ROOT, "results", "etf_book_bets_face.json")
LEGS_JSON = os.path.join(ROOT, "results", "etf_book_legs", "latest.json")
MACHINE = os.path.join(ROOT, "fleet", "machine.json")

# Single writer: the page is a plain-language mirror of shared artefacts, so two
# machines regenerating the same day would only produce a git race on docs/live_book.
# bm-a prints it; every other host says so and writes nothing (R31 lane-guard lineage).
HOST = "bm-a"


def machine_id():
    try:
        with open(MACHINE, encoding="utf-8-sig") as fh:
            return json.load(fh).get("machine_id")
    except Exception:
        return None


def writer_allowed(mid):
    return mid == HOST

CLASS_ZH = {
    "equity": "A股",
    "crossborder": "跨境",
    "commodity": "商品",
    "convertible": "转债",
    "bond": "债券",
    "money": "货币",
}


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def carry_regime(path=REGIME_PATH):
    """How much of the quoted headline is cash carry, and what is left without it.

    Read from the artifact, never recomputed here: one price source per number. The page
    used to print 11.33%/yr beside a cash leg paying 1.09% today, without saying that a
    tenth of that headline was the repo leg earning ~2% when the history happened.
    """
    out = {"available": False, "rows": [], "base": None, "cash_rates": None,
           "identity": None, "window": None, "flags": None,
           "source": _rel(path, ROOT).replace("\\", "/")}
    if not os.path.exists(path):
        return out
    obj = _load(path)
    gate = obj.get("gate") or {}
    cells = obj.get("cells") or []
    by_cell = {(round(float(c.get("beta", 0.0)), 4), c.get("regime")): c for c in cells
               if c.get("cagr_pct") is not None}
    rows = []
    for beta, r in (gate.get("betas") or {}).items():
        if not r:
            continue
        try:
            b = round(float(beta), 4)
        except (TypeError, ValueError):
            continue
        obs = by_cell.get((b, "observed")) or {}
        rows.append({"beta": b, "observed_pct": r.get("observed_pct"),
                     "flat_today_pct": r.get("flat_today_pct"),
                     "zero_pct": r.get("zero_pct"), "carry_pp": r.get("carry_pp"),
                     "cash_share": r.get("cash_share"),
                     "pp_per_100bp": r.get("pp_per_100bp"),
                     "maxdd_pct": obs.get("maxdd_pct"), "vol_pct": obs.get("vol_pct")})
    rows.sort(key=lambda x: x["beta"])
    if not rows:
        return out
    base_beta = gate.get("base_beta")
    out.update({
        "available": True, "rows": rows,
        "base": next((r for r in rows if r["beta"] == base_beta), None),
        "cash_rates": obj.get("cash_rates"), "identity": obj.get("identity"),
        "flags": gate.get("flags"),
        "window": ({"first": cells[0].get("first_bar"), "last": cells[0].get("last_bar")}
                   if cells else None),
        "evidence_cutoff": obj.get("evidence_cutoff"),
    })
    return out


def bets_face(path=BETS_JSON):
    """How many independent bets the holdings on this page actually are.

    Single implementation: the reader is `etf_book_bets_face.read_published`, so
    the page quotes the same sentence the executable ticket carries (r1290).  A
    missing or unreadable artifact reads as absent -- never as "five tickers means
    five bets", which is exactly the reading this face exists to correct."""
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    try:
        import etf_book_bets_face as _bf
    except Exception as exc:                                    # noqa: BLE001
        return {"status": "unavailable", "detail": str(exc)[:160]}
    try:
        return dict(_bf.read_published(path))
    except Exception as exc:                                    # noqa: BLE001
        return {"status": "unreadable", "detail": str(exc)[:160]}


def priced_faces(page_bar):
    """Which closing bar each of the three papers was priced on (r1185).

    Single implementation: `etf_book_production.priced_faces()` owns the rule. This page is
    the last of the three in the chain (card -> ticket -> page), so it is the first place that
    can print all three days beside each other. The footer used to say only
    "same priced bar = True"; a reader who is told "different" has to be told which paper is
    the stale one."""
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    try:
        import etf_book_production as _P
        return _P.priced_faces(page_bar=page_bar)
    except Exception as exc:                                    # noqa: BLE001
        return {"faces": {"card": None, "ticket": None, "page": page_bar},
                "verdict": "UNKNOWN", "detail": "reader failed (%s)" % str(exc)[:120],
                "missing": ["card", "ticket"], "same_day": None}


def family_coherence():
    """Whether the width family behind this page's name count was one measurement (r1184).

    Single implementation: `etf_book_production.family_coherence()` owns the rule; this
    page quotes it, exactly as the card does, so the two faces cannot drift into two
    definitions. The page quotes a backtest band whose width was chosen out of a family of
    arm cells -- if that family never priced one panel, the band is a configuration, not a
    measurement, and the reader has to be told which of the two it is. Absent or
    unreadable reads "unproven here", never a pass."""
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    try:
        import etf_book_production as _P
        return _P.family_coherence()
    except Exception as exc:                                    # noqa: BLE001
        return {"artifact": "results/etf_book_phase_atlas_arms.json", "verdict": None,
                "detail": "arm family face unreadable (%s)" % str(exc)[:120],
                "panels": [], "arms": 0, "evidence_cutoff": None,
                "priced_same_panel": None}


def leg_split(path=LEGS_JSON):
    """Where in the day this book's money is earned (r1189).

    Single implementation: `etf_book_leg_attribution.money_split_face()` owns the reader
    and the arithmetic check; this page quotes it. The page already tells the reader how
    much of the headline is lending cash out (the carry face) and how big the book is --
    what it never said is that the headline is earned on the ~1,500 quiet bars and that
    the ~83 bars where the order actually fills lose money. Without that line, a book
    that is a toll machine and a book that is a slow accumulator print the same CAGR.
    Absent/unreadable/broken reads as "cannot verify here", never as agreement."""
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    try:
        import etf_book_leg_attribution as _L
        return _L.money_split_face(path=path)
    except Exception as exc:                                    # noqa: BLE001
        return {"status": "unreadable", "artifact": path,
                "detail": "reader failed (%s)" % str(exc)[:120], "arms": {}}


def _load_ticket():
    """Pointer -> the dated ticket file it names."""
    ptr = _load(TICKET_PTR)
    rel = ptr.get("ticket_file") or ptr.get("file") or ptr.get("path")
    if isinstance(rel, str) and rel:
        cands = [rel] if os.path.isabs(rel) else [
            os.path.join(os.path.dirname(TICKET_PTR), rel),   # sibling of the pointer
            os.path.join(ROOT, rel),                          # repo-root relative
        ]
        for cand in cands:
            if os.path.exists(cand):
                return ptr, _load(cand), cand
    # fall back to the pointer itself when it already carries the ticket body
    if "ticket" in ptr:
        return ptr, ptr, TICKET_PTR
    raise FileNotFoundError("ticket body not resolvable from %s" % TICKET_PTR)


def trading_days_after(cal_dates, anchor, n):
    """The n-th trading day strictly after `anchor` (ISO strings, sorted asc)."""
    if anchor is None or n is None or int(n) <= 0:
        return None
    later = [d for d in cal_dates if d > anchor]
    if len(later) < int(n):
        return None
    return later[int(n) - 1]


def calendar_dates(path=CAL):
    out = []
    with open(path, encoding="utf-8") as fh:
        next(fh, None)
        for line in fh:
            s = line.strip()
            if s:
                out.append(s[:10])
    return out


def money_cny(tk, nav):
    """Backtest percentages -> yuan on this ticket's own capital.

    Pure unit change: every number is one already published on the ticket times `nav`.
    Anything unreadable stays None -- a 0 here would read as "this book earns nothing".
    """
    tk = tk or {}
    metrics = tk.get("metrics") or {}
    book = metrics.get("book") or {}
    bench = metrics.get("same_beta_benchmark") or {}
    out = {"capital_cny": round(float(nav or 0.0), 2), "expected_annual_cny": None,
           "benchmark_annual_cny": None, "excess_annual_cny": None,
           "worst_drawdown_cny": None, "basis": None}
    if not nav or not book:
        return out
    out["expected_annual_cny"] = round(float(book["cagr"]) * nav, 0)
    out["worst_drawdown_cny"] = round(float(book["maxdd"]) * nav, 0)
    out["basis"] = "backtest cagr/maxdd x this ticket's capital, no new assumption"
    if bench and metrics.get("excess_pp") is not None:
        out["benchmark_annual_cny"] = round(float(bench["cagr"]) * nav, 0)
        out["excess_annual_cny"] = round(float(metrics["excess_pp"]) / 100.0 * nav, 0)
    return out


TRADING_DAYS_PER_YEAR = 250

REPO_DIR = os.path.join(ROOT, "data", "repo_daily")
CASH_LEG_SYMBOL = "GC001"

# Where the cash ACTUALLY sits. The page can only advise; nothing in the repo could
# read the account, so the gap between "advice" and "placement" was invisible -- and
# invisible is exactly the 0% case the cash block warns about. This file is the
# handshake: whoever places the order records it once, the page reconciles every run.
PLACEMENT = os.path.join(ROOT, "state", "account", "cash_placement.json")
# A current account pays something, so "idle" is not a 100% loss. No panel exists for
# it, so the rate is a declared constant rather than a fabricated quote; a recorded
# placement may override it in the file.
DEMAND_RATE_PCT = 0.05
PLACEMENT_MAX_AGE_DAYS = 7
DEMAND_INSTRUMENTS = ("", "活期", "demand", "cash", "现金", "活期存款")


def _rel(path, base=ROOT):
    """Repository-relative when both live on one drive, the absolute path otherwise.

    os.path.relpath raises ValueError across drives, and the selftest pins its fixtures
    under %TEMP% (C:) while the repo sits on K: -- a display string must never be able
    to abort a run (same family as pool_deliverable_audit in r1371).
    """
    try:
        return os.path.relpath(path, base)
    except ValueError:
        return os.path.abspath(path)


def cash_yield(cash_amount, symbol=CASH_LEG_SYMBOL, panel_dir=REPO_DIR, window=20):
    """What the idle half earns: cash x the repo panel's own quoted close.

    The page told the reader to buy GC001 but never said what that is worth -- a
    number the CEO pays for by leaving the money in a current account instead.
    Again a pure unit change: the panel prints the rate, this multiplies it by the
    cash on the page. The 1-day repo spikes at quarter-end and before holidays, so
    the trailing mean is quoted beside it. Anything unreadable stays None -- 0 would
    read as "the cash earns nothing", which is exactly the case worth warning about.
    """
    out = {"leg": symbol, "quoted_as": "收盘年化利率 %", "rate_date": None,
           "rate_pct": None, "rate_20d_pct": None, "annual_cny": None,
           "daily_cny": None, "window": int(window), "basis": None,
           "panel": _rel(os.path.join(panel_dir, "%s.csv" % symbol), ROOT)
           .replace("\\", "/")}
    if cash_amount is None or float(cash_amount) <= 0:
        return out
    path = os.path.join(panel_dir, "%s.csv" % symbol)
    if not os.path.exists(path):
        return out
    rows = []
    with open(path, encoding="utf-8") as fh:
        next(fh, None)
        for line in fh:
            parts = line.strip().split(",")
            if len(parts) < 5:
                continue
            try:
                rows.append((parts[0], float(parts[4])))
            except ValueError:
                continue
    rows = [r for r in rows if 0.0 < r[1] < 200.0]   # same sanity band the collector enforces
    if not rows:
        return out
    out["rate_date"], out["rate_pct"] = rows[-1]
    tail = rows[-int(window):]
    out["rate_20d_pct"] = round(sum(v for _, v in tail) / len(tail), 4)
    out["annual_cny"] = round(float(cash_amount) * out["rate_pct"] / 100.0, 0)
    out["daily_cny"] = round(out["annual_cny"] / TRADING_DAYS_PER_YEAR, 0)
    out["basis"] = ("cash x panel close rate / 100; per session = annual / %d sessions"
                    % TRADING_DAYS_PER_YEAR)
    return out


LADDER_TENORS = ("GC001", "GC003", "GC007", "GC014", "GC028", "GC091")
LADDER_WINDOWS_YEARS = (1, 3, 5)
# Frozen adoption rule. A longer tenor is only worth the lock-up if it pays at
# least 20bp a year MORE than rolling the 1-day leg, in BOTH the 1-year and the
# 3-year window (a single year can be a rate-regime accident), while leaving
# <=1% of the calendar with the cash uninvested (maturity landing on a weekend),
# and while being ahead in a majority of the complete calendar years on record.
LADDER_MIN_EDGE_BP = 20.0
LADDER_MAX_IDLE_SHARE = 0.01
LADDER_MIN_POSITIVE_YEAR_SHARE = 0.60
LADDER_YEARS_CHECKED = 5


def repo_rows(symbol, panel_dir=REPO_DIR):
    """(date, close) pairs from one repo panel, holding the collector's sanity band."""
    path = os.path.join(panel_dir, "%s.csv" % symbol)
    if not os.path.exists(path):
        return []
    rows = []
    with open(path, encoding="utf-8") as fh:
        next(fh, None)
        for line in fh:
            parts = line.strip().split(",")
            if len(parts) < 5:
                continue
            try:
                val = float(parts[4])
                if 0.0 < val < 200.0:
                    rows.append((dt.date.fromisoformat(parts[0]), val))
            except ValueError:
                continue
    return rows


def rolled_yield(rows, tenor_days, start=None, end=None):
    """Annualised return of rolling a repo of this maturity, measured on the calendar.

    A repo quote is per annum, so what the money earns is rate x days held / 365 --
    and the days held are not the tenor. One-day money bought on a Friday is lent
    over the weekend (that is why Friday's quote dips); a 3-day leg bought on a
    Thursday matures on a Sunday and the cash sits idle until Monday. Both are read
    off the panel's own calendar here instead of being assumed, and the idle days
    are returned rather than hidden: they are the reason a longer tenor can pay
    less, not more.
    """
    if not rows:
        return None
    dates = [d for d, _ in rows]
    rate = dict(rows)
    idx = [i for i, d in enumerate(dates)
           if (start is None or d >= start) and (end is None or d <= end)]
    if len(idx) < 2:
        return None
    i, last = idx[0], idx[-1]
    tot = 0.0
    days = 0
    idle = 0
    rolls = 0
    while i < last:
        d = dates[i]
        tenor = int(tenor_days)
        mat = d + dt.timedelta(days=tenor)
        j = i + 1
        while j < len(dates) and dates[j] < mat:
            j += 1
        if j > last:
            break
        accrue = (dates[j] - d).days if tenor == 1 else (mat - d).days
        tot += rate[d] / 100.0 * accrue / 365.0
        rolls += 1
        idle += max(0, (dates[j] - max(mat, d + dt.timedelta(days=accrue))).days)
        days += (dates[j] - d).days
        i = j
    if days <= 0:
        return None
    return {"realized_pct": round(tot / (days / 365.0) * 100.0, 4), "rolls": rolls,
            "idle_days": idle, "days": days,
            "idle_share": round(float(idle) / days, 4)}


def cash_ladder(cash_amount, panel_dir=REPO_DIR, tenors=LADDER_TENORS,
                windows=LADDER_WINDOWS_YEARS, years_checked=LADDER_YEARS_CHECKED,
                min_edge_bp=LADDER_MIN_EDGE_BP, max_idle_share=LADDER_MAX_IDLE_SHARE,
                min_positive_year_share=LADDER_MIN_POSITIVE_YEAR_SHARE):
    """Should the idle half be laddered out to a longer repo, or left at one day?

    The page already says "buy GC001"; the question a reader actually has is whether
    a longer tenor pays for the lock-up. It does not follow from the quotes: they are
    per annum, so a 7-day leg can only win if it clears the 1-day leg's own
    quarter-end spikes plus its maturity friction. So every tenor is rolled on the
    panel's own calendar and priced against rolling the 1-day leg in the same window.
    The adoption rule is a frozen constant (see LADDER_MIN_EDGE_BP) and the verdict is
    recomputed from those cells, never written by hand. Unreadable panels stay None.
    """
    base = tenors[0]
    base_rows = repo_rows(base, panel_dir)
    out = {"base": base, "tenors": [], "pick": None, "verdict": "NOT-ASSESSED",
           "reason": None, "cash_amount_cny": None,
           "forgotten_day_cny": None, "rolls": {}, "windows_years": list(windows),
           "rule": {"min_edge_bp": min_edge_bp, "max_idle_share": max_idle_share,
                    "min_positive_year_share": min_positive_year_share,
                    "years_checked": years_checked,
                    "basis": ("edge must clear min_edge_bp in the 1y AND 3y windows, "
                              "idle <= max_idle_share, positive in "
                              "min_positive_year_share of complete years")}}
    if not base_rows:
        out["reason"] = "一天期面板缺席，无法做基线"
        return out
    end = base_rows[-1][0]
    cash = None if cash_amount is None else float(cash_amount)
    out["cash_amount_cny"] = None if (cash is None or cash <= 0) else round(cash, 2)
    base_by_window = {y: rolled_yield(base_rows, 1, end - dt.timedelta(days=365 * y))
                      for y in windows}
    base_spot = base_rows[-1][1]
    if out["cash_amount_cny"]:
        out["forgotten_day_cny"] = round(out["cash_amount_cny"] * base_spot / 100.0 / 365.0, 0)

    complete_years = sorted({d.year for d, _ in base_rows if d.year < end.year})[-years_checked:]

    for symbol in tenors:
        rows = repo_rows(symbol, panel_dir)
        tenor_days = {"GC001": 1, "GC003": 3, "GC004": 4, "GC007": 7,
                      "GC014": 14, "GC028": 28, "GC091": 91, "GC182": 182}.get(
            symbol, int(symbol[-3:]) if symbol[-3:].isdigit() else 1)
        row = {"symbol": symbol, "tenor_days": tenor_days, "spot_pct": None,
               "spot_date": None, "mean250_pct": None, "realized": {}, "edge_bp": {},
               "rolls_1y": None, "idle_days_1y": None, "idle_share_1y": None,
               "annual_cny_spot": None, "annual_cny_realized_1y": None,
               "positive_years": None, "years_checked": None, "verdict": None,
               "reason": None}
        out["tenors"].append(row)
        if not rows:
            row["verdict"] = "NO-PANEL"
            row["reason"] = "面板缺席"
            continue
        row["spot_date"], row["spot_pct"] = rows[-1][0].isoformat(), rows[-1][1]
        tail = [v for _, v in rows[-250:]]
        row["mean250_pct"] = round(sum(tail) / len(tail), 4)
        if row["spot_pct"] is not None and out["cash_amount_cny"]:
            row["annual_cny_spot"] = round(out["cash_amount_cny"] * row["spot_pct"] / 100.0, 0)
        if symbol == base:
            row["verdict"] = "BASELINE"
            row["reason"] = "基线：一天期，季末飙高全部吃进"
        for y in windows:
            r = rolled_yield(rows, tenor_days, end - dt.timedelta(days=365 * y))
            if r is None:
                continue
            row["realized"][str(y)] = r
            if y == 1:
                row["rolls_1y"] = r["rolls"]
                row["idle_days_1y"] = r["idle_days"]
                row["idle_share_1y"] = r["idle_share"]
                if out["cash_amount_cny"]:
                    row["annual_cny_realized_1y"] = round(
                        out["cash_amount_cny"] * r["realized_pct"] / 100.0, 0)
            b = base_by_window.get(y)
            if b is not None and symbol != base:
                row["edge_bp"][str(y)] = round((r["realized_pct"] - b["realized_pct"]) * 100.0, 1)
        out["rolls"][symbol] = row["rolls_1y"]
        if symbol != base:
            pos = tot = 0
            for yr in complete_years:
                a = dt.date(yr, 1, 1)
                b2 = dt.date(yr, 12, 31)
                rr = rolled_yield(rows, tenor_days, a, b2)
                bb = rolled_yield(base_rows, 1, a, b2)
                if rr is None or bb is None:
                    continue
                tot += 1
                if rr["realized_pct"] > bb["realized_pct"]:
                    pos += 1
            row["positive_years"] = pos
            row["years_checked"] = tot
            e1 = row["edge_bp"].get("1")
            e3 = row["edge_bp"].get("3")

            def _over(e):
                return ("多 %.1f bp" % e) if e >= 0 else ("少 %.1f bp" % -e)

            if e1 is None or e3 is None:
                row["verdict"] = "NOT-ASSESSED"
                row["reason"] = "窗口内历史不足"
            else:
                # every failing gate is named: reporting only the first one would tell the
                # reader "idle days" when the real miss is a 12bp gap to the door
                fails = []
                if e1 < min_edge_bp or e3 < min_edge_bp:
                    fails.append("%s（1年）/ %s（3年），门槛 %.0f bp"
                                 % (_over(e1), _over(e3), min_edge_bp))
                if row["idle_share_1y"] is not None and row["idle_share_1y"] > max_idle_share:
                    fails.append("到期撞上休市日，一年空转 %d 天（%.1f%% > %.0f%%）"
                                 % (row["idle_days_1y"], row["idle_share_1y"] * 100.0,
                                    max_idle_share * 100.0))
                if tot and (float(pos) / tot) < min_positive_year_share:
                    fails.append("%d 个完整年只赢了 %d 年" % (tot, pos))
                if fails:
                    row["verdict"] = "REJECT"
                    row["reason"] = "；".join(fails)
                else:
                    row["verdict"] = "ADOPT"
                    row["reason"] = ("1年 %s / 3年 %s，%d/%d 年为正，空转 %.1f%%"
                                     % (_over(e1), _over(e3), pos, tot,
                                        (row["idle_share_1y"] or 0.0) * 100.0))

    adopted = [r for r in out["tenors"] if r["verdict"] == "ADOPT"]
    if adopted:
        best = max(adopted, key=lambda r: min(float(r["edge_bp"]["1"]),
                                              float(r["edge_bp"]["3"])))
        out["pick"] = best["symbol"]
        out["verdict"] = "ADOPT"
        out["reason"] = "%s：%s" % (best["symbol"], best["reason"])
    else:
        out["pick"] = base
        out["verdict"] = "KEEP-1D"
        rejected = [r for r in out["tenors"] if r["verdict"] == "REJECT"]
        if rejected:
            out["reason"] = "；".join("%s %s" % (r["symbol"], r["reason"]) for r in rejected)
        else:
            out["reason"] = "没有可评估的长期限腿"
    return out


def cash_handshake(cash_amount, ladder, placement_path=PLACEMENT, today=None,
                   max_age_days=PLACEMENT_MAX_AGE_DAYS, demand_rate_pct=DEMAND_RATE_PCT):
    """Is the cash where the page says it should be? (advice vs account, priced)

    The page has been telling the reader to hold every idle yuan in the 1-day repo,
    while nothing anywhere could see whether that happened -- so a reader who left it
    in the current account read the same page as one who did not. This closes the loop
    on the only side the company can observe: what the account says was placed.

    Three honesty rules, learned from this file's own earlier faces:
      - no recording -> UNRECORDED and a None gap, never "0 missing" (unread is not zero)
      - the gap is priced from the repo panel's own close minus the declared demand
        rate, so it moves with the market instead of being a typed-in number
      - a revealed fact that contradicts the book (more placed than the book holds)
        is surfaced as OVER-PLACED rather than silently clamped to a comfortable 0
    """
    out = {"status": "UNRECORDED", "recorded": False, "asof": None, "age_days": None,
           "recorded_by": None, "placements": [], "placed_cny": None, "idle_cny": None,
           "idle_share": None, "repo_rate_pct": None, "repo_rate_date": None,
           "demand_rate_pct": float(demand_rate_pct),
           "gap_annual_cny": None, "gap_daily_cny": None,
           "worst_case_annual_cny": None, "stale": None, "reason": None,
           "placement_file": _rel(placement_path, ROOT).replace("\\", "/"),
           "basis": ("idle = book cash - recorded repo placements; gap = idle x "
                     "(repo panel close - declared demand rate) / 100")}
    cash = None if cash_amount is None else float(cash_amount)
    out["cash_amount_cny"] = None if (cash is None or cash <= 0) else round(cash, 2)

    # the rate the page already quotes -- one price source, never re-read here
    base = None
    for row in (ladder or {}).get("tenors") or []:
        if row.get("symbol") == (ladder or {}).get("base"):
            base = row
            break
    if base:
        out["repo_rate_pct"] = base.get("spot_pct")
        out["repo_rate_date"] = base.get("spot_date")
    if out["cash_amount_cny"] and out["repo_rate_pct"] is not None:
        out["worst_case_annual_cny"] = round(
            out["cash_amount_cny"] * (float(out["repo_rate_pct"]) - float(demand_rate_pct))
            / 100.0, 0)

    if not os.path.exists(placement_path):
        out["reason"] = "账户实况未登记，无法判断钱在不在逆回购里"
        return out
    try:
        with open(placement_path, encoding="utf-8-sig") as fh:
            rec = json.load(fh)
    except Exception as exc:
        out["reason"] = "登记件读不动（%s）" % exc
        return out

    out["recorded_by"] = rec.get("recorded_by")
    out["asof"] = rec.get("asof")
    rows = [r for r in (rec.get("placements") or []) if isinstance(r, dict)]
    out["placements"] = [{"instrument": r.get("instrument"),
                          "amount_cny": r.get("amount_cny"),
                          "rate_pct": r.get("rate_pct"),
                          "rate_date": r.get("rate_date")} for r in rows]
    if rec.get("demand_rate_pct") is not None:
        try:
            out["demand_rate_pct"] = float(rec["demand_rate_pct"])
            if out["cash_amount_cny"] and out["repo_rate_pct"] is not None:
                out["worst_case_annual_cny"] = round(
                    out["cash_amount_cny"]
                    * (float(out["repo_rate_pct"]) - out["demand_rate_pct"]) / 100.0, 0)
        except (TypeError, ValueError):
            pass
    if str(rec.get("recorded_by") or "").strip().lower() in ("", "unrecorded", "none", "null"):
        out["reason"] = "账户实况未登记（登记件在位但没人填）"
        return out

    out["recorded"] = True
    try:
        placed = 0.0
        for r in rows:
            amt = r.get("amount_cny")
            if amt is None:
                continue
            inst = str(r.get("instrument") or "").strip()
            if inst.lower() in DEMAND_INSTRUMENTS:
                continue
            placed += float(amt)
        out["placed_cny"] = round(placed, 2)
    except (TypeError, ValueError) as exc:
        out["recorded"] = False
        out["reason"] = "登记件金额不可读（%s）" % exc
        return out

    ref = today or dt.date.today()
    if isinstance(ref, str):
        ref = dt.date.fromisoformat(ref[:10])
    if out["asof"]:
        try:
            out["age_days"] = (ref - dt.date.fromisoformat(str(out["asof"])[:10])).days
        except ValueError:
            out["age_days"] = None
    out["stale"] = (out["age_days"] is not None and out["age_days"] > int(max_age_days))

    if out["cash_amount_cny"] is None:
        out["reason"] = "账面现金不可读，无法对账"
        out["recorded"] = False
        return out

    idle = out["cash_amount_cny"] - out["placed_cny"]
    tol = max(1.0, 0.001 * out["cash_amount_cny"])
    if idle < -tol:
        out["status"] = "OVER-PLACED"
        out["idle_cny"] = 0.0
        out["idle_share"] = 0.0
        out["reason"] = ("登记的在仓金额比账面现金还多 ¥%s：登记件与账本对不上，先核账再谈缺口"
                         % format(-idle, ",.0f"))
        return out
    idle = max(0.0, idle)
    out["idle_cny"] = round(idle, 2)
    out["idle_share"] = round(idle / out["cash_amount_cny"], 4) if out["cash_amount_cny"] else None
    if out["repo_rate_pct"] is not None:
        out["gap_annual_cny"] = round(idle * (float(out["repo_rate_pct"])
                                              - out["demand_rate_pct"]) / 100.0, 0)
        out["gap_daily_cny"] = round(out["gap_annual_cny"] / TRADING_DAYS_PER_YEAR, 0)
    if idle <= tol:
        out["status"] = "IN-PLACE"
        out["reason"] = "账面现金已全部登记在逆回购里"
    elif idle >= out["cash_amount_cny"] * 0.995:
        out["status"] = "IDLE"
        out["reason"] = "登记件显示现金全部不在逆回购里（等于活期）"
    else:
        out["status"] = "PARTIAL"
        out["reason"] = "只登记了一部分"
    if out["stale"]:
        out["reason"] = ("登记于 %s（%s 天前，已过期：超过 %s 天）：先重记一次再判断；%s"
                         % (out["asof"], out["age_days"], max_age_days, out["reason"]))
    return out


STRESS_DIR = os.path.join(ROOT, "results", "etf_book_stress")
STRESS_WINDOWS = (1, 5, 20)


def stress_stats(daily, windows=STRESS_WINDOWS, capital=None):
    """Worst run of `n` consecutive days for a fixed-weight book.

    `daily` is a pandas Series of (weight-applied) book returns; a name that printed no
    price on a leg simply earns nothing for that leg, which is how the research engine
    treats it too. Everything here is the same arithmetic in a different window -- no new
    assumption, no fitted model. Returns None when there is not enough history, so a
    missing panel can never be read as "this book never loses".
    """
    if daily is None or len(daily) == 0:
        return None
    s = daily.dropna()
    if len(s) == 0:
        return None
    out = {"n_days": int(len(s)), "first": str(s.index[0])[:10], "last": str(s.index[-1])[:10],
           "worst": {}, "capital_cny": capital}
    for n in windows:
        if len(s) < n:
            out["worst"]["%dd" % n] = None
            continue
        # compounded, not summed: the reader is being told what the money did over N days
        gross = (1.0 + s).cumprod() / (1.0 + s).cumprod().shift(n) - 1.0
        roll = gross.dropna()
        if len(roll) == 0:
            out["worst"]["%dd" % n] = None
            continue
        when = roll.idxmin()
        val = float(roll.min())
        row = {"pct": round(val * 100.0, 2), "end_date": str(when)[:10]}
        row["cny"] = None if capital is None else round(val * float(capital), 0)
        out["worst"]["%dd" % n] = row
    return out


def panel_fingerprint(close):
    """Content hash of the panel a replay was priced against -- not its date.

    A flip repair inside the panel rewrites today's worst window without moving today's
    date, so a cache keyed on the bar alone hands back numbers for a world that has
    since been corrected (r1374 hit exactly this on the per-tier replay; this is the
    one implementation, imported there as well).
    """
    h = hashlib.sha256()
    if close is not None and len(getattr(close, "index", [])):
        try:
            import pandas as _pd
            h.update(("shape|%d,%d" % close.shape).encode())
            h.update(_pd.util.hash_pandas_object(close.fillna(0.0), index=True)
                     .values.tobytes())
        except Exception:
            h.update(b"|unhashable")
    return h.hexdigest()


def book_returns(close, names, wts):
    """Fixed-weight book return series for a panel -- one arithmetic, both runs use it."""
    import pandas as _pd
    legs = {}
    for n, w in zip(names, wts):
        if n in close.columns:
            legs[n] = close[n].astype(float).pct_change().fillna(0.0) * w
        else:
            legs[n] = _pd.Series(0.0, index=close.index)
    return _pd.DataFrame(legs).sum(axis=1)


def flip_threshold():
    """The published repair threshold, read from its owner -- None when it cannot be read."""
    try:
        import sys as _sys
        _sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import etf_equity_alpha as A
        return float(getattr(A, "FLIP_THR", 0.35))
    except Exception:
        return None


def clean_panel(close):
    """The same panel with repairable price flips flattened -- published rule, imported.

    `etf_equity_alpha.repair_flips` is the single implementation (E270). It wants the
    open face as well; this page is close-only, so the open argument is the close face
    and the repaired open result is discarded. Returns (clean_close, n_flattened, thr),
    or (None, 0, None) when the rule cannot be imported -- no clean claim rather than a
    fabricated one.
    """
    try:
        import sys as _sys
        _sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import etf_equity_alpha as A
    except Exception:
        return None, 0, None
    thr = float(getattr(A, "FLIP_THR", 0.35))
    try:
        adj, _open_ignored, n = A.repair_flips(close, close, thr)
        return adj, int(n), thr
    except Exception:
        return None, 0, None


def contamination_block(raw_st, clean_st, n_flattened, thr):
    """Which part of the printed worst window is a data print rather than a market day.

    The stress table replays today's weights over the raw panel; the raw panel carries
    single-day quote flips (share-count changes read as -90% returns), and the book's own
    worst day sits on one of them. This block answers that question in the page's own
    construction -- same weights, same windows, the published repair applied -- instead of
    quoting a number from a different face. It decides nothing: switching production onto
    the repaired panel moves every number this book has published, which is a separate,
    deliberate decision.
    """
    out = {"flip_thr": thr, "flip_prints_flattened": int(n_flattened),
           "raw_worst": {}, "clean_worst": {}, "differs": False, "sentence": None}
    for n in STRESS_WINDOWS:
        r = ((raw_st or {}).get("worst") or {}).get("%dd" % n)
        c = ((clean_st or {}).get("worst") or {}).get("%dd" % n)
        out["raw_worst"]["%dd" % n] = None if not r else {
            "pct": r.get("pct"), "end_date": r.get("end_date"), "cny": r.get("cny")}
        out["clean_worst"]["%dd" % n] = None if not c else {
            "pct": c.get("pct"), "end_date": c.get("end_date"), "cny": c.get("cny")}
    r1 = out["raw_worst"].get("1d")
    c1 = out["clean_worst"].get("1d")
    if not r1:
        return out
    if not c1:
        out["sentence"] = ("这里没有可比对的修复版读数（修复规则没有返回本页需要的窗口，"
                           "或者它根本读不到），所以不主张这个最差日是干净还是脏。")
        return out
    out["differs"] = abs(float(r1["pct"]) - float(c1["pct"])) > 0.005
    if not out["differs"]:
        out["sentence"] = ("按同一条修复规则把面板里的单日翻转压平（共 %d 处，阈值 %.0f%%）之后，"
                           "这张表最差的一天没有变化（%+.2f%%），也就是说它是行情，不是报价。"
                           % (n_flattened, (thr or 0.0) * 100.0, float(r1["pct"])))
        return out
    out["sentence"] = ("面板里有 %d 处单日超过 %.0f%% 的报价翻转（份额变动被读成暴跌），这张表最差的一天 "
                       "%+.2f%%（%s）就是其中之一；按同一条规则（etf_equity_alpha.repair_flips，"
                       "导入未改写）把翻转压平后，最差的一天是 %+.2f%%（%s）。修与不修是一次单独的决定："
                       "它会把这本书已发布的每一个数字一起挪动，不在本页里悄悄生效。"
                       % (n_flattened, (thr or 0.0) * 100.0, float(r1["pct"]), r1.get("end_date"),
                          float(c1["pct"]), c1.get("end_date")))
    return out


def stress_cache_digest(close, priced_bar, capital, windows, order, flip_thr=None):
    """What the cached replay was computed FROM: bar, capital, weights, panel bytes.

    Every one of these can move while the priced bar stays put: a repaired print, a
    re-priced ticket (weights rescale), a different capital figure. Keying on the date
    alone would answer a question nobody asked.
    """
    h = hashlib.sha256()
    h.update(("bar|%s|cap|%.4f|win|%s" % (
        priced_bar, float(capital or 0.0),
        ",".join(str(int(w)) for w in windows or STRESS_WINDOWS))).encode())
    h.update(("|w|" + ",".join(
        "%s:%.10f" % (o.get("symbol"), float(o.get("weight") or 0.0))
        for o in order or [])).encode())
    h.update(("|panel|" + panel_fingerprint(close)).encode())
    h.update(("|flipthr|%.4f" % (flip_thr if flip_thr is not None else -1.0)).encode())
    return h.hexdigest()


def build_stress(order, capital, priced_bar, close=None):
    """Data path: replay today's weights over the whole panel, worst-window report.

    Cached per (priced bar, capital, weights, panel content) -- re-walking 20 years of a
    1,500-column panel every tick is cost without information, but the bar alone is not
    an identity: a repaired print rewrites the worst window without moving the date, and
    a re-priced ticket changes the weights on the very same bar. A cache written before
    this digest existed has no `inputs_sha256` and is a MISS, not a hit.
    """
    if not order:
        return None
    if close is None:
        try:
            import sys as _sys
            _sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import etf_book_forward as F
            close, _o, _a, _f, _sc, _cls, _nf = F.build_inputs()
        except Exception as exc:
            return {"error": "%s: %s" % (type(exc).__name__, exc), "worst": {},
                    "capital_cny": capital}
    inputs_sha = stress_cache_digest(close, priced_bar, capital, STRESS_WINDOWS, order,
                                     flip_thr=flip_threshold())
    cache = os.path.join(STRESS_DIR, "STRESS-%s.json" % str(priced_bar).replace("-", ""))
    if os.path.exists(cache):
        try:
            with open(cache, encoding="utf-8") as fh:
                c = json.load(fh)
            if (c.get("inputs_sha256") == inputs_sha
                    and c.get("priced_bar") == str(priced_bar)):
                return c
        except (OSError, ValueError):
            pass
    try:
        names = [o.get("symbol") for o in order]
        wts = [float(o.get("weight") or 0.0) for o in order]
        book = book_returns(close, names, wts)
    except Exception as exc:               # honest: no panel -> no stress claim
        return {"error": "%s: %s" % (type(exc).__name__, exc), "worst": {}, "capital_cny": capital}
    st = stress_stats(book, capital=capital)
    if st is None:
        return None
    # the same replay on the repaired panel, so the page can say whether its own worst
    # day is a market day or a quote flip -- exactly one number (the raw one) is published
    clean, n_flat, thr = clean_panel(close)
    clean_st = None
    if clean is not None:
        try:
            import pandas as _pd
            clean_st = stress_stats(book_returns(clean, names, wts), capital=capital)
        except Exception:
            clean_st = None
    st["contamination"] = contamination_block(st, clean_st, n_flat, thr)
    st["capital_cny"] = round(float(capital or 0.0), 2)
    st["basis"] = ("今天的权重原封不动摆回整段面板（现金 0 息），取最坏的连续 N 个交易日；"
                   "不是策略实际路径，是同一批票的最坏窗口")
    try:
        os.makedirs(STRESS_DIR, exist_ok=True)
        with open(cache, "w", encoding="utf-8", newline="\n") as fh:
            st["priced_bar"] = str(priced_bar)
            st["inputs_sha256"] = inputs_sha
            json.dump(st, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
    except OSError:
        pass
    return st


def today_action(p):
    """Does the reader have to touch the account today?

    The ticket is re-priced every session against a fixed set of weights, so the
    share counts in the order list change daily even though the DECISION has not
    moved since `book_decided_at`. Publishing that list as "buy this today" makes
    a holder re-buy a book they already own -- at 8bp a side that is more than the
    book's own expected annual return. So the page has to name the world the
    reader is in:

      rebalance -- this priced bar IS the decision bar: trade.
      open      -- the reader is not in the book yet: buy the list once.
      hold      -- already holding and the decision has not moved: do nothing.
      unknown   -- a date face is missing; refuse to guess.
    """
    decided = p.get("book_decided_at")
    priced = p.get("priced_bar")
    holding = bool((p.get("forward") or {}).get("bars"))
    out = {"mode": "unknown", "holding": holding, "book_decided_at": decided,
           "priced_bar": priced, "next_trade_date": None, "cost_if_retraded_pct_per_year": None,
           "cost_basis": None}
    if not decided or not priced:
        return out
    decided_bar_is_priced = (str(decided) == str(priced))
    if decided_bar_is_priced:
        out["mode"] = "rebalance" if holding else "open"
    else:
        out["mode"] = "hold" if holding else "open"
    out["next_trade_date"] = p.get("next_rebalance_date") if out["mode"] == "hold" else priced

    # What chasing this list every session would cost, in percent of CAPITAL per year.
    # 2 sides x cost_bp on the book slice x a 250-session year -- an assumption, published.
    cost_bp = p.get("cost_bp_per_side")
    k = p.get("k_now")
    if cost_bp and k:
        per_year = 2.0 * (float(cost_bp) / 10000.0) * TRADING_DAYS_PER_YEAR * float(k)
        out["cost_if_retraded_pct_per_year"] = round(per_year * 100.0, 2)
        out["cost_basis"] = ("2 sides x %s bp x %d sessions x book share %.4f, on capital"
                             % (cost_bp, TRADING_DAYS_PER_YEAR, float(k)))
    return out


def build(with_stress=False):
    ptr, tk, tk_path = _load_ticket()
    card = _load(CARD) if os.path.exists(CARD) else {}
    ledger = _load(LEDGER) if os.path.exists(LEDGER) else {}

    nav = float(tk.get("ticket", {}).get("nav") or 0.0)
    order = list(tk.get("ticket", {}).get("order") or [])
    cash_amt = float(tk.get("ticket", {}).get("cash_amount") or 0.0)
    book_amt = float(tk.get("ticket", {}).get("book_amount") or 0.0)
    cash_w = float(tk.get("ticket", {}).get("cash_weight") or 0.0)
    cash_leg = tk.get("ticket", {}).get("cash_leg") or "cash (no instrument named)"

    bars = list(ledger.get("bars") or [])
    fwd = {"bars": len(bars), "inception": None, "nav": None, "since_inception_pct": None,
           "as_of": None}
    if bars:
        fwd["inception"] = bars[0].get("bar")
        fwd["as_of"] = bars[-1].get("bar")
        fwd["nav"] = bars[-1].get("nav")
        fwd["since_inception_pct"] = round((float(bars[-1]["nav"]) - 1.0) * 100.0, 4)

    # the daily answer to "are we beating just buying the four exposures" -- read off the
    # forward ledger's own benchmark block, never re-priced here (one price source)
    bench = (ledger.get("benchmark") or {}).get("latest") or {}
    # r1316: a spread with no horizon is read as a verdict. Carry the ledger's own
    # power table (what edge this record can resolve inside 6m/1y/2y/3y, and how
    # many YEARS the published alphas would need) beside the number.
    _pw = ((ledger.get("benchmark") or {}).get("significance") or {}).get("power") or {}
    vs_basket = None
    if bench.get("excess_pp") is not None:
        vs_basket = {
            "bar": bench.get("bar"),
            "book_nav": bench.get("book_nav"),
            "basket_nav": bench.get("basket_nav"),
            "excess_pp": bench.get("excess_pp"),
            "basket": ((ledger.get("benchmark") or {}).get("labels") or {}),
            "basis": "等权 1/4、同一换仓日、次日开盘成交",
            "horizon": ({"min_detectable_edge_pp": _pw.get("min_detectable_edge_pp"),
                         "years_for_80pct_power": _pw.get("years_for_80pct_power"),
                         "candidate_sources": _pw.get("candidate_sources")}
                        if _pw.get("available") else None),
        }

    bt = (card.get("backtest") or {})
    band = {}
    # the executable ticket prices its own book; quote that口径 first, from the ticket itself
    tk_book = (tk.get("metrics") or {}).get("book") or {}
    if tk_book:
        band["%d 名·可执行单口径（本单这份账）" % (tk.get("n_hold") or len(order))] = {
            "full": {"cagr_pct": round(tk_book["cagr"] * 100, 2),
                     "sharpe": round(tk_book["sharpe"], 2),
                     "maxdd_pct": round(tk_book["maxdd"] * 100, 2)}}
    for key, label in (("n5_base", "5 名·beta 覆盖"),
                       ("n12_vt08", "12 名·8% 波动目标（生产卡片口径）")):
        blk = bt.get(key) or {}
        if not blk:
            continue
        row = {}
        for seg in ("full", "is", "oos"):
            s = blk.get(seg) or {}
            if s:
                row[seg] = {"cagr_pct": round(s["cagr"] * 100, 2),
                            "sharpe": round(s["sharpe"], 2),
                            "maxdd_pct": round(s["maxdd"] * 100, 2)}
        band[label] = row

    # the same percentages expressed in yuan on THIS ticket's capital -- a unit change, not a new estimate
    money = money_cny(tk, nav)

    feed = tk.get("feed_status") or {}
    agree = tk.get("card_agreement") or {}
    cal = calendar_dates() if os.path.exists(CAL) else []
    next_reb = trading_days_after(cal, tk.get("evidence_cutoff"), tk.get("next_decision_bars"))
    today = dt.date.today().isoformat()

    page = {
        "schema": "etf-book-ceo-page/v1",
        "generated_for_date": today,
        "evidence_cutoff": tk.get("evidence_cutoff"),
        "priced_bar": feed.get("ticket_bar"),
        "feed_status": feed.get("status"),
        "feed_lag_days": feed.get("lag_days"),
        "capital_cny": nav,
        "book_amount_cny": round(book_amt, 2),
        "cash_amount_cny": round(cash_amt, 2),
        "cash_weight": round(cash_w, 4),
        "cash_leg": cash_leg,
        "cash_yield": cash_yield(cash_amt),
        "cash_ladder": cash_ladder(cash_amt),
        "k_now": tk.get("k_now"),
        "n_hold": tk.get("n_hold"),
        "cost_bp_per_side": tk.get("cost_bp_per_side"),
        "book_decided_at": tk.get("book_decided_at"),
        "next_decision_bars": tk.get("next_decision_bars"),
        "next_rebalance_date": next_reb,
        "order": [{"symbol": o.get("symbol"), "class": o.get("class"),
                   "class_zh": CLASS_ZH.get(o.get("class"), o.get("class")),
                   "weight": o.get("weight"), "price": o.get("price"),
                   "lots": o.get("lots"), "shares": o.get("shares"),
                   "amount_cny": o.get("amount")} for o in order],
        "forward": fwd,
        "vs_basket": vs_basket,
        "backtest_band": band,
        "excess_pp": (tk.get("metrics") or {}).get("excess_pp"),
        "money_cny": money,
        "ticket_book": tk_book or None,
        "same_beta_benchmark": (tk.get("metrics") or {}).get("same_beta_benchmark"),
        "agreement": {"same_decision_bar": agree.get("same_decision_bar"),
                      "same_priced_bar": agree.get("same_priced_bar"),
                      "card_names": agree.get("card_names")},
        "sources": {"ticket": _rel(tk_path, ROOT),
                    "card": "results/etf_book_production/latest.json",
                    "ledger": "results/etf_book_forward/LEDGER.json",
                    "calendar": "data/exchange_calendar.csv"},
        "caveats": [
            "回测票池是现存 ETF（有幸存者偏差）；2020-2023 段弱、收益主要集中在 2024 之后。",
            "前向账本只有 %d 个交易日，自起始净值 %.4f 不构成业绩记录。" % (fwd["bars"], fwd["nav"] or 0.0),
            "现金腿若不下单，账本按 %s 计息；不买逆回购则实际是 0 息。" % cash_leg,
            "这是研究产出，不是投资建议；实盘下单是 CEO 的直接权限，公司自动实盘仍是 CEO 唯一门。",
        ],
    }
    page["today_action"] = today_action(page)
    page["bets"] = bets_face()
    page["family_coherence"] = family_coherence()
    page["priced_faces"] = priced_faces(page["priced_bar"])
    page["cash_handshake"] = cash_handshake(cash_amt, page["cash_ladder"], today=today)
    page["carry_regime"] = carry_regime()
    page["leg_split"] = leg_split()
    page["stress"] = build_stress(order, nav, feed.get("ticket_bar")) if with_stress else None
    return page, today


def render_md(p):
    L = []
    add = L.append
    add("# 今日 ETF 实盘单 —— %s" % p["generated_for_date"])
    add("")
    add("> 一页纸，全部数字从机器面直接抄来：单子来自可执行票、预期来自生产卡片、账面来自前向账本。没有新增判断。")
    add("")
    add("## 一句话")
    inv = p["book_amount_cny"]
    act = p.get("today_action") or {"mode": "unknown"}
    mode = act.get("mode")
    if mode == "hold":
        add("**今天不用动手。** 这套组合上一次定稿 **%s**，今天只是按新的收盘价（**%s**）把同一批权重重新算成份额——"
            "清单里份额和金额的变化是价格漂移，不是新指令。下一个动手日是 **%s**。"
            % (p["book_decided_at"], p["priced_bar"], p["next_rebalance_date"]))
        if act.get("cost_if_retraded_pct_per_year") is not None:
            add("")
            add("（照这份清单每天重下一遍的代价：单边 %s bp、进出两边、一年按 %d 个交易日、账内占比 %.1f%%，"
                "一年约 **%.1f%% 的资本**——比这本账回测的 %.2f%%/年还高。所以「今天不动」不是懒惰，是这条纪律的一部分。）"
                % (p.get("cost_bp_per_side"), TRADING_DAYS_PER_YEAR, (p.get("k_now") or 0.0) * 100,
                   act["cost_if_retraded_pct_per_year"],
                   (p.get("ticket_book") or {}).get("cagr", 0.0) * 100))
    elif mode == "rebalance":
        add("**今天是换仓日。** 先卖掉不在清单里的，再按下面清单买：花 **¥%s**（占总资金 %.1f%%）买 %d 只 ETF，"
            "剩下的 **¥%s**（%.1f%%）放%s。"
            % (format(inv, ",.0f"), (p["k_now"] or 0) * 100, p["n_hold"] or len(p["order"]),
               format(p["cash_amount_cny"], ",.0f"), p["cash_weight"] * 100, p["cash_leg"]))
    elif mode == "open":
        add("**还没建仓的话，按这个下单：** 花 **¥%s**（占总资金 %.1f%%）买 %d 只 ETF，"
            "剩下的 **¥%s**（%.1f%%）放%s。已经在账上的不要照着重下一遍，下一次动手日是 **%s**。"
            % (format(inv, ",.0f"), (p["k_now"] or 0) * 100, p["n_hold"] or len(p["order"]),
               format(p["cash_amount_cny"], ",.0f"), p["cash_weight"] * 100, p["cash_leg"],
               p["next_rebalance_date"]))
    else:
        add("**今天是否要动手：无法判定**（缺 book_decided_at 或 priced_bar，不猜）。下面只有数值，不代表指令。")
    add("")
    add("## 下单清单%s" % ("（如果你今天才建仓）" if mode == "hold" else ""))
    add("")
    add("| 代码 | 类别 | 份（100 股/份） | 参考价 | 金额 |")
    add("|---|---|---|---|---|")
    for o in p["order"]:
        add("| %s | %s | %s | %s | ¥%s |"
            % (o["symbol"], o["class_zh"] or "", format(o["lots"] or 0, ","),
               o["price"], format(o["amount_cny"] or 0, ",.0f")))
    add("| — | **合计** | | | **¥%s** |" % format(p["book_amount_cny"], ",.0f"))
    add("")
    add("剩余现金 ¥%s 买 %s（或等价），不要留活期。" % (format(p["cash_amount_cny"], ",.0f"), p["cash_leg"]))
    add("")
    bf = p.get("bets") or {}
    if bf.get("status") == "ok" and bf.get("sentence"):
        add("## 这几只票到底有几个赌注")
        add("")
        add("**%s**" % bf["sentence"])
        add("")
        if bf.get("effective_bets") is not None and bf.get("nominal_bets") is not None:
            add("- 数票数 %d 只，数方向 **%.2f** 个（这两个数不一样的原因：相关性）。"
                % (round(float(bf["nominal_bets"])), float(bf["effective_bets"])))
        if bf.get("risk_split") is not None:
            add("- 风险不是按钱分的：按波动与相关拆到每只身上，等效 **%.2f** 个下注。"
                % float(bf["risk_split"]))
        if bf.get("evidence_cutoff"):
            add("- 计价截止 %s（读的是这张单自己的持仓权重，不是另抄一份书）。"
                % bf["evidence_cutoff"])
        add("")
    elif bf:
        add("- 这几只票到底有几个赌注：%s（缺面不读成一个赌注）"
            % (bf.get("note") or bf.get("detail") or "未产出"))
        add("")
    cy = p.get("cash_yield") or {}
    if cy.get("annual_cny") is not None:
        add("## 现金那一半在赚多少")
        add("")
        add("¥%s 放着不是 0 息：按 **%s** 最近收盘年化 **%.2f%%**（%s 的报价）算，一年约 **+¥%s**，"
            "每个交易日约 +¥%s。"
            % (format(p["cash_amount_cny"], ",.0f"), cy["leg"], cy["rate_pct"], cy["rate_date"],
               format(cy["annual_cny"], ",.0f"), format(cy["daily_cny"], ",.0f")))
        if cy.get("rate_20d_pct") is not None:
            add("")
            add("- 近 %d 个交易日这个利率平均 %.2f%%（一天期逆回购在季末/节前会飙高，平时就是个零钱利率），"
                "所以这笔钱是「现金不缩水」，不是收益来源。"
                % (cy["window"], cy["rate_20d_pct"]))
        add("- 不买逆回购、留在活期，这 ¥%s 就是没有的。" % format(cy["annual_cny"], ",.0f"))
        add("")
    cl = p.get("cash_ladder") or {}
    rows_l = cl.get("tenors") or []
    if rows_l and cl.get("cash_amount_cny"):
        add("## 现金腿要不要换长一点的期限")
        add("")
        add("逆回购报价是年化，所以「期限越长利率越高」不等于「赚得更多」——一天的腿季末会飙高，"
            "长的腿到期撞周末还会空转。按这些面板自己的日历逐条滚出来：")
        add("")
        add("| 代码 | 期限 | 今日报价 | 过去 1 年实盘年化 | 比一天期 | 一年滚几次 | 空转天/年 | 一年约赚 |")
        add("|---|---|---|---|---|---|---|---|")
        for r in rows_l:
            r1 = (r.get("realized") or {}).get("1") or {}
            edge = (r.get("edge_bp") or {}).get("1")
            add("| %s | %d 天 | %.2f%% | %s | %s | %s | %s | %s |"
                % (r["symbol"], r["tenor_days"], r["spot_pct"],
                   ("%.2f%%" % r1["realized_pct"]) if r1 else "—",
                   ("%+.1f bp" % edge) if edge is not None else "基线",
                   r.get("rolls_1y") if r.get("rolls_1y") is not None else "—",
                   r.get("idle_days_1y") if r.get("idle_days_1y") is not None else "—",
                   ("¥%s" % format(r["annual_cny_realized_1y"], ",.0f"))
                   if r.get("annual_cny_realized_1y") is not None else "—"))
        add("")
        rule = cl.get("rule") or {}
        if cl.get("verdict") == "KEEP-1D":
            add("**结论：不换，继续一天期。** 过门的条件是三条一起满足：比一天期一年多赚 %.0f bp 以上、"
                "1 年和 3 年都成立、空转不超过 %.0f%% 的日历日。没有一条腿过门——逐条见下表与下面三行。"
                % (rule.get("min_edge_bp") or 0.0,
                   (rule.get("max_idle_share") or 0.0) * 100.0))
            add("")
            for r in rows_l:
                if r["symbol"] == cl.get("base"):
                    continue
                e = r.get("edge_bp") or {}
                if not e:
                    continue
                add("- %s（%d 天）：1 年 %s -> 3 年 %s -> 5 年 %s，%d 个完整年里赢了 %s 年 —— %s。"
                    % (r["symbol"], r["tenor_days"],
                       "%+.1f bp" % float(e.get("1") or 0.0),
                       "%+.1f bp" % float(e.get("3") or 0.0),
                       "%+.1f bp" % float(e.get("5") or 0.0),
                       int(r.get("years_checked") or 0),
                       r.get("positive_years") if r.get("positive_years") is not None else "—",
                       {"REJECT": "不选", "ADOPT": "选它",
                        "NOT-ASSESSED": "历史不足"}.get(r.get("verdict"), r.get("verdict"))))
            add("- 一句话：差价随窗口拉长而缩水，锁久了换不来确定性，只换来「这笔钱这几天不能动」。")
            _horizon = [r for r in rows_l if int(r.get("tenor_days") or 0) >= 28]
            if _horizon:
                _h = _horizon[0]
                _he = (_h.get("edge_bp") or {}).get("1")
                add("- 这笔钱一个月才换一次仓，所以真正对得上闲置期的是 %s（%d 天，一年只滚 %s 次），"
                    "它实测 %s、空转 %s 天——同样没过门，不是「期限没选对」。"
                    % (_h["symbol"], _h["tenor_days"], _h.get("rolls_1y"),
                       ("%+.1f bp" % float(_he)) if _he is not None else "—",
                       _h.get("idle_days_1y")))
            add("")
            rolls_a = (cl.get("rolls") or {}).get(cl.get("base") or "GC001")
            rolls_b = (cl.get("rolls") or {}).get("GC007")
            if rolls_a and rolls_b:
                add("- 换 7 天期唯一真实的好处不是收益，是按键次数：一年 %d 次 -> %d 次。"
                    "代价是每忘记一天，那天的利息就没了，约 ¥%s。自己判断哪边更容易出错。"
                    % (rolls_a, rolls_b,
                       format(cl.get("forgotten_day_cny") or 0, ",.0f")))
        elif cl.get("verdict") == "ADOPT":
            add("**结论：换 %s。** %s。"
                % (cl.get("pick"), cl.get("reason")))
            add("")
            add("- 门槛 %.0f bp 是写死在代码里的（1 年和 3 年都要过），不是事后挑的。"
                % (rule.get("min_edge_bp") or 0.0))
        else:
            add("**结论：未判定。** %s" % (cl.get("reason") or "面板不足"))
        add("")
        add("- 这些都是「现金不缩水」的量级，不是收益来源；季末/节前的飙高是常态，别把它当稳定收益。")
        add("")
    hs = p.get("cash_handshake") or {}
    if hs:
        add("## 现金现在到底在哪（账实对账）")
        add("")
        st = hs.get("status")
        if st == "UNRECORDED":
            add("**这一页不知道钱在哪。** 上面的建议是「¥%s 全部放 %s」，但账户里实际下了多少，"
                "本仓库看不到——没人登记过。"
                % (format(p["cash_amount_cny"], ",.0f"), p.get("cash_leg")))
            add("")
            add("- 差多少不猜：如果这 ¥%s 还在活期，按 %s 报的 %.2f%%（%s）减去活期 %.2f%%，"
                "一年少赚约 **¥%s**（每个交易日约 ¥%s）。这是「全留活期」这个最坏情形的量级，不是实测。"
                % (format(p["cash_amount_cny"], ",.0f"), p.get("cash_leg"),
                   float(hs.get("repo_rate_pct") or 0.0), hs.get("repo_rate_date") or "—",
                   float(hs.get("demand_rate_pct") or 0.0),
                   format(hs.get("worst_case_annual_cny") or 0, ",.0f"),
                   format(round((hs.get("worst_case_annual_cny") or 0) / TRADING_DAYS_PER_YEAR), ",.0f")))
            add("- 怎么接上：把实际下单结果记一行到 `%s`（`recorded_by` 填你的名字、`asof` 填日期、"
                "`placements` 里每条 `instrument/amount_cny/rate_pct/rate_date`）——下一轮这页就会自动对账。"
                % hs.get("placement_file"))
            add("- %s。" % (hs.get("reason") or ""))
        elif st == "OVER-PLACED":
            add("**登记件与账本对不上。** %s" % (hs.get("reason") or ""))
            add("")
            add("- 已登记在仓 ¥%s vs 账面现金 ¥%s —— 先核哪个数是对的，别在这基础上加仓。"
                % (format(hs.get("placed_cny") or 0, ",.0f"),
                   format(p["cash_amount_cny"], ",.0f")))
        else:
            if st == "IN-PLACE":
                add("**对上了：** 登记的 ¥%s 全部在逆回购里，账面现金 ¥%s 没有缺口。"
                    % (format(hs.get("placed_cny") or 0, ",.0f"),
                       format(p["cash_amount_cny"], ",.0f")))
            elif st == "IDLE":
                add("**全在活期。** 登记件显示现金一分钱都没进逆回购——一年少赚约 **¥%s**。"
                    % format(hs.get("gap_annual_cny") or 0, ",.0f"))
            else:
                add("**只放了一部分：** 已登记在仓 ¥%s，还剩 ¥%s（%.1f%%）没进逆回购，"
                    "一年少赚约 **¥%s**（每个交易日约 ¥%s）。"
                    % (format(hs.get("placed_cny") or 0, ",.0f"),
                       format(hs.get("idle_cny") or 0, ",.0f"),
                       (hs.get("idle_share") or 0.0) * 100.0,
                       format(hs.get("gap_annual_cny") or 0, ",.0f"),
                       format(hs.get("gap_daily_cny") or 0, ",.0f")))
            add("")
            add("- 登记于 %s（%s 天前，登记人 %s）。"
                % (hs.get("asof") or "—",
                   hs.get("age_days") if hs.get("age_days") is not None else "—",
                   hs.get("recorded_by") or "—"))
            if hs.get("stale"):
                add("- **这条登记已经过期**（超过 %d 天），先重新记一次再看缺口。" % PLACEMENT_MAX_AGE_DAYS)
            add("- 缺口按 %s 收盘年化 %.2f%%（%s）减活期 %.2f%% 计；利率是市场价，缺口会随它漂。"
                % (p.get("cash_leg"), float(hs.get("repo_rate_pct") or 0.0),
                   hs.get("repo_rate_date") or "—", float(hs.get("demand_rate_pct") or 0.0)))
        add("")
    add("## 账面与节奏")
    add("")
    add("- 定价用的收盘日：**%s**（数据状态 %s，滞后 %s 个交易日）"
        % (p["priced_bar"], p["feed_status"], p["feed_lag_days"]))
    add("- 这套组合上一次定稿：**%s**" % p["book_decided_at"])
    add("- 下次换仓：**%s**（还有 %s 个交易日）" % (p["next_rebalance_date"], p["next_decision_bars"]))
    fwd = p["forward"]
    if fwd["nav"]:
        add("- 前向账本：起始 %s 净值 1.0000 -> %s 净值 **%.4f**（%+.2f%%），共 %d 个交易日"
            % (fwd["inception"], fwd["as_of"], fwd["nav"], fwd["since_inception_pct"], fwd["bars"]))
        add("  - 这只是起步，不能当业绩看。")
    else:
        add("- 前向账本：尚未起算")
    vsb = p.get("vs_basket")
    if vsb:
        add("- 同时期对照（**买入并持有 ETF 篮子**，%s）：到 **%s** 篮子净值 %.4f，本账 %.4f，"
            "领先 **%+.2f 个百分点**"
            % (vsb["basis"], vsb["bar"], vsb["basket_nav"], vsb["book_nav"], vsb["excess_pp"]))
        add("  - 篮子=黄金/纳指/沪深300/国债四只等权、与本账同一换仓日与成交口径；"
            "这个差只说明这几天谁更好，不是长期超额，日子还短。")
        _h = vsb.get("horizon") or {}
        _mde = _h.get("min_detectable_edge_pp") or {}
        _yrs = _h.get("years_for_80pct_power") or {}
        _cand = _h.get("candidate_sources") or {}
        if _mde:
            _pairs = []
            for _k, _v in _yrs.items():
                _e = (_cand.get(_k) or {}).get("edge_pp_per_year")
                _pairs.append("%s %.2fpp/年 -> %s 年" % (_k.split(" (")[0], _e or 0.0, _v))
            add("  - 这个差要多大才算数：以本账对篮子的日波动（年化 %s）计，"
                "**12 个月只能分辨 %.1f 个百分点/年以上的差**（6 个月 %.1f、3 年 %.1f）；"
                "本账发表过的超额要 %s 才能被证明——所以这行数字是健康检查，不是判词。"
                % ("8.46%", _mde.get("1y", 0), _mde.get("6m", 0), _mde.get("3y", 0),
                   "；".join(_pairs) or "（未读到研究文件）"))
    add("")
    add("## 该期待什么（回测口径，扣成本后）")
    add("")
    add("| 组合口径 | 全窗年化 | 夏普 | 最大回撤 | 2020-2023 | 2024 起 |")
    add("|---|---|---|---|---|---|")
    for label, row in p["backtest_band"].items():
        def g(seg, k):
            v = (row.get(seg) or {}).get(k)
            return "—" if v is None else ("%.2f%%" % v if k == "cagr_pct" else
                                          ("%.2f%%" % v if k == "maxdd_pct" else "%.2f" % v))
        add("| %s | %s | %s | %s | %s | %s |"
            % (label, g("full", "cagr_pct"), g("full", "sharpe"), g("full", "maxdd_pct"),
               g("is", "cagr_pct"), g("oos", "cagr_pct")))
    add("")
    add("三行是同一套选券信号，区别只在名数和杠杆规则：第一行是你要下的这份账（5 名 + beta 覆盖 + 8bp 成本）；另两行是生产卡片跑的对照口径。同一决策日，票是卡片的子集。")
    add("")
    add("表里 \u2014 = 该口径没有拆 IS/OOS 分段，不是零。")
    if p.get("excess_pp") is not None and p.get("same_beta_benchmark") and p.get("ticket_book"):
        b = p["same_beta_benchmark"]
        bk = p["ticket_book"]
        add("")
        add("关键一句：**在同样的风险敞口下（beta 基准年化 %.2f%%、夏普 %.2f），这本账回测年化 %.2f%%、夏普 %.2f，多赚 %.2f 个百分点/年**——超额来自选券，不是来自加杠杆。"
            % (b["cagr"] * 100, b["sharpe"], bk["cagr"] * 100, bk["sharpe"], p["excess_pp"]))
    cr = p.get("carry_regime") or {}
    add("")
    add("## 这张表里的名数，是不是有实测撑腰")
    add("")
    fc = p.get("family_coherence") or {}
    if fc.get("verdict") == "ONE_WORLD":
        add("- **有。** %d 个宽度臂的判词全部算在同一张面板 `%s`（截至 %s）——卡片跑的那个名数是比出来的，"
            "不是配出来的。这张表之所以能对你说「该期待什么」，靠的就是这一句。"
            % (fc.get("arms") or 0, ((fc.get("panels") or [""])[0] or "?"),
               fc.get("evidence_cutoff")))
    elif fc.get("verdict"):
        add("- **没有。** 宽度臂家族已经收回了自己的判词（%s：%s）。所以上表里的名数只是配置，"
            "不是测出来的最优——读数照给，但别把它当「选过」的证据。"
            % (fc["verdict"], fc.get("detail") or "无细节"))
    else:
        add("- **不知道。** 读不到宽度臂家族的面（%s）。这是「没验」，不是「没问题」——"
            "上表的读数仍然有效，但它选的那个名数没有实测撑着。"
            % (fc.get("detail") or "家族面缺席"))
    add("")
    add("> 判词来源：`%s`。" % (fc.get("artifact") or "results/etf_book_phase_atlas_arms.json"))
    add("")
    add("## 这笔钱里有多少是「把现金借出去」挣的")
    add("")
    if not cr.get("available"):
        add("这一节没有数：`results/etf_book_return_regime.json` 不在盘上。跑 "
            "`python scripts/etf_book_return_regime.py run` 才会生成，不在这里现算。")
    else:
        rates = cr.get("cash_rates") or {}
        base = cr.get("base") or cr["rows"][-1]
        below = [r for r in cr["rows"] if r["beta"] < base["beta"]]
        above = [r for r in cr["rows"] if r["beta"] > base["beta"]]
        add("同一套引擎、同一批票、同样的 20 个交易日换仓和 8bp 成本，只把现金腿换成三种情形重算"
            "（历史真实报价 / 今天的报价固定不变 / 干脆 0 息）。风险和收益档位也一并列出，"
            "因为要不要多加风险是你可以自己选的事：")
        add("")
        add("| 风险档位 (beta) | 现金占比 | 回测年化（当时真实利率 %.2f%%） | 若一直只有今天的 %.2f%% | 若现金 0 息 | 最大回撤 |"
            % (rates.get("observed_mean_pct") or 0.0, rates.get("today_pct") or 0.0))
        add("|---|---|---|---|---|---|")
        for r in cr["rows"]:
            add("| %.2f%s | %.0f%% | %.2f%% | %.2f%% | %.2f%% | %s |"
                % (r["beta"], "（本单这一档）" if r is base else "",
                   (r["cash_share"] or 0.0) * 100, r["observed_pct"], r["flat_today_pct"],
                   r["zero_pct"],
                   "—" if r.get("maxdd_pct") is None else "%.2f%%" % r["maxdd_pct"]))
        add("")
        add("- **你现在这一档（beta %.2f）的 %.2f%% 里，%.2f 个百分点是把闲置现金借出去挣的**"
            "（占头条 %.0f%%）。就算逆回购掉到今天的 %.2f%% 不动，这本账还有 **%.2f%%**；"
            "就算现金一分利息都没有，也还有 **%.2f%%**——剩下来的钱来自选券，不是靠利息。"
            % (base["beta"], base["observed_pct"], base["carry_pp"],
               (100.0 * base["carry_pp"] / base["observed_pct"]) if base["observed_pct"] else 0.0,
               rates.get("today_pct") or 0.0, base["flat_today_pct"], base["zero_pct"]))
        if base.get("pp_per_100bp") is not None and cr.get("flags", {}).get("carry_positive"):
            add("- 利率每掉 100bp，这一档一年大约少 %.2f 个百分点（历史均值 %.2f%% -> 今天 %.2f%% 只差 %.0fbp，"
                "已经少赚约 %.2fpp）。这是个慢变量，不是每天看的东西。"
                % (base["pp_per_100bp"], rates.get("observed_mean_pct") or 0.0,
                   rates.get("today_pct") or 0.0,
                   100.0 * ((rates.get("observed_mean_pct") or 0.0) - (rates.get("today_pct") or 0.0)),
                   (base["observed_pct"] - base["flat_today_pct"])))
        if above:
            _hi = ("%.2f 档只剩 %.2fpp、%.2f 档只剩 %.2fpp"
                   % (above[0]["beta"], above[0]["carry_pp"],
                      above[-1]["beta"], above[-1]["carry_pp"])
                   if len(above) >= 2 else
                   "%.2f 档只剩 %.2fpp" % (above[0]["beta"], above[0]["carry_pp"]))
            add("- 档位越高、现金越少，这一项就越无关：%s。"
                "反过来，现金越多利息越要紧：%s 档有 %.0f%% 是现金，利息就撑起它头条的 %.0f%%。"
                "钱基本都投出去的时候，利不利率跟这本账没关系。"
                % (_hi,
                   "/".join("%.2f" % r["beta"] for r in below) or "更低",
                   100.0 * (below[-1].get("cash_share") or 0.0) if below else 0.0,
                   (100.0 * below[-1]["carry_pp"] / below[-1]["observed_pct"])
                   if below and below[-1]["observed_pct"] else 0.0))
        if above and above[0].get("maxdd_pct") is not None and base.get("maxdd_pct") is not None:
            add("- 想要更多钱就得扛更多波动，这个页不替你选：档位从 %.2f 提到 %.2f，"
                "回测年化 %.2f%% -> %.2f%%，代价是最大回撤 %.2f%% -> %.2f%%。"
                "今天这份单是按 %.2f 档开的。"
                % (base["beta"], above[0]["beta"], base["observed_pct"], above[0]["observed_pct"],
                   base["maxdd_pct"], above[0]["maxdd_pct"], base["beta"]))
        idy = cr.get("identity") or {}
        win = cr.get("window") or {}
        add("- 这段窗口是 **%s 起**（%s ~ %s），就是这张票自己在跑的那段，不是全史；"
            "全史口径看上一张表。%s"
            % (win.get("first") or "—", win.get("first") or "—", win.get("last") or "—",
               ("这一行是用你的票同一套引擎重算的（基准档 %.2f%% 与票面逐位对上）。"
                % (float(idy["published_cagr"]) * 100)) if idy.get("matched") else
               "重算结果与票面对不上，这张表不作为依据。"))
        add("")
        add("> 口径来源：`%s`（现金流按「前一根 bar 的报价 x 日历天数 / 365」计息，三种情形用同一约定；"
            "缺口日不计息并计数，不补默认值）。" % cr.get("source"))
    add("")
    ls = p.get("leg_split") or {}
    add("## 这笔钱是「一天里的哪一段」挣的")
    add("")
    if ls.get("status") != "ok":
        add("这一节没有数：拆解面%s（`%s`）。缺面就写「无法核验」，不拿零或「一致」顶上。"
            % ("未产出" if ls.get("status") == "absent" else "读不出",
               _rel(ls.get("artifact") or LEGS_JSON, ROOT).replace(os.sep, "/")))
        add("")
    else:
        pr_arm = ls["arms"].get("production") or {}
        bk = pr_arm.get("buckets_pp_per_year") or {}
        cw = (ls["arms"].get("control_ew") or {}).get("buckets_pp_per_year") or {}
        nf, npl = pr_arm.get("fill_bars") or 0, pr_arm.get("plain_bars") or 0
        drag = pr_arm.get("fill_bar_drag_pp_per_year") or 0.0
        carry = pr_arm.get("plain_carry_pp_per_year") or 0.0
        gross = (bk.get("overnight") or 0.0) + (bk.get("intraday") or 0.0)
        add("同一套引擎、同一批票、同样的换仓和成本，把上面那个回测年化按「钱是在哪一段挣的」拆成四桶——"
            "四桶按对数记账相加**精确等于**总额（不是大约等于），所以这一节不新增任何假设，"
            "只是把同一个数看仔细：")
        add("")
        add("| 桶 | 含义 | 一年几个百分点 |")
        add("|---|---|---|")
        add("| 安静 bar | %d 根「没有成交」的日子，持仓自己走 | %+.2f |" % (npl, bk.get("plain") or 0.0))
        add("| 隔夜 | 单子还没成交，旧持仓扛过收盘到开盘 | %+.2f |" % (bk.get("overnight") or 0.0))
        add("| 成交 bar 日内 | 新持仓在成交那天的开盘到收盘 | %+.2f |" % (bk.get("intraday") or 0.0))
        add("| 手续费 | 成交那一刻被收掉的 | %+.2f |" % (bk.get("toll") or 0.0))
        add("| **合计** | 与票面回测年化同一个词（对数口径） | **%+.2f** |" % (pr_arm.get("total_log_pp") or 0.0))
        add("")
        add("一句话：**%.2f 个百分点/年是在那 %d 根「什么都没发生」的 bar 上挣的；真正换手的那 %d 根 bar "
            "合计%s %.2f 个百分点**（手续费 + 开盘成交差）。"
            % (carry, npl, nf, "拖累" if drag < 0 else "贡献", abs(drag)))
        add("")
        add("- 这不是「少换手就多赚」的证据。把手续费当成 0，成交那一撮 bar 的毛腿**仍然是 %+.2f 个百分点**"
            "（隔夜 %+.2f + 日内 %+.2f）——问题不只在收费上，也在那一撮 bar 本身的方向上。"
            % (gross, bk.get("overnight") or 0.0, bk.get("intraday") or 0.0))
        if cw:
            add("- 同样这批票「平均买一遍」（等权、同样换仓同样成本）在安静 bar 上只有 **%+.2f**，"
                "这本账是 **%+.2f**——差的 %.2f 个百分点是选券给的，不是换手给的。"
                % (cw.get("plain") or 0.0, bk.get("plain") or 0.0,
                   (bk.get("plain") or 0.0) - (cw.get("plain") or 0.0)))
        add("")
        add("> 拆解面：`%s`（计价截止 %s；执行约定：%s；三臂=这本账 / 裸书 / 等权控制）。"
            % (_rel(ls.get("artifact") or LEGS_JSON, ROOT).replace(os.sep, "/"),
               ls.get("evidence_cutoff") or "—", ls.get("execution") or "—"))
        add("")
    add("## 换成年内能赚多少钱（按本单资金 ¥%s）" % format(p["money_cny"]["capital_cny"], ",.0f"))
    add("")
    add("同一批数字再换一把尺子，只做单位换算，不叠加任何新假设：")
    add("")
    add("| 项目 | 一年多少钱 | 怎么来的 |")
    add("|---|---|---|")
    mc = p["money_cny"]

    def y(v):
        return "—" if v is None else ("%s¥%s" % ("+" if v > 0 else "-", format(abs(v), ",.0f")))

    add("| 这本账回测期望 | %s | 年化 %s%% × 资金 |"
        % (y(mc["expected_annual_cny"]), "%.2f" % (p["ticket_book"]["cagr"] * 100) if p.get("ticket_book") else "—"))
    add("| 同风险基准（beta 覆盖） | %s | 基准年化 %s%% × 资金 |"
        % (y(mc["benchmark_annual_cny"]),
           "%.2f" % (p["same_beta_benchmark"]["cagr"] * 100) if p.get("same_beta_benchmark") else "—"))
    add("| **超额部分** | **%s** | 多赚 %.2f 个百分点 × 资金 |"
        % (y(mc["excess_annual_cny"]), p["excess_pp"] or 0.0))
    add("| 一次最坏回撤要亏 | %s | 最大回撤 %s%% × 资金 |"
        % (y(mc["worst_drawdown_cny"]),
           "%.2f" % (p["ticket_book"]["maxdd"] * 100) if p.get("ticket_book") else "—"))
    add("")
    add("读法：一年赚多少是回测期望，不是承诺；最坏回撤那一行才是你要能扛住的数。")
    add("")
    st = p.get("stress") or {}
    worst = st.get("worst") or {}
    if worst.get("1d") or worst.get("5d") or worst.get("20d"):
        add("## 最坏的日子长什么样（同一批票，整段历史）")
        add("")
        add("把今天这 %d 只票的权重重放回 %s~%s 的整段面板（现金 0 息），看最坏的连续几个交易日："
            % (len(p["order"]), st.get("first"), st.get("last")))
        add("")
        add("| 窗口 | 最差涨跌 | 折成钱 | 结束于 |")
        add("|---|---|---|---|")
        for n in STRESS_WINDOWS:
            row = worst.get("%dd" % n)
            if not row:
                add("| %d 个交易日 | — | — | — |" % n)
                continue
            add("| %d 个交易日 | %+.2f%% | %s | %s |"
                % (n, row["pct"], "—" if row.get("cny") is None else
                   ("%s¥%s" % ("+" if row["cny"] > 0 else "-", format(abs(row["cny"]), ",.0f"))),
                   row.get("end_date") or "—"))
        add("")
        add("读法：这是「同一批票、同样权重、最倒霉的一段」值多少钱，不是预测，也不是这本账实际走过的路"
            "（实际路径的回撤见上一张表的最大回撤列）。")
        add("")
        cont = st.get("contamination") or {}
        if cont.get("sentence"):
            add("**这张表最差的一天，是行情还是报价？** " + cont["sentence"])
            add("")
            raw_c, clean_c = cont.get("raw_worst") or {}, cont.get("clean_worst") or {}
            if clean_c.get("1d"):
                add("| 同一批票、同一权重 | 最差 1 日 | 最差 5 日 | 最差 20 日 |")
                add("|---|---|---|---|")
                for label, block in (("现在的面板", raw_c), ("把翻转压平后", clean_c)):
                    cells = []
                    for n in STRESS_WINDOWS:
                        r = block.get("%dd" % n)
                        cells.append("—" if not r else "%+.2f%%（%s）" % (r["pct"], r.get("end_date")))
                    add("| %s | %s |" % (label, " | ".join(cells)))
                add("")
    add("## 必须记住的四条")
    add("")
    for c in p["caveats"]:
        add("- " + c)
    add("")
    add("## 这三张纸是不是同一天算出来的")
    add("")
    _pf = p.get("priced_faces") or {}
    _fm = _pf.get("faces") or {}
    _shown = "卡片 %s / 票据 %s / 本页 %s" % (
        _fm.get("card") or "没写", _fm.get("ticket") or "没写", _fm.get("page") or "没写")
    if _pf.get("verdict") == "SAME_DAY":
        add("**同一天。** %s —— 你手上的单子、卡片和这一页，用的是同一个收盘价。" % _shown)
    elif _pf.get("verdict") == "DIFFERENT_DAYS":
        add("**不是同一天。** %s —— 落后的那张纸，报的是上一个收盘的价；先别按它下单。"
            % _shown)
    else:
        add("**无法判断。** %s —— 有一张纸没写自己的定价日，所以这里既不能说「一致」，"
            "也不能说「不一致」。" % _shown)
    add("")
    add("---")
    add("*生成脚本 scripts/etf_book_ceo_page.py｜证据截止 %s｜卡片与单子同一决策日=%s，"
        "三张纸同一定价日=%s（%s）*"
        % (p["evidence_cutoff"], p["agreement"]["same_decision_bar"],
           _pf.get("verdict") or "UNKNOWN", _shown))
    return "\n".join(L) + "\n"


def run():
    mid = machine_id()
    if not writer_allowed(mid):
        print("etf_book_ceo_page: host=%s is not the writer (host=%s) -- honest no-op, nothing written"
              % (mid, HOST))
        return 0
    page, today = build(with_stress=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    md_path = os.path.join(OUT_DIR, "LIVE-BOOK-%s.md" % today.replace("-", ""))
    js_path = os.path.join(OUT_DIR, "LIVE-BOOK-%s.json" % today.replace("-", ""))
    with open(md_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render_md(page))
    with open(js_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(page, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    # stable pointer for consumers that should not care about the date
    ptr = os.path.join(OUT_DIR, "latest.json")
    with open(ptr, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"generated_for_date": today,
                   "page": _rel(md_path, ROOT).replace("\\", "/"),
                   "json": _rel(js_path, ROOT).replace("\\", "/")},
                  fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print("LIVE-BOOK written: %s (order %d names, book %.0f, cash %.0f, next rebalance %s)"
          % (_rel(md_path, ROOT), len(page["order"]), page["book_amount_cny"],
             page["cash_amount_cny"], page["next_rebalance_date"]))
    return 0


def selftest():
    ok = 0
    total = 0

    def chk(name, cond, detail=""):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
            print("[%d/%d] PASS %s%s" % (ok, total, name, (" | " + detail) if detail else ""))
        else:
            print("[%d/%d] FAIL %s%s" % (ok, total, name, (" | " + detail) if detail else ""))
        return cond

    # 1. next-rebalance arithmetic on a hand fixture: the 3rd trading day after Fri
    cal = ["2026-10-23", "2026-10-26", "2026-10-27", "2026-10-28", "2026-10-29"]
    chk("L1 calendar: 3rd trading day after 2026-10-23", trading_days_after(cal, "2026-10-23", 3) == "2026-10-28",
        trading_days_after(cal, "2026-10-23", 3))
    chk("L2 calendar: anchor itself never counts", trading_days_after(cal, "2026-10-26", 1) == "2026-10-27")
    chk("L3 calendar: past the end -> None not a guess", trading_days_after(cal, "2026-10-26", 9) is None)
    chk("L4 calendar: degenerate n -> None", trading_days_after(cal, "2026-10-26", 0) is None)

    # 5. the live page's money must add up: order amounts + cash == capital
    page, _today = build()
    s = sum(float(o["amount_cny"] or 0) for o in page["order"])
    chk("L5 money: order sum + cash == capital",
        abs(s + page["cash_amount_cny"] - page["capital_cny"]) < 1.0,
        "sum %.2f + cash %.2f vs nav %.2f" % (s, page["cash_amount_cny"], page["capital_cny"]))
    chk("L6 money: book share == k_now", abs(page["book_amount_cny"] / page["capital_cny"] - page["k_now"]) < 0.002,
        "%.4f vs %.4f" % (page["book_amount_cny"] / page["capital_cny"], page["k_now"]))
    chk("L7 order non-empty and every row has a lot count",
        bool(page["order"]) and all((o["lots"] or 0) > 0 for o in page["order"]), "%d rows" % len(page["order"]))

    # 8. the page must actually say the things a human needs
    md = render_md(page)
    need = ["下单清单", "下次换仓", "该期待什么", "必须记住的四条"]
    missing = [k for k in need if k not in md]
    chk("L8 render: all required sections present", not missing, "missing=%s" % missing)
    chk("L9 render: no unformatted template leftovers", "{:" not in md and "%s" not in md and "%%" not in md)
    chk("L10 render: caveats carried onto the page",
        all(c.split("；")[0][:12] in md for c in page["caveats"]))
    chk("L11 page: next rebalance is a real calendar date",
        isinstance(page["next_rebalance_date"], str) and len(page["next_rebalance_date"]) == 10,
        str(page["next_rebalance_date"]))

    # 12. staleness is quoted, not hidden
    chk("L12 page: data freshness stated", page["feed_status"] is not None and page["priced_bar"] is not None,
        "%s lag=%s" % (page["feed_status"], page["feed_lag_days"]))

    # 13. the money block must be a pure unit change of numbers already on the page
    mc = page["money_cny"]
    tk_book = page.get("ticket_book") or {}
    exp_ok = (abs(mc["expected_annual_cny"] - tk_book["cagr"] * page["capital_cny"]) < 1.0
              if mc["expected_annual_cny"] is not None else mc["expected_annual_cny"] is None)
    chk("L13 money: annual yuan == backtest cagr x capital", exp_ok,
        "%s vs %.2f" % (mc["expected_annual_cny"], tk_book.get("cagr", 0) * page["capital_cny"]))
    chk("L14 money: excess yuan == excess_pp x capital",
        mc["excess_annual_cny"] is not None
        and abs(mc["excess_annual_cny"] - (page["excess_pp"] or 0.0) / 100.0 * page["capital_cny"]) < 1.0,
        "%s vs %s" % (mc["excess_annual_cny"], (page["excess_pp"] or 0.0) / 100.0 * page["capital_cny"]))
    chk("L15 money: absent inputs give None, never a zero that would read as 'earns nothing'",
        money_cny({}, 0.0)["expected_annual_cny"] is None
        and money_cny({}, 1000000.0)["excess_annual_cny"] is None
        and money_cny({"metrics": {"book": {"cagr": 0.1, "maxdd": -0.05}}}, 0.0)["expected_annual_cny"] is None,
        "empty ticket -> None; ticket without capital -> None")

    # 17. the page has to answer "do I trade today", and the answer must follow its own dates
    _base = {"book_decided_at": "2026-10-14", "priced_bar": "2026-10-26",
             "next_rebalance_date": "2026-11-11", "cost_bp_per_side": 8, "k_now": 0.5,
             "forward": {"bars": 3}}
    _hold = today_action(_base)
    chk("L17 action: holding + decision bar behind the priced bar -> hold, next date named",
        _hold["mode"] == "hold" and _hold["next_trade_date"] == "2026-11-11", _hold["mode"])
    _reb = today_action(dict(_base, book_decided_at="2026-10-26"))
    chk("L18 action: priced bar IS the decision bar -> rebalance (not hold)",
        _reb["mode"] == "rebalance", _reb["mode"])
    _open = today_action(dict(_base, forward={"bars": 0}))
    _none = today_action({"priced_bar": "2026-10-26", "forward": {"bars": 3}})
    chk("L19 action: no position -> open; missing date face -> unknown, never a guess",
        _open["mode"] == "open" and _none["mode"] == "unknown",
        "%s / %s" % (_open["mode"], _none["mode"]))
    chk("L20 action: re-trade cost is 2 sides x bp x 250 x book share on capital",
        _hold["cost_if_retraded_pct_per_year"] == 20.0,
        "%s vs 20.0 (%s)" % (_hold["cost_if_retraded_pct_per_year"], _hold["cost_basis"]))

    # 21. the LIVE page's own action line must agree with its own two dates and ledger
    _la = page["today_action"]
    _la_ok = (_la["mode"] in ("hold", "open", "rebalance")
              and (_la["mode"] == "rebalance") == (str(page["book_decided_at"]) == str(page["priced_bar"])
                                                   and bool(page["forward"]["bars"]))
              and (_la["mode"] != "hold" or _la["next_trade_date"] == page["next_rebalance_date"]))
    chk("L21 live page: action mode agrees with its own decision/priced bars and ledger",
        _la_ok, "%s decided=%s priced=%s bars=%s"
        % (_la["mode"], page["book_decided_at"], page["priced_bar"], page["forward"]["bars"]))
    # 22. single writer: only the host may write, and an unknown host must not write either
    chk("L22 guard: writer_allowed('bm-a') only",
        writer_allowed("bm-a") and not writer_allowed("bm-c") and not writer_allowed("bm-b")
        and not writer_allowed(None), "host=%s" % HOST)

    # 23-26. the stress block: hand fixture first, then the "absent panel is never zero" face
    import pandas as _pd
    _s = _pd.Series([0.01, -0.05, 0.02, -0.03, -0.04, 0.06, -0.08],
                    index=["2026-01-0%d" % i for i in range(1, 8)])
    _st = stress_stats(_s, windows=(1, 2, 5), capital=1000000.0)
    chk("L23 stress: worst 1-day is the single worst print, with its own end date",
        _st["worst"]["1d"]["pct"] == -8.0 and _st["worst"]["1d"]["end_date"] == "2026-01-07",
        str(_st["worst"]["1d"]))
    chk("L24 stress: the N-day window compounds its days and starts strictly after the anchor",
        -8.0 < _st["worst"]["5d"]["pct"] < -7.0 and _st["worst"]["5d"]["end_date"] == "2026-01-07",
        str(_st["worst"]["5d"]))
    chk("L25 stress: yuan is the percentage times this ticket's capital (a unit change only)",
        abs(_st["worst"]["1d"]["cny"] + 80000.0) < 1.0
        and abs(_st["worst"]["5d"]["cny"] / 1000000.0 * 100.0 - _st["worst"]["5d"]["pct"]) < 0.01,
        "%s / %s" % (_st["worst"]["1d"]["cny"], _st["worst"]["5d"]["cny"]))
    _no_cap = stress_stats(_s, windows=(1,), capital=None)["worst"]["1d"]
    chk("L26 stress: no panel / no capital gives None or a missing row, never a zero",
        stress_stats(None) is None and stress_stats(_pd.Series(dtype=float)) is None
        and _no_cap["cny"] is None and _no_cap["pct"] == -8.0,
        "empty panel -> None, capital-less yuan -> None")
    chk("L27 stress: a window longer than the history says 'no row', never a fabricated number",
        stress_stats(_s, windows=(50,))["worst"]["50d"] is None)
    # 27b-27e. the stress table's worst day has to be graded: a market day or a quote flip
    _cl = _pd.DataFrame({"A": [10.0, 10.0, 1.0, 1.05], "B": [10.0, 10.2, 10.3, 10.4]},
                        index=["2026-01-0%d" % i for i in range(1, 5)])
    _cleanA, _nflat, _thr = clean_panel(_cl)
    chk("L27b flip: the imported repair flattens a -90%% quote flip and keeps the level",
        _nflat == 1 and abs(float(_cleanA["A"].pct_change().iloc[2])) < 1e-12
        and abs(float(_cleanA["A"].iloc[3]) - 10.5) < 1e-9,
        "n=%s thr=%s last=%.4f" % (_nflat, _thr, float(_cleanA["A"].iloc[3])))
    _raws = stress_stats(book_returns(_cl, ["A"], [1.0]), capital=1000000.0)
    _cleans = stress_stats(book_returns(_cleanA, ["A"], [1.0]), capital=1000000.0)
    _cb = contamination_block(_raws, _cleans, _nflat, _thr)
    chk("L27c flip: the block names the raw worst day as a print and quotes both numbers",
        _cb["differs"] and _cb["raw_worst"]["1d"]["pct"] == -90.0
        and _cb["clean_worst"]["1d"]["pct"] == 0.0
        and ("-90.00%" in _cb["sentence"] and "repair_flips" in _cb["sentence"]),
        _cb["sentence"][:80])
    _cb_same = contamination_block(_raws, _raws, 0, _thr)
    chk("L27d flip: an unchanged worst day reads as a market move, not as clean-by-absence",
        (not _cb_same["differs"]) and ("行情" in _cb_same["sentence"])
        and ("-90.00%" in _cb_same["sentence"]), _cb_same["sentence"][:80])
    _cb_absent = contamination_block(_raws, None, 0, None)
    chk("L27e flip: no repaired panel -> no claim, never 'it is clean'",
        _cb_absent["clean_worst"]["1d"] is None and "不主张" in _cb_absent["sentence"],
        _cb_absent["sentence"][:80])

    # 28-29. the basket line must be the LEDGER's own number, and its absence must read as
    # absence -- re-pricing it here would be a second price source for the same claim
    _led = _load(LEDGER) if os.path.exists(LEDGER) else {}
    _bench = (_led.get("benchmark") or {}).get("latest") or {}
    if _bench.get("excess_pp") is not None:
        chk("L28 basket: page quotes the ledger's own benchmark, bar and navs to the digit",
            page["vs_basket"] is not None
            and page["vs_basket"]["bar"] == _bench.get("bar")
            and abs(page["vs_basket"]["excess_pp"] - _bench["excess_pp"]) < 1e-12
            and abs(page["vs_basket"]["book_nav"] - _bench["book_nav"]) < 1e-12,
            "ledger %s vs page %s" % (_bench.get("excess_pp"),
                                      (page["vs_basket"] or {}).get("excess_pp")))
    else:
        chk("L28 basket: page has no basket line when the ledger publishes none",
            page["vs_basket"] is None, "ledger benchmark latest absent -> page None")
    _md = render_md(dict(page, vs_basket={"bar": "2026-10-27", "book_nav": 1.004,
                                          "basket_nav": 0.9965, "excess_pp": 0.75,
                                          "basis": "等权 1/4、同一换仓日、次日开盘成交"}))
    chk("L29 basket: the rendered page carries the basket comparison and its caveat",
        "ETF 篮子" in _md and "+0.75" in _md and "不是长期超额" in _md,
        "rendered line present")

    # 30. the spread is not a verdict: the page must carry the horizon inside which the
    # number means anything (r1316). A power block that stays in the ledger is a decision
    # only a reader who opens the JSON gets.
    _pw = ((_led.get("benchmark") or {}).get("significance") or {}).get("power") or {}
    if _pw.get("available") and _bench.get("excess_pp") is not None:
        _md2 = render_md(dict(page, vs_basket=dict(page["vs_basket"])))
        _want = "%.1f 个百分点/年" % (_pw["min_detectable_edge_pp"]["1y"])
        chk("L30 basket: the page states the edge its 12-month view could resolve",
            _want in _md2 and "健康检查，不是判词" in _md2,
            "want=%s" % _want)
    else:
        chk("L30 basket: no horizon sentence when the ledger publishes no power block",
            page.get("vs_basket") is None
            or "健康检查，不是判词" not in render_md(dict(page)), "guard leg")

    # 31-34. the idle half is not 0% -- cash x the repo panel's own close, and an
    # unreadable panel stays None (a 0 would read as "the cash earns nothing", which is
    # the very case the reader needs to be warned about)
    import tempfile
    _td = tempfile.mkdtemp()
    with open(os.path.join(_td, "GC001.csv"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("date,open,high,low,close,volume\n")
        fh.write("2026-10-26,1.2,1.2,0.31,1.0,100\n")
        fh.write("2026-10-27,1.18,1.4,1,2.0,100\n")
    _cy = cash_yield(100000.0, panel_dir=_td)
    chk("L31 cash: annual yuan == cash x the panel's own close rate",
        _cy["rate_pct"] == 2.0 and _cy["rate_date"] == "2026-10-27"
        and _cy["annual_cny"] == 2000.0 and _cy["daily_cny"] == 8.0
        and _cy["rate_20d_pct"] == 1.5,
        "rate %.2f annual %s daily %s mean %s"
        % (_cy["rate_pct"], _cy["annual_cny"], _cy["daily_cny"], _cy["rate_20d_pct"]))
    _bad = tempfile.mkdtemp()
    with open(os.path.join(_bad, "GC001.csv"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("date,open,high,low,close,volume\n")
        fh.write("2026-10-27,900,900,900,900,100\n")
    chk("L32 cash: missing panel / zero cash / out-of-band print -> None, never 0",
        cash_yield(100000.0, panel_dir=os.path.join(_td, "nope"))["annual_cny"] is None
        and cash_yield(0.0, panel_dir=_td)["annual_cny"] is None
        and cash_yield(None, panel_dir=_td)["annual_cny"] is None
        and cash_yield(100000.0, panel_dir=_bad)["annual_cny"] is None,
        "absent / zero-cash / 900% print all None")
    _live = page["cash_yield"]
    _ok_live = (_live["annual_cny"] is None
                or (abs(_live["annual_cny"] - page["cash_amount_cny"] * _live["rate_pct"] / 100.0) < 1.0
                    and bool(_live["rate_date"])))
    chk("L33 live page: cash yuan == its own cash x its own rate, with the rate date",
        _ok_live, "cash %.0f rate %s @ %s -> %s"
        % (page["cash_amount_cny"], _live["rate_pct"], _live["rate_date"], _live["annual_cny"]))
    _md3 = render_md(dict(page, cash_yield={"leg": "GC001", "rate_pct": 1.09,
                                            "rate_date": "2026-10-27", "annual_cny": 5764.0,
                                            "daily_cny": 23.0, "rate_20d_pct": 1.1,
                                            "window": 20}))
    chk("L34 cash: the rendered page carries the rate, its date and the 'not a return source' line",
        "现金那一半在赚多少" in _md3 and "1.09%" in _md3 and "2026-10-27" in _md3
        and "+¥5,764" in _md3 and "不是收益来源" in _md3, "rendered cash block present")

    # 35-38. the ladder question ("should the cash sit in a longer repo?") is answered by
    # rolling each tenor on the panel's own calendar -- the adoption rule is a frozen
    # constant, and the verdict has to be recomputed from the cells, never typed in.
    import datetime as _dt

    def _panel(dirpath, symbol, pairs):
        with open(os.path.join(dirpath, "%s.csv" % symbol), "w",
                  encoding="utf-8", newline="\n") as fh:
            fh.write("date,open,high,low,close,volume\n")
            for d, v in pairs:
                fh.write("%s,%.4f,%.4f,%.4f,%.4f,100\n" % (d, v, v, v, v))

    def _sessions(start, n, weekdays=(0, 1, 2, 3, 4)):
        out = []
        d = start
        while len(out) < n:
            if d.weekday() in weekdays:
                out.append(d)
            d += _dt.timedelta(days=1)
        return out

    _lad = tempfile.mkdtemp()
    _days = _sessions(_dt.date(2021, 1, 4), 700)
    # flat calendar: every tenor quoted at 2.0% -> identical realised yield, so no
    # longer tenor may be adopted (an adoption here would be a rule bug, not an edge)
    for _sym in ("GC001", "GC003", "GC007", "GC014"):
        _panel(_lad, _sym, [(d.isoformat(), 2.0) for d in _days])
    _cl_flat = cash_ladder(100000.0, panel_dir=_lad)
    chk("L35 ladder: identical quotes -> nothing adopts, the 1-day leg is kept",
        _cl_flat["verdict"] == "KEEP-1D" and _cl_flat["pick"] == "GC001"
        and abs(_cl_flat["tenors"][0]["realized"]["1"]["realized_pct"] - 2.0) < 1e-9,
        "verdict=%s pick=%s base1y=%s"
        % (_cl_flat["verdict"], _cl_flat["pick"],
           _cl_flat["tenors"][0]["realized"]["1"]["realized_pct"]))
    chk("L36 ladder: rolling the 1-day leg covers every calendar day, no idle cash",
        _cl_flat["tenors"][0]["idle_days_1y"] == 0
        and _cl_flat["tenors"][0]["idle_share_1y"] == 0.0,
        "idle=%s share=%s" % (_cl_flat["tenors"][0]["idle_days_1y"],
                              _cl_flat["tenors"][0]["idle_share_1y"]))

    _lad2 = tempfile.mkdtemp()
    _panel(_lad2, "GC001", [(d.isoformat(), 2.0) for d in _days])
    _panel(_lad2, "GC007", [(d.isoformat(), 2.60) for d in _days])   # +60bp: clears 20bp
    _cl_wide = cash_ladder(100000.0, panel_dir=_lad2, tenors=("GC001", "GC007"))
    chk("L37 ladder: a +60bp tenor that never sits idle adopts, and its yuan follows it",
        _cl_wide["verdict"] == "ADOPT" and _cl_wide["pick"] == "GC007"
        and abs(_cl_wide["tenors"][1]["annual_cny_realized_1y"] - 2600.0) < 20.0,
        "verdict=%s pick=%s edge=%s yuan=%s"
        % (_cl_wide["verdict"], _cl_wide["pick"],
           _cl_wide["tenors"][1]["edge_bp"].get("1"),
           _cl_wide["tenors"][1]["annual_cny_realized_1y"]))
    _lad3 = tempfile.mkdtemp()
    _panel(_lad3, "GC001", [(d.isoformat(), 2.0) for d in _days])
    _panel(_lad3, "GC007", [(d.isoformat(), 2.10) for d in _days])   # +10bp: below the door
    _cl_thin = cash_ladder(100000.0, panel_dir=_lad3, tenors=("GC001", "GC007"))
    chk("L38 ladder: a +10bp edge is rejected by the frozen 20bp rule, not adopted",
        _cl_thin["verdict"] == "KEEP-1D" and _cl_thin["tenors"][1]["verdict"] == "REJECT"
        and "门槛" in (_cl_thin["tenors"][1]["reason"] or "")
        and "20 bp" in (_cl_thin["tenors"][1]["reason"] or ""),
        "verdict=%s arm=%s reason=%s"
        % (_cl_thin["verdict"], _cl_thin["tenors"][1]["verdict"],
           _cl_thin["tenors"][1]["reason"]))
    _cl_live = page.get("cash_ladder") or {}
    _ok_l = bool(_cl_live.get("tenors")) and _cl_live.get("verdict") in ("KEEP-1D", "ADOPT")
    _ok_l = _ok_l and all(
        (r.get("spot_pct") is None or 0.0 < float(r["spot_pct"]) < 200.0)
        for r in _cl_live.get("tenors") or [])
    _md4 = render_md(page)
    _ok_l = _ok_l and ("现金腿要不要换长一点的期限" in _md4
                       and ("继续一天期" in _md4 or "换 " in _md4)
                       and "空转" in _md4)
    chk("L39 ladder: the live page answers the ladder question with each tenor's own quote",
        _ok_l, "verdict=%s pick=%s rows=%d"
        % (_cl_live.get("verdict"), _cl_live.get("pick"),
           len(_cl_live.get("tenors") or [])))

    # 40-44. the handshake: advice ("buy the repo") vs account ("what was placed").
    # The failure mode this guards is the one the cash block has been advertising all
    # along -- a reader who did nothing reads the same page as one who did.
    _lad_h = tempfile.mkdtemp()
    _panel(_lad_h, "GC001", [(d.isoformat(), 2.0) for d in _days])
    _lad_v = cash_ladder(100000.0, panel_dir=_lad_h, tenors=("GC001",))
    _rec = tempfile.mkdtemp()
    _pfile = os.path.join(_rec, "cash_placement.json")

    _h_absent = cash_handshake(100000.0, _lad_v, placement_path=_pfile,
                               today="2026-10-29")
    chk("L40 handshake: no record -> UNRECORDED with a None gap (unread is not zero), and the worst case is stated",
        _h_absent["status"] == "UNRECORDED" and _h_absent["gap_annual_cny"] is None
        and _h_absent["idle_cny"] is None
        and abs(_h_absent["worst_case_annual_cny"] - 1950.0) < 1.0,
        "status=%s gap=%s worst=%s" % (_h_absent["status"], _h_absent["gap_annual_cny"],
                                       _h_absent["worst_case_annual_cny"]))

    def _write_placements(rec, by, asof, rows, demand=0.05):
        with open(_pfile, "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"schema": "cash-placement/v1", "asof": asof, "recorded_by": by,
                       "demand_rate_pct": demand, "placements": rows}, fh)
        return _pfile

    _write_placements(_rec, "unrecorded", "2026-10-29", [])
    _h_blank = cash_handshake(100000.0, _lad_v, placement_path=_pfile, today="2026-10-29")
    chk("L41 handshake: a file that exists but nobody filled is still UNRECORDED",
        _h_blank["status"] == "UNRECORDED" and _h_blank["gap_annual_cny"] is None,
        "status=%s" % _h_blank["status"])

    _write_placements(_rec, "jason", "2026-10-29",
                      [{"instrument": "GC001", "amount_cny": 40000.0,
                        "rate_pct": 1.9, "rate_date": "2026-10-28"}])
    _h_part = cash_handshake(100000.0, _lad_v, placement_path=_pfile, today="2026-10-29")
    chk("L42 handshake: half placed -> PARTIAL, idle and the gap are the panel's rate minus the declared demand rate",
        _h_part["status"] == "PARTIAL" and _h_part["idle_cny"] == 60000.0
        and abs(_h_part["gap_annual_cny"] - 1170.0) < 1.0
        and _h_part["gap_daily_cny"] == round(1170.0 / 250.0),
        "status=%s idle=%s gap=%s daily=%s" % (_h_part["status"], _h_part["idle_cny"],
                                               _h_part["gap_annual_cny"],
                                               _h_part["gap_daily_cny"]))

    _write_placements(_rec, "jason", "2026-10-29",
                      [{"instrument": "GC001", "amount_cny": 100000.0,
                        "rate_pct": 1.9, "rate_date": "2026-10-28"}])
    _h_full = cash_handshake(100000.0, _lad_v, placement_path=_pfile, today="2026-10-29")
    _write_placements(_rec, "jason", "2026-10-29",
                      [{"instrument": "GC001", "amount_cny": 100000.0, "rate_pct": 1.9},
                       {"instrument": "GC007", "amount_cny": 20000.0, "rate_pct": 2.0}])
    _h_over = cash_handshake(100000.0, _lad_v, placement_path=_pfile, today="2026-10-29")
    _write_placements(_rec, "jason", "2026-10-20",
                      [{"instrument": "GC001", "amount_cny": 100000.0, "rate_pct": 1.9}])
    _h_stale = cash_handshake(100000.0, _lad_v, placement_path=_pfile, today="2026-10-29")
    chk("L43 handshake: fully placed -> IN-PLACE at zero gap; more placed than the book holds -> OVER-PLACED, not silently clamped; an old record says so",
        _h_full["status"] == "IN-PLACE" and (_h_full["gap_annual_cny"] or 0) == 0.0
        and _h_over["status"] == "OVER-PLACED" and _h_over["idle_cny"] == 0.0
        and "对不上" in (_h_over["reason"] or "")
        and _h_stale["status"] == "IN-PLACE" and _h_stale["stale"] is True
        and "过期" in (_h_stale["reason"] or ""),
        "in-place=%s over=%s stale=%s" % (_h_full["status"], _h_over["status"],
                                          _h_stale["stale"]))

    _hs_live = page.get("cash_handshake") or {}
    _md5 = render_md(page)
    chk("L44 handshake: the live page renders the reconciliation and its status is one of the five honest states",
        "现金现在到底在哪" in _md5
        and _hs_live.get("status") in ("UNRECORDED", "IN-PLACE", "PARTIAL", "IDLE", "OVER-PLACED")
        and (("一年少赚约" in _md5) or ("没有缺口" in _md5) or ("对不上" in _md5)),
        "status=%s gap=%s" % (_hs_live.get("status"), _hs_live.get("gap_annual_cny")))

    # 45-47. the carry split: how much of the quoted headline is the repo leg. The failure
    # this guards is a page that quotes 11.33%/yr beside a 1.09% cash leg and leaves the
    # reader thinking selection earned all of it.
    _cr_live = page.get("carry_regime") or {}
    _md6 = render_md(page)
    if _cr_live.get("available"):
        _b = _cr_live.get("base") or {}
        _ok_c = ("这笔钱里有多少是" in _md6 and "%.2f%%" % (_b.get("zero_pct") or 0.0) in _md6
                 and "0 息" in _md6)
        chk("L45 carry split: the live page states what the book pays with a zero-rate cash leg",
            _ok_c, "base beta=%s observed=%s zero=%s" % (_b.get("beta"), _b.get("observed_pct"),
                                                         _b.get("zero_pct")))
        _rows = _cr_live.get("rows") or []
        _mono = all(r["observed_pct"] >= r["flat_today_pct"] >= r["zero_pct"] - 1e-9
                    for r in _rows)
        chk("L46 carry split: every published ladder row keeps observed >= today-flat >= zero",
            _mono and len(_rows) >= 2, "rows=%d" % len(_rows))
    else:
        _noart = carry_regime(path=os.path.join(tempfile.mkdtemp(), "absent.json"))
        chk("L45 carry split: absent artifact -> not available, and the section says so "
            "instead of inventing a number",
            _noart.get("available") is False and "这一节没有数" in _md6)
        chk("L46 carry split: absent artifact exposes no rows", _noart.get("rows") == [])

    _fake = os.path.join(tempfile.mkdtemp(), "regime.json")
    with open(_fake, "w", encoding="utf-8") as _fh:
        json.dump({"evidence_cutoff": "2026-10-29",
                   "cash_rates": {"observed_mean_pct": 2.0, "today_pct": 1.0},
                   "cells": [{"beta": 0.2, "regime": r, "cagr_pct": v, "maxdd_pct": -5.0,
                              "vol_pct": 8.0, "cash_share": 0.5, "first_bar": "2024-01-02",
                              "last_bar": "2026-10-29"}
                             for r, v in (("observed", 11.0), ("flat_today", 10.5), ("zero", 10.0))],
                   "gate": {"base_beta": 0.2, "flags": {"carry_positive": True},
                            "betas": {"0.2": {"observed_pct": 11.0, "flat_today_pct": 10.5,
                                             "zero_pct": 10.0, "carry_pp": 1.0,
                                             "cash_share": 0.5, "pp_per_100bp": 1.0}}}},
                  _fh)
    _fake_ok = carry_regime(path=_fake)
    chk("L47 carry split: a fixture artifact is read whole (base, ladder row, window, flags)",
        _fake_ok.get("available") is True and len(_fake_ok["rows"]) == 1
        and _fake_ok["base"]["beta"] == 0.2 and _fake_ok["base"]["pp_per_100bp"] == 1.0
        and _fake_ok["window"]["first"] == "2024-01-02",
        "rows=%d base=%s" % (len(_fake_ok.get("rows") or []), (_fake_ok.get("base") or {}).get("beta")))

    # 48-50. the bet count: five tickers are not five bets (r1172 face). The page must
    # quote the artifact's own sentence, and must never fall back to counting names.
    _sdir = os.path.dirname(os.path.abspath(__file__))
    if _sdir not in sys.path:
        sys.path.insert(0, _sdir)
    import etf_book_bets_face as _bfm
    _bf_live2 = bets_face()
    _bf_pub = _bfm.read_published()
    _md7 = render_md(page)
    chk("L48 bet count: the page goes through the one reader the ticket also quotes (no second copy)",
        _bf_live2.get("sentence") == _bf_pub.get("sentence")
        and _bf_live2.get("effective_bets") == _bf_pub.get("effective_bets"),
        "status=%s" % _bf_pub.get("status"))
    if _bf_pub.get("status") == "ok" and _bf_pub.get("sentence"):
        chk("L49 bet count: the live page prints the published sentence verbatim beside the order table",
            _bf_pub["sentence"] in _md7 and "这几只票到底有几个赌注" in _md7,
            "eff=%s nominal=%s" % (_bf_pub.get("effective_bets"), _bf_pub.get("nominal_bets")))
        chk("L50 bet count: the counts printed are the artifact's numbers, not a fresh computation",
            ("%.2f" % float(_bf_pub["effective_bets"])) in _md7
            and ("%.2f" % float(_bf_pub["risk_split"])) in _md7
            and ("数票数 %d 只" % round(float(_bf_pub["nominal_bets"]))) in _md7,
            "eff=%s nominal=%s split=%s" % (_bf_pub.get("effective_bets"),
                                            _bf_pub.get("nominal_bets"),
                                            _bf_pub.get("risk_split")))
    else:
        chk("L49 bet count: an absent artifact reads as absent, never as five bets",
            ("缺面不读成一个赌注" in _md7) and ("数方向" not in _md7),
            "status=%s" % _bf_pub.get("status"))

    # 51-53. the replay cache must key on what it was computed FROM, not on the date.
    # A repaired print (flip fix) rewrites today's worst window without moving today's
    # date, and a re-priced ticket changes the weights on the very same bar -- the cache
    # form of the staleness family closed in r1372-r1374.
    _pf = _pd.DataFrame({"AAA": [1.0, 1.01, 1.02, 1.0],
                         "BBB": [1.0, 0.99, 1.0, 1.01]},
                        index=_pd.to_datetime(["2020-01-02", "2020-01-03",
                                               "2020-01-06", "2020-01-07"]))
    _ord_a = [{"symbol": "AAA", "weight": 0.5}, {"symbol": "BBB", "weight": 0.5}]
    _d_a = stress_cache_digest(_pf, "2020-01-07", 1000000.0, STRESS_WINDOWS, _ord_a)
    chk("L51 stress cache: same bar, same weights, same panel -> same key (a hit is a hit)",
        _d_a == stress_cache_digest(_pf.copy(), "2020-01-07", 1000000.0,
                                    STRESS_WINDOWS, list(_ord_a)), "digest=%s" % _d_a[:12])
    _ord_b = [{"symbol": "AAA", "weight": 0.6}, {"symbol": "BBB", "weight": 0.4}]
    chk("L52 stress cache: re-pricing the ticket on the SAME bar changes the key",
        _d_a != stress_cache_digest(_pf, "2020-01-07", 1000000.0, STRESS_WINDOWS, _ord_b),
        "weights 50/50 vs 60/40")
    _pf2 = _pf.copy()
    _pf2.iloc[1, 0] = 1.03                  # a repaired print: same shape, same date
    chk("L53 stress cache: a repaired print on the SAME date changes the key",
        _d_a != stress_cache_digest(_pf2, "2020-01-07", 1000000.0, STRESS_WINDOWS, _ord_a),
        "identical bar and weights")

    # L54-L56 (r1184): the page quotes a band whose width was chosen out of a family of arm
    # cells. If that family never priced one panel, the band is a configuration -- and the
    # three states must read differently, or "unproven" and "proven" look identical.
    def _render_fc(fc):
        # the fixture is the LIVE page with one field swapped, so this leg fails only for
        # the reason it is about; a hand-built dict would rot the moment the page grows.
        _p, _ = build(with_stress=False)
        _p["family_coherence"] = fc
        return render_md(_p)

    _md_one = _render_fc({"verdict": "ONE_WORLD", "arms": 11, "panels": ["deadbeef"],
                          "evidence_cutoff": "2026-10-30",
                          "artifact": "results/etf_book_phase_atlas_arms.json"})
    _md_mixed = _render_fc({"verdict": "MIXED_WORLDS", "arms": 11, "panels": ["a", "b"],
                            "detail": "two panels", "evidence_cutoff": None,
                            "artifact": "results/etf_book_phase_atlas_arms.json"})
    _md_absent = _render_fc(None)
    chk("L54 family coherence: one world names the arm count, the panel and the cutoff",
        "有。" in _md_one and "11 个宽度臂" in _md_one and "deadbeef" in _md_one
        and "2026-10-30" in _md_one, "")
    chk("L55 family coherence: a withheld family reads 'no' and says the width is a config",
        "没有。" in _md_mixed and "MIXED_WORLDS" in _md_mixed
        and "ONE_WORLD" not in _md_mixed, "")
    chk("L56 family coherence: an absent face reads 'unknown', never a pass",
        "不知道。" in _md_absent and "ONE_WORLD" not in _md_absent
        and "没验" in _md_absent, "")

    # L57-L59 (r1185): the page used to answer "same priced bar = True" without ever printing
    # which day any of the three papers was priced on. A reader told "different" must be able
    # to see WHICH paper is stale, so all three days are printed and the three states read
    # differently -- an unknown must never borrow the wording of agreement.
    def _render_pf(pf):
        _p, _ = build(with_stress=False)
        _p["priced_faces"] = pf
        return render_md(_p)

    _md_same = _render_pf({"verdict": "SAME_DAY", "same_day": True, "missing": [],
                           "detail": "all three papers priced the 2026-10-30 bar",
                           "faces": {"card": "2026-10-30", "ticket": "2026-10-30",
                                     "page": "2026-10-30"}})
    _md_split = _render_pf({"verdict": "DIFFERENT_DAYS", "same_day": False, "missing": [],
                            "detail": "priced on different bars",
                            "faces": {"card": "2026-10-30", "ticket": "2026-10-30",
                                      "page": "2026-10-29"}})
    _md_unknown = _render_pf({"verdict": "UNKNOWN", "same_day": False, "missing": ["ticket"],
                              "detail": "no pricing day on: ticket",
                              "faces": {"card": "2026-10-30", "ticket": None,
                                        "page": "2026-10-30"}})
    # the section HEADING asks "are these three the same day" and therefore literally
    # contains the string 不是同一天, so every assertion anchors on the BOLDED verdict.
    chk("L57 priced days: all three papers print their own day and read 'same day'",
        "**同一天。**" in _md_same and _md_same.count("2026-10-30") >= 3
        and "**不是同一天。**" not in _md_same, "")
    chk("L58 priced days: a stale paper is named, not just denied",
        "**不是同一天。**" in _md_split and "本页 2026-10-29" in _md_split
        and "**同一天。**" not in _md_split, "")
    chk("L59 priced days: a paper with no day reads 'cannot tell', never agreement",
        "**无法判断。**" in _md_unknown and "**同一天。**" not in _md_unknown
        and "票据 没写" in _md_unknown, "")

    # L60-L62 (r1189): the page told the reader how much of the headline is cash lending
    # and how big the book is, but never where in the DAY the money accrues. The split
    # must be quoted verbatim from the artifact (not recomputed here), the three states
    # must read differently, and a broken face must print no numbers at all.
    def _render_legs(ls):
        _p, _ = build(with_stress=False)
        _p["leg_split"] = ls
        return render_md(_p)

    _legs_ok = {"status": "ok", "artifact": LEGS_JSON, "evidence_cutoff": "2026-10-30",
                "execution": "decide at close -> fill at next open",
                "arms": {"production": {"buckets_pp_per_year": {"plain": 9.83, "overnight": 0.16,
                                                                "intraday": -0.64, "toll": -1.15},
                                        "total_log_pp": 8.21,
                                        "plain_carry_pp_per_year": 9.83,
                                        "fill_bar_drag_pp_per_year": -1.62,
                                        "fill_bars": 83, "plain_bars": 1569},
                         "control_ew": {"buckets_pp_per_year": {"plain": 6.20}}}}
    _md_legs = _render_legs(_legs_ok)
    chk("L60 leg split: the four buckets and the fill-bar count reach the page verbatim",
        all(s in _md_legs for s in ("+9.83", "+0.16", "-0.64", "-1.15", "1569", "83")), "")
    chk("L61 leg split: a book that earns on quiet bars says so in one sentence",
        "什么都没发生" in _md_legs and "拖累 1.62" in _md_legs, "")
    _md_legs_gone = _render_legs({"status": "absent", "artifact": LEGS_JSON, "arms": {}})
    _md_legs_broken = _render_legs({"status": "broken", "artifact": LEGS_JSON,
                                    "detail": "production: buckets sum 5.000 != published 0.000",
                                    "arms": {}})
    chk("L62 leg split: absent or broken prints 'cannot verify' and no bucket numbers",
        "无法核验" in _md_legs_gone and "无法核验" in _md_legs_broken
        and "+9.83" not in _md_legs_gone and "+9.83" not in _md_legs_broken, "")

    print("\nSummary: %d/%d PASS%s" % (ok, total, "" if ok == total else " -- %d FAIL" % (total - ok)))
    return 0 if ok == total else 1


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "run":
        raise SystemExit(run())
    if cmd == "selftest":
        raise SystemExit(selftest())
    print("usage: etf_book_ceo_page.py [run|selftest]")
    raise SystemExit(2)