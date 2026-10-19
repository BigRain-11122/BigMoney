"""r1077 bm-a pool_dualrun.bm-a.jsonl NUL-corruption heal (TREASURE s2.4 line-level union, NOT blob restore).
Disk face = 15,597 bytes 100% NUL (dead-window kill mid-write; committed corrupted in round-start baseline).
Law: treasure_guard restore rc3 -> line-level union only.
Union = origin/main lines (clean, tail 50 kept by tool) + valid disk lines (none: all NUL) -> write -> rerun reconcile.
Asserts: zero NUL bytes, every line parses as JSON, line count >= origin count.
"""
import json
import subprocess
import sys

PATH = "results/pool_dualrun.bm-a.jsonl"

r = subprocess.run(["git", "show", "origin/main:" + PATH], capture_output=True)
if r.returncode != 0:
    print("origin show FAIL", r.stderr.decode()[:200])
    sys.exit(1)
origin_lines = [ln for ln in r.stdout.decode("utf-8", errors="replace").splitlines() if ln.strip()]

disk_raw = open(PATH, "rb").read()
disk_valid = []
for ln in disk_raw.decode("utf-8", errors="replace").splitlines():
    s = ln.strip()
    if not s or "\x00" in ln:
        continue
    try:
        json.loads(s)
        disk_valid.append(s)
    except json.JSONDecodeError:
        pass

origin_set = set(origin_lines)
extra = [ln for ln in disk_valid if ln not in origin_set]
union = origin_lines + extra
with open(PATH, "w", encoding="utf-8", newline="\n") as f:
    for ln in union:
        f.write(ln + "\n")

# verify
data = open(PATH, "rb").read()
assert data.count(b"\x00") == 0, "NUL bytes remain"
n_ok = 0
for ln in data.decode("utf-8").splitlines():
    json.loads(ln)
    n_ok += 1
print(f"heal done: origin={len(origin_lines)} disk_valid={len(disk_valid)} extra={len(extra)} -> lines={n_ok} bytes={len(data)}")
if n_ok < len(origin_lines):
    print("LINE LOSS FAIL")
    sys.exit(1)
print("ASSERT-OK zero-NUL all-json")
