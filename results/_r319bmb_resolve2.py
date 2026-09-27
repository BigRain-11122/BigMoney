"""R319 bm-b rebase round-2 S6-mirror resolver (fixed union-key law).

Second same-window mirror batch (origin 0cc429af vs my b42970fe replay).
Adjudication: all snapshot faces mine-newer (11:47:49 vs 11:43:44) ->
take-new verbatim; ledger faces union with EXPLICIT per-face dedupe keys
(in-round lesson from resolver v1: union on a key absent from the entries
collapses |A|+|B| to 1 = silent zero-loss violation -> every union now
asserts len(result) == len(keyset(A) | keyset(B)) before write-back).

Dedupe keys (probed live): compute_audit.history=ts; regime_state.history
=asof; regime_state.transitions=ts (empty both sides tolerated).
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TAKE_NEW = [
    "docs/daily_report/REPORT-2026-09-27.json",
    "docs/daily_report/REPORT-2026-09-27.md",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/token_usage.json",
    "results/update_status.json",
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


def union_by_key(a, b, key):
    ka = {str(e.get(key, "")) for e in a}
    kb = {str(e.get(key, "")) for e in b}
    expect = len(ka | kb)
    seen = {}
    for src in (a, b):
        for e in src:
            seen.setdefault(str(e.get(key, "")), e)
    result = sorted(seen.values(), key=lambda e: str(e.get(key, "")))
    assert len(result) == expect, f"union collapse {len(a)}+{len(b)}->{len(result)} (expect {expect})"
    return result, expect


def detect_format(raw):
    crlf = b"\r\n" in raw
    nl = b"\r\n" if crlf else b"\n"
    indent = " "
    for line in raw.decode("utf-8-sig").splitlines():
        stripped = line.lstrip(" ")
        if stripped and line != stripped:
            indent = " " * (len(line) - len(stripped))
            break
    return indent, nl


def resolve_audit():
    path = "results/compute_audit.json"
    ours = json.loads(stage_bytes(path, 2).decode("utf-8-sig"))
    mine = json.loads(stage_bytes(path, 3).decode("utf-8-sig"))
    merged, expect = union_by_key(ours["history"], mine["history"], "ts")
    out = dict(mine)                     # mine = newer snapshot fields
    out["history"] = merged
    newer = ours if str(ours["latest"]["ts"]) > str(mine["latest"]["ts"]) else mine
    out["latest"] = newer["latest"]
    indent, nl = detect_format(stage_bytes(path, 3))
    (ROOT / path).write_bytes(
        (json.dumps(out, ensure_ascii=False, indent=indent) + "\n")
        .encode("utf-8").replace(b"\n", nl))
    json.loads((ROOT / path).read_text(encoding="utf-8-sig"))
    print(f"  {path}: history union -> {len(merged)} (expect {expect}), "
          f"latest.ts={out['latest']['ts']}")


def resolve_regime():
    path = "results/regime_state.json"
    ours = json.loads(stage_bytes(path, 2).decode("utf-8-sig"))
    mine = json.loads(stage_bytes(path, 3).decode("utf-8-sig"))
    out = dict(mine)                     # mine newer (updated 11:47:46)
    hist, hexp = union_by_key(ours.get("history") or [],
                              mine.get("history") or [], "asof")
    trans, texp = union_by_key(ours.get("transitions") or [],
                               mine.get("transitions") or [], "ts")
    out["history"] = hist
    out["transitions"] = trans
    indent, nl = detect_format(stage_bytes(path, 3))
    (ROOT / path).write_bytes(
        (json.dumps(out, ensure_ascii=False, indent=indent) + "\n")
        .encode("utf-8").replace(b"\n", nl))
    json.loads((ROOT / path).read_text(encoding="utf-8-sig"))
    print(f"  {path}: history union -> {len(hist)} (expect {hexp}), "
          f"transitions -> {len(trans)} (expect {texp}), "
          f"updated={out['updated']}")


def main():
    resolved = []
    for path in TAKE_NEW:
        if not has_stages(path):
            print(f"  skip (no stages): {path}")
            continue
        raw = stage_bytes(path, 3)
        (ROOT / path).write_bytes(raw)
        if path.endswith(".json"):
            json.loads((ROOT / path).read_text(encoding="utf-8-sig"))
        print(f"  {path}: take-new :3: verbatim ({len(raw)}B)")
        resolved.append(path)
    for path in ("results/compute_audit.json", "results/regime_state.json"):
        if has_stages(path):
            (resolve_audit if "compute" in path else resolve_regime)()
            resolved.append(path)
    for path in resolved:
        subprocess.run(["git", "add", "--", path], check=True)
    print(f"resolved={len(resolved)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
