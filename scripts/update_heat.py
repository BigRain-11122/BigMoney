"""Daily popularity-ranking (人气榜) forward-collect snapshot - P-C v1.

O-20260923-1850 engineering lane (循环轮·工程部), HEAT_ATTENTION_SPEC §2C/§4.
Pure forward accumulation: the guba rank list is a LIVE rolling ranking with
no retrievable full history -> per spec §1 "前向采集" row, we snapshot it once
per day and never fabricate backtest history. Factor use joins by as_of date
with strict availability lag (no look-ahead) at the factor-build layer.

Source (bm-b r39 audit, DIGEST-20260923-heat-source-audit): EM emappdata
getAllCurrentList - the same endpoint akshare's stock_hot_rank_em wraps
(pageSize=100 = public 人气榜 top-100; pageSize>100 returns 0 rows, probed
2026-09-23). We take ONLY this one request: the akshare wrapper's second
call enriches with push2.eastmoney.com quotes, which (a) is the subdomain
bm-b observed IP-blocked and (b) duplicates prices we already have in bars.

Safety (update_daily / update_lhb paradigm):
  - direct route only: urllib + ProxyHandler({}) - Clash hijacks EM
    domains (J13 / bm-b r39 坑1); requests/env/registry proxies bypassed
  - window guard: weekday + >=15:30 local (post-close snapshot aligns with
    the daily bar; intraday snapshots would be a different dataset)
  - idempotent by date: one snapshot file per day, exists -> no-op exit 0
  - min re-attempt interval: last_attempt recorded in the status mirror
    BEFORE the network call (crash mid-fetch still throttles next round;
    EM datacenter citizenship - 1 request/day nominal)
  - atomic write: staged .tmp then os.replace
  - honest failure: fetch/validation fail -> no write, exit 2 verbatim
  - `selftest` subcommand: offline guard tests, zero network, tempdir only
"""
import datetime as dt
import json
import os
import re
import sys
import tempfile
import time
import urllib.request

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEAT_DIR = os.path.join(ROOT, "data", "heat", "popularity")
STATUS = os.path.join(ROOT, "results", "heat_update_status.json")
sys.path.insert(0, ROOT)
from config.lane_io import machine_id, write_lane, lane_host# noqa: E402

HEAT_LANE_HOST = lane_host("update_heat", "bm-a")   # R19 wiring / R31 lane-ownership precedent:
#   heat snapshots derive from the HOST's machine-local data/heat face
#   (gitignored) -- non-host runs must not author a lane (ts新 != 数据权威新).

_ACTIVE_TAKEOVER = None    # set by main() when a declared stale takeover
#   passed the gate; save_status stamps it into the tracked envelope so a
#   reader can tell WHICH machine-local face holds the rows (T25, r1161).

CLOSE_ACCEPT_TIME = dt.time(15, 30)   # post-close snapshot convention
SESSION_OPEN_GUARD = dt.time(9, 15)   # call auction: the ranking can move from here
MIN_ATTEMPT_INTERVAL = 30 * 60        # min seconds between network attempts
ENDPOINT = "https://emappdata.eastmoney.com/stockrank/getAllCurrentList"
PAGE_SIZE = 100                      # public top-100 (endpoint cap, probed)
MIN_ROWS = 50                        # validation floor (expect exactly 100)
SC_RE = re.compile(r"^(SH|SZ)(\d{6})$")
RETRY_SLEEP = 3                      # one retry, emappdata flakiness (r39)


