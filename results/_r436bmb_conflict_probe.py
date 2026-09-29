"""r436 rebase conflict freshness probe (17 UU). Print per-file stage2(ours=origin)/stage3(theirs=local) ts fields."""
import json, subprocess, sys

FILES = [
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
    "docs/daily_report/REPORT-2026-09-29.json",
    "docs/live_usage/LIVE-2026-09-29.json",
    "docs/live_usage/LIVE-latest.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
]

def blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    return r.stdout if r.returncode == 0 else b""

TS_KEYS = ["generated", "generated_at", "ts", "updated", "updated_at", "last_run", "asof", "date", "cutoff", "evidence_cutoff"]

def probe(path):
    for stage, label in ((2, "ours=origin"), (3, "theirs=local")):
        b = blob(stage, path)
        if not b:
            print(f"{path} [{label}] <no blob>")
            continue
        if path.endswith(".js"):
            txt = b.decode("utf-8", "replace")
            for k in TS_KEYS:
                for needle in (f'"{k}":', f'"{k}": '):
                    i = txt.find(needle)
                    if i >= 0:
                        print(f"{path} [{label}] {k}={txt[i+len(needle):i+len(needle)+40].split(chr(34))[0][:40]}")
                        break
                else:
                    continue
                break
            else:
                print(f"{path} [{label}] js no-ts-key len={len(txt)}")
            continue
        try:
            d = json.loads(b)
        except Exception as e:
            print(f"{path} [{label}] JSON-ERR {e} len={len(b)}")
            continue
        flat = {}
        def walk(o, pfx=""):
            if isinstance(o, dict):
                for k, v in o.items():
                    if isinstance(v, (str, int, float)) and any(t in k.lower() for t in ("generated", "updated", "ts", "asof", "cutoff", "date", "epoch")):
                        flat[pfx + k] = str(v)[:44]
                    elif isinstance(v, dict) and len(flat) < 8:
                        walk(v, pfx + k + ".")
        walk(d)
        print(f"{path} [{label}] " + (" ".join(f"{k}={v}" for k, v in list(flat.items())[:6]) or f"topkeys={list(d)[:8]}"))

for f in FILES:
    probe(f)
