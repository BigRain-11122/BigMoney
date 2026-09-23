"""Fundamental + ST eligibility snapshot (O-1820 item2 data lane).

R-pei1 (loss) / R-pei2 (blast) in firm/risk/iron_rules.md need a data lane
the bars panel cannot provide (no financial/name columns). This script is
that lane: an idempotent point-in-time per-stock verdict table consumed by
the B-layer screen as a side-table join (panel untouched) and later by
paper/live negative-list checks.

Sources (CEO-approved line, O-1820 item2; proven on this network by the
archived M0923 fundamental.py):
  - ak.stock_yjbb_em(date=YYYYMMDD)  East Money earnings report, full
    market per period (~11k rows), net profit = attributable (gui-mu)
    caliber per source docs -- the sign is what R-pei1 needs.
  - ST set via a three-tier chain (independent failure domains, serving
    tier recorded in status rows.st_source):
    ak.stock_zh_a_st_em (EM ST board, authoritative) -> same API via
    plain requests with browser UA (vendor sends no UA and push2 also
    burst-rate-limits this network, diagnosed 2026-09-23) -> sina
    full-market spot names filtered to ST/退 markers (provider-
    independent proxy: risk-warning stocks carry the markers in their
    names by exchange rule).

Verdict calibre (V1, conservative direction "unknown = do not buy"):
  - annual   = most recent published 1231 period with >= MIN_ROWS rows
  - interim  = most recent published non-annual period, plus its
    prior-year twin -> ttm = annual + interim - interim_prev
  - r1_loss  = np_annual < 0 (iron rule is strict "< 0") or
               (ttm_ok and np_ttm < 0); no financial row / NaN ->
               r1_loss via no_data (R-pei1 "missing = do not buy")
  - r2_st    = code in ST list or reported name contains ST/退 markers
  - eligible = not r1_loss and not r2_st  (R-pei1 & R-pei2 ONLY;
               liquidity / listing-age / price floors live in the
               screen's own dynamic rules, P4_BATCH2 spec SS2)
  - honest-skip: 立案调查 / 审计非标 (no reliable free source) ->
               status skipped_dims, never silently ignored

Contract (update_daily.py sibling):
  - snapshot semantics: full replace of a point-in-time table; a same-day
    rerun rewrites identical content (deterministic sort); git is the
    history ledger.
  - age guard: default run skips fetching while the snapshot is younger
    than SNAPSHOT_MAX_AGE_H (24h); --force bypasses.
  - atomic write: tmp + os.replace for both outputs.
  - degraded modes: annual OR ST-list failure -> exit 2, nothing written
    (core evidence missing); interim / prev-twin failure -> annual-only
    R-pei1 with degraded flags recorded.
  - --probe: fresh fetch + verdict diff vs the committed snapshot,
    nothing written (fleet cross-machine source-health check).
  - --selftest: offline synthetic tests of the verdict logic.
  - status log: results/fundamental_status.json (fetch evidence, health
    gates, verdict counts, coverage vs the Money02 bars universe).

Exit codes: 0 ok (incl. age-guard skip) | 1 selftest fail | 2 source
fetch failure (reported, never silenced).

Usage:
    python scripts/update_fundamental.py             # age-guarded update
    python scripts/update_fundamental.py --force    # fetch now
    python scripts/update_fundamental.py --probe    # verify vs snapshot
    python scripts/update_fundamental.py --selftest  # offline tests
"""
import datetime as dt
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from config import PATHS

SNAPSHOT_DIR = PATHS.fundamental_dir
SNAPSHOT_CSV = os.path.join(SNAPSHOT_DIR, "eligibility.csv")
STATUS_PATH = os.path.join(PATHS.results_dir, "fundamental_status.json")
PROBE_PATH = os.path.join(PATHS.results_dir, "fundamental_probe.json")
BARS_DIR = os.path.join(PATHS.root, "Money02", "data", "bars")

SNAPSHOT_MAX_AGE_H = 24      # financials change quarterly; ST list drifts slow
MIN_ROWS = 4000              # a genuinely published full-market period
ST_MIN, ST_MAX = 30, 600     # sanity band for the ST board list
NAME_MARKERS = ("ST", "退")
FETCH_RETRY = 2
NP_COL = "净利润-净利润"


# ---------------------------------------------------------------- periods

