"""Money-flow data-source audit probe (R58 bm-a, claim MSG-20260924-0830).

Probe-only, zero-engine, zero-ledger (r39 heat-source-audit / R47 futures-probe
precedent). Verifies availability + history depth + throttle risk for the
money-flow source family (SHORTLINE_PLAYBOOK P-3 lane, O-1620 GM-approved):

  A. individual stock main-fund-flow history  -> push2his.eastmoney.com
     (ak.stock_individual_fund_flow)
  B. sector fund-flow history                 -> push2his.eastmoney.com
     (ak.stock_sector_fund_flow_hist)
  C. market-wide fund-flow history            -> push2his.eastmoney.com
     (ak.stock_market_fund_flow)
  D. northbound hist (stop-date verify,       -> datacenter-web.eastmoney.com
     playbook frozen premise: real-time       (ak.stock_hsgt_hist_em)
     disclosure stopped 2024-08)
  E. northbound per-stock holding detail      -> datacenter-web.eastmoney.com
     (replacement channel)                    (ak.stock_hsgt_individual_detail_em)
  F. northbound holdings rank snapshot        -> datacenter-web.eastmoney.com
     (ak.stock_hsgt_hold_stock_em)

Network rules (r39/r40/R34 audit precedents):
- Direct connection (proxy env cleared + no-proxy opener) -- Clash hijack lesson.
- >=3.0s polite sleep between probes (EM push2 sensitivity, r40 throttle law).
- Judge probe life by stdout artifacts, never by tqdm/exit alone (r39 trap).
- Per-probe failures recorded honestly; script exit 0 = machinery wrote JSON,
  exit 2 = machinery failure. Exit code is NOT a probe verdict.

Usage: python scripts/moneyflow_source_probe.py [selftest|run]
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
import time
import traceback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "shortline", "moneyflow_source_probe.json")

SLEEP_S = 3.0
PROBE_TS = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _clear_proxy_env():
    for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY",
              "all_proxy", "ALL_PROXY"):
        os.environ.pop(k, None)


def _depth(df):
    """Common depth extraction: rows/first/last/cols from a dated DataFrame."""
    if df is None:
        return None
    n = len(df)
    if n == 0:
        return {"rows": 0}
    date_col = next((c for c in df.columns if "日" in str(c) or "date" in str(c).lower()), df.columns[0])
    return {"rows": int(n), "first": str(df[date_col].iloc[0]), "last": str(df[date_col].iloc[-1]),
            "cols": [str(c) for c in df.columns][:12]}


def _probe(name, fn, *args, **kwargs):
    """One probe with honest error capture. Returns dict(status=ok|fail, ...)."""
    rec = {"probe": name, "status": "fail", "error": None}
    t0 = time.time()
    try:
        df = fn(*args, **kwargs)
        d = _depth(df)
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
    print(f"[{rec['status'].upper():4}] {name}: rows={rec.get('rows')} "
          f"first={rec.get('first')} last={rec.get('last')} err={rec['error']}")
    return rec


def run():
    import akshare as ak
    _clear_proxy_env()
    probes: list = []

    # A. individual main-fund-flow history (push2his) -- 3 representative names
    for stock, mkt in (("000001", "sz"), ("600519", "sh"), ("300750", "sz")):
        probes.append(_probe(f"A.individual_fund_flow:{stock}",
                             ak.stock_individual_fund_flow, stock=stock, market=mkt))
        time.sleep(SLEEP_S)

    # B. sector fund-flow history (push2his)
    probes.append(_probe("B.sector_fund_flow_hist:汽车服务",
                         ak.stock_sector_fund_flow_hist, symbol="汽车服务"))
    time.sleep(SLEEP_S)

    # C. market-wide fund-flow history (push2his)
    probes.append(_probe("C.market_fund_flow", ak.stock_market_fund_flow))
    time.sleep(SLEEP_S)

    # D. northbound aggregate hist -- stop-date verification (datacenter-web)
    probes.append(_probe("D.hsgt_hist_em:北向资金",
                         ak.stock_hsgt_hist_em, symbol="北向资金"))
    time.sleep(SLEEP_S)

    # E. northbound per-stock holding detail -- replacement channel depth
    #    (start 2014-11 = HK-Connect launch era; honest depth probe)
    probes.append(_probe("E.hsgt_individual_detail:600519",
                         ak.stock_hsgt_individual_detail_em,
                         symbol="600519", start_date="20141101",
                         end_date=dt.date.today().strftime("%Y%m%d")))
    time.sleep(SLEEP_S)

    # F. northbound holdings rank snapshot (datacenter-web)
    probes.append(_probe("F.hsgt_hold_stock_rank:沪股通/今日排行",
                         ak.stock_hsgt_hold_stock_em,
                         market="沪股通", indicator="今日排行"))
    time.sleep(SLEEP_S)

    n_ok = sum(1 for p in probes if p["status"] == "ok")
    payload = {
        "probe_ts": PROBE_TS,
        "lane": "moneyflow_source_audit",
        "claim": "MSG-20260924-0830 (R58 bm-a, F-04)",
        "domain_map": {
            "A/B/C_fund_flow": "push2his.eastmoney.com (known intermittent, R34/r40)",
            "D/E/F_hsgt": "datacenter-web.eastmoney.com (proven working domain, r39)",
        },
        "northbound_premise": "playbook frozen: real-time disclosure stopped 2024-08 -> replacement channel = per-stock holding detail (E)",
        "probes": probes,
        "summary": {"n_probes": len(probes), "n_ok": n_ok,
                    "n_fail": len(probes) - n_ok},
        "notes": [
            "probe-only: NO data files written, pipeline/prereg belongs to a future batch",
            "throttle 3.0s/probe honored; direct connection (no-proxy opener + env cleared)",
        ],
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    os.replace(tmp, OUT)
    print(f"written: {OUT} (ok {n_ok}/{len(probes)})")
    return 0


def probe2():
    """Targeted follow-up probes (R58, after first-run findings).

    F1: D-tail -- what does the northbound aggregate series contain after the
        per-stock disclosure stop (values sample, honest).
    F2: E-minmax -- true date span of per-stock holding detail (min/max of the
        date column, unique dates, rows/day -> institution-level semantics).
    F3: F-retry -- holdings rank snapshot with akshare default indicator.
    F4: B-retry -- sector fund-flow hist single retry (transient vs persistent).
    """
    import akshare as ak
    import pandas as pd
    _clear_proxy_env()
    out = {"probe_ts": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
           "mode": "probe2", "items": {}}

    # F1: northbound aggregate tail
    try:
        df = ak.stock_hsgt_hist_em(symbol="北向资金")
        tail = df.tail(8).to_dict(orient="records")
        # recent rows after disclosure stop: sample values
        out["items"]["F1_hsgt_tail"] = {
            "status": "ok", "rows": int(len(df)),
            "cols": [str(c) for c in df.columns][:10],
            "tail_8": [{k: (str(v) if pd.isna(v) is not True and not isinstance(v, (int, float)) else v)
                        for k, v in r.items()} for r in tail],
        }
        print("[F1] tail rows dumped")
    except Exception as e:
        out["items"]["F1_hsgt_tail"] = {"status": "fail", "error": f"{type(e).__name__}: {str(e)[:200]}"}
        print(f"[F1] FAIL {e}")
    time.sleep(SLEEP_S)

    # F2: per-stock detail true span
    try:
        df = ak.stock_hsgt_individual_detail_em(
            symbol="600519", start_date="20141101",
            end_date=dt.date.today().strftime("%Y%m%d"))
        dcol = "持股日期"
        dates = pd.to_datetime(df[dcol])
        udates = dates.dt.date.nunique()
        out["items"]["F2_detail_span"] = {
            "status": "ok", "rows": int(len(df)),
            "date_min": str(dates.min().date()), "date_max": str(dates.max().date()),
            "unique_dates": int(udates),
            "rows_per_date_median": float((len(df) / udates) if udates else 0),
            "n_institutions": int(df["机构名称"].nunique()) if "机构名称" in df.columns else None,
        }
        print(f"[F2] span {dates.min().date()}..{dates.max().date()} "
              f"rows={len(df)} uniq_dates={udates}")
    except Exception as e:
        out["items"]["F2_detail_span"] = {"status": "fail", "error": f"{type(e).__name__}: {str(e)[:200]}"}
        print(f"[F2] FAIL {e}")
    time.sleep(SLEEP_S)

    # F3: holdings rank snapshot with default indicator
    try:
        df = ak.stock_hsgt_hold_stock_em(market="沪股通", indicator="5日排行")
        out["items"]["F3_hold_rank_default"] = {
            "status": "ok", "rows": int(len(df)),
            "cols": [str(c) for c in df.columns][:10],
            "head_1": str(df.iloc[0].to_dict())[:300] if len(df) else "",
        }
        print(f"[F3] ok rows={len(df)}")
    except Exception as e:
        out["items"]["F3_hold_rank_default"] = {"status": "fail", "error": f"{type(e).__name__}: {str(e)[:200]}"}
        print(f"[F3] FAIL {e}")
    time.sleep(SLEEP_S)

    # F4: sector fund-flow retry (transient vs persistent)
    try:
        df = ak.stock_sector_fund_flow_hist(symbol="汽车服务")
        d = _depth(df)
        out["items"]["F4_sector_retry"] = {"status": "ok", **d}
        print(f"[F4] ok rows={d.get('rows')}")
    except Exception as e:
        out["items"]["F4_sector_retry"] = {"status": "fail", "error": f"{type(e).__name__}: {str(e)[:200]}"}
        print(f"[F4] FAIL {e}")

    path = os.path.join(ROOT, "results", "shortline", "moneyflow_source_probe2.json")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)
    print(f"written: {path}")
    return 0


def selftest():
    """Offline checks: zero network. Signatures + domain map + depth helper."""
    import akshare as ak
    import inspect
    checks = []
    for name, need in [
        ("stock_individual_fund_flow", ("stock", "market")),
        ("stock_sector_fund_flow_hist", ("symbol",)),
        ("stock_market_fund_flow", ()),
        ("stock_hsgt_hist_em", ("symbol",)),
        ("stock_hsgt_individual_detail_em", ("symbol", "start_date", "end_date")),
        ("stock_hsgt_hold_stock_em", ("market", "indicator")),
    ]:
        fn = getattr(ak, name, None)
        ok = fn is not None and all(p in inspect.signature(fn).parameters for p in need)
        checks.append((f"sig:{name}", ok))
        src = inspect.getsource(fn)
        want = "datacenter-web" if name.startswith("stock_hsgt") else "push2his"
        checks.append((f"domain:{name}->{want}", want in src))
    # depth helper on a synthetic frame
    import pandas as pd
    df = pd.DataFrame({"日期": ["2020-01-02", "2020-01-03"], "主力净流入": [1.0, -2.0]})
    d = _depth(df)
    checks.append(("depth:synthetic", d["rows"] == 2 and d["first"] == "2020-01-02"))
    empty = _depth(pd.DataFrame({"日期": []}))
    checks.append(("depth:empty-rows0", empty is not None and empty.get("rows") == 0))
    checks.append(("depth:None", _depth(None) is None))
    bad = [(k, v) for k, v in checks if not v]
    for k, v in checks:
        print(("PASS " if v else "FAIL ") + k)
    print(f"selftest: {len(checks)-len(bad)}/{len(checks)} PASS")
    return 0 if not bad else 1


if __name__ == "__main__":
    _clear_proxy_env()
    mode = sys.argv[1] if len(sys.argv) > 1 else "run"
    if mode == "selftest":
        sys.exit(selftest())
    if mode == "probe2":
        try:
            sys.exit(probe2())
        except Exception:
            traceback.print_exc()
            sys.exit(2)
    try:
        sys.exit(run())
    except Exception:
        traceback.print_exc()
        sys.exit(2)
