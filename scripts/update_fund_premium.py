# -*- coding: utf-8 -*-
"""update_fund_premium.py -- T-16 ARB-1 fund-premium data lane, deliverable-2:
snapshot puller (bulk NAV face) + per-fund NAV history backfill for core48.

Ticket T-2026-09-24-16 (O-20260924-1155, ARB-1 per ARBITRAGE_PLAYBOOK.md sec.3).
Deliverable-1 evidence (r51 probe, results/shortline/fund_premium_probe.json):
  - ak.fund_etf_fund_daily_em()  : bulk face, 1660 rows, ONE request covers the
    universe; NAV dates are embedded in COLUMN NAMES ("2026-09-23-单位净值"),
    carries NAV(D) + NAV(D-1) pairs + 市价 + source-computed 折价率.
  - ak.fund_etf_fund_info_em(fund, start_date, end_date): per-fund NAV history
    (净值日期/单位净值/累计净值), fresh to previous trading day.
  - NAV is T-1 lagged by nature: on fetch-day T the bulk face carries NAV(T-1)
    and NAV(T-2). Forward-only usage (premium at D uses close(D) vs NAV(D-1)),
    no look-ahead -- lag convention frozen at the P-A1 prereg, not here.

Legs:
  snapshot      S6 daily step: weekday & >=15:30 guard, ONE bulk request,
                idempotent by NAV date, 30-min failure retry backoff,
                atomic write, lane-owner guard (bm-c; T-16 is bm-c's claimed
                lane per F-04). Non-owner machines: stdout-only no-op, zero
                shared-state writes (R31 precedent, hardened per bm-a R65
                moneyflow fix + bm-c r38 stomping incident).
  backfill-nav  one-shot resumable NAV history for core48 (bare-code CSVs in
                data/daily -- same enumeration as update_daily.core_files).
                2.5s throttle, per-symbol retry w/ backoff for data/api-level
                errors, conn-level failures never retried inline (R63 law),
                5-consecutive-conn fuse = source blocked, honest exit 2 with
                checkpoint preserved (per-symbol file = done marker).
  gate          zero-network completeness: NAV coverage >= 95% of core48 +
                snapshot freshness (prereg data-gate helper, ticket item 5).
  status        print disk facts + status file.
  selftest      offline guards, zero network (J18 self-consistency law: every
                assertion constant derived from the synthetic fixture).

Storage (gitignored, never fabricate backtest history -- data/heat precedent):
  data/fund_premium/snapshots/<navdate>.csv   normalized bulk snapshot
  data/fund_premium/nav/<code>.csv            date,nav,acc_nav history
  results/fund_premium_status.json            owner-written status mirror

Exit codes: 0 = ok/no-op/complete; 2 = source failure / incomplete (honest,
checkpoint preserved; never masked).
"""
from __future__ import annotations

import datetime as dt
import glob
import json
import os
import sys
import time
import traceback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data", "fund_premium")
SNAP_DIR = os.path.join(DATA_DIR, "snapshots")
NAV_DIR = os.path.join(DATA_DIR, "nav")
STATUS_PATH = os.path.join(ROOT, "results", "fund_premium_status.json")
DAILY_DIR = os.path.join(ROOT, "data", "daily")
MACHINE_JSON = os.path.join(ROOT, "fleet", "machine.json")

LANE_OWNER = "bm-c"        # T-16 claimed by bm-c (r51) -> lane owner per R31
THROTTLE_S = 2.5           # EM citizenship throttle (house constant)
COMPLETE_HOUR = dt.time(15, 30)   # close-data alignment, update_heat precedent
RETRY_BACKOFF_S = 8        # per-symbol retry backoff (R20 precedent)
MAX_ATTEMPTS = 3           # per-symbol attempts for data/api-level errors
CONN_FUSE = 5              # consecutive conn-level failures -> source blocked
RETRY_AFTER_FAIL_S = 30 * 60      # snapshot retry backoff after failure
SNAP_ROW_FLOOR = 500       # probe saw 1660; a broken day shows far fewer
SNAP_NAV_NONNULL = 0.90    # row-shell defense (R58 law) on the NAV(D) pair
NAV_ROW_FLOOR = 250        # ~1 trading year; youngest core48 member ~2023
NAV_NONNULL = 0.995
NAV_HISTORY_START = "19900101"    # full history; source clips to inception
NAV_GATE_COVERAGE = 0.95   # prereg data-gate floor (ticket item 5)

