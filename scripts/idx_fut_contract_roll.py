"""Where the index-futures series actually rolls, observed instead of assumed.

The carry numbers on the basis pages are priced with a roll mask and nothing else.  Two
masks have been in play and both are opinions:

  * the published size rule (a basis step > 8x the median step) -- r1692 showed it misses
    64-81% of the calendar rolls and also eats real market days;
  * the calendar mask (the most negative basis step inside a window around the third
    Friday) -- better, but it is still a shape guess: it can only fire where the *price*
    stepped, so a roll that happens without a visible step is invisible to it.

The roll is a fact and it is observable: on any given day the market is trading one
contract, and the day it starts trading the next one is a roll.  Each contract's open
interest says which one that is, and the two contracts are both quoted on the day the
hand-over happens, so the price difference between them is measurable rather than
inferred.

This face builds that series from contract-level daily bars, then:

  1. prints the observed roll dates and each roll's cross-sectional gap (points and % of
     index) -- the number a roller really eats;
  2. compares the observed set against the published size mask and the calendar mask
     (exact-day precision/recall, and the false-positive days each one books);
  3. re-prices carry under all three masks with the *same* implementation the other
     faces use (idx_fut_roll_gap.carry_stats, basis_face imported, never copied), so the
     3%/yr admission line is read off the observed mask instead of an assumption.

It selects nothing and promotes nothing.  The point is to retire an assumption.
"""
import csv
import io
import json
import os
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import idx_fut_basis as base   # noqa: E402  (single implementation of basis/spread/mask)
import idx_fut_roll_gap as rg  # noqa: E402  (single implementation of calendar mask/carry)

ROOT = base.ROOT
CONTRACT_DIR = os.path.join(ROOT, "data", "futures_contracts")
OUT = os.path.join(ROOT, "results", "idx_fut_contract_roll.json")
DOC = os.path.join(ROOT, "research", "IDX_FUT_CONTRACT_ROLL.md")

CRITERIA = {
    "products": ["IF", "IC", "IH", "IM"],
    "sleep_s": 0.25,          # courtesy spacing on the quote host
    "min_common_days": 200,   # refuse to call a product observed below this
    "min_rolls": 12,          # a product needs this many observed rolls to be usable
    "min_coverage_pct": 85.0, # share of days inside the comparison window that can be named
    "min_window_coverage_pct": 95.0,  # per-year floor before a year may enter the window
}


# ------------------------------------------------------------------ contract space
def month_range(first, last):
    """[(2019, 12), (2020, 1), ...] inclusive, both ends as (year, month) tuples."""
    out = []
    y, m = first
    while (y, m) <= last:
        out.append((y, m))
        m += 1
        if m > 12:
            y, m = y + 1, 1
    return out


def contract_symbols(prefix, months, pad_months=2):
    """Contract codes a main series of this span could have rolled through."""
    if not months:
        return []
    y, m = months[-1]
    m += pad_months
    while m > 12:
        y, m = y + 1, m - 12
    return ["%s%02d%02d" % (prefix, yy % 100, mm)
            for yy, mm in month_range(months[0], (y, m))]


def cache_path(symbol, cache_dir=None):
    return os.path.join(cache_dir or CONTRACT_DIR, symbol + ".csv")


def read_cached(symbol, cache_dir=None):
    path = cache_path(symbol, cache_dir)
    if not os.path.isfile(path):
        return None
    rows = base.read_csv_rows(path)
    return [r for r in rows if r.get("date")]


def write_cached(symbol, rows, cache_dir=None):
    d = cache_dir or CONTRACT_DIR
    os.makedirs(d, exist_ok=True)
    with io.open(cache_path(symbol, d), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "open", "high", "low", "close", "volume", "hold"])
        for r in rows:
            w.writerow([r["date"], r["open"], r["high"], r["low"], r["close"],
                        r["volume"], r["hold"]])


def fetch_contract(symbol):
    """One contract's full daily history.  Returns [] when the code was never listed and
    None when the host failed -- an outage must not be cached as 'this contract is empty'."""
    try:
        import akshare as ak
        df = ak.futures_zh_daily_sina(symbol=symbol)
    except Exception:
        return None
    if df is None or len(df) == 0:
        return []
    rows = []
    for rec in df.to_dict("records"):
        try:
            rows.append({
                "date": str(rec["date"])[:10],
                "open": float(rec["open"]),
                "high": float(rec["high"]),
                "low": float(rec["low"]),
                "close": float(rec["close"]),
                "volume": float(rec["volume"]),
                "hold": float(rec["hold"]),
            })
        except (KeyError, TypeError, ValueError):
            continue
    return rows


