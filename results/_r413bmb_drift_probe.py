import json, glob
for p in ("results/runnable_pool.json", "results/runnable_pool.bm-b.json",
          "results/runnable_pool.bm-a.json", "results/runnable_pool.bm-c.json"):
    try:
        d = json.load(open(p, encoding="utf-8"))
        print(p, "updated_at=", repr(d.get("updated_at")),
              "n_entries=", len(d.get("entries", [])),
              "w6judge=", next((e.get("status") for e in d["entries"]
                                if e.get("id") == "TRIAL-LABOR-W6-JUDGE"), "ABSENT"))
    except Exception as e:
        print(p, "ERR", e)
print("--- dualrun jsonl tail ---")
rows = [json.loads(x) for x in open("results/pool_dualrun.bm-b.jsonl",
                                    encoding="utf-8") if x.strip()]
for r in rows[-3:]:
    print(json.dumps(r, ensure_ascii=False)[:400])
