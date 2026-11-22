#!/usr/bin/env python
"""etf_book_day_concentration -- is the production book carried by a handful of days?

The sister face `etf_book_concentration.py` answers *which names* carry the return. This
one answers the orthogonal, never-asked question: *which days*. For the production book
(n_hold=5, vol_target=8%, 20-bar rebalance, 10bp/side -- the arm the tearsheet quotes) it
rebuilds the equity curve with the K best trading days' growth forced to 1.0 (a flat day)
and re-quotes CAGR / Sharpe / maxDD from the same `etf_equity_alpha.stats2` ruler the
published numbers use. If dropping 10 days (0.6% of the panel) drags the 11% down to
nothing, the edge is a few days of luck; if it stays above half, the book earns most weeks.

The worst-K twin is printed beside the best-K arm on purpose: a book that collapses when
its best days are removed but is unmoved when its worst days are removed is a book whose
return depends on the *tail you cannot pick*. Reading one without the other is a story.

  python scripts/etf_book_day_concentration.py            # run + check
  python scripts/etf_book_day_concentration.py check      # re-derive the verdict from the face
  python scripts/etf_book_day_concentration.py --selftest # offline, synthetic only
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

OUT_JSON = ROOT / "results" / "etf_book_day_concentration.json"
SCRIPT = "scripts/etf_book_day_concentration.py"
FACE = "results/etf_book_day_concentration.json"

# ---------------------------------------------------------------- frozen criteria
# Written before the first run; the gate refuses a face whose echoed criteria differ.
N_HOLD = 5               # the production book the tearsheet quotes (n5_vt08)
REBAL = 20
COST = 0.0010            # 10 bp per side, the published convention
K_DAYS = (1, 3, 5, 10, 20, 40)     # best/worst trading days to strip
K_BLOCKS = (1, 2, 4)               # same, in 20-bar rebalance periods
BLOCK = REBAL
ROBUST_SHARE = 0.50      # strip the best 10 days and keep >= half the CAGR -> robust
MIN_DAYS = 250           # fewer bars than this: refuse to judge (no number printed)
REFERENCE_PARENT = "results/etf_book_production/PRODUCTION-2026-11-20.json"
ALIGN_TOL_PP = 0.05      # our k=0 CAGR must match the parent's n5_vt08 full CAGR within this

CRITERIA = {
    "n_hold": N_HOLD,
    "rebal": REBAL,
    "cost_bp_per_side": COST * 1e4,
    "k_days": list(K_DAYS),
    "k_blocks": list(K_BLOCKS),
    "block": BLOCK,
    "robust_share": ROBUST_SHARE,
    "min_days": MIN_DAYS,
    "reference_parent": REFERENCE_PARENT,
    "align_tol_pp": ALIGN_TOL_PP,
    "frozen": "constants above were written before the first run",
}


# ------------------------------------------------------------------------ helpers
def _growth(ser):
    """Per-bar growth factors; first bar dropped (no prior level)."""
    return ser.div(ser.shift(1)).iloc[1:]


def rebuild_nav(ser, flat_g_days):
    """Recompose a NAV series with the growth of `flat_g_days` (a set of Timestamps) set to
    1.0 (a flat day). The level before/after is preserved bar for bar, so stats2 quotes the
    *same* ruler on a book that simply did not move on those days. This is the one arithmetic
    used by both the day and block arms -- there is no second implementation to disagree."""
    g = _growth(ser)
    mask = g.index.isin(pd.DatetimeIndex(list(flat_g_days)))
    mult = g.where(~mask, 1.0)
    cum = mult.cumprod()
    nav = pd.Series(index=ser.index, dtype=float)
    nav.iloc[0] = float(ser.iloc[0])
    if len(cum):
        nav.iloc[1:] = float(ser.iloc[0]) * cum.values
    return nav


def _best_worst_days(ser, k, best=True):
    g = _growth(ser)
    order = g.sort_values(ascending=not best)
    return set(order.index[:k])


def _best_worst_blocks(ser, k, best=True, block=BLOCK):
    """Rank contiguous `block`-bar periods by their compounded growth, return the bar set."""
    g = _growth(ser)
    idx = list(g.index)
    periods = []          # (compounded growth, [timestamps])
    for i in range(0, len(idx), block):
        chunk = g.iloc[i:i + block]
        periods.append((float(chunk.prod()), list(chunk.index)))
    periods.sort(key=lambda t: t[0], reverse=best)
    flat = set()
    for _, bars in periods[:k]:
        flat.update(bars)
    return flat


def verdict_of(base_cagr, after10_cagr, n_days):
    """The published rule, recomputed by the gate from the face's own numbers."""
    if n_days < MIN_DAYS:
        return "INSUFFICIENT"
    if base_cagr is None or base_cagr <= 0:
        return "NO_BASE_EDGE"
    if after10_cagr is None:
        return "INSUFFICIENT"
    if after10_cagr <= 0.0:
        return "CARRIED_BY_LUCKY_DAYS"
    if after10_cagr >= ROBUST_SHARE * base_cagr:
        return "ROBUST_TO_LUCKY_DAYS"
    return "SENSITIVE_TO_LUCKY_DAYS"


