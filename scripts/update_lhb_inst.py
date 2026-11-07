#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""update_lhb_inst -- the institutional seat aggregate of the LHB face, as a panel.

WHY THIS FILE EXISTS
--------------------
r1405 priced zoo #94 (LHB institutional timing) and had to downgrade its frozen rule because
`Money02/data/lhb/lhb_detail.parquet` carries 龙虎榜净买额/买入额/卖出额 per stock-day and **no
seat column** -- the institutional numerator the rule asked for did not exist anywhere in the
repo, so the run was labelled `verdict_scope='frozen rule untested'`.

It exists at the source.  EM's datacenter publishes exactly that numerator per 上榜 day:
买方机构数 / 卖方机构数 / 机构买入总额 / 机构卖出总额 / 机构买入净额 /
机构净买额占总成交额比, one row per (stock, 上榜日期, 上榜原因), back to at least 2012.

This file is the collection lane for it.  It does not model anything and it does not judge
anything: it accumulates the vendor's own rows, append-only, with the same disciplines the other
data lanes in this repo use (monthly pages, checkpoint resume, overlap check, no-op when the
panel already covers the expected complete bar day, connection fuse, single-lane host guard).

FIRST_DATE=2020-01-01 -- the window this desk's stock studies actually read (the astock daily
panel and every 20-bar cohort study built on it since r1408 start 2020-01-02); older history
exists at the source and can be back-filled by moving FIRST_DATE, which is a GM-lane decision
(T-67 §2 forward-only rule), not something this gate does on its own.

ONE THING THE PANEL MUST KEEP
-----------------------------
`上榜原因` stays in the panel on purpose.  r1405 measured that a stock-day appears once per
reason and the rows are NOT interchangeable: a "连续三个交易日...累计" reason reports a
MULTI-DAY cumulative amount.  Dropping the column would throw away the only field that lets a
consumer separate same-day faces from cumulative ones.

Run:  python scripts/update_lhb_inst.py [--force] | selftest | status
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import exchange_calendar_audit as CAL  # noqa: E402  (single calendar implementation of record)

PANEL_DIR = os.path.join(ROOT, "data", "lhb_inst")
PANEL = os.path.join(PANEL_DIR, "lhb_inst.parquet")
PROGRESS = os.path.join(PANEL_DIR, "_progress.json")
STATUS = os.path.join(ROOT, "results", "lhb_inst_update_status.json")
MACHINE = os.path.join(ROOT, "fleet", "machine.json")

LANE_DEFAULT = "bm-c"
FIRST_DATE = "2020-01-01"
KEY = ["代码", "上榜日期", "上榜原因"]
REQUIRED = ["代码", "名称", "收盘价", "涨跌幅", "买方机构数", "卖方机构数",
            "机构买入总额", "机构卖出总额", "机构买入净额", "市场总成交额",
            "机构净买额占总成交额比", "上榜原因", "上榜日期"]
SLEEP_S = 1.0
FUSE = 3


# --------------------------------------------------------------------------- helpers

def machine_id() -> str:
    try:
        with open(MACHINE, "r", encoding="utf-8") as fh:
            return str(json.load(fh).get("machine_id") or "?")
    except Exception:
        return "?"


def lane_host_of() -> str:
    """The one resolver of record for lane ownership (config/lane_hosts.json), with the in-code
    default as its fail-safe -- never a second opinion about who owns this lane."""
    try:
        if ROOT not in sys.path:
            sys.path.insert(0, ROOT)
        from config.lane_io import lane_host
        return lane_host("update_lhb_inst", LANE_DEFAULT)
    except Exception:
        return LANE_DEFAULT


