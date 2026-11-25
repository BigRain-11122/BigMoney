"""Data audit: find the defects that silently poison every backtest.

Why this is real work, not filler
---------------------------------
Every conclusion on this line assumes the bars are what they claim to be. A
duplicated row, a zero price, an OHLC order violation, an unadjusted split, or a
symbol that stops updating will not raise an error anywhere -- it will just make
a backtest quietly wrong. Auditing 5,221 A-share files and 1,725 ETF files by
hand is impossible, and it is exactly the kind of CPU-bound work that should run
continuously in shards.

Checks per file (all cheap, all mechanical):
  rows        >= min_rows
  dates       strictly increasing, no duplicates
  ohlc        high >= max(open, close), low <= min(open, close), high >= low
  prices      close > 0, volume >= 0
  jumps       single-day |return| > 35% (split/unadjusted signal, reported not fixed)
  tail        last bar date (staleness)

Output per shard: a JSON with per-file verdicts plus a defect census, and a
one-line summary. A shard is a unit of work the CPU-fill agent can claim.
"""
import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "results", "audit")
TZ = timezone(timedelta(hours=8))

LANES = {
    "astock": os.path.join(ROOT, "data", "astock_daily", "per"),
    "etf": os.path.join(ROOT, "data", "daily"),
    "cb": os.path.join(ROOT, "data", "cb_daily"),
    "futures": os.path.join(ROOT, "data", "futures_daily"),
    "index": os.path.join(ROOT, "data", "index_daily"),
    "moneyflow": os.path.join(ROOT, "data", "moneyflow"),
    "repo": os.path.join(ROOT, "data", "repo_daily"),
}
JUMP = 0.35
MIN_ROWS = {"astock": 200, "etf": 200, "cb": 100, "futures": 300, "index": 300,
            "moneyflow": 100, "repo": 300}


def now():
    return datetime.now(TZ)


def audit_file(path, min_rows, has_volume=True):
    """Return (verdict_dict, defects_list)."""
    defects = []
    rows = 0
    prev = None
    dup = 0
    ohlc_bad = 0
    px_bad = 0
    jumps = []
    last = None
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            header = f.readline().strip().split(",")
            idx = {k: i for i, k in enumerate(header)}
            di = idx.get("date", 0)
            ci = idx.get("close")
            oi = idx.get("open")
            hi = idx.get("high")
            li = idx.get("low")
            vi = idx.get("volume")
            prev_close = None
            for line in f:
                if not line.strip():
                    continue
                p = line.rstrip("\n").split(",")
                if len(p) <= di:
                    continue
                d = p[di][:10]
                rows += 1
                last = d if last is None or d > last else last
                if prev is not None and d <= prev:
                    dup += 1
                prev = d
                try:
                    c = float(p[ci]) if ci is not None else None
                except (TypeError, ValueError):
                    c = None
                if c is not None:
                    if c <= 0:
                        px_bad += 1
                    if prev_close and prev_close > 0:
                        r = c / prev_close - 1.0
                        if abs(r) > JUMP:
                            jumps.append({"date": d, "ret": round(r, 4)})
                    prev_close = c
                if oi is not None and hi is not None and li is not None and c is not None:
                    try:
                        o, h, l = float(p[oi]), float(p[hi]), float(p[li])
                        if not (h >= max(o, c) and l <= min(o, c) and h >= l):
                            ohlc_bad += 1
                    except (TypeError, ValueError):
                        pass
                if has_volume and vi is not None:
                    try:
                        if float(p[vi]) < 0:
                            px_bad += 1
                    except (TypeError, ValueError):
                        pass
    except OSError as e:
        return {"state": "unreadable", "error": str(e)}, ["unreadable"]

    if rows < min_rows:
        defects.append("short")
    if dup:
        defects.append("dates_not_strictly_increasing")
    if ohlc_bad:
        defects.append("ohlc_order")
    if px_bad:
        defects.append("nonpositive_price_or_volume")
    if jumps:
        defects.append("jumps_gt_35pct")
    return {
        "rows": rows, "dups": dup, "ohlc_bad": ohlc_bad, "px_bad": px_bad,
        "jumps": len(jumps), "last": last,
        "worst_jumps": sorted(jumps, key=lambda x: -abs(x["ret"]))[:3],
    }, defects


def run(lane, start, count):
    base = LANES.get(lane)
    if not base or not os.path.isdir(base):
        print(json.dumps({"ok": False, "error": f"lane {lane} not found"}))
        return 2
    files = sorted(f for f in os.listdir(base) if f.endswith(".csv") and not f.startswith("_"))
    shard = files[start:start + count]
    min_rows = MIN_ROWS.get(lane, 100)
    bad, ok = [], 0
    census = {}
    for f in shard:
        v, defects = audit_file(os.path.join(base, f), min_rows,
                                has_volume=(lane != "index"))
        if defects:
            bad.append({"file": f, "defects": defects, **v})
            for d in defects:
                census[d] = census.get(d, 0) + 1
        else:
            ok += 1
    payload = {
        "lane": lane, "start": start, "count": len(shard),
        "files_total_in_lane": len(files),
        "audited": len(shard), "clean": ok, "flagged": len(bad),
        "defect_census": census,
        "flagged_detail": bad[:60],
        "generated": now().isoformat(timespec="seconds"),
        "next_start": start + len(shard) if start + len(shard) < len(files) else None,
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, f"{lane}-{start:05d}-{start+len(shard)-1:05d}.json")
    with open(out + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    os.replace(out + ".tmp", out)
    print(json.dumps({"ok": True, "lane": lane, "audited": len(shard), "clean": ok,
                      "flagged": len(bad), "census": census,
                      "out": os.path.relpath(out, ROOT)}, ensure_ascii=False))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", required=True, choices=sorted(LANES))
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--count", type=int, default=250)
    a = ap.parse_args()
    return run(a.lane, a.start, a.count)


if __name__ == "__main__":
    sys.exit(main())
