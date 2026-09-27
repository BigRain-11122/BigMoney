# results/_r384bma_resolve.py -- r384 push-storm closeout (bm-a, 10-UU batch)
# 6 ALL_FACES already resolved in-shell via `merge_lane_views.py resolve` (r381 law:
# one-line canon, no hand-rolled probes). This script handles the out-of-registry
# trio (daily_report twins + fundamental_b_layer_filter, r133 manual deep-probe path
# per r136 law: not in the resolve registration face set) + CODELY.md memory-union
# (R208/r212/D-20260927-09: merge-base prefix identity assertion -> direct concat,
# NO line-level dedupe). Git objects read as subprocess BYTES (r209: no PS redirects).
# Same-window reconcile follows per r376 law.
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def stage(idx, path):
    r = subprocess.run(["git", "show", f":{idx}:{path}"],
                       capture_output=True, cwd=ROOT)
    return r.stdout if r.returncode == 0 else None


def deep_probe(obj, keys):
    """r311 nested-layer ts probe, existence-first (r319: missing key =
    always-false compare, never a silent tie)."""
    cur = obj
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return ""
        cur = cur[k]
    return str(cur)


log = []

# --- daily_report twins (r327/r329: same-day regen pair, json face by
# generated_at deep-probe picks the side, md face BYTE-COPIED from the SAME
# side -- md is not JSON, json.loads on it crashes; twins must never hybrid) ---
JP = "docs/daily_report/REPORT-2026-09-28.json"
MP = "docs/daily_report/REPORT-2026-09-28.md"
j2, j3 = stage(2, JP), stage(3, JP)
assert j2 and j3, "daily_report json stages missing"
t2 = deep_probe(json.loads(j2), ["generated_at"])
t3 = deep_probe(json.loads(j3), ["generated_at"])
side = 2 if t2 >= t3 else 3          # same-second tie -> origin (:2:), r140
pick_j = j2 if side == 2 else j3
pick_m = stage(side, MP)
assert pick_m, "daily_report md stage missing"
open(os.path.join(ROOT, os.path.normpath(JP)), "wb").write(pick_j)
open(os.path.join(ROOT, os.path.normpath(MP)), "wb").write(pick_m)
log.append(f"twins: side=:{side}: generated_at origin={t2!r} mine={t3!r} "
           f"(same side both files, md byte-copied)")

# --- fundamental_b_layer_filter.json (snapshot take-new by updated ts,
# R216; NOT in resolve face set -> manual deep probe, r133/r136 law) ---
FP = "results/fundamental_b_layer_filter.json"
f2, f3 = stage(2, FP), stage(3, FP)
assert f2 and f3, "fundamental_b_layer stages missing"
u2 = deep_probe(json.loads(f2), ["updated"])
u3 = deep_probe(json.loads(f3), ["updated"])
side_f = 2 if u2 >= u3 else 3
open(os.path.join(ROOT, os.path.normpath(FP)), "wb").write(
    f2 if side_f == 2 else f3)
log.append(f"fundamental_b_layer_filter: side=:{side_f}: "
           f"updated origin={u2!r} mine={u3!r}")

# --- CODELY.md memory-union (R208/r212/D-20260927-09) ---
CP = "CODELY.md"
base, a, b = stage(1, CP), stage(2, CP), stage(3, CP)
assert base and a and b, "CODELY.md stages missing"
if a.startswith(base) and b.startswith(base):
    # pure appends on both sides: new = base + A-suffix + B-suffix,
    # entries verbatim, byte math = len(a) + len(b) - len(base) (r212)
    new = a + b[len(base):]
    assert len(new) == len(a) + len(b) - len(base), "byte math broken"
    log.append(f"CODELY.md memory-union: prefix-identity BOTH sides holds; "
               f"base={len(base)}B a-suffix={len(a)-len(base)}B "
               f"b-suffix={len(b)-len(base)}B -> {len(new)}B")
else:
    # r327/r329: in-place edit on a side -> NO byte concat; fall back to
    # entry-level bidirectional coverage (manual review demanded)
    pa = a.startswith(base)
    pb = b.startswith(base)
    log.append(f"CODELY.md PREFIX FAIL (a={pa} b={pb}) -- in-place edit; "
               f"entry-level coverage review REQUIRED, no blind concat")
    new = None
if new is not None:
    open(os.path.join(ROOT, CP), "wb").write(new)

# parse-verify (r185 law: verify before add)
for p in (JP, FP, "results/compute_audit.json", "results/regime_state.json",
          "results/update_status.json", "results/futures_update_status.json",
          "results/lhb_update_status.json", "results/token_usage.json"):
    json.load(open(os.path.join(ROOT, os.path.normpath(p)), encoding="utf-8"))
log.append("parse-verify: all 8 json faces OK")

for line in log:
    print(line)
if new is None:
    sys.exit(2)
