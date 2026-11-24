#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""cash_shelf_year_by_year -- the extra is not one number: it has years.

WHY THIS FACE EXISTS
--------------------
r2045 (`cash_shelf_wait_payback`) priced the wait in "trading days of this shelf's own
extra-over-repo" -- 13.1 days for 511360 at the ticket.  That number divides by the
window-average extra, and the window-average extra is an annualisation of six years in
which the repo leg itself ranged from 0.93% to 2.15%.  A reader making the decision next
month does not get the average year; they get this year.

So this face keeps the ruler and changes the denominator's resolution: instead of one
extra-per-day, it prints one per year, and answers the only question that follows:

    in a year like 2025, what does the same wait cost?

Two by-products came out of building it and are published here because they change the
number r2045 prints:

* SUB-THRESHOLD FLIPS.  r2041's flip repair is a 35% single-bar rule; the money-ETF
  reader zeroes bars deeper than 50bp as share consolidations.  511360 carries a pair
  that neither rule handles: on 2023-09-08 its close fell 1.047%, and on 2023-09-11 it
  was back within 4.4bp of the pre-drop price.  Zeroing the drop and keeping the rebound
  inflates the window CAGR by ~0.165pp/py; this face zeroes both bars and prints the
  difference (`quote_audit`).
* The extra is negative in nameable years for three of the five shelves, including the
  one r2042 called the winner -- which this face prints rather than folds.

THE QUESTION (frozen before the first run)
------------------------------------------
For each shelf, year by year: what was its extra over the repo leg, and how many trading
days of that year's extra does the p95 net wait (imported from r2045) cost?  How many
years would the wait have finished inside the same one-month budget r2045 uses?

RULER (nothing re-decided here)
-------------------------------
* net wait (median and p95, CNY)  -- imported from results/cash_shelf_wait_payback.json
* budget and caliber             -- read from that face's own `adoption` block
* ticket size                    -- read from it too
* extra                           -- rebuilt per year here, same caliber as r2041:
                                     buy-and-hold, 4bp round trip on the entry bar;
                                     money shelves use the consolidation-aware reader
                                     plus this face's flip neutralisation
* annualisation                   -- per year: bars of that year, not 243 typed

VERDICTS (mechanical)
---------------------
* ONE_SESSION_NO_WAIT              -- the capacity ruler clears it in one session, so
                                     there is no wait to price; the year axis of extra is
                                     still printed (that is the interesting part).
* NO_EXTRA_TO_PAY_BACK             -- window extra <= 0; nothing to pay the wait with.
* WAIT_FITS_IN_EVERY_FULL_YEAR     -- every full year's payback <= budget.
* WAIT_FITS_ONLY_IN_GOOD_YEARS     -- some full years exceed it; they are named.
* WAIT_NEVER_FITS_IN_A_FULL_YEAR   -- no full year would have paid it back.
* EXTRA_GOES_NEGATIVE_IN_YEARS     -- tag: at least one full year had no extra at all.

Usage:
    python scripts/cash_shelf_year_by_year.py run
    python scripts/cash_shelf_year_by_year.py --check
    python scripts/cash_shelf_year_by_year.py --selftest
