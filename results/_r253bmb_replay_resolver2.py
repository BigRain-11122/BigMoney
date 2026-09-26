"""R253 bm-b push-replay conflict resolver #2 (third-cycle 14-UU batch vs
bm-a r249). Sides: :2 ours = origin/main (bm-a r249, S6 faces 14:01:52-14:02:19
= NEWEST per ts probe), :3 theirs = my r253 commit (14:00:13-14:01:02).

Recipes:
  - 12 snapshot faces (regime/fundamental/futures/heat/lhb/token/update/
    dashboard json+js/daily_report pair/prospect_promotion summary):
    take-OURS whole-byte (newest measurement face; r242 ts-probe law).
  - compute_audit.json: rolling-ledger union zero-loss; latest = ours
    (14:01:50); EOL/indent mirrored from blob probe.
  - CODELY.md: memory-union (r212): base + ours-added + theirs-added.
Verification: json.loads each written json (r185); js wrapper sanity;
union counts printed.
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

TAKE_OURS_WHOLE = [
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
    "results/prospect_promotion/_summary.json",
]

def main() -> int:
    report = []
    for p in TAKE_OURS_WHOLE:
        data = blob(2, p)
        with open(p, "wb") as fh:
            fh.write(data)
        if p.endswith(".json"):
            json.loads(open(p, "rb").read().decode("utf-8"))
        elif p.endswith(".js"):
            assert b"window.DASH_DATA" in data, "js wrapper sanity"
        report.append((p, "take-ours whole-byte (bm-a r249 newest ts)",
                       len(data)))

    # compute_audit rolling-ledger union, latest = ours (newest 14:01:50)
    p = "results/compute_audit.json"
    b2, b3 = blob(2, p), blob(3, p)
    d2, d3 = json.loads(b2.decode("utf-8")), json.loads(b3.decode("utf-8"))
    seen, union = set(), []
    for e in d2.get("history", []) + d3.get("history", []):
        k = e.get("ts")
        if k in seen:
            continue
        seen.add(k)
        union.append(e)
    merged = dict(d2)                       # newest latest face (ours)
    merged["history"] = union
    eol = b"\r\n" if b"\r\n" in b2[:2000] else b"\n"
    text = json.dumps(merged, ensure_ascii=False, indent=1)
    with open(p, "wb") as fh:
        fh.write(text.encode("utf-8").replace(b"\n", eol))
    json.loads(open(p, "rb").read().decode("utf-8"))
    report.append((p, f"union |{len(d2['history'])}|+|{len(d3['history'])}|"
                    f"->|{len(union)}| latest=ours(14:01:50)", len(union)))

    # CODELY.md memory-union
    p = "CODELY.md"
    base = blob(1, p).decode("utf-8").splitlines()
    ours = blob(2, p).decode("utf-8").splitlines()
    theirs = blob(3, p).decode("utf-8").splitlines()
    base_set = set(base)
    added_ours = [l for l in ours if l not in base_set]
    added_theirs = [l for l in theirs if l not in base_set]
    merged_lines = base + added_ours + \
        [l for l in added_theirs if l not in set(added_ours)]
    with open(p, "wb") as fh:
        fh.write(("\n".join(merged_lines) + "\n").encode("utf-8"))
    report.append((p, f"memory-union base|{len(base)}| +ours {len(added_ours)}"
                    f" +theirs {len(added_theirs)}", len(merged_lines)))

    for r in report:
        print(f"RESOLVED {r[0]} :: {r[1]} ({r[2]})", flush=True)
    return 0

if __name__ == "__main__":
    sys.exit(main())