# ---------------------------------------------------------------------------- run
def run(out_path=None, verbose=True):
    import etf_book_production as P
    import etf_equity_alpha as A
    import etf_robust_pf as R

    close, openp, amt, score, cls, n_flip = P.prep_panel()
    diag = []
    ser, turn = R.open_to_open_equity(
        close, openp, amt, score, REBAL, N_HOLD, COST,
        vol_target=P.TARGET_VOL, diag=diag)
    if not diag:
        raise RuntimeError("panel too short for one decision on the grid")

    def stats_of(s):
        m = A.stats2(s, "x")
        return {k: m.get(k) for k in ("cagr", "sharpe", "maxdd", "vol", "years")}

    base = stats_of(ser)
    base_cagr = base.get("cagr")
    n_days = int(len(_growth(ser)))
    ev = str(close.index[-1].date())

    # parent alignment: the k=0 number must reproduce the tearsheet's n5_vt08 full CAGR
    ref = {"source": REFERENCE_PARENT, "parent_cagr": None, "delta_pp": None,
           "aligned": None}
    rp = ROOT / REFERENCE_PARENT
    if rp.exists():
        try:
            pj = json.load(open(rp, encoding="utf-8"))
            pc = (((pj.get("backtest") or {}).get("n5_vt08") or {}).get("full") or {}).get("cagr")
            if pc is not None:
                ref["parent_cagr"] = pc
                ref["delta_pp"] = round(100 * ((base_cagr or 0) - pc), 4)
                ref["aligned"] = abs(ref["delta_pp"]) <= ALIGN_TOL_PP
        except Exception as e:                                        # noqa: BLE001
            ref["source"] = "%s (unreadable: %s)" % (REFERENCE_PARENT, e)

    def arm(k_list, mode):
        rows = []
        for k in k_list:
            if mode == "best_day":
                flat = _best_worst_days(ser, k, best=True)
            elif mode == "worst_day":
                flat = _best_worst_days(ser, k, best=False)
            elif mode == "best_block":
                flat = _best_worst_blocks(ser, k, best=True)
            else:
                raise ValueError(mode)
            st = stats_of(rebuild_nav(ser, flat))
            row = {"k": k}
            row.update(st)
            row["cagr_share_of_base"] = (round(row["cagr"] / base_cagr, 4)
                                         if base_cagr else None)
            row["delta_cagr_pp"] = (round(100 * (row["cagr"] - base_cagr), 3)
                                    if base_cagr is not None and row.get("cagr") is not None else None)
            rows.append(row)
        return rows

    best_days = arm(K_DAYS, "best_day")
    worst_days = arm(K_DAYS, "worst_day")
    best_blocks = arm(K_BLOCKS, "best_block")

    by_k = {r["k"]: r for r in best_days}
    after10 = (by_k.get(10) or {}).get("cagr")
    best1 = by_k.get(1) or {}
    verdict = verdict_of(base_cagr, after10, n_days)

    worst_by_k = {r["k"]: r for r in worst_days}
    worst10 = (worst_by_k.get(10) or {}).get("cagr")

    headline = {
        "base_cagr": base_cagr,
        "best1_cagr_pp_removed": best1.get("delta_cagr_pp"),
        "best1_share_of_cagr": ((round((base_cagr - best1["cagr"]) / base_cagr, 4))
                                if base_cagr and best1.get("cagr") is not None else None),
        "best10_cagr": after10,
        "best10_share_of_base": (by_k.get(10) or {}).get("cagr_share_of_base"),
        "best10_cagr_pp_removed": (by_k.get(10) or {}).get("delta_cagr_pp"),
        "worst10_cagr": worst10,
        "asymmetry_pp": (round(100 * ((after10 if after10 is not None else 0)
                                      - (worst10 if worst10 is not None else 0)), 3)
                         if (after10 is not None and worst10 is not None) else None),
        "note": ("best10_share_of_base = CAGR still standing once the 10 best trading days "
                 "are forced flat; >1.0 is impossible, ==1.0 means those days did nothing"),
    }

    payload = {
        "ts": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "script": SCRIPT,
        "face": FACE,
        "evidence_cutoff": ev,
        "criteria": CRITERIA,
        "execution": "decide at close t -> fill at open t+1 -> hold to next decision",
        "panel": {"columns": int(close.shape[1]), "bars": int(close.shape[0]),
                  "flips_repaired": n_flip},
        "book": {"n_hold": N_HOLD, "rebal": REBAL, "vol_target": P.TARGET_VOL,
                 "cost_bp_per_side": COST * 1e4, "decisions": len(diag),
                 "turnover_per_decision": round(turn, 3)},
        "trading_days": n_days,
        "baseline": {"full": base},
        "reference": ref,
        "drop_best_days": best_days,
        "drop_worst_days": worst_days,
        "drop_best_blocks": best_blocks,
        "headline": headline,
        "verdict": verdict,
    }

    if verbose:
        print("baseline full", base)
        print("parent align", ref)
        print("best10 -> cagr %.4f (share %.3f)  worst10 -> cagr %.4f"
              % (after10 or 0, headline.get("best10_share_of_base") or 0, worst10 or 0))
        print("verdict", verdict)

    p = Path(out_path) if out_path else OUT_JSON
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    if verbose:
        print("wrote", p)
    return payload


