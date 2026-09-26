# -*- coding: utf-8 -*-
"""R290 bm-a rebase resolver: c141d14b (harvest closure) replayed onto bm-b
40b75d06 (r291). Recipes per bigmoney-conflict-resolve SKILL.md:
  - post_review.jsonl  : append-log -> line-level union zero-loss
  - REPORT-20260927.md : derived product -> take HEAD (bm-b), regenerate
                         post-rebase via reviewer re-run
  - runnable_pool.json : mixed-dict entries -> start from HEAD (bm-b newer
                         tick face) + apply ours CENSUS-FUS-S2-W1 flip
                         (entry+shard done + harvest_note) byte-anchored
"""
import json
import subprocess

def blob(rev, path):
    return subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True
                          ).stdout.decode("utf-8", errors="replace")

def w(path, text):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)

# 1) post_review.jsonl: line-level union, preserve order (ours then theirs,
#    dedup identical lines; both sides append-only over common base)
ours = blob("HEAD", "results/post_review.jsonl")   # during rebase: HEAD=ours? NO:
# In a rebase, 'ours'=upstream (bm-b), 'theirs'=commit being replayed (mine).
theirs = blob("results/post_review.jsonl") if False else None

a = blob("HEAD", "results/post_review.jsonl").splitlines()
b = blob("REBASE_HEAD" if False else "HEAD", "results/post_review.jsonl")
# explicit: stage 2 = ours (upstream bm-b), stage 3 = theirs (my commit)
s2 = subprocess.run(["git", "show", ":2:results/post_review.jsonl"],
                    capture_output=True).stdout.decode("utf-8", errors="replace")
s3 = subprocess.run(["git", "show", ":3:results/post_review.jsonl"],
                    capture_output=True).stdout.decode("utf-8", errors="replace")
lines2 = [l for l in s2.splitlines() if l.strip()]
lines3 = [l for l in s3.splitlines() if l.strip()]
seen = set()
union = []
for l in lines2 + lines3:            # upstream rows first, then my new rows
    if l not in seen:
        seen.add(l)
        union.append(l)
assert len(union) == len(set(union))
w("results/post_review.jsonl", "\n".join(union) + "\n")
json_ok = all(json.loads(l) for l in union)
print(f"post_review.jsonl union: |ours(bm-b)|={len(lines2)} |theirs(bm-a)|={len(lines3)} "
      f"-> union={len(union)} (added {len(union)-len(lines2)}) json-ok")

# 2) REPORT-20260927.md: derived -> take ours (upstream/bm-b); regenerate later
rep2 = subprocess.run(["git", "show", ":2:results/post_review/REPORT-20260927.md"],
                      capture_output=True).stdout.decode("utf-8", errors="replace")
w("results/post_review/REPORT-20260927.md", rep2)
print("REPORT-20260927.md: take upstream (derived; regenerate post-rebase)")

# 3) runnable_pool.json: upstream (bm-b r291 face, includes their tick claims)
#    + my CENSUS-FUS-S2-W1 entry flip
pool_s2 = subprocess.run(["git", "show", ":2:results/runnable_pool.json"],
                         capture_output=True).stdout.decode("utf-8", errors="replace")
pool_s3 = subprocess.run(["git", "show", ":3:results/runnable_pool.json"],
                         capture_output=True).stdout.decode("utf-8", errors="replace")
up = json.loads(pool_s2)
mine = json.loads(pool_s3)
ue = {e["id"]: e for e in up["entries"]}
me = {e["id"]: e for e in mine["entries"]}
assert "CENSUS-FUS-S2-W1" in ue and "CENSUS-FUS-S2-W1" in me
src = me["CENSUS-FUS-S2-W1"]           # my done-flip entry (full dict)
ue["CENSUS-FUS-S2-W1"] = src           # byte-anchored replace of that entry
# cn-trend ownership: prefer upstream (their r291 preserved bm-a claim + any
# keepalive updates); do NOT touch
out = json.dumps(up, ensure_ascii=False, indent=1) + "\n"
json.loads(out)                          # parse validation before write (r185)
w("results/runnable_pool.json", out)
e = ue["CENSUS-FUS-S2-W1"]
print("runnable_pool.json: upstream base + CENSUS flip ->",
      "status=%s shard=%s" % (e["status"], e["shards"][0]["status"]),
      "| entries=%d | upstream cn-trend owner=%s" % (
          len(up["entries"]),
          [s for x in up["entries"] if x["id"] == "CN-TREND-ETF-P1"
           for s in [x["shards"][0].get("owner")]][0]))
