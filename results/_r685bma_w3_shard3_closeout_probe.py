"""r685 bm-a: W3 shard-3 coverage probe + full-wave id-dup scan (r482 bm-c law).

Verifies:
 1. shard-3 coverage: all combined-row ids at positions [3681,4909) present exactly
    once in w3_screen_checkpoint.jsonl (1228/1228, closeout gate for pool flip).
 2. full-wave dup scan (r482 bm-c finalize id-dedup pit): every id unique across
    all 4909 rows -- dup>0 -> keep-first dedup REQUIRED before finalize.
 3. full-wave coverage: all 4909 combined-row ids present (finalize gate refuses
    missing ids).
"""
import json, sys

sys.path.insert(0, "scripts")
OUT = r"results/_r685bma_w3_shard3_closeout_probe.json"

ckpt = {}
dup_ids = []
for line in open(r"results/mass_trial/w3_screen_checkpoint.jsonl", encoding="utf-8"):
    if not line.strip():
        continue
    row = json.loads(line)
    jid = row["id"]
    if jid in ckpt:
        dup_ids.append(jid)
    ckpt[jid] = row

# combined rows in frozen order (same construction as runner)
import mass_trial_w1 as M
ctx = M.Ctx()
rows = M._combined_rows(ctx, 3)
all_ids = [r["id"] for r in rows]
assert len(rows) == 4909, f"combined rows {len(rows)} != 4909"

shard3_ids = all_ids[3681:4909]
sh3_present = [i for i in shard3_ids if i in ckpt]
sh3_missing = [i for i in shard3_ids if i not in ckpt]

all_missing = [i for i in all_ids if i not in ckpt]

probe = {
    "round": 685, "machine": "bm-a",
    "ckpt_rows": len(ckpt), "dup_id_count": len(dup_ids),
    "shard3_expected": len(shard3_ids), "shard3_present": len(sh3_present),
    "shard3_missing": len(sh3_missing),
    "full_wave_expected": len(all_ids),
    "full_wave_missing": len(all_missing),
    "full_wave_covered": len(all_ids) - len(all_missing),
    "verdict": None,
}
if len(sh3_missing) == 0 and len(shard3_ids) == 1228:
    probe["shard3_closeout"] = "GREEN 1228/1228"
else:
    probe["shard3_closeout"] = f"RED missing={sh3_missing[:10]}"
if len(dup_ids) == 0 and len(all_missing) == 0:
    probe["verdict"] = "WAVE-FINALIZE-ELIGIBLE (4/4 complete, id-unique)"
else:
    probe["verdict"] = "BLOCKED"
    probe["dup_sample"] = dup_ids[:10]
    probe["missing_sample"] = all_missing[:10]
json.dump(probe, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(probe, ensure_ascii=False))
sys.exit(0 if probe["verdict"] == "WAVE-FINALIZE-ELIGIBLE" else 2)
