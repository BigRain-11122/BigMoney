"""P-1e survivor neighbor-corr check runner (P1E_NEIGHBOR_CORR_CHECK.md,
frozen r227 bm-b).

Consumption-precondition machinery check for the two P-1e shelf survivors
(zoo85_stv / zoo92_coin_team) vs their frozen named neighbors, per the
shelf precondition (P1E_ZOO_BEHAVIOR_IC.md SS7 + STRATEGY_LIBRARY SS4 Zoo
row): D6 same-family max|corr| >= 0.7 rejection law, checked BEFORE any
joint synth batch may consume the materials as independent columns.

machinery-check class: zero engine runs, zero ledger appends, zero gate
writes, zero shelf flips (harvest round does the library bookkeeping).

Reuse only, no new construction logic:
  - p1c_stock_ic_batch: load_universe / load_alpha191_bigpanel
  - p1e_ic_batch: load_sidecar_tr / equivalence_gate (write-once
    checkpoint, p1e batch precedent)
  - p1e_factors: frozen constructors (selftest-gated) + _xs_spearman_series
  - shortline_p1_ic._ic_series_fast + composite_ic.IS_END
  - xstock_synth._lhb_event_grids: PA2-verbatim LHB event-grid core
    (dedup max-turnover row, rolling20, shift1 T+1; pa_lhb_ic constants)

Frozen protocol (spec SS1):
  verdict pairs : stv x terrified; coin_team x {alpha191_070,
                 alpha191_081, lhb_count_20}
  advisory pairs (disclosure only, NOT in verdict face):
                 stv x {alpha191_070, alpha191_081, lhb_count_20};
                 coin_team x terrified
  faces         : F1 xs_spearman_mean (per-date n>=5 intersection),
                  F2 ic10-series pearson (common > 30); IS-only
                  (<= IS_END 2024-12-31, OOS untouched, probe precedent)
  reject line   : max|corr| >= 0.7 over verdict pairs x both faces
                  -> REJECT else PASS (D6 law, no watch band)
  probe anchors : r219 probe F1/F2 recorded values must reproduce
                  (|delta| <= 1e-4) -- drift = fail-closed exit 1,
                  zero artifacts (r157 pairing law)

Subcommands:
  selftest   hermetic offline legs (no big-panel loads)
  run        the check -> results/shortline/p1e_neighbor_corr.json
             (idempotent: existing self-consistent output = skip)
"""
import argparse
import json
import os
import sys
import tempfile
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import p1c_stock_ic_batch as P1C                  # established harness
from composite_ic import IS_END                   # methodology constants
from shortline_p1_ic import _ic_series_fast       # gated fast IC path
from p1e_factors import (_xs_spearman_series,     # frozen constructors
                         build_zoo85_stv, build_zoo85_terrified,
                         build_zoo92_coin_team)
from p1e_ic_batch import equivalence_gate, load_sidecar_tr

OUT_JSON = os.path.join(P1C.OUT_DIR, "p1e_neighbor_corr.json")
SPEC = "research/shortline/P1E_NEIGHBOR_CORR_CHECK.md (frozen r227 bm-b)"
CUTOFF = "2026-09-22"            # frozen cache stamp (p1c_stock panel)
IS_END_TS = pd.Timestamp(IS_END)
REJECT_LINE = 0.7                # D6 same-family law (PREREG_TEMPLATE SS1)
F2_MIN_COMMON = 30               # probe convention
ANCHOR_TOL = 1e-4               # probe values recorded at 4dp

