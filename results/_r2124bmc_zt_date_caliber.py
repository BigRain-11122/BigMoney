"""r2124 bm-c: put the zt panel's 日期 column back on the collector's caliber.

r2123 amended the 2026-11-23 slice (LATE_COMPLETION_SUPERSET) and stamped the
rows with `日期=20261123` (flat).  The collector's own caliber is `%Y-%m-%d`
(update_zt_pool.py:162/169/292), the other three panels hold `2026-11-23`, the
day ledger holds ISO, and `append_day` dedupes with `old["日期"] == day` -- so a
flat stamp does not just look different, it stops matching.  This script moves
the whole column back to ISO, proves nothing else moved, and refuses on any
disagreement.

Read-only on everything except data/zt_pool/zt.parquet.
"""
import io
import json
import os
import re
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PANEL = os.path.join(ROOT, "data", "zt_pool", "zt.parquet")
OUT = os.path.join(ROOT, "results", "_r2124bmc_zt_date_caliber.json")
FLAT = re.compile(r"^\d{8}$")


def flat_to_iso(v):
    s = str(v)
    if FLAT.match(s):
        return "%s-%s-%s" % (s[0:4], s[4:6], s[6:8])
    return s


def main():
    df = pd.read_parquet(PANEL)
    col = "日期"
    if col not in df.columns:
        print("FATAL: no 日期 column")
        return 3
    before = df[col].astype(str)
    n_before = len(df)
    # compare in one key space: the flat day and its ISO spelling are the same day
    canon_before = before.map(flat_to_iso)
    counts_before = canon_before.value_counts().to_dict()

    flat_n = int(before.map(lambda v: bool(FLAT.match(v))).sum())
    dash_n = int(before.str.contains("-").sum())
    out = {"panel": "data/zt_pool/zt.parquet", "rows_before": n_before,
           "rows_flat_before": flat_n, "rows_iso_before": dash_n}

    if flat_n == 0:
        out["action"] = "NO-OP (already ISO)"
        print(json.dumps(out, ensure_ascii=False))
        with io.open(OUT, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
        return 0

    df[col] = before.map(flat_to_iso)
    after = df[col].astype(str)
    counts_after = after.value_counts().to_dict()

    problems = []
    if len(df) != n_before:
        problems.append("row count moved %d -> %d" % (n_before, len(df)))
    if counts_after != counts_before:
        only_b = {k: v for k, v in counts_before.items() if counts_after.get(k) != v}
        only_a = {k: v for k, v in counts_after.items() if counts_before.get(k) != v}
        problems.append("per-day counts moved: before-only=%s after-only=%s"
                        % (list(only_b.items())[:4], list(only_a.items())[:4]))
    if int(after.str.contains("-").sum()) != n_before:
        problems.append("not every row is ISO after the repair")
    day = "2026-11-23"
    n_day = int((after == day).sum())
    if n_day != 146:
        problems.append("the amended day holds %d rows, the amendment ruled 146" % n_day)

    out.update({"rows_iso_after": int(after.str.contains('-').sum()),
                "day_2026_11_23_rows": n_day,
                "distinct_days": len(counts_after),
                "last_day": sorted(counts_after)[-1],
                "problems": problems})

    if problems:
        out["action"] = "REFUSED"
        print(json.dumps(out, ensure_ascii=False))
        with io.open(OUT, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
        return 3

    df.to_parquet(PANEL, index=False)
    out["action"] = "REWROTE-CALIBER"
    with io.open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
