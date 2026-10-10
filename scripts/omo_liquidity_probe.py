"""OMO (PBOC open-market operations) liquidity face probe -- E4 P3-queue head.

Probe-only, zero-engine, zero-ledger, zero-prereg. Mirrors hsgt_source_probe.py
(r947) / moneyflow_source_probe.py (R58) discipline. Queue item: state/queue/
explore.md E4 "央行公开市场操作流动性指标面（OMO 净投放→REPO 利率联动·REPO_PANEL 消费）".

Faces probed:
  A1-A3. EM datacenter OMO candidates (reportName guess family; akshare removed
         macro_china_gksccz after 0.6.x so the datacenter endpoint is probed
         directly -- first hit wins, later candidates skipped).
  B.    repo_rate_hist (chinamoney repo fixing rate FDR family) -- bank-market
         rate RESPONSE face (not OMO ops itself).
  C.    rate_interbank Shibor O/N (EM/shibor face).
  D.    macro_china_central_bank_balance (monthly PBOC balance sheet; 对其他
         存款性公司债权 column = OMO+MLF+PSL stock face, monthly frequency).
  E.    local linkage face (deterministic, zero network): probe-day join of the
         freshest reachable daily rate face (A net-injection, else B FDR001)
         vs local data/repo_daily/GC001.csv close -- descriptive only, no
         thresholds, no verdicts.

Network rules (r39/r40 precedents): direct connection (proxy env cleared),
>=3.0s polite sleep, 45s timeout jacket, per-face honest error capture.
Exit code is NOT a probe verdict: 0 = machinery wrote JSON, 2 = machinery
failure.

Usage: python scripts/omo_liquidity_probe.py [selftest|run]
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "shortline", "omo_liquidity_probe.json")
GC001_CSV = os.path.join(ROOT, "data", "repo_daily", "GC001.csv")

SLEEP_S = 3.0
TIMEOUT_S = 45.0

EM_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"
EM_CANDIDATES = [
    {"reportName": "RPT_ECONOMY_GKSCCZ", "note": "akshare 0.6.x macro_china_gksccz lineage guess"},
    {"reportName": "RPT_ECONOMY_OPEN_MARKET", "note": "generic open-market guess"},
    {"reportName": "RPT_ECONOMY_OMO", "note": "short-name guess"},
]


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
    return {"rows": int(n), "cols": [str(c) for c in df.columns][:16]}


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


def _series_depth(df):
    """Depth face for a dated frame: auto-locate date-like column, first/last."""
    if df is None or len(df) == 0:
        return None
    def _is_date_col(c):
        s = str(c).lower()
        return any(k in s for k in ("日期", "date", "time", "rq")) or "日" in str(c)
    date_col = next((c for c in df.columns if _is_date_col(c)), df.columns[0])
    s = df[date_col].astype(str)
    return {"rows": int(len(df)), "first": s.iloc[0], "last": s.iloc[-1],
            "date_col": str(date_col)}


def _em_probe(candidate):
    """Direct EM datacenter attempt with honest capture. Returns (rec, rows)."""
    import urllib.parse
    import urllib.request
    params = {
        "columns": "ALL",
        "pageSize": "50",
        "pageNumber": "1",
        "reportName": candidate["reportName"],
        "source": "WEB",
        "client": "WEB",
    }
    url = EM_URL + "?" + urllib.parse.urlencode(params)
    rec = {"probe": f"A.{candidate['reportName']}", "status": "fail",
           "error": None, "note": candidate["note"]}
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0 Safari/537.36",
            "Referer": "https://data.eastmoney.com/cjsj/gksccz.html",
        })
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as r:
            payload = json.loads(r.read().decode("utf-8", errors="replace"))
        rec["http_status"] = r.status
        if not payload.get("success") or not payload.get("result"):
            rec["error"] = f"EM code={payload.get('code')} msg={str(payload.get('message'))[:120]}"
            return rec, None
        data = (payload.get("result") or {}).get("data") or []
        rec["rows"] = len(data)
        rec["pages"] = (payload.get("result") or {}).get("pages")
        rec["count"] = (payload.get("result") or {}).get("count")
        if data:
            rec["cols"] = list(data[0].keys())
            rec["status"] = "ok"
            rec["head_rows"] = data[:2]
            dates = sorted(str(r.get("TRADE_DATE") or r.get("TRADE_DAY")
                               or r.get("DATE") or "") for r in data)
            rec["series"] = {"first": dates[0], "last": dates[-1]}
        else:
            rec["error"] = "success but zero data rows"
    except Exception as e:
        rec["error"] = f"{type(e).__name__}: {str(e)[:300]}"
    rec["elapsed_s"] = round(time.time() - t0, 1)
    return rec, (rec.get("head_rows") if rec["status"] == "ok" else None)


def _frr_direct_probe(label, start, end):
    """Direct chinamoney FrrHis POST for a bounded window.

    Returns record with fdr001_series = {date: value} (deterministic payload
    extraction; zero writes beyond the evidence JSON).
    """
    import urllib.parse
    import urllib.request
    url = "https://www.chinamoney.com.cn/ags/ms/cm-u-bk-currency/FrrHis"
    rec = {"probe": f"B2.FrrHis-direct:{label}", "status": "fail", "error": None,
           "window": [start, end]}
    t0 = time.time()
    try:
        data = urllib.parse.urlencode({"lang": "CN", "startDate": start,
                                        "endDate": end}).encode()
        req = urllib.request.Request(url, data=data, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/108.0.0.0 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
        })
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as r:
            payload = json.loads(r.read().decode("utf-8", errors="replace"))
        recs = payload.get("records") or []
        rec["rows"] = len(recs)
        series = {}
        for r0 in recs:
            m = r0.get("frValueMap") or {}
            d, v = m.get("date"), m.get("FDR001")
            if d and v not in (None, "", "-", "---"):
                try:
                    float(v)
                    series[str(d)[:10]] = v
                except (TypeError, ValueError):
                    continue
        if series:
            rec["status"] = "ok"
            rec["fdr001_series"] = series
            rec["series"] = {"first": min(series), "last": max(series),
                             "n_fdr001": len(series)}
            rec["head_rows"] = [
                {k: (r0.get("frValueMap") or {}).get(k)
                 for k in ("date", "FDR001", "FDR007", "FDR014")}
                for r0 in recs[:2]
            ]
        else:
            rec["error"] = f"records={len(recs)} but zero FDR001 values"
    except Exception as e:
        rec["error"] = f"{type(e).__name__}: {str(e)[:300]}"
    rec["elapsed_s"] = round(time.time() - t0, 1)
    return rec


def _fdr_vs_gc001(fdr_series, gc001_path=GC001_CSV):
    """Deterministic descriptive join: FDR001 (bank-market fixing, annualized %)
    vs GC001 exchange repo close on common dates. Zero thresholds/verdicts."""
    try:
        import pandas as pd
        fdr = pd.Series({k: float(v) for k, v in fdr_series.items()
                         if str(v).strip() not in ("", "-", "None", "nan")})
        fdr.index = fdr.index.astype(str)
        fdr = fdr[~fdr.index.duplicated(keep="last")]
        g = pd.read_csv(gc001_path)
        g["date"] = g["date"].astype(str)
        g = g.set_index("date")["close"].astype(float)
        joined = pd.concat([fdr.rename("fdr001"), g.rename("gc001")], axis=1,
                           join="inner").dropna()
        if len(joined) < 5:
            return {"n": int(len(joined)), "note": "insufficient overlap for stats"}
        spread = joined["gc001"] - joined["fdr001"]
        return {
            "n_common_days": int(len(joined)),
            "window": [joined.index.min(), joined.index.max()],
            "corr": round(float(joined["fdr001"].corr(joined["gc001"])), 4),
            "gc001_mean": round(float(joined["gc001"].mean()), 4),
            "fdr001_mean": round(float(joined["fdr001"].mean()), 4),
            "spread_mean_bp": round(float(spread.mean()) * 100, 1),
            "spread_p95_bp": round(float(spread.quantile(0.95)) * 100, 1),
        }
    except Exception as e:
        return {"error": f"{type(e).__name__}: {str(e)[:200]}"}


def _linkage_face(gc001_path=GC001_CSV):
    """Deterministic local descriptive face: GC001 annualized close stats.

    Zero network, zero thresholds; consumption anchor for any future OMO join.
    Reports: n, coverage, month-end vs mid-month mean close, top-5 spike days.
    """
    try:
        import pandas as pd
        df = pd.read_csv(gc001_path)
        df["date"] = df["date"].astype(str)
        df = df.sort_values("date")
        close = pd.to_numeric(df["close"], errors="coerce")
        d = df.assign(close=close).dropna(subset=["close"])
        d["dom"] = d["date"].str.slice(8, 10).astype(int)
        month_end = d[d["dom"] >= 26]
        mid = d[(d["dom"] >= 10) & (d["dom"] <= 20)]
        top5 = d.nlargest(5, "close")[["date", "close"]]
        return {
            "gc001_csv": "data/repo_daily/GC001.csv",
            "rows": int(len(d)),
            "coverage": [d["date"].iloc[0], d["date"].iloc[-1]],
            "mean_close_ann_pct": round(float(d["close"].mean()), 3),
            "month_end_dom26plus_mean": round(float(month_end["close"].mean()), 3) if len(month_end) else None,
            "mid_month_dom10_20_mean": round(float(mid["close"].mean()), 3) if len(mid) else None,
            "top5_spike_days": top5.astype(str).to_dict("records"),
        }
    except Exception as e:
        return {"error": f"{type(e).__name__}: {str(e)[:200]}"}


def run():
    import akshare as ak
    _clear_proxy_env()
    probes = []
    omo_rows = None

    # A. EM datacenter OMO candidates -- first hit wins
    for cand in EM_CANDIDATES:
        rec, rows = _em_probe(cand)
        probes.append(rec)
        if rec["status"] == "ok":
            omo_rows = rows
            break
        time.sleep(SLEEP_S)

    # B. chinamoney repo fixing rate history via wrapper -- SHORT window
    #    (wide 2020->today span returns zero records -> wrapper KeyError
    #    'frValueMap'; span cap disclosed)
    end = dt.date.today().strftime("%Y%m%d")
    start = (dt.date.today() - dt.timedelta(days=30)).strftime("%Y%m%d")
    rec, df = _probe("B.repo_rate_hist:FDR fixing wrapper 30d",
                     ak.repo_rate_hist, start_date=start, end_date=end)
    probes.append(rec)
    recent_fdr_series = None
    if df is not None:
        rec["series"] = _series_depth(df)
        if len(df):
            rec["tail_rows"] = df.tail(2).astype(str).to_dict("records")
            try:
                recent_fdr_series = {
                    str(d)[:10]: str(v)
                    for d, v in zip(df["date"].astype(str), df["FDR001"].astype(str))
                    if str(v).strip() not in ("", "-", "---", "None", "nan")
                }
            except KeyError:
                recent_fdr_series = None
    time.sleep(SLEEP_S)

    # B2. direct FrrHis depth samples (span-cap face: full-year windows)
    fdr_windows = {}
    for label, s, e in [
        ("2015", "2015-01-01", "2015-12-31"),
        ("2020", "2020-01-01", "2020-12-31"),
    ]:
        rec2 = _frr_direct_probe(label, s, e)
        probes.append(rec2)
        if rec2["status"] == "ok":
            fdr_windows[label] = rec2["fdr001_series"]
        time.sleep(SLEEP_S)

    # C. Shibor face via jin10 aggregate (rate_interbank EM wrapper
    #    KeyError'd on market map -- disclosed; alternative face probed)
    rec, df = _probe("C.macro_china_shibor_all (jin10)", ak.macro_china_shibor_all)
    probes.append(rec)
    if df is not None:
        rec["series"] = _series_depth(df)
        if len(df):
            rec["cols_full"] = [str(c) for c in df.columns][:20]
    time.sleep(SLEEP_S)

    # D. monthly PBOC balance sheet (OMO+MLF stock face)
    rec, df = _probe("D.macro_china_central_bank_balance (monthly)",
                     ak.macro_china_central_bank_balance)
    probes.append(rec)
    if df is not None:
        rec["series"] = _series_depth(df)
        if len(df):
            rec["cols_full"] = [str(c) for c in df.columns]
            rec["tail_row"] = df.tail(1).astype(str).to_dict("records")

    # E. local linkage descriptive face
    linkage = _linkage_face()
    # E2. FDR001 vs GC001 per-window descriptive join (deterministic, local)
    fdr_joins = {}
    for label, series in list(fdr_windows.items()) + [("recent30d", recent_fdr_series)]:
        if series:
            fdr_joins[label] = _fdr_vs_gc001(series)

    payload = {
        "probe_ts": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "law": "E4 P3-queue head (state/queue/explore.md) + R58/hsgt probe bloodline",
        "queue_item": "OMO net-injection -> REPO rate linkage, REPO_PANEL consumption",
        "probes": probes,
        "omo_ops_face_reachable": omo_rows is not None,
        "fdr_direct_windows": {k: {"n": len(v), "first": min(v), "last": max(v)}
                               for k, v in fdr_windows.items()},
        "linkage_face": linkage,
        "fdr_vs_gc001_joins": fdr_joins,
        "verdict_notes": "see digest for honest rating + data-debt register",
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    print(f"wrote {OUT}")
    for p in probes:
        print(f"  {p['probe']}: {p['status']} rows={p.get('rows')} "
              f"{str(p.get('series', {}).get('first', ''))[:10]}..{str(p.get('series', {}).get('last', ''))[:10]} "
              f"{('err=' + str(p.get('error'))[:80]) if p.get('error') else ''}")
    print("linkage:", json.dumps(linkage, ensure_ascii=False)[:300])
    return 0


def selftest():
    """Offline machinery check: signatures + synthetic face checks, no network."""
    import akshare as ak
    import inspect
    import pandas as pd
    import tempfile
    ok = 0
    checks = [
        ("repo_rate_hist", ["start_date", "end_date"]),
        ("macro_china_shibor_all", []),
        ("macro_china_central_bank_balance", []),
    ]
    n = len(checks)
    for name, expect_params in checks:
        fn = getattr(ak, name, None)
        if fn is None:
            print(f"  [FAIL] {name}: missing")
            continue
        params = list(inspect.signature(fn).parameters)
        if expect_params and not set(expect_params).issubset(set(params)):
            print(f"  [FAIL] {name}: params {params} != expect {expect_params}")
            continue
        ok += 1
    # series-depth synthetic check
    df = pd.DataFrame({"日期": ["2026-01-02", "2026-01-03"], "v": [1.0, 2.0]})
    sd = _series_depth(df)
    assert sd["rows"] == 2 and sd["first"] == "2026-01-02", sd
    ok += 1
    # FDR-vs-GC001 join synthetic check (>=5 common days for stats path)
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False,
                                     encoding="utf-8") as f:
        f.write("date,close\n"
                + "".join(f"2026-01-{d:02d},{1.0 + 0.1 * i}\n"
                          for i, d in enumerate((12, 13, 14, 15, 16, 17), start=1)))
        tmp = f.name
    j = _fdr_vs_gc001({f"2026-01-{d:02d}": 1.5 for d in (12, 13, 14, 15, 16, 17)},
                      gc001_path=tmp)
    os.unlink(tmp)
    assert j["n_common_days"] == 6 and j["spread_mean_bp"] == -15.0, j
    ok += 1
    # linkage face on synthetic CSV
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False,
                                     encoding="utf-8") as f:
        f.write("date,close\n2026-01-26,5.0\n2026-01-15,1.5\n2026-02-28,9.0\n")
        tmp = f.name
    lf = _linkage_face(gc001_path=tmp)
    os.unlink(tmp)
    assert lf["rows"] == 3 and lf["month_end_dom26plus_mean"] == 7.0, lf
    assert lf["top5_spike_days"][0]["close"] == "9.0", lf
    ok += 1
    # EM candidate params well-formed
    assert all(set(c) >= {"reportName", "note"} for c in EM_CANDIDATES)
    ok += 1
    print(f"selftest: {ok}/{n + 4} PASS")
    return 0 if ok == n + 4 else 1


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "run"
    if mode == "selftest":
        sys.exit(selftest())
    sys.exit(run())
