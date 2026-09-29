"""r226 rebase conflict resolution: blob-level compare + union (pit law: never
hand-edit conflicted working-tree files; rebuild from clean index blobs).

Strategy (r221/r225/bm-a-r436 canon):
- pure derive faces: deep-ts take-new (later regeneration wins, same cutoff
  idempotent derives)
- compute_audit.json: latest by ts at top level + history union by ts, cap 201
- token_usage.json: structure-inspect -> keyed-dict union vs take-new
Prints a per-file decision table; applies nothing (dry-run first).
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FILES = [
    "docs/daily_report/REPORT-2026-09-29.json",
    "docs/daily_report/REPORT-2026-09-29.md",
    "docs/live_usage/LIVE-2026-09-29.json",
    "docs/live_usage/LIVE-2026-09-29.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/compute_audit.json",
    "results/dashboard_status.js",
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


def blob(stage, path):
    out = subprocess.run(
        ["git", "show", f":{stage}:{path}"],
        capture_output=True, cwd=ROOT)
    if out.returncode != 0:
        return None
    return out.stdout.decode("utf-8", errors="replace")


def find_ts(text):
    for key in ("ts", "generated", "generated_at", "updated", "updated_at"):
        try:
            obj = json.loads(text)
        except Exception:
            continue
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == key and isinstance(v, str):
                    return v
            for v in obj.values():
                if isinstance(v, dict):
                    for k2, v2 in v.items():
                        if k2 == key and isinstance(v2, str):
                            return v2
    return None


def main():
    print(f"{'file':58s} {'ours(origin)':22s} {'theirs(r226)':22s} decision")
    for f in FILES:
        ours = blob(2, f)
        theirs = blob(3, f)
        if ours is None or theirs is None:
            print(f"{f:58s} BLOB-MISSING ours={ours is None} "
                  f"theirs={theirs is None}")
            continue
        if ours == theirs:
            print(f"{f:58s} {'':22s} {'':22s} IDENTICAL")
            continue
        to, tt = find_ts(ours) or "?", find_ts(theirs) or "?"
        if f == "results/compute_audit.json":
            dec = "UNION-HISTORY"
        elif f == "results/token_usage.json":
            dec = "INSPECT"
        else:
            dec = "TAKE-THEIRS" if tt > to else "TAKE-OURS"
        print(f"{f:58s} {to:22s} {tt:22s} {dec}")
    # structure inspect for the two special faces
    for f in ("results/token_usage.json", "results/compute_audit.json"):
        for stage, side in ((2, "ours"), (3, "theirs")):
            text = blob(stage, f)
            if not text:
                continue
            try:
                obj = json.loads(text)
            except Exception:
                print(f"[inspect {f} {side}] non-JSON head: "
                      f"{text[:120]!r}")
                continue
            keys = list(obj.keys()) if isinstance(obj, dict) else f"list[{len(obj)}]"
            print(f"[inspect {f} {side}] top keys: {keys}")
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if isinstance(v, list):
                        print(f"    {k}: list len={len(v)} "
                              f"first={json.dumps(v[0])[:150] if v else '-'}")
                    elif isinstance(v, dict):
                        print(f"    {k}: dict keys={list(v.keys())[:10]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
