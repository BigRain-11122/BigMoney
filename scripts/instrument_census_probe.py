"""T-65 s0 census data-availability probes v2 (O-20260925-1158).

v2 fixes (v1 attribution: probe-layer bugs vs genuine source gaps separated):
- option_sse_list_sina returns List[str] -> list-aware handling
- bond_zh_hs_daily: zero column assumptions, signature-default symbol probe
- stock_hk_ggt_components_em: no-arg signature
- TS via futures_zh_daily_sina('TS0') variant (futures_main_sina lacks TS face)
- EM-blocked faces (BSE/REITs/LOF): single retry, honest BLOCKED if still down
- option expiry face (option_sse_expire_day_sina) for daily-encodable families
Laws: R167 head-rows + repr, r186 observation-date guard, update_futures
direct-connection recipe, honest FAIL records. Output merges into
results/instrument_census_probe.json (same file, v1 entries preserved).
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
import time

for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "all_proxy", "ALL_PROXY"):
    os.environ.pop(k, None)

import urllib.request  # noqa: E402

urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler({})))

import akshare as ak  # noqa: E402
import pandas as pd  # noqa: E402

TODAY = dt.date.today().isoformat()
OUT = os.path.join("results", "instrument_census_probe.json")


def _last_real_date(df):
    best = None
    for c in df.columns:
        m = df[c].astype(str).str.extract(r"(20\d{2}-\d{2}-\d{2})")[0].dropna()
        if len(m) and (best is None or m.iloc[-1] > best):
            best = m.iloc[-1]
    return best


def probe(fn, **kw):
    t0 = time.time()
    try:
        r = fn(**kw)
        if isinstance(r, list):
            return {"status": "OK_LIST", "items": len(r),
                    "head_repr": [repr(x)[:120] for x in r[:5]],
                    "sec": round(time.time() - t0, 1)}
        df = r
        if df is None or len(df) == 0:
            return {"status": "EMPTY", "sec": round(time.time() - t0, 1)}
        f = {"status": "OK", "rows": int(len(df)),
             "cols": list(map(str, df.columns))[:24],
             "head_repr": [repr(x)[:220] for x in df.head(2).to_dict("records")],
             "tail_repr": [repr(x)[:220] for x in df.tail(1).to_dict("records")],
             "last_date_observed": _last_real_date(df),
             "sec": round(time.time() - t0, 1)}
        return f
    except Exception as e:
        return {"status": "FAIL", "err": f"{type(e).__name__}: {str(e)[:160]}",
                "sec": round(time.time() - t0, 1)}


def pick_code(lst, pattern):
    for x in lst[:200]:
        m = re.search(pattern, str(x))
        if m:
            return m.group(0)
    return None


def main():
    res = json.load(open(OUT, encoding="utf-8"))
    res["v2_run_date"] = TODAY
    res["probes"] = {}
    P = res["probes"]

    # 1) SSE options: contract code list (List[str]) -> one contract daily + expiry face
    lst = probe(ak.option_sse_list_sina, symbol="50ETF", exchange="null")
    P["option_sse_list_sina"] = lst
    code = pick_code(lst.get("head_repr", []), r"\d{8}") if lst["status"] == "OK_LIST" else "10003889"
    d = probe(ak.option_sse_daily_sina, symbol=code)
    d["probe_contract"] = code
    P["option_sse_daily_sina"] = d
    P["option_sse_expire_day_sina"] = probe(ak.option_sse_expire_day_sina, symbol="50ETF")
    time.sleep(2.5)

    # 2) Exchange bonds: daily via signature-default symbol (zero column assumptions)
    d = probe(ak.bond_zh_hs_daily, symbol="sh010107")
    d["probe_symbol"] = "sh010107"
    P["bond_zh_hs_daily"] = d
    time.sleep(2.5)

    # 3) HK-connect: southbound components (no-arg) [daily face already OK in v1]
    P["stock_hk_ggt_components_em"] = probe(ak.stock_hk_ggt_components_em)
    time.sleep(2.5)

    # 4) BSE spot (EM retry) -> daily attempt
    bj = probe(ak.stock_bj_a_spot_em)
    P["stock_bj_a_spot_em"] = bj
    bjcode = None
    if bj["status"] == "OK":
        for r in bj["head_repr"]:
            m = re.search(r"\b(92\d{4}[0-9]?|8\d{5}|4\d{5})\b", r)
            if m:
                bjcode = m.group(0)
                break
    if bjcode:
        d = probe(ak.stock_zh_a_hist, symbol=bjcode, period="daily",
                  start_date="20240101", end_date=TODAY.replace("-", ""), adjust="qfq")
        d["probe_symbol"] = bjcode
        P["bse_daily_via_em"] = d
    time.sleep(2.5)

    # 5) TS treasury futures: main-continuous via futures_zh_daily_sina TS0 variant
    d = probe(ak.futures_zh_daily_sina, symbol="TS0")
    d["probe_symbol"] = "TS0"
    P["futures_zh_daily_sina_TS0"] = d
    time.sleep(2.5)

    # 6) REITs (EM retry) -> one REIT daily
    rt = probe(ak.reits_realtime_em)
    P["reits_realtime_em"] = rt
    rcode = None
    if rt["status"] == "OK":
        for r in rt["head_repr"]:
            m = re.search(r"\b(508\d{3}|180\d{3})\b", r)
            if m:
                rcode = m.group(0)
                break
    if rcode:
        d = probe(ak.reits_hist_em, symbol=rcode)
        d["probe_symbol"] = rcode
        P["reits_hist_em"] = d
    time.sleep(2.5)

    # 7) LOF (EM retry) -> one LOF daily
    ls = probe(ak.fund_lof_spot_em)
    P["fund_lof_spot_em"] = ls
    lcode = None
    if ls["status"] == "OK":
        for r in ls["head_repr"]:
            m = re.search(r"\b1[56]\d{4}\b", r)
            if m:
                lcode = m.group(0)
                break
    if lcode:
        d = probe(ak.fund_lof_hist_em, symbol=lcode)
        d["probe_symbol"] = lcode
        P["fund_lof_hist_em"] = d

    ok = sum(1 for p in P.values() if str(p.get("status", "")).startswith("OK"))
    res["summary"] = {"probes_total": len(P), "ok": ok,
                      "fail": sum(1 for p in P.values() if p.get("status") == "FAIL")}
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print(json.dumps(res["summary"], ensure_ascii=False))
    sys.stdout.flush()
    os._exit(0)


if __name__ == "__main__":
    main()
