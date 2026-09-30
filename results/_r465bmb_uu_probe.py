# r465 bm-b push-rejection rebase UU batch probe: dump ts fields from both stages (:2=origin base, :3=my replayed commit)
import subprocess, json, sys, io

FILES = [
    "docs/daily_report/REPORT-2026-09-30.json",
    "docs/daily_report/REPORT-2026-09-30.md",
    "docs/live_usage/LIVE-2026-09-30.json",
    "docs/live_usage/LIVE-2026-09-30.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
]

TS_KEYS = ["ts", "generated", "generated_at", "updated", "updated_at", "scan_ts", "asof", "cutoff", "last_scan"]

def get_stage(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout.decode("utf-8", errors="replace")

def ts_of(text, path):
    if not text:
        return None
    if path.endswith(".json"):
        try:
            d = json.loads(text)
        except Exception as e:
            return f"PARSE-FAIL:{e}"
        out = {}
        for k in TS_KEYS:
            if isinstance(d, dict) and k in d:
                out[k] = d[k]
        # ledger sizes for union faces
        if isinstance(d, dict):
            for k in ("history", "transitions", "launches"):
                if k in d and isinstance(d[k], list):
                    out[f"|{k}|"] = len(d[k])
        return out or {k: d.get(k) for k in list(d)[:6] if isinstance(d, dict)}
    else:
        # md: grep ts-like header lines
        hits = [ln.strip()[:120] for ln in text.splitlines()[:20] if any(t in ln.lower() for t in ("2026-09-30", "generated", "ts:", "- generated"))]
        return hits[:4] if hits else text.splitlines()[:3]

for p in FILES:
    a, b = get_stage(2, p), get_stage(3, p)
    print("=" * 8, p)
    print(" :2 (origin/base):", ts_of(a, p))
    print(" :3 (mine/replay):", ts_of(b, p))
