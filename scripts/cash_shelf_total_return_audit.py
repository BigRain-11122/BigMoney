"""CASH SHELF TOTAL RETURN AUDIT (r2047, bm-c)

The question
------------
The five-shelf table (r2041 -> r2046) reads *prices*.  An ETF that pays a
distribution drops on the ex-date and the drop is booked as a loss.  Which of
the published shelf readings is therefore missing income, and by how much?

Why this is not a re-derivation
-------------------------------
Nothing about prices, slippage, wait or carry is recomputed here.  Every
published number is read from `results/cash_shelf_year_by_year.json` (r2046)
and printed as the price-only line.  The only new measurement is the size of
the distribution the price line cannot see, taken from the authoritative
per-fund dividend face (`fund_etf_dividend_sina`, the same call
`update_fund_premium.py` uses for its ex-div guard) and cross-checked against
the observed ex-date gap in the local price panel.

Three calibers are put side by side, because each one fails in its own way:
  * PRICE-ONLY   -- what the shelf table prints today.  Blind to distributions.
  * THRESHOLD    -- `etf_book_cash_vehicle.consolidation_returns`, which zeroes
                    every drop above its reset threshold.  Right for a money ETF
                    whose drops *are* distributions, destructive for a credit ETF
                    whose drops are real price moves (511380: 278 "resets").
  * SOURCED      -- the ex-date list from the dividend face, added back at the
                    size the event actually had.  This face's reading.

Verdicts
--------
  NO_DISTRIBUTIONS_PRICE_ONLY_IS_RIGHT
  DISTRIBUTIONS_ALREADY_COUNTED_BY_THE_MONEY_READER
  PRICE_ONLY_UNDERSTATES_EXTRA           -- the published extra is a floor
  EVENT_NOT_EXPLAINED_BY_THE_DISTRIBUTION -- a big ex-date gap the amount cannot cover

Usage
-----
    python scripts/cash_shelf_total_return_audit.py run
    python scripts/cash_shelf_total_return_audit.py --check
    python scripts/cash_shelf_total_return_audit.py --selftest
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import pandas as pd  # noqa: E402

import etf_book_cash_vehicle as CV  # noqa: E402  (threshold reader, counterfactual)
import update_fund_premium as U  # noqa: E402  (sina dividend face + normaliser)

UP_FACE = "results/cash_shelf_year_by_year.json"
FACE = "results/cash_shelf_total_return_audit.json"
DOC = "research/CASH_SHELF_TOTAL_RETURN.md"
DIV_DIR = "data/fund_premium/dividends"

# A distribution event is only called "explained" when the observed ex-date gap
# is within this many bp of the dividend's own size.  Chosen before the first
# run from the 13 on-shelf 511880 events (observed-vs-implied error 0.5-10.1bp);
# 25 leaves room for a normal day of price drift without hiding a mismatch.
EXPLAINED_TOL_BP = 25.0
# The gap is measured on the first bar at/after the ex-date; a fund whose ex-date
# falls on a non-trading day shows up on the next bar.
DIV_FETCH_PAUSE_S = 1.5
# Income only counts as a correction of the published line above this size (pp/yr).
# 10bp/yr on a 565k ticket is 565 元/yr -- below that it is not worth a table row.
MATERIAL_PP = 0.10
# A published line sitting within this of (price-only + distributions) is on the
# sourced caliber already, whatever reader produced it.
ALREADY_COUNTED_TOL_PP = 0.15
# A year's extra moving by this much (pp) is worth a line in the page.
YEAR_SHIFT_PP = 0.50
# A published line this far from the sourced reading, in either direction, is a
# repair that is not a distribution.
OVER_REPAIR_MIN_PP = 0.15

MARK_BEGIN = "<!-- TOTAL-RETURN-TABLE:BEGIN -->"
MARK_END = "<!-- TOTAL-RETURN-TABLE:END -->"


def _p(rel):
    return os.path.join(ROOT, rel)


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _load(rel):
    with io.open(_p(rel), "r", encoding="utf-8") as f:
        return json.load(f)


def _content_sha(obj):
    blob = json.dumps(obj, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def panel_path(code):
    return "data/daily/sh%s.csv" % code


def load_panel(code):
    p = _p(panel_path(code))
    if not os.path.exists(p):
        return None
    px = pd.read_csv(p).set_index("date")["close"]
    px.index = pd.to_datetime(px.index)
    return px.astype(float)


# ------------------------------------------------------------------ dividends


def load_disk_events(code):
    """The local ex-div guard face, if this fund has one.  Rows are cumulative."""
    p = _p(os.path.join(DIV_DIR, "%s.csv" % code))
    if not os.path.exists(p):
        return None
    d = pd.read_csv(p)
    if len(d) == 0:
        return d
    d["ex_date"] = pd.to_datetime(d["ex_date"])
    return d.sort_values("ex_date").reset_index(drop=True)


def fetch_events(code):
    """Authoritative per-fund ex-date list, same call the ex-div guard uses."""
    import akshare as ak

    got = ak.fund_etf_dividend_sina(symbol=U._sina_symbol(code))
    d = U.normalize_dividends(got)
    if d is None or len(d) == 0:
        return pd.DataFrame({"ex_date": [], "cum_div": []})
    d = d.copy()
    d["ex_date"] = pd.to_datetime(d["ex_date"])
    return d.sort_values("ex_date").reset_index(drop=True)


def events_with_amounts(d):
    """cum_div is cumulative; the event's own size is the step between rows."""
    d = d.copy()
    d["amount"] = d["cum_div"].astype(float).diff()
    if len(d):
        d.loc[d.index[0], "amount"] = float(d["cum_div"].iloc[0])
    return d


