import json
import subprocess


def blob(rev, path):
    r = subprocess.run(["git", "show", "%s:%s" % (rev, path)],
                       capture_output=True, cwd=".")
    return r.stdout


# --- 1. theirs CODELY: pointer line for migrated r453 receipt? ---
theirs_c = blob("MERGE_HEAD", "CODELY.md").decode("utf-8", errors="replace")
hits = [ln[:150] for ln in theirs_c.splitlines() if "r453" in ln]
print("theirs r453 mentions:", len(hits))
for h in hits[:6]:
    print("  ", h)

# --- 2. token_usage structure: machines sub-dict ts fields ---
oj = json.loads(blob("HEAD", "results/token_usage.json").decode("utf-8"))
tj = json.loads(blob("MERGE_HEAD", "results/token_usage.json").decode("utf-8"))
print("\ngenerated ours:", repr(oj.get("generated")))
print("generated theirs:", repr(tj.get("generated")))
om, tm_ = oj.get("machines", {}), tj.get("machines", {})
print("machines keys:", sorted(om.keys()), sorted(tm_.keys()))
for mk in sorted(set(om) | set(tm_)):
    o, t = om.get(mk), tm_.get(mk)
    same = (o == t)
    ots = o.get("ts") or o.get("generated") or o.get("updated") if isinstance(o, dict) else None
    tts = t.get("ts") or t.get("generated") or t.get("updated") if isinstance(t, dict) else None
    print("  machine %s same=%s ours_ts=%s theirs_ts=%s" % (mk, same, repr(ots), repr(tts)))
