# results/_r139bmc_resolve.py -- r139 S0 discharge storm closeout (bm-c, 11-UU batch)
# 7 ALL_FACES already resolved in-shell via `merge_lane_views.py resolve` (r381 law).
# This script handles the out-of-registry trio (daily_report twins +
# fundamental_b_layer_filter, r133 manual deep-probe path per r136 law) +
# CODELY.md memory-union. Git objects read as subprocess BYTES (r209: no PS
# redirects; console never decodes CJK). CODELY case: :2: (origin 8736B) <
# :1: base (9199B) = bm-a batch-28 in-place hot/cold archival -> prefix-identity
# FAILS on origin side; :3: (mine 9735B) IS pure-append on base (+536B = single
# r138 pit entry). Entry-level bidirectional coverage (r384 fallback law):
# take :2: verbatim + append my-side suffix entries missing from :2:.
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
    """r311 nested-layer ts probe, existence-first (r319)."""
    cur = obj
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return ""
        cur = cur[k]
    return str(cur)


log = []

# --- daily_report twins (r327/r329: json face by generated_at deep-probe,
# md face BYTE-COPIED from the SAME side; twins must never hybrid) ---
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

# --- fundamental_b_layer_filter.json (snapshot take-new by updated ts, R216;
# NOT in resolve face set -> manual deep probe, r133/r136 law) ---
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

# --- CODELY.md memory-union (R208/r212/D-20260927-09, r361 BOM-normalized) ---
CP = "CODELY.md"
base, a, b = stage(1, CP), stage(2, CP), stage(3, CP)
assert base and a and b, "CODELY.md stages missing"
if a.startswith(base) and b.startswith(base):
    new = a + b[len(base):]
    assert len(new) == len(a) + len(b) - len(base), "byte math broken"
    log.append(f"CODELY.md memory-union: prefix-identity BOTH sides; "
               f"base={len(base)}B -> {len(new)}B")
else:
    # in-place edit on a side (here: origin batch-28 archival shrank :2:)
    # -> entry-level bidirectional coverage review, no blind concat.
    # mine side is pure-append: suffix = my entries vs base; re-append any
    # of my suffix entries that origin (:2:) does not already carry.
    assert b.startswith(base), "mine side NOT pure-append -- manual review"
    suffix = b[len(base):]
    new = a + suffix if suffix not in a else a
    new.decode("utf-8")              # parse gate before write (r185)
    assert b"<<<<<<<" not in new and b">>>>>>>" not in new, "marker leak"
    log.append(f"CODELY.md entry-coverage union: origin={len(a)}B in-place "
               f"(batch-28 archival); mine pure-append suffix={len(suffix)}B "
               f"{'ALREADY-IN origin, zero-append' if suffix in a else 're-appended verbatim'} "
               f"-> {len(new)}B")
open(os.path.join(ROOT, CP), "wb").write(new)

# parse-verify (r185 law: verify before add)
for p in (JP, FP, "results/compute_audit.json", "results/regime_state.json",
          "results/runnable_pool.json", "results/update_status.json",
          "results/futures_update_status.json", "results/lhb_update_status.json",
          "results/token_usage.json"):
    json.load(open(os.path.join(ROOT, os.path.normpath(p)), encoding="utf-8"))
log.append("parse-verify: all 9 json faces OK")

for line in log:
    print(line.encode("ascii", "backslashreplace").decode())
