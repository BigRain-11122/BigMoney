"""r226 rebase conflict resolution APPLY step.

- 16 pure-derive faces: git checkout --theirs (r226 side verified newer by
  content-level ts on every pair)
- results/compute_audit.json: latest = newer-ts side (r226 16:19:09); history
  = union of both sides deduped by ts, oldest-first order, cap 201 (r221 canon)
- verify: zero conflict markers in all resolved files, then git add
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TAKE_THEIRS = [
    "docs/daily_report/REPORT-2026-09-29.json",
    "docs/daily_report/REPORT-2026-09-29.md",
    "docs/live_usage/LIVE-2026-09-29.json",
    "docs/live_usage/LIVE-2026-09-29.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
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
AUDIT = "results/compute_audit.json"


def run(args):
    return subprocess.run(args, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", cwd=ROOT)


def main() -> int:
    # 1. take-theirs for pure derive faces
    for f in TAKE_THEIRS:
        r = run(["git", "checkout", "--theirs", f])
        print(f"[take-theirs] {f} rc={r.returncode}"
              + (f" ERR={r.stderr.strip()[:120]}" if r.returncode else ""))
        if r.returncode:
            return 2

    # 2. compute_audit union (blob-level rebuild, no marker editing)
    ours = json.loads(run(["git", "show", f":2:{AUDIT}"]).stdout)
    theirs = json.loads(run(["git", "show", f":3:{AUDIT}"]).stdout)
    latest = theirs if (theirs["latest"]["ts"] > ours["latest"]["ts"]) else ours
    seen, union = set(), []
    for entry in ours["history"] + theirs["history"]:
        ts = entry.get("ts")
        if ts in seen:
            continue
        seen.add(ts)
        union.append(entry)
    union.sort(key=lambda e: e.get("ts", ""))
    if len(union) > 201:
        union = union[-201:]
    merged = {"latest": latest, "history": union}
    (ROOT / AUDIT).write_text(
        json.dumps(merged, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    print(f"[audit-union] latest ts={latest['latest']['ts'] if isinstance(latest, dict) else latest.get('ts')} "
          f"history union={len(union)} (ours={len(ours['history'])} "
          f"theirs={len(theirs['history'])}) cap=201")

    # 3. verify zero conflict markers in all 17 resolved files
    bad = []
    for f in TAKE_THEIRS + [AUDIT]:
        text = (ROOT / f).read_text(encoding="utf-8", errors="replace")
        if "<<<<<<<" in text or ">>>>>>>" in text:
            bad.append(f)
    print(f"[verify] conflict-marker scan: {len(bad)} dirty {bad}")
    if bad:
        return 2

    # 4. git add resolved files
    for f in TAKE_THEIRS + [AUDIT]:
        r = run(["git", "add", f])
        if r.returncode:
            print(f"[add-ERR] {f}: {r.stderr.strip()[:120]}")
            return 2
    st = run(["git", "status", "--porcelain"])
    unmerged = [l for l in st.stdout.splitlines()
                if l[:2] in ("UU", "AA", "DU", "UD", "AU", "UA", "DD")]
    print(f"[verify] remaining unmerged: {len(unmerged)} {unmerged}")
    return 0 if not unmerged else 2


if __name__ == "__main__":
    sys.exit(main())
