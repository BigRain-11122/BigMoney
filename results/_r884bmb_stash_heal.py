# -*- coding: utf-8 -*-
"""r884 bm-b stash-pop heal (r642 assert-before-drop + r570 row-union + r747 G4' live-wins).

Facts (probed):
- history_bm-b.jsonl: HEAD has 14:50:07 -> 14:57:07 gap; stash holds the 5 unique
  tick lines 14:52-14:56 (14:51 tick never written anywhere, disclosed). Heal =
  chronological line-union of HEAD + stash-only lines.
- runnable_pool.bm-b.json: stash-applied worktree (14:56:09) is NEWER than HEAD
  (14:46:09) => keep worktree (G4' live-wins), do NOT checkout HEAD over it.
- other 5 faces: HEAD newer (15:03-15:04 live absorb) => caller checkout HEAD.
This script ONLY does the history union write + two-side superset assertion.
"""
import subprocess, sys, json, re, io

REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
PATH = "results/saturation_engine/history_bm-b.jsonl"
WT = REPO + r"\results\saturation_engine\history_bm-b.jsonl"
TS_RE = re.compile(r'"(?:tick_ts|ts)"\s*:\s*"(20\d{2}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})')

def git(*a):
    r = subprocess.run(["git", "-C", REPO] + list(a), capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("git rc=%d %s" % (r.returncode, r.stderr[:200]))
    return r.stdout.decode("utf-8", "replace")

def ts_of(line):
    m = TS_RE.search(line)
    return m.group(1) if m else "0000-00-00T00:00:00"

h_lines = [l for l in git("show", "HEAD:" + PATH).splitlines() if l.strip()]
s_lines = [l for l in git("show", "stash@{0}:" + PATH).splitlines() if l.strip()]
h_set, s_set = set(h_lines), set(s_lines)
only_s = [l for l in s_lines if l not in h_set]

# chronological stable union: HEAD lines in order, stash-only lines inserted by ts
merged = list(h_lines)
inserts = sorted(only_s, key=ts_of)
for line in inserts:
    pos = len(merged)
    for i, ex in enumerate(merged):
        if ts_of(ex) > ts_of(line):
            pos = i
            break
    merged.insert(pos, line)

m_set = set(merged)
assert m_set >= h_set, "union lost HEAD lines"
assert m_set >= s_set, "union lost stash lines"
assert len(merged) == len(h_lines) + len(inserts), "line count mismatch"

out = ("\n".join(merged) + "\n").encode("utf-8")
with open(WT, "wb") as f:
    f.write(out)
reread = open(WT, "rb").read()
assert reread == out, "write-back mismatch"

print("HISTORY-UNION head=%d stash=%d inserted=%d merged=%d" % (
    len(h_lines), len(s_lines), len(inserts), len(merged)))
print("INSERTED-TS:", [ts_of(l) for l in inserts])
print("GAP-DISCLOSURE: tick 14:51:07 absent in both HEAD and stash (never written)")
print("SUPerset-ASSERT: PASS both sides")
sys.exit(0)
