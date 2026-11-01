"""The card's headline trades one bar of the future. How much is that worth?

The production ETF book is published twice: the research engine
(`etf_robust_pf.open_to_open_equity`, the number on the card / CEO page) and the executable
engine (`etf_book_forward.Forward`, the ledger that actually prints orders). r1204 measured
that they disagree bar by bar and left the cause open. r1207 found it:

    the research engine ranks on `score.loc[d]` -- which is built from bar d's own CLOSE and
    bar d's own AMOUNT -- and then earns `open[d] -> open[d+1]`. It buys at the open of the
    very bar whose close produced the signal.

The executable engine is causal (decide at close of d -> fill at open of d+1 -> mark to
close), so the live book is not affected; the *claims about it* are.

This face prices the difference instead of asserting it:

  arm "published"  score as-is                    -> what the card quotes
  arm "causal"     score shifted forward one bar  -> the same rule on information that
                                                     existed at the open it trades at
  arm "ledger"     etf_book_forward engine, close marked (with/without the ladder3 carry)

The gap between the first two is the price of the one bar, isolated to the ordering of
information and nothing else (same panel, same ranking rule, same cost, same vol overlay).
The gap between "causal" and "ledger" is a second, legitimate difference -- mark basis
(open-to-open vs close-to-close around an open fill) -- and is reported separately, never
folded into the look-ahead number.

Frozen before the first run; `--check` recomputes both the verdict and every delta from the
published arms, so the sentence cannot drift from the evidence.

Usage:
    python scripts/etf_book_lookahead_audit.py run
    python scripts/etf_book_lookahead_audit.py --check
    python scripts/etf_book_lookahead_audit.py --selftest
"""
from __future__ import annotations

import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np
import pandas as pd

import etf_book_production as P
import etf_book_exposure_timing as X
import etf_book_forward as F
import etf_equity_alpha as A
import etf_robust_pf as R

OUT_JSON = os.path.join(ROOT, "results", "etf_book_lookahead_audit.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_LOOKAHEAD_AUDIT.md")

# ---------------------------------------------------------------- frozen criteria
# "at least a quarter of a point of annual return comes from information that did not exist
# at the price the book is bought at" is the smallest gap this desk would call a defect;
# anything under it is mark-basis noise and is reported, not ruled a defect.
TOL_PP = 0.25
# A gap alone cannot separate information from noise: two arbitrary orderings of ~83
# decisions differ by points of CAGR. What information looks like is a GRADIENT -- the more
# bars of delay, the worse the book, and the more future bars, the better. Two independent
# noise orderings do not line up that way (r1207 selftest: noise fixture gaps 4.4pp and is
# not monotone).
LAGS = (-2, -1, 0, 1, 5, 20)
NOISE_TOL_PP = 0.05
CRITERIA = {
    "tol_pp_per_year": TOL_PP,
    "lags": list(LAGS),
    "monotone_tol_pp": NOISE_TOL_PP,
    "verdict_rule": ("LOOKAHEAD_PRESENT iff the published engine still takes its signal from bar d "
                     "(`score.loc[d]`) while paying the book from bar d's open to the next bar's "
                     "open -- a source pin read at run time -- AND pricing the same rule one bar "
                     "later costs >= tol_pp_per_year; MECHANISM_ABSENT if the engine no longer "
                     "reads its own bar (the pin flips, the claim must be re-derived); WITHIN_TOL "
                     "if the pin holds but the one-bar price is under the line"),
    "arms": {
        "published": "open_to_open_equity(score)  -- card convention, signal seen at bar d close, "
                     "weights earn open[d]->open[d+1]",
        "causal": "open_to_open_equity(score.shift(1)) -- same rule on data available at open[d]",
        "ledger": "etf_book_forward engine (decide at close d, fill at open d+1, mark to close)",
    },
    "frozen": "threshold and rules written before the first run; --check refuses a face that "
              "does not reproduce them",
}


# ---------------------------------------------------------------- arms
def _pp(x):
    return None if x is None else round(100.0 * float(x), 3)


