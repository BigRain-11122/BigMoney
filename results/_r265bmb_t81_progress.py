# -*- coding: utf-8 -*-
"""R265 bm-b: T-81 slice-4 progress_r265 append (five-face byte mirror per R255/R257 laws).
Five faces probed from HEAD blob: BOM=False, EOL=LF-only, indent=1, ensure_ascii=False,
trailing_newline=False. Diff must be field-increment level (2+/1-)."""
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
P = "fleet/tasks/T-2026-09-26-81-P1.json"

d = json.load(open(P, encoding="utf-8"))
assert "progress_r265" not in d, "already written"
last = [k for k in d if k.startswith("progress")][-1]
assert last == "progress_r257", last
d["progress_r265"] = (
    "R265 bm-b slice-4 LANDING HOOKS delivered (dept:策略+研究 joint, O-1342 sec.4 item-4 "
    "落地即画像): prereg research/LANDING_HOOKS_P1.md v1.0 FROZEN pre-run commit 668cbd5e "
    "(three-family landing watch CN five-model chain / GRID / WILD; landing criteria = each "
    "family's own frozen-batch verdict faces verbatim, zero new criteria; observation marks "
    "lane != landing; landing != activation) + landing_hooks() readout face in "
    "strategy_scorecard.py (run() top-level landing_hooks key; hermetic P11 selftest legs "
    "x4: absent-fail-closed / CN pass-bit landing / GRID SURVIVORS_NO_CANDIDACY intermediate "
    "+ shared CN-GRID-SLEEVE read / paper-candidacy dual-family firing; live leg asserts "
    "zero landings + five-model set identity) + S6 chain wiring strategy_scorecard "
    "re-derive before market_clock_call (Tools/iteration_prompt.txt) + L3 divlowvol "
    "structural label state refresh IN_FLIGHT->JUDGED_NEGATIVE (stale R250 freeze-time "
    "state vs R252 judged-negative fact; L3_ACTIVATION_EVIDENCE v1.1 change record; "
    "criteria untouched, activation semantics unchanged). RUN post-freeze: "
    "results/strategy_scorecard.json landing_hooks face = n_landings=0 hook_state=armed "
    "action_required=[] -- all sec.3 predictions confirmed (CN 5/5 negative: REV-TILT 0/4 "
    "DIV-LOWVOL-ROT 0/4 REGIME-POLICY 0/3 CORE-SATELLITE 0/4 GRID-SLEEVE 0 survivors 0 "
    "candidates; GRID 0/0; WILD 0/25), idempotent across reruns, prereg_sha16 "
    "6301f5c6f3a43d05; L3 table regenerated NOT_ACTIVATED_JUDGED_NEGATIVE; selftests "
    "strategy_scorecard ALL PASS + market_clock_call 8/8; sec.6 backfilled. Slice chain "
    "s1-s4 complete; no reopen face (new landings = new prereg judgments, hook armed)."
)

with open(P, "w", encoding="utf-8", newline="\n") as f:
    json.dump(d, f, ensure_ascii=False, indent=1)

out = subprocess.run(["git", "diff", "--stat", P], capture_output=True).stdout.decode("utf-8")
print("diff --stat:", out.strip())
n_lines = subprocess.run(["git", "diff", "-U0", P], capture_output=True).stdout.decode("utf-8")
adds = sum(1 for l in n_lines.splitlines() if l.startswith("+") and not l.startswith("+++"))
dels = sum(1 for l in n_lines.splitlines() if l.startswith("-") and not l.startswith("---"))
print("diff lines: +%d/-%d (expect 2+/1- field-increment level)" % (adds, dels))
assert adds == 2 and dels == 1, (adds, dels)
print("OK")
