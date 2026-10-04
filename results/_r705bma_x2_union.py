"""r705 bm-a rebase conflict resolve: x2_watch_log.jsonl append-only
union (r630 three-way law applied to stage blobs -- both sides appended
their own live_paper run's watch rows: bm-c 00:41 batch + bm-a 01:09
batch; union = common 2922 + 6 + 6, chronological by ts, exact-dup
dedupe). Writes the worktree file, caller git-adds it."""
import json
import subprocess


def stage_lines(n):
    r = subprocess.run(["git", "show", f":{n}:results/x2_watch_log.jsonl"],
                       capture_output=True)
    return r.stdout.decode("utf-8", "replace").splitlines()


s2 = [l for l in stage_lines(2) if l.strip()]
s3 = [l for l in stage_lines(3) if l.strip()]
seen = set()
rows = []
for line in s2 + s3:
    if line in seen:
        continue
    seen.add(line)
    try:
        rows.append((json.loads(line).get("ts", ""), line))
    except Exception:
        rows.append(("", line))
rows.sort(key=lambda x: x[0])
out = "\n".join(l for _, l in rows) + "\n"
with open("results/x2_watch_log.jsonl", "w", encoding="utf-8",
          newline="\n") as f:
    f.write(out)
print(f"union: s2={len(s2)} s3={len(s3)} -> out={len(rows)} rows, "
      f"dup-dropped={len(s2) + len(s3) - len(rows)}")
# verify: every stage line present in output
outset = set(out.splitlines())
assert all(l in outset for l in s2), "stage2 row lost"
assert all(l in outset for l in s3), "stage3 row lost"
print("zero-loss assertion PASS (every stage row present)")