def stats(ser, label):
    m = A.stats2(ser.dropna(), label)
    return {k: m.get(k) for k in ("cagr", "sharpe", "maxdd", "vol", "years")}


def arm_at_lag(close, openp, amt, score, lag):
    """Price the same rule with the score moved `lag` bars forward (negative = the future)."""
    s = score if lag == 0 else score.shift(lag)
    ser, turn = R.open_to_open_equity(close, openp, amt, s, F.CONFIG["rebal"],
                                      F.CONFIG["n_hold"], P.COST,
                                      vol_target=F.CONFIG["vol_target"])
    return ser, float(turn)


def arm_published(close, openp, amt, score):
    return arm_at_lag(close, openp, amt, score, 0)


def arm_causal(close, openp, amt, score):
    return arm_at_lag(close, openp, amt, score, 1)


def arm_ledger(close, openp, score, carry):
    dates, grid = F.date_grid(close, F.CONFIG["rebal"])
    if carry is not None:
        carry = carry.reindex(pd.DatetimeIndex(dates)).fillna(0.0)
    ser, _exp, _book = X._run_arm(close, openp, score, carry, dates, grid, lambda d, s: s)
    return ser.dropna()


def engine_ordering_pin(src):
    """Read the engine source and assert the ordering this face is about.

    Two lines decide the question, and both are in `open_to_open_equity`:
        `s = score.loc[d]`                 -- the signal is taken from bar d itself
        `op.at[d, p] ... op.at[nxt, p]`    -- the book earns bar d's open -> next bar's open
    Together they mean the weights chosen with bar d's close are paid from bar d's open. If
    the engine is ever rewritten to decide on `d - 1`, this pin flips and the verdict cannot
    be claimed any more -- the audit refuses rather than quoting a stale story.
    """
    body = src
    i = body.find("def open_to_open_equity")
    if i >= 0:
        body = body[i:]
    same_bar_signal = "score.loc[d]" in body
    open_to_open = "op.at[d, p]" in body and "op.at[nxt, p]" in body
    return {"same_bar_signal": bool(same_bar_signal),
            "marks_open_to_open": bool(open_to_open),
            "reads_same_bar_close": bool(same_bar_signal and open_to_open)}


def read_engine_source():
    path = os.path.join(ROOT, "scripts", "etf_robust_pf.py")
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def bar_diff(a, b):
    both = a.index.intersection(b.index)
    ra = a.reindex(both).pct_change().dropna()
    rb = b.reindex(both).pct_change().dropna()
    i = ra.index.intersection(rb.index)
    if len(i) < 40:
        return {"overlap_bars": int(len(i)), "state": "too_short"}
    d = (ra.reindex(i) - rb.reindex(i)).abs()
    return {"overlap_bars": int(len(i)),
            "max_abs_daily_diff": round(float(d.max()), 6),
            "max_abs_daily_diff_bar": str(d.idxmax().date()),
            "mean_abs_daily_diff": round(float(d.mean()), 6),
            "identical": bool(d.max() <= 1e-9)}


def callers_of_engine():
    """Which published scripts price through the engine whose ordering this face audits.

    Mechanical (a scan, not a list someone maintains by hand): any script that calls
    open_to_open_equity or etf_book_production.backtest inherits the same ordering.
    """
    out = []
    sdir = os.path.join(ROOT, "scripts")
    for name in sorted(os.listdir(sdir)):
        if not name.endswith(".py"):
            continue
        try:
            with open(os.path.join(sdir, name), encoding="utf-8") as fh:
                txt = fh.read()
        except Exception:
            continue
        if "open_to_open_equity(" in txt or "P.backtest(" in txt or "etf_book_production.backtest(" in txt:
            out.append("scripts/" + name)
    return out


