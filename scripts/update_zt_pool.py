"""ZT-pool daily snapshot collector gate (O-20261001-2103 R2 data face,
bm-a lane, S5-01 GO landing; OSS harvest ledger section-7 pointer).

Pure data engineering: zero IC, zero engine runs, ledger N untouched.
Source = akshare EM zt-pool family (probe-verified locally, akshare
1.18.96, vibe-probe-20261008.json + OSS_HARVEST_LEDGER.md L130):
  zt    = stock_zt_pool_em       (涨停股池, carries 连板数 ladder)
  zbgc  = stock_zt_pool_zbgc_em  (炸板股池, 分歧轴)
  dtgc  = stock_zt_pool_dtgc_em  (跌停股池, 亏钱效应轴)
  strong= stock_zt_pool_strong_em(强势股池)
Each endpoint is fetched per-trading-day (single call, day-slice API).

Panel layout (forward-accrual, minute_feed family law):
  data/zt_pool/<key>.parquet        -- all days concatenated, 日期 col first
  data/zt_pool/collected_days.json  -- per-endpoint day ledger (the
                                       completeness face: a zero-row day is
                                       ledgered without parquet rows)

Guards (bigmoney-data-gate-wiring contract):
  - 15:30 no-op window is TRANSITIVE via the trading calendar: only days
    whose bar has LANDED in data/daily (update_daily, post-close only)
    are collectable -- bar-未落禁拉 in its purest form, stricter than a
    wall-clock 15:30 check (sina-late bar defers this gate a few hours,
    self-healing, update_lhb documented caveat same law).
  - forward accrual: FIRST_DATE clamp -- no history backfill from the
    gate (store backfill stays a GM-lane decision, lhb store-absent law);
    T-67 §2 freeze law: forward history >= 12 months before any prereg.
  - overlap row-level check: before appending, the latest collected day
    per endpoint is re-fetched and compared (code set + 涨跌幅 row-wise,
    NaN==NaN); mismatch = source restated -> write NOTHING, exit 3.
    No late-disclosure superset acceptance here (unlike LHB r280): pool
    day-slices are final at close; benign-completion amendment = a later
    round with evidence, not a silent accept.
  - conn-fuse: 3 consecutive connection-level failures abort the pass
    (per-day writes already landed stay; next pass resumes from ledger).
  - 30-min min-attempt throttle, attempt recorded BEFORE network (r18).
  - lane guard (R31): bm-a only; other machines stdout-only honest no-op,
    zero shared-state writes (R65).
  - shape gate: invariant columns per endpoint checked on every fetch;
    missing = blocked flag + exit 3 awaiting manual ruling (ths precedent).
  - atomic writes: .tmp + os.replace everywhere; 代码 row-shell defense
    (R58): rows with empty code never land.

Exit codes: 0 = normal/no-op; 2 = source fail / conn-fuse abort;
3 = overlap mismatch (source restated, local untouched) or shape drift
(blocked, awaiting manual ruling). Never masked, never re-mapped.
"""
import json
import os
import sys
import time

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PANEL_DIR = os.path.join(ROOT, "data", "zt_pool")
LEDGER = os.path.join(PANEL_DIR, "collected_days.json")
STATUS = os.path.join(ROOT, "results", "zt_pool_update_status.json")
sys.path.insert(0, ROOT)
from config.lane_io import write_lane  # noqa: E402 -- after ROOT pin
DAILY_DIR = os.path.join(ROOT, "data", "daily")
CORE_CALENDAR_FILE = os.path.join(DAILY_DIR, "510300.csv")

LANE_OWNER = "bm-a"           # R31 lane-ownership precedent (claim line)
TOL = 1e-6
MIN_ATTEMPT_INTERVAL = 30 * 60   # min seconds between network attempts
CONN_FUSE = 3                    # consecutive connection failures -> abort
RATE_SLEEP = 2.5                 # seconds between source calls (citizenship)
FIRST_DATE = "2026-10-08"        # forward-accrual start (no gate backfill)

