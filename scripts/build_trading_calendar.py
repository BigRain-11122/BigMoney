# -*- coding: utf-8 -*-
"""build_trading_calendar.py -- real exchange trading-day calendar artifact.

D-M1_FUNDING_SEASON_P1 gate-4 pure-data piece (group prereg D-20260930-30
sec.2/sec.8-4; mechanism slate D-20260930-29 M1, CEO order 2026-09-30).
Replaces the month-approximation in strategies/seasonal.py holiday_effect
({1,2,10,11}) with the REAL exchange trading-day set, derived from local
bar/rate sources only (zero network, deterministic, byte-idempotent).

Canon: UNION of curated in-repo sources. A bar/rate row cannot exist on a
day the exchange was closed, so union membership = exchange-open evidence;
per-source presence flags carry corroboration, consumers may filter.
Weekend rows are impossible on real fabrics -> hard corruption gate.

Sources (frozen list, all in-repo, all exchange fabrics):
  etf50    data/daily/sh510050.csv   (2005-02->, deepest ETF backbone)
  etf300   data/daily/sh510300.csv   (2012-05->)
  etf500   data/daily/sh510500.csv
  sz159915 data/daily/sz159915.csv
  etf512100 data/daily/sh512100.csv
  etf588000 data/daily/sh588000.csv  (2019-11->)
  repo001  data/repo_daily/GC001.csv (2011-05->)
  repo007  data/repo_daily/GC007.csv (2011-05->)

Output:
  data/trading_calendar.csv -- one row per canonical trading day:
    date,weekday,n_src,src_etf50,src_etf300,src_etf500,src_sz159915,
    src_etf512100,src_etf588000,src_repo001,src_repo007,
    is_month_end,is_quarter_end,is_year_end
  (month/quarter/year-end = last canonical trading day within that
   calendar period -- pure calendar facts, batch window logic stays in
   the consumer)
  results/trading_calendar_verify.json -- per-source stats, backbone
  agreement/gap disclosure, flag counts, csv sha256. No wall clock:
  rerun on same data = byte-identical outputs.

Exit codes: run 0=ok / 2=mechanism failure (missing source, bad row,
weekend corruption). selftest 0=pass / 1=fail (hermetic, tmp sandbox).
"""

import argparse
import csv
import hashlib
import io
import json
import os
import re
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAL_PATH = os.path.join(ROOT, "data", "trading_calendar.csv")
VERIFY_PATH = os.path.join(ROOT, "results", "trading_calendar_verify.json")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
BACKBONE = "etf50"

SOURCES = [
    ("etf50", os.path.join(ROOT, "data", "daily", "sh510050.csv")),
    ("etf300", os.path.join(ROOT, "data", "daily", "sh510300.csv")),
    ("etf500", os.path.join(ROOT, "data", "daily", "sh510500.csv")),
    ("sz159915", os.path.join(ROOT, "data", "daily", "sz159915.csv")),
    ("etf512100", os.path.join(ROOT, "data", "daily", "sh512100.csv")),
    ("etf588000", os.path.join(ROOT, "data", "daily", "sh588000.csv")),
    ("repo001", os.path.join(ROOT, "data", "repo_daily", "GC001.csv")),
    ("repo007", os.path.join(ROOT, "data", "repo_daily", "GC007.csv")),
]

CSV_HEADER = [
    "date", "weekday", "n_src",
    "src_etf50", "src_etf300", "src_etf500", "src_sz159915",
    "src_etf512100", "src_etf588000", "src_repo001", "src_repo007",
    "is_month_end", "is_quarter_end", "is_year_end",
]


class CalendarError(Exception):
    """Honest failure: missing source / bad row / weekend corruption."""


def _valid_date(s):
    import datetime
    if not DATE_RE.match(s):
        return False
    try:
        datetime.date.fromisoformat(s)
        return True
    except ValueError:
        return False


