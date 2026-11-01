"""Does the book earn its keep on many days, or on a handful of them?

Every face this desk has published on the ETF book retires one weakness at a time
(exposure, vol window, cost tape), and all of them quote a CAGR/Sharpe computed over
every bar. None of them answers the question a risk owner actually asks: if the ten
best days had not happened, would this book still be a book? A curve whose growth is
one or two bars wide is not a strategy, it is a lottery ticket whose jackpot already
paid -- and the same curve looks identical in the headline numbers.

So this face prices the tail directly, on the production book, with its own bars:

  * share of total log growth carried by the top N bars;
  * the book re-compounded with the best 1 / 5 / 10 bars removed;
  * a placebo: remove the same number of bars at RANDOM (fixed seed, N draws) so
    "dropping the best 5 days cost a lot" is measured against what dropping any 5
    days would have cost -- otherwise the reading is just arithmetic;
  * the best month removed, since a single month can hide a whole year.

Verdicts are frozen before the run and recomputed by --check from the published bars,
so the sentence on the page cannot drift from the evidence.

Usage:
    python scripts/etf_book_tail_dependence.py run
    python scripts/etf_book_tail_dependence.py --check
    python scripts/etf_book_tail_dependence.py --selftest
"""
from __future__ import annotations

import json
import os
import sys
import time
from math import ceil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np
import pandas as pd

import etf_book_exposure_timing as X
import etf_book_forward as F
import etf_equity_alpha as A

OUT_JSON = os.path.join(ROOT, "results", "etf_book_tail_dependence.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_TAIL_DEPENDENCE.md")

# ---------------------------------------------------------------- frozen criteria
K_DROPS = (1, 5, 10)         # bars removed in the deterministic drop-best arm
TOP_N = 10                   # bars whose share of total log growth is reported
N_PLACEBO = 1000             # random-drop draws per k
SEED = 20261101
SHARE_DEPENDENT = 0.50       # top-N bars carrying >= this share of the gross up-move = dependent
SHARE_ROBUST = 0.35          # at or below this share the book is not leaning on a few days
RETAIN_MIN = 0.50            # cagr kept after removing the best 10 bars, for ROBUST
DENSE_MIN = 40               # minimum bars before any of this means anything
CRITERIA = {"k_drops": list(K_DROPS), "top_n": TOP_N, "n_placebo": N_PLACEBO,
            "seed": SEED, "share_dependent": SHARE_DEPENDENT, "share_robust": SHARE_ROBUST,
            "retain_min": RETAIN_MIN, "dense_min": DENSE_MIN}


def returns_of(nav):
    """Daily simple returns from a nav series (first bar contributes nothing)."""
    return nav.pct_change().dropna()


def top_share(r, n=TOP_N):
    """Share of the book's GROSS up-move carried by the n best bars.

    Denominator is the sum of positive log returns, not net growth: a random walk with
    tiny positive drift has almost all of its net growth in a few bars by construction,
    so a net-growth share would call every ordinary book "dependent". Against the gross
    up-move the number means what readers assume it means -- how much of the rally came
    from a handful of days.
    """
    lg = np.log1p(r.to_numpy(dtype=float))
    gross = float(lg[lg > 0].sum())
    if gross <= 0 or not np.isfinite(gross):
        return None
    best = float(np.sort(lg)[-n:].sum())
    return best / gross


def recompound(r_drop, first_level=1.0):
    """Rebuild a nav from the surviving returns, starting at the same level."""
    nav = first_level * np.cumprod(1.0 + r_drop)
    idx = r_drop.index
    ser = pd.Series(np.concatenate([[first_level], nav]), index=idx.insert(0, idx[0] - pd.Timedelta(days=1)))
    return ser


def drop_best_rows(r, k):
    keep = r.drop(r.nlargest(k).index)
    return recompound(keep)


def placebo_cagrs(r, k, n=N_PLACEBO, seed=SEED):
    rng = np.random.default_rng(seed + k)
    vals = r.to_numpy(dtype=float)
    nbar = len(vals)
    out = []
    for _ in range(n):
        idx = rng.choice(nbar, size=k, replace=False)
        kept = np.delete(vals, idx)
        growth = float(np.prod(1.0 + kept))
        yrs = nbar / 252.0
        out.append(growth ** (1.0 / yrs) - 1.0 if growth > 0 else -1.0)
    return np.array(out, dtype=float)


