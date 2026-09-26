# -*- coding: utf-8 -*-
"""T-73 s2 slice-D: A-share SIZE / LOW-VOL / DIVIDEND factor-history law,
in-repo census empirical check (CEO order O-20260926-0926 s2; CEO top
criterion 实战出真知).

PRE-REGISTERED (frozen before first run; no threshold edits after results):
- Law faces (s2 mandated topic 规模低波红利因子史):
  (1) LOWVOL 低波异象: lower realized volatility -> higher forward return
      -> negative IC of vol level. Signal = VOL{w} trailing nanstd of daily
      close returns, w in {20, 60}, min_periods = ceil(w/2). Returns from the
      P1C cache close (ffill family convention -- suspension gaps give 0
      return, disclosed; pairwise-complete IC excludes NaN signal days).
  (2) SIZE 规模异象: small-cap premium -> negative IC of log size proxy.
      Signal = log10(mktcap_raw sidecar) = raw_close x osh. raw_close is
      exchange-exact (preclose x (1+pct/100) reconstruction); osh is the
      CURRENT share snapshot ffilled BACKWARD (R258 empirical probe: ~zero
      historical osh changes) -> SIZE is a PROXY: splits/dilutive issuance
      OVERSTATE past caps of share-growing names; OOS 2025+ segment
      near-TRUE (osh_today == osh_t). Suspension days stay NaN (no ffill).
  (3) DIVIDEND 红利风格 (DESCRIPTIVE style face, no IC): 510880 (上证红利ETF,
      sh510880.csv corpus, 4784 bars 2007-01-18..2026-09-22) price-face era
      table + 510300 overlap comparison (2020-01-02..). Price face EXCLUDES
      the ETF's cash distributions -> systematically UNDERSTATES the dividend
      style's total return = conservative lower bound (disclosed). Fund-event
      detector: |daily ret| > 11% flagged descriptively (512890 2021-10-22
      precedent family). Cross-cited, not redone: CN-DIV-LOWVOL-ROT s3
      rotation batch (corpus/event machinery), VOLATILITY-CE-01 registered
      trader (low_vol(60,5) daily entry lineage), p1e zoo85_stv composite.
- Forward: fwd_h = close.shift(-h)/close - 1, h in {5,10,20} (P1C HORIZONS
  shared; close ffill convention = P1C cache family).
- IC: shortline_p1_ic._ic_series_fast (gated reference implementation).
- Split: IS <= 2024-12-31 / OOS >= 2025-01-01 (composite_ic.IS_END shared).
- Blocks: stats_block full/is/oos; gates_v123 with thr from
  results/shortline/p1c_nulls.json (50 random signals, seed0=20260923, SAME
  universe/method/split -- random-signal |IC| null distribution is
  signal-agnostic; cited, not re-run; slice-A/C precedent).
- LAW faces (primary judgment): VOL60/h10 + SIZE/h10. Verdicts:
    lowvol_alive_oos = oos ic_mean < -thr.h10.p95_abs_ic (neg = low-vol premium)
    size_premium_alive_oos = oos ic_mean < -thr.h10.p95_abs_ic (neg = small premium)
    gates: v1/v2/v3/a3 via gates_v123 (abs-based, sign-agnostic).
- Era table (DESCRIPTIVE ONLY, no verdicts): h10 IC per era for vol20/vol60/
  size; plus 510880 style eras + mktcap cross-sectional median per era
  (market-structure evolution face). Eras pre-2005 / 2005-2014 / 2015-2016 /
  2017-2020 / 2021-2024 / 2025+.
- trials_N: 9 IC faces this batch (VOL{20,60} x h{5,10,20} + SIZE x h{5,10,20});
  nulls 50 in-ledger reference; zero RNG zero seed-registry surface.
- Honesty: no cost-adjusted portfolio claims (IC/descriptive face only).

Engineering: idempotent per-face checkpoint into
results/t73_s2/factor_history.json (re-run resumes missing faces only).
Exit 0 = batch complete; 2 = mechanism failure (sidecar missing = scope-down
to vol+dividend faces with size_honest_skip disclosed, exit 0).
Selftest subcommand = offline asserts (formula, window math, no-lookahead,
split/era boundaries, era/CAGR helpers, event detector, corpus presence).
"""
import io
import json
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import p1c_stock_ic_batch as P1C                    # cache/universe conventions
from composite_ic import IS_END, stats_block        # established methodology
from shortline_p1_ic import _ic_series_fast         # gated fast IC