SNAP_COLS = ["code", "name", "ftype", "nav", "acc_nav", "nav_prev", "acc_nav_prev",
             "growth", "growth_rate", "mkt_price", "discount_rate"]
NAV_COLS = ["date", "nav", "acc_nav"]


# ------------------------------------------------------------------ env / lane
def clear_proxy_env():
    """Clash 全局代理劫持 python 流量（J13 回环坑族）——akshare 前一律清 env 代理。"""
    for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY",
              "all_proxy", "ALL_PROXY"):
        os.environ.pop(k, None)
    os.environ["NO_PROXY"] = "*"
    os.environ["no_proxy"] = "*"


def _lane_owner_id(path=MACHINE_JSON) -> str:
    """本机 machine_id；读不到=空串（按非 owner 处理，防御性降级）。"""
    try:
        with open(path, encoding="utf-8-sig") as f:      # BOM-tolerant (bm-c r6 law)
            return str(json.load(f).get("machine_id") or "")
    except Exception:
        return ""


# ------------------------------------------------------------------ error taxonomy (probe-verbatim)
CONN_MARKERS = ("ConnectionError", "Timeout", "RemoteDisconnected", "MaxRetryError",
                "ProtocolError", "ConnectionReset", "ConnectionAborted", "getaddrinfo")
API_MARKERS = ("HTTPError", "HTTP 4", "HTTP 5", "403", "404", "405", "429")


def classify_error(err: BaseException) -> str:
    """连接级/数据级/API 级三分类（fund_premium_probe.py 逐字复用）：
    连接级永不内联重试（R63 law），只进 fuse 计数。"""
    chain, e = [], err
    while e is not None and len(chain) <= 8:
        chain.append(type(e).__name__ + ": " + str(e)[:200])
        e = e.__cause__ or e.__context__
    text = " | ".join(chain)
    if any(m in text for m in CONN_MARKERS):
        return "conn_level"
    if any(m in text for m in API_MARKERS):
        return "api_level"
    return "data_level"


# ------------------------------------------------------------------ calendar (self-contained, update_futures sibling)
def _load_trading_dates(daily_dir=DAILY_DIR):
    """本地 ETF 交易日历：510300.csv 主源，glob 兜底（update_lhb 同构模式）。"""
    cands = [os.path.join(daily_dir, "510300.csv")] + \
            sorted(glob.glob(os.path.join(daily_dir, "*.csv")))
    for p in cands:
        try:
            with open(p, encoding="utf-8-sig") as f:
                dates = set()
                for i, line in enumerate(f):
                    if i == 0:
                        continue
                    d = line.split(",")[0].strip()
                    if len(d) == 10 and d[4] == "-" and d[7] == "-":
                        dates.add(d)
                if dates:
                    return sorted(dates)
        except Exception:
            continue
    return None


def expected_prev_trading_day(now: dt.datetime, dates=None) -> str:
    """快照应携带的 NAV 日 = 今天之前最近一个交易日（纯函数，selftest 覆盖）。
    今天是交易日也取 strictly-before：NAV(T) 尚未发布，T 日盘中/盘后面携带的是 NAV(T-1)。"""
    if dates is None:
        dates = _load_trading_dates()
    today = now.date().isoformat()
    if dates is not None:
        prior = [d for d in dates if d < today]
        if prior:
            return prior[-1]
    d = now.date() - dt.timedelta(days=1)
    while d.weekday() >= 5:
        d -= dt.timedelta(days=1)
    return d.isoformat()