# key -> (akshare fn name, invariant columns that must exist every fetch)
ENDPOINTS = {
    "zt":     ("stock_zt_pool_em",        ["代码", "名称", "涨跌幅", "连板数"]),
    "zbgc":   ("stock_zt_pool_zbgc_em",  ["代码", "名称", "涨跌幅"]),
    "dtgc":   ("stock_zt_pool_dtgc_em",   ["代码", "名称", "涨跌幅"]),
    "strong": ("stock_zt_pool_strong_em", ["代码", "名称", "涨跌幅"]),
}
NUM_COMPARE_COL = "涨跌幅"       # row-level overlap comparison column


def save_status(payload):
    payload["updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(STATUS), exist_ok=True)
    tmp = STATUS + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, default=str)
    os.replace(tmp, STATUS)
    # own-machine lane mirror, fail-soft never breaks the run
    write_lane("zt_pool_update_status", payload)


def load_status():
    if os.path.exists(STATUS):
        try:
            with open(STATUS, encoding="utf-8") as f:
                return json.load(f)
        except Exception as ex:
            print(f"WARN: zt_pool status unreadable "
                  f"({type(ex).__name__}: {str(ex)[:80]}); "
                  "starting from empty status", file=sys.stderr, flush=True)
    return {}


def _lane_owner_id():
    try:
        with open(os.path.join(ROOT, "fleet", "machine.json"),
                  encoding="utf-8-sig") as f:
            return str(json.load(f).get("machine_id", ""))
    except Exception:
        return ""


# ---------------------------------------------------------------- calendar
_DATES_CACHE = "unset"


def _load_trading_dates():
    """SSE trading-day history from local data/daily core bars (510300 =
    most liquid core ETF, every market day; update_daily maintains it on
    each node). Sorted list of 'YYYY-MM-DD' strings, or None when no
    local daily data exists (fresh node -> weekday approximation)."""
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
            ds = sorted(ds.dropna().dt.normalize().unique())
            if len(ds):
                dates = [pd.Timestamp(d).strftime("%Y-%m-%d") for d in ds]
        except Exception:
            dates = None
    if dates is None:
        # weekday approximation (old lhb behavior: harmless direction,
        # only extra throttled attempts on holidays)
        d0 = pd.Timestamp("2026-09-01")
        dates = [d.strftime("%Y-%m-%d") for d in
                pd.date_range(d0, pd.Timestamp.now().normalize())
                if d.weekday() < 5]
    _DATES_CACHE = dates
    return dates


def missing_days(collected, calendar):
    """Sorted collectable days for one endpoint: calendar days at/after
    FIRST_DATE that are beyond the latest collected day (fresh panel =
    every forward day missing). Bounded by the latest bar-landed
    calendar day. Pure function."""
    last = collected[-1] if collected else None
    return [d for d in calendar
            if d >= FIRST_DATE and (last is None or d > last)]


# ------------------------------------------------------------------ ledger
def load_ledger():
    if os.path.exists(LEDGER):
        try:
            with open(LEDGER, encoding="utf-8") as f:
                d = json.load(f)
            return {k: sorted(v) for k, v in d.items()
                    if k in ENDPOINTS and isinstance(v, list)}
        except Exception as ex:
            print(f"WARN: day ledger unreadable ({ex}); refusing to "
                  "collect (fail-closed, manual ruling)", file=sys.stderr,
                  flush=True)
            return None
    return {k: [] for k in ENDPOINTS}


def _atomic_json_write(obj, path):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def atomic_parquet_write(df, path):
    tmp = path + ".tmp"
    df.to_parquet(tmp, index=False)
    back = pd.read_parquet(tmp)
    if len(back) != len(df):
        raise RuntimeError(f"atomic write verify failed for {path}: "
                           f"wrote {len(df)} rows, tmp holds {len(back)}")
    os.replace(tmp, path)