OUT_DIR = os.path.join(ROOT, "results", "t73_s2")
OUT_JSON = os.path.join(OUT_DIR, "factor_history.json")
NULLS_JSON = os.path.join(ROOT, "results", "shortline", "p1c_nulls.json")
MKTCAP_NPY = os.path.join(P1C.CACHE_DIR, "mktcap_raw.npy")
DIV_CSV = os.path.join(ROOT, "data", "daily", "sh510880.csv")
HS300_CSV = os.path.join(ROOT, "data", "daily", "510300.csv")

VOL_WINDOWS = [20, 60]
HORIZONS = P1C.HORIZONS                            # [5, 10, 20] shared
ERAS = [("pre2005", None, "2004-12-31"),
        ("2005-2014", "2005-01-01", "2014-12-31"),
        ("2015-2016", "2015-01-01", "2016-12-31"),
        ("2017-2020", "2017-01-01", "2020-12-31"),
        ("2021-2024", "2021-01-01", "2024-12-31"),
        ("2025plus", "2025-01-01", None)]
DIV_EXPECTED_BARS = 4784          # corpus face (results/div_lowvol_rot_probe)
EVENT_RET_ABS = 0.11              # > ETF 10% daily band -> suspected fund event


def _min_periods(w):
    return max(1, int(np.ceil(w / 2)))


def _era_slice(s, a, b):
    lo = pd.Timestamp(a) if a else None
    hi = pd.Timestamp(b) if b else None
    seg = s
    if lo is not None:
        seg = seg[seg.index >= lo]
    if hi is not None:
        seg = seg[seg.index <= hi]
    return seg


def _cagr_maxdd(close):
    """CAGR (252/yr trading-day convention) + maxDD from a close series."""
    if len(close) < 20:
        return None
    ret = close.pct_change().dropna()
    n = len(close)
    total = float(close.iloc[-1] / close.iloc[0])
    yrs = n / 252.0
    cagr = total ** (1.0 / yrs) - 1.0 if total > 0 else np.nan
    ann_vol = float(ret.std() * np.sqrt(252.0))
    dd = float((close / close.cummax() - 1.0).min())
    return {"n_days": int(n), "cagr": round(cagr, 4),
            "ann_vol": round(ann_vol, 4), "max_dd": round(dd, 4)}


def _fund_events(close):
    ret = close.pct_change()
    bad = ret[ret.abs() > EVENT_RET_ABS]
    return [{"date": str(d.date()), "ret": round(float(v), 4)}
            for d, v in bad.items()]


def load_panels():
    idx, syms, meta = P1C.load_universe()
    close = pd.DataFrame(
        np.asarray(np.load(os.path.join(P1C.CACHE_DIR, "close.npy"),
                           mmap_mode="r"), dtype=np.float64),
        index=idx, columns=syms).ffill()
    cap = None
    if os.path.exists(MKTCAP_NPY):
        cap = pd.DataFrame(
            np.asarray(np.load(MKTCAP_NPY, mmap_mode="r"), dtype=np.float64),
            index=idx, columns=syms)
    return close, cap, meta