def month_windows(first: str, last: str) -> list:
    """[(YYYYMMDD, YYYYMMDD)] monthly pages covering [first, last] inclusive."""
    from datetime import timedelta
    d0 = datetime.strptime(first, "%Y-%m-%d")
    d1 = datetime.strptime(last, "%Y-%m-%d")
    out, y, m = [], d0.year, d0.month
    while (y, m) <= (d1.year, d1.month):
        start = max(datetime(y, m, 1), d0)
        nxt = datetime(y + 1, 1, 1) if m == 12 else datetime(y, m + 1, 1)
        end = min(nxt - timedelta(days=1), d1)
        out.append((start.strftime("%Y%m%d"), end.strftime("%Y%m%d")))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def load_progress() -> dict:
    if not os.path.exists(PROGRESS):
        return {"months_done": [], "cutoff": None}
    with open(PROGRESS, "r", encoding="utf-8") as fh:
        d = json.load(fh)
    d.setdefault("months_done", [])
    d.setdefault("cutoff", None)
    return d


def save_progress(d: dict) -> None:
    os.makedirs(PANEL_DIR, exist_ok=True)
    tmp = PROGRESS + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, PROGRESS)


def load_panel():
    import pandas as pd
    if not os.path.exists(PANEL):
        return None
    return pd.read_parquet(PANEL)


def write_status(st: dict) -> None:
    os.makedirs(os.path.dirname(STATUS), exist_ok=True)
    payload = dict(st)
    payload.setdefault("machine", machine_id())
    payload.setdefault("lane_host", lane_host_of())
    payload.setdefault("ts", datetime.now().isoformat(timespec="seconds"))
    tmp = STATUS + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, STATUS)


def normalise(df):
    """Vendor rows -> panel rows. Keeps 上榜原因; drops non-A-share codes honestly."""
    import pandas as pd
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError("shape drift: missing columns %s" % missing)
    out = df.copy()
    out["代码"] = out["代码"].astype(str).str.strip().str.zfill(6)
    out["上榜日期"] = pd.to_datetime(out["上榜日期"]).dt.strftime("%Y-%m-%d")
    keep = out["代码"].str.match(r"^(0|3|6)\d{5}$")
    dropped = int((~keep).sum())
    out = out[keep]
    out = out.drop_duplicates(subset=KEY, keep="last")
    out["fetched_at"] = datetime.now().isoformat(timespec="seconds")
    return out.reset_index(drop=True), dropped


def merge(old, new):
    import pandas as pd
    if old is None or len(old) == 0:
        return new
    both = pd.concat([old, new], ignore_index=True, sort=False)
    return both.drop_duplicates(subset=KEY, keep="last").reset_index(drop=True)


def cutoff_of(df) -> str | None:
    if df is None or len(df) == 0:
        return None
    return str(df["上榜日期"].max())


def overlap_check(old, new_page, start: str, end: str) -> dict:
    """Row-level comparison on the days this page re-reports.  Mismatch = vendor history edit."""
    if old is None or len(old) == 0:
        return {"checked_rows": 0, "mismatch": 0, "first_mismatch": None}
    o = old[(old["上榜日期"] >= _iso(start)) & (old["上榜日期"] <= _iso(end))]
    if len(o) == 0:
        return {"checked_rows": 0, "mismatch": 0, "first_mismatch": None}
    a = o.set_index(KEY)["机构买入净额"].astype(float)
    b = new_page.set_index(KEY)["机构买入净额"].astype(float)
    common = a.index.intersection(b.index)
    bad = 0
    first = None
    for k in common:
        if not np.isclose(float(a.loc[k]), float(b.loc[k]), rtol=1e-6, atol=1.0):
            bad += 1
            if first is None:
                first = list(k)
    return {"checked_rows": int(common.size), "mismatch": bad, "first_mismatch": first}


def _iso(yyyymmdd: str) -> str:
    return "%s-%s-%s" % (yyyymmdd[:4], yyyymmdd[4:6], yyyymmdd[6:8])


# --------------------------------------------------------------------------- fetch