MATERIALS = ["zoo85_stv", "zoo92_coin_team"]
VERDICT_PAIRS = [
    ("zoo85_stv", "zoo85_terrified"),
    ("zoo92_coin_team", "alpha191_070"),
    ("zoo92_coin_team", "alpha191_081"),
    ("zoo92_coin_team", "lhb_count_20"),
]
ADVISORY_PAIRS = [
    ("zoo85_stv", "alpha191_070"),
    ("zoo85_stv", "alpha191_081"),
    ("zoo85_stv", "lhb_count_20"),
    ("zoo92_coin_team", "zoo85_terrified"),
]
# r219 probe anchors (results/shortline/p1e_probe.json, IS-only, 4dp).
# (kind, pair-in-frame-order, recorded value)
PROBE_ANCHORS = [
    ("f1", ("zoo85_stv", "zoo85_terrified"), 0.3365),
    ("f1", ("zoo85_stv", "alpha191_070"), 0.2408),
    ("f1", ("zoo85_stv", "alpha191_081"), 0.1988),
    ("f1", ("zoo92_coin_team", "zoo85_terrified"), 0.3547),
    ("f1", ("zoo92_coin_team", "alpha191_070"), 0.2584),
    ("f1", ("zoo92_coin_team", "alpha191_081"), 0.2028),
    ("f2", ("zoo85_stv", "zoo85_terrified"), 0.4384),
    ("f2", ("zoo92_coin_team", "zoo85_terrified"), 0.2985),
]


# ------------------------------------------------------------------ faces

def f1_pair(fa, fb, is_rows):
    """F1: per-date cross-sectional spearman time-mean on the IS slice."""
    sp = _xs_spearman_series(fa.loc[is_rows], fb.loc[is_rows])
    return (round(float(sp.mean()), 4) if len(sp) else None), int(len(sp))


def f2_pair(sa, sb):
    """F2: pearson of the two IS IC10 series over common periods."""
    common = sa.index.intersection(sb.index)
    if len(common) <= F2_MIN_COMMON:
        return None, int(len(common))
    c = float(np.corrcoef(sa[common].values, sb[common].values)[0, 1])
    return round(c, 4), int(len(common))


# ----------------------------------------------------------- verdict face

def verdict_face(pairs):
    """max|corr| over verdict-face pairs x both faces -> (verdict, argmax)."""
    best = (-1.0, None, None)
    for p in pairs:
        if not p["in_verdict_face"]:
            continue
        for face, key in (("f1", "f1_xs_spearman_mean"),
                          ("f2", "f2_ic10_pearson")):
            v = p[key]
            if v is None:
                continue
            if abs(v) > best[0]:
                best = (abs(v), f'{p["a"]}|{p["b"]}', face)
    return ("reject" if best[0] >= REJECT_LINE else "pass"), \
        round(best[0], 4), best[1], best[2]


def anchor_check(computed_pairs):
    """r157 pairing law: reuse legs must reproduce the probe anchors."""
    lookup = {(p["a"], p["b"]): p for p in computed_pairs}
    checks, all_ok = [], True
    for kind, (a, b), recorded in PROBE_ANCHORS:
        p = lookup.get((a, b))
        key = "f1_xs_spearman_mean" if kind == "f1" else "f2_ic10_pearson"
        got = p.get(key) if p else None
        ok = got is not None and abs(got - recorded) <= ANCHOR_TOL
        all_ok &= bool(ok)
        checks.append({"kind": kind, "pair": f"{a}|{b}",
                       "computed": got, "recorded": recorded,
                       "abs_delta": None if got is None
                       else round(abs(got - recorded), 6), "ok": bool(ok)})
    return checks, all_ok


# ------------------------------------------------------------------- run

def _selfconsistent(path):
    try:
        d = json.load(open(path, encoding="utf-8"))
        return (isinstance(d, dict) and {"verdict", "pairs",
                "evidence_cutoff", "probe_anchor"} <= set(d)
                and d.get("evidence_cutoff") == CUTOFF)
    except Exception:
        return False


