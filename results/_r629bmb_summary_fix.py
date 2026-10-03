# -*- coding: utf-8 -*-
# r629 bm-b: rebuild _r633bma rehearsal summary from the three per-family
# report files (the --fam single-family rerun overwrote the trio summary with
# a one-family face). Aggregation only -- reads committed per-family reports,
# adds provenance, same schema as the tool's main().
import json, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = os.path.join(ROOT, "results")
FAMS = ["fund_quality_p1", "fund_value_p1", "fund_divlowvol_p1"]
MACHINE = json.load(open(os.path.join(ROOT, "fleet", "machine.json"),
                         encoding="utf-8"))["machine_id"]

families = {}
notes = {}
for fam in FAMS:
    rep = json.load(open(os.path.join(R, f"_r633bma_finalize_rehearsal_{fam}.json"),
                         encoding="utf-8"))
    families[fam] = {"all_legs_ok": rep["all_legs_ok"],
                     "elapsed_total_sec": rep["elapsed_total_sec"],
                     "failed_legs": [k for k, v in rep["legs"].items()
                                     if not v["ok"]]}
    notes[fam] = {"report_machine_field": rep.get("machine"),
                  "report_ts": rep.get("ts")}

import time
summary = {
    "machine": MACHINE,
    "ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
    "rehearsal": True,
    "NOT_A_VERDICT": True,
    "summary_rebuilt_by": "results/_r629bmb_summary_fix.py (r629 bm-b: --fam "
                          "single-family rerun had clobbered the trio summary "
                          "with a one-family face; this rebuilds it from the "
                          "three committed per-family reports, zero hand edit)",
    "provenance_note": ("quality/divlowvol reports = r628 bm-b rerun, written "
                        "by the pre-patch tool whose machine field was "
                        "hardcoded 'bm-a' (fixed r629 to read "
                        "fleet/machine.json); value report = r629 bm-b patched "
                        "rerun (mirror leg-3 fix, MSG-2026-10-03-1838). "
                        "Per-family 'report_machine_field' below carries each "
                        "file's raw field for honest provenance."),
    "families": families,
    "per_family_provenance": notes,
}
sp = os.path.join(R, "_r633bma_finalize_rehearsal_summary.json")
with open(sp, "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=1)
print("summary rebuilt:")
for fam, v in families.items():
    print(" ", fam, "all_legs_ok =", v["all_legs_ok"],
          "failed =", v["failed_legs"], "| report ts",
          notes[fam]["report_ts"], "machine field", notes[fam]["report_machine_field"])
