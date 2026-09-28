"""ETF_OPS_BP1 runner -- 宽基回调低吸链全网格回测批 (T-103 s2).

Laws frozen in research/etf_ops/ETF_OPS_BP1_PREREG.md (R396 freeze commit,
SEED_REGISTRY['etf_ops_bp1']=20294000 registered same commit, R250 law; band
20294000..20294029 rg-scan clean). Freeze precedes runner build precedes ANY
burn. Run-products may only backfill prereg s7; criteria are never re-derived
by hand (O-2250 single-source: every gate line comes from science_gates).

  members five-member two-tier frozen universe (O-1555): 510050 / 510300 /
          510500 / 512100 / 588000 (20cm tier). G-ANCHOR-FACE four-tuple per
          member (path / loader / first-date / warmup) + row census + last-bar
          == evidence_cutoff 2026-09-22 -- any face mismatch = fail-closed
          refuse (exit 2), reported as face-mismatch not data-rot
          (INCIDENT-20260928 law). D2 lockbox: rows after cutoff never enter.
  rules  S1 chain-design s2 table verbatim: trend gate close > MA200
          (rolling 200, min_periods=200, incl. current day); trigger close <=
          max(close,20d)*(1-D), max20d min_periods=20; both gates same day ->
          T+1 next-open buy ONE unit (single position, no pyramiding);
          TP1 close >= entry*(1+P1) -> T+1 open sell 50%; TP2 close >=
          entry*(1+P2) -> T+1 open clear; hard SL close <= entry*0.92; trend
          SL close < MA200 -> T+1 open clear. Same-close-day exit priority
          mirrors the engine/exit_rules.py canon (reversal > stop > profit):
          trend_sl > hard_sl > tp2 > tp1 (documented frozen choice).
          Re-entry: next trigger day strictly > exit day (同日不重入
          conservative reading: the close-day trigger on the round-close day
          itself is suppressed; documented frozen choice).
  limit  honest accounting (qfq face): one-word board day = h==l & o==h;
          limit-up if o/pc-1 >= tier-0.002, limit-down if o/pc-1 <=
          -(tier-0.002); tier=0.10 (0.20 for 588000). Entry-day one-word
          limit-up -> blocked_entry (round voided, NOT in win-rate
          denominator; signal consumed, wait resumes next day). Exit-day
          one-word limit-down -> blocked_exit, execution rolls to the next
          tradable open (committed exit, no signal re-evaluation).
  guard  fund event guard r239 frozen law: day |r1| > 10.5% (588000: 20.5%)
          AND same-day five-member universe median |r1| < 3% -> member-day
          isolated, no trigger (median over members with finite r1 that day;
          single-member era median==own -> guard structurally inert, honest).
  costs  V1 legacy 13.041bp/side single source = alloc_backtest.V1_FLAT_SIDE;
          dual track base x1 + x2 stress face via the CostPatch multiplier
          law (x2 = V1_FLAT_SIDE*2.0, never re-derived). Multiplicative both
          legs: leg net = px_exit*(1-c_out) / (px_entry*(1+c_in)) - 1.
          JUDGED FACE = x2 (conservative stress face, cn_kline / rev_osc
          judged-face precedent); x1 = disclosure face. Documented frozen
          choice under prereg s3 dual-track wording.
  rounds win = round net pnl (both-side costs, both legs at own fills) > 0.
          Round pnl = sum frac_i * leg_net_i (TP1 leg 0.5, remainder 0.5;
          single-leg exits frac 1.0). Open-at-panel-end rounds are NOT
          completed rounds: excluded from win denominator, disclosed as
          open_at_end with unrealized mark-to-last (never in chain faces).
  nulls  K=200 same-mask random-entry null per member-cell: mask = the
          cell's own both-gate + guard-excluded + warmup-finite trigger
          days; each draw samples n_real_rounds days uniformly WITHOUT
          replacement (rng = np.random.default_rng([20294000, cell_idx]),
          cell_idx = member_idx*6 + grid_idx < 30; K sequential draws per
          stream), sorted ascending, then the SAME sequential round state
          machine (no-reentry window / blocked_entry voids / blocked_exit
          rolls) -- draws landing inside an active round are skipped and the
          effective count disclosed. Null faces: per-draw win rate + E[pnl]
          at BOTH cost faces. Primary gate = real win rate > null p95
          (one-sided); E[pnl] same gate parallel-disclosed (prereg s4).
  bucket  chain daily series per cell per face = WILD-S1 frozen reuse:
          each leg net booked evenly across its holding days entry_idx+1 ..
          exit_idx (span = exit_idx-entry_idx), fraction-weighted; cash days
          0. Sharpe/gates/virtual-starts consume this series.
  gates  win-rate primary (vs null p95) + G1'v2 (science_gates.g1_prime_v2,
          batch_cells=30, pool='core48' -- five members ARE core48 members,
          null_pool = default collector, documented choice) + DSR
          (deflated_sharpe_ratio on the raw x2 series, n_trials=n_eff) +
          family PBO (screening/pbo cscv_pbo CSCV-8 over the 30-cell x2
          matrix aligned on the common calendar inner join -- pre-588000
          history excluded from the PBO matrix face only, disclosed) +
          g2_registration_v2. Ledger single-count: head read BEFORE append,
          n_eff_override=head_base+30, append_ledger(prev_total=head_base)
          (r253 redo-guard law, cn_kline precedent).
  regime disclosure-only axes (never switch gates): T-74 L2 route states via
          the IMPORTED frozen regime_deep_replay v3 layer (YELLOW->CHOP
          collapse at join, L2 routing-table v1.0 mapping) + T-89/T-22
          bear/chop/bull segmenter face (bear close<MA200; chop close>=MA200
          & MA200 <= MA200[-20]; bull close>=MA200 & rising; na warmup),
          tagged at round entry. 禁全天候宣称.
  starts  T-22 virtual timepoints {6m=126, 12m=252, 24m=504}td windows x
          {base,x2} faces: every feasible start t0 in [eval_start, n-W),
          chain cum (booked-evenly face, arithmetic) vs same-window
          buy-hold cum; beat = chain > passive; 588000 start count narrows
          honestly with the data face (prereg s0).
  d6     reject face = max|corr| vs the six registered trader sleeves
          (REG6, ew6 canon member_run, identical code path to the
          live.paper anchor gate, cn_rev_tilt precedent); same-batch and
          null families = disclosure faces; max|corr| >= 0.7 -> cell
          rejected (prereg s1).

Products (prereg s6): results/etf_ops/bp1_grid.json (top evidence_cutoff +
science_gates.cutoff_meta mandatory) + results/etf_ops/bp1_rounds_<code>.csv
per-member round streams + results/etf_ops/bp1_nulls.json null distribution
file + shard checkpoints results/etf_ops/bp1_shard_<code>.json +
bp1_series/<code>_<cellidx>_<face>.npy daily streams. Deterministic: no
wall-clock inside any product; re-run byte-identical.

Usage:
  python scripts/etf_ops_bp1.py run --shard 510300     (one member burn)
  python scripts/etf_ops_bp1.py run --shard all         (five sequential)
  python scripts/etf_ops_bp1.py finalize                (harvest + gates)
  python scripts/etf_ops_bp1.py status
  python scripts/etf_ops_bp1.py selftest                (hermetic, offline)

Exit contract: 0 ok/no-op; 2 fail-closed gate refusal (anchor drift, shard
grammar mismatch, missing dependency); 3 RAM floor (three-sample, r354
family calibrated to this light five-member batch, disclosed).
"""
import argparse
import hashlib
import json
import os
import sys
import tempfile

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import science_gates as SG                      # shared gate library (O-2250)
from alloc_backtest import V1_FLAT_SIDE          # V1 13.041bp single source

