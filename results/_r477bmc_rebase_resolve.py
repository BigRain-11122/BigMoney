# -*- coding: utf-8 -*-
# r477 bm-c REBASE resolver: 14 UU faces (rebase replay vs bm-b r674 wave).
# Lineage: r674bmb resolver verbatim-adapted (laws kept: staged-blob probes
# only R350, deep-ts probe r100 key-normalize + R350 shape, twins follow json
# same-side, tool faces via scripts/merge_lane_views.py single-source which
# is rebase-aware per r351 stage-mapping law [:2:=origin base, :3:=replayed],
# marker content-check r644, parse-verify, probe-miss default + loud flag +
# manual double-side review before rebase --continue per r656 law).
# REBASE side semantics in THIS run: stage2 ours = bm-b wave (14:04 regen),
# stage3 theirs = my r477 close (14:10-14:13 regen, fresher).
import io
import json
import re
import subprocess
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                              errors="replace")
CREATE = 0x08000000


def git(*a):
    p = subprocess.run(["git"] + list(a), capture_output=True,
                       creationflags=CREATE)
    return p.returncode, p.stdout, p.stderr


def stage(side, path):
    rc, out, _ = git("show", ":%d:%s" % (side, path))
    return out if rc == 0 else None


WALL_NORM = {k.replace("_", "").replace("-", "").lower() for k in
             ("ts", "generated", "generated_at", "updated", "updated_at",
              "scan_time", "time", "written_at", "state_updated")}
DATE_NORM = {"asof", "asofdate", "asofutc", "cutoff", "date", "cutoffdate"}
WALL_RE = re.compile(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")
DATE_RE = re.compile(r"20\d{2}-\d{2}-\d{2}$")


def _collect(obj, out, path="", depth=0):
    if depth > 6:
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = str(k).replace("_", "").replace("-", "").lower()
            if isinstance(v, str):
                if WALL_RE.match(v):
                    out.append((1 if nk in WALL_NORM else 2, v, path + "/" + k))
                elif DATE_RE.fullmatch(v) and nk in DATE_NORM:
                    out.append((3, v, path + "/" + k))
            else:
                _collect(v, out, path + "/" + str(k), depth + 1)
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:20]):
            _collect(v, out, path + "[%d]" % i, depth + 1)


def find_ts_json(blob):
    try:
        doc = json.loads(blob.decode("utf-8", "replace"))
    except Exception:
        return None, "parse-fail"
    c = []
    _collect(doc, c)
    if not c:
        return None, "no-ts"
    tier = min(t[0] for t in c)
    best = max((t for t in c if t[0] == tier), key=lambda t: t[1])
    return best[1], "t%d %s" % (tier, best[2])


TOOL_FACES = [
    "results/compute_audit.json",
    "results/regime_state.json",
    "results/lhb_update_status.json",
    "results/futures_update_status.json",
    "results/token_usage.json",
]
JSONL_UNION = []
SNAP_JSON = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-latest.json",
    "results/_attrition_guard_scan.json",
    "results/fundamental_b_layer_filter.json",
    "results/update_status.json",
]
TWIN_OF = {
    "docs/daily_report/REPORT-2026-10-04.md": "docs/daily_report/REPORT-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md": "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-latest.json",
}
OWN_PROBE_MD = []

fails = 0

# --- 1) tool faces: single-source recipes (rebase-aware per r351) ---
for f in TOOL_FACES:
    r = subprocess.run([sys.executable, "scripts/merge_lane_views.py",
                        "resolve", f], capture_output=True, creationflags=CREATE)
    out = ((r.stdout or b"") + (r.stderr or b"")).decode("utf-8", "replace")
    tail = " ; ".join([l for l in out.strip().splitlines() if l.strip()][-2:])
    print("[tool] %s rc=%d | %s" % (f, r.returncode, tail[:220]))
    if r.returncode != 0:
        fails += 1
        continue
    rc, _, err = git("add", f)
    if rc != 0:
        print("  add fail:", err.decode("utf-8", "replace")[:200])
        fails += 1

verdicts = {}
probe_miss_faces = []


def take_side(f, side, why):
    rc, _, err = git("checkout", "--" + side, "--", f)
    if rc != 0:
        print("[snap] %s checkout fail: %s" % (f, err.decode("utf-8", "replace")[:150]))
        return False
    rc, _, err = git("add", f)
    if rc != 0:
        print("[snap] %s add fail: %s" % (f, err.decode("utf-8", "replace")[:150]))
        return False
    verdicts[f] = side
    print("[snap] %s -> %s | %s" % (f, side, why))
    return True


# --- 2) snapshot json faces: deep-ts probe on staged blobs ---
for f in SNAP_JSON:
    ours, theirs = stage(2, f), stage(3, f)
    if theirs is None and ours is None:
        print("[snap] %s NO STAGES" % f)
        fails += 1
        continue
    if theirs is None:
        if not take_side(f, "ours", "theirs missing"):
            fails += 1
        continue
    if ours is None:
        if not take_side(f, "theirs", "ours missing"):
            fails += 1
        continue
    ts_o, why_o = find_ts_json(ours)
    ts_t, why_t = find_ts_json(theirs)
    if ts_o and ts_t:
        side = "ours" if ts_o >= ts_t else "theirs"
        why = "ours(base bm-b) %s (%s) vs theirs(replay mine) %s (%s)%s" % (
            ts_o, why_o, ts_t, why_t,
            " tie->base" if ts_o == ts_t else "")
    else:
        side = "ours"  # r656 lineage default = base side; flagged for manual
        why = "probe-miss ours=%s(%s) theirs=%s(%s) -> default base-side" % (ts_o, why_o, ts_t, why_t)
        probe_miss_faces.append(f)
        print("  !! PROBE-MISS on %s -- default base-side taken; MANUAL DOUBLE-SIDE REVIEW REQUIRED before rebase --continue (r656 law)" % f)
    if not take_side(f, side, why):
        fails += 1

# --- 3) twins follow their json twin (same-side law) ---
for f, twin in TWIN_OF.items():
    side = verdicts.get(twin)
    if side is None:
        print("[twin] %s twin %s has no verdict -- SKIPPED" % (f, twin))
        fails += 1
        continue
    if not take_side(f, side, "twin-follow %s" % twin):
        fails += 1

# --- 4) marker check on ALL staged (content check, r644 law) + parse-verify ---
rc, out, _ = git("grep", "-l", "-E", "^(<{7} |={7}$|>{7} )", "--cached")
if rc == 0:
    print("MARKER RESIDUAL in staged:", out.decode("utf-8", "replace"))
    fails += 1
elif rc == 1:
    print("marker_residual: NONE (all staged)")
else:
    print("grep rc=%d err=%s" % (rc, out.decode("utf-8", "replace")[:150]))

bad = 0
for f in TOOL_FACES + JSONL_UNION + SNAP_JSON:
    if not f.endswith((".json", ".jsonl")):
        continue
    rc, txt, _ = git("show", ":%s" % f)
    if rc != 0:
        print("stage0 miss", f)
        bad += 1
        continue
    try:
        json.loads(txt)
    except Exception as e:
        print("PARSE-FAIL", f, repr(e)[:120])
        bad += 1
print("resolver done: fails=%d parse_fail=%d resolved=%d/14 probe_miss=%s" % (
    fails, bad, len(verdicts), probe_miss_faces if probe_miss_faces else "none"))
sys.exit(1 if (fails or bad) else 0)