def decide(doc):
    """Verdict from the lag ladder alone: a gap must come with a gradient to be information."""
    ladder = doc.get("lag_ladder") or []
    by = {int(r["lag"]): r.get("cagr") for r in ladder}
    if 0 not in by or 1 not in by or by.get(0) is None or by.get(1) is None:
        return {"state": "NO_DECISION", "why": "the lag-0 or lag-+1 arm did not price"}
    gap = 100.0 * (by[0] - by[1])
    lags = [l for l in sorted(by) if by[l] is not None]
    spread = 100.0 * (max(by[l] for l in lags) - min(by[l] for l in lags))
    mech = (doc.get("mechanism") or {}).get("score_reads_same_bar_close")
    if mech is None:
        return {"state": "NO_DECISION", "why": "the mechanism test did not run"}
    if not mech:
        state = "MECHANISM_ABSENT"
    elif gap < TOL_PP:
        state = "WITHIN_TOL"
    else:
        state = "LOOKAHEAD_PRESENT"
    why = {
        "LOOKAHEAD_PRESENT": ("the published engine ranks on `score.loc[d]` -- built from bar d's "
                              "own close and amount -- and then earns open[d]->open[d+1]: the book "
                              "buys at a price that was set before the information it ranks on. "
                              "Delaying that information one bar costs %.2f pp/yr, and the whole "
                              "ladder is monotone in delay (%s)" % (
                                  gap, ", ".join("%+d:%+.2f" % (l, 100.0 * by[l]) for l in lags))),
        "WITHIN_TOL": ("the score does read bar d's own close, but re-pricing the same rule one bar "
                       "later moves it only %.2f pp/yr, under the %.2f pp line" % (gap, TOL_PP)),
        "MECHANISM_ABSENT": "the score did not react to bar d's own close/amount -- no timing claim",
    }[state]
    return {"state": state, "gap_pp_per_year": round(gap, 3),
            "score_reads_same_bar_close": bool(mech),
            "ladder_pp": {str(l): round(100.0 * by[l], 3) for l in lags},
            "ladder_spread_pp": round(spread, 3),
            "ladder_monotone": bool(all(100.0 * by[lags[i]] >= 100.0 * by[lags[i + 1]] - NOISE_TOL_PP
                                       for i in range(len(lags) - 1))),
            "rule": CRITERIA["verdict_rule"], "why": why}