def run():
    t0 = time.time()
    if _selfconsistent(OUT_JSON):
        print(f"checkpoint exists and self-consistent, skip: {OUT_JSON}",
              flush=True)
        return 0
    idx, syms, meta = P1C.load_universe()

    def _load(field, ffill=False):
        mm = np.load(os.path.join(P1C.CACHE_DIR, field + ".npy"),
                     mmap_mode="r")
        df = pd.DataFrame(np.asarray(mm, dtype=np.float64),
                          index=idx, columns=syms)
        if ffill:
            df = df.ffill()
        del mm
        return df

    close = _load("close", ffill=True)
    open_ = _load("open", ffill=True)
    tr_frac, tr_meta = load_sidecar_tr(idx, syms)
    panels = {"close": close, "open": open_}
    for f in ("high", "low", "volume", "amount", "turnover", "vwap"):
        panels[f] = _load(f, ffill=(f in ("high", "low")))
    ev = equivalence_gate(panels, "neighbor-corr/run")   # write-once ckpt
    print(f"panels loaded ({time.strftime('%H:%M:%S')})", flush=True)

    # -- frozen constructors (P-1e batch verbatim inputs)
    rets = close / close.shift(1) - 1.0
    frames = {
        "zoo85_terrified": build_zoo85_terrified(rets),
        "zoo85_stv": build_zoo85_stv(rets, tr_frac),
        "zoo92_coin_team": build_zoo92_coin_team(close, open_, tr_frac),
    }
    del rets
    mod = P1C.load_alpha191_bigpanel()
    frames["alpha191_070"] = mod.alpha191_070(panels)
    frames["alpha191_081"] = mod.alpha191_081(panels)
    del panels, mod
    print(f"factors constructed ({time.strftime('%H:%M:%S')})", flush=True)

    # -- LHB event grid on this calendar (PA2-verbatim core, T+1 shift1)
    from xstock_synth import _lhb_event_grids
    cal = idx.values.astype("datetime64[us]").astype("int64")
    col_map = {s: i for i, s in enumerate(syms)}
    count_s, _days, _share, _nb60, gmeta = _lhb_event_grids(
        cal, col_map, len(syms))
    frames["lhb_count_20"] = pd.DataFrame(count_s, index=idx, columns=syms)
    del count_s
    print(f"lhb grid placed: {json.dumps(gmeta, ensure_ascii=False)}",
          flush=True)

    # -- faces (IS-only; OOS untouched, probe precedent)
    is_rows = close.index <= IS_END_TS
    fwd10 = close.shift(-10) / close - 1.0
    del close, open_, tr_frac
    ic10 = {}
    for nm in frames:
        s = _ic_series_fast(frames[nm], fwd10)
        ic10[nm] = s[s.index <= IS_END_TS]
    del fwd10

    coverage = {}
    for nm, fdf in frames.items():
        fis = fdf.loc[is_rows]
        n_is = int(fis.notna().sum().sum())
        coverage[nm] = {
            "is_valid_cells": n_is,
            "is_valid_cell_share": round(n_is / float(np.prod(fis.shape)),
                                          4),
            "is_ic10_periods": int(len(ic10[nm])),
        }

    pairs = []
    for a, b in VERDICT_PAIRS + ADVISORY_PAIRS:
        tc = time.time()
        f1v, n1 = f1_pair(frames[a], frames[b], is_rows)
        f2v, n2 = f2_pair(ic10[a], ic10[b])
        pairs.append({"a": a, "b": b,
                      "in_verdict_face": (a, b) in VERDICT_PAIRS,
                      "f1_xs_spearman_mean": f1v, "f1_n_dates": n1,
                      "f2_ic10_pearson": f2v, "f2_n_common": n2})
        print(f"  {a}|{b}: F1={f1v} (n{n1}) F2={f2v} (n{n2}) "
              f"({time.time() - tc:.0f}s)", flush=True)

    checks, all_ok = anchor_check(pairs)
    if not all_ok:                       # fail-closed, zero artifacts
        print("PROBE ANCHOR DRIFT (fail-closed, zero artifacts):",
              flush=True)
        for c in checks:
            if not c["ok"]:
                print(f"  - {c['kind']} {c['pair']}: computed="
                      f"{c['computed']} recorded={c['recorded']}",
                      flush=True)
        sys.exit(1)

    v, mx, arg_pair, arg_face = verdict_face(pairs)
    out = {
        "meta": {
            "check": "P-1e survivor neighbor-corr check "
                     "(synth-batch consumption precondition)",
            "spec": SPEC,
            "claim": "MSG-20260926-0610-bm-b (F-04, r227)",
            "lane": "bm-b (machine-local p1c_stock cache + turnover "
                    "sidecar + lhb_detail.parquet, r188 lane-pin)",
            "class": "machinery-check: zero engine / zero ledger / "
                     "zero gate writes / zero shelf flips",
            "date": time.strftime("%Y-%m-%d %H:%M"),
            "is_end": str(IS_END),
            "window": "IS-only (<= IS_END; OOS untouched, r219 probe "
                       "precedent)",
            "materials": MATERIALS,
            "verdict_pairs": [f"{a}|{b}" for a, b in VERDICT_PAIRS],
            "advisory_pairs": [f"{a}|{b}" for a, b in ADVISORY_PAIRS],
            "constructors": "p1e_factors frozen (selftest-gated) + GTJA "
                            "vendor bigpanel + PA2-verbatim LHB event grid "
                            "(xstock_synth._lhb_event_grids, shift1 T+1)",
            "equivalence": ev,
            "turnover": tr_meta,
            "lhb_grid": gmeta,
            "elapsed_s": round(time.time() - t0, 1),
        },
        "evidence_cutoff": CUTOFF,        # C2 legal key (top level)
        "science_gates": {"cutoff_meta": CUTOFF},
        "verdict": {"verdict": v, "max_abs_corr": mx,
                    "argmax_pair": arg_pair, "argmax_face": arg_face,
                    "reject_line": REJECT_LINE,
                    "semantics": ">=0.7 over verdict-face pairs x {F1 "
                                 "xs_spearman_mean, F2 ic10 pearson} = "
                                 "REJECT (same-family duplicate; no "
                                 "independent column in joint synth batch)"},
        "probe_anchor": {"tol": ANCHOR_TOL,
                         "source": "results/shortline/p1e_probe.json "
                                   "(r219, IS-only)", "all_ok": True,
                         "checks": checks},
        "coverage": coverage,
        "pairs": pairs,
    }
    json.loads(json.dumps(out))            # verify-parse before write
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"verdict: {v} max|corr|={mx} argmax={arg_pair}/{arg_face}",
          flush=True)
    print(f"saved: {OUT_JSON} ({out['meta']['elapsed_s']}s)", flush=True)
    return 0