def selftest() -> int:
    thr = json.load(io.open(NULLS_JSON, encoding="utf-8"))
    assert thr["h10"]["p95_abs_ic"] == 0.0016 and thr["meta"]["n_nulls"] == 50
    # window math: trailing nanstd, min coverage, no-lookahead
    m = pd.DataFrame(np.arange(25, dtype=float).reshape(5, 5))
    m.iloc[1, :] = np.nan                       # full suspension row
    m.iloc[2, 1] = np.nan                       # single hole
    r = m.rolling(2, min_periods=_min_periods(2)).std()
    assert _min_periods(2) == 1 and _min_periods(20) == 10 \
        and _min_periods(60) == 30
    assert np.isnan(r.iloc[1, 0])               # one obs -> sample std (ddof=1) undefined = NaN, not fabricated 0
    assert np.isnan(r.iloc[2, 1])               # hole not fabricated
    # no-lookahead
    m2 = m.copy(); m2.iloc[3, 0] = 999.0
    r2 = m2.rolling(2, min_periods=1).std()
    assert np.array_equal(r2.iloc[:3, 0].values, r.iloc[:3, 0].values,
                          equal_nan=True)
    # IC sign: monotone anti-relation -> negative IC
    rng = np.random.default_rng(11)
    f = pd.DataFrame(rng.normal(size=(6, 12)))
    fwd = -f + 0.01 * pd.DataFrame(rng.normal(size=(6, 12)))
    s = _ic_series_fast(f, fwd)
    assert s.notna().all() and (s < 0).all()
    # split boundary sanity
    idx = pd.to_datetime(["2024-12-31", "2025-01-01", "2025-06-30"])
    assert (idx <= pd.Timestamp(IS_END)).tolist() == [True, False, False]
    # era mask boundaries: disjoint ascending contiguity
    edges = [pd.Timestamp(e[1]) if e[1] else pd.Timestamp("1900-01-01")
             for e in ERAS]
    ends = [pd.Timestamp(e[2]) if e[2] else pd.Timestamp("2100-01-01")
            for e in ERAS]
    for i in range(len(ERAS) - 1):
        assert ends[i] < edges[i + 1]
    # CAGR/maxDD helper: synthetic +50% in 252 days -> cagr 0.5, dd 0
    c = pd.Series(100.0 * (1.5 ** (np.arange(253) / 252.0)),
                  index=pd.date_range("2020-01-01", periods=253))
    st = _cagr_maxdd(c)
    assert abs(st["cagr"] - 0.5) < 0.01 and st["max_dd"] > -1e-9
    # maxDD face: 100 -> 50 -> 100 => dd -0.5
    c2 = pd.Series([100.0, 50.0, 100.0],
                   index=pd.date_range("2020-01-01", periods=3))
    assert _cagr_maxdd(c2) is None              # <20 days -> None (guard)
    c3 = pd.Series([100.0] + [50.0] * 10 + [100.0] * 12,
                   index=pd.date_range("2020-01-01", periods=23))
    assert abs(_cagr_maxdd(c3)["max_dd"] + 0.5) < 1e-9
    # fund event detector: 11% flagged, 9.9% not
    ce = pd.Series([1.0, 1.11, 1.11 * 1.099, 1.11 * 1.099 * 0.99],
                    index=pd.date_range("2020-01-01", periods=4))
    ev = _fund_events(ce)
    assert len(ev) == 1 and ev[0]["ret"] == round(0.11, 4)
    # corpus presence (repo-tracked data face, offline-safe)
    d = pd.read_csv(DIV_CSV)
    assert len(d) == DIV_EXPECTED_BARS, f"510880 corpus {len(d)} != {DIV_EXPECTED_BARS}"
    h = pd.read_csv(HS300_CSV)
    assert len(h) > 1600
    print("t73_s2 slice-D selftest: thr + std windows + no-lookahead + IC "
          "sign + split/era + CAGR/maxDD + event detector + corpus PASS")
    return 0


