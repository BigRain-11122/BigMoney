# -*- coding: utf-8 -*-
# r661 bm-c S3 probe: watermark + fleet task board + peer heartbeat freshness (read-only)
import json, glob, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

w = json.load(open(r"results\watermark_red.json", encoding="utf-8-sig"))
print("watermark red=%s next_pick=%s lane=%s" % (
    w.get("red"), w.get("next_pick"), w.get("lane") or w.get("reason") or ""))

tot = op = cl = 0
for f in glob.glob(r"fleet\tasks\*.json"):
    tot += 1
    try:
        d = json.load(open(f, encoding="utf-8-sig"))
    except Exception:
        continue
    s = d.get("status")
    if s == "open":
        op += 1
    elif s == "claimed":
        cl += 1
print("fleet_tasks total=%d open=%d claimed=%d" % (tot, op, cl))

for m in ("bm-a", "bm-b"):
    p = r"fleet\machines\%s.json" % m
    if os.path.exists(p):
        d = json.load(open(p, encoding="utf-8-sig"))
        print("hb %s last_seen=%s round_no=%s verdict=%s" % (
            m, d.get("last_seen"), d.get("round_no"), (d.get("verdict") or "")[:80]))

t = json.load(open(r"state-bm-c.json", encoding="utf-8-sig"))
print("self state round_no=%d" % t.get("round_no"))
