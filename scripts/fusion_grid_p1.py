"""FUSION_GRID_P1 runner (T-85 s2/s3) -- 5 weight families x 9 subsets judged grid.

R99 chain: prereg research/FUSION_GRID_P1_PREREG.md FROZEN 7cf87f13 (R295)
-> runner build + selftest + real-data gate (R296) -> pool burn -> harvest three-piece.
Law chain: BACKTEST_SCIENCE v2 + BACKTEST_PLAN three iron rules + COMPUTE_AUDIT batch law.

Subcommands:
  probe    -- data completeness gate (prereg sec.2) + fast face readouts; ZERO judged
              cell values computed (freeze-first law honored: prereg already frozen).
  selftest -- hermetic offline self-check: (a) v3 regime day-by-day equivalence
              sampling gate vs market_regime module originals (>=20 random dates +
              last NAV day vs bench_dims/breadth_dims truncated + last bench day vs
              probe() dims), (b) synthetic-member constructive tests, (c) null
              determinism replay gate.
  run      -- full batch: regime series recompute + 45 judged cells (x1 face) +
              x2 stress descriptive face (same decision sequence on x2 NAVs) +
              K=2000 same-mask random-portfolio nulls (rng [20275200,k,j]) +
              G1'v2/G2 gates + family PBO (CSCV 8 blocks) + ledger single count.

Idempotency: p1_results.json present -> honest no-op exit 0 (FUSION_GRID_P1_REFINALIZE=1
is the only redo path; engineering-fix re-run must be disclosed in the round report).
"""
import argparse
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "scripts"))

import numpy as np
import pandas as pd

import science_gates as SG
from science_gates import SEED_REGISTRY, append_ledger, cutoff_meta
from parallel_runner import run_cells_parallel
from screening.pbo import cscv_pbo
import market_regime as MR
from firm.risk.regime import load_benchmark_close, major_bear_state, major_bear_series
from config import PATHS

BATCH = "FUSION_GRID_P1"
BATCH_CELLS = 45
K_NULLS = 2000
N_BILL = BATCH_CELLS + K_NULLS          # 2045, every cell billed to N_eff
SEED = 20275200                         # SEED_REGISTRY["fusion_grid_p1"] (R295 one-step)
EVIDENCE_CUTOFF = "2026-09-22"          # member caliber r256 A1 pin law
PBP = 252
LOOKBACK = 252
WARMUP = 252
REBAL = 21
OOS_BARS = 504
MAXDD_LINE = -0.35
CRASH_YEAR_LINE = -0.50
NAV = os.path.join(PATHS.results_dir, "fusion_p1", "navs.jsonl")
NAVS_SUMMARY = os.path.join(PATHS.results_dir, "fusion_p1", "navs_summary.json")
OUT_DIR = os.path.join(PATHS.results_dir, "fusion_grid_p1")
FAMILIES = ["EW", "INV_VOL", "INV_MDD", "CORR_CLUSTER_RP", "REGIME_COND"]
SUBSETS = ["ALL32", "DEDUP"] + [f"TOP{k}" for k in range(2, 9)]
CAP_LADDER = {"GREEN": 0.80, "YELLOW": 0.65, "ORANGE": 0.50, "RED": 0.20}
YELLOW_CAP_NOTE = ("YELLOW 0.65 = engineering-frozen interpolation, L5 canon has "
                   "RED20/ORANGE50/GREEN80 only -- disclosed non-canon param")
REDRAW_J = (0, 25, 50)                  # null redraws every 25 rebalance points
TICKET = "T-2026-09-26-85 s2/s3 (O-20260926-2320)"
PREREG_REF = "research/FUSION_GRID_P1_PREREG.md FROZEN 7cf87f13 (R295)"


# ---------------------------------------------------------------- data load (sec.2 gates)

def load_members():
    lines = [json.loads(l) for l in open(NAV, encoding="utf-8")]
    if len(lines) != 64:
        raise SystemExit(f"gate FAIL: navs.jsonl {len(lines)} lines != 64")
    x1 = [l for l in lines if l["cost_face"] == "x1"]
    x2 = [l for l in lines if l["cost_face"] == "x2"]
    if len(x1) != 32 or len(x2) != 32:
        raise SystemExit(f"gate FAIL: faces {len(x1)}/{len(x2)} != 32/32")
    summ = json.load(open(NAVS_SUMMARY, encoding="utf-8"))
    if summ.get("anchor_all_ok") is not True:
        raise SystemExit("gate FAIL: s1 anchor_all_ok != true")
    base = [l for l in x1 if ":" not in l["member"]]
    dates = base[0]["dates"]
    for l in base:
        if l["dates"] != dates:
            raise SystemExit(f"gate FAIL: base member date drift {l['member']}")
    x2_by_member = {}
    for coll, tag in ((x1, "x1"), (x2, "x2")):
        for l in coll:
            if l["dates"][:len(dates)] != dates or len(l["dates"]) < len(dates):
                raise SystemExit(f"gate FAIL: {tag} member {l['member']} not on common grid")
            l["dates"] = l["dates"][:len(dates)]
            l["eq"] = [float(v) for v in l["eq"][:len(dates)]]
            if tag == "x2":
                x2_by_member[l["member"]] = l["eq"]
    if dates[-1] != EVIDENCE_CUTOFF:
        raise SystemExit(f"gate FAIL: grid last {dates[-1]} != lockbox {EVIDENCE_CUTOFF}")
    members = [l["member"] for l in x1]
    if sorted(members) != sorted(x2_by_member):
        raise SystemExit("gate FAIL: x1/x2 member sets differ")
    T = len(dates)
    R1 = np.array([l["eq"] for l in x1], dtype=float)
    R2 = np.array([x2_by_member[m] for m in members], dtype=float)
    if not np.isfinite(R1).all() or not np.isfinite(R2).all():
        raise SystemExit("gate FAIL: non-finite NAV value in matrix")
    fams = {}
    for l in x1:
        key = l.get("family") or ("OVERLAY" if ":" in l["member"] else "?")
        fams[key] = fams.get(key, 0) + 1
    return {"members": members, "R1": R1, "R2": R2, "dates": dates, "T": T,
            "n_trades": {l["member"]: int(l["n_trades"]) for l in x1},
            "families": fams, "n_bars": T}