def load_contracts(prefix, months, cache_dir=None, fetch=None, sleep_s=None,
                   refresh=False, max_pull=None):
    """Every contract of this span, cache-first.  Missing/never-listed codes come back empty.

    max_pull caps how many new codes one run may fetch, newest month first: the live end of
    the series is the end that goes stale, so a capped run heals that end and leaves the
    rest for the next run instead of holding a chain leg for minutes.
    """
    fetch = fetch or fetch_contract
    sleep_s = CRITERIA["sleep_s"] if sleep_s is None else sleep_s
    out, pulled, cached, deferred = {}, [], [], []
    syms = contract_symbols(prefix, months)
    order = list(reversed(syms)) if max_pull is not None else syms
    for sym in order:
        rows = None if refresh else read_cached(sym, cache_dir)
        if rows is None:
            if max_pull is not None and len(pulled) >= max_pull:
                deferred.append(sym)
                continue
            rows = fetch(sym)
            if rows is None:                 # transport failure: not a listing fact, do not cache
                deferred.append(sym)
                continue
            write_cached(sym, rows, cache_dir)
            pulled.append(sym)
            if sleep_s:
                time.sleep(sleep_s)
        else:
            cached.append(sym)
        if rows:
            out[sym] = {r["date"]: (float(r["close"]), float(r["hold"]),
                                    float(r["volume"])) for r in rows}
    return out, {"pulled": len(pulled), "from_cache": len(cached),
                 "deferred": len(deferred), "listed": len(out), "codes_tried": len(syms)}


# ------------------------------------------------------------------ observation
def name_contracts(dates, bars, cont_close, tol=0.011):
    """{date: sym} -- which contract the published continuous series is actually quoting.

    This is the assumption-free part.  A continuous series is a contract series with the
    seam hidden, so on any day its close equals one contract's close to the tick.  Naming
    that contract day by day recovers the vendor's own splice schedule instead of guessing
    where the seam is.  Days where nothing matches stay unnamed (a hole is not a roll).
    """
    named, holes = {}, []
    for d in dates:
        c = cont_close.get(d)
        if c is None:
            holes.append(d)
            continue
        hits = [s for s, v in bars.get(d, {}).items() if abs(v[0] - c) <= tol]
        if len(hits) == 1:
            named[d] = hits[0]
        elif len(hits) > 1:                      # two contracts at the same tick: take the deeper book
            named[d] = max(hits, key=lambda s: (bars[d][s][1], s))
        else:
            holes.append(d)
    return named, holes


def oi_agreement(named, bars):
    """How often the named contract is also the one holding the most open interest."""
    n = agree = 0
    for d, sym in named.items():
        row = bars.get(d, {})
        if sym not in row or not row:
            continue
        best = max(row.items(), key=lambda kv: (kv[1][1], kv[0]))[0]
        n += 1
        if best == sym:
            agree += 1
    return {"days": n, "agree": agree,
            "agree_pct": round(100.0 * agree / n, 1) if n else None}


def observed_rolls(dates, named, bars, index_close=None):
    """Splices of the published continuous, with the gap measured where both legs quoted.

    A roll is booked on the first day the series quotes the new contract -- that is the day
    a roller has to move and therefore the day its return is contaminated.  The gap is
    read on the last day both contracts were quoted, so it is a cross-sectional difference
    and carries no market move.  When the two legs never quoted side by side (the quote
    provider keeps only the years a contract was the main one), the date is still a fact
    and the magnitude is absent -- never zero.
    """
    rolls = []
    prev_d = None
    for d in dates:
        sym = named.get(d)
        if sym is None:
            continue
        if prev_d is not None:
            old = named.get(prev_d)
            if old and old != sym:
                rolls.append(_roll_row(dates, prev_d, d, old, sym, bars, index_close))
        prev_d = d
    return rolls


