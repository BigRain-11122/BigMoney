# r464 bm-b push-collision rebase: ts probe both stages of every UU file (r461 law: direction per-file, never assume)
import subprocess, json, sys

FILES = [
    "docs/daily_report/REPORT-2026-09-30.json",
    "docs/daily_report/REPORT-2026-09-30.md",
    "docs/live_usage/LIVE-2026-09-30.json",
    "docs/live_usage/LIVE-2026-09-30.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/paper/marks/marks-20260930.jsonl",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]

def blob(path, stage):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout.decode("utf-8", errors="replace")

def probe_json(text):
    try:
        j = json.loads(text)
    except Exception:
        return None
    out = {}
    for k in ("ts", "generated", "generated_at", "updated", "asof", "scan_ts", "elapsed_sec"):
        if isinstance(j, dict) and k in j:
            out[k] = str(j[k])[:40]
    if isinstance(j, dict):
        for k in ("meta", "status", "run", "last_scan"):
            v = j.get(k)
            if isinstance(v, dict):
                for kk in ("ts", "generated", "updated", "asof"):
                    if kk in v:
                        out[f"{k}.{kk}"] = str(v[kk])[:40]
        if "history" in j and isinstance(j["history"], list):
            out["history_len"] = len(j["history"])
        if "launches" in j and isinstance(j["launches"], list):
            out["launches_len"] = len(j["launches"])
        if "evidence" in j and isinstance(j["evidence"], list):
            out["evidence_len"] = len(j["evidence"])
    return out

for f in FILES:
    s2, s3 = blob(f, 2), blob(f, 3)
    print("==" * 3, f)
    for stage, name in ((s2, "S2(origin/bm-a)"), (s3, "S3(mine/bm-b)")):
        if stage is None:
            print(f"  {name}: <no blob>")
            continue
        if f.endswith(".jsonl"):
            lines = [l for l in stage.splitlines() if l.strip()]
            last = lines[-1][:200] if lines else "<empty>"
            first_ts = last_ts = "?"
            try:
                js = [json.loads(l) for l in lines]
                ts = [x.get("ts", x.get("time", "")) for x in js]
                first_ts, last_ts = ts[0], ts[-1]
            except Exception as e:
                last_ts = f"parse_err {e}"
            print(f"  {name}: lines={len(lines)} first_ts={first_ts} last_ts={last_ts}")
        elif f.endswith(".js"):
            import re
            m = re.search(r'"(?:ts|generated|updated)"\s*:\s*"?([^",}]+)"?', stage)
            print(f"  {name}: len={len(stage)} ts_field={m.group(1) if m else '?'} head={stage[:80]!r}")
        elif f.endswith(".json"):
            p = probe_json(stage)
            print(f"  {name}: {p}")
        else:  # .md
            import re
            ms = re.findall(r"2026-09-30[ T]\d{2}:\d{2}(:\d{2})?", stage)
            print(f"  {name}: len={len(stage)} last_ts_in_md={ms[-1] if ms else '?'} head={stage[:60]!r}")