def bench_panel(nav_dates):
    """510300 bench + core48 breadth fast faces (module-exact semantics)."""
    bench = load_benchmark_close()
    idx = pd.to_datetime(pd.Index(nav_dates))
    if len(bench) < len(idx) or bench.index[-1] < idx[-1]:
        raise SystemExit(f"gate FAIL: bench last {bench.index[-1]} < cutoff {idx[-1]}")
    r1 = bench.pct_change()
    r10 = bench.pct_change(10)
    vol20 = r1.rolling(MR.VOL_WIN).std()
    # module bench_dims: vol base = last VOL_BASE vol20 values EXCLUDING current,
    # available iff truncated-series vol20.dropna() count > VOL_BASE+VOL_WIN.
    # vol20 non-nan from bench position 20 (r1[0] NaN) -> count = i-19 -> i >= 796.
    p95 = vol20.shift(1).rolling(MR.VOL_BASE, min_periods=MR.VOL_BASE).quantile(0.95)
    p80 = vol20.shift(1).rolling(MR.VOL_BASE, min_periods=MR.VOL_BASE).quantile(0.80)
    pos = pd.Series(np.arange(len(bench)), index=bench.index)
    vol_ok = pos >= (MR.VOL_BASE + MR.VOL_WIN + 20)
    # breadth: per bare-code close<MA20 share on last 6 bench dates (module-literal)
    below_by_d, valid_by_d = {}, {}
    for code in MR._bare_codes():
        p = os.path.join(PATHS.daily_dir, f"{code}.csv")
        s = pd.read_csv(p, parse_dates=["date"]).set_index("date")["close"]
        s = s.astype(float).sort_index()
        ma = s.rolling(MR.MA_BRE, min_periods=MR.MA_BRE).mean()
        bel = (s < ma).fillna(False)
        cnt = pd.Series(np.arange(1, len(s) + 1), index=s.index)
        bel_f = bel.reindex(bench.index).ffill().fillna(False).astype(bool)
        cnt_f = cnt.reindex(bench.index).ffill().fillna(0.0)
        valid_by_d[code] = (cnt_f >= MR.MA_BRE).fillna(False).astype(bool)
        below_by_d[code] = bel_f
    codes = sorted(below_by_d)
    B = pd.DataFrame({c: below_by_d[c] for c in codes})
    V = pd.DataFrame({c: valid_by_d[c] for c in codes})
    below_n = B.sum(axis=1)
    valid_n = V.sum(axis=1)
    share_raw = below_n / valid_n.where(valid_n > 0)      # unrounded face (slope input)
    arr = list(bench.index)
    slope_raw = {}
    for i in range(len(arr)):
        slope_raw[arr[i]] = (share_raw.iloc[i] - share_raw.iloc[i - 5]
                             if i >= 5 else None)
    # module breadth_dims needs >=6 bench dates: share/slope None before position 5
    share_out = share_raw.where(pos >= 5)
    slope_out = pd.Series({d: (slope_raw[d] if (pos.loc[d] >= 5) else None)
                           for d in arr})
    # core48 gate: every bare code >= 20 bars since 2020-01 (breadth denominator face)
    core48_ok = True
    for code in codes:
        p = os.path.join(PATHS.daily_dir, f"{code}.csv")
        dfc = pd.read_csv(p, usecols=["date"])
        dts = pd.to_datetime(dfc["date"])
        if int((dts >= pd.Timestamp("2020-01-01")).sum()) < MR.MA_BRE:
            core48_ok = False
    bear = major_bear_series(bench)
    return {"bench": bench, "idx": idx, "r1": r1, "r10": r10, "vol20": vol20,
            "p95": p95, "p80": p80, "vol_ok": vol_ok, "share": share_out,
            "share_raw": share_raw, "slope": slope_out, "bear": bear,
            "valid_n": valid_n, "core48_ok": core48_ok}


def fast_dims_at(bp, d):
    """Module-shape bd/br dicts at bench date d (zero decision logic here)."""
    crash = bp["r10"].loc[d]
    panic = bp["r1"].loc[d]
    bd = {"crash_10d": float(crash) if pd.notna(crash) else None,
          "panic_1d": float(panic) if pd.notna(panic) else None}
    if bool(bp["vol_ok"].loc[d]) and pd.notna(bp["vol20"].loc[d]):
        bd["vol_status"] = "ok"
        bd["vol20"] = round(float(bp["vol20"].loc[d]), 6)
        bd["vol_p95"] = round(float(bp["p95"].loc[d]), 6)
        bd["vol_p80"] = round(float(bp["p80"].loc[d]), 6)
    else:
        bd["vol_status"] = "insufficient_history"
        bd["vol20"] = None
        bd["vol_p95"] = None
        bd["vol_p80"] = None
    bd["event_fomc"] = str(pd.Timestamp(d).date()) in MR.FOMC_2026_BEIJING
    bd["event_pre_holiday"] = None
    sh, sl = bp["share"].loc[d], bp["slope"].loc[d]
    br = {"share_below_ma20": None if pd.isna(sh) else round(float(sh), 4),
          "share_slope_5d": None if (sl is None or pd.isna(sl)) else round(float(sl), 4),
          "status": "ok"}
    return bd, br


def regime_states(bp, nav_idx):
    """v3 state series over NAV dates: fast dims + module raw_level_v3/resolve_state_v3
    verbatim (zero decision-logic rewrite). Init = probe() first-row convention."""
    states, raws, prev, streak = [], [], None, 0
    trig_census = {}
    caps = []
    for d in nav_idx:
        bd, br = fast_dims_at(bp, d)
        bear = bool(bp["bear"].loc[d])
        raw, trig = MR.raw_level_v3(bd, br, bear)
        if prev is None:
            state, streak = raw, (1 if raw == MR.GREEN else 0)
        else:
            state, streak = MR.resolve_state_v3(prev, streak, raw)
        for t in trig:
            key = t.split(" ")[0]
            trig_census[key] = trig_census.get(key, 0) + 1
        states.append(state)
        raws.append(raw)
        caps.append(CAP_LADDER[state])
        prev = state
    return {"states": states, "raws": raws, "caps": caps, "trig_census": trig_census}


# ---------------------------------------------------------------- subsets + weights (sec.3)

def _union_find(n, pairs):
    parent = list(range(n))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for a, b in pairs:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    clusters = {}
    for i in range(n):
        clusters.setdefault(find(i), []).append(i)
    return list(clusters.values())


def trailing_at(R, t):
    """Trailing stats at rebalance bar t from data <= t-1 (causal)."""
    lo = max(1, t - LOOKBACK)
    W = R[:, lo:t] / R[:, lo - 1:t - 1] - 1.0
    mu = W.mean(axis=1)
    sd = W.std(axis=1, ddof=1)
    L = R[:, lo - 1:t]
    runmax = np.maximum.accumulate(L, axis=1)
    mdd = (L / runmax - 1.0).min(axis=1)          # negative convention
    with np.errstate(invalid="ignore", divide="ignore"):
        tsh = np.where(sd > 0, mu / sd * math.sqrt(PBP), np.nan)
    valid = np.where(sd > 0)[0]
    C = np.full((R.shape[0], R.shape[0]), np.nan)
    if len(valid) > 1:
        C[np.ix_(valid, valid)] = np.corrcoef(W[valid])
    return {"tsh": tsh, "sd": sd, "mdd": mdd, "C": C, "valid": valid,
            "n_rets": W.shape[1]}


def subsets_at(st, names):
    """ALL32 / DEDUP / TOP2..TOP8 at one rebalance point (std=0 members excluded)."""
    valid = list(st["valid"])
    order = sorted(valid, key=lambda i: (-st["tsh"][i], names[i]))
    pairs = [(a, b) for a in valid for b in valid if a < b
             and np.isfinite(st["C"][a, b]) and abs(st["C"][a, b]) >= 0.95]
    clusters = _union_find(len(valid), [(valid.index(a), valid.index(b))
                                        for a, b in pairs])
    pool = []
    for cl in clusters:
        idxs = [valid[j] for j in cl]
        pool.append(min(idxs, key=lambda i: (-st["tsh"][i], names[i])))
    pool.sort(key=lambda i: (-st["tsh"][i], names[i]))
    out = {"ALL32": list(valid), "DEDUP": pool}
    for k in range(2, 9):
        out[f"TOP{k}"] = pool[:min(k, len(pool))]
    return out


