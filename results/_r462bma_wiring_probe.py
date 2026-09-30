# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
lines = io.open("scripts/trial_labor_w12.py", encoding="utf-8").read().splitlines()
pat = re.compile(r"run_candidate_curve_w12\(|_effective_signal_mask_w12\(|std_face|std_zeroed|rsqr_face|rsqr_zeroed|sumn|csv|writerow|fieldnames|std_state=|rsqr_state=|_dual_nulls_w12\(|std_seg|rsqr_seg|gvvvsktsam|FROZEN_SHA16|axis\[14\]|axis\[15\]|fifteen|FIFTEEN|94,058,496")
for i, l in enumerate(lines, 1):
    if pat.search(l):
        print(i, "|", l.rstrip()[:160])
