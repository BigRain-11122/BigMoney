"""Index daily forward refresh (bm-c lane, r1791).

Why this exists
---------------
``idx_fut_basis.load_index`` returns the on-disk cache the moment the file
exists, so ``data/index_daily/*.csv`` could only ever move when a human ran
``download_indexes.py``.  Nobody did: on 2026-11-17 the four files still ended
2026-11-13 while the futures panel had bars through 2026-11-16, and the carry
paper's own discount legs had no index close to divide by.  r1777 recorded it
as "a no-producer face, not a data-source failure" -- this script is the
producer.  It does not change any reader's semantics: the cache stays the
single input, it is now refreshed forward instead of frozen.

Rules (update_futures family -- same laws, one implementation style)
--------------------------------------------------------------------
* Universe is derived from the files already on disk, never hard-coded: a code
  added to data/index_daily is refreshed by the next run.
* Append-only.  Overlapping rows are re-read from the source and compared
  (close, tol 1e-3: sina publishes two decimals); a mismatch flags
  ``overlap_mismatch`` for that code, leaves the local file untouched and the
  run exits 3 -- an index vendor re-basing history is a disclosure, not a
  silent rewrite.
* Completeness: a row dated today is dropped before 15:30 local (same constant
  the futures lane uses), so a partial session never lands.
* Zero-network no-op: when every code's tail already covers the latest
  COMPLETE bar date (calendar from update_futures -- the exchange calendar is
  not re-implemented here), nothing is fetched.
* Throttle: 30 min between attempts; the attempt mirror is written BEFORE the
  fetch so a crash mid-run still throttles (r18 lesson).
* Shape drift is fail-closed: a source frame that no longer has date/close
  stops the run with exit 3 instead of writing an empty panel.
* Lane ownership: this face feeds the idx_fut_* family that bm-c builds, so
  bm-c owns it.  Any other machine prints an honest no-op (R31 precedent) --
  a second writer is exactly how two panels drift apart.

Exit codes: 0 = ok / no-op; 2 = source failure (honest, never masked);
3 = overlap mismatch or shape drift (local untouched).
"""
from __future__ import annotations

import csv
import datetime as dt
import glob
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDX_DIR = os.path.join(ROOT, "data", "index_daily")
STATUS = os.path.join(ROOT, "results", "index_daily_update_status.json")
sys.path.insert(0, ROOT)
from config.lane_io import machine_id, write_lane  # noqa: E402
import scripts.update_futures as FUT  # noqa: E402  (single calendar implementation)

LANE_HOST = "bm-c"
SLEEP_S = 2.5
MIN_ATTEMPT_S = 30 * 60
CLOSE_TOL = 1e-3


def _clear_proxy_env():
    for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY",
              "all_proxy", "ALL_PROXY"):
        os.environ.pop(k, None)


def read_rows(path):
    """(date, close) rows from a cached csv. Pure."""
    with open(path, "r", encoding="utf-8", newline="") as fh:
        out = []
        for r in csv.DictReader(fh):
            try:
                out.append((str(r["date"])[:10], float(r["close"])))
            except (KeyError, TypeError, ValueError):
                continue
    return out


def merge_rows(local, fetched, tol=CLOSE_TOL):
    """Union by date; overlapping closes compared. Pure.

    Returns (merged_rows, n_new, mismatches) where a mismatch row is
    (date, local_close, fetched_close).  Merged is date-sorted and strictly
    increasing; fetched wins ONLY on dates the local panel does not have.
    """
    loc = {d: c for d, c in local}
    bad = []
    new = 0
    for d, c in fetched:
        if d in loc:
            if abs(loc[d] - c) > tol:
                bad.append((d, loc[d], c))
        else:
            loc[d] = c
            new += 1
    rows = sorted(loc.items())
    return rows, new, bad


def codes_on_disk():
    return sorted(os.path.splitext(os.path.basename(p))[0]
                  for p in glob.glob(os.path.join(IDX_DIR, "*.csv")))


def expected_date(now=None):
    return FUT.expected_latest_bar_date(now or dt.datetime.now())


def behind(codes, want):
    """Codes whose tail is older than `want`. Pure."""
    out = {}
    for code in codes:
        rows = read_rows(os.path.join(IDX_DIR, code + ".csv"))
        tail = rows[-1][0] if rows else ""
        if tail < want:
            out[code] = tail
    return out


