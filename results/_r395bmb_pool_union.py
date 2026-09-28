# r395 bm-b rebase stop resolve v2: SURGICAL overlay (keep base lane_owner; apply only my flip deltas)
# lesson from failed v1: generic field-diff clobbered origin's newer lane_owner fix with my stale null.
import json, io, os, subprocess, sys

ROOT = r"C:\Users\Administrator\Desktop\Bigmoney"
PATH = "results/runnable_pool.json"
MARKERS = ("<<<<<<<", "=======", ">>>>>>>")

def side(stage):
    r = subprocess.run(["git", "show", f":{stage}:{PATH}"], cwd=ROOT,
                       capture_output=True)
    assert r.returncode == 0, r.stderr.decode()[:200]
    raw = r.stdout.decode("utf-8")
    for m in MARKERS:
        assert m not in raw, f"marker {m} in stage {stage}"
    return json.loads(raw)

base = side(2)   # origin line (bm-c lane_owner=bm-b routing fix state)
mine = side(3)   # my d0026fc7 done-flips state

bent = {e.get("id"): e for e in base.get("entries", [])}
ment = {e.get("id"): e for e in mine.get("entries", [])}

def note_delta(eid):
    """my appended note segment starting from my r395 marker, else ''"""
    mn = ment.get(eid, {}).get("note") or ""
    tag = "r395 bm-b"
    i = mn.find("| " + tag)
    return mn[i:] if i >= 0 else ""

def overlay_shard(eid, key):
    be = bent[eid]
    ms = next(s for s in ment[eid]["shards"] if s.get("key") == key)
    bs = next(s for s in be["shards"] if s.get("key") == key)
    for f in ("status", "result_ref", "owner", "owner_since"):
        if ms.get(f) is not None and bs.get(f) != ms[f]:
            bs[f] = ms[f]
    nd = note_delta(eid)
    if nd and nd not in (be.get("note") or ""):
        be["note"] = (be.get("note") or "") + " | " + nd

# W4-JUDGE: shard flip only -- entry status + lane_owner STAY base (routing fix preserved)
overlay_shard("TRIAL-LABOR-W4-JUDGE", "judge-0of1")
# SENTIMENT: entry done + shard done + note
se_be, se_me = bent["SENTIMENT-AXES-FULLHIST-P1"], ment["SENTIMENT-AXES-FULLHIST-P1"]
se_be["status"] = se_me.get("status", se_be.get("status"))
overlay_shard("SENTIMENT-AXES-FULLHIST-P1", "derive-0of1")
# updated_at: later wins
if (mine.get("updated_at") or "") > (base.get("updated_at") or ""):
    base["updated_at"] = mine["updated_at"]

# fail-closed sanity
w4 = bent["TRIAL-LABOR-W4-JUDGE"]
se = bent["SENTIMENT-AXES-FULLHIST-P1"]
assert w4.get("lane_owner") == "bm-b", "routing fix lost"
assert w4["shards"][0].get("status") == "done", "w4 shard flip lost"
assert "461/461" in (w4["shards"][0].get("result_ref") or ""), "w4 result_ref lost"
assert se.get("status") == "done" and se["shards"][0].get("status") == "done"
# entries count conservation
assert len(base["entries"]) >= len(mine["entries"]) - 1, "entries lost"

out = os.path.join(ROOT, PATH.replace("/", os.sep))
tmp = out + ".tmp"
with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(base, f, ensure_ascii=False, indent=1)
    f.write("\n")
os.replace(tmp, out)
# post-write marker scan + json self-check (r393 law: marker-scan assert before add)
raw = io.open(out, "r", encoding="utf-8").read()
for m in MARKERS:
    assert m not in raw, f"marker {m} in resolved file"
json.loads(raw)
print("UNION_OK_SURGICAL w4.lane_owner=", w4.get("lane_owner"),
      "w4.shard=", w4["shards"][0]["status"], "sent=", se.get("status"),
      "entries=", len(base["entries"]))