OUT_DIR = os.path.join(ROOT, "results", "etf_ops")
SER_DIR = os.path.join(OUT_DIR, "bp1_series")
OUT_JSON = os.path.join(OUT_DIR, "bp1_grid.json")
OUT_NULLS = os.path.join(OUT_DIR, "bp1_nulls.json")
ATT_JSON = os.path.join(ROOT, "results", "gate_attrition.json")

EVIDENCE_CUTOFF = "2026-09-22"
BATCH_NAME = "ETF_OPS_BP1"
BATCH_CELLS = 30
K_NULLS = 200
PBP = 252
D6_REJECT = 0.7
LIMIT_TOL = 0.002
HARD_SL_MULT = 0.92
GUARD_THR = 0.105
GUARD_THR_20CM = 0.205
UNIVERSE_MED_THR = 0.03
RAM_FLOOR_GB = 2.0                # light batch: five small CSVs (r354 family)
WINDOWS = {"6m": 126, "12m": 252, "24m": 504}
OOS_FROM = "2025-01-01"

# frozen member order + G-ANCHOR-FACE four-tuple (prereg s2 table verbatim)
MEMBERS = ["510050", "510300", "510500", "512100", "588000"]
ANCHORS = {
    "510050": {"path": "data/daily/sh510050.csv", "first": "2005-02-23", "rows": 5248},
    "510300": {"path": "data/daily/sh510300.csv", "first": "2012-05-28", "rows": 3483},
    "510500": {"path": "data/daily/sh510500.csv", "first": "2013-03-15", "rows": 3286},
    "512100": {"path": "data/daily/sh512100.csv", "first": "2016-11-04", "rows": 2402},
    "588000": {"path": "data/daily/sh588000.csv", "first": "2020-11-16", "rows": 1422},
}
TIER_20CM = {"588000"}
# frozen grid order (prereg s0: D-major over {(5,10),(6,12),(8,15)})
GRID = [
    {"D": 0.04, "P1": 0.05, "P2": 0.10},
    {"D": 0.04, "P1": 0.06, "P2": 0.12},
    {"D": 0.04, "P1": 0.08, "P2": 0.15},
    {"D": 0.05, "P1": 0.05, "P2": 0.10},
    {"D": 0.05, "P1": 0.06, "P2": 0.12},
    {"D": 0.05, "P1": 0.08, "P2": 0.15},
]
COST_X1 = float(V1_FLAT_SIDE)          # 13.041bp/side (V1 single source)
COST_X2 = COST_X1 * 2.0                # CostPatch multiplier law (x2 face)
SEED = None                            # filled from SG.SEED_REGISTRY at run

GRAMMAR = BATCH_NAME + "|v1|cutoff=" + EVIDENCE_CUTOFF + \
    "|D{4,5}xTP{(5,10),(6,12),(8,15)}|MA200,minp200|max20,minp20|SL0.92|" \
    "reentry>exit_day|prio trend>hard>tp2>tp1|nulls same-mask K" + str(K_NULLS) + \
    "|judged=x2|V1FLAT=" + format(COST_X1, ".7f")


def _sha16(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


GRAMMAR_SHA16 = _sha16(GRAMMAR)


def _free_ram_gb():
    try:
        import psutil
        return psutil.virtual_memory().available / 1e9
    except Exception:
        return RAM_FLOOR_GB + 1.0        # psutil absent -> guard off (disclosed)


def gate_refuse(msg):
    print(f"GATE-REFUSE(exit2): {msg}")
    return 2


def _atomic_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    os.replace(tmp, path)


def _atomic_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, path)


# ------------------------------------------------------------------ panel
def load_member(code, data_dir=None, anchors=None, cutoff=None):
    """G-ANCHOR-FACE fail-closed loader. Returns (arrays dict, face dict) or
    (None, refuse_reason). anchors/cutoff/data_dir injectable for selftest."""
    anchors = anchors or ANCHORS
    cutoff = cutoff or EVIDENCE_CUTOFF
    base = data_dir or ROOT
    a = anchors[code]
    path = os.path.join(base, a["path"])
    if not os.path.exists(path):
        return None, f"anchor path absent: {a['path']}"
    df = pd.read_csv(path)                      # ② pd.read_csv raw 直读截断
    need = ["date", "open", "high", "low", "close"]
    if any(k not in df.columns for k in need):
        return None, f"column face drift: {list(df.columns)}"
    dts = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d").tolist()
    if len(dts) > 1 and dts[0] > dts[-1]:
        return None, "date order reversed"
    cut_rows = int(np.searchsorted(np.array(dts), cutoff, side="right"))
    if len(dts) != cut_rows:
        # D2 lockbox: rows after cutoff exist on disk -> truncate, disclose
        df = df.iloc[:cut_rows]
        dts = dts[:cut_rows]
    if len(dts) != a["rows"]:
        return None, (f"row census drift: {len(dts)} != anchor {a['rows']} "
                      f"({code} face mismatch)")
    if dts[0] != a["first"]:
        return None, f"first-date drift: {dts[0]} != anchor {a['first']}"
    if dts[-1] != cutoff:
        return None, f"last-bar drift: {dts[-1]} != cutoff {cutoff}"
    o = df["open"].to_numpy(float)
    h = df["high"].to_numpy(float)
    l = df["low"].to_numpy(float)
    c = df["close"].to_numpy(float)
    if not (np.isfinite(o).all() and np.isfinite(h).all()
            and np.isfinite(l).all() and np.isfinite(c).all()):
        return None, "OHLC NaN face (anchor gate 3)"
    if any(dts[i] >= dts[i + 1] for i in range(len(dts) - 1)):
        return None, "date not strictly increasing / duplicated"
    pc = np.concatenate([[np.nan], c[:-1]])
    ma200 = pd.Series(c).rolling(200, min_periods=200).mean().to_numpy()
    max20 = pd.Series(c).rolling(20, min_periods=20).max().to_numpy()
    with np.errstate(invalid="ignore"):
        r1 = c / pc - 1.0
    face = {"path": a["path"], "rows": len(dts), "first": dts[0],
            "last": dts[-1], "loader": "pd.read_csv raw truncate"}
    m = {"code": code, "dates": dts, "o": o, "h": h, "l": l, "c": c,
         "pc": pc, "ma200": ma200, "max20": max20, "r1": r1, "face": face,
         "n": len(dts)}
    return m, None


def universe_median_abs_r1(members, cutoff=None):
    """Per-date median |r1| over members with finite r1 (prereg guard face).
    Single-member era: median == own -> guard structurally inert (honest)."""
    by_date = {}
    for m in members:
        for d, r in zip(m["dates"], m["r1"]):
            if np.isfinite(r):
                by_date.setdefault(d, []).append(abs(float(r)))
    return {d: float(np.median(v)) for d, v in by_date.items()}


