"""r641 bm-b: rebuild _r633bma_finalize_rehearsal_summary.json from the three
fresh per-family rehearsal JSONs (01:34/01:40/01:43 runs on bm-b), because
single-family `--fam` runs overwrite the summary with only that family.
Format mirrors _r633bma_finalize_rehearsal.py main() summary block verbatim."""
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAMS = ["fund_quality_p1", "fund_value_p1", "fund_divlowvol_p1"]

summary = {}
for key in FAMS:
    p = os.path.join(ROOT, "results", f"_r633bma_finalize_rehearsal_{key}.json")
    rep = json.load(open(p, encoding="utf-8"))
    failed = [k for k, v in rep["legs"].items() if not v["ok"]]
    summary[key] = {"all_legs_ok": rep["all_legs_ok"],
                    "elapsed_total_sec": rep["elapsed_total_sec"],
                    "failed_legs": failed}
    print(f"{key}: all_legs_ok={rep['all_legs_ok']} "
          f"elapsed={rep['elapsed_total_sec']}s failed={failed}")
machine = json.load(open(os.path.join(ROOT, "fleet", "machine.json"),
                         encoding="utf-8"))["machine_id"]
sp = os.path.join(ROOT, "results", "_r633bma_finalize_rehearsal_summary.json")
with open(sp, "w", encoding="utf-8") as f:
    json.dump({"machine": machine,
               "ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
               "rehearsal": True, "NOT_A_VERDICT": True,
               "families": summary}, f, ensure_ascii=False, indent=1)
bad = [k for k, v in summary.items() if not v["all_legs_ok"]]
print("SUMMARY REBUILT: " + ("ALL-GREEN x3" if not bad else "RED: " + ",".join(bad)))
sys.exit(0 if not bad else 4)
