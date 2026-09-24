# -*- coding: utf-8 -*-
"""fund_premium_probe.py -- T-16 deliverable-1: single-probe-first validation of
the four akshare fund faces named in ARBITRAGE_PLAYBOOK.md section 3.

Faces probed (each ONCE, honest-fail labeled, 2.5s throttle):
  1. ak.fund_etf_em()               -- ETF on-exchange spot list (fund.eastmoney domain family)
  2. ak.fund_lof_em()               -- LOF on-exchange spot list
  3. ak.fund_etf_fund_info_em(fund) -- per-fund off-exchange NAV history
       samples: 510300 (domestic core) + 513100 (QDII -- premium hypothesis key member)
  4. ak.fund_fhsp_em()              -- fund dividend/split records (ex-div pollution guard face)

Discipline (F-06 derived law, probe-first):
  - zero-assumption ledger: every face result recorded as-is, no retries in probe mode
  - error classification: conn_level (source blocked/网络级) vs data_level (shape/schema) vs api_level
    (HTTP error from source) -- conn-level failures NEVER silently retried
  - Clash proxy hijack guard: env proxies cleared before akshare import (house law, J13 family)
  - ledger_trials_added=0 (probe, not a trial batch; corr-watch/t18_deep_probe precedent)

Run:    python scripts/fund_premium_probe.py run      -> results/shortline/fund_premium_probe.json
Selftest (offline, zero network): python scripts/fund_premium_probe.py selftest
"""
import json
import os
import sys
import time
import datetime as dt
import traceback

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RESULTS_DIR = os.path.join(ROOT, "results", "shortline")
OUT_PATH = os.path.join(RESULTS_DIR, "fund_premium_probe.json")

THROTTLE_S = 2.5
PROBE_TS = None  # set in run()


def clear_proxy_env():
    """Clash 全局代理会劫持 python 流量（J13 回环坑族），akshare 前一律清 env 代理。"""
    for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "all_proxy", "ALL_PROXY"):
        os.environ.pop(k, None)
    os.environ["NO_PROXY"] = "*"
    os.environ["no_proxy"] = "*"


# ---------------------------------------------------------------- error taxonomy
CONN_MARKERS = ("ConnectionError", "Timeout", "RemoteDisconnected", "MaxRetryError",
                "ProtocolError", "ConnectionReset", "ConnectionAborted", "getaddrinfo")
API_MARKERS = ("HTTPError", "HTTP 4", "HTTP 5", "403", "404", "405", "429")


def classify_error(err: BaseException) -> str:
    """纯函数（selftest 覆盖）：连接级/数据级/API 级三分类，连接级永不静默重试。"""
    chain = []
    e = err
    while e is not None:
        chain.append(type(e).__name__ + ": " + str(e)[:200])
        e = e.__cause__ or e.__context__
        if len(chain) > 8:
            break
    text = " | ".join(chain)
    if any(m in text for m in CONN_MARKERS):
        return "conn_level"
    if any(m in text for m in API_MARKERS):
        return "api_level"
    return "data_level"


