# -*- coding: utf-8 -*-
# r661 bm-c pick-2 resolve: satengine live faces, ours(stage2)=newest live tick
# folded into pick-1 vs theirs(stage3)=older absorbed tick -> live-wins ours,
# judged by content ts with assert (r648 law), receipt appended.
import json, re, subprocess, os
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CNW = 0x08000000
ISO = re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")

def blob(stage, path):
    r = subprocess.run(["git", "cat-file", "-p", ":%d:%s" % (stage, path)],
                       capture_output=True, creationflags=CNW)
    assert r.returncode == 0
    return r.stdout

def ts_of(b):
    m = ISO.findall(b.decode("utf-8", "replace"))
    return max(m).replace("T", " ")[:19] if m else None

rec = {"probe": "r661 bm-c pick-2 satengine live-wins", "faces": {}}
for path in ("results/saturation_engine/face_bm-c.json",
             "results/saturation_engine_state.bm-c.json"):
    b2, b3 = blob(2, path), blob(3, path)
    t2, t3 = ts_of(b2), ts_of(b3)
    assert t2 and t3, (path, t2, t3)
    assert t2 >= t3, "live-wins violated: ours %s < theirs %s (%s)" % (t2, t3, path)
    with open(path, "wb") as fh:
        fh.write(b2)          # ours = newest engine live state
    r = subprocess.run(["git", "add", "--", path], capture_output=True,
                       creationflags=CNW)
    assert r.returncode == 0
    rec["faces"][path] = {"policy": "live-wins ours (newest engine tick)",
                         "ts_ours": t2, "ts_theirs": t3}
    print("pick2 resolved %s ours=%s theirs=%s" % (path, t2, t3))

P = r"results\_r661bmc_rebase_resolve.json"
d = json.load(open(P, encoding="utf-8"))
d["pick2_satengine_live_wins"] = rec
json.dump(d, open(P, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
print("receipt updated")
