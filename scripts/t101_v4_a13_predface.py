"""T-101-V4-A13-PREDFACE batch runner
(research/T-101-V4_A13_PREDFACE_PREREG.md, FROZEN r446 bm-a).

Input-feature route residual face: pure predictor (forecast / walk-forward)
INFORMATIONAL verdict -- Spearman rank IC of four frozen features vs 20-day
forward returns, stride-20 non-overlapping rebalance calendar, RAW face
(member's own forward return) and RESID face (leave-one-out peer-demeaned).
No portfolio construction anywhere (sec.1: information face; any downstream
conversion still faces the D6 beta-domination gate of the five closed
sublines -- pre-declared).

Subcommands (prereg s6 frozen set: run / selftest):
  run       fv gate checks -> per-member frozen features (probe verbatim)
            -> RAW windows (member own calendar, per-feature decidable) +
            RESID window (U5 master intersection, AND decidable, A11 law)
            -> 40 cells x {full/IS/OOS IC, circular-shift null pool K=200 on
            the rebalance pair array (empirical two-sided p + z, nan-safe),
            circular block bootstrap B=2000 block=10 percentile CI} -> FV
            verdict on the 12 IS-eligible cells (|IC_OOS|>=0.10 & p<0.05 &
            IS/OOS same sign & full/OOS same sign) + reading layer 28 cells
            (supply-note flag only) -> results/t101_v4_a13_predface.json
            (evidence_cutoff + cutoff_meta top level; append_ledger return
            MUST land in out["trials_ledger"] -- r442 law).
  selftest  offline engineering gates: contiguity fail-closed fixture,
            shift-null determinism, LOO-demean exact math, bootstrap CI
            fixture (monotone pairs exclude 0; constant feature NaN path),
            verdict-clause boundary math, IC nan-filter, RAW fwd math.

Frozen rng streams (prereg s3):
  shift nulls full  = rng([SCRNULL_BASE, cell_idx])           20318500 face
  shift nulls OOS   = rng([SCRNULL_BASE, 100000 + cell_idx])  derived stream
  bootstrap  full  = rng([UNC_BASE, cell_idx])                20319000 face
  bootstrap  OOS   = rng([UNC_BASE, 100000 + cell_idx])       derived stream
Declared base = actual base by construction (A12 rebind law: this batch
does not route through fv.dual_nulls; no inherited-base mismatch face).
"""
import argparse
import json
import os
import sys
import time

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

if hasattr(sys.stdout, "encoding") and sys.stdout.encoding \
        and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # r236 GBK law
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import science_gates as sg                     # noqa: E402
import t101_v4_a2_prescreen as tpl             # noqa: E402
import t101_v4_a158_fv as fv                   # noqa: E402
import a158_tsgate_probe as probe              # noqa: E402

EVIDENCE_CUTOFF = "2026-09-29"                 # prereg s2 forward lockbox
SPLIT = tpl.SPLIT                              # 2017-01-01 family constant
STRIDE = 20                                    # non-overlap rebalance grid
FWD = 20                                       # forward horizon (own tds)
MEMBERS = ["510300", "510050", "510500", "512100", "588000"]
IS_ELIGIBLE = ["510300", "510050", "510500"]  # RAW-face FV eligibility
FEATURES = ["f_rsv30", "f_c2", "f_roc20", "f_std20"]
FACES = ["raw", "resid"]
NULL_K = 200                                   # circular-shift nulls per cell
BOOT_B = 2000                                  # circular block bootstrap draws
BOOT_BLOCK = 10                                # bootstrap block length
IC_MAG = 0.10                                  # |IC_OOS| magnitude clause
P_ALPHA = 0.05                                 # shift-null empirical alpha
MIN_IS_PAIRS = 15                              # IS confirmability floor
MIN_OOS_PAIRS = 15                             # supply-note flag floor
SCRNULL_BASE = sg.SEED_REGISTRY["t101_v4_a13_predface_scrnull"]   # 20318500
UNC_BASE = sg.SEED_REGISTRY["t101_v4_a13_predface_unc"]           # 20319000
STREAM_SEG_OFFSET = 100000                     # OOS-segment derived-stream id
A13_ANCHOR_ROWS = {"510300": 3487, "510050": 5252, "510500": 3290,
                   "512100": 2406, "588000": 1426}
