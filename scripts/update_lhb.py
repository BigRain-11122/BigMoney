"""LHB event history incremental refresh (P-A family pointer 4, claim
MSG-20260923-2045). Pure data engineering: zero IC, zero engine runs,
ledger N untouched.

Source-consistent with the original archive: ak.stock_lhb_detail_em
(EastMoney), same schema by construction. The original pipeline
(Money02/lhb_download.py) is quarterly-chunked and idempotent; this
refresh keeps that mechanism intact: re-fetch every quarter from the
cutoff's quarter through the expected-disclosure quarter (superset
overwrite of one quarter-pure chunk per fetched quarter), then rebuild
lhb_detail.parquet exactly the way the original script does (concat all
chunks). Appending to the parquet without the chunks would
desynchronize the two and a future re-run of the original downloader
would silently drop the appended rows.

Safety (update_daily paradigm):
  - overlap check: re-fetched rows with date <= cutoff must match the
    stored rows for the cutoff date (row count + net-buy sum, tol 1e-6);
    mismatch = source restated history -> write NOTHING, flag, exit 3
  - quarter-boundary fetch window (r835 bm-c deadlock fix): the fetch
    used to re-fetch ONLY the cutoff's quarter, which deadlocks at
    quarter turnover -- cutoff froze at 2026-09-30 (Q3 end) while the
    gate expected disclosures to 2026-10-09; the Q4 window (10-08 and
    10-09, 164 rows live in the EM source per probe
    results/_r835bmc_lhb_q4_probe.json) was unreachable by construction
    and the gate refired every 30min for nothing. Fix: fetch EVERY
    quarter from the cutoff quarter through the quarter containing the
    expected disclosure date; rows are split back per quarter so each
    chunk file stays quarter-pure (a future original-downloader re-run
    must not silently drop appended rows).
  - late-disclosure superset acceptance (r280 bm-c deadlock fix): the
    EM source legitimately COMPLETES past-date rows for days after the
    event -- late LHB disclosures keep landing past-date rows (25 rows
    joined the 2026-09-28 window hours after first fetch) and the
    shangbang_hou_1/2/5/10ri forward-return columns get filled in as
    later closes happen (probe 2026-09-30: 42/42 common rows differ on
    上榜后1日/2日 with netbuy byte-identical). The strict equality check
    above misread that benign completion as restatement and deadlocked
    the panel (13 consecutive rc3 observations, cutoff frozen at
    09-28 while 09-29 disclosures waited). Fix: when the strict check
    fails but every stored cutoff-date row still exists in the fetched
    set with identical per-key netbuy (sorted-list identity, NaN-aware)
    = PURE ADDITION -> write proceeds (superset overwrite is the design
    anyway). Any mutation/removal of a stored row stays a hard exit-3.
  - idempotent: no events beyond cutoff -> honest no-op exit 0
  - fetch failure -> no write, exit 2 (retry next run)
Write-domain (claim-scoped): the current-quarter chunk file,
lhb_detail.parquet, results/lhb_update_status.json. Nothing else.

S6 wiring guards (bm-a loop round 18, delegated by MSG-2045 item 4):
called from the iteration loop right after update_daily on a 10-minute
schedule, so the fetch gates must make polling safe for the throttled
EM datacenter (bm-b r39 finding + seat-pull 300s backoff evidence):
  - publish-window/cutoff gate: no network unless the stored cutoff is
    behind the latest POSSIBLE disclosure date (weekday evening window,
    weekends roll back to Friday)
  - min re-attempt interval: last_attempt recorded in the status mirror
    BEFORE the network call (crash mid-fetch still throttles next round)
  - `selftest` subcommand: offline guard tests, zero network zero writes

T-04 F2 robustness batch (bm-c, AUDIT-20260923 P0-6/P1-7):
  - store-absent guard: nodes that sparse-clone without Money02 (HANDOVER
    s3, bm-c profile) exit 2 honestly instead of crashing on read_parquet;
    store backfill stays a GM-lane decision, never auto-fetched
  - holiday awareness: expected-disclosure now intersects the SSE trading
    calendar derived from local data/daily core bars (maintained by
    update_daily on every node, zero new deps, zero network). Mid-week
    holidays no longer trigger pointless fetches. Documented caveat: if
    sina publishes today's EOD bar late (09-23 precedent: ~20:26), the
    in-window branch rolls back one day and the fetch happens a few
    hours later the same evening -- self-healing, no correctness loss.
    No local daily data at all (fresh node) -> weekday fallback (old
    behavior, harmless direction: extra throttled fetch attempts)
  - last_attempt carried on ALL early-return paths (overlap-mismatch
    previously dropped it -> 30-min throttle bypassed, hammering EM)
  - chunk/parquet writes atomic (.tmp + rowcount verify + os.replace)
  - corrupted status file logged to stderr instead of silent {} reset
"""
import json
import os
import sys
import time

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LHB_DIR = os.path.join(ROOT, "Money02", "data", "lhb")
PARQUET = os.path.join(LHB_DIR, "lhb_detail.parquet")
CHUNKS = os.path.join(LHB_DIR, "chunks")
STATUS = os.path.join(ROOT, "results", "lhb_update_status.json")
sys.path.insert(0, ROOT)
from config.lane_io import write_lane  # noqa: E402 -- after ROOT pin
DAILY_DIR = os.path.join(ROOT, "data", "daily")
CORE_CALENDAR_FILE = os.path.join(DAILY_DIR, "510300.csv")
TOL = 1e-6
PUBLISH_HOUR = 17                # LHB disclosures land ~17-19h local
MIN_ATTEMPT_INTERVAL = 30 * 60  # min seconds between network attempts