def weights_at(family, subset, st):
    """Weight vector over ALL members (zeros outside subset); sum=1 inside."""
    w = np.zeros(len(st["tsh"]))
    if not subset:
        return w
    idx = np.array(subset, dtype=int)
    if family == "EW":
        w[idx] = 1.0 / len(idx)
    elif family == "INV_VOL":
        v = st["sd"][idx]
        v = np.where(v > 0, v, np.inf)            # std=0 excluded by subset law anyway
        w[idx] = (1.0 / v) / np.sum(1.0 / v)
    elif family == "INV_MDD":
        m = np.maximum(-st["mdd"][idx], 0.05)     # 5% floor (engineering-frozen)
        w[idx] = (1.0 / m) / np.sum(1.0 / m)
    elif family == "CORR_CLUSTER_RP":
        pairs = [(a, b) for a in subset for b in subset
                 if a < b and np.isfinite(st["C"][a, b])
                 and abs(st["C"][a, b]) >= 0.70]
        clusters = _union_find(len(subset), [(subset.index(a), subset.index(b))
                                             for a, b in pairs])
        cross = 1.0 / len(clusters)
        for cl in clusters:
            members = [subset[j] for j in cl]
            midx = np.array(members, dtype=int)
            v = st["sd"][midx]
            inv = np.where(v > 0, 1.0 / v, 0.0)
            tot = inv.sum()
            if tot <= 0:
                inv = np.ones(len(midx))
                tot = float(len(midx))
            w[midx] = cross * inv / tot
    elif family == "REGIME_COND":
        w[idx] = 1.0 / len(idx)                   # EW; cap applied by caller
    else:
        raise ValueError(family)
    return w


def build_points(R1, names, caps):
    """Per-rebalance-point subsets + weight vectors + caps (x1 causal decisions)."""
    T = R1.shape[1]
    rb = list(range(WARMUP, T, REBAL))
    points = []
    for t in rb:
        st = trailing_at(R1, t)
        subs = subsets_at(st, names)
        pt = {"bar": t, "stats_nrets": st["n_rets"], "subsets": subs,
              "dedup_n": len(subs["DEDUP"]),
              "subset_sizes": {s: len(v) for s, v in subs.items()},
              "weights": {}, "caps": {}}
        for fam in FAMILIES:
            for sub in SUBSETS:
                pt["weights"][(fam, sub)] = weights_at(fam, subs[sub], st)
                pt["caps"][(fam, sub)] = (caps[t - 1] if fam == "REGIME_COND" else 1.0)
        points.append(pt)
    return points, rb


def cell_series(Rm, weights, caps, rb, T, warmup=WARMUP):
    """Drift-weight cell equity path (warmup cash bars 0..warmup-1 = 1.0)."""
    eq = np.ones(T)
    for k, t in enumerate(rb):
        end = rb[k + 1] if k + 1 < len(rb) else T
        w = weights[k]
        cap = caps[k]
        base = Rm[:, t - 1]
        path = cap * (w @ (Rm[:, t:end] / base[:, None]))
        if cap < 1.0:
            path = (1.0 - cap) + path              # cash leg zero return
        eq[t:end] = eq[t - 1] * path
    return eq


def cell_returns(Rm, weights, caps, rb, T, warmup=WARMUP):
    eq = cell_series(Rm, weights, caps, rb, T, warmup)
    r = eq[1:] / eq[:-1] - 1.0
    return r[warmup - 1:], eq      # returns at bars warmup..T-1 (1379 real face)


def hold_shares(weights, rb, T, n_members, warmup=WARMUP):
    """F6 frozen formula support: member active-bar share over the cell window."""
    bars = np.zeros(n_members)
    total = T - warmup
    for k, t in enumerate(rb):
        end = rb[k + 1] if k + 1 < len(rb) else T
        active = np.where(weights[k] > 0)[0]
        bars[active] += (end - t)
    return bars / total


# ---------------------------------------------------------------- stats (house conventions)

def _sharpe(r):
    r = np.asarray(r, float)
    r = r[np.isfinite(r)]
    if len(r) < 20 or float(r.std(ddof=1)) == 0:
        return None
    return round(float(r.mean() / r.std(ddof=1) * math.sqrt(PBP)), 4)


def _ann(r):
    r = np.asarray(r, float)
    r = r[np.isfinite(r)]
    if len(r) < 20:
        return None
    return round(float((1.0 + r).prod() ** (PBP / len(r)) - 1.0), 6)


def _max_dd(r):
    r = np.asarray(r, float)
    r = r[np.isfinite(r)]
    if len(r) < 2:
        return None
    eq = np.cumprod(1.0 + r)
    return round(float((eq / np.maximum.accumulate(eq) - 1.0).min()), 6)


def _rolling_sharpe(r, win):
    r = np.asarray(r, float)
    if len(r) < win:
        return {"min": None, "median": None}
    mu = np.convolve(r, np.ones(win) / win, mode="valid")
    sq = np.convolve(r * r, np.ones(win) / win, mode="valid")
    var = np.maximum(sq - mu * mu, 0.0) * win / (win - 1)
    with np.errstate(invalid="ignore", divide="ignore"):
        sh = np.where(var > 0, mu / np.sqrt(var) * math.sqrt(PBP), np.nan)
    sh = sh[np.isfinite(sh)]
    if len(sh) == 0:
        return {"min": None, "median": None}
    return {"min": round(float(sh.min()), 4), "median": round(float(np.median(sh)), 4)}


def yearly_returns(r, dates):
    """Per-calendar-year compounded return over the cell window."""
    df = pd.DataFrame({"r": r}, index=pd.to_datetime(pd.Index(dates)))
    out = {}
    for y, g in df.groupby(df.index.year):
        out[int(y)] = round(float((1.0 + g["r"].values).prod() - 1.0), 6)
    return out


def cell_descriptive(r, dates, bench_trail):
    """Prereg sec.4 descriptive faces: OOS dual-positive, maxDD, rolling, segments."""
    oos = r[-OOS_BARS:] if len(r) >= OOS_BARS else r
    seg = {}
    for name, mask in (("bull", bench_trail >= 0.10),
                       ("bear", bench_trail <= -0.10),
                       ("chop", (bench_trail > -0.10) & (bench_trail < 0.10))):
        rr = np.asarray(r)[mask]
        seg[name] = {"n_bars": int(mask.sum()), "sharpe": _sharpe(rr),
                     "ann_ret": _ann(rr), "max_dd": _max_dd(rr)}
    years = yearly_returns(r, dates)
    return {
        "n_days": int(len(r)),
        "sharpe_full": _sharpe(r),
        "ann_ret": _ann(r), "max_dd": _max_dd(r),
        "oos_sharpe": _sharpe(oos), "oos_ann_ret": _ann(oos),
        "oos_dual_positive": bool((_sharpe(oos) or 0) > 0 and (_ann(oos) or 0) > 0),
        "maxdd_line_pass": bool((_max_dd(r) or 0) >= MAXDD_LINE),
        "rolling_sharpe": {f"win{w}": _rolling_sharpe(r, w) for w in (126, 252, 504)},
        "segments": seg, "yearly_returns": years,
        "crash_year": bool(any(v <= CRASH_YEAR_LINE for v in years.values())),
        "crash_year_line": CRASH_YEAR_LINE,
    }