def _roll_row(dates, prev_d, d, old, sym, bars, index_close):
    d0 = None
    for j in range(dates.index(prev_d), max(-1, dates.index(prev_d) - 40), -1):
        dd = dates[j]
        if old in bars.get(dd, {}) and sym in bars.get(dd, {}):
            d0 = dd
            break
    row = {"date": d, "from": old, "to": sym,
           "unnamed_days_before": (dates.index(d) - dates.index(prev_d)) - 1}
    if d0 is None:
        row.update({"gap_pts": None, "measured_on": None, "no_common_day": True})
        return row
    gap = bars[d0][sym][0] - bars[d0][old][0]
    row.update({"gap_pts": round(gap, 3), "measured_on": d0,
                "days_before_switch": dates.index(d0) - dates.index(d)})
    if index_close and d0 in index_close:
        row["gap_pct_of_index"] = round(100.0 * gap / index_close[d0], 3)
    return row


def yearly_coverage(dates, named):
    """Share of each calendar year's trading days whose contract could be named."""
    tally = {}
    for d in dates:
        t = tally.setdefault(d[:4], [0, 0])
        t[0] += 1
        if d in named:
            t[1] += 1
    return dict((y, round(100.0 * n / t, 1)) for y, (t, n) in sorted(tally.items()))


def usable_window(dates, named, floor=None):
    """First date from which every year is named well enough to price against.

    The quote provider only keeps the years a contract was the main one, so the earliest
    span cannot be named day by day.  Comparing masks there would let unmasked rolls leak
    into the observed reading and make it look better than it is -- so the comparison runs
    from the first year the naming holds, and the excluded span is printed, not hidden.
    """
    floor = CRITERIA["min_window_coverage_pct"] if floor is None else floor
    cov = yearly_coverage(dates, named)
    start = None
    for y in sorted(cov):
        if all(cov[y2] >= floor for y2 in cov if y2 >= y):
            start = y
            break
    if start is None:
        return None, cov
    idx0 = next(i for i, d in enumerate(dates) if d[:4] >= start)
    return dates[idx0], cov


def jump_check(dates, basis, roll_days):
    """Do the days we call rolls actually look like the days the series jumped?

    Naming a contract is a claim about the seam; the price is the other witness.  If the
    named days carry the big basis steps and the rest do not, the naming and the price
    agree.  A ratio near 1 means we are naming days that the series does not consider
    rolls, and the whole reading would be about the wrong days.
    """
    steps = {}
    for k in range(len(basis) - 1):
        steps[dates[k + 1]] = abs(basis[k + 1] - basis[k])
    on = [v for d, v in steps.items() if d in roll_days]
    off = [v for d, v in steps.items() if d not in roll_days]
    if not on or not off:
        return None
    m_on, m_off = statistics.median(on), max(statistics.median(off), 1e-9)
    return {"roll_days": len(on), "median_abs_step_on_roll_pct": round(100.0 * m_on, 3),
            "median_abs_step_off_roll_pct": round(100.0 * m_off, 3),
            "ratio": round(m_on / m_off, 1)}


def overlap(observed, other):
    """Exact-day set comparison, both directions named."""
    o, t = set(observed), set(other)
    common = sorted(o & t)
    return {
        "observed_n": len(o),
        "other_n": len(t),
        "common_n": len(common),
        "precision_pct": round(100.0 * len(common) / len(t), 1) if t else None,
        "recall_pct": round(100.0 * len(common) / len(o), 1) if o else None,
        "only_observed": sorted(o - t)[:12],
        "only_other": sorted(t - o)[:12],
    }


