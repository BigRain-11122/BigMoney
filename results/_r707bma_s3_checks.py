# r707 bm-a S3 checks: watermark verdict + open-ticket text scan (ConvertFrom-Json avoided per r641)
import json, glob, io, subprocess

w = json.load(io.open("results/watermark_red.json", encoding="utf-8"))
print("watermark red:", w.get("red"), "| reason:", str(w.get("reason", ""))[:150])

r = subprocess.run(["python", "scripts/saturation_engine.py", "status"], capture_output=True, text=True)
print("satengine rc:", r.returncode)
print(r.stdout.strip()[-500:])

open_t = []
for p in glob.glob("fleet/tasks/*.json"):
    try:
        t = json.load(io.open(p, encoding="utf-8"))
    except Exception as e:
        print("parse-skip", p, e.__class__.__name__); continue
    if t.get("status") == "open":
        open_t.append(p)
print("open tickets:", len(open_t), open_t[:8])
