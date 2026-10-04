"""r696 bm-b: pool index-stage probe (stage0 merged result vs stages)."""
import subprocess


def stage(idx):
    r = subprocess.run(["git", "show", f":{idx}:results/runnable_pool.json"],
                       capture_output=True)
    if r.returncode != 0:
        return None, r.stderr.decode()[:80]
    return r.stdout, None


for i in (0, 1, 2, 3):
    b, err = stage(i)
    if b is None:
        print(f"stage{i}: ABSENT ({err})")
        continue
    txt = b.decode("utf-8", "replace")
    mark = txt.find('"id": "PERPETUAL-N2-W15-SHARD-3"')
    seg = txt[mark:mark + 800] if mark >= 0 else "NOT FOUND"
    s3_status = "done" if '"status": "done"' in seg else ("ready" if '"status": "ready"' in seg else "?")
    trio = txt.find('"id": "FUND-VALUE-P1-NULLS"')
    tseg = txt[trio:trio + 900]
    import re
    m = re.search(r'"owner_since": "([^"]+)"', tseg)
    print(f"stage{i}: bytes={len(b)} SHARD-3~{s3_status} trio_since={m.group(1) if m else '?'}")