# ------------------------------------------------------------------ snapshot normalization (pure)
def _extract_nav_dates(cols) -> list:
    """列名内嵌日期（'2026-09-23-单位净值'）→ 去重升序日期列表（probe pass2 发现的坑）。"""
    out = []
    for c in cols:
        cs = str(c)
        if len(cs) >= 10 and cs[4] == "-" and cs[7] == "-":
            d = cs[:10]
            if len(d) == 10 and d[4] == "-" and d[7] == "-":
                out.append(d)
    return sorted(set(out))


def normalize_snapshot(df):
    """bulk face → (nav_date, norm_df)。取列名最大日期 D 为 nav/acc_nav，次大为 *_prev。
    返回 (D, DataFrame) 或抛 ValueError（shape 违约诚实炸，不静默）。"""
    import pandas as pd
    dates = _extract_nav_dates(df.columns)
    if len(dates) < 2:
        raise ValueError(f"bulk face: expected >=2 date-stamped NAV column pairs, got {dates}")
    d_max, d_prev = dates[-1], dates[-2]

    def col(base, d):
        for c in df.columns:
            if str(c) == f"{d}-{base}":
                return c
        raise ValueError(f"bulk face: missing column {d}-{base}")

    out = pd.DataFrame({
        "code": df["基金代码"].astype(str).str.strip(),
        "name": df["基金简称"].astype(str).str.strip(),
        "ftype": df["类型"].astype(str).str.strip(),
        "nav": pd.to_numeric(df[col("单位净值", d_max)], errors="coerce"),
        "acc_nav": pd.to_numeric(df[col("累计净值", d_max)], errors="coerce"),
        "nav_prev": pd.to_numeric(df[col("单位净值", d_prev)], errors="coerce"),
        "acc_nav_prev": pd.to_numeric(df[col("累计净值", d_prev)], errors="coerce"),
        "growth": pd.to_numeric(df.get("增长值"), errors="coerce"),
        "growth_rate": df.get("增长率").astype(str).str.strip() if "增长率" in df.columns else "",
        "mkt_price": pd.to_numeric(df.get("市价"), errors="coerce"),
        "discount_rate": df.get("折价率").astype(str).str.strip() if "折价率" in df.columns else "",
    })
    out["code"] = out["code"].str.zfill(6)
    return d_max, out


def validate_snapshot(nav_date: str, norm_df) -> list:
    """快照验证门（行壳防御 R58）：返回违规清单，空=通过。"""
    problems = []
    if len(norm_df) < SNAP_ROW_FLOOR:
        problems.append(f"rows {len(norm_df)} < floor {SNAP_ROW_FLOOR}")
    if nav_date is None or len(nav_date) != 10:
        problems.append(f"nav_date invalid: {nav_date!r}")
    nn = norm_df["nav"].notna().sum() if len(norm_df) else 0
    if len(norm_df) and nn / len(norm_df) < SNAP_NAV_NONNULL:
        problems.append(f"nav non-null rate {nn / len(norm_df):.3f} < {SNAP_NAV_NONNULL}")
    bad_codes = (~norm_df["code"].str.isdigit()).sum() if len(norm_df) else 1
    if len(norm_df) and bad_codes / len(norm_df) > 0.05:
        problems.append(f"non-digit code rows {bad_codes}")
    return problems


def snapshot_needs_fetch(newest_disk: str, expected: str) -> tuple:
    """(needs, reason) 纯函数：盘上最新快照日 >= 期望 NAV 日=已收当日份。"""
    if newest_disk is None:
        return True, "no local snapshot yet (first run)"
    if str(newest_disk) >= str(expected):
        return False, f"snapshot {newest_disk} already covers expected NAV date {expected}"
    return True, f"disk newest {newest_disk} behind expected NAV date {expected}"