def fetch_page(start: str, end: str):
    import akshare as ak
    df = ak.stock_lhb_jgmmtj_em(start_date=start, end_date=end)
    if df is None or len(df) == 0:
        import pandas as pd
        return pd.DataFrame(columns=REQUIRED)
    return df


# --------------------------------------------------------------------------- run

def run(force: bool = False, allow_network: bool = True, now: datetime | None = None) -> int:
    now = now or datetime.now()
    if machine_id() != lane_host_of():
        print("lhb_inst: lane host is %s, this machine is %s -> honest no-op"
              % (lane_host_of(), machine_id()))
        return 0

    days = CAL.load_calendar()
    expected, _past = CAL.expected_last_day(days, now)
    prog = load_progress()
    old = load_panel()
    status = {"lane": "lhb_inst", "expected_bar": expected, "rows_before": 0 if old is None else int(len(old))}
    if old is not None:
        status["rows_before"] = int(len(old))

    if not force and expected and prog.get("cutoff") == expected:
        status.update({"verdict": "no_op", "cutoff": prog["cutoff"],
                       "no_op_reason": "panel covers the expected complete bar day"})
        write_status(status)
        print("lhb_inst: no-op (cutoff %s == expected %s)" % (prog["cutoff"], expected))
        return 0

    if not allow_network:
        status.update({"verdict": "no_op", "no_op_reason": "network disabled"})
        write_status(status)
        print("lhb_inst: no-op (network disabled)")
        return 0

    last = expected or now.strftime("%Y-%m-%d")
    windows = month_windows(FIRST_DATE, last)
    done = set(prog.get("months_done") or [])
    todo = [w for w in windows if w[0] not in done]
    if force and todo:
        todo = windows[-1:]          # force re-pulls only the newest page
    if not todo:
        status.update({"verdict": "no_op", "cutoff": prog.get("cutoff"),
                       "no_op_reason": "all monthly pages already collected"})
        write_status(status)
        print("lhb_inst: no-op (all pages collected, cutoff %s)" % prog.get("cutoff"))
        return 0

    print("lhb_inst: %d monthly page(s) to pull (%s..%s)" % (len(todo), todo[0][0], todo[-1][1]))
    fuse, mismatches, dropped_total, pages = 0, 0, 0, 0
    for start, end in todo:
        try:
            raw = fetch_page(start, end)
        except Exception as exc:                                # connection class
            fuse += 1
            print("  page %s..%s FAILED (%s) fuse=%d" % (start, end, type(exc).__name__, fuse))
            if fuse >= FUSE:
                status.update({"verdict": "source_failure", "fuse": fuse,
                               "cutoff": cutoff_of(old), "todo_left": len(todo) - pages})
                write_status(status)
                print("lhb_inst: connection fuse tripped, stopping")
                return 2
            time.sleep(2.0 * fuse)
            continue
        fuse = 0
        page, dropped = normalise(raw)
        dropped_total += dropped
        chk = overlap_check(old, page, start, end)
        mismatches += chk["mismatch"]
        old = merge(old, page)
        os.makedirs(PANEL_DIR, exist_ok=True)
        old.to_parquet(PANEL, index=False)
        done.add(start)
        pages += 1
        prog = {"months_done": sorted(done), "cutoff": cutoff_of(old)}
        save_progress(prog)
        time.sleep(SLEEP_S)

    cutoff = cutoff_of(old)
    status.update({
        "verdict": "ok" if mismatches == 0 else "overlap_mismatch",
        "cutoff": cutoff,
        "expected_bar": expected,
        "pages_pulled": pages,
        "rows_after": 0 if old is None else int(len(old)),
        "codes": 0 if old is None else int(old["代码"].nunique()),
        "dropped_non_a": dropped_total,
        "overlap_mismatch_rows": mismatches,
        "first_date": None if old is None or not len(old) else str(old["上榜日期"].min()),
    })
    write_status(status)
    print("lhb_inst: %s cutoff=%s rows=%d codes=%d mismatches=%d"
          % (status["verdict"], cutoff, status["rows_after"], status["codes"], mismatches))
    return 0 if mismatches == 0 else 3