def append_day(key, date, df_day):
    """Append one day's rows to the endpoint panel; dedupe by (日期,代码);
    zero-row day = panel untouched (ledgered upstream). Atomic."""
    path = os.path.join(PANEL_DIR, f"{key}.parquet")
    if df_day is None or len(df_day) == 0:
        return 0
    rows = df_day.copy()
    rows.insert(0, "日期", date)
    rows["代码"] = rows["代码"].astype(str)
    if os.path.exists(path):
        old = pd.read_parquet(path)
        old["代码"] = old["代码"].astype(str)
        rows = pd.concat([old, rows], ignore_index=True)
        rows = rows.drop_duplicates(subset=["日期", "代码"], keep="first")
    os.makedirs(PANEL_DIR, exist_ok=True)
    atomic_parquet_write(rows, path)
    return len(rows)


def _nan_sk(v):
    nan = v != v
    return (bool(nan), 0.0 if nan else float(v))


def day_rows_match(old_day, new_day):
    """Row-level overlap verdict for one collected day: same code
    multiset with per-code 涨跌幅 lists equal (NaN==NaN), order-free
    (source may shuffle row order between calls). Pure addition /
    removal / mutation -> False (keep blocking)."""
    if len(old_day) == 0 or len(new_day) == 0:
        return len(old_day) == len(new_day)

    def _keyed(frame):
        codes = frame["代码"].astype(str).tolist()
        vals = pd.to_numeric(frame[NUM_COMPARE_COL],
                             errors="coerce").tolist()
        keyed = {}
        for c, v in zip(codes, vals):
            keyed.setdefault(c, []).append(v)
        return keyed

    om, nm = _keyed(old_day), _keyed(new_day)
    if set(om) != set(nm):
        return False
    for c in sorted(om):
        if len(om[c]) != len(nm[c]):
            return False
        for a, b in zip(sorted(om[c], key=_nan_sk),
                        sorted(nm[c], key=_nan_sk)):
            an, bn = a != a, b != b
            if an != bn:
                return False
            if not an and abs(a - b) > max(TOL, abs(a) * 1e-9):
                return False
    return True


def fetch_day(ak_fn, date_compact, invariant_cols):
    """One source call. Returns (df, shape_ok). Connection-level
    exceptions propagate to the caller's fuse; shape drift -> shape_ok
    False (blocked path, never masked)."""
    df = ak_fn(date=date_compact)
    if df is None:
        df = pd.DataFrame()
    if len(df):
        missing = [c for c in invariant_cols if c not in df.columns]
        if missing:
            return df, False
        # R58 row-shell defense: empty/NaN codes never land
        df = df[df["代码"].notna() & (df["代码"].astype(str).str.strip() != "")]
    return df, True