# ---------------------------------------------------------------- shape helpers
def df_freshness(df):
    """扫全列找日期样字段，返回 (best_col, max_value) 纯扫描；无则 (None, None)。
    诚实限制：字符串日期按 ISO 排序近似；datetime64 直接 max。"""
    best_col, best_val = None, None
    for c in df.columns:
        try:
            s = df[c]
        except Exception:
            continue
        try:
            if str(s.dtype).startswith("datetime"):
                v = s.max()
                if v is not None and (best_val is None or v > best_val):
                    best_col, best_val = c, v
                continue
        except Exception:
            pass
        # object/string columns: probe head+tail rows for date-like YYYY-MM-DD
        # (pit fixed pass-3: history faces sort ascending, head(200)-only scan
        #  truncates freshness reading -- scan both ends)
        try:
            s_str = s.dropna().astype(str)
            sample = s_str if len(s_str) <= 400 else pd_concat_ends(s_str)
            date_like = [x for x in sample if len(x) >= 10 and x[4] == "-" and x[7] == "-"]
            if date_like and len(date_like) >= max(1, len(sample) // 2):
                v = max(date_like)
                if best_val is None or str(v) > str(best_val):
                    best_col, best_val = c, v
        except Exception:
            continue
    return best_col, (str(best_val) if best_val is not None else None)


def pd_concat_ends(s, n=200):
    import pandas as pd
    if len(s) <= 2 * n:
        return s
    return pd.concat([s.head(n), s.tail(n)])


def sample_rows(df, n=3):
    out = []
    for _, r in df.head(n).iterrows():
        row = {}
        for c in df.columns[:14]:
            v = r[c]
            try:
                if v is None or v != v:  # NaN guard
                    row[str(c)] = None
                else:
                    row[str(c)] = v.item() if hasattr(v, "item") else str(v)
            except Exception:
                row[str(c)] = str(v)[:60]
        out.append(row)
    return out


def jsonable_freshness(col, val):
    if val is None:
        return {"col": col, "max": None}
    if isinstance(val, dt.datetime):
        return {"col": col, "max": val.isoformat()}
    return {"col": col, "max": str(val)}


def col_name_freshness(df):
    """批量面坑（pass2 发现）：fund_etf_fund_daily_em 日期嵌在列名（'2026-09-23-单位净值'）——
    值扫描空手时扫列名，返回 (col_name, date_str) 或 (None, None)。"""
    best = None
    for c in df.columns:
        cs = str(c)
        if len(cs) >= 10 and cs[4] == "-" and cs[7] == "-":
            d = cs[:10]
            if len(d) == 10 and d[4] == "-" and d[7] == "-":
                if best is None or d > best:
                    best = d
    return (best, best) if best else (None, None)


# ---------------------------------------------------------------- probe core
def probe_face(name, fn, meta=None):
    """单探针：一次调用、诚实记录、永不重试（probe-first 律）。"""
    rec = {"face": name, "meta": meta or {}, "ok": False}
    t0 = time.time()
    try:
        df = fn()
        rec["latency_s"] = round(time.time() - t0, 2)
        rec["rows"] = int(len(df))
        rec["cols"] = [str(c) for c in df.columns]
        rec["sample"] = sample_rows(df)
        fcol, fval = df_freshness(df)
        if fcol is None:
            fcol, fval = col_name_freshness(df)
            if fcol is not None:
                rec["freshness_via"] = "column_names"
        rec["freshness"] = jsonable_freshness(fcol, fval)
        rec["ok"] = True
        # value-column sanity (R58 行壳数据坑: 只数行数会误判源活, 抽样值列)
        rec["value_probe"] = _value_probe(df)
    except Exception as e:  # noqa: BLE001 -- probe must label, never crash
        rec["latency_s"] = round(time.time() - t0, 2)
        rec["ok"] = False
        rec["error_class"] = classify_error(e)
        rec["error"] = "".join(traceback.format_exception_only(type(e), e))[:400]
    return rec


def _value_probe(df):
    """行壳防御（R58 北向教训）：抽样首数值列统计非空率，防 rows>0 值全 NaN 的假活源。"""
    import pandas as pd
    num_cols = [c for c in df.columns
                if str(df[c].dtype) in ("float64", "float32", "int64", "int32", "object")]
    for c in num_cols[:6]:
        try:
            s = pd.to_numeric(df[c], errors="coerce")
            nn = int(s.notna().sum())
            if nn > 0:
                return {"col": str(c), "non_null": nn, "total": int(len(df)),
                        "non_null_rate": round(nn / max(1, len(df)), 4)}
        except Exception:
            continue
    return {"col": None, "non_null": 0, "total": int(len(df)), "non_null_rate": 0.0}


# ---------------------------------------------------------------- run
def _sig_args(fn, code="510300"):
    """inspect 实签名适配（防 TypeError 空耗请求）：按参数名猜最小实参集。"""
    import inspect
    try:
        params = list(inspect.signature(fn).parameters)
    except (TypeError, ValueError):
        return {}
    kw = {}
    for p in params:
        lp = p.lower()
        if lp in ("fund", "symbol", "code") and "fund" not in kw:
            # sina faces want exchange-prefixed codes; em faces want bare digits
            kw[p] = code
        elif lp in ("start_date", "beg", "begin_date"):
            kw[p] = "20250901"
        elif lp in ("end_date", "end"):
            kw[p] = "20260924"
    return kw


def run():
    clear_proxy_env()
    import akshare as ak
    import pandas as pd  # noqa: F401 -- akshare dependency
    _ = pd

    probes = []
    # 名称发现轨迹（零假设记账）：playbook 骨架名 fund_etf_em/fund_lof_em/fund_fhsp_em
    # 在 akshare 1.18.96 均不存在（AttributeError, 见 name_discovery 首跑记录）；
    # 真名 = fund_etf_spot_em / fund_lof_spot_em / fund_etf_dividend_sina(+fund_announcement_dividend_em)。
    name_discovery = {
        "playbook_skeleton_names": ["fund_etf_em", "fund_lof_em", "fund_fhsp_em"],
        "verdict": "absent in akshare 1.18.96 (AttributeError, first probe pass)",
        "real_names_probed": ["fund_etf_spot_em", "fund_lof_spot_em", "fund_etf_fund_daily_em",
                              "fund_etf_dividend_sina", "fund_announcement_dividend_em"],
    }

    # 1) ETF spot list (real name)
    probes.append(probe_face("fund_etf_spot_em", lambda: ak.fund_etf_spot_em(),
                             meta={"desc": "ETF 场内行情快照", "domain_family": "fund.eastmoney",
                                   "renamed_from": "fund_etf_em (skeleton)"}))
    time.sleep(THROTTLE_S)

    # 2) LOF spot list (real name)
    probes.append(probe_face("fund_lof_spot_em", lambda: ak.fund_lof_spot_em(),
                             meta={"desc": "LOF 场内行情快照", "domain_family": "fund.eastmoney",
                                   "renamed_from": "fund_lof_em (skeleton)"}))
    time.sleep(THROTTLE_S)

    # 3) per-fund NAV history -- domestic core + QDII (premium hypothesis key)
    for code, why in (("510300", "domestic core48 member"), ("513100", "QDII member (premium key)")):
        probes.append(probe_face(
            "fund_etf_fund_info_em",
            lambda c=code: ak.fund_etf_fund_info_em(fund=c, start_date="20250901", end_date="20260924"),
            meta={"desc": "场外单位净值历史（单基金）", "fund": code, "why": why}))
        time.sleep(THROTTLE_S)

    # 4) bulk daily NAV face (panel-value candidate: all funds one request)
    probes.append(probe_face("fund_etf_fund_daily_em", lambda: ak.fund_etf_fund_daily_em(),
                             meta={"desc": "ETF 日报表（净值/IOPV 批量面候选）", "domain_family": "fund.eastmoney"}))
    time.sleep(THROTTLE_S)

    # 5) dividend/split faces (ex-div pollution guard; real names via discovery)
    probes.append(probe_face("fund_etf_dividend_sina",
                             lambda: ak.fund_etf_dividend_sina(**_sig_args(ak.fund_etf_dividend_sina, "sh510300")),
                             meta={"desc": "ETF 分红除息记录", "domain_family": "sina",
                                   "renamed_from": "fund_fhsp_em (skeleton)",
                                   "arg_note": "pass2 bare '510300' returned 0 rows; sina wants prefixed code"}))
    time.sleep(THROTTLE_S)
    probes.append(probe_face("fund_announcement_dividend_em",
                             lambda: ak.fund_announcement_dividend_em(**_sig_args(ak.fund_announcement_dividend_em)),
                             meta={"desc": "基金分红公告（datacenter）", "domain_family": "datacenter-web",
                                   "renamed_from": "fund_fhsp_em (skeleton)"}))

    # cross-face sanity: 510300 spot price vs latest NAV (probe-grade only, NOT a panel)
    cross = {"constructible": False, "note": "probe-grade evidence for deliverable-3 panel feasibility"}
    try:
        # 2 extra minimal requests for the cross check (same throttle law)
        time.sleep(THROTTLE_S)
        sdf = ak.fund_etf_spot_em()
        px_row = sdf[sdf["代码"].astype(str).str.contains("510300")]
        time.sleep(THROTTLE_S)
        ndf = ak.fund_etf_fund_info_em(fund="510300", start_date="20260801", end_date="20260924")
        if len(px_row) and len(ndf):
            px = float(px_row.iloc[0]["最新价"])
            nav_row = ndf.iloc[-1]
            nav_val = float(nav_row["单位净值"])
            nav_date = str(nav_row["净值日期"])
            cross.update({
                "constructible": True,
                "spot_price_510300": px,
                "nav_510300": nav_val,
                "nav_date": nav_date,
                "naive_premium_pct": round((px / nav_val - 1) * 100, 3),
                "lag_semantics": "NAV is T-1 lagged by nature; forward-only usage per ticket note",
            })
    except Exception as e:  # noqa: BLE001
        cross["error"] = classify_error(e) + ": " + str(e)[:200]

    out = {
        "probe": "fund_premium_probe",
        "ticket": "T-2026-09-24-16",
        "lane": "ARB-1 fund premium (deliverable-1 probe-first)",
        "ran_at": dt.datetime.now().isoformat(timespec="seconds"),
        "name_discovery": name_discovery,
        "faces": probes,
        "cross_check_510300": cross,
        "audit": {
            "ledger_trials_added": 0,
            "kind": "source-probe (probe-first, zero-assumption)",
            "throttle_s": THROTTLE_S,
            "proxy_env_cleared": True,
            "passes": 2,
            "pass1_note": "skeleton-name AttributeError trail preserved here; pass2 = real names",
        },
    }
    os.makedirs(RESULTS_DIR, exist_ok=True)
    tmp = OUT_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    os.replace(tmp, OUT_PATH)

    n_ok = sum(1 for p in probes if p["ok"])
    print(f"[probe] {n_ok}/{len(probes)} faces ok; cross constructible={cross.get('constructible')}")
    print(f"[probe] out -> {OUT_PATH}")
    return 0 if n_ok > 0 else 2


# ---------------------------------------------------------------- selftest (offline)
def selftest():
    import pandas as pd
    fails = []

    def chk(name, cond):
        print(("PASS " if cond else "FAIL ") + name)
        if not cond:
            fails.append(name)

    # S1 error taxonomy (pure)
    chk("classify conn_level", classify_error(ConnectionError("RemoteDisconnected")) == "conn_level")
    chk("classify conn_level marker in chain",
        classify_error(RuntimeError("MaxRetryError caused by ConnectionReset")) == "conn_level")
    import urllib.error
    chk("classify api_level", classify_error(urllib.error.HTTPError(None, 404, "Not Found", None, None)) == "api_level")
    chk("classify data_level", classify_error(ValueError("column mismatch")) == "data_level")

    # S2 freshness scan (pure)
    df = pd.DataFrame({"净值日期": ["2026-09-20", "2026-09-23", "2026-09-22"], "单位净值": [4.0, 4.1, 4.05]})
    col, val = df_freshness(df)
    chk("freshness finds date col", col == "净值日期" and val == "2026-09-23")
    df2 = pd.DataFrame({"x": [1, 2, 3]})
    c2, v2 = df_freshness(df2)
    chk("freshness absent honest", c2 is None and v2 is None)
    dfdt = pd.DataFrame({"d": pd.to_datetime(["2026-09-01", "2026-09-23"])})
    c3, v3 = df_freshness(dfdt)
    chk("freshness datetime col", c3 == "d" and "2026-09-23" in str(v3))

    # S3 value probe (row-shell defense, R58 law)
    shell = pd.DataFrame({"日期": ["2026-09-01", "2026-09-02"], "值": [None, None]})
    vp = _value_probe(shell)
    chk("row-shell detected (non_null_rate 0)", vp["non_null_rate"] == 0.0)
    live = pd.DataFrame({"日期": ["2026-09-01"], "值": [1.23]})
    vp2 = _value_probe(live)
    chk("live values detected", vp2["non_null"] == 1)

    # S4 sample rows jsonable
    smp = sample_rows(df, 2)
    chk("sample rows jsonable", len(smp) == 2 and isinstance(smp[0], dict))

    # S5 probe_face honest-fail path (offline, fake fn)
    rec = probe_face("fake", lambda: (_ for _ in ()).throw(ConnectionError("blocked")))
    chk("probe_face honest fail", rec["ok"] is False and rec["error_class"] == "conn_level")

    print(f"selftest: {6 + 1 - 0} checks, {len(fails)} fail" if False else
          f"selftest: {'ALL PASS' if not fails else fails}")
    return 0 if not fails else 1


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "run"
    if mode == "selftest":
        sys.exit(selftest())
    elif mode == "run":
        sys.exit(run())
    else:
        print("usage: fund_premium_probe.py run|selftest")
        sys.exit(2)
