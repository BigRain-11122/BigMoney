# -*- coding: utf-8 -*-
# r518 bm-b rebase conflict resolution (r505/r294/r315 canon)
import subprocess, json, re, os

os.chdir(r"C:\Fluxgroup\FluxGroup\quant\bigmoney")
unmerged = subprocess.check_output(["git", "diff", "--name-only", "--diff-filter=U"]).decode().strip().splitlines()
print("unmerged n =", len(unmerged))

APPEND_UNION = {"results/pool_core_samples.jsonl"}
THEIRS = [f for f in unmerged
          if f not in APPEND_UNION and f != "CODELY.md" and f != "results/x2_watch_log.jsonl"]

# --- 1) idempotent same-day derive faces: take origin side (bm-a r531/532 same-window host regen) ---
for f in THEIRS:
    subprocess.run(["git", "checkout", "--theirs", f], check=True)
    subprocess.run(["git", "add", f], check=True)
print("theirs-taken:", len(THEIRS))

# --- 2) CODELY.md: real-conflict-block union, chronological ---
raw = open("CODELY.md", "rb").read().decode("utf-8")
lines = raw.split("\n")
strip = lambda l: l.rstrip("\r")
# real marker lines only (line-anchored, CR-tolerant)
real = [i for i, l in enumerate(lines) if strip(l).startswith("<<<<<<< ") or strip(l).startswith(">>>>>>> ")]
sep = [i for i, l in enumerate(lines) if strip(l) == "======="]
print("real marker lines:", real, "separators:", len(sep))
assert len(real) == 2, "expect exactly one conflict block (open+close)"
open_i = real[0]
close_i = real[1]
seps = [i for i in sep if open_i < i < close_i]
assert len(seps) == 1, f"expect 1 separator inside block, got {seps}"
mid = seps[0]
head_side = lines[open_i + 1:mid]        # during rebase HEAD = origin/incoming (bm-a r531+r532)
mine_side = lines[mid + 1:close_i]      # my r518 entry
# union chronological: mine (r518 19:0x) first, then head (r531/r532 19:1x)
assert any("r518 bm-b" in l for l in mine_side), "my r518 entry not found in mine side"
assert any("r531 bm-a" in l for l in head_side), "bm-a r531 entry not found in head side"
resolved = lines[:open_i] + mine_side + head_side + lines[close_i + 1:]
out = "\n".join(resolved)
# assertions: no line-anchored markers remain; both sides' entries present
for l in resolved:
    s = strip(l)
    assert not (s.startswith("<<<<<<< ") or s.startswith(">>>>>>> ") or s == "======="), f"marker remains: {l[:80]}"
assert "r518 bm-b" in out and "r531 bm-a" in out and "r532 bm-a" in out, "union lost an entry"
open("CODELY.md", "w", encoding="utf-8", newline="").write(out)
subprocess.run(["git", "add", "CODELY.md"], check=True)
print("CODELY union done: mine r518 + head r531/r532")

# --- 3) x2_watch_log.jsonl: content-dedup union, stable sort by ts (append-only, r294 domain law) ---
o = subprocess.check_output(["git", "show", ":2:results/x2_watch_log.jsonl"]).decode().splitlines()
m = subprocess.check_output(["git", "show", ":3:results/x2_watch_log.jsonl"]).decode().splitlines()
o_set, m_set = set(o), set(m)
union = [l for l in o] + [l for l in m if l not in o_set]
def ts_key(l):
    mt = re.search(r'"ts": "([^"]+)"', l)
    return mt.group(1) if mt else ""
union.sort(key=ts_key)  # stable: equal ts keeps origin-first order
assert set(union) == o_set | m_set, "content union loss"
assert len(union) == len(o_set | m_set), "dedup count mismatch"
with open("results/x2_watch_log.jsonl", "w", encoding="utf-8", newline="") as f:
    f.write("\n".join(union) + "\n")
subprocess.run(["git", "add", "results/x2_watch_log.jsonl"], check=True)
print("x2 union:", len(o), "+", len(m), "->", len(union), "(zero content loss)")

# --- 4) pool_core_samples.jsonl: content-dedup union (append-only; no sort -- entry order semantic) ---
o = subprocess.check_output(["git", "show", ":2:results/pool_core_samples.jsonl"]).decode().splitlines()
m = subprocess.check_output(["git", "show", ":3:results/pool_core_samples.jsonl"]).decode().splitlines()
o_set = set(o)
union = [l for l in o] + [l for l in m if l not in o_set]
assert set(union) == set(o) | set(m)
with open("results/pool_core_samples.jsonl", "w", encoding="utf-8", newline="") as f:
    f.write("\n".join(union) + ("\n" if union else ""))
subprocess.run(["git", "add", "results/pool_core_samples.jsonl"], check=True)
print("pool_core_samples union:", len(o), "+", len(m), "->", len(union))

rem = subprocess.check_output(["git", "diff", "--name-only", "--diff-filter=U"]).decode().strip()
print("remaining unmerged:", repr(rem))
