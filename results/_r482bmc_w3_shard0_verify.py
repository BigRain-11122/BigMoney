"""r482 bm-c: W3 screen shard-0 checkpoint coverage verification.
Expected id set = first 1227 candidate ids of w3_candidates.json (combined
rows = 4814 cand + 75 DEF + 20 NULL, candidates first -> shard-0 [0,1227)
= pure candidate slice). Set-identity + dupes + row_type stats + survivors."""
import json
import os

OUT_DIR = "results/mass_trial"

cand = json.load(open(os.path.join(OUT_DIR, "w3_candidates.json"),
                      encoding="utf-8"))
cands = cand["candidates"]
assert cand["n"] == len(cands) == 4814, (cand.get("n"), len(cands))

# shard-0 expected ids: positions [0,1227) = candidates[0:1227]
expected = [r["id"] for r in cands[:1227]]
assert len(expected) == 1227
assert len(set(expected)) == 1227, "candidate ids not unique??"

# checkpoint actual ids (ordered, with dup detection)
ck = os.path.join(OUT_DIR, "w3_screen_checkpoint.jsonl")
rows = []
with open(ck, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            rows.append(json.loads(line))
ids = [r["id"] for r in rows]

out = []
out.append("CHECKPOINT_ROWS %d" % len(rows))
out.append("UNIQUE_IDS %d" % len(set(ids)))
dupes = [i for i in set(ids) if ids.count(i) > 1]
out.append("DUPES %s" % (sorted(dupes)[:10],))

missing = sorted(set(expected) - set(ids))
extra = sorted(set(ids) - set(expected))
out.append("MISSING_vs_expected %d %s" % (len(missing), missing[:8]))
out.append("EXTRA_vs_expected %d %s" % (len(extra), extra[:8]))

# row_type distribution + screen survivors in shard-0
rt = {}
for r in rows:
    rt[r.get("row_type")] = rt.get(r.get("row_type"), 0) + 1
out.append("ROW_TYPES %s" % rt)
surv = [r["id"] for r in rows if r.get("row_type") == "candidate"
        and r.get("screen_pass")]
out.append("SCREEN_PASS %d" % len(surv))
err = [r["id"] for r in rows if r.get("status") == "signal_error"]
out.append("SIGNAL_ERRORS %d" % len(err))
beat = [r.get("beat_rate_6m") for r in rows
        if r.get("row_type") == "candidate" and "beat_rate_6m" in r]
out.append("CAND_WITH_BEAT %d min %s max %s" %
           (len(beat), min(beat) if beat else None, max(beat) if beat else None))
# elapsed stats (burn pace evidence)
el = [r.get("elapsed_s") for r in rows if isinstance(r.get("elapsed_s"), (int, float))]
if el:
    out.append("ELAPSED_S n=%d total=%.1f mean=%.3f max=%.3f" %
               (len(el), sum(el), sum(el) / len(el), max(el)))

# pool flip state now
pool = json.load(open("results/runnable_pool.json", encoding="utf-8"))
w3 = {e["id"]: (e.get("status"), e["shards"][0].get("owner"),
                e["shards"][0].get("owner_since"))
      for e in pool["entries"]
      if str(e.get("id", "")).startswith("MASS-TRIAL-W3-SCREEN-SHARD")}
out.append("POOL_W3_NOW %s" % json.dumps(w3, ensure_ascii=False))

ok = (len(rows) == 1227 and not dupes and not missing and not extra
      and set(rt.keys()) == {"candidate"})
out.append("VERDICT %s" % ("SHARD0_COMPLETE_COVERAGE_OK" if ok else "CHECK_FAIL"))

open("results/_r482bmc_w3_shard0_verify_out.txt", "w",
     encoding="utf-8").write("\n".join(out) + "\n")
print("PROBE_DONE", out[-1])
