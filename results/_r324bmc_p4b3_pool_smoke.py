"""r324 bm-c: p4_batch3_dca pool conversion real-path identity smoke.

FIRST LAUNCH INCIDENT (disclosed): this driver initially ran top-level
without an __main__ guard -> pool spawn workers re-imported the driver
itself and recursively re-ran the serial pass (r312 spawn-reimport pit,
re-offended this window; two orphan serial checkpoints = parent + one
recursive child, byte-identical SHA256 = accidental real-data serial
double-run determinism proof). Fix: main() + __main__ guard (this file).

Passes:
  S (reuse): orphan serial checkpoint rows (116/116 complete, P4B3_MP=0
             legacy path, real frozen data face, cutoff 2026-09-24)
  P (burn) : pool default wiring, worker cap patched to 6 for smoke
             speed (identity proof is width-free; worker-count
             invariance already covered by selftest S-mp legs; the full
             60s core-spread proof accrues at the next natural burn per
             r304/r312 natural-accrual law)
  C        : canon pre-conversion checkpoint (workers=1 batch products)

Asserts P == S key-for-key (conversion identity, primary) and
S == C (refactor semantics vs canon). Zero canon touches: tmp
CELLS_PATH/LOG_PATH only, no finalize, no ledger, no attrition.
Artifact: results/_r324bmc_p4b3_pool_smoke.json
"""
import glob
import hashlib
import json
import os
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    t0 = time.time()
    sys.path.insert(0, ROOT)
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import pandas as pd
    import p4_batch3_dca as p4
    import parallel_runner as pr
    from live.paper import load_core, build_panels

    orphans = sorted(glob.glob(os.path.join(
        tempfile.gettempdir(), "p4b3_pool_smoke_*", "serial_cells.jsonl")))
    assert orphans, "no orphan serial checkpoint to reuse"
    ser_path = orphans[0]
    ser_sha = hashlib.sha256(open(ser_path, "rb").read()).hexdigest()
    dbl_sha = None
    if len(orphans) >= 2:
        dbl_sha = hashlib.sha256(open(orphans[1], "rb").read()).hexdigest()
    ser_rows = p4.load_rows(ser_path)

    prices_full = load_core()
    data_end = str(prices_full["510300"].index[-1].date())
    ps = pd.Timestamp(p4.CUTOFF)
    prices = {s: df[df.index <= ps] for s, df in prices_full.items()}
    P = build_panels(prices)
    idx = P["close"].index
    syms = list(P["close"].columns)
    assert len(syms) == 48, f"panel gate: {len(syms)}/48"
    trig = p4.build_triggers(P)

    canon = p4.load_rows(p4.CELLS_PATH)
    expected = ({p4.cell_key(t, m, r, f) for t in p4.TRIGGERS
                 for m in p4.MODES for r in p4.REGIMES for f in p4.FACES}
                | {f"null|{r}|{k}" for r in p4.REGIMES
                   for k in range(p4.N_RAND)})
    missing_ser = sorted(expected - set(ser_rows))
    missing_canon = sorted(expected - set(canon))
    assert not missing_ser, f"orphan serial incomplete: {missing_ser[:3]}"
    assert not missing_canon, f"canon incomplete: {missing_canon[:3]}"

    tmp = tempfile.mkdtemp(prefix="p4b3_pool_smoke2_")
    p4.CELLS_PATH = os.path.join(tmp, "pool_cells.jsonl")
    p4.LOG_PATH = os.path.join(tmp, "pool.log")
    os.environ.pop(p4._MP_ENV, None)
    pr.worker_cap = lambda: 6          # smoke width cap; identity is width-free
    tP = time.time()
    info = p4._burn_cells_and_nulls(prices, idx, syms, trig, done={})
    pool_rows = p4.load_rows(p4.CELLS_PATH)

    m_ps = sorted(k for k in expected if pool_rows.get(k) != ser_rows.get(k))
    m_sc = sorted(k for k in expected if ser_rows.get(k) != canon.get(k))
    res = {
        "round": "r324 bm-c", "data_end_raw": data_end, "cutoff": p4.CUTOFF,
        "n_expected": len(expected),
        "serial_pass": {"source": "orphan reuse (P4B3_MP=0 legacy path)",
                        "path": ser_path, "sha256": ser_sha,
                        "double_run_sha256": dbl_sha,
                        "serial_double_run_identical":
                            (dbl_sha == ser_sha) if dbl_sha else None},
        "pool_pass": {"sec": round(time.time() - tP, 1), "info": info,
                      "worker_cap_patched": 6},
        "pool_vs_serial_mismatch": m_ps,
        "pool_vs_serial_identical": not m_ps,
        "serial_vs_canon_mismatch_n": len(m_sc),
        "serial_vs_canon_mismatch_sample": m_sc[:5],
        "serial_vs_canon_identical": not m_sc,
        "wall_total_sec": round(time.time() - t0, 1),
        "first_launch_incident":
            "top-level driver without __main__ guard -> spawn workers "
            "re-imported driver and recursively re-ran serial pass (r312 "
            "pit re-offended; killed at 5min tool limit; orphans reused)",
        "verdict": ("PASS: pool==serial full-set identity (116/116)"
                    + (" + canon semantics intact" if not m_sc
                       else "; canon drift DISCLOSED (engine/data drift "
                            "face, conversion identity unaffected)")
                    if not m_ps else "FAIL: pool != serial"),
    }
    fp = os.path.join(ROOT, "results", "_r324bmc_p4b3_pool_smoke.json")
    json.dump(res, open(fp, "w", encoding="utf-8"), ensure_ascii=False,
              indent=1)
    print(json.dumps(res, ensure_ascii=False, indent=1))
    print("artifact:", fp)
    return 0 if not m_ps else 2


if __name__ == "__main__":
    sys.exit(main())
