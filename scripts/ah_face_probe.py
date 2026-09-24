# -*- coding: utf-8 -*-
"""ah_face_probe.py -- T-17 deliverable-1: AH/HK data-face probe-first
validation (single-probe per face, honest-fail labels, zero trials).

Ticket T-2026-09-24-17, spec item 1 (GM order O-20260924-1155, ARB-2
exploration per ARBITRAGE_PLAYBOOK.md; probe-first pattern per T-17 claim
note, r57 early-age, executed r66 after T-16-lane P-A2 blocker resolved
by PA1E honest close r64).

Faces probed (spec list + panel-support faces, one pull each, nothing silent):
  spec-named:
    stock_zh_ah_spot()        -- tencent AH parity (spec's "stock_zh_ah_tx")
    stock_zh_ah_spot_em()     -- eastmoney AH parity alt (push2 family,
                                 same-day persistent-block risk, small window)
    stock_hk_daily()          -- sina HK quotes history leg (spec's
                                 "stock_hk_sina"), single symbol 00700
    stock_hk_spot()           -- sina HK realtime full market
    stock_hsgt_hist_em()      -- HSGT northbound history (spec's
                                 "stock_hsgt_em", push2 family risk)
    Hang Seng AH premium index availability: stock_hk_index_daily_sina with
                                 candidate symbols [HSAHP, HSI, HSCEI, CES100]
                                 + stock_hk_index_daily_em(HSAHP) push2 alt --
                                 per-symbol alive/dead labels (availability
                                 probe per spec, index module)
  panel-support (same lane, needed by deliverable-2/3 pullers):
    stock_zh_ah_name()        -- tencent AH universe list
    stock_zh_ah_daily()       -- tencent AH single-stock history (bounded window)
    fx_quote_baidu()          -- Baidu HKD/CNY quote (FX rate-basis preview)
    fx_spot_quote()           -- chinamoney CNY central parity (HKD row)

FX rate-basis preview (frozen here for deliverable-2, J18-style):
  AH premium convention = A_price(CNY) / (H_price(HKD) * fx_HKD_CNY) - 1,
  premium > 0 = A-share premium. Rate basis MUST be disclosed per series
  (Baidu quote vs central parity differ; deliverable-2 freezes one).

Honest boundaries: probes only, no factor run, no trials, no trading; HSGT
northbound flow face is context/monitoring only (usage decisions go through
prereg); research period = public data.

Storage: results/shortline/ah_face_probes.json (top-level evidence_cutoff
per S6 results-JSON law).
Exit codes: 0 = report written, every face labeled (alive or honest-fail);
2 = mechanism failure (crash / nothing written), never mask.
Selftest: offline, zero network, natural-serialized-shape fixtures (machine
pitfall law #1), pure functions only.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RESULTS_DIR = os.path.join(ROOT, "results", "shortline")
OUT_PATH = os.path.join(RESULTS_DIR, "ah_face_probes.json")

sys.path.insert(0, HERE)
from fund_premium_probe import clear_proxy_env, classify_error, _value_probe  # noqa: E402
from lof_census import THROTTLE_S, pull_retry_windowed, session_state  # noqa: E402

BACKOFF_S = 8              # small in-window backoff (push2 same-day persistent-block evidence)
ATTEMPTS_PRIMARY = 2       # spec-named faces
ATTEMPTS_SUPPORT = 1       # panel-support faces (stable families: sina/tencent)
ATTEMPTS_PUSH2 = 2         # push2 family risk faces

HK_DAILY_SYMBOL = "00700"          # probe symbol (liquid HK anchor)
AH_DAILY_SYMBOL = "02318"           # probe symbol (tencent AH history default face)
INDEX_CANDIDATES = ["HSAHP", "HSI", "HSCEI", "CES100"]


# ---------------------------------------------------------------- pure helpers
def ah_premium(a_price_cny, h_price_hkd, fx_hkd_cny):
    """AH 溢价（纯函数·FX 基准口径预冻结）。premium = A(CNY)/(H(HKD)*fx)-1。
    任一输入 None/非正数→None（停牌/坏行诚实剔除）。"""
    try:
        a, h, fx = float(a_price_cny), float(h_price_hkd), float(h_price_hkd and fx_hkd_cny)
        if not (a > 0 and h > 0 and fx > 0):
            return None
        return a / (h * fx) - 1.0
    except (TypeError, ValueError):
        return None


def extract_last_date(df):
    """宽容提取 DataFrame 末行的最近日期（纯函数）。
    支持 Timestamp/date 与 'YYYY-MM-DD' 字符串（序列化形态）。返回 'YYYY-MM-DD'|None。"""
    try:
        if df is None or len(df) == 0:
            return None
        last = df.iloc[-1]
        for v in last:
            s = None
            if isinstance(v, (dt.datetime, dt.date)):
                s = v.strftime("%Y-%m-%d")
            elif isinstance(v, str) and len(v) >= 10 and v[4] == "-" and v[7] == "-":
                s = v[:10]
            if s:
                return s
    except Exception:  # noqa: BLE001 -- tolerant by design, honest None
        return None
    return None


def panel_feasibility_verdict(face_results):
    """面板可行性判读（纯函数）。输入=faces dict（face名→{ok:bool}）。
    判据：AH 比价面活 + HK 日线活 + FX 活 = 可构造；缺任何一腿=partial/不可构造。"""
    def ok(*names):
        return any(face_results.get(n, {}).get("ok") for n in names)

    ah_parity = ok("stock_zh_ah_spot", "stock_zh_ah_spot_em")
    hk_leg = ok("stock_hk_daily", "stock_hk_spot", "stock_hk_spot_em")
    fx_leg = ok("fx_quote_baidu", "fx_spot_quote")
    universe = ok("stock_zh_ah_name")
    if ah_parity and hk_leg and fx_leg:
        basis = "AH parity + HK quote leg + FX leg alive"
        if universe:
            return "CONSTRUCTIBLE: per-stock AH premium panel buildable via alive faces (universe list alive)"
        return f"PARTIAL: {basis}, but AH universe list face dead -> membership face needed before panel build"
    if ah_parity and not (hk_leg and fx_leg):
        return "PARTIAL: AH parity alive but HK leg or FX leg dead -> cross-leg join not buildable this round"
    if not ah_parity:
        return "NOT CONSTRUCTIBLE: no AH parity face alive this round (honest-fail labels recorded)"
    return "PARTIAL: legs incomplete (honest-fail labels recorded)"


# ---------------------------------------------------------------- face probes
def probe_face(ak, name, fn, max_attempts, extra=None):
    """单面探针（retry-windowed，全量入账）。返回 (record, df|None)。"""
    df, attempts = pull_retry_windowed(name, fn, max_attempts=max_attempts, backoff_s=BACKOFF_S)
    rec = {"ok": df is not None, "attempts": attempts}
    if extra:
        rec["args"] = extra
    if df is not None:
        rec["rows"] = int(len(df))
        rec["cols"] = [str(c) for c in df.columns][:20]
        rec["value_probe"] = _value_probe(df)
        rec["last_date"] = extract_last_date(df)
    return rec, df


def run():
    clear_proxy_env()
    import akshare as ak
    ran_at = dt.datetime.now()
    run_date = ran_at.strftime("%Y-%m-%d")

    out = {
        "census": "ah_face_probe",
        "ticket": "T-2026-09-24-17",
        "lane": "ARB-2 deliverable-1 (probe-first face validation, zero trials)",
        "ran_at": ran_at.isoformat(timespec="seconds"),
        "session_state": session_state(ran_at),
        "akshare_version": getattr(ak, "__version__", "unknown"),
        "faces": {},
        "fx_basis_preview": {
            "premium_formula": "A_price(CNY) / (H_price(HKD) * fx_HKD_CNY) - 1",
            "rate_basis_disclosure": (
                "premium > 0 = A-share premium; fx series MUST carry explicit "
                "rate basis (Baidu quote vs chinamoney central parity differ) -- "
                "deliverable-2 puller freezes ONE basis before any join"),
        },
        "verdict": None,
        "audit": {
            "ledger_trials_added": 0,
            "kind": "face probe (probe-first family, zero trials)",
            "throttle_s": THROTTLE_S,
            "backoff_s": BACKOFF_S,
            "proxy_env_cleared": True,
        },
    }
    faces = out["faces"]
    rc_probe_ok = True

    # -- spec-named faces ----------------------------------------------------
    r, _ = probe_face(ak, "stock_zh_ah_spot", lambda: ak.stock_zh_ah_spot(),
                      ATTEMPTS_PRIMARY)
    faces["stock_zh_ah_spot"] = r
    time_wait()
    r, _ = probe_face(ak, "stock_zh_ah_spot_em", lambda: ak.stock_zh_ah_spot_em(),
                      ATTEMPTS_PUSH2, extra="push2 family, same-day block risk per moneyflow/lof evidence")
    faces["stock_zh_ah_spot_em"] = r
    time_wait()
    r, _ = probe_face(ak, "stock_hk_daily",
                      lambda: ak.stock_hk_daily(symbol=HK_DAILY_SYMBOL),
                      ATTEMPTS_PRIMARY, extra=f"symbol={HK_DAILY_SYMBOL}")
    faces["stock_hk_daily"] = r
    time_wait()
    r, _ = probe_face(ak, "stock_hk_spot", lambda: ak.stock_hk_spot(), ATTEMPTS_SUPPORT)
    faces["stock_hk_spot"] = r
    time_wait()
    r, _ = probe_face(ak, "stock_hk_spot_em", lambda: ak.stock_hk_spot_em(), ATTEMPTS_PUSH2)
    faces["stock_hk_spot_em"] = r
    time_wait()
    r, _ = probe_face(ak, "stock_hsgt_hist_em",
                      lambda: ak.stock_hsgt_hist_em(symbol="北向资金"),
                      ATTEMPTS_PUSH2, extra="symbol=北向资金 (push2 family risk)")
    faces["stock_hsgt_hist_em"] = r
    time_wait()

    # -- AH premium index availability (per-symbol labels) -------------------
    idx = {}
    for sym in INDEX_CANDIDATES:
        rec, _ = probe_face(ak, f"stock_hk_index_daily_sina[{sym}]",
                            lambda s=sym: ak.stock_hk_index_daily_sina(symbol=s),
                            ATTEMPTS_SUPPORT, extra=f"symbol={sym}")
        idx[sym] = rec
        time_wait()
    r, _ = probe_face(ak, "stock_hk_index_daily_em",
                      lambda: ak.stock_hk_index_daily_em(symbol="HSAHP"),
                      ATTEMPTS_PUSH2, extra="symbol=HSAHP (push2 family risk)")
    idx["em:HSAHP"] = r
    faces["ah_premium_index"] = {
        "ok": any(v.get("ok") for v in idx.values()),
        "candidates": idx,
        "note": "availability probe per spec: per-symbol alive/dead labels; "
                "HSAHP=Hang Seng Stock Connect AH Premium Index",
    }
    time_wait()

    # -- panel-support faces -------------------------------------------------
    r, _ = probe_face(ak, "stock_zh_ah_name", lambda: ak.stock_zh_ah_name(), ATTEMPTS_SUPPORT)
    faces["stock_zh_ah_name"] = r
    time_wait()
    r, _ = probe_face(ak, "stock_zh_ah_daily",
                      lambda: ak.stock_zh_ah_daily(symbol=AH_DAILY_SYMBOL,
                                                   start_year="2025", end_year="2026"),
                      ATTEMPTS_SUPPORT, extra=f"symbol={AH_DAILY_SYMBOL} 2025-2026 bounded window")
    faces["stock_zh_ah_daily"] = r
    time_wait()
    r, _ = probe_face(ak, "fx_quote_baidu", lambda: ak.fx_quote_baidu(symbol="港币"),
                      ATTEMPTS_SUPPORT, extra="symbol=港币 (Baidu quote basis)")
    faces["fx_quote_baidu"] = r
    time_wait()
    r, _ = probe_face(ak, "fx_spot_quote", lambda: ak.fx_spot_quote(), ATTEMPTS_SUPPORT,
                      extra="chinamoney CNY central parity incl HKD row")
    faces["fx_spot_quote"] = r

    # -- verdict + evidence cutoff -------------------------------------------
    out["verdict"] = panel_feasibility_verdict(faces)
    dates = [v.get("last_date") for v in faces.values() if isinstance(v, dict) and v.get("last_date")]
    dates.append(run_date)
    out["evidence_cutoff"] = max(dates)

    os.makedirs(RESULTS_DIR, exist_ok=True)
    tmp = OUT_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    os.replace(tmp, OUT_PATH)

    alive = [k for k, v in faces.items() if isinstance(v, dict) and v.get("ok")]
    dead = [k for k, v in faces.items() if isinstance(v, dict) and not v.get("ok")]
    print(f"[ah_probe] alive={len(alive)}: {alive}")
    print(f"[ah_probe] dead={len(dead)}: {dead}")
    print(f"[ah_probe] verdict: {out['verdict']}")
    print(f"[ah_probe] out -> {OUT_PATH}")
    return 0 if rc_probe_ok else 2


def time_wait():
    import time
    time.sleep(THROTTLE_S)


# ---------------------------------------------------------------- selftest
def selftest():
    import pandas as pd
    fails = []

    def chk(name, cond):
        print(("PASS " if cond else "FAIL ") + name)
        if not cond:
            fails.append(name)

    # S1 ah_premium (FX-basis math + guards)
    p = ah_premium(10.0, 11.0, 0.91)
    chk("premium math", p is not None and abs(p - (10.0 / (11.0 * 0.91) - 1.0)) < 1e-12)
    chk("premium none on bad fx", ah_premium(10.0, 11.0, None) is None)
    chk("premium none on zero h", ah_premium(10.0, 0.0, 0.91) is None)
    chk("premium none on str price", ah_premium("x", 11.0, 0.91) is None)
    chk("premium str-numbers ok (serialized shape)", abs(ah_premium("10.0", "11.0", "0.91") - p) < 1e-12)

    # S2 extract_last_date (natural serialized shapes)
    df = pd.DataFrame({"date": ["2026-09-23", "2026-09-24"], "close": ["1.0", "1.1"]})
    chk("last date str", extract_last_date(df) == "2026-09-24")
    df2 = pd.DataFrame({"日期": [dt.date(2026, 9, 23), dt.date(2026, 9, 24)], "x": [1, 2]})
    chk("last date date-obj", extract_last_date(df2) == "2026-09-24")
    chk("last date empty honest", extract_last_date(pd.DataFrame({"x": []})) is None)
    chk("last date none honest", extract_last_date(None) is None)

    # S3 verdict logic (pure)
    v = panel_feasibility_verdict({
        "stock_zh_ah_spot": {"ok": True}, "stock_hk_daily": {"ok": True},
        "fx_quote_baidu": {"ok": True}, "stock_zh_ah_name": {"ok": True}})
    chk("verdict constructible", v.startswith("CONSTRUCTIBLE"))
    v = panel_feasibility_verdict({
        "stock_zh_ah_spot_em": {"ok": True}, "stock_hk_spot": {"ok": True},
        "fx_spot_quote": {"ok": True}})
    chk("verdict partial no-universe", v.startswith("PARTIAL"))
    v = panel_feasibility_verdict({"stock_hk_daily": {"ok": True}, "fx_spot_quote": {"ok": True}})
    chk("verdict not-constructible no-parity", v.startswith("NOT CONSTRUCTIBLE"))
    v = panel_feasibility_verdict({"stock_zh_ah_spot": {"ok": True}})
    chk("verdict partial missing legs", v.startswith("PARTIAL"))

    # S4 retry window honest-fail (offline fake)
    def boom():
        raise ConnectionError("push2 blocked")
    df4, att4 = pull_retry_windowed("fake", boom, max_attempts=2, backoff_s=0)
    chk("retry honest fail", df4 is None and len(att4) == 2
        and all(a["ok"] is False for a in att4))

    print(f"selftest: {'ALL PASS' if not fails else fails}")
    return 0 if not fails else 1


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "run"
    if mode == "selftest":
        sys.exit(selftest())
    elif mode == "run":
        sys.exit(run())
    else:
        print("usage: ah_face_probe.py run|selftest")
        sys.exit(2)
