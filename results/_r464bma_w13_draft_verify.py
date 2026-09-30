# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
src = open("results/_r464bma_w13_runner_draft.py", encoding="utf-8").read()
checks = {
    "AXIS_SUMN": 'AXIS_SUMN = ["none", "sumn20_lo", "sumn10_lo"]',
    "combos": "282,175,488",
    "grammar_kind": '"w13-sumn-gate-extended"',
    "seeds_gen": '"trial_labor_w13_gen": SEED_GEN',
    "sobol_sumn": "rng.integers(0, len(AXIS_SUMN)",
    "sobol_unpack": "rq_, su_ = ax[i]",
    "excl_face": "std_rsqr_sumn_none_face",
    "axis15": 'cand["axis"][15]',
    "su_chain": "SU = sumn_zero_mask(RQ",
    "sumn_state_series": "sumn_state_series",
    "tl12_face": "rsqr_state_series = tl12.rsqr_state_series",
    "anchor_dec": '"decidable_days": 3363',
    "anchor_open": '"open_days": 387',
    "layer_def": "def _sumn_faces_raw",
    "structure_pass": "def _sumn_structure_pass",
    "w13_screen_src": 'disc["w13_screen_survivors"]',
    "w13_judge_src": 'disc["w13_judge_products"]',
    "frozen_placeholder": "PENDING-SLICE-B-PIN",
    "prior_w12": '"W12": tl12.FROZEN_SHA16',
    "cur_return_sumn": "rsqr_zeroed, sumn_zeroed",
    "null_sumn_leg": "AXIS_SUMN[int(rng.integers(len(AXIS_SUMN)))",
}
bad = 0
for k, v in checks.items():
    n = src.count(v)
    flag = "OK " if n >= 1 else "MISS"
    if n < 1:
        bad += 1
    print(f"{flag} {k}: {n}")
print("residual w12 build refs (sections 11-16 pending, expected >0):",
      src.count("build_grammar_w12("))
print("BAD:", bad)
sys.exit(1 if bad else 0)