def _takeover_gate(owner):
    """R31 lane guard + declared stale takeover (T25, r1161).

    The heat rows live in a gitignored MACHINE-LOCAL dir, so a takeover cannot
    hand them to the owner's disk. What it can do is keep forward accumulation
    alive on the taker and SAY SO on the tracked status envelope -- otherwise
    the takeover produces "a copy nobody reads", which is the pit T25 names.
    A non-owner without a valid declaration stays a stdout-only no-op (R31).
    The decision itself is imported from update_etf_daily, never re-implemented
    (r1100 single-source law).
    """
    if owner == HEAT_LANE_HOST:
        return None
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from update_etf_daily import (TAKEOVER_STALE_MIN, _owner_stale_min,
                                  takeover_decision)
    stale = _owner_stale_min(HEAT_LANE_HOST)
    ok, why = takeover_decision("--takeover" in sys.argv[1:], stale)
    if not ok:
        print(f"no-op: heat lane host {HEAT_LANE_HOST} authority, this "
              f"machine ({owner or 'unknown-id'}) stdout-only "
              f"(R31 lane-guard); takeover refused: {why}", flush=True)
        return None
    reason = (f"owner {HEAT_LANE_HOST} heartbeat silent {stale/60:.1f}h "
              f">= {TAKEOVER_STALE_MIN}min")
    print(f"TAKEOVER: declared stale takeover of {HEAT_LANE_HOST}'s heat lane "
          f"by {owner} -- {reason} | rows land in this machine's data/heat "
          f"(gitignored, machine-local) and the status envelope now names "
          f"{owner} as the data face", flush=True)
    return {"owner": HEAT_LANE_HOST, "by": owner, "reason": reason,
            "ts": dt.datetime.now().isoformat(timespec="seconds")}


