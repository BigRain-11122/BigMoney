"""r668 bm-a retry merge: resolve the single UU face runnable_pool.json
(registered face, merge_lane_views resolve, origin=stage2/local=stage3)."""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = "results/runnable_pool.json"


def blob(ref):
    r = subprocess.run(["git", "show", f"{ref}:{P}"],
                       capture_output=True, cwd=ROOT)
    assert r.returncode == 0, f"git show {ref} failed"
    return r.stdout


with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f2, \
        tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f3:
    f2.write(blob("MERGE_HEAD"))
    f3.write(blob("HEAD"))
    p2, p3 = f2.name, f3.name
try:
    r = subprocess.run(
        [sys.executable, "scripts/merge_lane_views.py", "resolve", P,
         "--stage2", p2, "--stage3", p3], capture_output=True, cwd=ROOT)
    out = r.stdout.decode("utf-8", "replace")
    assert r.returncode == 0, f"resolve rc={r.returncode}: {out[-300:]}"
    print(out.strip().splitlines()[0])
finally:
    os.unlink(p2)
    os.unlink(p3)

pool = json.load(open(os.path.join(ROOT, P), encoding="utf-8"))
by_id = {e.get("id"): e for e in pool["entries"]}
tj = by_id["THEME-JUDGE-P1"]["shards"][0]
facts = {"n_entries": len(pool["entries"]),
         "theme_judge": {k: tj.get(k) for k in ("status", "owner",
                                                "owner_since")},
         "fund_value": {k: by_id["FUND-VALUE-P1-NULLS"]["shards"][0].get(k)
                        for k in ("owner", "owner_since")},
         "fund_quality": {k: by_id["FUND-QUALITY-P1-NULLS"]["shards"][0].get(k)
                          for k in ("owner", "owner_since")},
         "fund_divlowvol": {k: by_id["FUND-DIVLOWVOL-P1-NULLS"]["shards"][0]
                            .get(k) for k in ("owner", "owner_since")}}
print(json.dumps(facts, ensure_ascii=False))
raw = open(os.path.join(ROOT, P), "rb").read()
assert b"<<<<<<<" not in raw and b">>>>>>>" not in raw, "marker leak"
print("pool retry resolve: parse + marker gates PASS")