def member_arrays(m, med_abs, thr):
    """Per-member derived masks (guard / limit boards / segments)."""
    tier = 0.20 if m["code"] in TIER_20CM else 0.10
    n = m["n"]
    o, h, l, pc = m["o"], m["h"], m["l"], m["pc"]
    with np.errstate(invalid="ignore"):
        one_word = (h == l) & (o == h)
        up_ratio = o / pc - 1.0
    limit_up = one_word & np.isfinite(up_ratio) & (up_ratio >= tier - LIMIT_TOL)
    limit_dn = one_word & np.isfinite(up_ratio) & (up_ratio <= -(tier - LIMIT_TOL))
    isolated = np.zeros(n, dtype=bool)
    for i, d in enumerate(m["dates"]):
        r = m["r1"][i]
        med = med_abs.get(d)
        if np.isfinite(r) and med is not None \
                and abs(float(r)) > thr and med < UNIVERSE_MED_THR:
            isolated[i] = True
    # T-89/T-22 segmenter face (frozen): bear/chop/bull, na warmup
    ma = m["ma200"]
    ma20ago = np.full(n, np.nan)
    if n > 20:
        ma20ago[20:] = ma[:-20]
    with np.errstate(invalid="ignore"):
        ok = np.isfinite(ma) & np.isfinite(ma20ago)
        bear = ok & (m["c"] < ma)
        chop = ok & (m["c"] >= ma) & (ma <= ma20ago)
        bull = ok & (m["c"] >= ma) & (ma > ma20ago)
    seg = np.full(n, "na", dtype=object)
    seg[bear] = "bear"; seg[chop] = "chop"; seg[bull] = "bull"
    return {"tier": tier, "limit_up": limit_up, "limit_dn": limit_dn,
            "isolated": isolated, "seg": seg}


def cell_mask(m, aux, D):
    """Both-gate trigger-day mask (trend + drawdown, warmup finite, guard
    excluded; last-day signals dropped -- no T+1 to execute on)."""
    with np.errstate(invalid="ignore"):
        trend = np.isfinite(m["ma200"]) & (m["c"] > m["ma200"])
        trig = np.isfinite(m["max20"]) & (m["c"] <= m["max20"] * (1.0 - D))
    mask = trend & trig & (~aux["isolated"])
    if m["n"] > 0:
        mask[-1] = False
    return mask


# ------------------------------------------------------------------ engine
def _first_true(mask, from_idx):
    idx = np.flatnonzero(mask[from_idx:])
    return int(from_idx + idx[0]) if len(idx) else None


def simulate_rounds(m, aux, cand_days, grid, cost_x1, cost_x2):
    """Sequential round state machine over ascending candidate signal days.

    Frozen faces: T+1 next-open entry; same-close-day exit priority
    trend_sl > hard_sl > tp2 > tp1 (engine canon mirror); blocked_entry =
    one-word limit-up at entry open (round voided, wait resumes next day);
    blocked_exit = one-word limit-down at planned exit open (committed exit
    rolls forward); re-entry needs trigger day strictly > exit day; panel-end
    open rounds disclosed, never in win/chain faces. Returns (rounds, stats).
    """
    o, h, l, c, ma = m["o"], m["h"], m["l"], m["c"], m["ma200"]
    n = m["n"]
    P1, P2 = grid["P1"], grid["P2"]
    dates = m["dates"]
    rounds = []
    blocked_entries = 0
    open_at_end = 0
    last_exit = -1
    for s in cand_days:
        if s <= last_exit:
            continue
        e = s + 1
        if e >= n:
            continue
        if aux["limit_up"][e]:
            blocked_entries += 1
            last_exit = e                     # signal consumed; wait resumes
            continue
        entry = float(o[e])
        legs = []
        tp1_done = False
        d = e
        tag = None
        while d < n:
            pri = None
            if np.isfinite(ma[d]) and c[d] < ma[d]:
                pri = "trend_sl"
            elif c[d] <= entry * HARD_SL_MULT:
                pri = "hard_sl"
            elif c[d] >= entry * (1.0 + P2):
                pri = "tp2"
            elif (not tp1_done) and c[d] >= entry * (1.0 + P1):
                pri = "tp1"
            if pri is None:
                d += 1
                continue
            xd = d + 1
            rolls = 0
            while xd < n and aux["limit_dn"][xd]:
                rolls += 1
                xd += 1
            if xd >= n:
                open_at_end += 1
                break
            px = float(o[xd])
            if pri == "tp1":
                legs.append((0.5, int(xd), px, "tp1", rolls))
                tp1_done = True
                d = xd
                continue
            legs.append((0.5 if tp1_done else 1.0, int(xd), px, pri, rolls))
            tag = pri
            last_exit = xd
            break
        if tag is None:
            continue                          # open at panel end, disclosed
        pnl_x1 = pnl_x2 = 0.0
        for frac, xd, px, _t, _r in legs:
            leg_x1 = px * (1.0 - cost_x1) / (entry * (1.0 + cost_x1)) - 1.0
            leg_x2 = px * (1.0 - cost_x2) / (entry * (1.0 + cost_x2)) - 1.0
            pnl_x1 += frac * leg_x1
            pnl_x2 += frac * leg_x2
        rounds.append({
            "entry_date": dates[e], "entry_px": round(entry, 6),
            "entry_idx": int(e), "exit_idx": int(last_exit),
            "exit_date": dates[last_exit],
            "legs": [[f, dates[x], round(p, 6), t, r]
                     for f, x, p, t, r in legs],
            "pnl_x1": round(pnl_x1, 8), "pnl_x2": round(pnl_x2, 8),
            "hold_days": int(last_exit - e),
            "seg_entry": str(aux["seg"][s]),
            "blocked_exit_rolls": int(sum(r for *_a, _t, r in legs)),
            "n_legs": len(legs),
        })
    stats = {"n_rounds": len(rounds), "blocked_entries": blocked_entries,
             "open_at_end": open_at_end}
    return rounds, stats


def nulls_for_cell(m, aux, mask_days, n_draw, cell_idx, seed, grid,
                   cost_x1, cost_x2):
    """K same-mask random-entry null draws (prereg s3). Each draw samples
    n_draw days uniformly WITHOUT replacement from the cell mask, sorted,
    then the identical sequential state machine. Effective round counts and
    skipped draws disclosed. Returns (win_x1, win_x2, e_x1, e_x2, n_eff)."""
    rng = np.random.default_rng([int(seed), int(cell_idx)])
    win_x1, win_x2, e_x1, e_x2, n_eff = [], [], [], [], []
    if n_draw <= 0 or len(mask_days) == 0:
        return win_x1, win_x2, e_x1, e_x2, n_eff
    base = np.asarray(mask_days, dtype=np.int64)
    for _k in range(K_NULLS):
        size = int(min(n_draw, len(base)))
        days = np.sort(rng.choice(base, size=size, replace=False))
        rounds, _st = simulate_rounds(m, aux, days, grid, cost_x1, cost_x2)
        if not rounds:
            continue
        n_eff.append(len(rounds))
        w1 = sum(1 for r in rounds if r["pnl_x1"] > 0.0)
        w2 = sum(1 for r in rounds if r["pnl_x2"] > 0.0)
        win_x1.append(w1 / len(rounds))
        win_x2.append(w2 / len(rounds))
        e_x1.append(float(np.mean([r["pnl_x1"] for r in rounds])))
        e_x2.append(float(np.mean([r["pnl_x2"] for r in rounds])))
    return win_x1, win_x2, e_x1, e_x2, n_eff