# ---------------------------------------------------------------- nulls (sec.3 K=2000)

def null_draw(rng, dedup_n, n_pool=32):
    """One null redraw: size law (p mirror) + members + Dirichlet weights."""
    u = float(rng.random())
    if u < 7.0 / 9.0:
        k = int(rng.integers(2, 9))               # uniform {2..8}
    elif u < 8.0 / 9.0:
        k = int(dedup_n)
    else:
        k = n_pool
    k = max(1, min(k, n_pool))
    mem = rng.choice(n_pool, size=k, replace=False)
    w = rng.dirichlet(np.ones(k))
    return mem, w


def null_rows(k_null, js, dedup_ns, n_pool=32):
    """Per-null weight vectors, one per redraw segment j (rng [SEED,k,j])."""
    rows = []
    for j in js:
        rng = np.random.default_rng([SEED, k_null, j])
        mem, w = null_draw(rng, dedup_ns.get(j, n_pool), n_pool)
        row = np.zeros(n_pool)
        row[mem] += w
        rows.append(row)
    return rows


def run_nulls(R1, rb, dedup_ns, T, n_members):
    """K=2000 same-mask random-portfolio nulls, vectorized per redraw segment.

    Redraw cadence: every 25 rebalance points (j in {0,25,50} clipped to grid);
    between redraws weights drift naturally (units held) -- same cell mechanics.
    Full Sharpe over the cell window (bars WARMUP..T-1).
    """
    js = [j for j in REDRAW_J if j < len(rb)] or [0]
    bounds = js + [len(rb)]
    segs = [(bounds[i], bounds[i + 1]) for i in range(len(bounds) - 1)]
    all_rets = np.zeros((K_NULLS, T - WARMUP))
    for si, (j0, j1) in enumerate(segs):
        Wm = np.zeros((K_NULLS, n_members))
        for k in range(K_NULLS):
            Wm[k] = null_rows(k, [j0], dedup_ns, n_members)[0]
        t = rb[j0]
        end = rb[j1] if j1 < len(rb) else T
        Rat = R1[:, t:end] / R1[:, t - 1][:, None]      # 32 x seglen
        P = Wm @ Rat                                     # K x seglen
        seg = np.empty_like(P)
        seg[:, 0] = P[:, 0] - 1.0
        seg[:, 1:] = P[:, 1:] / P[:, :-1] - 1.0
        width = seg.shape[1]
        col0 = (rb[j0] - WARMUP) if j0 > 0 else 0
        all_rets[:, col0:col0 + width] = seg
    assert (all_rets != 0).any(axis=1).all(), "null return grid misaligned"
    values = []
    for k in range(K_NULLS):
        s = _sharpe(all_rets[k])
        values.append(0.0 if s is None else float(s))
    mu = sum(values) / len(values)
    sigma = math.sqrt(sum((x - mu) ** 2 for x in values) / (len(values) - 1))
    coverage = {"n_values": len(values), "mu": mu, "sigma": sigma,
                "schemas_parsed": [f"{BATCH} own K=2000 random-portfolio nulls "
                                   "(rng [seed,k,j], redraw every 25 rebalance points)"],
                "known_unparsed": []}
    return {"values": values, "coverage": coverage, "workers": 1,
            "method": "in-process vectorized (matrix segments)",
            "segments": [[rb[bounds[i]], rb[bounds[i + 1]] if bounds[i + 1] < len(rb)
                          else T] for i in range(len(bounds) - 1)]}


# ---------------------------------------------------------------- cell jobs (parallel)

_CTX = None


def _cell_init(payload):
    global _CTX
    _CTX = payload


def _cell_job(fam, sub):
    ctx = _CTX
    R1, R2 = ctx["R1"], ctx["R2"]
    T, rb = ctx["T"], ctx["rb"]
    points = ctx["points"]
    names = ctx["names"]
    weights = [pt["weights"][(fam, sub)] for pt in points]
    caps = [pt["caps"][(fam, sub)] for pt in points]
    r1, eq1 = cell_returns(R1, weights, caps, rb, T)
    r2, _ = cell_returns(R2, weights, caps, rb, T)
    st = cell_descriptive(r1, ctx["cell_dates"], ctx["bench_trail"])
    hs = hold_shares(weights, rb, T, len(names))
    n_entries = round(float(sum(ctx["n_trades"][i] * hs[i] for i in range(len(names)))), 4)
    null_pool = {"values": ctx["null_values"], "coverage": ctx["null_coverage"]}
    rets_pd = pd.Series(r1, index=pd.to_datetime(pd.Index(ctx["cell_dates"])))
    g1 = SG.g1_prime_v2(st["sharpe_full"] or 0.0, rets_pd, batch_cells=BATCH_CELLS,
                        pool="core48", n_trades=n_entries, n_entries=n_entries,
                        null_pool=null_pool, n_eff_override=ctx["n_eff"])
    dsr = SG.deflated_sharpe_ratio(rets_pd, n_trials=ctx["n_eff"],
                                   var_null_sr=ctx["sigma_null"] ** 2)
    x2_st = {"sharpe_full": _sharpe(r2), "ann_ret": _ann(r2), "max_dd": _max_dd(r2)}
    years_x1 = st["yearly_returns"]
    years_x2 = yearly_returns(r2, ctx["cell_dates"])
    return {
        "family": fam, "subset": sub,
        "subset_sizes": [int(pt["subset_sizes"][sub]) for pt in points],
        "dedup_n_series": [int(pt["dedup_n"]) for pt in points],
        "caps_series": [float(c) for c in caps],
        "stats": st, "x2": {**x2_st,
                            "sharpe_degradation": round(
                                (x2_st["sharpe_full"] or 0) - (st["sharpe_full"] or 0), 4),
                            "yearly_returns": years_x2,
                            "yearly_degradation": {str(y): round(
                                (years_x2.get(y, 0) - years_x1.get(y, 0)), 6)
                                for y in sorted(set(years_x1) | set(years_x2))}},
        "n_entries_f6": n_entries, "hold_shares_nonzero": {
            names[i]: round(float(hs[i]), 6) for i in range(len(names)) if hs[i] > 0},
        "g1_prime_v2": g1, "dsr": dsr,
        "returns": [round(float(x), 8) for x in r1],
        "x2_returns": [round(float(x), 8) for x in r2],
        "eq_end": round(float(eq1[-1]), 6),
    }


# ---------------------------------------------------------------- baselines (descriptive)

