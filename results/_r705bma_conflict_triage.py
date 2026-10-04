"""r705 bm-a rebase-conflict triage: inspect the two potentially
append-only faces (x2_watch_log.jsonl, token_usage.json) before
resolving the 18-UU deterministic-regen batch.

Rebase stage semantics (r351 law check): during rebase replay
  stage 2 (ours)   = origin side (bm-c r505/r506)
  stage 3 (theirs) = my round-705 commit
"""
import subprocess

def stage_blob(path, n):
    r = subprocess.run(["git", "show", f":{n}:{path}"],
                       capture_output=True)
    return r.stdout

for path in ("results/x2_watch_log.jsonl", "results/token_usage.json"):
    o = stage_blob(path, 2)
    t = stage_blob(path, 3)
    print("=" * 60)
    print(path)
    print("  stage2 (origin/bm-c) bytes:", len(o), "lines:", o.count(b"\n"))
    print("  stage3 (mine r705)   bytes:", len(t), "lines:", t.count(b"\n"))
    # is stage3 a strict superset of stage2 (pure append)?
    if o and t:
        print("  stage3 starts with stage2:", t.startswith(o))
        print("  stage3 tail extra:", len(t) - len(o), "bytes")
    o_lines = set(o.splitlines())
    t_lines = set(t.splitlines())
    print("  s2-only lines:", len(o_lines - t_lines),
          "| s3-only lines:", len(t_lines - o_lines))
    both = o_lines & t_lines
    print("  common lines:", len(both))
    for ln in sorted(o_lines - t_lines)[:3]:
        print("   s2only:", ln[:150])
    for ln in sorted(t_lines - o_lines)[:3]:
        print("   s3only:", ln[:150])
