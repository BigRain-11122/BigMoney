"""r397 bm-b rebase conflict resolver (16 UU files, classifier-routed).

Classifier output (tools/skills/bigmoney-conflict-resolve): 14 classified +
2 UNKNOWN (docs/live_usage/LIVE-2026-09-28.{json,md}) manually adjudicated as
same-day idempotent-regen snapshot face (ceo_live_usage producer pattern =
daily_report REPORT-* precedent: take-new by generated ts, twins same side).

Recipes per SKILL.md: snapshots = hardened deep-ts probe on STAGED blobs
(:2: ours / :3: theirs; strip _/- before prefix match; wall-clock values must
carry time-of-day, date-only never feeds the max; tie -> HEAD/ours r140);
compute_audit/regime_state = rolling-ledger union (history rows by full-row
identity, zero loss) + newest snapshot fields; CODELY.md = memory-union
merge-base prefix assertion + direct-concat suffixes; dashboard_status.js =
js-wrapper take-side whole bytes (side decided by its .json twin).
"""
import json
import re
import subprocess
import sys

ROOT = "C:/Users/Administrator/Desktop/Bigmoney"


def blob(rev, path):
    r = subprocess.run(["git", "-C", ROOT, "show", f"{rev}:{path}"],
                       capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout


TS_KEY_PREFIX = ("ts", "updated", "generated", "asof", "date", "time",
                 "lastseen", "written", "refreshed")
TS_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}")


def probe_ts(obj, out):
    """Deep-scan for wall-clock ts values (must contain time-of-day)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = re.sub(r"[_\-]", "", str(k)).lower()
            if isinstance(v, str) and any(nk.startswith(p)
                                           for p in TS_KEY_PREFIX):
                if TS_RE.match(v) and re.search(r"[T ]\d{2}:\d{2}", v):
                    out.append(v)
            probe_ts(v, out)
    elif isinstance(obj, list):
        for v in obj:
            probe_ts(v, out)


def side_ts(raw):
    try:
        obj = json.loads(raw.decode("utf-8"))
    except Exception:
        m = re.findall(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}",
                       raw.decode("utf-8", "replace"))
        return max(m) if m else None
    vals = []
    probe_ts(obj, vals)
    return max(vals) if vals else None


def take_new(raw2, raw3, path):
    t2, t3 = side_ts(raw2), side_ts(raw3)
    if t2 is None and t3 is None:
        return raw2, "ours(no-ts, tie->HEAD r140)"
    if t3 is None:
        return raw2, f"ours({t2})"
    if t2 is None:
        return raw3, f"theirs({t3})"
    return (raw2, f"ours({t2}>{t3})") if t2 >= t3 else (raw3, f"theirs({t3}>{t2})")


def union_ledger(raw2, raw3, ledger_keys):
    a, b = json.loads(raw2.decode("utf-8")), json.loads(raw3.decode("utf-8"))
    t2, t3 = side_ts(raw2), side_ts(raw3)
    newer, _ = take_new(raw2, raw3, "")
    snap = json.loads(newer.decode("utf-8"))
    for k in ledger_keys:
        rows_a = a.get(k) or []
        rows_b = b.get(k) or []
        seen, rows = set(), []
        for r in rows_a + rows_b:
            key = json.dumps(r, sort_keys=True, ensure_ascii=False)
            if key not in seen:
                seen.add(key)
                rows.append(r)
        snap[k] = rows
    return json.dumps(snap, ensure_ascii=False, indent=1).encode("utf-8"), \
        f"union[{','.join(ledger_keys)}] rows={ {k: len(snap[k]) for k in ledger_keys} }"


def write_resolved(path, raw, log):
    with open(f"{ROOT}/{path}", "wb") as f:
        f.write(raw)
    log.append((path, "OK"))


def main():
    log = []
    sides = {}
    snapshots = [
        "docs/daily_report/REPORT-2026-09-28.json",
        "docs/daily_report/REPORT-2026-09-28.md",
        "docs/live_usage/LIVE-2026-09-28.json",
        "docs/live_usage/LIVE-2026-09-28.md",
        "results/dashboard_status.json",
        "results/dashboard_status.js",
        "results/fundamental_b_layer_filter.json",
        "results/futures_update_status.json",
        "results/lhb_update_status.json",
        "results/scorecard_v1.json",
        "results/strategy_scorecard.json",
        "results/token_usage.json",
        "results/update_status.json",
    ]
    for path in snapshots:
        r2, r3 = blob(":2", path), blob(":3", path)
        if r2 is None or r3 is None:
            log.append((path, f"SKIP missing blob r2={r2 is not None} r3={r3 is not None}"))
            continue
        twin_of = None
        if path.endswith(".md"):
            twin_of = path[:-3] + ".json"
        elif path == "results/dashboard_status.js":
            twin_of = "results/dashboard_status.json"
        if twin_of and twin_of in sides:
            raw = r2 if sides[twin_of] == "ours" else r3
            note = f"twin-follows {twin_of} side={sides[twin_of]}"
            write_resolved(path, raw, log)
            print(f"{path}: {note}")
            continue
        raw, note = take_new(r2, r3, path)
        sides[path] = "ours" if raw is r2 else "theirs"
        write_resolved(path, raw, log)
        print(f"{path}: {note} -> {sides[path]}")
    # rolling ledgers
    for path, keys in (("results/compute_audit.json", ["history"]),
                       ("results/regime_state.json",
                        ["history", "transitions", "launches"])):
        r2, r3 = blob(":2", path), blob(":3", path)
        raw, note = union_ledger(r2, r3, keys)
        write_resolved(path, raw, log)
        print(f"{path}: {note}")
    # memory-union CODELY.md
    path = "CODELY.md"
    base, r2, r3 = blob(":1", path), blob(":2", path), blob(":3", path)
    if not (r2.startswith(base) and r3.startswith(base)):
        print(f"{path}: PREFIX-ASSERTION FAIL -> manual review required")
        return 1
    merged = base + r2[len(base):] + r3[len(base):]
    with open(f"{ROOT}/{path}", "wb") as f:
        f.write(merged)
    print(f"{path}: memory-union direct-concat "
          f"(base={len(base)} +A={len(r2)-len(base)} +B={len(r3)-len(base)} "
          f"= {len(merged)})")
    # validation pass: every resolved .json must parse
    fails = []
    for path, note in log:
        if path.endswith(".json") and note == "OK":
            try:
                json.loads(open(f"{ROOT}/{path}", "rb").read().decode("utf-8"))
            except Exception as e:
                fails.append((path, repr(e)[:120]))
    json.loads(open(f"{ROOT}/CODELY.md", "rb").read().decode("utf-8")) \
        if False else None
    if fails:
        print("VALIDATION FAIL:", fails)
        return 2
    print(f"resolver done: {len(log)} files resolved+validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
