"""r273 bm-c push-collision rebase resolver (canon recipes, bigmoney-conflict-resolve).

Conflict set: 18 UU shared-snapshot faces (structural per F-20260927-06; bm-a
r475 push-window collision, same treadmill as r271 18-UU / r272 14-UU).
Direction law (r461): NEVER assume base=new in a replay -- probe BOTH staged
blobs per file and assert the chosen side's ts is strictly newer (tie ->
HEAD/ours = stage2 per r140).
Probe laws: r100 (value must be ts-shaped WITH time-of-day), r311/R208
(deep-scan nested layers), R350 (key-EXCLUDE lists forbidden, value-shape
gate only), staged-blob probe only (:2:/:3:, never working tree).
Recipes: snapshot=take-new(+twin same-side); rolling-ledger=union history
zero-loss + take-new state fields (r459 union assertion |A u B| >= max).
New members vs r272: DASH twins (dashboard_status.js/.json), scorecard twins
(strategy_scorecard.json + scorecard_v1.json, one derive run -> same-side).
Rebase stage semantics: stage2 = HEAD = origin side (bm-a r475); stage3 =
replayed commit = THIS MACHINE's side (bm-c r273).
"""
import json
import re
import subprocess
import sys

TS_RE = re.compile(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2})?")
TS_FULL_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2}(\.\d+)?)?(\+\d{2}:\d{2})?$")


def blob_bytes(stage: int, path: str) -> bytes:
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git show :{stage}:{path} rc={r.returncode}")
    return r.stdout


def deep_ts(obj, best=""):
    """Deep-scan all string values; wall-clock candidates must be ts-shaped
    with time-of-day (R350 value-shape gate, no key excludes)."""
    if isinstance(obj, dict):
        for v in obj.values():
            best = deep_ts(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = deep_ts(v, best)
    elif isinstance(obj, str):
        for m in TS_RE.finditer(obj):
            cand = m.group(0)
            if len(cand) >= 16 and cand > best:  # date+HH:MM minimum = wall clock
                best = cand
    return best


def probe(stage: int, path: str) -> str:
    b = blob_bytes(stage, path)
    if path.endswith(".json"):
        return deep_ts(json.loads(b.decode("utf-8")))
    text = b.decode("utf-8", errors="replace")
    m = TS_RE.findall(text)
    return max(m) if m else ""


def take(path: str, stage: int):
    b = blob_bytes(stage, path)
    with open(path, "wb") as f:
        f.write(b)
    subprocess.run(["git", "add", path], check=True)
    return f"take-s{stage}"


def union_ledger(path: str, list_keys, ident_fn, newer_stage: int):
    a = json.loads(blob_bytes(2, path).decode("utf-8"))   # origin
    b = json.loads(blob_bytes(3, path).decode("utf-8"))   # mine
    out = dict(b if newer_stage == 3 else a)               # take-new top fields
    report = []
    for k in list_keys:
        la, lb = a.get(k) or [], b.get(k) or []
        seen, union = set(), []
        for e in la + lb:
            key = ident_fn(e)
            if key in seen:
                continue
            seen.add(key)
            union.append(e)
        union.sort(key=ident_fn)
        assert len(union) >= max(len(la), len(lb)), f"{path}.{k} union loss"
        out[k] = union
        report.append(f"{k}:{len(la)}+{len(lb)}->{len(union)}")
    raw = blob_bytes(newer_stage, path).decode("utf-8")
    m2 = re.search(r"\n( +)\"", raw)
    indent = len(m2.group(1)) if m2 else 1
    with open(path, "w", encoding="utf-8", newline="") as f:
        json.dump(out, f, ensure_ascii=False, indent=indent)
        f.write("\n")
    subprocess.run(["git", "add", path], check=True)
    return "; ".join(report)


def main() -> int:
    log = []
    twin_groups = {
        "REPORT": ["docs/daily_report/REPORT-2026-09-30.json",
                   "docs/daily_report/REPORT-2026-09-30.md"],
        "LIVE": ["docs/live_usage/LIVE-2026-09-30.json",
                 "docs/live_usage/LIVE-2026-09-30.md",
                 "docs/live_usage/LIVE-latest.json",
                 "docs/live_usage/LIVE-latest.md"],
        "DASH": ["results/dashboard_status.js",
                 "results/dashboard_status.json"],
        "SCORECARD": ["results/strategy_scorecard.json",
                      "results/scorecard_v1.json"],
    }
    for gname, paths in twin_groups.items():
        t2, t3 = probe(2, paths[0]), probe(3, paths[0])
        side = 3 if t3 > t2 else 2  # tie -> HEAD/ours stage2 (r140)
        for p in paths:
            take(p, side)
        log.append(f"twin-{gname}: s2={t2} s3={t3} -> take-s{side} x{len(paths)}")
    snaps = [
        "results/_attrition_guard_scan.json",
        "results/fundamental_b_layer_filter.json",
        "results/futures_update_status.json",
        "results/lhb_update_status.json",
        "results/token_usage.json",
        "results/update_status.json",
    ]
    for p in snaps:
        t2, t3 = probe(2, p), probe(3, p)
        assert TS_FULL_RE.match(t2) and TS_FULL_RE.match(t3), f"{p}: probe not ts-shaped ({t2!r} vs {t3!r})"
        side = 3 if t3 > t2 else 2
        take(p, side)
        log.append(f"{p}: s2={t2} s3={t3} -> take-s{side}")
    t2, t3 = probe(2, "results/compute_audit.json"), probe(3, "results/compute_audit.json")
    newer = 3 if t3 > t2 else 2
    log.append("compute_audit: union[" + union_ledger(
        "results/compute_audit.json", ["history"],
        lambda e: e.get("ts") or "", newer) + f"] latest-take-s{newer} (s2={t2} s3={t3})")
    t2, t3 = probe(2, "results/regime_state.json"), probe(3, "results/regime_state.json")
    newer = 3 if t3 > t2 else 2
    log.append("regime_state: union[" + union_ledger(
        "results/regime_state.json", ["transitions", "history"],
        lambda e: json.dumps(e, ensure_ascii=False, sort_keys=True), newer) + f"] top-take-s{newer} (s2={t2} s3={t3})")
    for line in log:
        print(line)
    leftover = subprocess.run(["git", "ls-files", "-u"], capture_output=True, text=True).stdout.strip()
    print("leftover-UU:", leftover or "NONE")
    return 0 if not leftover else 2


if __name__ == "__main__":
    sys.exit(main())