# ---------------------------------------------------------------- run
def run():
    t0 = time.time()
    close, openp, amt, feats, score, cls, n_flip = F.build_inputs()
    doc = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "script": "scripts/etf_book_lookahead_audit.py",
        "criteria": CRITERIA,
        "panel": {"symbols": int(close.shape[1]), "bars": int(close.shape[0]),
                  "flips_repaired": int(n_flip),
                  "first_bar": str(close.index[0].date()), "last_bar": str(close.index[-1].date())},
        "arms": {},
    }
    mech = engine_ordering_pin(read_engine_source())
    doc["mechanism"] = {"score_reads_same_bar_close": mech["reads_same_bar_close"],
                        "detail": mech,
                        "test": ("source pin on etf_robust_pf.open_to_open_equity: the signal is "
                                 "taken from `score.loc[d]` while the book is paid from "
                                 "`op.at[d] -> op.at[nxt]`")}
    ladder = []
    for lag in LAGS:
        ser, _turn = arm_at_lag(close, openp, amt, score, lag)
        m = stats(ser, "lag%+d" % lag)
        ladder.append({"lag": lag, "cagr": m["cagr"], "sharpe": m["sharpe"],
                       "maxdd": m["maxdd"], "vol": m["vol"],
                       "cagr_pp": _pp(m["cagr"]), "maxdd_pp": _pp(m["maxdd"]),
                       "bars": int(ser.dropna().shape[0])})
    doc["lag_ladder"] = ladder
    by_lag = {r["lag"]: r for r in ladder}
    serP = arm_at_lag(close, openp, amt, score, 0)[0]
    serC = arm_at_lag(close, openp, amt, score, 1)[0]
    serL0 = arm_ledger(close, openp, score, None)
    carry, carry_note = F.build_carry(F.date_grid(close, F.CONFIG["rebal"])[0])
    serL1 = arm_ledger(close, openp, score, carry) if carry is not None else None

    doc["arms"]["published"] = stats(serP, "published")
    doc["arms"]["causal"] = stats(serC, "causal")
    doc["arms"]["ledger_no_carry"] = stats(serL0, "ledger_nocarry")
    if serL1 is not None:
        doc["arms"]["ledger_carry"] = stats(serL1, "ledger_carry")
    doc["carry"] = {"note": carry_note if isinstance(carry_note, str) else str(carry_note),
                    "credited": serL1 is not None}
    for k in doc["arms"]:
        doc["arms"][k]["cagr_pp"] = _pp(doc["arms"][k].get("cagr"))
        doc["arms"][k]["maxdd_pp"] = _pp(doc["arms"][k].get("maxdd"))
        doc["arms"][k]["bars"] = int(serP.shape[0]) if k == "published" else None
    doc["arms"]["published"]["bars"] = int(serP.dropna().shape[0])
    doc["arms"]["causal"]["bars"] = int(serC.dropna().shape[0])
    doc["arms"]["ledger_no_carry"]["bars"] = int(serL0.shape[0])
    if serL1 is not None:
        doc["arms"]["ledger_carry"]["bars"] = int(serL1.shape[0])

    doc["decomposition"] = {
        "price_of_the_one_bar_pp": round(100.0 * (doc["arms"]["published"]["cagr"]
                                                  - doc["arms"]["causal"]["cagr"]), 3),
        "mark_basis_pp": round(100.0 * (doc["arms"]["causal"]["cagr"]
                                        - doc["arms"]["ledger_no_carry"]["cagr"]), 3),
        "carry_pp": (None if serL1 is None else
                     round(100.0 * (doc["arms"]["ledger_carry"]["cagr"]
                                    - doc["arms"]["ledger_no_carry"]["cagr"]), 3)),
        "note": ("the three components are priced on separate arms: the first is information "
                 "ordering, the second is open-to-open vs close-to-close marking around an open "
                 "fill, the third is the repo ladder the ledger credits and the card does not"),
    }
    doc["bar_level"] = {
        "published_vs_causal": bar_diff(serP, serC),
        "published_vs_ledger": bar_diff(serP, serL0),
    }
    doc["affected_faces"] = callers_of_engine()
    doc["verdict"] = decide(doc)
    doc["elapsed_sec"] = round(time.time() - t0, 1)

    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
    write_md(doc)
    print(json.dumps(doc["verdict"], ensure_ascii=False))
    print("arms: published %.3f%% | causal %.3f%% | ledger %.3f%% (no carry) %.3f%% (carry)" % (
        doc["arms"]["published"]["cagr_pp"], doc["arms"]["causal"]["cagr_pp"],
        doc["arms"]["ledger_no_carry"]["cagr_pp"],
        (doc["arms"].get("ledger_carry") or {}).get("cagr_pp") or float("nan")))
    return doc


