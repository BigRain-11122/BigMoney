# -*- coding: utf-8 -*-
"""_r247bmc_catalog_append.py -- surgical append of INNOVATION-QUOTA-SLOT-5
berth entry to Tools/fill_ladder_catalog.json (r246 row-level surgery law:
load -> append -> dump, no reorder; version string extended in-place).
Idempotent: refuses if SLOT-5 id already present (rc=2)."""
import json
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PATH = "Tools/fill_ladder_catalog.json"

with open(PATH, encoding="utf-8") as f:
    d = json.load(f)

if any(e.get("id") == "INNOVATION-QUOTA-SLOT-5" for e in d["entries"]):
    print("SLOT-5 already present -- refuse (rc=2)")
    raise SystemExit(2)

entry = {
    "id": "INNOVATION-QUOTA-SLOT-5",
    "lane_owner": None,
    "enqueue_gates": [
        "prereg_frozen",
        "runner_exists"
    ],
    "prereg_ref": "research/INNOVATION_QUOTA_W5_PREREG.md BERTH (bm-c r247; freeze step = next-round precise continuation per W4 r243->r244 timeline: SEED_REGISTRY key registration (berth draft-read band 20322500 candidate, live three-step reverify at freeze) + FROZEN banner + prediction finalization)",
    "runner": "NOT BUILT (berth state; runner step = scripts/innovation_quota_w5.py mirror of w4 skeleton: scipy siegelslopes rolling RM endpoint + G-ANCHOR fail-closed vs r247 probe facts + r450 landed-state guard + GBK reconfigure entry law)",
    "consumer_plan": "ICU_MA_TIMING_P1 judged verdict (results/innovation_quota/ICU-MA-TIMING-P1.json) -> G2 pass = T-34 fastline candidate pool eligibility; fail = judged-negative family closure + attrition row + 48h CEO report",
    "note": "ladder (d) slot-5 (bm-c r247 berth): zoo #86 icu_ma_timing family (r222 digest param-frozen deep-read, clean-room; #95 consumed slot-3 judged-negative r240, #96 consumed slot-4 judged-negative r246). Robust-regression RM-endpoint trend face = new estimator object for quota line (burned axes all single readings; MOM-axis overlap a_in_b <=9.7% non-collapse, probe-verified). Probe facts frozen results/_r247bmc_icu_w5_probe_facts.json (N5/N120/N15 decidable 3479/3364/3469, open 33.7/51.5/45.3%; N5 tie-maintain mass 1084 days = 31.1% structural face; extreme days 2-3/7 partial-open; scipy-vs-manual RM cross-check 50/50 exact). Supply-law anchor: O-1614 sec.4(d) idle-window quota (pool ready=1<3 at r246 close, only entry = bm-b-lane W11-JUDGE)."
}
d["entries"].append(entry)
d["version"] = (d.get("version") or "") + (" + SLOT-5 berth (bm-c r247: "
               "INNOVATION-QUOTA-SLOT-5 entry added per berth; zoo #86 "
               "icu_ma_timing, prereg BERTH research/INNOVATION_QUOTA_W5_PREREG.md)")

with open(PATH, "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=1)

# re-verify round-trip
with open(PATH, encoding="utf-8") as f:
    d2 = json.load(f)
assert any(e.get("id") == "INNOVATION-QUOTA-SLOT-5" for e in d2["entries"])
assert len(d2["entries"]) == len(d["entries"])
print("appended SLOT-5; entries=%d; version tail ok" % len(d2["entries"]))
