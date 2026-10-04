"""r708 bm-b merge resolver: 19 UU duplicate-maintenance/timestamp faces -> take-new (ts newer-wins).

Per bigmoney-conflict-resolve canon: repeated-maintenance faces resolve by
embedded timestamp newer-wins; ties and missing-ts -> theirs (origin authority).
Stage mapping in MERGE mode: :2: = ours (bm-b), :3: = theirs (origin side).
"""
import json
import subprocess
import sys

FACES_JSON = [
    "docs/daily_report/REPORT-2026-10-05.json",
    "docs/live_usage/LIVE-2026-10-05.json",
    "docs/live_usage/LIVE-latest.json",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
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
FACES_MD = [
    "docs/daily_report/REPORT-2026-10-05.md",
    "docs/live_usage/LIVE-2026-10-05.md",
    "docs/live_usage/LIVE-latest.md",
]
FACE_JS = "results/dashboard_status.js"

TS_KEYS = ("generated_at", "updated", "generated", "now", "ts", "asof", "last_run", "scan_ts")


def stage_bytes(path, stage):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout


def probe_ts(obj, depth=0):
    """First timestamp-ish string found, shallow-first."""
    if depth > 2 or not isinstance(obj, dict):
        return None
    for k in TS_KEYS:
        v = obj.get(k)
        if isinstance(v, str) and len(v) >= 8:
            return v
    for v in obj.values():
        if isinstance(v, dict):
            t = probe_ts(v, depth + 1)
            if t:
                return t
    return None


def resolve_json(path):
    o_raw = stage_bytes(path, 2)
    t_raw = stage_bytes(path, 3)
    if t_raw is None:
        return ("ours", "theirs-missing")
    if o_raw is None:
        return ("theirs", "ours-missing")
    try:
        o = json.loads(o_raw.decode("utf-8"))
        t = json.loads(t_raw.decode("utf-8"))
    except Exception as ex:
        return ("theirs", f"parse-fail={ex}")
    to, tt = probe_ts(o), probe_ts(t)
    if to and tt:
        if tt >= to:
            return ("theirs", f"ts {to} <= {tt}")
        return ("ours", f"ts {to} > {tt}")
    return ("theirs", f"ts-missing ours={to} theirs={tt} -> origin authority")


def main():
    decisions = {}
    for p in FACES_JSON:
        side, why = resolve_json(p)
        decisions[p] = (side, why)
    # md twins follow their json twin's decision (same-run twins)
    for p in FACES_MD:
        twin = p[:-3] + ".json"
        side, why = decisions[twin]
        decisions[p] = (side, f"md-twin of {twin} ({why})")
    # JS face: probe generated_at inside the DASH_DATA blob
    o_raw = stage_bytes(FACE_JS, 2)
    t_raw = stage_bytes(FACE_JS, 3)
    if t_raw is None:
        decisions[FACE_JS] = ("ours", "theirs-missing")
    elif o_raw is None:
        decisions[FACE_JS] = ("theirs", "ours-missing")
    else:
        def js_ts(raw):
            s = raw.decode("utf-8", "replace")
            for key in TS_KEYS:
                needle = f'"{key}"'
                i = s.find(needle)
                if i >= 0:
                    j = s.find('"', i + len(needle) + 2)
                    if j > i:
                        return s[i + len(needle) + 2:j]
            return None
        to, tt = js_ts(o_raw), js_ts(t_raw)
        if to and tt and to > tt:
            decisions[FACE_JS] = ("ours", f"ts {to} > {tt}")
        else:
            decisions[FACE_JS] = ("theirs", f"ts ours={to} theirs={tt} -> newer/origin")

    for p, (side, why) in decisions.items():
        stage = 3 if side == "theirs" else 2
        raw = stage_bytes(p, stage)
        if raw is None:
            print(f"SKIP {p}: stage {stage} unreadable")
            continue
        with open(p, "wb") as f:
            f.write(raw)
        r = subprocess.run(["git", "add", p], capture_output=True)
        if r.returncode != 0:
            print(f"ADD-FAIL {p}: {r.stderr.decode('utf-8','replace')}")
            sys.exit(1)
        print(f"RESOLVED {p} -> {side} ({why})")

    # post-verify: no conflict markers in worktree resolved files
    bad = []
    for p in list(decisions):
        try:
            body = open(p, "rb").read().decode("utf-8", "replace")
        except Exception:
            continue
        for marker in ("<<<<<<< ", ">>>>>>> ", "=======\n"):
            if marker in body:
                bad.append((p, marker))
                break
    if bad:
        print("MARKER-LEAK:", bad)
        sys.exit(1)
    print("ALL RESOLVED, zero markers, decisions:", len(decisions))


if __name__ == "__main__":
    main()