def b_maxdiv_face(R1, names, dates):
    """B_MAXDIV frozen weights (T-27 roster) read-only, same-window recompute --
    benchmark-only descriptive disclosure, zero wiring (veto window to 10-01)."""
    path = os.path.join(PATHS.results_dir, "portfolio_blend_tournament.json")
    try:
        d = json.load(open(path, encoding="utf-8-sig"))
        wmap = d["weights"]["B_MAXDIV"]["weights"]
    except (OSError, KeyError, ValueError):
        return {"available": False, "note": "tournament file unreadable"}
    w = np.zeros(len(names))
    hit = 0
    for i, m in enumerate(names):
        if m in wmap:
            w[i] += float(wmap[m])
            hit += 1
    if hit == 0:
        return {"available": False, "note": "no member weight hits"}
    w /= w.sum()
    T = R1.shape[1]
    eq = np.ones(T)
    eq[WARMUP:] = w @ (R1[:, WARMUP:] / R1[:, WARMUP - 1][:, None])
    r = eq[1:] / eq[:-1] - 1.0
    r = r[WARMUP - 1:]
    return {"available": True, "source": "results/portfolio_blend_tournament.json "
            "weights/B_MAXDIV (read-only)", "n_members_hit": hit,
            "sharpe_cell_window": _sharpe(r), "ann_ret": _ann(r)}


def bench_buyhold_face(bench, nav_dates):
    pos = {d: i for i, d in enumerate(bench.index)}
    T = len(nav_dates)
    eq = np.ones(T)
    b = bench.values
    p0 = pos[pd.Timestamp(nav_dates[WARMUP - 1])]
    for i in range(WARMUP, T):
        eq[i] = b[pos[pd.Timestamp(nav_dates[i])]] / b[p0]
    r = eq[1:] / eq[:-1] - 1.0
    r = r[WARMUP - 1:]
    return {"sharpe_cell_window": _sharpe(r), "ann_ret": _ann(r),
            "note": "510300 buy-and-hold from cell window start (descriptive)"}


# ---------------------------------------------------------------- probe gate (sec.2)

def cmd_probe():
    t0 = time.time()
    M = load_members()
    bp = bench_panel(M["dates"])
    if not bp["core48_ok"]:
        print("  [gate] core48 breadth denominator warning (some symbols <20 bars "
              "since 2020-01)")
    nav_idx = pd.to_datetime(pd.Index(M["dates"]))
    reg = regime_states(bp, nav_idx)
    counts = {}
    for s in reg["states"]:
        counts[s] = counts.get(s, 0) + 1
    print(f"  [gate] members x1={len(M['members'])} bars={M['n_bars']} "
          f"({M['dates'][0]}..{M['dates'][-1]}) families={M['families']}")
    print(f"  [gate] bench last={bp['bench'].index[-1].date()} "
          f"core48_ok={bp['core48_ok']}")
    print(f"  [gate] regime v3 exact recompute shares={counts} "
          f"(probe F4 approximate face disclosed in prereg; exact face governs)")
    rb_n = len(range(WARMUP, M["T"], REBAL))
    print(f"  [gate] rebalance points={rb_n} (from bar {WARMUP} every {REBAL}) "
          f"cell window={M['T'] - WARMUP} bars")
    print(f"  [gate] probe complete in {time.time() - t0:.1f}s -- ZERO judged cell "
          f"values computed (freeze-first law)")
    return 0


# ---------------------------------------------------------------- run

