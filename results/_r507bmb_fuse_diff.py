import json
import subprocess


def stage(n):
    return subprocess.check_output(
        ["git", "show", f":{n}:results/crash_fuse.json"])


base = json.loads(stage(1))
ours = json.loads(stage(2))
theirs = json.loads(stage(3))

for name, d in (("base", base), ("ours", ours), ("theirs", theirs)):
    print(name, "sigs=", len(d.get("sigs", {})),
          "cleared=", len(d.get("cleared", {})))

bs, os_, ts = base.get("sigs", {}), ours.get("sigs", {}), theirs.get("sigs", {})
bc, oc, tc = (base.get("cleared", {}), ours.get("cleared", {}),
              theirs.get("cleared", {}))
print("ours-only sigs:", sorted(set(os_) - set(ts) - set(bs))[:8])
print("theirs-only sigs:", sorted(set(ts) - set(os_) - set(bs))[:8])
print("both-changed sigs:", sorted(
    (set(os_) & set(ts)) - {k for k in (set(os_) & set(ts))
                            if os_[k] == ts[k] or bs.get(k) == os_[k]
                            or bs.get(k) == ts[k]}))
print("ours-only cleared:", sorted(set(oc) - set(tc) - set(bc))[:6])
print("theirs-only cleared:", sorted(set(tc) - set(oc) - set(bc))[:6])
for k in sorted(set(oc) & set(tc)):
    if oc[k] != tc[k] and bc.get(k) != oc[k] and bc.get(k) != tc[k]:
        print("both-changed cleared:", k)
        print("  ours:", oc[k])
        print("  theirs:", tc[k])
