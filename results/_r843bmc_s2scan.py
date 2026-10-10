import json, glob, io, os
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
# fleet tasks open scan
open_tasks = []
for p in glob.glob(ROOT + r"\fleet\tasks\*.json"):
    try:
        t = json.load(io.open(p, encoding="utf-8-sig"))
        st = t.get("status","?")
        if st == "open":
            open_tasks.append({"file": os.path.basename(p), "subject": str(t.get("subject", t.get("title","")))[:120], "priority": t.get("priority")})
    except Exception as e:
        open_tasks.append({"file": os.path.basename(p), "err": str(e)[:80]})
print("OPEN TASKS:", json.dumps(open_tasks, ensure_ascii=False))
# watermark red
try:
    wm = json.load(io.open(ROOT + r"\results\watermark_red.json", encoding="utf-8-sig"))
    print("watermark_red:", wm.get("red"), "| reason:", str(wm.get("reason", wm.get("note","")))[:150])
except Exception as e:
    print("watermark_red read err:", str(e)[:80])
try:
    j = [json.loads(l) for l in io.open(ROOT + r"\results\watermark.jsonl", encoding="utf-8").read().splitlines() if l.strip()]
    last = j[-1]
    print("watermark latest verdict:", last.get("verdict"), "| ts:", last.get("ts", last.get("time","")))
    print("next_pick:", str(last.get("next_pick", last.get("bandit_advisory","")))[:200])
except Exception as e:
    print("watermark.jsonl err:", str(e)[:80])
