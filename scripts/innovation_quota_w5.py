"""INNOVATION_QUOTA_W5 runner -- ICU_MA_TIMING_P1 robust-regression
MA timing family judged batch (INNOVATION-QUOTA-SLOT-5, zoo #86
icu_ma_timing, param-frozen bm-b r222 digest sec.1).

Laws frozen in research/INNOVATION_QUOTA_W5_PREREG.md (r247 berth +
r248 bm-c freeze, seed three-step law ALL GREEN via full import view,
results/_r248bmc_w5_seed_law_facts.json):

  panel   data/daily/sh510300.csv raw pd.read_csv direct read
          (date,open,high,low,close,volume,amount), D2-truncated to
          evidence cutoff 2026-09-22 (P-5C frozen binding, W4-W12
          probe anchor, cross-family D6 date alignment). G-PANEL:
          rows == 3483, first == 2012-05-28, last == 2026-09-22.
          G-ANCHOR (strict-side faces, fail-closed vs the r247 frozen
          probe facts results/_r247bmc_icu_w5_probe_facts.json,
          one-face-off = config mismatch VOID): N5 decidable 3479 /
          first decidable bar-idx 4 / long-open 1171 / flat-open 1224
          / tie-maintain 1084 / open-rate 0.336591; N120 decidable
          3364 / first 119 / long-open 1733 / flat-open 1631 / tie 0 /
          open-rate 0.515161; N15 decidable 3469 / first 14 /
          long-open 1570 / flat-open 1612 / tie 287 / open-rate
          0.45258; extreme-day per-state records frozen (N5 2/7,
          N120 3/7, N15 2/7 long_above) incl. rounded ICU/close
          values; intra-family containment N5_in_N120 0.5098 /
          N5_in_N15 0.5884 / N15_in_N120 0.5484.
  engine  deterministic daily state machine (prereg s3 frozen,
          r222 digest clean-room): ICU(N) = rolling(N) Siegel(1982)
          repeated-median robust regression endpoint value
          intercept + slope*(N-1) (scipy.stats.siegelslopes
          method='hierarchical', scipy 1.16.1 = probe-recorded
          version; manual-numpy RM cross-check 50/50 exact in probe);
          side(t) = sign(close(t) - ICU(N)(t)); state(t) = long on
          cross-up, flat on cross-down, MAINTAIN previous on tie
          (entangled-maintain = ffill of side != 0 -- N5 1084 tie
          days = 31.1% structural face, prereg s2(a)); position(t) =
          state(t-1) close-to-close (T+1 onset causality, house law
          superseding the digest's same-day-coc narrative, prereg
          s2(e) divergence disclosed); binary 1.0/0.0 position
          (digest 0.95 sizing divergence disclosed, s3); NO stop line
          (cross-down exit IS the exit; r222 card has no stop clause,
          two-reading note kept); costs x1 =
          ce_transfer.COST_X1_RATE (13.041bp/side) on |dpos| booked
          to the following day (round trip = 2 sides); judged face =
          x1; x2 = double-rate disclosure column. Batch accrual
          window lo = max(first_decidable)+1 = 120 shared by all
          cells (single passive_override scalar + cross-cell
          PBO/CSCV date alignment; N5 pre-window decidable days
          4..118 and N15 days 14..118 discarded for batch
          comparability, disclosed per cell).
  cells   3 judged cells (prereg s3 frozen, zero in-batch
          selection, all-three channels = snooping-discount carrier):
          ICU-N5 (research-note channel), ICU-N120 (skopt Bayesian
          channel, reproduced score-optimal N), ICU-N15
          (differentiable-obj channel). Passive = PASSIVE-510300-BH
          buy-and-hold over the same batch window, live-computed
          Sharpe fed to g1_prime_v2 passive_override
          (REPO_CALENDAR_P2 law, no hand-copied lines).
  nulls   K=2000 uniform random-day-placement nulls per cell
          (RANDOM_LARGE_SAMPLE_LAW s3, prereg s3 frozen, W4 null
          family): each draw preserves the cell's window position-day
          count (exposure preserved) and resets placement uniformly
          over the pos_end domain [lo-1, n) -- trend structure
          destroyed. Flip count is NOT preserved by construction
          (isolated days = 2 flips each): null cost drag runs HIGHER
          than the real cell = frozen honest face (prereg s3
          disclosure, s5.4 expectation basis: low-exposure 34-52%
          open-rate faces run deepest in cost share). rng =
          np.random.default_rng([SEED, k]), k < 2000, one k-stream
          shared across cells (seed law frozen); shard npy
          checkpoints for idempotent resume.
  starts  K=1000 virtual starts (k in [2000, 3000), law s1 K>=1000):
          windows 6m/12m/24m = 126/252/504 trading days (252 ppy
          convention, disclosed); beat = cell window cum ret (x1 net)
          > passive window cum ret, per-window beat_rate disclosed.
          100 random split windows (k in [3000, 3100), law s3 >= 100):
          random split point in [0.2n, 0.8n], half-window Sharpe
          same-sign rate >= 80% = segment-stable.
  gates   G1'v2 per cell via science_gates.g1_prime_v2 (batch_cells
          = 2003 = 3 judged cells + 2000 null draws, the s0 counting
          law; prereg s4 wrote "batch_cells=3" as the judged-cell
          shorthand, s0's N_eff governs per the W1/W3/W4 family
          prereg-vs-runner reconciliation, disclosed here), pool=
          'core48' default named-pool reader overridden by
          passive_override = this batch's 510300-BH window Sharpe;
          batch-own null_pool per cell; NaN-safe nan-aware runner
          stats (r442 pit law: all-closed-state zero-return face must
          not silently degrade Sharpe to NaN via raw mean/std);
          n_trades = n_entries = derived position-face episode count
          (contiguous True runs, disclosed per cell); DSR via
          deflated_sharpe_ratio on the raw x1 cell series; family
          PBO via screening.pbo cscv_pbo CSCV-8 over the 3-cell
          matrix; G2 via g2_registration_v2. No hand-copied lines
          (O-2250).
  d6      3-cell pairwise |corr| + vs the registered 6 CE members
          (core48 equity face via cn_rev_tilt_p1.load_member_rets +
          REG6 reuse, W4 mirror); reject line 0.7; near-neighbor
          warning list = W10 MOM open (probe a_in_b 0.6-9.7%), W11
          STD20 open (10.7-12.0%), W9 AMP wide (46.6-58.3%), W7
          STREAK up (30.5-44.1%), W8 TSTATE (1.3-21.0%), W4 calm/wild
          (40.6-46.9%), VCONF surge descriptive face (52.1-57.0%,
          never a burned axis) -- all non-collapse per prereg s1.
  ledger  append_ledger("ICU_MA_TIMING_P1", 2003, "results/
          innovation_quota/ICU-MA-TIMING-P1.json", evidence_cutoff
          ="2026-09-22"); out["trials_ledger"] carries the return
          value (r434 pit law); gate_attrition measurement row.
Products (prereg s6): results/innovation_quota/ICU-MA-TIMING-P1.json
(top evidence_cutoff + cutoff_meta + panel + anchor faces + passive +
3 cells + per-cell nulls + virtual starts + splits + d6 + extreme-day
face + tie-maintain year distribution (s2(a) accountability column) +
funnel + gates + ledger) + nulls shard npy checkpoints (idempotent
resume).

Usage: run | selftest   (exit 0 ok; 2 = fail-closed gate refusal,
including the r450 landed-state guard: a judged product (trials_ledger
present, read from CONTENT not existence/timestamps) refuses re-run
rc=2 unless INNOVATION_QUOTA_W5_REFINALIZE=1; a phase-1-only product
resumes via npy checkpoints).
"""
import argparse
import json
import math
import os
import shutil
import sys
import tempfile
import time

import numpy as np
import pandas as pd
from scipy.stats import siegelslopes
import scipy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import science_gates as SG                      # shared gate library (O-2250)
from ce_transfer import COST_X1_RATE            # x1 = 13.041bp/side (G2-recorded)
from screening.pbo import cscv_pbo              # family PBO CSCV-8
from cn_rev_tilt_p1 import load_member_rets, _corr, REG6   # D6 member face

PANEL_CSV = os.path.join(ROOT, "data", "daily", "sh510300.csv")
OUT_DIR = os.path.join(ROOT, "results", "innovation_quota")
NULL_DIR = os.path.join(OUT_DIR, "nulls_w5")
OUT_JSON = os.path.join(OUT_DIR, "ICU-MA-TIMING-P1.json")
OUT_DIR_RESULTS = os.path.dirname(OUT_DIR)      # results root for lib faces
ATT_JSON = os.path.join(ROOT, "results", "gate_attrition.json")

