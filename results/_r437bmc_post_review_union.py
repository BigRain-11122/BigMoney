# -*- coding: utf-8 -*-
"""r437 bm-c: resolve the 2 post_review conflicts left by _r436bmc_merge_resolve
(rebase pick-1 vs origin tip c33be51b7: bm-b r639 same-window post_review writes).
Rules: post_review.jsonl = byte-level append-only line union (exact-dup removal,
r463 precedent, no re-encode = zero line-ending churn); REPORT-20261004.md =
add/add newer-wins by embedded ts. Rebase stage semantics: :2:=origin tip,
:3:=replayed commit (rules are side-symmetric).
Validations: no line-start conflict markers, every jsonl line parses, git add ok."""
import json
import os
import re
import subprocess
import sys

CREATE = 0x08000000
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def blob(stage, path):
    p = subprocess.run(["git", "show", ":%s:%s" % (stage, path)],
                       capture_output=True, creationflags=CREATE, cwd=REPO)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.decode("utf-8", "replace")[:200])
    return p.stdout


def assert_no_markers(data):
    for ln in data.split(b"\n"):
        s = ln.strip()
        assert not (s.startswith(b"<<<<<<<") or s.startswith(b">>>>>>>") or
                    s.startswith(b"|||||||")), "marker line %r" % ln[:40]


path = "results/post_review.jsonl"
o = [l for l in blob("2", path).split(b"\n") if l.strip()]
t = [l for l in blob("3", path).split(b"\n") if l.strip()]
seen = set(o)
add = [l for l in t if l not in seen]
chosen = b"\n".join(o + add) + (b"\n" if (o or add) else b"")
assert_no_markers(chosen)
for ln in chosen.split(b"\n"):
    if ln.strip():
        json.loads(ln.decode("utf-8", "replace"))
with open(os.path.join(REPO, path), "wb") as f:
    f.write(chosen)
print("post_review.jsonl: ours=%d +%d new-theirs lines" % (len(o), len(add)))

path = "results/post_review/REPORT-20261004.md"
TS = re.compile(r"20\d{2}-\d{2}-\d{2}[T ][0-9]{2}:[0-9]{2}(?::[0-9]{2})?")


def max_ts(b):
    m = [x.group(0) for x in TS.finditer(b.decode("utf-8", "replace"))]
    return max(m) if m else None


o, t = blob("2", path), blob("3", path)
to, tt = max_ts(o), max_ts(t)
if tt and (not to or tt > to):
    chosen, side, ts = t, "theirs(new base)", tt
else:
    chosen, side, ts = o, "ours(origin tip)", to
assert_no_markers(chosen)
with open(os.path.join(REPO, path), "wb") as f:
    f.write(chosen)
print("REPORT-20261004.md: side=%s max_ts=%s" % (side, ts))

r = subprocess.run(["git", "add", "--", "results/post_review.jsonl",
                    "results/post_review/REPORT-20261004.md"],
                   capture_output=True, creationflags=CREATE, cwd=REPO)
assert r.returncode == 0, r.stderr.decode("utf-8", "replace")[:200]
print("ADDED OK")
