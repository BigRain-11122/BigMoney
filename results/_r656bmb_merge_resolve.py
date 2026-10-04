# -*- coding: utf-8 -*-
# r656 bm-b merge resolver: 21 UU same-window S6 derive faces (dead r655 session
# merge of origin/main adopted per r643; recipes = r652 lineage + classifier
# r440/r652 categories; ts probe hardened per r100 key-normalize + R350 shape law).
#   5 tool faces  -> scripts/merge_lane_views.py resolve (single-source recipes)
#   1 append-log  -> post_review.jsonl line union zero loss (r188/r217)
#  14 snapshot    -> take-new-by-deep-ts; .md/.js twins follow their json twin
#                    (same-side law r98/r99/r100/r439bmb); tie -> ours (r140)
# Probe law: staged blobs (:2:/:3:) only, never working tree (R350).
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


MD_WALL_RE = re.compile(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")


def find_ts_text(blob):
    if blob is None:
        return None, "no-blob"
    m = MD_WALL_RE.findall(blob.decode("utf-8", "replace"))
    return (max(m), "text-max") if m else (None, "no-ts")


TOOL_FACES = [
    "results/compute_audit.json",
    "results/regime_state.json",
    "results/lhb_update_status.json",
    "results/futures_update_status.json",
    "results/token_usage.json",
]
JSONL_UNION = ["results/post_review.jsonl"]
SNAP_JSON = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-latest.json",
    "results/_attrition_guard_scan.json",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/update_status.json",
]
TWIN_OF = {
    "docs/daily_report/REPORT-2026-10-04.md": "docs/daily_report/REPORT-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md": "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-latest.json",
    "results/dashboard_status.js": "results/dashboard_status.json",
}
OWN_PROBE_MD = ["results/post_review/REPORT-20261004.md"]

fails = 0

# --- 1) tool faces: single-source recipes ---
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

# --- 2) append-log: line-level union zero loss ---
for f in JSONL_UNION:
    ours, theirs = stage(2, f), stage(3, f)
    if ours is None or theirs is None:
        print("[union] %s missing stage ours=%s theirs=%s" % (f, ours is not None, theirs is not None))
        fails += 1
        continue
    eol = b"\r\n" if b"\r\n" in ours else b"\n"  # EOL probe r657 law
    o_lines = ours.split(eol)
    o_canon = {ln.rstrip(b"\r") for ln in o_lines}
    t_lines = [ln for ln in theirs.split(eol) if ln.rstrip(b"\r") not in o_canon]
    merged = [ln for ln in o_lines if ln] + [ln for ln in t_lines if ln]
    body = eol.join(merged) + eol
    with open(f, "wb") as fh:
        fh.write(body)
    n_o, n_t, n_u = len([l for l in o_lines if l]), len([l for l in theirs.split(eol) if l]), len(merged)
    print("[union] %s eol=%s ours=%d theirs=%d union=%d zero-loss=%s"
          % (f, repr(eol), n_o, n_t, n_u, n_u >= max(n_o, n_t)))
    if n_u < max(n_o, n_t):
        fails += 1
        continue
    rc, _, err = git("add", f)
    if rc != 0:
        print("  add fail:", err.decode("utf-8", "replace")[:200])
        fails += 1

# --- 3) snapshot json faces: deep-ts probe on staged blobs ---
verdicts = {}


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
        why = "ours %s (%s) vs theirs %s (%s)%s" % (ts_o, why_o, ts_t, why_t,
                                                    " tie->HEAD" if ts_o == ts_t else "")
    else:
        side = "ours"  # r652 lineage default, honest print below
        why = "probe-miss ours=%s(%s) theirs=%s(%s) -> default ours" % (ts_o, why_o, ts_t, why_t)
    if not take_side(f, side, why):
        fails += 1

# --- 4) twins follow their json twin (same-side law) ---
for f, twin in TWIN_OF.items():
    side = verdicts.get(twin)
    if side is None:
        print("[twin] %s twin %s has no verdict -- SKIPPED" % (f, twin))
        fails += 1
        continue
    if not take_side(f, side, "twin-follow %s" % twin):
        fails += 1

# --- 5) own-probe md faces ---
for f in OWN_PROBE_MD:
    ours, theirs = stage(2, f), stage(3, f)
    ts_o, why_o = find_ts_text(ours)
    ts_t, why_t = find_ts_text(theirs)
    if ts_o and ts_t:
        side = "ours" if ts_o >= ts_t else "theirs"
        why = "ours %s vs theirs %s%s" % (ts_o, ts_t, " tie->HEAD" if ts_o == ts_t else "")
    else:
        side = "ours"
        why = "probe-miss ours=%s(%s) theirs=%s(%s) -> default ours" % (ts_o, why_o, ts_t, why_t)
    if not take_side(f, side, why):
        fails += 1

# --- 6) marker check on ALL staged (content check, r644 law) + parse-verify ---
rc, out, _ = git("grep", "-l", "-E", "^(<{7} |={7}$|>{7} )", "--cached")
if rc == 0:
    print("MARKER RESIDUAL in staged:", out.decode("utf-8", "replace"))
    fails += 1
elif rc == 1:
    print("marker_residual: NONE (all staged)")
else:
    print("grep rc=%d err=%s" % (rc, out.decode("utf-8", "replace")[:150]))

bad = 0
for f in TOOL_FACES + JSONL_UNION + SNAP_JSON + list(TWIN_OF) + OWN_PROBE_MD:
    if f.endswith((".json", ".jsonl", ".js")) and f.endswith(".js"):
        continue  # js is producer-format, not plain json
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
print("resolver done: fails=%d parse_fail=%d resolved=%d/21" % (fails, bad, len(verdicts)))
sys.exit(1 if (fails or bad) else 0)
