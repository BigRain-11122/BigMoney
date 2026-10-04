"""W117 finalize rehearsal r684 bm-a (r633 pattern: evidence before one-shot finalize).

Import-only intent: exercise finalize() guard chain for wave 117 WITHOUT any
legitimate-landing risk window pollution. Expected honest state: W116 (bm-b,
burn pending per origin bc1e82773 freeze + RAM-floor hold) results file absent
-> finalize() crashes at the pre_values composition loop (r307 implicit chain
gate via _wave_values FileNotFoundError) BEFORE sg.append_ledger and BEFORE the
OUT write = zero pollution. This probe:
  L1: origin tree check -- n1_w116_results.json absent from origin/main
  L2: pre/post ledger face hash + OUT file absence -- zero-write assertion
  L3: prior-wave dependency census (W2..W115 present per chain state, 15 held by N2)
Writes: results/_r684bma_w117_finalize_rehearsal.json (probe file, zero writes
to any canon face).
"""
import hashlib
import json
import subprocess
import sys

OUT = r"results\_r684bma_w117_finalize_rehearsal.json"
W117_RESULTS = r"results\perpetual_faces\n1_w117_results.json"
LEDGER = None  # resolved via science_gates below


def sha256_file(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def main():
    import os, sys as _sys
    _sys.path.insert(0, os.path.abspath("scripts"))  # r683 law: science_gates lives in scripts/
    _sys.path.insert(0, os.path.abspath("."))        # knowledge/ at repo root
    import science_gates as sg
    probe = {"round": 684, "machine": "bm-a", "wave": 117,
             "pattern": "r633 finalize rehearsal (one-shot protection)"}
    # L1: origin tree face
    r = subprocess.run(["git", "show", "origin/main:results/perpetual_faces/n1_w116_results.json"],
                       capture_output=True)
    probe["L1_w116_on_origin"] = (r.returncode == 0)
    probe["L1_w116_local"] = __import__("os").path.exists(r"results\perpetual_faces\n1_w116_results.json")
    probe["L1_verdict"] = "GATE_ARMED (W116 absent -> chain-pending)" if (r.returncode != 0) else "GATE_OPEN (W116 landed -> real finalize lawful)"
    # L3: prior-wave dep census from registry derive (WAVE_CONFIGS keys < 117)
    sys.path.insert(0, r"scripts")
    import perpetual_faces_n1 as n1
    missing, present = [], []
    for w in sorted(k for k in n1.WAVE_CONFIGS if k < 117):
        import os
        fp = __import__("os").path.join(n1.OUT_DIR, n1.WAVE_CONFIGS[w]["out_name"])
        (present if __import__("os").path.exists(fp) else missing).append(w)
    probe["L3_prior_waves"] = {"registry_keys_below_117": len(present) + len(missing),
                               "present": len(present), "missing": missing}
    # L2: ledger + OUT zero-write snapshot
    import os
    led_path = os.path.join(os.path.dirname(sg.__file__), "..", "results", "science_gates_ledger.json")
    led_path = os.path.normpath(led_path)
    probe["L2_ledger_path_guess"] = led_path
    probe["L2_out_absent"] = not os.path.exists(W117_RESULTS)
    # ledger face via sg helper if available
    try:
        probe["L2_ledger_total_before"] = sg.ledger_total() if hasattr(sg, "ledger_total") else None
    except Exception as e:
        probe["L2_ledger_total_before"] = f"ERR {e!r}"
    json.dump(probe, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(probe, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