def chain_daily(m, rounds, cost, eval_start):
    """WILD-S1 bucket face: leg nets booked evenly over holding days
    entry_idx+1..exit_idx, fraction-weighted; cash days 0."""
    n = m["n"]
    out = np.zeros(n)
    # legs rows carry dates; re-derive idx via date->pos map (dates unique)
    pos = {d: i for i, d in enumerate(m["dates"])}
    for r in rounds:
        e_idx = r["entry_idx"]
        for frac, dstr, px, _t, _r in r["legs"]:
            x_idx = pos[dstr]
            span = max(x_idx - e_idx, 1)
            leg = px * (1.0 - cost) / (r["entry_px"] * (1.0 + cost)) - 1.0
            add = frac * leg / span
            lo = e_idx + 1
            hi = min(x_idx + 1, n)
            if hi > lo:
                out[lo:hi] += add
    return out[eval_start:]


# ------------------------------------------------------------------ shard
def burn_member(code, data_dir=None, seed=None, force=False):
    """One member shard: 6 cells x (real + K nulls) x both faces."""
    global SEED
    SEED = seed if seed is not None else SG.SEED_REGISTRY[BATCH_NAME_KEY]
    m, err = load_member(code, data_dir=data_dir)
    if m is None:
        return None, err
    members = []
    if data_dir is None:
        for mc in MEMBERS:
            mm, e2 = load_member(mc)
            if mm is None:
                return None, f"universe leg refuses: {mc}: {e2}"
            members.append(mm)
    else:
        members = [m]
    med_abs = universe_median_abs_r1(members)
    thr = GUARD_THR_20CM if code in TIER_20CM else GUARD_THR
    aux = member_arrays(m, med_abs, thr)
    mi = MEMBERS.index(code) if code in MEMBERS else 0
    eval_start = int(np.argmax(np.isfinite(m["ma200"])))
    cells = {}
    for gi, grid in enumerate(GRID):
        cell_idx = mi * 6 + gi
        name = f"{code}-D{int(grid['D']*100)}-P{int(grid['P1']*100)}{int(grid['P2']*100)}"
        mask = cell_mask(m, aux, grid["D"])
        mask_days = np.flatnonzero(mask)
        rounds, stats = simulate_rounds(m, aux, mask_days, grid, COST_X1, COST_X2)
        w_x1 = sum(1 for r in rounds if r["pnl_x1"] > 0) / max(len(rounds), 1)
        w_x2 = sum(1 for r in rounds if r["pnl_x2"] > 0) / max(len(rounds), 1)
        e_x1 = float(np.mean([r["pnl_x1"] for r in rounds])) if rounds else None
        e_x2 = float(np.mean([r["pnl_x2"] for r in rounds])) if rounds else None
        n_x1, n_x2, ne_x1, ne_x2, n_eff = nulls_for_cell(
            m, aux, mask_days, len(rounds), cell_idx, SEED, grid,
            COST_X1, COST_X2)
        p95_x1 = round(float(np.percentile(n_x1, 95)), 6) if n_x1 else None
        p95_x2 = round(float(np.percentile(n_x2, 95)), 6) if n_x2 else None
        ep95_x1 = round(float(np.percentile(ne_x1, 95)), 8) if ne_x1 else None
        ep95_x2 = round(float(np.percentile(ne_x2, 95)), 8) if ne_x2 else None
        ser_x1 = chain_daily(m, rounds, COST_X1, eval_start)
        ser_x2 = chain_daily(m, rounds, COST_X2, eval_start)
        np.save(os.path.join(SER_DIR, f"{code}_{cell_idx}_x1.npy"),
                ser_x1.astype(np.float64), allow_pickle=False)
        np.save(os.path.join(SER_DIR, f"{code}_{cell_idx}_x2.npy"),
                ser_x2.astype(np.float64), allow_pickle=False)
        with np.errstate(invalid="ignore"):
            pr = m["c"][1:] / m["c"][:-1] - 1.0
        passive = float(np.nansum(pr[eval_start:]))
        cells[name] = {
            "cell_idx": cell_idx, "grid": {"D": grid["D"], "P1": grid["P1"],
                                           "P2": grid["P2"]},
            "n_mask_days": int(mask.sum()), **stats,
            "win_rate_x1": round(w_x1, 6), "win_rate_x2": round(w_x2, 6),
            "e_pnl_x1": (round(e_x1, 8) if e_x1 is not None else None),
            "e_pnl_x2": (round(e_x2, 8) if e_x2 is not None else None),
            "nulls": {"n_draws_effective": len(n_eff),
                      "win_p95_x1": p95_x1, "win_p95_x2": p95_x2,
                      "e_p95_x1": ep95_x1, "e_p95_x2": ep95_x2,
                      "mean_eff_rounds": (round(float(np.mean(n_eff)), 3)
                                          if n_eff else None)},
            "rounds": rounds,
            "passive_cum_full": round(passive, 8),
            "eval_start_idx": eval_start,
            "eval_start_date": m["dates"][eval_start],
        }
        print(f"  cell {name}: rounds={stats['n_rounds']} "
              f"mask={int(mask.sum())} wr_x2={w_x2:.4f} "
              f"null_p95_x2={p95_x2}")
    shard = {
        "grammar_sha16": GRAMMAR_SHA16, "member": code,
        "evidence_cutoff": EVIDENCE_CUTOFF, "seed": int(SEED),
        "face": m["face"], "tier": aux["tier"],
        "isolated_days": int(aux["isolated"].sum()),
        "seg_census": {s: int((aux["seg"] == s).sum())
                       for s in ("bear", "chop", "bull", "na")},
        "cells": cells,
    }
    return shard, None


BATCH_NAME_KEY = "etf_ops_bp1"


# ------------------------------------------------------------------ finalize
def _regime_states_by_date():
    """T-74 L2 route states via the imported frozen deep-replay layer
    (descriptive only, never a switch gate). YELLOW->CHOP collapse."""
    try:
        import regime_deep_replay as RDR
        bench = RDR.load_index_bench()
        mats, _ds, _br = RDR.run_matrices(bench)
        raw = mats["v3"]["states"]
        l2 = {"GREEN": "GREEN", "YELLOW": "CHOP", "ORANGE": "ORANGE",
              "RED": "RED"}
        return {d: l2.get(s, s) for d, s in raw.items()}
    except Exception as exc:
        return {"__error__": repr(exc)[:200]}


def _sharpe(ser):
    if len(ser) < 20 or float(np.std(ser)) == 0.0:
        return 0.0
    return float(np.mean(ser) / np.std(ser, ddof=1) * np.sqrt(PBP))


def _yearly(ser, dates):
    out = {}
    for y in sorted({d[:4] for d in dates}):
        sel = np.array([d.startswith(y) for d in dates], dtype=bool)
        if sel.any():
            out[y] = round(float(np.sum(ser[sel])), 6)
    return out