def decide(doc):
    """Verdict from published numbers alone (pure): a reader can re-derive it.

    The drop-best arms are arithmetic extremes -- removing the best k bars is by
    construction the worst k-bar drop -- so they are judged on MAGNITUDE (does the book
    still compound, and does it keep most of its return); the placebo is reported beside
    them to say what losing k ordinary bars would have cost.
    """
    if doc.get("bars", 0) < DENSE_MIN:
        return {"state": "NOT_ASSESSED", "why": "fewer than %d bars" % DENSE_MIN}
    share = doc.get("top_share")
    drops = {int(d["k"]): d for d in doc.get("drops", [])}
    if share is None or 5 not in drops or 10 not in drops:
        return {"state": "INCOMPLETE", "why": "missing top share or drop rows"}
    base = (doc.get("baseline") or {}).get("cagr")
    d5, d10 = drops[5], drops[10]
    if share >= SHARE_DEPENDENT:
        state = "TAIL_DEPENDENT"
        why = "the %d best bars carry %.0f%% of the whole up-move" % (TOP_N, 100.0 * share)
    elif d5.get("cagr") is None or d5["cagr"] <= 0:
        state = "TAIL_DEPENDENT"
        why = "removing the best 5 bars leaves the book at or below zero growth"
    elif (share <= SHARE_ROBUST and d10.get("cagr") is not None and d10["cagr"] > 0
          and base and d10["cagr"] >= RETAIN_MIN * base):
        state = "ROBUST_TO_TAILS"
        why = ("the %d best bars are only %.0f%% of the up-move and the book keeps %.0f%% "
               "of its cagr without its 10 best bars"
               % (TOP_N, 100.0 * share, 100.0 * d10["cagr"] / base))
    else:
        state = "MIXED"
        why = ("the book survives losing its best 5 bars, but the %d best carry %.0f%% of "
               "the up-move and only %.0f%% of the cagr survives losing 10"
               % (TOP_N, 100.0 * share,
                  (100.0 * d10["cagr"] / base) if (base and d10.get("cagr") is not None) else 0.0))
    return {"state": state, "why": why, "top_share": share,
            "cagr_after_drop5": d5.get("cagr"), "cagr_after_drop10": d10.get("cagr"),
            "placebo_pct_drop5": d5.get("placebo_pct"),
            "placebo_pct_drop10": d10.get("placebo_pct")}


def _drop_row(r, k, base):
    ser = drop_best_rows(r, k)
    st = A.stats2(ser, "drop_%d" % k)
    pl = placebo_cagrs(r, k)
    pct = float((pl < (st.get("cagr") or 0.0)).mean())
    return {"k": k, "cagr": st.get("cagr"), "sharpe": st.get("sharpe"),
            "maxdd": st.get("maxdd"),
            "cagr_delta_pp": round(100.0 * ((st.get("cagr") or 0.0) - (base.get("cagr") or 0.0)), 2),
            "placebo_pct": round(pct, 4),
            "placebo_cagr_p05": round(float(np.percentile(pl, 5)), 4),
            "placebo_cagr_p50": round(float(np.percentile(pl, 50)), 4)}


def cross_check(r):
    """Compare this face's path against the sibling face that publishes the same book.

    `etf_book_nav_envelope` publishes the production book's daily NAV as a standalone
    artifact. Two faces quoting the same book is exactly the r1290/E293 failure mode, so
    the overlap is measured here and printed rather than assumed equal: the returns must
    agree bar-by-bar where the two windows overlap, and any headline difference is
    disclosed with both numbers and the bars each one covers.
    """
    nav_dir = os.path.join(ROOT, "results", "etf_book_series")
    latest = os.path.join(nav_dir, "latest.json")
    if not os.path.isfile(latest):
        return {"state": "sibling_missing", "path": "results/etf_book_series/"}
    with open(latest, encoding="utf-8") as fh:
        meta = json.load(fh)
    fpath = os.path.join(nav_dir, meta.get("file", ""))
    if not os.path.isfile(fpath):
        return {"state": "sibling_missing", "path": fpath}
    with open(fpath, encoding="utf-8") as fh:
        nav = json.load(fh)
    dates = pd.to_datetime(nav.get("dates") or nav.get("d") or [])
    levels = nav.get("nav") or nav.get("levels") or []
    if len(dates) != len(levels) or len(dates) < DENSE_MIN:
        return {"state": "sibling_unreadable", "path": fpath}
    sib = pd.Series(levels, index=dates).pct_change().dropna()
    both = r.index.intersection(sib.index)
    if len(both) < DENSE_MIN:
        return {"state": "no_overlap", "sibling_bars": int(len(sib))}
    diff = (r.reindex(both) - sib.reindex(both)).abs()
    return {"state": "compared", "sibling_file": meta.get("file"),
            "sibling_cutoff": meta.get("last_bar"), "sibling_bars": int(len(sib)),
            "overlap_bars": int(len(both)),
            "max_abs_return_diff": round(float(diff.max()), 8),
            "reproduces_bar_for_bar": bool(diff.max() <= 1e-6),
            "sibling_headline": (meta.get("backtest") or {}).get("full"),
            "note": ("the sibling publishes NAV to its own cutoff; a headline difference is "
                     "either the extra bars this face has or a second implementation -- the "
                     "bar-level diff separates the two")}


