"""T-101-V4-A14-PREDFACE batch runner
(research/T-101-V4_A14_PREDFACE_PREREG.md, FROZEN r872 bm-b).

v4 22-gate library A13-style predictor extension arm: pure predictor
(forecast / walk-forward) INFORMATIONAL verdict -- Spearman rank IC of
three frozen mask-mean features vs 20-day forward returns, stride-20
non-overlapping rebalance calendar, RAW face (member's own forward
return) and RESID face (leave-one-out peer-demeaned). No portfolio
construction anywhere (prereg sec.1: information face; any downstream
conversion still faces the D6 beta-domination gate -- pre-declared,
A13 sec.1 verbatim continuation).

Feature face (prereg sec.0-X frozen):
  f_c2v4 = 22-gate mask mean (A158 17 CONFIRM fv.GATES17 + MP1 5
           CONFIRM gate_recheck_mp1.json library_entries, overlap 0)
  f_mp1  = MP1 5-gate mask mean (predictor usage never-tested new face)
  f_c2   = 17-gate mask mean (A13 discovery replication anchor at the
           new cutoff -- in-batch control, zero special treatment)
Mask machinery single-source imports: a158_tsgate_probe (probe) +
mp1_tsgate_probe (mp1, t23.evaluate inside) -- both rolling(252,
min_periods=120) q10/q90, same construction parameters.

Subcommands (prereg s6 frozen set):
  run --shard 0 --shards 1
            fv gate checks -> per-member ProcessPool jobs (feature
            build + 3 RAW cells each, shift-nulls K=200 + block
            bootstrap B=2000) -> master-intersection RESID cell jobs
            (15, ProcessPool) -> results/t101_v4_a14/shard_0of1.jsonl
            append-per-record checkpoint (done-set resume, r340 law) +
            pool-claim handshake on completion (claim-close leg).
  finalize  read shard rows -> 30 cells in frozen order -> FV verdict
            (9 IS-eligible cells, A13 clause quartet verbatim) +
            reading layer (21) -> results/t101_v4_a14_predface.json
            (evidence_cutoff + cutoff_meta top level; append_ledger
            return MUST land in out["trials_ledger"] -- r442 law);
            refuse-if-exists + single-shot landed-batch law (r450).
  selftest  offline engineering gates (hermetic fixtures, zero burn).

Frozen rng streams (prereg s3):
  shift nulls full  = rng([SCRNULL_BASE, cell_idx])           20615500
  shift nulls OOS   = rng([SCRNULL_BASE + 100000, cell_idx])  derived
  bootstrap  full  = rng([UNC_BASE, cell_idx])                20616500
  bootstrap  OOS   = rng([UNC_BASE + 100000, cell_idx])       derived
Declared base = actual base by construction (A12 rebind law: this batch
does not route through fv.dual_nulls; no inherited-base mismatch face).

Cell index order (frozen, prereg s0-X): face raw(0..14) then resid
(15..29); within a face: member 510300/510050/510500/512100/588000 x
feature f_c2v4/f_mp1/f_c2. Workers receive their cell_idx by position
= rng streams deterministic regardless of scheduling order.
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
ROOT = os.path.dirname(HERE)
for _p in (HERE, ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import science_gates as sg                     # noqa: E402
import t101_v4_a2_prescreen as tpl             # noqa: E402
import t101_v4_a158_fv as fv                   # noqa: E402
import a158_tsgate_probe as probe              # noqa: E402
import mp1_tsgate_probe as mp1                  # noqa: E402
from parallel_runner import run_cells_parallel, worker_cap   # pool multicore

BATCH = "T-101-V4-A14-PREDFACE"
EVIDENCE_CUTOFF = "2026-10-09"                 # prereg s2 forward lockbox
SPLIT = tpl.SPLIT                              # 2017-01-01 family constant
STRIDE = 20                                     # non-overlap rebalance grid
FWD = 20                                        # forward horizon (own tds)
MEMBERS = ["510300", "510050", "510500", "512100", "588000"]
IS_ELIGIBLE = ["510300", "510050", "510500"]   # RAW-face FV eligibility
FEATURES = ["f_c2v4", "f_mp1", "f_c2"]
FACES = ["raw", "resid"]
NULL_K = 200                                    # circular-shift nulls per cell
BOOT_B = 2000                                   # circular block bootstrap draws
BOOT_BLOCK = 10                                 # bootstrap block length
IC_MAG = 0.10                                   # |IC_OOS| magnitude clause
P_ALPHA = 0.05                                  # shift-null empirical alpha
MIN_IS_PAIRS = 15                               # IS confirmability floor
MIN_OOS_PAIRS = 15                              # supply-note flag floor
STREAM_SEG_OFFSET = 100000                      # OOS-segment derived-stream id
SCRNULL_BASE = sg.SEED_REGISTRY["t101_v4_a14_predface_scrnull"]  # 20615500
UNC_BASE = sg.SEED_REGISTRY["t101_v4_a14_predface_unc"]           # 20616500
A14_ANCHOR_ROWS = {"510300": 3490, "510050": 5255, "510500": 3293,
                   "512100": 2409, "588000": 1429}   # r872 probe facts
MP1_CONFIRM = [
    "CORR(HIGH,MUL(CLOSE,HIGH),20)_q90",
    "CORR(MA(CLOSE,10),VWAP,10)_q90",
    "CORR(OPEN,VWAP,10)_q90",
    "DELTA(MAX(RET,30),5)_q90",
    "MA(LOW,30)_q10",
]                                               # gate_recheck_mp1.json face
MP1_ANCHOR = {"gate": "DELTA(VOLUME,30)_q10", "member": "510300",
              "decidable": 3341, "open": 390, "first_idx": 149}
ANCHOR_FACE = {c: "data/daily/sh%s.csv" % c for c in MEMBERS}
PREREG_REL = "research/T-101-V4_A14_PREDFACE_PREREG.md"
OUT_DIR = os.path.join(ROOT, "results", "t101_v4_a14")
RESULTS_JSON = os.path.join(ROOT, "results", "t101_v4_a14_predface.json")
RECHECK_JSON = os.path.join(ROOT, "results", "gate_recheck_mp1.json")


def _fail(msg: str):
    print("FAIL-CLOSED: %s" % msg)
    raise SystemExit(2)


def _now():
    return time.strftime("%Y-%m-%d %H:%M:%S")


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
    if len(df) != A14_ANCHOR_ROWS[code]:
        _fail("G-ANCHOR VOID: %s rows %d != frozen anchor %d"
              % (code, len(df), A14_ANCHOR_ROWS[code]))
    return df


# ----------------------------------------------------- feature construction

def member_features(df: pd.DataFrame, code: str):
    """Per-member frozen mask-mean features (prereg s3). A158 face via
    probe (alpha158_factors + gate_universe), MP1 face via mp1 machinery
    import single-source (mp1_factors -> t23.evaluate + gate_universe).
    G-ANCHOR-MP1 reproduction on 510300 (fail-closed). Returns
    (feats: name -> (values_ndarray, dec_ndarray), close_ndarray,
    dates_index)."""
    Fa = probe.alpha158_factors(df)
    if len(Fa) != probe.N_FACTORS:
        _fail("G-FACTORS VOID: A158 factor table %d != %d"
              % (len(Fa), probe.N_FACTORS))
    ga = {g[0]: (g[1], g[2]) for g in probe.gate_universe(Fa)}
    miss = [g for g in fv.GATES17 if g not in ga]
    if miss:
        _fail("G-FACTORS VOID: A158 gates absent: %s" % miss)
    Fm = mp1.mp1_factors(df)                    # t23.evaluate single source
    if len(Fm) != mp1.N_POOL_COMPUTABLE:
        _fail("G-FACTORS VOID: MP1 factor face %d != %d"
              % (len(Fm), mp1.N_POOL_COMPUTABLE))
    gm = {g[0]: (g[1], g[2]) for g in mp1.gate_universe(Fm)}
    miss2 = [g for g in MP1_CONFIRM if g not in gm]
    if miss2:
        _fail("G-FACTORS VOID: MP1 CONFIRM gates absent: %s" % miss2)
    if code == MP1_ANCHOR["member"]:
        k = MP1_ANCHOR["gate"]
        m0 = gm[k]
        dec_n = int(m0[1].sum())
        open_n = int(m0[0].sum())
        first_i = int(np.flatnonzero(m0[1].values)[0])
        if (dec_n, open_n, first_i) != (MP1_ANCHOR["decidable"],
                                        MP1_ANCHOR["open"],
                                        MP1_ANCHOR["first_idx"]):
            _fail("G-ANCHOR-MP1 VOID: (%d,%d,%d) != (%d,%d,%d)"
                  % (dec_n, open_n, first_i, MP1_ANCHOR["decidable"],
                     MP1_ANCHOR["open"], MP1_ANCHOR["first_idx"]))
    c2 = pd.concat([ga[g][0].astype(float) for g in sorted(fv.GATES17)],
                   axis=1).mean(axis=1)
    c2dec = pd.Series(True, index=df.index)
    for g in sorted(fv.GATES17):
        c2dec = c2dec & ga[g][1]
    f5 = pd.concat([gm[g][0].astype(float) for g in MP1_CONFIRM],
                   axis=1).mean(axis=1)
    f5dec = pd.Series(True, index=df.index)
    for g in MP1_CONFIRM:
        f5dec = f5dec & gm[g][1]
    v4 = pd.concat([c2, f5], axis=1).mean(axis=1)
    v4dec = c2dec & f5dec
    feats = {
        "f_c2v4": (v4.values, v4dec.values),
        "f_mp1": (f5.values, f5dec.values),
        "f_c2": (c2.values, c2dec.values),
    }
    close = df["close"].values.astype(float)
    dates = pd.DatetimeIndex(df["date"])
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
    start (A13 verbatim); stride-20 grid; fwd20 by panel position."""
    pos = _contiguous_positions(dec, "raw")
    n = len(pos)
    rebal = np.arange(0, n, STRIDE)
    keep = rebal[rebal + FWD <= n_panel - 1 - pos[0]]
    idx = pos[keep]
    feat = feat_vals[idx]
    fwd = close_full[idx + FWD] / close_full[idx] - 1.0
    return feat, fwd, dates[idx]