def report_candidates(today: dt.date) -> list:
    """Quarter-end periods <= today, newest first (this + prior 2 years)."""
    out = []
    for year in (today.year, today.year - 1, today.year - 2):
        for md in ("1231", "0930", "0630", "0331"):
            d = dt.date(year, int(md[:2]), int(md[2:]))
            if d <= today:
                out.append(d.strftime("%Y%m%d"))
    return sorted(set(out), reverse=True)


def prev_twin(period: str) -> str:
    """Same MMDD one year earlier (for the TTM subtraction)."""
    return str(int(period[:4]) - 1) + period[4:]


# ---------------------------------------------------------------- fetchers

def fetch_yjbb(period: str) -> pd.DataFrame:
    """One earnings-report period -> code/name/np frame (deduped).

    Returns an EMPTY frame when the period is not (fully) published yet;
    RAISES on transport failure after retries -- the two cases are never
    conflated (a silent fallback to an older period would mislabel data).
    """
    import akshare as ak
    last = None
    for _ in range(FETCH_RETRY):
        try:
            df = ak.stock_yjbb_em(date=period)
        except Exception as e:  # noqa: BLE001 -- transport vs empty split
            last = e
            time.sleep(1.0)
            continue
        if df is None or len(df) < MIN_ROWS:
            return pd.DataFrame()
        out = pd.DataFrame({
            "code": df["股票代码"].astype(str).str.zfill(6),
            "name": df["股票简称"].astype(str),
            "np": pd.to_numeric(df[NP_COL], errors="coerce"),
        })
        return out.drop_duplicates("code", keep="first").reset_index(drop=True)
    raise RuntimeError(f"stock_yjbb_em({period}) failed: {last}")


def pick_annual(cands: list):
    for p in (c for c in cands if c.endswith("1231")):
        df = fetch_yjbb(p)
        if len(df) >= MIN_ROWS:
            return df, p
    raise RuntimeError("no published annual period reachable")


def pick_interim(cands: list):
    """Most recent fully-published non-annual period (empty df = degraded)."""
    for p in (c for c in cands if not c.endswith("1231")):
        df = fetch_yjbb(p)
        if len(df) >= MIN_ROWS:
            return df, p
    return pd.DataFrame(), ""


def fetch_st():
    """Current ST set -> (code/name frame, source label).

    Three-tier chain, independent failure domains:
      1. vendor ak.stock_zh_a_st_em (EM ST board, authoritative)
      2. same API via plain requests + browser UA (vendor sends no UA;
         push2 also rate-limits bursts on this network -- diagnosed
         2026-09-23: 200s then RemoteDisconnected after ~15 probe calls)
      3. sina full-market spot names -> ST/退 marker subset (provider
         independent; name-rule proxy: 风险警示/退市整理 stocks carry the
         markers in their names by exchange rule)
    """
    try:
        return _fetch_st_vendor(), "em_st_board"
    except Exception as e:  # noqa: BLE001
        print(f"  [st] vendor endpoint failed ({type(e).__name__}) -> direct UA")
    try:
        return _fetch_st_direct(), "em_push2_direct_ua"
    except Exception as e:  # noqa: BLE001
        print(f"  [st] direct UA failed ({type(e).__name__}) -> sina markers")
    return _fetch_st_sina_names(), "sina_name_markers"


def _fetch_st_vendor() -> pd.DataFrame:
    import akshare as ak
    df = ak.stock_zh_a_st_em()
    if df is None or len(df) == 0:
        raise RuntimeError("stock_zh_a_st_em returned empty")
    code_col = next((c for c in ("代码", "股票代码", "symbol") if c in df.columns), None)
    name_col = next((c for c in ("名称", "股票简称") if c in df.columns), None)
    if code_col is None or name_col is None:
        raise RuntimeError(f"ST list unexpected columns: {list(df.columns)}")
    codes = df[code_col].astype(str).str.extract(r"(\d{6})")[0]
    out = pd.DataFrame({"code": codes, "name": df[name_col].astype(str)})
    out = out.dropna(subset=["code"]).drop_duplicates("code")
    return out.reset_index(drop=True)


ST_URL = "https://push2.eastmoney.com/api/qt/clist/get"
ST_PARAMS = {"pn": "1", "pz": "100", "po": "1", "np": "1",
             "ut": "bd1d9ddb04089700cf9c27f6f7426281",
             "fltt": "2", "invt": "2", "fid": "f3",
             "fs": "m:0 f:4,m:1 f:4", "fields": "f12,f14"}


