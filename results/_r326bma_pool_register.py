# -*- coding: utf-8 -*-
"""r326 bm-a: register CENSUS-FUS-S2-W2A into runnable_pool (T-86 s2 wave-2).

House pattern = results/_r220_pool_register.py (fresh read -> append ->
verify-parse -> write indent=2). Idempotent: skips ids already present.
lane_owner=bm-b frozen by prereg sec.9.3 (astock panel data locality, R31
family). Runner built bm-a R326: hermetic selftest 12/12 ALL PASS (roster/
enumeration/seeds, vendor engines on synthetic 9-key panels, LHB literal
dedup+shift1, rs controls, blend top_k equivalence vs wave-1 default,
gate fail-closed, sidecar worker glue, ledger pure-fn, np-native coercion).
"""
import json
import time

POOL = "results/runnable_pool.json"
TS = time.strftime("%Y-%m-%d %H:%M:%S")

ENTRY = {
    "id": "CENSUS-FUS-S2-W2A",
    "ticket_ref": "T-2026-09-26-86-P1 s2 wave-2 W2-A (CEO O-20260926-2320 "
                  "factor-level fusion census; roster+prereg sec.9.3 FROZEN "
                  "R325 commit 38c7dc96; runner built bm-a R326, wave-1 "
                  "machinery imported not rewritten)",
    "prereg_ref": "research/CENSUS_FUSION_S2_PREREG.md sec.9.3 + results/"
                  "census_fusion_s2/w2_roster.json (same-commit freeze; seeds "
                  "census_fusion_s2_w2=20281500 band 20281500..20281899 + "
                  "census_fusion_s2_w2_unc=20282000 registered R325); "
                  "EXPLORATION FACE (zero judgment claims / zero paper "
                  "eligibility); N=5,920 = 5,456 candidates + 64 rs controls "
                  "+ 400 nulls; UNC face = separate follow-up batch after "
                  "W2-A finalizes (sec.9.3 routing)",
    "runner": "scripts/census_fusion_s2_w2.py",
    "runner_args": ["run"],
    "lane_owner": "bm-b",
    "priority": 1,
    "status": "ready",
    "entered_at": TS,
    "workers_plan": {
        "workers": 4,
        "priority": "BelowNormal",
        "note": "state sidecars Money02/data/cache/census_w2/ (~15GB, gitignored, "
                "p1c-cache dir family) + worker mmap init (p1e _worker_init "
                "pattern -- the ~12GB state cannot pickle to Windows spawn "
                "workers); est prep 15-40min (5,217 CSVs -> panels + 34 face "
                "builds incl. zoo/GTJA191x10/WQ101x10/A158x7/LHB + sidecar "
                "writes) then burn est 3-6h wall (5,920 specs ~5-10s/spec at "
                "5,217 syms, ic_series wide anchor ~8.7s/combo benchmarked); "
                "checkpoint 200-combo JSONL cross-kill resume; prep re-runs "
                "on resume (sidecars deterministic rebuild)",
    },
    "data_gates": "in-runner fail-closed exit 2: panel dir present + universe "
                  "join >= 5,000 FROZEN gate (panel 5,217 files x mask 5,222 "
                  "codes -> ~5,200 expected; ok_static=True subset = 3,517 "
                  "DISCLOSED in gate report, NOT gated -- universe reading = "
                  "panel x mask CODE set; ok_static-only join 3,517 < 5,000 "
                  "cannot satisfy the frozen gate; zero-run amendment record "
                  "ledger_trials_added=0: MSG-20260927-1425-bm-a + ticket "
                  "progress_r326_bma per 2026-09-27 freeze-alignment law) + "
                  "grid feasibility (all-32-faces >=50 valid) + LHB parquet "
                  "present (both machines per sec.9.3) + free-RAM >=12GB prep "
                  "guard + cutoff lockbox 2026-09-24 + incomplete finalize "
                  "exit 2 checkpoint-retained; LANE OWNER NOTE: run the "
                  "`probe` subcommand once on first sight (real-panel gate + "
                  "sidecar prep + EW-univ + 4-spec validation) before/alongside "
                  "the first full burn; selftest 12/12 pre-pooling bm-a R326",
    "shards": [{
        "key": "censusw2a-0of1",
        "status": "ready",
        "owner": None,
        "owner_since": None,
        "checkpoint": "results/census_fusion_s2/w2a_checkpoint.jsonl "
                      "(200-combo cadence; resume = done-set i)",
        "note": "single shard whole-batch (checkpoint makes cross-kill resume "
                "safe); finalize -> results/census_fusion_s2/w2a_results.json "
                "(ledger N=5,920 declared at run finalize, r252 embed key; "
                "products w2a_cells.csv/w2a_nulls.json/w2a_top_matrices.json/"
                "w2a_summary.json); pool flip = round work per r203 law",
    }],
}

with open(POOL, encoding="utf-8") as f:
    pool = json.load(f)
entries = pool.get("entries", [])
have = {e.get("id") for e in entries}
if ENTRY["id"] in have:
    print(f"skip {ENTRY['id']}: already present")
else:
    entries.append(ENTRY)
    pool["entries"] = entries
    pool["updated_at"] = TS
    json.loads(json.dumps(pool))            # verify-parse before write (r185)
    with open(POOL, "w", encoding="utf-8") as f:
        json.dump(pool, f, indent=2, ensure_ascii=False)
    print(f"pool updated: +{ENTRY['id']}, total {len(entries)} (lane_owner=bm-b, "
          f"status=ready)")