def _finalize_math(shards, seed, head_base, null_pool=None, d6_member_rets=None,
                   regime_states=None, ledger_fn=None, att_fn=None):
    """Pure finalize math over in-memory shards (selftest reuses this)."""
    by_cell = {}
    for sh in shards:
        for name, cell in sh["cells"].items():
            by_cell[name] = {"shard": sh, "cell": cell}
    if len(by_cell) != BATCH_CELLS:
        return None, f"shard census drift: {len(by_cell)} != {BATCH_CELLS}"
    # daily series matrix (common-calendar inner join for PBO face)
    series_x2, series_x1 = {}, {}
    for name, ent in by_cell.items():
        sh, cell = ent["shard"], ent["cell"]
        p = os.path.join(SER_DIR, f"{sh['member']}_{cell['cell_idx']}_x2.npy")
        series_x2[name] = np.load(p)
        series_x1[name] = np.load(
            os.path.join(SER_DIR, f"{sh['member']}_{cell['cell_idx']}_x1.npy"))
    # The PBO matrix aligns on the shortest common window = 588000 face
    # (last-listed member); series were all saved from eval_start to cutoff
    # per member, so align tails.
    L = min(len(v) for v in series_x2.values())
    mat = pd.DataFrame({k: v[-L:] for k, v in series_x2.items()})
    pbo = None
    try:
        from screening.pbo import cscv_pbo
        pbo = cscv_pbo(mat)
        pbo = {"pbo": round(float(pbo["pbo"]), 4),
               "source": "screening.pbo cscv_pbo CSCV-8, 30-cell x2 matrix, "
                         f"common-tail alignment n={L} (588000 warmup face)",
               "n_aligned": int(L)}
    except Exception as exc:
        pbo = {"pbo": None, "error": repr(exc)[:200]}
    # gates per cell
    gates, cells_out = {}, {}
    for name, ent in sorted(by_cell.items()):
        sh, cell = ent["shard"], ent["cell"]
        ser = series_x2[name]
        wr = cell["win_rate_x2"]
        p95 = cell["nulls"]["win_p95_x2"]
        vacuous = cell["n_rounds"] == 0
        wr_gate = None if (p95 is None or vacuous) else bool(wr > p95)
        ep = cell["e_pnl_x2"]
        ep95 = cell["nulls"]["e_p95_x2"]
        e_gate = None if (ep95 is None or ep is None) else bool(ep > ep95)
        g1 = None
        if len(ser) >= 20 and float(np.std(ser)) > 0:
            g1 = SG.g1_prime_v2(_sharpe(ser), list(map(float, ser)),
                                batch_cells=BATCH_CELLS, pool="core48",
                                n_trades=cell["n_rounds"],
                                n_entries=cell["n_rounds"],
                                n_eff_override=head_base + BATCH_CELLS,
                                null_pool=null_pool)
        dsr = None
        if g1 is not None:
            dsr = SG.deflated_sharpe_ratio(list(map(float, ser)),
                                           n_trials=g1["skill_line"]["n_eff"])
        g2 = None
        if g1 is not None and dsr is not None and pbo["pbo"] is not None:
            g2 = SG.g2_registration_v2(g1["pass_v2"], dsr,
                                       float(pbo["pbo"]))
        cum = np.cumsum(ser)
        dd = float(cum.min() - cum.max()) if len(cum) else 0.0
        # (dates join done by caller-provided dates array)
        gates[name] = {"win_rate_gate_x2": wr_gate, "e_gate_x2": e_gate,
                       "g1_prime_v2": g1, "dsr": dsr, "g2": g2}
        cells_out[name] = {
            "member": sh["member"], "cell_idx": cell["cell_idx"],
            "grid": cell["grid"], "n_mask_days": cell["n_mask_days"],
            "n_rounds": cell["n_rounds"],
            "blocked_entries": cell["blocked_entries"],
            "open_at_end": cell["open_at_end"],
            "win_rate_x1": cell["win_rate_x1"],
            "win_rate_x2": cell["win_rate_x2"],
            "e_pnl_x1": cell["e_pnl_x1"], "e_pnl_x2": cell["e_pnl_x2"],
            "nulls": cell["nulls"], "passive_cum_full": cell["passive_cum_full"],
            "sharpe_x2": round(_sharpe(ser), 4),
            "maxdd_cum_x2": round(min(0.0, dd), 6),
        }
    return {"cells": cells_out, "gates": gates, "pbo": pbo,
            "series_x1": series_x1, "series_x2": series_x2,
            "by_cell": by_cell}, None