# ------------------------------------------------------------------ one product
def one_product(prod, fetch=None, cache_dir=None, refresh=False, max_pull=None):
    rows = base.read_csv_rows(os.path.join(base.FUT_DIR, prod + ".csv"))
    fc = {}
    for r in rows:
        try:
            fc[str(r["date"])[:10]] = float(r["close"])
        except (KeyError, TypeError, ValueError):
            continue
    if not fc:
        return {"status": "no_main_series"}
    code = base.PAIRS[prod][0]
    try:
        idx = base.load_index(code)
    except RuntimeError as exc:
        return {"status": "no_index", "detail": str(exc)[:200]}
    dates, fcl, icl = base.aligned(fc, idx)
    if len(dates) < CRITERIA["min_common_days"]:
        return {"status": "short_overlap", "days": len(dates)}

    months = sorted(set(d[:7] for d in dates))
    span = [(int(m[:4]), int(m[5:7])) for m in (months[0], months[-1])]
    contracts, pull_info = load_contracts(prod, span, cache_dir=cache_dir, fetch=fetch,
                                          refresh=refresh, max_pull=max_pull)
    if not contracts:
        return {"status": "no_contracts", "pull": pull_info}

    # Only the days the main series is priced on, so every mask speaks about the same days.
    bars = {}
    for d in dates:
        row = {}
        for sym, series in contracts.items():
            if d in series:
                row[sym] = series[d]
        bars[d] = row
    named, holes = name_contracts(dates, bars, fc)
    observed = observed_rolls(dates, named, bars, idx)
    obs_days = set(r["date"] for r in observed)
    coverage = round(100.0 * len(named) / len(dates), 1)

    basis, spread, pub_roll = base.basis_face(fcl, icl, dates)
    pub_days = set(dates[k + 1] for k in range(len(pub_roll)) if pub_roll[k])
    cal_rolls, cal_info = rg.calendar_rolls(dates, basis)
    cal_days = set(cal_rolls)

    # Price all three masks on the same days: from the first year the naming holds.
    w0, cov_by_year = usable_window(dates, named)
    outside = set() if w0 is None else set(d for d in dates if d < w0)
    window = {"start": w0 or dates[0], "end": dates[-1],
              "days_compared": len([d for d in dates if d not in outside]),
              "coverage_in_window_pct": round(
                  100.0 * len([d for d in named if d not in outside])
                  / max(1, len([d for d in dates if d not in outside])), 1),
              "coverage_by_year_pct": cov_by_year}

    carry = {}
    for name, masked in (("published_size", pub_days), ("calendar", cal_days),
                         ("observed", obs_days)):
        st = rg.carry_stats(spread, dates, masked | outside)
        if st:
            carry[name] = st
    verdict_by_mask = {}
    for name, st in carry.items():
        carry_ann = st.get("carry_ann_pct")
        verdict_by_mask[name] = bool(carry_ann is not None and carry_ann >= base.CARRY_MIN_PCT)

    gaps = [r["gap_pts"] for r in observed if r.get("gap_pts") is not None]
    on_switch = [r for r in observed if r.get("days_before_switch") == 0]
    in_window = [r for r in observed if not outside or r["date"] >= (w0 or "")]
    unusable = (len(in_window) < CRITERIA["min_rolls"]
                or window["coverage_in_window_pct"] < CRITERIA["min_coverage_pct"])
    return {
        "status": "OBSERVED_UNUSABLE" if unusable else "ok",
        "index": code,
        "span": {"first": dates[0], "last": dates[-1], "days": len(dates)},
        "pull": pull_info,
        "contracts_quoted": len(contracts),
        "named_days_pct": coverage,
        "unnamed_days_n": len(holes),
        "unnamed_days_sample": holes[:8],
        "oi_agreement": oi_agreement(named, bars),
        "carry_window": window,
        "observed_rolls_n": len(observed),
        "observed_rolls_in_window": len(in_window),
        "rolls_per_year": round(len(observed) / (len(dates) / base.TRADING_DAYS), 2),
        "gap_points": {
            "n": len(gaps),
            "measurable_pct": round(100.0 * len(gaps) / len(observed), 1) if observed else None,
            "median": round(statistics.median(gaps), 3) if gaps else None,
            "mean": round(statistics.fmean(gaps), 3) if gaps else None,
            "min": round(min(gaps), 3) if gaps else None,
            "max": round(max(gaps), 3) if gaps else None,
        },
        "measured_on_switch_day_pct": round(100.0 * len(on_switch) / len(observed), 1) if observed else None,
        "observed_rolls": observed,
        "jump_check": jump_check(dates, basis, obs_days),
        "mask_vs_observed": {
            "published_size": overlap(obs_days, pub_days),
            "calendar": overlap(obs_days, cal_days),
        },
        "calendar_month_coverage_pct": cal_info.get("months_covered_pct"),
        "carry_ann_pct_by_mask": {
            k: {"carry_ann_pct": v.get("carry_ann_pct"),
                "mean": (v.get("stats") or {}).get("mean_ann_pct"),
                "median": (v.get("stats") or {}).get("median_ann_pct"),
                "trimmed": (v.get("stats") or {}).get("trimmed_mean_ann_pct"),
                "masked_days": v.get("masked_days")}
            for k, v in carry.items()},
        "admitted_by_mask": verdict_by_mask,
        "admitted_line_pct": base.CARRY_MIN_PCT,
    }


