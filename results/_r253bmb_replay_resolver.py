"""R253 bm-b push-replay conflict resolver (13-UU batch vs bm-a r248).

Sides (rebase semantics, r245 law): :2 ours = origin/main (bm-a r248 face),
:3 theirs = my r253 commit being replayed.

Recipes per classify_conflicts.py + SKILL.md table:
  - 7 snapshots (regime_state/fundamental_b_layer_filter/futures/heat/lhb/
    token_usage/update_status): take-new by probed ts -- ALL probes put the
    r253 face newest (14:00-14:01 vs bm-a 13:55) -> take :3 whole-byte.
  - dashboard_status.json (meta.generated_at 14:01:00 > 13:55:47) + .js
    wrapper: take :3 whole-byte same side (R209 js-wrapper law).
  - daily_report REPORT-2026-09-26 json (generated_at 14:00:58 > 13:55:45)
    + md twin: same-side whole-byte (r242 daily-report-pair precedent).
  - compute_audit.json: rolling-ledger -- history union by ts zero-loss,
    latest = take-new (:3, 14:00:05); EOL+indent mirrored from blob probe.
  - CODELY.md: memory-union (r212) -- base + ours-added + theirs-added,
    dedupe identical lines.
Verification (post-write law r185): json.loads every written json; js
wrapper sanity; zero-loss counts printed. runnable_pool.json auto-merged
by git -- verified separately (CN-REV done flip + T80 entry present).
"""

import json
import subprocess
import sys

def blob(side: int, path: str) -> bytes:
    out = subprocess.run(["git", "show", f":{side}:{path}"],
                         capture_output=True)
    if out.returncode != 0:
        raise SystemExit(f"blob read fail {side}:{path}")
    return out.stdout

TAKE_MINE_WHOLE = [
    "results/regime_state.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/token_usage.json",
    "results/update_status.json",
    "results/dashboard_status.json",
    "results/dashboard_status.js",
    "docs/daily_report/REPORT-2026-09-26.json",
    "docs/daily_report/REPORT-2026-09-26.md",
]

def main() -> int:
    report = []

    # -- whole-byte take-mine (newest measurement face per ts probe)
    for p in TAKE_MINE_WHOLE:
        data = blob(3, p)
        with open(p, "wb") as fh:
            fh.write(data)
        if p.endswith(".json"):
            json.loads(open(p, "rb").read().decode("utf-8"))   # r185 law
        elif p.endswith(".js"):
            assert b"window.DASH_DATA" in data, "js wrapper sanity"
        report.append((p, "take-mine whole-byte", len(data)))

    # -- compute_audit.json: rolling-ledger union + latest take-new
    p = "results/compute_audit.json"
    b2, b3 = blob(2, p), blob(3, p)
    d2, d3 = json.loads(b2.decode("utf-8")), json.loads(b3.decode("utf-8"))
    hist2, hist3 = d2.get("history", []), d3.get("history", [])
    seen, union = set(), []
    for e in hist2 + hist3:                       # base-side first (stable)
        k = e.get("ts")
        if k in seen:
            continue
        seen.add(k)
        union.append(e)
    merged = dict(d3)                             # newest latest face
    merged["history"] = union
    eol = b"\r\n" if b"\r\n" in b3[:2000] else b"\n"
    indent = 1                                    # producer caliber (probe)
    text = json.dumps(merged, ensure_ascii=False, indent=indent)
    with open(p, "wb") as fh:
        fh.write(text.encode("utf-8").replace(b"\n", eol))
    json.loads(open(p, "rb").read().decode("utf-8"))       # r185 law
    report.append((p, f"rolling-ledger union |{len(hist2)}+{len(hist3)}"
                    f"->|{len(union)}| latest=mine(14:00:05)",
                    len(union)))

    # -- CODELY.md: memory-union (r212)
    p = "CODELY.md"
    base = blob(1, p).decode("utf-8").splitlines()
    ours = blob(2, p).decode("utf-8").splitlines()
    theirs = blob(3, p).decode("utf-8").splitlines()
    base_set = set(base)
    added_ours = [l for l in ours if l not in base_set]
    added_theirs = [l for l in theirs if l not in base_set]
    merged_lines = base + added_ours + \
        [l for l in added_theirs if l not in set(added_ours)]
    text = "\n".join(merged_lines) + ("\n" if merged_lines else "")
    with open(p, "wb") as fh:
        fh.write(text.encode("utf-8"))
    report.append((p, f"memory-union base|{len(base)}| +ours {len(added_ours)}"
                    f" +theirs {len(added_theirs)}", len(merged_lines)))

    # -- runnable_pool.json auto-merge verification (both faces present)
    p = "results/runnable_pool.json"
    pool = json.loads(open(p, "rb").read().decode("utf-8"))
    by_id = {e.get("id"): e for e in pool["entries"]}
    cn = by_id.get("CN-REV-TILT-P1", {})
    t80 = by_id.get("T80-AGGR-FULLPOOL-BATTERY", {})
    assert cn.get("status") == "done", f"CN-REV flip lost: {cn.get('status')}"
    assert t80.get("status") == "ready" and t80.get("lane_owner") == "bm-a", \
        "T80 entry lost in auto-merge"
    report.append((p, "auto-merge verified (CN-REV done + T80 ready lane bm-a)",
                    len(pool["entries"])))

    for r in report:
        print(f"RESOLVED {r[0]} :: {r[1]} ({r[2]})", flush=True)
    return 0

if __name__ == "__main__":
    sys.exit(main())