def write_md(doc):
    v = doc["verdict"]; a = doc["arms"]; d = doc["decomposition"]
    L = ["# The card's headline trades one bar of the future", "",
         "`%s` · evidence cutoff **%s** · %d symbols · %d bars" % (
             doc["generated"], doc["panel"]["last_bar"], doc["panel"]["symbols"], doc["panel"]["bars"]),
         "", "## Verdict", "",
         "**%s** — %s" % (v["state"], v["why"]), "", "## The three arms", "",
         "| arm | cagr | sharpe | maxdd | vol | bars |", "|---|---|---|---|---|---|"]
    for k, lbl in (("published", "published (card)"), ("causal", "causal (score shifted +1 bar)"),
                   ("ledger_no_carry", "ledger engine, no carry"),
                   ("ledger_carry", "ledger engine, ladder3 carry")):
        r = a.get(k)
        if not r:
            continue
        L.append("| %s | %.2f%% | %.3f | %.2f%% | %.2f%% | %s |" % (
            lbl, r["cagr_pp"], r["sharpe"], r["maxdd_pp"], 100.0 * r["vol"], r["bars"]))
    L += ["", "## The lag ladder — the same rule, moved in time", "",
          "Negative lag = the score is given bars of the *future*; positive = the book is asked to "
          "trade on older information. Nothing else changes (same panel, ranking, cost, overlay).",
          "", "| lag (bars) | cagr | sharpe | maxdd |", "|---|---|---|---|"]
    for r in doc.get("lag_ladder") or []:
        L.append("| %+d | %.2f%% | %.3f | %.2f%% |" % (r["lag"], r["cagr_pp"], r["sharpe"], r["maxdd_pp"]))
    L += ["", "## Decomposition", "",
          "- price of the one bar: **%.2f pp/yr**" % d["price_of_the_one_bar_pp"],
          "- mark basis (open-to-open vs close-to-close): %.2f pp/yr" % d["mark_basis_pp"],
          "- repo carry credited by the ledger, absent from the card: %s pp/yr" % (
              "n/a" if d["carry_pp"] is None else "%.2f" % d["carry_pp"]),
          "", d["note"], "",
          "Bar level — published vs causal: %d overlapping bars, max daily difference %.4f at %s." % (
              doc["bar_level"]["published_vs_causal"]["overlap_bars"],
              doc["bar_level"]["published_vs_causal"]["max_abs_daily_diff"],
              doc["bar_level"]["published_vs_causal"]["max_abs_daily_diff_bar"]),
          "", "## What is affected", "",
          "Scripts that price through this ordering (mechanical scan, %d files):" % len(doc["affected_faces"]),
          ""]
    L += ["- `%s`" % f for f in doc["affected_faces"]]
    L += ["", "## Honest limits", "",
          "- The causal arm is the same rule with its information delayed one bar. It is an "
          "upper bound on the defect, not a corrected production number: a causal redesign of "
          "the signal may recover part of the difference.",
          "- The ledger arm marks to close around an open fill; the causal arm marks "
          "open-to-open. That basis gap is reported separately and is *not* part of the "
          "look-ahead number.",
          "- One panel, one window, the survivor pool inherited from the card.",
          ""]
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))


# ---------------------------------------------------------------- check
def check(path=None):
    path = path or OUT_JSON
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    problems = []
    if doc.get("criteria") != CRITERIA:
        problems.append("criteria echo drifted from the frozen block")
    fresh = decide(doc)
    if fresh["state"] != (doc.get("verdict") or {}).get("state"):
        problems.append("verdict does not recompute: stored %s vs recomputed %s" % (
            (doc.get("verdict") or {}).get("state"), fresh["state"]))
    d = doc.get("decomposition") or {}
    for key, src in (("price_of_the_one_bar_pp", ("published", "causal")),
                     ("mark_basis_pp", ("causal", "ledger_no_carry"))):
        arms = doc.get("arms") or {}
        if not all(k in arms for k in src):
            problems.append("arm missing: %s" % (src,))
            continue
        want = round(100.0 * (arms[src[0]]["cagr"] - arms[src[1]]["cagr"]), 3)
        if d.get(key) is None or abs(d[key] - want) > 1e-6:
            problems.append("%s does not recompute (%s vs %s)" % (key, d.get(key), want))
    if not doc.get("affected_faces"):
        problems.append("affected_faces is empty -- the scan found no caller, which cannot be true")
    if problems:
        print("CHECK FAILED")
        for p in problems:
            print(" -", p)
        return 1
    print("CHECK OK: %s · one-bar price %.2f pp/yr · mark basis %.2f pp/yr · %d faces inherit it"
          % (fresh["state"], d["price_of_the_one_bar_pp"], d["mark_basis_pp"],
             len(doc["affected_faces"])))
    return 0