def read_dates(path):
    """Sorted unique ^YYYY-MM-DD$ values from the 'date' column."""
    if not os.path.exists(path):
        raise CalendarError("source missing: %s" % path)
    out = set()
    with io.open(path, "r", encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            d = str(row.get("date") or "").strip()
            if not d:
                continue
            if not _valid_date(d):
                raise CalendarError("bad date row %r in %s" % (d, path))
            out.add(d)
    if not out:
        raise CalendarError("zero dates parsed from %s" % path)
    return sorted(out)


def derive(sources):
    """Core derivation. sources: list of (key, sorted_dates). Returns rows.

    Weekend gate: exchange fabrics never trade Sat/Sun; any weekend date is
    corruption -> CalendarError (hard gate, no silent skip).
    """
    import datetime
    keys = [k for k, _ in sources]
    if len(set(keys)) != len(keys):
        raise CalendarError("duplicate source keys")
    union = sorted(set().union(*[set(ds) for _, ds in sources]))
    for d in union:
        if datetime.date.fromisoformat(d).weekday() >= 5:
            raise CalendarError("weekend trading date %r = corruption" % d)
    rows = []
    for d in union:
        dt = datetime.date.fromisoformat(d)
        flags = {k: (1 if d in set(ds) else 0) for k, ds in sources}
        rows.append({
            "date": d,
            "weekday": dt.weekday() + 1,
            "n_src": sum(flags.values()),
            **{"src_%s" % k: flags[k] for k in keys},
        })
    # period-end flags: last canonical day within month/quarter/year
    for scope in ("month", "quarter", "year"):
        col = "is_%s_end" % scope
        groups = {}
        for r in rows:
            y, m = int(r["date"][:4]), int(r["date"][5:7])
            if scope == "month":
                g = (y, m)
            elif scope == "quarter":
                g = (y, (m - 1) // 3)
            else:
                g = y
            groups.setdefault(g, []).append(r)
        for g, rs in groups.items():
            for r in rs:
                r[col] = 0
            rs[-1][col] = 1
    for r in rows:
        for c in CSV_HEADER:
            r.setdefault(c, 0)
    return rows


def rows_to_csv_bytes(rows):
    buf = io.StringIO()
    buf.write(",".join(CSV_HEADER) + "\r\n")
    for r in rows:
        buf.write(",".join(str(r[c]) for c in CSV_HEADER) + "\r\n")
    return buf.getvalue().encode("utf-8")


def _atomic_write(path, data):
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    fd, tmp = tempfile.mkstemp(dir=d or ".", prefix=".tmp_cal_")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def verify_payload(sources, rows, csv_bytes, backbone=BACKBONE):
    per = {}
    for k, ds in sources:
        per[k] = {"n_days": len(ds), "first": ds[0], "last": ds[-1]}
    bb = dict(sources)[backbone]
    bb_set = set(bb)
    agreement = {}
    for k, ds in sources:
        if k == backbone:
            continue
        ds_set = set(ds)
        # days backbone has within source span but source lacks (source gap)
        gap = sorted(d for d in bb_set
                      if ds[0] <= d <= ds[-1] and d not in ds_set)
        # days source has within backbone span but backbone lacks (backbone gap candidates)
        extra = sorted(d for d in ds_set
                       if bb[0] <= d <= bb[-1] and d not in bb_set)
        agreement[k] = {
            "missing_vs_backbone_in_overlap": len(gap),
            "missing_head": gap[:5],
            "extra_vs_backbone_in_overlap": len(extra),
            "extra_head": extra[:5],
        }
    def count(col):
        return sum(1 for r in rows if r.get(col) == 1)
    return {
        "batch": "TRADING_CALENDAR_P1",
        "piece": "D-M1_FUNDING_SEASON_P1 gate-4 real trading calendar",
        "sources": [k for k, _ in sources],
        "n_union_days": len(rows),
        "first": rows[0]["date"] if rows else None,
        "last": rows[-1]["date"] if rows else None,
        "per_source": per,
        "backbone_agreement": agreement,
        "n_month_end": count("is_month_end"),
        "n_quarter_end": count("is_quarter_end"),
        "n_year_end": count("is_year_end"),
        "weekend_rows": 0,
        "csv_sha256": hashlib.sha256(csv_bytes).hexdigest(),
        "csv_bytes": len(csv_bytes),
    }


def run(paths=None):
    src_paths = paths or SOURCES
    sources = [(k, read_dates(p)) for k, p in src_paths]
    rows = derive(sources)
    csv_bytes = rows_to_csv_bytes(rows)
    _atomic_write(CAL_PATH, csv_bytes)
    vp = verify_payload(sources, rows, csv_bytes)
    _atomic_write(VERIFY_PATH,
                  (json.dumps(vp, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    print("trading_calendar: %d days %s..%s | month_end=%d quarter_end=%d "
          "year_end=%d | csv_sha16=%s" % (
              vp["n_union_days"], vp["first"], vp["last"],
              vp["n_month_end"], vp["n_quarter_end"], vp["n_year_end"],
              vp["csv_sha256"][:16]))
    return 0


def selftest():
    """Hermetic offline selftest (tmp sandbox, zero real-data reads)."""
    import datetime
    ok = []

    def check(name, cond):
        ok.append((name, bool(cond)))

    with tempfile.TemporaryDirectory() as td:
        # fixtures: two sources with an overlap gap + a third disjoint-era source
        a = ["2024-01-31", "2024-02-01", "2024-02-02", "2024-02-05",
             "2024-02-06", "2024-02-07", "2024-02-08", "2024-02-09",
             "2024-03-29", "2024-12-31", "2025-01-02", "2025-03-31"]
        # 2024-02-03/04 = Sat/Sun correctly absent; b lacks 02-02 (gap) but has 02-26
        b = ["2024-01-31", "2024-02-01", "2024-02-05", "2024-02-06",
             "2024-02-07", "2024-02-08", "2024-02-09", "2024-02-26",
             "2024-03-29", "2024-12-31"]
        c = ["2023-06-30", "2023-07-03"]  # pre-backbone era (union-only era)
        srcs = [("a", a), ("b", b), ("c", c)]
        rows = derive(srcs)
        dates = [r["date"] for r in rows]
        check("union-sorted", dates == sorted(set(a) | set(b) | set(c)))
        check("union-count", len(dates) == len(set(a) | set(b) | set(c)))
        by = {r["date"]: r for r in rows}
        check("weekend-zero", all(datetime.date.fromisoformat(d).weekday() < 5
                                  for d in dates))
        check("weekday-map", by["2024-02-05"]["weekday"] == 1)  # Monday
        check("nsrc-union-day", by["2024-01-31"]["n_src"] == 2)  # in a+b, not c-era
        check("nsrc-single-source-day", by["2024-02-26"]["n_src"] == 1)
        check("gap-day-kept-with-flag", by["2024-02-02"]["src_a"] == 1
              and by["2024-02-02"]["src_b"] == 0)
        check("month-end-202402", by["2024-02-26"]["is_month_end"] == 1)
        check("month-end-not-mid", by["2024-02-09"]["is_month_end"] == 0)
        check("quarter-end-202403", by["2024-03-29"]["is_quarter_end"] == 1)
        check("year-end-20241231", by["2024-12-31"]["is_year_end"] == 1
              and by["2024-12-31"]["is_quarter_end"] == 1
              and by["2024-12-31"]["is_month_end"] == 1)
        check("year-end-not-20250102", by["2025-01-02"]["is_year_end"] == 0)
        check("era-c-included", "2023-06-30" in dates)
        # corruption gate: weekend date must hard-fail
        try:
            derive([("x", ["2024-02-03"])])  # Saturday
            check("weekend-gate", False)
        except CalendarError:
            check("weekend-gate", True)
        # idempotency: derive twice -> byte-identical
        check("idempotent-bytes",
              rows_to_csv_bytes(derive(srcs)) == rows_to_csv_bytes(derive(srcs)))
        # verify payload shape
        vp = verify_payload(srcs, derive(srcs), rows_to_csv_bytes(derive(srcs)),
                            backbone="a")
        for k in ("n_union_days", "per_source", "backbone_agreement",
                  "csv_sha256", "n_month_end", "n_quarter_end", "n_year_end"):
            check("verify-key-%s" % k, k in vp)
        check("verify-gap-counted",
              vp["backbone_agreement"]["b"]["missing_vs_backbone_in_overlap"] == 1)
        check("verify-extra-counted",
              vp["backbone_agreement"]["b"]["extra_vs_backbone_in_overlap"] == 1)
        # missing source honesty
        try:
            run(paths=[("a", os.path.join(td, "nope.csv"))])
            check("missing-source-fails", False)
        except CalendarError:
            check("missing-source-fails", True)
    n_pass = sum(1 for _, v in ok if v)
    for name, v in ok:
        if not v:
            print("FAIL: %s" % name)
    print("selftest: %d/%d PASS" % (n_pass, len(ok)))
    return 0 if n_pass == len(ok) else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("mode", choices=["run", "selftest"])
    args = ap.parse_args()
    try:
        if args.mode == "run":
            return run()
        return selftest()
    except CalendarError as e:
        print("trading_calendar: FAIL %s" % e)
        return 2


if __name__ == "__main__":
    sys.exit(main())