BATCH_NAME = "ICU_MA_TIMING_P1"
BATCH_CELLS = 2003                # 3 judged cells + 2000 null draws (s0 law)
EVIDENCE_CUTOFF = "2026-09-22"
PBP = SG.PERIODS_PER_YEAR         # gate-chain single-source convention (252)
K_NULLS = 2000
NULL_SHARDS = 8
K_STARTS = 1000
K_SPLITS = 100
SEED = None                       # filled from SG.SEED_REGISTRY at run
D6_REJECT = 0.7
WIN_DAYS = {"6m": 126, "12m": 252, "24m": 504}   # trading-day windows (252 ppy)

# judged cells: all three N channels enter, zero in-batch selection
# (snooping-discount carrier, prereg s3)
CELLS = ["ICU-N5", "ICU-N120", "ICU-N15"]
CELL_N = {"ICU-N5": 5, "ICU-N120": 120, "ICU-N15": 15}

# frozen probe faces (G-PANEL / G-ANCHOR; r247 probe facts file,
# results/_r247bmc_icu_w5_probe_facts.json -- prereg s2 verbatim)
PANEL_ROWS = 3483
PANEL_FIRST = "2012-05-28"
PANEL_LAST = "2026-09-22"
ANCHOR = {
    "N5": {"decidable": 3479, "first_decidable_bar_idx": 4,
           "long_open": 1171, "flat_open": 1224,
           "tie_maintain_days": 1084, "open_rate": 0.336591},
    "N120": {"decidable": 3364, "first_decidable_bar_idx": 119,
             "long_open": 1733, "flat_open": 1631,
             "tie_maintain_days": 0, "open_rate": 0.515161},
    "N15": {"decidable": 3469, "first_decidable_bar_idx": 14,
            "long_open": 1570, "flat_open": 1612,
            "tie_maintain_days": 287, "open_rate": 0.45258},
}
EXTREME_DAYS = ["2015-07-27", "2016-01-04", "2024-02-28", "2024-09-24",
                "2024-09-30", "2025-04-07", "2026-01-19"]
# per-day frozen strict-state records + rounded ICU/close values
# (probe facts verbatim; state in {long_above, flat_below, tie, warmup})
EXTREME_EXPECT = {
    "N5": {
        "2015-07-27": ("flat_below", 4.1295, 3.803),
        "2016-01-04": ("flat_below", 3.7605, 3.535),
        "2024-02-28": ("flat_below", 3.461, 3.448),
        "2024-09-24": ("long_above", 3.31, 3.427),
        "2024-09-30": ("long_above", 4.0665, 4.233),
        "2025-04-07": ("flat_below", 3.9475, 3.695),
        "2026-01-19": ("flat_below", 4.829, 4.738),
    },
    "N120": {
        "2015-07-27": ("flat_below", 5.6513, 3.803),
        "2016-01-04": ("flat_below", 3.8053, 3.535),
        "2024-02-28": ("long_above", 3.211, 3.448),
        "2024-09-24": ("long_above", 3.2996, 3.427),
        "2024-09-30": ("long_above", 3.2886, 4.233),
        "2025-04-07": ("flat_below", 4.002, 3.695),
        "2026-01-19": ("flat_below", 4.8592, 4.738),
    },
    "N15": {
        "2015-07-27": ("flat_below", 4.2458, 3.803),
        "2016-01-04": ("flat_below", 3.7702, 3.535),
        "2024-02-28": ("flat_below", 3.5513, 3.448),
        "2024-09-24": ("long_above", 3.222, 3.427),
        "2024-09-30": ("long_above", 3.426, 4.233),
        "2025-04-07": ("flat_below", 3.9479, 3.695),
        "2026-01-19": ("flat_below", 4.8942, 4.738),
    },
}
EXTREME_OPEN_EXPECT = {"N5": 2, "N120": 3, "N15": 2}
# intra-family containment (probe intra_family verbatim, anchor face)
INTRA_EXPECT = {
    "N5_vs_N120": {"both_dec": 3364, "both_long": 597, "a_in_b": 0.5098,
                   "b_in_a": 0.3445},
    "N5_vs_N15": {"both_dec": 3469, "both_long": 689, "a_in_b": 0.5884,
                  "b_in_a": 0.4389},
    "N15_vs_N120": {"both_dec": 3364, "both_long": 861, "a_in_b": 0.5484,
                    "b_in_a": 0.4968},
}


def gate_refuse(msg):
    print(f"GATE-REFUSE(exit2): {msg}")
    return 2


def sharpe_of(series):
    """NaN-safe nan-aware Sharpe (r442 pit law): non-finite dropped, a
    degenerate all-zero face returns 0.0, never NaN via raw mean/std."""
    r = np.asarray(series, dtype=float)
    r = r[np.isfinite(r)]
    if len(r) < 2:
        return 0.0
    sd = r.std(ddof=1)
    return float(r.mean() / sd * math.sqrt(PBP)) if sd > 0 else 0.0


def cum_ret(series, lo, hi):
    """Window cumulative return over indices [lo, hi)."""
    seg = np.asarray(series[lo:hi], dtype=float)
    seg = seg[np.isfinite(seg)]
    return float(np.prod(1.0 + seg) - 1.0) if len(seg) else 0.0


# ------------------------------------------------------------- ICU chain
def icu_series(close, n):
    """ICU(N): rolling(N) Siegel repeated-median robust regression
    endpoint value intercept + slope*(N-1) (r247 probe verbatim,
    r222 digest truth-source; scipy siegelslopes hierarchical)."""
    n = int(n)
    vals = np.full(len(close), np.nan)
    c = np.asarray(close, dtype=float)
    for i in range(n - 1, len(c)):
        y = c[i - n + 1:i + 1]
        sl, ic = siegelslopes(y, np.arange(n, dtype=float),
                             method="hierarchical")
        vals[i] = ic + sl * (n - 1)
    return pd.Series(vals, index=close.index)


def manual_rm_endpoint(y):
    """Manual numpy RM (hierarchical) for the selftest scipy cross-check
    (probe verbatim)."""
    n = len(y)
    xi = np.arange(n, dtype=float)
    dy = y[:, None] - y[None, :]
    dx = xi[:, None] - xi[None, :]
    np.fill_diagonal(dx, 1.0)
    mask = ~np.eye(n, dtype=bool)
    slopes = dy / dx
    row_med = np.array([np.median(slopes[i][mask[i]]) for i in range(n)])
    slope = float(np.median(row_med))
    intercept = float(np.median(y - slope * xi))
    return intercept + slope * (n - 1)


def state_machine(above, below, dec):
    """Entangled-maintain state (prereg s3 frozen): side(t) = sign of
    close - ICU(N); cross-up -> long, cross-down -> flat, tie -> carry
    previous state (ffill of side != 0). Non-decidable warmup days hold
    the initial flat state. Returns boolean state array."""
    ab = np.asarray(above, dtype=bool)
    be = np.asarray(below, dtype=bool)
    d = np.asarray(dec, dtype=bool)
    state = np.zeros(len(ab), dtype=bool)
    cur = False
    for i in range(len(state)):
        if d[i]:
            if ab[i]:
                cur = True
            elif be[i]:
                cur = False
            # tie: maintain (cur unchanged)
        state[i] = cur
    return state


def raw_side_transitions(above, below, dec):
    """Raw three-valued side transition count on consecutive decidable
    days (prereg s5.3 prediction-3 carrier: episodes < raw transitions
    for tie-heavy N5 -- above<->tie and tie<->below each count)."""
    ab = np.asarray(above, dtype=bool)
    be = np.asarray(below, dtype=bool)
    d = np.asarray(dec, dtype=bool)
    side = np.zeros(len(ab), dtype=int)      # 0 = tie (or warmup)
    side[ab] = 1
    side[be] = -1
    idx = np.where(d)[0]
    if len(idx) < 2:
        return 0
    seg = side[idx]
    return int(np.sum(seg[1:] != seg[:-1]))


