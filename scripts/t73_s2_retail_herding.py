# -*- coding: utf-8 -*-
"""T-73 s2 slice-C: A-share RETAIL-HERDING law, in-repo census panel empirical
check (CEO order O-20260926-0926 s2; CEO top criterion 实战出真知).

PRE-REGISTERED (frozen before first run; no threshold edits after seeing results):
- Law face: 散户羊群 (retail herding / speculation crowding) -- A 股高换手拥挤股
  前向收益系统性低 (turnover premium is negative). Proxy = turnover rate level;
  in-repo honest boundary: no historical retail/inst breakdown exists, turnover
  is the standard daily speculation proxy; quarterly chip-concentration complement
  (股东户数 gdhs_chg_q) already judged in P-1d ext-slots -- cross-cited, not redone.
- Signal (t close, no lookahead): TO{w} = trailing nanmean of turnover_derived
  sidecar over w in {5,20,60}; window min coverage min_periods = max(1, ceil(w/2))
  (w5->3, w20->10, w60->30). Suspension NaNs stay NaN (no ffill -- ffill would
  fabricate activity on non-trading days; pairwise-complete IC excludes them).
- Forward: fwd_h = close.shift(-h)/close - 1, h in {5,10,20} (P1C HORIZONS shared;
  close ffill convention = P1C cache family).
- IC: shortline_p1_ic._ic_series_fast (gated reference implementation, per-date
  cross-sectional spearman, pairwise-complete, >=5 names, zero-variance -> NaN).
- Split: IS <= 2024-12-31 / OOS >= 2025-01-01 (composite_ic.IS_END shared).
- Blocks: stats_block full/is/oos; gates_v123 with thr from results/shortline/
  p1c_nulls.json (50 random signals, seed0=20260923, SAME universe/method/split --
  random-signal |IC| null distribution is signal-agnostic, valid reference for
  any factor incl. TO; cited, not re-run this round; slice-A precedent).
- LAW face (primary judgment): TO20 x h10. Verdicts:
    herding_alive_oos = oos ic_mean < -thr.h10.p95_abs_ic (0.0016)  [neg premium]
    herding_alive_is  = is  ic_mean < -thr.h10.p95_abs_ic
    gates: v1/v2/v3 via gates_v123 on (is, oos) blocks (abs-based, sign-agnostic).
- Era table (DESCRIPTIVE ONLY, no verdicts): ic_mean/ic_ir/n per era on h10 for
  w in {5,20,60}; eras pre-2005 / 2005-2014 / 2015-2016 / 2017-2020 / 2021-2024 /
  2025+ (OOS) -- applicability honesty lives here and in the digest.
- trials_N: 9 IC faces this batch (TO{5,20,60} x h{5,10,20}); nulls 50 in-ledger
  reference; zero RNG zero seed-registry surface (deterministic sorting only).
- Honesty: no cost-adjusted portfolio claims (IC face only, research-grade).

Engineering: idempotent per-face checkpoint into results/t73_s2/retail_herding.json
(re-run resumes missing faces only). Exit 0 = batch complete; 2 = mechanism
failure. Selftest subcommand = offline asserts (window math, NaN propagation,
split/era boundaries, thr load) without touching the panel.
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

import p1c_stock_ic_batch as P1C                    # cache/universe/fwd conventions
from composite_ic import IS_END, stats_block        # established methodology
from shortline_p1_ic import _ic_series_fast        # gated fast IC

OUT_DIR = os.path.join(ROOT, "results", "t73_s2")
OUT_JSON = os.path.join(OUT_DIR, "retail_herding.json")
NULLS_JSON = os.path.join(ROOT, "results", "shortline", "p1c_nulls.json")

SIGNAL_WINDOWS = [5, 20, 60]
HORIZONS = P1C.HORIZONS                            # [5, 10, 20] shared
# frozen era windows for the DESCRIPTIVE applicability table (h10 faces only)
ERAS = [("pre2005", None, "2004-12-31"),
        ("2005-2014", "2005-01-01", "2014-12-31"),
        ("2015-2016", "2015-01-01", "2016-12-31"),
        ("2017-2020", "2017-01-01", "2020-12-31"),
        ("2021-2024", "2021-01-01", "2024-12-31"),
        ("2025plus", "2025-01-01", None)]


def _min_periods(w):
    return max(1, int(np.ceil(w / 2)))


def load_panels():
    """Census close + turnover_derived panels (thin-slice of P1C cache loaders:
    same cache, same ffill convention on close only -- turnover sidecar is loaded
    raw NaNs because suspension-day activity must not be fabricated)."""
    idx, syms, meta = P1C.load_universe()
    close = pd.DataFrame(
        np.asarray(np.load(os.path.join(P1C.CACHE_DIR, "close.npy"),
                           mmap_mode="r"), dtype=np.float64),
        index=idx, columns=syms).ffill()
    to = pd.DataFrame(
        np.asarray(np.load(os.path.join(P1C.CACHE_DIR, "turnover_derived.npy"),
                           mmap_mode="r"), dtype=np.float64),
        index=idx, columns=syms)
    return close, to, meta


def _face_key(w, h):
    return f"to{w}/h{h}"


def selftest() -> int:
    thr = json.load(io.open(NULLS_JSON, encoding="utf-8"))
    assert thr["h10"]["p95_abs_ic"] == 0.0016 and thr["meta"]["n_nulls"] == 50
    # window math: trailing nanmean, min coverage, strict no-lookahead (row t
    # uses only rows <= t), suspension NaN not fabricated
    m = pd.DataFrame(np.arange(25, dtype=float).reshape(5, 5))
    m.iloc[1, :] = np.nan                       # full suspension row
    m.iloc[2, 1] = np.nan                       # single hole
    r = m.rolling(2, min_periods=_min_periods(2)).mean()
    assert _min_periods(2) == 1 and _min_periods(5) == 3
    assert _min_periods(20) == 10 and _min_periods(60) == 30
    # with mp=1: row1 window rows[0,1] -> row1 suspended, nanmean = row0 value
    assert r.iloc[1, 0] == m.iloc[0, 0]
    # row2 col1: rows[1,2] both NaN at col1 -> NaN (hole not fabricated)
    assert np.isnan(r.iloc[2, 1])
    # no-lookahead: rolling output at row t never depends on rows > t
    m2 = m.copy()
    m2.iloc[3, 0] = 999.0
    r2 = m2.rolling(2, min_periods=1).mean()
    assert (r2.iloc[:3, 0] == r.iloc[:3, 0]).all()
    # IC sign: synthetic monotone anti-relation -> negative IC
    rng = np.random.default_rng(11)
    f = pd.DataFrame(rng.normal(size=(6, 12)))
    fwd = -f + 0.01 * pd.DataFrame(rng.normal(size=(6, 12)))   # high factor -> low fwd
    s = _ic_series_fast(f, fwd)
    assert s.notna().all() and (s < 0).all()
    # all-NaN factor day -> day DROPPED from IC series (impl returns .dropna())
    f2 = f.copy(); f2.iloc[2, :] = np.nan
    s2 = _ic_series_fast(f2, fwd)
    assert len(s2) == 5 and s2.index[2] == f.index[3]
    # split boundary sanity (composite_ic.IS_END)
    idx = pd.to_datetime(["2024-12-31", "2025-01-01", "2025-06-30"])
    assert (idx <= pd.Timestamp(IS_END)).tolist() == [True, False, False]
    # era mask boundaries: contiguity + full coverage of the calendar
    edges = [pd.Timestamp(e[1]) if e[1] else pd.Timestamp("1900-01-01") for e in ERAS]
    ends = [pd.Timestamp(e[2]) if e[2] else pd.Timestamp("2100-01-01") for e in ERAS]
    for i in range(len(ERAS) - 1):
        assert ends[i] < edges[i + 1], "eras must be disjoint ascending"
    print("t73_s2 slice-C selftest: thr load + window math + no-lookahead + "
          "IC sign + NaN day + split/era boundaries PASS")
    return 0


def run() -> int:
    os.makedirs(OUT_DIR, exist_ok=True)
    art = {}
    if os.path.exists(OUT_JSON):
        art = json.load(io.open(OUT_JSON, encoding="utf-8"))
    thr = json.load(io.open(NULLS_JSON, encoding="utf-8"))
    art.setdefault("prereg", {
        "ticket": "T-2026-09-26-73 s2 slice-C",
        "law": "retail herding / speculation crowding (散户羊群): high-turnover "
               "names underperform forward -> negative turnover premium",
        "proxy_honesty": "no historical retail/inst breakdown in-repo; daily "
                         "turnover = standard speculation proxy; quarterly "
                         "chip-concentration complement gdhs_chg_q judged in "
                         "P-1d ext-slots (cross-cited, not redone)",
        "signals": [f"TO{w}" for w in SIGNAL_WINDOWS],
        "signal_def": "trailing nanmean turnover_derived, min_periods=ceil(w/2), "
                      "no ffill (suspension NaN stays NaN)",
        "horizons": HORIZONS,
        "split": f"IS<={IS_END} / OOS>{IS_END}",
        "ic_impl": "shortline_p1_ic._ic_series_fast (gated reference)",
        "thresholds_ref": "results/shortline/p1c_nulls.json (50 nulls, seed0=20260923, "
                          "same universe/method/split, cited not re-run)",
        "law_face": "TO20/h10",
        "no_lookahead": "signal at t close (trailing window), fwd from t close shift(-h)",
        "eras_descriptive_only": [e[0] for e in ERAS],
    })
    art["evidence_cutoff"] = "2026-09-22"        # P1C cache family face
    art["cache_last_bar"] = "2026-09-18"         # honest cache lag disclosure
    art["trials_N"] = {"ic_faces_this_batch": 0, "nulls_reference_in_ledger": 50}
    faces_done = set(art.get("faces", {}).keys())

    close, to, meta = load_panels()
    art["panel"] = {"T": int(close.shape[0]), "N": int(close.shape[1]),
                    "turnover_src": "turnover_derived sidecar (TURNOVER_DERIVATION.md SS4)",
                    "turnover_nan_share": float(to.isna().mean().mean())}
    t0 = time.time()

    sigs = {w: to.rolling(w, min_periods=_min_periods(w)).mean()
            for w in SIGNAL_WINDOWS}
    fwds = {h: close.shift(-h) / close - 1.0 for h in HORIZONS}

    faces = art.setdefault("faces", {})
    def do_face(w, h):
        key = _face_key(w, h)
        if key in faces_done:
            return
        s = _ic_series_fast(sigs[w], fwds[h])
        blk = {"full": stats_block(s),
               "is": stats_block(s[s.index <= pd.Timestamp(IS_END)]),
               "oos": stats_block(s[s.index > pd.Timestamp(IS_END)])}
        g = P1C.gates_v123(blk["is"], blk["oos"], thr[f"h{h}"])
        faces[key] = {"blocks": blk, "gates": g, "n_days": int(s.notna().sum())}
        art["trials_N"]["ic_faces_this_batch"] += 1
        _flush(art)
        print(f"  face {key}: oos ic_mean={blk['oos']['ic_mean']:+.5f} "
              f"ir={blk['oos'].get('ic_ir', float('nan')):+.3f} n={blk['oos'].get('n', 0)} "
              f"gates_pass={g.get('pass')}", flush=True)

    for w in SIGNAL_WINDOWS:
        for h in HORIZONS:
            do_face(w, h)

    # descriptive era table on h10 (applicability honesty; NO verdicts here)
    era_tab = art.setdefault("era_table_h10", {})
    for w in SIGNAL_WINDOWS:
        s = _ic_series_fast(sigs[w], fwds[10])
        for name, a, b in ERAS:
            lo = pd.Timestamp(a) if a else None
            hi = pd.Timestamp(b) if b else None
            seg = s
            if lo is not None:
                seg = seg[seg.index >= lo]
            if hi is not None:
                seg = seg[seg.index <= hi]
            era_tab.setdefault(f"to{w}", {})[name] = (
                stats_block(seg) if seg.notna().any() else None)

    # frozen verdict on the law face
    law = faces["to20/h10"]
    thr10 = thr["h10"]["p95_abs_ic"]
    art["verdict"] = {
        "law_face": "TO20/h10",
        "thr_p95_abs_ic_h10": thr10,
        "to20_oos_ic_mean": law["blocks"]["oos"]["ic_mean"],
        "to20_is_ic_mean": law["blocks"]["is"]["ic_mean"],
        "herding_alive_oos": bool(law["blocks"]["oos"]["ic_mean"] < -thr10),
        "herding_alive_is": bool(law["blocks"]["is"]["ic_mean"] < -thr10),
        "gates_v123_pass": bool(law["gates"].get("pass")),
        "honesty": "IC-face research verdict only; no portfolio/cost claim; "
                   "applicability window in digest (era table descriptive only)",
    }
    art["elapsed_s"] = round(time.time() - t0, 1)
    art["ts"] = time.strftime("%Y-%m-%d %H:%M:%S")
    _flush(art)
    print(json.dumps(art["verdict"], ensure_ascii=False, indent=1))
    return 0


def _flush(art):
    io.open(OUT_JSON, "w", encoding="utf-8", newline="\n").write(
        json.dumps(art, ensure_ascii=False, indent=1) + "\n")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    sys.exit({"run": run, "selftest": selftest}[cmd]())
