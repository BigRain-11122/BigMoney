# -*- coding: utf-8 -*-
"""R241 bm-a push-collision resolver #2 (second window: bm-b r241 landed mid-rebase).

Pair (same forms as R240 collision, skill canon):
  results/post_review.jsonl          append-log -> line-level union zero-loss (r188/r217)
  results/post_review/REPORT-20260926.md generated -> take-mine(:3); deterministic
     regeneration (Tools/post_review.py) post-rebase closes both machines' rows (r157).

Stage semantics: :2 = ours (bm-b r241 side), :3 = theirs (my replayed commit).
EOL mirror per base blob (r223/r234); parse-verify before add (r185).
"""
import json
import subprocess

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"


def blob(rev, path):
    r = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True,
                       cwd=REPO)
    if r.returncode != 0:
        raise SystemExit(f"git show failed {rev}:{path}: {r.stderr[:150]}")
    return r.stdout


# 1) post_review.jsonl -- line-level union
P = "results/post_review.jsonl"
b2, b3 = blob(":2", P), blob(":3", P)
crlf = (b"\r\n" in b2) or (b"\r\n" in b3)


def to_lines(b):
    return [l for l in b.decode("utf-8").replace("\r\n", "\n").split("\n")
            if l.strip()]


l2, l3 = to_lines(b2), to_lines(b3)
seen = set(l2)
union = list(l2)
added = 0
for l in l3:
    if l not in seen:
        union.append(l)
        added += 1
for l in union:
    json.loads(l)  # r185 parse-verify
eol = "\r\n" if crlf else "\n"
with open(P, "w", encoding="utf-8", newline="") as f:
    f.write(eol.join(union) + eol)
json.loads(open(P, encoding="utf-8").readline())  # smoke parse
subprocess.run(["git", "add", P], cwd=REPO, check=True)
print(f"post_review.jsonl: base {len(l2)} + mine-unique {added} -> {len(union)} "
      f"rows; zero-loss={set(union) == set(l2) | set(l3)}; EOL={'CRLF' if crlf else 'LF'}")

# 2) REPORT-20260926.md -- generated product: take mine (regen post-rebase)
P2 = "results/post_review/REPORT-20260926.md"
with open(P2, "wb") as f:
    f.write(blob(":3", P2))
subprocess.run(["git", "add", P2], cwd=REPO, check=True)
print("REPORT-20260926.md: take-mine + added (deterministic regen post-rebase)")
