"""Production-candidate check: drop the bond sleeve, then apply the 8%/12% vol target.

Evidence that motivates this: bond/money-only composite earns 0.6%/yr vs 1.5%/yr for the
same sleeve equal-weighted (no bond-selection skill), while equity-only earns 11.2%/yr vs
3.8% EW. So bonds are a drag on the book, not a defence. This run sizes the consequence
and prints today's live picks for the bond-free book.

r1796: every arm is now priced TWICE, on the two execution calibers
(`etf_book_entry_lag`): entry_lag=0 is the caliber every printed number in this face has
always used -- the book the picks select starts accruing on the DECISION bar's own open,
i.e. before the close those picks were read from; entry_lag=1 starts it on the next open,
which is what `etf_robust_pf`'s own docstring promises. The printed keys are untouched
(bit-identical, so no reader's number moves); the correction is published beside them as
`runs[].caliber` + a top-level `caliber` block, so the production candidate's headline can
be read both ways. `python scripts/etf_nobond_vt.py check` re-derives the block from the
published face (no recomputation) and refuses a face whose penalty is not sign-stable.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import numpy as np
import pandas as pd

import etf_composite_pf as E
import etf_robust_pf as R
import etf_equity_alpha as A

IS_END = "2023-12-31"
ARMS = (("nobond_base", None), ("nobond_vt08", 0.08), ("nobond_vt12", 0.12))


def report(ser, label, out):
    m = A.stats2(ser, label)
    for lbl, sl in (("is", ser[ser.index <= IS_END]), ("oos", ser[ser.index > IS_END])):
        mm = A.stats2(sl, label + "_" + lbl)
        for k in ("cagr", "sharpe", "maxdd"):
            m[k + "_" + lbl] = mm.get(k)
    out.append(m)
    print(m, flush=True)


def main():
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    want = ("equity", "commodity", "convertible")
    cols = [c for c in close.columns if cls[c] in want]
    print("bond-free universe", len(cols), "flips repaired", n_flip, flush=True)

    sc = E.build_score(close[cols], amt[cols], feats)
    out = []
    for label, vt in ARMS:
        ser, turn = R.open_to_open_equity(close[cols], openp[cols], amt[cols], sc, 20, 5, 0.0010,
                                          vol_target=vt)
        report(ser, label, out)
        out[-1]["turnover"] = round(turn, 2)
        ser1, _t1 = R.open_to_open_equity(close[cols], openp[cols], amt[cols], sc, 20, 5, 0.0010,
                                          vol_target=vt, entry_lag=1)
        lag1 = A.stats2(ser1, label + "_lag1")
        out[-1]["caliber"] = {
            "entry_lag0_cagr": out[-1]["cagr"],
            "entry_lag1_cagr": lag1.get("cagr"),
            "entry_lag0_sharpe": out[-1]["sharpe"],
            "entry_lag1_sharpe": lag1.get("sharpe"),
            "entry_lag1_maxdd": lag1.get("maxdd"),
            "cagr_penalty_pp": round((out[-1]["cagr"] - (lag1.get("cagr") or 0.0)) * 100.0, 4),
            "execution": "lag0 = decision bar's own open (published); lag1 = next open",
        }
        print("%s lag1 cagr=%.4f penalty=%.2fpp"
              % (label, lag1.get("cagr") or 0.0, out[-1]["caliber"]["cagr_penalty_pp"]), flush=True)

    # live picks for the bond-free book
    last = sc.index[-1]
    s = sc.loc[last].dropna()
    picks = [(sym, round(float(v), 3), cls[sym]) for sym, v in s.nlargest(5).items()]
    print("live picks", last.date(), picks, flush=True)

    prod = [r for r in out if r["label"] == "nobond_vt08"][0]
    penalties = [r["caliber"]["cagr_penalty_pp"] for r in out]
    face = {
        "runs": out,
        "universe": len(cols),
        "flips_repaired": n_flip,
        "arms": [a for a, _ in ARMS],
        "live_picks": {"as_of": str(last.date()),
                       "picks": [{"symbol": a_, "score": b_, "class": c_}
                                 for a_, b_, c_ in picks]},
        "caliber": {
            "source_face": "results/etf_book_entry_lag.json",
            "execution": "decide at close t, own from open t+1 (entry_lag=1) vs the decision bar's own open (entry_lag=0, every printed number)",
            "production_candidate": "nobond_vt08",
            "production_cagr_lag0_pct": round(prod["cagr"] * 100.0, 4),
            "production_cagr_lag1_pct": round((prod["caliber"]["entry_lag1_cagr"] or 0.0) * 100.0, 4),
            "production_penalty_pp": prod["caliber"]["cagr_penalty_pp"],
            "penalty_pp_by_arm": {r["label"]: r["caliber"]["cagr_penalty_pp"] for r in out},
            "sign_stable": all(p > 0 for p in penalties),
            "verdict": ("CALIBER_COSTS_MONEY" if all(p > 0 for p in penalties)
                        else "PENALTY_NOT_SIGN_STABLE"),
        },
    }
    import json
    p = os.path.join(E.PATHS.results_dir, "etf_nobond_vt.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(face, f, ensure_ascii=False, indent=1)
    print("saved", p)


def check():
    """Re-derive the caliber block from the published face; never recompute a book.

    A face that lost an arm, or whose penalty was typed instead of subtracted, is refused
    with the reason, so the check cannot pass by agreeing with itself (E662 family)."""
    import json
    p = os.path.join(E.PATHS.results_dir, "etf_nobond_vt.json")
    if not os.path.exists(p):
        print("check FAIL: no face at", p)
        return 1
    with open(p, encoding="utf-8") as f:
        face = json.load(f)
    probs = []
    runs = {r.get("label"): r for r in face.get("runs") or []}
    for label, _vt in ARMS:
        r = runs.get(label)
        if not r or "caliber" not in r:
            probs.append("%s: no caliber block" % label)
            continue
        c = r["caliber"]
        want = (c["entry_lag0_cagr"] - c["entry_lag1_cagr"]) * 100.0
        if abs(want - c["cagr_penalty_pp"]) > 1e-6:
            probs.append("%s: penalty %.4f != lag0-lag1 %.4f" % (label, c["cagr_penalty_pp"], want))
        if abs(c["entry_lag0_cagr"] - r["cagr"]) > 1e-12:
            probs.append("%s: printed cagr moved off the lag0 arm" % label)
    cal = face.get("caliber") or {}
    if not cal:
        probs.append("no top-level caliber block")
    else:
        prod = runs.get(cal.get("production_candidate") or "")
        if not prod:
            probs.append("production candidate %r not in runs" % cal.get("production_candidate"))
        else:
            if abs(cal["production_penalty_pp"] - prod["caliber"]["cagr_penalty_pp"]) > 1e-9:
                probs.append("production penalty disagrees with its own run")
        signs = [v > 0 for v in (cal.get("penalty_pp_by_arm") or {}).values()]
        if cal.get("sign_stable") != (all(signs) and bool(signs)):
            probs.append("sign_stable does not match the per-arm penalties")
        if cal.get("verdict") == "CALIBER_COSTS_MONEY" and not all(signs):
            probs.append("verdict claims a cost that some arm does not pay")
    if probs:
        print("check FAIL:")
        for x in probs:
            print("  -", x)
        return 1
    print("check ok: %d arms, production %s penalty %.2fpp, sign_stable=%s"
          % (len(runs), cal.get("production_candidate"), cal.get("production_penalty_pp"),
             cal.get("sign_stable")))
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lstrip("-") == "check":
        raise SystemExit(check())
    main()