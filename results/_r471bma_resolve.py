"""r471 bm-a rebase-storm UU resolver (non-ALL_FACES 13 files).

Laws applied (bigmoney-conflict-resolve SKILL.md):
- snapshot take-new via hardened deep-ts probe: probe STAGED blobs (:2:/:3:), never worktree;
  key normalized (strip '_','-') prefix-match, value must match ^20\\d{2}-;
  wall-clock values require time-of-day ([T ]HH:MM) to feed max (r100/R350);
  ambiguity adjudicated by value shape ONLY, no key-exclude lists (R350);
  same-second tie -> HEAD side (:2:) per r140.
- twins (daily_report REPORT-*.json/.md, live_usage LIVE-* family): side decided on .json
  probe, ALL family members take SAME side, .md = same-side blob bytes (r327/r329/r439bmb).
- js-wrapper-snapshot (dashboard_status.js): same side as dashboard_status.json (single
  producer run), whole bytes, wrapper-shape verified (R209).
- results/_attrition_guard_scan.json UNKNOWN->manual adjudication: per-run whole-doc
  scan snapshot (r448 law, regenerated every round) -> snapshot take-new by deep-ts probe.
Zero re-serialization: whole-blob take only (r223/r234 mirror law).
"""
import json
import re
import subprocess
import sys

WALLCLOCK_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")
DATE_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}")
KEY_PROBES = ("asof", "generated", "updated", "ts", "cutoff", "scan", "last", "created")


def blob(stage: int, path: str) -> bytes:
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0 or not r.stdout:
        raise RuntimeError(f"stage {stage} read fail for {path}: {r.stderr[:200]!r}")
    return r.stdout


def probe_ts(obj, acc):
    """Deep-scan nested layers; collect wall-clock and date-only ts candidates."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            norm = str(k).replace("_", "").replace("-", "").lower()
            if isinstance(v, str):
                if any(norm.startswith(p) for p in KEY_PROBES):
                    if WALLCLOCK_RE.match(v):
                        acc[0].append(v)
                    elif DATE_RE.match(v):
                        acc[1].append(v)
            probe_ts(v, acc)
    elif isinstance(obj, list):
        for it in obj:
            probe_ts(it, acc)


def side_newer(path: str) -> int:
    """Return 2 or 3 by hardened deep-ts probe on staged blobs."""
    best = None
    for st in (2, 3):
        d = json.loads(blob(st, path).decode("utf-8"))
        acc = ([], [])
        probe_ts(d, acc)
        cand = max(acc[0]) if acc[0] else (max(acc[1]) if acc[1] else "")
        print(f"  :{st}: probe wall={len(acc[0])} date={len(acc[1])} best={cand!r}")
        if cand:
            if best is None or cand > best[1]:
                best = (st, cand)
            elif cand == best[1]:
                best = (2, cand)  # same-second tie -> HEAD side (:2:) r140
    if best is None:
        raise RuntimeError(f"no ts candidate either side for {path} -- fail-closed")
    return best[0]


def take(path: str, st: int, verify_json: bool = True) -> None:
    data = blob(st, path)
    if verify_json:
        json.loads(data.decode("utf-8"))
    with open(path, "wb") as f:
        f.write(data)
    print(f"  took :{st}: -> {path} ({len(data)}B)")


def resolve() -> int:
    decisions = {}

    # --- pure snapshots ---
    for p in [
        "results/dashboard_status.json",
        "results/fundamental_b_layer_filter.json",
        "results/scorecard_v1.json",
        "results/strategy_scorecard.json",
        "results/_attrition_guard_scan.json",
    ]:
        print(f"[snapshot] {p}")
        st = side_newer(p)
        take(p, st)
        decisions[p] = st

    # --- js wrapper: same side as dashboard_status.json, whole bytes ---
    js = "results/dashboard_status.js"
    st_js = decisions["results/dashboard_status.json"]
    raw = blob(st_js, js).decode("utf-8")
    m = re.search(r"window\.DASH_DATA\s*=\s*(\{.*\})\s*;?\s*$", raw, re.S)
    assert m, "DASH_DATA wrapper shape violated (R209)"
    json.loads(m.group(1))
    with open(js, "wb") as f:
        f.write(blob(st_js, js))
    print(f"[js-wrapper] {js} took :{st_js}: whole bytes, wrapper verified")
    decisions[js] = st_js

    # --- daily_report twin ---
    jr, mr = "docs/daily_report/REPORT-2026-09-30.json", "docs/daily_report/REPORT-2026-09-30.md"
    print(f"[twin] {jr}")
    st = side_newer(jr)
    take(jr, st)
    take(mr, st, verify_json=False)
    decisions[jr] = decisions[mr] = st

    # --- live_usage family (dated + latest pointers, ALL same side) ---
    j0 = "docs/live_usage/LIVE-2026-09-30.json"
    print(f"[twin-family] {j0}")
    st = side_newer(j0)
    for p in [j0, "docs/live_usage/LIVE-2026-09-30.md",
              "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"]:
        take(p, st, verify_json=p.endswith(".json"))
        decisions[p] = st

    # --- defensive: marks replay preservation check (r470 12:16/12:25 lines) ---
    marks = "results/paper/marks/marks-20260930.jsonl"
    txt = open(marks, "rb").read().decode("utf-8")
    ok1 = '"ts": "2026-09-30T12:16:19"' in txt
    ok2 = '"ts": "2026-09-30T12:25:08"' in txt
    print(f"[marks-check] 12:16:19={'OK' if ok1 else 'MISSING'} 12:25:08={'OK' if ok2 else 'MISSING'}")
    if not (ok1 and ok2):
        print("ERROR: r470 marks lines lost in replay")
        return 2

    print(json.dumps(decisions, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(resolve())
