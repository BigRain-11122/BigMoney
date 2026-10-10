"""HSGT (northbound) data-source reachability probe -- E3 P3-queue head.

Probe-only, zero-engine, zero-ledger. Mirrors moneyflow_source_probe.py (R58)
discipline; residual scope after R58 already covered D/E/F legs:

  1. hist_em policy-face verify    : series continues to today? which columns
                                     survive non-degenerate after the 2024-08-16
                                     HKEX real-time-flow termination?
  2. fund_flow_summary_em          : NOT probed by R58 (summary face).
  3. fund_min_em                   : NOT probed by R58 (intraday face, policy-dead
                                     hypothesis).
  4. hold_stock_em                 : R58 leg F failed (TypeError); retry with
                                     corrected market/indicator params.
  5. stock_statistics_em           : NOT probed by R58 (daily per-stock stats,
                                     recent-window freshness check).
  6. individual_detail_em          : R58 leg E showed last data 2024-09-30 --
                                     re-verify latest date + sort order.

Network rules (r39/r40 audit precedents): direct connection (proxy env
cleared), >=3.0s polite sleep between probes, per-probe honest error capture,
45s timeout jacket. Exit code is NOT a probe verdict: 0 = machinery wrote
JSON, 2 = machinery failure.

Usage: python scripts/hsgt_source_probe.py [selftest|run]
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "shortline", "hsgt_source_probe.json")

SLEEP_S = 3.0
POLICY_DATE = "2024-08-16"  # HKEX real-time northbound flow disclosure termination


def _clear_proxy_env():
    for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY",
              "all_proxy", "ALL_PROXY"):
        os.environ.pop(k, None)


def _basic(df):
    if df is None:
        return None
    n = len(df)
    if n == 0:
        return {"rows": 0}
    return {"rows": int(n), "cols": [str(c) for c in df.columns][:14]}


def _probe(name, fn, *args, **kwargs):
    rec = {"probe": name, "status": "fail", "error": None}
    t0 = time.time()
    try:
        df = fn(*args, **kwargs)
        d = _basic(df)
        if d is None:
            rec["error"] = "returned None"
        else:
            rec.update(d)
            rec["status"] = "ok" if d.get("rows", 0) > 0 else "fail"
            if d.get("rows", 0) == 0:
                rec["error"] = "empty result"
    except Exception as e:
        rec["error"] = f"{type(e).__name__}: {str(e)[:300]}"
    rec["elapsed_s"] = round(time.time() - t0, 1)
    return rec, (df if rec["status"] == "ok" else None)


def _series_depth(df, date_col_hint="日期"):
    """Depth face for a dated series frame (date column + first/last)."""
    if df is None or len(df) == 0:
        return None
    date_col = next((c for c in df.columns
                     if "日" in str(c) or "date" in str(c).lower()
                     or "持股日期" in str(c)), df.columns[0])
    s = df[date_col].astype(str)
    return {"rows": int(len(df)), "first": s.iloc[0], "last": s.iloc[-1],
            "date_col": str(date_col)}


def _policy_face(df):
    """Post-policy degeneracy check: per column, count non-null non-zero
    values strictly after POLICY_DATE. dict col -> {n, n_alive, sample_latest}.
    """
    if df is None or len(df) == 0:
        return None
    date_col = next((c for c in df.columns
                     if "日" in str(c) or "date" in str(c).lower()), df.columns[0])
    try:
        dates = df[date_col].astype(str)
        mask = dates > POLICY_DATE
    except Exception:
        return {"error": "date compare failed"}
    post = df[mask]
    out = {"post_rows": int(mask.sum()), "cols": {}}
    for c in df.columns:
        if c == date_col:
            continue
        try:
            vals = post[c].dropna()
            nn = vals[vals.apply(lambda v: str(v).strip() not in ("", "0", "0.0", "-", "nan", "None"))]
            alive = int(len(nn))
        except Exception:
            alive = -1
        out["cols"][str(c)] = {"post_n": int(len(post)), "alive_n": alive}
    return out


def run():
    import akshare as ak
    _clear_proxy_env()
    probes = []
    results = {}

    # 1. hist_em full series + policy face
    rec, df = _probe("1.hsgt_hist_em:北向资金", ak.stock_hsgt_hist_em, symbol="北向资金")
    probes.append(rec)
    if df is not None:
        rec["series"] = _series_depth(df)
        rec["tail_dates"] = [str(x) for x in df.iloc[-3:, 0].tolist()]
        rec["policy_face"] = _policy_face(df)
        results["hist_em_tail"] = df.tail(3).astype(str).to_dict("records")
    time.sleep(SLEEP_S)

    # 2. fund_flow_summary_em
    rec, df = _probe("2.hsgt_fund_flow_summary_em", ak.stock_hsgt_fund_flow_summary_em)
    probes.append(rec)
    if df is not None:
        rec["series"] = _series_depth(df)
    time.sleep(SLEEP_S)

    # 3. fund_min_em (intraday face -- policy-dead hypothesis)
    rec, df = _probe("3.hsgt_fund_min_em:北向资金", ak.stock_hsgt_fund_min_em, symbol="北向资金")
    probes.append(rec)
    if df is not None:
        rec["series"] = _series_depth(df)
        if len(df):
            rec["tail_rows"] = df.tail(2).astype(str).to_dict("records")
    time.sleep(SLEEP_S)

    # 4. hold_stock_em retry (R58 leg F TypeError fix: 北向 + 持股市值)
    rec, df = _probe("4.hsgt_hold_stock_em:北向/持股市值",
                     ak.stock_hsgt_hold_stock_em, market="北向", indicator="持股市值")
    probes.append(rec)
    if df is not None and len(df):
        rec["head_rows"] = df.head(2).astype(str).to_dict("records")
    time.sleep(SLEEP_S)

    # 5. stock_statistics_em recent window (freshness check)
    end = dt.date.today().strftime("%Y%m%d")
    start = (dt.date.today() - dt.timedelta(days=20)).strftime("%Y%m%d")
    rec, df = _probe("5.hsgt_stock_statistics_em:沪股通/recent20d",
                     ak.stock_hsgt_stock_statistics_em, symbol="沪股通",
                     start_date=start, end_date=end)
    probes.append(rec)
    if df is not None:
        rec["series"] = _series_depth(df)
    time.sleep(SLEEP_S)

    # 6. individual_detail_em latest-date re-verify (R58 leg E said 2024-09-30)
    rec, df = _probe("6.hsgt_individual_detail_em:600519",
                     ak.stock_hsgt_individual_detail_em, symbol="600519")
    probes.append(rec)
    if df is not None:
        rec["series"] = _series_depth(df)
        if len(df):
            rec["head_dates"] = [str(x) for x in df.iloc[:3, 0].tolist()]

    payload = {
        "probe_ts": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "law": "E3 P3-queue (state/queue/explore.md) + R58 moneyflow_source_probe residual scope",
        "policy_anchor": "HKEX terminated real-time northbound flow disclosure 2024-08-16",
        "probes": probes,
        "verdict_notes": "see digest for candidate rating",
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    print(f"wrote {OUT}")
    for p in probes:
        print(f"  {p['probe']}: {p['status']} rows={p.get('rows')} "
              f"{p.get('series', {}).get('first', '')}..{p.get('series', {}).get('last', '')} "
              f"{('err=' + p['error'][:80]) if p.get('error') else ''}")
    return 0


def selftest():
    """Offline machinery check: target fns exist, param signatures, no network."""
    import akshare as ak
    ok = 0
    checks = [
        ("stock_hsgt_hist_em", ["symbol"]),
        ("stock_hsgt_fund_flow_summary_em", []),
        ("stock_hsgt_fund_min_em", ["symbol"]),
        ("stock_hsgt_hold_stock_em", ["market", "indicator"]),
        ("stock_hsgt_stock_statistics_em", ["symbol", "start_date", "end_date"]),
        ("stock_hsgt_individual_detail_em", ["symbol"]),
    ]
    n = len(checks)
    for name, expect_params in checks:
        fn = getattr(ak, name, None)
        if fn is None:
            print(f"  [FAIL] {name}: missing")
            continue
        import inspect
        params = list(inspect.signature(fn).parameters)
        if expect_params and not set(expect_params).issubset(set(params)):
            print(f"  [FAIL] {name}: params {params} != expect {expect_params}")
            continue
        ok += 1
    # policy-face function unit check on synthetic frame
    import pandas as pd
    df = pd.DataFrame({"日期": ["2024-08-15", "2024-08-19", "2026-01-05"],
                       "v": [1.0, 0.0, 3.0], "dead": [1.0, 0.0, 0.0]})
    pf = _policy_face(df)
    assert pf["post_rows"] == 2
    assert pf["cols"]["v"]["alive_n"] == 1, pf
    assert pf["cols"]["dead"]["alive_n"] == 0, pf
    ok += 1
    print(f"selftest: {ok}/{n + 1} PASS")
    return 0 if ok == n + 1 else 1


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "run"
    if mode == "selftest":
        sys.exit(selftest())
    sys.exit(run())
