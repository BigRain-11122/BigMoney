# r422 bm-b W7-JUDGE harvest closeout: attrition backfill (T-119 face #3) + pool dual-face done-flip
# Laws: 坑律一百零一批 (entry+shard dual-face); r185 parse-verify; three-way receipt prints.
import json, datetime

# ---------- 1. gate_attrition.json backfill ----------
ap = "results/gate_attrition.json"
a = json.load(open(ap, encoding="utf-8"))
prop_names = [k for k, v in a.items() if isinstance(v, list)]
print("attrition props:", {k: len(a[k]) for k in prop_names})
# locate the array(s) where W6 rows live (same array as precedent)
target = None
for k in prop_names:
    batches = {row.get("batch") for row in a[k] if isinstance(row, dict)}
    if "TRIAL_LAB_W6_JUDGE" in batches:
        target = k
        break
assert target is not None, "no array carries TRIAL_LAB_W6_* precedent rows"
have = {row.get("batch") for row in a[target] if isinstance(row, dict)}
assert "TRIAL_LAB_W7_SCREEN" not in have and "TRIAL_LAB_W7_JUDGE" not in have, "W7 rows already present"

row_screen = {
    "batch": "TRIAL_LAB_W7_SCREEN",
    "ts": "2026-09-29 10:59:31",
    "kind": "measurement",
    "retro_fill": False,
    "cells_ledger_delta": 3904,
    "ledger_total_after": 337336,
    "gates": {
        "screen_pass": {"n_candidates": 3704, "n_survivors": 284,
                        "line": "beat6m_rate > null_p95 strictly-greater (null_p95=0.5180, prereg sec.3 frozen)"},
        "null_face": {"p50": 0.51, "p95": 0.518, "n": 200,
                      "note": "K=200 ten-tuple axis nulls with streak leg, seed 20305500; p50 0.51 > 0.50 = null-bottom prediction miss second consecutive wave (W6 0.5036 -> W7 0.51), disclosed honestly; screen survival line = program-frozen null p95 (W2-W6 identical law)"},
        "streak_face": {"segmented_survival": "down_streak2 9.34% (102/1092) > none 7.95% (103/1296) > up_streak2 6.00% (79/1316)",
                        "top_interaction_cell": "none|wild|none|volume_dry|down_streak2 35% (7/20)",
                        "note": "STREAK new-face direction intel: reversal-confirmation (buy after 2 down bars) enriches screen survival vs momentum-confirmation, same direction as in-book reversal anchors (T-22/T-73/O-2330); judge face all-zero G1 in all streak segments"}
    },
    "eliminated": 3420,
    "refs": {"prereg": "research/TRIAL_LABOR_W7_PREREG.md",
             "results": "results/trial_labor_w7/w7_screen.json",
             "ticket": "T-2026-09-29-118"},
    "note": "r422 bm-b backfill (T-119 drift-debt face #3): attrition row missed at r421 screen-finalize landing window; original event ts preserved; numbers true-source = results/trial_labor_w7/w7_screen.json read-only (no re-burn); receipt = TRIAL_LABOR_W7_PREREG sec.8"
}
row_judge = {
    "batch": "TRIAL_LAB_W7_JUDGE",
    "ts": "2026-09-29 11:42:55",
    "kind": "judgment",
    "retro_fill": False,
    "cells_ledger_delta": 284,
    "ledger_total_after": 337620,
    "gates": {
        "g1_prime_v2": {"n": 284, "n_pass": 0,
                        "line": "skill_line_v2 per-cell (ledger_head live read); top cell W7-B-0809 pullback_bounce sharpe_full=0.9533 vs line=1.1930 (n_eff=341240) -- line_ok false; five-face total zero (gate/vol/yang/vconf/streak all segments 0)"},
        "g2_registration_v2": {"n_eligible": 0, "top_dsr": 0.748135, "n_trials": 337336,
                              "line": "G1 pass AND DSR>=0.95 AND PBO<=0.25"},
        "e_fp_nominal_5pct": 14.2,
        "family_pbo": {"folk": 0.8286, "seasonal": 0.8286, "patterns": 0.6571,
                       "ta": 0.6, "mean_reversion": 0.5429, "momentum": 0.4857,
                       "trend": 0.4429, "composite_rotation": "insufficient (<8 cells)"}
    },
    "eliminated": 284,
    "refs": {"prereg": "research/TRIAL_LABOR_W7_PREREG.md",
             "results": "results/trial_labor_w7/w7_judge.json",
             "intake": "results/trial_labor_w7/w7_intake.json (zero-face n_eligible=0)",
             "ticket": "T-2026-09-29-118"}
}
a[target].append(row_screen)
a[target].append(row_judge)
json.dumps(a)  # serialize check
with open(ap, "w", encoding="utf-8") as f:
    json.dump(a, f, ensure_ascii=False, indent=4)
re = json.load(open(ap, encoding="utf-8"))  # reparse verify (r185)
assert len(re[target]) >= 2 and any(r.get("batch") == "TRIAL_LAB_W7_JUDGE" for r in re[target])
print(f"attrition: 2 rows appended to '{target}' (now {len(re[target])} rows), reparse-verified")

