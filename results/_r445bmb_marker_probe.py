# -*- coding: utf-8 -*-
"""_r445bmb_marker_probe.py -- W12 surgeon pre-flight: marker uniqueness
check on the frozen W11 runner (scripts/trial_labor_w11.py). Read-only."""
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
src = open("scripts/trial_labor_w11.py", encoding="utf-8").read()
print("total lines", src.count("\n"))
markers = [
    'WAVE = "TRIAL_LABOR_W11"', "MOM_ANCHOR", "STD_ANCHOR = {",
    "# --------------------------------------------- std overlay layer",
    "import trial_labor_w10 as tl10", "import trial_labor_w9 as tl9",
    "def build_grammar_w11():", "def draw_candidate_sobol_w11(",
    "def _load_exclusion_rows_w11(", "def _excluded_w11(",
    "def _effective_signal_mask_w11(", "def run_candidate_curve_w11(",
    "def _null_axis_draw_w11", "def cmd_generate() -> int:",
    "# ------------------------------------------------------ screen slice (s2)",
    "def _judge_cell_w11(", "Twenty-two real-read source faces",
    "std_state_series = tl10", "mom_state_series = tl10.mom_state_series",
    'SEED_REGISTRY["trial_labor_w11_gen"]', "PROBE_FACTS_FILE",
    "AXIS_COMBOS = ", "# ------------------------------------------------------------ Sobol draw leg",
    "# ------------------------------------------------ exclusion",
    "# -------------------------------------------- effective face + engine curves",
    "# ------------------------------------------------------------ grammar build",
    "# ------------------------------------------------------------ grammar / status",
    "def _grammar_sha16(grammar):", "FROZEN_SHA16 = None",
    'PRIOR_WAVE_SHA16 = {', '"W10": tl10.FROZEN_SHA16',
    "# ------------------------------------------------- mom overlay (tl10 import face)",
    'def _std_state_full():', 'def _std_structure_pass(std_meta)',
    'std_state_series(prices)', 'std_state, std_err = _std_state_full()',
]
for m in markers:
    print(src.count(m), repr(m[:75]))
for pat in ("RSQR", "rsqr", "a158"):
    print(pat, "->", len(re.findall(re.escape(pat), src)))