def run() -> int:
    os.makedirs(OUT_DIR, exist_ok=True)
    art = {}
    if os.path.exists(OUT_JSON):
        art = json.load(io.open(OUT_JSON, encoding="utf-8"))
    thr = json.load(io.open(NULLS_JSON, encoding="utf-8"))
    art.setdefault("prereg", {
        "ticket": "T-2026-09-26-73 s2 slice-D",
        "law": "size/low-vol/dividend factor history (规模低波红利因子史): "
               "(1) low-vol premium negative IC of vol level; (2) small-cap "
               "premium negative IC of true log mktcap; (3) dividend style "
               "descriptive era face",
        "signals": ["VOL20", "VOL60", "SIZE(log10 mktcap_raw)"],
        "signal_def": "VOL{w}=trailing nanstd of close returns "
                      "(ffill family, min_periods=ceil(w/2)); SIZE=log10 of "
                      "mktcap_raw sidecar (exchange-exact raw_close x "
                      "current-osh-ffilled-back PROXY -- splits/issuance "
                      "overstate past caps, OOS 2025+ near-true; sidecar "
                      "meta honesty_face), level, no ffill",
        "horizons": HORIZONS,
        "split": f"IS<={IS_END} / OOS>{IS_END}",
        "ic_impl": "shortline_p1_ic._ic_series_fast (gated reference)",
        "thresholds_ref": "results/shortline/p1c_nulls.json (50 nulls, "
                          "seed0=20260923, cited not re-run, slice-A/C "
                          "precedent)",
        "law_faces": ["VOL60/h10", "SIZE/h10"],
        "size_proxy_honesty": "SIZE faces are a PROXY (osh = current "
                              "snapshot ffilled back, R258 probe); IS "
                              "segment carries split/issuance distortion, "
                              "OOS 2025+ near-true; turnover_derived sidecar "
                              "shares the same osh provenance (cross-family "
                              "note, not a slice-C reopen -- its OOS face "
                              "is near-true and verdicts were alive both "
                              "sides)",
        "no_lookahead": "signal at t close (trailing), fwd from t close shift(-h)",
        "eras_descriptive_only": [e[0] for e in ERAS],
        "dividend_face_honesty": "510880 price face EXCLUDES cash "
                                 "distributions -> understates dividend "
                                 "style total return (conservative bound); "
                                 "fund-event detector |ret|>11% descriptive",
        "cross_cited_not_redone": ["CN-DIV-LOWVOL-ROT s3 (corpus+events)",
                                   "VOLATILITY-CE-01 trader (low_vol lineage)",
                                   "p1e zoo85_stv composite"],
    })
    art["evidence_cutoff"] = "2026-09-22"        # P1C cache family face
    art["trials_N"] = {"ic_faces_this_batch": 0, "nulls_reference_in_ledger": 50}
    faces_done = set(art.get("faces", {}).keys())

    close, cap, meta = load_panels()
    raw_close_last = np.asarray(
        np.load(os.path.join(P1C.CACHE_DIR, "close.npy"), mmap_mode="r"))
    fin_rows = np.flatnonzero(np.isfinite(raw_close_last).any(axis=1))
    art["cache_last_bar"] = str(
        close.index[fin_rows[-1]].date()) if len(fin_rows) else None
    dates_tail = str(close.index[-1].date())
    art["panel"] = {"T": int(close.shape[0]), "N": int(close.shape[1]),
                    "cache_last_date": dates_tail}
    t0 = time.time()

    rets = close.pct_change(fill_method=None)
    sigs = {f"VOL{w}": rets.rolling(w, min_periods=_min_periods(w)).std()
            for w in VOL_WINDOWS}
    size_avail = cap is not None
    if size_avail:
        sigs["SIZE"] = np.log10(cap)
    fwds = {h: close.shift(-h) / close - 1.0 for h in HORIZONS}

    faces = art.setdefault("faces", {})
    def do_face(key, sig, h):
        if key in faces_done:
            return
        s = _ic_series_fast(sig, fwds[h])
        blk = {"full": stats_block(s),
               "is": stats_block(s[s.index <= pd.Timestamp(IS_END)]),
               "oos": stats_block(s[s.index > pd.Timestamp(IS_END)])}
        g = P1C.gates_v123(blk["is"], blk["oos"], thr[f"h{h}"])
        faces[key] = {"blocks": blk, "gates": g, "n_days": int(s.notna().sum())}
        art["trials_N"]["ic_faces_this_batch"] += 1
        _flush(art)
        print(f"  face {key}: oos ic_mean={blk['oos']['ic_mean']:+.5f} "
              f"ir={blk['oos'].get('ic_ir', float('nan')):+.3f} "
              f"n={blk['oos'].get('n_periods', 0)} "
              f"gates_pass={g.get('pass')}", flush=True)

    for w in VOL_WINDOWS:
        for h in HORIZONS:
            do_face(f"vol{w}/h{h}", sigs[f"VOL{w}"], h)
    if size_avail:
        for h in HORIZONS:
            do_face(f"size/h{h}", sigs["SIZE"], h)
    else:
        art["size_honest_skip"] = ("mktcap_raw sidecar missing -> SIZE "
                                   "faces skipped honestly this run (build "
                                   "via scripts/t73_mktcap_sidecar.py)")

    # descriptive era table on h10 (applicability honesty; NO verdicts)
    era_tab = art.setdefault("era_table_h10", {})
    for sig_name in ([f"VOL{w}" for w in VOL_WINDOWS]
                     + (["SIZE"] if size_avail else [])):
        s = _ic_series_fast(sigs[sig_name], fwds[10])
        for name, a, b in ERAS:
            seg = _era_slice(s, a, b)
            era_tab.setdefault(sig_name, {})[name] = (
                stats_block(seg) if seg.notna().any() else None)

    # market-structure evolution: cross-sectional median TRUE cap per era
    if size_avail:
        med_tab = art.setdefault("mktcap_median_era", {})
        for name, a, b in ERAS:
            seg = _era_slice(cap, a, b)
            if len(seg):
                daily_med = seg.median(axis=1)
                daily_med = daily_med[daily_med > 0]
                med_tab[name] = (round(float(daily_med.median()), 1)
                                 if len(daily_med) else None)

    # frozen verdicts on the law faces
    thr10 = thr["h10"]["p95_abs_ic"]
    verdict = {}
    if "vol60/h10" in faces:
        v = faces["vol60/h10"]["blocks"]
        verdict["lowvol"] = {
            "law_face": "VOL60/h10", "thr_p95_abs_ic_h10": thr10,
            "oos_ic_mean": v["oos"]["ic_mean"], "is_ic_mean": v["is"]["ic_mean"],
            "lowvol_alive_oos": bool(v["oos"]["ic_mean"] < -thr10),
            "lowvol_alive_is": bool(v["is"]["ic_mean"] < -thr10),
            "gates_v123_pass": bool(faces["vol60/h10"]["gates"].get("pass")),
        }
    if "size/h10" in faces:
        v = faces["size/h10"]["blocks"]
        verdict["size"] = {
            "law_face": "SIZE/h10", "thr_p95_abs_ic_h10": thr10,
            "oos_ic_mean": v["oos"]["ic_mean"], "is_ic_mean": v["is"]["ic_mean"],
            "small_premium_alive_oos": bool(v["oos"]["ic_mean"] < -thr10),
            "small_premium_alive_is": bool(v["is"]["ic_mean"] < -thr10),
            "gates_v123_pass": bool(faces["size/h10"]["gates"].get("pass")),
        }
    verdict["honesty"] = ("IC-face research verdict only; no portfolio/cost "
                          "claim; applicability window in digest (era table "
                          "descriptive only)")
    art["verdict"] = verdict

    # DIVIDEND style face (descriptive)
    div = pd.read_csv(DIV_CSV, parse_dates=["date"]).set_index("date")["close"]
    hs = pd.read_csv(HS300_CSV, parse_dates=["date"]).set_index("date")["close"]
    div_tab = art.setdefault("dividend_style", {})
    div_tab.setdefault("honesty", {
        "price_face_no_dividends": True,
        "note": "510880 cash distributions excluded from price face -> "
                "style total return UNDERSTATED (conservative bound); "
                "510300 distributes ~nothing so the RELATIVE face is the "
                "lower bound of the true spread",
        "events_threshold_abs_ret": EVENT_RET_ABS,
    })
    if "eras_510880" not in div_tab:
        eras_out = {}
        for name, a, b in ERAS:
            seg = _era_slice(div, a, b)
            if len(seg) >= 20:
                eras_out[name] = _cagr_maxdd(seg)
        div_tab["eras_510880"] = eras_out
        div_tab["suspected_fund_events_510880"] = _fund_events(div)
        ov = div.index.intersection(hs.index)
        seg_d, seg_h = div[ov], hs[ov]
        div_tab["overlap_vs_510300"] = {
            "window": [str(ov[0].date()), str(ov[-1].date())],
            "n_days": int(len(ov)),
            "div_510880": _cagr_maxdd(seg_d), "hs300_510300": _cagr_maxdd(seg_h),
            "relative_cum": round(float(seg_d.iloc[-1] / seg_d.iloc[0])
                                 / (seg_h.iloc[-1] / seg_h.iloc[0]), 4),
        }

    art["elapsed_s"] = round(time.time() - t0, 1)
    art["ts"] = time.strftime("%Y-%m-%d %H:%M:%S")
    _flush(art)
    print(json.dumps({k: art[k] for k in ("verdict", "trials_N")
                      if k in art}, ensure_ascii=False, indent=1)[:1200],
          flush=True)
    return 0


def _flush(art):
    io.open(OUT_JSON, "w", encoding="utf-8", newline="\n").write(
        json.dumps(art, ensure_ascii=False, indent=1) + "\n")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    sys.exit({"run": run, "selftest": selftest}[cmd]())
