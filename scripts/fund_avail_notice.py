"""T27 first-announce availability face for the three statement panels.

DEFECT (r1098 bm-a RCA, evidence results/_r1098bma_t27_notice_rca.json):
the column the collector stores as ``avail_date`` is a LATEST-REVISION stamp,
not the first-announce date. Measured on income 2025-03-31 (6,030 joined
rows): panel == source UPDATE_DATE for 99.83% of rows, == NOTICE_DATE for
4.67%; median stored lag from period end 393d vs true notice lag 29d; 99.25%
of stored dates fall AFTER the statutory deadline -- so the existing
``min(latest_revision, deadline)`` rescue (fund_avail_pit_t27) collapses
essentially every row onto one identical date, which destroys the
cross-sectional dispersion any PIT event study needs.

REPAIR: pull the per-period NOTICE_DATE field straight from the EM datacenter
reports (all three expose it) and derive ``avail_first = min(NOTICE_DATE)`` per
(code, period). Multiple source rows per (code, period) exist for original vs
restated filings; the minimum is the first availability and is therefore the
PIT-correct, never-early bound.

Outputs (derived faces only, source panels never rewritten):
    data/fund_statement_export/_avail_notice/<face>_<period>.parquet
    data/fund_statement_export/pit_avail/<face>_avail_first.parquet
    results/fund_avail_notice.json

Subcommands: refresh [--face income|cashflow|balance|all] [--max-periods N]
             build | status | selftest
Exit codes: 0 ok / no-op / spawned, 2 machinery, 3 coverage incomplete or
panel face missing. Selftest: python scripts/fund_avail_notice.py selftest
"""
from __future__ import annotations

import datetime as dt
import io
import json
import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
from update_fund_statements import (  # noqa: E402
    DATA_DIR, FACE_PATH, STAGING_DIR, statutory_deadline)
from config.lane_io import lane_host  # noqa: E402

LANE_OWNER = lane_host("fund_avail_notice", "bm-a")
CACHE_DIR = os.path.join(DATA_DIR, "_avail_notice")
OUT_DIR = os.path.join(DATA_DIR, "pit_avail")
SUMMARY = os.path.join(ROOT, "results", "fund_avail_notice.json")
STATUS_PATH = os.path.join(DATA_DIR, "_avail_notice_status.json")
LOCK = os.path.join(DATA_DIR, "_avail_notice.lock")
LOG = os.path.join(ROOT, "logs", "fund_avail_notice.log")
API = "https://datacenter-web.eastmoney.com/api/data/v1/get"
SLEEP_S = 2.5            # citizen pace (R109 precedent)
PAGE_SIZE = 500
CONN_STOP = 3            # consecutive connection failures -> honest stop
CALL_TIMEOUT_S = 40
NOTICE_GRACE_DAYS = 90   # disclosure window past the statutory deadline
FACES = ("income", "cashflow", "balance")
# report + period filter column per face (probed r1098: all expose NOTICE_DATE)
REPORTS = {
    "income": ("RPT_LICO_FN_CPD", "REPORTDATE"),
    "cashflow": ("RPT_DMSK_FN_CASHFLOW", "REPORT_DATE"),
    "balance": ("RPT_DMSK_FN_BALANCE", "REPORT_DATE"),
}


# ------------------------------------------------------------------ helpers
def atomic_write_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False, indent=1))
    os.replace(tmp, path)


def read_json(path, default):
    try:
        with io.open(path, "r", encoding="utf-8-sig") as fh:
            return json.load(fh)
    except Exception:                                          # noqa: BLE001
        return default


def lane_owner_id():
    try:
        with io.open(os.path.join(ROOT, "fleet", "machine.json"),
                     "r", encoding="utf-8-sig") as fh:
            return json.load(fh).get("machine_id")
    except Exception:                                          # noqa: BLE001
        return None


def staged_periods(face):
    """Periods that already have a staging panel (= our coverage target)."""
    if not os.path.isdir(STAGING_DIR):
        return []
    out = []
    for name in os.listdir(STAGING_DIR):
        if name.startswith(f"{face}_") and name.endswith(".parquet"):
            out.append(name[len(face) + 1:-len(".parquet")])
    return sorted(out)


def cache_path(face, period):
    return os.path.join(CACHE_DIR, f"{face}_{period}.parquet")


def iso_period(period):
    return f"{period[:4]}-{period[4:6]}-{period[6:]}"


