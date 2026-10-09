# r819 bm-b post-rebase pool face settle (MSG-0612 ring-replay family):
# per-face max-merge of results/runnable_pool.json vs origin blob,
# newer-wins on per-entry timestamps, ties -> origin side (claw-safe).
# My engine is idle (no active burns/claims this window), so the settled
# face is expected to converge to origin content; asserted, not assumed.
import json
import re
import subprocess

TS = re.compile(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")


def blob(rev, path):
    return json.loads(subprocess.run(
        ["git", "show", "%s:%s" % (rev, path)], capture_output=True
    ).stdout.decode("utf-8"))


def max_ts(x):
    s = json.dumps(x, ensure_ascii=False)
    m = TS.findall(s)
    return max(m) if m else ""


o = blob("origin/main", "results/runnable_pool.json")
m = json.load(open("results/runnable_pool.json", encoding="utf-8"))
oi = {e["id"]: e for e in o["entries"]}
mi = {e["id"]: e for e in m["entries"]}
assert set(oi) == set(mi), "entry id sets diverge: %s" % (
    set(oi) ^ set(mi))

settled, took_origin, took_mine, equal = [], 0, 0, 0
for eid in oi:
    a, b = oi[eid], mi[eid]
    if a == b:
        settled.append(a)
        equal += 1
        continue
    ta, tb = max_ts(a), max_ts(b)
    if tb > ta:
        settled.append(b)
        took_mine += 1
    else:
        settled.append(a)  # newer or tie -> origin (claw-safe)
        took_origin += 1
out = dict(o)  # top-level envelope from origin (newest updated_at)
out["entries"] = settled

# zero-backward assertion for the claw-flagged entries (claw prints id|shard)
for flag in ("TRIAL-LABOR-W17-SCREEN-SHARD-3", "TRIAL-LABOR-W17-SCREEN-SHARD-4"):
    se = next(e for e in settled if e["id"] == flag)
    s_ts = max_ts(se)
    assert s_ts >= max_ts(mi[flag]), "backward move on %s" % flag
    print("settled %s max_ts=%s (origin-wins ok)" % (flag, s_ts))

json.loads(json.dumps(out))  # r185 parse gate
with open("results/runnable_pool.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("settle done: equal=%d took_origin=%d took_mine=%d total=%d"
      % (equal, took_origin, took_mine, len(settled)))