# ------------------------------------------------------------------ NAV history validation (pure)
def validate_nav_df(df) -> list:
    """NAV 历史验证门：日期严格递增（去重后）、nav 非空率、行数地板。"""
    problems = []
    if len(df) < NAV_ROW_FLOOR:
        problems.append(f"rows {len(df)} < floor {NAV_ROW_FLOOR}")
        return problems
    nn = df["nav"].notna().sum()
    if nn / len(df) < NAV_NONNULL:
        problems.append(f"nav non-null rate {nn / len(df):.4f} < {NAV_NONNULL}")
    pos = (df["nav"].dropna() > 0).sum()
    if pos < nn:
        problems.append(f"{nn - pos} non-positive nav values")
    dates = list(df["date"])
    if dates != sorted(dates):
        problems.append("dates not ascending")
    if len(set(dates)) != len(dates):
        problems.append(f"{len(dates) - len(set(dates))} duplicate dates")
    return problems


# ------------------------------------------------------------------ status I/O (owner only)
def load_status() -> dict:
    try:
        with open(STATUS_PATH, encoding="utf-8-sig") as f:
            return json.load(f)
    except Exception:
        return {}


def write_status(st: dict):
    os.makedirs(os.path.dirname(STATUS_PATH), exist_ok=True)
    tmp = STATUS_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)
    os.replace(tmp, STATUS_PATH)


def _core48_codes(daily_dir=DAILY_DIR) -> list:
    """core48 = data/daily 裸码 CSV（update_daily.core_files 镜像，单一源）。"""
    if not os.path.isdir(daily_dir):
        return []
    return sorted(f[:-4] for f in os.listdir(daily_dir)
                  if f.endswith(".csv") and f[:-4].isdigit())


def _newest_snapshot(snap_dir=SNAP_DIR) -> str:
    if not os.path.isdir(snap_dir):
        return None
    files = [f[:-4] for f in os.listdir(snap_dir)
             if f.endswith(".csv") and len(f[:-4]) == 10 and f[:-4][4] == "-"]
    return max(files) if files else None