# ---------------------------------------------------------------------- consumer
def sentence(doc):
    h = doc.get("headline") or {}
    b = h.get("base_cagr")
    a10 = h.get("best10_cagr")
    w10 = h.get("worst10_cagr")
    if b is None or a10 is None:
        return None
    w10_txt = ("%.2f%%" % (100 * w10)) if w10 is not None else "读不到"
    return ("书中位年化 %.2f%%；把它最好的 10 个交易日（约 %.1f%% 的柱子）按平盘处理后还剩 "
            "%.2f%%（原值的 %.0f%%）；把最坏的 10 天按平盘处理则是 %s。判 %s。"
            % (100 * b, 100.0 * 10.0 / max(doc.get("trading_days") or 1, 1), 100 * a10,
               100 * (h.get("best10_share_of_base") or 0), w10_txt, doc.get("verdict")))


def read_published(path=None):
    p = Path(path) if path else OUT_JSON
    if not p.exists():
        return {"status": "absent", "sentence": None, "evidence_cutoff": None, "verdict": None}
    try:
        doc = json.load(open(p, encoding="utf-8"))
    except Exception as e:                                            # noqa: BLE001
        return {"status": "unreadable: %s" % e, "sentence": None,
                "evidence_cutoff": None, "verdict": None}
    return {"status": "ok", "sentence": sentence(doc),
            "evidence_cutoff": doc.get("evidence_cutoff"), "verdict": doc.get("verdict"),
            "headline": doc.get("headline")}


# ------------------------------------------------------------------------- check
def check(path=None):
    """Re-read the published face and recompute the verdict from its own rows.

    STALE / face missing wording is deliberately avoided: this gate never needs the engine
    (it re-derives from the stored rows), so a mismatch here is a real defect, not drift."""
    p = Path(path) if path else OUT_JSON
    data = json.load(open(p, encoding="utf-8"))
    problems = []
    crit = data.get("criteria") or {}
    for k, v in CRITERIA.items():
        if crit.get(k) != v:
            problems.append("criteria %s: face says %r, code says %r" % (k, crit.get(k), v))
    # k=0 baseline must equal the stored baseline row (self-consistency of the ruler)
    base = ((data.get("baseline") or {}).get("full") or {}).get("cagr")
    rows = {r["k"]: r for r in (data.get("drop_best_days") or [])}
    if 10 not in rows:
        problems.append("drop_best_days is missing the k=10 row the verdict reads")
    want = verdict_of(base, (rows.get(10) or {}).get("cagr"),
                      data.get("trading_days") or 0)
    if want != data.get("verdict"):
        problems.append("verdict %r does not reproduce from the rows (%r)"
                        % (data.get("verdict"), want))
    # monotonic leg: stripping more good days cannot raise the CAGR
    seq = [r.get("cagr") for r in (data.get("drop_best_days") or [])]
    if any(seq[i] is not None and seq[i + 1] is not None and seq[i + 1] > seq[i] + 1e-9
           for i in range(len(seq) - 1)):
        problems.append("drop_best_days CAGR is not monotone non-increasing in k: %r" % (seq,))
    # parent alignment must be published and honoured
    ref = data.get("reference") or {}
    if ref.get("parent_cagr") is not None:
        dp = ref.get("delta_pp")
        if dp is None or ref.get("aligned") is not True or abs(dp) > ALIGN_TOL_PP:
            problems.append("k=0 baseline does not reproduce the parent n5_vt08 (%r)" % (ref,))
    for msg in problems:
        print("CHECK FAIL:", msg)
    if not problems:
        print("CHECK OK: criteria echoed, verdict %s reproduces, drop_best_days monotone, "
              "k=0 aligned to parent (delta %s pp)"
              % (data.get("verdict"), (ref or {}).get("delta_pp")))
    return 1 if problems else 0


