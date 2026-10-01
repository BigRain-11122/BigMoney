# -*- coding: utf-8 -*-
# r522 bm-b: resolve 13 shared-derive-face UU conflicts by wall-clock-newer side (r505 law)
import io, sys, subprocess, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

FILES = [
    "docs/daily_report/REPORT-2026-10-01.json",
    "docs/daily_report/REPORT-2026-10-01.md",
    "docs/live_usage/LIVE-2026-10-01.json",
    "docs/live_usage/LIVE-2026-10-01.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
]

def stage(side, path):
    r = subprocess.run(["git", "show", f":{side}:{path}"], capture_output=True)
    return r.stdout.decode("utf-8", errors="replace")

def probe_ts(text):
    # find first ISO-like timestamp anywhere (JSON ts field or md line)
    m = re.search(r'"(?:ts|generated_at|updated_at|asof)"\s*:\s*"?(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})', text)
    if not m:
        m = re.search(r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})', text)
    return m.group(1) if m else ""

for f in FILES:
    ours = stage("2", f)     # rebase: stage2 = upstream (bm-c r335 side)
    theirs = stage("3", f)   # stage3 = my commit side
    to, tt = probe_ts(ours), probe_ts(theirs)
    if not to and not tt:
        pick, side = theirs, "theirs(no-ts-pair: prefer own commit face, disclosed)"
    elif not tt:
        pick, side = ours, "ours"
    elif not to:
        pick, side = theirs, "theirs"
    elif tt >= to:
        pick, side = theirs, "theirs"
    else:
        pick, side = ours, "ours"
    with open(f, "w", encoding="utf-8", newline="") as fh:
        fh.write(pick)
    subprocess.run(["git", "add", "--", f], check=True)
    print(f"RESOLVED {f}: ours_ts={to or '-'} theirs_ts={tt or '-'} -> {side}")

# json.loads verification on all resolved JSON faces
ok = True
for f in FILES:
    if f.endswith(".json"):
        try:
            json.load(open(f, encoding="utf-8"))
        except Exception as e:
            ok = False
            print(f"JSON FAIL {f}: {e}")
print("RESOLVE RESULT:", "ALL PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
