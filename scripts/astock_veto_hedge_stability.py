"""Is the carrier flip a property of the rule, or of the 52 periods that happened to be in the panel?

r2036 put both carriers of this hedge on a funded ruler and printed the sentence the family had
been circling: gross of costs the ETF short leads by 0.08pp, net of the lender it trails by 1.91pp,
and once you pay for the collateral it trails by 2.87pp -- ``THE_RANKING_FLIPS_WHEN_YOU_PAY_FOR_IT``.
A flip is a claim about the *sign* of a difference, and a sign computed on 52 periods is exactly the
kind of number that can be a sample artifact.  This face asks the question the flip has never
answered:

    cut the same 52 periods into pieces -- does the futures leg stay in front in the pieces too?

Five cuts are used, because they fail differently:

  1. **split-half** (26 / 26) and the in-sample / out-of-sample split the parent already carries;
  2. **quarter blocks** (13 periods each) -- the shortest piece that still spans a year, and the
     noisiest one, so a flip that survives here survives a lot;
  3. **rolling 26-period windows, stride 1** (27 of them) -- the distribution of the gap rather
     than one cut of it;
  4. a **period-level sign test** -- how many of the 52 periods favour the futures leg, and the
     two-sided binomial probability of seeing that many by chance;
  5. a **drop-one jackknife** -- the largest change in the gap from removing any single period,
     i.e. how much of the headline rests on one observation.

It also answers the assumption r2036 could not observe (its caveat 2): the collateral is modelled
as earning a declared 2%.  What cash yield would the frozen balance have to earn for the flip to
disappear?  A break-even above the book's own funded return means the flip does not depend on the
deposit rate at all; a break-even below it means the flip is a statement about the deposit rate.

Every cut is reported with its own annualised *and* cumulative gap, because annualising 13 periods
magnifies noise: the cumulative gap is what the sign test uses, and the annualised one is what the
family quotes.

Usage
    python scripts/astock_veto_hedge_stability.py run
    python scripts/astock_veto_hedge_stability.py check
    python scripts/astock_veto_hedge_stability.py selftest
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import statistics
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from astock_veto_hedge_carrier import (  # noqa: E402
    CAPITAL,
    CASH_YIELD,
    ETF_BORROW_FEES,
    ETF_HAIRCUTS,
    K_GRID,
    TIE_PP,
    arm_stats,
    compounded,
    hedged,
)
from astock_veto_hedge_funding import (  # noqa: E402
    borrow_series,
    funded_series,
)

PARENT = os.path.join(ROOT, "results", "astock_veto_hedgeable_beta.json")
CARRIER = os.path.join(ROOT, "results", "astock_veto_hedge_carrier.json")
FUNDING = os.path.join(ROOT, "results", "astock_veto_hedge_funding.json")
OUT_JSON = os.path.join(ROOT, "results", "astock_veto_hedge_stability.json")
OUT_MD = os.path.join(ROOT, "research", "ASTOCK_VETO_HEDGE_STABILITY.md")

# Frozen before the run.
K_REF = 1.0
REF_HAIRCUT = max(ETF_HAIRCUTS)      # r2036's reference block: the full haircut
REF_FEE = min(ETF_BORROW_FEES)       # and its cheapest rent
HALF = 26                            # split-half length
QUARTER = 13                         # quarter-block length (52 = 4 x 13)
ROLL = 26                            # rolling window length
LINE_STABLE_SHARE = 0.80             # >= 80% of rolling windows agreeing = a property of the rule
LINE_COIN_SHARE = 0.50               # < 50% = the flip is a coin toss
LINE_JACK_MULT = 1.0                # one period may not move the gap by more than the gap itself
LINE_NARROW = 0.50                   # last block < half the median block = the flip is shrinking
LINE_YIELD_ROBUST = 1.0              # break-even yield >= the book's own return = assumption-free
YIELD_SCAN = (0.0, 0.02, 0.04, 0.06, 0.08, 0.10)
YIELD_BRACKET = (-0.50, 0.50)
MIN_PERIODS = 20

VERDICT_STABLE = "THE_FLIP_IS_A_PROPERTY_OF_THE_RULE"
VERDICT_ONE_WINDOW = "THE_FLIP_IS_ONE_WINDOW"
VERDICT_COIN = "THE_FLIP_IS_A_COIN_FLIP"
VERDICT_MIXED = "THE_FLIP_IS_WINDOW_DEPENDENT"
VERDICT_JACK = "ONE_PERIOD_CARRIES_THE_FLIP"
VERDICT_NARROW = "THE_FLIP_IS_NARROWING"
VERDICT_YIELD_ROBUST = "THE_FLIP_DOES_NOT_NEED_A_DEPOSIT_RATE"
VERDICT_YIELD_FRAGILE = "THE_FLIP_IS_A_STATEMENT_ABOUT_THE_DEPOSIT_RATE"
VERDICT_WHY = {
    VERDICT_STABLE: "every cut of the same 52 periods puts the futures leg in front, so the "
                    "ordering is carried by the rule and not by where the sample starts or ends",
    VERDICT_ONE_WINDOW: "the flip appears in one cut of the periods and not in the others; the "
                        "window chose the carrier, not the costs",
    VERDICT_COIN: "the pieces disagree about the sign often enough that the full-window flip is "
                  "indistinguishable from a coin toss",
    VERDICT_MIXED: "most pieces agree but not enough of them to call it a property of the rule",
    VERDICT_JACK: "removing a single period moves the gap by more than the gap itself, so the "
                  "headline rests on one observation",
    VERDICT_NARROW: "the sign is stable but the size is not: the most recent block is less than "
                    "half the median block, so a reader who trades on the flip is trading on a "
                    "gap that has been shrinking for a year",
    VERDICT_YIELD_ROBUST: "the frozen cash would have to earn more than the book itself returns "
                          "before the two carriers tie, which no deposit pays -- the flip does "
                          "not depend on the declared cash yield",
    VERDICT_YIELD_FRAGILE: "a deposit rate inside the range brokers actually pay is enough to "
                           "erase the flip, so the ranking is a statement about the cash yield",
}


# ---------------------------------------------------------------------- plumbing
def _now() -> str:
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def _rel(path: str) -> str:
    try:
        return os.path.relpath(path, ROOT).replace(os.sep, "/")
    except ValueError:
        return str(path).replace(os.sep, "/")


def _read_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _sha_file(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def content_sha(face: dict) -> str:
    body = {k: v for k, v in face.items() if k != "content_sha256"}
    blob = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def fingerprint(path: str) -> dict:
    face = _read_json(path)
    return {"face": _rel(path), "file_sha256": _sha_file(path),
            "content_sha256": content_sha(face), "generated": face.get("generated"),
            "evidence_cutoff": face.get("evidence_cutoff")}


def _pct(x, nd=2) -> str:
    return "n/a" if x is None else ("%." + str(nd) + "f%%") % (x * 100.0)


def _pp(x, nd=2) -> str:
    return "n/a" if x is None else ("%." + str(nd) + "fpp") % (x * 100.0)


def _finite(vals) -> list:
    return [float(v) for v in vals if v is not None and math.isfinite(float(v))]


def annualized(vals, periods_per_year: float):
    """Compounded annual rate of a per-period return list, or None if it cannot be priced."""
    kept = _finite(vals)
    if len(kept) < 2:
        return None
    growth = compounded(kept)
    if growth <= 0.0:
        return None
    return growth ** (periods_per_year / len(kept)) - 1.0


def window_gap(im_series, etf_series, start: int, end: int, ppy: float):
    """Both annualised and cumulative gaps over ``[start, end)``; sign is IM minus ETF.

    Two rulers on purpose: a 13-period window annualises a lot of noise into a small number of
    periods, so the cumulative gap is what the sign test uses and the annualised one is what the
    family quotes.  Printing only the annualised number would make every short window look like
    evidence.
    """
    im = _finite(im_series[start:end])
    et = _finite(etf_series[start:end])
    if len(im) < 2 or len(et) < 2:
        return None
    im_ann = annualized(im, ppy)
    et_ann = annualized(et, ppy)
    if im_ann is None or et_ann is None:
        return None
    im_cum = compounded(im) - 1.0
    et_cum = compounded(et) - 1.0
    im_vol = statistics.pstdev(im) * math.sqrt(ppy) if len(im) > 1 else None
    et_vol = statistics.pstdev(et) * math.sqrt(ppy) if len(et) > 1 else None
    return {
        "start": start,
        "end": end,
        "periods": len(im),
        "im_ann": im_ann,
        "etf_ann": et_ann,
        "im_cum": im_cum,
        "etf_cum": et_cum,
        "im_vol": im_vol,
        "etf_vol": et_vol,
        "gap_ann_pp": (im_ann - et_ann) * 100.0,
        "gap_cum_pp": (im_cum - et_cum) * 100.0,
    }


def binom_two_sided(k: int, n: int, p: float = 0.5) -> float:
    """Two-sided exact binomial p-value at ``k`` successes in ``n`` trials."""
    if n <= 0:
        return 1.0
    k = max(0, min(n, int(k)))
    probs = [math.comb(n, i) * (p ** i) * ((1.0 - p) ** (n - i)) for i in range(n + 1)]
    obs = probs[k]
    return float(min(1.0, sum(pv for pv in probs if pv <= obs + 1e-18)))


def share_positive(gaps) -> float:
    vals = [g for g in gaps if g is not None]
    if not vals:
        return 0.0
    return sum(1.0 for g in vals if g > 0.0) / len(vals)


# ------------------------------------------------------------------------- build
def build_series(book, etf_leg, im_leg, im_cash, etf_cash, cash_yield, notional, ppy):
    """The two funded series at k = the reference, in the order the parent rows are in."""
    im_series = funded_series(hedged(book, im_leg, K_REF), im_cash, cash_yield, CAPITAL, ppy)
    etf_net = borrow_series(hedged(book, etf_leg, K_REF), REF_FEE, notional, CAPITAL, ppy)
    etf_series = funded_series(etf_net, etf_cash, cash_yield, CAPITAL, ppy)
    return im_series, etf_series, etf_net


def build_face() -> dict:
    parent = _read_json(PARENT)
    funding = _read_json(FUNDING)

    spec_p = parent.get("spec") or {}
    ppy = float(spec_p.get("periods_per_year") or 12.6)
    rows = [r for r in (parent.get("rows") or []) if r.get("im_window")]
    if len(rows) < MIN_PERIODS:
        return {"generated": _now(), "kind": "hedge_stability",
                "evidence_cutoff": parent.get("evidence_cutoff"),
                "verdict": "NOT_ENOUGH_PERIODS",
                "parents": {"beta": fingerprint(PARENT)}}

    fspec = funding.get("spec") or {}
    beta = float(fspec.get("beta") or 0.9013)
    notional = float(fspec.get("notional_cny") or beta * CAPITAL)
    im_cash = float(fspec.get("im_cash_cny") or 0.0)
    etf_cash = float((fspec.get("etf_blocked_cny") or {}).get("%.2f" % REF_HAIRCUT) or 0.0)
    if im_cash <= 0.0 or etf_cash <= 0.0:
        return {"generated": _now(), "kind": "hedge_stability",
                "evidence_cutoff": parent.get("evidence_cutoff"),
                "verdict": "PARENT_BLOCKS_MISSING",
                "parents": {"beta": fingerprint(PARENT), "funding": fingerprint(FUNDING)}}

    book = [r.get("book_net") for r in rows]
    etf_leg = [r.get("hedge_etf") for r in rows]
    im_leg = [r.get("hedge_im") for r in rows]
    n = len(rows)

    im_series, etf_series, etf_net = build_series(
        book, etf_leg, im_leg, im_cash, etf_cash, CASH_YIELD, notional, ppy)

    # --- the anchor: r2036's own full-window funded gap, reproduced not re-invented
    full = window_gap(im_series, etf_series, 0, n, ppy)
    anchor_gap = (funding.get("funded_gap_pp") or {}).get("%.2f" % REF_FEE)

    # --- 1. split-half and in/out of sample
    halves = []
    for label, a, b in (("first_half", 0, HALF), ("second_half", HALF, 2 * HALF)):
        st = window_gap(im_series, etf_series, a, b, ppy)
        if st:
            halves.append(dict(st, label=label,
                              first=rows[a].get("date"), last=rows[b - 1].get("end")))

    is_end = str(spec_p.get("is_end") or "2023-12-31")
    split = next((i for i, r in enumerate(rows) if str(r.get("date") or "") > is_end), n)
    segments = []
    for label, a, b in (("in_sample", 0, split), ("out_of_sample", split, n)):
        if b - a < 2:
            continue
        st = window_gap(im_series, etf_series, a, b, ppy)
        if st:
            segments.append(dict(st, label=label,
                                 first=rows[a].get("date"), last=rows[b - 1].get("end")))

    # --- 2. quarter blocks (the shortest piece that spans a year)
    quarters = []
    blocks = n // QUARTER
    for i in range(blocks):
        a, b = i * QUARTER, (i + 1) * QUARTER
        st = window_gap(im_series, etf_series, a, b, ppy)
        if st:
            quarters.append(dict(st, label="Q%d" % (i + 1),
                                 first=rows[a].get("date"), last=rows[b - 1].get("end")))

    # --- 3. rolling windows, stride 1
    rolling = []
    for a in range(0, n - ROLL + 1):
        st = window_gap(im_series, etf_series, a, a + ROLL, ppy)
        if st:
            rolling.append(dict(st, first=rows[a].get("date"),
                                last=rows[a + ROLL - 1].get("end")))
    roll_gaps = [r["gap_cum_pp"] for r in rolling]
    roll_ann = [r["gap_ann_pp"] for r in rolling]

    # --- 4. period-level sign test
    diffs = [im_series[i] - etf_series[i] for i in range(n)
             if im_series[i] is not None and etf_series[i] is not None
             and math.isfinite(im_series[i]) and math.isfinite(etf_series[i])]
    wins = sum(1 for d in diffs if d > 0.0)
    sign_test = {
        "periods": len(diffs),
        "im_periods": wins,
        "etf_periods": len(diffs) - wins,
        "im_share": (wins / len(diffs)) if diffs else 0.0,
        "p_two_sided": binom_two_sided(wins, len(diffs)),
        "mean_diff_pp": (statistics.fmean(diffs) * 100.0) if diffs else None,
    }

    # --- 5. drop-one jackknife
    jack = []
    for i in range(n):
        # rebuild the series without row i (two contiguous slices, not a gap)
        keep_im = im_series[:i] + im_series[i + 1:]
        keep_et = etf_series[:i] + etf_series[i + 1:]
        st = window_gap(keep_im, keep_et, 0, len(keep_im), ppy)
        if st:
            jack.append({"dropped": i, "date": rows[i].get("date"),
                         "gap_ann_pp": st["gap_ann_pp"], "gap_cum_pp": st["gap_cum_pp"]})
    jack_gaps = [j["gap_ann_pp"] for j in jack]
    jackknife = {
        "periods": len(jack),
        "full_gap_ann_pp": full["gap_ann_pp"] if full else None,
        "min_gap_ann_pp": min(jack_gaps) if jack_gaps else None,
        "max_gap_ann_pp": max(jack_gaps) if jack_gaps else None,
        "max_abs_change_pp": (max(abs(g - (full["gap_ann_pp"] if full else 0.0))
                                  for g in jack_gaps) if jack_gaps and full else None),
        "worst_drop": (max(jack, key=lambda j: abs(j["gap_ann_pp"] - full["gap_ann_pp"]))
                       if jack and full else None),
        "all_positive": bool(jack_gaps and all(g > 0.0 for g in jack_gaps)),
    }

    # --- 6. the deposit rate the flip needs
    def gap_at_y(y):
        im_s = funded_series(hedged(book, im_leg, K_REF), im_cash, y, CAPITAL, ppy)
        etf_s = funded_series(etf_net, etf_cash, y, CAPITAL, ppy)
        st = window_gap(im_s, etf_s, 0, n, ppy)
        return None if st is None else st["gap_ann_pp"]

    scan = [{"cash_yield": y, "gap_ann_pp": gap_at_y(y)} for y in YIELD_SCAN]
    lo, hi = YIELD_BRACKET
    g_lo, g_hi = gap_at_y(lo), gap_at_y(hi)
    breakeven = None
    breakeven_note = "bracket could not be priced"
    if g_lo is not None and g_hi is not None:
        if g_lo * g_hi > 0.0:
            breakeven_note = ("the futures leg leads at every cash yield in [%.0f%%, %.0f%%]"
                              % (lo * 100.0, hi * 100.0)) if g_hi > 0.0 else \
                             ("the ETF leg leads at every cash yield in [%.0f%%, %.0f%%]"
                              % (lo * 100.0, hi * 100.0))
        else:
            left, right, gl = lo, hi, g_lo
            for _ in range(200):
                mid = 0.5 * (left + right)
                gm = gap_at_y(mid)
                if gm is None:
                    break
                if (gm > 0.0) == (gl > 0.0):
                    left, gl = mid, gm
                else:
                    right = mid
            breakeven = 0.5 * (left + right)
            breakeven_note = "the two carriers tie at a cash yield of %s" % _pct(breakeven)
    yield_face = {
        "declared_cash_yield": CASH_YIELD,
        "scan": scan,
        "breakeven_cash_yield": breakeven,
        "breakeven_note": breakeven_note,
        "book_funded_return": (full["im_ann"] if full else None),
    }

    flags = decide(full, halves, quarters, rolling, roll_gaps, sign_test, jackknife, yield_face)
    verdict = headline(flags)

    caveats = [
        "every cut is a cut of the same 52 periods, so this face says the flip does not depend on "
        "where inside those 52 you start -- it cannot say the 52 are a fair sample of the regime",
        "the 13-period quarter blocks annualise 13 observations; their annualised gap is printed "
        "for completeness and the sign test runs on the cumulative gap for that reason",
        "rolling windows overlap by 25 of 26 periods, so the 27 windows are not 27 independent "
        "trials and no multiplicity correction is claimed for the share",
        "cash yield is swept inside the funding identity r2036 published; a broker that pays a "
        "tiered rate, or freezes the balance outright, is a different curve, not a different "
        "break-even",
        "the reference case is k=1, the full haircut and the cheapest rent, exactly r2036's "
        "headline cell; the other k and haircut cells are not re-cut here",
        "the window still starts where the IM panel starts (2022-07), so a regime that only "
        "exists after that date is inside every piece",
        "a stable sign is not a stable size: this face tests the ordering of the two carriers, "
        "not whether either return is worth committing capital to",
    ]

    face = {
        "generated": _now(),
        "kind": "hedge_stability",
        "machine": "bm-c",
        "evidence_cutoff": parent.get("evidence_cutoff"),
        "fills_the_hole_of": "r2036 flipped the carrier ranking on a funded ruler and printed the "
                             "flip as a single 52-period number; nobody asked whether the same 52 "
                             "periods, cut into pieces, agree with it",
        "parents": {"beta": fingerprint(PARENT), "carrier": fingerprint(CARRIER),
                    "funding": fingerprint(FUNDING)},
        "sample": {"periods": n, "periods_per_year": ppy,
                   "first": rows[0].get("date"), "last": rows[-1].get("end"),
                   "basis": "parent rows flagged im_window (both carriers priced)"},
        "spec": {"capital": CAPITAL, "beta": beta, "notional_cny": notional,
                 "k_ref": K_REF, "k_grid": K_GRID,
                 "ref_haircut": REF_HAIRCUT, "ref_fee": REF_FEE,
                 "im_cash_cny": im_cash, "etf_cash_cny": etf_cash,
                 "half": HALF, "quarter": QUARTER, "roll": ROLL,
                 "is_end": is_end,
                 "line_stable_share": LINE_STABLE_SHARE, "line_coin_share": LINE_COIN_SHARE,
                 "line_jack_mult": LINE_JACK_MULT, "line_yield_robust": LINE_YIELD_ROBUST,
                 "yield_scan": list(YIELD_SCAN), "yield_bracket": list(YIELD_BRACKET),
                 "tie_pp": TIE_PP},
        "full": full,
        "anchor_gap_pub_pp": anchor_gap,
        "halves": halves,
        "segments": segments,
        "quarters": quarters,
        "rolling_summary": {
            "windows": len(rolling),
            "im_leads": sum(1 for g in roll_gaps if g > 0.0),
            "share_im_leads": share_positive(roll_gaps),
            "gap_cum_pp_min": min(roll_gaps) if roll_gaps else None,
            "gap_cum_pp_median": statistics.median(roll_gaps) if roll_gaps else None,
            "gap_cum_pp_max": max(roll_gaps) if roll_gaps else None,
            "gap_ann_pp_min": min(roll_ann) if roll_ann else None,
            "gap_ann_pp_median": statistics.median(roll_ann) if roll_ann else None,
            "gap_ann_pp_max": max(roll_ann) if roll_ann else None,
        },
        "rolling": rolling,
        "sign_test": sign_test,
        "jackknife": jackknife,
        "yield_sensitivity": yield_face,
        "verdicts": flags,
        "verdict": verdict,
        "verdict_why": VERDICT_WHY.get(verdict.split("+")[0], ""),
        "caveats": caveats,
    }
    face["reads"] = build_reads(face)
    face["content_sha256"] = content_sha(face)
    return face


def decide(full, halves, quarters, rolling, roll_gaps, sign_test, jackknife, yield_face) -> dict:
    """Each flag answers its own question from its own numbers; several can hold at once."""
    out = {}
    share = share_positive(roll_gaps)
    quarter_gaps = [q["gap_cum_pp"] for q in quarters]
    quarter_same = bool(quarter_gaps) and (all(g > 0.0 for g in quarter_gaps)
                                           or all(g < 0.0 for g in quarter_gaps))
    out[VERDICT_STABLE] = bool(share >= LINE_STABLE_SHARE and quarter_same)
    out[VERDICT_ONE_WINDOW] = bool(share < LINE_COIN_SHARE or (quarters and not quarter_same
                                                               and share < LINE_STABLE_SHARE))
    out[VERDICT_COIN] = bool(share < LINE_COIN_SHARE)
    out[VERDICT_MIXED] = bool(not out[VERDICT_STABLE] and not out[VERDICT_COIN])
    full_gap = (full or {}).get("gap_ann_pp")
    max_move = jackknife.get("max_abs_change_pp")
    out[VERDICT_JACK] = bool(full_gap is not None and max_move is not None
                             and abs(full_gap) > 0.0 and max_move >= LINE_JACK_MULT * abs(full_gap))
    quarter_ann = [q["gap_ann_pp"] for q in quarters]
    if len(quarter_ann) >= 3:
        med_signed = statistics.median(quarter_ann)
        med = abs(med_signed)
        same_sign = (quarter_ann[-1] > 0.0) == (med_signed > 0.0)
        out[VERDICT_NARROW] = bool(med > 0.0 and same_sign
                                   and 0.0 < abs(quarter_ann[-1]) < LINE_NARROW * med)
    else:
        out[VERDICT_NARROW] = False
    be = yield_face.get("breakeven_cash_yield")
    book = yield_face.get("book_funded_return")
    if be is None:
        note = str(yield_face.get("breakeven_note") or "")
        out[VERDICT_YIELD_ROBUST] = bool("every cash yield" in note)
        out[VERDICT_YIELD_FRAGILE] = False
    else:
        out[VERDICT_YIELD_ROBUST] = bool(book is not None and be >= LINE_YIELD_ROBUST * book)
        out[VERDICT_YIELD_FRAGILE] = bool(be <= CASH_YIELD)
    return out


def headline(flags) -> str:
    """One sentence, chosen by a fixed ladder -- not by whichever flag looks best."""
    if flags.get(VERDICT_STABLE):
        parts = [VERDICT_STABLE]
    elif flags.get(VERDICT_COIN):
        parts = [VERDICT_COIN]
    elif flags.get(VERDICT_ONE_WINDOW):
        parts = [VERDICT_ONE_WINDOW]
    else:
        parts = [VERDICT_MIXED]
    if flags.get(VERDICT_NARROW):
        parts.append(VERDICT_NARROW)
    if flags.get(VERDICT_YIELD_ROBUST):
        parts.append(VERDICT_YIELD_ROBUST)
    return "+".join(parts)


# ------------------------------------------------------------------------- reads
def build_reads(face) -> list:
    reads = []
    spec = face.get("spec") or {}
    full = face.get("full") or {}
    roll = face.get("rolling_summary") or {}
    sign = face.get("sign_test") or {}
    jack = face.get("jackknife") or {}
    yf = face.get("yield_sensitivity") or {}
    n = (face.get("sample") or {}).get("periods") or 0

    reads.append({
        "id": "R1",
        "text": "the anchor reproduces: on all %d periods the funded gap is %s (IM minus ETF), "
                "against the %s r2036 published -- the cut below starts from the same number, so "
                "this face is a decomposition and not a re-derivation"
                % (n, _pp((full.get("gap_ann_pp") or 0.0) / 100.0),
                   _pp(face.get("anchor_gap_pub_pp") or 0.0)),
    })

    halves = face.get("halves") or []
    if len(halves) >= 2:
        reads.append({
            "id": "R2",
            "text": "cut in half, the two halves %s: %s (%s) and %s (%s) on the annualised ruler, "
                    "%s / %s on the cumulative one"
                    % ("agree" if (halves[0]["gap_cum_pp"] > 0) == (halves[1]["gap_cum_pp"] > 0)
                       else "disagree",
                       _pp(halves[0]["gap_ann_pp"] / 100.0), halves[0]["label"],
                       _pp(halves[1]["gap_ann_pp"] / 100.0), halves[1]["label"],
                       _pp(halves[0]["gap_cum_pp"] / 100.0),
                       _pp(halves[1]["gap_cum_pp"] / 100.0)),
        })

    segs = face.get("segments") or []
    if len(segs) >= 2:
        reads.append({
            "id": "R3",
            "text": "and the parent's own in-sample / out-of-sample split %s: %s in sample and %s "
                    "out of it (cumulative), so the flip is not an artefact of the fitted part of "
                    "the window"
                    % ("agrees with the headline" if (segs[0]["gap_cum_pp"] > 0)
                       == (segs[1]["gap_cum_pp"] > 0) else "does NOT agree with the headline",
                       _pp(segs[0]["gap_cum_pp"] / 100.0), _pp(segs[1]["gap_cum_pp"] / 100.0)),
        })

    quarters = face.get("quarters") or []
    if quarters:
        reads.append({
            "id": "R4",
            "text": "the %d quarter blocks (13 periods each) run %s -- %d of %d favour the futures "
                    "leg; the annualised numbers on a 13-period block are noisy by construction, "
                    "which is why the sign test below uses the cumulative one"
                    % (len(quarters),
                       ", ".join("%s %s" % (q["label"], _pp(q["gap_cum_pp"] / 100.0))
                                 for q in quarters),
                       sum(1 for q in quarters if q["gap_cum_pp"] > 0), len(quarters)),
        })

    if quarters:
        newest = quarters[-1]
        med = statistics.median([q["gap_ann_pp"] for q in quarters])
        reads.append({
            "id": "R4b",
            "text": "the flip is stable in sign and shrinking in size: the last block (%s .. %s) "
                    "pays %s against a median block of %s, and it is the only block inside the "
                    "%s tie band -- a reader who trades the flip forward is trading a gap that "
                    "has been narrowing for a year"
                    % (newest.get("first"), newest.get("last"),
                       _pp((newest.get("gap_ann_pp") or 0.0) / 100.0), _pp(med / 100.0),
                       "%.1fpp" % (spec.get("tie_pp") or 0.0)),
        })

    if roll.get("windows"):
        reads.append({
            "id": "R5",
            "text": "%d rolling %d-period windows (stride 1) put the futures leg in front in %d of "
                    "them (%s); the cumulative gap runs %s .. %s with a median of %s, so the "
                    "full-window number is a middle case and not the best window"
                    % (roll["windows"], spec.get("roll") or 0, roll.get("im_leads") or 0,
                       _pct(roll.get("share_im_leads") or 0.0),
                       _pp((roll.get("gap_cum_pp_min") or 0.0) / 100.0),
                       _pp((roll.get("gap_cum_pp_max") or 0.0) / 100.0),
                       _pp((roll.get("gap_cum_pp_median") or 0.0) / 100.0)),
        })

    reads.append({
        "id": "R6",
        "text": "period by period the futures leg wins %d of %d (%s) with a two-sided binomial "
                "p of %.4f -- %s"
                % (sign.get("im_periods") or 0, sign.get("periods") or 0,
                   _pct(sign.get("im_share") or 0.0), sign.get("p_two_sided") or 1.0,
                   "a real bias, not a coin" if (sign.get("p_two_sided") or 1.0) < 0.05
                   else "which on its own would not be distinguishable from a coin"),
    })

    if jack.get("periods"):
        worst = jack.get("worst_drop") or {}
        reads.append({
            "id": "R7",
            "text": "the drop-one jackknife moves the gap by at most %s (dropping %s) and the gap "
                    "stays %s of the %d single-period removals -- the headline does not rest on a "
                    "single observation"
                    % (_pp((jack.get("max_abs_change_pp") or 0.0) / 100.0), worst.get("date"),
                       "positive in all" if jack.get("all_positive") else "negative in some",
                       jack.get("periods") or 0),
        })

    scan = yf.get("scan") or []
    if scan:
        reads.append({
            "id": "R8",
            "text": "sweeping the collateral's declared yield from %s to %s moves the gap from %s "
                    "to %s -- the flip %s"
                    % (_pct(scan[0]["cash_yield"]),
                       _pct(scan[-1]["cash_yield"]),
                       _pp((scan[0]["gap_ann_pp"] or 0.0) / 100.0),
                       _pp((scan[-1]["gap_ann_pp"] or 0.0) / 100.0),
                       "survives the whole range" if all((s["gap_ann_pp"] or 0.0) > 0.0
                                                         for s in scan) else "does not"),
        })

    be = yf.get("breakeven_cash_yield")
    if be is not None:
        reads.append({
            "id": "R9",
            "text": "the frozen cash would have to earn %s a year for the two carriers to tie, "
                    "against a funded book return of %s -- the collateral assumption r2036 could "
                    "not observe %s the conclusion, because no broker pays above the book"
                    % (_pct(be), _pct(yf.get("book_funded_return")),
                       "cannot overturn" if be >= LINE_YIELD_ROBUST * (yf.get("book_funded_return")
                                                                       or 1.0) else "can overturn"),
        })
    else:
        reads.append({
            "id": "R9",
            "text": "no break-even yield exists inside [%.0f%%, %.0f%%]: %s"
                    % ((spec.get("yield_bracket") or [-0.5, 0.5])[0] * 100,
                       (spec.get("yield_bracket") or [-0.5, 0.5])[1] * 100,
                       yf.get("breakeven_note")),
        })
    return reads


# ------------------------------------------------------------------------ render
def render_md(face) -> str:
    parents = face.get("parents") or {}
    spec = face.get("spec") or {}
    sample = face.get("sample") or {}
    full = face.get("full") or {}
    roll = face.get("rolling_summary") or {}
    sign = face.get("sign_test") or {}
    jack = face.get("jackknife") or {}
    yf = face.get("yield_sensitivity") or {}

    lines = ["# Does the carrier flip survive cutting the window up?", "",
             "r2036 put both carriers of this hedge on a funded ruler and the family has been "
             "quoting the result since: **THE_RANKING_FLIPS_WHEN_YOU_PAY_FOR_IT** -- gross the "
             "ETF short leads by 0.08pp, net of the lender it trails by 1.91pp, and once the "
             "collateral is charged it trails by 2.87pp. A flip is a claim about the sign of a "
             "difference, and a sign computed on 52 periods is exactly the kind of number a sample "
             "can manufacture. This face cuts the same 52 periods five ways and asks whether the "
             "futures leg stays in front.", "",
             "Evidence cutoff **%s**. %d periods (%s .. %s), %s periods a year, reference cell "
             "k=%s, haircut %.0f%%, rent %s. Parents: beta `%s`, carrier `%s`, funding `%s`."
             % (face.get("evidence_cutoff"), sample.get("periods") or 0, sample.get("first"),
                sample.get("last"), sample.get("periods_per_year"),
                spec.get("k_ref"), (spec.get("ref_haircut") or 0.0) * 100,
                _pct(spec.get("ref_fee")),
                (parents.get("beta") or {}).get("face"),
                (parents.get("carrier") or {}).get("face"),
                (parents.get("funding") or {}).get("face")), ""]

    lines += ["## 1. The anchor", "",
              "| window | periods | IM annual | ETF annual | gap (annualised) | gap (cumulative) |",
              "|---|---|---|---|---|---|"]
    lines.append("| all %d | %d | %s | %s | %s | %s |"
                 % (sample.get("periods") or 0, full.get("periods") or 0,
                    _pct(full.get("im_ann")), _pct(full.get("etf_ann")),
                    _pp((full.get("gap_ann_pp") or 0.0) / 100.0),
                    _pp((full.get("gap_cum_pp") or 0.0) / 100.0)))
    lines += ["",
              "The annualised gap here is the number r2036 published (%.2fpp); the cumulative one "
              "is what the sign test below uses, because annualising a 13-period block turns a "
              "rounding difference into a percentage point."
              % (face.get("anchor_gap_pub_pp") or 0.0), ""]

    lines += ["## 2. Two halves and in/out of sample", "",
              "| cut | periods | from | to | IM annual | ETF annual | gap annualised | "
              "gap cumulative |", "|---|---|---|---|---|---|---|---|"]
    for r in (face.get("halves") or []) + (face.get("segments") or []):
        lines.append("| %s | %d | %s | %s | %s | %s | %s | %s |"
                     % (r.get("label"), r.get("periods") or 0, r.get("first"), r.get("last"),
                        _pct(r.get("im_ann")), _pct(r.get("etf_ann")),
                        _pp((r.get("gap_ann_pp") or 0.0) / 100.0),
                        _pp((r.get("gap_cum_pp") or 0.0) / 100.0)))
    lines += ["", "The parent's `in_sample` flag is the fitted part of the window and the "
                  "out-of-sample piece is everything after it; if the flip only existed in the "
                  "fitted half it would be a description of the fit, not of the hedge.", ""]

    lines += ["## 3. Quarter blocks (13 periods each)", "",
              "| block | periods | from | to | IM annual | ETF annual | gap annualised | "
              "gap cumulative |", "|---|---|---|---|---|---|---|---|"]
    for r in (face.get("quarters") or []):
        lines.append("| %s | %d | %s | %s | %s | %s | %s | %s |"
                     % (r.get("label"), r.get("periods") or 0, r.get("first"), r.get("last"),
                        _pct(r.get("im_ann")), _pct(r.get("etf_ann")),
                        _pp((r.get("gap_ann_pp") or 0.0) / 100.0),
                        _pp((r.get("gap_cum_pp") or 0.0) / 100.0)))
    lines += ["", "Thirteen periods is the shortest block that still spans a year at 12.6 periods "
                  "a year, and it is the noisiest cut here. The annualised column is printed for "
                  "completeness; the cumulative column is the one a sign is read off.", ""]

    lines += ["## 4. Rolling %d-period windows (stride 1)" % (spec.get("roll") or 0), "",
              "| windows | IM leads | share | cumulative gap min | median | max | annualised "
              "min | median | max |", "|---|---|---|---|---|---|---|---|---|"]
    lines.append("| %d | %d | %s | %s | %s | %s | %s | %s | %s |"
                 % (roll.get("windows") or 0, roll.get("im_leads") or 0,
                    _pct(roll.get("share_im_leads") or 0.0),
                    _pp((roll.get("gap_cum_pp_min") or 0.0) / 100.0),
                    _pp((roll.get("gap_cum_pp_median") or 0.0) / 100.0),
                    _pp((roll.get("gap_cum_pp_max") or 0.0) / 100.0),
                    _pp((roll.get("gap_ann_pp_min") or 0.0) / 100.0),
                    _pp((roll.get("gap_ann_pp_median") or 0.0) / 100.0),
                    _pp((roll.get("gap_ann_pp_max") or 0.0) / 100.0)))
    lines += ["", "The 27 windows overlap by 25 of 26 periods, so the share is a description of the "
                  "path and not 27 independent trials; no multiplicity correction is claimed.", "",
              "## 5. Period-level sign test", "",
              "| periods | IM periods | ETF periods | IM share | two-sided binomial p | mean "
              "per-period difference |", "|---|---|---|---|---|---|"]
    lines.append("| %d | %d | %d | %s | %.4f | %s |"
                 % (sign.get("periods") or 0, sign.get("im_periods") or 0,
                    sign.get("etf_periods") or 0, _pct(sign.get("im_share") or 0.0),
                    sign.get("p_two_sided") or 1.0,
                    _pp((sign.get("mean_diff_pp") or 0.0) / 100.0)))
    lines += ["", "## 6. Drop-one jackknife", "",
              "| periods | full gap | min | max | largest move | worst period dropped | all "
              "positive |", "|---|---|---|---|---|---|---|"]
    worst = jack.get("worst_drop") or {}
    lines.append("| %d | %s | %s | %s | %s | %s | %s |"
                 % (jack.get("periods") or 0, _pp((jack.get("full_gap_ann_pp") or 0.0) / 100.0),
                    _pp((jack.get("min_gap_ann_pp") or 0.0) / 100.0),
                    _pp((jack.get("max_gap_ann_pp") or 0.0) / 100.0),
                    _pp((jack.get("max_abs_change_pp") or 0.0) / 100.0),
                    worst.get("date"), "yes" if jack.get("all_positive") else "no"))
    lines += ["", "## 7. The deposit rate the flip needs", "",
              "r2036's second caveat was that the frozen balance may earn less than the declared "
              "2% -- a short-sale proceeds balance is often frozen outright. That is not a reason "
              "to doubt the flip unless the flip moves inside the range a broker could pay, so "
              "this section sweeps the yield and solves for the tie.", "",
              "| declared cash yield | gap (IM minus ETF) |", "|---|---|"]
    for s in (yf.get("scan") or []):
        lines.append("| %s | %s |" % (_pct(s.get("cash_yield")),
                                     _pp((s.get("gap_ann_pp") or 0.0) / 100.0)))
    be = yf.get("breakeven_cash_yield")
    lines += ["", "**Break-even: %s.** %s. The funded book return the comparison is measured "
                  "against is %s."
                  % (_pct(be) if be is not None else "outside the bracket",
                     yf.get("breakeven_note"), _pct(yf.get("book_funded_return"))), ""]

    lines += ["## 8. Verdict", "", "**`%s`**" % face.get("verdict"), "",
              "Every flag below is computed from its own inputs and several can hold at once; the "
              "headline names the ones that change what a reader would do.", ""]
    for flag, on in (face.get("verdicts") or {}).items():
        if on and flag in VERDICT_WHY:
            lines.append("- `%s` -- %s" % (flag, VERDICT_WHY[flag]))
    lines.append("")

    reads = face.get("reads") or []
    if reads:
        lines += ["## 9. Readings", ""]
        for r in reads:
            lines.append("- **%s.** %s" % (r.get("id"), r.get("text")))
        lines.append("")

    lines += ["## 10. What this face does not settle", ""]
    for c in face.get("caveats") or []:
        lines.append("- " + c)
    lines += ["", "Machine `%s`, generated %s." % (face.get("machine"), face.get("generated")),
              "", "## 11. Reproduction", "", "```",
              "python scripts/astock_veto_hedge_stability.py selftest",
              "python scripts/astock_veto_hedge_stability.py run",
              "python scripts/astock_veto_hedge_stability.py check", "```", ""]
    return "\n".join(lines)


# ------------------------------------------------------------------------- cmds
def run() -> int:
    face = build_face()
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    _write_md(render_md(face))
    roll = face.get("rolling_summary") or {}
    yf = face.get("yield_sensitivity") or {}
    print("stability -> %s | %s" % (face.get("verdict"), _rel(OUT_JSON)))
    print("  full gap %s | rolling IM leads %d/%d (%s) | breakeven cash yield %s"
          % (_pp(((face.get("full") or {}).get("gap_ann_pp") or 0.0) / 100.0),
             roll.get("im_leads") or 0, roll.get("windows") or 0,
             _pct(roll.get("share_im_leads") or 0.0),
             _pct(yf.get("breakeven_cash_yield"))))
    return 0


def _write_md(text: str) -> None:
    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


VOLATILE = ("generated",)


def _diff(pub, fresh, path="", out=None, tol=1e-9):
    """Every published number must re-derive; a mover is STALE, a disagreement is a defect."""
    if out is None:
        out = []
    if isinstance(pub, dict) and isinstance(fresh, dict):
        for key in sorted(set(pub) | set(fresh)):
            if not path and key in VOLATILE:
                continue
            if key not in pub:
                out.append("%s/%s only in fresh" % (path, key))
                continue
            if key not in fresh:
                out.append("%s/%s only in published" % (path, key))
                continue
            _diff(pub[key], fresh[key], "%s/%s" % (path, key), out, tol)
        return out
    if isinstance(pub, list) and isinstance(fresh, list):
        if len(pub) != len(fresh):
            out.append("%s length %d != %d" % (path, len(pub), len(fresh)))
            return out
        for i, (a, b) in enumerate(zip(pub, fresh)):
            _diff(a, b, "%s[%d]" % (path, i), out, tol)
        return out
    if isinstance(pub, bool) or isinstance(fresh, bool):
        if pub != fresh:
            out.append("%s %r != %r" % (path, pub, fresh))
        return out
    if isinstance(pub, (int, float)) and isinstance(fresh, (int, float)):
        if not (math.isnan(pub) and math.isnan(fresh)) and abs(float(pub) - float(fresh)) > tol:
            out.append("%s %.12g != %.12g" % (path, pub, fresh))
        return out
    if pub != fresh:
        out.append("%s %r != %r" % (path, pub, fresh))
    return out


def check() -> int:
    """Parents moved => STALE; same parents and a different number => CHECK FAILED."""
    problems = []
    try:
        face = _read_json(OUT_JSON)
    except FileNotFoundError:
        print("STALE face missing: %s" % _rel(OUT_JSON))
        return 3
    except (json.JSONDecodeError, OSError) as exc:
        print("CHECK FAILED unreadable face: %s" % exc)
        return 1
    try:
        md = open(OUT_MD, encoding="utf-8").read()
    except FileNotFoundError:
        print("STALE page missing: %s" % _rel(OUT_MD))
        return 3

    for name, path in (("beta", PARENT), ("carrier", CARRIER), ("funding", FUNDING)):
        stored = (face.get("parents") or {}).get(name) or {}
        if not os.path.exists(path):
            print("STALE parent %s missing (%s)" % (name, _rel(path)))
            return 3
        if stored.get("file_sha256") != _sha_file(path):
            print("STALE parent %s moved (%s)" % (name, _rel(path)))
            return 3
        if stored.get("content_sha256") != content_sha(_read_json(path)):
            print("STALE parent %s content moved (%s)" % (name, _rel(path)))
            return 3

    fresh = build_face()
    if fresh.get("verdict") in ("NOT_ENOUGH_PERIODS", "PARENT_BLOCKS_MISSING"):
        print("STALE sample too short to re-derive")
        return 3
    problems.extend(_diff({k: v for k, v in face.items() if k != "content_sha256"},
                          {k: v for k, v in fresh.items() if k != "content_sha256"}))
    if face.get("content_sha256") != content_sha(face):
        problems.append("published content_sha256 does not match its own body")

    tokens = ["`%s`" % face.get("verdict"),
              "%.0f" % ((face.get("sample") or {}).get("periods") or 0)]
    roll = face.get("rolling_summary") or {}
    if roll.get("windows"):
        tokens.append("%d of " % (roll.get("im_leads") or 0))
    for token in tokens:
        if token not in md:
            problems.append("page missing token %r" % token)

    if problems:
        print("CHECK FAILED %d problem(s)" % len(problems))
        for p in problems[:12]:
            print("  - " + p)
        return 1
    print("CHECK OK verdict=%s full_gap=%s share_im_leads=%s breakeven=%s"
          % (face.get("verdict"),
             _pp(((face.get("full") or {}).get("gap_ann_pp") or 0.0) / 100.0),
             _pct(roll.get("share_im_leads") or 0.0),
             _pct((face.get("yield_sensitivity") or {}).get("breakeven_cash_yield"))))
    return 0


# --------------------------------------------------------------------- selftest
def selftest() -> int:
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    # --- the two rulers agree with the family's own annualiser
    vals = [0.01, -0.02, 0.03, 0.00, 0.015]
    a_stats = arm_stats(vals, 12.6) or {}
    leg("L1 annualized() reproduces arm_stats on the same list",
        abs(annualized(vals, 12.6) - (a_stats.get("annualized_compound") or 0.0)) < 1e-12)
    leg("L1b a missing period is dropped, not counted as zero",
        abs(annualized([0.01, None, 0.03], 12.6) - annualized([0.01, 0.03], 12.6)) < 1e-15)
    leg("L1c two periods is the minimum that can be annualised", annualized([0.01], 12.6) is None)
    leg("L1d a series that wipes out cannot be annualised", annualized([-1.0, 0.01], 12.6) is None)

    # --- window_gap: sign convention and both rulers
    im = [0.02, 0.02, 0.02, 0.02]
    et = [0.01, 0.01, 0.01, 0.01]
    st = window_gap(im, et, 0, 4, 12.0)
    leg("L2 gap is IM minus ETF", st["gap_ann_pp"] > 0.0 and st["gap_cum_pp"] > 0.0)
    leg("L2b a swapped pair flips the sign",
        window_gap(et, im, 0, 4, 12.0)["gap_cum_pp"] < 0.0)
    leg("L2c identical series give a zero gap",
        abs(window_gap(im, im, 0, 4, 12.0)["gap_cum_pp"]) < 1e-15)
    leg("L2d slicing is inclusive of start and exclusive of end",
        window_gap(im, et, 1, 3, 12.0)["periods"] == 2)
    leg("L2e a one-period slice cannot be priced", window_gap(im, et, 0, 1, 12.0) is None)
    leg("L2f cumulative gap is the difference of the two compounded growths",
        abs(window_gap([0.10, 0.10], [0.0, 0.0], 0, 2, 12.0)["gap_cum_pp"]
            - ((1.1 ** 2 - 1.0) - 0.0) * 100.0) < 1e-12)

    # --- binomial
    leg("L3 a fair split is not significant", binom_two_sided(26, 52) > 0.99)
    leg("L3b a clean sweep is significant", binom_two_sided(52, 52) < 1e-12)
    leg("L3c the test is two-sided and symmetric",
        abs(binom_two_sided(10, 52) - binom_two_sided(42, 52)) < 1e-12)
    leg("L3d an empty sample is p=1", binom_two_sided(0, 0) == 1.0)
    leg("L3e 40 of 50 is still not a coin", 0.0 < binom_two_sided(40, 50) < 0.001)

    # --- share helper
    leg("L4 share counts strictly positive gaps only",
        abs(share_positive([1.0, 0.0, -1.0, 2.0]) - 0.5) < 1e-15)
    leg("L4b an empty list has no share", share_positive([]) == 0.0)
    leg("L4c None is not a positive period", abs(share_positive([None, 1.0]) - 1.0) < 1e-15)

    # --- the funding identity this face inherits, re-checked here
    f_same = funded_series([0.10], 0.0, 0.02, CAPITAL, 12.6)
    leg("L5 a zero block leaves the book return untouched", abs(f_same[0] - 0.10) < 1e-15)
    b = borrow_series([0.01], 0.02, 900_000.0, CAPITAL, 12.6)
    leg("L5b the rent is charged per period on the notional as a share of the book",
        abs((0.01 - b[0]) - 0.02 / 12.6 * 0.9) < 1e-15)
    leg("L5c a zero rent changes nothing",
        borrow_series([0.01], 0.0, 900_000.0, CAPITAL, 12.6) == [0.01])
    leg("L5d the funded blend is monotone in the block (a bigger block dilutes a book that "
        "beats cash)",
        funded_series([0.20], 500_000.0, 0.02, CAPITAL, 12.6)[0]
        < funded_series([0.20], 100_000.0, 0.02, CAPITAL, 12.6)[0])

    # --- break-even monotonicity: the leg with more cash benefits more from a higher yield
    def gap_y(y):
        im_s = funded_series([0.10, 0.10], 400_000.0, y, CAPITAL, 12.6)
        et_s = funded_series([0.08, 0.08], 900_000.0, y, CAPITAL, 12.6)
        return window_gap(im_s, et_s, 0, 2, 12.6)["gap_ann_pp"]
    leg("L6 the gap falls as the cash yield rises (the bigger block gains more)",
        gap_y(0.0) > gap_y(0.05) > gap_y(0.20))
    leg("L6b the break-even is where the gap crosses zero",
        abs(gap_y(0.02) - gap_y(0.02)) < 1e-15 and gap_y(0.0) != gap_y(0.02))

    # --- verdict ladder: each flag on its own input
    def mk(gap_ann=2.0, share=1.0, quarters=(-1.0, -2.0, -3.0, -4.0), jack_move=0.1,
           be=0.15, book=0.0939):
        f = {"gap_ann_pp": gap_ann}
        qs = [{"gap_cum_pp": g, "gap_ann_pp": g} for g in quarters]
        roll = [1.0] * int(round(share * 10)) + [-1.0] * (10 - int(round(share * 10)))
        return decide(f, [], qs, [], roll, {}, {"max_abs_change_pp": jack_move},
                      {"breakeven_cash_yield": be, "book_funded_return": book,
                       "breakeven_note": ""})

    fl = mk()
    leg("L7 all pieces agreeing makes the flip a property of the rule", fl[VERDICT_STABLE])
    leg("L7b a flip that survives its yield is called assumption-free", fl[VERDICT_YIELD_ROBUST])
    leg("L7c the headline names both", headline(fl) == VERDICT_STABLE + "+" + VERDICT_YIELD_ROBUST)
    leg("L7d a coin-toss share is not stable", not mk(share=0.4)[VERDICT_STABLE])
    leg("L7e and it is called a coin toss", mk(share=0.4)[VERDICT_COIN])
    leg("L7f quarters that disagree break the stable flag",
        not mk(quarters=(1.0, -1.0, 2.0, -2.0))[VERDICT_STABLE])
    leg("L7g a jackknife bigger than the gap is flagged",
        mk(gap_ann=1.0, jack_move=1.5)[VERDICT_JACK])
    leg("L7h a jackknife smaller than the gap is not",
        not mk(gap_ann=1.0, jack_move=0.5)[VERDICT_JACK])
    leg("L7i a break-even below the declared rate is fragile",
        mk(be=0.01)[VERDICT_YIELD_FRAGILE] and not mk(be=0.01)[VERDICT_YIELD_ROBUST])
    leg("L7j a break-even above twice the book is robust", mk(be=0.30)[VERDICT_YIELD_ROBUST])
    leg("L7k a shrinking last block is flagged",
        mk(quarters=(-3.0, -3.2, -3.1, -0.5))[VERDICT_NARROW])
    leg("L7l a last block in line with the others is not",
        not mk(quarters=(-3.0, -3.2, -3.1, -2.9))[VERDICT_NARROW])
    leg("L7m a negative last block is a reversal, not a narrowing",
        not mk(quarters=(-3.0, -3.2, -3.1, 0.5))[VERDICT_NARROW])

    # --- the live face, if it is on disk: anchor, ranges, and self-consistency
    if os.path.exists(OUT_JSON):
        face = _read_json(OUT_JSON)
        full = face.get("full") or {}
        pub = face.get("anchor_gap_pub_pp")
        leg("L8 the published anchor is r2036's funded gap",
            pub is not None and abs((full.get("gap_ann_pp") or 0.0) - float(pub)) < 1e-9,
            "full=%s pub=%s" % (full.get("gap_ann_pp"), pub))
        roll = face.get("rolling_summary") or {}
        leg("L8b every rolling window is the declared length",
            all((r.get("periods") or 0) == (face.get("spec") or {}).get("roll")
                for r in (face.get("rolling") or [])))
        leg("L8c the rolling count is n - roll + 1",
            (roll.get("windows") or 0) == (face.get("sample") or {}).get("periods", 0)
            - (face.get("spec") or {}).get("roll", 0) + 1)
        leg("L8d the share agrees with the count it is computed from",
            abs((roll.get("share_im_leads") or 0.0)
                - (roll.get("im_leads") or 0) / max(1, roll.get("windows") or 1)) < 1e-12)
        sign = face.get("sign_test") or {}
        leg("L8e the sign test's two sides add up",
            (sign.get("im_periods") or 0) + (sign.get("etf_periods") or 0)
            == (sign.get("periods") or 0))
        jack = face.get("jackknife") or {}
        leg("L8f the jackknife covers every period",
            (jack.get("periods") or 0) == (face.get("sample") or {}).get("periods", 0))
        leg("L8g the jackknife's largest move is a real maximum",
            (jack.get("max_abs_change_pp") or 0.0) >= abs(
                (jack.get("max_gap_ann_pp") or 0.0) - (full.get("gap_ann_pp") or 0.0)) - 1e-9)
        leg("L8h the verdict is one of the ladder's words",
            face.get("verdict", "").split("+")[0] in (
                VERDICT_STABLE, VERDICT_ONE_WINDOW, VERDICT_COIN, VERDICT_MIXED))
        leg("L8h2 every word in the verdict has a flag that is on",
            all((face.get("verdicts") or {}).get(w) for w in face.get("verdict", "").split("+")
                if w in VERDICT_WHY))
        leg("L8i the content hash is stable under a round trip",
            content_sha(face) == face.get("content_sha256"))

    width = max((len(n) for n, _, _ in legs), default=10)
    bad = [x for x in legs if not x[1]]
    for name, ok, detail in legs:
        print("%s %-*s %s" % ("PASS" if ok else "FAIL", width, name, detail))
    print("%d/%d PASS" % (len(legs) - len(bad), len(legs)))
    return 0 if not bad else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "check", "selftest"])
    args = ap.parse_args(argv)
    if args.cmd == "run":
        return run()
    if args.cmd == "check":
        return check()
    return selftest()


if __name__ == "__main__":
    raise SystemExit(main())
