"""r630-2 byte-restore: rebase-overwrite lost satengine tick 20:53:04 (epoch 1791031984).

Lost from live history_bm-b.jsonl when the dead session's pull --rebase checked out
origin base over the worktree (~20:54, after the daemon wrote the 20:53:04 tick).
Row recovered byte-level from superseded pick 79db8aeba blob, inserted at ts-sorted
position. Write mode verified open-append-close (saturation_engine.py L461/463/466).
Captured in lineage by this round's S7 commit.
"""
import json
import subprocess

PATH = "results/saturation_engine/history_bm-b.jsonl"

r = subprocess.run(["git", "show", "79db8aeba:" + PATH], capture_output=True)
p2_lines = r.stdout.decode("utf-8").splitlines()
lost = [l for l in p2_lines if '"epoch": 1791031984' in l]
assert len(lost) == 1, f"expected 1 lost row, got {len(lost)}"
row = lost[0]
json.loads(row)

raw = open(PATH, "rb").read()
crlf = b"\r\n" in raw
lines = raw.decode("utf-8").splitlines()
assert not any("1791031984" in l for l in lines), "row already present"

ts_target = "2026-10-03T20:53:04"
pos = 0
for i, l in enumerate(lines):
    try:
        t = json.loads(l).get("ts", "")
    except Exception:
        t = ""
    if t > ts_target:
        pos = i
        break
    pos = i + 1

new_lines = lines[:pos] + [row] + lines[pos:]
nl = "\r\n" if crlf else "\n"
data = nl.join(new_lines) + nl
for l in new_lines:
    json.loads(l)
open(PATH, "wb").write(data.encode("utf-8"))

check = open(PATH, encoding="utf-8").read().splitlines()
print(
    f"restored at pos {pos} | total {len(check)} | "
    f"present: {any('1791031984' in l for l in check)} | all-parse OK"
)
