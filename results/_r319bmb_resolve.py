"""R319 bm-b rebase S6-mirror batch resolver (bigmoney-conflict-resolve canon).

Rebase of r319 commit onto origin 323150a0 hit the familiar same-window
S6-mirror batch (both machines ran the full S6 lane chain ~11:40 vs ~11:48).
Classifier: 10 auto + 5 UNKNOWN hand-adjudicated per r317-addendum precedent
(daily_report twins + scorecards + promotion summary = deterministic
same-day re-derivation -> newest generated wins wholesale).

Adjudication evidence (stage :2: origin vs :3: mine):
  daily_report.json   generated_at 11:41:01 vs 11:49:00  -> mine
  prospect_promotion  generated    11:40:58 vs 11:48:46  -> mine
  scorecard_v1        generated    11:40:32 vs 11:47:48  -> mine
  strategy_scorecard  generated    11:40:38 vs 11:47:59  -> mine
  fundamental/futures/heat/lhb/token/update/dashboard   -> mine (all newer)

Recipes (per SKILL.md):
  take-new (whole stage bytes verbatim, zero re-serialization risk):
    13 snapshot/re-derivation faces -> write :3: bytes.
  union-ledger (zero row loss):
    compute_audit.json  -> history union by ts, latest = newer-ts side.
    regime_state.json   -> transitions + history union by ts, fields newer.
  Format mirror: union files re-serialized with indent/CRLF detected from
  the side being kept; every .json re-parsed before write-back (r185 law).
Idempotent: refuses paths without unmerged stages.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TAKE_NEW = [
    "docs/daily_report/REPORT-2026-09-27.json",
    "docs/daily_report/REPORT-2026-09-27.md",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/token_usage.json",
    "results/update_status.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
]


def stage_bytes(path, n):
    r = subprocess.run(["git", "show", f":{n}:{path}"], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def has_stages(path):
    r = subprocess.run(["git", "ls-files", "-u", "--", path],
                       capture_output=True, text=True)
    return bool(r.stdout.strip())


def detect_format(raw):
    """(indent_str, newline_bytes) mirror probe from raw stage bytes."""
    crlf = b"\r\n" in raw
    nl = b"\r\n" if crlf else b"\n"
    indent = " "
    for line in raw.decode("utf-8-sig").splitlines():
        stripped = line.lstrip(" ")
        if stripped and line != stripped:
            indent = " " * (len(line) - len(stripped))
            break
    return indent, nl


def union_by_ts(a, b):
    """List union deduped on entry ts (stable, sorted by ts)."""
    seen = {}
    for src in (a, b):
        for e in src:
            k = str(e.get("ts", ""))
            seen.setdefault(k, e)
    return sorted(seen.values(), key=lambda e: str(e.get("ts", "")))


def resolve_union(path, list_keys, ts_key="ts"):
    ours = json.loads(stage_bytes(path, 2).decode("utf-8-sig"))
    mine = json.loads(stage_bytes(path, 3).decode("utf-8-sig"))
    for k in list_keys:
        merged = union_by_ts(ours.get(k) or [], mine.get(k) or [])
        ours[k] = merged
        print(f"  {path}: {k} union |ours|+|mine| -> {len(merged)}")
    newer = ours if str(ours.get(ts_key, "")) >= str(mine.get(ts_key, "")) \
        else mine
    for k in mine:
        if k not in list_keys:
            ours[k] = newer[k]          # newest side wins on state fields
    indent, nl = detect_format(stage_bytes(path, 3))
    text = json.dumps(ours, ensure_ascii=False, indent=indent) + "\n"
    p = ROOT / path
    p.write_bytes(text.encode("utf-8").replace(b"\n", nl))
    json.loads(p.read_text(encoding="utf-8-sig"))    # r185 parse gate
    print(f"  {path}: union written ({ts_key} kept={newer.get(ts_key)})")


def resolve_take_new(path):
    raw = stage_bytes(path, 3)
    if raw is None:
        print(f"  {path}: no :3: stage -- skip")
        return False
    (ROOT / path).write_bytes(raw)
    if path.endswith(".json"):
        json.loads((ROOT / path).read_text(encoding="utf-8-sig"))
    print(f"  {path}: take-new (:3: mine newer, {len(raw)}B verbatim)")
    return True


def main():
    todo = TAKE_NEW + ["results/compute_audit.json", "results/regime_state.json"]
    resolved, skipped = [], []
    for path in todo:
        if not has_stages(path):
            skipped.append(path)
            continue
        if path == "results/compute_audit.json":
            resolve_union(path, ["history"])
        elif path == "results/regime_state.json":
            resolve_union(path, ["transitions", "history"], ts_key="updated")
        else:
            if not resolve_take_new(path):
                continue
        resolved.append(path)
    for path in resolved:
        subprocess.run(["git", "add", "--", path], check=True)
    print(f"resolved={len(resolved)} skipped(no stages)={len(skipped)}")
    for s in skipped:
        print(f"  skip: {s}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
