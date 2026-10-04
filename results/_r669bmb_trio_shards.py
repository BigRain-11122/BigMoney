# r669 trio shard-claim + burn progress probe
import json, os
d = json.load(open(r"results\runnable_pool.json", encoding="utf-8"))
out = {}
for e in d.get("entries", []):
    if e.get("id", "").startswith(("FUND-VALUE-P1-NULLS", "FUND-QUALITY-P1-NULLS", "FUND-DIVLOWVOL-P1-NULLS")):
        sh = e.get("shards", [])
        out[e["id"]] = {
            "status": e.get("status"),
            "n_shards": len(sh),
            "shards": [{k: v for k, v in s.items() if k not in ("runner_args",)} for s in sh][:4],
        }
# burn progress from nulls.jsonl line counts
prog = {}
for fam in ("fund_value_p1", "fund_quality_p1", "fund_divlowvol_p1"):
    p = os.path.join("results", fam, "nulls.jsonl")
    if os.path.exists(p):
        with open(p, "rb") as f:
            n = sum(1 for _ in f)
        prog[fam] = n
out["nulls_rows"] = prog
with open(r"results\_r669bmb_trio_shards_out.json", "wb") as f:
    f.write(json.dumps(out, ensure_ascii=True, indent=1).encode("ascii"))
print("TRIO-SHARDS-DONE", prog)
