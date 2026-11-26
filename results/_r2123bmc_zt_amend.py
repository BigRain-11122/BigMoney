"""Round 2123 bm-c: rule on the suspended 2026-11-23 zt-pool day slice.

Why this exists
---------------
`scripts/update_zt_pool.py` refuses to append when the re-fetched latest
collected day no longer matches the stored slice (overlap gate, exit 3). Since
2026-11-23 it has been refusing, so the four pool faces stopped two sessions
short of the book's bar (the CEO page says so in words: "上面的数不是今天的
盘面").

The gate's own docstring names the way out: "benign-completion amendment = a
later round with evidence, not a silent accept". This is that round.

Evidence (results/_r2123bmc_zt_overlap_probe.py, 2026-11-26)
    stored 143 rows / source 146 rows for 2026-11-23
    codes only local  : []                       (nothing removed)
    codes only source : 001360 002623 600838     (three added)
    restated among the 143 shared: 2             (000700 10.0 -> 9.992372,
                                                  603706 10.139860 -> 9.981430)
    zero removals + late additions + values still moving on two names =
    the stored slice was written before the tape settled, not a restatement
    of a settled day.

What this does
--------------
Replaces only that one (day, key) slice with the source's settled rows, keeps
every other day byte-identical, and appends the ruling to
`data/zt_pool/amendments.json` so the next reader sees why a day changed.

Refuses (exit 3, no write) when the stored slice is no longer what the probe
examined -- an amendment must never quietly cover a later, different edit.
"""
import json
import os
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import update_zt_pool as uz  # noqa: E402

import akshare as ak  # noqa: E402

DAY = sys.argv[1] if len(sys.argv) > 1 else "2026-11-23"
KEY = sys.argv[2] if len(sys.argv) > 2 else "zt"
FLAT = DAY.replace("-", "")
AMENDMENTS = os.path.join(uz.PANEL_DIR, "amendments.json")

# baseline the probe saw: 143 rows, these three missing, these two restated
EXPECT_ROWS = 143
EXPECT_MISSING = ["001360", "002623", "600838"]


def main():
    fn_name, inv = uz.ENDPOINTS[KEY]
    path = os.path.join(uz.PANEL_DIR, KEY + ".parquet")
    old = pd.read_parquet(path)
    old["日期"] = old["日期"].astype(str).str.replace("-", "", regex=False)
    old_day = old[old["日期"] == FLAT]
    if len(old_day) != EXPECT_ROWS:
        print("AMEND REFUSED: stored %s rows for %s, baseline said %d -- a later edit happened"
              % (len(old_day), DAY, EXPECT_ROWS))
        return 3

    new_day, shape_ok = uz.fetch_day(getattr(ak, fn_name), FLAT, inv)
    if not shape_ok or len(new_day) == 0:
        print("AMEND REFUSED: refetch shape_ok=%s rows=%d" % (shape_ok, len(new_day)))
        return 3
    # fetch_day returns the source frame; the collector itself stamps the day
    # column and keeps 代码 as zero-padded text (R58 row-shell defence). Mirror
    # both here, otherwise the merged slice lands with a NaN day and unpadded
    # codes (r2123 first attempt: 143 rows replaced by 146 unkeyed rows).
    new_day = new_day.copy()
    new_day["日期"] = FLAT  # panel convention: flat YYYYMMDD, no dashes
    new_day["代码"] = new_day["代码"].astype(str).str.strip().str.zfill(6)
    new_day = new_day.reindex(columns=list(old.columns))

    added = sorted(set(new_day["代码"]) - set(old_day["代码"].astype(str)))
    removed = sorted(set(old_day["代码"].astype(str)) - set(new_day["代码"].astype(str)))
    if added != EXPECT_MISSING or removed:
        print("AMEND REFUSED: added=%s removed=%s, baseline said added=%s removed=[]"
              % (added, removed, EXPECT_MISSING))
        return 3

    keep = old[old["日期"] != FLAT]
    merged = pd.concat([new_day, keep], ignore_index=True)
    merged = merged.drop_duplicates(subset=["日期", "代码"], keep="first")
    merged["日期"] = merged["日期"].astype(str)
    merged = merged.sort_values(["日期", "代码"], kind="mergesort").reset_index(drop=True)

    # a slice rewrite that silently loses rows is worse than the mismatch it
    # fixes: assert the panel kept everything except the one day it replaced
    expected_rows = len(old) - len(old_day) + len(new_day)
    if len(merged) != expected_rows:
        print("AMEND REFUSED: merged %d rows, expected %d (day %d -> %d)"
              % (len(merged), expected_rows, len(old_day), len(new_day)))
        return 3

    uz.atomic_parquet_write(merged, path)

    record = {
        "day": DAY,
        "key": KEY,
        "ruling": "LATE_COMPLETION_SUPERSET",
        "why": ("stored slice was written before the tape settled: three names "
                "arrived late, two of the shared names still had unsettled "
                "涨跌幅, and nothing was removed"),
        "rows_before": int(len(old_day)),
        "rows_after": int(len(new_day)),
        "added": added,
        "removed": removed,
        "restated": ["000700", "603706"],
        "witness": "results/_r2123bmc_zt_overlap_probe.py",
        "ruled_at": uz.time.strftime("%Y-%m-%d %H:%M:%S"),
        "ruled_by": "bm-c round 2123",
    }
    ledger = []
    if os.path.exists(AMENDMENTS):
        with open(AMENDMENTS, encoding="utf-8") as fh:
            ledger = json.load(fh)
    ledger.append(record)
    tmp = AMENDMENTS + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(ledger, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, AMENDMENTS)
    print("AMENDED %s/%s %d->%d rows added=%s removed=%s restated=%s"
          % (DAY, KEY, record["rows_before"], record["rows_after"], added, removed, record["restated"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
