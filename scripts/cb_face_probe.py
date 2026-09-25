# -*- coding: utf-8 -*-
"""cb_face_probe.py -- T-60 s2: convertible-bond data-face probe-first
validation (single-probe per face, honest-fail labels, zero trials).

Ticket T-2026-09-25-60 (CEO order O-20260925-1152 product-matrix s1/s2);
probe plan pre-declared in research/digests/DIGEST-20260925-matrix-gap-dims-s1.md
(off-hours window per its 〇 channel-discipline clause -- push2 clist face
is intraday-forbidden 09:15-15:05 per R108/R109, this run fires post-close).

Faces probed (s1 audit table, one pull each, nothing silent):
  全谱/截面腿 (double-low cross-section):
    bond_cov_comparison()           -- EM push2 clist 比价截面 (price+premium
                                       full spectrum; push2 family risk)
    bond_cb_jsl(cookie=None)        -- jisilu full table (cookie wall face,
                                       honest-wall label expected without login)
  价格日线腿 (per-bond history):
    bond_zh_hs_cov_daily(symbol)   -- sina per-bond daily (IP-block warned in
                                       docstring; single probe, polite pacing)
  条款/事件腿 (terms & event faces):
    bond_zh_cov()                   -- EM datacenter full issuance table
    bond_zh_cov_info(symbol,..)    -- EM datacenter per-bond terms
    bond_zh_cov_value_analysis(..) -- EM datacenter per-bond premium analysis
    bond_cb_redeem_jsl()            -- jisilu public 强赎 face
    bond_cb_adj_logs_jsl(symbol)    -- jisilu public 下修记录 face
    bond_cb_index_jsl()             -- jisilu public 等权指数 face

R167 hardening (probe-semantics law): every alive face records sample head
rows (real data, column semantics reviewable later) + col list + value
probe + last date; garbled-name faces get keyword-anchored quantity probes
(price band / premium band) instead of trusting column labels alone.

Honest boundaries: probes only, no factor run, no trials, no prereg (s2
prereg freeze follows AFTER audit evidence lands); cookie face is expected
to fail without login -- label honestly, no workaround; all external
patterns stay hypothesis-grade (s1 folklores-standard tags).

Storage: results/shortline/cb_face_probes.json (top-level evidence_cutoff
per S6 results-JSON law).
Exit codes: 0 = report written, every face labeled (alive or honest-fail);
2 = mechanism failure (crash / nothing written), never mask.
Selftest: offline, zero network, natural-serialized-shape fixtures, pure
functions only (machine pitfall law #1).
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
OUT_PATH = os.path.join(RESULTS_DIR, "cb_face_probes.json")

sys.path.insert(0, HERE)
from fund_premium_probe import (  # noqa: E402
    clear_proxy_env, classify_error, _value_probe, sample_rows,
)
from lof_census import THROTTLE_S, pull_retry_windowed, session_state  # noqa: E402

BACKOFF_S = 8              # small in-window backoff (push2/datacenter intermittent)
ATTEMPTS_PUSH2 = 2         # EM push2/datacenter family risk faces
ATTEMPTS_SUPPORT = 1       # stable-family faces (jsl public / sina single)

SINA_DAILY_SYMBOL = "sh113527"      # real CB code (EM value_analysis example, sh-prefix)
JSL_ADJ_SYMBOL = "128013"           # bond_cb_adj_logs_jsl signature default
EM_INFO_SYMBOL = "123121"            # bond_zh_cov_info signature default
EM_VALUE_SYMBOL = "113527"           # bond_zh_cov_value_analysis signature default

PRICE_KEYS = ("价", "price")
PREMIUM_KEYS = ("溢价", "premium")

JSL_FULL_SPECTRUM_MIN = 100  # jsl cookie-free wall sample ~=30 rows; full CB market ~=500


# ---------------------------------------------------------------- pure helpers
def kw_quantity_probe(df, keys, lo=None, hi=None):
    """量纲级审计（R167 律·乱码列名面）：按关键词找列，用 iloc 位置+数值
    量纲双探（非信列名）。返回命中最前列的 (col, n, vmin, vmax) 或 None。
    lo/hi 给出时额外记录 in_band 率（量纲合理性），不作为门。"""
    for c in df.columns:
        if not any(k in str(c) for k in keys):
            continue
        try:
            import pandas as pd
            s = pd.to_numeric(df[c], errors="coerce").dropna()
            if len(s) == 0:
                continue
            vmin, vmax = float(s.min()), float(s.max())
            rec = {"col": str(c), "n": int(len(s)), "vmin": round(vmin, 4),
                   "vmax": round(vmax, 4)}
            if lo is not None and hi is not None:
                rec["band"] = [lo, hi]
                rec["in_band_rate"] = round(float(((s >= lo) & (s <= hi)).mean()), 4)
            return rec
        except Exception:  # noqa: BLE001 -- tolerant probe, honest skip
            continue
    return None


def extract_last_date(df):
    """宽容提取末行最近日期（纯函数·ah_face_probe 同式复用）。"""
    try:
        if df is None or len(df) == 0:
            return None
        last = df.iloc[-1]
        for v in last:
            if isinstance(v, (dt.datetime, dt.date)):
                return v.strftime("%Y-%m-%d")
            s = str(v)
            if len(s) >= 10 and s[4] == "-" and s[7] == "-":
                return s[:10]
    except Exception:  # noqa: BLE001
        return None
    return None


def cb_feasibility_verdict(face_results):
    """CB 维度可行性判读（纯函数·s1 三源结构口径）。
    腿定义：双低全谱截面（EM clist 比价面，或 jsl 全表=须 cookie）+ 个券
    价格日线 + 条款/事件面（EM 条款 或 jsl 强赎/下修/等权）。
    jsl 墙面律（probe 实证）：cookie=None 时 jsl 仅回 ~30 行样本=格式参照
    非==全谱面；rows<JSL_FULL_SPECTRUM_MIN 一律按 walled-sample 判，
    禁把 30 行样本冒充双低宇宙（R167 探针语义律+诚实标签律）。"""
    def ok(*names):
        return any(face_results.get(n, {}).get("ok") for n in names)

    comparison_ok = ok("bond_cov_comparison")
    jsl = face_results.get("bond_cb_jsl", {})
    jsl_rows = jsl.get("rows")
    jsl_full = jsl.get("ok") and jsl_rows is not None and jsl_rows >= JSL_FULL_SPECTRUM_MIN
    jsl_walled_sample = jsl.get("ok") and (jsl_rows is None or jsl_rows < JSL_FULL_SPECTRUM_MIN)
    cross_section = comparison_ok or jsl_full
    daily_leg = ok("bond_zh_hs_cov_daily")
    terms_leg = ok("bond_zh_cov", "bond_zh_cov_info", "bond_cb_redeem_jsl",
                   "bond_cb_adj_logs_jsl", "bond_cb_index_jsl")
    if cross_section and daily_leg:
        return "CONSTRUCTIBLE: double-low cross-section + per-bond daily legs alive (terms/event legs: {})"\
            .format("alive" if terms_leg else "DEAD -- disclosure needed in s2 prereg")
    if jsl_walled_sample and daily_leg and not comparison_ok:
        return ("PARTIAL: jsl cookie-free face alive but walled sample ({} rows < {}, full "
                "spectrum needs cookie) + EM clist face dead this round -> cross-section leg "
                "NOT established; sample serves as format/semantic reference only").format(
                    jsl_rows, JSL_FULL_SPECTRUM_MIN)
    if cross_section and not daily_leg:
        return "PARTIAL: cross-section alive but per-bond daily face dead this round (honest-fail recorded)"
    if daily_leg and not cross_section:
        return "PARTIAL: daily face alive but no full-spectrum cross-section alive (cookie wall / clist blocked)"
    return "NOT CONSTRUCTIBLE: both cross-section and daily legs dead this round"


def observation_dates(dates, run_date):
    """cutoff 语义卫（纯函数·禁未来数据律+R167 事件面语义族）：事件/条款面
    的到期日/发行日列（>run_date 或远早于近窗）不是观测日期——cutoff 只取
    <=run_date 的日期加 run_date 兜底，结构性禁未来 cutoff。"""
    obs = [d for d in dates if d and d <= run_date]
    obs.append(run_date)
    return max(obs)


def semantic_notes(faces):
    """探针语义注记（纯函数·R167 语义盲区律）：从 faces 实况推导判读者须知，
    不改任何原始证据。"""
    notes = []
    jsl = faces.get("bond_cb_jsl", {})
    if jsl.get("ok") and (jsl.get("rows") or 0) < JSL_FULL_SPECTRUM_MIN:
        notes.append(
            "bond_cb_jsl cookie-free returns a walled sample ({} rows < {}): format/semantic "
            "reference only, NOT the double-low universe; full spectrum needs login cookie "
            "(s1 audit wall clause confirmed by probe)".format(jsl.get("rows"), JSL_FULL_SPECTRUM_MIN))
    daily = faces.get("bond_zh_hs_cov_daily", {})
    if daily.get("ok") and daily.get("last_date"):
        notes.append(
            "bond_zh_hs_cov_daily probe symbol history ends {} (probe symbol may be "
            "redeemed/delisted -- 113527 redeemed 2025-01); puller must select "
            "currently-listed bonds (e.g. from issuance table or redeem face)".format(daily.get("last_date")))
    notes.append(
        "event/terms faces (redeem/adj_logs/issuance/info) carry maturity/issue date "
        "columns that are NOT observation dates -- excluded from evidence_cutoff by "
        "observation_dates() guard (R167 family: tolerant date extraction across "
        "event faces misreads maturity as freshness)")
    return notes


# ---------------------------------------------------------------- face probes
def probe_face(ak, name, fn, max_attempts, extra=None, kw_probes=None):
    """单面探针（retry-windowed，全量入账）。返回 (record, df|None)。"""
    df, attempts = pull_retry_windowed(name, fn, max_attempts=max_attempts, backoff_s=BACKOFF_S)
    rec = {"ok": df is not None, "attempts": attempts}
    if extra:
        rec["args"] = extra
    if df is not None:
        rec["rows"] = int(len(df))
        rec["cols"] = [str(c) for c in df.columns][:20]
        rec["value_probe"] = _value_probe(df)
        rec["head_rows"] = sample_rows(df, 3)      # R167: real data for later semantic review
        if kw_probes:
            for label, (keys, lo, hi) in kw_probes.items():
                rec[f"kw_probe_{label}"] = kw_quantity_probe(df, keys, lo, hi)
        rec["last_date"] = extract_last_date(df)
    return rec, df


def run():
    clear_proxy_env()
    import akshare as ak
    ran_at = dt.datetime.now()

    out = {
        "census": "cb_face_probe",
        "ticket": "T-2026-09-25-60",
        "lane": "product-matrix s2 data-face audit (probe-first, zero trials)",
        "ran_at": ran_at.isoformat(timespec="seconds"),
        "session_state": session_state(ran_at),
        "akshare_version": getattr(ak, "__version__", "unknown"),
        "faces": {},
        "verdict": None,
        "audit": {
            "ledger_trials_added": 0,
            "kind": "face probe (probe-first family, zero trials)",
            "throttle_s": THROTTLE_S,
            "backoff_s": BACKOFF_S,
            "proxy_env_cleared": True,
            "window_note": "post-close window per s1 digest 〇 clause (push2 clist intraday-forbidden)",
        },
    }
    faces = out["faces"]

    # -- 全谱/截面腿 --------------------------------------------------------
    r, _ = probe_face(ak, "bond_cov_comparison", lambda: ak.bond_cov_comparison(),
                      ATTEMPTS_PUSH2, extra="EM push2 clist (post-close single shot, R108/R109 pacing law)",
                      kw_probes={"price": (PRICE_KEYS, 50.0, 300.0),
                                 "premium": (PREMIUM_KEYS, -0.5, 3.0)})
    faces["bond_cov_comparison"] = r
    time_wait()
    r, _ = probe_face(ak, "bond_cb_jsl", lambda: ak.bond_cb_jsl(cookie=None),
                      ATTEMPTS_SUPPORT, extra="cookie=None -- login wall face, honest label expected")
    faces["bond_cb_jsl"] = r
    time_wait()

    # -- 价格日线腿 ---------------------------------------------------------
    r, _ = probe_face(ak, "bond_zh_hs_cov_daily",
                      lambda: ak.bond_zh_hs_cov_daily(symbol=SINA_DAILY_SYMBOL),
                      ATTEMPTS_SUPPORT, extra=f"symbol={SINA_DAILY_SYMBOL} (real CB, docstring example sh010107 stale)")
    faces["bond_zh_hs_cov_daily"] = r
    time_wait()

    # -- 条款/事件腿 --------------------------------------------------------
    r, _ = probe_face(ak, "bond_zh_cov", lambda: ak.bond_zh_cov(), ATTEMPTS_PUSH2,
                      extra="EM datacenter full issuance table (moneyflow same-family, R108 dual-face law)")
    faces["bond_zh_cov"] = r
    time_wait()
    r, _ = probe_face(ak, "bond_zh_cov_info",
                      lambda: ak.bond_zh_cov_info(symbol=EM_INFO_SYMBOL, indicator="基本信息"),
                      ATTEMPTS_PUSH2, extra=f"symbol={EM_INFO_SYMBOL} indicator=基本信息")
    faces["bond_zh_cov_info"] = r
    time_wait()
    r, _ = probe_face(ak, "bond_zh_cov_value_analysis",
                      lambda: ak.bond_zh_cov_value_analysis(symbol=EM_VALUE_SYMBOL),
                      ATTEMPTS_PUSH2, extra=f"symbol={EM_VALUE_SYMBOL} per-bond premium analysis")
    faces["bond_zh_cov_value_analysis"] = r
    time_wait()
    r, _ = probe_face(ak, "bond_cb_redeem_jsl", lambda: ak.bond_cb_redeem_jsl(),
                      ATTEMPTS_SUPPORT, extra="jsl public 强赎 face (feed channel validated R138/R141)")
    faces["bond_cb_redeem_jsl"] = r
    time_wait()
    r, _ = probe_face(ak, "bond_cb_adj_logs_jsl",
                      lambda: ak.bond_cb_adj_logs_jsl(symbol=JSL_ADJ_SYMBOL),
                      ATTEMPTS_SUPPORT, extra=f"symbol={JSL_ADJ_SYMBOL} 下修记录 face")
    faces["bond_cb_adj_logs_jsl"] = r
    time_wait()
    r, _ = probe_face(ak, "bond_cb_index_jsl", lambda: ak.bond_cb_index_jsl(),
                      ATTEMPTS_SUPPORT, extra="jsl public 等权指数 face (market baseline leg)")
    faces["bond_cb_index_jsl"] = r

    # -- verdict + evidence cutoff -------------------------------------------
    run_date = ran_at.strftime("%Y-%m-%d")
    out["verdict"] = cb_feasibility_verdict(faces)
    dates = [v.get("last_date") for v in faces.values() if isinstance(v, dict) and v.get("last_date")]
    out["evidence_cutoff"] = observation_dates(dates, run_date)
    out["semantic_notes"] = semantic_notes(faces)

    os.makedirs(RESULTS_DIR, exist_ok=True)
    tmp = OUT_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    os.replace(tmp, OUT_PATH)

    alive = [k for k, v in faces.items() if isinstance(v, dict) and v.get("ok")]
    dead = [k for k, v in faces.items() if isinstance(v, dict) and not v.get("ok")]
    print(f"[cb_probe] alive={len(alive)}: {alive}")
    print(f"[cb_probe] dead={len(dead)}: {dead}")
    print(f"[cb_probe] verdict: {out['verdict']}")
    print(f"[cb_probe] out -> {OUT_PATH}")
    return 0


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

    # S1 kw_quantity_probe (garbled-name faces: keyword anchor + quantity band)
    df = pd.DataFrame({"转股价": ["100.5", "105.0"], "溢价率-纯债": ["0.12", "0.31"]})
    q = kw_quantity_probe(df, PREMIUM_KEYS, -0.5, 3.0)
    chk("kw probe premium col", q is not None and q["col"] == "溢价率-纯债" and q["n"] == 2)
    chk("kw probe in-band", abs(q["in_band_rate"] - 1.0) < 1e-9)
    chk("kw probe none when missing", kw_quantity_probe(df, ("不存在",)) is None)
    df_bad = pd.DataFrame({"溢价率": ["abc", ""]})
    chk("kw probe all-coerce skip", kw_quantity_probe(df_bad, PREMIUM_KEYS) is None)

    # S2 extract_last_date (natural serialized shapes)
    df2 = pd.DataFrame({"日期": ["2026-09-23", "2026-09-24"], "x": [1, 2]})
    chk("last date str", extract_last_date(df2) == "2026-09-24")
    df3 = pd.DataFrame({"d": [dt.date(2026, 9, 23), dt.date(2026, 9, 24)]})
    chk("last date date-obj", extract_last_date(df3) == "2026-09-24")
    chk("last date empty honest", extract_last_date(pd.DataFrame({"x": []})) is None)
    chk("last date none honest", extract_last_date(None) is None)

    # S3 verdict logic (three-leg structure per s1 + jsl wall law)
    v = cb_feasibility_verdict({"bond_cov_comparison": {"ok": True},
                                "bond_zh_hs_cov_daily": {"ok": True},
                                "bond_zh_cov": {"ok": True}})
    chk("verdict constructible", v.startswith("CONSTRUCTIBLE"))
    v = cb_feasibility_verdict({"bond_cb_jsl": {"ok": True, "rows": 522},
                                "bond_zh_hs_cov_daily": {"ok": True}})
    chk("verdict constructible via jsl full table", v.startswith("CONSTRUCTIBLE"))
    v = cb_feasibility_verdict({"bond_cb_jsl": {"ok": True, "rows": 30},
                                "bond_zh_hs_cov_daily": {"ok": True}})
    chk("verdict partial jsl walled sample", v.startswith("PARTIAL") and "walled" in v)
    v = cb_feasibility_verdict({"bond_cov_comparison": {"ok": True}})
    chk("verdict partial no-daily", v.startswith("PARTIAL"))
    v = cb_feasibility_verdict({"bond_zh_hs_cov_daily": {"ok": True}})
    chk("verdict partial no-cross-section", v.startswith("PARTIAL"))
    v = cb_feasibility_verdict({"bond_cb_redeem_jsl": {"ok": True}})
    chk("verdict not constructible", v.startswith("NOT CONSTRUCTIBLE"))

    # S3b cutoff semantic guard (no-future-data law + event-face artifact)
    chk("cutoff drops future maturity dates",
        observation_dates(["2027-07-28", "2026-09-24"], "2026-09-25") == "2026-09-25")
    chk("cutoff keeps recent observation",
        observation_dates(["2026-09-24"], "2026-09-25") == "2026-09-25")
    chk("cutoff run_date floor on empty",
        observation_dates([], "2026-09-25") == "2026-09-25")

    # S3c semantic notes (R167 disclosure derivation)
    n = semantic_notes({"bond_cb_jsl": {"ok": True, "rows": 30},
                        "bond_zh_hs_cov_daily": {"ok": True, "last_date": "2025-01-20"}})
    chk("notes jsl wall + daily symbol bounds",
        any("walled sample" in x for x in n) and any("2025-01-20" in x for x in n)
        and any("maturity" in x for x in n))

    # S4 sample_rows head evidence (R167: real data into evidence file)
    df4 = pd.DataFrame({"代码": ["113527", "123121"], "价格": [130.5, 128.9]})
    rows = sample_rows(df4, 2)
    chk("sample rows shape", len(rows) == 2 and rows[0]["代码"] == "113527")

    # S5 retry window honest-fail (offline fake)
    def boom():
        raise ConnectionError("push2 blocked")
    df5, att5 = pull_retry_windowed("fake", boom, max_attempts=2, backoff_s=0)
    chk("retry honest fail", df5 is None and len(att5) == 2
        and all(a["ok"] is False for a in att5))

    print(f"selftest: {'ALL PASS' if not fails else fails}")
    return 0 if not fails else 1


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "run"
    if mode == "selftest":
        sys.exit(selftest())
    elif mode == "run":
        sys.exit(run())
    else:
        print("usage: cb_face_probe.py run|selftest")
        sys.exit(2)