# ------------------------------------------------------------------ panel
def load_panel():
    """G-PANEL / G-ANCHOR fail-closed battery + ICU state-face assembly.
    Engine re-derivation must match the r247 frozen probe faces exactly
    (one-face-off = config mismatch VOID, not data corruption)."""
    df = pd.read_csv(PANEL_CSV)
    df["date"] = df["date"].astype(str)
    df = df[df["date"] <= EVIDENCE_CUTOFF].reset_index(drop=True)
    if len(df) != PANEL_ROWS:
        return None, f"G-PANEL rows {len(df)} != {PANEL_ROWS}"
    if df["date"].iloc[0] != PANEL_FIRST or df["date"].iloc[-1] != \
            PANEL_LAST:
        return None, (f"G-PANEL span {df['date'].iloc[0]}.."
                      f"{df['date'].iloc[-1]} != {PANEL_FIRST}.."
                      f"{PANEL_LAST}")
    close = df["close"]
    ret = close.pct_change()

    icus = {}
    faces = {}
    states = {}
    for name, n in CELL_N.items():
        key = "N%d" % n
        icu = icu_series(close, n)
        icus[key] = icu
        dec = icu.notna()
        if not bool(dec.any()):
            return None, f"G-ANCHOR {key}: zero decidable bars"
        first_dec = int(np.argmax(dec.values))
        above = close > icu
        below = close < icu
        tie = (close == icu) & dec
        long_open = above
        got = {"decidable": int(dec.sum()),
               "first_decidable_bar_idx": first_dec,
               "long_open": int(long_open.sum()),
               "flat_open": int(below.sum()),
               "tie_maintain_days": int(tie.sum()),
               "open_rate": round(float(long_open.sum() / dec.sum()), 6)}
        exp = ANCHOR[key]
        for f, v in exp.items():
            if got[f] != v:
                return None, (f"G-ANCHOR {key} {f} {got[f]} != frozen {v} "
                              f"(face mismatch -> config VOID, not data "
                              f"corruption)")
        # extreme-day per-state records (fail-closed, probe facts
        # verbatim incl. rounded ICU/close values)
        ext_states = {}
        ext_open = 0
        for day in EXTREME_DAYS:
            idx = df.index[df["date"] == day]
            if len(idx) == 0:
                return None, f"G-ANCHOR extreme day {day} absent from panel"
            i = int(idx[0])
            st = ("long_above" if bool(above.iloc[i]) else
                  "flat_below" if bool(below.iloc[i]) else
                  "tie" if bool(tie.iloc[i]) else "warmup")
            e_st, e_icu, e_close = EXTREME_EXPECT[key][day]
            if st != e_st:
                return None, (f"G-ANCHOR extreme {day} {key} {st} != "
                              f"frozen {e_st}")
            if round(float(icu.iloc[i]), 4) != e_icu or \
                    round(float(close.iloc[i]), 4) != e_close:
                return None, (f"G-ANCHOR extreme {day} {key} value drift "
                              f"icu={round(float(icu.iloc[i]), 4)} close="
                              f"{round(float(close.iloc[i]), 4)} != frozen "
                              f"({e_icu}, {e_close})")
            ext_states[day] = {"state": st,
                               "icu": round(float(icu.iloc[i]), 4),
                               "close": round(float(close.iloc[i]), 4)}
            if st == "long_above":
                ext_open += 1
        if ext_open != EXTREME_OPEN_EXPECT[key]:
            return None, (f"G-ANCHOR extreme_open {key} {ext_open} != "
                          f"frozen {EXTREME_OPEN_EXPECT[key]}")
        faces[key] = got
        faces[key]["extreme_states"] = ext_states
        faces[key]["extreme_open_count"] = ext_open
        states[key] = {"icu": icu, "dec": dec, "above": above,
                       "below": below, "tie": tie}
    # intra-family containment anchor (probe intra_family verbatim)
    for pair, exp in INTRA_EXPECT.items():
        a_k, b_k = pair.split("_vs_")
        ia, ib = icus[a_k], icus[b_k]
        la = (close > ia) & ia.notna()
        lb = (close > ib) & ib.notna()
        both = ia.notna() & ib.notna()
        got = {"both_dec": int(both.sum()),
               "both_long": int((la & lb & both).sum()),
               "a_in_b": round(float((la & lb).sum()) / float(la.sum()), 4)
               if la.sum() else None,
               "b_in_a": round(float((la & lb).sum()) / float(lb.sum()), 4)
               if lb.sum() else None}
        for f, v in exp.items():
            if got[f] != v:
                return None, (f"G-ANCHOR intra {pair} {f} {got[f]} != "
                              f"frozen {v}")
    # batch accrual window: first position day = max(first_decidable)+1
    lo = max(f["first_decidable_bar_idx"] for f in faces.values()) + 1
    face = {"rows": len(df), "first": str(df["date"].iloc[0]),
            "last": str(df["date"].iloc[-1]),
            "close_min": float(close.min()), "close_max": float(close.max()),
            "batch_lo": lo, "batch_days": len(df) - lo}
    return {"df": df, "ret": ret.to_numpy(dtype=float),
            "dates": df["date"].to_numpy(), "states": states,
            "icus": icus, "anchor_faces": faces, "lo": lo,
            "panel_face": face}, None


# ------------------------------------------------------------- engine leg
def state_pos_end(state):
    """pos_end[j] = state[j]: the decision made at close j is what the
    position_series day-mapping holds on day j+1 (T+1 onset causal)."""
    return np.asarray(state, dtype=bool)


def position_series(pos_end, ret, lo):
    """Batch-window close-to-close position face (W3/W4 mirror): pos[t] =
    pos_end[lo-1+t] over window indices [lo, n); cost = x1 rate on
    |dpos| booked to the following day (entry side on the first
    accrual day, exit side on the first flat day; round trip = 2
    sides)."""
    n = len(ret)
    w = n - lo
    pos = np.zeros(w)
    pos[0] = 0.0 if lo == 0 else float(pos_end[lo - 1])
    for t in range(1, w):
        pos[t] = float(pos_end[lo - 1 + t])
    gross = pos * ret[lo:]
    flips = np.zeros(w)
    flips[0] = abs(pos[0] - (0.0 if lo == 0 else float(pos_end[lo - 2])))
    for t in range(1, w):
        flips[t] = abs(pos[t] - pos[t - 1])
    net = gross - COST_X1_RATE * flips
    return pos, gross, net, flips


def passive_series(ret, lo):
    """PASSIVE-510300-BH: buy-and-hold over the same batch window
    (zero flips, zero cost); batch-window live-computed face."""
    return ret[lo:].copy()


def episodes_of(pos):
    """Contiguous True runs of the position face -> episode list
    (window indices, half-open spans) + entry count (0->1 edges)."""
    eps = []
    entries = 0
    t = 0
    w = len(pos)
    while t < w:
        if pos[t] > 0:
            entries += 1
            j = t
            while j < w and pos[j] > 0:
                j += 1
            eps.append((t, j))
            t = j
        else:
            t += 1
    return eps, entries


# ------------------------------------------------------------------ nulls
def uniform_day_null(pos_end_domain, held, n, rng):
    """One uniform random-day-placement draw (prereg s3 frozen, W4
    null family): preserve the cell's window position-day count
    (exposure), reset placement uniformly over the pos_end domain
    [lo-1, n) -- trend structure destroyed, flip count NOT preserved
    (isolated days = 2 flips each; null cost drag higher than the real
    cell = frozen honest face)."""
    npos = np.zeros(n, dtype=bool)
    if held > 0:
        idx = rng.choice(pos_end_domain, size=held, replace=False)
        npos[idx] = True
    return npos


def run_nulls(cell_key, held, ret, lo):
    """K=2000 null draws for one cell (shared k-stream seed law,
    rng([SEED, k]) k<2000); shard npy checkpoints for idempotent
    resume."""
    os.makedirs(NULL_DIR, exist_ok=True)
    n = len(ret)
    domain = np.arange(lo - 1, n)
    per = K_NULLS // NULL_SHARDS
    vals = np.empty(K_NULLS)
    for s in range(NULL_SHARDS):
        path = os.path.join(NULL_DIR, f"{cell_key}_shard{s}.npy")
        if os.path.exists(path):
            vals[s * per:(s + 1) * per] = np.load(path)
            continue
        chunk = np.empty(per)
        for i in range(per):
            k = s * per + i
            rng = np.random.default_rng([SEED, k])
            npos = uniform_day_null(domain, held, n, rng)
            _, _, net, _ = position_series(npos, ret, lo)
            chunk[i] = sharpe_of(net)
        np.save(path, chunk)
        vals[s * per:(s + 1) * per] = chunk
    cov = {"mu": round(float(vals.mean()), 4),
           "sigma": round(float(vals.std(ddof=1)), 4),
           "n_values": int(len(vals))}
    return {"values": [round(float(v), 4) for v in vals],
            "coverage": cov,
            "face": "uniform random day placement (window position-day "
                    "count preserved = exposure; placement uniform over "
                    "pos_end domain [lo-1,n); flip count NOT preserved "
                    "-- isolated days = 2 flips each, null cost drag "
                    "higher than the real cell = frozen honest face "
                    "(prereg s3, W4 null family)"}


