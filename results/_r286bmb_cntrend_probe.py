"""r286 bm-b probe: CN-TREND-ETF-P1 int64 dump crash face verification.

01:10:01 launch crashed at the per-cell checkpoint json.dump (np.int64
'leg' in transitions_head, judged face x2 collect=True only). Fix =
_jsonable coercion. This probe re-runs the exact crash face on REAL
panel data (MA_BASE/x2), writes the legit checkpoint pair the pool
runner reuses idempotently, and round-trips the JSON.
Output: results/_r286bmb_cntrend_probe.json (dict top, r276 law).
"""
import json
import os
import sys
import time
from datetime import datetime

sys.path.insert(0, "scripts")
import numpy as np                      # noqa: E402
import cn_trend_etf_p1 as mod           # noqa: E402

OUT = "results/_r286bmb_cntrend_probe.json"


def main():
    t0 = time.time()
    cell = next(c for c in mod.CELLS if c["name"] == "MA_BASE")
    P, gates = mod.load_panel()
    if P is None:
        json.dump({"probe": "r286 cntrend int64 crash-face", "status":
                   "FAIL", "reason": "load_panel returned None"},
                  open(OUT, "w"), ensure_ascii=False, indent=1)
        return 2
    enter_ev, exit_ev = mod.cell_events(P, cell)
    rec = mod.run_portfolio(P, enter_ev, exit_ev,
                             invvol=cell.get("invvol", False),
                             trail=cell.get("trail", False),
                             cost_fn=mod.FACES["x2"],
                             collect=True)
    assert rec["t1_ok"], "T+1 violation on probe cell"
    blob = {"series": rec["returns"],
            "stats": mod.cell_stats(rec["returns"], P["idx"]),
            "n_trades": rec["n_trades"],
            "n_entries": rec["n_entries"],
            "cost_total": rec["cost_total"],
            "rolls": rec["rolls"],
            "max_trade_notional": rec["max_trade_notional"],
            "min_adv_at_trade": rec["min_adv_at_trade"],
            "final_held_n": rec["final_held_n"],
            "transitions_head": rec["transitions_head"]}
    tr = blob["transitions_head"]
    leg_type = repr(type(tr[0]["leg"])) if tr else "EMPTY(no-face)"
    if not tr:
        json.dump({"probe": "r286 cntrend int64 crash-face", "status":
                   "FAIL", "reason": "transitions_head empty -- crash "
                   "face not exercised"}, open(OUT, "w"),
                  ensure_ascii=False, indent=1)
        return 2
    ck = os.path.join(mod.CELL_DIR, "MA_BASE_x2.json")
    os.makedirs(mod.CELL_DIR, exist_ok=True)
    np.save(ck.replace(".json", ".npy"), rec["returns"])
    dump = {k: v for k, v in blob.items() if k != "series"}
    with open(ck + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(mod._jsonable(dump), fh, ensure_ascii=False, indent=1)
    os.replace(ck + ".tmp", ck)
    back = json.load(open(ck, encoding="utf-8"))
    arr = np.load(ck.replace(".json", ".npy"))
    ok = (isinstance(back["transitions_head"][0]["leg"], int)
          and len(back["transitions_head"]) == len(tr)
          and arr.shape == rec["returns"].shape
          and bool(np.allclose(arr, rec["returns"], equal_nan=True)))
    out = {
        "probe": "r286 cntrend int64 crash-face (real-data MA_BASE/x2 "
                 "collect=True dump through fixed path)",
        "ts": datetime.now().astimezone().isoformat(),
        "status": "PASS" if ok else "FAIL",
        "panel": {"T": int(P["T"]), "N": int(P["N"]),
                  "universe_n": int(len(P["syms"]))},
        "cell": "MA_BASE", "face": "x2",
        "leg_type_pre_coercion": leg_type,
        "transitions_n": len(tr),
        "n_trades": int(rec["n_trades"]), "n_entries": int(rec["n_entries"]),
        "sharpe_full": float(blob["stats"]["sharpe_full"]),
        "checkpoint_roundtrip": "ok",
        "elapsed_sec": round(time.time() - t0, 1),
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(f"probe: {out['status']} leg_type={leg_type} "
          f"transitions={len(tr)} elapsed={out['elapsed_sec']}s")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
