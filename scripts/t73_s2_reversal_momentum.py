# -*- coding: utf-8 -*-
"""T-73 s2 slice-A: A-share short-term REVERSAL vs MOMENTUM law, in-repo census
panel empirical check (CEO order O-20260926-0926 s2; CEO top criterion 实战出真知).

PRE-REGISTERED (frozen before first run; no threshold edits after seeing results):
- Signals (t close, no lookahead): REV{w} = -(close_t/close_{t-w} - 1), w in {5,20,60}.
  MOM{w} = +(...) is the exact mirror of REV{w} in rank space; verified empirically on
  one face (MOM20/h10) with per-day max|d| == 0, remaining MOM faces derived by mirror.
- Forward: fwd_h = close.shift(-h)/close - 1, h in {5,10,20} (P1C HORIZONS shared).
- IC: shortline_p1_ic._ic_series_fast (gated reference implementation, per-date
  cross-sectional spearman, pairwise-complete, >=5 names, zero-variance -> NaN).
- Split: IS <= 2024-12-31 / OOS >= 2025-01-01 (composite_ic.IS_END shared).
- Blocks: stats_block full/is/oos; gates_v123 with thr from results/shortline/
  p1c_nulls.json (50 random signals, seed0=20260923, SAME universe/method/split --
  cited, not re-run this round; per BACKTEST_PLAN the random baseline is on record
  and this batch's trial count N is disclosed in the artifact).
- LAW face (primary judgment): REV20 x h10. Verdicts:
    law_alive_oos   = oos ic_mean > thr.h10.p95_abs_ic (0.0016)  [reversal premium]
    law_alive_is    = is  ic_mean > thr.h10.p95_abs_ic
    mom_loses_face  = MOM20 oos ic_mean < -thr.h10.p95_abs_ic (momentum mirror loses)
    gates: v1/v2/v3 via gates_v123 on (is, oos) blocks.
- Honesty: no cost-adjusted portfolio claims here (IC face only, research-grade);
  applicability-window note lives in the digest, not the verdict.

Engineering: idempotent per-face checkpoint into results/t73_s2/rev_mom_ic.json
(re-run resumes missing faces only). Exit 0 = batch complete; 2 = gate/mechanism
failure. Selftest subcommand = offline asserts (mirror math, thr load, split
boundaries) without touching the panel.
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
OUT_JSON = os.path.join(OUT_DIR, "rev_mom_ic.json")
NULLS_JSON = os.path.join(ROOT, "results", "shortline", "p1c_nulls.json")

SIGNAL_WINDOWS = [5, 20, 60]
HORIZONS = P1C.HORIZONS                            # [5, 10, 20] shared
MIRROR_VERIFY_FACE = ("mom", 20, 10)               # one empirical mirror check


def load_close():
    """Census close panel only (thin-slice of P1C.load_panels: same cache, same
    ffill convention, single field -- loader thin-slice, not a reimplementation
    of the IC/fwd methodology)."""
    idx, syms, meta = P1C.load_universe()
    mm = np.load(os.path.join(P1C.CACHE_DIR, "close.npy"), mmap_mode="r")
    close = pd.DataFrame(np.asarray(mm, dtype=np.float64), index=idx, columns=syms)
    close = close.ffill()
    return close, meta


def _face_key(sig, w, h):
    return f"{sig}{w}/h{h}"


def selftest() -> int:
    thr = json.load(io.open(NULLS_JSON, encoding="utf-8"))
    assert thr["h10"]["p95_abs_ic"] == 0.0016 and thr["meta"]["n_nulls"] == 50
    # mirror math: rank(-x) == -rank(x) incl. tie groups (average method) -> IC mirror
    rng = np.random.default_rng(7)
    x = pd.DataFrame(rng.normal(size=(6, 12)))
    x.iloc[0, 3] = x.iloc[0, 4]            # force a tie
    x.iloc[2, :] = np.nan                   # zero-variance day -> NaN IC both signs
    fwd = pd.DataFrame(rng.normal(size=(6, 12)))
    a = _ic_series_fast(-x, fwd)
    b = _ic_series_fast(x, fwd)
    d = (a + b).abs().max()
    assert d == 0.0, f"mirror identity broken: {d}"
    # split boundary sanity
    idx = pd.to_datetime(["2024-12-31", "2025-01-01", "2025-06-30"])
    assert (idx <= pd.Timestamp(IS_END)).tolist() == [True, False, False]
    print("t73_s2 selftest: mirror identity + thr load + split boundary PASS")
    return 0


def run() -> int:
    os.makedirs(OUT_DIR, exist_ok=True)
    art = {}
    if os.path.exists(OUT_JSON):
        art = json.load(io.open(OUT_JSON, encoding="utf-8"))
    thr = json.load(io.open(NULLS_JSON, encoding="utf-8"))
    art.setdefault("prereg", {
        "ticket": "T-2026-09-26-73 s2 slice-A",
        "signals": [f"REV{w}" for w in SIGNAL_WINDOWS] + ["MOM20 (mirror)"],
        "signal_windows": SIGNAL_WINDOWS,
        "horizons": HORIZONS,
        "split": f"IS<={IS_END} / OOS>{IS_END}",
        "ic_impl": "shortline_p1_ic._ic_series_fast (gated reference)",
        "thresholds_ref": "results/shortline/p1c_nulls.json (50 nulls, seed0=20260923, cited not re-run)",
        "law_face": "REV20/h10",
        "no_lookahead": "signal at t close, fwd from t close shift(-h)",
    })
    faces_done = set(art.get("faces", {}).keys())

    close, meta = load_close()
    art["panel"] = {"T": int(close.shape[0]), "N": int(close.shape[1])}
    art["trials_N"] = {"ic_faces_this_batch": 0, "mirror_verify_faces": 0}

    t0 = time.time()
    # REV signals once per window; reuse across horizons
    sigs = {}
    for w in SIGNAL_WINDOWS:
        mom = close / close.shift(w) - 1.0
        sigs[("rev", w)] = -mom
        sigs[("mom", w)] = mom
    fwds = {h: close.shift(-h) / close - 1.0 for h in HORIZONS}

    faces = art.setdefault("faces", {})
    def do_face(sig, w, h):
        key = _face_key(sig, w, h)
        if key in faces_done:
            return
        s = _ic_series_fast(sigs[(sig, w)], fwds[h])
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
            do_face("rev", w, h)

    # empirical mirror verification on one face (MOM20/h10 must equal -REV20/h10)
    mk = _face_key("mom", 20, 10)
    if mk not in faces_done:
        s_mom = _ic_series_fast(sigs[("mom", 20)], fwds[10])
        s_rev = _ic_series_fast(sigs[("rev", 20)], fwds[10])
        j = s_mom.index.intersection(s_rev.index)
        d = float((s_mom[j] + s_rev[j]).abs().max())
        assert d == 0.0, f"mirror identity broken on real panel: max|d|={d}"
        blk = {"full": stats_block(s_mom),
               "is": stats_block(s_mom[s_mom.index <= pd.Timestamp(IS_END)]),
               "oos": stats_block(s_mom[s_mom.index > pd.Timestamp(IS_END)])}
        g = P1C.gates_v123(blk["is"], blk["oos"], thr["h10"])
        faces[mk] = {"blocks": blk, "gates": g, "n_days": int(s_mom.notna().sum()),
                     "mirror_vs_rev_max_abs_d": d}
        art["trials_N"]["ic_faces_this_batch"] += 1
        art["trials_N"]["mirror_verify_faces"] += 1
        _flush(art)
        print(f"  face {mk}: MIRROR VERIFIED max|d|={d} oos ic_mean="
              f"{blk['oos']['ic_mean']:+.5f}", flush=True)

    # derived MOM faces via exact mirror (mathematical identity, empirically verified)
    for w in SIGNAL_WINDOWS:
        for h in HORIZONS:
            mk = _face_key("mom", w, h)
            if mk in faces:
                continue
            rk = _face_key("rev", w, h)
            src = json.loads(json.dumps(faces[rk]))     # deep copy
            for seg in ("full", "is", "oos"):
                for k in src["blocks"][seg]:
                    if isinstance(src["blocks"][seg][k], (int, float)) and k in (
                            "ic_mean", "ic_ir", "ic_tstat"):
                        src["blocks"][seg][k] = -src["blocks"][seg][k]
            src["derived_by"] = f"mirror of {rk} (rank-space identity, empirically verified)"
            faces[mk] = src

    # frozen verdict on the law face
    law = faces["rev20/h10"]
    mom_law = faces["mom20/h10"]
    thr10 = thr["h10"]["p95_abs_ic"]
    art["verdict"] = {
        "law_face": "REV20/h10",
        "thr_p95_abs_ic_h10": thr10,
        "rev20_oos_ic_mean": law["blocks"]["oos"]["ic_mean"],
        "rev20_is_ic_mean": law["blocks"]["is"]["ic_mean"],
        "mom20_oos_ic_mean": mom_law["blocks"]["oos"]["ic_mean"],
        "law_alive_oos": bool(law["blocks"]["oos"]["ic_mean"] > thr10),
        "law_alive_is": bool(law["blocks"]["is"]["ic_mean"] > thr10),
        "mom_mirror_loses_oos": bool(mom_law["blocks"]["oos"]["ic_mean"] < -thr10),
        "gates_v123_pass": bool(law["gates"].get("pass")),
        "honesty": "IC-face research verdict only; no portfolio/cost claim; "
                   "applicability window in digest",
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