# ------------------------------------------------- starts / splits
def virtual_starts(series_by_face, passive):
    """K=1000 random virtual starts x 3 windows (law s1); one rng per k
    shared across windows (per-window identical start position, nested
    windows honest overlap disclosed); beat = cell window cum (x1 net)
    > passive window cum."""
    out = {"n_starts": K_STARTS, "windows_days": WIN_DAYS, "cells": {}}
    n = len(passive)
    wmax = max(WIN_DAYS.values())
    los = []
    for k in range(K_STARTS):
        rng = np.random.default_rng([SEED, 2000 + k])
        los.append(int(rng.integers(0, n - wmax)))
    for name, ser in series_by_face.items():
        s = np.asarray(ser, dtype=float)
        wins = {}
        for wname, w in WIN_DAYS.items():
            hits = 0
            for k in range(K_STARTS):
                lo = los[k]
                hits += int(cum_ret(s, lo, lo + w) >
                            cum_ret(passive, lo, lo + w))
            wins[wname] = {"beats": hits,
                           "beat_rate": round(hits / K_STARTS, 4)}
        out["cells"][name] = wins
    return out


def split_windows(series_by_face):
    """100 random split windows (law s3): split point in [0.2n, 0.8n],
    half-window Sharpe same-sign rate >= 80% = segment-stable."""
    out = {}
    for name, ser in series_by_face.items():
        r = np.asarray(ser, dtype=float)
        n = len(r)
        agree = 0
        for k in range(K_SPLITS):
            rng = np.random.default_rng([SEED, 3000 + k])
            cut = int(rng.integers(int(0.2 * n), int(0.8 * n)))
            a, b = sharpe_of(r[:cut]), sharpe_of(r[cut:])
            agree += int((a > 0) == (b > 0))
        rate = agree / K_SPLITS
        out[name] = {"same_sign_rate": round(rate, 4),
                     "segment_stable": bool(rate >= 0.80),
                     "n_splits": K_SPLITS}
    return out


# ------------------------------------------------------------------ d6
MR_LOADER = None        # member-returns loader (selftest stub hook)


def _default_mr_loader():
    rets, _cuts = load_member_rets()
    return rets, _corr, list(REG6)


def d6_block(P, series_by_cell):
    loader = MR_LOADER or _default_mr_loader
    member_rets, corr_fn, reg6 = loader()
    lo = P["lo"]
    idx = pd.DatetimeIndex(P["dates"][lo:])
    out = {"reject_line": D6_REJECT, "members": reg6,
           "near_neighbor_warning": [
               "W10 MOM open (probe a_in_b 0.6-9.7% non-collapse, "
               "prereg s1: trend-axis new estimator, not a collapse)",
               "W11 STD20 open (10.7-12.0% disclosed)",
               "W9 AMP wide (46.6-58.3% disclosed)",
               "W7 STREAK up (30.5-44.1% disclosed)",
               "W8 TSTATE open (1.3-21.0% disclosed)",
               "W4 calm/wild volume regime (40.6-46.9%, W4 49.7% "
               "precedent band, non-collapse)",
               "VCONF surge/dry descriptive face (52.1-57.0%, never a "
               "burned axis, disclosed)"],
           "cells": {}}
    for name, ser in series_by_cell.items():
        s = pd.Series(np.asarray(ser, dtype=float), index=idx)
        per = {}
        for tid, mr in member_rets.items():
            v, ov = corr_fn(s, mr)
            per[tid] = {"corr": v, "overlap_days": ov}
        fin = {t: v["corr"] for t, v in per.items()
               if v["corr"] is not None}
        amax = max(fin, key=lambda t: abs(fin[t])) if fin else None
        out["cells"][name] = {
            "per_member": per,
            "max_abs_corr_member": round(abs(fin[amax]), 4) if amax else None,
            "reject": bool(amax and abs(fin[amax]) >= D6_REJECT)}
    cross = {}
    names = list(series_by_cell)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a = np.asarray(series_by_cell[names[i]], dtype=float)
            b = np.asarray(series_by_cell[names[j]], dtype=float)
            if a.std() > 0 and b.std() > 0:
                cross[f"{names[i]}|{names[j]}"] = round(float(
                    np.corrcoef(a, b)[0, 1]), 4)
    out["same_batch_cross"] = cross
    return out


# ------------------------------------------------------------------ product
def _cell_stats(ser):
    r = np.asarray(ser, dtype=float)
    fin = r[np.isfinite(r)]
    n = len(fin)
    eq = np.cumprod(1.0 + fin)
    dd = float((eq / np.maximum.accumulate(eq) - 1.0).min()) if n else 0.0
    ann = float(eq[-1] ** (PBP / max(n, 1)) - 1.0) if n else 0.0
    return {"sharpe_full": round(sharpe_of(r), 4),
            "ann_ret": round(ann, 6),
            "max_dd": round(dd, 6), "n_days": int(len(r)),
            "median_abs_r": round(float(np.median(np.abs(fin))), 8)
            if n else None}


def episode_kpi(passive_ser, net_ser, episodes):
    """O-1524 KPI dual disclosure (W3/W4 mirror). Trade-level faces (the
    law's primary reading) + the W1-lineage passive-same-days faces.
    Degeneracy disclosure: for a pure long-flat timing face the cell is
    fully invested on every intra-episode day, so the vs-passive-same-
    days edge is -entry-cost by construction (kept for W1 lineage
    comparability); the alpha question lives at the full-window /
    segment-mix level (G1/vstarts/splits)."""
    pas = np.asarray(passive_ser, dtype=float)
    cel = np.asarray(net_ser, dtype=float)
    wins_p, edges, ep_rets = 0, [], []
    for (a, b) in episodes:
        if b > len(pas):
            b = len(pas)
        if a >= b:
            continue
        e_cum = float(np.prod(1.0 + cel[a:b]) - 1.0)
        p_cum = float(np.prod(1.0 + pas[a:b]) - 1.0)
        if np.isfinite(e_cum) and np.isfinite(p_cum):
            wins_p += int(e_cum > p_cum)
            edges.append(e_cum - p_cum)
            ep_rets.append(e_cum)
    n_ep = len(ep_rets)
    win_rets = [r for r in ep_rets if r > 0]
    loss_rets = [r for r in ep_rets if r <= 0]
    payoff = None
    if win_rets and loss_rets:
        mw = float(np.mean(win_rets))
        ml = abs(float(np.mean(loss_rets)))
        payoff = round(mw / ml, 4) if ml > 0 else None
    return {
        "n_closed_episodes": n_ep,
        "win_rate_trade_level": round(
            len(win_rets) / n_ep, 4) if n_ep else None,
        "mean_episode_return": round(
            float(np.mean(ep_rets)), 8) if ep_rets else None,
        "payoff_ratio_win_over_loss": payoff,
        "win_rate_vs_passive_same_days": round(wins_p / n_ep, 4)
        if n_ep else None,
        "mean_episode_edge_vs_passive": round(float(np.mean(edges)), 8)
        if edges else None,
        "kpi_face_note": "trade-level faces are the O-1524 primary "
                         "reading; vs-passive-same-days faces are "
                         "structurally -entry-cost for long-flat timing "
                         "(degenerate, kept for W1 lineage)",
    }


