# -*- coding: utf-8 -*-
"""R345 bm-a: append CENSUS-FUS-S2-W2B pool entry (status=waiting, deps:
D8 transfer receipt + W2-A finalize; lane_owner=bm-b per frozen roster)."""
import io, json

POOL = "results/runnable_pool.json"
pool = json.load(io.open(POOL, encoding="utf-8"))
assert not any(e["id"] == "CENSUS-FUS-S2-W2B" for e in pool["entries"]), \
    "entry already present"
mf = json.load(io.open("results/census_fusion_s2/w2b_d8_manifest.json",
                       encoding="utf-8"))
entry = {
    "id": "CENSUS-FUS-S2-W2B",
    "ticket_ref": ("T-2026-09-26-86-P1 s2 wave-2 W2-B (CEO O-20260926-2320 "
                   "cross-wave fusion census; roster+prereg sec.9.4 FROZEN "
                   "R344 commit f084c8e2; runner built bm-a R345, wave-1 + "
                   "W2-A machinery imported not rewritten; selftest 7/7 "
                   "hermetic incl. D8 sha fail-closed gate + 5,620 enum math)"),
    "prereg_ref": ("research/CENSUS_FUSION_S2_PREREG.md sec.9.4 + "
                   "results/census_fusion_s2/w2b_roster.json (same-commit "
                   "freeze; seed census_fusion_s2_w2b=20282500 band "
                   "20282500..20282899 registered R344 same-commit R250); "
                   "EXPLORATION FACE (zero judgment claims / zero paper "
                   "eligibility); N=5,620 = 5,204 cross-wave candidates "
                   "(each >=1 D face) + 16 D rs-controls + 400 nulls "
                   "(rejection-redraw >=1 D); D-family standalone REJECT "
                   "(R338) disclosed with the batch"),
    "runner": "scripts/census_fusion_s2_w2b.py",
    "runner_args": ["run"],
    "lane_owner": "bm-b",
    "priority": 1,
    "status": "waiting",
    "entered_at": "2026-09-27 19:10:30",
    "workers_plan": {
        "workers": 4,
        "priority": "BelowNormal",
        "note": ("A-side state REUSED READ-ONLY from W2-A sidecars "
                 "Money02/data/cache/census_w2/ (validated vs w2_roster at "
                 "prep; absent -> W2A.prep_state() rebuild fallback "
                 "fail-closed) + D8 own sidecars "
                 "Money02/data/cache/census_w2b/ (~2GB, gitignored, "
                 "regenerable from the npz); D8 input = "
                 "data/census_w2b/w2b_d8_faces.npz 60.4MB sha256=" +
                 mf["sha256"][:16] + "... IN-RUNNER sha gate fail-closed vs "
                 "git-tracked manifest w2b_d8_manifest.json; grid anchors "
                 "inside the D-covered window (~250 artifact dates, ~47 "
                 "weekly signals); est burn < W2-A (5,620 specs, same "
                 "per-spec machinery, shorter window); checkpoint "
                 "200-combo JSONL cross-kill resume"),
    },
    "data_gates": ("WAITING DEPS (flip to ready by bm-b upon BOTH): "
                   "(1) D8 transfer receipt -- transfer branch "
                   "transfer/w2b-d8 carries the npz; receiving SOP: git "
                   "fetch + git checkout transfer/w2b-d8 -- "
                   "data/census_w2b/w2b_d8_faces.npz + git restore --staged "
                   "that path (r90 law), verify runner selftest [3] sha "
                   "gate passes; (2) W2-A finalize (CPU physical "
                   "dependency, roster lane note; A sidecars must be "
                   "post-burn stable). IN-RUNNER fail-closed exit 2: "
                   "roster anchors sha12 re-verify + D8 sha256 gate + "
                   "universe join >=5,000 (sec.9.3 frozen reading, "
                   "ok_static subset DISCLOSED not gated) + grid "
                   "feasibility (all-40-faces >=50 valid in D-window) + "
                   "free-RAM >=12GB prep guard + cutoff lockbox 2026-09-24 "
                   "+ incomplete finalize exit 2 checkpoint-retained. "
                   "FIRST-SIGHT PROTOCOL: run `probe` once before the full "
                   "burn (gate + D prep + EW-univ + 4-spec validation)"),
    "shards": [
        {
            "key": "censusw2b-0of1",
            "status": "waiting",
            "owner": None,
            "owner_since": None,
            "checkpoint": ("results/census_fusion_s2/w2b_checkpoint.jsonl "
                           "(200-combo cadence; resume = done-set i)"),
            "note": ("single shard whole-batch (checkpoint makes cross-kill "
                     "resume safe); finalize -> results/census_fusion_s2/"
                     "w2b_results.json (ledger N=5,620 declared at run "
                     "finalize, r252 embed key; products w2b_cells.csv/"
                     "w2b_nulls.json/w2b_top_matrices.json/"
                     "w2b_summary.json); pool flip = round work per r203 law"),
        }
    ],
}
pool["entries"].append(entry)
pool["updated_at"] = "2026-09-27 19:10:30"
s = json.dumps(pool, ensure_ascii=False, indent=1)
json.loads(s)
io.open(POOL, "w", encoding="utf-8", newline="\n").write(s)
print("pool entry appended; total entries:", len(pool["entries"]))