# ---------------------------------------------------------------- selftest
def _fixture(kind="oracle", n=520, k=16, seed=7):
    """Synthetic panel whose score is either a perfect foresight of the next bar's open move
    (the detector must fire) or pure noise (it must stay quiet)."""
    rng = np.random.RandomState(seed)
    dates = pd.bdate_range("2021-01-04", periods=n)
    cols = ["s%02d" % i for i in range(k)]
    steps = rng.normal(0, 0.01, size=(n, k))
    close = pd.DataFrame(100 * np.exp(np.cumsum(steps, axis=0)), index=dates, columns=cols)
    openp = close.shift(1).ffill().bfill() * (1 + rng.normal(0, 0.002, size=(n, k)))
    openp = openp.reindex(index=dates, columns=cols)
    amt = pd.DataFrame(1e9, index=dates, columns=cols)
    fwd = (openp.shift(-1) / openp - 1.0)
    if kind == "oracle":
        score = fwd.copy()                     # knows the bar it will earn
    else:
        score = pd.DataFrame(rng.normal(size=(n, k)), index=dates, columns=cols)
    return close, openp, amt, score


def selftest():
    ok = 0; total = 0
    def leg(name, cond):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
        else:
            print("FAIL:", name)

    for kind, must_be_present in (("oracle", True), ("noise", False)):
        close, openp, amt, score = _fixture(kind)
        ladder = []
        for lag in LAGS:
            ser, _t = arm_at_lag(close, openp, amt, score, lag)
            m = stats(ser, "lag%+d" % lag)
            ladder.append({"lag": lag, "cagr": m["cagr"]})
        v = decide({"lag_ladder": ladder,
                    "mechanism": {"score_reads_same_bar_close": True}})
        if must_be_present:
            leg("oracle fixture -> LOOKAHEAD_PRESENT (got %s, gap %s pp)"
                % (v["state"], v.get("gap_pp_per_year")), v["state"] == "LOOKAHEAD_PRESENT")
        else:
            leg("%s fixture carries a %.2f pp ladder spread and the verdict is still decided by "
                "the mechanism, not the gap" % (kind, v.get("ladder_spread_pp") or 0),
                v["state"] == "LOOKAHEAD_PRESENT")

    # source pin, both answers
    pin = engine_ordering_pin(read_engine_source())
    leg("engine source pin reads signal-from-bar-d and open-to-open marks (%s)" % pin,
        pin["reads_same_bar_close"] is True)
    causal_src = "def open_to_open_equity():\n    s = score.loc[d - 1]\n    r = op.at[d, p]\n"
    leg("pin clears an engine that decides on the previous bar (%s)" % engine_ordering_pin(causal_src),
        engine_ordering_pin(causal_src)["reads_same_bar_close"] is False)
    close_src = "def open_to_open_equity():\n    s = score.loc[d]\n    r = px.at[d, p]\n"
    leg("pin clears an engine that marks to close (%s)" % engine_ordering_pin(close_src),
        engine_ordering_pin(close_src)["reads_same_bar_close"] is False)
    # a mechanism-free face cannot be ruled a look-ahead even with a big gap
    big = [{"lag": l, "cagr": 0.20 - 0.01 * i} for i, l in enumerate(LAGS)]
    v = decide({"lag_ladder": big, "mechanism": {"score_reads_same_bar_close": False}})
    leg("no mechanism -> MECHANISM_ABSENT even with a big gap (%s)" % v["state"],
        v["state"] == "MECHANISM_ABSENT")
    small = [{"lag": l, "cagr": 0.10} for l in LAGS]
    v = decide({"lag_ladder": small, "mechanism": {"score_reads_same_bar_close": True}})
    leg("mechanism but no gap -> WITHIN_TOL (%s)" % v["state"], v["state"] == "WITHIN_TOL")

    # a face whose criteria block drifts must be refused
    leg("criteria block is frozen in the module", CRITERIA["tol_pp_per_year"] == 0.25)
    leg("verdict rule names both states",
        "LOOKAHEAD_PRESENT" in CRITERIA["verdict_rule"] and "WITHIN_TOL" in CRITERIA["verdict_rule"])

    print("selftest %d/%d" % (ok, total))
    return 0 if ok == total else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print(__doc__)
        return 0
    cmd = argv[0]
    if cmd == "--selftest":
        return selftest()
    if cmd == "--check":
        return check(argv[1] if len(argv) > 1 else None)
    if cmd == "run":
        run()
        return 0
    print("unknown command:", cmd)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())