def extreme_face(P, cells):
    """Extreme-day single-column disclosure (prereg s2(d)/s5.5): panel
    worst/best day + per-cell extreme-day strict state + window
    position on that day (crisis-day partial-defense face: 2-3/7
    open)."""
    ret = P["ret"]
    dates = P["dates"]
    lo = P["lo"]
    worst = int(np.nanargmin(ret))
    best = int(np.nanargmax(ret))
    out = {
        "worst_day": {"date": str(dates[worst]),
                      "ret": round(float(ret[worst]), 6)},
        "best_day": {"date": str(dates[best]),
                     "ret": round(float(ret[best]), 6)},
        "crisis_face_note": "partial defense face: 2-3/7 extreme days "
                            "open (vs W4 structurally-open 6-7/7 and "
                            "W12 all-closed 0/7); maxdd face inherits "
                            "partial 2015/2016/2024 drawdown priors "
                            "(prereg s2(d))",
        "cells": {},
    }
    for name in CELLS:
        st = P["states"]["N%d" % CELL_N[name]]
        pos = cells[name]["pos"]
        per = {}
        openc = 0
        for day in EXTREME_DAYS:
            idx = np.where(dates == day)[0]
            if len(idx) == 0:
                per[day] = {"state": "absent"}
                continue
            i = int(idx[0])
            state = ("long_above" if bool(st["above"].iloc[i]) else
                     "flat_below" if bool(st["below"].iloc[i]) else
                     "tie" if bool(st["tie"].iloc[i]) else "warmup")
            win_pos = None
            if i >= lo:
                win_pos = float(pos[i - lo])
            per[day] = {"state": state, "window_position": win_pos}
            if state == "long_above":
                openc += 1
        out["cells"][name] = {"extreme_days": per, "extreme_open_count":
                              openc}
    return out


def maintain_face(P, cells):
    """Tie-maintain year distribution (prereg s2(a) accountability
    column): per-cell window tie-maintain days (strict-face ties) and
    position days grouped by calendar year -- the N5 31.1%
    entangled-maintain structural face readout."""
    dates = P["dates"]
    lo = P["lo"]
    years = np.array([d[:4] for d in dates[lo:]])
    out = {}
    for name in CELLS:
        st = P["states"]["N%d" % CELL_N[name]]
        pos = cells[name]["pos"]
        tie_all = (st["dec"] & ~st["above"] & ~st["below"]).to_numpy()
        tie_w = tie_all[lo:]
        pos_on = pos > 0
        per_tie, per_pos = {}, {}
        for y in np.unique(years):
            m = years == y
            per_tie[str(y)] = int((tie_w & m).sum())
            per_pos[str(y)] = int((pos_on & m).sum())
        out[name] = {"tie_maintain_days_by_year": per_tie,
                     "tie_maintain_days_total": int(tie_w.sum()),
                     "position_days_by_year": per_pos,
                     "position_days_total": int(pos_on.sum())}
    return out


def _attr_row(batch, delta, total, gates, entries):
    d = json.load(open(ATT_JSON, encoding="utf-8"))
    row = {"batch": batch,
           "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
           "kind": "measurement", "cells_ledger_delta": delta,
           "ledger_total_after": total, "gates": gates,
           "entries": entries}
    own = [i for i, e in enumerate(d["entries"])
           if e.get("batch") == batch and e.get("kind") == "measurement"]
    if own:
        d["entries"][own[-1]] = row
    else:
        d["entries"].append(row)
    with open(ATT_JSON + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)
    os.replace(ATT_JSON + ".tmp", ATT_JSON)


