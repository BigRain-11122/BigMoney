# r669 trio entry detail probe
import json
d = json.load(open(r"results\runnable_pool.json", encoding="utf-8"))
out = {}
for e in d.get("entries", []):
    if e.get("id") in ("FUND-VALUE-P1-NULLS", "FUND-QUALITY-P1-NULLS", "FUND-DIVLOWVOL-P1-NULLS", "TRIAL-LABOR-W14-GENERATE"):
        out[e.get("id")] = {k: v for k, v in e.items() if k not in ("runner_args", "shards")}
with open(r"results\_r669bmb_trio_detail_out.json", "wb") as f:
    f.write(json.dumps(out, ensure_ascii=True, indent=1).encode("ascii"))
print("TRIO-DETAIL-DONE")
