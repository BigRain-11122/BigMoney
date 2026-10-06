# -*- coding: utf-8 -*-
# r650 bm-c: HANDOVER 5x facts probe -- unified ledger head + wave state (read-only)
import json, os, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = {}
# 1) unified ledger head: live head = newest n1_w*_results.json science_gates.ledger.total
heads = []
for f in glob.glob(os.path.join(ROOT, "results", "perpetual_faces", "n1_w*_results.json")):
    try:
        d = json.load(open(f, encoding="utf-8-sig"))
    except Exception:
        continue
    led = (d.get("science_gates") or {}).get("ledger") or {}
    tot = led.get("total")
    if isinstance(tot, int):
        w = int(os.path.basename(f).split("_w")[1].split("_")[0])
        heads.append((w, tot, os.path.basename(f)))
heads.sort()
out["n1_wave_heads_tail"] = heads[-3:]
out["live_head_file"] = heads[-1][2] if heads else None
out["unified_ledger_head"] = heads[-1][1] if heads else None
# 2) W167 ledger block cross-check (prev_total/batch_trials arithmetic)
live = json.load(open(os.path.join(ROOT, "results", "perpetual_faces", out["live_head_file"]), encoding="utf-8-sig"))
led = live["science_gates"]["ledger"]
out["ledger_block"] = {"prev_total": led.get("prev_total"), "batch_trials": led.get("batch_trials"),
                       "total": led.get("total"), "batch": led.get("batch")}
assert led["prev_total"] + led["batch_trials"] == led["total"], "ledger arithmetic check"
with open(os.path.join(ROOT, "results", "_r650bmc_handover_facts.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
print(json.dumps(out, ensure_ascii=False))