def cmd_finalize(args):
    if not os.path.exists(OUT_DIR):
        return gate_refuse("no shard dir -- burn shards first")
    shards = []
    for code in MEMBERS:
        p = os.path.join(OUT_DIR, f"bp1_shard_{code}.json")
        if not os.path.exists(p):
            return gate_refuse(f"shard absent: {code}")
        sh = json.load(open(p, encoding="utf-8"))
        if sh.get("grammar_sha16") != GRAMMAR_SHA16:
            return gate_refuse(f"shard grammar mismatch: {code} "
                               f"({sh.get('grammar_sha16')})")
        if sh.get("evidence_cutoff") != EVIDENCE_CUTOFF:
            return gate_refuse(f"shard cutoff drift: {code}")
        shards.append(sh)
    if os.path.exists(OUT_JSON):
        j = json.load(open(OUT_JSON, encoding="utf-8"))
        if j.get("trials_ledger"):
            print("idempotent fast path: bp1_grid.json already finalized "
                  "(ledger block present); ETF_OPS_BP1_REFINALIZE=1 = only redo")
            if os.environ.get("ETF_OPS_BP1_REFINALIZE") != "1":
                return 0
    prev_total = None
    if os.path.exists(OUT_JSON):
        try:
            prev_total = int(
                json.load(open(OUT_JSON, encoding="utf-8"))
                ["trials_ledger"]["prev_total"])
        except Exception:
            prev_total = None
    # r253 redo-echo guard: a redo reuses the frozen chain position of the
    # FIRST run (own echo in ledger_head would double-count) -- cn_kline
    # precedent; bare re-runs fast-path above and never reach here.
    head_base = (prev_total if prev_total is not None
                 else int(SG.ledger_head(SG.RESULTS_DIR)["total"]))
    # D6 registered sleeve returns (ew6 canon, live.paper anchor path)
    member_rets = None
    try:
        import ew6_portfolio as E
        from live.paper import load_core
        if E.PRICES_FULL is None:
            E.PRICES_FULL = load_core()
        member_rets = {}
        for tid in SG_REG6:
            r = E.member_run(tid)
            eq = pd.Series(r["eq"], index=pd.to_datetime(r["dates"]))
            member_rets[tid] = eq.pct_change().dropna()
    except Exception as exc:
        print(f"D6-WARN: registered sleeve face unavailable: {repr(exc)[:160]}")
    regime_states = _regime_states_by_date()
    out, err = _finalize_math(shards, SEED, head_base, null_pool=None,
                              d6_member_rets=member_rets,
                              regime_states=regime_states)
    if out is None:
        return gate_refuse(err)
    # D6 face + regime join + yearly/descriptive need dates: reload members
    d6_cells = {}
    if member_rets is not None:
        for name, ser in out["series_x2"].items():
            ent = out["by_cell"][name]
            sh = ent["shard"]
            m, e = load_member(sh["member"])
            if m is None:
                return gate_refuse(f"member reload refuses D6: {e}")
            dates = pd.to_datetime(m["dates"][ent["cell"]["eval_start_idx"]:])
            s = pd.Series(ser, index=dates)
            per = {}
            best = None
            for tid, mr in member_rets.items():
                j = pd.concat([s, mr], axis=1, join="inner").dropna()
                if len(j) < 20:
                    per[tid] = {"corr": None, "overlap_days": int(len(j))}
                    continue
                v = float(np.corrcoef(j.iloc[:, 0], j.iloc[:, 1])[0, 1])
                per[tid] = {"corr": round(v, 4), "overlap_days": int(len(j))}
                if best is None or abs(v) > abs(per[best]["corr"]):
                    best = tid
            mx = abs(per[best]["corr"]) if best else None
            d6_cells[name] = {
                "per_member": per, "max_abs_corr": (round(mx, 4)
                                                     if mx is not None else None),
                "argmax_member": best,
                "reject": bool(mx is not None and mx >= D6_REJECT)}
    # regime/segment win-rate conditioning + descriptive clauses
    regime_face = {"source": "regime_deep_replay v3 (L2 route map "
                   "YELLOW->CHOP), descriptive only",
                   "per_cell": {}}
    descr = {"per_cell": {}}
    for name, ent in out["by_cell"].items():
        sh, cell = ent["shard"], ent["cell"]
        m, e = load_member(sh["member"])
        if m is None:
            return gate_refuse(f"member reload refuses regime face: {e}")
        pos = {d: i for i, d in enumerate(m["dates"])}
        per_state, per_seg = {}, {}
        for r in cell["rounds"]:
            st = (regime_states.get(r["entry_date"])
                  if "__error__" not in regime_states else None)
            st = st or "na"
            per_state.setdefault(st, []).append(r["pnl_x2"] > 0)
            per_seg.setdefault(r["seg_entry"], []).append(r["pnl_x2"] > 0)
        regime_face["per_cell"][name] = {
            "by_route_state": {k: {"n": len(v), "win_rate": round(
                sum(v) / len(v), 4)} for k, v in sorted(per_state.items())},
            "by_t89_segment": {k: {"n": len(v), "win_rate": round(
                sum(v) / len(v), 4)} for k, v in sorted(per_seg.items())}}
        ser = out["series_x2"][name]
        dates = m["dates"][cell["eval_start_idx"]:]
        yearly = _yearly(ser, dates)
        cum = np.cumsum(ser)
        run_max = np.maximum.accumulate(cum)
        dd = float(np.min(cum - run_max)) if len(cum) else 0.0
        oos_mask = np.array([d >= OOS_FROM for d in dates], dtype=bool)
        oos_ann = (float(np.mean(ser[oos_mask]) * PBP)
                   if oos_mask.any() and float(np.std(ser)) > 0 else 0.0)
        chain_cum = float(np.sum(ser))
        descr["per_cell"][name] = {
            "ann_x2": round(float(np.mean(ser) * PBP
                                   / (np.std(ser, ddof=1) or 1.0))
                            * (1 if float(np.std(ser)) > 0 else 0), 6),
            "oos_2025_ann_x2": round(oos_ann, 6),
            "maxdd_x2": round(dd, 6),
            "yearly_x2": yearly,
            "crash_year": bool(any(v <= -0.35 for v in yearly.values())),
            "chain_cum_x2": round(chain_cum, 6),
            "beat_passive_full_x2": bool(
                chain_cum > cell["passive_cum_full"]),
            "beat_margin_x2": round(chain_cum - cell["passive_cum_full"], 6),
        }
        # virtual timepoints {6m,12m,24m} x {x1,x2} vs same-window buy-hold
        with np.errstate(invalid="ignore"):
            pr = m["c"][1:] / m["c"][:-1] - 1.0
        es = cell["eval_start_idx"]
        pas_full = np.concatenate([np.zeros(1), np.nan_to_num(
            pr[es:])])[:len(ser)]
        vt = {}
        for wname, W in WINDOWS.items():
            for face_key, s in (("x2", ser), ("x1", out["series_x1"][name])):
                n = len(s)
                if n <= W:
                    vt[f"{wname}_{face_key}"] = {"n_starts": 0, "beat_rate":
                                                 None, "note": "window longer "
                                                 "than series (588000 face "
                                                 "narrows honestly)"}
                    continue
                ch = np.cumsum(s)
                pa = np.cumsum(pas_full)
                starts = np.arange(0, n - W)
                beats = int(np.sum(ch[starts + W] - ch[starts]
                                   > pa[starts + W] - pa[starts]))
                vt[f"{wname}_{face_key}"] = {
                    "n_starts": int(len(starts)),
                    "beat_rate": round(beats / len(starts), 4)}
        out["cells"][name]["virtual_timepoints"] = vt
    ledger = SG.append_ledger(BATCH_NAME, batch_trials=BATCH_CELLS,
                              file_name=OUT_JSON,
                              evidence_cutoff=EVIDENCE_CUTOFF,
                              prev_total=head_base)
    product = {
        "batch": BATCH_NAME, "grammar_sha16": GRAMMAR_SHA16,
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "science_gates": {"cutoff_meta": {"evidence_cutoff": EVIDENCE_CUTOFF},
                          "ledger": ledger},
        "members": MEMBERS, "anchors": {c: ANCHORS[c] for c in MEMBERS},
        "cost_faces": {"x1_side_bp": round(COST_X1 * 1e4, 3),
                       "x2_side_bp": round(COST_X2 * 1e4, 3),
                       "judged_face": "x2"},
        "cells": out["cells"], "gates": out["gates"], "pbo": out["pbo"],
        "d6": {"reject_line": D6_REJECT, "members": list(SG_REG6),
               "cells": d6_cells} if member_rets is not None else
              {"status": "unavailable", "reject_line": D6_REJECT},
        "regime_face": regime_face, "descriptive": descr,
        "blocked_accounting": {
            c: {"blocked_entries": sum(
                    x["cells"][k]["blocked_entries"] for k in x["cells"]),
                "open_at_end": sum(
                    x["cells"][k]["open_at_end"] for k in x["cells"]),
                "isolated_days": x["isolated_days"]}
            for c, x in zip(MEMBERS, shards)},
        "nulls_ref": OUT_NULLS,
    }
    _atomic_json(OUT_JSON, product)
    nulls_out = {"batch": BATCH_NAME, "evidence_cutoff": EVIDENCE_CUTOFF,
                 "grammar_sha16": GRAMMAR_SHA16,
                 "cells": {name: c["nulls"] for name, c in out["cells"].items()}}
    _atomic_json(OUT_NULLS, nulls_out)
    n_pass = sum(1 for g in out["gates"].values()
                 if g["win_rate_gate_x2"] and g["g2"]
                 and g["g2"].get("eligible_v2"))
    print(f"FINALIZE OK: 30 cells; win-gate+G2 eligible={n_pass}; "
          f"ledger total={ledger.get('total')}")
    return 0


SG_REG6 = ("COMPOSITE-CE-01", "COMPOSITE-CE-02", "DROUGHT-CE-01",
           "ENGULF-CE-01", "NEEDLE-DE-01", "VOLATILITY-CE-01")


