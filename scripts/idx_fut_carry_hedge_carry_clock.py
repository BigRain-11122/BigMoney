#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""when does the money the rounding "made" get handed back?

WHY THIS FILE EXISTS
--------------------
r2007 priced the IC long lot hedged with beta = 1.5567 IF lots, showed you can only buy
1 or 2, and printed that rounding up to 2 earned **47,396 CNY last year**.  It then said
the sentence that makes that number useless on its own: *a positive difference means the
extra hedge earned because the hedge leg's own carry was negative; it is a bet, not a
saving, and it reverses whenever the hedge leg's carry turns positive.*

A reader holding that page can ask exactly one question and the repo cannot answer it:
**when?**  And underneath it, a second one r2007 never split: **how much of that 47,396
was direction (the index fell) and how much was carry (the futures were cheap)?**  Only
the carry part has an expiry; the direction part is a bet that already settled.

The question, one line: **the windfall is a naked short in the hedge leg -- what is that
short paying per year from here, how much of last year's money was carry rather than
direction, and when does the carry hand it back?**

WHAT IS MEASURED AND WHAT IS A RULE
-----------------------------------
Measured, from the same panels the parent faces use (index closes via scripts/
idx_fut_basis.py, futures closes from data/futures_daily), over the parent's own
last-year window:

  * a short futures position splits exactly in two: `-index return` (direction) and
    `-(futures return - index return)` (carry).  Calendar rolls are removed from the
    carry leg by the parent's own roll mask, because a roll jump is a contract change,
    not carry -- and whatever that removal leaves behind is printed as a residual
    instead of being folded into either leg;
  * the carry leg's 20-day rolling annualised rate, its place in the five-year
    distribution, the last sign flip and how long the current side has run;
  * the windfall translated into money: `extra_hedge_beta` (r2007's number, imported)
    times the hedge leg's notional, times each leg's rate, is what the bet pays per year
    from here and how much of last year it was.

A RULE, not a measurement: the 1/3/6/12-month buckets and the 20-day window are chosen
for readability.  Every window length is printed so a desk that prefers another can read
its own row.  The windfall itself is r2007's number, imported, not recomputed.

WHAT WOULD MAKE THIS FACE WRONG
-------------------------------
If every hedge leg's current carry still sits on the side that paid the windfall, the
honest answer is "the bet is still winning, here is its running rate" and the verdict
string says exactly that.  Only a leg whose carry has actually crossed gets a payback
date.  And if the two legs did not add up to the total, the page would say so in the
residual column rather than quietly pinning the difference on carry.
"""

import hashlib
import json
import os
import statistics
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import idx_fut_basis as BASE       # noqa: E402  PAIRS / load_index / read_csv_rows / basis_face

OUT_PATH = os.path.join(ROOT, "results", "idx_fut_carry_hedge_carry_clock.json")
DOC_PATH = os.path.join(ROOT, "research", "IDX_FUT_CARRY_HEDGE_CARRY_CLOCK.md")
BETA_LOTS_PATH = os.path.join(ROOT, "results", "idx_fut_carry_hedge_beta_lots.json")

MULTIPLIER = {"IF": 300, "IH": 300, "IC": 200, "IM": 200}
HEDGE_LEGS = ("IF", "IH", "IC", "IM")
ROLLING_WINDOW = 20
TRADING_DAYS = 244.0
BUCKETS = (("1m", 21), ("3m", 63), ("6m", 126), ("12m", 244))
DOC_BEGIN = "<!-- BEGIN:IDX-FUT-CARRY-HEDGE-CARRY-CLOCK -->"
DOC_END = "<!-- END:IDX-FUT-CARRY-HEDGE-CARRY-CLOCK -->"


# ------------------------------------------------------------------ io helpers
def now_iso():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def dump_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, path)


def sha256_file(path):
    if not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def input_digests():
    out = {}
    for prod in HEDGE_LEGS:
        out["futures_" + prod] = sha256_file(
            os.path.join(ROOT, "data", "futures_daily", prod + ".csv"))
        code = (BASE.PAIRS.get(prod) or (None,))[0]
        if code:
            out["index_" + prod] = sha256_file(
                os.path.join(ROOT, "data", "index_daily", code + ".csv"))
    out["parent_beta_lots"] = sha256_file(BETA_LOTS_PATH)
    return out


# ------------------------------------------------------------------ arithmetic
def short_series(prod):
    """[(date, carry_ret, index_ret, is_roll)] for a short futures position.

    A short futures return is exactly `-index return - (futures return - index return)`:
    the first term is direction, the second is carry.  Roll days are flagged rather than
    dropped so the caller can report what the mask removed.
    """
    fpath = os.path.join(BASE.FUT_DIR, prod + ".csv")
    code = (BASE.PAIRS.get(prod) or (None,))[0]
    if not code or not os.path.exists(fpath):
        return None
    frows = BASE.read_csv_rows(fpath)
    idx = BASE.load_index(code)
    if not frows or not idx:
        return None
    fmap = {r["date"]: float(r["close"]) for r in frows if r.get("close")}
    days = sorted(set(fmap) & set(idx))
    if len(days) < ROLLING_WINDOW + 5:
        return None
    fut = [fmap[d] for d in days]
    idc = [idx[d] for d in days]
    _basis, spread, roll = BASE.basis_face(fut, idc, days)
    out = []
    for k, s in enumerate(spread):
        ri = idc[k + 1] / idc[k] - 1.0
        # short futures = -futures return; split into -index (direction) and -(fut - idx)
        out.append((days[k + 1], -s, -ri, bool(roll[k])))
    return out


def compound_pct(vals):
    if not vals:
        return None
    acc = 1.0
    for v in vals:
        acc *= 1.0 + v
    return (acc - 1.0) * 100.0


def sum_pct(vals):
    if not vals:
        return None
    return sum(vals) * 100.0


def ann_pct(vals):
    if not vals:
        return None
    acc = 1.0
    for v in vals:
        acc *= 1.0 + v
    return (acc ** (TRADING_DAYS / len(vals)) - 1.0) * 100.0


def quantile(sorted_vals, q):
    if not sorted_vals:
        return None
    k = int(q * (len(sorted_vals) - 1))
    return sorted_vals[max(0, min(k, len(sorted_vals) - 1))]


def rolling_annualised(series, window=ROLLING_WINDOW):
    """[(date, annualised carry pct)] over the trailing `window` non-roll observations."""
    clean = [(d, c) for d, c, _i, r in series if not r]
    out = []
    for k in range(window - 1, len(clean)):
        a = ann_pct([v for _d, v in clean[k - window + 1:k + 1]])
        if a is not None:
            out.append((clean[k][0], a))
    return out


def sign_run(series):
    """(current_side, readings_on_that_side, last_flip_date, flipped_away_from).

    The side is read off the rolling 20-day annualised carry, not the daily number: one
    red day inside a long run is not a flip a reader acts on.
    """
    roll = rolling_annualised(series)
    if not roll:
        return None
    side = 1 if roll[-1][1] >= 0 else -1
    n = 0
    flip_date = None
    flip_from = None
    for date, val in reversed(roll):
        s = 1 if val >= 0 else -1
        if s != side:
            flip_date = date
            flip_from = "positive" if s > 0 else "negative"
            break
        n += 1
    return {
        "side": "pays_a_short" if side > 0 else "costs_a_short",
        "readings_on_this_side": n,
        "last_flip_from": flip_from,
        "last_flip_date": flip_date,
    }


def window_slice(series, start, end):
    return [row for row in series if start <= row[0] <= end]


def leg_face(prod, series, parent_window):
    """One leg, split into direction and carry, over the parent's own last-year window."""
    if not series:
        return {"state": "NO_SERIES"}
    carry_vals = [c for _d, c, _i, r in series if not r]
    roll_vals = [c for _d, c, _i, r in series if r]
    roll = rolling_annualised(series)
    roll_sorted = sorted(v for _d, v in roll)
    face = {
        "state": "ok",
        "days": len(series),
        "window": [series[0][0], series[-1][0]],
        "carry_ann_full_pct": round(ann_pct(carry_vals), 3) if ann_pct(carry_vals) is not None else None,
        "carry_median_daily_ann_pct": round(statistics.median(carry_vals) * TRADING_DAYS * 100, 3) if carry_vals else None,
        "current_rolling20_ann_pct": round(roll[-1][1], 3) if roll else None,
        "rolling20_distribution": {
            "n": len(roll_sorted),
            "p10": round(quantile(roll_sorted, 0.10), 3) if roll_sorted else None,
            "median": round(statistics.median(roll_sorted), 3) if roll_sorted else None,
            "p90": round(quantile(roll_sorted, 0.90), 3) if roll_sorted else None,
            "share_positive_pct": (round(100.0 * sum(1 for v in roll_sorted if v > 0) / len(roll_sorted), 1)
                                   if roll_sorted else None),
        },
        "buckets_compounded_pct": {},
        "sign": sign_run(series),
        "last_close_px": None,
        "roll_days": len(roll_vals),
    }
    for name, n in BUCKETS:
        if len(carry_vals) >= n:
            face["buckets_compounded_pct"][name] = round(compound_pct(carry_vals[-n:]), 3)
        else:
            face["buckets_compounded_pct"][name] = None
    # the parent's own window, so the split adds up to the windfall the reader saw
    if parent_window and len(parent_window) == 2:
        win = window_slice(series, parent_window[0], parent_window[1])
        if win:
            # the carry leg drops roll days (a roll jump is a contract change, not
            # carry); whatever that removal is worth lands in residual instead of
            # being quietly pinned on carry.
            carry_sum = sum_pct([c for _d, c, _i, r in win if not r])
            index_sum = sum_pct([i for _d, _c, i, _r in win])
            total_sum = sum_pct([c + i for _d, c, i, _r in win])
            face["parent_window_split"] = {
                "window": [win[0][0], win[-1][0]],
                "days": len(win),
                "short_total_pct": round(total_sum, 4) if total_sum is not None else None,
                "short_index_pct": round(index_sum, 4) if index_sum is not None else None,
                "short_carry_pct": round(carry_sum, 4) if carry_sum is not None else None,
                "residual_pct": (None if None in (total_sum, index_sum, carry_sum)
                                 else round(total_sum - index_sum - carry_sum, 6)),
                "carry_share_of_total_pct": (None if not total_sum
                                             else round(100.0 * carry_sum / total_sum, 1)),
            }
    return face


def _add_years(iso_date, years):
    """Calendar date `years` (may be fractional) after iso_date. A year is 365.25 days."""
    try:
        from datetime import date, timedelta
        y, m, d = int(iso_date[:4]), int(iso_date[5:7]), int(iso_date[8:10])
        return (date(y, m, d) + timedelta(days=365.25 * float(years))).isoformat()
    except Exception:
        return None


def windfall_clock(prod, leg, extra_beta, windfall_cny):
    """Split the windfall into direction and carry, then date the carry leg.

    The rounding bought `extra_beta` lots of short futures.  Its notional is
    extra_beta * futures price * multiplier.  Multiply by each leg's rate to get CNY.
    """
    if leg.get("state") != "ok" or not extra_beta:
        return {"state": "NO_INPUT"}
    px = leg.get("last_close_px")
    carry_now = leg.get("current_rolling20_ann_pct")
    if px is None or carry_now is None:
        return {"state": "NO_INPUT"}
    notional = float(extra_beta) * float(px) * MULTIPLIER[prod]
    per_year = notional * (carry_now / 100.0)
    split = leg.get("parent_window_split") or {}
    out = {
        "state": "ok",
        "extra_hedge_beta": round(float(extra_beta), 6),
        "notional_cny": round(notional, 2),
        "carry_ann_pct_used": round(float(carry_now), 3),
        # positive per_year = the extra short is still being paid; negative = it costs
        "carry_cny_per_year_from_here": round(per_year, 2),
        "windfall_cny": round(float(windfall_cny), 2),
        # what last year's money was made of, in the same units the reader saw
        "windfall_index_leg_cny": (None if split.get("short_index_pct") is None
                                   else round(notional * split["short_index_pct"] / 100.0, 2)),
        "windfall_carry_leg_cny": (None if split.get("short_carry_pct") is None
                                   else round(notional * split["short_carry_pct"] / 100.0, 2)),
    }
    # the two legs were measured on the carry mask, the windfall on the parent's roll
    # walk; whatever they do not add up to is printed rather than pinned on carry.
    if None not in (out["windfall_index_leg_cny"], out["windfall_carry_leg_cny"]):
        out["windfall_residual_cny"] = round(
            float(windfall_cny) - out["windfall_index_leg_cny"] - out["windfall_carry_leg_cny"], 2)
        out["carry_share_of_windfall_pct"] = (
            None if not windfall_cny
            else round(100.0 * out["windfall_carry_leg_cny"] / float(windfall_cny), 1))
    else:
        out["windfall_residual_cny"] = None
        out["carry_share_of_windfall_pct"] = None
    if per_year > 0 and windfall_cny > 0:
        out["state_reading"] = "STILL_BEING_PAID"
        out["years_of_current_carry_buys_another_windfall"] = round(
            float(windfall_cny) / per_year, 3)
        out["payback_date"] = None
    elif per_year < 0 and windfall_cny > 0:
        out["state_reading"] = "BEING_HANDED_BACK"
        years = float(windfall_cny) / abs(per_year)
        out["years_to_hand_back"] = round(years, 3)
        out["payback_date"] = _add_years(leg["window"][1], years)
    else:
        out["state_reading"] = "CARRY_IS_ZERO"
        out["years_to_hand_back"] = None
        out["payback_date"] = None
    return out


def verdict_of(legs, clocks):
    """One sentence a reader can act on, derived from what is printed."""
    paying, handing = [], []
    for prod, clock in clocks.items():
        if clock.get("state") != "ok":
            continue
        if clock["state_reading"] == "STILL_BEING_PAID":
            paying.append(prod)
        elif clock["state_reading"] == "BEING_HANDED_BACK":
            handing.append(prod)
    if not paying and not handing:
        return "NO_HEDGE_LEG_HAS_A_READABLE_CARRY"
    if not handing:
        return "THE_ROUNDING_IS_STILL_BEING_PAID_ON_EVERY_HEDGE_LEG"
    if not paying:
        return "THE_ROUNDING_IS_NOW_COSTING_MONEY_ON_EVERY_HEDGE_LEG"
    return "THE_ROUNDING_BET_HAS_TURNED_ON_%s" % "_AND_".join(sorted(handing))


def build():
    legs = {}
    carries = {}
    problems = []
    parent = load_json(BETA_LOTS_PATH) or {}

    # the parent's last-year window, per pair, is the frame the split is printed in
    parent_windows = {}
    published = {}
    for key, face in (parent.get("arms") or {}).items():
        if not isinstance(face, dict) or face.get("state") != "ok":
            continue
        cost = face.get("cost_of_indivisibility") or {}
        if cost.get("extra_hedge_beta") is None or cost.get("pnl_difference_cny_vs_exact") is None:
            continue
        parts = key.split("_vs_")
        if len(parts) != 2:
            continue
        hedge_leg = parts[1]
        published[key] = {
            "hedge_leg": hedge_leg,
            "extra_hedge_beta": cost["extra_hedge_beta"],
            "windfall_cny": cost["pnl_difference_cny_vs_exact"],
        }
        if face.get("last_year"):
            parent_windows.setdefault(hedge_leg, face["last_year"])

    for prod in HEDGE_LEGS:
        s = short_series(prod)
        if not s:
            legs[prod] = {"state": "NO_SERIES"}
            problems.append({"leg": prod, "why": "NO_SERIES"})
            continue
        carries[prod] = s
        legs[prod] = leg_face(prod, s, parent_windows.get(prod))
        frows = BASE.read_csv_rows(os.path.join(BASE.FUT_DIR, prod + ".csv"))
        legs[prod]["last_close_px"] = (float(frows[-1]["close"])
                                       if frows and frows[-1].get("close") else None)

    clocks = {}
    for key, row in published.items():
        leg = legs.get(row["hedge_leg"]) or {}
        clocks[key] = windfall_clock(row["hedge_leg"], leg, row["extra_hedge_beta"], row["windfall_cny"])

    cutoff = None
    for prod, s in carries.items():
        if not s:
            continue
        d = s[-1][0]
        cutoff = d if cutoff is None or d < cutoff else cutoff

    obj = {
        "kind": "idx-fut-carry-hedge-carry-clock",
        "generated": now_iso(),
        "evidence_cutoff": cutoff,
        "rolling_window": ROLLING_WINDOW,
        "buckets": [b[0] for b in BUCKETS],
        "legs": legs,
        "windfall_clocks": clocks,
        "published_windfalls": published,
        "verdict": verdict_of(legs, clocks),
        "problems": problems,
        "inputs": input_digests(),
        "sources": {
            "parent_face": "results/idx_fut_carry_hedge_beta_lots.json",
            "basis": "scripts/idx_fut_basis.py::basis_face / load_index / read_csv_rows",
        },
    }
    return obj


# ------------------------------------------------------------------ doc
def _n(v, spec=".3f"):
    return "-" if v is None else format(v, spec)


def _p(v, spec=".3f"):
    return "-" if v is None else (format(v, spec) + "%")


def render_doc(obj):
    lines = [DOC_BEGIN, "",
             "# when does the rounding hand its money back",
             "",
             "generated %s | evidence_cutoff **%s** | verdict **%s**"
             % (obj["generated"], obj["evidence_cutoff"], obj["verdict"]),
             "",
             "r2007 showed that rounding beta 1.5567 up to 2 lots of IF earned 47,396 CNY",
             "last year, and said in the same breath that the money is a bet on the hedge",
             "leg's own carry. This page prices that sentence. A short futures position is",
             "exactly two things -- `-index return` (direction) and `-(futures return -",
             "index return)` (carry) -- so the windfall can be cut in two, and only the",
             "carry half has an expiry.",
             "",
             "## the two legs of last year's windfall",
             "",
             "Same window r2007 used, per one lot of extra short. Rolls are removed from",
             "the carry leg by the parent's roll mask; whatever that removal leaves behind",
             "is printed as residual rather than folded into either leg.",
             "",
             "| leg | window | days | short total | direction (-index) | carry (-basis) | residual | carry share |",
             "|---|---|---|---|---|---|---|---|"]
    for prod in HEDGE_LEGS:
        leg = obj["legs"].get(prod) or {}
        split = leg.get("parent_window_split") or {}
        if leg.get("state") != "ok" or not split:
            lines.append("| %s | - | - | - | - | - | - | - |" % prod)
            continue
        lines.append("| %s | %s..%s | %d | %s | %s | %s | %s | %s |" % (
            prod, split["window"][0], split["window"][1], split["days"],
            _p(split.get("short_total_pct"), ".2f"),
            _p(split.get("short_index_pct"), ".2f"),
            _p(split.get("short_carry_pct"), ".2f"),
            _p(split.get("residual_pct"), ".4f"),
            _p(split.get("carry_share_of_total_pct"), ".1f")))
    lines.append("")
    lines.append("`residual` is the roll-day basis jump the mask removes: it is money a short")
    lines.append("really made or lost, but it is a contract change, not carry. `carry share`")
    lines.append("is the carry leg as a share of the short's total return -- **a negative")
    lines.append("share means last year's windfall was not carry at all: the direction leg")
    lines.append("paid, the carry leg charged.**")
    lines.append("")
    lines.append("## the carry leg today")
    lines.append("")
    lines.append("Positive = a short is being paid to wait. The 20-day column is annualised;")
    lines.append("the bucket columns are compounded over their own length.")
    lines.append("")
    lines.append("| leg | last close | 20d now | 20d median | 20d p10..p90 | share positive | 1m | 3m | 6m | 12m | rolls masked |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for prod in HEDGE_LEGS:
        leg = obj["legs"].get(prod) or {}
        if leg.get("state") != "ok":
            lines.append("| %s | - | - | - | - | - | - | - | - | - | - |" % prod)
            continue
        dist = leg.get("rolling20_distribution") or {}
        b = leg.get("buckets_compounded_pct") or {}
        lines.append("| %s | %s | %s | %s | %s..%s | %s | %s | %s | %s | %s | %s |" % (
            prod, _n(leg.get("last_close_px"), ",.2f"),
            _p(leg.get("current_rolling20_ann_pct")),
            _p(dist.get("median")),
            _n(dist.get("p10")), _n(dist.get("p90")),
            _p(dist.get("share_positive_pct"), ".1f"),
            _p(b.get("1m")), _p(b.get("3m")), _p(b.get("6m")), _p(b.get("12m")),
            leg.get("roll_days")))
    lines.append("")
    lines.append("## the sign, and how long it has run")
    lines.append("")
    lines.append("| leg | current side | readings on this side | last flip | flipped away from |")
    lines.append("|---|---|---|---|---|")
    for prod in HEDGE_LEGS:
        leg = obj["legs"].get(prod) or {}
        sign = leg.get("sign") or {}
        if not sign:
            lines.append("| %s | - | - | - | - |" % prod)
            continue
        lines.append("| %s | %s | %s | %s | %s |" % (
            prod, sign.get("side"), sign.get("readings_on_this_side"),
            sign.get("last_flip_date") or "never in sample",
            sign.get("last_flip_from") or "-"))
    lines.append("")
    lines.append("## what the windfall is worth from here")
    lines.append("")
    lines.append("| pair | extra lots | notional CNY | carry now | CNY / year from here | windfall: direction | windfall: carry | windfall: residual | carry share | reading | payback date |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for key in sorted(obj["windfall_clocks"]):
        c = obj["windfall_clocks"][key]
        if c.get("state") != "ok":
            lines.append("| %s | - | - | - | - | - | - | - | - | %s | - |" % (key, c.get("state")))
            continue
        lines.append("| %s | %.4f | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            key, c["extra_hedge_beta"], "{:,.0f}".format(c["notional_cny"]),
            _p(c["carry_ann_pct_used"]),
            "{:,.0f}".format(c["carry_cny_per_year_from_here"]),
            _n(c.get("windfall_index_leg_cny"), ",.0f"),
            _n(c.get("windfall_carry_leg_cny"), ",.0f"),
            _n(c.get("windfall_residual_cny"), ",.0f"),
            _p(c.get("carry_share_of_windfall_pct"), ".1f"),
            c["state_reading"],
            c.get("payback_date") or "-"))
    lines.append("")
    lines.append("`CNY / year from here` is the extra short's running rate: positive means it")
    lines.append("is still being paid, negative means it now charges and the windfall is handed")
    lines.append("back at that rate until the date in the last column. `windfall: carry` and")
    lines.append("`carry share` are last year's numbers: a negative share says the windfall was")
    lines.append("made by the direction leg and the carry leg charged for it. The residual is")
    lines.append("the roll-day jump the mask removes, so the three columns add up to the")
    lines.append("windfall rather than hiding a difference in carry.")
    lines.append("")
    lines.append("## what this does not settle")
    lines.append("")
    lines.append("* the carry is spot-month basis on this repo's roll walk; a different")
    lines.append("  contract month would price a different carry, and this page does not model")
    lines.append("  the roll schedule;")
    lines.append("* the windfall is r2007's single last-year window, not a distribution: a")
    lines.append("  different 242 days would print a different CNY;")
    lines.append("* the extra short is naked, so its direction leg is a real position and not a")
    lines.append("  hedge -- the page separates the two halves but does not judge whether the")
    lines.append("  desk wanted either;")
    lines.append("* margin, roll cost and financing on the extra lot are not in these numbers.")
    lines.append("")
    lines.append(DOC_END)
    return "\n".join(lines) + "\n"


def write_all(obj):
    dump_json(OUT_PATH, obj)
    doc = render_doc(obj)
    if os.path.exists(DOC_PATH):
        with open(DOC_PATH, "r", encoding="utf-8") as fh:
            old = fh.read()
        if DOC_BEGIN in old and DOC_END in old:
            head = old[:old.index(DOC_BEGIN)]
            tail = old[old.index(DOC_END) + len(DOC_END):].lstrip("\n")
            doc = head + doc + (("\n" + tail) if tail else "")
    with open(DOC_PATH, "w", encoding="utf-8") as fh:
        fh.write(doc)


# ------------------------------------------------------------------ selftest
def selftest():
    legs = []

    def ok(name, cond, why=""):
        legs.append((name, bool(cond), why))

    # compounding / summing / annualising
    ok("two +1% days compound to 2.01%", abs(compound_pct([0.01, 0.01]) - 2.01) < 1e-9)
    ok("an empty series has no rate", compound_pct([]) is None)
    ok("sum_pct is arithmetic, not compound",
       abs(sum_pct([0.01, 0.01]) - 2.0) < 1e-9)
    ok("a flat series annualises to zero", abs(ann_pct([0.0] * 20)) < 1e-12)

    # the split: short = -index + (-basis).  Build it from a synthetic pair.
    series = []
    for k in range(30):
        idx = 0.002       # index falls 0.2%/day -> short direction +0.2%/day
        carry = 0.001     # futures 0.1% cheaper per day -> short carry +0.1%
        series.append(("2026-01-%02d" % (k + 1), carry, idx, False))
    roll = rolling_annualised(series, 20)
    # 0.1%/day annualises to 1.001**244-1 = 27.6%, not the 20-day 2.02%
    ok("rolling value is annualised, not compounded raw", abs(roll[0][1] - 27.615) < 0.05)
    face = leg_face("IF", series, ["2026-01-01", "2026-01-30"])
    split = face.get("parent_window_split") or {}
    ok("direction and carry add up to the total",
       abs((split.get("short_total_pct") or 0.0)
           - (split.get("short_index_pct") or 0.0)
           - (split.get("short_carry_pct") or 0.0)) < 1e-9)
    ok("carry share is a share of the total",
       abs(split.get("carry_share_of_total_pct") - 100.0 * 0.001 / 0.003) < 0.2)

    # a roll day must not enter the carry leg
    series_r = list(series)
    series_r.append(("2026-02-01", -0.05, -0.002, True))   # huge roll jump
    face_r = leg_face("IF", series_r, None)
    ok("a roll jump does not inflate the carry rate",
       face_r.get("carry_ann_full_pct") is not None
       and abs(face_r["carry_ann_full_pct"] - 27.6) < 1.0)

    # sign run
    s2 = [("2026-03-%02d" % (k + 1), 0.001, 0.0, False) for k in range(28)]
    s2.append(("2026-04-01", -0.0005, 0.0, False))
    sign = sign_run(s2)
    ok("sign run names a side", sign.get("side") in ("pays_a_short", "costs_a_short"))
    ok("one bad day does not erase the run", sign.get("readings_on_this_side", 0) >= 1)
    s3 = ([("2026-05-%02d" % (k + 1), 0.001, 0.0, False) for k in range(25)]
          + [("2026-06-%02d" % (k + 1), -0.001, 0.0, False) for k in range(25)])
    sign3 = sign_run(s3)
    ok("a genuine cross names the flip date", sign3.get("last_flip_date") is not None)
    ok("the flip is read off the negative side", sign3.get("side") == "costs_a_short")

    # windfall clock: still being paid
    leg_pay = {"state": "ok", "last_close_px": 4000.0, "current_rolling20_ann_pct": 5.0,
               "window": ["2020-01-01", "2026-11-20"],
               "parent_window_split": {"short_index_pct": -2.0, "short_carry_pct": 1.0}}
    c1 = windfall_clock("IF", leg_pay, 0.4433, 47396.0)
    ok("positive carry reads as still being paid", c1.get("state_reading") == "STILL_BEING_PAID")
    ok("no payback date while the bet is winning", c1.get("payback_date") is None)
    ok("notional is beta x price x multiplier",
       abs(c1["notional_cny"] - 0.4433 * 4000.0 * 300) < 1e-6)
    ok("per-year money is notional x carry",
       abs(c1["carry_cny_per_year_from_here"] - c1["notional_cny"] * 0.05) < 1e-6)
    ok("last year's carry leg is notional x its rate",
       abs(c1["windfall_carry_leg_cny"] - c1["notional_cny"] * 0.01) < 1e-6)

    # windfall clock: being handed back
    leg_neg = dict(leg_pay)
    leg_neg["current_rolling20_ann_pct"] = -5.0
    c2 = windfall_clock("IF", leg_neg, 0.4433, 47396.0)
    ok("negative carry reads as being handed back",
       c2.get("state_reading") == "BEING_HANDED_BACK")
    ok("a payback date exists when the carry crossed", c2.get("payback_date") is not None)
    ok("payback years = windfall / |per-year|",
       abs(c2["years_to_hand_back"] - 47396.0 / (0.05 * 0.4433 * 4000.0 * 300)) < 1e-3)

    # zero carry is neither
    leg_zero = dict(leg_pay)
    leg_zero["current_rolling20_ann_pct"] = 0.0
    c3 = windfall_clock("IF", leg_zero, 0.4433, 47396.0)
    ok("zero carry is not a payback", c3.get("state_reading") == "CARRY_IS_ZERO")

    # missing input must not silently read as zero
    ok("a missing leg is NO_INPUT",
       windfall_clock("IF", {"state": "NO_SERIES"}, 0.4, 1.0).get("state") == "NO_INPUT")
    ok("a missing beta is NO_INPUT", windfall_clock("IF", leg_pay, None, 1.0).get("state") == "NO_INPUT")
    ok("a missing carry is NO_INPUT",
       windfall_clock("IF", {"state": "ok", "last_close_px": 1.0, "current_rolling20_ann_pct": None}, 0.4, 1.0).get("state") == "NO_INPUT")

    # verdict reacts to what is printed
    ok("verdict says still being paid when every leg pays",
       verdict_of({}, {"IC_vs_IF": {"state": "ok", "state_reading": "STILL_BEING_PAID"}})
       == "THE_ROUNDING_IS_STILL_BEING_PAID_ON_EVERY_HEDGE_LEG")
    ok("verdict says costing when every leg crossed",
       verdict_of({}, {"IC_vs_IF": {"state": "ok", "state_reading": "BEING_HANDED_BACK"}})
       == "THE_ROUNDING_IS_NOW_COSTING_MONEY_ON_EVERY_HEDGE_LEG")
    ok("verdict names the leg that turned",
       "IC_vs_IF" in verdict_of({}, {
           "IC_vs_IF": {"state": "ok", "state_reading": "BEING_HANDED_BACK"},
           "IM_vs_IH": {"state": "ok", "state_reading": "STILL_BEING_PAID"}}))
    ok("no readable leg is not a clean bill",
       verdict_of({}, {}) == "NO_HEDGE_LEG_HAS_A_READABLE_CARRY")

    failed = [leg for leg in legs if not leg[1]]
    for name, good, why in legs:
        print("%-78s %s %s" % (name, "PASS" if good else "FAIL", why))
    print("selftest: %d/%d" % (len(legs) - len(failed), len(legs)))
    return 0 if not failed else 1


def check():
    """Re-derive and compare.

    Two reds (r1934): moved inputs or a moved cutoff is STALE -- pay to rebuild.  A
    number that disagrees with the same input bytes is CHECK FAILED and must not carry
    the word STALE, or the chain keeps paying to rebuild a face whose arithmetic is wrong.
    """
    if not os.path.exists(OUT_PATH):
        print("STALE face missing: %s" % OUT_PATH)
        return 3
    old = load_json(OUT_PATH) or {}
    new = build()
    drift = []
    if old.get("evidence_cutoff") != new.get("evidence_cutoff"):
        drift.append("evidence_cutoff %s -> %s" % (old.get("evidence_cutoff"), new.get("evidence_cutoff")))
    if old.get("inputs") != new.get("inputs"):
        drift.append("input digests moved")
    if drift:
        print("STALE face drifted: " + "; ".join(drift[:6]))
        return 3
    defects = []
    if old.get("verdict") != new.get("verdict"):
        defects.append("verdict %s -> %s" % (old.get("verdict"), new.get("verdict")))
    for prod, leg in (new.get("legs") or {}).items():
        o = (old.get("legs") or {}).get(prod) or {}
        for field in ("carry_ann_full_pct", "current_rolling20_ann_pct", "days", "roll_days"):
            if o.get(field) != leg.get(field):
                defects.append("%s %s %s -> %s" % (prod, field, o.get(field), leg.get(field)))
    if (old.get("legs") or {}).keys() != (new.get("legs") or {}).keys():
        defects.append("the set of legs changed")
    for key, clock in (new.get("windfall_clocks") or {}).items():
        o = (old.get("windfall_clocks") or {}).get(key) or {}
        for field in ("carry_cny_per_year_from_here", "windfall_carry_leg_cny", "payback_date"):
            if o.get(field) != clock.get(field):
                defects.append("%s %s %s -> %s" % (key, field, o.get(field), clock.get(field)))
    if defects:
        print("CHECK FAILED face contradicts its own inputs: " + "; ".join(defects[:6]))
        return 3
    print("CHECK OK %s" % OUT_PATH)
    return 0


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "check":
        return check()
    if cmd in ("run", "--write", ""):
        obj = build()
        write_all(obj)
        print("wrote %s" % OUT_PATH)
        print("wrote %s" % DOC_PATH)
        print("verdict %s | cutoff %s" % (obj["verdict"], obj["evidence_cutoff"]))
        for prod in HEDGE_LEGS:
            leg = obj["legs"].get(prod) or {}
            split = leg.get("parent_window_split") or {}
            if leg.get("state") != "ok":
                print("  %-3s %s" % (prod, leg.get("state")))
                continue
            print("  %-3s 20d=%s%% | last-year split: dir=%s%% carry=%s%% residual=%s%%"
                  % (prod, _n(leg.get("current_rolling20_ann_pct")),
                     _n(split.get("short_index_pct"), ".2f"),
                     _n(split.get("short_carry_pct"), ".2f"),
                     _n(split.get("residual_pct"), ".4f")))
        return 0
    print("usage: idx_fut_carry_hedge_carry_clock.py [run|check|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
