# -*- coding: utf-8 -*-
"""R287 bm-a: submit CENSUS-FUS-S2-W1 pool entry (byte-face-mirrored write,
R255/R257 law: indent=1, ensure_ascii=False, LF, no trailing newline)."""
import json
from datetime import datetime

POOL = "results/runnable_pool.json"
raw = open(POOL, "rb").read()
d = json.loads(raw.decode("utf-8"))

assert not any(e.get("id") == "CENSUS-FUS-S2-W1" for e in d["entries"]), "already entered"
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
entry = {
    "id": "CENSUS-FUS-S2-W1",
    "ticket_ref": "T-2026-09-26-86-P1 s2 (CEO O-20260926-2320 factor-level fusion census; claimed bm-a R277; F-04 MSG-20260927-0230-bm-a declared R286 before freeze commit)",
    "prereg_ref": "research/CENSUS_FUSION_S2_PREREG.md FROZEN e51e55e0 precedes runner build 8a00f514+ precedes ANY run (R99); seed census_fusion_s2=20274500 registered at freeze commit (band 20274500..20274900, science_gates.SEED_REGISTRY); EXPLORATION FACE (zero judgment claims / zero paper eligibility; sole output = frozen-rule family aggregation feeding T-23 intake funnel); RANDOM_LARGE_SAMPLE_LAW v1.0 binding (400 same-machinery combo nulls through identical blend/cost face)",
    "runner": "scripts/census_fusion_s2.py",
    "runner_args": ["run"],
    "lane_owner": None,
    "priority": 1,
    "status": "ready",
    "entered_at": now,
    "data_gates": "in-runner fail-closed exit 2: 48 bare-code members + >=60 rows each + end==2026-09-24 + OHLCV+amount cols + volume>0 mask (prereg sec.2) + grid feasibility (all-29-faces >=16 valid) + incomplete finalize exit 2 checkpoint-retained; per-200-combo JSONL checkpoint cross-kill resume; bench disclosure: csi300.csv ends 2026-09-22, compute_all reindex+ffill bridges to 09-24 (rs control faces only, 2-bar stale tail disclosed in audit); selftest 14/14 pre-pooling (r263 law: incl r286 np-native injection leg + real worker-glue leg + gate fail-closed legs); real-data gate probe PASSED 2026-09-27 02:4x bm-a (gate 48/48 all-green, grid 279 signals first 2020-12-29, EW48 x1 sharpe 0.154 ann 0.0266, 4 rows real-assembly json round-trip)",
    "workers_plan": {
        "workers": 4,
        "priority": "BelowNormal",
        "note": "parallel_runner run_cells_parallel (23 blocks x 200 combos, keyed consumption r259 law); est 4,518 combos ~20-40min wall per prereg sec.0; RAM peak <1GB/worker (shared arrays ~45MB)"
    },
    "shards": [
        {"key": "censusfus-0of1", "status": "ready", "owner": None,
         "owner_since": None, "checkpoint": None}
    ]
}
d["entries"].append(entry)
d["updated_at"] = now
out = json.dumps(d, ensure_ascii=False, indent=1)
json.loads(out)
with open(POOL, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(out)
print("pool entry submitted:", entry["id"], "entries:", len(d["entries"]))
