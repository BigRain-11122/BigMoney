"""r451 bm-b stash-pop collision batch resolver (19 classified, 0 UNKNOWN).

Push-rejection -> rebase -> stash pop conflict: stage2 (ours) = post-rebase
HEAD = upstream bm-c r259 round S6 faces; stage3 (theirs) = stashed bm-b
r451 S6 faces. Recipes per bigmoney-conflict-resolve SKILL.md classifier:
- snapshot groups (REPORT / LIVE / DASH twins): take-new by hardened deep
  wall-clock ts probe (R350: no key-exclude lists, value-shape-only, values
  must carry time-of-day); ALL twins in one group take the SAME side, json
  probe decides; take-side raw bytes verbatim (R209 js-wrapper safe).
- snapshot singles: take-new by same hardened probe, raw bytes verbatim.
- rolling-ledgers (compute_audit / regime_state): union list faces
  (history/transitions) zero-loss dedup by in-entry ts (r319 per-face probe),
  scalar/other faces take-new by ts probe; json re-serialize indent=2.
Blob reads via `git cat-file :<stage>:<path>` bytes (no PS redirection).
Parse-verify (r185) every .json before write-back.
"""
import json
import re
import subprocess
import sys

TS_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")


def blob(stage, path):
    out = subprocess.run(["git", "cat-file", "-p", f":{stage}:{path}"],
                         capture_output=True)
    if out.returncode != 0:
        sys.exit(f"cat-file :{stage}:{path} failed: {out.stderr!r}")
    return out.stdout


def deep_ts(obj):
    """Hardened wall-clock probe: max full-timestamp-shaped value anywhere."""
    best = ""
    stack = [obj]
    while stack:
        cur = stack.pop()
        if isinstance(cur, dict):
            stack.extend(cur.values())
        elif isinstance(cur, list):
            stack.extend(cur)
        elif isinstance(cur, str) and TS_RE.match(cur):
            if cur > best:
                best = cur
    return best


def jload(stage, path):
    return json.loads(blob(stage, path).decode("utf-8"))


def resolve_snapshot(stage_pick, path):
    raw = blob(stage_pick, path)
    if path.endswith(".json"):
        json.loads(raw.decode("utf-8"))      # parse-verify (r185)
    with open(path, "wb") as fh:
        fh.write(raw)
    return stage_pick


def pick_newer(path):
    ts2, ts3 = deep_ts(jload(2, path)), deep_ts(jload(3, path))
    if ts2 == ts3:
        pick = 2            # same-second tie -> HEAD (r140 law)
    else:
        pick = 2 if ts2 > ts3 else 3
    return pick, ts2, ts3


def union_ledger(path, list_keys):
    a, b = jload(2, path), jload(3, path)
    merged = dict(a) if deep_ts(a) >= deep_ts(b) else dict(b)  # newest scalars
    for key in list_keys:
        la, lb = a.get(key), b.get(key)
        if not isinstance(la, list) or not isinstance(lb, list):
            continue
        dedup = {}
        for e in la + lb:               # probe per-face dedup key (r319)
            k = e.get("ts") if isinstance(e, dict) else None
            if k is None:
                k = json.dumps(e, sort_keys=True, ensure_ascii=False)
            dedup[k] = e                # later same-key entry wins
        merged[key] = list(dedup.values())
    txt = json.dumps(merged, ensure_ascii=False, indent=2)
    json.loads(txt)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(txt)
    return len(merged.get(list_keys[0], [])) if list_keys else 0


def main():
    log = []
    # twin groups: json probe decides, whole group same side, raw bytes
    groups = {
        "REPORT": ["docs/daily_report/REPORT-2026-09-30.json",
                   "docs/daily_report/REPORT-2026-09-30.md"],
        "LIVE": ["docs/live_usage/LIVE-2026-09-30.json",
                 "docs/live_usage/LIVE-2026-09-30.md",
                 "docs/live_usage/LIVE-latest.json",
                 "docs/live_usage/LIVE-latest.md"],
        "DASH": ["results/dashboard_status.json",
                 "results/dashboard_status.js"],
    }
    for name, members in groups.items():
        pick, ts2, ts3 = pick_newer(members[0])
        for m in members:
            resolve_snapshot(pick, m)
        log.append(f"{name}: side{pick} (s2={ts2} s3={ts3})")
    # snapshot singles
    singles = [
        "results/fundamental_b_layer_filter.json",
        "results/futures_update_status.json",
        "results/lhb_update_status.json",
        "results/prospect_paper/_summary.json",
        "results/prospect_promotion/_summary.json",
        "results/scorecard_v1.json",
        "results/strategy_scorecard.json",
        "results/token_usage.json",
        "results/update_status.json",
    ]
    for p in singles:
        pick, ts2, ts3 = pick_newer(p)
        resolve_snapshot(pick, p)
        log.append(f"{p}: side{pick} (s2={ts2} s3={ts3})")
    # rolling ledgers: union list faces, take-new scalars
    n = union_ledger("results/compute_audit.json", ["history"])
    log.append(f"compute_audit.json: history union -> {n} entries")
    n = union_ledger("results/regime_state.json", ["history", "transitions"])
    log.append(f"regime_state.json: history union -> {n} entries")
    for line in log:
        print(line)


if __name__ == "__main__":
    main()
