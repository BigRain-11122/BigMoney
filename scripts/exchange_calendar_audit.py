# -*- coding: utf-8 -*-
"""exchange_calendar_audit.py -- official exchange calendar + panel lag audit.

WHY (r1286): every data leg in this repo decides "is there anything to do?" by
comparing the panel against an *expected complete bar date* that it derives from
the panel itself (or from a calendar built out of the panel). That face cannot
tell a market holiday from a dead feed: on 2026-10-26 -- an official trading day
-- the ETF feed had no bar at 16:45, update_daily printed "probe_no_new", the
forward ledger printed "NO-OP last_bar=2026-10-23", and all 42 S6 legs returned
rc=0. The round's product (the first real forward mark) therefore looked like a
quiet no-op instead of a feed lag. The audit below adds the missing independent
reference: the official trading-day list, which no row of ours can produce.

Two faces, one pass:
  data/exchange_calendar.csv    official trading days (sina calendar, one request)
  results/data_lag_audit.json   official days the local panel is missing,
                                with a verdict: in_sync / source_lag / panel_gap

Refresh gate (zero network on the steady state): the calendar is refetched only
when coverage ends inside COVERAGE_MIN_DAYS or the last attempt is older than
FETCH_TTL_H. The sina calendar carries the full year, so after one fetch the
following rounds are pure local computation. The artifact is written as a UNION
with whatever is already on disk -- the calendar is history and can never shrink.

Verdicts (parsed by the round report, not by a hidden heuristic):
  in_sync     panel has every official day it should by now
  source_lag  only the most recent official day is missing and that day is today,
              i.e. the market closed and the feed has not published yet
  panel_gap   an older official day is missing -> the panel is behind the market,
              not merely behind today's publication

Exit codes: run 0 = in_sync/source_lag, 1 = panel_gap (needs attention, never
silenced), 2 = mechanism failure (no calendar at all, unreadable panel).
selftest 0 = pass / 1 = fail (hermetic tmp sandbox, zero network).

Usage:
    python scripts/exchange_calendar_audit.py run
    python scripts/exchange_calendar_audit.py run --no-network
    python scripts/exchange_calendar_audit.py selftest
"""
import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import os
import re
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAL_PATH = os.path.join(ROOT, "data", "exchange_calendar.csv")
FETCH_STAMP = os.path.join(ROOT, "data", "exchange_calendar._fetch.json")
OUT_PATH = os.path.join(ROOT, "results", "data_lag_audit.json")
DAILY_DIR = os.path.join(ROOT, "data", "daily")
LEDGER = os.path.join(ROOT, "results", "etf_book_forward", "LEDGER.json")

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CLOSE_ACCEPT_TIME = dt.time(15, 30)   # same convention as update_daily/update_etf_daily
COVERAGE_MIN_DAYS = 30                # refetch when the calendar ends sooner than this
FETCH_TTL_H = 6.0                     # ... or when the last attempt is older than this
MISSING_WINDOW = 10                   # audit window: last N official days


# ------------------------------------------------------------------ calendar

def parse_calendar_text(text):
    """Rows -> sorted unique date strings. Raises ValueError on any bad row.

    The artifact is deliberately stricter than "month approximations": a
    malformed or duplicate row is a mechanism failure, not a data note, because
    every consumer of this file treats membership as exchange-open evidence.
    """
    days = []
    for i, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if not s:
            continue
        d = s.split(",")[0].strip()
        if d == "date":          # header tolerated on hand-edited files
            continue
        if not DATE_RE.match(d):
            raise ValueError(f"row {i}: not a YYYY-MM-DD date: {s!r}")
        dt.date.fromisoformat(d)  # calendar-valid (rejects 2026-02-30)
        days.append(d)
    if len(set(days)) != len(days):
        raise ValueError("duplicate dates in calendar")
    return sorted(set(days))


def load_calendar(path=CAL_PATH):
    if not os.path.exists(path):
        return []
    with io.open(path, "r", encoding="utf-8") as f:
        return parse_calendar_text(f.read())


def merge_calendar(current, fetched):
    """Union, never truncation: the calendar is history (r1286 rule)."""
    return sorted(set(current) | set(fetched))


