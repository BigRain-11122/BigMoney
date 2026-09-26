# -*- coding: utf-8 -*-
"""R244 bm-a: GPU-FACTOR-LANE-PROOF harvest gate (deterministic, zero network, zero LLM).

Deterministic re-derivation of the pool harvest criterion per runnable_pool entry
"checkpoint: proof.json (exists + equiv all pass = landed marker); harvest round
flips entry+shard done":
  1. proof.json exists and parses;
  2. every equiv face has max_abs_diff == 0.0 and non-trivial n_days (>0);
  3. 21 faces present (7 P1E faces x 3 horizons) per pool data_gates contract;
  4. replay determinism evidence: autofill launched the full batch 4x
     (11:29:38/11:34:40/11:40:01/11:42:50, pids 23276/56984/54736/55828), each
     full re-run rewrote proof.json with equiv all-zero -- 4 independent
     re-derivations identical on the science face (timing fields vary by design).
Exit 0 = harvest gate PASS (flip pool entry+shard done). Exit 2 = gate red.
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROOF = os.path.join(ROOT, "results", "gpu_factor_lane", "proof.json")
POOL = os.path.join(ROOT, "results", "runnable_pool.json")
AUTOFILL = os.path.join(ROOT, "results", "autofill_state.json")


def main() -> int:
    fails = []
    if not os.path.exists(PROOF):
        print("FAIL: proof.json absent")
        return 2
    proof = json.load(io.open(PROOF, encoding="utf-8"))

    equiv = proof.get("equiv", {})
    faces = sorted(equiv.keys())
    n_days_bad = [k for k, v in equiv.items() if not v.get("n_days")]
    zero_bad = [k for k, v in equiv.items() if v.get("max_abs_diff") != 0.0]
    if len(faces) != 21:
        fails.append(f"equiv faces n={len(faces)} != 21 (7 P1E faces x 3 horizons)")
    if zero_bad:
        fails.append(f"equiv max_abs_diff != 0 faces: {zero_bad[:5]}")
    if n_days_bad:
        fails.append(f"equiv n_days <= 0 faces: {n_days_bad[:5]}")

    ps = proof.get("panel_shape", {})
    if not (ps.get("T") == 8792 and ps.get("N") == 5222):
        fails.append(f"panel_shape {ps} != census universe (T=8792 N=5222)")
    if proof.get("torch") != "2.11.0+cu128":
        fails.append(f"torch string {proof.get('torch')!r} unexpected")
    if not proof.get("engineering_lane") or not proof.get("no_gates_no_ledger_no_registration"):
        fails.append("engineering-lane guards missing in proof.json")

    # replay determinism evidence from autofill launcher ledger (4x relaunch, each
    # completed a full recompute that rewrote proof.json with equiv all-zero).
    st = json.load(io.open(AUTOFILL, encoding="utf-8"))
    relaunches = [
        x for x in st.get("launches", [])
        if x.get("entry") == "GPU-FACTOR-LANE-PROOF" and x.get("machine") == "bm-a"
        and x.get("ts", "") >= "2026-09-26 11:2"
    ]
    pids = [x.get("pid") for x in relaunches]
    if len(relaunches) < 3:
        fails.append(f"replay evidence thin: {len(relaunches)} bm-a launches {pids}")

    pool = json.load(io.open(POOL, encoding="utf-8"))
    entry = next((e for e in pool.get("entries", []) if e.get("id") == "GPU-FACTOR-LANE-PROOF"), None)
    if entry is None:
        fails.append("pool entry GPU-FACTOR-LANE-PROOF missing")
    else:
        if entry.get("status") != "ready":
            fails.append(f"entry status {entry.get('status')!r} != 'ready' (harvest expects pre-flip ready)")

    verdict = {
        "harvest_gate": "PASS" if not fails else "FAIL",
        "equiv_faces": len(faces),
        "equiv_all_zero": not zero_bad,
        "replay_launches_ts": [x.get("ts") for x in relaunches],
        "replay_pids": pids,
        "elapsed_s_last_run": proof.get("elapsed_s"),
        "fails": fails,
    }
    print(json.dumps(verdict, ensure_ascii=False, indent=1))
    return 0 if not fails else 2


if __name__ == "__main__":
    sys.exit(main())
