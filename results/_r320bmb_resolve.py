# -*- coding: utf-8 -*-
"""R320 bm-b rebase S6-mirror resolver (canon: r319 v2 + r317 autofill union).

Push-collision rebase replay vs origin c94907a5 (bm-a r319 S6 window).
Probe (_r320bmb_probe.py): ALL snapshot faces mine-newer (12:06-12:08 vs
12:00:08-12:00:54) -> take-new :3: verbatim. Ledger faces union with
explicit per-face dedupe keys + len==|keyset-union| zero-loss assert
(r319 law); autofill_state via r317 stage-union canon (launches key-union,
HEAD-priority, last_tick newer-ts whole-dict).
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TAKE_NEW = [
    "docs/daily_report/REPORT-2026-09-27.json",
    "docs/daily_report/REPORT-2026-09-27.md",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/dashboard_status.js",          # js-wrapper: whole bytes (R209 law)
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/token_usage.json",
    "results/update_status.json",
]

AUTOFFILL_KEY = ("ts", "machine", "entry", "shard", "pid")


def stage_bytes(path, n):
    r = subprocess.run(["git", "show", f":{n}:{path}"], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def has_stages(path):
    r = subprocess.run(["git", "ls-files", "-u", "--", path],
                       capture_output=True, text=True)
    return bool(r.stdout.strip())


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


def union_by_key(a, b, key):
    ka = {str(e.get(key, "")) for e in a}
    kb = {str(e.get(key, "")) for e in b}
    expect = len(ka | kb)
    seen = {}
    for src in (a, b):
        for e in src:
            seen.setdefault(str(e.get(key, "")), e)
    result = sorted(seen.values(), key=lambda e: str(e.get(key, "")))
    assert len(result) == expect, \
        f"union collapse {len(a)}+{len(b)}->{len(result)} (expect {expect})"
    return result, expect


def resolve_audit():
    path = "results/compute_audit.json"
    ours = json.loads(stage_bytes(path, 2).decode("utf-8-sig"))
    mine = json.loads(stage_bytes(path, 3).decode("utf-8-sig"))
    merged, expect = union_by_key(ours["history"], mine["history"], "ts")
    out = dict(mine)                     # mine = newer snapshot fields
    out["history"] = merged
    newer = ours if str(ours["latest"]["ts"]) > str(mine["latest"]["ts"]) \
        else mine
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
    out = dict(mine)                     # mine newer (12:06:41 vs 12:00:17)
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
          f"transitions -> {len(trans)} (expect {texp}), updated={out['updated']}")


def resolve_autofill():
    path = "results/autofill_state.json"
    ours = json.loads(stage_bytes(path, 2).decode("utf-8-sig"))
    mine = json.loads(stage_bytes(path, 3).decode("utf-8-sig"))
    seen = {}
    for src in (ours, mine):            # HEAD face (:2) wins key collisions
        for e in src.get("launches", []):
            k = tuple(e.get(f) for f in AUTOFFILL_KEY)
            seen.setdefault(k, e)
    merged = dict(mine)
    merged["launches"] = sorted(seen.values(),
                                key=lambda e: str(e.get("ts", "")))
    faces = [f for f in (ours.get("last_tick"), mine.get("last_tick")) if f]
    merged["last_tick"] = max(faces, key=lambda f: str(f.get("ts", ""))) \
        if faces else None
    text = json.dumps(merged, ensure_ascii=False, indent=1) + "\r\n"
    (ROOT / path).write_bytes(text.encode("utf-8"))
    chk = json.loads((ROOT / path).read_text(encoding="utf-8-sig"))
    assert isinstance(chk["last_tick"], dict), "last_tick must stay dict"
    print(f"  {path}: launches union -> {len(chk['launches'])} entries "
          f"(|A|={len(ours.get('launches', []))} |B|={len(mine.get('launches', []))}), "
          f"last_tick.ts={chk['last_tick']['ts']}")


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
    for path in ("results/compute_audit.json", "results/regime_state.json",
                 "results/autofill_state.json"):
        if has_stages(path):
            (resolve_audit if "compute" in path else
             resolve_regime if "regime" in path else resolve_autofill)()
            resolved.append(path)
    for path in resolved:
        subprocess.run(["git", "add", "--", path], check=True)
    print(f"resolved={len(resolved)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
