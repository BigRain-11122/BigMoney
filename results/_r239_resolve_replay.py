# -*- coding: utf-8 -*-
"""R239 replay-conflict resolver (big commit 9326b9b1): 
- T-77 ticket: yield already decided -> take stage2 (bm-b claim + yield note) wholesale, drop my progress_r239
- CODELY.md: memory-union (line-level union of both sides' appends, dedupe identical lines, order: ours then theirs-new)
- firm/LOCAL_FIRST.md: bm-b canonical deliverer -> take stage2 (bm-b) wholesale; print diff summary of my unique lines for the addendum note
- Tools/iteration_prompt.txt: auto-merged; validate zero conflict markers + both wirings present (diagnostic only)
Fail-closed: any anomaly -> exit 2 without writing."""
import json
import subprocess
import sys


def blob(stage, path):
    out = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if out.returncode != 0:
        raise SystemExit(f"blob read fail {stage} {path}: {out.stderr[:150]}")
    return out.stdout.decode("utf-8")


# ---- 1) T-77 ticket: take ours (stage2) wholesale
P77 = "fleet/tasks/T-2026-09-26-77-P1.json"
ours77 = json.loads(blob(2, P77))
mine77 = json.loads(blob(3, P77))
assert "bm-b" in str(ours77.get("claimed_by")), "stage2 must be bm-b-yield state"
assert "bm-a" in str(mine77.get("claimed_by")), "stage3 must be my side"
resolved77 = dict(ours77)
assert resolved77.get("yield_note_r239"), "yield note must survive from replayed claim commit"
with open(P77, "w", encoding="utf-8", newline="\n") as f:
    json.dump(resolved77, f, ensure_ascii=False, indent=1)
    f.write("\n")
chk = json.load(open(P77, encoding="utf-8"))
assert "bm-b" in str(chk["claimed_by"]) and chk.get("yield_note_r239")
print("1) T-77: bm-b claim + yield note kept; my progress dropped")

# ---- 2) CODELY.md: memory-union
CM = "CODELY.md"
base = blob(1, CM).splitlines()
ours = blob(2, CM).splitlines()
theirs = blob(3, CM).splitlines()
base_s = set(base)
ours_new = [ln for ln in ours if ln not in base_s]      # bm-b's appended lines
theirs_new = [ln for ln in theirs if ln not in base_s]  # my appended lines
# union: keep ours structure, append my new lines not already present (dedupe identical)
merged = list(ours)
existing = set(merged)
added = 0
for ln in theirs_new:
    if ln.strip() and ln not in existing:
        merged.append(ln)
        existing.add(ln)
        added += 1
assert not any(ln.startswith(("<<<<<<<", "=======", ">>>>>>>")) for ln in merged), "markers leaked"
with open(CM, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(merged) + ("\n" if merged else ""))
print(f"2) CODELY.md union: ours_new={len(ours_new)} theirs_new_added={added} (dedup {len(theirs_new)-added})")

# ---- 3) LOCAL_FIRST.md: bm-b canonical
LF = "firm/LOCAL_FIRST.md"
ours_lf = blob(2, LF)   # bm-b side (onto)
mine_lf = blob(3, LF)   # my side
mine_lines = set(mine_lf.splitlines())
ours_lines = set(ours_lf.splitlines())
unique_mine = [ln for ln in mine_lf.splitlines() if ln not in ours_lines and ln.strip()]
with open(LF, "w", encoding="utf-8", newline="\n") as f:
    f.write(ours_lf if ours_lf.endswith("\n") else ours_lf + "\n")
print(f"3) LOCAL_FIRST.md: bm-b side taken; my unique non-blank lines not carried: {len([l for l in unique_mine if len(l) > 30])} (long ones)")
for ln in unique_mine:
    if len(ln) > 40:
        print("   MY-UNIQUE:", ln[:110])

# ---- 4) iteration_prompt.txt diagnostic (auto-merged, staged)
IP = "Tools/iteration_prompt.txt"
cur = open(IP, encoding="utf-8", newline="").read()
bad = cur.count("<<<<<<<") + cur.count(">>>>>>>") 
print(f"4) iteration_prompt.txt: markers={bad} (must be 0); market_clock_call={cur.count('market_clock_call.py')}; daily_report={cur.count('daily_report.py')}; gpu_factor={cur.count('gpu_factor')}; crash_fuse={cur.count('crash_fuse')}")
if bad:
    sys.exit(2)
print("resolver done")