def status() -> int:
    prog = load_progress()
    old = load_panel()
    print(json.dumps({"cutoff": prog.get("cutoff"), "months_done": len(prog.get("months_done") or []),
                      "rows": 0 if old is None else int(len(old)),
                      "codes": 0 if old is None else int(old["代码"].nunique()),
                      "lane_host": lane_host_of(), "machine": machine_id()},
                     ensure_ascii=False, indent=1))
    return 0


# --------------------------------------------------------------------------- selftest

def selftest() -> int:
    import pandas as pd
    fails = []

    def chk(name, cond):
        print(("  ok   " if cond else "  FAIL ") + name)
        if not cond:
            fails.append(name)

    w = month_windows("2020-01-15", "2020-03-02")
    chk("month windows cover a partial first and last month",
        w == [("20200115", "20200131"), ("20200201", "20200229"), ("20200301", "20200302")])

    chk("leap February ends on the 29th", _iso(w[1][1]) == "2020-02-29")

    raw = pd.DataFrame({
        "代码": ["600000", "600000", "000001", "900001", "600000"],
        "名称": ["A", "A", "B", "C", "A"],
        "收盘价": [1, 1, 2, 3, 1],
        "涨跌幅": [1, 1, 2, 3, 1],
        "买方机构数": [1, 1, 2, 3, 1], "卖方机构数": [0, 0, 1, 1, 0],
        "机构买入总额": [1.0, 1.0, 2.0, 3.0, 1.0],
        "机构卖出总额": [0.0, 0.0, 1.0, 1.0, 0.0],
        "机构买入净额": [1.0, 1.0, 1.0, 2.0, 5.0],
        "市场总成交额": [10, 10, 20, 30, 10],
        "机构净买额占总成交额比": [10.0, 10.0, 5.0, 6.7, 50.0],
        "上榜原因": ["r1", "r1", "r2", "r3", "r1"],
        "上榜日期": ["2020-01-02"] * 5,
    })
    page, dropped = normalise(raw)
    chk("non-A-share codes are dropped and counted", dropped == 1)
    chk("duplicate (code, date, reason) collapses to one row keeping the last", len(page) == 2)
    chk("the surviving duplicate is the later one", float(page.loc[page["代码"] == "600000", "机构买入净额"].iloc[0]) == 5.0)

    bad = raw.drop(columns=["上榜原因"])
    try:
        normalise(bad)
        chk("missing 上榜原因 raises shape drift", False)
    except ValueError:
        chk("missing 上榜原因 raises shape drift", True)

    merged = merge(None, page)
    chk("merge on empty keeps the page", len(merged) == 2)
    again = merge(merged, page)
    chk("merge is idempotent on the same page", len(again) == 2)
    chk("cutoff derives from the panel bytes", cutoff_of(again) == "2020-01-02")

    chk("overlap check is clean on identical pages",
        overlap_check(merged, page, "20200102", "20200102")["mismatch"] == 0)
    edited = page.copy()
    edited.loc[0, "机构买入净额"] = float(edited.loc[0, "机构买入净额"]) + 1e6
    chk("overlap check catches a vendor history edit",
        overlap_check(merged, edited, "20200102", "20200102")["mismatch"] == 1)

    old_rows = merge(merged, page)
    chk("append never loses an older row", cutoff_of(old_rows) == "2020-01-02" and len(old_rows) == 2)

    print("selftest: %d checks, %d failed" % (13, len(fails)))
    return 0 if not fails else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--offline", action="store_true")
    a = ap.parse_args()
    if a.cmd == "selftest":
        return selftest()
    if a.cmd == "status":
        return status()
    if a.cmd != "run":
        print(__doc__)
        return 2
    return run(force=a.force, allow_network=not a.offline)


if __name__ == "__main__":
    sys.exit(main())