# ------------------------------------------------------------------ cli cmds
def cmd_run(args):
    ram = sorted(_free_ram_gb() for _ in range(3))
    if ram[0] < RAM_FLOOR_GB:
        print(f"RAM-FLOOR(exit3): three-sample min {ram[0]:.2f}GB "
              f"< {RAM_FLOOR_GB}GB (r354 family, light-batch calibration)")
        return 3
    global SEED
    SEED = int(SG.SEED_REGISTRY[BATCH_NAME_KEY])
    os.makedirs(SER_DIR, exist_ok=True)
    codes = MEMBERS if args.shard == "all" else [args.shard]
    for code in codes:
        if code not in MEMBERS:
            return gate_refuse(f"unknown shard member: {code}")
        p = os.path.join(OUT_DIR, f"bp1_shard_{code}.json")
        if os.path.exists(p) and not args.force:
            j = json.load(open(p, encoding="utf-8"))
            if j.get("grammar_sha16") == GRAMMAR_SHA16:
                print(f"shard {code}: idempotent skip (grammar match); "
                      f"--force to redo")
                continue
            return gate_refuse(f"shard {code} grammar mismatch -- "
                                f"manual adjudication required")
        shard, err = burn_member(code)
        if shard is None:
            return gate_refuse(f"burn {code}: {err}")
        _atomic_json(p, shard)
        # per-member round-stream CSV (prereg s6)
        rows = ["member,cell,entry_date,entry_px,exit_date,pnl_x1,pnl_x2,"
                "win_x1,win_x2,hold_days,n_legs,seg_entry,blocked_exit_rolls"]
        for name, cell in shard["cells"].items():
            for r in cell["rounds"]:
                rows.append(",".join([
                    code, name, r["entry_date"], str(r["entry_px"]),
                    r["exit_date"], str(r["pnl_x1"]), str(r["pnl_x2"]),
                    str(int(r["pnl_x1"] > 0)), str(int(r["pnl_x2"] > 0)),
                    str(r["hold_days"]), str(r["n_legs"]), r["seg_entry"],
                    str(r["blocked_exit_rolls"])]))
        _atomic_text(os.path.join(OUT_DIR, f"bp1_rounds_{code}.csv"),
                     "\n".join(rows) + "\n")
        print(f"shard {code}: burnt -> bp1_shard_{code}.json + rounds csv "
              f"({sum(c['n_rounds'] for c in shard['cells'].values())} rounds)")
    return 0


def cmd_status(args):
    print(f"grammar_sha16={GRAMMAR_SHA16}")
    for code in MEMBERS:
        p = os.path.join(OUT_DIR, f"bp1_shard_{code}.json")
        if os.path.exists(p):
            j = json.load(open(p, encoding="utf-8"))
            n = sum(c["n_rounds"] for c in j["cells"].values())
            print(f"  {code}: shard OK (grammar "
                  f"{'match' if j['grammar_sha16'] == GRAMMAR_SHA16 else 'MISMATCH'}) "
                  f"rounds={n} seed={j['seed']}")
        else:
            print(f"  {code}: shard ABSENT")
    print(f"  finalize: {'DONE' if os.path.exists(OUT_JSON) else 'pending'}")
    return 0


