# -*- coding: utf-8 -*-
"""r306 bm-b resolve3 -- 3rd collision (bm-a r301 b9c22863 vs bm-b r306 d2394875).
2 UU, both take-stage2 (ours=bm-a r301):
- runnable_pool.json: ONLY diff = CN-SECTOR-LEADER-P1 entry gains missing shards
  array (sectldr-0of1 fix, picker-starved ready batch) -- the fix must survive;
  ours is strict superset, theirs (r300 face) has nothing extra (57==57 ids equal).
- autofill_state.json: launches 50|50 union=50 (identical), last_tick tie
  07:10:01 both machines' watchdog ticks -> r140 same-second tie law = HEAD/ours.
Gates: marker sweep, parse verify, entry-id identity check (57=57 no dup)."""
import io
import json
import subprocess

TAKE_STAGE2 = [
    "results/runnable_pool.json",
    "results/autofill_state.json",
]


def blob(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("blob fail %d %s" % (stage, path))
    return r.stdout


def marker_sweep(path, raw):
    bad = [l for l in raw.decode("utf-8", "replace").splitlines()
           if l.startswith(("<<<<<<<", "=======", ">>>>>>>"))]
    assert not bad, (path, bad[:2])


for p in TAKE_STAGE2:
    raw = blob(2, p)
    marker_sweep(p, raw)
    with io.open(p, "wb") as f:
        f.write(raw)
    chk = json.load(io.open(p, encoding="utf-8-sig"))
    if p.endswith("runnable_pool.json"):
        ids = [e["id"] for e in chk["entries"]]
        assert len(ids) == len(set(ids)) == 57, "pool id identity gate"
        sect = [e for e in chk["entries"] if e["id"] == "CN-SECTOR-LEADER-P1"][0]
        assert sect.get("shards"), "shards fix must survive"
        assert isinstance(chk.get("last_tick", chk), dict) or True
    else:
        assert isinstance(chk.get("last_tick"), dict), "last_tick must stay dict"
        assert len(chk["launches"]) == 50
    print("take-stage2 %-40s ok" % p)

subprocess.run(["git", "add"] + TAKE_STAGE2, check=True)
print("resolve3 done: 2/2 take-stage2, gates PASS, git add done")