def fetch_page(report, col, period, page):
    params = {
        "reportName": report,
        "columns": f"SECURITY_CODE,{col},NOTICE_DATE",
        "quoteColumns": "",
        "filter": f"({col}='{iso_period(period)}')",
        "pageNumber": str(page),
        "pageSize": str(PAGE_SIZE),
        "source": "WEB",
        "client": "WEB",
    }
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0",
                      "Referer": "https://data.eastmoney.com/"})
    with urllib.request.urlopen(req, timeout=CALL_TIMEOUT_S) as fh:
        payload = json.load(fh)
    result = payload.get("result") or {}
    return result.get("data") or [], int(result.get("pages") or 1)


def fetch_first_notice(face, period, sleep_s=SLEEP_S, fetcher=None):
    """Paginate one (face, period) and return per-code first NOTICE_DATE."""
    report, col = REPORTS[face]
    fetcher = fetcher or fetch_page
    rows, page, pages = [], 1, 1
    while page <= pages:
        data, pages = fetcher(report, col, period, page)
        if not data:
            break
        rows.extend(data)
        if page >= pages:
            break
        page += 1
        time.sleep(sleep_s)
    if not rows:
        return pd.DataFrame(columns=["code", "first_notice"])
    df = pd.DataFrame(rows)
    df = df.rename(columns={"SECURITY_CODE": "code"})
    df["code"] = df["code"].astype(str).str.zfill(6)
    df["notice"] = pd.to_datetime(df["NOTICE_DATE"], errors="coerce")
    df = df[df["notice"].notna() & df["code"].str.len().eq(6)]
    if df.empty:
        return pd.DataFrame(columns=["code", "first_notice"])
    agg = (df.groupby("code")["notice"].min()
             .reset_index().rename(columns={"notice": "first_notice"}))
    return agg


def write_cache(face, period, frame):
    os.makedirs(CACHE_DIR, exist_ok=True)
    tmp = cache_path(face, period) + ".tmp"
    frame.to_parquet(tmp, index=False)
    os.replace(tmp, cache_path(face, period))


# ------------------------------------------------------------------ refresh
def refresh(face="income", max_periods=None, sleep_s=SLEEP_S, fetcher=None,
            log=print):
    owner = lane_owner_id()
    if owner != LANE_OWNER:
        log(f"no-op: fund_avail_notice lane owned by {LANE_OWNER}, "
            f"not this machine ({owner or '?'})")
        return 0
    done, touched, missing_rows, fails = [], [], [], 0
    todo = [p for p in staged_periods(face) if not os.path.exists(cache_path(face, p))]
    if max_periods:
        todo = todo[-int(max_periods):]
    if not todo:
        log(f"no-op: {face} notice cache already covers every staged period")
        return 0
    for period in todo:
        try:
            frame = fetch_first_notice(face, period, sleep_s=sleep_s,
                                       fetcher=fetcher)
            write_cache(face, period, frame)
            if len(frame) == 0:
                missing_rows.append(period)
            done.append(period)
            fails = 0
            log(f"{face} {iso_period(period)}: {len(frame)} codes")
        except Exception as exc:                              # noqa: BLE001
            fails += 1
            log(f"{face} {iso_period(period)} FAILED ({fails}/{CONN_STOP}): "
                f"{type(exc).__name__}: {exc}")
            if fails >= CONN_STOP:
                log("connection fuse: stopping honestly, checkpoint kept")
                break
            continue
        time.sleep(sleep_s)
    atomic_write_json(STATUS_PATH, {
        "ts": dt.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z"),
        "face": face,
        "cache_dir": os.path.relpath(CACHE_DIR, ROOT),
        "periods_done": done,
        "periods_zero_rows": missing_rows,
        "staged_total": len(staged_periods(face)),
        "cached_total": sum(
            1 for p in staged_periods(face) if os.path.exists(cache_path(face, p))),
        "conn_fuse_tripped": fails >= CONN_STOP,
    })
    return 0


