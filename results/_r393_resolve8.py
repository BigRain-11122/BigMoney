"""r393 resolve #8: third-rebase stop #4 (part-1 commit replay) -- 14 files.

Per-file try/except (one non-conflicted face must NOT kill the batch --
resolve3 crash lesson live) + final ZERO-MARKER assertion before add.
  twins (REPORT/live_usage): take-new pair, whole bytes same side.
  compute_audit / regime_state: rolling-ledger union (r188/R208).
  everything else: snapshot take-new by value-shape wallclock probe
  (R208/R216); js follows its json twin (R209).
"""
import json
import re
import subprocess

TS_SHAPE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")
FILES = [
    "docs/daily_report/REPORT-2026-09-28.json",
    "docs/daily_report/REPORT-2026-09-28.md",
    "docs/live_usage/LIVE-2026-09-28.json",
    "docs/live_usage/LIVE-2026-09-28.md",
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/lhb_update_status.json",
    "results/prospect_promotion/_summary.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]


def bb(stage, path):
    return subprocess.run(["git", "show", f":{stage}:{path}"],
                           capture_output=True).stdout


def bj(stage, path):
    return json.loads(bb(stage, path))


def probe(obj, best=""):
    if isinstance(obj, dict):
        for v in obj.values():
            best = probe(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = probe(v, best)
    elif isinstance(obj, str) and TS_SHAPE.match(obj):
        best = max(best, obj)
    return best


done, skipped = [], []


def resolve_one(path):
    a3 = bb(3, path)
    if not a3:
        skipped.append(path)
        return
    # marker-safe: if only ONE side has stage blobs it's not a real
    # content conflict for us -> take ours bytes if theirs missing
    a2 = bb(2, path)
    if path.endswith(".json") and "compute_audit" not in path \
            and "regime_state" not in path:
        ta, tb = probe(bj(2, path)), probe(bj(3, path))
        side = 2 if tb <= ta else 3
        open(path, "wb").write(bb(side, path))
        done.append(f"{path}:take{'ours' if side == 2 else 'theirs'}"
                     f"({ta or '-'}|{tb or '-'})")
        return
    if path.endswith(".md") or path.endswith(".js"):
        # twins: side follows json sibling probe; REPORT/live_usage pairs
        jf = path.replace(".md", ".json").replace(".js", ".json")
        try:
            ta, tb = probe(bj(2, jf)), probe(bj(3, jf))
            side = 2 if tb <= ta else 3
        except Exception:
            side = 3
        open(path, "wb").write(bb(side, path))
        done.append(f"{path}:twin-side{side}")
        return
    # ledgers
    A, B = bj(2, path), bj(3, path)
    if "compute_audit" in path:
        seen, union = set(), []
        for row in A.get("history", []) + B.get("history", []):
            k = json.dumps(row, sort_keys=True, ensure_ascii=False)
            if k not in seen:
                seen.add(k)
                union.append(row)
        union.sort(key=lambda r: r.get("ts", ""))
        la = (A.get("latest") or {}).get("ts") or ""
        lb = (B.get("latest") or {}).get("ts") or ""
        merged = {"history": union,
                  "latest": (A if lb <= la else B).get("latest")}
        json.loads(json.dumps(merged))
        open(path, "w", encoding="utf-8").write(json.dumps(
            merged, ensure_ascii=False, indent=1))
        done.append(f"compute_audit:union {len(A['history'])}+"
                     f"{len(B['history'])}->{len(union)}")
        return
    if "regime_state" in path:
        merged = {}
        for key in ("history", "transitions"):
            if key in A or key in B:
                s2, u2 = set(), []
                for row in A.get(key, []) + B.get(key, []):
                    k = json.dumps(row, sort_keys=True, ensure_ascii=False)
                    if k not in s2:
                        s2.add(k)
                        u2.append(row)
                u2.sort(key=lambda r: r.get("ts", r.get("date", "")))
                merged[key] = u2
        state_side = A if probe(B) <= probe(A) else B
        for k, v in state_side.items():
            if k not in merged:
                merged[k] = v
        json.loads(json.dumps(merged))
        open(path, "w", encoding="utf-8").write(json.dumps(
            merged, ensure_ascii=False, indent=1))
        done.append("regime_state:union+take-new")
        return


for f in FILES:
    try:
        resolve_one(f)
    except Exception as exc:
        # honest per-file failure: report, DO NOT add silently later
        done.append(f"{f}:FAIL:{type(exc).__name__}:{exc}")

bad = []
for f in FILES:
    try:
        txt = open(f, "rb").read().decode("utf-8", errors="replace")
        if txt.startswith("<<<<<<<") or "\n<<<<<<< " in txt:
            bad.append(f)
    except FileNotFoundError:
        bad.append(f + ":MISSING")
print("RESOLVED/FAILED:")
for d in done:
    print(" ", d)
if skipped:
    print("SKIPPED (no stage blob):", skipped)
print("ZERO-MARKER CHECK:", "PASS" if not bad else f"FAIL {bad}")
raise SystemExit(1 if bad else 0)
