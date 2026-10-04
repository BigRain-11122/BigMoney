"""Inspect W3 screen shard entry shape in resolved runnable_pool.json (read-only)."""
import json

d = json.load(open(r"results\runnable_pool.json", encoding="utf-8"))
w3 = [e for e in d.get("entries", []) if str(e.get("id", "")).startswith("MASS-TRIAL-W3-SCREEN-SHARD")]
print("w3 entries:", len(w3))
for e in w3:
    keys = sorted(e.keys())
    claim = e.get("claim")
    shards = e.get("shards")
    print("-", e.get("id"), "| top-keys:", keys[:12])
    if claim is not None:
        print("   claim:", json.dumps(claim, ensure_ascii=False)[:200])
    if shards is not None:
        print("   shards:", json.dumps(shards, ensure_ascii=False)[:200])