# ------------------------------------------------------------------ snapshot leg
def cmd_snapshot() -> int:
    owner = _lane_owner_id()
    if owner != LANE_OWNER:
        # R31 lane guard (moneyflow R65 hardening): stdout-only, ZERO shared-state writes
        print(f"no-op: fund_premium lane owned by {LANE_OWNER}, not this machine ({owner or '?'})")
        return 0
    now = dt.datetime.now()
    st = load_status()
    st["lane_owner"] = LANE_OWNER
    snap = st.get("snapshot") or {}

    if now.weekday() >= 5:
        snap["no_op_reason"] = "weekend"
        st.update({"ts": now.isoformat(timespec="seconds"), "mode": "no-op: weekend", "snapshot": snap})
        write_status(st)
        print("no-op: weekend (NAV publishes on trading days only)")
        return 0
    if now.time() < COMPLETE_HOUR:
        snap["no_op_reason"] = f"before {COMPLETE_HOUR}"
        st.update({"ts": now.isoformat(timespec="seconds"), "mode": "no-op: before close", "snapshot": snap})
        write_status(st)
        print(f"no-op: before {COMPLETE_HOUR} (close-data alignment, update_heat precedent)")
        return 0

    newest = _newest_snapshot()
    expected = expected_prev_trading_day(now)
    needs, reason = snapshot_needs_fetch(newest, expected)
    if not needs:
        snap["no_op_reason"] = reason
        st.update({"ts": now.isoformat(timespec="seconds"), "mode": "no-op: fresh", "snapshot": snap})
        write_status(st)
        print(f"no-op: {reason}")
        return 0

    # 30-min retry backoff after a failure (r18 law: last_attempt written BEFORE fetch)
    last = snap.get("last_attempt")
    if last:
        try:
            if (now - dt.datetime.fromisoformat(last)).total_seconds() < RETRY_AFTER_FAIL_S \
                    and snap.get("last_error"):
                print(f"throttle: last failed attempt {last} < 30min -> retry later")
                return 0
        except Exception:
            pass
    snap["last_attempt"] = now.isoformat(timespec="seconds")
    st["snapshot"] = snap
    write_status(st)

    clear_proxy_env()
    import akshare as ak
    t0 = time.time()
    try:
        df = ak.fund_etf_fund_daily_em()
    except Exception as e:  # noqa: BLE001 -- honest fail, never mask
        snap = st.get("snapshot") or {}
        snap["last_error"] = classify_error(e) + ": " + str(e)[:200]
        st.update({"ts": dt.datetime.now().isoformat(timespec="seconds"),
                   "mode": "snapshot fetch failed",
                   "snapshot": snap})
        write_status(st)
        print(f"snapshot fetch FAILED ({snap['last_error']}) -> honest exit 2")
        return 2

    try:
        nav_date, norm = normalize_snapshot(df)
    except ValueError as e:
        snap = st.get("snapshot") or {}
        snap["last_error"] = f"shape violation: {e}"
        st.update({"ts": dt.datetime.now().isoformat(timespec="seconds"),
                   "mode": "snapshot shape violation",
                   "snapshot": snap})
        write_status(st)
        print(f"snapshot shape VIOLATION: {e} -> honest exit 2")
        return 2

    problems = validate_snapshot(nav_date, norm)
    if problems:
        snap = st.get("snapshot") or {}
        snap["last_error"] = "; ".join(problems)
        st.update({"ts": dt.datetime.now().isoformat(timespec="seconds"),
                   "mode": "snapshot validation failed",
                   "snapshot": snap})
        write_status(st)
        print(f"snapshot validation FAILED: {snap['last_error']} -> honest exit 2")
        return 2

    out_path = os.path.join(SNAP_DIR, f"{nav_date}.csv")
    if os.path.exists(out_path):
        snap = st.get("snapshot") or {}
        snap.update({"latest_nav_date": nav_date, "no_op_reason": "file already on disk",
                     "last_error": None})
        st.update({"ts": dt.datetime.now().isoformat(timespec="seconds"),
                   "mode": "no-op: idempotent", "snapshot": snap})
        write_status(st)
        print(f"no-op: snapshot {nav_date} already on disk")
        return 0

    os.makedirs(SNAP_DIR, exist_ok=True)
    tmp = out_path + ".tmp"
    norm[SNAP_COLS].to_csv(tmp, index=False, encoding="utf-8")
    os.replace(tmp, out_path)
    snap = st.get("snapshot") or {}
    snap.update({"latest_nav_date": nav_date, "last_fetch": dt.datetime.now().isoformat(timespec="seconds"),
                 "rows": int(len(norm)), "last_error": None})
    st.update({"ts": dt.datetime.now().isoformat(timespec="seconds"),
               "mode": "snapshot stored",
               "snapshot": snap})
    write_status(st)
    print(f"snapshot stored: {nav_date} rows={len(norm)} ({time.time() - t0:.1f}s fetch+write)")
    return 0


# ------------------------------------------------------------------ NAV backfill leg
def _fetch_nav_history(ak, code: str, end_date: str):
    return ak.fund_etf_fund_info_em(fund=code, start_date=NAV_HISTORY_START, end_date=end_date)


