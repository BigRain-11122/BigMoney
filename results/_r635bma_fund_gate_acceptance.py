"""r635 bm-a acceptance probe: fund-trio finalize-readiness dashboard face.

Verifies the J10 increment landed this round (build_status._fund_family_state
nulls_target derive + _fund_finalize_gate rehearsal-sourced blockers +
dashboard.html render hooks). Import-only, read-only, zero pool/engine faces.
Run: python results/_r635bma_fund_gate_acceptance.py
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from monitor import build_status  # noqa: E402

FAIL = []


def check(name, cond, detail=""):
    print(("[PASS] " if cond else "[FAIL] ") + name + (" | " + detail if detail else ""))
    if not cond:
        FAIL.append(name)


ff = build_status._fund_family_state()

fams = {f["family"]: f for f in ff.get("families", [])}
for label in ("VALUE", "QUALITY", "DIVLOWVOL"):
    f = fams.get(label)
    check(f"{label} family present", f is not None)
    if f:
        # single source = runnable_pool FUND-*-P1-NULLS prereg_ref 'nulls 2000'
        check(f"{label} nulls_target==2000 (pool prereg_ref parsed)",
              f.get("nulls_target") == 2000,
              f"nulls_target={f.get('nulls_target')} nulls_rows={f.get('nulls_rows')}")

fg = ff.get("finalize_gate")
check("finalize_gate present", fg is not None)
if fg:
    check("finalize_gate NOT_A_VERDICT banner carried", fg.get("not_a_verdict") is True)
    check("finalize_gate rehearsal ts present", bool(fg.get("rehearsal_ts")),
          str(fg.get("rehearsal_ts")))
    gfam = fg.get("families") or {}
    for name in ("fund_quality_p1", "fund_value_p1", "fund_divlowvol_p1"):
        g = gfam.get(name)
        check(f"gate[{name}] present", g is not None)
        if g:
            check(f"gate[{name}] g_seg_pass is False (GM ruling face)",
                  g.get("g_seg_pass") is False and g.get("g_seg_ruling_face") == "GM",
                  f"coverage={json.dumps(g.get('g_seg_coverage'))}")
            check(f"gate[{name}] coverage chop==14", 
                  (g.get("g_seg_coverage") or {}).get("chop") == 14)
    gv = gfam.get("fund_value_p1") or {}
    check("gate[fund_value_p1] passive_crash=True fix_face=bm-b",
          gv.get("passive_crash") is True and gv.get("passive_fix_face") == "bm-b")
    check("gate[fund_quality_p1] passive_crash=False",
          (gfam.get("fund_quality_p1") or {}).get("passive_crash") is False)
    check("gate[fund_divlowvol_p1] passive_crash=False",
          (gfam.get("fund_divlowvol_p1") or {}).get("passive_crash") is False)

# degrade honesty: missing source -> None (temp-path probe, no file writes to repo)
orig = build_status.PATHS.results_dir
gate_missing = None
class _P:
    root = orig
    results_dir = os.path.join(os.environ.get("TEMP", "/tmp"), "_r635_no_such_dir")
build_status.PATHS = _P
try:
    gate_missing = build_status._fund_finalize_gate()
finally:
    build_status.PATHS = orig
check("missing rehearsal source degrades to honest None", gate_missing is None)

# dashboard.html render hooks present (DOM-equivalent static face)
html = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "dashboard.html"), encoding="utf-8").read()
check("dashboard.html NULLS target render hook", "f.nulls_target ? \"/\" + n2(f.nulls_target)" in html)
check("dashboard.html finalize gate row hook", "基本面族 · finalize 前置门" in html)
check("dashboard.html gate status logic", 'g.g_seg_pass === false || g.passive_crash' in html)

# end-to-end: live payload regeneration lands the fields in the JSON twin
st = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                 "results", "dashboard_status.json"), encoding="utf-8"))
stff = (st.get("data") or {}).get("fund_family") or {}
check("live dashboard_status.json carries nulls_target x3",
      sum(1 for f in stff.get("families", []) if f.get("nulls_target") == 2000) == 3,
      "json twin may lag until next build_status run -- run probe after S6 leg")

print()
print("SUMMARY:", ("ALL PASS" if not FAIL else f"{len(FAIL)} FAIL: {FAIL}"))
sys.exit(0 if not FAIL else 1)
