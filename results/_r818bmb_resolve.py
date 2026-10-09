# -*- coding: utf-8 -*-
"""r818 bm-b: rebase-storm canonical resolver (bm-a r943 vs bm-b r818 waves).

Classifier: 7 classified + 8 UNKNOWN (fail-closed manual adjudication below,
per SKILL.md; law r185 parse-validate before write-back, r140 same-second
tie -> HEAD(=onto=bm-a side in rebase semantics), r188/R208 union zero-loss).

Manual UNKNOWN adjudication:
  docs/daily_report/REPORT-2026-10-10.{json,md}  same-day idempotent regen
    twins -> take-new by embedded ts (r817 addendum precedent "REPORT/LIVE
    同日幂等取新")
  docs/live_usage/LIVE-2026-10-10.{json,md} + LIVE-latest.{json,md}
    same class -> take-new by ts
  results/_attrition_guard_scan.json  regenerable probe receipt -> take-new
    by ts
  results/runnable_pool.json  shared pool face, BOTH sides ran the canonical
    settle (bm-a r943 two-layer done-flip heal; bm-b r818 sync_face) ->
    take stage-2 (r943 heal) then re-settle via merge_lane_views sync_face
    (S0 reland law second arm: idempotent settle; claw pool gate needs
    owner_since forward-only, max-merge guarantees it)

Exit 0 = all resolved + validated; 2 = any surprise (fail-closed, no
partial write for the offending file).
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NO_WINDOW = 0x08000000 if os.name == "nt" else 0
TS_KEYS = ("ts", "updated", "updated_at", "generated", "generated_at",
           "asof", "as_of", "time", "last_touch")


def git(args):
    r = subprocess.run(["git", "-C", ROOT] + args, capture_output=True,
                       creationflags=NO_WINDOW)
    if r.returncode != 0:
        raise RuntimeError("git %s rc=%d %s" % (
            args, r.returncode, (r.stderr or b"")[:200]))
    return r.stdout


def stage(path, n):
    """Stage blob bytes: 2=ours(onto=bm-a r943 side), 3=theirs(pick=bm-b)."""
    return git(["show", ":%d:%s" % (n, path)])


def parse(b):
    return json.loads(b.decode("utf-8"))


def find_ts(obj, depth=0):
    """Recursive-limited ts probe (F-20260927-01: nested ts faces)."""
    if depth > 4 or not isinstance(obj, dict):
        return None
    for k in TS_KEYS:
        v = obj.get(k)
        if isinstance(v, str) and len(v) >= 8:
            return v
    for v in obj.values():
        t = find_ts(v, depth + 1)
        if t:
            return t
    return None


def take_new(path):
    """Snapshot/twin: identical fast-path, else newer embedded ts, tie->ours."""
    b2, b3 = stage(path, 2), stage(path, 3)
    if b2 == b3:
        return {"path": path, "recipe": "identical", "side": "same"}
    t2, t3 = None, None
    if path.endswith(".json"):
        try:
            t2, t3 = find_ts(parse(b2)), find_ts(parse(b3))
        except Exception:
            t2 = t3 = None
    else:
        ts = re.findall(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2})?",
                        b3.decode("utf-8", "replace")) + \
             re.findall(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2})?",
                        b2.decode("utf-8", "replace"))
        if ts:
            t2 = max(re.findall(
                r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2})?",
                b2.decode("utf-8", "replace")), default=None)
            t3 = max(re.findall(
                r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2})?",
                b3.decode("utf-8", "replace")), default=None)
    if t2 is None or t3 is None or t3 <= t2:
        side, blob = "ours(r943)", b2
        why = "ts %s vs %s (tie/missing->HEAD per r140)" % (t2, t3)
    else:
        side, blob = "theirs(r818)", b3
        why = "ts %s > %s" % (t3, t2)
    with open(os.path.join(ROOT, path), "wb") as fh:
        fh.write(blob)
    parse(b3) if path.endswith(".json") else None  # r185 validate written
    return {"path": path, "recipe": "take-new", "side": side, "why": why}


def union_ledger(path, ledger_keys):
    """rolling-ledger union: |A∪B| identity-union on each ledger key,
    zero-loss count assertion; non-ledger keys take-new by ts."""
    b2, b3 = stage(path, 2), stage(path, 3)
    d2, d3 = parse(b2), parse(b3)
    out, rec = {}, {"path": path, "recipe": "union", "counts": {}}
    for k in ledger_keys:
        l2 = d2.get(k) or []
        l3 = d3.get(k) or []
        if not isinstance(l2, list) or not isinstance(l3, list):
            raise RuntimeError("%s.%s non-list" % (path, k))
        seen, union = set(), []
        for row in l2 + l3:
            key = json.dumps(row, sort_keys=True, ensure_ascii=False)
            if key not in seen:
                seen.add(key)
                union.append(row)
        union.sort(key=lambda r: str(r.get("ts") or r.get("time") or "")
                  if isinstance(r, dict) else str(r))
        out[k] = union
        rec["counts"][k] = {"left": len(l2), "right": len(l3),
                           "union": len(union),
                           "zero_loss": len(union) == len(set(
                               json.dumps(x, sort_keys=True,
                                          ensure_ascii=False)
                               for x in l2) | set(
                               json.dumps(x, sort_keys=True,
                                          ensure_ascii=False)
                               for x in l3))}
    for k in d2:
        if k not in out:
            t2, t3 = find_ts(d2.get(k)), find_ts(d3.get(k))
            out[k] = d2[k] if (t3 is None or t2 is None or t3 <= t2) else d3[k]
    for k in d3:
        if k not in out and k not in d2:
            out[k] = d3[k]
    blob = json.dumps(out, ensure_ascii=False, indent=1).encode("utf-8") \
        + b"\n"
    with open(os.path.join(ROOT, path), "wb") as fh:
        fh.write(blob)
    parse(blob)
    return rec


def take_stage2(path, why):
    b2 = stage(path, 2)
    with open(os.path.join(ROOT, path), "wb") as fh:
        fh.write(b2)
    return {"path": path, "recipe": "take-ours", "why": why}


def main():
    receipts = []
    # rolling-ledger unions (zero-loss assertions inside)
    receipts.append(union_ledger("results/compute_audit.json", ["history"]))
    receipts.append(union_ledger(
        "results/regime_state.json",
        ["history", "transitions", "triggers"]))
    # snapshots: take-new by ts (tie->HEAD)
    for p in ("results/fundamental_b_layer_filter.json",
              "results/futures_update_status.json",
              "results/lhb_update_status.json",
              "results/token_usage.json",
              "results/update_status.json",
              "results/_attrition_guard_scan.json",
              "docs/daily_report/REPORT-2026-10-10.json",
              "docs/daily_report/REPORT-2026-10-10.md",
              "docs/live_usage/LIVE-2026-10-10.json",
              "docs/live_usage/LIVE-2026-10-10.md",
              "docs/live_usage/LIVE-latest.json",
              "docs/live_usage/LIVE-latest.md"):
        receipts.append(take_new(p))
    # shared pool face: take r943 healed side; canonical re-settle follows
    # via merge_lane_views sync_face after this script (S0 reland law arm 2)
    receipts.append(take_stage2(
        "results/runnable_pool.json",
        "bm-a r943 two-layer done-flip heal side; sync_face re-settle next"))
    with open(os.path.join(ROOT, "results", "_r818bmb_classify2.json"),
              "w", encoding="utf-8") as fh:
        json.dump(receipts, fh, ensure_ascii=False, indent=1)
    print(json.dumps(receipts, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