def phase1_write(P, cells, passive_stats, nulls, vstarts, splits, d6,
                 xfaces, mfaces):
    """Phase-1 product (no gates): passive_override consumer face."""
    os.makedirs(OUT_DIR, exist_ok=True)
    product = {
        "batch": BATCH_NAME,
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "cutoff_meta": SG.cutoff_meta(EVIDENCE_CUTOFF),
        "prereg": "research/INNOVATION_QUOTA_W5_PREREG.md (r247 berth "
                  "+ r248 bm-c freeze, seed 20322500)",
        "seed": {"base": SEED, "k_nulls": K_NULLS,
                 "k_substreams": "nulls k<2000; starts k in [2000,3000); "
                                 "splits k in [3000,3100) -- rng([SEED, k]) "
                                 "one k-stream shared across cells"},
        "panel": P["panel_face"],
        "anchor_faces": {k: {f: v for f, v in P["anchor_faces"][k].items()
                            if f != "extreme_states"}
                         for k in P["anchor_faces"]},
        "scipy_version": scipy.__version__,
        "warmup_law": "ICU(5) first valid idx 4; ICU(120) idx 119; "
                      "ICU(15) idx 14 (rolling RM window) -> batch "
                      "accrual window lo = 120 (max first-decidable + 1; "
                      "N5 pre-window decidable days 4..118 and N15 days "
                      "14..118 discarded for batch comparability, "
                      "disclosed)",
        "legs_face": {n: {"decidable":
                          P["anchor_faces"]["N%d" % CELL_N[n]]["decidable"],
                          "long_open_strict":
                          P["anchor_faces"]["N%d" % CELL_N[n]]["long_open"],
                          "tie_maintain_days":
                          P["anchor_faces"]["N%d" % CELL_N[n]]
                          ["tie_maintain_days"],
                          "raw_side_transitions":
                          cells[n]["raw_side_transitions"],
                          "window_position_days": int(cells[n]["pos"].sum()),
                          "episodes": cells[n]["entries"],
                          "pre_window_discard_days":
                          max(0, P["lo"] - 1 -
                              P["anchor_faces"]["N%d" % CELL_N[n]]
                              ["first_decidable_bar_idx"])}
                      for n in CELLS},
        "cost_face": {"x1_rate_per_side": COST_X1_RATE,
                      "booking": "|dpos| booked to the following day; "
                                 "round trip = 2 sides",
                      "judged_face": "x1",
                      "x2_disclosure": 2 * COST_X1_RATE},
        "engine_law": "ICU(N)=rolling(N) Siegel repeated-median endpoint "
                      "intercept+slope*(N-1) (scipy siegelslopes "
                      "hierarchical); side(t)=sign(close-ICU); state: "
                      "cross-up long / cross-down flat / tie maintain "
                      "(ffill of side!=0); position(t)=state(t-1) T+1 "
                      "onset close-to-close; binary 1.0/0.0 (digest 0.95 "
                      "sizing divergence disclosed); NO stop line "
                      "(cross-down exit IS the exit, r222 no-stop-clause "
                      "two-reading note kept)",
        "passive": {"passive_510300_bh": {"full": passive_stats}},
        "cells": {n: cells[n]["stats"] for n in CELLS},
        "nulls": nulls, "virtual_starts": vstarts, "splits": splits,
        "d6": d6,
        "extreme_day_face": xfaces["extreme"],
        "maintain_face": mfaces,
        "funnel": {"harvest_column": 1,
                   "harvest_note": "zoo #86 icu_ma_timing param-frozen "
                                   "untried family, r247 probe facts "
                                   "(quota line: first robust-regression "
                                   "estimator timing face)",
                   "gate_column": "0/3 pending judgment (this batch)"},
    }
    with open(OUT_JSON + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(product, fh, ensure_ascii=False, indent=1)
    os.replace(OUT_JSON + ".tmp", OUT_JSON)
    return product


def finalize(product, P, cells, passive_ser):
    prev_total = None
    if os.path.exists(OUT_JSON):
        try:
            with open(OUT_JSON, encoding="utf-8") as fh:
                old = json.load(fh)
            prev_total = (old.get("trials_ledger") or {}).get("prev_total")
        except Exception:
            prev_total = None
    passive_override = product["passive"]["passive_510300_bh"]["full"][
        "sharpe_full"]
    gates = {}
    for name in CELLS:
        net = cells[name]["net"]
        st = cells[name]["stats"]
        g1 = SG.g1_prime_v2(st["sharpe_full"], net,
                            batch_cells=BATCH_CELLS, pool="core48",
                            results_dir=OUT_DIR_RESULTS,
                            null_pool={"values": product["nulls"][name][
                                           "values"],
                                       "coverage": product["nulls"][name][
                                           "coverage"]},
                            n_trades=cells[name]["entries"],
                            n_entries=cells[name]["entries"],
                            passive_override=passive_override)
        dsr = SG.deflated_sharpe_ratio(
            net, n_trials=g1["skill_line"]["n_eff"])
        gates[name] = {"g1_prime_v2": g1, "dsr": dsr}
    mat = pd.DataFrame({n: np.asarray(cells[n]["net"], dtype=float)
                        for n in CELLS})
    pbo = cscv_pbo(mat)
    for name in gates:
        gates[name]["g2"] = SG.g2_registration_v2(
            gates[name]["g1_prime_v2"]["pass_v2"], gates[name]["dsr"],
            float(pbo["pbo"]))
        gates[name]["d6_reject"] = bool(
            product["d6"]["cells"][name]["reject"])
    ledger = SG.append_ledger(BATCH_NAME, BATCH_CELLS,
                              file_name="results/innovation_quota/"
                                        "ICU-MA-TIMING-P1.json",
                              evidence_cutoff=EVIDENCE_CUTOFF,
                              prev_total=prev_total)
    product["gates"] = gates
    product["family_pbo"] = pbo
    product["passive_override_fed"] = passive_override
    product["episode_kpi"] = {
        n: episode_kpi(passive_ser, cells[n]["net"], cells[n]["episodes"])
        for n in CELLS}
    product["trials_ledger"] = ledger          # r434 pit law: value carried
    product["judgment_note"] = ("judged per prereg s4 via shared library "
                                "(batch_cells=2003 s0 counting law; s4's "
                                "'batch_cells=3' is the judged-cell "
                                "shorthand, W1/W3/W4 family reconciliation); "
                                "judged-negative family = slot closed + "
                                "new-evidence reopen note (law s5); "
                                "G2-eligible cell = T-34 fastline "
                                "candidate pool registration face, "
                                "intake walks the CE admission harness "
                                "separately; T0 brake authority stays "
                                "with REGIME_GUARD")
    with open(OUT_JSON + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(product, fh, ensure_ascii=False, indent=1)
    os.replace(OUT_JSON + ".tmp", OUT_JSON)
    _attr_row(BATCH_NAME, BATCH_CELLS, int(ledger["total"]),
              {"g1_pass": {n: gates[n]["g1_prime_v2"]["pass_v2"]
                           for n in gates},
               "g2_eligible": {n: gates[n]["g2"]["eligible_v2"]
                               for n in gates},
               "family_pbo": pbo},
              {"episodes": {n: cells[n]["entries"] for n in CELLS},
               "long_open_strict": {
                   n: P["anchor_faces"]["N%d" % CELL_N[n]]["long_open"]
                   for n in CELLS},
               "tie_maintain_days": {
                   n: P["anchor_faces"]["N%d" % CELL_N[n]]
                   ["tie_maintain_days"] for n in CELLS}})
    return product


# ------------------------------------------------------------------ driver
def cmd_run():
    global SEED
    key = "innovation_quota_w5_icu_ma"
    if key not in SG.SEED_REGISTRY:
        return gate_refuse(f"SEED_REGISTRY key {key} missing (freeze-window "
                           f"registration absent)")
    SEED = SG.SEED_REGISTRY[key]
    t0 = time.time()
    P, err = load_panel()
    if err:
        return gate_refuse(err)
    lo = P["lo"]
    print(f"panel ok: {P['panel_face']['rows']} rows, lo={lo} "
          f"({time.time() - t0:.0f}s)", flush=True)
    passive_ser = passive_series(P["ret"], lo)
    passive_stats = _cell_stats(passive_ser)
    passive_stats["sharpe"] = passive_stats["sharpe_full"]  # alias face
    cells = {}
    for name in CELLS:
        st = P["states"]["N%d" % CELL_N[name]]
        state = state_machine(st["above"], st["below"], st["dec"])
        pos_end = state_pos_end(state)
        raw_flips = raw_side_transitions(st["above"], st["below"],
                                        st["dec"])
        pos, gross, net, flips = position_series(pos_end, P["ret"], lo)
        net2 = gross - 2 * COST_X1_RATE * flips     # x2 disclosure column
        eps, entries = episodes_of(pos)
        cells[name] = {"pos": pos, "gross": gross, "net": net,
                       "stats": _cell_stats(net), "entries": entries,
                       "episodes": eps, "raw_side_transitions": raw_flips,
                       "stats_x2": _cell_stats(net2)}
        print(f"  cell {name}: sharpe_x1="
              f"{cells[name]['stats']['sharpe_full']} "
              f"pos_days={int(pos.sum())} episodes={entries} "
              f"raw_side_transitions={raw_flips} "
              f"({time.time() - t0:.0f}s)", flush=True)
    nulls = {}
    for name in CELLS:
        held = int(cells[name]["pos"].sum())
        nulls[name] = run_nulls(name, held, P["ret"], lo)
        print(f"  nulls {name}: mu={nulls[name]['coverage']['mu']} "
              f"sigma={nulls[name]['coverage']['sigma']} "
              f"({time.time() - t0:.0f}s)", flush=True)
    series_by_face = {n: cells[n]["net"] for n in CELLS}
    vstarts = virtual_starts(series_by_face, passive_ser)
    splits = split_windows({**series_by_face,
                            "PASSIVE-510300-BH": passive_ser})
    d6 = d6_block(P, series_by_face)
    xfaces = {"extreme": extreme_face(P, cells)}
    mfaces = maintain_face(P, cells)
    product = phase1_write(P, cells, passive_stats, nulls, vstarts, splits,
                           d6, xfaces, mfaces)
    print(f"phase-1 product written ({time.time() - t0:.0f}s)", flush=True)
    product = finalize(product, P, cells, passive_ser)
    print(f"finalize ok: cells={len(cells)} "
          f"ledger={product['trials_ledger']['total']} "
          f"elapsed={time.time() - t0:.0f}s")
    return 0


# ------------------------------------------------------------------ selftest
def _mk_icu_fixture(tmp):
    """Synthetic 510300-like panel: geometric price walk + planted
    trend/crash/recovery segments so the ICU robust-regression state
    machine crosses above and below on every N (plus linear segments
    that exercise the tie-maintain face via exact endpoint landing)."""
    global PANEL_CSV
    dates = pd.bdate_range("2012-05-28", end="2026-09-22")
    n = len(dates)
    rng = np.random.default_rng(7)
    ret = rng.normal(0.0002, 0.010, n)
    crash = n // 2
    ret[crash] = -0.1005
    ret[crash + 1] = 0.0999
    ret[100:400] += 0.0015          # planted mild uptrend
    ret[600:700] -= 0.004           # planted downtrend (below face)
    ret[1500:1560] += 0.003
    ret[2000:2060] -= 0.003
    ret[2600:2660] += 0.003
    close = 3.0 * np.cumprod(1.0 + ret)
    vol = 1e6 * (1.0 + 0.25 * np.sin(np.arange(n) / 13.0))
    df = pd.DataFrame({
        "date": dates.strftime("%Y-%m-%d"),
        "open": close * 0.999, "high": close * 1.01, "low": close * 0.99,
        "close": close, "volume": vol, "amount": close * vol,
    })
    PANEL_CSV = os.path.join(tmp, "sh510300.csv")
    df.to_csv(PANEL_CSV, index=False)
    return df


def cmd_selftest():
    global OUT_DIR, NULL_DIR, OUT_JSON, OUT_DIR_RESULTS, ATT_JSON, SEED, \
        K_NULLS, NULL_SHARDS, K_STARTS, K_SPLITS, PANEL_ROWS, PANEL_FIRST, \
        PANEL_LAST, ANCHOR, EXTREME_EXPECT, EXTREME_OPEN_EXPECT, \
        INTRA_EXPECT, MR_LOADER, PANEL_CSV
    tmp = tempfile.mkdtemp(prefix="innovation_quota_w5_selftest_")
    K_NULLS, NULL_SHARDS = 40, 2     # >= 30: skill_line_v2 thin-pool floor
    K_STARTS, K_SPLITS = 12, 6
    SEED = 20322500

    def _stub_corr(a, b, min_overlap=20):
        j = pd.concat([a, b], axis=1, join="inner").dropna()
        if len(j) < min_overlap:
            return None, int(len(j))
        v = float(np.corrcoef(j.iloc[:, 0], j.iloc[:, 1])[0, 1])
        return round(v, 4), int(len(j))

    MR_LOADER = (lambda: (
        {"M1": pd.Series(np.sin(np.arange(800) / 30.0) * 0.01,
                         index=pd.bdate_range("2020-01-01", periods=800))},
        _stub_corr, ["M1"]))
    # tmp-path reassignment FIRST: every face (nulls included) must stay
    # hermetic -- a late reassignment poisons the real nulls_w5 dir with
    # selftest-sized shards (W3 resume-broadcast crash lineage)
    OUT_DIR = os.path.join(tmp, "results", "innovation_quota")
    NULL_DIR = os.path.join(OUT_DIR, "nulls_w5")
    OUT_JSON = os.path.join(OUT_DIR, "ICU-MA-TIMING-P1.json")
    OUT_DIR_RESULTS = os.path.dirname(OUT_DIR)
    os.makedirs(NULL_DIR, exist_ok=True)
    ATT_JSON = os.path.join(tmp, "attr.json")
    json.dump({"entries": []}, open(ATT_JSON, "w"))
    ok = []
    try:
        # ---- ICU hand-check: scipy vs manual RM endpoint (probe
        # cross-check family; probe tolerance 1e-9 rel, 50/50 exact)
        ys = np.array([3.0, 3.1, 3.2, 3.3, 3.4])   # perfect linear
        sl, ic = siegelslopes(ys, np.arange(5, dtype=float),
                              method="hierarchical")
        ok.append(("ICU perfect-linear endpoint == last value "
                   "(tie face)",
                   abs((ic + sl * 4) - ys[-1]) < 1e-12))
        y7 = np.array([3.0, 2.9, 3.05, 3.2, 3.15, 3.3, 3.25])
        sl7, ic7 = siegelslopes(y7, np.arange(7, dtype=float),
                               method="hierarchical")
        ok.append(("manual RM == scipy RM on noisy window",
                   abs(manual_rm_endpoint(y7) - (ic7 + sl7 * 6)) <=
                   1e-9 * max(1.0, abs(ic7 + sl7 * 6))))
        # first valid idx = N-1 (rolling window law)
        s5 = icu_series(pd.Series(np.arange(50, dtype=float)), 5)
        ok.append(("icu_series first valid idx = N-1",
                   int(s5.first_valid_index()) == 4))

        # ---- tie-maintain state machine hand-check (prereg s2(a))
        # above, tie, tie, below, tie, above -> T T T F F T
        above = pd.Series([True, False, False, False, False, True])
        below = pd.Series([False, False, False, True, False, False])
        dec = pd.Series([True] * 6)
        st = state_machine(above, below, dec)
        ok.append(("tie-maintain: carry through ties, flip on cross",
                   list(st.astype(int)) == [1, 1, 1, 0, 0, 1]))
        # warmup days hold flat before first decidable
        st2 = state_machine(pd.Series([False, True, True]),
                            pd.Series([False, False, False]),
                            pd.Series([False, True, True]))
        ok.append(("warmup days hold initial flat",
                   list(st2.astype(int)) == [0, 1, 1]))
        # raw side transitions: above,tie,below,below,tie,above = 4
        rt = raw_side_transitions(pd.Series([True, False, False, False,
                                             False, True]),
                                  pd.Series([False, False, True, True,
                                             False, False]),
                                  pd.Series([True] * 6))
        ok.append(("raw side transitions count via-tie doubles",
                   rt == 4))

        # ---- T+1 onset semantics via position_series
        state = pd.Series([False, True, True, False, False, True,
                           False, False, False, False])
        pos_end = state_pos_end(state)
        ret_arr = np.array([0.01, 0.02, 0.03, -0.04, 0.05, 0.06,
                            0.0, 0.0, 0.0, 0.0])
        pos, gross, net, flips = position_series(pos_end, ret_arr, 2)
        # window days 2..9: pos[t] = pos_end[1+t] = state[1+t]
        # -> [state2,state3,...,state9]=[T,T,F,F,T,F,F,F]
        ok.append(("pos = state(t-1) T+1 onset face",
                   list(pos.astype(float)) ==
                   [1, 1, 0, 0, 1, 0, 0, 0]))
        # cost: entry flip booked on first accrual day + re-entry + exit
        ok.append(("cost booking x1 on |dpos| next day",
                   abs(net[0] - (ret_arr[2] - COST_X1_RATE)) < 1e-12
                   and abs(net[4] - (ret_arr[6] - COST_X1_RATE)) < 1e-12
                   and abs(net[5] - (0.0 - COST_X1_RATE)) < 1e-12))
        eps, entries = episodes_of(pos)
        ok.append(("episodes = contiguous runs (2 entries)",
                   entries == 2 and eps == [(0, 2), (4, 5)]))

        # ---- uniform-day null: exposure preserved, placement uniform
        n_t = 10
        domain = np.arange(1, n_t)      # lo-1=1 domain
        npos = uniform_day_null(domain, 3, n_t,
                                np.random.default_rng([SEED, 0]))
        ok.append(("null preserves position-day count",
                   int(npos.sum()) == 3 and
                   not npos[0]))          # domain excludes idx 0

        # ---- fixture derive-then-freeze (W3/W4 pattern); anchors are
        # derived from the CSV-READ frame (not the in-memory frame):
        # pandas to_csv float round-trip is not bitwise-exact (691/3737
        # last-ULP drifts measured), and the ICU endpoint often lands
        # exactly on close (tie face) -> above/below/tie classification
        # is ULP-sensitive; deriving from the read-back frame makes
        # selftest anchors and load_panel see identical bits (real-data
        # path unaffected: probe and runner read the same real CSV).
        df = _mk_icu_fixture(tmp)
        cut_df = pd.read_csv(PANEL_CSV)
        cut_df["date"] = cut_df["date"].astype(str)
        PANEL_ROWS = len(cut_df)
        PANEL_FIRST = str(cut_df["date"].iloc[0])
        PANEL_LAST = str(cut_df["date"].iloc[-1])
        close = cut_df["close"]
        new_anchor = {}
        new_extreme = {}
        new_ext_open = {}
        icus_f = {}
        for name, n in CELL_N.items():
            n_key = "N%d" % n
            icu = icu_series(close, n)
            icus_f[n_key] = icu
            dec = icu.notna()
            above_f = close > icu
            below_f = close < icu
            tie_f = (close == icu) & dec
            new_anchor[n_key] = {
                "decidable": int(dec.sum()),
                "first_decidable_bar_idx": int(np.argmax(dec.values)),
                "long_open": int(above_f.sum()),
                "flat_open": int(below_f.sum()),
                "tie_maintain_days": int(tie_f.sum()),
                "open_rate": round(float(above_f.sum() / dec.sum()), 6)}
            ext_d, cnt = {}, 0
            for day in EXTREME_DAYS:
                idx = cut_df.index[cut_df["date"] == day]
                if len(idx) == 0:
                    continue
                i = int(idx[0])
                stx = ("long_above" if bool(above_f.iloc[i]) else
                       "flat_below" if bool(below_f.iloc[i]) else
                       "tie" if bool(tie_f.iloc[i]) else "warmup")
                ext_d[day] = (stx, round(float(icu.iloc[i]), 4),
                              round(float(close.iloc[i]), 4))
                if stx == "long_above":
                    cnt += 1
            new_extreme[n_key] = ext_d
            new_ext_open[n_key] = cnt
        ANCHOR = new_anchor
        EXTREME_EXPECT = new_extreme
        EXTREME_OPEN_EXPECT = new_ext_open
        new_intra = {}
        for pair in INTRA_EXPECT:
            a_k, b_k = pair.split("_vs_")
            ia, ib = icus_f[a_k], icus_f[b_k]
            la = (close > ia) & ia.notna()
            lb = (close > ib) & ib.notna()
            both = ia.notna() & ib.notna()
            new_intra[pair] = {
                "both_dec": int(both.sum()),
                "both_long": int((la & lb & both).sum()),
                "a_in_b": round(float((la & lb).sum()) /
                                float(la.sum()), 4) if la.sum() else None,
                "b_in_a": round(float((la & lb).sum()) /
                                float(lb.sum()), 4) if lb.sum() else None}
        INTRA_EXPECT = new_intra
        ok.append(("fixture has both above and below crossings",
                   all(new_anchor[k]["long_open"] > 0 and
                       new_anchor[k]["flat_open"] > 0
                       for k in new_anchor)))

        # ---- full pipeline on fixture
        P, err = load_panel()
        ok.append(("panel/anchor gates pass on fixture", err is None))
        if err:
            raise RuntimeError(err)
        lo = P["lo"]
        ok.append(("batch window lo = max(first_decidable)+1",
                   lo == max(f["first_decidable_bar_idx"]
                             for f in P["anchor_faces"].values()) + 1))
        passive_ser = passive_series(P["ret"], lo)
        cells = {}
        for name in CELLS:
            st = P["states"]["N%d" % CELL_N[name]]
            state = state_machine(st["above"], st["below"], st["dec"])
            pos_end = state_pos_end(state)
            raw_flips = raw_side_transitions(st["above"], st["below"],
                                            st["dec"])
            pos, gross, net, flips = position_series(pos_end, P["ret"], lo)
            eps, entries = episodes_of(pos)
            cells[name] = {"pos": pos, "gross": gross, "net": net,
                           "stats": _cell_stats(net), "entries": entries,
                           "episodes": eps,
                           "raw_side_transitions": raw_flips}
        ok.append(("3 cells + passive derive finite",
                   all(np.isfinite(cells[c]["stats"]["sharpe_full"])
                       for c in cells)
                   and np.isfinite(_cell_stats(passive_ser)["sharpe_full"])))
        ok.append(("N5 episodes <= raw side transitions (tie-maintain "
                   "law face)",
                   cells["ICU-N5"]["entries"] <=
                   cells["ICU-N5"]["raw_side_transitions"] + 2))
        n1 = run_nulls("ICU-N5", int(cells["ICU-N5"]["pos"].sum()),
                       P["ret"], lo)
        n2 = run_nulls("ICU-N5", int(cells["ICU-N5"]["pos"].sum()),
                       P["ret"], lo)
        ok.append(("nulls deterministic (npy resume) + size",
                   n1["values"] == n2["values"]
                   and len(n1["values"]) == K_NULLS))
        ok.append(("null exposure preserved (face contract)",
                   "uniform random day placement" in n1["face"]))
        series_by_face = {n: cells[n]["net"] for n in CELLS}
        vstarts = virtual_starts(series_by_face, passive_ser)
        splits = split_windows({**series_by_face,
                                "PASSIVE-510300-BH": passive_ser})
        d6 = d6_block(P, series_by_face)
        xfaces = {"extreme": extreme_face(P, cells)}
        mfaces = maintain_face(P, cells)
        ok.append(("vstarts/splits/d6 shapes",
                   set(vstarts["cells"]) == set(CELLS)
                   and all(set(vstarts["cells"][c]) == set(WIN_DAYS)
                           for c in vstarts["cells"])
                   and all("segment_stable" in splits[s] for s in splits)
                   and not d6["cells"]["ICU-N5"]["reject"]))
        ok.append(("extreme face: per-cell 7-day states + worst/best",
                   all(len(xfaces["extreme"]["cells"][c]["extreme_days"])
                       == len(EXTREME_DAYS) for c in CELLS)
                   and "worst_day" in xfaces["extreme"]))
        ok.append(("maintain-face year distribution (s2(a) column)",
                   all("tie_maintain_days_by_year" in mfaces[c]
                       for c in CELLS)
                   and sum(mfaces["ICU-N5"]["tie_maintain_days_by_year"]
                           .values()) ==
                   mfaces["ICU-N5"]["tie_maintain_days_total"]))
        nulls_all = {n: run_nulls(n, int(cells[n]["pos"].sum()),
                                  P["ret"], lo) for n in CELLS}
        product = phase1_write(P, cells, _cell_stats(passive_ser),
                               nulls_all, vstarts, splits, d6, xfaces,
                               mfaces)
        ok.append(("phase-1 product fields",
                   os.path.exists(OUT_JSON)
                   and product["evidence_cutoff"] == EVIDENCE_CUTOFF
                   and "cutoff_meta" in product
                   and product["panel"]["batch_lo"] == lo
                   and set(product["legs_face"]) == set(CELLS)))

        # ---- r450 landed-state guard: judged product refuses re-run
        with open(OUT_JSON + ".tmp2", "w", encoding="utf-8") as fh:
            json.dump({"trials_ledger": {"prev_total": 1, "total": 2}},
                      fh)
        os.replace(OUT_JSON + ".tmp2", OUT_JSON)
        ok.append(("r450 guard: judged product refuses (rc=2 face)",
                   _refuse_if_judged() == 2))
        # phase-1-only product (no ledger) resumes
        phase1_write(P, cells, _cell_stats(passive_ser), nulls_all,
                     vstarts, splits, d6, xfaces, mfaces)
        ok.append(("r450 guard: phase-1-only product resumes",
                   _refuse_if_judged() == 0))

        # shared-library stateful faces stubbed (hermetic isolation)
        _ne, _al, _lh = SG.n_eff, SG.append_ledger, SG.ledger_head
        SG.n_eff = lambda bc, rd=None: int(bc)
        SG.append_ledger = lambda *a, **k: {"prev_total": 0, "total": 100,
                                            "batch": BATCH_NAME}
        SG.ledger_head = lambda rd=None: {"total": 500, "file": None,
                                          "note": None}
        _real_cscv = globals()["cscv_pbo"]
        globals()["cscv_pbo"] = lambda mat: {"pbo": 0.1}
        try:
            product = finalize(product, P, cells, passive_ser)
            ok.append(("finalize product fields",
                       os.path.exists(OUT_JSON)
                       and product["evidence_cutoff"] == EVIDENCE_CUTOFF
                       and len(product["gates"]) == 3
                       and all("g2" in g for g in product["gates"].values())
                       and product["trials_ledger"]["total"] == 100
                       and product["passive_override_fed"] ==
                       product["passive"]["passive_510300_bh"]["full"]
                       ["sharpe_full"]))
            ok.append(("episode kpi face (O-1524 trade-level + lineage)",
                       all("win_rate_vs_passive_same_days"
                           in product["episode_kpi"][n]
                           and "win_rate_trade_level"
                           in product["episode_kpi"][n]
                           for n in CELLS)))
            att = json.load(open(ATT_JSON, encoding="utf-8"))
            ok.append(("attrition row + funnel dual columns",
                       att["entries"][-1]["batch"] == BATCH_NAME
                       and product["funnel"]["harvest_column"] == 1))
        finally:
            SG.n_eff, SG.append_ledger, SG.ledger_head = _ne, _al, _lh
            globals()["cscv_pbo"] = _real_cscv

        # ---- gate-refusal paths (drift -> refuse, not corruption)
        real_rows = PANEL_ROWS
        PANEL_ROWS = real_rows + 1
        _, err2 = load_panel()
        ok.append(("G-PANEL drift refusal", err2 is not None
                   and "rows" in str(err2)))
        PANEL_ROWS = real_rows
        real_long = ANCHOR["N5"]["long_open"]
        ANCHOR["N5"] = dict(ANCHOR["N5"], long_open=real_long + 1)
        _, err3 = load_panel()
        ok.append(("G-ANCHOR face drift refusal", err3 is not None
                   and "G-ANCHOR" in str(err3)))
        ANCHOR["N5"] = dict(ANCHOR["N5"], long_open=real_long)
        real_ext = EXTREME_OPEN_EXPECT["N5"]
        EXTREME_OPEN_EXPECT["N5"] = real_ext + 1
        _, err4 = load_panel()
        ok.append(("G-ANCHOR extreme-open drift refusal", err4 is not None
                   and "extreme_open" in str(err4)))
        EXTREME_OPEN_EXPECT["N5"] = real_ext
        real_intra = INTRA_EXPECT["N5_vs_N120"]["both_long"]
        INTRA_EXPECT["N5_vs_N120"] = dict(INTRA_EXPECT["N5_vs_N120"],
                                          both_long=real_intra + 1)
        _, err6 = load_panel()
        ok.append(("G-ANCHOR intra drift refusal", err6 is not None
                   and "intra" in str(err6)))
        INTRA_EXPECT["N5_vs_N120"] = dict(INTRA_EXPECT["N5_vs_N120"],
                                          both_long=real_intra)
        _, err5 = load_panel()
        ok.append(("anchor restored -> gates pass again", err5 is None))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    n_ok = sum(1 for _, v in ok if v)
    print(f"innovation_quota_w5 selftest: {n_ok}/{len(ok)} PASS")
    for name, v in ok:
        if not v:
            print(f"  FAIL: {name}")
    return 0 if n_ok == len(ok) else 1


# ------------------------------------------------------------------ guard
def _refuse_if_judged():
    """r450 landed-state guard: read CONTENT (trials_ledger block), not
    existence/timestamps. Judged product refuses re-run (rc=2) unless
    INNOVATION_QUOTA_W5_REFINALIZE=1; phase-1-only product resumes."""
    if not os.path.exists(OUT_JSON):
        return 0
    try:
        with open(OUT_JSON, encoding="utf-8") as fh:
            old = json.load(fh)
    except Exception:
        return 0        # unreadable partial write -> resume path
    if (old.get("trials_ledger") or {}).get("total") is not None and \
            os.environ.get("INNOVATION_QUOTA_W5_REFINALIZE") != "1":
        print("GATE-REFUSE(exit2): ICU-MA-TIMING-P1.json already "
              "judged (trials_ledger present, content-read per r450); "
              "INNOVATION_QUOTA_W5_REFINALIZE=1 = only redo")
        return 2
    return 0


def main():
    try:
        # r236 GBK-console law: reconfigure at entry (idempotent, must
        # not depend on last round's output having no unencodable chars)
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "selftest"])
    a = ap.parse_args()
    if a.cmd == "selftest":
        return cmd_selftest()
    guard = _refuse_if_judged()
    if guard:
        return guard
    return cmd_run()


if __name__ == "__main__":
    sys.exit(main())