def cmd_run():
    t0 = time.time()
    out_json = os.path.join(OUT_DIR, "p1_results.json")
    if os.path.exists(out_json) and os.environ.get("FUSION_GRID_P1_REFINALIZE") != "1":
        print(f"  [run] {out_json} present -- idempotent no-op exit 0 "
              f"(FUSION_GRID_P1_REFINALIZE=1 is the only redo path)")
        return 0
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUT_DIR, "cells"), exist_ok=True)
    assert SEED_REGISTRY.get("fusion_grid_p1") == SEED, "SEED_REGISTRY drift"
    head_base = int(SG.ledger_head()["total"])
    n_eff = head_base + N_BILL

    M = load_members()
    names, T = M["members"], M["T"]
    R1, R2 = M["R1"], M["R2"]
    bp = bench_panel(M["dates"])
    nav_idx = pd.to_datetime(pd.Index(M["dates"]))
    reg = regime_states(bp, nav_idx)
    counts = {}
    for s in reg["states"]:
        counts[s] = counts.get(s, 0) + 1
    reg_product = {
        "rule": "market_regime.py v3 verbatim (raw_level_v3 + resolve_state_v3 module "
                "functions; fast DIMS precompute only, zero decision-logic rewrite)",
        "n_days": len(reg["states"]), "state_counts": counts,
        "trigger_census": reg["trig_census"], "cap_ladder_frozen": CAP_LADDER,
        "yellow_cap_note": YELLOW_CAP_NOTE,
        "fomc_note": "2026 frozen calendar only; 2020-2025 FOMC days not modeled "
                     "(prereg sec.2 honest disclosure)",
        "probe_f4_note": "frozen probe F4 shares were the APPROXIMATE face "
                         "(R295 probe script); this exact module-recompute governs "
                         "-- divergence is expected and disclosed, prereg sec.2 "
                         "'runner-exact' clause",
        "states": reg["states"], "dates": M["dates"],
    }
    with open(os.path.join(OUT_DIR, "regime_series.json"), "w", encoding="utf-8") as f:
        json.dump(reg_product, f, ensure_ascii=False, indent=1)
    t_reg = time.time() - t0

    points, rb = build_points(R1, names, reg["caps"])
    t_pts = time.time() - t0

    dedup_ns = {j: points[j]["dedup_n"] for j in REDRAW_J if j < len(rb)}
    nulls = run_nulls(R1, rb, dedup_ns, T, len(names))
    with open(os.path.join(OUT_DIR, "nulls_summary.json"), "w", encoding="utf-8") as f:
        json.dump({"batch": BATCH, "K": K_NULLS, "seed": SEED,
                   "rng_law": "np.random.default_rng([20275200, k, j]) per null k per "
                              "redraw j; redraw every 25 rebalance points (j in 0/25/50)",
                   "size_law": "p=7/9 uniform{2..8}; p=1/9 DEDUP count at redraw point; "
                               "p=2/9 all 32; members without-replacement uniform; "
                               "weights Dirichlet(1..1) simplex-uniform",
                   "segments": nulls["segments"],
                   "coverage": nulls["coverage"]}, f, ensure_ascii=False, indent=1)
    t_nulls = time.time() - t0

    # 510300 trailing-252 return over cell window (segment masks, prereg sec.4)
    cell_dates = M["dates"][WARMUP:]
    bvals = bp["bench"].values
    bpos = {d: i for i, d in enumerate(bp["bench"].index)}
    nav_pos = [bpos[d] for d in nav_idx]
    bench_trail = np.zeros(len(cell_dates))
    for i in range(len(cell_dates)):
        p = nav_pos[WARMUP + i]
        bench_trail[i] = bvals[p] / bvals[p - LOOKBACK] - 1.0 if p >= LOOKBACK else 0.0

    payload = {
        "R1": R1, "R2": R2, "T": T, "rb": rb, "points": points, "names": names,
        "n_trades": [M["n_trades"][m] for m in names],
        "cell_dates": cell_dates, "bench_trail": bench_trail,
        "null_values": nulls["values"], "null_coverage": nulls["coverage"],
        "sigma_null": float(nulls["coverage"]["sigma"]), "n_eff": n_eff,
    }
    jobs = [(f"{fam}__{sub}", _cell_job, (fam, sub))
            for fam in FAMILIES for sub in SUBSETS]
    assert len(jobs) == BATCH_CELLS
    out = run_cells_parallel(jobs, workers=4, desc="fusion grid cells",
                             initializer=_cell_init, initargs=(payload,))
    workers_used = out.pop("__workers__", 1)
    keys = [j[0] for j in jobs]
    cells = {k: out[k] for k in keys}
    t_cells = time.time() - t0

    # family PBO (CSCV 8 blocks, same-family 45-cell return matrix)
    mat = pd.DataFrame({k: pd.Series(cells[k]["returns"],
                                     index=pd.to_datetime(pd.Index(cell_dates)))
                        for k in keys})
    pbo = cscv_pbo(mat)
    pbo_val = float(pbo["pbo"]) if isinstance(pbo, dict) else float(pbo)

    for k in keys:
        c = cells[k]
        c["g2"] = SG.g2_registration_v2(c["g1_prime_v2"]["pass_v2"], c["dsr"], pbo_val)
        c["g2"]["d6_note"] = ("zero new signal functions in batch (members = already-"
                              "judged registered faces, NAV-level combination); "
                              "batch-internal structural corr is the N_eff billing "
                              "face, admission line not applicable (prereg sec.1)")
        with open(os.path.join(OUT_DIR, "cells", f"{k}.json"), "w",
                  encoding="utf-8") as f:
            json.dump({"batch": BATCH, "cell": k, "prereg_ref": PREREG_REF,
                       "evidence_cutoff": EVIDENCE_CUTOFF,
                       "family": c["family"], "subset": c["subset"],
                       "subset_sizes": c["subset_sizes"],
                       "dedup_n_series": c["dedup_n_series"],
                       "caps_series": c["caps_series"],
                       "stats": c["stats"], "x2": c["x2"],
                       "n_entries_f6": c["n_entries_f6"],
                       "hold_shares_nonzero": c["hold_shares_nonzero"],
                       "g1_prime_v2": c["g1_prime_v2"], "dsr": c["dsr"],
                       "g2": c["g2"], "eq_end": c["eq_end"],
                       "returns": c["returns"], "x2_returns": c["x2_returns"]},
                      f, ensure_ascii=False, indent=1)

    ledger = append_ledger(BATCH, N_BILL, file_name="fusion_grid_p1",
                           evidence_cutoff=EVIDENCE_CUTOFF, prev_total=head_base,
                           note=f"45 judged cells (5 weight families x 9 subsets) + "
                                f"K=2000 same-mask random-portfolio nulls; x1 judged "
                                f"face (fusion-layer cost 0, members embed own costs); "
                                f"v3 regime verbatim recompute; seed fusion_grid_p1="
                                f"{SEED} R250 one-step; prereg {PREREG_REF}; {TICKET}")

    b_maxdiv = b_maxdiv_face(R1, names, M["dates"])
    buyhold = bench_buyhold_face(bp["bench"], M["dates"])
    any_g1 = cells[keys[0]]["g1_prime_v2"]["skill_line"]

    summary_cells = {}
    for k in keys:
        c = cells[k]
        summary_cells[k] = {
            "sharpe_full": c["stats"]["sharpe_full"],
            "ann_ret": c["stats"]["ann_ret"], "max_dd": c["stats"]["max_dd"],
            "oos_dual_positive": c["stats"]["oos_dual_positive"],
            "g1_pass_v2": c["g1_prime_v2"]["pass_v2"],
            "line_ok": c["g1_prime_v2"]["line_ok"],
            "ci_lower_bound_positive": c["g1_prime_v2"]["ci_lower_bound_positive"],
            "dsr": c["dsr"]["dsr"], "eligible_v2": c["g2"]["eligible_v2"],
            "n_entries_f6": c["n_entries_f6"],
            "x2_sharpe": c["x2"]["sharpe_full"],
            "x2_sharpe_degradation": c["x2"]["sharpe_degradation"],
        }

    product = {
        "batch": BATCH, "ticket_ref": TICKET, "prereg_ref": PREREG_REF,
        "seed": SEED, "seed_law": "fusion_grid_p1=20275200 registered at freeze commit "
                                 "(R250 one-step, R295); null streams [seed,k,j]",
        "evidence_cutoff": EVIDENCE_CUTOFF, "cutoff_meta": cutoff_meta(EVIDENCE_CUTOFF),
        "science_gates": {"cutoff_meta": cutoff_meta(EVIDENCE_CUTOFF),
                          "ledger": ledger},
        "panel": {"members": names, "n_members": len(names), "families": M["families"],
                  "bars": M["n_bars"], "first": M["dates"][0], "last": M["dates"][-1],
                  "warmup_bars": WARMUP, "rebalance_every": REBAL,
                  "rebalance_points": len(rb), "cell_window_bars": T - WARMUP,
                  "x2_face": "same decision sequence (x1 causal subsets/weights/caps) "
                             "evaluated on x2 member NAVs -- stress descriptive face"},
        "regime": {"state_counts": counts, "trigger_census": reg["trig_census"],
                   "cap_ladder_frozen": CAP_LADDER, "yellow_cap_note": YELLOW_CAP_NOTE},
        "subsets_audit": {"dedup_n_series_all32": [p["dedup_n"] for p in points],
                          "subset_size_note": "dynamic faces per point disclosed in "
                                              "cells/*.json subset_sizes"},
        "nulls": {"K": K_NULLS, "coverage": nulls["coverage"],
                  "method": nulls["method"], "segments": nulls["segments"]},
        "skill_line": any_g1,
        "baselines_descriptive": {
            "ew48_passive": {"sharpe": round(any_g1["passive_term"] - 0.10, 4),
                             "note": "skill_line_v2 passive term -0.10 (core48 pool)"},
            "b_maxdiv": b_maxdiv, "bench_510300_buyhold": buyhold,
            "note": "descriptive disclosure only, no extra verdict lines (prereg sec.3)"},
        "family_pbo": {"pbo": pbo_val, "method": "screening/pbo.py cscv_pbo 8 blocks "
                         "on 45-cell same-family return matrix"},
        "cells": summary_cells,
        "trials_ledger": ledger,
        "audit": {"workers": workers_used, "nulls_workers": nulls["workers"],
                  "elapsed_sec": round(time.time() - t0, 1),
                  "phase_sec": {"regime": round(t_reg, 1), "points": round(t_pts, 1),
                                "nulls": round(t_nulls, 1), "cells": round(t_cells, 1)},
                  "ledger_head_before": head_base,
                  "ledger_total_after": ledger["total"],
                  "machine_note": "burned via runnable_pool autofill lane "
                                  "(O-2100/O-2130 laws)"},
        "cost": {"judged_face": "x1", "fusion_layer_cost": 0.0,
                 "note": "member NAVs embed member-level costs (s1 engine face); FoF "
                         "reconfiguration friction unmodeled = disclosed batch "
                         "limitation; x2 member stress face partially covers "
                         "sensitivity (prereg sec.3)"},
        "hard_bounds_note": "not a data-corruption/health-detection batch (NAV linear "
                            "combinations carry no health-detection line) -- three-"
                            "piece hard-bound set not applicable, disclosed (prereg "
                            "sec.4); sec.5 P5 extreme-day priors still carried",
        "predictions_prereg_s5": [
            "P1: EW-ALL32 full Sharpe in [0.7, 1.1]",
            "P2: skill line (batch-own null calibration) >= 1.4 -> honest-negative "
            "most-likely outcome; only large-subset x diversified-weight families "
            "can approach the line",
            "P3: REGIME_COND bear-segment maxDD improves >= 5pp vs same-subset EW",
            "P4: TOP-K small K (2-4) cells show higher vol + deeper maxDD vs ALL",
            "P5: extreme-day priors (2024-02-28 microcap crash, 2024-09-30 policy "
            "pulse) carried by member NAVs; linear combination does not amplify "
            "single-day extremes; RED cap<=0.20 compresses deep-replay days"],
        "attrition_note": "gate_attrition row appended at prereg sec.8 harvest time "
                          "(r248 entries-list law), not at run time",
    }
    with open(out_json + ".tmp", "w", encoding="utf-8") as f:
        json.dump(product, f, ensure_ascii=False, indent=1)
    os.replace(out_json + ".tmp", out_json)

    n_pass = sum(1 for c in cells.values() if c["g1_prime_v2"]["pass_v2"])
    n_elig = sum(1 for c in cells.values() if c["g2"]["eligible_v2"])
    print(f"  [run] {BATCH}: 45 cells, nulls mu={nulls['coverage']['mu']:.4f} "
          f"sigma={nulls['coverage']['sigma']:.4f}, PBO={pbo_val}")
    print(f"  [run] G1'v2 pass {n_pass}/45, G2 eligible {n_elig}/45, "
          f"line={any_g1['line']}, n_eff={any_g1['n_eff']}")
    print(f"  [run] regime counts={counts}, workers={workers_used}, "
          f"elapsed={time.time() - t0:.1f}s, ledger={ledger['total']}")
    return 0