"""

from __future__ import annotations

import datetime as dt
import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import cb_parking_shelf_at_size as SS  # noqa: E402  (buy-and-hold caliber, window)
import cb_parking_bakeoff as BK  # noqa: E402  (cagr/level helpers, same convention)
import etf_book_cash_ladder as CL  # noqa: E402  (repo engine)
import etf_book_cash_vehicle as CV  # noqa: E402  (money ETF resets)
import etf_composite_pf as E  # noqa: E402  (ETF panel)
import etf_equity_alpha as A  # noqa: E402  (35% flip repair)

PAYBACK_FACE = "results/cash_shelf_wait_payback.json"
SIZE_FACE = "results/cb_parking_shelf_at_size.json"
FACE = "results/cash_shelf_year_by_year.json"
DOC = "research/CASH_SHELF_YEAR_BY_YEAR.md"

# A flip pair: a single bar down at least FLIP_DROP_BP, followed within FLIP_WINDOW bars
# by a close back within FLIP_TOL_BP of the pre-drop close.  Both bars are booked at zero.
# Chosen before the first run; the observed pair on 511360 is -104.7bp / rebound to -4.4bp.
FLIP_DROP_BP = 50.0
FLIP_WINDOW = 3
FLIP_TOL_BP = 5.0
FULL_YEAR_BARS = 100          # fewer bars in a calendar year = partial year, excluded from verdicts

MARK_BEGIN = "<!-- YEAR-TABLE:BEGIN -->"
MARK_END = "<!-- YEAR-TABLE:END -->"


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _load(path):
    with io.open(os.path.join(ROOT, path), "r", encoding="utf-8") as f:
        return json.load(f)


def _content_sha(obj):
    blob = json.dumps(obj, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def find_flip_pairs(px):
    """Sub-threshold quote-flip pairs: deep one-bar drop, price back within tolerance.

    Returns a list of {drop_date, drop_pct, back_date, back_pct, net_pct}.  A pair is
    reported once (the first recovery bar that satisfies the tolerance ends it).
    """
    px = px.dropna().astype(float)
    ret = px.pct_change()
    out = []
    i = 1
    dates = list(px.index)
    while i < len(dates):
        r = ret.iloc[i]
        if not np.isfinite(r) or r * 1e4 > -FLIP_DROP_BP:
            i += 1
            continue
        before = float(px.iloc[i - 1])
        found = None
        for j in range(i + 1, min(i + 1 + FLIP_WINDOW, len(dates))):
            back = float(px.iloc[j])
            if abs(back / before - 1.0) * 1e4 <= FLIP_TOL_BP:
                found = j
                break
        if found is None:
            i += 1
            continue
        pair_ret = float((1.0 + r) * (1.0 + ret.iloc[found]) - 1.0)
        out.append({
            "drop_date": str(pd.Timestamp(dates[i]).date()),
            "drop_bp": round(float(r) * 1e4, 2),
            "back_date": str(pd.Timestamp(dates[found]).date()),
            "back_bp": round(float(ret.iloc[found]) * 1e4, 2),
            "gap_bars": found - i,
            "round_trip_bp": round(pair_ret * 1e4, 2),
        })
        i = found + 1
    return out


def neutralise(rets, px, pairs):
    """Zero both bars of every detected pair in a per-bar return series."""
    out = rets.copy()
    for p in pairs:
        for key in ("drop_date", "back_date"):
            try:
                out.loc[pd.Timestamp(p[key])] = 0.0
            except KeyError:
                pass
    return out


def shelf_returns(code, px, klass, window_end):
    """Same caliber as r2041: buy-and-hold, 4bp round trip on the entry bar."""
    pairs = []
    if klass == "money":
        base = CV.load_etf(code)
        rets, _resets = CV.consolidation_returns(base)
        pairs = find_flip_pairs(base)
        rets = neutralise(rets, base, pairs)
        rets = rets[(rets.index >= pd.Timestamp(SS.START)) & (rets.index <= pd.Timestamp(window_end))]
        raw = CV.consolidation_returns(base)[0]
        raw = raw[(raw.index >= pd.Timestamp(SS.START)) & (raw.index <= pd.Timestamp(window_end))]
    else:
        raw = SS.buy_hold_rets(px, SS.START, window_end)
        rets = raw
    if rets is None or len(rets) < 40:
        return None, None, pairs
    rets = rets.copy()
    rets.iloc[0] -= SS.round_trip_bp(SS.COST_BP_SIDE) / 1e4
    if raw is not None:
        raw = raw.copy()
        raw.iloc[0] -= SS.round_trip_bp(SS.COST_BP_SIDE) / 1e4
    return rets, raw, pairs


def bars_per_year(rets):
    """Trading days per year derived from the shelf's own bars and window (r2045's ruler)."""
    if len(rets) < 2:
        return None
    years = (rets.index[-1] - rets.index[0]).days / 365.25
    if years <= 0:
        return None
    return len(rets) / years


def year_axis(rets, repo, ticket, net_p95, net_median):
    years = {}
    for y, grp in rets.groupby(rets.index.year):
        r = float((1.0 + grp).prod() - 1.0)
        rp = repo[repo.index.year == y]
        repo_r = float((1.0 + rp).prod() - 1.0) if len(rp) else None
        row = {
            "bars": int(len(grp)),
            "shelf_pct": round(r * 100.0, 4),
            "repo_pct": round(repo_r * 100.0, 4) if repo_r is not None else None,
            "full_year": bool(len(grp) >= FULL_YEAR_BARS),
        }
        if repo_r is None:
            row.update({"extra_pp": None, "extra_cny": None,
                        "extra_per_day_cny": None,
                        "payback_days_p95": None, "payback_days_median": None})
        else:
            extra_pp = (r - repo_r) * 100.0
            extra_cny = extra_pp / 100.0 * float(ticket)
            per_day = extra_cny / float(len(grp))
            row["extra_pp"] = round(extra_pp, 4)
            row["extra_cny"] = round(extra_cny, 2)
            row["extra_per_day_cny"] = round(per_day, 4)
            if per_day > 0 and net_p95 is not None:
                row["payback_days_p95"] = round(float(net_p95) / per_day, 2)
            else:
                row["payback_days_p95"] = None
            if per_day > 0 and net_median is not None:
                row["payback_days_median"] = round(float(net_median) / per_day, 2)
            else:
                row["payback_days_median"] = None
        years[str(y)] = row
    return years


def verdict(up_tier, years, window_extra_cny, budget):
    if up_tier.get("sessions_to_fill") is not None and up_tier["sessions_to_fill"] <= 1:
        return ["ONE_SESSION_NO_WAIT"]
    if window_extra_cny is None or window_extra_cny <= 0:
        return ["NO_EXTRA_TO_PAY_BACK"]
    full = {y: v for y, v in years.items() if v["full_year"]}
    negative = sorted([y for y, v in full.items() if v.get("extra_pp") is not None and v["extra_pp"] <= 0])
    priced = {y: v["payback_days_p95"] for y, v in full.items() if v.get("payback_days_p95") is not None}
    tags = []
    if priced:
        inside = sorted([y for y, d in priced.items() if d <= budget])
        outside = sorted([y for y, d in priced.items() if d > budget])
        unpriced_full = sorted([y for y in full if y not in priced])
        if outside:
            tags.append("WAIT_FITS_IN_EVERY_FULL_YEAR" if not outside else "WAIT_FITS_ONLY_IN_GOOD_YEARS")
        else:
            tags.append("WAIT_FITS_IN_EVERY_FULL_YEAR")
        if not inside:
            tags = [t for t in tags if t != "WAIT_FITS_ONLY_IN_GOOD_YEARS"] + ["WAIT_NEVER_FITS_IN_A_FULL_YEAR"]
    else:
        tags.append("WAIT_NEVER_FITS_IN_A_FULL_YEAR")
        inside, outside, unpriced_full = [], [], sorted(full)
    if negative:
        tags.append("EXTRA_GOES_NEGATIVE_IN_YEARS")
    return tags


def build():
    pay = _load(PAYBACK_FACE)
    size = _load(SIZE_FACE)
    adoption = pay["adoption"]
    budget = float(adoption["budget_sessions"])
    caliber = adoption["caliber"]
    ticket = float(pay["headline"]["ticket_cash_cny"])
    tier_key = str(pay["headline"]["tier_used"])

    close_all, open_all, _amt, _feats = E.build_panel()
    close_all, _o2, n_flip = A.repair_flips(close_all, open_all)
    window_end = str(close_all.index[-1].date())

    rates = CL.load_panel()
    allb = sorted(set().union(*[set(s.index) for s in rates.values()]))
    bars = pd.DatetimeIndex([b for b in allb if b >= pd.Timestamp(SS.START)])
    repo_arr, _repo_info = CL.roll_rung(bars, rates, None, fees=None, name="GC001")
    repo = pd.Series(repo_arr, index=bars).dropna()

    pub_size = {r["code"]: r for r in size["rows"]}
    rows = []
    for code, r2041 in pub_size.items():
        klass = r2041["class"]
        if code not in close_all.columns and klass != "money":
            raise KeyError("%s missing from the ETF panel" % code)
        rets, raw, pairs = shelf_returns(code, close_all[code], klass, window_end)
        if rets is None:
            raise KeyError("%s has too few bars" % code)
        up = None
        for prow in pay["rows"]:
            if prow["code"] == code:
                up = prow["tiers"].get(tier_key)
        if up is None:
            raise KeyError("%s has no tier %s in the payback face" % (code, tier_key))
        window_cagr = float(BK.cagr(rets))
        raw_cagr = float(BK.cagr(raw)) if raw is not None and len(raw) else None
        repo_cagr = float(BK.cagr(repo))
        window_extra_pp = window_cagr - repo_cagr
        window_extra_cny = window_extra_pp / 100.0 * ticket
        # the published face's own window extra, for the delta
        pub_extra_cny = up.get("extra_cny")
        years = year_axis(rets, repo, ticket, up.get("net_p95_cny"), up.get("net_median_cny"))
        full = {y: v for y, v in years.items() if v["full_year"]}
        priced = {y: v for y, v in full.items() if v.get("payback_days_p95") is not None}
        worst = max(priced.items(), key=lambda kv: kv[1]["payback_days_p95"]) if priced else None
        best = min(priced.items(), key=lambda kv: kv[1]["payback_days_p95"]) if priced else None
        bpy = bars_per_year(rets)
        rows.append({
            "code": code,
            "label": r2041.get("label"),
            "class": klass,
            "index_bars": int(len(rets)),
            "index_first": str(rets.index[0].date()),
            "index_last": str(rets.index[-1].date()),
            "window_cagr_pct": round(window_cagr, 4),
            "bars_per_year": round(bpy, 4) if bpy else None,
            "window_cagr_before_neutralisation_pct": round(raw_cagr, 4) if raw_cagr is not None else None,
            "published_own_net_cagr_pct": r2041.get("own_net_cagr_pct"),
            "repo_cagr_pct": round(repo_cagr, 4),
            "window_extra_pp": round(window_extra_pp, 4),
            "window_extra_cny": round(window_extra_cny, 2),
            "published_extra_cny": pub_extra_cny,
            "delta_vs_published_cny": (round(window_extra_cny - pub_extra_cny, 2)
                                       if pub_extra_cny is not None else None),
            "sessions_to_fill": up.get("sessions_to_fill"),
            "net_p95_cny": up.get("net_p95_cny"),
            "net_median_cny": up.get("net_median_cny"),
            "published_payback_days_p95": up.get("payback_days_p95"),
            "payback_days_p95_on_this_line": (
                round(float(up["net_p95_cny"]) / (window_extra_cny / bpy), 2)
                if (up.get("net_p95_cny") is not None and window_extra_cny > 0 and bpy) else None),
            "years": years,
            "years_beating_repo": "%d/%d" % (
                sum(1 for y, v in full.items() if (v.get("extra_pp") or 0) > 0), len(full)),
            "worst_year": ({"year": worst[0], "payback_days_p95": worst[1]["payback_days_p95"]}
                           if worst else None),
            "best_year": ({"year": best[0], "payback_days_p95": best[1]["payback_days_p95"]}
                          if best else None),
            "quote_audit": {
                "flip_pairs": pairs,
                "flip_effect_pp_per_year": (round(window_cagr - raw_cagr, 4)
                                            if raw_cagr is not None else 0.0),
                "caliber": ("money shelf: consolidation-aware reader (drops > %.0fbp booked at "
                            "zero) plus this face's sub-threshold flip neutralisation"
                            % (-CV.CONSOLIDATION_JUMP * 1e4)) if klass == "money"
                           else "buy-and-hold, 4bp round trip on the entry bar (r2041 caliber)",
            },
            "verdict": verdict(up, years, window_extra_cny, budget),
        })

    headline = _headline(rows, ticket, budget, caliber, tier_key, n_flip, window_end)
    face = {
        "schema": "cash-shelf-year-by-year/v1",
        "artifact": "cash_shelf_year_by_year",
        "generated": dt.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": window_end,
        "window": {"start": SS.START, "end": window_end},
        "question": ("year by year: what was each shelf's extra over the repo leg, and how "
                     "many trading days of that year's extra does the same p95 net wait cost"),
        "adoption": {
            "budget_sessions": budget,
            "caliber": caliber,
            "source": PAYBACK_FACE + " :: adoption",
            "note": "no second budget is declared here; the upstream one is read and printed",
        },
        "flip_rule": {
            "drop_bp_at_least": FLIP_DROP_BP,
            "rebound_within_bars": FLIP_WINDOW,
            "rebound_tolerance_bp": FLIP_TOL_BP,
            "treatment": "both bars booked at exactly zero return; pair listed in quote_audit",
            "why": ("r2041's repair is a 35% rule and the money reader zeroes drops > 50bp but "
                    "keeps the rebound; a sub-threshold quote flip therefore lands as a fake gain"),
        },
        "upstream": {
            "payback_face": PAYBACK_FACE, "payback_sha256": _sha(os.path.join(ROOT, PAYBACK_FACE)),
            "size_face": SIZE_FACE, "size_sha256": _sha(os.path.join(ROOT, SIZE_FACE)),
        },
        "panel": {"columns": int(close_all.shape[1]), "flips_repaired_35pct_rule": int(n_flip)},
        "rows": rows,
        "headline": headline,
    }
    face["content_sha256"] = _content_sha({k: v for k, v in face.items() if k != "content_sha256"})
    return face


def _headline(rows, ticket, budget, caliber, tier_key, n_flip, window_end):
    priced = [r for r in rows if r["payback_days_p95_on_this_line"] is not None]
    priced.sort(key=lambda r: r["payback_days_p95_on_this_line"])
    inside = [r["code"] for r in priced if r["payback_days_p95_on_this_line"] <= budget]
    outside = [r["code"] for r in priced if r["payback_days_p95_on_this_line"] > budget]
    moved = [r for r in rows
             if r["published_payback_days_p95"] is not None
             and r["payback_days_p95_on_this_line"] is not None
             and abs(r["payback_days_p95_on_this_line"] - r["published_payback_days_p95"]) > 0.5]
    worst = None
    for r in rows:
        if r["worst_year"] is None:
            continue
        if worst is None or r["worst_year"]["payback_days_p95"] > worst["payback_days_p95"]:
            worst = {"code": r["code"], "year": r["worst_year"]["year"],
                     "payback_days_p95": r["worst_year"]["payback_days_p95"]}
    best = None
    for r in rows:
        if r["best_year"] is None:
            continue
        if best is None or r["best_year"]["payback_days_p95"] < best["payback_days_p95"]:
            best = {"code": r["code"], "year": r["best_year"]["year"],
                    "payback_days_p95": r["best_year"]["payback_days_p95"]}
    negative_years = {}
    for r in rows:
        ys = sorted([y for y, v in r["years"].items()
                     if v["full_year"] and v.get("extra_pp") is not None and v["extra_pp"] <= 0])
        if ys:
            negative_years[r["code"]] = ys
    return {
        "ticket_cash_cny": ticket,
        "tier_used": tier_key,
        "budget_sessions": budget,
        "caliber": caliber,
        "window_end": window_end,
        "inside_budget_on_this_line": inside,
        "outside_budget_on_this_line": outside,
        "shelves_moved_by_more_than_half_a_day": [{"code": r["code"],
                                                   "published": r["published_payback_days_p95"],
                                                   "on_this_line": r["payback_days_p95_on_this_line"]}
                                                  for r in moved],
        "worst_year_payback": worst,
        "best_year_payback": best,
        "years_extra_negative": negative_years,
        "verdict_counts": _counts([t for r in rows for t in r["verdict"]]),
        "panel_flips_repaired_35pct": n_flip,
    }


def _counts(tags):
    out = {}
    for t in tags:
        out[t] = out.get(t, 0) + 1
    return out


# --------------------------------------------------------------------------- render
def _f(v, nd=2):
    if v is None:
        return "-"
    if isinstance(v, float) and not np.isfinite(v):
        return "-"
    if abs(v) >= 1000:
        return "{:,.{}f}".format(v, nd)
    return "{:.{}f}".format(v, nd)


def render_block(face):
    h = face["headline"]
    lines = []
    lines.append("票面 **%s 元**，预算 = **%d 个交易日的超额**（`%s` 口径，读自 r2045 的 `adoption`）。"
                 % ("{:,.0f}".format(h["ticket_cash_cny"]), int(h["budget_sessions"]), h["caliber"]))
    lines.append("")
    lines.append("### 一、同一个等待，按年算（每一行用该年自己的超额做分母）")
    lines.append("")
    lines.append("| 货架 | 排队天数 | 窗口超额（元/年） | 本面重算（元/年） | 排队=p95（工作日） | 最好的一年 | 最差的一年 | 胜回购年数 | 判词 |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for r in face["rows"]:
        best = ("%s：%.1f 天" % (r["best_year"]["year"], r["best_year"]["payback_days_p95"])
                if r["best_year"] else "-")
        worst = ("%s：%.1f 天" % (r["worst_year"]["year"], r["worst_year"]["payback_days_p95"])
                 if r["worst_year"] else "-")
        lines.append("| `%s` | %s | %s | %s | **%s** | %s | %s | %s | %s |" % (
            r["code"], r["sessions_to_fill"], _f(r["published_extra_cny"]),
            _f(r["window_extra_cny"]),
            _f(r["payback_days_p95_on_this_line"], 1),
            best, worst, r["years_beating_repo"], " ".join(r["verdict"])))
    lines.append("")
    lines.append("### 二、逐年明细（超额 pp / 该年等待=几天的超额）")
    lines.append("")
    codes = [r["code"] for r in face["rows"] if r["sessions_to_fill"] and r["sessions_to_fill"] > 1]
    if codes:
        all_years = sorted({y for r in face["rows"] for y in r["years"]})
        lines.append("| 年 | " + " | ".join("`%s`" % c for c in codes) + " |")
        lines.append("|---" * (len(codes) + 1) + "|")
        for y in all_years:
            cells = []
            for c in codes:
                r = [x for x in face["rows"] if x["code"] == c][0]
                v = r["years"].get(y)
                if v is None:
                    cells.append("-")
                elif not v["full_year"]:
                    cells.append("%+.2fpp（不整年）" % v["extra_pp"] if v.get("extra_pp") is not None else "-")
                elif v.get("payback_days_p95") is None:
                    cells.append("%+.2fpp → 无超额" % v["extra_pp"] if v.get("extra_pp") is not None else "-")
                else:
                    cells.append("%+.2fpp → %.1f 天" % (v["extra_pp"], v["payback_days_p95"]))
            lines.append("| %s | %s |" % (y, " | ".join(cells)))
        lines.append("")
    lines.append("### 三、报价翻转审计（为什么本面的天数与 r2045 不同）")
    lines.append("")
    for r in face["rows"]:
        q = r["quote_audit"]
        if not q["flip_pairs"]:
            continue
        for p in q["flip_pairs"]:
            lines.append("- `%s`：%s 单日 **%.1fbp** 下跌，%s（隔 %d 个 bar）收在下跌前收盘价的 **%.1fbp** 以内，"
                         "整段往返 **%.1fbp**。35%% 规则看不见它，货币 ETF 读取器只抹掉下跌、留下回跳 → "
                         "窗口年化虚高 **%.4fpp/年**。本面把两根 bar 都记为零。"
                         % (r["code"], p["drop_date"], p["drop_bp"], p["back_date"], p["gap_bars"],
                            abs(p["round_trip_bp"]), p["round_trip_bp"],
                            abs(q["flip_effect_pp_per_year"])))
    if not any(r["quote_audit"]["flip_pairs"] for r in face["rows"]):
        lines.append("- 本窗未检出亚阈值翻转对。")
    lines.append("")
    last = sorted({y for r in face["rows"] for y in r["years"]})[-1]
    bits = []
    for r in face["rows"]:
        v = r["years"].get(last)
        if not v or not v["full_year"]:
            continue
        if v.get("extra_pp") is None:
            continue
        if r["sessions_to_fill"] is not None and r["sessions_to_fill"] <= 1:
            bits.append("`%s` %+.2fpp（一次买完，无排队）" % (r["code"], v["extra_pp"]))
        elif v.get("payback_days_p95") is None:
            bits.append("`%s` %+.2fpp（该年无超额）" % (r["code"], v["extra_pp"]))
        else:
            bits.append("`%s` %+.2fpp → **%.1f 天**" % (r["code"], v["extra_pp"], v["payback_days_p95"]))
    if bits:
        lines.append("**最新整年（%s）**：%s。" % (last, "；".join(bits)))
        lines.append("")
    lines.append("> 口径：超额 = 该年货架收益 − 同年回购腿收益；「等待=几天的超额」= r2045 的净等待 p95（元）÷ 该年每日超额（元/bar）。"
                 "不满 %d 个 bar 的日历年在表内标注「不整年」，不参与判词。" % FULL_YEAR_BARS)
    return "\n".join(lines)


def render_doc(face):
    h = face["headline"]
    neg = h["years_extra_negative"]
    lead_bits = []
    for r in face["rows"]:
        if r["code"] == "511360":
            lead_bits.append("`511360` 在七年平均上是 **%.1f 天**，落在最好的一年（%s）只要 **%.1f 天**，"
                             "落在最差的一年（%s）要 **%.1f 天**。"
                             % (r["payback_days_p95_on_this_line"] or 0,
                                r["best_year"]["year"] if r["best_year"] else "-",
                                r["best_year"]["payback_days_p95"] if r["best_year"] else 0,
                                r["worst_year"]["year"] if r["worst_year"] else "-",
                                r["worst_year"]["payback_days_p95"] if r["worst_year"] else 0))
    if neg:
        suspect = "、".join("`%s`（%s）" % (c, "、".join(ys)) for c, ys in neg.items())
        lead_bits.append("超额为负的年份不是尾部，是点名可数的：%s。" % suspect)
    head = [
        "# 超额不是常数，它有年份",
        "",
        "> 一句话：" + " ".join(lead_bits),
        "",
        "## 为什么要按年再算一遍",
        "",
        "`cash_shelf_wait_payback`（r2045）把排队成本换算成「几天的超额」，分母用的是全窗口年化。"
        "但这个窗口里回购腿自己从 **0.93%**（2026）走到 **2.15%**（2023），货架超额因此年年不同。"
        "下个月要下单的人拿到的不是「平均年」，是「这一年」。",
        "",
        "## 本面唯一的新的测量",
        "",
        "- 逐年重建五个货架的收益（与 r2041 同源面板、同一成本口径：买入持有、进场 bar 收 4bp 往返），"
        "再与同年回购腿相减 → 每年的超额 pp 与元。",
        "- 分子不动：净等待 p95 直接读 r2045，预算与口径也从它的 `adoption` 块读，本面不另立标准。",
        "- 副产品：货币 ETF 族里发现一对**亚阈值报价翻转**（35% 规则与 50bp 重置规则都不吃），"
        "见下文审计节；本面把两根 bar 都记为零，并把与 r2045 的差印出来。",
        "",
        "## 读数",
        "",
        MARK_BEGIN,
        render_block(face),
        MARK_END,
        "",
        "## 怎么用",
        "",
        "- 判词只回答「这份排队在多少个整年里是安全的」，不回答「该不该买」。"
        "容量（r2041）、摆动（r2042）、排期（r2043）、在途 carry（r2044）四道另算。",
        "- 「胜回购年数」是 5/7 还是 4/7，比一个平均数更能说明这类货架的稳定性；负年份点名印出，不折叠。",
        "- 若要用 511360 排期：本面给的余量约为 %.1f 天，r2045 给的余量约为 %.1f 天（预算 %d 天）。"
        % (_headroom(face, "511360"), _published_headroom(face, "511360"), int(h["budget_sessions"])),
        "",
        "## 未验证（如实）",
        "",
        "- 本面不重算价格以外的任何东西：滑点/在途 carry 全部继承 r2043/r2044。",
        "- 逐年超额是历史分段，不是对下一年的预测。2026 只到 11-20（213 个 bar），已按该年自己的 bar 数摊薄并入判词；"
        "不满 %d 个 bar 的年份（`511360` 的 2020 只有 63 bar）标为不整年、不入判词。" % FULL_YEAR_BARS,
        "- 翻转审计只覆盖「单 bar 深跌 + 快速回到原位」这一种形状；其它数据缺陷不在此面射程内。",
        "- 511360 的重置处置沿用 r2041 的读取器（>50bp 记零），这会把它真实的付息日当作零收益，"
        "属保守偏差（低估收益）。",
        "",
    ]
    return "\n".join(head)


def _row(face, code):
    for r in face["rows"]:
        if r["code"] == code:
            return r
    return None


def _headroom(face, code):
    r = _row(face, code)
    b = face["headline"]["budget_sessions"]
    if not r or r["payback_days_p95_on_this_line"] is None:
        return float("nan")
    return b - r["payback_days_p95_on_this_line"]


def _published_headroom(face, code):
    r = _row(face, code)
    b = face["headline"]["budget_sessions"]
    if not r or r["published_payback_days_p95"] is None:
        return float("nan")
    return b - r["published_payback_days_p95"]


def cmd_run():
    face = build()
    with io.open(os.path.join(ROOT, FACE), "w", encoding="utf-8", newline="\n") as f:
        json.dump(face, f, ensure_ascii=False, indent=1)
        f.write("\n")
    doc_path = os.path.join(ROOT, DOC)
    body = render_doc(face)
    if os.path.exists(doc_path):
        old = io.open(doc_path, encoding="utf-8").read()
        if MARK_BEGIN in old and MARK_END in old:
            pre = old.split(MARK_BEGIN)[0]
            post = MARK_END + old.split(MARK_END, 1)[1]
            body = pre + MARK_BEGIN + "\n" + render_block(face) + "\n" + post
    with io.open(doc_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(body)
    print("RUN OK %s rows=%d inside=%d outside=%d"
          % (FACE, len(face["rows"]),
             len(face["headline"]["inside_budget_on_this_line"]),
             len(face["headline"]["outside_budget_on_this_line"])))
    return 0


def cmd_check():
    path = os.path.join(ROOT, FACE)
    if not os.path.exists(path):
        print("CHECK FAILED: face missing -> STALE, run `run`")
        return 3
    face = _load(FACE)
    for key, path_key in (("payback_sha256", PAYBACK_FACE), ("size_sha256", SIZE_FACE)):
        want = face["upstream"][key]
        got = _sha(os.path.join(ROOT, path_key))
        if want != got:
            print("STALE: %s bytes changed (face %s.. != disk %s..) -> re-run"
                  % (path_key, want[:12], got[:12]))
            return 3
    fresh = build()
    bad = []
    fmap = {r["code"]: r for r in fresh["rows"]}
    for r in face["rows"]:
        fr = fmap.get(r["code"])
        if fr is None:
            bad.append("%s vanished upstream" % r["code"])
            continue
        for field in ("window_cagr_pct", "window_extra_pp", "window_extra_cny",
                      "payback_days_p95_on_this_line"):
            a, b = r.get(field), fr.get(field)
            if a is None and b is None:
                continue
            if a is None or b is None or abs(float(a) - float(b)) > 1e-6:
                bad.append("%s %s: face=%s recompute=%s" % (r["code"], field, a, b))
        if r.get("years_beating_repo") != fr.get("years_beating_repo"):
            bad.append("%s years_beating_repo: face=%s recompute=%s"
                       % (r["code"], r.get("years_beating_repo"), fr.get("years_beating_repo")))
        if r["verdict"] != fr["verdict"]:
            bad.append("%s verdict: face=%s recompute=%s" % (r["code"], r["verdict"], fr["verdict"]))
        for y, v in r["years"].items():
            fv = fr["years"].get(y)
            if fv is None:
                bad.append("%s/%s year gone" % (r["code"], y))
                continue
            for field in ("extra_pp", "extra_cny", "payback_days_p95"):
                a, b = v.get(field), fv.get(field)
                if a is None and b is None:
                    continue
                if a is None or b is None or abs(float(a) - float(b)) > 1e-6:
                    bad.append("%s/%s %s: face=%s recompute=%s" % (r["code"], y, field, a, b))
        if len(r["quote_audit"]["flip_pairs"]) != len(fr["quote_audit"]["flip_pairs"]):
            bad.append("%s flip pairs count changed" % r["code"])
    # the imported numbers must equal what upstream prints right now
    pay = _load(PAYBACK_FACE)
    for r in face["rows"]:
        up = [p for p in pay["rows"] if p["code"] == r["code"]][0]["tiers"].get(str(pay["headline"]["tier_used"]))
        if r["net_p95_cny"] != up.get("net_p95_cny") or r["published_extra_cny"] != up.get("extra_cny"):
            bad.append("%s imported numbers no longer match the payback face" % r["code"])
    if bad:
        for b in bad[:14]:
            print("CHECK FAILED:", b)
        return 1
    n = sum(len(r["years"]) for r in face["rows"])
    print("CHECK OK (%d shelves / %d shelf-years / %d flip pair(s) recomputed)"
          % (len(face["rows"]), n, sum(len(r["quote_audit"]["flip_pairs"]) for r in face["rows"])))
    return 0


def cmd_selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    # 1-3. flip detector: detects a flip, ignores a real drop, ignores a slow recovery
    flip = pd.Series([100.0, 100.0, 99.0, 99.9, 100.0], index=pd.bdate_range("2024-01-01", periods=5))
    pair = find_flip_pairs(flip)
    leg("L1 a drop-and-return pair is detected", len(pair) == 1, str(pair))
    real = pd.Series([100.0, 100.0, 99.0, 99.1, 99.3], index=pd.bdate_range("2024-01-01", periods=5))
    leg("L2 a drop that stays down is not a flip", find_flip_pairs(real) == [])
    slow = pd.Series([100.0, 100.0, 99.0, 99.2, 99.4, 99.6, 100.0],
                     index=pd.bdate_range("2024-01-01", periods=7))
    leg("L3 a slow recovery is not a flip", find_flip_pairs(slow) == [])
    tight = pd.Series([100.0, 100.0, 99.0, 100.09], index=pd.bdate_range("2024-01-01", periods=4))
    leg("L4 a rebound outside tolerance is not a flip", find_flip_pairs(tight) == [])

    # 5. neutralisation zeroes both bars
    rets = pd.Series([0.0, 0.0, -0.01, 0.0101, 0.0], index=pd.bdate_range("2024-01-01", periods=5))
    neut = neutralise(rets, flip, [{"drop_date": "2024-01-03", "back_date": "2024-01-04"}])
    leg("L5 both bars of the pair are booked at zero",
        abs(neut.iloc[2]) < 1e-15 and abs(neut.iloc[3]) < 1e-15)

    # 6. the flip effect is exactly the rebound the old caliber kept
    leg("L6 flip effect equals the rebound bar", abs((rets.iloc[3] - neut.iloc[3]) - 0.0101) < 1e-12)

    # 7-9. year axis arithmetic on hand numbers
    idx = pd.bdate_range("2024-01-01", periods=250)
    r = pd.Series([0.001] * 250, index=idx)
    repo = pd.Series([0.0005] * 250, index=idx)
    ya = year_axis(r, repo, 100000.0, 200.0, 20.0)
    y = ya["2024"]
    leg("L7 extra_pp is the difference of the two yearly returns",
        abs(y["extra_pp"] - (((1.001 ** 250 - 1) - (1.0005 ** 250 - 1)) * 100.0)) < 0.01, str(y["extra_pp"]))
    leg("L8 payback days = net wait / that year's extra per bar",
        abs(y["payback_days_p95"] - (200.0 / (y["extra_cny"] / y["bars"]))) < 0.01)
    leg("L9 a 250-bar year counts as a full year", y["full_year"] is True)

    # 10. a partial year is flagged and left out of the verdict
    idx2 = pd.bdate_range("2024-12-01", periods=20)
    r2 = pd.Series([0.001] * 20, index=idx2)
    repos2 = pd.Series([0.0] * 20, index=idx2)
    ya2 = year_axis(r2, repos2, 100000.0, 200.0, 20.0)
    v2 = verdict({"sessions_to_fill": 5}, ya2, 100.0, 20.0)
    leg("L10 a 20-bar year is not a full year and cannot pass the verdict",
        ya2["2024"]["full_year"] is False and v2 == ["WAIT_NEVER_FITS_IN_A_FULL_YEAR"], str(v2))

    # 11-14. verdict ladder
    def mk(days_list, extra_pp=1.0):
        out = {}
        for i, d in enumerate(days_list):
            out[str(2020 + i)] = {"full_year": True, "extra_pp": extra_pp, "bars": 250,
                                  "payback_days_p95": d}
        return out
    leg("L11 all years inside the budget",
        verdict({"sessions_to_fill": 5}, mk([5.0, 10.0]), 100.0, 20.0) == ["WAIT_FITS_IN_EVERY_FULL_YEAR"])
    leg("L12 one year outside names the good-year verdict",
        "WAIT_FITS_ONLY_IN_GOOD_YEARS" in verdict({"sessions_to_fill": 5}, mk([5.0, 60.0]), 100.0, 20.0))
    leg("L13 no year inside says so",
        "WAIT_NEVER_FITS_IN_A_FULL_YEAR" in verdict({"sessions_to_fill": 5}, mk([60.0, 90.0]), 100.0, 20.0))
    leg("L14 a negative-extra year is tagged",
        "EXTRA_GOES_NEGATIVE_IN_YEARS" in verdict({"sessions_to_fill": 5}, mk([5.0], extra_pp=-0.4), 100.0, 20.0))
    leg("L15 one session wins before any wait arithmetic",
        verdict({"sessions_to_fill": 1}, {}, 100.0, 20.0) == ["ONE_SESSION_NO_WAIT"])
    leg("L16 no window extra => no denominator",
        verdict({"sessions_to_fill": 5}, mk([5.0]), -1.0, 20.0) == ["NO_EXTRA_TO_PAY_BACK"])

    # 17-19. the live face's invariants
    face = build()
    body = render_block(face)
    leg("L17 rendered block prints no doubled per-cent sign", "%%" not in body)
    leg("L18 every shelf appears in the block",
        all(("`%s`" % r["code"]) in body for r in face["rows"]))
    pay = _load(PAYBACK_FACE)
    leg("L19 the budget printed is the upstream one, not a local copy",
        float(face["headline"]["budget_sessions"]) == float(pay["adoption"]["budget_sessions"]))

    # 20-21. upstream agreement: shelves whose caliber is unchanged must match r2041 exactly
    mism = [r for r in face["rows"]
            if r["published_own_net_cagr_pct"] is not None
            and abs(r["window_cagr_before_neutralisation_pct"] - r["published_own_net_cagr_pct"]) > 0.01]
    leg("L20 every shelf reproduces r2041's own CAGR before neutralisation (<=0.01pp)",
        not mism, str([r["code"] for r in mism]))
    moved = [r for r in face["rows"] if abs(r["quote_audit"]["flip_effect_pp_per_year"]) > 0]
    leg("L21 a flip moves the window extra in the direction the audit claims",
        all(r["window_cagr_pct"] < r["window_cagr_before_neutralisation_pct"] for r in moved),
        str([(r["code"], r["window_cagr_pct"], r["window_cagr_before_neutralisation_pct"]) for r in moved]))

    passed = sum(1 for _, ok, _ in legs if ok)
    for name, ok, detail in legs:
        print(("PASS " if ok else "FAIL ") + name + (("  [" + detail + "]") if detail and not ok else ""))
    print("SELFTEST %d/%d" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "run":
        return cmd_run()
    if cmd == "--check":
        return cmd_check()
    if cmd == "--selftest":
        return cmd_selftest()
    if cmd == "show":
        print(json.dumps(build()["headline"], ensure_ascii=False, indent=1))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
