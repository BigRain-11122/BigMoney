import json
repo = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
with open(repo + r"\results\runnable_pool.json", "rb") as f:
    pool = json.loads(f.read().decode('utf-8'))
for e in pool.get("entries", []):
    if e.get("id", "").startswith("MASS-TRIAL-W2-JUDGE") or e.get("id") == "MASS-TRIAL-W1-JUDGE":
        print(json.dumps({k: v for k, v in e.items() if k != "shards"}, ensure_ascii=True)[:900])
        for sh in e.get("shards", [])[:2]:
            print("  shard:", json.dumps({k: v for k, v in sh.items() if k != "note"}, ensure_ascii=True)[:400])
        print("===")
