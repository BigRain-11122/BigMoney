# -*- coding: utf-8 -*-
# r632 bm-a push-collision resolver (15 UU on pick e959dc3f0, onto f06abc65f)
# Recipes: ALL_FACES via scripts/merge_lane_views.py resolve (single source, parse-verified);
# REPORT/LIVE twins deep-ts take-new with SAME-SIDE coupling; attrition scan R216 take-new;
# CODELY.md memory-union (base-prefix assertion + direct concat suffixes).
import subprocess, sys, io, os, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

def git(args):
    r = subprocess.run(["git"] + args, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("git %s rc=%d :: %s" % (args[:2], r.returncode, r.stderr.decode("utf-8", "replace")[:200]))
    return r.stdout

def stage(path, n):
    return git(["show", ":%d:%s" % (n, path)])

TS_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[ T]?\d{2}:\d{2}")

def deep_ts(obj, best=""):
    """Deep-scan for wall-clock ts values (any key, value matches ^20xx-..); return max found."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and TS_RE.match(v):
                if v > best:
                    best = v
            else:
                best = deep_ts(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = deep_ts(v, best)
    return best

# 1) ALL_FACES via merge_lane_views resolve (single-source recipe; tool-supported faces only)
ALL_FACES = [
    "results/compute_audit.json",
    "results/regime_state.json",
    "results/update_status.json",
    "results/lhb_update_status.json",
    "results/futures_update_status.json",
]
# snapshot faces NOT in tool's ALL_FACES table -> manual deep-ts take-new below
SNAPSHOTS = [
    "results/fundamental_b_layer_filter.json",
    "results/token_usage.json",
    "results/_attrition_guard_scan.json",
]
for p in ALL_FACES:
    r = subprocess.run([sys.executable, "scripts/merge_lane_views.py", "resolve", p],
                       capture_output=True, encoding="utf-8", errors="replace")
    print("[resolve] %s rc=%d :: %s" % (p, r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()[:150]))
    json.load(open(p, encoding="utf-8"))  # parse-verify after resolve
print("ALL_FACES resolve done + parse-verified")

# 2) Twins: deep-ts take-new, SAME SIDE for .json + .md (and latest pointers follow the dated pair)
def side_ts(json_bytes):
    try:
        return deep_ts(json.loads(json_bytes.decode("utf-8")))
    except Exception:
        return ""

PAIRS = [
    ("docs/daily_report/REPORT-2026-10-03.json", "docs/daily_report/REPORT-2026-10-03.md"),
    ("docs/live_usage/LIVE-2026-10-03.json", "docs/live_usage/LIVE-2026-10-03.md"),
    ("docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"),
]
for jp, mp in PAIRS:
    j2, j3 = stage(jp, 2), stage(jp, 3)
    m2, m3 = stage(mp, 2), stage(mp, 3)
    t2, t3 = side_ts(j2), side_ts(j3)
    side = 3 if t3 >= t2 else 2  # take local on tie is wrong in rebase (origin=:2:); use >=? -> newer wins; tie -> origin side (:2:) per r140 same-second tie -> HEAD... in rebase HEAD==origin side, so tie -> :2:
    if t3 > t2:
        side = 3
    else:
        side = 2
    jb, mb = (j3, m3) if side == 3 else (j2, m2)
    print("[twin] %s :: origin_ts=%s local_ts=%s -> side %s" % (jp, t2 or "NONE", t3 or "NONE", "local" if side == 3 else "origin"))
    open(jp, "wb").write(jb)
    open(mp, "wb").write(mb)
    json.loads(jb.decode("utf-8"))  # parse-verify json twin
print("twins done (same-side coupling enforced)")

# 3) snapshot faces (tool-unsupported + per-run R216): deep-ts take-new
for p in SNAPSHOTS:
    s2, s3 = stage(p, 2), stage(p, 3)
    t2, t3 = side_ts(s2), side_ts(s3)
    sb = s3 if t3 > t2 else s2
    print("[snapshot] %s :: origin_ts=%s local_ts=%s -> %s" % (p, t2 or "NONE", t3 or "NONE", "local" if sb is s3 else "origin"))
    open(p, "wb").write(sb)
    json.loads(sb.decode("utf-8"))

# 4) CODELY.md memory-union: base prefix identity + direct concat suffixes
p = "CODELY.md"
b1, b2, b3 = stage(p, 1), stage(p, 2), stage(p, 3)
if b2.startswith(b1) and b3.startswith(b1):
    new = b2 + b3[len(b1):]
    print("[codely] prefix-identity holds; union = base %dB + origin-suffix %dB + local-suffix %dB = %dB" % (
        len(b1), len(b2) - len(b1), len(b3) - len(b1), len(new)))
else:
    # in-place edit path: entry-level bidirectional coverage (r327/r329)
    l1 = b1.decode("utf-8", "replace").splitlines()
    l2 = b2.decode("utf-8", "replace").splitlines()
    l3 = b3.decode("utf-8", "replace").splitlines()
    s2, s3 = set(l2), set(l3)
    missing_in_2 = [x for x in l3 if x not in s2 and x not in set(l1)]
    missing_in_3 = [x for x in l2 if x not in s3 and x not in set(l1)]
    # preserve both sides' appended entries verbatim: origin first, then local-only
    new_lines = l2 + [x for x in l3 if x not in s2]
    new = ("\n".join(new_lines) + ("\n" if b3.endswith(b"\n") else "")).encode("utf-8")
    print("[codely] prefix FAIL -> entry-level coverage union; origin-only=%d local-only=%d" % (len(missing_in_2), len(missing_in_3)))
open(p, "wb").write(new)
# verify: every side line present
chk = open(p, "rb").read().decode("utf-8", "replace")
for tag, blob in ((":2:", b2), (":3:", b3)):
    miss = [x for x in blob.decode("utf-8", "replace").splitlines() if x.strip() and x not in chk]
    if miss:
        print("[codely][WARN] %s missing %d lines after union: %s" % (tag, len(miss), str(miss[:2])[:120]))
        sys.exit(2)
print("[codely] zero-loss verify PASS (both sides' lines all present)")

# 5) stage resolved files
paths = ALL_FACES + SNAPSHOTS + [x for pr in PAIRS for x in pr] + ["CODELY.md"]
git(["add"] + paths)
print("resolver complete: %d files resolved + staged" % len(paths))
