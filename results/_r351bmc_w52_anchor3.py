import json, sys
sys.stdout.reconfigure(encoding="utf-8")
d = json.load(open("results/perpetual_faces/n1_w49_results.json", encoding="utf-8"))
f = d["families"]
print("[families keys]", list(f.keys()) if isinstance(f, dict) else type(f))
print(json.dumps(f, ensure_ascii=False)[:2000])
