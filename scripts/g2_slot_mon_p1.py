"""G2_SLOT_MON_P1 census runner (monthly-translation decomposition variant;
frozen prereg research/G2_SLOT_MON_P1.md v1.0, freeze commit 076c53dd2
precedes any census run -- R99).

Law lineage: r644 G2_SLOT_TAIL_P1 sec.8 heritage clause ("any future
low-cost translation-layer variant = new translation caliber new prereg,
not a reversal") -> this batch asks the cost-vs-horizon decomposition ONCE
on the 47/126 IC-enriched roster (old 18 + stock 2 + tail 27 cond1
passers, deterministic union of the three frozen parent censuses): did the
weekly x2 translation layer die of COST (monthly saves ~4x cost events ->
survivors expected) or of HORIZON (5d IC not extendable to 21d holding ->
monthly dies cheaper)? Parent weekly verdicts (0/41 + 0/14 + 0/71) are
untouched -- new caliber, not a reversal.

Frozen mechanics (prereg sec.2/sec.3; structure mirrors scripts/g2_slot_tail_p1.py):
  panel   = core48 INSERVICE_WHITELIST (sha16 abf3d43b9ca13ea5), raw
            pd.read_csv truncation at evidence_cutoff 2026-09-22, window from
            2020-01-02, union 1631 td; mask = 6-field notna & volume>0 &
            amount>0 (+ pre-IPO masked); vwap = amount/volume.
  vendor  = ml-quant-trading pinned install (HEAD==a770825), LEGACY_REGISTRY
            import face + add/better/best/extra/old/stock family modules,
            torch CPU only (GPU never used -- compute_audit face).
  grid    = MONTHLY: g = first trading day of each calendar month, e = next
            trading day (T+1 mirror; ~81 months in window; sec.3 leg ii).
  faces   = 47 enriched roster faces (probe roster_freeze sha16
            7ce1e81d019eba3d); class/family tags carried from parent
            censuses AS-IS (frozen inheritance, no re-adjudication -- r644
            E22 vendor-adjudication canon).
  leg i   = per-day cross-sectional Spearman rank-IC vs fwd-5d (re-measured
            for batch self-containment) + PARENT-IC DETERMINISM CROSS-CHECK:
            re-measured ic5_mean must equal the parent census value (same
            panel / same vendor / same window -> drift = mechanical fault,
            fail-closed).
  leg ii  = monthly Top-16 equal-weight blend sleeve; exec = next trading
            day; flat cost 13.041bp per side x COST_FACES {x1 main, x2
            nomination}; passive = EW48 B&H.
  leg iii = 20 same-mask monthly random sleeves, rng([20560000, k])
            substream law, K=20, seed band pre-registered (band
            [20560000,20560020) disjoint). Null band = p95 of |mean IC| +
            beat-rate distribution at MONTHLY caliber (wider se: ~81
            effective months vs weekly ~345).
  leg iv  = D6 numeric face: per-face x1 blend daily series vs REG6
            registered-member daily series pairwise |corr| + in-batch
            47x46/2 pairwise -> d6_numeric.json.
  leg v   = family aggregation: old/stock/tail enriched subpools
            independently adjudicated; 0 nominations = family's
            MONTHLY-cadence question answered (parent weekly verdicts
            unaffected); >=1 nomination = stage-2 shortlist face.
  regime  = 510300 t22 3-way proxy per-segment blend-leg disclosure.
  BAN     = class carried from parent census as-is; price_banned faces
            measured but never nominatable (frozen sec.0.5 inheritance).
  exit    = hold-to-end monthly rank rotation (falling out of the monthly
            Top-16 ranking is the ONLY exit; no price-type exit) --
            sec.0.6 census approximation face, honestly disclosed.

Determinism: zero wall-clock fields in the batch JSON; selftest = double-run
byte identity (mini-pipeline, real panel) + roster/cutoff/mask/seed/cost/
parent-IC/monthly-grid legs. Budget cap 300s (O-1901 (a)-1 item iii):
over-budget abort = exit 3, nothing finalized.

Usage: run | selftest
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "research", "shortline", "screening"))

VENDOR_SRC = r"C:\Users\sjs20\Desktop\FluxGroup\quant\toolstack\repos\ml-quant-trading\src"
VENDOR_REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\toolstack\repos\ml-quant-trading"
ANCHOR_HEAD = "a770825f841504e41581f057b4d94160e6a50c2e"
sys.path.insert(0, VENDOR_SRC)

BATCH = "G2_SLOT_MON_P1"
TICKET = "T-2026-10-03-163-P1"
PREREG_REL = "research/G2_SLOT_MON_P1.md"
CUTOFF = "2026-09-22"
PANEL_START = "2020-01-02"
SEED_NULLS = 20560000
K_NULLS = 20
TOP_K = 16
W6M, STRIDE, WARMUP = 126, 21, 252        # T-22 caliber beat-rate windows
BUDGET_CAP_S = 300                        # O-1901 (a)-1 item iii
D6_REJECT = 0.7
D6_MIN_OVERLAP = 20
ROSTER_SHA16 = "7ce1e81d019eba3d"         # probe roster_freeze anchor (r647)
INERVICE_SHA16_EXPECT = "abf3d43b9ca13ea5"
FAMILIES = ("old", "stock", "tail")        # enriched subpools (probe leg1)
N_BURN_EXPECT = 47
PARENT_IC_TOL = 1e-6                       # rounded-6dp identity tolerance
REG6 = ("COMPOSITE-CE-01", "COMPOSITE-CE-02", "DROUGHT-CE-01",
        "ENGULF-CE-01", "NEEDLE-DE-01", "VOLATILITY-CE-01")
PROBE_JSON = os.path.join(ROOT, "results", "_r647bma_slot_mon_roster_probe.json")
OUT_DIR = os.path.join(ROOT, "results", "g2_slot_mon_p1")
OUT_JSON = os.path.join(OUT_DIR, "g2_slot_mon_p1_census.json")
D6_JSON = os.path.join(OUT_DIR, "d6_numeric.json")
IC_CSV = os.path.join(OUT_DIR, "ic_by_face.csv")
IC_DAILY_CSV = os.path.join(OUT_DIR, "ic_daily.csv")
ATTR_JSON = os.path.join(ROOT, "results", "gate_attrition.json")

SIX_FIELDS = ("open", "high", "low", "close", "volume", "amount")

import science_gates as sg  # noqa: E402
from rev_osc_stock_p1 import COST_X1  # noqa: E402
from t22_virtual_timepoints import regime_proxy  # noqa: E402
from knowledge.panel_gate import INSERVICE_WHITELIST, INSERVICE_SHA16  # noqa: E402
from p1_factor_screen import ic_series  # noqa: E402

COST_FACES = {"x1": float(COST_X1), "x2": float(COST_X1) * 2.0}
COST_X1_EXPECT = 0.0013041


def _fail(msg, code=2):
    print("[g2slotmonp1] FAIL: %s" % msg, flush=True)
    raise SystemExit(code)


def _r(x, nd=4):
    return None if x is None or not np.isfinite(x) else round(float(x), nd)


# ---------------------------------------------------------------- gates

def vendor_head():
    r = subprocess.run(["git", "-C", VENDOR_REPO, "rev-parse", "HEAD"],
                       capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else "RC=%d" % r.returncode


def roster_from_probe():
    probe = json.load(open(PROBE_JSON, encoding="utf-8"))
    roster = probe["roster"]
    canon = json.dumps(roster, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":"))
    sha = hashlib.sha256(canon.encode("utf-8")).hexdigest()
    return probe, roster, sha


def roster_faces():
    probe, roster, sha = roster_from_probe()
    faces = sorted(roster)
    families = {fam: sorted(probe["leg1_roster"]["per_batch"][fam]["faces"])
                for fam in FAMILIES}
    return probe, roster, sha, faces, families


def run_gates(panel_facts):
    fails = []
    g = {}
    g["members"] = panel_facts["n_members"] == 48
    g["columns"] = not panel_facts["bad_columns_members"]
    g["dup_dates"] = not panel_facts["dup_date_members"]
    g["cutoff_truncation"] = panel_facts["union_last"] == CUTOFF
    g["vendor_head"] = vendor_head() == ANCHOR_HEAD
    probe, roster, sha, faces, families = roster_faces()
    g["roster_sha"] = (sha.startswith(ROSTER_SHA16)
                       and len(faces) == N_BURN_EXPECT
                       and sum(len(v) for v in families.values()) == N_BURN_EXPECT)
    g["families"] = (sorted(families) == sorted(FAMILIES)
                     and len(families["old"]) == 18
                     and len(families["stock"]) == 2
                     and len(families["tail"]) == 27)
    own = sg.SEED_REGISTRY.get("g2_slot_mon_p1_nulls")
    g["seed_registered"] = own == SEED_NULLS
    overlap = []
    for k, v in sg.SEED_REGISTRY.items():
        if k == "g2_slot_mon_p1_nulls":
            continue
        try:
            iv = int(v)
        except (TypeError, ValueError):
            continue
        if SEED_NULLS <= iv < SEED_NULLS + K_NULLS:
            overlap.append(k)
    g["seed_band_disjoint"] = not overlap
    g["cost_x1_single_source"] = abs(COST_X1 - COST_X1_EXPECT) < 1e-12
    g["whitelist_sha16"] = INSERVICE_SHA16 == INERVICE_SHA16_EXPECT
    fails = [k for k, v in g.items() if not v]
    return (not fails), g, fails, probe


# ---------------------------------------------------------------- panel

def build_panel():
    members = sorted(INSERVICE_WHITELIST)
    dfs = {}
    dup_date_members, bad_cols = [], []
    for code in members:
        p = os.path.join(ROOT, "data", "daily", "%s.csv" % code)
        if not os.path.exists(p):
            _fail("G-PANEL FAIL: %s csv missing" % code)
        df = pd.read_csv(p, parse_dates=["date"])
        if not set(SIX_FIELDS) <= set(df.columns):
            bad_cols.append(code)
            continue
        df = df[(df["date"] >= pd.Timestamp(PANEL_START))
                & (df["date"] <= pd.Timestamp(CUTOFF))]
        if df["date"].duplicated().any():
            dup_date_members.append(code)
        dfs[code] = df.set_index("date")
    if len(dfs) != 48:
        _fail("G-PANEL FAIL: loaded %d != 48 members" % len(dfs))
    idx = pd.DatetimeIndex(sorted(set().union(*[set(d.index) for d in dfs.values()])))
    N, T = len(members), len(idx)

    def mat(fld):
        f = pd.DataFrame({c: dfs[c][fld] for c in members}).reindex(idx)
        return np.asarray(f, dtype=np.float32)

    F = {fld: mat(fld) for fld in SIX_FIELDS}
    base = (np.isfinite(F["open"]) & np.isfinite(F["high"]) & np.isfinite(F["low"])
            & np.isfinite(F["close"]) & np.isfinite(F["volume"]) & (F["volume"] > 0)
            & np.isfinite(F["amount"]) & (F["amount"] > 0))
    vol_safe = np.where(F["volume"] == 0, 1.0, F["volume"])
    vwap = np.asarray(F["amount"] / vol_safe, dtype=np.float32)
    close_df = pd.DataFrame(F["close"], index=idx, columns=members)
    rets = np.asarray(close_df.pct_change(), dtype=np.float64)
    fwd5 = np.asarray(close_df.shift(-5) / close_df - 1.0, dtype=np.float64)
    fwd1 = np.asarray(close_df.shift(-1) / close_df - 1.0, dtype=np.float64)
    facts = {
        "n_members": N, "n_days": T,
        "union_first": str(idx[0].date()), "union_last": str(idx[-1].date()),
        "mask_fraction": round(float(base.mean()), 6),
        "min_valid_per_member": int(base.sum(axis=0).min()),
        "bad_columns_members": bad_cols, "dup_date_members": dup_date_members,
    }
    return {"members": members, "idx": idx, "F": F, "vwap": vwap,
            "base": base, "rets": rets, "fwd5": fwd5, "fwd1": fwd1, "facts": facts}


def make_torch_panel(panel):
    import torch
    from mlquant.data.panel import Panel
    F, base = panel["F"], panel["base"]
    return Panel(dates=np.arange(base.shape[0]), stocks=panel["members"],
                 open=torch.from_numpy(F["open"]), high=torch.from_numpy(F["high"]),
                 low=torch.from_numpy(F["low"]), close=torch.from_numpy(F["close"]),
                 volume=torch.from_numpy(F["volume"]),
                 vwap=torch.from_numpy(panel["vwap"]),
                 mask=torch.from_numpy(base),
                 amount=torch.from_numpy(F["amount"]))


def compute_faces(panel, faces):
    """Vendor single-source face computation -> {face: (Fmat, valid, beyond_ct)}."""
    from mlquant.features.legacy_factors import LEGACY_REGISTRY
    import mlquant.features._factors_add  # noqa: F401  registration side-effect
    import mlquant.features._factors_better  # noqa: F401
    import mlquant.features._factors_best  # noqa: F401
    import mlquant.features._factors_extra  # noqa: F401
    import mlquant.features._factors_old  # noqa: F401
    import mlquant.features._factors_stock  # noqa: F401
    tpanel = make_torch_panel(panel)
    base = panel["base"]
    out = {}
    for f in faces:
        try:
            val, m = LEGACY_REGISTRY[f](tpanel)
            mv = np.asarray(m.numpy(), dtype=bool)
            valid = mv & base
            vals = np.asarray(val.numpy(), dtype=np.float64)
            Fmat = np.where(valid, vals, np.nan)
            out[f] = (Fmat, valid, int((mv & ~base).sum()))
        except Exception as e:  # noqa: BLE001  honest per-face failure
            out[f] = (None, None, "err:%s" % type(e).__name__)
    return out


# ---------------------------------------------------------------- grid + sleeves

def monthly_grid(idx):
    """(g, e) positions: g = first trading day of each calendar month."""
    months = [(d.year, d.month) for d in idx]
    gs = []
    seen = set()
    for pos, m in enumerate(months):
        if m not in seen:
            seen.add(m)
            gs.append(pos)
    return [(g, g + 1) for g in gs if g + 1 < len(idx)]


def _accrue(rets, d, wmap):
    r = 0.0
    for s, w in wmap.items():
        rv = rets[d, s]
        if np.isfinite(rv):
            r += w * rv
    return r


def blend_sleeve(score_fn, grid_pairs, rets, cost_side):
    """Monthly Top-16 equal-weight sleeve (identical accrual/cost model to
    the weekly canon; only the grid is monthly). score_fn(g) -> row/None."""
    T = rets.shape[0]
    pairs = [(g, e) for (g, e) in grid_pairs if e < T]
    prev = {}
    daily = np.zeros(T, dtype=np.float64)
    first_exec = None
    turnover_total = 0.0
    n_rebal = 0
    n_skip = 0
    n_buys_total = 0        # additive r649 (P2 trade-census face, no P1 consumer)
    n_exits_total = 0       # additive r649: rank-rotation exits (constructive only)
    exit_log = []           # additive r649: per-rebalance {n_exits, n_buys} census rows
    for j, (g, e) in enumerate(pairs):
        row = score_fn(g)
        target = None
        if row is not None:
            valid = np.flatnonzero(np.isfinite(row))
            if len(valid) >= TOP_K:
                target = valid[np.argsort(-row[valid], kind="stable")[:TOP_K]]
        r_old = _accrue(rets, e, prev) if prev else 0.0
        if target is None:
            # sec.0.6: falling out of the monthly Top-16 ranking is the ONLY
            # exit; a month with no full ranking is no rebalance -> hold
            n_skip += 1
            if prev:
                daily[e] = r_old
        else:
            tset = set(int(t) for t in target)
            want = 1.0 / TOP_K
            new_w = {s: prev[s] for s in tset if s in prev}
            buys = [s for s in tset if s not in prev]
            for s in buys:
                new_w[s] = want
            dw = sum(w for s, w in prev.items() if s not in tset) + len(buys) * want
            cost = dw * cost_side
            turnover_total += dw
            n_rebal += 1
            n_buys_total += len(buys)
            n_ex_rot = sum(1 for s in prev if s not in tset)
            n_exits_total += n_ex_rot
            exit_log.append({"n_exits": n_ex_rot, "n_buys": len(buys)})
            if first_exec is None:
                first_exec = e
            daily[e] = r_old - cost
            prev = new_w
        stop = pairs[j + 1][1] if j + 1 < len(pairs) else T
        for d in range(e + 1, stop):
            if d >= T:
                break
            r = _accrue(rets, d, prev)
            daily[d] = r
    if first_exec is None:
        return None
    series = daily[first_exec:]
    return {"series": series, "first_exec": first_exec,
            "turnover_total": turnover_total, "n_rebal": n_rebal, "n_skip": n_skip,
            "n_buys_total": n_buys_total, "n_exits_total": n_exits_total,
            "exit_log": exit_log}


def sleeve_metrics(series, idx, first_exec):
    if len(series) < 20:
        return {"ann": None, "vol": None, "sharpe": None, "maxdd": None,
                "total_ret": None, "n_days": int(len(series))}
    ann = float(np.mean(series) * 252.0)
    sd = float(np.std(series, ddof=1))
    vol = sd * float(np.sqrt(252.0))
    sharpe = ann / vol if vol > 0 else 0.0
    eq = np.cumprod(1.0 + series)
    peak = np.maximum.accumulate(eq)
    maxdd = float(np.min(eq / peak - 1.0))
    return {"ann": _r(ann), "vol": _r(vol), "sharpe": _r(sharpe), "maxdd": _r(maxdd),
            "total_ret": _r(float(eq[-1] - 1.0)), "n_days": int(len(series))}


def ew48_window(rets, first_exec):
    """EW48 B&H passive baseline (fixed 1/48, NaN->0 accrual; costless)."""
    w = 1.0 / rets.shape[1]
    ew = np.where(np.isfinite(rets), rets, 0.0).sum(axis=1) * w
    return ew[first_exec:]


def beat_rate(series, ew, first_exec, T):
    starts = range(max(WARMUP, first_exec), T - W6M + 1, STRIDE)
    starts = list(starts)
    if not starts:
        return None, 0
    beats = 0
    for i in starts:
        s_r = float(np.prod(1.0 + series[i - first_exec:i - first_exec + W6M]) - 1.0)
        b_r = float(np.prod(1.0 + ew[i - first_exec:i - first_exec + W6M]) - 1.0)
        beats += int(s_r > b_r)
    return round(beats / len(starts), 4), len(starts)


def ic_block(Fmat, panel):
    idx, members = panel["idx"], panel["members"]
    Fdf = pd.DataFrame(Fmat, index=idx, columns=members)
    f5 = pd.DataFrame(panel["fwd5"], index=idx, columns=members)
    f1 = pd.DataFrame(panel["fwd1"], index=idx, columns=members)
    s5 = ic_series(Fdf, f5)
    s1 = ic_series(Fdf, f1)
    if len(s5) < 30:
        return {"ic5_mean": None, "ic5_std": None, "ic5_ir": None,
                "ic5_n": int(len(s5)), "ic1_mean": None, "daily": (s5, s1)}
    mu, sd = float(s5.mean()), float(s5.std(ddof=1))
    return {"ic5_mean": _r(mu, 6), "ic5_std": _r(sd, 6),
            "ic5_ir": _r(mu / sd, 4) if sd > 0 else 0.0,
            "ic5_n": int(len(s5)), "ic1_mean": _r(float(s1.mean()), 6) if len(s1) else None,
            "daily": (s5, s1)}


def null_sleeves(panel, grid_pairs, k_nulls=K_NULLS, seed=None):
    """K same-mask monthly random sleeves (rng([seed, k]) substream law) +
    indicator factor matrices for the null |mean IC| band (monthly caliber).
    seed=None = module SEED_NULLS (P1 callers byte-stable); additive r649
    param lets P2 run its own frozen band [20570000, 20570060)."""
    s = SEED_NULLS if seed is None else int(seed)
    base = panel["base"]
    T, N = base.shape
    out = {}
    for k in range(k_nulls):
        rng = np.random.default_rng([s, k])
        picks = {}
        for g, e in grid_pairs:
            elig = np.flatnonzero(base[g])
            if len(elig) < TOP_K:
                picks[g] = None
                continue
            sel = rng.choice(elig, size=TOP_K, replace=False)
            picks[g] = sorted(int(x) for x in sel)

        def score_fn(g, _p=picks):
            sel = _p.get(g)
            if sel is None:
                return None
            row = np.full(N, np.nan)
            row[sel] = 1.0
            return row
        # indicator factor: selection constant within [g, next_g)
        Fk = np.full((T, N), np.nan)
        gs = [g for g, _ in grid_pairs]
        for j, g in enumerate(gs):
            sel = picks[g]
            if sel is None:
                continue
            g_next = gs[j + 1] if j + 1 < len(gs) else T
            for d in range(g, min(g_next, T)):
                elig = base[d]
                Fk[d][elig] = 0.0
                if sel:
                    Fk[d][sel] = 1.0
        out[k] = {"score_fn": score_fn, "Fmat": Fk}
    return out


# ---------------------------------------------------------------- D6

def _corr(a: pd.Series, b: pd.Series, min_overlap=D6_MIN_OVERLAP):
    j = pd.concat([a, b], axis=1, join="inner").dropna()
    if len(j) < min_overlap:
        return None, int(len(j))
    v = float(np.corrcoef(j.iloc[:, 0], j.iloc[:, 1])[0, 1])
    return round(v, 4), int(len(j))


def member_series():
    """REG6 daily return series via the ew6 canon (identical code path to the
    live.paper anchor gate; g2_slot_tail_p1 d6_block precedent)."""
    import ew6_portfolio as E
    from live.paper import load_core
    if E.PRICES_FULL is None:
        E.PRICES_FULL = load_core()
    rets, cutoffs = {}, {}
    for tid in REG6:
        r = E.member_run(tid)
        eq = pd.Series(r["eq"], index=pd.to_datetime(r["dates"]))
        rets[tid] = eq.pct_change().dropna()
        cutoffs[tid] = r.get("cutoff")
    return rets, cutoffs


# ---------------------------------------------------------------- family aggregation (leg v)

def family_verdicts(families, face_rows):
    """Enriched-subpool monthly-cadence adjudication (prereg sec.4 family
    line): 0 nominations = family's MONTHLY-cadence question answered
    negative (parent weekly verdicts UNAFFECTED -- new caliber, no
    reversal); >=1 = stage-2 shortlist face. Families with zero measured
    faces this run carry an explicit not-measured verdict (mini selftest
    runs must never emit adjudication claims)."""
    out = {}
    for fam, faces in families.items():
        faces = [f for f in faces if f in face_rows]
        if not faces:
            out[fam] = {"n_faces_measured": 0, "n_nominated": 0,
                        "nominated_faces": [],
                        "verdict": "not-measured-this-run (no adjudication)"}
            continue
        nom = sorted(f for f in faces
                     if face_rows[f].get("nomination", {}).get("nominated_stage2"))
        out[fam] = {
            "n_faces_measured": len(faces), "n_nominated": len(nom),
            "nominated_faces": nom,
            "verdict": ("monthly-cadence answered-negative (enriched subpool; "
                        "parent weekly verdicts unaffected)"
                        if not nom else
                        "monthly-cadence survivor (stage-2 shortlist face; "
                        "independent sec.9 freeze required)"),
        }
    return out


# ---------------------------------------------------------------- pipeline

def run_pipeline(panel, faces, k_nulls, d6=True, ledger=False,
                 families=None, class_carry=None, parent_ic=None):
    """Deterministic core: everything except final write. ledger=False ->
    trials_ledger block omitted (selftest mini-runs never touch the chain)."""
    t_start = time.time()
    facts = panel["facts"]
    idx, members, T = panel["idx"], panel["members"], panel["facts"]["n_days"]
    grid_pairs = monthly_grid(idx)
    faces_res = compute_faces(panel, faces)

    # leg (i): per-face IC + parent determinism cross-check (fail-closed)
    ic_res, face_failed, ic_drift = {}, [], []
    for f in faces:
        Fmat, valid, beyond = faces_res[f]
        if Fmat is None:
            face_failed.append(f)
            continue
        blk = ic_block(Fmat, panel)
        blk["vendor_beyond_base_ct"] = beyond
        ic_res[f] = blk
        if parent_ic is not None and f in parent_ic:
            pv = parent_ic[f]
            if pv is not None and blk["ic5_mean"] is not None:
                if abs(blk["ic5_mean"] - pv) > PARENT_IC_TOL:
                    ic_drift.append((f, blk["ic5_mean"], pv))

    # leg (ii)+(iii): sleeves (faces x2 cost faces + nulls both faces)
    sleeves = {}
    for f in faces:
        Fmat = faces_res[f][0]
        if Fmat is None:
            continue

        def score_fn(g, _F=Fmat):
            return _F[g]
        for cname, cost in COST_FACES.items():
            sleeves[(f, cname)] = blend_sleeve(score_fn, grid_pairs, panel["rets"], cost)
    nulls = null_sleeves(panel, grid_pairs, k_nulls) if k_nulls else {}
    null_ic, null_stats = {}, {}
    for k in sorted(nulls):
        nb = nulls[k]
        icb = ic_block(nb["Fmat"], panel)
        null_ic[k] = {"ic5_mean": icb["ic5_mean"], "ic5_n": icb["ic5_n"]}
        row = {}
        for cname, cost in COST_FACES.items():
            sl = blend_sleeve(nb["score_fn"], grid_pairs, panel["rets"], cost)
            if sl is None:
                row[cname] = None
                continue
            ew = ew48_window(panel["rets"], sl["first_exec"])
            br, nw = beat_rate(sl["series"], ew, sl["first_exec"], T)
            row[cname] = {"metrics": sleeve_metrics(sl["series"], idx, sl["first_exec"]),
                          "beat_rate": br, "n_windows": nw,
                          "turnover_total": _r(sl["turnover_total"], 4),
                          "n_rebal": sl["n_rebal"], "n_skip": sl["n_skip"]}
        null_stats[k] = row
    null_abs_means = [abs(v["ic5_mean"]) for v in null_ic.values()
                      if v["ic5_mean"] is not None]
    null_p95 = round(float(np.percentile(null_abs_means, 95)), 6) if null_abs_means else None
    null_br_x2 = [null_stats[k]["x2"]["beat_rate"] for k in null_stats
                  if null_stats[k].get("x2") and null_stats[k]["x2"]["beat_rate"] is not None]

    # per-face stats + beat windows vs EW48
    face_rows = {}
    for f in faces:
        if f in face_failed:
            continue
        cls = (class_carry or {}).get(f, "unknown")
        sl2 = sleeves[(f, "x2")]
        sl1 = sleeves[(f, "x1")]
        if sl2 is None or sl1 is None:
            face_rows[f] = {"class": cls,
                            "ic": {k: v for k, v in ic_res[f].items() if k != "daily"},
                            "sleeve": "insufficient-signal-days (no month with >=16 valid; honest)",
                            "nomination": {"nominated_stage2": False,
                                           "claim": "exploration only; NO registration, NO paper eligibility (stage-1 census variant)"}}
            continue
        ew2 = ew48_window(panel["rets"], sl2["first_exec"])
        br2, nw2 = beat_rate(sl2["series"], ew2, sl2["first_exec"], T)
        m2 = sleeve_metrics(sl2["series"], idx, sl2["first_exec"])
        m1 = sleeve_metrics(sl1["series"], idx, sl1["first_exec"])
        ew2_total = float(np.prod(1.0 + ew2) - 1.0)
        face_rows[f] = {
            "class": cls,
            "ic": {k: v for k, v in ic_res[f].items() if k != "daily"},
            "x1": {**m1, "beat_rate": beat_rate(sl1["series"], ew48_window(panel["rets"], sl1["first_exec"]), sl1["first_exec"], T)[0],
                   "turnover_total": _r(sl1["turnover_total"], 4), "n_rebal": sl1["n_rebal"]},
            "x2": {**m2, "beat_rate": br2, "n_windows": nw2,
                   "turnover_total": _r(sl2["turnover_total"], 4), "n_rebal": sl2["n_rebal"]},
            "x2_beats_ew48_full": bool(m2["total_ret"] is not None
                                       and m2["total_ret"] > _r(ew2_total, 6)),
            "ew48_total_ret": _r(ew2_total, 6),
        }

    # D6 leg (real member runs; skipped only in synthetic mini mode via flag)
    d6_out = {"reject_line": D6_REJECT, "members": list(REG6), "faces": {}}
    if d6:
        mrets, mcutoffs = member_series()
        fseries = {}
        for f in face_rows:
            sl = sleeves[(f, "x1")]
            if sl is None:
                continue
            fseries[f] = pd.Series(sl["series"],
                                   index=idx[sl["first_exec"]:sl["first_exec"] + len(sl["series"])])
        per_face_members, inbatch = {}, {}
        fnames = sorted(face_rows)
        for f in fnames:
            pm = {}
            for tid in REG6:
                v, ov = _corr(fseries[f], mrets[tid])
                pm[tid] = {"corr": v, "overlap_days": ov}
            finite = {t: v["corr"] for t, v in pm.items() if v["corr"] is not None}
            argmax = max(finite, key=lambda t: abs(finite[t])) if finite else None
            per_face_members[f] = {"per_member": pm, "max_abs_corr": abs(finite[argmax]) if argmax else None,
                                   "argmax_member": argmax,
                                   "reject": bool(argmax and abs(finite[argmax]) >= D6_REJECT)}
        for i, a in enumerate(fnames):
            for b in fnames[i + 1:]:
                v, ov = _corr(fseries[a], fseries[b])
                if v is not None:
                    inband = inbatch.setdefault(str(round(abs(v), 4)), [])
                    inband.append("%s|%s" % (a, b))
        d6_out["faces"] = per_face_members
        d6_out["member_cutoffs"] = mcutoffs
        d6_out["inbatch_pairs_ge_0p7"] = {k: v for k, v in inbatch.items()
                                          if float(k) >= D6_REJECT}
        d6_out["inbatch_note"] = "keys=|corr| rounded 4dp; pairs list; census stage no-disposal (stage-2 family dedup consumes list)"
        for f in fnames:
            face_rows[f]["d6_max_abs_corr"] = per_face_members[f]["max_abs_corr"]
            face_rows[f]["d6_reject"] = per_face_members[f]["reject"]

    # regime segmentation (510300 t22 3-way proxy; disclosure only)
    if "510300" in members:
        c510300 = pd.Series(panel["F"]["close"][:, members.index("510300")], index=idx)
        labels = np.asarray(regime_proxy(c510300), dtype=object)
        for f, row in face_rows.items():
            sl = sleeves[(f, "x2")]
            if sl is None:
                continue
            ew = ew48_window(panel["rets"], sl["first_exec"])
            seg = {}
            for lab in ("bull", "chop", "bear", "na"):
                dpos = np.flatnonzero(labels[sl["first_exec"]:] == lab) + sl["first_exec"]
                if len(dpos) < 5:
                    seg[lab] = {"n_days": int(len(dpos))}
                    continue
                rel = dpos - sl["first_exec"]
                s_cum = float(np.prod(1.0 + sl["series"][rel]) - 1.0)
                e_cum = float(np.prod(1.0 + ew[rel]) - 1.0)
                seg[lab] = {"n_days": int(len(dpos)), "sleeve_cum": _r(s_cum, 4),
                            "ew48_cum": _r(e_cum, 4), "beat": bool(s_cum > e_cum)}
            row["regime_segments"] = seg

    # nomination (sec.4 monthly-caliber three-condition line + BAN + D6)
    for f, row in face_rows.items():
        if "x2" not in row:
            continue
        c1 = row["ic"]["ic5_mean"] is not None and null_p95 is not None \
            and abs(row["ic"]["ic5_mean"]) > null_p95
        c2 = row["x2_beats_ew48_full"]
        c3 = row["x2"]["beat_rate"] is not None and row["x2"]["beat_rate"] >= 0.60
        banned = row["class"] == "price_banned"
        d6_block = bool(row.get("d6_reject"))
        row["nomination"] = {
            "cond1_ic_gt_null_p95_monthly": bool(c1), "cond2_x2_beats_ew48": bool(c2),
            "cond3_beat_rate_ge_060": bool(c3), "ban_blocked": banned,
            "d6_blocked": d6_block,
            "nominated_stage2": bool(c1 and c2 and c3 and not banned and not d6_block),
            "claim": "exploration only; NO registration, NO paper eligibility (stage-1 census variant)",
        }

    fam_verdicts = family_verdicts(families, face_rows) if families else None

    payload = {
        "batch": BATCH, "ticket": TICKET, "prereg": PREREG_REL,
        "stage": "stage-1 census variant (monthly-translation decomposition; exploration; zero registration claims)",
        "evidence_cutoff": CUTOFF,
        "science_gates": {"cutoff_meta": sg.cutoff_meta(CUTOFF)},
        "panel": {
            "members_sha16": INSERVICE_SHA16, "n_members": facts["n_members"],
            "n_days": facts["n_days"], "window": "%s..%s" % (facts["union_first"], facts["union_last"]),
            "mask_fraction": facts["mask_fraction"],
            "min_valid_per_member": facts["min_valid_per_member"],
            "grid": {"caliber": "monthly (first trading day of each calendar month)",
                     "n_signal_days": len(grid_pairs),
                     "first_signal": str(idx[grid_pairs[0][0]].date()) if grid_pairs else None},
            "ew48_definition": "fixed 1/48 weights, NaN->0 accrual, costless B&H (disclosed)",
            "cost_faces_bp_per_side": {"x1": round(COST_FACES["x1"] * 1e4, 3),
                                       "x2": round(COST_FACES["x2"] * 1e4, 3)},
            "vendor_head": vendor_head(),
        },
        "ban_rule": "sec.0.5 inheritance: class carried AS-IS from parent censuses (frozen adjudication, r644 E22 canon); price_banned faces measured, never nominatable",
        "audit": {"network": "zero", "deterministic": True, "device": "cpu (torch)",
                  "engine": "none (census variant face)", "budget_cap_s": BUDGET_CAP_S,
                  "exit_axis": "hold-to-end monthly rank rotation (sec.0.6 census approximation, no price-type exit)",
                  "parent_ic_drift": ic_drift},
        "roster": {"faces": sorted(faces), "n_faces": len(faces),
                   "roster_freeze_sha16": ROSTER_SHA16,
                   "class_inheritance": "parent census classes carried as-is (24 volume_price / 20 price_other / 3 price_banned expected)",
                   "failed_faces": sorted(face_failed)},
        "family_verdicts": fam_verdicts,
        "nulls": {"k": len(nulls), "seed": SEED_NULLS, "substream": "rng([seed, k])",
                  "abs_mean_ic": sorted(_r(x, 6) for x in null_abs_means),
                  "p95_abs_mean_ic": null_p95,
                  "beat_rate_x2": sorted(x for x in null_br_x2),
                  "beat_rate_x2_mean": _r(float(np.mean(null_br_x2)), 4) if null_br_x2 else None,
                  "indicator_ic_note": "null factor = monthly random selection indicator (1/0 within frozen base mask, held constant within month); mean daily rank-IC vs fwd-5d; se inflated by monthly persistence (~81 effective months, wider than weekly ~345; honest)"},
        "faces": face_rows,
        "d6": {"reject_line": D6_REJECT,
               "max_abs_corr_by_face": {f: face_rows[f].get("d6_max_abs_corr") for f in sorted(face_rows)} if d6 else None,
               "inbatch_pairs_ge_0p7_count": len(d6_out.get("inbatch_pairs_ge_0p7", {})) if d6 else None,
               "note": "full numeric face in results/g2_slot_mon_p1/d6_numeric.json (same write)"},
    }
    if ledger:
        payload["trials_ledger"] = sg.append_ledger(
            batch_name=BATCH, batch_trials=len(faces) + len(nulls),
            file_name="results/g2_slot_mon_p1/g2_slot_mon_p1_census.json",
            evidence_cutoff=CUTOFF,
            note="47 enriched-roster faces (18 old + 2 stock + 27 tail cond1 passers; probe roster sha16 7ce1e81d019eba3d) + 20 same-mask monthly random nulls (monthly-translation cost-vs-horizon decomposition census variant; parent weekly verdicts unaffected)")
    return payload, d6_out, {"ic": {f: ic_res[f]["daily"] for f in ic_res},
                             "elapsed": round(time.time() - t_start, 1),
                             "ic_drift": ic_drift}


# ---------------------------------------------------------------- run / selftest

def cmd_run():
    if os.path.exists(OUT_JSON):
        _fail("refuse-if-exists: %s already present (single-shot rerun ban; "
              "engineering-fix rerun needs dual-run evidence + fresh prereg note)" % OUT_JSON)
    t0 = time.time()
    probe, roster, sha, faces, families = roster_faces()
    class_carry = {f: roster[f]["class"] for f in faces}
    parent_ic = {f: roster[f]["parent_ic5_mean"] for f in faces}
    panel = build_panel()
    ok, gates, fails, _ = run_gates(panel["facts"])
    print("[g2slotmonp1] gates: %s %s" % ("PASS" if ok else "FAIL", gates), flush=True)
    if not ok:
        _fail("gates failed: %s" % fails)
    if time.time() - t0 > 240:
        _fail("over-budget abort (panel+gates > 240s); nothing finalized", code=3)

    payload, d6_full, extras = run_pipeline(panel, faces, K_NULLS, d6=True,
                                             ledger=True, families=families,
                                             class_carry=class_carry,
                                             parent_ic=parent_ic)
    elapsed = extras["elapsed"]
    if elapsed > BUDGET_CAP_S:
        _fail("over-budget abort (%.1fs > %ds cap); nothing finalized" % (elapsed, BUDGET_CAP_S), code=3)
    if extras["ic_drift"]:
        _fail("parent-IC determinism drift (mechanical fault; fail-closed): %s"
              % extras["ic_drift"][:5])
    if len(payload["faces"]) + len(payload["roster"]["failed_faces"]) != N_BURN_EXPECT:
        _fail("F1 face count: rows %d + failed %d != %d" %
              (len(payload["faces"]), len(payload["roster"]["failed_faces"]), N_BURN_EXPECT))
    fv = payload["family_verdicts"]
    if sorted(fv.keys()) != sorted(FAMILIES):
        _fail("F2 family aggregation keys mismatch: %s" % sorted(fv.keys()))
    if any("not-measured" in v["verdict"] for v in fv.values()):
        _fail("F2b real run must adjudicate every family (found not-measured)")
    if sum(v["n_faces_measured"] for v in fv.values()) != len(payload["faces"]):
        _fail("F3 family aggregation face-count mismatch")
    gp = payload["panel"]["grid"]["n_signal_days"]
    if not (79 <= gp <= 83):
        _fail("F4 monthly grid count %d outside 81+/-2" % gp)

    os.makedirs(OUT_DIR, exist_ok=True)
    d6_full_write = {k: v for k, v in d6_full.items()}
    d6_full_write["batch"] = BATCH
    d6_full_write["evidence_cutoff"] = CUTOFF
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    with open(D6_JSON, "w", encoding="utf-8") as fh:
        json.dump(d6_full_write, fh, ensure_ascii=False, indent=1)

    # IC artifacts: per-face summary CSV + daily long-format CSV
    with open(IC_CSV, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("face,family,class,ic5_mean,ic5_std,ic5_ir,ic5_n,ic1_mean,x1_ann,x2_ann,x2_beat_rate,turnover_total,n_rebal,nominated\n")
        for f in sorted(payload["faces"]):
            r = payload["faces"][f]
            ic = r["ic"]
            fam = roster[f]["family"]
            if "x2" not in r:
                fh.write("%s,%s,%s,%s,%s,%s,%d,%s,,,,,,%d\n" % (
                    f, fam, r["class"], ic["ic5_mean"], ic["ic5_std"], ic["ic5_ir"], ic["ic5_n"],
                    ic["ic1_mean"], int(r["nomination"]["nominated_stage2"])))
                continue
            fh.write("%s,%s,%s,%s,%s,%s,%d,%s,%s,%s,%s,%s,%d,%d\n" % (
                f, fam, r["class"], ic["ic5_mean"], ic["ic5_std"], ic["ic5_ir"], ic["ic5_n"],
                ic["ic1_mean"], r["x1"]["ann"], r["x2"]["ann"], r["x2"]["beat_rate"],
                r["x2"]["turnover_total"], r["x2"]["n_rebal"],
                int(r["nomination"]["nominated_stage2"])))
    with open(IC_DAILY_CSV, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("face,date,ic5\n")
        for f in sorted(extras["ic"]):
            s5 = extras["ic"][f][0]
            for d, v in s5.items():
                fh.write("%s,%s,%.6f\n" % (f, d.date(), float(v)))

    # gate_attrition entry (append-only; r248 law)
    led = payload.get("trials_ledger", {})
    att = json.load(open(ATTR_JSON, encoding="utf-8-sig"))
    nom = [f for f in payload["faces"] if payload["faces"][f]["nomination"]["nominated_stage2"]]
    classes = {}
    for f in payload["faces"]:
        classes[payload["faces"][f]["class"]] = classes.get(payload["faces"][f]["class"], 0) + 1
    att["entries"].append({
        "batch": BATCH, "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "kind": "measurement",
        "cells_ledger_delta": led.get("batch_trials", 0),
        "ledger_total_after": led.get("total"),
        "gates": {
            "nomination_line": "monthly caliber: ic5|mean|>monthly-null p95 AND x2 full>EW48 AND x2 beat_rate>=0.60 AND not BAN-inherited AND D6<0.7 (census variant, stage-2 shortlist only)",
            "classes": classes, "nominated": len(nom), "nominated_faces": sorted(nom),
            "null_p95_abs_mean_ic": payload["nulls"]["p95_abs_mean_ic"],
            "null_beat_rate_x2_mean": payload["nulls"]["beat_rate_x2_mean"],
            "failed_faces": payload["roster"]["failed_faces"],
            "family_verdicts": {k: v["verdict"] for k, v in fv.items()},
        },
        "budget_elapsed_s": elapsed,
        "note": "stage-1 census variant (monthly-translation cost-vs-horizon decomposition on 47/126 enriched roster); zero registration claims; parent weekly verdicts unaffected; stage-2 judge face = separate freeze",
    })
    with open(ATTR_JSON, "w", encoding="utf-8") as fh:
        json.dump(att, fh, ensure_ascii=False, indent=1)

    print("[g2slotmonp1] census done: faces=%d nulls=%d months=%d elapsed=%.1fs" %
          (len(payload["faces"]), payload["nulls"]["k"], gp, elapsed), flush=True)
    print("[g2slotmonp1] nominated_stage2=%d %s" % (len(nom), sorted(nom)), flush=True)
    print("[g2slotmonp1] family verdicts: %s" %
          {k: v["n_nominated"] for k, v in fv.items()}, flush=True)
    print("[g2slotmonp1] null p95|meanIC|=%s null beat_x2 mean=%s" %
          (payload["nulls"]["p95_abs_mean_ic"], payload["nulls"]["beat_rate_x2_mean"]), flush=True)
    print("[g2slotmonp1] ledger total=%s" % led.get("total"), flush=True)
    print("[g2slotmonp1] products: %s | %s | %s | %s" %
          (OUT_JSON, D6_JSON, IC_CSV, IC_DAILY_CSV), flush=True)
    return 0


def cmd_selftest():
    fails = []
    t0 = time.time()
    # L1 roster sha identity (47 burn faces, 18/2/27 families)
    probe, roster, sha, faces, families = roster_faces()
    l1 = (sha.startswith(ROSTER_SHA16) and len(faces) == N_BURN_EXPECT
          and len(families["old"]) == 18 and len(families["stock"]) == 2
          and len(families["tail"]) == 27)
    print("L1 roster sha + 47/18-2-27 counts: %s" % ("PASS" if l1 else "FAIL"))
    if not l1:
        fails.append("L1")

    # L2+L3 real panel: cutoff truncation + mask gate
    panel = build_panel()
    f = panel["facts"]
    l2 = f["union_last"] == CUTOFF and f["union_first"] == PANEL_START
    l3 = (f["n_members"] == 48 and not f["bad_columns_members"]
          and not f["dup_date_members"] and f["min_valid_per_member"] >= 100
          and 0.90 <= f["mask_fraction"] <= 0.999)
    print("L2 cutoff truncation (%s..%s): %s" % (f["union_first"], f["union_last"], "PASS" if l2 else "FAIL"))
    print("L3 mask gate (48 members, mask_frac %.4f, min_valid %d): %s" %
          (f["mask_fraction"], f["min_valid_per_member"], "PASS" if l3 else "FAIL"))
    if not l2:
        fails.append("L2")
    if not l3:
        fails.append("L3")

    # L4 monthly grid count (81 +/- 2, prereg sec.6)
    gp = monthly_grid(panel["idx"])
    l4 = 79 <= len(gp) <= 83 and gp[0][1] == gp[0][0] + 1
    print("L4 monthly grid count=%d (81+/-2): %s" % (len(gp), "PASS" if l4 else "FAIL"))
    if not l4:
        fails.append("L4")

    # L5 seed band disjoint
    own = sg.SEED_REGISTRY.get("g2_slot_mon_p1_nulls")
    overlap = []
    for k, v in sg.SEED_REGISTRY.items():
        if k == "g2_slot_mon_p1_nulls":
            continue
        try:
            iv = int(v)
        except (TypeError, ValueError):
            continue
        if SEED_NULLS <= iv < SEED_NULLS + K_NULLS:
            overlap.append(k)
    l5 = own == SEED_NULLS and not overlap
    print("L5 seed registered=%s band-disjoint=%s: %s" %
          (own, not overlap, "PASS" if l5 else "FAIL"))
    if not l5:
        fails.append("L5")

    # L6 cost single-source + vendor head
    l6 = abs(COST_X1 - COST_X1_EXPECT) < 1e-12 and vendor_head() == ANCHOR_HEAD
    print("L6 COST_X1 single-source + vendor HEAD anchor: %s" % ("PASS" if l6 else "FAIL"))
    if not l6:
        fails.append("L6")

    # L7 deterministic double-run byte identity (mini-pipeline, real panel;
    # one face per family: first sorted face of old/stock/tail)
    mini_faces = [sorted(families[fam])[0] for fam in FAMILIES]
    class_carry = {x: roster[x]["class"] for x in mini_faces}
    parent_ic = {x: roster[x]["parent_ic5_mean"] for x in mini_faces}
    p1, _, e1 = run_pipeline(panel, mini_faces, 2, d6=True, ledger=False,
                             families=families, class_carry=class_carry,
                             parent_ic=parent_ic)
    p2, _, e2 = run_pipeline(panel, mini_faces, 2, d6=True, ledger=False,
                             families=families, class_carry=class_carry,
                             parent_ic=parent_ic)
    b1 = json.dumps(p1, ensure_ascii=False, sort_keys=False)
    b2 = json.dumps(p2, ensure_ascii=False, sort_keys=False)
    l7 = b1 == b2 and len(p1["faces"]) == 3 and p1["nulls"]["k"] == 2
    print("L7 double-run byte identity + counts (3 faces/2 nulls): %s" %
          ("PASS" if l7 else "FAIL"))
    if not l7:
        fails.append("L7")

    # L8 parent-IC determinism cross-check (mini faces vs parent census)
    l8 = (not e1["ic_drift"] and not e2["ic_drift"]
          and all(abs(p1["faces"][x]["ic"]["ic5_mean"] - parent_ic[x]) <= PARENT_IC_TOL
                  for x in mini_faces
                  if p1["faces"][x]["ic"]["ic5_mean"] is not None
                  and parent_ic[x] is not None))
    print("L8 parent-IC determinism (mini %s): %s" %
          (mini_faces, "PASS" if l8 else "FAIL"))
    if not l8:
        fails.append("L8")

    # L9 family aggregation leg (mini roster slice)
    fv1, fv2 = p1["family_verdicts"], p2["family_verdicts"]
    mini_fams = {FAMILIES[0], FAMILIES[1], FAMILIES[2]}  # one face each
    l9 = (fv1 is not None and fv1 == fv2
          and set(fv1.keys()) == set(FAMILIES)
          and sum(v["n_faces_measured"] for v in fv1.values()) == 3
          and all(v["n_faces_measured"] == 1 for v in fv1.values())
          and all("not-measured" not in v["verdict"] for v in fv1.values()))
    print("L9 family aggregation (all 3 families measured 1 face, deterministic): %s" %
          ("PASS" if l9 else "FAIL"))
    if not l9:
        fails.append("L9")

    print("selftest: %s fails=%s elapsed=%.1fs" %
          ("PASS" if not fails else "FAIL", fails, time.time() - t0))
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "selftest"])
    a = ap.parse_args()
    if a.cmd == "run":
        return cmd_run()
    return cmd_selftest()


if __name__ == "__main__":
    sys.exit(main())
