"""r500 bm-a rebase conflict resolver (9 snapshot/twin faces) per bigmoney-conflict-resolve skill.

Mid-rebase stage law (r351): :2: = origin/base side, :3: = replay/local side.
Snapshot faces: hardened deep-ts probe take-new (r100/R350: key normalize strip '_','-';
wall-clock values require time-of-day; date-only never feeds max; probe STAGED blob).
Twin faces (daily_report REPORT-*, live_usage LIVE-*): .json side decided by probe, .md byte-copies
the SAME side (r327/r329 twin coupling, no hybrid twins).
js-wrapper (dashboard_status.js): byte-copies the side chosen for dashboard_status.json (R209).
All reads/writes via python subprocess raw bytes (r292: no PS pipe transcode).
"""
import json
import re
import subprocess
import sys

TS_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}")
WALL_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")
PROBE_PREFIXES = ("asof", "generated", "updated", "ts", "scanned", "checked", "written", "time", "at")


def blob(stage, path):
    out = subprocess.check_output(["git", "cat-file", "-p", f":{stage}:{path}"])
    return out


def deep_wallclock_probe(obj, best):
    """Recursively find max wall-clock ts among ts-shaped keys (r100/R350 hardening)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            key = str(k).replace("_", "").replace("-", "").lower()
            if isinstance(v, str) and any(key.startswith(p) for p in PROBE_PREFIXES) \
                    and WALL_RE.match(v):
                if best is None or v > best:
                    best = v
            else:
                best = deep_wallclock_probe(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = deep_wallclock_probe(v, best)
    return best


def probe_side(stage, path):
    try:
        raw = blob(stage, path)
    except subprocess.CalledProcessError:
        return None, None
    try:
        obj = json.loads(raw.decode("utf-8"))
    except Exception:
        return None, None
    ts = deep_wallclock_probe(obj, None)
    if ts is None:  # fallback: any ts-shaped string value (deep)
        flat = []

        def scan(o):
            if isinstance(o, dict):
                for v in o.values():
                    scan(v)
            elif isinstance(o, list):
                for v in o:
                    scan(v)
            elif isinstance(o, str) and TS_RE.match(o):
                flat.append(o)
        scan(obj)
        ts = max(flat) if flat else None
    return ts, raw


def resolve_snapshot(path, label):
    ts2, raw2 = probe_side(2, path)
    ts3, raw3 = probe_side(3, path)
    if ts2 is None and ts3 is None:
        side, why = 3, "no-probe-both -> replay side (r140 tie->HEAD law, replay=HEAD family)"
    elif ts3 is None:
        side, why = 2, f"probe only :2: ({ts2})"
    elif ts2 is None:
        side, why = 3, f"probe only :3: ({ts3})"
    elif ts3 >= ts2:
        side, why = (3, f":3: {ts3} >= :2: {ts2} take-newer") if ts3 > ts2 \
            else (3, f"tie {ts3} -> :3: replay side (r140)")
    else:
        side, why = 2, f":2: {ts2} > :3: {ts3} take-newer"
    raw = raw2 if side == 2 else raw3
    with open(path, "wb") as f:
        f.write(raw)
    if path.endswith(".json"):
        json.loads(raw.decode("utf-8"))  # parse-verify before add (r185)
    print(f"[{label}] {path}: {why}")
    return side


def resolve_twin(json_path, md_path, label):
    side = resolve_snapshot(json_path, label + "/json")
    raw = blob(side, md_path)
    with open(md_path, "wb") as f:
        f.write(raw)
    print(f"[{label}/md] {md_path}: byte-copy of :{side}: (twin coupling r327/r329)")
    return side


def main():
    # twin pairs first (json decides side; md byte-copies)
    resolve_twin("docs/daily_report/REPORT-2026-10-01.json",
                 "docs/daily_report/REPORT-2026-10-01.md", "daily_report")
    resolve_twin("docs/live_usage/LIVE-2026-10-01.json",
                 "docs/live_usage/LIVE-2026-10-01.md", "live_usage_dated")
    resolve_twin("docs/live_usage/LIVE-latest.json",
                 "docs/live_usage/LIVE-latest.md", "live_usage_latest")
    # snapshots
    side = resolve_snapshot("results/dashboard_status.json", "dashboard_json")
    raw = blob(side, "results/dashboard_status.js")
    with open("results/dashboard_status.js", "wb") as f:
        f.write(raw)
    head = raw[:64].decode("utf-8", "replace")
    assert "window.DASH_DATA" in raw.decode("utf-8", "replace")[:200], "js wrapper must stay intact (R209)"
    print(f"[dashboard_js] results/dashboard_status.js: byte-copy of :{side}: ({head.strip()[:32]}...)")
    resolve_snapshot("results/fundamental_b_layer_filter.json", "fundamental_blf (non-member fail-closed manual)")
    resolve_snapshot("results/scorecard_v1.json", "scorecard_v1")
    resolve_snapshot("results/strategy_scorecard.json", "strategy_scorecard")
    resolve_snapshot("results/_attrition_guard_scan.json", "attrition_scan (UNKNOWN adjudicated: per-run snapshot)")
    print("RESOLVER DONE")


if __name__ == "__main__":
    sys.exit(main())