def main():
    t0 = time.time()
    owner = _lane_owner_id()
    if owner != LANE_OWNER:
        # R31 lane guard + R65 zero-shared-state law: stdout-only no-op
        print(f"no-op: zt_pool lane owned by {LANE_OWNER}, "
              f"not this machine ({owner or '?'})", flush=True)
        return 0

    st = load_status()
    if st.get("blocked"):
        print(f"blocked: {st.get('block_reason', 'shape drift')} "
              "(exit 3, awaiting manual ruling)", flush=True)
        return 3

    ledger = load_ledger()
    if ledger is None:
        print("day ledger unreadable -> fail-closed exit 2", flush=True)
        return 2
    calendar = _load_trading_dates()
    todo = {k: missing_days(ledger[k], calendar) for k in ENDPOINTS}
    n_missing = sum(len(v) for v in todo.values())
    if n_missing == 0:
        cutoffs = {k: (ledger[k][-1] if ledger[k] else None)
                   for k in ENDPOINTS}
        save_status({"cutoffs": cutoffs, "new_rows": 0, "verdict":
                     "no-op: panel covers all bar-landed trading days",
                     "last_attempt": st.get("last_attempt")})
        print("no-op: panel covers all bar-landed trading days", flush=True)
        return 0

    now = pd.Timestamp.now()
    last_attempt = st.get("last_attempt")
    if isinstance(last_attempt, str):
        try:
            last_attempt = pd.Timestamp(last_attempt)
        except Exception:
            last_attempt = None
    if (last_attempt is not None
            and (now - last_attempt).total_seconds() < MIN_ATTEMPT_INTERVAL):
        save_status({"verdict": f"no-op: <{MIN_ATTEMPT_INTERVAL // 60}min "
                                "since last attempt (min-interval guard)",
                     "last_attempt": st.get("last_attempt"),
                     "pending_days": n_missing})
        print(f"throttle: last attempt {last_attempt} < 30min -> no-op "
              f"({n_missing} days pending)", flush=True)
        return 0

    # record the attempt BEFORE the network: crash mid-fetch still
    # throttles the next round (r18 law)
    save_status({"verdict": "fetching", "pending_days": n_missing,
                 "last_attempt": now.isoformat(timespec="seconds")})

    # r806 bounded-fetch jacket: requests has no default timeout
    import requests as _rq
    _rq_request_orig = _rq.Session.request

    def _jacket_request(self, *args, **kwargs):
        kwargs.setdefault("timeout", 45)
        return _rq_request_orig(self, *args, **kwargs)

    _rq.Session.request = _jacket_request

    import akshare as ak

    # ---- overlap check: latest collected day per endpoint (1 call each)
    for key, (fn_name, inv) in ENDPOINTS.items():
        if not ledger[key]:
            continue
        day = ledger[key][-1]
        try:
            df_ref, shape_ok = fetch_day(getattr(ak, fn_name),
                                         day.replace("-", ""), inv)
        except Exception as ex:
            save_status({"verdict": f"overlap refetch fail "
                                     f"{type(ex).__name__}: {str(ex)[:100]}",
                         "last_attempt": now.isoformat(timespec="seconds")})
            print(f"OVERLAP REFETCH FAIL {key} {day} "
                  f"{type(ex).__name__}: {str(ex)[:100]}", flush=True)
            return 2
        if not shape_ok:
            save_status({"blocked": True, "block_reason":
                         f"shape drift on {key} refetch (invariant col "
                         f"missing: {inv})", "last_attempt":
                         now.isoformat(timespec="seconds")})
            print(f"SHAPE DRIFT {key} ({fn_name}) invariant cols missing "
                  "-- blocked, exit 3", flush=True)
            return 3
        path = os.path.join(PANEL_DIR, f"{key}.parquet")
        if os.path.exists(path):
            old = pd.read_parquet(path)
            old_day = old[old["日期"] == day] if "日期" in old.columns \
                else old.iloc[0:0]
            if not day_rows_match(old_day, df_ref):
                save_status({"verdict": "overlap_mismatch: source restated "
                                         f"{key} {day}, local untouched",
                             "last_attempt":
                             now.isoformat(timespec="seconds")})
                print(f"OVERLAP MISMATCH {key} {day} - kept local, "
                      "no write", flush=True)
                return 3

    # ---- collect missing days (per-day checkpoint: each landed day
    #      persists in panel+ledger before the next call)
    fuse = 0
    total_new = 0
    for key, (fn_name, inv) in ENDPOINTS.items():
        ak_fn = getattr(ak, fn_name)
        for day in todo[key]:
            try:
                df_day, shape_ok = fetch_day(ak_fn, day.replace("-", ""), inv)
            except Exception as ex:
                fuse += 1
                print(f"FETCH FAIL {key} {day} {type(ex).__name__}: "
                      f"{str(ex)[:100]} (fuse {fuse}/{CONN_FUSE})", flush=True)
                if fuse >= CONN_FUSE:
                    save_status({"verdict": f"conn-fuse {CONN_FUSE} "
                                             "consecutive failures, pass "
                                             "aborted (landed days kept)",
                                 "last_attempt":
                                 now.isoformat(timespec="seconds")})
                    print(f"conn-fuse tripped after {fuse} failures -> "
                          "exit 2", flush=True)
                    return 2
                time.sleep(RATE_SLEEP)
                continue
            fuse = 0
            if not shape_ok:
                save_status({"blocked": True, "block_reason":
                             f"shape drift on {key} {day} (invariant col "
                             f"missing: {inv})", "last_attempt":
                             now.isoformat(timespec="seconds")})
                print(f"SHAPE DRIFT {key} {day} -- blocked, exit 3",
                      flush=True)
                return 3
            n_new = append_day(key, day, df_day)
            ledger[key] = sorted(set(ledger[key]) | {day})
            _atomic_json_write({k: sorted(v) for k, v in ledger.items()},
                               LEDGER)
            total_new += n_new
            print(f"collected {key} {day}: {len(df_day)} rows "
                  f"(panel {n_new})", flush=True)
            time.sleep(RATE_SLEEP)

    cutoffs = {k: (ledger[k][-1] if ledger[k] else None) for k in ENDPOINTS}
    save_status({"cutoffs": cutoffs, "new_rows": int(total_new),
                 "verdict": "updated",
                 "last_attempt": now.isoformat(timespec="seconds")})
    print(f"updated: +{total_new} rows, cutoffs {cutoffs} "
          f"({time.time() - t0:.0f}s)", flush=True)
    return 0


