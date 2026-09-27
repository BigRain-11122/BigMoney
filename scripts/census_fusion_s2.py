# -*- coding: utf-8 -*-
"""CENSUS_FUS_S2_W1 runner -- T-86 s2 factor-level fusion census (wave-1 core48).

Prereg (FROZEN precedes this build, R99): research/CENSUS_FUSION_S2_PREREG.md
@ commit e51e55e0. EXPLORATION FACE: zero judgment claims / zero paper
eligibility; sole output = frozen-rules family aggregation feeding the T-23
intake funnel (judged consumers carry their own prereg + gates).

Single-source anchors (zero-invention law, FACTOR_CENSUS_REGISTRY.md):
  - 28 A-row faces : engine/factors.py FACTORS via compute_all (source anchor)
  - G-row lowamp20 : 20d mean((high-low)/close), sign prior '-' (registry v1.1)
  - F-row bench    : rs_20_csi300 / rs_60_csi300 (compute_all bench branch),
                     control-only faces -> 29x2 = 58 control pairs
  - sign priors    : scripts/factor_registry.py ENGINE_FACES (+ G/F rows)
  - loader         : research/shortline/screening/p1_factor_screen.py
                     load_core48 semantics (bare code, >=60 rows)
  - IC estimator   : p1_factor_screen.ic_series (P-1/P-2 recorded line)
  - cost faces     : scripts/alloc_backtest.py side_cost_v2 / side_cost_x2
                     (shared single source; V2 ADV20 tiers + 1% ADV entry cap)
  - seeds          : science_gates.SEED_REGISTRY['census_fusion_s2'] = 20274500
                     (band 20274500..20274900, K=400 combo nulls)

Blend face (prereg sec.3 frozen): weekly (5-trading-day) grid, common anchor;
signal at t, exec next close (t+1) conservative T+1 proxy; long leg = combo
score top-16/48 equal weight; entry notional capped at 1% ADV20(signal day);
two-leg turnover costs per changed member; x1 = V2, x2 = doubled (comm rate
AND floor). Fixed weights inside each window (no intra-window drift). NAV
starts at 1,000,000 (fleet paper convention). Day accounting: exec day e
carries the OLD positions' final close-to-close return (close e-1 -> e) minus
the transition cost; new positions accrue from e+1 to the next exec day.

Ledger: append_ledger("CENSUS_FUS_S2_W1", 4518, ...) embedded under the
trials_ledger key (r252 law). audit section mandatory (O-1810). Native-type
coercion at every dump site + non-native injection selftest leg (r286 law).
In-runner fail-closed data gates exit 2 (prereg sec.2). Checkpoint every 200
combos (JSONL, cross-kill resume). Deterministic: byte-stable rerun (r253).

Usage: python scripts/census_fusion_s2.py run | unc | probe | selftest
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "research", "shortline", "screening"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "scripts"))

import numpy as np
import pandas as pd

from config import PATHS
from engine.factors import FACTORS, compute_all, rs_vs
from science_gates import SEED_REGISTRY, append_ledger, cutoff_meta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "results", "census_fusion_s2")
CKPT = os.path.join(OUT_DIR, "w1_checkpoint.jsonl")

BATCH = "CENSUS_FUS_S2_W1"
TICKET = "T-2026-09-26-86-P1 s2 (CEO O-20260926-2320)"
PREREG = ("research/CENSUS_FUSION_S2_PREREG.md FROZEN e51e55e0 "
          "precedes runner build precedes ANY run (R99)")
CUTOFF = "2026-09-24"                       # evidence_cutoff (prereg sec.2)
N_MEMBERS = 48
TOP_K = 16                                  # long leg = top tercile (16/48)
HORIZON = 5                                 # IC forward 5d close->close
REB = 5                                     # weekly grid, 5 trading days
NOTIONAL = 1_000_000.0
N_NULLS = 400                               # 200 random pairs + 200 random triples
BLOCK = 200                                 # checkpoint cadence (prereg sec.0)
SEED_BASE = SEED_REGISTRY["census_fusion_s2"]
LOWAMP_SIGN = -1.0                          # G-row prior: low amplitude = premium
RS_SIGN = 1.0                               # bench rs convention (disclosed)
BENCH_FACES = ["rs_20_csi300", "rs_60_csi300"]

# --- s3 UNC face (prereg sec.3 s3 frozen rules + sec.9.1 seed freeze, R290) ---
UNC_BATCH = "CENSUS_FUS_S2_W1-UNC"
UNC_TICKET = "T-2026-09-26-86-P1 s3 (CEO O-20260926-2320)"
UNC_PREREG = ("research/CENSUS_FUSION_S2_PREREG.md sec.3 s3 frozen rules + "
              "sec.9.1 seed freeze commit precedes unc runner build (R99)")
UNC_B = 200                                 # block bootstrap draws (frozen)
UNC_BLOCK = 20                              # trading days per block (frozen)
UNC_P = 200                                 # sign-flip permutations (frozen)
UNC_SEED = SEED_REGISTRY["census_fusion_s2_unc"]
UNC_CKPT = os.path.join(OUT_DIR, "unc_checkpoint.jsonl")


# ---------------------------------------------------------------- face roster

def _sign_priors():
    """{face: sign float} for 29 candidate faces + 2 bench faces."""
    from factor_registry import ENGINE_FACES
    priors = {n: (1.0 if s == "+" else -1.0) for n, (_f, s, _p) in ENGINE_FACES.items()}
    priors["lowamp20"] = LOWAMP_SIGN
    for b in BENCH_FACES:
        priors[b] = RS_SIGN
    return priors


def _faces_sorted():
    """29 candidate faces (28 engine + lowamp20), registry order = sorted."""
    return sorted(FACTORS.keys()) + ["lowamp20"]


# ---------------------------------------------------------------- data gates

def load_universe():
    """p1_factor_screen.load_core48 semantics (prereg sec.2 loader anchor)."""
    from p1_factor_screen import load_core48
    return load_core48()


def data_gate(univ):
    """Fail-closed completeness gate (prereg sec.2): returns (ok, report)."""
    rep = {"n_members": len(univ), "gate_members": len(univ) == N_MEMBERS}
    cols_ok, rows_ok, end_ok, vol_ok = True, True, True, True
    ends = set()
    for sym, df in univ.items():
        need = {"open", "high", "low", "close", "volume", "amount"}
        cols_ok &= need.issubset(set(df.columns))
        rows_ok &= len(df) >= 60
        ends.add(str(df.index.max().date()))
        vol_ok &= bool((df["volume"] > 0).any())
    end_ok &= ends == {CUTOFF}
    rep.update({"gate_columns": bool(cols_ok), "gate_min_rows": bool(rows_ok),
                "gate_end_date": bool(end_ok), "gate_volume_mask": bool(vol_ok),
                "end_dates_unique": sorted(ends)})
    rep["ok"] = all([rep["gate_members"], cols_ok, rows_ok, end_ok, vol_ok])
    return rep["ok"], rep


# ---------------------------------------------------------------- panel build

def _zscore(F):
    """Cross-sectional z-score per date (rows with <2 valid -> NaN)."""
    mu = F.mean(axis=1)
    sd = F.std(axis=1)
    Z = F.sub(mu, axis=0).div(sd.replace(0, np.nan), axis=0)
    Z[sd < 1e-12] = np.nan
    Z[F.notna().sum(axis=1) < 2] = np.nan
    return Z


def _tercile_labels(Z):
    """Per-date tercile labels 0/1/2 (-1 = invalid) as int8 array."""
    pct = Z.rank(axis=1, pct=True)
    lab = np.full(Z.shape, -1, dtype=np.int8)
    lab[np.asarray((pct > 0) & (pct <= 1.0 / 3.0))] = 0
    lab[np.asarray((pct > 1.0 / 3.0) & (pct <= 2.0 / 3.0))] = 1
    lab[np.asarray(pct > 2.0 / 3.0)] = 2
    return lab


def build_state(univ, bench):
    """All shared arrays for workers: faces/z-scores/terciles/returns/adv/grid."""
    prices = {s: df[df.index <= pd.Timestamp(CUTOFF)] for s, df in univ.items()}
    cutoff_real = max(df.index.max() for df in prices.values())
    factors = compute_all(prices, bench)          # 28 A-row + 2 rs bench faces
    panel = {}
    for fld in ["open", "high", "low", "close", "volume", "amount"]:
        panel[fld] = pd.DataFrame({s: p[fld] for s, p in prices.items()}).sort_index().ffill()
    factors["lowamp20"] = ((panel["high"] - panel["low"]) / panel["close"]).rolling(20).mean()

    close = panel["close"]
    idx = close.index
    syms = list(close.columns)
    rets = close.pct_change()
    fwd5 = close.shift(-HORIZON) / close - 1
    adv20 = panel["amount"].rolling(20).mean()

    faces = _faces_sorted()
    zed, terc = {}, {}
    for f in faces + BENCH_FACES:
        F = factors[f].reindex(index=idx, columns=syms)
        Z = _zscore(F)
        zed[f] = Z
        terc[f] = _tercile_labels(Z)

    # common grid anchor: first date where every candidate face has >=TOP_K valid
    valid_min = None
    for f in faces:
        cnt = zed[f].notna().sum(axis=1)
        valid_min = cnt if valid_min is None else np.minimum(valid_min, cnt)
    feasible = np.asarray(valid_min) >= TOP_K
    anchor = int(np.argmax(feasible)) if feasible.any() else -1
    grid_sig = list(range(anchor, len(idx) - 1, REB)) if anchor >= 0 else []
    grid_exec = [g + 1 for g in grid_sig if g + 1 < len(idx)]

    return {
        "idx": idx, "syms": syms, "faces": faces, "sign": _sign_priors(),
        "zed": zed, "terc": terc, "rets": rets, "fwd5": fwd5, "adv20": adv20,
        "grid_sig": grid_sig, "grid_exec": grid_exec,
        "years": np.array([d.year for d in idx]),
        "cutoff_real": str(cutoff_real.date()), "n_days": len(idx),
    }


# ---------------------------------------------------------------- blend face

def blend_top16(state, score_row_fn, x2=False, fixed_all=False,
                return_series=False, top_k=None):
    """Weekly-grid long-leg blend: top-16 equal weight, V2 costs, 1% ADV cap.

    score_row_fn(sig_i) -> (48,) combo score at signal date, or None.
    fixed_all=True -> EW48 benchmark (all members, constant membership).
    top_k=None -> TOP_K (wave-1 default path byte-stable); int override for
    wave-2 wide-universe instantiation (prereg sec.9.3 top-50, disclosed
    divergence from wave-1 top-tercile).
    Exec day e carries old positions' final close-to-close return minus the
    transition cost; new positions accrue e+1 .. next exec day.
    return_series=True -> (metrics, daily_net_series, first_exec) for the
    s3 UNC face (sec.3 s3); default path unchanged (w1 byte-stable).
    """
    k = TOP_K if top_k is None else int(top_k)
    from alloc_backtest import side_cost_v2, side_cost_x2
    fn = side_cost_x2 if x2 else side_cost_v2
    rets = np.asarray(state["rets"], dtype=float)
    adv = np.asarray(state["adv20"], dtype=float)
    pairs = [(g, e) for g, e in zip(state["grid_sig"], state["grid_exec"]) if e < state["n_days"]]
    T, n_sym = state["n_days"], len(state["syms"])

    nav = NOTIONAL
    prev_w = {}
    daily = np.zeros(T, dtype=float)
    capped = 0
    first_exec = pairs[0][1] if pairs else 0

    def _accrue(d, wmap):
        r = 0.0
        for s, w in wmap.items():
            rv = rets[d, s]
            if np.isfinite(rv):
                r += w * rv
        return r

    for j, (g, e) in enumerate(pairs):
        # 1) exec day: old positions' final return, then transition cost
        r_old = _accrue(e, prev_w) if prev_w else 0.0
        # 2) target set from the signal at g
        if fixed_all:
            target = list(range(n_sym))
        else:
            row = score_row_fn(g)
            if row is None:
                target = []
            else:
                valid = np.where(np.isfinite(row))[0]
                target = [] if len(valid) < k else list(valid[np.argsort(-row[valid])[:k]])
        tset = set(target)
        want = NOTIONAL / len(target) if target else 0.0
        buys = []
        for s, w in prev_w.items():
            if s not in tset:
                a = adv[g, s]
                nav -= fn(w * nav, a if np.isfinite(a) else float("nan"))
        for s in target:
            if s not in prev_w:
                a = adv[g, s]
                cap = 0.01 * a if np.isfinite(a) and a > 0 else 0.0
                filled = min(want, cap) if cap > 0 else 0.0
                if filled <= 0:
                    continue               # zero/missing ADV: entry does not fill
                if filled < want:
                    capped += 1
                buys.append((s, filled / NOTIONAL))
        cost = 0.0
        for s, w in buys:
            a = adv[g, s]
            cost += fn(w * nav, a if np.isfinite(a) else float("nan"))
        nav_prev = nav
        nav = nav * (1.0 + r_old) - cost
        daily[e] = (r_old * nav_prev - cost) / nav_prev if nav_prev > 0 else 0.0
        # 3) swap membership (staying keep fixed weight; no intra-window drift)
        new_w = {s: prev_w[s] for s in tset if s in prev_w}
        for s, w in buys:
            new_w[s] = w
        prev_w = new_w
        # 4) accrue e+1 .. (next exec day - 1); the last window runs to panel
        #    end (stop = T), so no separate tail pass is needed
        stop = pairs[j + 1][1] if j + 1 < len(pairs) else T
        for d in range(e + 1, stop):
            if d >= T:
                break
            r = _accrue(d, prev_w)
            daily[d] = r
            nav *= (1.0 + r)
    del nav
    met = _metrics(daily[first_exec:], state, first_exec, capped)
    if return_series:
        return met, daily[first_exec:], first_exec
    return met


def _metrics(series, state, first_exec, capped):
    """Annualized/vol/Sharpe/maxDD/monthly-win from the daily net series."""
    if len(series) < 20:
        return {"ann": None, "vol": None, "sharpe": None, "maxdd": None,
                "monthly_win": None, "n_days": int(len(series)),
                "capped_entries": int(capped)}
    ann = float(np.mean(series) * 252.0)
    sd = float(np.std(series, ddof=1))
    vol = sd * np.sqrt(252.0)
    sharpe = float(ann / vol) if vol > 0 else 0.0
    eq = np.cumprod(1.0 + series)
    peak = np.maximum.accumulate(eq)
    maxdd = float(np.min(eq / peak - 1.0))
    df = pd.Series(series, index=state["idx"][first_exec:])
    m = df.groupby(df.index.year * 100 + df.index.month).apply(lambda x: float((1 + x).prod() - 1))
    mwin = float((m > 0).mean()) if len(m) else None
    return {"ann": round(ann, 4), "vol": round(float(vol), 4),
            "sharpe": round(sharpe, 4), "maxdd": round(maxdd, 4),
            "monthly_win": None if mwin is None else round(mwin, 4),
            "n_days": int(len(series)), "capped_entries": int(capped)}


# ---------------------------------------------------------------- stat faces

def _ic_stats(state, S):
    """rank-IC full window + per-calendar-year means (ic_series anchor)."""
    from p1_factor_screen import ic_series
    Sf = pd.DataFrame(S, index=state["idx"], columns=state["syms"])
    s = ic_series(Sf, state["fwd5"])
    if len(s) < 30:
        return {"ic_mean": None, "ic_ir": None, "ic_pos_pct": None,
                "ic_n": int(len(s)), "ic_by_year": {}}
    mu, sd = float(s.mean()), float(s.std(ddof=1))
    yr = s.groupby(s.index.year).mean()
    return {"ic_mean": round(mu, 4), "ic_ir": round(mu / sd, 4) if sd > 0 else 0.0,
            "ic_pos_pct": round(float((s > 0).mean()), 4), "ic_n": int(len(s)),
            "ic_by_year": {int(y): round(float(v), 4) for y, v in yr.items()}}


def _dual_sort_pair(state, f1, f2):
    """3x3 tercile-tercile conditional forward-5d mean return matrix."""
    t1, t2 = state["terc"][f1], state["terc"][f2]
    fwd = np.asarray(state["fwd5"], dtype=float)
    ok = (t1 >= 0) & (t2 >= 0) & np.isfinite(fwd)
    out = [[None] * 3 for _ in range(3)]
    if not ok.any():
        return out
    cell = (t1[ok] * 3 + t2[ok]).ravel()
    w = fwd[ok].ravel()
    cnt = np.bincount(cell, minlength=9)
    ssum = np.bincount(cell, weights=w, minlength=9)
    for c in range(9):
        if cnt[c] > 0:
            out[c // 3][c % 3] = round(float(ssum[c] / cnt[c]), 5)
    return out


def _dual_sort_triple(state, S):
    """1x3 combo-score tercile conditional forward-5d mean returns."""
    Sf = pd.DataFrame(S, index=state["idx"], columns=state["syms"])
    lab = _tercile_labels(Sf)
    fwd = np.asarray(state["fwd5"], dtype=float)
    ok = (lab >= 0) & np.isfinite(fwd)
    out = [None, None, None]
    if not ok.any():
        return out
    cell = lab[ok].ravel()
    w = fwd[ok].ravel()
    cnt = np.bincount(cell, minlength=3)
    ssum = np.bincount(cell, weights=w, minlength=3)
    for c in range(3):
        if cnt[c] > 0:
            out[c] = round(float(ssum[c] / cnt[c]), 5)
    return out


def _score_matrix(state, faces, signs):
    """Combo score S (T x 48) = sum z(f_i) * s_i."""
    S = None
    for f, s in zip(faces, signs):
        Z = np.asarray(state["zed"][f], dtype=float) * float(s)
        S = Z if S is None else S + Z
    return S


# ---------------------------------------------------------------- combos

def enumerate_specs(state):
    """Canonical enumeration: 4060 candidates + 58 controls + 400 nulls."""
    from itertools import combinations
    faces = state["faces"]
    specs = []
    for f1, f2 in combinations(faces, 2):
        specs.append({"kind": "pair", "id": f"P:{f1}|{f2}", "faces": [f1, f2],
                      "signs": [state["sign"][f1], state["sign"][f2]]})
    for f1, f2, f3 in combinations(faces, 3):
        specs.append({"kind": "triple", "id": f"T:{f1}|{f2}|{f3}",
                      "faces": [f1, f2, f3],
                      "signs": [state["sign"][f1], state["sign"][f2], state["sign"][f3]]})
    for f in faces:
        for b in BENCH_FACES:
            specs.append({"kind": "control", "id": f"C:{f}|{b}",
                          "faces": [f, b], "signs": [state["sign"][f], RS_SIGN]})
    for k in range(N_NULLS):
        rng = np.random.default_rng(SEED_BASE + k)
        n = 2 if k < 200 else 3
        sel = rng.choice(len(faces), size=n, replace=False)
        sgn = rng.choice([-1.0, 1.0], size=n)
        specs.append({"kind": "null", "id": f"N{k}",
                      "faces": [faces[i] for i in sel],
                      "signs": [float(x) for x in sgn]})
    return specs


def eval_spec(state, spec, ew48_x1, ew48_x2):
    """One combo -> full stat row (native types only, r286 law)."""
    S = _score_matrix(state, spec["faces"], spec["signs"])
    b1 = blend_top16(state, lambda g: S[g], x2=False)
    b2 = blend_top16(state, lambda g: S[g], x2=True)
    ic = _ic_stats(state, S)
    mat = _dual_sort_triple(state, S) if spec["kind"] == "triple" \
        else _dual_sort_pair(state, spec["faces"][0], spec["faces"][1])
    row = {
        "id": spec["id"], "kind": spec["kind"], "faces": "|".join(spec["faces"]),
        "signs": "".join("+" if s > 0 else "-" for s in spec["signs"]),
        "ic_mean": ic["ic_mean"], "ic_ir": ic["ic_ir"],
        "ic_pos_pct": ic["ic_pos_pct"], "ic_n": ic["ic_n"],
        "x1_ann": b1["ann"], "x1_vol": b1["vol"], "x1_sharpe": b1["sharpe"],
        "x1_maxdd": b1["maxdd"], "x1_monthly_win": b1["monthly_win"],
        "x1_capped": b1["capped_entries"],
        "x2_ann": b2["ann"], "x2_vol": b2["vol"], "x2_sharpe": b2["sharpe"],
        "x2_maxdd": b2["maxdd"], "x2_monthly_win": b2["monthly_win"],
        "x2_capped": b2["capped_entries"],
        "delta_x1_ann_vs_ew48": None if b1["ann"] is None or ew48_x1["ann"] is None
            else round(b1["ann"] - ew48_x1["ann"], 4),
        "delta_x2_sharpe_vs_ew48": None if b2["sharpe"] is None or ew48_x2["sharpe"] is None
            else round(b2["sharpe"] - ew48_x2["sharpe"], 4),
        "matrix": mat,
    }
    for y, v in ic["ic_by_year"].items():
        row[f"ic_y{y}"] = v
    return row


# ---------------------------------------------------------------- worker glue

_G = {}


def _init_worker(state, ew48_x1, ew48_x2):
    _G["state"] = state
    _G["ew48_x1"] = ew48_x1
    _G["ew48_x2"] = ew48_x2


def block_worker(start, end):
    """Top-level picklable: evaluate specs[start:end], return {i: row}."""
    state = _G["state"]
    specs = state["specs"]
    return {i: eval_spec(state, specs[i], _G["ew48_x1"], _G["ew48_x2"])
            for i in range(start, end)}


def _jsonable(o):
    if isinstance(o, dict):
        return {str(k): _jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_jsonable(v) for v in o]
    if isinstance(o, bool) or isinstance(o, int) or isinstance(o, str) or o is None:
        return o
    if isinstance(o, float):
        return o if np.isfinite(o) else None
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        v = float(o)
        return v if np.isfinite(v) else None
    if isinstance(o, np.bool_):
        return bool(o)
    return str(o)


# ---------------------------------------------------------------- run

def _load_bench():
    bp = os.path.join(PATHS.basic_dir, "csi300.csv")
    return pd.read_csv(bp, parse_dates=["date"]).set_index("date")["close"]


def _load_checkpoint():
    done = set()
    if os.path.exists(CKPT):
        with open(CKPT, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        done.add(json.loads(line)["i"])
                    except (ValueError, KeyError):
                        continue
    return done


def _append_ckpt(rows):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(CKPT, "a", encoding="utf-8") as fh:
        for i, row in rows.items():
            fh.write(json.dumps({"i": int(i), "row": _jsonable(row)},
                                ensure_ascii=False, separators=(",", ":")) + "\n")


def _ew48(state):
    return (blend_top16(state, None, x2=False, fixed_all=True),
            blend_top16(state, None, x2=True, fixed_all=True))


def run(probe=False, workers=None):
    t0 = time.time()
    from parallel_runner import run_cells_parallel

    univ = load_universe()
    ok, rep = data_gate(univ)
    print("[gate]", json.dumps(_jsonable(rep), ensure_ascii=False))
    if not ok:
        print("DATA GATE FAIL (fail-closed, exit 2)")
        return 2

    bench = _load_bench()
    bench_end = str(bench.index.max().date())
    state = build_state(univ, bench)
    if not state["grid_sig"]:
        print("GRID INFEASIBLE (no date with all-29-faces >=16 valid) -> exit 2")
        return 2
    state["specs"] = enumerate_specs(state)
    n_total = len(state["specs"])
    n = min(n_total, 4) if probe else n_total

    ew48_x1, ew48_x2 = _ew48(state)
    print(f"[ew48] x1 sharpe={ew48_x1['sharpe']} ann={ew48_x1['ann']} | "
          f"x2 sharpe={ew48_x2['sharpe']} ann={ew48_x2['ann']}")

    done = set() if probe else _load_checkpoint()
    jobs = []
    for s in range(0, n, BLOCK):
        e = min(s + BLOCK, n)
        if all(i in done for i in range(s, e)):
            continue
        jobs.append((f"blk{s // BLOCK:02d}", block_worker, (s, e)))
    print(f"[plan] specs={n} blocks_todo={len(jobs)} ckpt_done={len(done)}")

    results = {}
    if jobs:
        res = run_cells_parallel(jobs, workers=workers, desc="census",
                                 initializer=_init_worker,
                                 initargs=(state, ew48_x1, ew48_x2))
        w = res.pop("__workers__", 1)      # r259 law: skip the int audit key
        for _blk, rows in res.items():
            results.update(rows)
            if not probe:
                _append_ckpt(rows)
    else:
        w = 0
        with open(CKPT, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    d = json.loads(line)
                    results[d["i"]] = d["row"]

    if probe:
        payload = _jsonable({
            "batch": BATCH, "mode": "probe", "gate": rep, "bench_end": bench_end,
            "n_days": state["n_days"], "cutoff_real": state["cutoff_real"],
            "grid_first_signal": str(state["idx"][state["grid_sig"][0]].date()),
            "n_grid_signals": len(state["grid_sig"]),
            "n_grid_execs": len(state["grid_exec"]),
            "ew48_x1": ew48_x1, "ew48_x2": ew48_x2,
            "rows": list(results.values()),
        })
        s = json.dumps(payload, ensure_ascii=False)
        json.loads(s)                       # round-trip assertion (r286 law)
        os.makedirs(OUT_DIR, exist_ok=True)
        with open(os.path.join(OUT_DIR, "probe.json"), "w", encoding="utf-8") as fh:
            fh.write(s)
        print(f"[probe] OK rows={len(results)} grid={len(state['grid_exec'])} "
              f"first_sig={payload['grid_first_signal']}")
        return 0

    # ---- finalize ----
    missing = [i for i in range(n_total) if i not in results]
    if missing:
        print(f"INCOMPLETE: {len(missing)} specs missing -> exit 2 (checkpoint retained)")
        return 2
    cand = [results[i] for i in range(n_total) if results[i]["kind"] != "null"]
    nulls = [results[i] for i in range(n_total) if results[i]["kind"] == "null"]

    import csv as _csv
    cols = ["id", "kind", "faces", "signs", "ic_mean", "ic_ir", "ic_pos_pct", "ic_n",
            "x1_ann", "x1_vol", "x1_sharpe", "x1_maxdd", "x1_monthly_win", "x1_capped",
            "x2_ann", "x2_vol", "x2_sharpe", "x2_maxdd", "x2_monthly_win", "x2_capped",
            "delta_x1_ann_vs_ew48", "delta_x2_sharpe_vs_ew48"]
    ycols = sorted({c for r in cand + nulls for c in r if c.startswith("ic_y")})
    with open(os.path.join(OUT_DIR, "w1_cells.csv"), "w", encoding="utf-8", newline="") as fh:
        wr = _csv.DictWriter(fh, fieldnames=cols + ycols, extrasaction="ignore")
        wr.writeheader()
        for r in cand:
            wr.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in cols + ycols})
    with open(os.path.join(OUT_DIR, "w1_nulls.json"), "w", encoding="utf-8") as fh:
        json.dump(_jsonable({"batch": BATCH, "n": len(nulls), "seed_base": int(SEED_BASE),
                             "nulls": nulls}), fh, ensure_ascii=False, indent=1)

    ranked = sorted((r for r in cand if r["ic_mean"] is not None),
                    key=lambda r: -abs(r["ic_mean"]))[:50]
    with open(os.path.join(OUT_DIR, "w1_top_matrices.json"), "w", encoding="utf-8") as fh:
        json.dump(_jsonable({"batch": BATCH, "top_rule": "|ic_mean| top-50 (prereg sec.4)",
                             "n": len(ranked),
                             "items": [{"id": r["id"], "kind": r["kind"],
                                        "ic_mean": r["ic_mean"], "matrix": r["matrix"]}
                                       for r in ranked]}), fh, ensure_ascii=False, indent=1)

    from factor_registry import ENGINE_FACES
    fam_of = {f: v[0] for f, v in ENGINE_FACES.items()}
    fam_of["lowamp20"] = "low_vol"
    fam_stats = {}
    for fam in sorted(set(fam_of.values())):
        members = [r for r in cand if r["kind"] in ("pair", "triple")
                   and any(fam_of.get(f) == fam for f in r["faces"].split("|"))]
        xs = sorted(r["x2_sharpe"] for r in members if r["x2_sharpe"] is not None)
        fam_stats[fam] = {"n_combos": len(members),
                          "median_x2_sharpe": round(float(np.median(xs)), 4) if xs else None}
    cross_top10 = sorted((r for r in cand if r["kind"] in ("pair", "triple")
                          and r["x2_sharpe"] is not None),
                         key=lambda r: -r["x2_sharpe"])[:10]
    null_x2 = sorted(r["x2_sharpe"] for r in nulls if r["x2_sharpe"] is not None)
    cand_x2 = [r["x2_sharpe"] for r in cand if r["x2_sharpe"] is not None]
    summary = _jsonable({
        "batch": BATCH,
        "family_rule": ("prereg sec.4: per ENGINE_FACES family, median x2 blend Sharpe of "
                        "combos containing >=1 family face + coverage count; cross-family "
                        "top-10 by x2 Sharpe; EXPLORATION ONLY (zero registration effect)"),
        "families": fam_stats,
        "cross_family_top10": [{"id": r["id"], "faces": r["faces"], "signs": r["signs"],
                                 "x2_sharpe": r["x2_sharpe"], "x1_sharpe": r["x1_sharpe"],
                                 "ic_mean": r["ic_mean"]} for r in cross_top10],
        "ew48_benchmark": {"x1": ew48_x1, "x2": ew48_x2},
        "null_x2_sharpe": {"n": len(null_x2),
                           "median": round(float(np.median(null_x2)), 4) if null_x2 else None,
                           "p95": round(float(np.quantile(null_x2, 0.95)), 4) if null_x2 else None},
        "cand_x2_p95": round(float(np.quantile(cand_x2, 0.95)), 4) if cand_x2 else None,
    })
    with open(os.path.join(OUT_DIR, "w1_summary.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=1)

    ledger = append_ledger(BATCH, n_total, "census_fusion_s2/w1_results.json",
                           evidence_cutoff=CUTOFF,
                           note="exploration face: 4060 fusion combos + 58 rs controls + 400 nulls")
    payload = {
        **cutoff_meta(CUTOFF),
        "batch": BATCH, "ticket": TICKET, "prereg_ref": PREREG,
        "face": "EXPLORATION (zero judgment claims / zero paper eligibility)",
        "n_candidates": sum(1 for r in cand if r["kind"] in ("pair", "triple")),
        "n_controls": sum(1 for r in cand if r["kind"] == "control"),
        "n_nulls": len(nulls),
        "data_gate": _jsonable(rep),
        "bench_disclosure": {
            "bench_end": bench_end,
            "note": (f"csi300.csv ends {bench_end}; compute_all reindex+ffill convention "
                     f"(engine/factors.py source anchor) bridges to {CUTOFF}; "
                     "affects rs CONTROL faces only (2-bar stale tail, disclosed)")},
        "grid": {"anchor_first_signal": str(state["idx"][state["grid_sig"][0]].date()),
                 "n_signals": len(state["grid_sig"]), "n_execs": len(state["grid_exec"]),
                 "cadence": f"{REB} trading days", "top_k": TOP_K,
                 "panel_days": state["n_days"], "cutoff_real": state["cutoff_real"]},
        "products": ["w1_cells.csv", "w1_nulls.json", "w1_top_matrices.json",
                     "w1_summary.json"],
        "audit": {"workers": int(w), "purpose": "exploration census (no selection gate)",
                  "ledger_trials_added": int(n_total),
                  "elapsed_sec": round(time.time() - t0, 1),
                  "null_seed_band": f"{SEED_BASE}..{SEED_BASE + N_NULLS - 1}",
                  "checkpoint": "w1_checkpoint.jsonl (200-combo cadence)"},
        "trials_ledger": ledger,   # r252 law: canonical embed key
    }
    out = os.path.join(OUT_DIR, "w1_results.json")
    s = json.dumps(_jsonable(payload), ensure_ascii=False, indent=1)
    json.loads(s)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(s)
    print(f"[done] cells={len(cand)} nulls={len(nulls)} workers={w} "
          f"elapsed={payload['audit']['elapsed_sec']}s ledger={ledger['total']}")
    return 0


# ------------------------------------------------- s3 UNC face (sec.3 s3/9.1)

def _bs_sharpe_ci(series, rng):
    """Circular block bootstrap on the daily net series: B=200 draws,
    block=20 trading days (frozen sec.3 s3), Sharpe per draw ->
    (ci_lo p2.5, ci_hi p97.5, bootstrap median)."""
    sv = np.asarray(series, dtype=float)
    n = len(sv)
    if n < UNC_BLOCK:
        return None, None, None
    n_blocks = int(np.ceil(n / UNC_BLOCK))
    starts = rng.integers(0, n, size=(UNC_B, n_blocks))
    idx = (starts[:, :, None] + np.arange(UNC_BLOCK)[None, None, :]) % n
    samples = sv[idx.reshape(UNC_B, -1)][:, :n]
    mus = samples.mean(axis=1)
    sds = samples.std(axis=1, ddof=1)
    sh = np.where(sds > 0, mus * 252.0 / (sds * np.sqrt(252.0)), 0.0)
    lo, hi = np.percentile(sh, [2.5, 97.5])
    return round(float(lo), 4), round(float(hi), 4), round(float(np.median(sh)), 4)


def _perm_ic_p(s_values, rng):
    """Sign-flip permutation P=200 on the daily rank-IC series, two-sided:
    p = (1 + #{|mu_perm| >= |mu_obs|}) / (P + 1)."""
    sv = np.asarray(s_values, dtype=float)
    mu = float(sv.mean())
    signs = rng.choice([-1.0, 1.0], size=(UNC_P, len(sv)))
    mu_p = (signs * sv[None, :]).mean(axis=1)
    return round(float((1 + int((np.abs(mu_p) >= abs(mu)).sum()))
                       / (UNC_P + 1)), 4)


def unc_eval(state, i, spec):
    """One candidate combo -> UNC row (frozen sec.3 s3 rules).

    rng = default_rng([seed_base, combo_ordinal]) per sec.9.1; draw order
    fixed: 1) bootstrap block starts, 2) permutation signs (sec.9.1)."""
    S = _score_matrix(state, spec["faces"], spec["signs"])
    met, series, _fe = blend_top16(state, lambda g: S[g], x2=True,
                                  return_series=True)
    rng = np.random.default_rng([int(UNC_SEED), int(i)])
    ci_lo, ci_hi, bs_med = _bs_sharpe_ci(series, rng)
    from p1_factor_screen import ic_series
    Sf = pd.DataFrame(S, index=state["idx"], columns=state["syms"])
    s = ic_series(Sf, state["fwd5"])
    if len(s) >= 30:
        ic_mean = round(float(s.mean()), 4)
        ic_p = _perm_ic_p(s.values, rng)
    else:
        ic_mean = None
        ic_p = None
    return {
        "i": int(i), "id": spec["id"], "kind": spec["kind"],
        "faces": "|".join(spec["faces"]),
        "x2_sharpe": met["sharpe"],
        "bs_sharpe_median": bs_med,
        "bs_ci_lo": ci_lo, "bs_ci_hi": ci_hi,
        "bs_ci_pos": None if ci_lo is None else bool(ci_lo > 0.0),
        "ic_mean": ic_mean, "ic_p_perm": ic_p,
    }


def unc_block_worker(start, end):
    """Top-level picklable: UNC rows for candidate ordinals [start:end)."""
    state = _G["state"]
    return {i: unc_eval(state, i, spec)
            for i, spec in state["cand_specs"][start:end]}


def _load_unc_checkpoint():
    done = set()
    if os.path.exists(UNC_CKPT):
        with open(UNC_CKPT, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        done.add(json.loads(line)["i"])
                    except (ValueError, KeyError):
                        continue
    return done


def _append_unc_ckpt(rows):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(UNC_CKPT, "a", encoding="utf-8") as fh:
        for i, row in rows.items():
            fh.write(json.dumps({"i": int(i), "row": _jsonable(row)},
                                ensure_ascii=False, separators=(",", ":")) + "\n")


def run_unc(probe=False, workers=None):
    """s3 UNC face: per-candidate block-bootstrap Sharpe CI + sign-flip IC
    permutation p. Derivation face -- ledger +0 (frozen sec.3 s3)."""
    t0 = time.time()
    from parallel_runner import run_cells_parallel

    univ = load_universe()
    ok, rep = data_gate(univ)
    print("[gate]", json.dumps(_jsonable(rep), ensure_ascii=False))
    if not ok:
        print("DATA GATE FAIL (fail-closed, exit 2)")
        return 2

    bench = _load_bench()
    state = build_state(univ, bench)
    if not state["grid_sig"]:
        print("GRID INFEASIBLE -> exit 2")
        return 2
    state["specs"] = enumerate_specs(state)
    # candidates in enumerate order (pairs then triples) -> ordinals 0..4059
    state["cand_specs"] = [(n, s) for n, s in enumerate(
        [x for x in state["specs"] if x["kind"] in ("pair", "triple")])]
    n_total = len(state["cand_specs"])
    n = min(n_total, 4) if probe else n_total
    assert n_total == 4060, n_total

    done = set() if probe else _load_unc_checkpoint()
    jobs = []
    for s in range(0, n, BLOCK):
        e = min(s + BLOCK, n)
        if all(i in done for i in range(s, e)):
            continue
        jobs.append((f"ublk{s // BLOCK:02d}", unc_block_worker, (s, e)))
    print(f"[plan] cand={n} blocks_todo={len(jobs)} ckpt_done={len(done)}")

    results = {}
    if jobs:
        flushed = set()

        def _flush(blk, rows):
            # r340 pitlaw fix mirrored (MSG-2010 item 5): incremental UNC
            # checkpoint -- _append_unc_ckpt fires per COMPLETED block via
            # on_result, so a mid-run kill retains finished blocks instead
            # of re-burning the whole UNC face (collect-only-tail miss).
            flushed.add(blk)
            results.update(rows)
            if not probe:
                _append_unc_ckpt(rows)

        res = run_cells_parallel(jobs, workers=workers, desc="census-unc",
                                 initializer=_init_worker,
                                 initargs=(state, None, None),
                                 on_result=_flush)
        w = res.pop("__workers__", 1)
        for _blk, rows in res.items():
            if _blk not in flushed:  # safety net if on_result path skipped
                results.update(rows)
                if not probe:
                    _append_unc_ckpt(rows)
    else:
        w = 0
        with open(UNC_CKPT, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    d = json.loads(line)
                    results[d["i"]] = d["row"]

    if probe:
        payload = _jsonable({"batch": UNC_BATCH, "mode": "probe",
                             "gate": rep, "n_combos": n_total,
                             "rows": list(results.values())})
        s = json.dumps(payload, ensure_ascii=False)
        json.loads(s)
        os.makedirs(OUT_DIR, exist_ok=True)
        with open(os.path.join(OUT_DIR, "unc_probe.json"), "w",
                  encoding="utf-8") as fh:
            fh.write(s)
        print(f"[unc-probe] OK rows={len(results)}")
        return 0

    # ---- finalize ----
    missing = [i for i in range(n_total) if i not in results]
    if missing:
        print(f"INCOMPLETE: {len(missing)} cand missing -> exit 2 "
              f"(checkpoint retained)")
        return 2
    rows = [results[i] for i in range(n_total)]

    # cross-anchor vs w1_cells.csv (same code path -> x2_sharpe must match)
    w1_csv = os.path.join(OUT_DIR, "w1_cells.csv")
    mism = 0
    checked = 0
    if os.path.exists(w1_csv):
        import csv as _csv
        w1 = {}
        with open(w1_csv, encoding="utf-8") as fh:
            for r in _csv.DictReader(fh):
                if r["kind"] in ("pair", "triple"):
                    w1[r["id"]] = r["x2_sharpe"]
        for row in rows:
            ref = w1.get(row["id"])
            if ref is None or ref == "" or row["x2_sharpe"] is None:
                continue
            checked += 1
            if abs(float(ref) - float(row["x2_sharpe"])) > 1e-9:
                mism += 1
        if mism:
            print(f"CROSS-ANCHOR MISMATCH vs w1_cells.csv: {mism}/{checked} "
                  f"-> exit 2 (no products written)")
            return 2
    print(f"[cross-anchor] checked={checked} mismatches={mism}")

    ci_pos = sum(1 for r in rows if r["bs_ci_pos"] is True)
    p_small = sum(1 for r in rows
                  if r["ic_p_perm"] is not None and r["ic_p_perm"] <= 0.05)
    both = sum(1 for r in rows if r["bs_ci_pos"] is True
               and r["ic_p_perm"] is not None and r["ic_p_perm"] <= 0.05)
    payload = _jsonable({
        **cutoff_meta(CUTOFF),
        "batch": UNC_BATCH, "ticket": UNC_TICKET, "prereg_ref": UNC_PREREG,
        "face": ("DERIVATION (same-combo same-cell, ledger +0; NAV "
                 "derivation-face precedent; uncertainty annotations only, "
                 "zero registration effect)"),
        "n_combos": n_total,
        "unc": {"B": UNC_B, "block_days": UNC_BLOCK, "P": UNC_P,
                "seed_family": "census_fusion_s2_unc",
                "seed_base": int(UNC_SEED),
                "derive_rule": "np.random.default_rng([seed_base, combo_ordinal])",
                "rng_order": "1) bootstrap block starts 2) permutation signs (sec.9.1)"},
        "data_gate": _jsonable(rep),
        "uncert_summary": {"n_ci_pos": ci_pos, "n_ic_p_le_0.05": p_small,
                           "n_ci_pos_and_p": both,
                           "note": "exploratory uncertainty annotations for the "
                                   "T-23 intake funnel; not gates"},
        "cross_anchor": {"vs": "w1_cells.csv", "checked": checked,
                         "mismatches": mism},
        "products": ["w1_unc.json", "unc_checkpoint.jsonl"],
        "audit": {"workers": int(w),
                  "purpose": "uncertainty face derivation (no selection gate)",
                  "ledger_trials_added": 0,
                  "elapsed_sec": round(time.time() - t0, 1),
                  "checkpoint": "unc_checkpoint.jsonl (200-combo cadence)"},
        "trials_ledger": {"batch": UNC_BATCH, "added": 0,
                          "note": "derivation face ledger +0 per prereg sec.3 "
                                  "s3 (same combos as CENSUS_FUS_S2_W1, no new "
                                  "trials)"},
        "rows": rows,
    })
    out = os.path.join(OUT_DIR, "w1_unc.json")
    s = json.dumps(payload, ensure_ascii=False, indent=1)
    json.loads(s)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(s)
    print(f"[done] unc rows={len(rows)} ci_pos={ci_pos} p<=.05={p_small} "
          f"both={both} workers={w} "
          f"elapsed={payload['audit']['elapsed_sec']}s")
    return 0


# ---------------------------------------------------------------- selftest

def _synth_universe(seed=7, n_sym=48, n_day=320):
    """Hermetic synthetic universe: 48 syms x 320 days (mom_12_1 needs 240)."""
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2020-01-01", periods=n_day)
    univ = {}
    for i in range(n_sym):
        drift = rng.normal(0.0002, 0.0006)
        close = 10.0 * np.cumprod(1 + rng.normal(drift, 0.015, n_day))
        univ[f"s{i:02d}"] = pd.DataFrame({
            "open": close * (1 + rng.normal(0, 0.004, n_day)),
            "high": close * (1 + np.abs(rng.normal(0, 0.008, n_day))),
            "low": close * (1 - np.abs(rng.normal(0, 0.008, n_day))),
            "close": close,
            "volume": rng.uniform(1e6, 5e6, n_day),
            "amount": rng.uniform(1e8, 5e8, n_day),
        }, index=dates)
    return univ


def _synth_state(seed=7, n_sym=48, n_day=320):
    univ = _synth_universe(seed, n_sym, n_day)
    prices = {s: df.copy() for s, df in univ.items()}
    bench = pd.Series(pd.DataFrame({s: p["close"] for s, p in prices.items()}).iloc[:, 0])
    factors = compute_all(prices, bench)
    panel = {f: pd.DataFrame({s: p[f] for s, p in prices.items()}).sort_index().ffill()
             for f in ["open", "high", "low", "close", "volume", "amount"]}
    factors["lowamp20"] = ((panel["high"] - panel["low"]) / panel["close"]).rolling(20).mean()
    close = panel["close"]
    idx, syms = close.index, list(close.columns)
    zed, terc = {}, {}
    for f in _faces_sorted() + BENCH_FACES:
        Z = _zscore(factors[f].reindex(index=idx, columns=syms))
        zed[f] = Z
        terc[f] = _tercile_labels(Z)
    valid_min = None
    for f in _faces_sorted():
        cnt = zed[f].notna().sum(axis=1)
        valid_min = cnt if valid_min is None else np.minimum(valid_min, cnt)
    feasible = np.asarray(valid_min) >= TOP_K
    anchor = int(np.argmax(feasible)) if feasible.any() else -1
    grid_sig = list(range(anchor, n_day - 1, REB)) if anchor >= 0 else []
    return {"idx": idx, "syms": syms, "faces": _faces_sorted(), "sign": _sign_priors(),
            "zed": zed, "terc": terc, "rets": close.pct_change(),
            "fwd5": close.shift(-HORIZON) / close - 1,
            "adv20": panel["amount"].rolling(20).mean(), "close": close,
            "grid_sig": grid_sig, "grid_exec": [g + 1 for g in grid_sig],
            "years": np.array([d.year for d in idx]),
            "cutoff_real": str(idx[-1].date()), "n_days": n_day}


def _drift_state(n_sym=48, n_day=320):
    """Noise-free distinct-drift blend state (selftest [3] only): higher
    member index = higher deterministic drift; ADV fixed in the 2bp tier
    with a non-binding 1% cap."""
    dates = pd.bdate_range("2020-01-01", periods=n_day)
    syms = [f"s{i:02d}" for i in range(n_sym)]
    close = pd.DataFrame({s: 10.0 * (1 + 0.0002 + 0.00002 * i) ** np.arange(n_day)
                          for i, s in enumerate(syms)}, index=dates)
    adv = pd.DataFrame({s: np.full(n_day, 1e8) for s in syms}, index=dates)
    grid_sig = list(range(260, n_day - 1, REB))
    return {"idx": dates, "syms": syms, "rets": close.pct_change(),
            "fwd5": close.shift(-5) / close - 1, "adv20": adv, "close": close,
            "grid_sig": grid_sig, "grid_exec": [g + 1 for g in grid_sig],
            "years": np.array([d.year for d in dates]), "n_days": n_day}


def selftest():
    """Hermetic selftest (no network, no real panel). r263 pre-pooling law."""
    ok = True

    def t(name, cond):
        nonlocal ok
        print(("PASS" if cond else "FAIL"), name)
        ok = ok and bool(cond)

    # [1] synthetic state: 48 syms x 320 days, 29 faces, grid feasible
    st = _synth_state()
    t("[1] synth state 48x320, 29 faces, grid non-empty",
      len(st["syms"]) == 48 and st["n_days"] == 320 and len(st["faces"]) == 29
      and len(st["grid_sig"]) > 0)

    # [2] IC == 1.0 on a noise-free distinct-drift mini panel (P-1 S6 anchor):
    #     cross-sectionally monotonic factor (price level ranks == drift ranks)
    from p1_factor_screen import ic_series
    dts = pd.bdate_range("2021-01-04", periods=60)
    px = pd.DataFrame({f"s{i}": 100.0 * (1 + 0.001 * (i + 1)) ** np.arange(1, 61)
                       for i in range(6)}, index=dts)
    ic = ic_series(px, px.shift(-5) / px - 1)
    t("[2] cross-sectionally monotonic factor IC==1",
      len(ic) == 55 and abs(np.mean(ic.values) - 1.0) < 1e-9)

    # [3] blend on a noise-free distinct-drift state: perfect score (true drift
    #     rank) top-16 must beat EW48 on ann; x2 costs bite EW48
    st_dr = _drift_state()
    score = np.arange(len(st_dr["syms"]), dtype=float)   # higher index = higher drift
    b_perf = blend_top16(st_dr, lambda g: score, x2=False)
    ew1, ew2 = _ew48(st_dr)
    t("[3a] perfect-signal blend ann > EW48 ann",
      (b_perf["ann"] or -9) > (ew1["ann"] or -9) + 1e-9)
    t("[3b] EW48 x2 ann <= x1 ann (doubled costs bite)",
      (ew2["ann"] or 0) <= (ew1["ann"] or 0) + 1e-9)

    # [4] 1% ADV entry cap binds on a tiny-ADV panel
    st_cap = _synth_state(seed=11)
    st_cap["adv20"] = st_cap["adv20"] * 1e-4
    ewc = blend_top16(st_cap, None, x2=False, fixed_all=True)
    t("[4] ADV cap binds (capped_entries > 0)", ewc["capped_entries"] > 0)

    # [5] dual-sort shapes 3x3 / 1x3
    m = _dual_sort_pair(st, "mom_20", "vol_20")
    m3 = _dual_sort_triple(st, _score_matrix(st, ["mom_20", "vol_20"], [1.0, -1.0]))
    t("[5] dual-sort shapes 3x3 / 1x3",
      len(m) == 3 and all(len(r) == 3 for r in m) and len(m3) == 3)

    # [6] ledger block + cutoff_meta top-level (C2 face, r252 embed key law)
    led = append_ledger(BATCH, 4518, "census_fusion_s2/w1_results.json",
                        evidence_cutoff=CUTOFF)
    t("[6] ledger dict + cutoff_meta keys",
      {"prev_total", "batch_trials", "total", "batch"} <= set(led)
      and led["total"] == led["prev_total"] + 4518
      and cutoff_meta(CUTOFF) == {"evidence_cutoff": CUTOFF})

    # [7] non-native type injection (r286 law)
    dirty = {"a": np.int64(5), "b": np.float32(1.5), "c": np.bool_(True),
             "d": np.float64(np.nan), "e": np.int8(2), "f": np.uint16(7)}
    clean = _jsonable(dirty)
    json.dumps(clean)
    t("[7] np-native coercion + NaN->None",
      isinstance(clean["a"], int) and isinstance(clean["b"], float)
      and isinstance(clean["c"], bool) and clean["d"] is None and clean["e"] == 2)

    # [8] data gate fail-closed: 47 members -> fail; stale end date -> fail
    u = _synth_universe()
    ok47, _r1 = data_gate({k: v for k, v in list(u.items())[:47]})
    u_stale = _synth_universe()
    k0 = sorted(u_stale)[0]
    u_stale[k0] = u_stale[k0].iloc[:-1]
    ok_end, _r2 = data_gate(u_stale)
    t("[8] gate fails on 47 members and on stale end date", (not ok47) and (not ok_end))

    # [9] spec census: 4060 + 58 + 400 = 4518; null seed determinism
    specs = enumerate_specs(st)
    t("[9] spec census 4060/58/400 = 4518",
      len(specs) == 4518
      and sum(1 for s in specs if s["kind"] == "pair") == 406
      and sum(1 for s in specs if s["kind"] == "triple") == 3654
      and sum(1 for s in specs if s["kind"] == "control") == 58
      and sum(1 for s in specs if s["kind"] == "null") == 400)
    a = np.random.default_rng(SEED_BASE + 0).choice(29, size=2, replace=False)
    b = np.random.default_rng(SEED_BASE + 0).choice(29, size=2, replace=False)
    t("[9b] null seed determinism (same base -> same draw)", list(a) == list(b))

    # [10] per-year IC table on synthetic
    icst = _ic_stats(st, _score_matrix(st, ["mom_20"], [1.0]))
    t("[10] per-year IC table non-empty", len(icst["ic_by_year"]) >= 1)

    # [11] real worker glue on synthetic (r286 glue law): control+null slice
    st["specs"] = specs
    _init_worker(st, ew1, ew2)
    rows = block_worker(4060, 4064)
    json.loads(json.dumps({"rows": _jsonable(rows)}, ensure_ascii=False))
    t("[11] worker glue on control/null slice, json round-trip",
      len(rows) == 4 and all(r["kind"] in ("control", "null") for r in rows.values())
      and all(r["x2_sharpe"] is not None or r["x2_sharpe"] is None for r in rows.values()))

    # [12] grid: exec = signal+1, all execs < n_days
    t("[12] grid exec = signal+1, all < n_days",
      all(e == g + 1 for g, e in zip(st["grid_sig"], st["grid_exec"]))
      and all(e < st["n_days"] for e in st["grid_exec"]))

    # [13] UNC determinism: same seed-sequence stream -> byte-identical row
    spec0 = {"kind": "pair", "id": "P:x|y",
             "faces": ["mom_20", "vol_20"], "signs": [1.0, -1.0]}
    r1 = unc_eval(st, 0, spec0)
    r2 = unc_eval(st, 0, spec0)
    t("[13] unc_eval determinism (same ordinal -> identical row)", r1 == r2
      and r1["i"] == 0 and json.dumps(r1) == json.dumps(r2))
    r3 = unc_eval(st, 1, spec0)
    t("[13b] unc_eval ordinal sensitivity (different ordinal -> different rng)",
      r3["bs_ci_lo"] != r1["bs_ci_lo"] or r3["ic_p_perm"] != r1["ic_p_perm"])

    # [14] bootstrap math on synthetic series: drift -> CI positive, contains
    #      observed-scale Sharpe; noise -> CI straddles zero
    dr = np.random.default_rng(41)
    up = 0.0012 + dr.normal(0.0, 0.002, 400)   # positive drift + real variance
    lo_c, hi_c, med_c = _bs_sharpe_ci(up, np.random.default_rng([int(UNC_SEED), 0]))
    t("[14a] drift series bootstrap CI positive & ordered",
      lo_c is not None and hi_c > lo_c and lo_c > 0.0)
    noise = dr.normal(0.0, 0.01, 400)
    lo_n, hi_n, _ = _bs_sharpe_ci(noise, np.random.default_rng([int(UNC_SEED), 1]))
    t("[14b] noise series bootstrap CI straddles zero",
      lo_n < 0.0 < hi_n)

    # [15] permutation math: strong IC -> tiny p; noise IC -> p not tiny
    ic_up = np.repeat(0.05, 120)
    p_up = _perm_ic_p(ic_up, np.random.default_rng([int(UNC_SEED), 2]))
    ic_nz = dr.normal(0.0, 0.05, 120)
    p_nz = _perm_ic_p(ic_nz, np.random.default_rng([int(UNC_SEED), 3]))
    t("[15] permutation p: strong IC tiny, noise IC not tiny",
      p_up <= 0.05 and p_nz > 0.05)

    # [16] unc row native types only (r286 law) + json round-trip
    clean = _jsonable(r1)
    json.loads(json.dumps(clean, ensure_ascii=False))
    t("[16] unc row native types + round-trip",
      isinstance(clean["x2_sharpe"], (float, int, type(None)))
      and isinstance(clean["bs_ci_pos"], (bool, type(None)))
      and isinstance(clean["i"], int))

    # [17] return_series=True metrics == default-path metrics (same compute)
    S = _score_matrix(st, ["mom_20", "vol_20"], [1.0, -1.0])
    m_def = blend_top16(st, lambda g: S[g], x2=True)
    m_ser, _ser, _fe = blend_top16(st, lambda g: S[g], x2=True,
                                   return_series=True)
    t("[17] return_series metrics == default metrics", m_def == m_ser
      and len(_ser) == m_ser["n_days"])

    # [18] unc worker glue on synthetic: candidate slice rows well-formed
    st2 = _synth_state(seed=13)
    st2["specs"] = enumerate_specs(st2)
    st2["cand_specs"] = [(n, s) for n, s in enumerate(
        [x for x in st2["specs"] if x["kind"] in ("pair", "triple")])]
    _init_worker(st2, None, None)
    urows = unc_block_worker(0, 3)
    t("[18] unc worker glue slice (3 rows, ordinal keys 0..2)",
      sorted(urows) == [0, 1, 2]
      and all("bs_ci_lo" in r and "ic_p_perm" in r for r in urows.values()))

    print("selftest:", "ALL PASS" if ok else "FAIL")
    return 0 if ok else 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "unc", "probe", "selftest"])
    ap.add_argument("--workers", type=int, default=None)
    a = ap.parse_args()
    if a.cmd == "selftest":
        return selftest()
    if a.cmd == "probe":
        return run(probe=True, workers=a.workers or 4)
    if a.cmd == "unc":
        return run_unc(workers=a.workers or 4)
    return run(workers=a.workers or 4)


if __name__ == "__main__":
    sys.exit(main())