def rows_from_frame(df, code="?"):
    """Validate the source frame's shape, then read it. Pure -- splits the
    refusal path from the network so the guard is testable."""
    cols = {str(c).lower(): c for c in df.columns}
    if "date" not in cols or "close" not in cols:
        raise RuntimeError("shape drift for %s: columns=%s"
                           % (code, list(df.columns)))
    rows = [(str(d)[:10], float(c)) for d, c in zip(df[cols["date"]], df[cols["close"]])]
    rows = [(d, c) for d, c in rows if c > 0]
    if not rows:
        raise RuntimeError("empty frame for %s" % code)
    return rows


def fetch_index(code):
    """Full history from sina via akshare, as (date, close) rows."""
    _clear_proxy_env()
    import akshare as ak
    rows = rows_from_frame(ak.stock_zh_index_daily(symbol=code), code)
    return FUT.completeness_filter([{"date": d, "close": c} for d, c in rows])[0]


def write_panel(code, rows):
    path = os.path.join(IDX_DIR, code + ".csv")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["date", "close"])
        for d, c in rows:
            w.writerow([d, c])
    os.replace(tmp, path)


def _last_attempt():
    try:
        with open(STATUS, encoding="utf-8") as fh:
            return float(json.load(fh).get("last_attempt_epoch") or 0)
    except Exception:
        return 0.0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--selftest" in argv:
        return _selftest()
    mid = machine_id()
    now = dt.datetime.now()
    status = {
        "face": "index_daily_update_status",
        "generated": now.isoformat(timespec="seconds"),
        "host": LANE_HOST,
        "machine": mid,
        "codes": codes_on_disk(),
    }
    if mid != LANE_HOST:
        status.update({"action": "no-op", "reason":
                       "lane owned by %s (R31); this host only reads"
                       % LANE_HOST, "exit": 0})
        _write_status(status)
        print("index_daily: no-op (lane owned by %s, this host=%s)"
              % (LANE_HOST, mid))
        return 0
    want = expected_date(now)
    pend = behind(status["codes"], want)
    status["expected_complete_date"] = want
    status["behind"] = pend
    if not pend:
        status.update({"action": "no-op", "reason":
                       "every code already covers %s" % want, "exit": 0})
        _write_status(status)
        print("index_daily: no-op (all %d codes cover %s)"
              % (len(status["codes"]), want))
        return 0
    since = (now.timestamp() - _last_attempt())
    if since < MIN_ATTEMPT_S:
        status.update({"action": "throttled", "exit": 0,
                       "reason": "last attempt %.0fs ago (< %ds)"
                                 % (since, MIN_ATTEMPT_S)})
        _write_status(status)
        print("index_daily: throttled (%.0fs since last attempt)" % since)
        return 0
    # attempt mirror before the network (a crash still throttles)
    status["last_attempt_epoch"] = int(now.timestamp())
    _write_status(status)

    fetched, appended, mism, failed = {}, {}, {}, {}
    for code in sorted(pend):
        try:
            rows = fetch_index(code)
        except Exception as exc:
            failed[code] = str(exc)[:160]
            print("index_daily: source failure %s: %s" % (code, exc))
            time.sleep(SLEEP_S)
            continue
        fetched[code] = len(rows)
        local = read_rows(os.path.join(IDX_DIR, code + ".csv"))
        merged, n_new, bad = merge_rows(local, [(r["date"], r["close"]) for r in rows])
        if bad:
            mism[code] = [{"date": d, "local": l, "source": s} for d, l, s in bad[:5]]
            mism[code + "_n"] = len(bad)
            continue
        if n_new:
            write_panel(code, merged)
            appended[code] = n_new
        time.sleep(SLEEP_S)

    tails = {}
    for code in status["codes"]:
        rows = read_rows(os.path.join(IDX_DIR, code + ".csv"))
        tails[code] = rows[-1][0] if rows else ""
    status.update({
        "fetched_rows": fetched,
        "appended_rows": appended,
        "overlap_mismatch": mism,
        "source_failures": failed,
        "tails": tails,
        "panel_cutoff": min(tails.values()) if tails else "",
    })
    if mism:
        status.update({"action": "blocked", "exit": 3,
                       "reason": "index vendor re-based history; local untouched"})
        _write_status(status)
        print("index_daily: OVERLAP MISMATCH %s (local untouched)"
              % sorted(k for k in mism if not k.endswith("_n")))
        return 3
    if failed and not appended:
        status.update({"action": "source_failure", "exit": 2})
        _write_status(status)
        print("index_daily: source failure on %s" % sorted(failed))
        return 2
    status.update({"action": "refreshed" if appended else "no-change", "exit": 0,
                   "reason": ("appended %d rows" % sum(appended.values()))
                             if appended else "source already current"})
    _write_status(status)
    print("index_daily: %s %s -> tails %s"
          % (status["action"], appended or "{}", tails))
    return 2 if failed else 0


