import json, os

# probe: do frozen judge shards carry legL_daily_returns for the 4 E15 members?
MEMBERS = {"W2-23057", "W3-23027", "W3-27009", "W3-46133"}
hits = {}
for wv, shards in (("w2", 4), ("w3", 4)):
    for k in range(shards):
        p = rf"results\mass_trial\{wv}_judge_shard_{k}of4.jsonl"
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as f:
            for line in f:
                if not any(m in line for m in MEMBERS):
                    continue
                try:
                    c = json.loads(line)
                except Exception:
                    continue
                cid = c.get("candidate_id")
                if cid in MEMBERS and cid not in hits:
                    hits[cid] = {
                        "wave": wv,
                        "shard": p,
                        "keys": sorted(c.keys()),
                        "has_daily": "legL_daily_returns" in c,
                        "n_daily": len(c.get("legL_daily_returns") or []),
                        "first_ts": (c.get("legL_daily_returns") or [None])[0],
                    }
for cid in sorted(hits):
    h = hits[cid]
    print(cid, "wave", h["wave"], "has_daily", h["has_daily"],
          "n_daily", h["n_daily"])
    print("  keys:", h["keys"])
print("total hits:", len(hits))