# -------------------------------------------------------------------- build
def build_face(face, frame, cache, grace_days=NOTICE_GRACE_DAYS):
    """avail_first = min(source NOTICE_DATE, stored) -- both are upper bounds
    on the true announce date, so the minimum cannot be early. Rows without a
    cached notice date fall back to the statutory deadline (never fabricated
    early).

    NOTICE-WINDOW GATE (r1099 bm-a, evidence results/fund_avail_dispersion.json):
    for periods before ~2010 the earliest source NOTICE_DATE per (code, period)
    is a RESTATEMENT-era stamp. Measured on income 2005-03-31: 1387 of 1437
    codes carry their first notice in 2006-04, a full year after the period,
    because the EM income table stores old quarters as they appear in later
    filings. Consuming that directly would push ~97% of the pre-2010 rows
    ~360 days late. A notice is therefore accepted only inside the plausible
    disclosure window (period_end, deadline + grace_days]; anything beyond it
    is reported as out_of_window and falls back to the deadline bound (the
    pre-existing, already-disclosed optimism)."""
    sub = frame[["code", "period_end", "avail_date"]].copy()
    cache = cache.rename(columns={"first_notice": "first_notice"})
    cache["code"] = cache["code"].astype(str).str.zfill(6)
    sub["code"] = sub["code"].astype(str).str.zfill(6)
    sub = sub.merge(cache, on="code", how="left")
    sub["stored"] = pd.to_datetime(sub["avail_date"], errors="coerce")
    period_d = pd.to_datetime(sub["period_end"])
    deadline = pd.Series(
        [pd.Timestamp(statutory_deadline(f"{p.year}{p.month:02d}{p.day:02d}"))
         for p in period_d], index=sub.index, dtype="datetime64[ns]")
    notice = pd.to_datetime(sub["first_notice"], errors="coerce")
    # a notice before the period end is impossible -> treat as absent
    notice = notice.where(notice >= period_d)
    # restatement-era stamps land far beyond the disclosure window -> absent
    window_end = deadline + pd.Timedelta(days=int(grace_days))
    in_window = notice.notna() & (notice <= window_end)
    sub["notice_status"] = "absent"
    sub["notice_status"] = sub["notice_status"].where(
        notice.isna(), "out_of_window")
    sub["notice_status"] = sub["notice_status"].mask(in_window, "ok")
    notice = notice.where(in_window)
    stored = sub["stored"].where(sub["stored"] >= period_d)
    # with a notice date, the tighter of the two upper bounds wins; without
    # one the statutory deadline is the only honest bound (stored is a
    # latest-revision stamp, far looser than the deadline).
    first = pd.concat([notice, stored], axis=1).min(axis=1)
    first = first.where(notice.notna(), deadline)
    first = first.where(first >= period_d, deadline)
    sub["avail_first"] = first.dt.strftime("%Y-%m-%d")
    sub["deadline"] = deadline.dt.strftime("%Y-%m-%d")
    sub["source_notice"] = notice.dt.strftime("%Y-%m-%d")
    sub["late_filer"] = first > deadline
    if (pd.to_datetime(sub["avail_first"]) < period_d).any():
        raise AssertionError(f"{face}: avail_first before period_end")
    return sub[["code", "period_end", "avail_first", "source_notice",
                "deadline", "late_filer", "notice_status"]]


def build(log=print):
    receipts = {"ts": dt.datetime.now().astimezone().strftime(
                    "%Y-%m-%dT%H:%M:%S%z"),
                "audit": "T27 first-announce availability face "
                         "(min(source NOTICE_DATE, stored) per code/period)",
                "faces": {}}
    incomplete, missing_face = [], []
    os.makedirs(OUT_DIR, exist_ok=True)
    for face in FACES:
        path = FACE_PATH[face]
        if not os.path.exists(path):
            missing_face.append(face)
            continue
        periods = staged_periods(face)
        uncached = [p for p in periods if not os.path.exists(cache_path(face, p))]
        frames = [pd.read_parquet(cache_path(face, p))
                  for p in periods if os.path.exists(cache_path(face, p))]
        frame = pd.read_parquet(path)
        entry = {"rows": int(len(frame)), "periods_staged": len(periods),
                 "periods_cached": len(periods) - len(uncached),
                 "periods_uncached_n": len(uncached)}
        if uncached:
            # honest partial: never publish a face that silently lacks periods
            entry["status"] = "coverage_incomplete"
            entry["periods_uncached_sample"] = uncached[:8]
            receipts["faces"][face] = entry
            incomplete.append(face)
            continue
        cache = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(
            columns=["code", "first_notice"])
        out = build_face(face, frame, cache)
        target = os.path.join(OUT_DIR, f"{face}_avail_first.parquet")
        out.to_parquet(target, index=False)
        lag_stored = (pd.to_datetime(frame.set_index(
            ["code", "period_end"]).loc[
                zip(out["code"], out["period_end"]), "avail_date"].values)
            .to_numpy())
        st = pd.to_datetime(out.set_index(["code", "period_end"]).loc[
            list(zip(out["code"], out["period_end"])), "avail_first"].values)
        per = pd.to_datetime(out["period_end"])
        known_stored = pd.to_datetime(frame.set_index(
            ["code", "period_end"]).loc[
                list(zip(out["code"], out["period_end"])), "avail_date"].values,
            errors="coerce")
        entry.update({
            "status": "ready",
            "rows": int(len(out)),
            "late_filer_rows": int(out["late_filer"].sum()),
            "median_lag_stored_days": float(
                (known_stored - per).dt.days.median()),
            "median_lag_first_days": float((st - per).dt.days.median()),
            "rows_tightened": int(
                ((st - per).dt.days < (known_stored - per).dt.days).sum()),
            "out": os.path.relpath(target, ROOT),
        })
        del lag_stored
        receipts["faces"][face] = entry
        log(f"{face} ready: {entry}")
    atomic_write_json(SUMMARY, receipts)
    log("wrote " + os.path.relpath(SUMMARY, ROOT))
    if missing_face:
        log(f"MISSING PANEL FACES: {missing_face}")
        return 3
    if incomplete:
        log(f"coverage incomplete: {incomplete} (run refresh first)")
        return 3
    return 0