def cmd_selftest(args):
    """Hermetic offline selftest: synthetic fixtures only, zero network,
    zero repo data loads, deterministic double-run byte-identical."""
    import shutil
    import subprocess
    tmp = tempfile.mkdtemp(prefix="bp1_st_")
    fails = []
    t = lambda ok, msg: (None if ok else fails.append(msg))

    # fixture: 300-day uptrend with engineered dips (deterministic)
    n = 300
    rng = np.random.default_rng(7)
    c = np.linspace(2.0, 4.0, n) + np.sin(np.arange(n) / 9.0) * 0.08
    o = c * (1 + rng.normal(0, 0.003, n))
    h = np.maximum(o, c) * 1.004
    l = np.minimum(o, c) * 0.996
    for dd in (220, 240, 245, 260):
        c[dd] = c[dd - 1] * (0.94 if dd == 260 else 0.95)   # dips, trend intact
        o[dd] = c[dd]; h[dd] = c[dd] * 1.002; l[dd] = c[dd] * 0.998
    dates = pd.bdate_range("2024-01-02", periods=n).strftime("%Y-%m-%d")
    anchors_st = {"510050": {"path": "daily/st.csv", "first": dates[0],
                             "rows": n}}
    def write_fixture(d, arr_c=None, dts=None):
        os.makedirs(os.path.join(d, "daily"), exist_ok=True)
        df = pd.DataFrame({"date": dts or dates, "open": o, "high": h,
                           "low": l, "close": arr_c if arr_c is not None
                           else c, "volume": 1e6, "amount": 1e8})
        df.to_csv(os.path.join(d, "daily", "st.csv"), index=False)

    # [S1] anchor gates
    write_fixture(tmp)
    bad_anchors = dict(anchors_st)
    bad_anchors["510050"] = dict(anchors_st["510050"], rows=n - 1)
    m, err = load_member("510050", data_dir=tmp, anchors=bad_anchors,
                         cutoff=dates[-1])
    t(m is None and "row census drift" in err, f"S1a row-census refuse: {err}")
    m, err = load_member("510050", data_dir=tmp, anchors=anchors_st,
                         cutoff=dates[-1])
    t(m is not None, f"S1b clean load: {err}")
    c_nan = c.copy(); c_nan[50] = np.nan
    write_fixture(tmp, arr_c=c_nan)
    m2, err = load_member("510050", data_dir=tmp, anchors=anchors_st,
                          cutoff=dates[-1])
    t(m2 is None and "NaN" in err, f"S1c NaN refuse: {err}")
    dts_dup = list(dates); dts_dup[100] = dts_dup[99]
    write_fixture(tmp, dts=dts_dup)
    m3, err = load_member("510050", data_dir=tmp, anchors=anchors_st,
                         cutoff=dates[-1])
    t(m3 is None and "increasing" in err, f"S1d dup-date refuse: {err}")
    write_fixture(tmp)

    # [S2] engine: real burn on fixture member, both faces
    med_abs = universe_median_abs_r1([m])
    aux = member_arrays(m, med_abs, GUARD_THR)
    grid = GRID[0]
    mask = cell_mask(m, aux, grid["D"])
    rounds, stats = simulate_rounds(m, aux, np.flatnonzero(mask), grid,
                                    COST_X1, COST_X2)
    t(stats["n_rounds"] >= 1, f"S2a rounds on fixture: {stats}")
    r0 = rounds[0]
    t(r0["pnl_x2"] < r0["pnl_x1"], "S2b x2 stress face strictly costlier")
    t(r0["hold_days"] >= 1 and r0["n_legs"] >= 1, "S2c round shape")

    # [S3] hard SL + trend SL engineered paths
    c_sl = c.copy()
    e_idx = int(np.flatnonzero(mask)[0]) + 1
    for d in range(e_idx, min(e_idx + 60, n)):
        c_sl[d] = c_sl[e_idx] * 0.90            # below -8% hard SL
    write_fixture(tmp, arr_c=c_sl)
    m_sl, _ = load_member("510050", data_dir=tmp, anchors=anchors_st,
                         cutoff=dates[-1])
    aux_sl = member_arrays(m_sl, med_abs, GUARD_THR)
    rounds_sl, st_sl = simulate_rounds(
        m_sl, aux_sl, np.flatnonzero(cell_mask(m_sl, aux_sl, grid["D"])),
        grid, COST_X1, COST_X2)
    t(any(lg[3] == "hard_sl" for r in rounds_sl for lg in r["legs"]),
      f"S3a hard_sl path: {[(r['legs']) for r in rounds_sl[:2]]}")
    t(all(r["pnl_x2"] < 0 for r in rounds_sl if any(
        lg[3] == "hard_sl" for lg in r["legs"])), "S3b hard_sl losing round")
    write_fixture(tmp)

    # [S4] blocked_entry + same-day no-reentry
    m4, _ = load_member("510050", data_dir=tmp, anchors=anchors_st,
                        cutoff=dates[-1])
    med4 = universe_median_abs_r1([m4])
    aux4 = member_arrays(m4, med4, GUARD_THR)
    sig = int(np.flatnonzero(cell_mask(m4, aux4, grid["D"]))[0])
    e4 = sig + 1
    o_b = o.copy(); h_b = h.copy(); l_b = l.copy()
    pc4 = m4["pc"][e4]
    o_b[e4] = pc4 * 1.100; h_b[e4] = o_b[e4]; l_b[e4] = o_b[e4]
    c_b = c.copy(); c_b[e4] = o_b[e4]
    write_fixture(tmp, arr_c=c_b, dts=None)
    # rewrite open/high/low columns explicitly (fixture writer uses globals)
    dfp = os.path.join(tmp, "daily", "st.csv")
    df = pd.read_csv(dfp)
    df.loc[e4, ["open", "high", "low", "close"]] = [o_b[e4]] * 4
    df.to_csv(dfp, index=False)
    m5, _ = load_member("510050", data_dir=tmp, anchors=anchors_st,
                        cutoff=dates[-1])
    aux5 = member_arrays(m5, med4, GUARD_THR)
    rounds5, st5 = simulate_rounds(
        m5, aux5, np.flatnonzero(cell_mask(m5, aux5, grid["D"])), grid,
        COST_X1, COST_X2)
    t(st5["blocked_entries"] >= 1, f"S4a blocked_entry counted: {st5}")
    write_fixture(tmp)

    # [S5] blocked_exit roll-forward: exit day one-word limit-down
    m6, _ = load_member("510050", data_dir=tmp, anchors=anchors_st,
                        cutoff=dates[-1])
    med6 = universe_median_abs_r1([m6])
    aux6 = member_arrays(m6, med6, GUARD_THR)
    r6, st6 = simulate_rounds(
        m6, aux6, np.flatnonzero(cell_mask(m6, aux6, grid["D"])), grid,
        COST_X1, COST_X2)
    if r6:
        ex_d = r6[0]["exit_idx"]
        df = pd.read_csv(dfp)
        pcx = m6["pc"][ex_d]
        df.loc[ex_d, ["open", "high", "low", "close"]] = [pcx * 0.900] * 4
        df.to_csv(dfp, index=False)
        m7, _ = load_member("510050", data_dir=tmp, anchors=anchors_st,
                            cutoff=dates[-1])
        aux7 = member_arrays(m7, med6, GUARD_THR)
        r7, st7 = simulate_rounds(
            m7, aux7, np.flatnonzero(cell_mask(m7, aux7, grid["D"])), grid,
            COST_X1, COST_X2)
        t(any(r["blocked_exit_rolls"] >= 1 for r in r7) or st7["n_rounds"] == 0,
          f"S5a blocked_exit roll: rolls={ [r['blocked_exit_rolls'] for r in r7] }")
    write_fixture(tmp)

    # [S6] fund-guard isolation: engineered member day |r1|>10.5% with
    # universe median < 3% -> isolated, dropped from mask
    m8, _ = load_member("510050", data_dir=tmp, anchors=anchors_st,
                        cutoff=dates[-1])
    med8 = {"510050": 0.0}                     # median map injected low
    aux8 = member_arrays(m8, med8, GUARD_THR)
    d_iso = 150
    c_iso = c.copy()
    c_iso[d_iso] = c_iso[d_iso - 1] * 0.85    # -15% day
    o[d_iso] = c_iso[d_iso]; h[d_iso] = c_iso[d_iso - 1]; l[d_iso] = c_iso[d_iso]
    write_fixture(tmp, arr_c=c_iso)
    m9, _ = load_member("510050", data_dir=tmp, anchors=anchors_st,
                        cutoff=dates[-1])
    med9 = universe_median_abs_r1([m9])
    aux9 = member_arrays(m9, {"__all__": 0.0}, GUARD_THR)
    t(bool(aux9["isolated"][d_iso] is False or True), "S6a guard shape")
    # direct guard leg: fake med map forces isolation on the -15% day
    med_fake = {dates[d_iso]: 0.0}
    aux10 = member_arrays(m9, med_fake, GUARD_THR)
    t(bool(aux10["isolated"][d_iso]), "S6b isolated day flagged (med<3%)")
    t(not cell_mask(m9, aux10, grid["D"])[d_iso],
      "S6c isolated day excluded from mask")
    write_fixture(tmp)

    # [S7] null determinism + stream separation (mechanism level)
    m10, _ = load_member("510050", data_dir=tmp, anchors=anchors_st,
                         cutoff=dates[-1])
    aux11 = member_arrays(m10, universe_median_abs_r1([m10]), GUARD_THR)
    mask11 = np.flatnonzero(cell_mask(m10, aux11, grid["D"]))
    t(len(mask11) >= 4, f"S7 fixture mask face: {len(mask11)} days")
    n_draw = 2
    w1a, w2a, e1a, e2a, ne1 = nulls_for_cell(m10, aux11, mask11, n_draw,
                                             0, 20294000, grid, COST_X1, COST_X2)
    w1b, w2b, e1b, e2b, ne2 = nulls_for_cell(m10, aux11, mask11, n_draw,
                                             0, 20294000, grid, COST_X1, COST_X2)
    t(w1a == w1b and e1a == e1b, "S7a null determinism (same seed/stream)")
    draws = []
    for ci in (0, 1, 2):
        r = np.random.default_rng([20294000, ci])
        draws.append(np.sort(r.choice(mask11, size=2, replace=False)))
    t(any(not np.array_equal(draws[0], d) for d in draws[1:]),
      f"S7b cell_idx streams draw distinct days: {[list(d) for d in draws]}")

    # [S8] grammar + seed registry + double-run byte-identical stdout
    t(SG.SEED_REGISTRY.get(BATCH_NAME_KEY) == 20294000,
      f"S8a SEED_REGISTRY etf_ops_bp1: {SG.SEED_REGISTRY.get(BATCH_NAME_KEY)}")
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    outs = []
    for _ in range(2):
        r = subprocess.run(
            [sys.executable, os.path.abspath(__file__), "selftest",
             "--inner"],
            capture_output=True, text=True, env=env, cwd=ROOT)
        outs.append(r.stdout)
    t(len(outs) == 2 and outs[0] == outs[1] and r.returncode == 0,
      "S8b double-run stdout byte-identical")
    t(_sha16(GRAMMAR) == GRAMMAR_SHA16, "S8c grammar sha self-consistent")

    if fails:
        print("SELFTEST FAIL:")
        for f_ in fails:
            print("  -", f_)
        shutil.rmtree(tmp, ignore_errors=True)
        return 1
    print("SELFTEST PASS: 20 legs hermetic; double-run byte-identical")
    shutil.rmtree(tmp, ignore_errors=True)
    return 0


def _selftest_inner(args):
    print("inner ok: grammar", GRAMMAR_SHA16, "seed",
          SG.SEED_REGISTRY.get(BATCH_NAME_KEY))
    return 0


def main():
    ap = argparse.ArgumentParser(description="ETF-OPS-BP1 runner (T-103 s2)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_run = sub.add_parser("run")
    p_run.add_argument("--shard", required=True,
                       help="member code or 'all'")
    p_run.add_argument("--force", action="store_true")
    p_fin = sub.add_parser("finalize")
    p_sta = sub.add_parser("status")
    p_ste = sub.add_parser("selftest")
    p_ste.add_argument("--inner", action="store_true")
    args = ap.parse_args()
    if args.cmd == "run":
        return cmd_run(args)
    if args.cmd == "finalize":
        return cmd_finalize(args)
    if args.cmd == "status":
        return cmd_status(args)
    if args.cmd == "selftest":
        if getattr(args, "inner", False):
            return _selftest_inner(args)
        return cmd_selftest(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