# -------------------------------------------------------------- selftest

def selftest():
    t0 = time.time()
    ok_all = True

    def check(name, cond):
        nonlocal ok_all
        ok_all &= bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}", flush=True)

    print("[1/7] F1 math leg (_xs_spearman_series, hand-computed):",
          flush=True)
    rng = np.random.default_rng(7)
    T, N = 12, 10
    idx = pd.date_range("2020-01-01", periods=T, freq="B")
    cols = [f"S{i}" for i in range(N)]
    base = pd.DataFrame(rng.standard_normal((T, N)), index=idx, columns=cols)
    holes = pd.DataFrame(rng.random((T, N)) < 0.8, index=idx, columns=cols)
    fa = base.where(holes)
    fb = -base.where(holes)                       # exact negation
    sp = _xs_spearman_series(fa, fb)
    check("F1(f, -f) == -1.0 all dates",
          len(sp) == T and bool(np.allclose(sp.values, -1.0)))
    sp2 = _xs_spearman_series(fa, fa)
    check("F1(f, f) == +1.0 all dates",
          len(sp2) == T and bool(np.allclose(sp2.values, 1.0)))
    # hand-computed single date: manual rank spearman on day 3
    row_a = fa.iloc[3].dropna()
    common = fa.iloc[3].index.intersection(fb.iloc[3].dropna().index)
    ra = fa.iloc[3][common].rank()
    rb = fb.iloc[3][common].rank()
    manual = float(np.corrcoef(ra.values, rb.values)[0, 1])
    check(f"F1 hand-computed date corr {manual:.4f} == series value",
          bool(np.isclose(manual, sp.iloc[3], atol=1e-12)))
    # n>=5 gate: a date with only 3 common symbols is excluded
    fa3, fb3 = fa.copy(), fb.copy()
    fa3.iloc[4, 3:] = np.nan
    fb3.iloc[4, 3:] = np.nan                      # 3 common remain
    sp3 = _xs_spearman_series(fa3, fb3)
    check("n>=5 gate drops the 3-common date", 4 not in sp3.index
          and len(sp3) == T - 1)

    print("[2/7] F2 leg (ic10-series pearson contract):", flush=True)
    sa = pd.Series(rng.standard_normal(100),
                   index=pd.date_range("2020-01-01", periods=100, freq="B"))
    sb = 0.5 * sa + 0.1 * pd.Series(rng.standard_normal(100), index=sa.index)
    v2, n2 = f2_pair(sa, sb)
    manual2 = float(np.corrcoef(sa.values, sb.values)[0, 1])
    check(f"F2 == manual corrcoef ({v2} vs {manual2:.4f})",
          v2 == round(manual2, 4) and n2 == 100)
    short = pd.Series(rng.standard_normal(10),
                      index=pd.date_range("2020-01-01", periods=10, freq="B"))
    v3, n3 = f2_pair(sa, short)
    check("F2 common<=30 -> None (probe convention)",
          v3 is None and n3 == 10)

    print("[3/7] LHB grid leg (synthetic events, hand-computed):",
          flush=True)
    import pa_lhb_ic
    from xstock_synth import _lhb_event_grids
    cal10 = pd.date_range("2020-01-01", periods=10, freq="D")
    cal_us = cal10.values.astype("datetime64[us]").astype("int64")
    ev = pd.DataFrame({
        "序号": [1, 2, 1, 1],
        "代码": ["A", "A", "A", "B"],
        "上榜日": ["2020-01-03", "2020-01-03", "2020-01-04", "2020-01-06"],
        "龙虎榜成交额": [100.0, 200.0, 150.0, 50.0],  # dup day -> max kept
        "成交额占总成交比": [0.1, 0.2, 0.15, 0.3],
        "龙虎榜净买额": [1.0, 2.0, 1.5, 3.0],
    })
    tmp = tempfile.mktemp(suffix=".parquet")
    ev.to_parquet(tmp, index=False)
    real_path = pa_lhb_ic.LHB_PATH
    try:
        pa_lhb_ic.LHB_PATH = tmp          # function imports attr at call
        count_s, days_s, _sh, _nb, gm = _lhb_event_grids(
            cal_us, {"A": 0, "B": 1}, 2)
    finally:
        pa_lhb_ic.LHB_PATH = real_path
        os.remove(tmp)
    exp_A = [0, 0, 0, 1, 2, 2, 2, 2, 2, 2]      # events day 2+3, shift1
    exp_B = [0, 0, 0, 0, 0, 0, 1, 1, 1, 1]      # event day 5 visible day 6
    check("count_s A == hand-computed (dedup + roll20 + shift1)",
          bool(np.allclose(count_s[:, 0], exp_A)))
    check("count_s B == hand-computed (T+1 visibility)",
          bool(np.allclose(count_s[:, 1], exp_B)))
    check("grid meta: raw 4 -> dedup 3 (max-turnover row kept per day)",
          gm["raw_rows"] == 4 and gm["dedup_events"] == 3
          and gm["placed"] == 3)

    print("[4/7] IS window leg (<= IS_END semantics):", flush=True)
    probe_idx = pd.DatetimeIndex(["2024-12-30", "2024-12-31",
                                  "2025-01-01", "2025-01-02"])
    m = probe_idx <= IS_END_TS
    check("boundary row 2024-12-31 included, next-day excluded",
          bool(m[1]) and not bool(m[2]) and list(m) == [True, True,
                                                        False, False])

    print("[5/7] verdict/threshold leg (D6 hard line + face isolation):",
          flush=True)
    mk = lambda a, b, f1, f2, vf: {"a": a, "b": b, "in_verdict_face": vf,
                                    "f1_xs_spearman_mean": f1,
                                    "f2_ic10_pearson": f2}
    v, mx, ap, af = verdict_face([
        mk("stv", "terr", 0.6999, 0.55, True),
        mk("coin", "lhb", 0.30, None, True)])
    check("0.6999 -> pass (max 0.6999)", v == "pass"
          and mx == 0.6999 and ap == "stv|terr" and af == "f1")
    v2b, mx2, ap2, af2 = verdict_face([
        mk("stv", "terr", 0.65, 0.7000, True),
        mk("coin", "lhb", 0.30, None, True)])
    check("0.7000 -> reject (>= semantics, F2 face)", v2b == "reject"
          and mx2 == 0.7 and af2 == "f2")
    v3c, _, _, _ = verdict_face([
        mk("stv", "terr", 0.10, 0.05, True),
        mk("coin", "lhb", 0.99, 0.95, False)])   # advisory only
    check("advisory 0.99 does NOT trigger reject (face isolation)",
          v3c == "pass")
    v4d, mx4, ap4, _ = verdict_face([
        mk("stv", "terr", -0.85, None, True)])
    check("|negative corr| -0.85 -> reject with |corr| semantics",
          v4d == "reject" and mx4 == 0.85 and ap4 == "stv|terr")

    print("[6/7] probe-anchor leg (drift = fail-closed):", flush=True)
    canned = [                          # all 8 anchors, reproducing values
        mk("zoo85_stv", "zoo85_terrified", 0.33654, 0.43842, True),
        mk("zoo85_stv", "alpha191_070", 0.24084, None, False),
        mk("zoo85_stv", "alpha191_081", 0.19883, None, False),
        mk("zoo92_coin_team", "zoo85_terrified", 0.35472, 0.29854, False),
        mk("zoo92_coin_team", "alpha191_070", 0.25842, None, True),
        mk("zoo92_coin_team", "alpha191_081", 0.20283, None, True),
    ]
    checks, ok = anchor_check(canned)
    check("all canned anchors reproduce within 1e-4",
          ok and len(checks) == len(PROBE_ANCHORS))
    drift = [mk("zoo85_stv", "zoo85_terrified", 0.5, 0.4384, True)]
    _, ok2 = anchor_check(drift)
    check("drifted F1 0.5 vs recorded 0.3365 -> not ok (fail-closed)",
          not ok2)

    print("[7/7] idempotency guard leg:", flush=True)
    tmpjson = tempfile.mktemp(suffix=".json")
    with open(tmpjson, "w", encoding="utf-8") as f:
        json.dump({"verdict": "pass", "pairs": [],
                   "evidence_cutoff": CUTOFF,
                   "probe_anchor": {"all_ok": True}}, f)
    check("self-consistent existing file -> guard True (skip path)",
          _selfconsistent(tmpjson))
    with open(tmpjson, "w", encoding="utf-8") as f:
        f.write("{corrupted")
    check("corrupted file -> guard False (rewrite path)",
          not _selfconsistent(tmpjson))
    os.remove(tmpjson)

    print(f"SELFTEST {'PASS' if ok_all else 'FAIL'} "
          f"({time.time() - t0:.0f}s)", flush=True)
    return 0 if ok_all else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["selftest", "run"])
    a = ap.parse_args()
    sys.exit(selftest() if a.mode == "selftest" else run())


if __name__ == "__main__":
    main()
