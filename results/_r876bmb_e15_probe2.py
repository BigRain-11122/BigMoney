import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
import science_gates as sg

# 1) closed families
print("CLOSED_FAMILIES keys:", sorted(getattr(sg, "CLOSED_FAMILIES", {}).keys()))
for fam in ("sentiment.turnover_surge", "seasonal.trend_by_season",
            "ta.strong_close", "sentiment"):
    hit = [k for k in getattr(sg, "CLOSED_FAMILIES", {}) if fam in k or k in fam]
    print(" ", fam, "-> closed-family hits:", hit)

# 2) cutoff_meta helper
print("has cutoff_meta:", hasattr(sg, "cutoff_meta"))
if hasattr(sg, "cutoff_meta"):
    print("  sample:", sg.cutoff_meta("2026-09-22"))
print("has deflated_sharpe_ratio:", hasattr(sg, "deflated_sharpe_ratio"))
print("has t_from_sharpe:", hasattr(sg, "t_from_sharpe"))
print("has bh_batch_fdr:", hasattr(sg, "bh_batch_fdr"))
print("has reform_weight_freeze_integrity:", hasattr(sg, "reform_weight_freeze_integrity"))
print("freeze integrity:", sg.reform_weight_freeze_integrity()["pass"])

# 3) trial labor contracts
import trial_labor_w1 as tl1
print("tl1.A_TEMPLATES n:", len(tl1.A_TEMPLATES),
      "ids:", [t["trader_id"] for t in tl1.A_TEMPLATES])
print("tl1.DEFAULT_AXIS:", tl1.DEFAULT_AXIS)
import trial_labor_w2 as tl2
import inspect
print("_d6_admit_core sig:", inspect.signature(tl2._d6_admit_core))
print("tl2.D6_CEILING:", tl2.D6_CEILING)

# 4) mass trial leg-L index + census
import mass_trial_w1 as mt
from p5c_virtual_timepoint import FROZEN_CENSUS
print("FROZEN_CENSUS['L']:", FROZEN_CENSUS["L"])
print("mt.CUTOFF:", mt.CUTOFF, "LEG_L_FLOOR:", getattr(mt, "LEG_L_FLOOR", None))
print("WINDOWS:", mt.WINDOWS)

# 5) reeval18 constants for reuse-law reference
import reeval18_drill as rd
print("reeval18 CI_SEED:", rd.CI_SEED, "PPY:", rd.PPY, "MIN_SEG_DAYS:", rd.MIN_SEG_DAYS)
print("reeval18 REGIME_MAP:", rd.REGIME_MAP)
