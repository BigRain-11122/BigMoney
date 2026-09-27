# results/_r143bmc_resolve.py -- r143 push-storm closeout (bm-c, 11-UU batch)
# 7 ALL_FACES already resolved in-shell via `merge_lane_views.py resolve` (r381 law).
# This script handles the out-of-registry trio (daily_report twins +
# fundamental_b_layer_filter, r133/r136 manual deep-probe law) + CODELY.md
# memory-union (D-20260927-09(2) suffix-concat law). Git objects read as
# subprocess BYTES (r209). CODELY fallback: entry-level bidirectional coverage
# (r384 law) if a side is an in-place edit rather than pure-append.
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def stage(idx, path):
    r = subprocess.run(["git", "show", f":{idx}:{path}"],
                       capture_output=True, cwd=ROOT)
    return r.stdout if r.returncode == 0 else None


def deep_probe(obj, keys):
    cur = obj
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return ""
        cur = cur[k]
    return str(cur)


log = []

# --- daily_report twins (json by generated_at deep-probe; md BYTE-COPIED
# from the SAME side; twins must never hybrid, r327/r329) ---
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

# --- fundamental_b_layer_filter.json (snapshot take-new by updated ts, R216) ---
FP = "results/fundamental_b_layer_filter.json"
f2, f3 = stage(2, FP), stage(3, FP)
assert f2 and f3, "fundamental_b_layer_filter stages missing"
u2 = deep_probe(json.loads(f2), ["updated"])
u3 = deep_probe(json.loads(f3), ["updated"])
side_f = 2 if u2 >= u3 else 3
open(os.path.join(ROOT, os.path.normpath(FP)), "wb").write(
    f2 if side_f == 2 else f3)
log.append(f"fundamental_b_layer_filter: side=:{side_f}: "
           f"updated origin={u2!r} mine={u3!r}")

# --- CODELY.md memory-union (R208/r212/D-20260927-09, r361 BOM-normalized) ---
CP = "CODELY.md"
base, a, b = stage(1, CP), stage(2, CP), stage(3, CP)
assert base and a and b, "CODELY.md stages missing"
if a.startswith(base) and b.startswith(base):
    new = a + b[len(base):]
    assert len(new) == len(a) + len(b) - len(base), "byte math broken"
    new.decode("utf-8")
    log.append(f"CODELY.md memory-union: prefix-identity BOTH sides; "
               f"base={len(base)}B -> {len(new)}B")
else:
    # a side edited in place (e.g. origin hot/cold archival) -> entry-level
    # bidirectional coverage review, no blind concat (r384 law).
    if b.startswith(base) and not a.startswith(base):
        suffix = b[len(base):]
        new = a + suffix if suffix not in a else a
    elif a.startswith(base) and not b.startswith(base):
        suffix = a[len(base):]
        new = b + suffix if suffix not in b else b
    else:
        raise SystemExit("both sides in-place edits -- manual review required")
    new.decode("utf-8")              # parse gate before write (r185)
    assert b"<<<<<<<" not in new and b">>>>>>>" not in new, "marker leak"
    log.append(f"CODELY.md entry-coverage union -> {len(new)}B")
open(os.path.join(ROOT, CP), "wb").write(new)

# parse-verify (r185 law: verify before add)
for p in (JP, FP, "results/compute_audit.json", "results/regime_state.json",
          "results/crash_fuse.json", "results/update_status.json",
          "results/futures_update_status.json", "results/lhb_update_status.json",
          "results/token_usage.json"):
    json.load(open(os.path.join(ROOT, os.path.normpath(p)), encoding="utf-8"))
log.append("parse-verify: all 9 json faces OK")

for line in log:
    print(line.encode("ascii", "backslashreplace").decode())
