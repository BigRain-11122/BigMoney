"""R381 bm-a push-storm 15-UU canon resolver.

Classes (bigmoney-conflict-resolve law + r377 resolve subcommand):
  * ALL_FACES (autofill_state/compute_audit/regime_state):
    scripts/merge_lane_views.py resolve <path>  (union recipes, r376 law)
  * B snapshots (update_status/token_usage/futures_update_status/
    lhb_update_status/fundamental_b_layer_filter): staged-blob deep-ts
    probe take-new (:2: origin vs :3: mine; tie -> :2: origin, r140)
  * C twins (dashboard_status.json/.js, scorecard_v1, strategy_scorecard,
    prospect_promotion/_summary, daily_report REPORT json/md):
    host side whole bytes (host=bm-a = replay side :3:, R209 js
    whole-bytes / r98 twins same-side; bm-b side = stale-takeover derive,
    designed tolerance, host wins)
"""
import json
import subprocess
import sys

ROOT = "results/"


def sh(args):
    r = subprocess.run(args, capture_output=True)
    return r.returncode, r.stdout, r.stderr


ALL_FACES_UU = [
    "results/autofill_state.json",
    "results/compute_audit.json",
    "results/regime_state.json",
]
B_PROBE_UU = [
    # (path, probe key list -- first hit wins at top level, else 'ts')
    ("results/update_status.json", ["updated", "ts"]),
    ("results/token_usage.json", ["ts", "updated"]),
    ("results/futures_update_status.json", ["updated", "ts"]),
    ("results/lhb_update_status.json", ["updated", "ts"]),
    ("results/fundamental_b_layer_filter.json", ["ts", "updated",
                                                 "generated"]),
]
C_TAKE_MINE = [
    "results/dashboard_status.json",
    "results/dashboard_status.js",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/prospect_promotion/_summary.json",
    "docs/daily_report/REPORT-2026-09-28.json",
    "docs/daily_report/REPORT-2026-09-28.md",
]

results = []

# 1) ALL_FACES: canonical resolve one-liner
for path in ALL_FACES_UU:
    rc, out, err = sh([sys.executable, "scripts/merge_lane_views.py",
                       "resolve", path])
    tail = out.decode("utf-8", errors="replace").strip().splitlines()
    last = tail[-1] if tail else (err.decode()[:120])
    ok = rc == 0 and "parse-verified" in out.decode("utf-8",
                                                    errors="replace")
    results.append((path, "ALL_FACES-resolve", ok, last[:150]))

# 2) B snapshots: staged-blob deep-ts probe take-new
for path, keys in B_PROBE_UU:
    rc2, b2, _ = sh(["git", "show", f":2:{path}"])
    rc3, b3, _ = sh(["git", "show", f":3:{path}"])
    if rc2 != 0 or rc3 != 0:
        results.append((path, "B-probe", False, "stage read fault"))
        continue
    d2 = json.loads(b2.decode("utf-8"))
    d3 = json.loads(b3.decode("utf-8"))

    def probe(d):
        for k in keys:
            if k in d:
                return str(d[k])
        return str(d.get("ts", ""))

    p2, p3 = probe(d2), probe(d3)
    side = "--theirs" if p3 > p2 else "--ours"      # tie -> :2: origin (r140)
    rc, _, err = sh(["git", "checkout", side, path])
    results.append((path, f"B-take-new p2={p2} p3={p3} -> "
                    f"{':3: mine' if side == '--theirs' else ':2: origin'}",
                    rc == 0, err.decode()[:100]))

# 3) C twins: host side whole bytes (mine = :3: = --theirs in rebase)
for path in C_TAKE_MINE:
    rc, _, err = sh(["git", "checkout", "--theirs", path])
    results.append((path, "C-host-take-mine", rc == 0,
                    err.decode()[:100]))

for path, kind, ok, note in results:
    print(f"[{'OK' if ok else 'FAIL'}] {kind} :: {path} :: {note}")
sys.exit(0 if all(r[2] for r in results) else 1)