ANCHOR_FACE = {c: f"data/daily/sh{c}.csv" for c in MEMBERS}
PREREG_REL = "research/T-101-V4_A13_PREDFACE_PREREG.md"
RESULTS_JSON = os.path.join(os.path.dirname(HERE), "results",
                            "t101_v4_a13_predface.json")


def _fail(msg: str):
    print("FAIL-CLOSED: %s" % msg)
    raise SystemExit(2)


# ------------------------------------------------------------- frozen loader

def load_panel(code: str) -> pd.DataFrame:
    path = ANCHOR_FACE[code]
    if not os.path.exists(path):
        _fail("G-ANCHOR VOID: declared anchor %s missing" % path)
    df = pd.read_csv(path)                     # raw direct read (four-tuple)
    df["date"] = df["date"].astype(str)
    df = df[df["date"] <= EVIDENCE_CUTOFF].reset_index(drop=True)
    if df.empty or df["date"].iloc[-1] != EVIDENCE_CUTOFF:
        _fail("FACE-MISMATCH VOID: %s tail != %s" % (code, EVIDENCE_CUTOFF))
    if len(df) != A13_ANCHOR_ROWS[code]:
        _fail("G-ANCHOR VOID: %s rows %d != frozen anchor %d"
              % (code, len(df), A13_ANCHOR_ROWS[code]))
    return df


# ----------------------------------------------------- feature construction

def member_features(df: pd.DataFrame):
    """Per-member frozen feature frame (A11 verbatim semantics + f_std20 per
    A12 sig_i). Returns (feats: name -> (value_series, dec_bool_array),
    close_series, dates)."""
    dates = pd.DatetimeIndex(df["date"])
    F = probe.alpha158_factors(df)
    if len(F) != probe.N_FACTORS:
        _fail("G-FACTORS VOID: factor table %d != %d"
              % (len(F), probe.N_FACTORS))
    gates = {g[0]: (g[1], g[2]) for g in probe.gate_universe(F)}
    miss = [g for g in fv.GATES17 if g not in gates]
    if miss:
        _fail("G-FACTORS VOID: gates absent from gate_universe: %s" % miss)
    c2 = pd.concat([gates[g][0].astype(float) for g in fv.GATES17],
                   axis=1).mean(axis=1)
    c2dec = pd.Series(True, index=df.index)
    for g in fv.GATES17:
        c2dec = c2dec & gates[g][1]
    ret = df["close"].pct_change()
    std20 = ret.rolling(20).std()              # A12 sig_i semantics, ddof=1
    feats = {
        "f_rsv30": (pd.Series(F["RSV30"].values, index=dates),
                    F["RSV30"].notna().values),
        "f_c2": (pd.Series(c2.values, index=dates), c2dec.values),
        "f_roc20": (pd.Series(F["ROC20"].values, index=dates),
                    F["ROC20"].notna().values),
        "f_std20": (pd.Series(std20.values, index=dates),
                    std20.notna().values),
    }
    close = pd.Series(df["close"].values, index=dates)
    return feats, close, dates


def _contiguous_positions(dec: np.ndarray, tag: str) -> np.ndarray:
    pos = np.flatnonzero(dec)
    if len(pos) == 0:
        _fail("G-WINDOW VOID: %s empty decidable mask" % tag)
    if pos[-1] - pos[0] + 1 != len(pos):
        _fail("G-CONTIGUITY VOID: %s decidable mask not contiguous "
              "(warmup structure broken)" % tag)
    return pos


# ------------------------------------------------------------ cell machinery

def cell_pairs_raw(feat_vals, dec, close_full, n_panel, dates):
    """RAW face: member own-calendar window from the feature's decidable
    start; stride-20 rebalance grid over the window; fwd20 by panel position
    (20 own trading days); tail rebalances without a full forward window
    are dropped."""
    pos = _contiguous_positions(dec, "raw")
    n = len(pos)
    rebal = np.arange(0, n, STRIDE)
    keep = rebal[rebal + FWD <= n_panel - 1 - pos[0]]
    idx = pos[keep]                            # panel positions
    feat = feat_vals[idx]
    fwd = close_full[idx + FWD] / close_full[idx] - 1.0
    return feat, fwd, dates[idx]


