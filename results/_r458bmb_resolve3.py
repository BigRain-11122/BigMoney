"""_r458bmb_resolve3.py -- bm-b r458 rebase collision resolver (batch 3: onto bm-c r266 tip).

Stage :2: = bm-c tip 99f7f8820 (r266 runner-build round S6 faces, pre-fix fundamental code
-> rc2 error face); stage :3: = my r457 replay (post-fix rc0 face).
- compute_audit / regime_state: ledger union zero-loss.
- fundamental_status: MANUAL truth-wins take-m AGAIN (origin chain still carries pre-fix
  update_fundamental; my replayed commit chain carries the _unpublished_null fix, so the
  truthful post-merge face = my rc0 full face; third same-window adjudication, r457 precedent).
"""
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def blob(spec):
    return subprocess.run(["git", "show", spec], capture_output=True).stdout.decode("utf-8", errors="replace")


WALL = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")
report = []


def deep_ts(obj):
    best = ""
    def scan(o):
        nonlocal best
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, (str, int, float)):
                    nk = str(k).lower().replace("_", "").replace("-", "")
                    if any(p in nk for p in ("ts", "generated", "updated", "asof",
                                             "attempt", "scanned", "written")):
                        s = str(v)
                        if WALL.match(s) and s > best:
                            best = s
                else:
                    scan(v)
        elif isinstance(o, list):
            for it in o:
                scan(it)
    scan(obj)
    return best


def union_ledger(p, ledger_key, ident):
    dc = json.loads(blob(":2:" + p))
    dm = json.loads(blob(":3:" + p))
    hc, hm = dc[ledger_key], dm[ledger_key]
    seen, merged = set(), []
    for row in hc + hm:
        key = row[ident]
        if key not in seen:
            seen.add(key)
            merged.append(row)
    merged.sort(key=lambda r: str(r[ident]))
    ts_c, ts_m = deep_ts(dc), deep_ts(dm)
    src = dm if ts_m >= ts_c else dc
    out = dict(src)
    out[ledger_key] = merged
    json.loads(json.dumps(out))
    with open(p, "w", encoding="utf-8", newline="") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    report.append((p, f"union {len(hc)}+{len(hm)}->{len(merged)} on {ledger_key}/{ident}, state take-{'m' if ts_m >= ts_c else 'c'}"))


union_ledger("results/compute_audit.json", "history", "ts")
union_ledger("results/regime_state.json", "history", "asof")

# fundamental_status: manual truth-wins take-m
p = "results/fundamental_status.json"
ts_c = deep_ts(json.loads(blob(":2:" + p)))
ts_m = deep_ts(json.loads(blob(":3:" + p)))
data = blob(":3:" + p)
json.loads(data)
with open(p, "w", encoding="utf-8", newline="") as f:
    f.write(data)
report.append((p, f"take-m MANUAL truth-wins (c={ts_c} pre-fix rc2 face m={ts_m} post-fix rc0 face; fix rides this chain)"))

print("=== _r458bmb_resolve3.py (batch 3) ===")
for p, note in report:
    print(f"{p} | {note}")
