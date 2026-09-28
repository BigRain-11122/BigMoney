"""r391 bm-b: DECISION-CHAIN-V2-P1 waiting->ready arm (O-20260928-1533 sec.3
pool reorder: V2-P1 = immediate next pool position, P0 top priority).

Discharges the r357 defer contract (all three conditions):
  (1) RAM >=4GB x 3 samples >=30s (r354 three-sample gate) -- live probe here
  (2) W2B census burn landed (pool CENSUS-FUS-S2-W2B done; dual-4GB squeeze
      face cleared)
  (3) T-95 G-REPRO fix verified -- bm-c 53be4125 + r380 bm-b live gate probe
      all-pass both faces (artifact-drift-fallback path, prereg s9-a5)
"""
import datetime as dt
import json
import time

import psutil

POOL = r"results\runnable_pool.json"
POOL_BMB = r"results\runnable_pool.bm-b.json"
ENTRY = "DECISION-CHAIN-V2-P1"

samples = []
for i in range(3):
    free_gb = psutil.virtual_memory().available / (1 << 30)
    samples.append(round(free_gb, 2))
    if i < 2:
        time.sleep(16)
print(f"RAM 3-sample gate: {samples} GB (min gate 4.0)")
assert min(samples) >= 4.0, samples
assert (samples and True)

now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
ARM_NOTE = (
    "r391 bm-b arm waiting->ready (r357 defer discharged, all 3 conditions): "
    "(1) RAM 3-sample " + str(samples) + " GB >=4GB (r354); (2) W2B census "
    "burn landed (dual-4GB squeeze cleared, CENSUS-FUS-S2-W2B done); "
    "(3) T-95 G-REPRO-REV fix verified live (bm-c 53be4125 + r380 bm-b gate "
    "probe all-pass base+x2 via prereg s9-a5 artifact-drift-fallback path). "
    "O-20260928-1533 sec.3 pool reorder: V2-P1 = next pool position "
    "(W4-JUDGE yields per CEO order; V3 tournament queued behind v2 verdict). "
    "S16c fix-is-the-unflag auto-clear in force (runner sha "
    "6b850e168fad4e46 != fused 880297a0fb0854bf)."
)

for path in (POOL, POOL_BMB):
    d = json.load(open(path, encoding="utf-8"))
    items = d.get("entries", d) if isinstance(d, dict) else d
    e = next(x for x in items if x.get("id") == ENTRY)
    assert e["status"] == "waiting", (path, e["status"])
    e["status"] = "ready"
    e["ready_note"] = ARM_NOTE
    e["armed_at"] = now
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    d2 = json.load(open(path, encoding="utf-8"))
    items2 = d2.get("entries", d2) if isinstance(d2, dict) else d2
    e2 = next(x for x in items2 if x.get("id") == ENTRY)
    assert e2["status"] == "ready"
    print(f"{path}: {ENTRY} waiting->ready (dual-face, armed {now})")
print("autofill next tick claims v2-0of1 (owner bm-b since 02:33:18)")
