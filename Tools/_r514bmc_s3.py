# -*- coding: utf-8 -*-
"""r514 bm-c S3 scan: post_review whole-ledger unresolved-X scan + pool
census. Read-only. Bloodline: r512/r513 round reports (5697-row zero-X
derivation). CREATE_NO_WINDOW not needed (zero subprocess here)."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def post_review_scan():
    p = os.path.join(ROOT, "results", "post_review.jsonl")
    rows = []
    with open(p, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except ValueError:
                pass
    by_id = {}
    for r in rows:
        by_id.setdefault(r.get("id", "?"), []).append(r)
    unresolved = []
    for rid, rs in by_id.items():
        last = rs[-1]
        if str(last.get("verdict", "")).upper() == "NO":
            unresolved.append((rid, last.get("ts", "?")))
    verdicts = {}
    for r in rows:
        v = str(r.get("verdict", "?")).upper()
        verdicts[v] = verdicts.get(v, 0) + 1
    print("POST_REVIEW rows=%d verdicts=%s unresolved_NO=%d %s"
          % (len(rows), verdicts, len(unresolved), unresolved[:8]))
    return len(unresolved)


def pool_census():
    p = os.path.join(ROOT, "results", "runnable_pool.json")
    with open(p, encoding="utf-8-sig") as fh:
        data = json.load(fh)
    entries = data.get("entries", data) if isinstance(data, dict) else data
    if isinstance(entries, dict):
        entries = list(entries.values())
    counts = {}
    interesting = []
    for e in entries:
        st = str(e.get("status", "?"))
        counts[st] = counts.get(st, 0) + 1
        if st in ("ready", "waiting", "claimed", "running"):
            interesting.append((e.get("id", "?"), st, e.get("owner", "") or
                                e.get("claimed_by", "") or "", e.get("lane", "")))
    print("POOL total=%d counts=%s" % (len(entries), counts))
    for row in sorted(interesting):
        print("  POOL-OPEN %s" % (row,))


def main():
    x = post_review_scan()
    pool_census()
    print("S3_SCAN_DONE unresolved_NO=%d" % x)
    return 1 if x else 0


if __name__ == "__main__":
    raise SystemExit(main())
