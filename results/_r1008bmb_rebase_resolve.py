# -*- coding: utf-8 -*-
# r1008 bm-b rebase-conflict resolution: token_usage.json per-machine union (bm-b=mine newer 16:32,
# other machines=origin side freshest), all other conflicted shared regen faces resolved by caller
# via checkout --theirs (whole-file regen, my 16:29-16:33 runs newer than bm-c dead-window 16:08).
import subprocess, json, io

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"

def stage(n):
    out = subprocess.run(["git", "show", ":%d:results/token_usage.json" % n],
                         capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
    if out.returncode != 0:
        raise SystemExit("stage %d read failed: %s" % (n, out.stderr[:200]))
    return json.loads(out.stdout)

ours = stage(2)    # upstream/origin side (bm-c r1094 16:08 landed rows)
theirs = stage(3)  # my r1008 commit side (bm-b 16:32 rows)

print("ours top keys:", sorted(ours.keys()))
print("theirs top keys:", sorted(theirs.keys()))
om = ours.get("machines", {})
tm = theirs.get("machines", {})
def _sig(v):
    if isinstance(v, dict):
        for k in ("ts", "updated", "generated", "last_run"):
            if k in v:
                return "%s=%s" % (k, v[k])
        return "keys:" + ",".join(list(v.keys())[:4])
    return str(v)[:40]
print("ours machines:", {k: _sig(v) for k, v in om.items()})
print("theirs machines:", {k: _sig(v) for k, v in tm.items()})

m = dict(theirs)  # top-level scalars from my newer run (generated/per_round_context)
mach = {}
for k, v in om.items():
    mach[k] = v          # origin-side = freshest for non-bm-b machines
for k, v in tm.items():
    if k == "bm-b" or k not in mach:
        mach[k] = v      # bm-b rows = my run; unknown keys = mine
m["machines"] = mach

# any other per-machine-keyed dicts union the same way (defensive)
for key in theirs:
    if key in ("machines", "generated", "per_round_context"):
        continue
    ov, tv = ours.get(key), theirs.get(key)
    if isinstance(tv, dict) and isinstance(ov, dict) and all(isinstance(x, str) for x in list(tv.keys())[:6]) and any(str(x).startswith("bm-") for x in tv.keys()):
        u = dict(ov)
        for k, v in tv.items():
            if k == "bm-b" or k not in u:
                u[k] = v
        m[key] = u
    else:
        m[key] = tv  # default = my side (newer run)

with io.open(ROOT + r"\results\token_usage.json", "w", encoding="utf-8") as f:
    json.dump(m, f, ensure_ascii=False, indent=2)
    f.write("\n")
print("RESOLVED token_usage.json union: machines =", sorted(mach.keys()))