def resid_pairs_master(feat_frames, close_frames, dec_frames, member, feature,
                       master):
    """RESID face: U5 master intersection window (A11 AND-decidability law);
    LOO peer-demeaned fwd20 target for `member`."""
    dec = None
    for m in MEMBERS:
        d = dec_frames[feature][m].reindex(master).fillna(False).astype(bool)
        dec = d if dec is None else (dec & d)
    pos = _contiguous_positions(dec.values, "resid|%s|%s" % (member, feature))
    n_panel = len(master)
    v0 = pos[0]
    n = len(pos)
    rebal = np.arange(0, n, STRIDE)
    keep = rebal[v0 + rebal + FWD <= n_panel - 1]
    wpos = pos[keep]                            # master window positions
    fwd = {}
    for m in MEMBERS:
        c = close_frames[m].reindex(master).values
        fwd[m] = c[wpos + FWD] / c[wpos] - 1.0
    peer = [fwd[m] for m in MEMBERS if m != member]
    resid = fwd[member] - np.mean(peer, axis=0)   # LOO peer mean
    feat = feat_frames[feature][member].reindex(master).values[wpos]
    return feat, resid, master[wpos]


def _ic(x, y):
    """Spearman IC, nan-safe: valid-pair filter + nan_excluded count."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    ok = ~(np.isnan(x) | np.isnan(y))
    nan_ex = int((~ok).sum())
    if int(ok.sum()) < 3:
        return float("nan"), int(ok.sum()), nan_ex
    r = spearmanr(x[ok], y[ok]).statistic
    return float(r), int(ok.sum()), nan_ex


def shift_null_pool(x, y, cell_idx, stream_base):
    """K=200 circular-shift nulls on the rebalance pair array (offsets in
    [1, n_pairs-1], rng([stream_base, cell_idx])); same pair positions, same
    targets -> null IC values."""
    n = len(x)
    if n < 3:
        return np.array([])
    rng = np.random.default_rng([int(stream_base), int(cell_idx)])
    offs = rng.integers(1, n, size=NULL_K)     # n>=3 -> valid range
    ics = np.full(NULL_K, np.nan)
    for k in range(NULL_K):
        ics[k], _, _ = _ic(np.roll(x, int(offs[k])), y)
    return ics


def _pool_summary(v, ic):
    """nan-safe summary + empirical two-sided p (r442 law)."""
    if len(v) == 0 or np.isnan(ic):
        return {"mu": float("nan"), "sigma": float("nan"), "n": int(len(v)),
                "nan": NULL_K - int(len(v)), "p_two": float("nan"),
                "z": float("nan")}
    sigma = float(v.std(ddof=1)) if len(v) > 1 else 0.0
    z = float((ic - float(v.mean())) / sigma) if sigma > 0 else float("nan")
    return {"mu": float(v.mean()), "sigma": sigma, "n": int(len(v)),
            "nan": NULL_K - int(len(v)),
            "p_two": float((1.0 + np.count_nonzero(np.abs(v) >= abs(ic)))
                           / (len(v) + 1.0)), "z": z}


def block_bootstrap_ci(x, y, cell_idx, stream_base):
    """Circular block bootstrap B=2000 block=10 on the pair index
    (rng([stream_base, cell_idx])); percentile CI 2.5/97.5."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    ok = ~(np.isnan(x) | np.isnan(y))
    xs, ys = x[ok], y[ok]
    n = len(xs)
    if n < BOOT_BLOCK + 3:
        return {"lo": float("nan"), "hi": float("nan"), "n": int(n),
                "nan_draws": 0}
    rng = np.random.default_rng([int(stream_base), int(cell_idx)])
    n_blocks = int(np.ceil(n / BOOT_BLOCK))
    starts = rng.integers(0, n, size=(BOOT_B, n_blocks))
    offs = np.arange(BOOT_BLOCK)
    ics = np.full(BOOT_B, np.nan)
    nan_draws = 0
    for b in range(BOOT_B):
        idx = ((starts[b][:, None] + offs[None, :]).ravel() % n)[:n]
        r, _, _ = _ic(xs[idx], ys[idx])
        if np.isnan(r):
            nan_draws += 1
        ics[b] = r
    v = ics[~np.isnan(ics)]
    if len(v) < 100:
        return {"lo": float("nan"), "hi": float("nan"), "n": int(n),
                "nan_draws": nan_draws}
    return {"lo": float(np.percentile(v, 2.5)),
            "hi": float(np.percentile(v, 97.5)), "n": int(n),
            "nan_draws": nan_draws}


