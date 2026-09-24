"""O-20260924-1600 CEO order: current-market fitness slice.

Registered traders re-run from the FIRST 2026 TRADING DAY (data-verified
2026-01-05 per bm-c o1600_slice_preconditions.json) to evidence cutoff
(2026-09-23). Report: window return, max drawdown, trade count, vs
passive EW48 holding over the same window. Default cost face (13bp,
registration caliber). Zero new engine code -- live/paper.py anchoring
pipeline reused verbatim (SIGNAL_BUILDERS/ExitPatch/run_backtest window
semantics). Report-only measurement: zero registration claims, ledger
reconciliation deferred to the T-22 owning machine (bm-b claim).
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd

import live.paper as LP


def run() -> dict:
    prices_full = LP.load_core()
    P = LP.build_panels(prices_full)
    idx = P["close"].index
    start = None
    for d in idx:
        if d >= pd.Timestamp("2026-01-05"):
            start = d
            break
    cutoff = idx[-1]
    assert start is not None, "no bars >= 2026-01-05"

    # passive EW48 same-window reference
    wmask = (idx >= start)
    closes = P["close"].loc[wmask]
    rets = closes.pct_change(fill_method=None).iloc[1:]
    passive = float((1.0 + rets.mean(axis=1)).prod() - 1.0)

    rows = []
    roster = sorted(
        f for f in os.listdir(os.path.join(LP.PATHS.roster_dir, ".."))
        if False)  # placeholder removed below
    import glob
    tdir = os.path.join(os.path.dirname(__file__), "..", "firm", "traders")
    files = [f for f in sorted(glob.glob(os.path.join(tdir, "*.json")))
             if "_template" not in f]
    for fp in files:
        t = json.load(open(fp, encoding="utf-8"))
        if t.get("status") in ("retired", "fired"):
            continue
        t2 = dict(t)
        t2["created"] = str(start.date())  # virtual hire on first 2026 bar
        r = LP.paper_run(t2, prices_full, P)
        eq = r.get("equity")
        if eq is None or len(eq) < 5:
            rows.append({"id": t["id"], "bars": r.get("bars", 0),
                         "note": "insufficient window"})
            continue
        total = float(eq.iloc[-1] / eq.iloc[0] - 1.0)
        dd = float((eq / eq.cummax() - 1.0).min())
        n_tr = len(r.get("trades") or [])
        rows.append({
            "id": t["id"], "bars": int(r["bars"]),
            "ret_pct": round(total * 100, 2),
            "dd_pct": round(dd * 100, 2),
            "trades": n_tr,
            "beat_passive": bool(total > passive),
            "sharpe": round(float(r["metrics"].get("sharpe", 0.0)), 3)
            if r.get("metrics") else None,
        })

    out = {
        "order": "O-20260924-1600",
        "start": str(start.date()), "end": str(cutoff.date()),
        "passive_ew48_ret_pct": round(passive * 100, 2),
        "traders": rows,
        "report_only": True,
        "ledger_note": "measurement slice; accounting lands with T-22 (bm-b)",
    }
    op = os.path.join("results", "shortline", "o1600_market_fit.json")
    with open(op, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"window {out['start']} -> {out['end']}")
    print(f"passive EW48: {out['passive_ew48_ret_pct']}%")
    for r in rows:
        if "note" in r:
            print(f"{r['id']}: {r['note']}")
        else:
            beat = "BEAT" if r["beat_passive"] else "LOST"
            print(f"{r['id']}: ret {r['ret_pct']}% dd {r['dd_pct']}% "
                  f"trades {r['trades']} sharpe {r['sharpe']} [{beat}]")
    return out


if __name__ == "__main__":
    run()
