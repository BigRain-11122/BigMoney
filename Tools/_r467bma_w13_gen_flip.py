import json, sys

POOL = "results/runnable_pool.json"
NOW = "2026-09-30 10:5x"

with open(POOL, encoding="utf-8") as fh:
    pool = json.load(fh)

entries = pool["entries"]
gen = next(e for e in entries if e["id"] == "TRIAL-LABOR-W13-GENERATE")

# --- flip GENERATE -> done (autofill burn credit stays; single-shot refuse guard proven) ---
assert gen["status"] == "ready", f"generate status {gen['status']} != ready"
gen["status"] = "done"
gen["done_at"] = "2026-09-30T10:55:00+08:00"
gen["result_ref"] = (
    "results/trial_labor_w13/w13_candidates.json (autofill burn bm-a tick 10:40:01 pid 87476 "
    "target_met=true; single-shot refuse-if-exists guard; raw 5000 -> distinct 393 = 7.9% dedup "
    "HONEST far-below W12 17.2% -- sixteen-tuple axis 282,175,488 combos collapses heaviest in lineage "
    "= falsifiable-prediction face judged by actual not by band per prereg sec.5.1; exclusion A0/B0 hits "
    "25-source union incl w1-w12 survivors + registered/negative rows; grammar sha16 868cd0c6413636e6 "
    "pinned r466 == consumed; seeds gen=20323000/null=20323500/unc=20324000 R250; evidence_cutoff "
    "2026-09-22 P-5C binding; ledger TRIAL_GRAMMAR_LEDGER W13 row consumed 10:46:04 append-verified)"
)
sh = gen["shards"][0]
assert sh["key"] == "main"
sh["status"] = "done"
sh["done_note"] = "burn complete 10:46:04 candidates n=393 landed; grammar ledger consume row same window; flip by bm-a r467"

with open(POOL, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(pool, fh, ensure_ascii=False, indent=1)
    fh.write("\n")

# round-trip self-verify
with open(POOL, encoding="utf-8") as fh:
    p2 = json.load(fh)
g2 = next(e for e in p2["entries"] if e["id"] == "TRIAL-LABOR-W13-GENERATE")
assert g2["status"] == "done" and g2["shards"][0]["status"] == "done"
assert len(p2["entries"]) == len(entries)
print(f"pool flip OK: W13-GENERATE -> done; entries={len(p2['entries'])}")
