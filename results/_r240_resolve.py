# -*- coding: utf-8 -*-
"""R240 bm-a push-collision rebase resolver (bigmoney-conflict-resolve canonical).

Files at this step:
  results/post_review.jsonl          -> append-log: line-level union zero loss (r188/r217)
  results/post_review/REPORT-20260926.md -> generated product: take-my-side now,
     deterministic regeneration (Tools/post_review.py) closes the merge after
     the rebase completes (r157 post-hoc regeneration precedent).

Stage semantics during rebase: :2 = base/ours (origin/bm-b side), :3 = theirs
(my commit being replayed).
"""
import json
import subprocess
import sys

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"


def blob(rev, path):
    r = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True,
                       cwd=REPO)
    if r.returncode != 0:
        raise SystemExit(f"git show failed for {rev}:{path}: {r.stderr[:200]}")
    return r.stdout


P = "results/post_review.jsonl"
b2 = blob(":2", P)   # origin/bm-b side
b3 = blob(":3", P)   # my side

# EOL mirror (r223/r234 law): detect producer EOL from the base blob
crlf2 = b"\r\n" in b2
crlf3 = b"\r\n" in b3
print(f"EOL: base CRLF={crlf2} mine CRLF={crlf3}")

def to_lines(b):
    txt = b.decode("utf-8")
    txt = txt.replace("\r\n", "\n")
    return [l for l in txt.split("\n") if l.strip()]

l2, l3 = to_lines(b2), to_lines(b3)
print(f"rows: base={len(l2)} mine={len(l3)}")

# line-level union preserving order: base rows first, then mine not in base
seen = set(l2)
union = list(l2)
added = 0
for l in l3:
    if l not in seen:
        union.append(l)
        added += 1
print(f"union rows={len(union)} (added mine={added}); zero-loss check: "
      f"{len(union) == len(set(union)) and set(union) == set(l2) | set(l3)}")

# parse-verify every line (r185 law: resolve verify before write+add)
for l in union:
    json.loads(l)
print("parse-verify: all rows valid JSON")

eol = "\r\n" if (crlf2 or crlf3) else "\n"
with open(P, "w", encoding="utf-8", newline="") as f:
    f.write(eol.join(union) + eol)
subprocess.run(["git", "add", P], cwd=REPO, check=True)
print("post_review.jsonl resolved (union) + added")

# generated report: take my side (stage 3), regenerated canonically post-rebase
P2 = "results/post_review/REPORT-20260926.md"
with open(P2, "wb") as f:
    f.write(b3 if False else blob(":3", P2))
subprocess.run(["git", "add", P2], cwd=REPO, check=True)
print("REPORT-20260926.md take-mine + added (post-rebase regeneration pending)")