def cmd_backfill_nav() -> int:
    owner = _lane_owner_id()
    if owner != LANE_OWNER:
        print(f"no-op: fund_premium lane owned by {LANE_OWNER}, not this machine ({owner or '?'})")
        return 0
    codes = _core48_codes()
    if not codes:
        print("no core48 codes found (data/daily empty) -> honest exit 2")
        return 2
    os.makedirs(NAV_DIR, exist_ok=True)
    now = dt.datetime.now()
    end_date = now.date().isoformat().replace("-", "")
    clear_proxy_env()
    import akshare as ak

    todo, done_skip = [], []
    for c in codes:
        p = os.path.join(NAV_DIR, f"{c}.csv")
        if os.path.exists(p):
            done_skip.append(c)
        else:
            todo.append(c)

    st = load_status()
    nav = st.get("nav") or {}
    failures, conn_streak = [], 0
    fused = False
    for i, c in enumerate(todo):
        if conn_streak >= CONN_FUSE:
            fused = True
            break
        got = None
        err_last = None
        for attempt in range(MAX_ATTEMPTS):
            try:
                got = _fetch_nav_history(ak, c, end_date)
                break
            except Exception as e:  # noqa: BLE001
                cls = classify_error(e)
                err_last = cls + ": " + str(e)[:150]
                if cls == "conn_level":
                    # R63 law: conn-level failures never burn inline retries
                    conn_streak += 1
                    break
                time.sleep(RETRY_BACKOFF_S)
        if conn_streak >= CONN_FUSE:
            fused = True
            break
        if got is None:
            failures.append({"code": c, "reason": err_last or "unknown"})
            print(f"nav {c}: FAILED ({err_last}) -> honest skip label")
            time.sleep(THROTTLE_S)
            continue
        try:
            import pandas as pd
            d = pd.DataFrame({
                "date": got["净值日期"].astype(str).str.strip(),
                "nav": pd.to_numeric(got["单位净值"], errors="coerce"),
                "acc_nav": pd.to_numeric(got["累计净值"], errors="coerce"),
            })
            d = d.drop_duplicates(subset="date", keep="first").sort_values("date").reset_index(drop=True)
        except Exception as e:  # noqa: BLE001
            failures.append({"code": c, "reason": "shape: " + str(e)[:150]})
            print(f"nav {c}: SHAPE violation ({e}) -> honest skip label")
            time.sleep(THROTTLE_S)
            continue
        problems = validate_nav_df(d)
        if problems:
            failures.append({"code": c, "reason": "; ".join(problems)})
            print(f"nav {c}: VALIDATION failed ({'; '.join(problems)}) -> not stored")
        else:
            out_path = os.path.join(NAV_DIR, f"{c}.csv")
            tmp = out_path + ".tmp"
            d[NAV_COLS].to_csv(tmp, index=False, encoding="utf-8")
            os.replace(tmp, out_path)
            print(f"nav {c}: stored rows={len(d)} "
                  f"({d['date'].iloc[0]}..{d['date'].iloc[-1]})")
        time.sleep(THROTTLE_S)

    total = len(codes)
    have = len(done_skip) + sum(1 for c in todo
                                if os.path.exists(os.path.join(NAV_DIR, f"{c}.csv")))
    coverage = have / total if total else 0.0
    nav.update({"done": have, "total": total, "coverage": round(coverage, 4),
                "failures": failures, "fused": fused,
                "last_run": now.isoformat(timespec="seconds"),
                "history_start": NAV_HISTORY_START})
    st.update({"ts": dt.datetime.now().isoformat(timespec="seconds"),
               "lane_owner": LANE_OWNER,
               "mode": ("nav backfill fused (source blocked)" if fused
                        else "nav backfill complete" if not failures
                        else "nav backfill partial (honest labels)"),
               "nav": nav})
    write_status(st)
    print(f"nav backfill: {have}/{total} on disk, coverage {coverage:.1%}, "
          f"failures={len(failures)}, fused={fused}")
    if have == total and not failures:
        return 0
    return 2