def verdict_cell(face, member, ic_is, n_is, ic_oos, n_oos, ic_full, p_oos):
    """Frozen FV clauses (prereg s4). IS-eligible = RAW x {510300, 510050,
    510500} x n_IS >= 15. Reading layer: supply-note flag = OOS p<0.05 with
    n_OOS >= 15 (no IS confirmation structurally possible -> disclosed)."""
    eligible = (face == "raw" and member in IS_ELIGIBLE
                and n_is >= MIN_IS_PAIRS)
    out = {"fv_eligible": bool(eligible), "n_is": int(n_is),
           "n_oos": int(n_oos)}
    if eligible:
        c_mag = (not np.isnan(ic_oos)) and abs(ic_oos) >= IC_MAG
        c_p = (not np.isnan(p_oos)) and p_oos < P_ALPHA
        c_is = (not np.isnan(ic_is)) and np.sign(ic_is) == np.sign(ic_oos)
        c_full = (not np.isnan(ic_full)) and np.sign(ic_full) == np.sign(ic_oos)
        out["clauses"] = {"mag": bool(c_mag), "p": bool(c_p),
                          "is_sign": bool(c_is), "full_sign": bool(c_full)}
        out["verdict"] = "FV_PASS" if (c_mag and c_p and c_is and c_full) \
            else "FV_FAIL"
    else:
        flag = (n_oos >= MIN_OOS_PAIRS and not np.isnan(p_oos)
                and p_oos < P_ALPHA)
        out["verdict"] = "READING_OOS_ONLY"
        out["supply_note_flag"] = bool(flag)
    return out


# ---------------------------------------------------------------- main burn

