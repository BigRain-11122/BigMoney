# -*- coding: utf-8 -*-
"""r713 bm-c rehearsal: prove the CTA-P1 first-bar wiring path end-to-end.

Copies the real 9-variety panel to a TEMP dir, appends one synthetic
2026-10-08 bar per variety, monkeypatches fr.FUT_DIR + the harness state
paths onto the temp faces, and runs the real cmd_run twice (accrual then
idempotent no-op). Zero repo data touch, zero canon touch. Evidence JSON
written to results/_r713bmc_cta_paper_rehearsal.json; temp dir removed.
"""
import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

import pandas as pd

import cta_p1_paper as cpp
from engine import futures_runner as fr

facts = {}
tmp = tempfile.mkdtemp(prefix="cta_paper_rehearsal_")
try:
    # build temp panel = real 9 csvs + one synthetic 2026-10-08 bar
    for v in cpp.NINE:
        src = os.path.join(fr.FUT_DIR, f"{v}.csv")
        df = pd.read_csv(src, index_col=0, parse_dates=True).sort_index()
        last = float(df["close"].iloc[-1])
        o = round(last * 1.004, 3)
        c = round(last * 1.008, 3)
        row = pd.DataFrame(
            {"open": o, "high": round(max(o, c) * 1.001, 3),
             "low": round(min(o, c) * 0.999, 3), "close": c,
             "volume": 1000.0},
            index=[pd.Timestamp("2026-10-08")])
        df = pd.concat([df, row])
        df.to_csv(os.path.join(tmp, f"{v}.csv"))

    # patch faces onto temp
    fr.FUT_DIR = tmp
    cpp.LANE_DIR = os.path.join(tmp, "state")
    cpp.STATE_PATH = os.path.join(cpp.LANE_DIR, "CTA-P1_paper.json")

    rc1 = cpp.cmd_run()
    st = json.load(open(cpp.STATE_PATH, encoding="utf-8"))
    rc2 = cpp.cmd_run()

    marks = st.get("marks", [])
    facts["rc1"] = rc1
    facts["rc2"] = rc2
    facts["n_marks"] = len(marks)
    facts["first_mark_date"] = marks[0]["date"] if marks else None
    facts["first_mark_ret"] = marks[0]["daily_ret"] if marks else None
    facts["equity_cny"] = st.get("equity_cny")
    facts["panel_cutoff"] = st.get("panel_cutoff")
    facts["status"] = st.get("status")
    facts["schema"] = st.get("schema")
    facts["slot_registration_ok"] = "experimental account #28" in \
        str(st.get("slot_registration", ""))
    facts["honest_history_keys"] = sorted(list(st.get("honest_history", {}).keys()))
    facts["construction_universe"] = st.get("construction", {}).get("universe")
    facts["marks_summary"] = st.get("marks_summary")

    checks = [
        ("first cmd_run accrues rc=0", rc1 == 0),
        ("exactly 1 mark (the 10-08 bar)", len(marks) == 1),
        ("mark date = 2026-10-08", marks and marks[0]["date"] == "2026-10-08"),
        ("equity positive near initial", bool(facts["equity_cny"])
         and 0.5e7 < facts["equity_cny"] < 1.5e7),
        ("panel_cutoff = 2026-10-08", st.get("panel_cutoff") == "2026-10-08"),
        ("status = trial-live", st.get("status") == "trial-live"),
        ("schema = cta_p1_paper_v1", st.get("schema") == "cta_p1_paper_v1"),
        ("slot registration #28 present", facts["slot_registration_ok"]),
        ("universe = frozen nine",
         st.get("construction", {}).get("universe") == cpp.NINE),
        ("honest-history disclosures carried (6 keys)",
         len(facts["honest_history_keys"]) == 6),
        ("second cmd_run idempotent rc=0", rc2 == 0),
    ]
    facts["checks"] = [{"name": n, "ok": bool(c)} for n, c in checks]
    facts["all_pass"] = all(c for _, c in checks)
finally:
    shutil.rmtree(tmp, ignore_errors=True)

out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "results", "_r713bmc_cta_paper_rehearsal.json")
with open(out, "w", encoding="utf-8") as fh:
    json.dump(facts, fh, ensure_ascii=True, indent=1)

for n, c in checks:
    print(f"[{'PASS' if c else 'FAIL'}] {n}")
print(f"rehearsal: {'ALL PASS' if facts['all_pass'] else 'FAILED'} "
      f"(first mark ret {facts['first_mark_ret']:+.6f}, "
      f"equity {facts['equity_cny']:,.2f})")
sys.exit(0 if facts["all_pass"] else 2)
