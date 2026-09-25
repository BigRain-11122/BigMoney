import io, sys, json, glob, os, datetime
sys.stdout.reconfigure(encoding="utf-8")
for p in glob.glob("data/ah_panel/*.json") + glob.glob("results/ah_*.json"):
    try:
        j = json.load(open(p, encoding="utf-8-sig"))
        print("==", p)
        print(json.dumps(j, ensure_ascii=False)[:700])
    except Exception as e:
        print(p, "parse fail", e)
# per-pair data dir
for d in ["data/ah_panel", "data/ah", "data/ah_pairs"]:
    if os.path.isdir(d):
        items = os.listdir(d)
        print("dir", d, "count:", len(items), "sample:", items[:6])