def run() -> int:
    t0 = time.time()
    fv.g_p1_check()
    fv.g_accept_check()
    panels = {m: load_panel(m) for m in MEMBERS}
    prev_head = sg.ledger_head()

    feats_all, close_all, dates_all = {}, {}, {}
    for m in MEMBERS:
        feats_all[m], close_all[m], dates_all[m] = member_features(panels[m])
    print("features built: %d members x %d frozen factors"
          % (len(MEMBERS), probe.N_FACTORS))

    master = None
    for m in MEMBERS:
        master = dates_all[m] if master is None \
            else master.intersection(dates_all[m])
    feat_frames = {f: {m: feats_all[m][f][0] for m in MEMBERS}
                   for f in FEATURES}
    dec_frames = {f: {m: pd.Series(feats_all[m][f][1],
                                   index=dates_all[m]) for m in MEMBERS}
                  for f in FEATURES}
    close_frames = {m: close_all[m] for m in MEMBERS}

    # feature cross-correlation disclosure (per member, common decidable)
    xcorr = {}
    for m in MEMBERS:
        base = None
        for f in FEATURES:
            d = feats_all[m][f][1]
            base = d if base is None else (base & d)
        pos = np.flatnonzero(base)
        mat = {}
        for a in FEATURES:
            for b in FEATURES:
                if a < b:
                    xa = feats_all[m][a][0].values[pos]
                    xb = feats_all[m][b][0].values[pos]
                    r, n, _ = _ic(xa, xb)
                    mat["%s~%s" % (a, b)] = {"spearman": r, "n": n}
        xcorr[m] = mat

    cells = []
    cell_idx = 0
    for face in FACES:
        for m in MEMBERS:
            for f in FEATURES:
                if face == "raw":
                    feat_series, dec = feats_all[m][f]
                    x, y, dts = cell_pairs_raw(
                        feat_series.values, dec, close_all[m].values,
                        len(panels[m]), dates_all[m])
                else:
                    x, y, dts = resid_pairs_master(
                        feat_frames, close_frames, dec_frames, m, f, master)
                if len(x) == 0:
                    cells.append({"face": face, "member": m, "feature": f,
                                  "cell_idx": cell_idx,
                                  "error": "EMPTY_PAIRS"})
                    cell_idx += 1
                    continue
                ic_full, n_full, nex_full = _ic(x, y)
                is_mask = (dts < pd.Timestamp(SPLIT)).values
                if is_mask.any():
                    ic_is, n_is, nex_is = _ic(x[is_mask], y[is_mask])
                else:
                    ic_is, n_is, nex_is = float("nan"), 0, 0
                if (~is_mask).any():
                    ic_oos, n_oos, nex_oos = _ic(x[~is_mask], y[~is_mask])
                else:
                    ic_oos, n_oos, nex_oos = float("nan"), 0, 0
                # frozen rng streams: full = [BASE, cell]; OOS = [BASE+100k]
                v_full = shift_null_pool(x, y, cell_idx, SCRNULL_BASE)
                x_oos, y_oos = x[~is_mask], y[~is_mask]
                v_oos = shift_null_pool(x_oos, y_oos, cell_idx,
                                        SCRNULL_BASE + STREAM_SEG_OFFSET)
                s_full = _pool_summary(v_full, ic_full)
                s_oos = _pool_summary(v_oos, ic_oos)
                ci_full = block_bootstrap_ci(x, y, cell_idx, UNC_BASE)
                ci_oos = block_bootstrap_ci(x_oos, y_oos, cell_idx,
                                            UNC_BASE + STREAM_SEG_OFFSET)
                v = verdict_cell(face, m, ic_is, n_is, ic_oos, n_oos,
                                 ic_full, s_oos["p_two"])
                cells.append({
                    "face": face, "member": m, "feature": f,
                    "cell_idx": cell_idx,
                    "window": {"first_rebal": str(dts[0].date()),
                               "last_rebal": str(dts[-1].date()),
                               "n_pairs": int(len(x))},
                    "ic": {"full": ic_full, "is": ic_is, "oos": ic_oos},
                    "n_pairs_seg": {"full": n_full, "is": n_is,
                                    "oos": n_oos},
                    "nan_excluded": {"full": nex_full, "is": nex_is,
                                     "oos": nex_oos},
                    "shift_null": {"full": s_full, "oos": s_oos},
                    "boot_ci": {"full": ci_full, "oos": ci_oos},
                    **v,
                })
                print("cell %02d %s|%s|%s IC f/i/o = %+.4f / %+.4f / %+.4f "
                      "p_oos=%.4f n_i=%d n_o=%d %s"
                      % (cell_idx, face, m, f, ic_full, ic_is, ic_oos,
                         s_oos["p_two"], n_is, n_oos, v["verdict"]))
                cell_idx += 1

    fv_cells = [c for c in cells if c.get("fv_eligible")]
    fv_pass = [c for c in fv_cells if c.get("verdict") == "FV_PASS"]
    notes = [c for c in cells if c.get("supply_note_flag")]

    out = {
        "batch": "T-101-V4-A13-PREDFACE",
        "prereg": PREREG_REL,
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "science_gates": sg.cutoff_meta(EVIDENCE_CUTOFF),
        "frozen": {"split": SPLIT, "stride": STRIDE, "fwd": FWD,
                   "features": FEATURES, "faces": FACES,
                   "members": MEMBERS, "null_k": NULL_K, "boot_b": BOOT_B,
                   "boot_block": BOOT_BLOCK, "ic_mag": IC_MAG,
                   "p_alpha": P_ALPHA, "min_is_pairs": MIN_IS_PAIRS,
                   "min_oos_pairs": MIN_OOS_PAIRS,
                   "scrnull_seed": SCRNULL_BASE, "unc_seed": UNC_BASE,
                   "stream_seg_offset": STREAM_SEG_OFFSET,
                   "anchor_rows": A13_ANCHOR_ROWS,
                   "is_eligible_members": IS_ELIGIBLE},
        "fv_eligible_cells": len(fv_cells),
        "fv_pass": len(fv_pass),
        "fv_pass_cells": ["%s|%s|%s" % (c["face"], c["member"], c["feature"])
                          for c in fv_pass],
        "reading_layer": {"n": len(cells) - len(fv_cells),
                          "supply_note_flags":
                          ["%s|%s|%s" % (c["face"], c["member"], c["feature"])
                           for c in notes]},
        "feature_xcorr_disclosure": xcorr,
        "cells": cells,
        "audit": {"elapsed_sec": round(time.time() - t0, 1),
                  "ledger_head_before": prev_head.get("total"),
                  "host": "bm-a", "workers": 1},
    }
    ledger = sg.append_ledger("T-101-V4-A13-PREDFACE", 40,
                              "t101_v4_a13_predface.json",
                              evidence_cutoff=EVIDENCE_CUTOFF)
    out["trials_ledger"] = ledger                     # r442 law
    with open(RESULTS_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print("A13-PREDFACE burn done in %.1fs: FV %d/%d pass, %d supply notes, "
          "ledger total=%s" % (time.time() - t0, len(fv_pass), len(fv_cells),
                               len(notes), ledger.get("total")))
    return 0


# ------------------------------------------------------------- engineering

def selftest() -> int:
    results = []

    def ok(name, cond):
        results.append(bool(cond))
        print(("PASS" if cond else "FAIL") + " " + name)

    # 1. contiguity fail-closed
    try:
        _contiguous_positions(np.array([True, False, True]), "fixture")
        ok("contiguity fail-closed", False)
    except SystemExit:
        ok("contiguity fail-closed", True)

    # 2. shift-null determinism (frozen stream law)
    a1 = np.random.default_rng([SCRNULL_BASE, 0]).integers(1, 100, size=5)
    a2 = np.random.default_rng([SCRNULL_BASE, 0]).integers(1, 100, size=5)
    a3 = np.random.default_rng([SCRNULL_BASE, 1]).integers(1, 100, size=5)
    ok("shift-null determinism",
       bool(np.array_equal(a1, a2)) and not bool(np.array_equal(a1, a3)))

    # 3. LOO-demean exact math
    fwd = {"a": np.array([0.10, 0.20]), "b": np.array([0.30, 0.40]),
           "c": np.array([0.50, 0.60])}
    resid = fwd["a"] - np.mean([fwd["b"], fwd["c"]], axis=0)
    ok("LOO-demean exact",
       bool(np.allclose(resid, [0.10 - 0.40, 0.20 - 0.50])))

    # 4. bootstrap CI: monotone pairs exclude 0; constant feature NaN-safe
    x = np.linspace(1.0, 2.0, 120)
    y = x.copy()
    ci = block_bootstrap_ci(x, y, 999, UNC_BASE)
    ok("bootstrap monotone CI excludes 0", ci["lo"] > 0.0)
    cic = block_bootstrap_ci(np.ones(120), np.linspace(0.0, 1.0, 120),
                             998, UNC_BASE)
    ok("constant-feature CI nan-safe", bool(np.isnan(cic["lo"])))

    # 5. verdict clause boundary math
    v = verdict_cell("raw", "510300", 0.11, 40, 0.10, 100, 0.09, 0.049)
    ok("verdict boundary pass", v["verdict"] == "FV_PASS"
       and v["clauses"] == {"mag": True, "p": True, "is_sign": True,
                            "full_sign": True})
    v2 = verdict_cell("raw", "510300", 0.11, 40, 0.10, 100, -0.09, 0.049)
    ok("verdict full-sign kill", v2["verdict"] == "FV_FAIL")
    v3 = verdict_cell("resid", "510300", float("nan"), 0, 0.20, 60, 0.18,
                      0.02)
    ok("reading-layer flag", v3["verdict"] == "READING_OOS_ONLY"
       and v3["supply_note_flag"] is True)
    v4 = verdict_cell("raw", "512100", 0.5, 50, 0.5, 100, 0.5, 0.01)
    ok("oos-only member reading", v4["verdict"] == "READING_OOS_ONLY")

    # 6. IC nan-safety
    ic, n, nex = _ic(np.array([1.0, np.nan, 3.0, 4.0]),
                     np.array([4.0, 3.0, 2.0, 1.0]))
    ok("ic nan filter", n == 3 and nex == 1 and ic < 0.0)

    # 7. RAW pair fixture: fwd math by panel position
    close = np.arange(10.0, 33.0)              # 23 rows: 10..32
    dec = np.zeros(23, dtype=bool)
    dec[2:] = True
    feat = np.arange(23, dtype=float)
    x, y, dts = cell_pairs_raw(feat, dec, close, 23,
                               pd.date_range("2020-01-01", periods=23))
    ok("raw fwd math",
       bool(np.allclose(y[0], close[2 + FWD] / close[2] - 1.0))
       and len(x) >= 1)

    # 8. pool summary p math
    v = np.array([0.0, 0.05, -0.05, 0.10])
    s = _pool_summary(v, 0.10)
    ok("pool p math", abs(s["p_two"] - 2.0 / 5.0) < 1e-12)

    allok = all(results)
    print("selftest: %s" % ("ALL PASS" if allok else "HAS FAIL"))
    return 0 if allok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "selftest"])
    a = ap.parse_args()
    if a.cmd == "selftest":
        raise SystemExit(selftest())
    raise SystemExit(run())


if __name__ == "__main__":
    main()
