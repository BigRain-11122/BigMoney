"""_r458bmb_probe.py -- probe rebase stage sides for r458 resolver planning."""
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def blob(spec):
    return subprocess.run(["git", "show", spec], capture_output=True).stdout.decode("utf-8", errors="replace")


WALL = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")


def deep_ts(obj):
    best = ""
    def scan(o):
        nonlocal best
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, (str, int, float)):
                    nk = str(k).lower().replace("_", "").replace("-", "")
                    if any(p in nk for p in ("ts", "generated", "updated", "asof",
                                             "attempt", "scanned", "written")):
                        s = str(v)
                        if WALL.match(s) and s > best:
                            best = s
                else:
                    scan(v)
        elif isinstance(o, list):
            for it in o:
                scan(it)
    scan(obj)
    return best


print("== fundamental_status.json ts probe ==")
for side in (":2:", ":3:"):
    d = json.loads(blob(side + "results/fundamental_status.json"))
    print(side, "ts=", deep_ts(d), "| rc=", d.get("rc"), "| snapshot_ts=", d.get("snapshot_ts", "?"),
          "| n_rows=", d.get("n_rows"), "| keys:", list(d.keys())[:8])

print()
print("== CODELY.md delta scale ==")
base = blob(":1:CODELY.md").splitlines()
oc = blob(":2:CODELY.md").splitlines()
mine = blob(":3:CODELY.md").splitlines()
for name, other in (("origin", oc), ("mine", mine)):
    tb = list(base)
    added = []
    for ln in other:
        if ln in tb:
            tb.remove(ln)
        else:
            added.append(ln)
    print(name, "size", len(blob((':2:' if name == 'origin' else ':3:') + 'CODELY.md').encode('utf-8')),
          "| added", len(added), "| dropped", len(tb))
    for ln in added[:12]:
        print("   +", ln[:100])
    for ln in tb[:12]:
        print("   -", ln[:100])

print()
print("== full UU list ==")
r = subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"], capture_output=True, text=True)
print(r.stdout)
