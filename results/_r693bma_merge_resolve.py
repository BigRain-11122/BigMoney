# -*- coding: utf-8 -*-
"""r693 bm-a merge resolver: 18 S6 regen UU faces.
Canon: per-face ts-freshness (r440/r461 ts_norm law), token_usage per-key
union with r456/r466 fallback (side_pick>0 assert, else whole-face ts),
md twins follow their json twin side (r692 law). Both sides read via
git show HEAD:/MERGE_HEAD: raw bytes (r657-ii law). Json reparse proof per face.
"""
import json, subprocess, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

FACES = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/crash_fuse.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]


def blob(rev, path):
    r = subprocess.run(["git", "show", "%s:%s" % (rev, path)], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def ts_norm(v):
    """r461 law: normalize 'T'->space, keep first 19 chars."""
    if not isinstance(v, str) or len(v) < 10:
        return ""
    s = v.replace("T", " ")[:19]
    return s


def face_ts(data):
    if not isinstance(data, dict):
        return ""
    for k in ("ts", "generated", "generated_at", "last_run", "asof"):
        if k in data:
            t = ts_norm(data[k])
            if t:
                return t
    return ""


def pick_newer(path):
    """Return (side, reason) by ts-freshness; json-aware."""
    o = blob("HEAD", path)
    t = blob("MERGE_HEAD", path)
    if o is None and t is None:
        return None, "both-absent"
    if o is None:
        return "theirs", "ours-absent"
    if t is None:
        return "ours", "theirs-absent"
    try:
        jo, jt = json.loads(o), json.loads(t)
    except Exception:
        # non-json (md/js): compare raw equality then embedded ts string
        if o == t:
            return "ours", "byte-equal"
        so, st = face_ts_jsonl_sniff(o), face_ts_jsonl_sniff(t)
        side = "ours" if so >= st else "theirs"
        return side, "raw-ts-sniff %s vs %s" % (so, st)
    to, tt = face_ts(jo), face_ts(jt)
    if to and tt:
        return ("ours" if to >= tt else "theirs"), "ts %s vs %s" % (to, tt)
    return "ours", "no-ts-fields (ours kept, both dict)"


def face_ts_jsonl_sniff(raw):
    """md/js: find last 'generated'-like ts in text."""
    import re
    m = re.findall(r'"(?:ts|generated|generated_at)"\s*:\s*"([^"]+)"', raw.decode("utf-8", errors="replace"))
    return ts_norm(m[-1]) if m else ""


def resolve_token(path):
    """r456/r466 canon: per-key union (machines by ts), side_pick>0 assert,
    else whole-face ts freshness fallback."""
    o = blob("HEAD", path)
    t = blob("MERGE_HEAD", path)
    jo, jt = json.loads(o), json.loads(t)
    mo = {m.get("machine"): m for m in jo.get("machines", []) if isinstance(m, dict)}
    mt = {m.get("machine"): m for m in jt.get("machines", []) if isinstance(m, dict)}
    merged, side_pick = [], 0
    for k in sorted(set(mo) | set(mt)):
        a, b = mo.get(k), mt.get(k)
        if a and b:
            ta, tb = face_ts(a), face_ts(b)
            win = a if (ta and (not tb or ta >= tb)) else (b if tb else a)
            if win is a and (not tb or ta >= tb):
                side_pick += 1
            elif win is b:
                pass
            merged.append(win)
        else:
            merged.append(a or b)
            side_pick += 1
    if side_pick == 0:
        # r466 law: zero per-key picks -> whole-face ts freshness
        to, tt = face_ts(jo), face_ts(jt)
        win_obj = jo if to >= tt else jt
        reason = "side_pick=0 -> whole-face ts %s vs %s (r466)" % (to, tt)
        return json.dumps(win_obj, ensure_ascii=False, indent=1).encode("utf-8"), reason
    out = dict(jo)
    out["machines"] = merged
    reason = "per-key union side_pick=%d/%d" % (side_pick, len(merged))
    return json.dumps(out, ensure_ascii=False, indent=1).encode("utf-8"), reason


# md twins follow json twin side
JSON_TWIN = {
    "docs/daily_report/REPORT-2026-10-04.md": "docs/daily_report/REPORT-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md": "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-latest.json",
}

results = []
for path in FACES:
    if path == "results/token_usage.json":
        data, reason = resolve_token(path)
        side = "union"
    elif path in JSON_TWIN:
        twin = JSON_TWIN[path]
        side, reason = pick_newer(twin)
        side_note = reason
        data = blob("HEAD" if side == "ours" else "MERGE_HEAD", path)
        reason = "md-follows-json-twin (%s %s)" % (side, side_note)
        if data is None:
            side, reason = pick_newer(path)
            data = blob("HEAD" if side == "ours" else "MERGE_HEAD", path)
    else:
        side, reason = pick_newer(path)
        data = blob("HEAD" if side == "ours" else "MERGE_HEAD", path)
    if data is None:
        print("FAIL no-data", path)
        sys.exit(2)
    with open(path, "wb") as f:
        f.write(data)
    # reparse proof for json faces
    if path.endswith(".json"):
        json.loads(open(path, "rb").read())
    results.append((path, side, reason))

for path, side, reason in results:
    print("RESOLVED %-50s %-7s %s" % (path, side, reason))

# marker scan (r453 law: line-start judgment, not substring)
import re
bad = []
for path in FACES:
    raw = open(path, "rb").read()
    for ln in raw.split(b"\n"):
        if ln.startswith(b"<<<<<<<") or ln.startswith(b">>>>>>>"):
            bad.append(path)
            break
print("MARKER-SCAN:", "CLEAN" if not bad else bad)
json.dump(results, open("results/_r693bma_merge_resolve.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
sys.exit(0 if not bad else 3)