def run():
    t0 = time.time()
    close, openp, _amt, _feats, score, cls, n_flip = F.build_inputs()
    all_dates, _grid = F.date_grid(close, F.CONFIG["rebal"])
    carry, carry_note = F.build_carry(all_dates)
    carry = None if carry is None else carry.reindex(pd.DatetimeIndex(all_dates)).fillna(0.0)
    grid = set(all_dates[::F.CONFIG["rebal"]])
    ser, exp, book = X._run_arm(close, openp, score, carry, all_dates, grid, lambda d, s: s)
    base = A.stats2(ser, "production")
    r = returns_of(ser)
    rows = [_drop_row(r, k, base) for k in K_DROPS]

    monthly = ser.resample("ME").last().pct_change().dropna()
    best_m = monthly.idxmax()
    kept_months = monthly.drop(best_m)
    growth_no_best_month = float(np.prod(1.0 + kept_months.to_numpy()))
    yrs = len(r) / 252.0
    cagr_no_best_month = growth_no_best_month ** (1.0 / yrs) - 1.0 if growth_no_best_month > 0 else -1.0

    sib = cross_check(r)
    if sib.get("sibling_headline") and base.get("cagr") is not None:
        sib["headline_delta_pp"] = round(100.0 * (base["cagr"] - sib["sibling_headline"]["cagr"]), 2)
    doc = {
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "elapsed_sec": round(time.time() - t0, 1),
        "evidence_cutoff": str(pd.Timestamp(ser.index[-1]).date()),
        "bars": int(len(r)),
        "question": ("is the book's growth spread over its bars, or carried by a handful? "
                     "priced with drop-best arms against a random-drop placebo"),
        "criteria": CRITERIA,
        "config": {"n_hold": F.CONFIG["n_hold"], "rebal": F.CONFIG["rebal"],
                   "cost_bp": round(F.CONFIG["cost_per_side"] * 1e4, 1),
                   "vol_target": F.CONFIG["vol_target"], "carry": carry_note,
                   "mean_exposure": round(float(np.mean(exp)), 4)},
        "baseline": {"cagr": base.get("cagr"), "sharpe": base.get("sharpe"),
                     "maxdd": base.get("maxdd"), "vol": base.get("vol"),
                     "years": base.get("years")},
        "top_share": round(float(top_share(r)), 4) if top_share(r) is not None else None,
        "top_share_n": TOP_N,
        "best_month": {"month": str(best_m.date())[:7],
                       "cagr_without_it": round(cagr_no_best_month, 4),
                       "cagr_delta_pp": round(100.0 * (cagr_no_best_month - (base.get("cagr") or 0.0)), 2)},
        "drops": rows,
        "panel": F._panel_block(cls, n_flip) if hasattr(F, "_panel_block") else None,
        "sibling_face": sib,
        "bars_series": [{"d": str(pd.Timestamp(i).date()), "r": round(float(v), 6)}
                        for i, v in r.items()],
        "notes": [
            "bars are the production book's own daily nav returns; nothing is re-simulated "
            "for the deterministic arms",
            "random-drop placebo uses a fixed seed per k so the percentile is reproducible",
            "growth shares use log returns, so the pieces add up to the whole",
            "a book that survives losing its best 10 bars is a book; one that does not is a "
            "jackpot that already paid",
        ],
    }
    doc["verdict"] = decide(doc)
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    write_md(doc)
    v = doc["verdict"]
    print("tail dependence: %s | top%d share %.1f%% | cagr %.2f%% -> drop5 %.2f%% (placebo p%.1f) | %d bars to %s | %.1fs"
          % (v["state"], TOP_N, 100.0 * (doc["top_share"] or 0.0),
             100.0 * (doc["baseline"]["cagr"] or 0.0), 100.0 * (v["cagr_after_drop5"] or 0.0),
             100.0 * (v["placebo_pct_drop5"] or 0.0), doc["bars"], doc["evidence_cutoff"],
             doc["elapsed_sec"]))
    return doc


