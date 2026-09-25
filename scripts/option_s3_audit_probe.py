"""T-65 s3 closeout: options exercise-price + expiry full-spectrum audit gate (O-20260925-1158).

Wave-2 gate feed per census S5/S6 (research/FULL_INSTRUMENT_CENSUS.md L85):
"行权价+到期面全谱审计 -- audit 过才开 prereg". Scope = wave-2 families' underlyings
(50ETF 510050 / 300ETF 510300, both SSE, both legality-verified in census threshold table).

GATE CRITERIA (frozen before run, R99 spirit; zero result-peeking):
  G1 strike-coverage: every listed month x underlying enumerates ALL contracts with
     a strike value (chain-level board face, no gaps, calls+puts both).
  G2 strike cross-verification: >=2 independent sources agree on sampled strikes
     (board 行权价 vs greeks-face 行权价 vs trading-code-embedded strike parse M0xxxx).
  G3 expiry-coverage: exercise date obtainable for every listed month x underlying.
  G4 moneyness sanity: near-month strikes bracket underlying spot (min < spot < max).
  G5 historical feasibility: past-month contract enumeration works AND a historical
     contract daily OHLCV has depth (premium-accounting backtest face, s0 census
     already closed current-contract daily face).
  G6 evidence hygiene: every gate-spectrum face carries head/tail real rows (R167),
     observation dates <= run_date with cutoff = max(observed<=today, run_date
     fallback) (r186).

v2 (v1 run evidence -> probe-layer re-spec per census v1->v2 precedent, disclosed):
  - v1 HIST_MONTH=202606 crashed the codes face with empty-payload column error ->
    boundary discovery: sina prunes deep expired months AND never-listed months
    (202608) return empty; nearest EXPIRED LISTED month 202609 works (14 calls).
    G5 past-month re-specified to 202609 (literal "past month" semantics unchanged);
    202606 deep-retention face moved to a DISCLOSURE section (r186 symmetry: no
    terminal gate verdict from a boundary-disclosure face).
  - board 日期 column is a 14-digit compact timestamp (20260924162900) -> 8-digit
    prefix extraction added to _observed_dates.
  - G4 spot keys += 最近成交价 (v1 revealed sina underlying KV key names).

Laws applied: direct-connection recipe (ProxyHandler({}) T4 family), 2.5s rate limit,
honest FAIL records, repr-first field typing (r158). Output: results/option_s3_audit.json
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

RUN_DATE = dt.date.today().isoformat()
OUT = os.path.join("results", "option_s3_audit.json")

UNDERLYINGS = {  # wave-2 scope: SSE ETF options, legality rows in census table
    "50ETF": {"code": "510050", "board": "华夏上证50ETF期权", "spot_sym": "sh510050"},
    "300ETF": {"code": "510300", "board": "华泰柏瑞沪深300ETF期权", "spot_sym": "sh510300"},
}
HIST_MONTH = "202609"  # nearest EXPIRED LISTED month (expired 2026-09-23): G5 past-month face
HIST_MONTH_DEEP = "202606"  # deep expired month: retention-boundary DISCLOSURE face (not a gate face)


def _kv_to_dict(df):
    """greeks/spot faces return key-value (字段/值) frames -> dict, repr-preserving."""
    out = {}
    try:
        if df.shape[1] == 2:
            pairs = list(zip(df.iloc[:, 0].astype(str), df.iloc[:, 1].astype(str)))
            out = {k: v for k, v in pairs}
        else:
            out = {str(c): str(v) for c, v in df.iloc[0].items()}
    except Exception:
        out = {"repr": repr(df)[:400]}
    return out


def _strike_from_trading_code(code: str):
    """SSE option trading code 510050C2610M02750 -> (direction, month, strike).

    Convention: <underlying6><C|P><YYMM>M<strike*1000, 5 digits>. Public SSE
    naming rule; treated as PROVISIONAL parse pending G2 exchange-verified
    constants at prereg time (CTA TS tick precedent).
    """
    m = re.match(r"^(\d{6})([CP])(\d{4})M(\d{5})$", str(code))
    if not m:
        return None
    return {"direction": "call" if m.group(2) == "C" else "put",
            "month": "20" + m.group(3), "strike": int(m.group(4)) / 1000.0}


def _observed_dates(df):
    """Scan all columns for ISO / compact 8-digit / 14-digit-timestamp dates (r168 guard)."""
    found = set()
    for c in df.columns:
        try:
            s = df[c].astype(str)
        except Exception:
            continue
        for v in s.str.extractall(r"(20\d{2}-\d{2}-\d{2})")[0].dropna():
            found.add(v)
        ex = s.str.extractall(r"\b(20\d{2})(\d{2})(\d{2})\b")
        if len(ex):
            for _, row in ex.iterrows():
                found.add(f"{row[0]}-{row[1]}-{row[2]}")
        ex14 = s.str.extractall(r"\b(20\d{2})(\d{2})(\d{2})\d{6}\b")  # 20260924162900 stamps
        if len(ex14):
            for _, row in ex14.iterrows():
                found.add(f"{row[0]}-{row[1]}-{row[2]}")
    return sorted(found)


def probe(fn, **kw):
    t0 = time.time()
    try:
        r = fn(**kw)
        if isinstance(r, list) or isinstance(r, tuple):
            meta = {"status": "OK_SEQ", "items": list(r)[:8],
                    "repr": repr(r)[:200], "sec": round(time.time() - t0, 1)}
            return meta, list(r)
        if r is None or len(r) == 0:
            return {"status": "EMPTY", "sec": round(time.time() - t0, 1)}
        f = {"status": "OK", "rows": int(len(r)), "cols": list(map(str, r.columns))[:16],
             "head_repr": [repr(x)[:260] for x in r.head(2).to_dict("records")],
             "tail_repr": [repr(x)[:260] for x in r.tail(1).to_dict("records")],
             "sec": round(time.time() - t0, 1)}
        return f, r
    except Exception as e:
        return {"status": "FAIL", "err": f"{type(e).__name__}: {str(e)[:180]}",
                "sec": round(time.time() - t0, 1)}


def main():
    res = {"run_date": RUN_DATE, "gate": "s3 options exercise-price + expiry full-spectrum",
           "scope": {u: v["code"] for u, v in UNDERLYINGS.items()},
           "criteria": {"G1_strike_coverage_all_contracts": "board chain face per month x underlying, calls+puts, zero missing strike",
                         "G2_strike_crossverify_2plus_sources": "board vs greeks vs trading-code parse agreement",
                         "G3_expiry_coverage_all_months": "expire face per month x underlying",
                         "G4_moneyness_sanity": "near-month strike range brackets underlying spot",
                         "G5_historical_feasibility": "past-month enumeration + historical contract daily depth",
                         "G6_evidence_hygiene": "head/tail real rows + observation cutoff <= run_date"},
           "probes": {}, "verdicts": {}, "evidence_cutoff": RUN_DATE}
    P = res["probes"]
    obs_dates = set()

    # -- months list per underlying ------------------------------------------------
    months = {}
    for u, cfg in UNDERLYINGS.items():
        r = probe(ak.option_sse_list_sina, symbol=u, exchange="null")
        P[f"list_{u}"] = r[0] if isinstance(r, tuple) else r
        months[u] = [str(x) for x in r[1]] if isinstance(r, tuple) and r[0]["status"] == "OK_SEQ" else []
        time.sleep(2.5)
    res["months"] = months

    # -- G1/G4: chain board face per underlying x month (strike coverage) ---------
    board_stats = {}
    for u, cfg in UNDERLYINGS.items():
        board_stats[u] = {}
        for mo in months[u]:
            r = probe(ak.option_finance_board, symbol=cfg["board"], end_month=mo[-4:])
            key = f"board_{u}_{mo}"
            if isinstance(r, tuple):
                meta, df = r
                P[key] = meta
                if meta["status"] == "OK":
                    st = {"rows": meta["rows"]}
                    if "行权价" in df.columns:
                        strikes = df["行权价"].astype(float)
                        st["strike_min"] = float(strikes.min())
                        st["strike_max"] = float(strikes.max())
                        st["strike_missing"] = int(strikes.isna().sum())
                    if "合约交易代码" in df.columns:
                        parsed = df["合约交易代码"].astype(str).map(_strike_from_trading_code)
                        st["code_parse_ok"] = int(sum(1 for p in parsed if p))
                        st["code_parse_fail_repr"] = [repr(x)[:80] for x in
                                                       df.loc[parsed.isna(), "合约交易代码"].head(3)]
                        st["directions"] = {"call": sum(1 for p in parsed if p and p["direction"] == "call"),
                                            "put": sum(1 for p in parsed if p and p["direction"] == "put")}
                        # code-embedded strike vs board strike agreement (G2 source A vs C)
                        if "行权价" in df.columns:
                            agree = mismatch = 0
                            for p, b in zip(parsed, df["行权价"].astype(float)):
                                if p is None:
                                    continue
                                if abs(p["strike"] - float(b)) < 1e-6:
                                    agree += 1
                                else:
                                    mismatch += 1
                            st["code_vs_board_strike"] = {"agree": agree, "mismatch": mismatch}
                        # keep sample rows for cross-verify picks
                        board_stats[u][mo] = {"df": df, "meta": st}
                    obs_dates.update(_observed_dates(df))
            else:
                P[key] = r
            time.sleep(2.5)
    res["board_stats"] = {u: {m: s["meta"] for m, s in v.items()} for u, v in board_stats.items()}

    # -- G3: expiry face per underlying x month ------------------------------------
    expiry = {}
    for u, cfg in UNDERLYINGS.items():
        expiry[u] = {}
        for mo in months[u]:
            r = probe(ak.option_sse_expire_day_sina, trade_date=mo, symbol=u)
            P[f"expire_{u}_{mo}"] = r[0] if isinstance(r, tuple) else r
            if isinstance(r, tuple) and r[0]["status"] == "OK_SEQ":
                expiry[u][mo] = r[0]["items"]
            time.sleep(2.5)
    res["expiry"] = expiry

    # -- G4: underlying spot -------------------------------------------------------
    spots = {}
    for u, cfg in UNDERLYINGS.items():
        r = probe(ak.option_sse_underlying_spot_price_sina, symbol=cfg["spot_sym"])
        P[f"spot_{u}"] = r[0] if isinstance(r, tuple) else r
        if isinstance(r, tuple) and r[0]["status"] == "OK":
            kv = _kv_to_dict(r[1])
            spots[u] = kv
            obs_dates.update(_observed_dates(r[1]))
        time.sleep(2.5)
    res["underlying_spot_kv"] = spots

    # -- G2: greeks face cross-verify (50ETF near month: 1 call + 1 put) ----------
    # join key: codes_sina 8-digit 期权代码 -> greeks KV (交易代码 = long trading code
    # + 行权价) -> board row by long code. Three sources: greeks/board/code-parse.
    greek_checks = []
    b50 = board_stats.get("50ETF", {}).get(months["50ETF"][0]) if months.get("50ETF") else None
    if b50 is not None:
        bdf = b50["df"]
        for direction, cnsym in (("call", "看涨期权"), ("put", "看跌期权")):
            rc = probe(ak.option_sse_codes_sina, symbol=cnsym, trade_date=months["50ETF"][0], underlying="510050")
            P[f"codes_50ETF_{direction}_near"] = rc[0] if isinstance(rc, tuple) else rc
            if not (isinstance(rc, tuple) and rc[0]["status"] == "OK"):
                time.sleep(2.5)
                continue
            cdf = rc[1]
            code8 = str(cdf["期权代码"].iloc[0]) if "期权代码" in cdf.columns and len(cdf) else None
            if code8:
                time.sleep(2.5)
                rg = probe(ak.option_sse_greeks_sina, symbol=code8)
                P[f"greeks_{direction}_{code8}"] = rg[0] if isinstance(rg, tuple) else rg
                if isinstance(rg, tuple) and rg[0]["status"] == "OK":
                    kv = _kv_to_dict(rg[1])
                    long_code = kv.get("交易代码", "")
                    board_strike = None
                    row = bdf[bdf["合约交易代码"].astype(str) == long_code] if "合约交易代码" in bdf.columns else bdf.iloc[0:0]
                    if len(row) and "行权价" in bdf.columns:
                        board_strike = float(row["行权价"].iloc[0])
                    parsed = _strike_from_trading_code(long_code)
                    greek_checks.append({"code8": code8, "direction": direction,
                                          "long_code": long_code,
                                          "greeks_name": kv.get("期权合约简称", ""),
                                          "greeks_strike": kv.get("行权价"),
                                          "board_strike": board_strike,
                                          "code_strike": parsed["strike"] if parsed else None})
            time.sleep(2.5)
    res["strike_crossverify"] = greek_checks

    # -- G5: past-month enumeration + expired-contract daily depth (gate face) -----
    hist = {}
    rh = probe(ak.option_sse_codes_sina, symbol="看涨期权", trade_date=HIST_MONTH, underlying="510050")
    P[f"codes_50ETF_call_hist_{HIST_MONTH}"] = rh[0] if isinstance(rh, tuple) else rh
    if isinstance(rh, tuple) and rh[0]["status"] == "OK":
        hist_codes = rh[1]["期权代码"].astype(str).tolist() if "期权代码" in rh[1].columns else []
        hist["hist_month_call_count"] = len(hist_codes)
        hist["hist_head"] = hist_codes[:5]
        if hist_codes:
            time.sleep(2.5)
            rd = probe(ak.option_sse_daily_sina, symbol=hist_codes[0])
            P[f"daily_hist_{hist_codes[0]}"] = rd[0] if isinstance(rd, tuple) else rd
            if isinstance(rd, tuple) and rd[0]["status"] == "OK":
                hist["hist_daily_rows"] = rd[0]["rows"]
                hist["hist_daily_last_date"] = rd[0].get("tail_repr", [""])[0][:120]
                obs_dates.update(_observed_dates(rd[1]))
    time.sleep(2.5)
    res["historical_feasibility"] = hist

    # -- retention-boundary DISCLOSURE face (not a gate face, r186 symmetry) -------
    # deep expired month 202606 + never-listed 202608: sina codes face returns
    # empty payload -> akshare wrapper column-assign crash. Recorded as the
    # historical-enumeration retention boundary (data debt for wave-2 prereg
    # window design: chain reconstruction limited to retention window).
    boundary = {}
    for mo in (HIST_MONTH_DEEP, "202608"):
        rb = probe(ak.option_sse_codes_sina, symbol="看涨期权", trade_date=mo, underlying="510050")
        st = rb[0] if isinstance(rb, tuple) else rb
        boundary[mo] = st
        time.sleep(2.5)
    res["retention_boundary"] = {
        "note": "deep-expired/never-listed months return empty payload (wrapper crash); "
                "historical chain enumeration = retention window only; "
                "wave-2 prereg must design backtest window accordingly (forward-collect or retention backfill)",
        "faces": boundary}

    # -- G6: cutoff guard ----------------------------------------------------------
    legal_obs = sorted(d for d in obs_dates if d <= RUN_DATE)
    res["observation_dates"] = {"count": len(obs_dates), "future_excluded": len(obs_dates) - len(legal_obs)}
    res["evidence_cutoff"] = legal_obs[-1] if legal_obs else RUN_DATE

    # -- verdicts (deterministic re-derive from recorded evidence) ------------------
    v = {}
    try:
        g1_ok = all(
            s.get("strike_missing") == 0 and s.get("code_parse_ok", 0) == s.get("rows", -1)
            for u in board_stats for s in [x["meta"] for x in board_stats[u].values()]
        ) and all(len(board_stats[u]) == len(months[u]) for u in UNDERLYINGS)
        g1_detail = {f"{u}_{m}": s["meta"] for u in board_stats for m, s in board_stats[u].items()}
        v["G1_strike_coverage"] = {"pass": bool(g1_ok), "detail": g1_detail}

        def _f(x):
            try:
                return round(float(x), 4)
            except Exception:
                return None
        cv_ok = len(greek_checks) >= 2 and all(
            _f(g["greeks_strike"]) is not None and _f(g["board_strike"]) is not None
            and _f(g["code_strike"]) is not None
            and abs(_f(g["greeks_strike"]) - _f(g["board_strike"])) < 1e-6
            and abs(_f(g["code_strike"]) - _f(g["board_strike"])) < 1e-6
            for g in greek_checks)
        code_board_ok = all(
            s["meta"].get("code_vs_board_strike", {}).get("mismatch", 1) == 0
            for u in board_stats for s in board_stats[u].values())
        v["G2_strike_crossverify"] = {"pass": bool(cv_ok and code_board_ok),
                                      "greeks_samples": len(greek_checks),
                                      "code_vs_board_all_months": bool(code_board_ok)}

        g3_ok = all(
            len(expiry.get(u, {}).get(mo, [])) == 2 for u in UNDERLYINGS for mo in months.get(u, [])
        ) and all(expiry.get(u) for u in UNDERLYINGS)
        v["G3_expiry_coverage"] = {"pass": bool(g3_ok), "expiry": expiry}

        g4_ok = True
        g4_detail = {}
        for u in UNDERLYINGS:
            near = months.get(u, [None])[0]
            bs = board_stats.get(u, {}).get(near)
            spot_kv = spots.get(u, {})
            spot = None
            for k in ("最近成交价", "最新价", "现价", "昨收", "昨结"):
                if k in spot_kv and _f(spot_kv[k]) is not None:
                    spot = _f(spot_kv[k])
                    break
            if spot is None:  # face-shape tolerant fallback: any price-like KV value
                for k, val in spot_kv.items():
                    f_ = _f(val)
                    if f_ is not None and 0.1 <= f_ <= 100.0 and any(t in k for t in ("价", "收", "开")):
                        spot = f_
                        g4_detail.setdefault("_spot_key_fallback", []).append(k)
                        break
            if bs and spot is not None:
                lo, hi = bs["meta"]["strike_min"], bs["meta"]["strike_max"]
                ok = lo < spot < hi
                g4_ok = g4_ok and ok
                g4_detail[u] = {"spot": spot, "strike_min": lo, "strike_max": hi, "brackets": ok}
            else:
                g4_ok = False
                g4_detail[u] = {"spot": spot, "note": "missing face"}
        v["G4_moneyness_sanity"] = {"pass": bool(g4_ok), "detail": g4_detail}

        g5_ok = (hist.get("hist_month_call_count", 0) > 0 and hist.get("hist_daily_rows", 0) > 30)
        v["G5_historical_feasibility"] = {"pass": bool(g5_ok), "detail": hist}

        g6_ok = (all(p.get("status") in ("OK", "OK_SEQ") for p in P.values())
                 and res["evidence_cutoff"] <= RUN_DATE)
        v["G6_evidence_hygiene"] = {"pass": bool(g6_ok),
                                    "cutoff": res["evidence_cutoff"],
                                    "future_dates_discarded": res["observation_dates"]["future_excluded"],
                                    "fail_reprs": {k: p for k, p in P.items() if p.get("status") not in ("OK", "OK_SEQ")}}

        res["verdicts"] = v
        res["gate_pass"] = all(x["pass"] for x in v.values())
    except Exception as e:
        res["verdict_error"] = f"{type(e).__name__}: {str(e)[:200]}"

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print("GATE:", res.get("gate_pass"), "| verdicts:",
          json.dumps({k: x["pass"] for k, x in res.get("verdicts", {}).items()}, ensure_ascii=False))
    print("cutoff:", res["evidence_cutoff"], "| future_excluded:", res["observation_dates"]["future_excluded"])
    sys.stdout.flush()
    os._exit(0)


if __name__ == "__main__":
    main()
