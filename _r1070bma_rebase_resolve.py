# -*- coding: utf-8 -*-
# r1070 bm-a rebase-conflict resolver: 22 shared regen faces
# law: ordinary regen face = newer-wins whole-file (r1008/r1065); per-machine
# keyed face (token_usage.json) = deep UNION preserving other machines' rows
# (r1008); md/js twins follow their json twin's winning side; watermark_red =
# ts newer-wins (r1028). Fall back to theirs (my r1070 commit) when a side
# has no parseable timestamp.
import subprocess, json, os, re, sys

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"

def stage(stage_no, path):
    r = subprocess.run(["git", "-C", REPO, "show", ":%d:%s" % (stage_no, path)],
                       capture_output=True)
    if r.returncode != 0:
        raise SystemExit("stage %d %s rc=%d %s" % (stage_no, path, r.returncode, r.stderr[:200]))
    return r.stdout

TS_KEYS = ["ts", "generated", "generated_at", "updated", "last_attempt", "now", "time", "audit_ts"]

def pick_ts(obj):
    if not isinstance(obj, dict):
        return None
    for k in TS_KEYS:
        v = obj.get(k)
        if isinstance(v, str) and len(v) >= 16:
            return v.replace(" ", "T").replace("+08:00", "")
    return None

def newer_wins(path):
    b2, b3 = stage(2, path), stage(3, path)
    t2 = t3 = None
    try:
        j2 = json.loads(b2.decode("utf-8", "replace")); t2 = pick_ts(j2)
    except Exception:
        pass
    try:
        j3 = json.loads(b3.decode("utf-8", "replace")); t3 = pick_ts(j3)
    except Exception:
        pass
    if t2 and t3:
        winner = 2 if t2 > t3 else 3
    else:
        winner = 3          # no parseable face on a side -> theirs (my newer commit)
    body = b2 if winner == 2 else b3
    with open(os.path.join(REPO, path), "wb") as f:
        f.write(body)
    return {"winner": "ours" if winner == 2 else "theirs", "ts_ours": t2, "ts_theirs": t3}

def deep_union(o, t):
    """Union preserving both sides' keyed rows; scalar/list conflicts take
    theirs (newer commit); lists merge with order-preserving dedupe."""
    if isinstance(o, dict) and isinstance(t, dict):
        out = {}
        for k, v in o.items():
            out[k] = deep_union(v, t[k]) if k in t else v
        for k, v in t.items():
            if k not in out:
                out[k] = v
        return out
    if isinstance(o, list) and isinstance(t, list):
        out, seen = [], []
        for item in o + t:
            key = json.dumps(item, sort_keys=True, ensure_ascii=False) if isinstance(item, (dict, list)) else str(item)
            if key not in seen:
                seen.append(key)
                out.append(item)
        return out
    return t

def union_face(path):
    j2 = json.loads(stage(2, path).decode("utf-8", "replace"))
    j3 = json.loads(stage(3, path).decode("utf-8", "replace"))
    merged = deep_union(j2, j3)
    body = json.dumps(merged, ensure_ascii=False, indent=1).encode("utf-8")
    json.loads(body.decode("utf-8"))            # validate round-trip
    with open(os.path.join(REPO, path), "wb") as f:
        f.write(body + b"\n")
    return {"winner": "union", "ts_ours": pick_ts(j2), "ts_theirs": pick_ts(j3)}

TWIN_OF = {
    "docs/daily_report/REPORT-20261019.md": "docs/daily_report/REPORT-20261019.json",
    "docs/live_usage/LIVE-2026-10-19.md": "docs/live_usage/LIVE-2026-10-19.json",
    "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-latest.json",
    "results/dashboard_status.js": "results/dashboard_status.json",
}

CONFLICTS = [
    "docs/daily_report/REPORT-20261019.json",
    "docs/daily_report/REPORT-20261019.md",
    "docs/live_usage/LIVE-20261010-19.json",
    "docs/live_usage/LIVE-2026-10-19.json",
    "docs/live_usage/LIVE-2026-10-19.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/_r686bmb_d19_check.json",
    "results/compute_audit.json",
    "results/d19_watermark.json",
    "results/daily_scorecard.json",
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
    "results/watermark_red.json",
]
# fix the one path typo defensively: use actual enumerated faces from git
r = subprocess.run(["git", "-C", REPO, "status", "--porcelain"], capture_output=True, text=True)
actual = [ln[3:].strip() for ln in r.stdout.splitlines()
          if ln[:2] in ("UU", "AA")]
report, json_winners = {}, {}
for path in actual:
    if path == "results/token_usage.json":
        report[path] = union_face(path)
        continue
    if path in TWIN_OF:                      # md/js twin -> follow json twin's side
        twin = TWIN_OF[path]
        if twin in json_winners:
            side = json_winners[twin]["winner"]
            body = stage(2, path) if side == "ours" else stage(3, path)
            with open(os.path.join(REPO, path), "wb") as f:
                f.write(body)
            report[path] = {"winner": side + " (twin-follow %s)" % twin}
        else:
            report[path] = newer_wins(path)
        continue
    res = newer_wins(path)
    if path.endswith(".json"):
        json_winners[path] = res
    report[path] = res

# zero leftover marker assertion on resolved bodies
for path in actual:
    with open(os.path.join(REPO, path), "rb") as f:
        body = f.read()
    assert b"<<<<<<< HEAD" not in body and b">>>>>>>" not in body, "markers left in " + path

print(json.dumps({"resolved": len(actual), "detail": report}, ensure_ascii=False))