def disk_vs_fresh(disk, fresh):
    """What a consumer diffing the *disk* cum values would book, event by event.

    The disk copy can be missing rows while keeping cumulative totals consistent,
    which makes a cumulative diff silently merge two distributions into one.
    """
    if disk is None or len(disk) == 0 or fresh is None or len(fresh) == 0:
        return None
    dm = {str(pd.Timestamp(r["ex_date"]).date()): float(r["cum_div"]) for _, r in disk.iterrows()}
    fm = {str(pd.Timestamp(r["ex_date"]).date()): float(r["cum_div"]) for _, r in fresh.iterrows()}
    missing = sorted(k for k in fm if k not in dm)
    dates = sorted(fm)
    per_event = {}
    for i, k in enumerate(dates):
        per_event[k] = fm[k] - (fm[dates[i - 1]] if i else 0.0)
    disagree = []
    prev_k = None
    for k in sorted(dm):
        if prev_k is not None:
            disk_step = dm[k] - dm[prev_k]
            inside = [x for x in dates if prev_k < x <= k]
            biggest = max([per_event[x] for x in inside], default=0.0)
            if len(inside) > 1 and disk_step > biggest + 5e-4:
                disagree.append({"to_date": k, "disk_step_amount": round(disk_step, 4),
                                 "largest_single_event": round(biggest, 4),
                                 "merged_dates": inside,
                                 "merged_total": round(sum(per_event[x] for x in inside), 4)})
        prev_k = k
    return {"disk_rows": int(len(disk)), "fresh_rows": int(len(fresh)),
            "dates_missing_on_disk": missing, "steps_that_over_book": disagree}


# ------------------------------------------------------------------ per event


def event_gap(px, ex_date):
    """Observed price change on the first bar at/after the ex-date, in bp."""
    if px is None or len(px) == 0:
        return None
    ex = pd.Timestamp(ex_date)
    before = px[px.index < ex]
    on_after = px[px.index >= ex]
    if len(before) == 0 or len(on_after) == 0:
        return None
    bar = on_after.index[0]
    prev = float(before.iloc[-1])
    if prev <= 0:
        return None
    return {"bar": str(bar.date()), "prev_close": prev, "close": float(on_after.iloc[0]),
            "observed_bp": round((float(on_after.iloc[0]) / prev - 1.0) * 1e4, 2)}


def event_yield_bp(px, ex_date, amount):
    """The income the price line cannot see: amount / previous close."""
    g = event_gap(px, ex_date)
    if g is None or amount is None or not pd.notna(amount):
        return None
    return round(float(amount) / g["prev_close"] * 1e4, 2), g