def selftest():
    """Offline guard tests: calendar window, FIRST_DATE clamp, overlap
    comparator, ledger/append idempotence, atomic writes, throttle.
    Zero network, zero writes outside a temp sandbox."""
    ts = pd.Timestamp

    # ---- missing_days: fresh panel clamps to FIRST_DATE
    cal = ["2026-09-28", "2026-09-29", "2026-09-30",
           "2026-10-08", "2026-10-09"]
    got = missing_days([], cal)
    assert got == ["2026-10-08", "2026-10-09"], got
    print("[PASS] missing_days fresh panel -> FIRST_DATE clamp", flush=True)
    got = missing_days(["2026-10-08"], cal)
    assert got == ["2026-10-09"], got
    print("[PASS] missing_days partial collected -> only later days",
          flush=True)
    got = missing_days(["2026-10-09"], cal)
    assert got == [], got
    print("[PASS] missing_days caught up -> empty", flush=True)
    got = missing_days(["2026-09-30"], cal)
    assert got == ["2026-10-08", "2026-10-09"], got
    print("[PASS] missing_days pre-FIRST cutoff -> clamped start",
          flush=True)

    # ---- holiday gap: golden-week style hole never yields a collect day
    cal_gap = ["2026-09-29", "2026-09-30", "2026-10-08"]
    got = missing_days(["2026-09-30"], cal_gap)
    assert got == ["2026-10-08"], got
    print("[PASS] missing_days holiday gap -> skips non-calendar days",
          flush=True)

    # ---- day_rows_match (overlap comparator)
    def _mk(rows):
        return pd.DataFrame({
            "代码": [r[0] for r in rows],
            "名称": ["x"] * len(rows),
            "涨跌幅": [r[1] for r in rows],
        })

    base = [("000513", 10.03), ("000560", 9.98)]
    assert day_rows_match(_mk(base), _mk(base)) is True
    print("[PASS] day_rows_match identical -> True", flush=True)
    assert day_rows_match(_mk(base), _mk(base + [("300999", 20.0)])) is False
    print("[PASS] day_rows_match pure addition -> blocked (pool day "
          "slices are final; amendment = manual ruling)", flush=True)
    mut = [("000513", 9.99), ("000560", 9.98)]
    assert day_rows_match(_mk(base), _mk(mut)) is False
    print("[PASS] day_rows_match value mutated -> blocked", flush=True)
    swapped = [("000560", 9.98), ("000513", 10.03)]
    assert day_rows_match(_mk(base), _mk(swapped)) is True
    print("[PASS] day_rows_match row order shuffle -> True (sorted keys)",
          flush=True)
    nan_pair = [("000002", float("nan")), ("000003", 5.55)]
    assert day_rows_match(_mk(nan_pair), _mk(nan_pair)) is True
    assert day_rows_match(_mk(nan_pair),
                          _mk([("000002", 0.0), ("000003", 5.55)])) is False
    print("[PASS] day_rows_match NaN identity NaN==NaN only", flush=True)
    empty = _mk(base).iloc[0:0]
    assert day_rows_match(empty, _mk(base).iloc[0:0]) is True
    assert day_rows_match(empty, _mk(base)) is False
    assert day_rows_match(_mk(base), empty) is False
    print("[PASS] day_rows_match empty-vs-rows -> blocked both ways",
          flush=True)

    # ---- panel append + ledger + idempotence, in a temp sandbox
    import tempfile
    global PANEL_DIR, LEDGER
    with tempfile.TemporaryDirectory() as td:
        real_panel, real_ledger = PANEL_DIR, LEDGER
        PANEL_DIR = os.path.join(td, "zt_pool")
        LEDGER = os.path.join(PANEL_DIR, "collected_days.json")
        try:
            os.makedirs(PANEL_DIR)
            _atomic_json_write({"zt": []}, LEDGER)
            day_df = _mk(base)
            n1 = append_day("zt", "2026-10-08", day_df)
            assert n1 == 2, n1
            # same-day re-append must not duplicate (dedupe gate)
            n2 = append_day("zt", "2026-10-08", day_df)
            assert n2 == 2, n2
            back = pd.read_parquet(os.path.join(PANEL_DIR, "zt.parquet"))
            assert len(back) == 2 and list(back["日期"]) == ["2026-10-08"] * 2
            print("[PASS] append_day dedupe + 日期 stamp roundtrip",
                  flush=True)
            # zero-row day: panel untouched, caller ledgers it
            n3 = append_day("zt", "2026-10-09", _mk(base).iloc[0:0])
            assert n3 == 0
            back = pd.read_parquet(os.path.join(PANEL_DIR, "zt.parquet"))
            assert len(back) == 2
            print("[PASS] append_day zero-row day -> panel untouched",
                  flush=True)
            # next day lands
            n4 = append_day("zt", "2026-10-09", _mk([("600001", -4.44)]))
            assert n4 == 3, n4
            back = pd.read_parquet(os.path.join(PANEL_DIR, "zt.parquet"))
            assert len(back) == 3 and not os.path.exists(
                os.path.join(PANEL_DIR, "zt.parquet.tmp"))
            print("[PASS] append_day next-day append + tmp cleanup",
                  flush=True)
            # ledger roundtrip via load_ledger
            _atomic_json_write({"zt": ["2026-10-08", "2026-10-09"],
                                "foreign": ["x"]}, LEDGER)
            led = load_ledger()
            assert led == {"zt": ["2026-10-08", "2026-10-09"]}, led
            print("[PASS] load_ledger filters foreign keys + sorts",
                  flush=True)
        finally:
            PANEL_DIR, LEDGER = real_panel, real_ledger

    # ---- min-interval throttle arithmetic (mirror of lhb gate law)
    now = ts("2026-10-09 16:00")
    assert (now - ts("2026-10-09 15:50")).total_seconds() \
        < MIN_ATTEMPT_INTERVAL          # 10min -> throttled
    assert (now - ts("2026-10-09 10:00")).total_seconds() \
        >= MIN_ATTEMPT_INTERVAL         # 6h -> fresh attempt ok
    print("[PASS] min-interval throttle arithmetic", flush=True)

    # ---- lane guard: owner id resolution never guesses (r98 face)
    assert isinstance(_lane_owner_id(), str)
    print("[PASS] lane_owner_id returns str (no guess)", flush=True)

    # ---- endpoints registry sanity: akshare import-time presence
    try:
        import akshare as ak
        for key, (fn_name, inv) in ENDPOINTS.items():
            assert hasattr(ak, fn_name), f"akshare missing {fn_name}"
            assert all(isinstance(c, str) for c in inv)
        print("[PASS] ENDPOINTS akshare fn presence x"
              f"{len(ENDPOINTS)}", flush=True)
    except ImportError:
        print("[SKIP] akshare absent on this node -- ENDPOINTS check "
              "skipped (import-time only, no network)", flush=True)

    print("selftest: all guard cases PASS", flush=True)
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    sys.exit(main())
