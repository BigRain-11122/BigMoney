import json
d = json.load(open("results/runnable_pool.json", encoding="utf-8"))
print("top keys:", list(d.keys()))
ents = d.get("entries", [])
print("n_entries:", len(ents))
if ents:
    print("first entry keys:", list(ents[0].keys()))
    for e in ents:
        blob = json.dumps(e, ensure_ascii=False)
        if "W6" in blob or "V3-TOUR" in blob or "T-105" in blob or "SCREEN" in blob or "JUDGE" in blob:
            print("---")
            print(blob[:700])