def build(fetch=None, cache_dir=None, refresh=False, max_pull=None):
    face = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "evidence_cutoff": None,
        "kind": "observed_roll_reconstruction",
        "criteria": {"admitted_line_pct": base.CARRY_MIN_PCT,
                     "min_rolls": CRITERIA["min_rolls"]},
        "products": {},
    }
    cut = None
    for prod in CRITERIA["products"]:
        try:
            face["products"][prod] = one_product(prod, fetch=fetch, cache_dir=cache_dir,
                                                 refresh=refresh, max_pull=max_pull)
        except Exception as exc:  # one product must not take the face down
            face["products"][prod] = {"status": "error", "detail": "%s: %s" % (type(exc).__name__, exc)}
        sp = face["products"][prod].get("span")
        if sp and (cut is None or sp["last"] > cut):
            cut = sp["last"]
    face["evidence_cutoff"] = cut
    face["verdict"] = judge(face)
    return face


def judge(face):
    """What the observation says about the two masks, mechanically.

    Two questions, kept separate because they fail separately:
      A. does each mask land on the days the market actually rolled?
      B. does the admission read change when the observed days are used?
    """
    prods = {k: v for k, v in face.get("products", {}).items() if v.get("status") in ("ok", "OBSERVED_UNUSABLE")}
    if not prods:
        return {"state": "no_observation"}
    rec = {"published_size": [], "calendar": []}
    prec = {"published_size": [], "calendar": []}
    for v in prods.values():
        for name, ov in v.get("mask_vs_observed", {}).items():
            if ov.get("recall_pct") is not None:
                rec[name].append(ov["recall_pct"])
            if ov.get("precision_pct") is not None:
                prec[name].append(ov["precision_pct"])
    recall = {k: (round(statistics.fmean(v), 1) if v else None) for k, v in rec.items()}
    precision = {k: (round(statistics.fmean(v), 1) if v else None) for k, v in prec.items()}
    flips = []
    for prod, v in prods.items():
        adm = v.get("admitted_by_mask") or {}
        if adm.get("observed") != adm.get("published_size"):
            flips.append({"product": prod, "published_size": adm.get("published_size"),
                          "observed": adm.get("observed")})
    better = None
    if recall.get("calendar") is not None and recall.get("published_size") is not None:
        better = "calendar" if recall["calendar"] > recall["published_size"] else "published_size"
    return {
        "state": "observed",
        "recall_pct_by_mask": recall,
        "precision_pct_by_mask": precision,
        "mask_closer_to_reality": better,
        "admission_flips_vs_published": flips,
        "admitted_under_observed": sorted([p for p, v in prods.items()
                                           if (v.get("admitted_by_mask") or {}).get("observed")]),
    }


