# r1100 bm-c: dump W271 skill_line block field faces for sec78 backfill authoring
import json
w271 = json.load(open("results/perpetual_faces/n1_w271_results.json", encoding="utf-8"))
sl = w271["skill_line_v2_k_lift"]
print(json.dumps(sl, indent=1, ensure_ascii=False)[:2000])
print("---shards_consumed---")
print(json.dumps(w271.get("shards_consumed"), ensure_ascii=False)[:400])
print("---audit---")
print(json.dumps(w271.get("audit"), ensure_ascii=False)[:600] if w271.get("audit") else "NO audit key")
