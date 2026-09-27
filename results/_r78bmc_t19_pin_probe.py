"""r78 bm-c: probe -- 6 pinned-face baselines vs frozen T-14 A faces.

Validates the r78 pin fix on REAL data before the pool relaunch: each
trader's rail reproduced with the pinned (T-14-freeze) registration must
be bit-exact vs the frozen T-14 batch A face (the G-REPRO hard gate's
own check, executed for all 6 traders up front). This is diagnosis/
validation only -- the pool batch (counterfactuals + 150 placebos)
stays with autofill C8 (inline-ban law).

Usage: python results/_r78bmc_t19_pin_probe.py
Writes: results/_r78bmc_t19_pin_probe.json
"""
import json
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import live.paper as LP
from scripts.t14_rules_fidelity import _seg_clean, run_rail
from scripts.t19_phantom_contribution import (T14_BATCH, _baseline,
                                              load_traders_t14_face)

OUT = os.path.join(_REPO, "results", "_r78bmc_t19_pin_probe.json")


def main() -> int:
    frozen = json.load(open(T14_BATCH, encoding="utf-8-sig"))
    rows_f = {r["trader"]: r for r in frozen["traders"]}
    prices_full = LP.load_core()
    results, n_pass = [], 0
    for t in load_traders_t14_face():
        tid = t["id"]
        base = _baseline(t, prices_full, rows_f)     # asserts G-REPRO itself
        n_pass += 1
        got_is = _seg_clean(base["rail"]["got"]["in_sample"])
        got_oos = _seg_clean(base["rail"]["got"]["out_sample"])
        results.append({
            "trader": tid, "cutoff": base["cutoff"], "g_repro": "PASS",
            "is": got_is, "oos": got_oos,
            "frozen_is": rows_f[tid]["A"]["is"],
            "frozen_oos": rows_f[tid]["A"]["oos"],
        })
        print(f"[probe] {tid}: G-REPRO PASS (IS s={got_is['sharpe']}, "
              f"OOS s={got_oos['sharpe']}, cutoff {base['cutoff']})")
    out = {
        "batch": "r78 pin-fix validation probe (not the pool batch)",
        "g_repro_pass": n_pass, "g_repro_total": 6,
        "pin": "data/consolidation/t14_anchor_face.json (src 4a5754a3)",
        "verdict": "PIN-VALID: 6/6 bit-exact vs frozen T-14 A faces"
        if n_pass == 6 else "PIN-INVALID",
        "traders": results,
    }
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(f"[probe] written: {OUT} ({n_pass}/6 PASS)")
    return 0 if n_pass == 6 else 1


if __name__ == "__main__":
    raise SystemExit(main())