def resid_pairs_master(member, feature, master_dates, member_payloads):
    """RESID face: U5 master intersection window + AND decidable across
    members (A13 verbatim semantics on the collected master payload)."""
    master = pd.DatetimeIndex(master_dates)
    dec = None
    for m in MEMBERS:
        p = member_payloads[m]
        d = pd.Series(p["feats"][feature]["dec"], index=master
                      ).fillna(False).astype(bool)
        dec = d if dec is None else (dec & d)
    pos = _contiguous_positions(dec.values, "resid|%s|%s" % (member, feature))
    n_panel = len(master)
    v0 = pos[0]
    n = len(pos)
    rebal = np.arange(0, n, STRIDE)
    keep = rebal[v0 + rebal + FWD <= n_panel - 1]
    wpos = pos[keep]
    fwd = {}
    for m in MEMBERS:
        c = np.asarray(member_payloads[m]["close"], dtype=float)
        fwd[m] = c[wpos + FWD] / c[wpos] - 1.0
    peer = [fwd[m] for m in MEMBERS if m != member]
    resid = fwd[member] - np.mean(peer, axis=0)   # LOO peer mean
    feat = np.asarray(member_payloads[member]["feats"][feature]["vals"],
                     dtype=float)[wpos]
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
    [1, n_pairs-1], rng([stream_base, cell_idx])); A13 verbatim."""
    n = len(x)
    if n < 3:
        return np.array([])
    rng = np.random.default_rng([int(stream_base), int(cell_idx)])
    offs = rng.integers(1, n, size=NULL_K)
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
    """Circular block bootstrap B=2000 block=10 percentile CI (A13)."""
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
    """Frozen FV clauses (prereg s4, A13 verbatim). IS-eligible = RAW x
    {510300, 510050, 510500} x n_IS >= 15. Reading layer: supply-note
    flag = OOS p<0.05 with n_OOS >= 15."""
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


def _cell_stats(face, member, feature, cell_idx, x, y, dts):
    """Shared per-cell stats block (A13 verbatim math): three-segment IC,
    frozen-stream shift nulls + bootstrap CIs, verdict."""
    ic_full, n_full, nex_full = _ic(x, y)
    is_mask = np.asarray(dts < pd.Timestamp(SPLIT))
    if is_mask.any():
        ic_is, n_is, nex_is = _ic(x[is_mask], y[is_mask])
    else:
        ic_is, n_is, nex_is = float("nan"), 0, 0
    if (~is_mask).any():
        ic_oos, n_oos, nex_oos = _ic(x[~is_mask], y[~is_mask])
    else:
        ic_oos, n_oos, nex_oos = float("nan"), 0, 0
    v_full = shift_null_pool(x, y, cell_idx, SCRNULL_BASE)
    x_oos, y_oos = x[~is_mask], y[~is_mask]
    v_oos = shift_null_pool(x_oos, y_oos, cell_idx,
                            SCRNULL_BASE + STREAM_SEG_OFFSET)
    s_full = _pool_summary(v_full, ic_full)
    s_oos = _pool_summary(v_oos, ic_oos)
    ci_full = block_bootstrap_ci(x, y, cell_idx, UNC_BASE)
    ci_oos = block_bootstrap_ci(x_oos, y_oos, cell_idx,
                                 UNC_BASE + STREAM_SEG_OFFSET)
    v = verdict_cell(face, member, ic_is, n_is, ic_oos, n_oos,
                     ic_full, s_oos["p_two"])
    rec = {
        "face": face, "member": member, "feature": feature,
        "cell_idx": cell_idx,
        "window": {"first_rebal": str(dts[0].date()),
                   "last_rebal": str(dts[-1].date()),
                   "n_pairs": int(len(x))},
        "ic": {"full": ic_full, "is": ic_is, "oos": ic_oos},
        "n_pairs_seg": {"full": n_full, "is": n_is, "oos": n_oos},
        "nan_excluded": {"full": nex_full, "is": nex_is, "oos": nex_oos},
        "shift_null": {"full": s_full, "oos": s_oos},
        "boot_ci": {"full": ci_full, "oos": ci_oos},
        "t_face_m1_disclosure": {"z_full": s_full["z"], "z_oos": s_oos["z"]},
    }
    rec.update(v)
    return rec


# ------------------------------------------------------------------ workers

def process_member(code):
    """TOP-LEVEL worker (ProcessPool pickles the fn): panel load + frozen
    features + 3 RAW cells (cell_idx = member_pos*3 + feature_pos, raw
    block 0..14) + feature cross-correlation + master payload for the
    RESID phase. Zero shared state via closures (parallel_runner law)."""
    t0 = time.time()
    df = load_panel(code)
    feats, close, dates = member_features(df, code)
    mi = MEMBERS.index(code)
    raw_cells = []
    for fi, f in enumerate(FEATURES):
        cell_idx = mi * len(FEATURES) + fi
        x, y, dts = cell_pairs_raw(feats[f][0], feats[f][1], close,
                                   len(df), dates)
        if len(x) == 0:
            raw_cells.append({"face": "raw", "member": code, "feature": f,
                              "cell_idx": cell_idx, "error": "EMPTY_PAIRS"})
            continue
        raw_cells.append(_cell_stats("raw", code, f, cell_idx, x, y, dts))
    # feature cross-correlation disclosure (common AND-decidable face)
    base = np.ones(len(df), dtype=bool)
    for f in FEATURES:
        base = base & feats[f][1]
    pos = np.flatnonzero(base)
    xcorr = {}
    for a in FEATURES:
        for b in FEATURES:
            if a < b:
                xa = feats[a][0][pos]
                xb = feats[b][0][pos]
                r, n, _ = _ic(xa, xb)
                xcorr["%s~%s" % (a, b)] = {"spearman": r, "n": n}
    master_payload = {
        "dates": [str(d.date()) for d in dates],
        "close": [float(v) for v in close],
        "feats": {f: {"vals": [float(v) for v in feats[f][0]],
                      "dec": [bool(v) for v in feats[f][1]]}
                  for f in FEATURES},
    }
    return {"key": "raw-%s" % code, "member": code,
            "raw_cells": raw_cells, "xcorr": xcorr,
            "master_payload": master_payload,
            "elapsed": round(time.time() - t0, 1)}


def process_resid_cell(member, feature, master_dates, member_payloads):
    """TOP-LEVEL worker: one RESID cell (cell_idx = 15 + pos*3 + fpos)
    from the collected master payloads (A13 resid_pairs_master math)."""
    mi = MEMBERS.index(member)
    fi = FEATURES.index(feature)
    cell_idx = len(MEMBERS) * len(FEATURES) + mi * len(FEATURES) + fi
    x, y, dts = resid_pairs_master(member, feature, master_dates,
                                   member_payloads)
    if len(x) == 0:
        return {"key": "resid-%s|%s" % (member, feature),
                "cell": {"face": "resid", "member": member,
                         "feature": feature, "cell_idx": cell_idx,
                         "error": "EMPTY_PAIRS"}}
    rec = _cell_stats("resid", member, feature, cell_idx, x, y, dts)
    return {"key": "resid-%s|%s" % (member, feature), "cell": rec}


# ------------------------------------------------------- checkpoint + claims

def _shard_path(shard, shards):
    return os.path.join(OUT_DIR, "shard_%dof%d.jsonl" % (shard, shards))


def _done_keys(shard, shards):
    done = set()
    fp = _shard_path(shard, shards)
    if os.path.exists(fp):
        for line in open(fp, encoding="utf-8"):
            try:
                done.add(json.loads(line)["key"])
            except Exception:
                continue
    return done


def _pool_claim(shard, shards, detail):
    """O-20261009-2355 claim-close leg (mp1 verbatim pattern, r942 leg-3):
    completed shard writes results/pool_claims/<BATCH>/<key>.<machine>.json
    state=closed so the launcher harvest flip lands the shard done. Worker
    NEVER writes runnable_pool.json (pool single-writer law). Idempotent
    fast-path: a todo==0 rerun rewrites the claim (redo immunity)."""
    try:
        mid = json.load(open(os.path.join(ROOT, "fleet", "machine.json"),
                             encoding="utf-8"))["machine_id"]
    except Exception:
        mid = "unknown"
    now = _now()
    d = os.path.join(ROOT, "results", "pool_claims", BATCH)
    os.makedirs(d, exist_ok=True)
    key = "t101-v4-a14-run-%dof%d" % (shard, shards)
    fp = os.path.join(d, "%s.%s.json" % (key, mid))
    with open(fp, "w", encoding="utf-8") as fh:
        json.dump({"machine_id": mid, "state": "closed", "pid": os.getpid(),
                   "heartbeat": now, "outcome": "ok", "exit_code": 0,
                   "started": _CLAIM_STARTED, "closed_at": now,
                   "result_ref": detail}, fh, ensure_ascii=False, indent=1)
    print("[a14] pool claim closed: %s" % os.path.basename(fp), flush=True)


# ---------------------------------------------------------------- main burn

def cmd_run(shard, shards, workers):
    global _CLAIM_STARTED
    _CLAIM_STARTED = _now()
    t0 = time.time()
    fv.g_p1_check()
    fv.g_accept_check()
    os.makedirs(OUT_DIR, exist_ok=True)
    fp = _shard_path(shard, shards)
    my_members = [m for i, m in enumerate(MEMBERS) if i % shards == shard]
    done = _done_keys(shard, shards)
    todo = [m for m in my_members if "raw-%s" % m not in done]
    print("[a14] shard %d/%d members=%d raw-todo=%d" %
          (shard, shards, len(my_members), len(todo)), flush=True)
    if todo:
        jobs = [("raw-%s" % m, process_member, (m,)) for m in todo]
        with open(fp, "a", encoding="utf-8") as fh:
            def keep(key, payload):
                fh.write(json.dumps(payload, ensure_ascii=False,
                                    separators=(",", ":")) + "\n")
                fh.flush()
            res = run_cells_parallel(jobs, workers=workers or worker_cap(),
                                      desc="a14-raw", on_result=keep)
        print("[a14] raw phase done: %d members, workers=%s"
              % (len(res), res.get("__workers__")), flush=True)
    # RESID phase: needs ALL member records (0of1 contract face; with
    # multi-shard splits an incomplete member set defers honestly)
    done = _done_keys(shard, shards)
    payloads = {}
    if os.path.exists(fp):
        for line in open(fp, encoding="utf-8"):
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("key", "").startswith("raw-"):
                payloads[r["member"]] = r["master_payload"]
    missing = [m for m in MEMBERS if m not in payloads]
    if missing:
        print("[a14] resid DEFERRED: members incomplete %s" % missing,
              flush=True)
        return 0
    master_dates = None
    for m in MEMBERS:
        d = pd.DatetimeIndex(payloads[m]["dates"])
        master_dates = d if master_dates is None \
            else master_dates.intersection(d)
    master_dates = [str(x.date()) for x in master_dates]
    # reindex payloads to master (dec fillna False, vals ffill-free reindex)
    re = {}
    for m in MEMBERS:
        p = payloads[m]
        di = pd.DatetimeIndex(p["dates"])
        close = pd.Series(p["close"], index=di).reindex(master_dates)
        feats = {}
        for f in FEATURES:
            vals = pd.Series(p["feats"][f]["vals"], index=di) \
                .reindex(master_dates)
            dec = pd.Series(p["feats"][f]["dec"], index=di
                            ).reindex(master_dates
                                      ).fillna(False).astype(bool)
            feats[f] = {"vals": vals.values, "dec": dec.values}
        re[m] = {"close": close.values, "feats": feats}
    todo_r = [(m, f) for m in MEMBERS for f in FEATURES
              if "resid-%s|%s" % (m, f) not in done]
    if todo_r:
        jobs = [("resid-%s|%s" % (m, f), process_resid_cell,
                 (m, f, master_dates, re)) for m, f in todo_r]
        with open(fp, "a", encoding="utf-8") as fh:
            def keep2(key, payload):
                fh.write(json.dumps({"key": key, "cell": payload["cell"]},
                                    ensure_ascii=False,
                                    separators=(",", ":")) + "\n")
                fh.flush()
            res2 = run_cells_parallel(jobs, workers=workers or worker_cap(),
                                      desc="a14-resid", on_result=keep2)
        print("[a14] resid phase done: %d cells, workers=%s"
              % (len(res2) - 1 if "__workers__" in res2 else len(res2),
                 res2.get("__workers__")), flush=True)
    done = _done_keys(shard, shards)
    remaining = len([m for m in MEMBERS if "raw-%s" % m not in done]) + \
        len([(m, f) for m in MEMBERS for f in FEATURES
             if "resid-%s|%s" % (m, f) not in done])
    if remaining == 0:
        _pool_claim(shard, shards,
                    "shard complete (5 raw members + 15 resid cells, "
                    "checkpoint %s); finalize=%s"
                    % (os.path.basename(fp), os.path.exists(RESULTS_JSON)))
    print("[a14] shard done in %.0fs -> %s" % (time.time() - t0, fp),
          flush=True)
    return 0


def _landed_block(path):
    """Single-shot law (r450): the trials_ledger block of THIS batch
    already landed -> refuse re-run (fresh prereg needed)."""
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            j = json.load(fh)
    except Exception:
        return None
    tl = j.get("trials_ledger") if isinstance(j, dict) else None
    if isinstance(tl, dict) and tl.get("batch") == BATCH:
        return tl
    return None


def cmd_finalize():
    if os.path.exists(RESULTS_JSON):
        _fail("refuse-if-exists: %s already on disk" %
              os.path.basename(RESULTS_JSON))
    if _landed_block(RESULTS_JSON) is not None:
        _fail("verdict already landed (trials_ledger block present) -- "
              "single-shot law, re-run needs fresh prereg")
    t0 = time.time()
    # roster identity pin (gate_recheck_mp1.json face, prereg s0-X)
    with open(RECHECK_JSON, encoding="utf-8") as fh:
        rj = json.load(fh)
    lib = sorted(e["gate"] if isinstance(e, dict) else e
                 for e in rj["library_entries"])
    if lib != sorted(MP1_CONFIRM):
        _fail("ROSTER DRIFT: gate_recheck_mp1.json library_entries != "
              "frozen MP1_CONFIRM")
    fv.g_p1_check()
    fv.g_accept_check()
    prev_head = sg.ledger_head()
    cells_raw, cells_resid, xcorr, workers_seen = {}, {}, {}, []
    payloads = {}
    for shard_key in ("shard_0of1.jsonl",):
        fp = os.path.join(OUT_DIR, shard_key)
        if not os.path.exists(fp):
            _fail("SHARD VOID: %s missing -- run the shard first" % fp)
        for line in open(fp, encoding="utf-8"):
            try:
                r = json.loads(line)
            except Exception:
                continue
            k = r.get("key", "")
            if k.startswith("raw-"):
                m = r["member"]
                payloads[m] = r["master_payload"]
                xcorr[m] = r["xcorr"]
                workers_seen.append(r.get("elapsed"))
                for c in r["raw_cells"]:
                    cells_raw[(c["member"], c["feature"])] = c
            elif k.startswith("resid-"):
                c = r["cell"]
                cells_resid[(c["member"], c["feature"])] = c
    if len(cells_raw) != 15 or len(cells_resid) != 15:
        _fail("CELL VOID: raw=%d resid=%d != 15/15"
              % (len(cells_raw), len(cells_resid)))
    cells = []
    idx = 0
    for face in FACES:
        for m in MEMBERS:
            for f in FEATURES:
                src = cells_raw if face == "raw" else cells_resid
                c = dict(src[(m, f)])
                if c.get("cell_idx") != idx:
                    _fail("CELL ORDER DRIFT: %s|%s|%s idx %s != %d"
                          % (face, m, f, c.get("cell_idx"), idx))
                cells.append(c)
                idx += 1
    fv_cells = [c for c in cells if c.get("fv_eligible")]
    fv_pass = [c for c in fv_cells if c.get("verdict") == "FV_PASS"]
    notes = [c for c in cells if c.get("supply_note_flag")]
    out = {
        "batch": BATCH,
        "prereg": PREREG_REL,
        "generated": _now(),
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
                   "anchor_rows": A14_ANCHOR_ROWS,
                   "is_eligible_members": IS_ELIGIBLE,
                   "mp1_confirm_5": MP1_CONFIRM,
                   "a158_confirm_17": sorted(fv.GATES17)},
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
                  "host": json.load(open(os.path.join(
                      ROOT, "fleet", "machine.json"),
                      encoding="utf-8"))["machine_id"],
                  "workers": "parallel_runner ProcessPool (member jobs + "
                             "resid cell jobs)",
                  "member_elapsed": workers_seen},
    }
    ledger = sg.append_ledger(BATCH, 30, "t101_v4_a14_predface.json",
                              evidence_cutoff=EVIDENCE_CUTOFF)
    out["trials_ledger"] = ledger                     # r442 law
    with open(RESULTS_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print("A14-PREDFACE finalize done in %.1fs: FV %d/%d pass, %d supply "
          "notes, ledger total=%s" % (time.time() - t0, len(fv_pass),
                                      len(fv_cells), len(notes),
                                      ledger.get("total")))
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

    # 5. verdict clause boundary math (A13 quartet)
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

    # 9. single-shot guard (r450 incident)
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p_landed = os.path.join(td, "landed.json")
        with open(p_landed, "w", encoding="utf-8") as fh:
            json.dump({"trials_ledger": {"batch": BATCH, "total": 1}}, fh)
        p_other = os.path.join(td, "other.json")
        with open(p_other, "w", encoding="utf-8") as fh:
            json.dump({"trials_ledger": {"batch": "SOME-OTHER-BATCH"}}, fh)
        ok("single-shot guard",
           _landed_block(p_landed) is not None
           and _landed_block(p_other) is None
           and _landed_block(os.path.join(td, "absent.json")) is None)

    # 10. MP1 roster identity pin (gate_recheck_mp1.json live face)
    try:
        with open(RECHECK_JSON, encoding="utf-8") as fh:
            rj = json.load(fh)
        lib = sorted(e["gate"] if isinstance(e, dict) else e
                     for e in rj["library_entries"])
        vc = rj.get("verdict_counts", {}).get("RECHECK-CONFIRM")
        ok("mp1 roster identity pin",
           lib == sorted(MP1_CONFIRM) and vc == 5)
    except Exception:
        ok("mp1 roster identity pin", False)

    # 11. frozen anchor rows pin
    ok("anchor rows pin", set(A14_ANCHOR_ROWS) == set(MEMBERS)
       and set(ANCHOR_FACE) == set(MEMBERS))

    # 12. resid master fixture: AND decidable + LOO target exact math
    md = pd.bdate_range("2020-01-01", periods=300)
    md_s = [str(d.date()) for d in md]
    pay = {}
    for m in MEMBERS:
        pay[m] = {"close": np.linspace(1.0, 2.0, 300),
                  "feats": {"f": {"vals": np.linspace(0.0, 1.0, 300),
                                  "dec": np.ones(300, dtype=bool)}}}
    x, y, dts = resid_pairs_master(MEMBERS[0], "f", md_s, pay)
    pos_expected = np.arange(len(x) + 1)   # grid from pos[0]=0, stride 20
    k = len(x)
    exp_fwd = {m: pay[m]["close"][pos_expected[:k] + FWD]
               / pay[m]["close"][pos_expected[:k]] - 1.0 for m in MEMBERS}
    exp_resid = exp_fwd[MEMBERS[0]] - np.mean(
        [exp_fwd[m] for m in MEMBERS[1:]], axis=0)
    ok("resid master fixture",
       bool(np.allclose(y, exp_resid)) and len(x) == len(y))

    allok = all(results)
    print("selftest: %d/%d %s" % (sum(results), len(results),
                                  "ALL PASS" if allok else "HAS FAIL"))
    return 0 if allok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "finalize", "selftest"])
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--shards", type=int, default=1)
    ap.add_argument("--workers", type=int, default=None)
    a = ap.parse_args()
    if a.cmd == "selftest":
        raise SystemExit(selftest())
    if a.cmd == "run":
        raise SystemExit(cmd_run(a.shard, a.shards, a.workers))
    raise SystemExit(cmd_finalize())


if __name__ == "__main__":
    main()
