# -*- coding: utf-8 -*-
"""R265 bm-b addendum: fix freeze-commit hash citation in T-81 progress_r265 after S7
rebase replay (668cbd5e -> 174be4b8; R99 order law preserved in replayed chain).
Five faces probed from HEAD blob: BOM=False, EOL=LF-only, indent=1, ensure_ascii=False,
trailing_newline=False. Diff must stay field-increment level."""
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
P = "fleet/tasks/T-2026-09-26-81-P1.json"

d = json.load(open(P, encoding="utf-8"))
old = d["progress_r265"]
assert "668cbd5e" in old and "174be4b8" not in old
d["progress_r265"] = old.replace(
    "prereg research/LANDING_HOOKS_P1.md v1.0 FROZEN pre-run commit 668cbd5e ",
    "prereg research/LANDING_HOOKS_P1.md v1.0 FROZEN pre-run commit 668cbd5e "
    "(replayed 174be4b8 after S7 push-collision rebase, R99 order law preserved "
    "in replayed chain: freeze still precedes run commit 8b392771) ")
with open(P, "w", encoding="utf-8", newline="\n") as f:
    json.dump(d, f, ensure_ascii=False, indent=1)

out = subprocess.run(["git", "diff", "-U0", P], capture_output=True).stdout.decode("utf-8")
adds = sum(1 for l in out.splitlines() if l.startswith("+") and not l.startswith("+++"))
dels = sum(1 for l in out.splitlines() if l.startswith("-") and not l.startswith("---"))
print("diff lines: +%d/-%d" % (adds, dels))
assert adds == 1 and dels == 1, (adds, dels)
print("OK")
