# -*- coding: utf-8 -*-
# r980: verify stash@{0} content superseded by worktree (regen-class daemon faces)
import subprocess, re

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
faces = [
    "results/autofill_state.bm-c.json",
    "results/dispatcher_state.bm-c.json",
    "results/saturation_engine/face_bm-c.json",
    "results/saturation_engine_state.bm-c.json",
]
out = subprocess.run(["git", "diff", "stash@{0}", "--"] + faces,
                     capture_output=True, cwd=REPO)
d = out.stdout.decode("utf-8", "replace")
plus = [l for l in d.splitlines() if l.startswith("+") and not l.startswith("+++")]
minus = [l for l in d.splitlines() if l.startswith("-") and not l.startswith("---")]
print("stash-vs-worktree changed lines: +%d -%d" % (len(plus), len(minus)))
ts = re.findall(r'"(?:ts|updated_at|tick_ts|last_flush_at)"\s*:\s*"([^"]+)"', d)
print("timestamps seen in diff:", ts[:10])
for l in plus[:6]:
    print("PLUS", l[:150])
for l in minus[:6]:
    print("MINUS", l[:150])
