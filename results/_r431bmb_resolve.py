# -*- coding: utf-8 -*-
"""_r431bmb_resolve.py -- r431 bm-b rebase conflict resolver (vs bm-c r224 + bm-a r435 same-window pushes).

Skill-driven per bigmoney-conflict-resolve SKILL.md: 16 classifier-matched files
+ 4 manual-classified UNKNOWN (docs/live_usage/* = ceo_live_usage same-day
idempotent regen face, r428 push-storm precedent manual-classified snapshot,
.md/.json twins MUST take the SAME side).

Recipes:
- rolling-ledger (compute_audit.json: history; regime_state.json: transitions):
  union zero-loss (line count = |A u B|), state fields take-new by deep-ts probe.
- snapshot (14 files): take-new by hardened deep-ts probe on STAGED blobs
  (:2: = upstream/origin side, :3: = our replayed side); probe laws r100/R350:
  key normalized (strip '_','-' before asof/updated/generated/ts prefix match),
  value must be ts-shaped ^20\\d{2}- with time-of-day for wall-clock compare,
  no key-EXCLUDE lists; tie -> HEAD (upstream, r140).
- js-wrapper (dashboard_status.js): take-side whole bytes == .json twin side.
- twins (daily_report x2, live_usage x4, paper_export x2): same side both files.
"""
import json
import re
import subprocess
import sys

TS_SHAPE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")


def blob(stage, path):
    return subprocess.run(["git", "show", f":{stage}:{path}"],
                          capture_output=True).stdout.decode("utf-8", errors="replace")


def deep_ts(d, path="$"):
    """Hardened deep-ts probe (r100/R350): normalized key prefix + ts-shaped
    value WITH time-of-day; no exclusion lists; recursive."""
    best = None
    if isinstance(d, dict):
        for k, v in d.items():
            nk = str(k).replace("_", "").replace("-", "").lower()
            if isinstance(v, str) and TS_SHAPE.match(v) and any(
                    nk.startswith(p) for p in ("asof", "updated", "generated", "ts", "clock", "time")):
                if best is None or v > best[0]:
                    best = (v, f"{path}.{k}")
            sub = deep_ts(v, f"{path}.{k}")
            if sub and (best is None or sub[0] > best[0]):
                best = sub
    elif isinstance(d, list):
        for i, v in enumerate(d):
            sub = deep_ts(v, f"{path}[{i}]")
            if sub and (best is None or sub[0] > best[0]):
                best = sub
    return best


def take_new(path, log):
    a, b = blob(2, path), blob(3, path)
    try:
        da, db = json.loads(a), json.loads(b)
    except json.JSONDecodeError:
        # non-JSON (md/js): fall back to raw-embedded ts scan
        ta = max(TS_SHAPE.findall(a) or ["0"])
        tb = max(TS_SHAPE.findall(b) or ["0"])
        side = 2 if ta >= tb else 3
        log.append(f"{path}: raw-ts probe ours2={ta} theirs3={tb} -> take :{side}:")
        return blob(side, path), side
    pa, pb = deep_ts(da), deep_ts(db)
    if pa is None or pb is None:
        side = 2 if pa is None else (3 if pb is not None else 2)
        log.append(f"{path}: probe one-sided ({pa} vs {pb}) -> take :{side}:")
        return (a if side == 2 else b), side
    side = 2 if pa[0] >= pb[0] else 3  # tie -> HEAD/upstream (:2:), r140
    log.append(f"{path}: ts probe :2:={pa[0]}@{pa[1]} :3:={pb[0]}@{pb[1]} -> take :{side}:")
    return (a if side == 2 else b), side