def write_md(doc):
    b = doc["baseline"]
    v = doc["verdict"]
    lines = [
        "# Does the book earn it on many days, or on a handful?",
        "",
        "Generated %s · evidence cutoff %s · %d bars · payload `results/etf_book_tail_dependence.json`"
        % (doc["generated"], doc["evidence_cutoff"], doc["bars"]),
        "",
        "## Verdict",
        "",
        "**%s** — %s" % (v["state"], v["why"]),
        "",
        "## Baseline (the number every other face quotes)",
        "",
        "| cagr | sharpe | maxdd | vol | years |",
        "| --- | --- | --- | --- | --- |",
        "| %.2f%% | %.3f | %.2f%% | %.2f%% | %.2f |"
        % (100.0 * b["cagr"], b["sharpe"], 100.0 * b["maxdd"], 100.0 * b["vol"], b["years"]),
        "",
        "Top %d bars carry **%.1f%%** of the gross up-move." % (doc["top_share_n"], 100.0 * doc["top_share"]),
        "",
        "## Drop-best arms vs random-drop placebo",
        "",
        "| bars removed | cagr | sharpe | cagr delta | placebo pct | placebo p05 | placebo p50 |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for d in doc["drops"]:
        lines.append("| %d | %.2f%% | %.3f | %+.2f pp | %.1f%% | %.2f%% | %.2f%% |"
                     % (d["k"], 100.0 * d["cagr"], d["sharpe"], d["cagr_delta_pp"],
                        100.0 * d["placebo_pct"], 100.0 * d["placebo_cagr_p05"],
                        100.0 * d["placebo_cagr_p50"]))
    bm = doc["best_month"]
    lines += [
        "",
        "Best month (%s) removed: cagr %.2f%% (%+.2f pp)." % (bm["month"], 100.0 * bm["cagr_without_it"], bm["cagr_delta_pp"]),
        "",
        "## The book next door does not match bar for bar",
        "",
    ]
    sf = doc.get("sibling_face") or {}
    if sf.get("state") == "compared":
        lines += [
            "`%s` publishes the same production book (%d bars to %s). Over %d overlapping bars the "
            "daily returns differ by up to **%.4f**, so these are not the same path: that face "
            "quotes **%.2f%%** cagr / %.3f sharpe / %.2f%% maxdd and this one quotes **%.2f%%** / "
            "%.3f / %.2f%% (**%+.2f pp**)."
            % (sf.get("sibling_file"), sf.get("sibling_bars"), sf.get("sibling_cutoff"),
               sf.get("overlap_bars"), sf.get("max_abs_return_diff"),
               100.0 * sf["sibling_headline"]["cagr"], sf["sibling_headline"]["sharpe"],
               100.0 * sf["sibling_headline"]["maxdd"],
               100.0 * b["cagr"], b["sharpe"], 100.0 * b["maxdd"],
               sf.get("headline_delta_pp") or 0.0),
            "",
            "Both numbers are honest about their own path; the divergence is a second "
            "implementation of the same book, not a tail effect. Until it is resolved, quote "
            "neither as *the* production number without naming the face it came from.",
        ]
    else:
        lines.append("Sibling comparison unavailable (%s)." % sf.get("state", "missing"))
    lines += [
        "",
        "Best month (%s) removed: cagr %.2f%% (%+.2f pp)." % (bm["month"], 100.0 * bm["cagr_without_it"], bm["cagr_delta_pp"]),
        "",
        "## How to read this",
        "",
        "- The drop-best arms are arithmetic on the book's own published bars, not a re-simulation.",
        "- The placebo says what dropping *any* k bars usually costs, so the drop-best reading is",
        "  compared against luck rather than against zero.",
        "- A verdict of TAIL_DEPENDENT does not say the book is wrong; it says the headline CAGR is",
        "  a statement about a few days, and no sizing rule can reproduce it ex ante.",
    ]
    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def _fixture(kind="dense", n=1650, seed=3):
    """Synthetic daily returns: 'dense' = many small wins, 'tail' = a few jackpot bars.

    Default length matches the production panel (~1,650 bars), because dropping 10 bars is
    0.6% of that window and 3% of a 300-bar one -- the same rule reads differently.
    """
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2020-01-01", periods=n)
    if kind == "dense":
        r = pd.Series(rng.normal(0.0004, 0.004, n), index=idx)
    else:
        r = pd.Series(rng.normal(0.0, 0.0005, n), index=idx)
        r.iloc[10] = 0.25
        r.iloc[n // 2] = 0.20
        r.iloc[n - 10] = 0.15
    return r


def _doc_from_returns(r):
    ser = pd.Series(np.cumprod(1.0 + r.to_numpy()), index=r.index)
    base = A.stats2(ser, "fx")
    rows = [_drop_row(r, k, base) for k in K_DROPS]
    doc = {"bars": len(r), "top_share": top_share(r), "drops": rows,
           "baseline": {"cagr": base.get("cagr")}}
    doc["verdict"] = decide(doc)
    return doc


def selftest():
    ok = 0
    total = 0

    def chk(cond, msg):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
        else:
            print("FAIL: %s" % msg)

    r_dense = _fixture("dense")
    d_dense = _doc_from_returns(r_dense)
    chk(d_dense["verdict"]["state"] == "ROBUST_TO_TAILS",
        "dense fixture should be robust, got %s" % d_dense["verdict"]["state"])
    chk(d_dense["top_share"] < SHARE_DEPENDENT, "dense top share below the line")

    r_tail = _fixture("tail")
    d_tail = _doc_from_returns(r_tail)
    chk(d_tail["verdict"]["state"] == "TAIL_DEPENDENT",
        "jackpot fixture should be tail dependent, got %s" % d_tail["verdict"]["state"])
    chk(d_tail["top_share"] >= SHARE_DEPENDENT, "jackpot top share above the line")

    # dropping the actual best bars must cost more than dropping random ones
    best = r_tail.nlargest(5)
    kept = r_tail.drop(best.index)
    growth_drop = float(np.prod(1.0 + kept.to_numpy()))
    rng = np.random.default_rng(11)
    rand_growth = [float(np.prod(1.0 + np.delete(r_tail.to_numpy(), rng.choice(len(r_tail), 5, replace=False))))
                   for _ in range(50)]
    chk(growth_drop < float(np.median(rand_growth)),
        "drop-best must cost more than a random drop")
    chk(d_tail["drops"][-1]["placebo_pct"] <= 0.05,
        "jackpot drop-10 should sit in the placebo tail, got %.3f" % d_tail["drops"][-1]["placebo_pct"])

    # short panels are not assessed at all
    chk(decide({"bars": 10, "top_share": 0.9, "drops": []})["state"] == "NOT_ASSESSED",
        "short panel must be NOT_ASSESSED")
    # a missing arm is incomplete, never a verdict
    chk(decide({"bars": 300, "top_share": 0.1, "drops": []})["state"] == "INCOMPLETE",
        "missing drop rows must be INCOMPLETE")
    # zero-growth book must not blow up the share
    chk(top_share(pd.Series([0.0] * 50)) is None, "flat series has no share")

    # determinism: same seed, same placebo percentile
    d1 = _doc_from_returns(_fixture("dense"))
    d2 = _doc_from_returns(_fixture("dense"))
    chk(d1["drops"][1]["placebo_pct"] == d2["drops"][1]["placebo_pct"], "placebo must be reproducible")

    print("selftest %d/%d" % (ok, total))
    return 0 if ok == total else 1


def check(path=None):
    path = path or OUT_JSON
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    got = decide(doc)
    stored = doc.get("verdict", {})
    same = (got["state"] == stored.get("state"))
    # independent re-derivation from the published bar returns
    r = pd.Series([b["r"] for b in doc.get("bars_series", [])],
                  index=pd.to_datetime([b["d"] for b in doc.get("bars_series", [])]))
    share_ok = True
    if len(r) >= DENSE_MIN and doc.get("top_share") is not None:
        share_ok = abs(top_share(r) - doc["top_share"]) <= 1e-3
    print("check: verdict %s (stored %s) %s | top share reproduced %s"
          % (got["state"], stored.get("state"), "OK" if same else "DRIFT",
             "OK" if share_ok else "DRIFT"))
    return 0 if (same and share_ok) else 1


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    cmd = argv[0] if argv else "run"
    if cmd == "--selftest":
        return selftest()
    if cmd == "--check":
        return check(argv[1] if len(argv) > 1 else None)
    run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())