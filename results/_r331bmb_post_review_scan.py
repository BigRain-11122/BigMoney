import json

rows = [json.loads(l) for l in open(r"results\post_review.jsonl", encoding="utf-8") if l.strip()]
targets = ["T-27-BMAXDIV-WIRING", "T-33-CORPS-ROSTER", "O-2030-PRESIGNAL",
           "O-2100-COMPUTE-DISPATCH", "O-2115-POST-REVIEW"]
for t in targets:
    hist = [r for r in rows if (r.get("id") or r.get("row_id") or r.get("name")) == t]
    print("=" * 20, t, "history", len(hist))
    for h in hist[-3:]:
        print(json.dumps(h, ensure_ascii=False)[:400])
