"""r681 bm-a merge resolver: 14 UU faces.
13 snapshot-regen faces -> ts-freshness newer-wins (r440 two-bucket law);
token_usage.json -> per-key union on machines entries (r456/r466 law, side-pick>0 asserted,
zero-hit falls back to whole-face ts freshness).
Both sides via git show HEAD:<p> / MERGE_HEAD:<p> raw bytes (r657 law: add wipes :2:/:3:).
"""
import json, subprocess, sys

def show(ref, path):
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout

TS_KEYS = ["ts", "generated", "generated_at", "updated_at", "updated", "_ts",
           "timestamp", "date", "asof", "run_ts"]

def ts_of(obj):
    if isinstance(obj, dict):
        for k in TS_KEYS:
            if k in obj:
                return str(obj[k])
        for v in obj.values():
            t = ts_of(v)
            if t:
                return t
    return None

SNAP = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/update_status.json",
]
UNION = ["results/token_usage.json"]

def pick_fresh(path):
    ours, theirs = show("HEAD", path), show("MERGE_HEAD", path)
    if ours is None:
        return "theirs", theirs
    if theirs is None:
        return "ours", ours
    to, tt = None, None
    if path.endswith(".json"):
        try:
            to = ts_of(json.loads(ours.decode("utf-8", "replace")))
            tt = ts_of(json.loads(theirs.decode("utf-8", "replace")))
        except Exception:
            pass
    else:  # md twin: scan first lines for a date-ish key
        for blob, which in ((ours, "o"), (theirs, "t")):
            head = blob.decode("utf-8", "replace")[:800]
            import re
            m = re.search(r"20\d\d-\d\d-\d\d[T ]\d\d:\d\d(:\d\d)?", head)
            if which == "o":
                to = m.group(0) if m else None
            else:
                tt = m.group(0) if m else None
    if to and tt:
        winner = "ours" if to >= tt else "theirs"
    elif to:
        winner = "ours"
    elif tt:
        winner = "theirs"
    else:
        winner = "ours"  # no ts anywhere: keep ours
    return winner, ours if winner == "ours" else theirs

def union_token(path):
    ours, theirs = show("HEAD", path), show("MERGE_HEAD", path)
    jo = json.loads(ours.decode("utf-8", "replace"))
    jt = json.loads(theirs.decode("utf-8", "replace"))
    side_pick = 0
    out = {}
    # top-level: merge dict keys, prefer newer ts where both present
    keys = set(jo) | set(jt)
    for k in keys:
        vo, vt = jo.get(k), jt.get(k)
        if k == "machines" and isinstance(vo, dict) and isinstance(vt, dict):
            m = {}
            for mk in set(vo) | set(vt):
                o, t = vo.get(mk), vt.get(mk)
                if o is not None and t is not None:
                    tso, tst = ts_of(o), ts_of(t)
                    if tso and tst and tst > tso:
                        m[mk] = t
                        side_pick += 1
                    else:
                        m[mk] = o
                        side_pick += 1
                else:
                    m[mk] = o if o is not None else t
                    side_pick += 1
            out[k] = m
        elif vo is not None and vt is not None:
            tso, tst = ts_of(vo), ts_of(vt)
            out[k] = vt if (tso and tst and tst > tso) else vo
        else:
            out[k] = vo if vo is not None else vt
    if side_pick == 0:
        # r456 law: zero per-key hits -> explicit whole-face freshness fallback
        to, tt = ts_of(jo), ts_of(jt)
        winner = "ours" if (to and (not tt or to >= tt)) else "theirs"
        return winner, ours if winner == "ours" else theirs, 0
    return "union", json.dumps(out, ensure_ascii=False, indent=1).encode("utf-8"), side_pick

report = {"resolved": [], "union_side_pick": None}
for p in SNAP:
    w, blob = pick_fresh(p)
    with open(p, "wb") as f:
        f.write(blob)
    report["resolved"].append([p, w])
for p in UNION:
    w, blob, sp = union_token(p)
    with open(p, "wb") as f:
        f.write(blob)
    report["union_side_pick"] = sp
    report["resolved"].append([p, w])

# marker check before add (r657 law: no staged face may carry conflict markers)
bad = []
for p in SNAP + UNION:
    b = open(p, "rb").read()
    for ln in b.split(b"\n"):
        if ln.startswith(b"<<<<<<<") or ln.startswith(b">>>>>>>"):
            bad.append(p)
            break
if bad:
    print("MARKER_REMAIN", bad)
    sys.exit(1)
with open("results/_r681bma_merge_resolve.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(report, f, ensure_ascii=False, indent=1)
print("RESOLVE_DONE", len(report["resolved"]), "faces, union_side_pick=", report["union_side_pick"])