# ------------------------------------------------------------------ gate / status
def cmd_gate() -> int:
    codes = _core48_codes()
    have = sum(1 for c in codes if os.path.exists(os.path.join(NAV_DIR, f"{c}.csv")))
    coverage = have / len(codes) if codes else 0.0
    newest = _newest_snapshot()
    expected = expected_prev_trading_day(dt.datetime.now())
    snap_ok = newest is not None and str(newest) >= str(expected)
    problems = []
    if coverage < NAV_GATE_COVERAGE:
        problems.append(f"NAV coverage {coverage:.1%} < {NAV_GATE_COVERAGE:.0%}")
    if not snap_ok:
        problems.append(f"snapshot missing/behind: disk={newest} expected>={expected}")
    print(f"gate: nav {have}/{len(codes)} ({coverage:.1%}), snapshot newest={newest} "
          f"expected={expected} -> {'PASS' if not problems else 'FAIL'}")
    for p in problems:
        print(f"  - {p}")
    return 0 if not problems else 2


def cmd_status() -> int:
    st = load_status()
    print(json.dumps({
        "status_file": st,
        "disk": {"snapshots": len(glob.glob(os.path.join(SNAP_DIR, '*.csv'))),
                 "newest_snapshot": _newest_snapshot(),
                 "nav_files": len(glob.glob(os.path.join(NAV_DIR, '*.csv'))),
                 "core48": len(_core48_codes())},
    }, ensure_ascii=False, indent=1))
    return 0


