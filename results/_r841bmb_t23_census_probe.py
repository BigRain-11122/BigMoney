"""r841 probe: T23 census runner real-data path smoke on the PARTIAL astock
per-set (rebuild in flight, disk truth 3xx/5229 files).

Read-only: loads the panel slice that exists on disk right now, samples
probe-local formulas (probe seeds 424242/424243 -- NOT the registered
T23 substreams; registry seeds are consumed only by the gated census run),
runs census_core with tiny K/B, and prints the faces. Zero writes to
results/t23_census (probe evidence = this file + stdout capture); zero
ledger appends; marks +0; SEED registry untouched.

This validates: load_panel real shapes, P4_BATCH2 elig clauses on real
float64 arrays, evaluator ops on real OHLCV/vwap/ret leaves, ic_from_ranks
calibration with the real calendar, permutation null machinery -- i.e. the
whole run() path except the frozen K=64/B=64 burn itself.
"""
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))), "scripts"))

import t23_random_grammar_census as tc    # noqa: E402

PROBE_SEED_GEN = 424242     # probe-local, disjoint from registry substreams
PROBE_SEED_NULL = 424243

t0 = time.time()
# shrink the census window for probe speed (core accepts panel as given)
panel = tc.load_panel()
print("probe: panel loaded", len(panel["universe"]), "stocks,",
      len(panel["cal"]), "calendar rows,",
      int(panel["census_rows"].shape[0]), "census rows,",
      round(time.time() - t0, 1), "s")
rows = panel["census_rows"]
ns = panel["elig"][rows, :].sum(axis=1)
print("probe: eligible median", int(float(np.median(ns))),
      "min", int(ns.min()), "max", int(ns.max()))

formulas = tc.sample_formulas(6, PROBE_SEED_GEN)
print("probe formulas:", [tc.formula_str(f) for f in formulas])
core = tc.census_core(panel, formulas, 6, 8, min_cross=100,
                      min_periods=30, seed_gen=PROBE_SEED_GEN,
                      seed_null=PROBE_SEED_NULL)
for r in core["formulas"]:
    h1 = r["horizons"]["h1"]
    print("probe formula:", r["formula"], "| depth", r["depth"], "| skip",
          r["skip"], "| h1", h1, "| null_p95", r.get("null_abs_ir_p95"))
print("probe core:", {k: core[k] for k in
                      ("n_ok", "n_skip", "n_unique_formulas",
                       "observed_family_max_abs_icir", "null_family_p95",
                       "census_holds")})
print("probe: elapsed", round(time.time() - t0, 1), "s")
print("probe: RESULT=PASS (real-data path exercised end-to-end; partial-",
      "universe faces are probe-only, no science claims)")
