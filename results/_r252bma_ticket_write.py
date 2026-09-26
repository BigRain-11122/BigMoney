# -*- coding: utf-8 -*-
"""R252 bm-a: T-73 ticket progress_r252 append (byte-mirror producer per r254 law:
raw UTF-8, no BOM, CRLF, indent=1; field-level diff only)."""
import json

p = "fleet/tasks/T-2026-09-26-73-P1.json"
raw = open(p, "rb").read()
d = json.loads(raw.decode("utf-8-sig"))
assert "progress_r252" not in d, "progress_r252 already present"
assert d.get("status") == "claimed"

d["progress_r252"] = (
    "R252 s3 slice-2 = CN-DIV-LOWVOL-ROT-P1 BATCH RUN + HARVESTED + "
    "PREREG BACKFILLED (research/CN_DIV_LOWVOL_ROT_PREREG.md s7/s8 one-pass "
    "final). Execution chain: pool entry (R251 14:39:04) starved by fused "
    "T80 head until r252 autofill anti-starvation fix (Tools/autofill.py "
    "refuse-and-skip loop + S16e selftest leg, 26/26 green) -> autofill "
    "tick 14:50:27 launched bm-a pid 43612 -> landed 14:50:53 (18.4s, 65 "
    "units fresh, 0 resumed). VERDICT: 0/4 cells pass G1'v2 -> "
    "CN-DIV-LOWVOL-ROT adjudicated NEGATIVE, line closed per prereg s4 "
    "(no paper account, no judgment-board entry; anti-retrial law applies "
    "-- reopening requires new prereg + new evidence). Numbers: best "
    "W252_bare x2 sharpe 0.7371 < skill line 0.9527 (CI95 [0.0139,1.4851] "
    "low positive; line unmet by -0.216); W63_bare 0.4596; MA200-gate "
    "faces WORSE on both axes (whipsaw cost > trend protection in 2-leg "
    "universe; maxDD -18.18%->-25.85% / -19.89%->-24.61%, sharpe delta "
    "-0.29/-0.47 both below s5.2 band) = prediction double-MISS; W252>W63 "
    "HIT; x1->x2 decay -0.6%/-5.8% <15% HIT; fill_days queue evidence HIT "
    "(W63_bare max 17d 2020-2021 thin-ADV window). Ledger 185798+54=185852 "
    "(runner append_ledger); gate_attrition row 44 visible in `entries` "
    "(r248 law); D6 max|corr| 0.2583 < 0.7 no reject; family PBO 0.0; "
    "EW-pair baseline 0.4972 (rotation increment +0.24 exists but below "
    "line, not zero-increment). Harvest gate "
    "results/_r252bma_rot_harvest.py PASS (10-face deterministic "
    "re-derive) -> pool entry+shard flipped done + harvest_note (r244 "
    "law). s3 scoreboard after this slice: CN-REVERSAL-TILT negative "
    "(R249), CN-DIV-LOWVOL-ROT negative (R252) = 2/5 models judged, 0 "
    "pass; remaining = CORE-SATELLITE (satellite supply absent per T-57 "
    "0/25 honest negative), REGIME-POLICY (s2 policy-axis research not "
    "done -- research-first law), CN-GRID-SLEEVE (grid engine landed "
    "T-78 s5, combo-model prereg open). Next slice = s2 policy-axis "
    "digest leg for REGIME-POLICY (research-first) or GRID-SLEEVE combo "
    "prereg draft; both are in-repo deterministic opens."
)

out = json.dumps(d, ensure_ascii=False, indent=1)
data = out.encode("utf-8").replace(b"\n", b"\r\n")
with open(p, "wb") as fh:
    fh.write(data)
print("progress_r252 appended; bytes:", len(data))