# ------------------------------------------------------------------ selftest (offline, zero network)
def selftest() -> int:
    import pandas as pd
    fails = []

    def chk(name, cond):
        print(("PASS " if cond else "FAIL ") + name)
        if not cond:
            fails.append(name)

    # S1 error taxonomy (probe parity)
    chk("classify conn_level", classify_error(ConnectionError("RemoteDisconnected")) == "conn_level")
    import urllib.error
    chk("classify api_level",
        classify_error(urllib.error.HTTPError(None, 404, "Not Found", None, None)) == "api_level")
    chk("classify data_level", classify_error(ValueError("shape")) == "data_level")

    # S2 nav-date extraction from column names (probe pass2 pit)
    cols = ["基金代码", "2026-09-23-单位净值", "2026-09-22-单位净值", "市价"]
    chk("extract nav dates", _extract_nav_dates(cols) == ["2026-09-22", "2026-09-23"])
    chk("extract none honest", _extract_nav_dates(["a", "b"]) == [])

    # S3 normalize bulk face (synthetic 2-date-pair shape, mirrors probe cols)
    bulk = pd.DataFrame({
        "基金代码": ["510300", "513100"],
        "基金简称": ["沪深300ETF", "纳指ETF"],
        "类型": ["指数型-股票", "QDII"],
        "2026-09-23-单位净值": ["4.5904", "5.10"],
        "2026-09-23-累计净值": ["4.59", "5.0"],
        "2026-09-22-单位净值": ["4.58", "5.08"],
        "2026-09-22-累计净值": ["4.58", "5.0"],
        "增长值": ["0.01", "0.02"],
        "增长率": ["0.2%", "0.4%"],
        "市价": ["4.59", "5.11"],
        "折价率": ["0.01%", "0.2%"],
    })
    d_max, norm = normalize_snapshot(bulk)
    chk("normalize nav_date", d_max == "2026-09-23")
    chk("normalize nav pair", abs(float(norm["nav"].iloc[0]) - 4.5904) < 1e-9
        and abs(float(norm["nav_prev"].iloc[0]) - 4.58) < 1e-9)
    chk("normalize discount passthrough", norm["discount_rate"].iloc[0] == "0.01%")
    chk("normalize code zfill", norm["code"].iloc[0] == "510300")
    try:
        normalize_snapshot(bulk.drop(columns=["2026-09-22-单位净值"]))
        chk("normalize missing pair raises", False)
    except ValueError:
        chk("normalize missing pair raises", True)

    # S4 snapshot validation gates
    ok_norm = norm.copy()
    chk("validate snapshot ok", validate_snapshot("2026-09-23", pd.concat([ok_norm] * 300)) == [])
    tiny = norm.copy()
    probs = validate_snapshot("2026-09-23", tiny)
    chk("validate row floor", any("rows" in p for p in probs))
    shell = pd.concat([ok_norm] * 300)
    shell["nav"] = None
    probs2 = validate_snapshot("2026-09-23", shell)
    chk("validate row-shell (nav null)", any("non-null" in p for p in probs2))

    # S5 calendar expectation (injected dates, J18 self-consistency: derived from fixture)
    cal = ["2026-09-18", "2026-09-21", "2026-09-22", "2026-09-23"]
    chk("expected prev trading day (weekday)",
        expected_prev_trading_day(dt.datetime(2026, 9, 24, 16, 0), cal) == "2026-09-23")
    chk("expected prev trading day (monday)",
        expected_prev_trading_day(dt.datetime(2026, 9, 21, 16, 0), cal) == "2026-09-18")
    chk("expected prev trading day (no calendar, weekday)",
        expected_prev_trading_day(dt.datetime(2026, 9, 24, 16, 0), None) == "2026-09-23")
    chk("expected prev trading day (no calendar, monday fallback)",
        expected_prev_trading_day(dt.datetime(2026, 9, 21, 16, 0), None) == "2026-09-18")

    # S6 snapshot no-op logic
    chk("needs fetch when none", snapshot_needs_fetch(None, "2026-09-23")[0] is True)
    chk("no-op when covered", snapshot_needs_fetch("2026-09-23", "2026-09-23")[0] is False)
    chk("needs fetch when behind", snapshot_needs_fetch("2026-09-22", "2026-09-23")[0] is True)

    # S7 NAV history validation
    n = 300
    navdf = pd.DataFrame({"date": [f"2026-{(i // 30) + 1:02d}-{(i % 30) + 1:02d}" for i in range(n)]})
    navdf = navdf.sort_values("date").reset_index(drop=True)
    navdf["nav"] = 1.0 + navdf.index / 1000
    navdf["acc_nav"] = navdf["nav"] + 0.5
    chk("validate nav ok", validate_nav_df(navdf) == [])
    dup = pd.concat([navdf, navdf.tail(1)], ignore_index=True)
    chk("validate nav dup dates", any("duplicate" in p for p in validate_nav_df(dup)))
    short = navdf.head(50)
    chk("validate nav row floor", any("rows" in p for p in validate_nav_df(short)))
    holes = navdf.copy()
    holes.loc[0:5, "nav"] = None      # 6/300 = 2% null > 0.5% floor
    chk("validate nav null rate", any("non-null" in p for p in validate_nav_df(holes)))
    neg = navdf.copy()
    neg.loc[0, "nav"] = -1.0
    chk("validate nav positive", any("non-positive" in p for p in validate_nav_df(neg)))

    # S8 lane guard (injected identity file)
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "machine.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump({"machine_id": "bm-b"}, f)
        chk("lane owner id read", _lane_owner_id(p) == "bm-b")
        chk("non-owner != LANE_OWNER", _lane_owner_id(p) != LANE_OWNER)
        with open(p, "w", encoding="utf-8-sig") as f:   # BOM variant (fleet file reality)
            f.write(json.dumps({"machine_id": "bm-c"}))
        chk("lane owner BOM-tolerant", _lane_owner_id(p) == "bm-c")

    print(f"selftest: {'ALL PASS' if not fails else 'FAIL -> ' + str(fails)}")
    return 0 if not fails else 1


# ------------------------------------------------------------------ entry
def main(argv):
    if len(argv) < 2:
        print("usage: update_fund_premium.py snapshot|backfill-nav|gate|status|selftest")
        return 2
    cmd = argv[1]
    if cmd == "snapshot":
        return cmd_snapshot()
    if cmd == "backfill-nav":
        return cmd_backfill_nav()
    if cmd == "gate":
        return cmd_gate()
    if cmd == "status":
        return cmd_status()
    if cmd == "selftest":
        return selftest()
    print(f"unknown subcommand: {cmd}")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