def shelf_events(code, px, window_start, window_end):
    """Fresh ex-date list for one shelf, calibrated against its own price panel."""
    notes = {}
    disk = None
    try:
        disk = load_disk_events(code)
        notes["disk_source"] = "data/fund_premium/dividends/%s.csv" % code if disk is not None else None
    except Exception as exc:                                  # pragma: no cover
        notes["disk_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:120])
    try:
        fresh = fetch_events(code)
        notes["caliber"] = "sina_fund_etf_dividend"
    except Exception as exc:
        if disk is None:
            raise
        fresh = disk
        notes["caliber"] = "disk_fallback_stale"
        notes["fetch_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:120])
    compare = disk_vs_fresh(disk, fresh)
    ev = events_with_amounts(fresh)
    rows = []
    for _, r in ev.iterrows():
        ex = pd.Timestamp(r["ex_date"])
        if px is not None and (ex < px.index[0] or ex > px.index[-1]):
            continue
        got = event_yield_bp(px, ex, r["amount"])
        if got is None:
            rows.append({"ex_date": str(ex.date()), "amount": round(float(r["amount"]), 4),
                         "yield_bp": None, "observed_bp": None, "error_bp": None,
                         "bar": None, "in_window": False})
            continue
        ybp, gap = got
        err = round(gap["observed_bp"] + ybp, 2) if ybp else None
        rows.append({
            "ex_date": str(ex.date()),
            "amount": round(float(r["amount"]), 4),
            "yield_bp": ybp,
            "observed_bp": gap["observed_bp"],
            "error_bp": err,
            "bar": gap["bar"],
            "in_window": bool(window_start <= ex <= window_end),
            "explained": bool(err is not None and abs(err) <= EXPLAINED_TOL_BP),
        })
    return rows, notes, compare


def annual_yields(rows):
    """Sum of event yields per calendar year, in bp (the income per year)."""
    out = {}
    for r in rows:
        if not r.get("in_window") or r.get("yield_bp") is None:
            continue
        y = str(r["ex_date"])[:4]
        out[y] = round(out.get(y, 0.0) + float(r["yield_bp"]), 2)
    return out


def window_yield_bp(rows, bars, bars_per_year):
    """Same annualisation ruler the chain uses: per-bar income x bars per year."""
    total = sum(float(r["yield_bp"]) for r in rows if r.get("in_window") and r.get("yield_bp") is not None)
    if not bars or not bars_per_year:
        return 0.0, round(total, 2)
    return round(total / bars * bars_per_year, 2), round(total, 2)


def threshold_reader_gap(code, px, window_start, window_end, sourced_cagr_pct):
    """How far the blanket reset reader would land from the sourced reading."""
    try:
        base = CV.load_etf(code)
        rets, resets = CV.consolidation_returns(base)
    except Exception as exc:                                  # pragma: no cover
        return {"error": "%s: %s" % (type(exc).__name__, str(exc)[:120])}
    if rets is None or len(rets) < 40:
        return {"error": "too few bars"}
    r = rets[(rets.index >= pd.Timestamp(window_start)) & (rets.index <= pd.Timestamp(window_end))]
    yrs = (r.index[-1] - r.index[0]).days / 365.25
    if yrs <= 0 or len(r) < 2:
        return {"error": "window too short"}
    cagr = ((1.0 + r).prod() ** (1.0 / yrs) - 1.0) * 100.0
    return {"resets_detected": int(len(resets)) if resets is not None else None,
            "threshold_cagr_pct": round(float(cagr), 4),
            "gap_vs_sourced_pp": round(float(cagr) - float(sourced_cagr_pct), 4)}


# ------------------------------------------------------------------ the face


def verdict_for(code, klass, rows, events_in_window, added_pp, published_vs_sourced_pp, gap_to_price_only_pp):
    """Which caliber the published line is on, and what it costs.

    added_pp              -- income the price line cannot see, pp per year
    published_vs_sourced  -- published cagr minus (price-only + distributions), pp
    """
    tags = []
    unexplained = [r for r in rows if r.get("in_window") and r.get("explained") is False]
    if unexplained:
        tags.append("EVENT_NOT_EXPLAINED_BY_THE_DISTRIBUTION")
    if events_in_window == 0:
        tags.append("NO_DISTRIBUTIONS_PRICE_ONLY_IS_RIGHT")
        if abs(published_vs_sourced_pp) >= OVER_REPAIR_MIN_PP:
            tags.append("PUBLISHED_LINE_IS_ABOVE_PRICE_ONLY_WITHOUT_A_DISTRIBUTION")
    elif abs(published_vs_sourced_pp) <= ALREADY_COUNTED_TOL_PP:
        tags.append("DISTRIBUTIONS_ALREADY_COUNTED_BY_THE_MONEY_READER")
    elif published_vs_sourced_pp < 0 and -published_vs_sourced_pp >= MATERIAL_PP:
        tags.append("PRICE_ONLY_UNDERSTATES_EXTRA")
    elif published_vs_sourced_pp < 0:
        tags.append("DISTRIBUTIONS_TOO_SMALL_TO_MOVE_THE_READING")
    elif gap_to_price_only_pp is not None and abs(gap_to_price_only_pp) >= OVER_REPAIR_MIN_PP:
        tags.append("PUBLISHED_LINE_IS_NOT_PRICE_ONLY")
    return tags


def _ss_start():
    import cb_parking_shelf_at_size as SS

    return SS.START


def _repaired_panel():
    """The same panel and the same repair r2046 reads, built once per process."""
    global _PANEL_CACHE
    if _PANEL_CACHE is None:
        import etf_composite_pf as E
        import etf_equity_alpha as A

        close_all, open_all, _amt, _feats = E.build_panel()
        close_all, _o2, _n = A.repair_flips(close_all, open_all)
        _PANEL_CACHE = (close_all, str(close_all.index[-1].date()))
    return _PANEL_CACHE


_PANEL_CACHE = None


def caliber_series(code, klass):
    """The price series the chain itself feeds that shelf's reader."""
    if klass == "money":
        return CV.load_etf(code)
    close_all, _end = _repaired_panel()
    return close_all[code]


def price_only_line(px, start, end):
    """Price-only buy-and-hold, same cost convention and same start as the shelf table."""
    import cb_parking_shelf_at_size as SS

    rets = SS.buy_hold_rets(px, str(start), str(end))
    if rets is None or len(rets) < 40:
        return None, None
    rets = rets.copy()
    rets.iloc[0] -= SS.round_trip_bp(SS.COST_BP_SIDE) / 1e4
    yrs = (rets.index[-1] - rets.index[0]).days / 365.25
    if yrs <= 0:
        return None, len(rets)
    return round(float(((1.0 + rets).prod() ** (1.0 / yrs) - 1.0) * 100.0), 4), len(rets)


def build():
    import cb_parking_shelf_at_size as SS

    up = _load(UP_FACE)
    ticket = float(up["headline"]["ticket_cash_cny"])
    budget = float(up["headline"]["budget_sessions"])
    _close_all, panel_end = _repaired_panel()
    start = pd.Timestamp(SS.START)
    end = pd.Timestamp(panel_end)
    rows = []
    for src in up["rows"]:
        code = src["code"]
        klass = src["class"]
        px = caliber_series(code, klass)
        ev_rows, notes, compare = shelf_events(code, px, start, end)
        bars = int(src["index_bars"])
        bpy = float(src["bars_per_year"])
        wy_bp, wy_total_bp = window_yield_bp(ev_rows, bars, bpy)
        po_cagr, po_bars = price_only_line(px, SS.START, panel_end)
        if po_cagr is None:
            raise KeyError("%s has too few bars for the price-only line" % code)
        published_cagr = float(src["window_cagr_pct"])
        published_pp = float(src["window_extra_pp"])
        repo_cagr = float(src["repo_cagr_pct"])
        sourced_cagr = round(po_cagr + wy_bp / 100.0, 4)
        sourced_extra_pp = round(sourced_cagr - repo_cagr, 4)
        sourced_extra_cny = round(sourced_extra_pp / 100.0 * ticket, 2)
        threshold = threshold_reader_gap(code, px, str(start.date()), str(end.date()), sourced_cagr)
        # The per-year rows inherit the caliber of the published window line: adding
        # the distribution again to a year that the money reader already zeroes would
        # book the same income twice (the mistake this face exists to catch).
        published_is_price_only = abs(published_cagr - po_cagr) < 0.02
        years = {}
        ay = annual_yields(ev_rows)
        for y, v in src.get("years", {}).items():
            y_bp = float(ay.get(y, 0.0)) if published_is_price_only else 0.0
            tot = round(float(v["shelf_pct"]) + y_bp / 100.0, 4)
            sep = round(tot - float(v["repo_pct"]), 4)
            years[y] = {
                "bars": int(v["bars"]),
                "full_year": bool(v["full_year"]),
                "published_shelf_pct": v["shelf_pct"],
                "distribution_bp": y_bp,
                "sourced_shelf_pct": tot,
                "repo_pct": v["repo_pct"],
                "published_extra_pp": v["extra_pp"],
                "sourced_extra_pp": sep,
                "sourced_extra_cny": round(sep / 100.0 * ticket, 2),
                "shift_pp": round(sep - float(v["extra_pp"] or 0.0), 4),
                "material": bool(abs(sep - float(v["extra_pp"] or 0.0)) >= YEAR_SHIFT_PP),
                "sign_flips": bool((v["extra_pp"] or 0) * (sep or 0) < 0),
            }
        rows.append({
            "code": code,
            "label": src.get("label"),
            "class": klass,
            "window": {"first": src["index_first"], "last": src["index_last"], "bars": bars},
            "dividend_source": notes,
            "events": ev_rows,
            "events_in_window": len([r for r in ev_rows if r.get("in_window")]),
            "distribution_yield_bp_per_year": wy_bp,
            "distribution_yield_total_bp": wy_total_bp,
            "price_only": {
                "cagr_pct": po_cagr,
                "bars": po_bars,
                "source": ("recomputed from data/daily/sh%s.csv: buy-and-hold, "
                           "%.1fbp round trip on the entry bar (r2041 convention)" % (code, 2.0 * 2.0)),
            },
            "published": {
                "cagr_pct": published_cagr,
                "repo_cagr_pct": repo_cagr,
                "extra_pp": published_pp,
                "extra_cny": src["window_extra_cny"],
                "own_net_cagr_pct": src.get("published_own_net_cagr_pct"),
                "gap_to_price_only_pp": round(published_cagr - po_cagr, 4),
                "is_price_only": bool(published_is_price_only),
            },
            "sourced": {
                "cagr_pct": sourced_cagr,
                "extra_pp": sourced_extra_pp,
                "extra_cny": sourced_extra_cny,
                "cny_added": round(sourced_extra_cny - float(src["window_extra_cny"]), 2),
                "added_pp": round(sourced_cagr - published_cagr, 4),
            },
            "threshold_reader": threshold,
            "disk_vs_fresh": compare,
            "verdict": verdict_for(code, klass, ev_rows,
                                   len([r for r in ev_rows if r.get("in_window")]),
                                   wy_bp / 100.0, round(published_cagr - sourced_cagr, 4),
                                   round(published_cagr - po_cagr, 4)),
            "years": years,
        })
    headline = _headline(rows, ticket, budget)
    face = {
        "schema": "cash_shelf_total_return_audit.v1",
        "artifact": FACE,
        "generated": pd.Timestamp.now().strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": up["evidence_cutoff"],
        "window": up.get("window"),
        "question": ("The shelf table reads prices.  Which readings are missing the "
                     "distributions the funds actually paid, and by how much?"),
        "upstream": {
            "face": UP_FACE,
            "sha256": _sha(_p(UP_FACE)),
            "ticket_cash_cny": ticket,
            "budget_sessions": budget,
            "adoption": up.get("adoption"),
        },
        "calibration": {
            "explained_tol_bp": EXPLAINED_TOL_BP,
            "why": ("chosen before the first run from the 13 on-shelf 511880 events "
                    "(observed ex-date gap minus the dividend's own size: 0.5 to 10.1bp)"),
        },
        "panels": {r["code"]: _sha(_p(panel_path(r["code"]))) for r in rows
                   if os.path.exists(_p(panel_path(r["code"])))},
        "headline": headline,
        "rows": rows,
        "content_sha256": "",
    }
    face["content_sha256"] = _content_sha({k: v for k, v in face.items() if k != "content_sha256"})
    return face


def _headline(rows, ticket, budget):
    under_stated = []
    for r in rows:
        if "PRICE_ONLY_UNDERSTATES_EXTRA" in r["verdict"]:
            under_stated.append({
                "code": r["code"],
                "published_extra_cny": r["published"]["extra_cny"],
                "sourced_extra_cny": r["sourced"]["extra_cny"],
                "cny_added": r["sourced"]["cny_added"],
                "added_pp": r["sourced"]["added_pp"],
            })
    over_repair = []
    for r in rows:
        gap = r["threshold_reader"].get("gap_vs_sourced_pp")
        if gap is not None and abs(gap) >= OVER_REPAIR_MIN_PP:
            over_repair.append({"code": r["code"],
                                "resets_detected": r["threshold_reader"].get("resets_detected"),
                                "gap_vs_sourced_pp": gap})
    above = []
    for r in rows:
        if "PUBLISHED_LINE_IS_ABOVE_PRICE_ONLY_WITHOUT_A_DISTRIBUTION" in r["verdict"]:
            above.append({"code": r["code"],
                          "gap_to_price_only_pp": r["published"]["gap_to_price_only_pp"],
                          "cny": round(r["published"]["gap_to_price_only_pp"] / 100.0 * ticket, 2)})
    movers = []
    for r in rows:
        for y, v in r["years"].items():
            if v["material"] and v["full_year"]:
                movers.append({"code": r["code"], "year": y,
                               "published_extra_pp": v["published_extra_pp"],
                               "sourced_extra_pp": v["sourced_extra_pp"],
                               "shift_pp": v["shift_pp"],
                               "sign_flips": v["sign_flips"]})
    return {
        "ticket_cash_cny": ticket,
        "budget_sessions": budget,
        "price_only_understates": under_stated,
        "published_above_price_only_without_a_distribution": above,
        "threshold_reader_over_repairs": over_repair,
        "year_verdicts_that_move": movers,
        "no_distributions": [r["code"] for r in rows if "NO_DISTRIBUTIONS_PRICE_ONLY_IS_RIGHT" in r["verdict"]],
        "already_counted": [r["code"] for r in rows if "DISTRIBUTIONS_ALREADY_COUNTED_BY_THE_MONEY_READER" in r["verdict"]],
        "disk_face_missing_events": [{"code": r["code"], "dates": r["disk_vs_fresh"]["dates_missing_on_disk"]}
                                     for r in rows if r["disk_vs_fresh"] and r["disk_vs_fresh"]["dates_missing_on_disk"]],
        "verdict_counts": _counts([t for r in rows for t in r["verdict"]]),
    }


def _counts(tags):
    out = {}
    for t in tags:
        out[t] = out.get(t, 0) + 1
    return dict(sorted(out.items()))


def _f(v, nd=2, dash="n/a"):
    if v is None:
        return dash
    try:
        return ("%%.%df" % nd) % float(v)
    except (TypeError, ValueError):
        return dash


def table_row(r):
    """One shelf's rendered row, built from the face and nothing else."""
    return ("| %s | %s | %d | %s%% | %s | %s%% | %s%%（%s 元） | %s | %s |"
            % (r["code"], r["class"], r["events_in_window"],
               _f(r["price_only"]["cagr_pct"], 2),
               _f(r["distribution_yield_bp_per_year"], 1),
               _f(r["sourced"]["cagr_pct"], 2),
               _f(r["published"]["cagr_pct"], 2),
               _f(r["published"]["extra_cny"], 0),
               _f(r["sourced"]["cny_added"], 0),
               " · ".join(r["verdict"])))


def render_block(face):
    h = face["headline"]
    lines = []
    lines.append("> 票面 = %s 元 · 等待预算 = %s 个交易日（预算与口径都从 r2045 的 `adoption` 块读，本面不另立标准）"
                 % (_f(h["ticket_cash_cny"], 0), _f(h["budget_sessions"], 0)))
    lines.append("")
    lines.append("| 货架 | 类 | 分红(窗内) | 只读价格 | 分红年化 (bp) | 价格+分红 | 公布（r2046 这一行） | 差额 (元/年) | 判词 |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for r in face["rows"]:
        lines.append(table_row(r))
    lines.append("")
    if h["price_only_understates"]:
        bits = ["%s 每年少算 **%s 元**（公布 %s 元 → 价格+分红 %s 元，差 %s pp）"
                % (u["code"], _f(u["cny_added"], 0), _f(u["published_extra_cny"], 0),
                   _f(u["sourced_extra_cny"], 0), _f(u["added_pp"], 2))
                for u in h["price_only_understates"]]
        lines.append("**公布读数偏低**：" + "；".join(bits) + "。")
    if h["already_counted"]:
        lines.append("**已经算进去了**：%s —— 货币读取器把除息日当重置记零，与「价格+分红」"
                     "只差 %s pp，所以它的表必须原样读，不能再加一次分红。"
                     % ("、".join(h["already_counted"]),
                        _f(next((abs(r["published"]["cagr_pct"] - r["sourced"]["cagr_pct"])
                                 for r in face["rows"] if r["code"] in h["already_counted"]), None), 2)))
    if h["published_above_price_only_without_a_distribution"]:
        bits = ["%s 公布读数比裸价格高 **%s pp**（约 %s 元/年）而它一笔分红都没有——"
                "这是把一次真实下跌当成了重置"
                % (a["code"], _f(a["gap_to_price_only_pp"], 2), _f(a["cny"], 0))
                for a in h["published_above_price_only_without_a_distribution"]]
        lines.append("**公布读数偏高**：" + "；".join(bits) + "。")
    if h["no_distributions"]:
        lines.append("**没有分红**：%s —— 这几只不发分红，价格口径就是全收益口径。" % "、".join(h["no_distributions"]))
    if h["threshold_reader_over_repairs"]:
        bits = ["%s 把 %s 个下跌当成分红（年化抬高 **%s pp**）"
                % (o["code"], o["resets_detected"], _f(o["gap_vs_sourced_pp"], 2))
                for o in h["threshold_reader_over_repairs"]]
        money_fix = [r for r in face["rows"]
                     if r["class"] == "money" and r["events_in_window"] == 0
                     and r["threshold_reader"].get("gap_vs_sourced_pp") is not None
                     and abs(r["threshold_reader"]["gap_vs_sourced_pp"]) >= OVER_REPAIR_MIN_PP]
        tail = "。它只对 class=money 启用"
        if money_fix:
            m = money_fix[0]
            tail += ("；%s 那一条，r2046 的翻转中性化已经抵掉（公布读数只比裸价格高 %s pp）"
                     % (m["code"], _f(m["published"]["gap_to_price_only_pp"], 2)))
        tail += "——但任何把信用债 ETF 归到 money 的改动都会立刻造出假收益。"
        lines.append("**一刀切也不行**：把重置读取器套到信用债货架上，" + "；".join(bits) + tail)
    if h["disk_face_missing_events"]:
        bits = ["%s 少 %d 个除息日（%s）" % (d["code"], len(d["dates"]), "、".join(d["dates"]))
                for d in h["disk_face_missing_events"]]
        lines.append("**本地面也有缺口**：" + "；".join(bits) +
                     "。按本地累积值做差会把两次分红并成一次——本面每次运行都直取来源，不读本地累积值。")
    if h["year_verdicts_that_move"]:
        bits = ["%s %s 年：%s → %s pp%s"
                % (m["code"], m["year"], _f(m["published_extra_pp"], 2), _f(m["sourced_extra_pp"], 2),
                   "（亏赚翻面）" if m["sign_flips"] else "")
                for m in h["year_verdicts_that_move"][:8]]
        lines.append("**超额移动 ≥%s pp 的年份**：" % _f(YEAR_SHIFT_PP, 1) + "；".join(bits) + "。")
    lines.append("")
    lines.append("判词计数：" + " · ".join("%s=%d" % (k, v) for k, v in h["verdict_counts"].items()))
    return "\n".join(lines)


def render_doc(face):
    h = face["headline"]
    head = [
        "# 五个货架，谁的分红被价格挡住了",
        "",
        "> 证据截止 %s · 生成 %s · 票面 %s 元" % (face["evidence_cutoff"], face["generated"],
                                              _f(h["ticket_cash_cny"], 0)),
        "> 上游：`%s`（r2046）· 分红面：`fund_etf_dividend_sina`（与 `update_fund_premium` 的除息守卫同一次调用）"
        % UP_FACE,
        "",
        "## 一句话",
        "",
    ]
    if h["price_only_understates"]:
        bits = ["%s 每年少算 **%s 元**（公布 %s 元 → 价格+分红 %s 元，差 %s pp）"
                % (u["code"], _f(u["cny_added"], 0), _f(u["published_extra_cny"], 0),
                   _f(u["sourced_extra_cny"], 0), _f(u["added_pp"], 2))
                for u in h["price_only_understates"]]
        head.append("> 公布读数偏低的是 %s：%s。这不是预测，是把已经记在账上的分红加回去。"
                    % ("、".join(u["code"] for u in h["price_only_understates"]), "；".join(bits)))
    head += [
        "",
        "## 为什么要单独做这一步",
        "",
        "r2041 起这一族面全部用价格算收益（买入持有、进场 bar 收 4bp 往返）。"
        "债券/货币 ETF 付息那天价格会掉一截，掉的那一截被当成本金亏损记进收益里——"
        "钱其实以现金形式进了持有人口袋，只是不在这条价格序列上。",
        "",
        "这条链之前有一半防护：`etf_book_cash_vehicle.consolidation_returns` 会把超过阈值的单日下跌当「重置」记零，"
        "但它只在 `class=money` 上启用，而且它分不清「分红」和「真的跌」。本面把两边都量出来："
        "漏记（价格口径）与过记（阈值读取器）。",
        "",
        "## 读数",
        "",
        MARK_BEGIN,
        render_block(face),
        MARK_END,
        "",
        "## 校准：掉的那一截就是分红吗",
        "",
        "每一笔除息日都做一次对照——把「价格实际掉了多少 bp」与「分红金额 ÷ 前一交易日收盘」放在一起。"
        "容差 %s bp 是第一次运行前定的，取自在架 13 笔 511880 事件（误差 0.5–10.1bp）。"
        % _f(EXPLAINED_TOL_BP, 0),
        "",
    ]
    cal = []
    for r in face["rows"]:
        for e in r["events"]:
            if e.get("in_window") and e.get("observed_bp") is not None:
                cal.append("| %s | %s | %s | %s | %s | %s |"
                           % (r["code"], e["ex_date"], _f(e["amount"], 4),
                              _f(e["yield_bp"], 1), _f(e["observed_bp"], 1), _f(e["error_bp"], 1)))
    if cal:
        head += ["| 货架 | 除息日 | 每份分红 | 应有 (bp) | 实际 (bp) | 残差 (bp) |", "|---|---|---|---|---|---|"]
        head += cal
    head += [
        "",
        "## 怎么用",
        "",
        "- 判词只回答「公布的超额是不是漏了分红」。容量（r2041）、摆动（r2042）、排期（r2043）、"
        "在途 carry（r2044）、排队天数（r2045/r2046）各自照旧。",
        "- 本面不改任何上游数字：公布列是 r2046 原样，来源口径列是「公布 + 分红」。谁要下单用哪一列，由下游决定。",
        "- 分红是历史事件，不是承诺：一只基金明年可以选择不分。",
        "",
        "## 未验证（如实）",
        "",
        "- 本面不重算价格、滑点、等待、carry：全部继承 r2043–r2046。",
        "- 分红金额是「每份」口径；份额折算类事件（拆分/合并）不在射程内。",
        "- 分红面覆盖的是 ETF 分红，不含基金内部结转的未分配收益（那部分会体现在净值里、不一定体现为价格缺口）。",
        "- 价格面板是收盘价，除息日当天若同时有大额申赎，残差会被混进去；本面的残差列用于看这一点，不做剔除。",
        "",
    ]
    return "\n".join(head)


# ------------------------------------------------------------------ commands


def cmd_run():
    face = build()
    with io.open(_p(FACE), "w", encoding="utf-8", newline="\n") as f:
        json.dump(face, f, ensure_ascii=False, indent=1)
        f.write("\n")
    doc_path = _p(DOC)
    body = render_doc(face)
    with io.open(doc_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(body)
    h = face["headline"]
    print("RUN OK %s shelves=%d understated=%d over_repair=%d movers=%d"
          % (FACE, len(face["rows"]), len(h["price_only_understates"]),
             len(h["threshold_reader_over_repairs"]), len(h["year_verdicts_that_move"])))
    return 0


def cmd_check():
    path = _p(FACE)
    if not os.path.exists(path):
        print("CHECK FAILED: face missing -> STALE, run `run`")
        return 3
    face = _load(FACE)
    for key, path_key in (("face", UP_FACE),):
        want = face["upstream"]["sha256"]
        got = _sha(_p(path_key))
        if want != got:
            print("STALE: upstream %s bytes changed (face %s.. != disk %s..) -> re-run"
                  % (path_key, want[:12], got[:12]))
            return 3
    for code, want in face.get("panels", {}).items():
        got = _sha(_p(panel_path(code)))
        if want != got:
            print("STALE: panel %s bytes changed (face %s.. != disk %s..) -> re-run"
                  % (panel_path(code), want[:12], got[:12]))
            return 3
    bad = []
    ticket = float(face["upstream"]["ticket_cash_cny"])
    up = _load(UP_FACE)
    upmap = {r["code"]: r for r in up["rows"]}
    for r in face["rows"]:
        src = upmap.get(r["code"])
        if src is None:
            bad.append("%s vanished upstream" % r["code"])
            continue
        # the published column must still be upstream verbatim
        for a, b, name in ((r["published"]["cagr_pct"], src["window_cagr_pct"], "cagr_pct"),
                           (r["published"]["extra_pp"], src["window_extra_pp"], "extra_pp"),
                           (r["published"]["extra_cny"], src["window_extra_cny"], "extra_cny")):
            if abs(float(a) - float(b)) > 1e-9:
                bad.append("%s published %s: face=%s upstream=%s" % (r["code"], name, a, b))
        # and every sourced number must fall out of the stored events
        ay = annual_yields(r["events"])
        bars = int(r["window"]["bars"])
        bpy = float(src["bars_per_year"])
        wy_bp = round(sum(float(e["yield_bp"]) for e in r["events"]
                          if e.get("in_window") and e.get("yield_bp") is not None) / bars * bpy, 2)
        if abs(wy_bp - float(r["distribution_yield_bp_per_year"])) > 1e-6:
            bad.append("%s yield_bp_per_year: face=%s recompute=%s"
                       % (r["code"], r["distribution_yield_bp_per_year"], wy_bp))
        cagr = round(float(r["price_only"]["cagr_pct"]) + wy_bp / 100.0, 4)
        if abs(cagr - float(r["sourced"]["cagr_pct"])) > 1e-6:
            bad.append("%s sourced cagr: face=%s recompute=%s"
                       % (r["code"], r["sourced"]["cagr_pct"], cagr))
        extra_pp = round(cagr - float(src["repo_cagr_pct"]), 4)
        if abs(extra_pp - float(r["sourced"]["extra_pp"])) > 1e-6:
            bad.append("%s sourced extra_pp: face=%s recompute=%s"
                       % (r["code"], r["sourced"]["extra_pp"], extra_pp))
        extra_cny = round(extra_pp / 100.0 * ticket, 2)
        if abs(extra_cny - float(r["sourced"]["extra_cny"])) > 1e-6:
            bad.append("%s sourced extra_cny: face=%s recompute=%s"
                       % (r["code"], r["sourced"]["extra_cny"], extra_cny))
        # the price-only line must be reproducible from the panel, and for the
        # shelves the chain reads with prices it must equal the published cagr --
        # that is the evidence that "published" and "price-only" are one caliber
        po, _n = price_only_line(caliber_series(r["code"], src["class"]), _ss_start(), _repaired_panel()[1])
        if po is None or abs(po - float(r["price_only"]["cagr_pct"])) > 1e-6:
            bad.append("%s price_only cagr: face=%s recompute=%s"
                       % (r["code"], r["price_only"]["cagr_pct"], po))
        if r["class"] != "money" and abs(po - float(src["window_cagr_pct"])) > 0.02:
            bad.append("%s published cagr is not the price-only line (%.4f vs %.4f) -> "
                       "re-run, its class or reader changed" % (r["code"], src["window_cagr_pct"], po))
        for y, v in r["years"].items():
            sv = src.get("years", {}).get(y)
            if sv is None:
                bad.append("%s/%s year gone upstream" % (r["code"], y))
                continue
            tot = round(float(sv["shelf_pct"]) + (float(ay.get(y, 0.0)) if r["published"]["is_price_only"] else 0.0) / 100.0, 4)
            if abs(tot - float(v["sourced_shelf_pct"])) > 1e-6:
                bad.append("%s/%s sourced_shelf_pct: face=%s recompute=%s"
                           % (r["code"], y, v["sourced_shelf_pct"], tot))
            sep = round(tot - float(sv["repo_pct"]), 4)
            if abs(sep - float(v["sourced_extra_pp"])) > 1e-6:
                bad.append("%s/%s sourced_extra_pp: face=%s recompute=%s"
                           % (r["code"], y, v["sourced_extra_pp"], sep))
            if bool(v["sign_flips"]) != bool((sv["extra_pp"] or 0) * (sep or 0) < 0):
                bad.append("%s/%s sign_flips flag disagrees with its own numbers" % (r["code"], y))
            if bool(v["material"]) != bool(abs(sep - float(sv["extra_pp"] or 0.0)) >= YEAR_SHIFT_PP):
                bad.append("%s/%s material flag disagrees with its own shift" % (r["code"], y))
    doc_path = _p(DOC)
    if os.path.exists(doc_path):
        doc = io.open(doc_path, encoding="utf-8").read()
        if MARK_BEGIN not in doc or MARK_END not in doc:
            bad.append("%s lost its marker block" % DOC)
        elif "%%" in doc:
            bad.append("%s prints a literal %%%% (escape slip on the page)" % DOC)
        else:
            block = doc.split(MARK_BEGIN)[1].split(MARK_END)[0]
            for r in face["rows"]:
                if table_row(r) not in block:
                    bad.append("%s's row on the page is not the row this face renders "
                               "(a number was typed by hand or drifted)" % r["code"])
    if bad:
        for b in bad[:14]:
            print("CHECK FAILED:", b)
        return 1
    n = sum(len(r["years"]) for r in face["rows"])
    print("CHECK OK (%d shelves / %d shelf-years / %d dividend events recomputed)"
          % (len(face["rows"]), n, sum(len(r["events"]) for r in face["rows"])))
    return 0


def cmd_selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    # L1-L3: cumulative -> per-event amounts
    d = pd.DataFrame({"ex_date": pd.to_datetime(["2020-01-02", "2021-01-04", "2022-01-04"]),
                      "cum_div": [1.0, 3.0, 3.5]})
    ev = events_with_amounts(d)
    leg("L1 the first event's amount is its own cumulative value", abs(ev.loc[0, "amount"] - 1.0) < 1e-12,
        str(list(ev["amount"])))
    leg("L2 later events are steps of the cumulative column",
        abs(ev.loc[1, "amount"] - 2.0) < 1e-12 and abs(ev.loc[2, "amount"] - 0.5) < 1e-12)

    # L4-L6: the yield is amount / previous close, and the gap is measured on the
    # first bar at or after the ex-date
    px = pd.Series([100.0, 100.0, 98.0, 98.1], index=pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"]))
    got = event_yield_bp(px, "2024-01-04", 2.0)
    leg("L4 yield_bp == amount / previous close", got and abs(got[0] - 200.0) < 1e-9, str(got))
    leg("L5 the observed gap is the ex-date bar's own change",
        got and abs(got[1]["observed_bp"] - (-200.0)) < 1e-9, str(got[1]) if got else "")
    weekend_px = pd.Series([100.0, 100.0, 98.0], index=pd.to_datetime(["2024-01-04", "2024-01-05", "2024-01-08"]))
    weekend = event_gap(weekend_px, "2024-01-06")
    leg("L6 an ex-date on a non-trading day lands on the next bar",
        weekend is not None and weekend["bar"] == "2024-01-08", str(weekend))
    leg("L7 an ex-date past the last bar is unknown, not zero",
        event_gap(weekend_px, "2024-01-09") is None)

    # L8: a dividend-sized drop is 'explained'; a drop twice its size is not
    ok_row = {"observed_bp": -200.0, "yield_bp": 200.0}
    leg("L8 an explained event has a residual inside the tolerance",
        abs(ok_row["observed_bp"] + ok_row["yield_bp"]) <= EXPLAINED_TOL_BP)
    bad_row = {"observed_bp": -400.0, "yield_bp": 200.0}
    leg("L9 a gap twice the dividend is flagged, not averaged away",
        abs(bad_row["observed_bp"] + bad_row["yield_bp"]) > EXPLAINED_TOL_BP)

    # L10-L12: annualisation uses the chain's ruler (per-bar x bars per year)
    rows = [{"in_window": True, "yield_bp": 100.0}, {"in_window": True, "yield_bp": 50.0},
            {"in_window": False, "yield_bp": 999.0}]
    wy, tot = window_yield_bp(rows, bars=300, bars_per_year=243.0)
    leg("L10 annualised yield == in-window sum / bars * bars_per_year", abs(wy - 121.5) < 1e-9, str(wy))
    leg("L11 events outside the window never enter the total", abs(tot - 150.0) < 1e-9, str(tot))
    empty = window_yield_bp([], bars=10, bars_per_year=243.0)
    leg("L12 no events is zero, not an error", empty == (0.0, 0.0), str(empty))

    # L13-L19: verdicts answer the right question
    leg("L13 no events -> price-only is the total return",
        "NO_DISTRIBUTIONS_PRICE_ONLY_IS_RIGHT" in verdict_for("X", "quote", [], 0, 0.0, 0.0, 0.0))
    leg("L14 a bond shelf whose published line is price-only is understated",
        "PRICE_ONLY_UNDERSTATES_EXTRA" in verdict_for("X", "bond", [{"in_window": True, "explained": True}],
                                                      1, 0.455, -0.455, 0.0))
    leg("L15 income too small to matter is not called a correction",
        "PRICE_ONLY_UNDERSTATES_EXTRA" not in verdict_for("X", "bond", [{"in_window": True, "explained": True}],
                                                          1, 0.02, -0.02, 0.0))
    leg("L16 a money shelf already on the sourced caliber is 'already counted', not added twice",
        "DISTRIBUTIONS_ALREADY_COUNTED_BY_THE_MONEY_READER"
        in verdict_for("X", "money", [{"in_window": True, "explained": True}], 1, 1.60, -0.03, 1.57))
    leg("L17 a published line above price-only with no distribution is its own tag",
        "PUBLISHED_LINE_IS_ABOVE_PRICE_ONLY_WITHOUT_A_DISTRIBUTION"
        in verdict_for("X", "money", [], 0, 0.0, -0.18, 0.18))
    leg("L18 an unexplained gap is its own tag",
        "EVENT_NOT_EXPLAINED_BY_THE_DISTRIBUTION"
        in verdict_for("X", "bond", [{"in_window": True, "explained": False}], 1, 0.455, -0.455, 0.0))
    leg("L19 a disk face missing rows is tagged by the comparison block, "
        "not by the verdict (it is provenance, not arithmetic)",
        disk_vs_fresh(pd.DataFrame({"ex_date": pd.to_datetime(["2024-01-02"]), "cum_div": [1.0]}),
                      pd.DataFrame({"ex_date": pd.to_datetime(["2024-01-02", "2024-02-02"]),
                                    "cum_div": [1.0, 2.0]}))["dates_missing_on_disk"] == ["2024-02-02"])

    # L20-L21: the disk-vs-fresh comparison finds a merged pair
    disk = pd.DataFrame({"ex_date": pd.to_datetime(["2024-01-02", "2024-04-02"]), "cum_div": [1.0, 3.0]})
    fresh = pd.DataFrame({"ex_date": pd.to_datetime(["2024-01-02", "2024-02-02", "2024-04-02"]),
                          "cum_div": [1.0, 2.0, 3.0]})
    cmp = disk_vs_fresh(disk, fresh)
    leg("L20 a missing row is named, not silently merged",
        cmp and cmp["dates_missing_on_disk"] == ["2024-02-02"], str(cmp))
    leg("L21 the merged step is printed with both amounts and the dates it swallowed",
        bool(cmp and cmp["steps_that_over_book"]
             and abs(cmp["steps_that_over_book"][0]["disk_step_amount"] - 2.0) < 1e-9
             and abs(cmp["steps_that_over_book"][0]["largest_single_event"] - 1.0) < 1e-9
             and len(cmp["steps_that_over_book"][0]["merged_dates"]) == 2),
        str(cmp["steps_that_over_book"]) if cmp else "")

    # L22-L23: the page must print the table and must not print an unescaped %%
    fake = {"headline": {"ticket_cash_cny": 565245.9, "budget_sessions": 20.0,
                         "price_only_understates": [{"code": "511010", "published_extra_cny": 3241.89,
                                                     "sourced_extra_cny": 5835.6, "cny_added": 2593.71,
                                                     "added_pp": 0.455}],
                         "published_above_price_only_without_a_distribution": [],
                         "already_counted": [], "no_distributions": [], "threshold_reader_over_repairs": [],
                         "disk_face_missing_events": [], "year_verdicts_that_move": [],
                         "verdict_counts": {"PRICE_ONLY_UNDERSTATES_EXTRA": 1}},
            "rows": [{"code": "511010", "class": "bond", "events_in_window": 5,
                      "price_only": {"cagr_pct": 2.3398},
                      "published": {"cagr_pct": 2.3398, "extra_cny": 3241.89},
                      "distribution_yield_bp_per_year": 45.5,
                      "sourced": {"cagr_pct": 2.7948, "cny_added": 2593.71},
                      "verdict": ["PRICE_ONLY_UNDERSTATES_EXTRA"]}],
            "evidence_cutoff": "2026-11-20"}
    block = render_block(fake)
    leg("L22 the rendered block has no bare %%", "%%" not in block.replace("%%", "") and "%" in block)
    leg("L23 the rendered block prints the shelf, the yield and the money it adds",
        "511010" in block and "45.5" in block and "2594" in block, block.splitlines()[2][:90])

    ok = sum(1 for _, v, _ in legs if v)
    for name, v, detail in legs:
        print(("PASS " if v else "FAIL ") + name + ((" | " + str(detail)) if (detail and not v) else ""))
    print("SELFTEST %d/%d PASS" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "run":
        return cmd_run()
    if cmd == "--check":
        return cmd_check()
    if cmd == "--selftest":
        return cmd_selftest()
    print("unknown command: %s" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