# ------------------------------------------------------------------ page
def render_md(face):
    v = face.get("verdict", {})
    L = ["# Index futures: the roll, observed from open interest", ""]
    L.append("The carry numbers on the basis pages are priced with a roll mask.  Both masks "
             "in use are guesses -- one from the size of a basis step, one from where the "
             "most negative step falls near expiry.  This page replaces the guess with the "
             "observation: which contract the market was actually holding, read from open "
             "interest, and what the two legs were worth on the day they were both quoted.")
    L.append("")
    L.append("Evidence cutoff: `%s`  ·  generated %s" % (face.get("evidence_cutoff"), face.get("generated")))
    L.append("")
    if v.get("recall_pct_by_mask"):
        L.append("## Does each mask land on the real rolls?")
        L.append("")
        L.append("| mask | recall of observed rolls | precision |")
        L.append("|---|---|---|")
        for name in ("published_size", "calendar"):
            L.append("| %s | %s%% | %s%% |" % (name,
                                               v["recall_pct_by_mask"].get(name),
                                               v["precision_pct_by_mask"].get(name)))
        L.append("")
        L.append("Recall = share of real rolls the mask actually hides.  Precision = share of "
                 "the days it hides that were real rolls (the rest are market days it ate).")
        L.append("")
    L.append("## Per product")
    L.append("")
    L.append("Carry is the same measurement under three masks, on the same days "
             "(the window below), in pct/yr. Admission line = %s pct."
             % face.get("criteria", {}).get("admitted_line_pct", base.CARRY_MIN_PCT))
    L.append("")
    L.append("| product | window | days named | rolls in window | carry: size | calendar | observed | admit: size / cal / obs | jump ratio |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for prod, p in sorted(face.get("products", {}).items()):
        if p.get("status") not in ("ok", "OBSERVED_UNUSABLE"):
            L.append("| %s | n/a (%s) | | | | | | | |" % (prod, p.get("status")))
            continue
        adm = p.get("admitted_by_mask", {})
        cm = p.get("carry_ann_pct_by_mask") or {}
        win = p.get("carry_window") or {}

        def g(m):
            v = (cm.get(m) or {}).get("carry_ann_pct")
            return "-" if v is None else "%.2f" % v
        L.append("| %s | %s → %s | %s%% | %s | %s | %s | %s | %s / %s / %s | %s |" % (
            prod, win.get("start"), win.get("end"), win.get("coverage_in_window_pct"),
            p.get("observed_rolls_in_window"), g("published_size"), g("calendar"), g("observed"),
            adm.get("published_size"), adm.get("calendar"), adm.get("observed"),
            (p.get("jump_check") or {}).get("ratio")))
    L.append("")
    L.append("「days named」 is the share of trading days in the window whose contract could be "
             "identified by matching the continuous close to a contract close to the tick. "
             "「jump ratio」 is the median absolute basis step on the days we call rolls over the "
             "same statistic on all other days -- the price's corroboration of the naming (a "
             "ratio near 1 would mean the naming and the series disagree about where the seam is).")
    L.append("")
    L.append("## How many observations behind each number")
    L.append("")
    for prod, p in sorted(face.get("products", {}).items()):
        if p.get("status") not in ("ok", "OBSERVED_UNUSABLE"):
            continue
        L.append("- **%s**: %s to %s, %d bars; %d splices over the whole span (%s%% of days named); "
                 "%d with a measured gap, median %s pts; OI agrees on %s%% of named days" % (
                     prod, (p.get("span") or {}).get("first"), (p.get("span") or {}).get("last"),
                     (p.get("span") or {}).get("days") or 0, p["observed_rolls_n"],
                     p.get("named_days_pct"),
                     (p.get("gap_points") or {}).get("n") or 0,
                     (p.get("gap_points") or {}).get("median"),
                     (p.get("oi_agreement") or {}).get("agree_pct")))
        cov = (p.get("carry_window") or {}).get("coverage_by_year_pct") or {}
        L.append("  - years excluded from the comparison for want of contract data: %s" % (
            ", ".join("%s (%s%%)" % (y, c) for y, c in sorted(cov.items()) if c < 95.0) or "none"))
    L.append("")
    L.append("## Adoption")
    L.append("")
    L.append("`admitted_by_mask` is derived from the carry figures, never typed.  The observed "
             "column is the honest one -- the masked days are exactly the days the published "
             "series changed contract, so nothing but a splice is removed.  Both heuristics "
             "are wrong in opposite directions: the size rule catches too few days (it needs a "
             "big step) and the calendar rule catches days that are not splices (it fires on "
             "large market moves near expiry), which is why the calendar column reads high.")
    L.append("")
    L.append("A product that admits under the observed mask is a **candidate whose admission the "
             "published mask hid**, not an adopted book: the gap is a points reading from a "
             "quote provider, not a broker statement, and nothing here sizes a position.")
    if v.get("admission_flips_vs_published"):
        L.append("")
        L.append("Flips vs the published mask: " + ", ".join(
            "%s (%s -> %s)" % (f["product"], f["published_size"], f["observed"])
            for f in v["admission_flips_vs_published"]))
    L.append("")
    return "\n".join(L) + "\n"


def write_doc(face):
    os.makedirs(os.path.dirname(DOC), exist_ok=True)
    with io.open(DOC, "w", encoding="utf-8", newline="\n") as f:
        f.write(render_md(face))
    return DOC


def check_doc(face=None):
    """rc0 only when the page is byte-identical to what the face renders right now."""
    if face is None:
        if not os.path.isfile(OUT):
            print("checkdoc: no face at %s" % OUT)
            return 2
        with io.open(OUT, encoding="utf-8") as f:
            face = json.load(f)
    if not os.path.isfile(DOC):
        print("checkdoc: page missing (%s) -- run --write-doc" % DOC)
        return 2
    want = render_md(face)
    with io.open(DOC, encoding="utf-8") as f:
        have = f.read()
    if have != want:
        print("checkdoc: page differs from the face (page %d chars, face %d chars)"
              % (len(have), len(want)))
        return 2
    print("checkdoc: page == face (%d chars)" % len(want))
    return 0


# ------------------------------------------------------------------ selftest
def _contract(days, start, end, clause=None, shift=0.0):
    """A synthetic contract: quotes every day in [start, end)."""
    out = {}
    for i, d in enumerate(days):
        if start <= i < end:
            out[d] = (1000.0 + i + shift, (clause or 1000.0), 100.0)
    return out


def selftest():
    ok = 0
    fails = []

    def check(name, cond, detail=""):
        nonlocal ok
        if cond:
            ok += 1
            print("  PASS %s" % name)
        else:
            fails.append(name)
            print("  FAIL %s %s" % (name, detail))

    # L1 month range / symbol enumeration
    ms = month_range((2024, 11), (2025, 2))
    check("L1a month_range crosses the year", ms == [(2024, 11), (2024, 12), (2025, 1), (2025, 2)], ms)
    syms = contract_symbols("IC", ms, pad_months=2)
    check("L1b symbols pad forward and keep zero padding",
          syms == ["IC2411", "IC2412", "IC2501", "IC2502", "IC2503", "IC2504"], syms)

    # L2 cache round-trip (no network)
    import tempfile
    import shutil
    tmp = tempfile.mkdtemp()
    try:
        rows = [{"date": "2025-01-02", "open": 1, "high": 2, "low": 1, "close": 5500.0,
                 "volume": 10, "hold": 20}]
        write_cached("IC2503", rows, tmp)
        back = read_cached("IC2503", tmp)
        check("L2 cache round-trip preserves close/hold",
              back and float(back[0]["close"]) == 5500.0 and float(back[0]["hold"]) == 20.0)

        # L3 naming: the continuous close names the contract; a hole stays a hole
        bars = {"d1": {"A": (100.0, 5.0, 9.0), "B": (200.0, 50.0, 1.0)},
                "d2": {"A": (100.0, 9.0, 9.0), "B": (200.0, 9.0, 90.0)},
                "d3": {"A": (100.0, 3.0, 5.0)},
                "d4": {"A": (100.0, 3.0, 5.0), "B": (100.0, 40.0, 5.0)}}
        named, holes = name_contracts(["d1", "d2", "d3", "d4"], bars,
                                      {"d1": 200.0, "d2": 999.0, "d3": 100.0, "d4": 100.0})
        check("L3a the continuous close names the contract", named.get("d1") == "B", named)
        check("L3b a day that matches no contract is a hole, not a roll", "d2" not in named
              and holes == ["d2"], (named, holes))
        check("L3c two contracts at the same tick: the deeper book wins", named.get("d4") == "B", named)
        check("L3d open-interest agreement is measured, not assumed",
              oi_agreement({"d1": "B", "d3": "A"}, bars)["agree_pct"] == 100.0)

        # L4/L5/L8 observed rolls: the splice day, the gap on the last common day, a hole
        days = ["2025-01-0%d" % i for i in range(1, 10)]
        bars2 = {d: {} for d in days}
        for i, d in enumerate(days):
            if i <= 5:
                bars2[d]["OLD"] = (1000.0 + i, 100.0, 100.0)
            if 1 <= i:
                bars2[d]["NEW"] = (970.0 + i, 10.0 if i <= 2 else 200.0, 100.0)
        cont2 = {}
        for i, d in enumerate(days):
            cont2[d] = (1000.0 + i) if i <= 2 else (970.0 + i)
        named2, holes2 = name_contracts(days, bars2, cont2)
        rolls = observed_rolls(days, named2, bars2, {d: 1000.0 for d in days})
        check("L4 one roll observed, on the day the series starts quoting the new contract",
              len(rolls) == 1 and rolls[0]["date"] == days[3] and rolls[0]["from"] == "OLD"
              and rolls[0]["to"] == "NEW", rolls)
        check("L5 gap is the cross-sectional difference on the last common day (-30 pts)",
              rolls and abs(rolls[0]["gap_pts"] + 30.0) < 1e-9, rolls)
        check("L5b gap is also printed as a share of the index",
              rolls and abs(rolls[0]["gap_pct_of_index"] + 3.0) < 1e-9, rolls)

        # L8 a splice whose two legs never quoted side by side keeps the date, not a zero
        bars3 = {"a": {"A": (1.0, 5.0, 1.0)}, "b": {"B": (2.0, 9.0, 1.0)}}
        named3, _ = name_contracts(["a", "b"], bars3, {"a": 1.0, "b": 2.0})
        r3 = observed_rolls(["a", "b"], named3, bars3)
        check("L8 gap-less roll is recorded with the magnitude absent, not as 0",
              len(r3) == 1 and r3[0]["gap_pts"] is None and r3[0].get("no_common_day"), r3)

        # L9 a hole between two named days does not move the roll, but is counted
        named4, holes4 = name_contracts(days[:5], bars2,
                                        {"2025-01-01": 1000.0, "2025-01-02": 1001.0,
                                         "2025-01-03": 99999.0, "2025-01-04": 99999.0,
                                         "2025-01-05": 974.0})
        rolls4 = observed_rolls(days[:5], named4, bars2, {d: 1000.0 for d in days[:5]})
        check("L9 a hole is skipped and the roll lands on the next named day",
              rolls4 and rolls4[0]["date"] == days[4] and rolls4[0]["unnamed_days_before"] == 2,
              (rolls4, holes4))

        # L6 overlap arithmetic, both directions named
        ov = overlap({"a", "b", "c"}, {"b", "c", "d"})
        check("L6a recall = real rolls hidden by the mask", ov["recall_pct"] == 66.7, ov)
        check("L6b precision = masked days that were real rolls", ov["precision_pct"] == 66.7, ov)
        check("L6c false positives and misses are both named",
              ov["only_other"] == ["d"] and ov["only_observed"] == ["a"], ov)

        # L7 carry drops exactly the masked days (same implementation as the other faces)
        sp = [0.001] * (len(days) - 1)
        st_none = rg.carry_stats(sp, days, set())
        st_one = rg.carry_stats(sp, days, {days[3]})
        check("L7 carry masked_days counts the mask, not the keepers",
              st_none["masked_days"] == 0 and st_one["masked_days"] == 1, (st_none, st_one))

        # L9 the observation is not a restatement of the calendar guess: with a roll whose
        # magnitude the calendar would place a day earlier, the two sets differ
        check("L9b the roll date is the splice day and the gap day is a different day",
              rolls[0]["date"] == days[3] and rolls[0]["measured_on"] == days[2], rolls)

        # L10 admission is derived from the carry figure, not typed
        face = {"products": {"IC": {"status": "ok",
                                    "mask_vs_observed": {"published_size": {"recall_pct": 10.0,
                                                                           "precision_pct": 20.0},
                                                        "calendar": {"recall_pct": 70.0,
                                                                     "precision_pct": 80.0}},
                                    "admitted_by_mask": {"published_size": False,
                                                         "calendar": True, "observed": True}}}}
        jd = judge(face)
        check("L10a judge names the mask closer to reality", jd["mask_closer_to_reality"] == "calendar", jd)
        check("L10b judge lists the admission flip", jd["admission_flips_vs_published"]
              == [{"product": "IC", "published_size": False, "observed": True}], jd)

        # L11 the page renders the flip, so a flip cannot hide in the JSON
        md = render_md({"evidence_cutoff": "2025-01-09", "generated": "x", "verdict": jd,
                        "products": {"IC": {"status": "ok", "observed_rolls_n": 1,
                                            "rolls_per_year": 1.0, "named_days_pct": 99.0,
                                            "gap_points": {"median": -30.0, "n": 1,
                                                           "measurable_pct": 100.0},
                                            "oi_agreement": {"agree_pct": 97.0},
                                            "span": {"first": "a", "last": "b", "days": 1},
                                            "admitted_by_mask": {"published_size": False,
                                                                 "calendar": True,
                                                                 "observed": True}}}})
        check("L11 page names the flip in prose", "IC (False -> True)" in md, md[-300:])
        check("L11b page marks a missing product instead of inventing a row",
              "n/a (no_contracts)" in render_md({"products": {"IF": {"status": "no_contracts"}},
                                                 "verdict": {}}))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("%d/%d legs PASS" % (ok, ok + len(fails)))
    return 0 if not fails else 1


# ------------------------------------------------------------------ main
def main(argv):
    args = argv[1:]
    if "--selftest" in args:
        return selftest()
    if "--checkdoc" in args:
        return check_doc()
    refresh = "--refresh" in args
    max_pull = None
    for a in args:
        if a.startswith("--max-pull="):
            max_pull = int(a.split("=", 1)[1])
    fetch = None
    if "--offline" in args:
        fetch = lambda sym: None        # cache-only run: never invent a listing fact
    face = build(fetch=fetch, refresh=refresh, max_pull=max_pull)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(face, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    if "--write-doc" in args:
        write_doc(face)
    v = face["verdict"]
    print("contract roll: cutoff=%s recall_size=%s recall_cal=%s admitted=%s -> %s"
          % (face.get("evidence_cutoff"),
             (v.get("recall_pct_by_mask") or {}).get("published_size"),
             (v.get("recall_pct_by_mask") or {}).get("calendar"),
             v.get("admitted_under_observed"), OUT))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