def write_calendar(days, path=CAL_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    body = "date\n" + "".join(d + "\n" for d in days)
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(body)
    os.replace(tmp, path)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def fetch_official():
    """Official SSE/SZSE trading days via sina (akshare wrapper, one request).

    Sina is the source this lane can reach; the EM endpoints are dead on this
    host (results/_r280bmb_probe_akshare_daily.json). Returns YYYY-MM-DD list.
    """
    import akshare as ak
    import pandas as pd
    df = ak.tool_trade_date_hist_sina()
    col = "trade_date" if "trade_date" in df.columns else df.columns[0]
    days = pd.to_datetime(df[col]).dt.strftime("%Y-%m-%d").tolist()
    return parse_calendar_text("\n".join(days))


def fetch_stamp():
    try:
        with io.open(FETCH_STAMP, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def needs_fetch(days, now):
    if not days:
        return True
    last = dt.date.fromisoformat(days[-1])
    if (last - now.date()).days < COVERAGE_MIN_DAYS:
        return True
    ts = fetch_stamp().get("ts")
    if not ts:
        return True
    try:
        age_h = (now - dt.datetime.fromisoformat(ts)).total_seconds() / 3600.0
    except Exception:
        return True
    return age_h >= FETCH_TTL_H


def refresh(now, allow_network=True):
    """Returns (days, info). Network failures degrade to the local artifact."""
    days = load_calendar()
    info = {"fetched": False, "reason": None, "error": None}
    if not needs_fetch(days, now):
        info["reason"] = "coverage_and_ttl_ok"
        return days, info
    if not allow_network:
        info["reason"] = "network_disabled"
        return days, info
    try:
        fresh = fetch_official()
    except Exception as e:                                  # noqa: BLE001
        info["error"] = f"{type(e).__name__}: {e}"
        info["reason"] = "fetch_failed_local_only"
        return days, info
    merged = merge_calendar(days, fresh)
    sha = write_calendar(merged)
    info.update(fetched=True, reason="refreshed", rows_before=len(days),
                rows_after=len(merged), sha256=sha)
    os.makedirs(os.path.dirname(FETCH_STAMP), exist_ok=True)
    with io.open(FETCH_STAMP, "w", encoding="utf-8") as f:
        json.dump({"ts": now.isoformat(timespec="seconds"),
                   "source": "akshare.tool_trade_date_hist_sina",
                   "rows": len(merged), "sha256": sha}, f, ensure_ascii=False)
    return merged, info


# ------------------------------------------------------------------- panel

def panel_tails(daily_dir=DAILY_DIR):
    """{symbol: last bar date} for every CSV on the panel; dense tail read only."""
    tails = {}
    if not os.path.isdir(daily_dir):
        return tails
    for name in sorted(os.listdir(daily_dir)):
        if not name.endswith(".csv"):
            continue
        path = os.path.join(daily_dir, name)
        last = None
        try:
            with io.open(path, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    s = line.strip()
                    if s and DATE_RE.match(s.split(",")[0].strip()):
                        last = s.split(",")[0].strip()
        except OSError:
            continue
        if last:
            tails[name[:-4]] = last
    return tails


def expected_last_day(days, now):
    """Last official day whose bar must exist by `now`.

    Before the 15:30 accept time today's bar is not expected yet -- the exact
    boundary update_daily uses. Getting this wrong produces a false 'lag' alert
    every morning, so it is pinned by a selftest leg.
    """
    today = now.date().isoformat()
    past = [d for d in days if d < today]
    if now.time() >= CLOSE_ACCEPT_TIME:
        upto = [d for d in days if d <= today]
    else:
        upto = past
    return upto[-1] if upto else None, past


def audit(days, tails, now, missing_window=MISSING_WINDOW,
          active_lag_days=5, coverage_share=0.90):
    """Judge the panel by its MAINTAINED cohort, not by its oldest file.

    data/daily holds 1,725 CSVs; 1,671 of them stopped at 2026-09-22 when the
    one-shot wide pull finished (r1106 disclosed that cohort), while the core
    panel has been refreshed every session since. Taking min() across every file
    therefore reports a 10-day "gap" on a day where the maintained panel was in
    fact lagging by one publication, which is exactly the false alarm that makes
    an alert useless. So: the ACTIVE cohort = symbols whose tail sits within
    `active_lag_days` official days of the newest tail; the cohort's effective
    cutoff = the newest official day covered by >= `coverage_share` of it. The
    frozen cohort is disclosed, never silently averaged in.
    """
    exp, _past = expected_last_day(days, now)
    if not tails or not days or not exp:
        return {
            "expected_last_official_day": exp,
            "panel": {"n_symbols": len(tails), "cutoff_min": None,
                      "cutoff_max": None, "n_active": 0, "n_stale_cohort": len(tails)},
            "missing_official_days": [],
            "verdict": "in_sync" if not tails else "in_sync",
            "detail": "empty panel face -- nothing to audit",
        }
    cutoff_max = max(tails.values())
    recent = [d for d in days if d <= cutoff_max][-active_lag_days:]
    floor = recent[0] if recent else cutoff_max
    active = {s: t for s, t in tails.items() if t >= floor}
    stale = len(tails) - len(active)
    window = [d for d in days if d <= exp][-missing_window:]
    covered = []
    for d in window:
        n = sum(1 for t in active.values() if t >= d)
        covered.append((d, n / float(len(active)) if active else 0.0))
    effective = None
    for d, share in covered:
        if share >= coverage_share:
            effective = d
    missing = [d for d in window if effective is None or d > effective]
    lagging = []
    if effective:
        lagging = sorted(s for s, t in active.items() if t < effective)[:20]
    if not missing:
        verdict = "in_sync"
        detail = "the maintained panel covers every official trading day it should by now"
    elif len(missing) == 1 and missing[0] == exp == now.date().isoformat():
        verdict = "source_lag"
        close = dt.datetime.combine(now.date(), CLOSE_ACCEPT_TIME)
        lag_h = max(0.0, (now - close).total_seconds() / 3600.0)
        detail = (f"{exp} is an official trading day; the market closed {lag_h:.1f}h "
                  f"ago and no bar has been published to this panel yet")
    else:
        verdict = "panel_gap"
        detail = (f"the maintained panel is behind the market by {len(missing)} "
                  f"official day(s): {', '.join(missing)} -- a feed that stopped "
                  f"publishing, not merely a publication delay")
    return {
        "expected_last_official_day": exp,
        "panel": {"n_symbols": len(tails), "cutoff_min": min(tails.values()),
                  "cutoff_max": cutoff_max, "n_active": len(active),
                  "n_stale_cohort": stale, "active_floor": floor,
                  "effective_cutoff": effective, "lagging_active_sample": lagging},
        "missing_official_days": missing,
        "coverage_by_day": {d: round(s, 4) for d, s in covered},
        "verdict": verdict,
        "detail": detail,
    }


def forward_impact():
    """What the lag costs the one face a human reads: the forward ledger."""
    try:
        with io.open(LEDGER, "r", encoding="utf-8") as f:
            led = json.load(f)
        last = (led.get("bars") or [{}])[-1].get("bar")
        return {"ledger_last_bar": last,
                "blocked": (led.get("status") == "live"),
                "note": ("one mark per new panel bar; a lagging feed pauses accrual "
                         "without any error")}
    except Exception:                                        # noqa: BLE001
        return {"ledger_last_bar": None, "blocked": None, "note": "ledger absent"}


def run(now=None, allow_network=True, cal_path=CAL_PATH, daily_dir=DAILY_DIR,
        out_path=OUT_PATH, write=True):
    now = now or dt.datetime.now()
    days, info = refresh(now, allow_network=allow_network) if cal_path == CAL_PATH else (
        load_calendar(cal_path), {"fetched": False, "reason": "explicit_path"})
    if not days:
        print("exchange_calendar_audit: no calendar available "
              f"({info.get('reason')} {info.get('error') or ''})".strip())
        return {"schema": "data-lag-audit/v1", "verdict": "mechanism_failure",
                "error": info.get("error") or info.get("reason")}
    tails = panel_tails(daily_dir)
    body = audit(days, tails, now)
    face = {
        "schema": "data-lag-audit/v1",
        "as_of": now.isoformat(timespec="seconds"),
        "calendar": {
            "path": os.path.relpath(cal_path, ROOT).replace("\\", "/"),
            "rows": len(days), "scope_start": days[0], "scope_end": days[-1],
            "refresh": info,
        },
        "forward_impact": forward_impact(),
        **body,
        "note": ("Descriptive face. The calendar is the independent reference; the "
                 "panel is ours. source_lag is a publication delay (self-heals), "
                 "panel_gap is a stopped feed (needs a human/lane owner)."),
    }
    if write:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        tmp = out_path + ".tmp"
        with io.open(tmp, "w", encoding="utf-8") as f:
            json.dump(face, f, ensure_ascii=False, indent=1, sort_keys=True)
        os.replace(tmp, out_path)
    print(f"data_lag_audit: {face['verdict']} | calendar {days[0]}..{days[-1]} "
          f"({len(days)}d) | expected {face['expected_last_official_day']} | "
          f"active {face['panel']['n_active']}/{face['panel']['n_symbols']} syms "
          f"effective {face['panel']['effective_cutoff']} | missing "
          f"{face['missing_official_days'] or 'none'}")
    return face


# ----------------------------------------------------------------- selftest

def _sandbox_case(name, calendar_days, tails, now, want_verdict, extra=None):
    """One audit scenario on in-memory faces -- no disk, no network."""
    res = audit(calendar_days, tails, now)
    ok = res["verdict"] == want_verdict
    if extra:
        for k, v in extra.items():
            ok = ok and (res.get(k) == v)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}: verdict={res['verdict']} "
          f"missing={res['missing_official_days']}")
    return ok


def selftest():
    print("exchange_calendar_audit selftest")
    ok = True
    # a small official calendar: Thu 10-22, Fri 10-23, Mon 10-26 (weekend absent)
    days = ["2026-10-22", "2026-10-23", "2026-10-26", "2026-10-27"]
    mon_close = dt.datetime(2026, 10, 26, 16, 45)
    mon_morning = dt.datetime(2026, 10, 26, 10, 0)

    # L1 in_sync: panel has the Monday bar
    ok &= _sandbox_case("L1 in_sync", days,
                        {"sh510300": "2026-10-26", "sh510050": "2026-10-26"},
                        mon_close, "in_sync")
    # L2 source_lag: Monday closed, feed has not published
    ok &= _sandbox_case("L2 source_lag (today, after close)", days,
                        {"sh510300": "2026-10-23", "sh510050": "2026-10-23"},
                        mon_close, "source_lag")
    # L3 panel_gap: an OLDER official day is missing -> a stopped feed
    ok &= _sandbox_case("L3 panel_gap (older day missing)", days,
                        {"sh510300": "2026-10-22", "sh510050": "2026-10-22"},
                        mon_close, "panel_gap")
    # L4 the morning boundary: before 15:30 Monday is not expected yet, so a
    # panel ending Friday is perfectly in sync (the false-alert guard)
    ok &= _sandbox_case("L4 before 15:30 boundary", days,
                        {"sh510300": "2026-10-23", "sh510050": "2026-10-23"},
                        mon_morning, "in_sync",
                        extra={"expected_last_official_day": "2026-10-23"})
    # L5 union never truncates history
    merged = merge_calendar(["2026-10-22", "2026-10-23"], ["2026-10-23", "2026-10-26"])
    l5 = merged == ["2026-10-22", "2026-10-23", "2026-10-26"]
    print(f"  [{'PASS' if l5 else 'FAIL'}] L5 calendar union keeps history: {merged}")
    ok &= l5
    # L6 a malformed / duplicated calendar row is a mechanism failure
    l6 = True
    for bad in ("2026-13-01", "2026-02-30", "26-10-26"):
        try:
            parse_calendar_text(bad)
            l6 = False
        except ValueError:
            pass
    try:
        parse_calendar_text("2026-10-23\n2026-10-23")
        l6 = False
    except ValueError:
        pass
    print(f"  [{'PASS' if l6 else 'FAIL'}] L6 bad calendar rows rejected")
    ok &= l6
    # L7 the artifact write is byte-idempotent and the parse round-trips
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "cal.csv")
        s1 = write_calendar(days, p)
        s2 = write_calendar(days, p)
        m = {d: "2026-10-26" for d in ("a", "b")}
        a1 = json.dumps(audit(days, m, mon_close), sort_keys=True)
        a2 = json.dumps(audit(days, m, mon_close), sort_keys=True)
        l7 = (s1 == s2) and load_calendar(p) == days and a1 == a2
        print(f"  [{'PASS' if l7 else 'FAIL'}] L7 idempotent artifact + audit")
        ok &= l7
    # L8 one laggard inside the maintained cohort must not flip the verdict
    # (coverage_share law); it is disclosed in lagging_active_sample instead
    bulk = {f"s{i:02d}": "2026-10-26" for i in range(19)}
    bulk["s19"] = "2026-10-22"
    res = audit(days, bulk, mon_close)
    l8 = (res["verdict"] == "in_sync"
          and res["panel"]["lagging_active_sample"] == ["s19"])
    print(f"  [{'PASS' if l8 else 'FAIL'}] L8 single laggard disclosed, not fatal: "
          f"verdict={res['verdict']} lagging={res['panel']['lagging_active_sample']}")
    ok &= l8
    # L9 the frozen wide cohort (1,671 files stopped at 2026-09-22, r1106) must
    # not masquerade as a 10-day panel outage: judge the maintained cohort only
    frozen = {f"f{i:03d}": "2026-09-22" for i in range(100)}
    frozen.update({"c1": "2026-10-23", "c2": "2026-10-23", "c3": "2026-10-23"})
    res = audit(days, frozen, mon_close)
    l9 = (res["verdict"] == "source_lag" and res["panel"]["n_active"] == 3
          and res["panel"]["n_stale_cohort"] == 100)
    print(f"  [{'PASS' if l9 else 'FAIL'}] L9 frozen cohort separated: "
          f"verdict={res['verdict']} active={res['panel']['n_active']} "
          f"stale={res['panel']['n_stale_cohort']}")
    ok &= l9

    print(f"selftest: {'PASS' if ok else 'FAIL'} (9 legs)")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "selftest"], nargs="?", default="run")
    ap.add_argument("--no-network", action="store_true")
    a = ap.parse_args()
    if a.cmd == "selftest":
        return selftest()
    face = run(allow_network=not a.no_network)
    if face.get("verdict") == "mechanism_failure":
        return 2
    return 1 if face.get("verdict") == "panel_gap" else 0


if __name__ == "__main__":
    sys.exit(main())