# ---------------------------------------------------------------- selftest (hermetic)

def _synth_members(n=4, T=800, seed=7):
    """Synthetic NAV matrix: deterministic distinct behaviours (MA/MC ~0.99 corr)."""
    rng = np.random.default_rng(seed)
    R = np.ones((n, T))
    drifts = [0.0008, 0.0006, -0.0002, 0.0004]
    vols = [0.004, 0.008, 0.004, 0.020]
    common = rng.standard_normal(T)
    for m in range(n):
        if m in (0, 2):
            shocks = 0.1 * rng.standard_normal(T) + 1.5 * common
        else:
            shocks = 0.9 * rng.standard_normal(T)
        r = drifts[m] + vols[m] * shocks
        R[m, 1:] = np.cumprod(1.0 + r)[1:] * (1.0 + r[0])
    return R


def _selftest_regime_equivalence():
    """(a) fast dims vs module originals on truncated series, >=20 random dates."""
    ok = True

    def check(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  [selftest] {name}... {'PASS' if cond else 'FAIL'}")

    M = load_members()
    bp = bench_panel(M["dates"])
    nav_idx = pd.to_datetime(pd.Index(M["dates"]))
    rng = np.random.default_rng(20260927)
    sample = sorted(set(rng.choice(len(nav_idx), size=20, replace=False).tolist())
                    | {len(nav_idx) - 1})
    bench = bp["bench"]
    bad = 0
    for i in sample:
        d = nav_idx[i]
        bd_f, br_f = fast_dims_at(bp, d)
        bd_m = MR.bench_dims(bench.loc[:d])
        br_m = MR.breadth_dims(bench.loc[:d])
        for k in ("crash_10d", "panic_1d"):
            a, b = bd_f.get(k), bd_m.get(k)
            if not ((a is None and b is None) or
                    (a is not None and b is not None and abs(a - b) < 1e-9)):
                bad += 1
        for k in ("vol_status", "vol20", "vol_p95", "vol_p80"):
            a, b = bd_f.get(k), bd_m.get(k)
            if a != b and not (a is not None and b is not None and abs(a - b) < 1e-9):
                bad += 1
        if bd_f["event_fomc"] != bd_m["event_fomc"]:
            bad += 1
        for k in ("share_below_ma20", "share_slope_5d"):
            a, b = br_f.get(k), br_m.get(k)
            if a != b and not (a is not None and b is not None and abs(a - b) < 1e-9):
                bad += 1
        raw_f, _ = MR.raw_level_v3(bd_f, br_f, bool(bp["bear"].loc[d]))
        raw_m, _ = MR.raw_level_v3(bd_m, br_m,
                                   bool(major_bear_state(bench.loc[:d])["is_major_bear"]))
        if raw_f != raw_m:
            bad += 1
        if bool(bp["bear"].loc[d]) != bool(major_bear_state(bench.loc[:d])["is_major_bear"]):
            bad += 1
    check(f"A1 fast dims == module bench_dims/breadth_dims on {len(sample)} sampled "
          f"dates (incl. last NAV day), zero mismatches", bad == 0)

    bd_p = MR.probe(write=False)["dims"]
    d_last = bench.index[-1]
    bd_f, br_f = fast_dims_at(bp, d_last)
    bdp, brp = bd_p["bench"], bd_p["breadth"]
    same = (bd_f["crash_10d"] is not None and
            abs(bd_f["crash_10d"] - bdp["crash_10d"]) < 1e-9 and
            bd_f["vol_status"] == bdp["vol_status"] and
            (bd_f["vol_status"] != "ok" or
             (abs(bd_f["vol20"] - bdp["vol20"]) < 1e-9 and
              abs(bd_f["vol_p95"] - bdp["vol_p95"]) < 1e-9 and
              abs(bd_f["vol_p80"] - bdp["vol_p80"]) < 1e-9)) and
            bd_f["event_fomc"] == bdp["event_fomc"] and
            br_f["share_below_ma20"] == brp["share_below_ma20"] and
            br_f["share_slope_5d"] == brp["share_slope_5d"])
    check("A2 last bench day dims == live probe() dims", same)

    reg = regime_states(bp, nav_idx)
    counts = {}
    for s in reg["states"]:
        counts[s] = counts.get(s, 0) + 1
    check("A3 regime series covers all NAV dates with module state set",
          len(reg["states"]) == len(nav_idx) and
          set(reg["states"]) <= set(CAP_LADDER))
    return ok


def _selftest_constructive():
    """(b) synthetic-member constructive tests (warmup/drift/families/subsets)."""
    ok = True

    def check(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  [selftest] {name}... {'PASS' if cond else 'FAIL'}")

    names = ["MA", "MB", "MC", "MD"]
    R = _synth_members()
    T = R.shape[1]
    rb = list(range(WARMUP, T, REBAL))
    assert len(rb) >= 3
    st = trailing_at(R, rb[0])
    subs = subsets_at(st, names)
    check("B1 ALL32 = all valid members on synthetic", len(subs["ALL32"]) == 4)
    check("B2 DEDUP collapses the 0.95-correlated pair (MA/MC common factor)",
          len(subs["DEDUP"]) == 3 and
          all(names.index(m) in list(subs["DEDUP"]) for m in ("MB", "MD")))
    check("B3 TOP2 = first 2 of DEDUP pool order",
          subs["TOP2"] == subs["DEDUP"][:2])

    w_ew = weights_at("EW", subs["ALL32"], st)
    check("B4 EW weights = 1/n and sum 1", abs(w_ew.sum() - 1) < 1e-12 and
          np.allclose(w_ew[subs["ALL32"]], 0.25))
    w_iv = weights_at("INV_VOL", subs["ALL32"], st)
    expect = np.array([1.0 / st["sd"][i] for i in subs["ALL32"]])
    expect = expect / expect.sum()
    check("B5 INV_VOL weights proportional 1/vol",
          np.allclose(w_iv[subs["ALL32"]], expect, atol=1e-12))
    w_im = weights_at("INV_MDD", subs["ALL32"], st)
    m_mag = np.array([max(-st["mdd"][i], 0.05) for i in subs["ALL32"]])
    expect = (1.0 / m_mag) / (1.0 / m_mag).sum()
    check("B6 INV_MDD floor 0.05 + proportionality",
          np.allclose(w_im[subs["ALL32"]], expect, atol=1e-12))
    w_cc = weights_at("CORR_CLUSTER_RP", subs["ALL32"], st)
    check("B7 CORR_CLUSTER_RP sums 1, nonneg, zero outside subset",
          abs(w_cc.sum() - 1) < 1e-12 and w_cc.min() >= 0 and
          all(w_cc[i] == 0 for i in range(4) if i not in subs["ALL32"]))

    # R297 E1 contract leg: every st[...] key subscripted downstream by
    # _cell_job/summary must exist -- the 05:50 burn crashed all 45 cell jobs
    # on a missing 'sharpe_full'; prior hermetic legs never subscripted it.
    n = 300
    rr = np.random.default_rng(7).normal(0.0005, 0.01, n)
    dd = pd.date_range("2020-01-01", periods=n, freq="B")
    stc = cell_descriptive(rr, dd, np.zeros(n))
    check("B7b cell_descriptive downstream key contract (sharpe_full et al)",
          {"sharpe_full", "ann_ret", "max_dd", "oos_dual_positive",
           "yearly_returns"} <= set(stc) and stc["sharpe_full"] is not None)

    # warmup + drift math: hand-computed mini-grid (warmup=2)
    R2s = np.array([[1.0, 1.0, 2.0, 2.0, 2.0],
                    [1.0, 1.0, 1.0, 1.0, 1.0]])
    w = np.array([0.5, 0.5])
    rb_s = [2]
    r, eq = cell_returns(R2s, [w], [1.0], rb_s, 5, warmup=2)
    check("B8 warmup cash bars 0..warmup-1 flat 1.0",
          abs(eq[0] - 1) < 1e-15 and abs(eq[1] - 1) < 1e-15)
    check("B9 drift-weight path exact (units held, weights drift)",
          abs(eq[2] - 1.5) < 1e-12 and abs(eq[3] - 1.5) < 1e-12 and
          abs(eq[4] - 1.5) < 1e-12 and len(r) == 3)
    r_cap, eq_cap = cell_returns(R2s, [w], [0.2], rb_s, 5, warmup=2)
    check("B10 REGIME_COND cap ladder + zero-return cash leg (cap=0.2)",
          abs(eq_cap[2] - (0.8 + 0.2 * 1.5)) < 1e-12)
    hs = hold_shares([w], rb_s, 5, 2, warmup=2)
    check("B11 hold shares = active bars / cell window bars",
          abs(hs[0] - 1.0) < 1e-12 and abs(hs[1] - 1.0) < 1e-12)

    st2 = trailing_at(R, rb[0])
    subs2 = subsets_at(st2, names)
    same = (subs2 == subs and
            np.array_equal(weights_at("INV_VOL", subs2["ALL32"], st2),
                           weights_at("INV_VOL", subs["ALL32"], st)))
    check("B12 subset/weight derivation deterministic on rerun", same)
    return ok


def _selftest_nulls():
    """(c) null determinism replay + size law + no-replacement."""
    ok = True

    def check(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  [selftest] {name}... {'PASS' if cond else 'FAIL'}")

    mem, w = null_draw(np.random.default_rng([SEED, 0, 0]), dedup_n=5)
    mem2, w2 = null_draw(np.random.default_rng([SEED, 0, 0]), dedup_n=5)
    check("C1 null stream [seed,k,j] deterministic replay",
          np.array_equal(mem, mem2) and np.allclose(w, w2))
    check("C2 null members no-replacement + weights simplex",
          len(set(mem.tolist())) == len(mem) and abs(w.sum() - 1) < 1e-9)
    sizes = set()
    for k in range(200):
        m_, _ = null_draw(np.random.default_rng([SEED, k, 0]), dedup_n=5)
        sizes.add(len(m_))
    check("C3 size law support subset of {2..8} U {dedup_n} U {32} with p-branches hit",
          sizes <= set(range(2, 9)) | {5, 32} and {5, 32} <= sizes)
    rows_a = null_rows(3, [0, 25, 50], {0: 4, 25: 4, 50: 4})
    rows_b = null_rows(3, [0, 25, 50], {0: 4, 25: 4, 50: 4})
    check("C4 per-segment null rows replay byte-identical, simplex each",
          all(np.array_equal(a, b) for a, b in zip(rows_a, rows_b)) and
          all(abs(a.sum() - 1) < 1e-9 for a in rows_a))
    R = _synth_members()
    T = R.shape[1]
    rb = list(range(WARMUP, T, REBAL))
    nl = run_nulls(R, rb, {0: 3, 25: 3, 50: 3}, T, 4)
    nl2 = run_nulls(R, rb, {0: 3, 25: 3, 50: 3}, T, 4)
    check("C5 synthetic nulls run deterministic (values + coverage)",
          nl["values"] == nl2["values"] and
          nl["coverage"]["mu"] == nl2["coverage"]["mu"] and
          nl["coverage"]["n_values"] == K_NULLS)
    return ok


def cmd_selftest():
    ok = True
    ok &= _selftest_regime_equivalence()
    ok &= _selftest_constructive()
    ok &= _selftest_nulls()
    check = SEED_REGISTRY.get("fusion_grid_p1") == SEED
    print(f"  [selftest] SEED_REGISTRY fusion_grid_p1=={SEED}... "
          f"{'PASS' if check else 'FAIL'}")
    ok &= bool(check)
    print(f"  [selftest] {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["probe", "selftest", "run"])
    args = ap.parse_args()
    if args.cmd == "probe":
        return cmd_probe()
    if args.cmd == "selftest":
        return cmd_selftest()
    return cmd_run()


if __name__ == "__main__":
    sys.exit(main())