def save_status(payload):
    os.makedirs(os.path.dirname(STATUS), exist_ok=True)
    payload["updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(STATUS, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, default=str)
    # Lane dual-track (D-20260928-03 batch-2): own-machine lane mirror,
    # fail-soft never breaks the run.
    write_lane("lhb_update_status", payload)


def load_status():
    if os.path.exists(STATUS):
        try:
            with open(STATUS, encoding="utf-8") as f:
                return json.load(f)
        except Exception as ex:
            print(f"WARN: lhb status file unreadable "
                  f"({type(ex).__name__}: {str(ex)[:80]}); "
                  "starting from empty status", file=sys.stderr, flush=True)
            return {}
    return {}


# ---------------------------------------------------------------- calendar
_DATES_CACHE = "unset"


def _load_local_dates():
    """SSE trading-day history from local data/daily core bars (510300 =
    most liquid core ETF, trades every market day; updated by update_daily
    each round on every node). Returns sorted list of Timestamps or None
    when no local daily data exists. Module-level cache: single-shot CLI
    plus repeated selftest calls must not re-read the CSV each time."""
    global _DATES_CACHE
    if _DATES_CACHE != "unset":
        return _DATES_CACHE
    path = CORE_CALENDAR_FILE
    if not os.path.exists(path):
        import glob as _glob
        cands = sorted(_glob.glob(os.path.join(DAILY_DIR, "*.csv")))
        path = cands[0] if cands else None
    dates = None
    if path:
        try:
            df = pd.read_csv(path, usecols=[0])
            ds = pd.to_datetime(df[df.columns[0]], errors="coerce")
            # r806 (bm-b): Series.normalize() does not exist (AttributeError,
            # swallowed by the except below) -> calendar was ALWAYS None ->
            # R18 holiday awareness silently dead since landing; weekday
            # fallback fetched during golden week. .dt.normalize restores
            # the documented intent (probe _r806bmb_lhb_gate_probe.json).
            ds = sorted(ds.dropna().dt.normalize().unique())
            if len(ds):
                dates = [pd.Timestamp(d) for d in ds]
        except Exception:
            dates = None
    _DATES_CACHE = dates
    return dates


def expected_disclosure_date(now, dates=None):
    """LHB trading-day events disclose in the evening (~17h+). Latest
    POSSIBLE disclosure date given `now`:
      - in publish window with today present in the local trading
        calendar (today's EOD bar already landed) -> today
      - otherwise the most recent local trading day strictly before
        today (handles weekends AND mid-week holidays precisely; a
        same-evening sina publication delay just defers the fetch a few
        hours, self-healing)
      - no local calendar at all -> weekday approximation (old behavior)
    """
    if dates is None:
        dates = _load_local_dates()
    today = now.normalize()
    if dates is None:
        if now.hour >= PUBLISH_HOUR and today.weekday() < 5:
            return today
        d = today - pd.Timedelta(days=1)
        while d.weekday() >= 5:
            d -= pd.Timedelta(days=1)
        return d
    if now.hour >= PUBLISH_HOUR and today in dates:
        return today
    prior = [d for d in dates if d < today]
    if prior:
        return prior[-1]
    # local history does not reach back before today (degenerate):
    # weekday fallback rather than crash
    d = today - pd.Timedelta(days=1)
    while d.weekday() >= 5:
        d -= pd.Timedelta(days=1)
    return d


def fetch_gate(cutoff, now, last_attempt, dates=None):
    """(should_fetch, reason). Publish-window/cutoff staleness first, then
    min re-attempt interval (EM datacenter throttle citizenship)."""
    expected = expected_disclosure_date(now, dates)
    if cutoff >= expected:
        return False, (f"no-op: cutoff {cutoff.date()} covers latest "
                       f"disclosure window ({expected.date()})")
    if (last_attempt is not None
            and (now - last_attempt).total_seconds() < MIN_ATTEMPT_INTERVAL):
        return False, (f"no-op: <{MIN_ATTEMPT_INTERVAL // 60}min since last "
                       "fetch attempt (min-interval guard)")
    return True, (f"fetch: cutoff {cutoff.date()} behind expected "
                 f"disclosure {expected.date()}")


def quarters_to_fetch(cutoff, expected):
    """r835 quarter-boundary fix: quarters from the cutoff's quarter through
    the expected disclosure date's quarter (inclusive). Same-quarter case
    collapses to a single entry (pre-r835 behavior). Crossing cases walk
    forward one quarter at a time; a multi-year gap still yields a finite
    list because the gate only fires when the panel is stale, not absent."""
    q0 = pd.Period(cutoff, freq="Q")
    q1 = pd.Period(expected, freq="Q")
    out = []
    qi = q0
    while qi <= q1:
        out.append(qi)
        qi = qi + 1
    return out


def atomic_parquet_write(df, path):
    """.tmp + rowcount verify + os.replace: a crash mid-write must never
    leave a truncated store that the next rebuild silently ingests."""
    tmp = path + ".tmp"
    df.to_parquet(tmp, index=False)
    back = pd.read_parquet(tmp)
    if len(back) != len(df):
        raise RuntimeError(f"atomic write verify failed for {path}: "
                           f"wrote {len(df)} rows, tmp holds {len(back)}")
    os.replace(tmp, path)


def store_state(parquet_path, chunks_dir):
    """(present, reason). Sparse-clone nodes (HANDOVER s3, bm-c profile)
    must skip honestly instead of crashing on read_parquet."""
    if not os.path.exists(parquet_path):
        return False, "lhb_detail.parquet missing (sparse-clone " \
                      "design exclusion, HANDOVER s3)"
    if not os.path.isdir(chunks_dir):
        return False, "chunks dir missing (cannot rebuild parquet)"
    return True, "ok"


def _nan_sk(v):
    # deterministic sort key: NaN sorts first, never compares as equal
    nan = v != v
    return (bool(nan), 0.0 if nan else float(v))


def is_pure_addition(old_day, new_day):
    """r280 deadlock fix: True when every stored cutoff-date row still
    exists in the fetched set with identical per-key 龙虎榜净买额
    (sorted per-key lists, NaN==NaN) -- i.e. the source only ADDED
    late-disclosure rows. Any stored row missing, count-changed or
    netbuy-mutated -> False (true restatement, keep blocking)."""
    if len(old_day) == 0:
        return True
    if len(new_day) == 0:
        return False

    def _keyed(frame):
        keyed = {}
        keys = list(zip(frame["代码"].astype(str),
                        pd.to_datetime(frame["上榜日"]).dt.strftime("%Y-%m-%d"),
                        frame["上榜原因"].astype(str)))
        nb = pd.to_numeric(frame["龙虎榜净买额"], errors="coerce").tolist()
        for i, kk in enumerate(keys):
            keyed.setdefault(kk, []).append(nb[i])
        return keyed

    om, nm = _keyed(old_day), _keyed(new_day)
    for kk, vals in om.items():
        if kk not in nm or len(nm[kk]) != len(vals):
            return False
        for a, b in zip(sorted(vals, key=_nan_sk), sorted(nm[kk], key=_nan_sk)):
            an, bn = a != a, b != b
            if an != bn:
                return False
            if not an and abs(a - b) > max(TOL, abs(a) * 1e-9):
                return False
    return True


def rebuild_from_chunks():
    frames = []
    for name in sorted(os.listdir(CHUNKS)):
        if not name.endswith(".parquet"):
            continue
        p = os.path.join(CHUNKS, name)
        if os.path.getsize(p) == 0:
            continue
        frames.append(pd.read_parquet(p))
    full = pd.concat([f for f in frames if len(f)], ignore_index=True)
    atomic_parquet_write(full, PARQUET)
    return len(full)


def main():
    t0 = time.time()
    present, store_reason = store_state(PARQUET, CHUNKS)
    if not present:
        prev = load_status()
        save_status({"cutoff": "unknown", "new_rows": 0,
                     "verdict": f"store absent on this node "
                                f"({store_reason}); backfill is a GM-lane "
                                "decision, not auto-fetched",
                     "last_attempt": prev.get("last_attempt")})
        print(f"STORE ABSENT - {store_reason}; honest skip, no crash",
              flush=True)
        return 2
    lhb = pd.read_parquet(PARQUET)
    dates = pd.to_datetime(lhb["上榜日"])
    cutoff = dates.max()
    q = pd.Period(cutoff, freq="Q")
    now = pd.Timestamp.now()
    prev = load_status()
    last_attempt = prev.get("last_attempt")
    if isinstance(last_attempt, str):
        try:
            last_attempt = pd.Timestamp(last_attempt)
        except Exception:
            last_attempt = None
    print(f"cutoff={cutoff.date()} quarter={q} today={now.date()}",
          flush=True)

    should, reason = fetch_gate(cutoff, now, last_attempt)
    print(reason, flush=True)
    if not should:
        save_status({"cutoff": str(cutoff.date()), "new_rows": 0,
                     "verdict": reason,
                     "last_attempt": prev.get("last_attempt")})
        return 0

    # record the attempt BEFORE the network call: a crash mid-fetch must
    # still throttle the next round (EM datacenter citizenship)
    save_status({"cutoff": str(cutoff.date()), "verdict": "fetching",
                 "last_attempt": str(now)})

    # r835 (bm-c): multi-quarter fetch window -- see docstring. The old
    # single-quarter window deadlocked at quarter turnover (cutoff frozen
    # at 2026-09-30 while 10-08/10-09 events sat unreachable in Q4).
    # CALENDAR, not panel dates: passing the panel's own dates here
    # pinned `expected` to the panel max (=cutoff) and collapsed the
    # window back to a single quarter -- the exact deadlock this fix
    # targets (caught live 16:0x, quarters=1). The gate computes its
    # expected from the local trading calendar (dates=None); the window
    # MUST use the same source or the two disagree at every turnover.
    quarters = quarters_to_fetch(cutoff, expected_disclosure_date(now))

    # r806 (bm-b): bounded-fetch jacket -- requests has no default timeout,
    # so a stalled server hung this leg forever (CloseWait 23min+ at
    # 15:29, killed two loop sessions). 45s turns any stall into an
    # honest fetch_fail rc2 instead of an unbounded hang.
    import requests as _rq
    _rq_request_orig = _rq.Session.request

    def _jacket_request(self, *args, **kwargs):
        kwargs.setdefault("timeout", 45)
        return _rq_request_orig(self, *args, **kwargs)

    _rq.Session.request = _jacket_request

    # ---- fetch every quarter on the stale path, one call per quarter
    # (per-quarter windows keep each chunk quarter-pure; the EM endpoint
    # honors arbitrary start/end windows so Q3 and Q4 are disjoint by
    # construction)
    frames = []
    try:
        import akshare as ak
        for qt in quarters:
            dfq = ak.stock_lhb_detail_em(
                start_date=qt.start_time.strftime("%Y%m%d"),
                end_date=qt.end_time.strftime("%Y%m%d"))
            if dfq is not None and not dfq.empty:
                frames.append(dfq)
    except Exception as ex:
        save_status({"cutoff": str(cutoff.date()), "verdict":
                     f"fetch_fail: {type(ex).__name__}: {str(ex)[:120]}",
                     "last_attempt": str(now)})
        print(f"FETCH FAIL {type(ex).__name__}: {str(ex)[:120]}", flush=True)
        return 2
    df = pd.concat(frames, ignore_index=True) if frames else None
    if df is None or df.empty:
        save_status({"cutoff": str(cutoff.date()), "new_rows": 0,
                     "verdict": "fetch returned empty (kept local)",
                     "last_attempt": str(now)})
        print("fetch empty - kept local", flush=True)
        return 0
    fd = pd.to_datetime(df["上榜日"])
    new = df[fd > cutoff]
    print(f"refetched rows={len(df)} quarters={len(quarters)} "
          f"({','.join(str(qt) for qt in quarters)}) "
          f"new_beyond_cutoff={len(new)}", flush=True)

    # ---- overlap check at the cutoff date
    old_day = lhb[pd.to_datetime(lhb["上榜日"]) == cutoff]
    new_day = df[fd == cutoff]
    ok_overlap = True
    late_ok = False
    detail = {"old_rows": int(len(old_day)), "new_rows": int(len(new_day))}
    if len(old_day) and len(new_day):
        old_sum = float(pd.to_numeric(old_day["龙虎榜净买额"],
                                      errors="coerce").sum())
        new_sum = float(pd.to_numeric(new_day["龙虎榜净买额"],
                                      errors="coerce").sum())
        detail["netbuy_sum_old"] = round(old_sum, 2)
        detail["netbuy_sum_new"] = round(new_sum, 2)
        ok_overlap = (len(old_day) == len(new_day)
                      and abs(old_sum - new_sum) <= max(TOL, abs(old_sum) * 1e-9))
        if not ok_overlap:
            # r280: late disclosures land past-date rows for hours after
            # the event (probe 2026-09-30: 25 rows joined the 09-28 window
            # with all 42 stored rows netbuy-identical). Pure ADDITION =
            # legitimate completion -> proceed; mutation/removal -> exit 3.
            late_ok = is_pure_addition(old_day, new_day)
            if late_ok:
                detail["overlap_note"] = ("late_disclosure_superset_accepted"
                                          " (stored rows netbuy-identical,"
                                          " source only added rows)")
    elif len(old_day) != len(new_day):
        ok_overlap = False
        late_ok = is_pure_addition(old_day, new_day)
        if late_ok:
            detail["overlap_note"] = "late_disclosure_superset_accepted"
    if not ok_overlap and not late_ok:
        save_status({"cutoff": str(cutoff.date()),
                     "verdict": "overlap_mismatch: source restated history, "
                                "local kept untouched",
                     "overlap": detail,
                     "last_attempt": str(now)})
        print(f"OVERLAP MISMATCH {detail} - kept local, no write", flush=True)
        return 3

    # ---- overwrite one chunk per fetched quarter, rebuild parquet
    # (r835: multi-quarter split keeps every chunk file quarter-pure)
    if len(new) == 0:
        save_status({"cutoff": str(cutoff.date()), "new_rows": 0,
                     "verdict": "no-op (no events beyond cutoff yet)",
                     "overlap": detail, "last_attempt": str(now)})
        print("no events beyond cutoff yet - no-op", flush=True)
        return 0
    per = fd.dt.to_period("Q")
    for qt in quarters:
        fq = df[per == qt]
        if len(fq):
            atomic_parquet_write(fq, os.path.join(CHUNKS, f"{qt}.parquet"))
    total = rebuild_from_chunks()
    new_cutoff = str(pd.to_datetime(
        pd.read_parquet(PARQUET, columns=["上榜日"])["上榜日"]).max().date())
    save_status({"cutoff_before": str(cutoff.date()),
                 "cutoff_after": new_cutoff, "new_rows": int(len(new)),
                 "quarters_refetched": [str(qt) for qt in quarters],
                 "total_rows": int(total),
                 "overlap": detail, "last_attempt": str(now),
                 "verdict": "updated"})
    print(f"updated: +{len(new)} rows, cutoff {cutoff.date()} -> "
          f"{new_cutoff}, total {total} ({time.time()-t0:.0f}s)", flush=True)
    return 0


def selftest():
    """Offline guard tests: disclosure-window/weekend/holiday dates, gate
    logic, min-interval, store-absent guard, atomic writes. Zero network,
    zero writes outside a temp sandbox."""
    ts = pd.Timestamp
    global _DATES_CACHE

    # ---- weekday fallback (fresh node without local daily data)
    _DATES_CACHE = None
    exp_cases = [
        ("Fri 16:00 pre-window", "2026-09-25 16:00", "2026-09-24"),
        ("Fri 17:30 in-window", "2026-09-25 17:30", "2026-09-25"),
        ("Sat 12:00 weekend", "2026-09-26 12:00", "2026-09-25"),
        ("Sat 18:00 weekend evening", "2026-09-26 18:00", "2026-09-25"),
        ("Sun 20:00 weekend evening", "2026-09-27 20:00", "2026-09-25"),
        ("Mon 09:00 pre-window", "2026-09-28 09:00", "2026-09-25"),
        ("Mon 18:30 in-window", "2026-09-28 18:30", "2026-09-28"),
    ]
    for name, now_s, want_s in exp_cases:
        got = expected_disclosure_date(ts(now_s))
        want = ts(want_s)
        assert got == want, f"{name}: got {got.date()} want {want.date()}"
        print(f"[PASS] expected_disclosure_date(fallback) {name} -> "
              f"{got.date()}", flush=True)

    # ---- holiday-aware calendar (SSE closure style: mid-week holiday)
    # synthetic week: Mon 09-28, Tue 09-29 trade; Wed 09-30 holiday;
    # next trade days Thu 10-08, Fri 10-09 (National-Day-style gap)
    cal = [ts("2026-09-28"), ts("2026-09-29"), ts("2026-10-08"),
           ts("2026-10-09")]
    hol_cases = [
        ("holiday evening rolls back to Tue", "2026-09-30 18:00",
         "2026-09-29"),
        ("holiday morning rolls back to Tue", "2026-09-30 09:00",
         "2026-09-29"),
        ("trading day in window -> today", "2026-10-08 18:00", "2026-10-08"),
        ("pre-window on trade day -> prior trade day", "2026-10-09 10:00",
         "2026-10-08"),
    ]
    for name, now_s, want_s in hol_cases:
        got = expected_disclosure_date(ts(now_s), cal)
        want = ts(want_s)
        assert got == want, f"{name}: got {got.date()} want {want.date()}"
        print(f"[PASS] expected_disclosure_date(calendar) {name} -> "
              f"{got.date()}", flush=True)

    # ---- sina-late self-heal pair: Wed 09-30 trades, bar lands 20:26
    # (09-23 precedent). Before the bar: expected rolls back (fetch
    # deferred); after the bar lands: expected == today (fetch fires).
    cal_before = [ts("2026-09-28"), ts("2026-09-29")]
    got = expected_disclosure_date(ts("2026-09-30 18:00"), cal_before)
    assert got == ts("2026-09-29"), \
        f"sina-late before-bar: got {got.date()} want 2026-09-29"
    print(f"[PASS] sina-late before-bar rollbacks -> {got.date()}",
          flush=True)
    cal_after = cal_before + [ts("2026-09-30")]
    got = expected_disclosure_date(ts("2026-09-30 20:30"), cal_after)
    assert got == ts("2026-09-30"), \
        f"sina-late after-bar: got {got.date()} want 2026-09-30"
    print(f"[PASS] sina-late after-bar self-heals -> {got.date()}",
          flush=True)

    # ---- fetch_gate with holiday calendar
    should, reason = fetch_gate(ts("2026-09-29"), ts("2026-09-30 18:00"),
                                None, cal)
    assert should is False, f"holiday no-op case: {reason}"
    print("[PASS] fetch_gate holiday caught-up -> no-op", flush=True)
    should, reason = fetch_gate(ts("2026-09-28"), ts("2026-09-29 18:00"),
                                None, cal)
    assert should is True, f"behind-on-calendar case: {reason}"
    print("[PASS] fetch_gate behind calendar -> fetch", flush=True)

    # ---- min-interval gate (unchanged semantics, explicit dates)
    gate_cases = [
        ("behind -> fetch", "2026-09-23", "2026-09-25 16:00", None, True),
        ("caught up -> no-op", "2026-09-25", "2026-09-26 18:00", None,
         False),
        ("fresh attempt -> throttled", "2026-09-23", "2026-09-25 16:00",
         "2026-09-25 15:50", False),
        ("stale attempt -> fetch", "2026-09-23", "2026-09-25 16:00",
         "2026-09-25 10:00", True),
    ]
    for name, cutoff_s, now_s, la_s, want_fetch in gate_cases:
        should, reason = fetch_gate(ts(cutoff_s), ts(now_s),
                                    ts(la_s) if la_s else None)
        assert should == want_fetch, f"{name}: got {should} ({reason})"
        print(f"[PASS] fetch_gate {name}", flush=True)

    # ---- r835: quarter-boundary fetch window (deadlock fix --
    # cutoff at Q3 end, expected disclosure in Q4 must widen the fetch)
    got = quarters_to_fetch(ts("2026-09-30"), ts("2026-10-09"))
    assert [str(x) for x in got] == ["2026Q3", "2026Q4"], got
    print("[PASS] quarters_to_fetch boundary crossing -> [Q3, Q4]",
          flush=True)
    got = quarters_to_fetch(ts("2026-09-15"), ts("2026-09-20"))
    assert [str(x) for x in got] == ["2026Q3"], got
    print("[PASS] quarters_to_fetch same quarter -> [Q3]", flush=True)
    got = quarters_to_fetch(ts("2026-09-30 18:00"), ts("2027-01-05 18:00"))
    assert [str(x) for x in got] == ["2026Q3", "2026Q4", "2027Q1"], got
    print("[PASS] quarters_to_fetch multi-year walk -> [Q3, Q4, 2027Q1]",
          flush=True)
    got = quarters_to_fetch(ts("2026-10-08"), ts("2026-10-09"))
    assert [str(x) for x in got] == ["2026Q4"], got
    print("[PASS] quarters_to_fetch inside Q4 -> [Q4]", flush=True)

    # ---- r835 live-fire regression leg: the call site must feed the
    # quarters window from the CALENDAR-based expected (dates=None ->
    # local trading calendar, same source as the gate), never from the
    # panel's own dates (panel max == cutoff collapses the window to one
    # quarter = the deadlock this fix targets; caught live 16:0x)
    src = open(__file__, encoding="utf-8").read()
    bad = "expected_disclosure_date(now, " + "dates))"
    good = "expected_disclosure_date(now" + "))"
    assert bad not in src, "quarters window fed from panel dates (deadlock)"
    assert src.count(good) == 1, f"call-site calendar form x{src.count(good)}"
    print("[PASS] quarters window fed from calendar (not panel dates)",
          flush=True)

    # ---- store-absent guard (HANDOVER s3 sparse-clone profile)
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        ok, reason = store_state(os.path.join(td, "nope.parquet"),
                                 os.path.join(td, "chunks"))
        assert ok is False and "missing" in reason, \
            f"absent parquet: {ok} {reason}"
        print("[PASS] store_state absent parquet -> honest skip", flush=True)
        p = os.path.join(td, "lhb_detail.parquet")
        pd.DataFrame({"a": [1]}).to_parquet(p)
        ok, reason = store_state(p, os.path.join(td, "no_chunks"))
        assert ok is False and "chunks" in reason, \
            f"absent chunks: {ok} {reason}"
        print("[PASS] store_state absent chunks dir -> honest skip",
              flush=True)
        cd = os.path.join(td, "chunks")
        os.makedirs(cd)
        ok, reason = store_state(p, cd)
        assert ok is True, f"present store: {ok} {reason}"
        print("[PASS] store_state present -> ok", flush=True)

        # ---- atomic write: verify + replace + no tmp residue
        df = pd.DataFrame({"上榜日": ["2026-09-23", "2026-09-24"],
                           "v": [1.0, 2.0]})
        atomic_parquet_write(df, p)
        back = pd.read_parquet(p)
        assert len(back) == 2 and not os.path.exists(p + ".tmp"), \
            "atomic write roundtrip failed"
        print("[PASS] atomic_parquet_write roundtrip + tmp cleanup",
              flush=True)

        # ---- r280: is_pure_addition (late-disclosure superset acceptance)
        def _mk(rows):
            return pd.DataFrame({
                "代码": [r[0] for r in rows],
                "上榜日": ["2026-09-28"] * len(rows),
                "上榜原因": [r[1] for r in rows],
                "龙虎榜净买额": [r[2] for r in rows],
            })

        base = [("000513", "日涨幅偏离值达到7%的前5只证券", 1.2e8),
                ("000560", "日换手率达到20%的前5只证券", -1.9e8)]
        late = [("300999", "日振幅值达到15%的前5只证券", -5.0e7)]
        assert is_pure_addition(_mk(base), _mk(base + late)) is True
        print("[PASS] is_pure_addition late row added -> accepted",
              flush=True)
        assert is_pure_addition(_mk(base), _mk(base)) is True
        print("[PASS] is_pure_addition identical sets -> accepted",
              flush=True)
        mut = [("000513", "日涨幅偏离值达到7%的前5只证券", 9.9e7), base[1]]
        assert is_pure_addition(_mk(base), _mk(mut)) is False
        print("[PASS] is_pure_addition stored netbuy mutated -> blocked",
              flush=True)
        assert is_pure_addition(_mk(base), _mk([base[0]])) is False
        print("[PASS] is_pure_addition stored row removed -> blocked",
              flush=True)
        dup_old = [("000001", "reason-a", 10.0), ("000001", "reason-a", 20.0)]
        dup_new = [("000001", "reason-a", 5.0), ("000001", "reason-a", 25.0)]
        assert is_pure_addition(_mk(dup_old), _mk(dup_new)) is False
        print("[PASS] is_pure_addition intra-key swap (sum-equal) -> blocked",
              flush=True)
        nan_pair = [("000002", "reason-b", float("nan")),
                    ("000002", "reason-b", 1.0)]
        assert is_pure_addition(_mk(nan_pair),
                                _mk([nan_pair[0], nan_pair[1]])) is True
        assert is_pure_addition(_mk(nan_pair),
                                _mk([("000002", "reason-b", 1.0),
                                     ("000002", "reason-b", 1.0)])) is False
        print("[PASS] is_pure_addition NaN identity NaN==NaN only",
              flush=True)
        assert is_pure_addition(_mk(base).iloc[0:0], _mk(late)) is True
        print("[PASS] is_pure_addition empty stored -> additions accepted",
              flush=True)
        assert is_pure_addition(_mk(base), _mk(base).iloc[0:0]) is False
        print("[PASS] is_pure_addition source emptied window -> blocked",
              flush=True)

    print("selftest: all guard cases PASS", flush=True)
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    sys.exit(main())
