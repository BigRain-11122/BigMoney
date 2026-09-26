# -*- coding: utf-8 -*-
"""R281 bm-a rebase resolver batch 2: post_review pair.
- results/post_review.jsonl = append-log -> line-level union zero loss
  (r188/r217).
- results/post_review/REPORT-20260927.md = snapshot (named '生成 <ts>'
  producer stamp, deterministic re-derive view) -> take NEWER whole face
  (00:50:03 theirs vs 00:30:14 ours); next post_review run regenerates
  the full view from the merged ledger either way (R208 snapshot law).
Manual classification per classifier RED (fail-closed face), documented
here for the audit trail."""


def blob(rev, path):
    import subprocess
    return subprocess.run(["git", "show", f"{rev}:{path}"],
                          capture_output=True, check=True).stdout


# -- 1) append-log union
P1 = "results/post_review.jsonl"
a = blob(":2", P1).decode("utf-8-sig").splitlines()
b = blob(":3", P1).decode("utf-8-sig").splitlines()
seen = set(a)
union = list(a)
new_b = [l for l in b if l not in seen and not (l.strip() == ""
        and l in union)]
# append-log: ours first, then theirs-only lines in original order
for l in b:
    if l not in seen:
        union.append(l)
        seen.add(l)
eol = "\r\n" if "\r\n" in blob(":2", P1).decode("utf-8-sig", "replace") \
    else "\n"
with open(P1, "w", encoding="utf-8", newline="") as fh:
    fh.write(eol.join(union) + (eol if union else ""))
print(f"post_review.jsonl: ours={len(a)} theirs={len(b)} union={len(union)}")

# -- 2) snapshot take-newer by 生成 ts
P2 = "results/post_review/REPORT-20260927.md"
ra = blob(":2", P2).decode("utf-8-sig")
rb = blob(":3", P2).decode("utf-8-sig")
import re
ta = re.search(r"生成 ([\d\-: ]+)", ra)
tb = re.search(r"生成 ([\d\-: ]+)", rb)
va = ta.group(1) if ta else ""
vb = tb.group(1) if tb else ""
winner = rb if va < vb else ra          # tie -> ours (r140)
with open(P2, "w", encoding="utf-8", newline="") as fh:
    fh.write(winner)
print(f"REPORT: ours ts={va} theirs ts={vb} -> took "
      f"{'theirs' if va < vb else 'ours'}")

# -- parse-verify (r185)
import json
for l in open(P1, encoding="utf-8-sig"):
    if l.strip():
        json.loads(l)
print("parse-verify OK")