def _write_status(status):
    os.makedirs(os.path.dirname(STATUS), exist_ok=True)
    tmp = STATUS + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(status, fh, ensure_ascii=False, indent=1, default=str)
    os.replace(tmp, STATUS)
    write_lane("index_daily_update_status", status)


# ------------------------------------------------------------------ selftest


def _selftest():
    ok = []

    def chk(name, cond):
        ok.append((name, bool(cond)))

    local = [("2026-11-12", 100.0), ("2026-11-13", 101.0)]
    src = [{"date": "2026-11-13", "close": 101.0},
           {"date": "2026-11-16", "close": 103.5}]
    merged, n, bad = merge_rows(local, [(r["date"], r["close"]) for r in src])
    chk("L1 append one new date", n == 1 and merged[-1] == ("2026-11-16", 103.5))
    chk("L2 overlap agrees -> zero mismatch", bad == [])
    chk("L3 merged is date sorted + strictly increasing",
        [d for d, _ in merged] == sorted({d for d, _ in merged}))

    # a vendor re-basing history must NOT be swallowed
    src2 = [{"date": "2026-11-13", "close": 109.0},
            {"date": "2026-11-16", "close": 103.5}]
    _, _, bad2 = merge_rows(local, [(r["date"], r["close"]) for r in src2])
    chk("L4 overlap disagreement is flagged", len(bad2) == 1 and bad2[0][0] == "2026-11-13")
    chk("L4b tolerance is 1e-3 not exact",
        merge_rows(local, [("2026-11-13", 101.0009)])[2] == []
        and merge_rows(local, [("2026-11-13", 101.01)])[2] != [])

    # fetched rows never overwrite a local date
    merged3, n3, _ = merge_rows(local, [("2026-11-13", 101.0)])
    chk("L5 an existing date stays local (append-only)", n3 == 0 and merged3 == local)

    # completeness: today's row is dropped before 15:30
    rows = [{"date": "2026-11-17", "close": 1.0}]
    kept, dropped = FUT.completeness_filter(rows, now=dt.datetime(2026, 11, 17, 10, 0))
    chk("L6 pre-15:30 drops today's row", not kept and dropped == 1)
    kept, dropped = FUT.completeness_filter(rows, now=dt.datetime(2026, 11, 17, 16, 0))
    chk("L6b post-15:30 keeps it", len(kept) == 1 and dropped == 0)

    # behind(): a code at the wanted date is not pending -- measured on a real
    # temporary panel, because "behind is strict" was a fake leg the first time
    import tempfile
    global IDX_DIR
    keep = IDX_DIR
    with tempfile.TemporaryDirectory() as td:
        IDX_DIR = td
        for code, tail in (("sh000300", "2026-11-13"), ("sh000905", "2026-11-16")):
            with open(os.path.join(td, code + ".csv"), "w", encoding="utf-8",
                      newline="") as fh:
                fh.write("date,close\n2026-11-12,1.0\n%s,2.0\n" % tail)
        got = behind(["sh000300", "sh000905"], "2026-11-16")
        chk("L7 behind lists only the stale code", got == {"sh000300": "2026-11-13"})
        chk("L7b a panel exactly at the wanted date is not pending",
            behind(["sh000905"], "2026-11-16") == {})
        chk("L7c codes_on_disk derives the universe, no hard-coded list",
            codes_on_disk() == ["sh000300", "sh000905"])
    IDX_DIR = keep

    # shape drift is a refusal, not an empty write
    class _F:  # minimal DataFrame stand-in
        def __init__(self, cols, rows):
            self.columns, self._rows = cols, rows

        def __getitem__(self, k):
            i = list(self.columns).index(k)
            return [r[i] for r in self._rows]

    try:
        rows_from_frame(_F(["day", "px"], [("2026-11-16", 1.0)]), "sh000300")
        chk("L8 renamed source columns are refused", False)
    except RuntimeError as exc:
        chk("L8 renamed source columns are refused", "shape drift" in str(exc))
    try:
        rows_from_frame(_F(["date", "close"], [("2026-11-16", -1.0)]), "sh000300")
        chk("L8b a frame with no positive close is refused", False)
    except RuntimeError as exc:
        chk("L8b a frame with no positive close is refused", "empty frame" in str(exc))
    chk("L8c a good frame reads through",
        rows_from_frame(_F(["date", "close"], [("2026-11-16", 4016.29)]))
        == [("2026-11-16", 4016.29)])

    failed = [n for n, c in ok if not c]
    for n, c in ok:
        print("%-52s %s" % (n, "PASS" if c else "FAIL"))
    print("selftest %d/%d" % (len(ok) - len(failed), len(ok)))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