# ---------- 2. runnable_pool.json dual-face flip ----------
pp = "results/runnable_pool.json"
p = json.load(open(pp, encoding="utf-8"))
e = None
for ent in p["entries"]:
    if ent["id"] == "TRIAL-LABOR-W7-JUDGE":
        e = ent
        break
assert e is not None, "pool entry TRIAL-LABOR-W7-JUDGE missing"
assert e["status"] == "ready", f"entry status != ready: {e['status']}"
assert len(e["shards"]) == 1, "expected single shard"
sh = e["shards"][0]
print(f"pre-flip: entry.status={e['status']} shard.status={sh['status']} shard.owner={sh.get('owner')} owner_since={sh.get('owner_since')}")

# three-way verification (坑律一百零一批): product numbers vs pool/prereg expectations
j = json.load(open("results/trial_labor_w7/w7_judge.json", encoding="utf-8"))
i = json.load(open("results/trial_labor_w7/w7_intake.json", encoding="utf-8"))
assert j["n_judged_cells"] == 284 == len(j["cells"]), "judged cells mismatch"
assert j["trials_ledger"]["prev_total"] == 337336 and j["trials_ledger"]["batch_trials"] == 284 \
       and j["trials_ledger"]["total"] == 337620, "ledger chain mismatch"
assert j["n_eligible_g2"] == 0 and not j["eligible_g2"], "G2 nonzero unexpected"
assert i["n_eligible"] == 0, "intake nonzero unexpected"
assert sum(1 for c in j["cells"] if c["g1_pass"]) == 0, "G1 nonzero unexpected"
print("three-way verified: 284 cells / ledger 337336+284=337620 / G1 0 / G2 0 / intake 0")

now = "2026-09-29T12:1x+08:00"
sh["status"] = "done"
sh["owner"] = "bm-b"          # actual burner; bm-c 11:30:05 dead-hand takeover voided at this flip (MSG-1142 own declaration)
sh["owner_since"] = "2026-09-29 11:10:04"  # bm-b autofill claim (commit 67a53bf2a)
sh["done_at"] = "2026-09-29 11:42:55"
sh["result_ref"] = ("results/trial_labor_w7/checkpoint/judge_shard_0of1.jsonl (284/284 cells, unique cell_id 284 == "
                    "w7_screen survivors 284 verified; burn bm-b pid4948 11:10:01 launch -> detached finalize landed "
                    "11:42:55 w7_judge.json; bm-c staleness takeover 11:30:05 = P5C cache-less exit in seconds, zero "
                    "science writes per MSG-1142, dead-hand claim voided at this flip)")
sh["closed_at"] = "2026-09-29 12:1x"
e["status"] = "done"
e["done_at"] = "2026-09-29T11:42:55+08:00"
e["result_ref"] = "results/trial_labor_w7/w7_judge.json"
e["done_note"] = (
    "r422 bm-b successor harvest: judge-finalize detached by predecessor r422-attempt 11:26:01 (predecessor died "
    "~11:37 stream-timeout; finalize process survived session death and landed 11:42:55, W6 r415 same pattern) -> "
    "w7_judge.json: 284 judged cells (== w7_screen survivors 284), TOTAL-ZERO G1 across all five faces (gate "
    "none/bear/bull 0; vol none/calm/wild 0; yang none/first_yang 0; vconf none/dry/surge 0; streak none/up/down 0) "
    "-> G2 eligible 0 -> [] (best cell W7-B-0809 pullback_bounce sharpe_full=0.9533 vs line=1.1930 n_eff=341240 "
    "line_ok false; top DSR 0.7481 no G1); E[FP]=14.2 at nominal 5% caliber (DSR>=0.95 gate IS the correction); "
    "family PBO 11 modules (folk/seasonal 0.8286 highest, trend 0.4429 lowest, composite_rotation 1c insufficient "
    "disclosed); trials_ledger TRIAL_LAB_W7_JUDGE prev 337336 + 284 = 337620 cross-wave linear no-reset verified; "
    "evidence_cutoff 2026-09-22 lockbox; grammar 1fba956c2f21d1d3 (== FROZEN_SHA16 build anchor). Intake zero-face "
    "landed same round: results/trial_labor_w7/w7_intake.json (prereg sec.6 s4 actual-count clause; zero eligible = "
    "D6/library/paper-desk all zero-surface). Attrition rows W7-SCREEN + W7-JUDGE backfilled same round (T-119 "
    "drift-debt face #3). 48h CEO report clock started at finalize landing 2026-09-29T11:42:55+08:00 (standing "
    "deadline 2026-10-01 11:42:55); CEO report landed same round docs/trial_labor/CEO-REPORT-WAVE7-20260929.md."
)
# dual-face closure assert (坑律一百零一批: for-shard full closure)
assert e["status"] == "done" and all(s["status"] == "done" for s in e["shards"]), "dual-face flip incomplete"
json.dumps(p)
with open(pp, "w", encoding="utf-8") as f:
    json.dump(p, f, ensure_ascii=False, indent=1)
rp = json.load(open(pp, encoding="utf-8"))  # reparse verify
ent = next(x for x in rp["entries"] if x["id"] == "TRIAL-LABOR-W7-JUDGE")
assert ent["status"] == "done" and ent["shards"][0]["status"] == "done"
print(f"pool flip LANDED: TRIAL-LABOR-W7-JUDGE entry+shard dual-face done (reparse-verified)")