def _fetch_st_direct() -> pd.DataFrame:
    """Same ST board via plain requests with a browser UA (paginated)."""
    import requests
    rows, pn = [], 1
    while True:
        r = requests.get(ST_URL, params=dict(ST_PARAMS, pn=str(pn)), timeout=15,
                         headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        data = r.json().get("data") or {}
        diff = data.get("diff") or []
        if isinstance(diff, dict):
            diff = list(diff.values())
        if not diff:
            break
        rows.extend(diff)
        if pn * 100 >= int(data.get("total", 0)):
            break
        pn += 1
        time.sleep(0.3)
    if not rows:
        raise RuntimeError("ST board direct fetch empty")
    out = pd.DataFrame({"code": [str(x.get("f12")) for x in rows],
                        "name": [str(x.get("f14")) for x in rows]})
    out["code"] = out["code"].str.zfill(6)
    return out.drop_duplicates("code").reset_index(drop=True)


def _fetch_st_sina_names() -> pd.DataFrame:
    """Sina full-market spot -> ST/退 marker subset (provider-independent)."""
    import akshare as ak
    df = ak.stock_zh_a_spot()
    if df is None or len(df) < 4000:
        raise RuntimeError(f"sina spot sweep too small: {0 if df is None else len(df)}")
    code_col = next((c for c in ("代码", "股票代码", "symbol") if c in df.columns), None)
    name_col = next((c for c in ("名称", "股票简称") if c in df.columns), None)
    if code_col is None or name_col is None:
        raise RuntimeError(f"sina spot unexpected columns: {list(df.columns)}")
    names = df[name_col].astype(str)
    m = df[names.str.contains("ST|退", regex=True)]
    if len(m) < ST_MIN:
        raise RuntimeError(f"sina marker subset suspiciously small: {len(m)}")
    codes = m[code_col].astype(str).str.extract(r"(\d{6})")[0]
    out = pd.DataFrame({"code": codes, "name": m[name_col].astype(str)})
    out = out.dropna(subset=["code"]).drop_duplicates("code")
    return out.reset_index(drop=True)


# ---------------------------------------------------------------- verdicts

def build_verdicts(annual, interim, prev, st) -> pd.DataFrame:
    """Assemble per-code R-pei1/R-pei2 verdicts. Pure: offline-testable."""
    def idx(df):
        return df.set_index("code") if df is not None and len(df) else None
    a, i, p = idx(annual), idx(interim), idx(prev)
    st_set = set(st["code"]) if st is not None and len(st) else set()
    st_name = dict(zip(st["code"], st["name"])) if st is not None and len(st) else {}

    def np_at(index, code):
        if index is None or code not in index.index:
            v = None
        else:
            v = index.at[code, "np"]
        return None if v is None or pd.isna(v) else float(v)

    def name_at(code):
        # freshest name wins: ST list (current) > interim > annual
        if code in st_name:
            return st_name[code]
        for index in (i, a):
            if index is not None and code in index.index:
                v = index.at[code, "name"]
                if pd.notna(v):
                    return str(v)
        return ""

    codes = set()
    for df in (annual, interim, prev):
        if df is not None and len(df):
            codes |= set(df["code"])
    codes |= st_set

    recs = []
    for code in codes:
        np_a, np_i, np_p = np_at(a, code), np_at(i, code), np_at(p, code)
        ttm_ok = np_a is not None and np_i is not None and np_p is not None
        np_ttm = (np_a + np_i - np_p) if ttm_ok else None
        if np_a is None:
            r1_loss, r1_reason = True, "no_data"
        elif np_a < 0:
            r1_loss, r1_reason = True, "annual<0"
        elif ttm_ok and np_ttm < 0:
            r1_loss, r1_reason = True, "ttm<0"
        else:
            r1_loss, r1_reason = False, ""
        name = name_at(code)
        in_list = code in st_set
        marker = bool(name) and any(m in name for m in NAME_MARKERS)
        r2_st = in_list or marker
        r2_source = "+".join(s for s, on in (("st_list", in_list),
                                             ("name_marker", marker)) if on)
        recs.append({
            "code": code, "name": name,
            "np_annual": np_a, "np_interim": np_i, "np_interim_prev": np_p,
            "np_ttm": np_ttm, "ttm_ok": ttm_ok,
            "r1_loss": r1_loss, "r1_reason": r1_reason,
            "r2_st": r2_st, "r2_source": r2_source,
            "eligible": not (r1_loss or r2_st),
        })
    return pd.DataFrame(recs).sort_values("code").reset_index(drop=True)


# ---------------------------------------------------------------- health

def health_gates(annual, annual_period, st, verdicts, today) -> dict:
    gates = {}
    gates["annual_rows_ge_min"] = bool(len(annual) >= MIN_ROWS)
    ap = dt.date(int(annual_period[:4]), 12, 31)
    gates["annual_period_within_18m"] = bool((today - ap).days <= 550)
    np_ratio = float(annual["np"].notna().mean()) if len(annual) else 0.0
    gates["annual_np_nonnull_ge_095"] = np_ratio >= 0.95
    gates["st_rows_in_band"] = bool(ST_MIN <= len(st) <= ST_MAX)
    marker_ratio = (float(sum(any(m in n for m in NAME_MARKERS)
                              for n in st["name"])) / max(len(st), 1))
    gates["st_names_marker_ge_08"] = marker_ratio >= 0.8
    gates["verdict_rows_gt_4000"] = bool(len(verdicts) > 4000)
    gates["np_ratio"], gates["st_marker_ratio"] = round(np_ratio, 4), round(marker_ratio, 4)
    gates["all_pass"] = all(v for k, v in gates.items() if isinstance(v, bool))
    return gates


def coverage_vs_bars(verdicts) -> dict:
    """Best-effort: how many bars-universe codes have a verdict row."""
    if not os.path.isdir(BARS_DIR):
        return {"bars_dir": "absent"}
    stems = {f[:-8] for f in os.listdir(BARS_DIR) if f.endswith(".parquet")}
    have = set(verdicts["code"])
    missing = sorted(stems - have)
    return {"bars_codes": len(stems), "covered": len(stems) - len(missing),
            "missing": len(missing), "missing_sample": missing[:10]}


def verdict_counts(v: pd.DataFrame) -> dict:
    loss = v[v["r1_loss"]]
    st = v[v["r2_st"]]
    return {
        "rows": int(len(v)),
        "eligible": int(v["eligible"].sum()),
        "r1_loss_total": int(len(loss)),
        "r1_by_reason": {k: int(n) for k, n in
                         loss["r1_reason"].value_counts().items()},
        "r2_st_total": int(len(st)),
        "r2_by_source": {k: int(n) for k, n in
                         st["r2_source"].value_counts().items()},
        "ttm_ok_rows": int(v["ttm_ok"].sum()),
    }


def _atomic_write_csv(df: pd.DataFrame, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    df.to_csv(tmp, index=False)
    os.replace(tmp, path)


def _atomic_write_json(obj: dict, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


# ---------------------------------------------------------------- run paths

def _fetch_all(today: dt.date) -> dict:
    """Shared fetch for update & probe. Raises RuntimeError on core failure."""
    cands = report_candidates(today)
    annual, annual_period = pick_annual(cands)
    interim, interim_period = pick_interim(cands)
    prev, prev_period, prev_err = pd.DataFrame(), "", None
    if len(interim):
        try:
            prev = fetch_yjbb(prev_twin(interim_period))
            prev_period = prev_twin(interim_period)
            if len(prev) < MIN_ROWS:
                prev, prev_period = pd.DataFrame(), ""
        except Exception as e:  # noqa: BLE001 -- TTM degrades, not fatal
            prev_err = f"{type(e).__name__}: {e}"
    st, st_source = fetch_st()
    return {"annual": annual, "annual_period": annual_period,
            "interim": interim, "interim_period": interim_period,
            "prev": prev, "prev_period": prev_period, "prev_err": prev_err,
            "st": st, "st_source": st_source}


def run_update(force: bool = False) -> int:
    if not force and os.path.exists(SNAPSHOT_CSV):
        age_h = (time.time() - os.path.getmtime(SNAPSHOT_CSV)) / 3600.0
        if age_h < SNAPSHOT_MAX_AGE_H:
            print(f"snapshot fresh ({age_h:.1f}h < {SNAPSHOT_MAX_AGE_H}h) -> skip")
            return 0
    today = dt.date.today()
    print(f"=== Bigmoney fundamental eligibility update "
          f"{time.strftime('%Y-%m-%d %H:%M:%S')} ===")
    try:
        src = _fetch_all(today)
    except Exception as e:  # noqa: BLE001 -- core source failure
        print(f"FATAL source fetch: {e}")
        _atomic_write_json({"ok": False, "updated": time.strftime("%Y-%m-%d %H:%M:%S"),
                            "error": f"{type(e).__name__}: {e}"},
                           STATUS_PATH)
        return 2
    v = build_verdicts(src["annual"], src["interim"], src["prev"], src["st"])
    gates = health_gates(src["annual"], src["annual_period"],
                         src["st"], v, today)
    status = {
        "ok": bool(gates["all_pass"]),
        "updated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "periods": {"annual": src["annual_period"],
                    "interim": src["interim_period"] or None,
                    "interim_prev": src["prev_period"] or None},
        "rows": {"annual": int(len(src["annual"])),
                 "interim": int(len(src["interim"])),
                 "interim_prev": int(len(src["prev"])),
                 "st_list": int(len(src["st"])),
                 "st_source": src["st_source"]},
        "degraded": {"ttm_ok": bool(len(src["interim"]) and len(src["prev"])),
                     "prev_err": src["prev_err"]},
        "skipped_dims": ["证监会立案调查", "年报审计非标意见"],
        "health_gates": gates,
        "verdicts": verdict_counts(v),
        "coverage_vs_bars": coverage_vs_bars(v),
        "snapshot": "data/fundamental/eligibility.csv",
    }
    if not gates["all_pass"]:
        print(f"health gates FAILED: "
              f"{[k for k, g in gates.items() if isinstance(g, bool) and not g]}")
        status["error"] = "health gates failed -- snapshot NOT written"
        _atomic_write_json(status, STATUS_PATH)
        return 2
    _atomic_write_csv(v, SNAPSHOT_CSV)
    _atomic_write_json(status, STATUS_PATH)
    c = status["verdicts"]
    print(f"snapshot: {c['rows']} rows | eligible {c['eligible']} | "
          f"loss {c['r1_loss_total']} {c['r1_by_reason']} | st {c['r2_st_total']}")
    print(f"periods: annual {status['periods']['annual']} "
          f"interim {status['periods']['interim']} "
          f"(ttm_ok={status['degraded']['ttm_ok']}) | "
          f"st_source={src['st_source']}")
    print(f"status -> {STATUS_PATH}")
    return 0


def run_probe() -> int:
    """Cross-machine source-health check: fresh fetch vs committed snapshot."""
    if not os.path.exists(SNAPSHOT_CSV):
        print("no committed snapshot to compare against -- run update first")
        return 2
    today = dt.date.today()
    print(f"=== fundamental probe {time.strftime('%Y-%m-%d %H:%M:%S')} ===")
    try:
        src = _fetch_all(today)
    except Exception as e:  # noqa: BLE001
        print(f"FATAL source fetch: {e}")
        return 2
    v = build_verdicts(src["annual"], src["interim"], src["prev"], src["st"])
    gates = health_gates(src["annual"], src["annual_period"],
                         src["st"], v, today)
    old = pd.read_csv(SNAPSHOT_CSV, dtype={"code": str})
    old["code"] = old["code"].str.zfill(6)
    m = old.merge(v, on="code", suffixes=("_old", "_new"))
    agree = {
        "r1_loss": float((m["r1_loss_old"].astype(str) ==
                          m["r1_loss_new"].astype(str)).mean()),
        "r2_st": float((m["r2_st_old"].astype(str) ==
                        m["r2_st_new"].astype(str)).mean()),
        "eligible": float((m["eligible_old"].astype(str) ==
                           m["eligible_new"].astype(str)).mean()),
    }
    drift = m[m["eligible_old"].astype(str) != m["eligible_new"].astype(str)]
    ok = gates["all_pass"] and agree["eligible"] >= 0.98
    _atomic_write_json({
        "probed": time.strftime("%Y-%m-%d %H:%M:%S"),
        "snapshot_age_h": round((time.time() - os.path.getmtime(SNAPSHOT_CSV)) / 3600.0, 2),
        "health_gates": gates,
        "verdict_agreement": {k: round(x, 6) for k, x in agree.items()},
        "eligible_drift_codes": [str(c) for c in drift["code"].head(20)],
        "ok": bool(ok),
    }, PROBE_PATH)
    print(f"agreement: { {k: round(x, 4) for k, x in agree.items()} } "
          f"| drift {len(drift)} | gates all_pass={gates['all_pass']}")
    print(f"probe -> {PROBE_PATH} ({'PASS' if ok else 'FAIL'})")
    return 0 if ok else 2


# ---------------------------------------------------------------- selftest

def selftest() -> bool:
    ok = True

    # A: period candidates -- newest first, future excluded, membership
    cands = report_candidates(dt.date(2026, 9, 23))
    a = (cands[0] == "20260630" and "20251231" in cands
         and "20260930" not in cands and "20241231" in cands)
    ok &= a
    print("  [fund] report candidates ordering... " + ("PASS" if a else "FAIL"))

    # B: prev twin
    a = prev_twin("20260630") == "20250630" and prev_twin("20251231") == "20241231"
    ok &= a
    print("  [fund] prior-year twin... " + ("PASS" if a else "FAIL"))

    # C: verdict logic on synthetic frames (offline, deterministic)
    annual = pd.DataFrame({
        "code": ["600001", "000002", "300003", "688004"],
        "name": ["Good", "BadLoss", "TTMBad", "NoNum"],
        "np": [100.0, -50.0, 100.0, float("nan")]})
    interim = pd.DataFrame({
        "code": ["600001", "000002", "300003", "688004"],
        "name": ["Good", "BadLoss", "TTMBad", "NoNum"],
        "np": [10.0, -5.0, 80.0, 1.0]})
    prev = pd.DataFrame({
        "code": ["600001", "000002", "300003", "688004"],
        "name": ["Good", "BadLoss", "TTMBad", "NoNum"],
        "np": [5.0, -1.0, 200.0, 0.5]})
    st = pd.DataFrame({"code": ["600001"], "name": ["ST Goodname"]})
    v = build_verdicts(annual, interim, prev, st).set_index("code")
    c = (bool(v.at["600001", "r2_st"])
         and v.at["600001", "r2_source"] == "st_list+name_marker"  # list + marker in its own name
         and not bool(v.at["600001", "r1_loss"])          # np 100, ttm 105
         and not bool(v.at["600001", "eligible"])
         and bool(v.at["000002", "r1_loss"])
         and v.at["000002", "r1_reason"] == "annual<0"    # -50 annual first
         and bool(v.at["300003", "r1_loss"])
         and v.at["300003", "r1_reason"] == "ttm<0"        # 100+80-200=-20
         and abs(float(v.at["300003", "np_ttm"]) + 20.0) < 1e-9
         and bool(v.at["688004", "r1_loss"])
         and v.at["688004", "r1_reason"] == "no_data")     # NaN np -> conservative
    ok &= c
    print("  [fund] verdict logic (annual/ttm/no_data/st_list)... "
          + ("PASS" if c else "FAIL"))

    # D: name-marker blast net + ST-only code survives outside yjbb
    v2 = build_verdicts(
        pd.DataFrame({"code": ["600005"], "name": ["*ST Foo"], "np": [10.0]}),
        None, None, None)
    v3 = build_verdicts(None, None, None,
                        pd.DataFrame({"code": ["000099"], "name": ["退市X"]}))
    d = (bool(v2.loc[0, "r2_st"]) and v2.loc[0, "r2_source"] == "name_marker"
         and not bool(v2.loc[0, "r1_loss"]) and not bool(v2.loc[0, "eligible"])
         and bool(v3.loc[0, "r1_loss"]) and v3.loc[0, "r1_reason"] == "no_data"
         and bool(v3.loc[0, "r2_st"]) and v3.loc[0, "name"] == "退市X"
         and not bool(v3.loc[0, "eligible"]))
    ok &= d
    print("  [fund] name-marker net + ST-only code... " + ("PASS" if d else "FAIL"))

    # E: strict "< 0" -- zero profit is NOT a loss per iron-rule wording
    v4 = build_verdicts(
        pd.DataFrame({"code": ["600006"], "name": ["ZeroCo"], "np": [0.0]}),
        None, None, None)
    e = (not bool(v4.loc[0, "r1_loss"]) and bool(v4.loc[0, "eligible"]))
    ok &= e
    print("  [fund] strict <0 (zero profit passes)... " + ("PASS" if e else "FAIL"))

    # F: health gates on synthetic inputs
    g = health_gates(annual, "20251231", st,
                     build_verdicts(annual, interim, prev, st),
                     dt.date(2026, 9, 23))
    f = (g["annual_rows_ge_min"] is False      # 4 < MIN_ROWS, honest
         and g["st_rows_in_band"] is False      # 1 < ST_MIN, honest
         and g["all_pass"] is False)
    ok &= f
    print("  [fund] health gates sanity... " + ("PASS" if f else "FAIL"))
    return bool(ok)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--selftest" in argv:
        print(f"=== update_fundamental selftest "
              f"{time.strftime('%Y-%m-%d %H:%M:%S')} ===")
        return 0 if selftest() else 1
    if "--probe" in argv:
        return run_probe()
    return run_update(force="--force" in argv)


if __name__ == "__main__":
    sys.exit(main())