def save_status(payload):
    os.makedirs(os.path.dirname(STATUS), exist_ok=True)
    payload["updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
    # WHO and WHAT (r1156): the envelope is committed by whichever machine ran
    # the leg, and every machine keeps its own gitignored copy of the snapshots.
    # Without these two fields a reader cannot tell "the lane is dead" from
    # "this is a stale copy of a lane that is alive on its host" -- which is
    # exactly how seven missing days went unnoticed (data_lane_freshness).
    payload["machine"] = machine_id()
    payload["lane_host"] = HEAT_LANE_HOST
    # Authority block (T25, r1161): the data face is machine-local and a
    # takeover CANNOT move the rows -- it can only re-declare the writer.
    # Without this block a declared takeover leaves a copy no reader can
    # attribute, so the reader is told exactly whose disk holds the rows.
    took = _ACTIVE_TAKEOVER or {}
    payload["authority"] = {
        "lane_owner": HEAT_LANE_HOST,
        "writer_machine": machine_id(),
        "data_face_machine": machine_id(),
        "declared_takeover": bool(_ACTIVE_TAKEOVER),
        "took_over_by": took.get("by"),
        "took_over_at": took.get("ts"),
        "reason": took.get("reason"),
    }
    payload["latest_snapshot"] = latest_snapshot()
    payload["snapshots"] = count_snapshots()
    with open(STATUS, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, default=str)
    # Lane dual-track (D-20260928-03 batch-2), host-guarded: only the
    # R31 host authors the heat lane; fail-soft never breaks the run.
    # A declared takeover IS the authority while it holds the rows.
    if machine_id() == HEAT_LANE_HOST or _ACTIVE_TAKEOVER is not None:
        write_lane("heat_update_status", payload)


def latest_snapshot():
    """Newest as_of on disk, so another machine can audit the lane."""
    if not os.path.isdir(HEAT_DIR):
        return None
    days = []
    for name in os.listdir(HEAT_DIR):
        if len(name) == 13 and name.endswith(".json") and name[:8].isdigit():
            n = name[:8]
            days.append(f"{n[:4]}-{n[4:6]}-{n[6:]}")
    return max(days) if days else None


def load_status():
    if os.path.exists(STATUS):
        try:
            with open(STATUS, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def trading_sessions():
    """Official trading days as datetimes at the close, newest last.

    Imported from the calendar audit rather than re-derived (r1290 class). If
    the calendar is missing the lane keeps working on a weekday approximation
    and says so in the reason string -- it never silently invents a holiday.
    """
    try:
        from scripts.exchange_calendar_audit import load_calendar
        days = load_calendar()
        return [dt.datetime.combine(dt.date.fromisoformat(d), CLOSE_ACCEPT_TIME)
                for d in days], True
    except Exception:
        return [], False


def target_session(now, sessions):
    """Which session's close a snapshot taken at `now` would represent.

    WHY (r1156): the gate compared `now` with TODAY's 15:30 and answered
    "before 15:30 -> no-op" for every round that ran after midnight, even when
    the previous session had no snapshot at all. This host's rounds run mostly
    at night, so the lane lost seven consecutive trading days (2026-10-21..29)
    while the endpoint stayed alive -- measured: 100/100 rows fetched at 02:13.
    The rank list is a live ROLLING list: it does not move between a close and
    the next 09:15 call auction. A snapshot taken in that carry window therefore
    IS the last session's close state; the file is labelled with the session and
    carries `fetched_at`, so a reader can tell when it was actually taken.

    Returns (session_date_or_None, allowed, reason). allowed=False means a later
    session has likely opened and the ranking has moved: the stale day stays
    missing rather than being filled with the wrong close.
    """
    if sessions:
        closed = [s for s in sessions if s <= now]
        if not closed:
            return None, False, "no session has closed yet"
        target = closed[-1]
        nxt = [s for s in sessions if s > target]
        if nxt:
            reopen = dt.datetime.combine(nxt[0].date(), SESSION_OPEN_GUARD)
            if now >= reopen:
                return (target.date(), False,
                        f"{target.date()} close is stale: the {reopen.date()} "
                        f"session opened at {SESSION_OPEN_GUARD} and the live "
                        "ranking has moved on (a missed day stays missing)")
        return target.date(), True, "post-close carry: the live ranking has not moved"

    # no calendar: weekday approximation, disclosed in the reason
    day = now.date()
    close_today = dt.datetime.combine(day, CLOSE_ACCEPT_TIME)
    if day.weekday() < 5 and now >= close_today:
        return day, True, "post-close carry (no calendar: weekday approximation)"
    back = day - dt.timedelta(days=1)
    while back.weekday() >= 5:
        back -= dt.timedelta(days=1)
    if now < dt.datetime.combine(day, SESSION_OPEN_GUARD) or day.weekday() >= 5:
        return back, True, "post-close carry (no calendar: weekday approximation)"
    return back, False, (f"{back} is stale: the {day} session opened at "
                         f"{SESSION_OPEN_GUARD} (no calendar: weekday "
                         "approximation, a missed day stays missing)")


def session_gate(now, target, target_file, last_attempt, allowed, basis):
    """(should_fetch, reason) for a resolved target session."""
    if not allowed:
        return False, f"no-op: {basis}"
    if target is None:
        return False, f"no-op: {basis}"
    if os.path.exists(target_file):
        return False, f"no-op: snapshot for {target} already collected"
    if (last_attempt is not None
            and (now - last_attempt).total_seconds() < MIN_ATTEMPT_INTERVAL):
        return False, (f"no-op: <{MIN_ATTEMPT_INTERVAL // 60}min since last "
                       "fetch attempt (min-interval guard)")
    return True, f"fetch: {target} snapshot missing ({basis})"


def fetch_rank_rows():
    """One direct-route POST -> list of raw {sc, rk, ...} dicts."""
    payload = json.dumps({"appId": "appId01",
                          "globalId": "786e4c21-70dc-435a-93bb-38",
                          "marketType": "", "pageNo": 1,
                          "pageSize": PAGE_SIZE}).encode()
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    last_ex = None
    for _ in range(2):  # one retry; emappdata route observed flaky (r39)
        try:
            req = urllib.request.Request(
                ENDPOINT, data=payload,
                headers={"Content-Type": "application/json",
                         "User-Agent": "Mozilla/5.0"})
            with opener.open(req, timeout=12) as r:
                data = json.loads(r.read().decode("utf-8"))
            rows = data.get("data") or []
            if rows:
                return rows, None
            last_ex = RuntimeError("endpoint returned 0 rows "
                                   f"(payload keys={sorted(data.keys())})")
        except Exception as ex:  # noqa: BLE001
            last_ex = ex
        time.sleep(RETRY_SLEEP)
    return [], last_ex


def canonical_rows(raw_rows):
    """Validate + project to the frozen schema. Any schema drift raises."""
    out = []
    seen = set()
    for row in raw_rows:
        m = SC_RE.match(str(row.get("sc", "")))
        if not m:
            raise ValueError(f"bad sc field: {row.get('sc')!r}")
        rank = int(row["rk"])
        if not (1 <= rank <= 1000):
            raise ValueError(f"rank out of range: {rank}")
        code = m.group(2)
        if code in seen:
            raise ValueError(f"duplicate code in list: {code}")
        seen.add(code)
        out.append({"code": code, "market": m.group(1), "rank": rank,
                    "rc": row.get("rc"), "hisrc": row.get("hisRc"),
                    "raw_sc": row["sc"]})
    ranks = sorted(r["rank"] for r in out)
    if ranks != list(range(1, len(out) + 1)):
        raise ValueError(f"ranks not a 1..N permutation: {ranks[:5]}...")
    return out


def write_snapshot(path, rows, now, session=None, basis=None):
    """Write one day file. `as_of` is the SESSION the ranking represents;
    `fetched_at` is when it was actually taken (they differ in the carry
    window, and a reader is entitled to see both)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    doc = {"as_of": str(session or now.date()),
           "fetched_at": now.strftime("%Y-%m-%d %H:%M:%S"),
           "source": "emappdata getAllCurrentList (direct)",
           "n_rows": len(rows), "rows": rows}
    if session is not None and session != now.date():
        doc["label_basis"] = (basis or "") + " -- as_of is the session whose "
        doc["label_basis"] += "close this ranking still is, not the fetch date"
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def main():
# R31 host-guard (r378 obs-window catch #5): heat snapshots and their
    # status face derive from the HOST's machine-local data/heat
    # directory -- a non-host run must not fetch, snapshot, or advance
    # the shared envelope (ts新!= 数据权威新; an envelope-only no-op
    # write from a non-host advanced shared freshness past the
    # authoritative host lane and forced reconcile drift, live-fire
    # bm-c r130 vs bm-a r378 same-window). Non-host = stdout-only
    # honest no-op (update_astock_daily precedent), EXCEPT a declared
    # stale takeover (T25, r1161): explicit --takeover AND an owner
    # heartbeat silent >= TAKEOVER_STALE_MIN, in which case this machine
    # becomes the declared authority and says so on the envelope.
    global _ACTIVE_TAKEOVER
    _ACTIVE_TAKEOVER = _takeover_gate(machine_id())
    if machine_id() != HEAT_LANE_HOST and _ACTIVE_TAKEOVER is None:
        return 0
    now = pd.Timestamp.now()
    prev = load_status()
    last_attempt = prev.get("last_attempt")
    if isinstance(last_attempt, str):
        try:
            last_attempt = pd.Timestamp(last_attempt)
        except Exception:
            last_attempt = None

    sessions, from_calendar = trading_sessions()
    target, allowed, basis = target_session(now.to_pydatetime(), sessions)
    if not from_calendar:
        basis += " [no data/exchange_calendar.csv: weekday approximation]"
    target_file = os.path.join(
        HEAT_DIR, f"{(target or now.date()):%Y%m%d}.json")

    should, reason = session_gate(now, target, target_file, last_attempt,
                                  allowed, basis)
    print(reason, flush=True)
    if not should:
        save_status({"verdict": reason,
                     "target_session": str(target) if target else None,
                     "snapshots": count_snapshots(),
                     "last_attempt": prev.get("last_attempt")})
        return 0

    # record the attempt BEFORE the network call: a crash mid-fetch must
    # still throttle the next round (EM datacenter citizenship)
    save_status({"verdict": "fetching", "snapshots": count_snapshots(),
                 "last_attempt": str(now)})

    raw, ex = fetch_rank_rows()
    if ex is not None:
        save_status({"verdict": f"fetch_fail: {type(ex).__name__}: "
                                f"{str(ex)[:160]}",
                     "snapshots": count_snapshots(),
                     "last_attempt": str(now)})
        print(f"FETCH FAIL {type(ex).__name__}: {str(ex)[:160]}", flush=True)
        return 2
    try:
        rows = canonical_rows(raw)
        if len(rows) < MIN_ROWS:
            raise ValueError(f"only {len(rows)} rows < floor {MIN_ROWS}")
    except Exception as ve:  # noqa: BLE001
        save_status({"verdict": f"validation_fail: {str(ve)[:160]}",
                     "snapshots": count_snapshots(),
                     "last_attempt": str(now)})
        print(f"VALIDATION FAIL: {str(ve)[:160]}", flush=True)
        return 2

    write_snapshot(target_file, rows, now.to_pydatetime(), session=target,
                   basis=basis)
    save_status({"verdict": f"snapshot {target} landed",
                 "target_session": str(target),
                 "label_basis": basis,
                 "snapshots": count_snapshots(),
                 "n_rows": len(rows), "last_attempt": str(now)})
    print(f"snapshot landed: as_of={target} fetched_at={now:%Y-%m-%d %H:%M} "
          f"n_rows={len(rows)} (total snapshots={count_snapshots()})",
          flush=True)
    return 0


def count_snapshots():
    if not os.path.isdir(HEAT_DIR):
        return 0
    return len([f for f in os.listdir(HEAT_DIR) if f.endswith(".json")])


def selftest():
    """Offline guard tests: session carry window, idempotence, throttle,
    schema validation, atomic write. Zero network; file ops in a tempdir."""
    ts = pd.Timestamp

    # synthetic calendar: Mon 10-19 .. Fri 10-23, then Mon 10-26 .. Thu 10-29
    sess = [dt.datetime.combine(dt.date(2026, 10, d), CLOSE_ACCEPT_TIME)
            for d in (19, 20, 21, 22, 23, 26, 27, 28, 29)]

    carry_cases = [
        # name, now, want target, want allowed
        ("Wed 15:00 -> Tue's close is already stale (09:15 opened)", "2026-10-21 15:00",
         dt.date(2026, 10, 20), False),
        ("Wed 15:31 -> Wed (today's close)", "2026-10-21 15:31",
         dt.date(2026, 10, 21), True),
        ("Thu 02:13 -> Wed, carry still current", "2026-10-22 02:13",
         dt.date(2026, 10, 21), True),
        ("Thu 09:10 -> Wed, before the auction", "2026-10-22 09:10",
         dt.date(2026, 10, 21), True),
        ("Thu 09:20 -> Wed is stale (auction opened)", "2026-10-22 09:20",
         dt.date(2026, 10, 21), False),
        ("Sat 10:00 -> Fri, weekend carry", "2026-10-24 10:00",
         dt.date(2026, 10, 23), True),
        ("Mon 09:20 -> Fri is stale", "2026-10-26 09:20",
         dt.date(2026, 10, 23), False),
        ("Mon 20:00 -> Mon", "2026-10-26 20:00",
         dt.date(2026, 10, 26), True),
        ("before the first close -> nothing", "2026-10-01 10:00", None, False),
    ]
    for name, now_s, want_t, want_ok in carry_cases:
        tgt, ok, basis = target_session(ts(now_s).to_pydatetime(), sess)
        assert (tgt, ok) == (want_t, want_ok), f"{name}: {tgt} {ok} {basis}"
        print(f"[PASS] target_session {name}", flush=True)

    # a weekday approximation is used (and disclosed) when the calendar is absent
    tgt, ok, basis = target_session(dt.datetime(2026, 10, 22, 2, 13), [])
    assert (tgt, ok) == (dt.date(2026, 10, 21), True) and "approximation" in basis
    print("[PASS] target_session falls back to weekdays, says so", flush=True)

    # gate: allowed/blocked, idempotence, throttle
    with tempfile.TemporaryDirectory() as td:
        tf = os.path.join(td, "x.json")
        should, reason = session_gate(ts("2026-10-22 15:00"),
                                      dt.date(2026, 10, 21), tf, None,
                                      True, "post-close carry")
        assert should and "2026-10-21" in reason, reason
        open(tf, "w").close()
        should, reason = session_gate(ts("2026-10-22 15:00"),
                                      dt.date(2026, 10, 21), tf, None, True, "x")
        assert not should and "already collected" in reason, reason
        print("[PASS] session_gate fetches a missing session, then no-ops",
              flush=True)

    with tempfile.TemporaryDirectory() as td:
        tf = os.path.join(td, "x.json")
        for la_s, want in (("2026-10-21 19:50", False), ("2026-10-21 10:00", True)):
            should, reason = session_gate(ts("2026-10-21 20:00"),
                                          dt.date(2026, 10, 21), tf, ts(la_s),
                                          True, "x")
            assert should == want, f"throttle {la_s}: {reason}"
        print("[PASS] session_gate keeps the 30min min-interval", flush=True)

    with tempfile.TemporaryDirectory() as td:
        should, reason = session_gate(ts("2026-10-22 09:20"),
                                      dt.date(2026, 10, 21),
                                      os.path.join(td, "x.json"), None, False,
                                      "2026-10-21 close is stale: the "
                                      "2026-10-22 session opened")
        assert not should and "stale" in reason, reason
        print("[PASS] session_gate refuses a stale session (never fills a "
              "missed day with the wrong close)", flush=True)

    good = [{"sc": "SH600418", "rk": 1, "rc": 0, "hisRc": 7},
            {"sc": "SZ000001", "rk": 2, "rc": -1, "hisRc": 3}]
    rows = canonical_rows(good)
    assert rows[0]["code"] == "600418" and rows[0]["rank"] == 1
    assert rows[1]["market"] == "SZ" and rows[1]["hisrc"] == 3
    print("[PASS] canonical_rows projection", flush=True)

    bads = [
        ("bad sc", [{"sc": "XX12345", "rk": 1}]),
        ("rank out of range", [{"sc": "SH600418", "rk": 0}]),
        ("duplicate code", [{"sc": "SH600418", "rk": 1},
                            {"sc": "SH600418", "rk": 2}]),
        ("rank gap", [{"sc": "SH600418", "rk": 1},
                      {"sc": "SZ000001", "rk": 3}]),
    ]
    for name, raw in bads:
        try:
            canonical_rows(raw)
            raise AssertionError(f"{name}: not rejected")
        except (ValueError, KeyError):
            print(f"[PASS] canonical_rows rejects {name}", flush=True)

    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "snap.json")
        write_snapshot(p, canonical_rows(good), dt.datetime(2026, 9, 23, 20, 1))
        with open(p, encoding="utf-8") as f:
            doc = json.load(f)
        assert doc["as_of"] == "2026-09-23" and doc["n_rows"] == 2
        assert doc["rows"][1]["code"] == "000001"
        assert not os.path.exists(p + ".tmp")
        assert "label_basis" not in doc, "same-day label needs no explanation"
        # carry-window file: as_of is the session, fetched_at is the truth
        p2 = os.path.join(td, "carry.json")
        write_snapshot(p2, canonical_rows(good), dt.datetime(2026, 10, 22, 2, 13),
                       session=dt.date(2026, 10, 21), basis="post-close carry")
        doc2 = json.load(open(p2, encoding="utf-8"))
        assert (doc2["as_of"] == "2026-10-21"
                and doc2["fetched_at"].startswith("2026-10-22")
                and "post-close carry" in doc2["label_basis"]), doc2
        print("[PASS] write_snapshot atomic + labels the session it represents",
              flush=True)

    # T25 (r1161): the authority block is what a takeover's reader depends on.
    saved_status = globals()["STATUS"]
    saved_take = globals()["_ACTIVE_TAKEOVER"]
    saved_lane = globals()["write_lane"]
    lanes_written = []
    with tempfile.TemporaryDirectory() as td:
        globals()["STATUS"] = os.path.join(td, "st.json")
        globals()["write_lane"] = lambda face, payload: lanes_written.append(face)
        try:
            globals()["_ACTIVE_TAKEOVER"] = None
            save_status({"verdict": "unit-plain"})
            with open(globals()["STATUS"], encoding="utf-8") as f:
                a = json.load(f)["authority"]
            assert a["declared_takeover"] is False and a["took_over_by"] is None
            assert a["data_face_machine"] == machine_id(), a
            assert a["lane_owner"] == HEAT_LANE_HOST, a
            plain_lane = list(lanes_written)
            globals()["_ACTIVE_TAKEOVER"] = {"by": "bm-x", "ts": "unit",
                                             "reason": "unit",
                                             "owner": HEAT_LANE_HOST}
            save_status({"verdict": "unit-takeover"})
            with open(globals()["STATUS"], encoding="utf-8") as f:
                a2 = json.load(f)["authority"]
            assert a2["declared_takeover"] is True, a2
            assert a2["took_over_by"] == "bm-x", a2
            assert a2["data_face_machine"] == machine_id(), a2
            # the declared takeover MUST author the shared lane, or its rows
            # are exactly the "copy nobody reads" this card exists to prevent
            assert lanes_written and lanes_written[-1] == "heat_update_status"
            assert len(plain_lane) == (1 if machine_id() == HEAT_LANE_HOST else 0)
            print("[PASS] authority block names who holds the machine-local rows "
                  "(plain run vs declared takeover), and only the authority "
                  "authors the shared lane", flush=True)
        finally:
            globals()["STATUS"] = saved_status
            globals()["_ACTIVE_TAKEOVER"] = saved_take
            globals()["write_lane"] = saved_lane

    print("selftest: all guard cases PASS", flush=True)
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    sys.exit(main())