# ------------------------------------------------------------------- status
def status():
    payload = {"ts": dt.datetime.now().astimezone().strftime(
                   "%Y-%m-%dT%H:%M:%S%z"),
               "lane_owner": LANE_OWNER, "machine": lane_owner_id(),
               "faces": {}}
    for face in FACES:
        periods = staged_periods(face)
        cached = [p for p in periods if os.path.exists(cache_path(face, p))]
        payload["faces"][face] = {
            "periods_staged": len(periods),
            "periods_cached": len(cached),
            "complete": bool(periods) and len(cached) == len(periods),
            "last_status": read_json(STATUS_PATH, {}),
        }
    print(json.dumps(payload, ensure_ascii=False, indent=1))
    return 0


# ----------------------------------------------------------------- selftest
def selftest():
    checks = []
    # 1. min(notice, stored) takes the earlier upper bound
    frame = pd.DataFrame({"code": ["000001", "000002"],
                          "period_end": ["2025-03-31", "2025-03-31"],
                          "avail_date": ["2026-04-25", "2025-04-20"]})
    cache = pd.DataFrame({"code": ["000001", "000002"],
                          "first_notice": ["2025-04-25", "2025-04-30"]})
    out = build_face("income", frame, cache)
    checks.append(list(out["avail_first"]) == ["2025-04-25", "2025-04-20"])
    # 2. absent cache -> statutory deadline, never fabricated early (the
    #    stored revision stamp is deliberately NOT used as a fallback)
    out2 = build_face("income", frame, pd.DataFrame(
        columns=["code", "first_notice"]))
    checks.append(list(out2["avail_first"]) == ["2025-04-30", "2025-04-30"])
    # 3. a notice date before period_end is impossible -> ignored (deadline)
    cache3 = pd.DataFrame({"code": ["000001"], "first_notice": ["2025-01-05"]})
    out3 = build_face("income", frame.iloc[:1], cache3)
    checks.append(out3["avail_first"].iloc[0] == "2025-04-30")
    # 4. late filer flag (first announce after the statutory deadline)
    cache4 = pd.DataFrame({"code": ["000001", "000002"],
                           "first_notice": ["2025-06-15", "2025-04-01"]})
    out4 = build_face("income", frame, cache4)
    checks.append(list(out4["late_filer"]) == [True, False])
    # 5. never earlier than period end
    checks.append(not (pd.to_datetime(out4["avail_first"]) <
                       pd.to_datetime(out4["period_end"])).any())
    # 6. first-announce aggregation keeps the minimum across restatements
    raw = [{"SECURITY_CODE": "1", "NOTICE_DATE": "2025-08-30 00:00:00"},
           {"SECURITY_CODE": "1", "NOTICE_DATE": "2026-04-25 00:00:00"},
           {"SECURITY_CODE": "2", "NOTICE_DATE": "2025-04-29 00:00:00"}]
    df = pd.DataFrame(raw)
    df = df.rename(columns={"SECURITY_CODE": "code"})
    df["code"] = df["code"].astype(str).str.zfill(6)
    df["notice"] = pd.to_datetime(df["NOTICE_DATE"], errors="coerce")
    agg = (df.groupby("code")["notice"].min()
             .reset_index().rename(columns={"notice": "first_notice"}))
    checks.append(agg.loc[agg["code"] == "000001", "first_notice"].iloc[0] ==
                  pd.Timestamp("2025-08-30"))
    # 7. period coverage helper reads the staging dir naming convention
    checks.append(iso_period("20250331") == "2025-03-31")
    # 8. build_face output schema is stable
    checks.append(list(out.columns) == ["code", "period_end", "avail_first",
                                        "source_notice", "deadline",
                                        "late_filer", "notice_status"])
    # 9. restatement-era notice (a year late) is gated out -> deadline bound,
    #    never a ~360d delay (the pre-2010 defect measured in r1099)
    cache9 = pd.DataFrame({"code": ["000001"], "first_notice": ["2026-04-25"]})
    out9 = build_face("income", frame.iloc[:1], cache9)
    checks.append(out9["avail_first"].iloc[0] == "2025-04-30"
                  and out9["notice_status"].iloc[0] == "out_of_window")
    # 10. the window is inclusive at deadline+grace and closes one day later
    edge_ok = pd.DataFrame({"code": ["000001"], "first_notice": ["2025-07-29"]})
    edge_bad = pd.DataFrame({"code": ["000001"], "first_notice": ["2025-07-30"]})
    o_ok = build_face("income", frame.iloc[:1], edge_ok)
    o_bad = build_face("income", frame.iloc[:1], edge_bad)
    checks.append(o_ok["notice_status"].iloc[0] == "ok"
                  and o_ok["avail_first"].iloc[0] == "2025-07-29"
                  and o_bad["notice_status"].iloc[0] == "out_of_window"
                  and o_bad["avail_first"].iloc[0] == "2025-04-30")
    failed = [i for i, ok in enumerate(checks) if not ok]
    print(f"selftest {len(checks) - len(failed)}/{len(checks)} PASS")
    if failed:
        print("failed cases:", failed)
        return 1
    return 0