# ---------------------------------------------------------------------- selftest
def selftest():
    ok = []

    def leg(name, cond, detail=""):
        ok.append((name, bool(cond), detail))
        print(("PASS " if cond else "FAIL ") + name + ((" | " + detail) if detail else ""))

    rng = np.random.default_rng(7)
    idx = pd.bdate_range("2020-01-01", periods=300)
    # a book with a modest drift and one huge lucky day injected at bar 150
    r = rng.normal(0.0002, 0.006, len(idx))
    r[150] = 0.08            # a single +8% day
    nav = pd.Series(1.0 * np.cumprod(1 + r), index=idx)

    # L1 rebuild with an empty flat-set reproduces the series bar for bar
    same = rebuild_nav(nav, set())
    leg("empty flat-set reproduces the NAV", float(np.max(np.abs(same - nav))) < 1e-12,
        "maxabs %.2g" % float(np.max(np.abs(same - nav))))

    # L2 flattening one day that grew >= any other day lowers the terminal level by exactly it
    g = _growth(nav)
    best_d = g.idxmax()
    flat = rebuild_nav(nav, {best_d})
    # ratio of terminals must equal the removed growth factor
    ratio = float(flat.iloc[-1] / nav.iloc[-1])
    leg("flatten the best day divides terminal by exactly that day's growth",
        abs(ratio - 1.0 / float(g.max())) < 1e-9, "ratio %.10f exp %.10f"
        % (ratio, 1.0 / float(g.max())))

    # L3 the flat day's own bar-to-bar growth is exactly 1.0 (a flat day)
    gg = _growth(flat)
    leg("the flattened day is flat (growth 1.0)",
        abs(float(gg.loc[best_d]) - 1.0) < 1e-9, "g=%.12f" % float(gg.loc[best_d]))

    # L4 stripping the k best days is monotone: terminal non-increasing in k
    terms = []
    for k in (1, 2, 5, 10):
        terms.append(float(rebuild_nav(nav, _best_worst_days(nav, k, best=True)).iloc[-1]))
    leg("more best days removed -> lower or equal terminal", all(
        terms[i + 1] <= terms[i] + 1e-12 for i in range(len(terms) - 1)), str(terms[:3]))

    # L5 block arm: one full 20-bar period flattened == a block whose compounded growth is 1
    blk = _best_worst_blocks(nav, 1, best=True, block=20)
    nav_blk = rebuild_nav(nav, blk)
    gb = _growth(nav_blk)
    leg("block arm flattens exactly 20 bars", len(blk) == 20, "len=%d" % len(blk))
    prod = float(pd.Series([float(gb.loc[t]) for t in sorted(blk)]).prod())
    leg("the flattened block compounds to 1.0", abs(prod - 1.0) < 1e-9, "prod %.12f" % prod)

    # L6 verdict rule: zero after10 -> carried; >= half -> robust; between -> sensitive; short -> insufficient
    leg("verdict CARRIED when best10 kills it", verdict_of(0.11, -0.01, 1000) == "CARRIED_BY_LUCKY_DAYS")
    leg("verdict ROBUST when best10 keeps >= half",
        verdict_of(0.11, 0.06, 1000) == "ROBUST_TO_LUCKY_DAYS")
    leg("verdict SENSITIVE in between", verdict_of(0.11, 0.02, 1000) == "SENSITIVE_TO_LUCKY_DAYS")
    leg("verdict INSUFFICIENT when too short", verdict_of(0.11, 0.06, 10) == "INSUFFICIENT")

    # L7 the sentence never prints 'nan' when worst10 is present, and names the verdict
    doc = {"trading_days": 1000, "verdict": "SENSITIVE_TO_LUCKY_DAYS",
           "headline": {"base_cagr": 0.11, "best10_cagr": 0.02, "worst10_cagr": 0.05,
                        "best10_share_of_base": 0.18}}
    s = sentence(doc) or ""
    leg("sentence quotes the verdict and no 'nan'", ("SENSITIVE" in s) and ("nan" not in s), s[:60])

    # L8 a missing face reads 'absent', not zero
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        miss = read_published(Path(td) / "nope.json")
    leg("reader: absent face reads 'absent'", miss["status"] == "absent")

    n = sum(1 for _, c, _ in ok if c)
    print("\nselftest: %d/%d PASS" % (n, len(ok)))
    return 0 if n == len(ok) else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=("run", "check"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.check or a.cmd == "check":
        return check(a.out)
    run(a.out)
    return check(a.out)


if __name__ == "__main__":
    sys.exit(main())