def union_ledger(path, ledger_key, id_fn, log):
    da, db = json.loads(blob(2, path)), json.loads(blob(3, path))
    la, lb = da.get(ledger_key, []), db.get(ledger_key, [])
    seen, union = set(), []
    for row in la + lb:
        kid = id_fn(row)
        if kid in seen:
            continue
        seen.add(kid)
        union.append(row)
    # newest-last ordering by embedded ts (probe per-row; missing ts keeps order)
    def row_ts(r):
        p = deep_ts(r)
        return p[0] if p else "0"
    union.sort(key=row_ts)
    # state fields: take-new side by top-level probe
    pa, pb = deep_ts(da), deep_ts(db)
    base = da if (pa and (pb is None or pa[0] >= pb[0])) else db
    out = dict(base)
    out[ledger_key] = union
    log.append(f"{path}: {ledger_key} union |{len(la)}|+|{len(lb)}| -> |{len(union)}| zero-loss, base-side "
               f"{':2:' if base is da else ':3:'} (ts {pa[0] if pa else None} vs {pb[0] if pb else None})")
    return json.dumps(out, ensure_ascii=False, indent=1) + "\n", (2 if base is da else 3)


def main():
    log = []
    written = {}

    # ---- rolling-ledgers: union zero-loss ----
    ca, side = union_ledger("results/compute_audit.json", "history",
                            lambda r: json.dumps(r, sort_keys=True, ensure_ascii=False), log)
    written["results/compute_audit.json"] = ca
    rs, side = union_ledger("results/regime_state.json", "transitions",
                            lambda r: json.dumps(r, sort_keys=True, ensure_ascii=False), log)
    written["results/regime_state.json"] = rs

    # ---- plain snapshots: take-new deep-ts probe ----
    snaps = [
        "results/daily_scorecard.json", "results/dashboard_status.json",
        "results/fundamental_b_layer_filter.json", "results/futures_update_status.json",
        "results/lhb_update_status.json", "results/scorecard_v1.json",
        "results/strategy_scorecard.json", "results/token_usage.json",
        "results/update_status.json",
    ]
    twin_side = {}
    for p in snaps:
        txt, side = take_new(p, log)
        written[p] = txt
        twin_side[p] = side

    # ---- paper_export twins: same side both ----
    pe_side = None
    for p in ("results/paper_export/latest.json", "results/paper_export/export-2026-09-28.json"):
        txt, side = take_new(p, log)
        if pe_side is None:
            pe_side = side
        elif side != pe_side:
            log.append(f"!! {p}: twin side mismatch {side} vs {pe_side} -> forcing common {pe_side} (twins law)")
            txt, side = blob(pe_side, p), pe_side
        written[p] = txt

    # ---- daily_report twins (.md + .json same side) ----
    dr_side = None
    for p in ("docs/daily_report/REPORT-2026-09-29.json", "docs/daily_report/REPORT-2026-09-29.md"):
        txt, side = take_new(p, log)
        if dr_side is None:
            dr_side = side
        elif side != dr_side:
            log.append(f"!! {p}: twin side mismatch {side} vs {dr_side} -> forcing common {dr_side} (twins law)")
            txt, side = blob(dr_side, p), dr_side
        written[p] = txt

    # ---- live_usage twins x2 pairs (manual-classified snapshot, same side all four) ----
    lu_side = None
    for p in ("docs/live_usage/LIVE-2026-09-29.json", "docs/live_usage/LIVE-2026-09-29.md",
              "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"):
        txt, side = take_new(p, log)
        if lu_side is None:
            lu_side = side
        elif side != lu_side:
            log.append(f"!! {p}: live_usage twin side mismatch {side} vs {lu_side} -> forcing {lu_side} (twins law)")
            txt, side = blob(lu_side, p), lu_side
        written[p] = txt

    # ---- js-wrapper: take-side whole bytes == .json twin side ----
    js_side = twin_side.get("results/dashboard_status.json")
    written["results/dashboard_status.js"] = blob(js_side, "results/dashboard_status.js")
    log.append(f"results/dashboard_status.js: js-wrapper take-side whole bytes = .json twin side :{js_side}: (R209)")

    # ---- validation before write-back (r185) ----
    for p, txt in written.items():
        if p.endswith(".json"):
            json.loads(txt)  # raise on bad json
    for p, txt in written.items():
        with open(p, "w", encoding="utf-8", newline="") as fh:
            fh.write(txt)
    for line in log:
        print(line)
    print(f"RESOLVED {len(written)} files; validation-pass; written back")
    return 0


if __name__ == "__main__":
    sys.exit(main())