def spawn_refresh(face="all"):
    """Detach a refresh run so the round does not block on ~1500 requests."""
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    args = [sys.executable, os.path.abspath(__file__)]
    code = (
        "import sys; sys.path.insert(0, r'%s');"
        "import fund_avail_notice as m;"
        "faces = ('income','cashflow','balance') if %r == 'all' else (%r,);"
        "[m.refresh(f) for f in faces]"
        % (os.path.join(ROOT, "scripts"), face, face)
    )
    with io.open(LOG, "a", encoding="utf-8") as fh:
        fh.write("\n=== spawn %s face=%s ===\n"
                 % (time.strftime("%Y-%m-%dT%H:%M:%S"), face))
    env = dict(os.environ, PYTHONUNBUFFERED="1")
    proc = subprocess.Popen(
        [sys.executable, "-c", code],
        cwd=ROOT, stdout=io.open(LOG, "a", encoding="utf-8"),
        stderr=subprocess.STDOUT, close_fds=True, env=env,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    atomic_write_json(STATUS_PATH, {
        "ts": dt.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z"),
        "mode": "refresh_spawned", "face": face, "pid": proc.pid,
        "log": os.path.relpath(LOG, ROOT),
    })
    print(f"spawned refresh pid={proc.pid} face={face} log={LOG}")
    del args
    return 0


def main(argv=None):
    argv = argv or sys.argv[1:]
    cmd = argv[0] if argv else "build"
    if cmd == "selftest":
        return selftest()
    if cmd == "status":
        return status()
    if cmd == "build":
        return build()
    if cmd == "refresh":
        face = "income"
        max_periods = None
        detach = False
        rest = argv[1:]
        i = 0
        while i < len(rest):
            if rest[i] == "--face" and i + 1 < len(rest):
                face = rest[i + 1]
                i += 2
            elif rest[i] == "--max-periods" and i + 1 < len(rest):
                max_periods = int(rest[i + 1])
                i += 2
            elif rest[i] == "--detach":
                detach = True
                i += 1
            else:
                i += 1
        if detach:
            return spawn_refresh(face)
        if face == "all":
            rc = 0
            for f in FACES:
                rc = refresh(f, max_periods=max_periods) or rc
            return rc
        return refresh(face, max_periods=max_periods)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())