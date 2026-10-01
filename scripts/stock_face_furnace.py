"""STOCK_FACE_FURNACE_P1 runner (T-2026-10-01-139-P1 akshare face, bm-b lane).

CEO direct order O-2026-10-01-1035 (stocks -- do not run only ETFs): three
family furnaces on the bm-b akshare full-A panel, EXPLORATION face
(zero verdict claims; supply = trial-wave STOCK grammar bands).

  probe     real data anchors -> results/stock_face_furnace/probe_facts.json
            (also builds the panel cache npz under gitignored data/)
  selftest  hermetic offline checks (enumeration, judged-cell exclusion,
            real-engine-path legs on a synthetic panel per r494/r506 laws,
            hand-value cost legs per r474, nulls determinism, guards)
  run       burn one cell block: --family rev|lowamp|mom --cells a:b
            ProcessPool over cells (O-20260930-2355 multicore law),
            per-cell JSON checkpoint (presence=done), FAIL-CLOSED probe
            equality gate, free-RAM gate exit 3, worker-side pool claim
            handshake (burn-complete + idempotent no-op call points,
            lowamp_p1 canon; runner+handshake same commit per r497)
  finalize  per-family aggregate -> ranked table + robust flags + dual-null
            p-values + significant-band list + summary JSON/CSV; trials-ledger
            append single-shot when all three families complete.

Laws carried: R99 freeze-before-burn (research/STOCK_FACE_FURNACE_P1.md,
banned_direction_gate ADMIT r502), TRIAL_LABOR_LAW sec.4 meaning gate +
same-grammar rerun ban (REV_OSC_STOCK_P1 7 judged cells EXCLUDED from the
rev enumeration), P4_BATCH2 sec.2 dynamic eligibility verbatim, V1 stock
cost 13.041bp/side single-source import (rev_osc_stock_p1.COST_X1, no hand
copies), T+1 open conservative proxy O-1132, evidence_cutoff=2026-09-30
panel lockbox, engine reuse over rewrite (REV event engine imported
verbatim from rev_osc_stock_p1; only the akshare panel builder and the two
new cross-sectional exploration engines are new).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (ROOT, os.path.join(ROOT, "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import science_gates as sg                                   # noqa: E402
import rev_osc_stock_p1 as revo                              # noqa: E402

OUT_DIR = os.path.join(ROOT, "results", "stock_face_furnace")
PROBE_FILE = os.path.join(OUT_DIR, "probe_facts.json")
CELLS_DIR = os.path.join(OUT_DIR, "cells")
PANEL_CACHE = os.path.join(ROOT, "data", "astock_daily", "_furnace_panel.npz")
ASTOCK_STATUS = os.path.join(ROOT, "results", "astock_daily_update_status.json")
PANEL_DIR = os.path.join(ROOT, "data", "astock_daily", "per")
ELIG_CSV = os.path.join(ROOT, "data", "fundamental", "eligibility.csv")
MASK_CSV = os.path.join(ROOT, "data", "fundamental", "b_layer_mask.csv")
CAL_CSV = os.path.join(ROOT, "data", "daily", "sh510050.csv")
GATE_CSV = os.path.join(ROOT, "data", "daily", "sh510300.csv")

EVIDENCE_CUTOFF = "2026-09-30"          # panel lockbox (prereg sec.2)
PANEL_FROM = "2013-06-01"                # >=200 trading days before val start
                                          # (510300 MA200 warmup complete by
                                          # 2015-01-01, zero gate_undefined
                                          # inside validation)
VAL_WIN = ("2015-01-01", "2025-09-30")   # validation window (frozen, no overlap)
DISC_WIN = ("2025-10-01", "2026-09-30")  # discovery window (frozen)
COST_X1 = revo.COST_X1                   # 13.041bp/side, single-source import
COST_FACES = {"x1": COST_X1, "x2": COST_X1 * 2}
K_NULLS = 2000                           # per cell, dual method (prereg sec.3)
BLOCK_LEN = 10
NULLS_SEED_KEY = "stock_face_furnace_nulls"
NULLS_SEED = sg.SEED_REGISTRY[NULLS_SEED_KEY]
RAM_BASE_GB = 2.0          # main-process panel + overhead
RAM_PER_WORKER_GB = 0.55   # per-worker panel slice (~500MB) + slack


def _ram_floor_gb(workers: int) -> float:
    return RAM_BASE_GB + RAM_PER_WORKER_GB * max(1, workers)
HOLD_BUFFER_FURNACE = 28                 # H=20 + entry + suspension roll slack
WORKERS_CAP = 12

REV_HOLD = (5, 7, 10, 20)
LOWAMP_W = (40, 50, 60, 70, 77, 85, 89, 95, 104)
LOWAMP_N = (2, 3, 5, 10)
MOM_L = (20, 60, 120, 252)
MOM_N = (5, 10)

# REV_OSC_STOCK_P1 judged cells (grammar-consumed, excluded from the furnace
# enumeration -- TRIAL_LABOR_LAW sec.4 same-grammar rerun ban; prereg sec.0.4)
REV_JUDGED = {
    (False, False, False, False, 7, "eq"),   # BASE
    (False, False, True, False, 7, "eq"),    # BASE_BG
    (True, False, True, False, 7, "eq"),     # FY_BG
    (True, False, True, True, 7, "eq"),      # FY_BG_TP8
    (True, False, True, False, 10, "eq"),    # FY_BG_H10
    (False, True, True, True, 10, "eq"),     # DWR_BG_TP8
    (True, False, True, False, 7, "invvol"),  # FY_BG_INVVOL
}


def _now_iso() -> str:
    import datetime
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def _machine_id() -> str:
    try:
        with open(os.path.join(ROOT, "fleet", "machine.json"), encoding="utf-8") as f:
            return json.load(f).get("machine_id", "unknown")
    except Exception:
        return "unknown"


def _dump(obj, path: str) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    os.replace(tmp, path)


def _free_ram_gb() -> float:
    try:
        import psutil
        return psutil.virtual_memory().available / (1 << 30)
    except Exception:
        return 64.0


def _sha16(path: str) -> str:
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def _sha16_text(text: str) -> str:
    import hashlib
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _elig_code_face() -> list[str]:
    # r503 semantic pin: the eligibility snapshot face actually consumed by
    # _universe() is the 6-digit 0/3/6 code set, NOT the np columns -- the
    # daily S6 fundamental refresh rotates np bytes with the consumed code
    # set identical, so a raw-file sha pin false-positives mid-wave (live
    # 2026-10-01 12:14-12:18: LOWAMP-108/MOM-0/MOM-4 fused on the cosmetic
    # refresh, 7273-code eligible set byte-identical, mask unchanged).
    import pandas as pd
    elig = pd.read_csv(ELIG_CSV, dtype={"code": str})
    return sorted({c for c in elig["code"].astype(str).tolist()
                   if len(c) == 6 and c[0] in ("0", "3", "6")})


# --------------------------------------------------------------------------
# family enumerations (pure; selftest exercises these paths)
# --------------------------------------------------------------------------
def rev_cells() -> list[dict]:
    cells, i = [], 0
    for gate in (False, True):
        for yang in (False, True):
            for dwr in (False, True):
                for tpsl in (False, True):
                    for H in REV_HOLD:
                        for w in ("eq", "invvol"):
                            key = (yang, dwr, gate, tpsl, H, w)
                            if key in REV_JUDGED:
                                continue
                            cells.append({"name": f"R{len(cells):03d}",
                                          "yang": yang, "dwr": dwr,
                                          "gate": gate, "tpsl": tpsl,
                                          "H": H, "w": w,
                                          "cell_index": i})
                            i += 1
    return cells


def lowamp_cells() -> list[dict]:
    cells, i = [], 121          # global cell_index: rev 0..120, lowamp 121..264
    for W in LOWAMP_W:
        for N in LOWAMP_N:
            for sizing in ("eq", "invvol"):
                for gate in ("none", "bear"):
                    cells.append({"name": f"L{len(cells):03d}", "W": W,
                                  "N": N, "sizing": sizing, "gate": gate,
                                  "cell_index": i})
                    i += 1
    return cells


def mom_cells() -> list[dict]:
    cells, i = [], 265          # global cell_index: mom 265..280
    for L in MOM_L:
        for N in MOM_N:
            for gate in ("none", "bear"):
                cells.append({"name": f"M{len(cells):03d}", "L": L,
                              "N": N, "gate": gate, "cell_index": i})
                i += 1
    return cells


FAMILIES = {"rev": rev_cells, "lowamp": lowamp_cells, "mom": mom_cells}
N_CELLS_TOTAL = sum(len(f()) for f in FAMILIES.values())   # 281


# --------------------------------------------------------------------------
# panel construction (probe + run SAME builder -- face assertion law)
# --------------------------------------------------------------------------
def _universe() -> list[str]:
    import pandas as pd
    elig = pd.read_csv(ELIG_CSV, dtype={"code": str})
    codes = {c for c in elig["code"].astype(str).tolist()
             if len(c) == 6 and c[0] in ("0", "3", "6")}
    mask = pd.read_csv(MASK_CSV, dtype={"code": str})
    ok = {r.code for r in mask.itertuples() if bool(r.ok_static)}
    have = {os.path.splitext(p)[0] for p in os.listdir(PANEL_DIR)
            if p.endswith(".csv")}
    return sorted(codes & ok & have)


def build_panel(universe=None) -> dict:
    """Akshare panel -> engine-P dict (rev_osc_stock_p1 P contract).

    Regime face = family convention 510300<MA200 (REFINE-BENCH precedent;
    the sse index face of the judged batch is disclosed in prereg sec.2).
    """
    import pandas as pd
    if universe is None:
        universe = _universe()
    cal = pd.read_csv(CAL_CSV, usecols=["date"])["date"].astype(str).tolist()
    cal = [d for d in cal if d >= PANEL_FROM]
    idx = pd.to_datetime(np.asarray(cal, dtype="datetime64[us]"))
    T, N = len(idx), len(universe)

    F = {k: np.full((T, N), np.nan, dtype=np.float32)
         for k in ("open", "high", "low", "close", "pct_chg", "amount")}
    mask = pd.read_csv(MASK_CSV, dtype={"code": str}).set_index("code")
    board = {s: (mask.loc[s, "board"] if s in mask.index else "main")
             for s in universe}
    dpos = {d: i for i, d in enumerate(cal)}
    for j, code in enumerate(universe):
        df = pd.read_csv(os.path.join(PANEL_DIR, code + ".csv"))
        if df["date"].dtype != object:
            df["date"] = df["date"].astype(str)
        rows = np.fromiter((dpos.get(d, -1) for d in df["date"]),
                           dtype=np.int64, count=len(df))
        m = rows >= 0
        r = rows[m]
        F["open"][r, j] = df["open"].to_numpy(dtype=np.float32)[m]
        F["high"][r, j] = df["high"].to_numpy(dtype=np.float32)[m]
        F["low"][r, j] = df["low"].to_numpy(dtype=np.float32)[m]
        F["close"][r, j] = df["close"].to_numpy(dtype=np.float32)[m]
        F["amount"][r, j] = df["amount"].to_numpy(dtype=np.float32)[m]

    close = F["close"]
    with np.errstate(invalid="ignore"):
        prev1 = np.vstack([np.full((1, N), np.nan, np.float32), close[:-1]])
        F["pct_chg"] = (close / prev1 - 1.0).astype(np.float32)
        p20 = np.vstack([np.full((20, N), np.nan, np.float32), close[:-20]])
        drop20 = (close / p20 - 1.0).astype(np.float32)
        p60 = np.vstack([np.full((60, N), np.nan, np.float32), close[:-60]])
        drop60 = (close / p60 - 1.0).astype(np.float32)

    # P4_BATCH2 sec.2 dynamic eligibility (verbatim clauses)
    fin = np.isfinite(close)
    amt20 = revo._roll_mean20(F["amount"])
    listed = fin.cumsum(axis=0)
    lvidx = np.where(fin, np.arange(T)[:, None], -1)
    lastvalid = np.maximum.accumulate(lvidx, axis=0)
    fresh = (np.arange(T)[:, None] - lastvalid) <= revo.FRESH_MAX
    ok_row = np.array([board.get(s) not in ("other", None) for s in universe])
    elig = (ok_row[None, :] & fin & (close >= revo.PRICE_MIN)
            & np.isfinite(amt20) & (amt20 >= revo.AMT20_MIN)
            & (listed >= revo.LISTED_MIN) & fresh)
    med = float(np.median(elig.sum(axis=1)))

    g = pd.read_csv(GATE_CSV, usecols=["date", "close"])
    gv = (g.set_index(g["date"].astype(str))["close"]
          .reindex(cal).ffill().to_numpy(float))
    ma200 = pd.Series(gv).rolling(200, min_periods=200).mean().to_numpy()

    idx64 = idx.astype("datetime64[us]")
    fl = np.full((N, T), revo.MAIN_FLOOR, dtype=np.float32)
    for j, s in enumerate(universe):
        if board.get(s) == "chinext":
            fl[j, idx64 >= np.datetime64(str(revo.CN_20CM_FROM))] = revo.WIDE_FLOOR
        elif board.get(s) == "star":
            fl[j, idx64 >= np.datetime64(str(revo.STAR_FROM))] = revo.WIDE_FLOOR

    pct = F["pct_chg"]
    with np.errstate(invalid="ignore"):
        ew_f = np.where(elig & np.isfinite(pct), pct, 0.0)
        n_e = (elig & np.isfinite(pct)).sum(axis=1)
    ew = np.where(n_e > 0, ew_f.sum(axis=1) / np.maximum(n_e, 1), 0.0)

    col = {f: np.ascontiguousarray(F[f].T)
           for f in ("open", "high", "low", "close")}
    return {"idx": idx, "syms": list(universe), "board": board, "F": F,
            "col": col, "fl": fl, "elig": elig, "drop20": drop20,
            "drop60": drop60, "sse": gv, "ma200": ma200, "ew_ret": ew,
            "elig_median": med}


def _panel_from_cache(expected_universe: list[str]):
    if not os.path.exists(PANEL_CACHE):
        return None
    try:
        z = np.load(PANEL_CACHE, allow_pickle=False)
        if list(z["syms"]) != expected_universe:
            return None
        P = {"idx": __import__("pandas").to_datetime(z["idx"]),
             "syms": expected_universe,
             "board": dict(zip(expected_universe, [str(b) for b in z["board"]])),
             "F": {k: z["F_" + k] for k in
                   ("open", "high", "low", "close", "pct_chg", "amount")},
             "fl": z["fl"], "elig": z["elig"], "drop20": z["drop20"],
             "drop60": z["drop60"], "sse": z["sse"], "ma200": z["ma200"],
             "ew_ret": z["ew_ret"], "elig_median": float(z["elig_median"])}
        P["col"] = {f: np.ascontiguousarray(P["F"][f].T)
                    for f in ("open", "high", "low", "close")}
        return P
    except Exception:
        return None


def _panel_to_cache(P: dict) -> None:
    os.makedirs(os.path.dirname(PANEL_CACHE), exist_ok=True)
    tmp = PANEL_CACHE + ".tmp"
    np.savez_compressed(tmp,
                        idx=P["idx"].astype("datetime64[us]"),
                        syms=np.asarray(P["syms"]),
                        board=np.asarray([P["board"][s] for s in P["syms"]]),
                        **{("F_" + k): v for k, v in P["F"].items()},
                        fl=P["fl"], elig=P["elig"], drop20=P["drop20"],
                        drop60=P["drop60"], sse=P["sse"], ma200=P["ma200"],
                        ew_ret=P["ew_ret"],
                        elig_median=np.float64(P["elig_median"]))
    os.replace(tmp + ".npz" if os.path.exists(tmp + ".npz") else tmp,
               PANEL_CACHE)


# --------------------------------------------------------------------------
# window metrics + dual nulls (shared across families)
# --------------------------------------------------------------------------
def _win_slice(P, win) -> slice:
    i0 = int(np.searchsorted(P["idx"], np.datetime64(win[0])))
    i1 = int(np.searchsorted(P["idx"], np.datetime64(win[1]), side="right"))
    return slice(i0, i1)


def win_stats(series: np.ndarray) -> dict:
    return revo.cell_stats(series)


def dual_nulls(series: np.ndarray, cell_index: int) -> dict:
    """Sign-flip 2000 + block bootstrap 2000 (prereg sec.3).

    seed = SEED_REGISTRY[stock_face_furnace_nulls] + cell_index*4000 + k;
    band [20333000, 20445400) disjoint-registered in science_gates r502.
    """
    r = np.asarray(series, dtype=np.float64)
    r = r[np.isfinite(r)]
    if r.size < 50:
        return {"p_sign": None, "p_block": None, "n_days": int(r.size),
                "note": "insufficient days"}
    obs = float(r.mean())
    base = NULLS_SEED + cell_index * (2 * K_NULLS)
    rng = np.random.default_rng(base)
    signs = rng.integers(0, 2, size=(K_NULLS, r.size)) * 2.0 - 1.0
    p_sign = float(((r[None, :] * signs).mean(axis=1) >= obs - 1e-15).mean())
    rng2 = np.random.default_rng(base + K_NULLS)
    n_blocks = int(np.ceil(r.size / BLOCK_LEN))
    starts = rng2.integers(0, max(r.size - BLOCK_LEN, 1),
                           size=(K_NULLS, n_blocks))
    off = np.arange(BLOCK_LEN)[None, :]
    boot = np.empty(K_NULLS)
    for k in range(K_NULLS):
        idxs = (starts[k][:, None] + off).ravel()[:r.size]
        boot[k] = r[idxs].mean()
    p_block = float((boot >= obs - 1e-15).mean())
    return {"p_sign": round(p_sign, 5), "p_block": round(p_block, 5),
            "n_days": int(r.size)}


# --------------------------------------------------------------------------
# LOWAMP / MOM vectorized exploration engines (prereg sec.3)
# --------------------------------------------------------------------------
def _bear_mask(P) -> np.ndarray:
    m = np.isfinite(P["sse"]) & np.isfinite(P["ma200"])
    bear = np.zeros(len(P["sse"]), dtype=bool)
    bear[m] = P["sse"][m] < P["ma200"][m]
    return bear


def _xs_weights(amp_row, elig_row, N, sizing):
    """Top-N lowest-amp picks + weights on the eligible cross-section."""
    cand = np.flatnonzero(elig_row & np.isfinite(amp_row))
    if cand.size == 0:
        return cand, None
    k = min(N, cand.size)
    part = np.argpartition(amp_row[cand], k - 1)[:k]
    order = cand[part[np.argsort(amp_row[cand][part], kind="stable")]]
    if sizing == "eq":
        w = np.full(order.size, 1.0 / order.size)
    else:
        a = amp_row[order]
        inv = np.where(np.isfinite(a) & (a > 0), 1.0 / np.where(a > 0, a, 1.0), 0.0)
        w = inv / inv.sum() if inv.sum() > 0 else np.full(order.size, 1.0 / order.size)
    return order, w


def _rolling_std(pct: np.ndarray, W: int) -> np.ndarray:
    """Rolling std of returns, min_periods=W (lowamp_p1.build_signal face)."""
    T, N = pct.shape
    c1 = np.nan_to_num(pct, nan=0.0)
    cnt = np.isfinite(pct).astype(np.float32)
    s1 = c1.cumsum(axis=0)
    s2 = (c1 * c1).cumsum(axis=0)
    n = cnt.cumsum(axis=0)
    pad = np.zeros((W, N), dtype=np.float32)

    def _off(a):
        return np.vstack([pad, a[:-W]])

    n_w = _off(n)
    with np.errstate(invalid="ignore", divide="ignore"):
        mean_w = (s1 - _off(s1)) / n_w
        var_w = np.maximum((s2 - _off(s2)) / n_w - mean_w * mean_w, 0.0)
    std = np.sqrt(var_w).astype(np.float32)
    std[n_w < W] = np.nan
    return std


def lowamp_sim_costface(P, cell, cost):
    """Daily-rebalance low-amp portfolio, one cost face.

    Weights decided at t apply from t+1 (T+1 proxy); daily re-rank; cost =
    per-side fee x one-way turnover |w[t]-w[t-1]| (exploration approximation,
    disclosed prereg sec.3).
    """
    T, N = P["F"]["close"].shape
    std_w = _rolling_std(P["F"]["pct_chg"], cell["W"])
    bear = _bear_mask(P)
    elig = P["elig"] & np.isfinite(std_w)
    W_daily = np.zeros((T, N))
    for t in range(200, T):
        if cell["gate"] == "bear" and not bear[t]:
            continue
        picks, w = _xs_weights(std_w[t], elig[t], cell["N"], cell["sizing"])
        if picks.size and t + 1 < T:
            W_daily[t + 1][picks] = w
    rets = P["F"]["pct_chg"]
    out = np.zeros(T)
    turnover = 0.0
    prev_w = np.zeros(N)
    for t in range(1, T):
        w_t = W_daily[t]
        if prev_w.any():
            r = rets[t]
            m = np.isfinite(r)
            out[t] = float(np.where(m, prev_w * np.where(m, r, 0.0), 0.0).sum())
        dturn = float(np.abs(w_t - prev_w).sum())
        turnover += dturn
        out[t] -= cost * dturn
        prev_w = w_t
    return out, turnover


def lowamp_sim_faces(P, cell):
    s1, to = lowamp_sim_costface(P, cell, COST_FACES["x1"])
    s2, _ = lowamp_sim_costface(P, cell, COST_FACES["x2"])
    return s1, s2, to


def mom_sim_faces(P, cell):
    """Monthly rebalance momentum: L-lookback DESCENDING Top-N, eq weights."""
    import pandas as pd
    close = P["F"]["close"]
    T, N = close.shape
    L = cell["L"]
    prevL = np.vstack([np.full((L, N), np.nan, np.float32), close[:-L]])
    with np.errstate(invalid="ignore"):
        mom = close / prevL - 1.0
    bear = _bear_mask(P)
    elig = P["elig"] & np.isfinite(mom)
    months = pd.Index(P["idx"].strftime("%Y-%m"))
    W_daily = np.zeros((T, N))
    for t in range(max(L, 200), T):
        is_month_end = (t + 1 >= T) or (months[t + 1] != months[t])
        if not is_month_end:
            continue
        if cell["gate"] == "bear" and not bear[t]:
            continue
        cand = np.flatnonzero(elig[t])
        if cand.size == 0:
            continue
        k = min(cell["N"], cand.size)
        part = np.argpartition(-mom[t][cand], k - 1)[:k]
        picks = cand[part[np.argsort(-mom[t][cand][part], kind="stable")]]
        if t + 1 < T:
            W_daily[t + 1][picks] = 1.0 / picks.size
    rets = P["F"]["pct_chg"]
    out = {f: np.zeros(T) for f in COST_FACES}
    prev_w = np.zeros(N)
    turnover = 0.0
    for t in range(1, T):
        w_t = W_daily[t]
        if prev_w.any():
            r = rets[t]
            m = np.isfinite(r)
            gross = float(np.where(m, prev_w * np.where(m, r, 0.0), 0.0).sum())
            dturn = float(np.abs(w_t - prev_w).sum())
            for f, c in COST_FACES.items():
                out[f][t] = gross - c * dturn
        turnover += float(np.abs(w_t - prev_w).sum())
        prev_w = w_t
    return out["x1"], out["x2"], turnover


# --------------------------------------------------------------------------
# REV family burn (engine imported from rev_osc_stock_p1, zero rewrite)
# --------------------------------------------------------------------------
def rev_sim_faces(P, cell):
    m1 = revo.sim_cell(P, cell, "x1")
    m2 = revo.sim_cell(P, cell, "x2")
    return m1["series"], m2["series"], m1


# --------------------------------------------------------------------------
# per-cell orchestration
# --------------------------------------------------------------------------
def burn_cell(P, family, cell) -> dict:
    t0 = time.time()
    sl_val = _win_slice(P, VAL_WIN)
    sl_disc = _win_slice(P, DISC_WIN)
    if family == "rev":
        s1, s2, meta = rev_sim_faces(P, cell)
        extra = {"entries": meta["entries"], "trades": meta["trades"],
                 "unfillable": meta["unfillable"], "skips": meta["skips"],
                 "exits": meta["exits"], "cohorts": meta["cohorts"]}
    elif family == "lowamp":
        s1, s2, turnover = lowamp_sim_faces(P, cell)
        extra = {"turnover_1w": round(turnover, 3)}
    else:
        s1, s2, turnover = mom_sim_faces(P, cell)
        extra = {"turnover_1w": round(turnover, 3)}

    ew = P["ew_ret"]
    row = {"family": family, "cell": cell["name"],
           "params": {k: v for k, v in cell.items() if k != "name"},
           "cell_index": cell["cell_index"], "evidence_cutoff": EVIDENCE_CUTOFF,
           "windows": {"validation": VAL_WIN, "discovery": DISC_WIN},
           "x1": {}, "x2": {}, "passive": {}, "burned_by": _machine_id(),
           "burned_at": _now_iso(), "elapsed_s": round(time.time() - t0, 2),
           "seed_key": NULLS_SEED_KEY, "seed_base": NULLS_SEED, **extra}
    for face, s in (("x1", s1), ("x2", s2)):
        row[face] = {"validation": win_stats(s[sl_val]),
                     "discovery": win_stats(s[sl_disc])}
    row["passive"] = {"validation": win_stats(ew[sl_val]),
                      "discovery": win_stats(ew[sl_disc])}
    row["beat_val"] = round(row["x1"]["validation"]["ann_ret"]
                            - row["passive"]["validation"]["ann_ret"], 6)
    nulls = dual_nulls(s1[sl_val], cell["cell_index"])
    row["nulls"] = nulls
    p_s, p_b = nulls.get("p_sign"), nulls.get("p_block")
    same_sign = (row["x1"]["validation"]["ann_ret"] > 0
                 and row["x1"]["discovery"]["ann_ret"] > 0)
    row["robust"] = bool(p_s is not None and p_s < 0.05 and p_b is not None
                         and p_b < 0.05 and same_sign
                         and row["x1"]["validation"]["sharpe_full"] > 0)
    return row


def cell_path(family, name) -> str:
    return os.path.join(CELLS_DIR, family, f"cell-{name}.json")


# --------------------------------------------------------------------------
# pool claim handshake (lowamp_p1 canon; r497 same-commit law)
# --------------------------------------------------------------------------
_CLAIM_STARTED = None


def _pool_claim(entry_id: str, shard_key: str, detail: str,
                write: bool = True) -> None:
    if not write:
        return
    d = os.path.join(ROOT, "results", "pool_claims", entry_id)
    os.makedirs(d, exist_ok=True)
    fp = os.path.join(d, f"{shard_key}.{_machine_id()}.json")
    now = _now_iso()
    _dump({"machine_id": _machine_id(), "state": "closed",
           "pid": os.getpid(), "heartbeat": now, "outcome": "ok",
           "exit_code": 0, "started": _CLAIM_STARTED, "closed_at": now,
           "result_ref": detail}, fp)


# --------------------------------------------------------------------------
# worker pool (O-20260930-2355 multicore law; r304 initializer pattern)
# --------------------------------------------------------------------------
_W: dict = {}


def _worker_init(family: str, universe: list[str]) -> None:
    try:
        import psutil
        pri = getattr(psutil, "BELOW_NORMAL_PRIORITY_CLASS", None)
        if pri is not None:
            try:
                psutil.Process().nice(pri)      # low-priority pool law
            except Exception:
                pass
    except Exception:
        pass
    P = _panel_from_cache(universe)
    assert P is not None, "worker: panel cache missing (run probe first)"
    revo.T_EXPECT = P["F"]["close"].shape[0]
    revo.HOLD_BUFFER = HOLD_BUFFER_FURNACE
    _W["P"] = P
    _W["family"] = family


def _worker_task(cell: dict) -> dict:
    return burn_cell(_W["P"], _W["family"], cell)


# --------------------------------------------------------------------------
# commands
# --------------------------------------------------------------------------
def cmd_probe(args) -> int:
    os.makedirs(OUT_DIR, exist_ok=True)
    st = json.load(open(ASTOCK_STATUS, encoding="utf-8"))
    panel = st.get("panel", {})
    if not (panel.get("complete") and panel.get("cutoff") == EVIDENCE_CUTOFF):
        print(f"probe: panel not complete at cutoff {EVIDENCE_CUTOFF}: {panel}")
        return 2
    per_files = len([p for p in os.listdir(PANEL_DIR) if p.endswith(".csv")])
    uni = _universe()
    P = build_panel(uni)
    i_val = int(np.searchsorted(P["idx"], np.datetime64(VAL_WIN[0])))
    ma200_all = np.isfinite(P["ma200"])
    gate_cover = float(ma200_all[i_val:].mean())    # measured from val start
    gate_warmup_head = int((~ma200_all[:i_val]).sum())  # 200d head, disclosed
    facts = {"per_files": per_files, "cutoff": EVIDENCE_CUTOFF,
             "universe_n": len(uni), "panel_rows": int(len(P["idx"])),
             "panel_from": PANEL_FROM,
             "first": str(P["idx"][0].date()), "last": str(P["idx"][-1].date()),
             "elig_median": P["elig_median"], "elig_median_min": 150,
             "gate_cover": gate_cover,
             "gate_cover_from": VAL_WIN[0],
             "gate_warmup_head_days": gate_warmup_head,
             "gate_cover_min": 0.999,
             "elig_sha16": _sha16(ELIG_CSV),
             "elig_face_sha16": _sha16_text("\n".join(_elig_code_face())),
             "mask_sha16": _sha16(MASK_CSV),
             "n_cells_total": N_CELLS_TOTAL,
             "rev_cells": len(rev_cells()), "lowamp_cells": len(lowamp_cells()),
             "mom_cells": len(mom_cells()),
             "cost_x1": COST_X1, "seed_key": NULLS_SEED_KEY,
             "seed_base": NULLS_SEED,
             "probed_at": _now_iso(), "probed_by": _machine_id()}
    if facts["elig_median"] < facts["elig_median_min"]:
        print(f"probe: eligible median {facts['elig_median']} below floor")
        return 2
    if facts["gate_cover"] < facts["gate_cover_min"]:
        print(f"probe: 510300 MA200 coverage {facts['gate_cover']} below floor")
        return 2
    _panel_to_cache(P)
    _dump(facts, PROBE_FILE)
    print(f"probe: OK universe={len(uni)} rows={facts['panel_rows']} "
          f"elig_median={facts['elig_median']} cells={N_CELLS_TOTAL} "
          f"cache={os.path.basename(PANEL_CACHE)}")
    return 0


def _require_probe() -> dict:
    if not os.path.exists(PROBE_FILE):
        print("run: probe_facts.json missing -- run probe first (FAIL-CLOSED)")
        raise SystemExit(2)
    return json.load(open(PROBE_FILE, encoding="utf-8"))


def _assert_probe_fresh(P, facts, uni) -> None:
    st = json.load(open(ASTOCK_STATUS, encoding="utf-8"))
    panel = st.get("panel", {})
    assert panel.get("complete") and panel.get("cutoff") == EVIDENCE_CUTOFF, \
        "panel status drift (cutoff lockbox)"
    assert len(uni) == facts["universe_n"], "universe drift vs probe"
    assert int(len(P["idx"])) == facts["panel_rows"], "panel rows drift vs probe"
    assert P["elig_median"] == facts["elig_median"], "elig median drift vs probe"
    if "elig_face_sha16" in facts:
        # r503: pin the consumed face (code set); raw sha16 stays in facts
        # as provenance only -- np-column refresh with identical code set
        # passes, any code addition/removal still fails closed.
        assert _sha16_text("\n".join(_elig_code_face())) \
            == facts["elig_face_sha16"], "eligibility code-face drift"
    else:
        assert _sha16(ELIG_CSV) == facts["elig_sha16"], \
            "eligibility snapshot drift (legacy pin -- re-probe to upgrade)"
    assert _sha16(MASK_CSV) == facts["mask_sha16"], "b_layer mask drift"


def cmd_run(args) -> int:
    global _CLAIM_STARTED
    _CLAIM_STARTED = _now_iso()
    facts = _require_probe()
    workers = int(min(args.workers or WORKERS_CAP, WORKERS_CAP))
    ram = _free_ram_gb()
    floor = _ram_floor_gb(workers)
    if ram < floor:
        # r491 park family (resource-wait cousin of the data-wait law):
        # free-RAM gate exit 3 is an honest zero-burn refusal, NOT a
        # crash -- live 2026-10-01: rev-0to31 exit-3 fed the fuse and
        # 21 refusals froze the shard. Marker -> confirmer parks the
        # entry instead of fusing; un-park = RAM frees above floor.
        import datetime as _dt
        print(_dt.datetime.now().strftime(
            "AUTOFILL-PARK: %Y-%m-%d %H:%M:%S ")
              + f"free-RAM gate {ram:.1f}GB < floor {floor:.1f}GB "
              f"(workers={workers}) -- honest zero-burn, exit 3")
        print(f"run: free RAM {ram:.1f}GB below floor {floor:.1f}GB "
              f"(workers={workers}) -- exit 3")
        return 3
    os.makedirs(os.path.join(CELLS_DIR, args.family), exist_ok=True)
    uni = _universe()
    P = _panel_from_cache(uni)
    if P is None:
        P = build_panel(uni)
        _panel_to_cache(P)
    _assert_probe_fresh(P, facts, uni)
    revo.T_EXPECT = P["F"]["close"].shape[0]
    revo.HOLD_BUFFER = HOLD_BUFFER_FURNACE

    cells = FAMILIES[args.family]()
    a, _, b = args.cells.partition(":")
    a, b = int(a), int(b)
    block = cells[a:b]
    if not block:
        print(f"run: empty cell block {args.cells}")
        return 2
    todo = [c for c in block
            if not os.path.exists(cell_path(args.family, c["name"]))]
    print(f"run: family={args.family} cells[{a}:{b}]={len(block)} "
          f"todo={len(todo)} ram={ram:.1f}GB T={revo.T_EXPECT} "
          f"seed_base={NULLS_SEED} workers<={WORKERS_CAP}")
    t0 = time.time()
    if todo:
        from concurrent.futures import ProcessPoolExecutor, as_completed
        with ProcessPoolExecutor(max_workers=workers,
                                 initializer=_worker_init,
                                 initargs=(args.family, uni)) as pool:
            futs = {pool.submit(_worker_task, c): c for c in todo}
            n = 0
            for fut in as_completed(futs):
                row = fut.result()
                _dump(row, cell_path(args.family, row["cell"]))
                n += 1
                print(f"  {row['cell']} done (val sharpe "
                      f"{row['x1']['validation']['sharpe_full']}, p_sign "
                      f"{row['nulls'].get('p_sign')}, {row['elapsed_s']}s, "
                      f"{n}/{len(todo)}, {time.time() - t0:.0f}s elapsed)")
    entry_id = f"STOCKFURN-{args.family.upper()}-AKSHARE-SHARD-{a}"
    shard_key = f"stockfurn-{args.family}-{a}to{b}"
    _pool_claim(entry_id, shard_key,
                f"cells {len(block)} -> {CELLS_DIR}/{args.family} "
                f"({facts['cutoff']} face, prereg STOCK_FACE_FURNACE_P1)")
    print(f"run: shard complete {entry_id}/{shard_key} "
          f"({time.time() - t0:.0f}s)")
    return 0


def cmd_finalize(args) -> int:
    family = args.family
    cells = FAMILIES[family]()
    rows, missing = [], []
    for c in cells:
        fp = cell_path(family, c["name"])
        if not os.path.exists(fp):
            missing.append(c["name"])
            continue
        rows.append(json.load(open(fp, encoding="utf-8")))
    if missing:
        print(f"finalize: {family} missing {len(missing)}/{len(cells)} cells "
              f"({missing[:5]}...) -- FAIL-CLOSED, burn shards first")
        return 2
    rows.sort(key=lambda r: r["x1"]["validation"]["sharpe_full"], reverse=True)
    robust = [r for r in rows if r["robust"]]
    summary = {"family": family, "evidence_cutoff": EVIDENCE_CUTOFF,
               "prereg": "research/STOCK_FACE_FURNACE_P1.md (frozen r502)",
               "n_cells": len(rows), "n_robust": len(robust),
               "expected_false_positives": round(len(rows) * 0.05, 1),
               "windows": {"validation": VAL_WIN, "discovery": DISC_WIN},
               "cost_x1": COST_X1, "seed_key": NULLS_SEED_KEY,
               "ranked": [
                   {"cell": r["cell"], "params": r["params"],
                    "val_sharpe": r["x1"]["validation"]["sharpe_full"],
                    "val_ann": r["x1"]["validation"]["ann_ret"],
                    "val_dd": r["x1"]["validation"]["max_dd"],
                    "disc_ann": r["x1"]["discovery"]["ann_ret"],
                    "x2_val_sharpe": r["x2"]["validation"]["sharpe_full"],
                    "beat_val": r["beat_val"],
                    "p_sign": r["nulls"].get("p_sign"),
                    "p_block": r["nulls"].get("p_block"),
                    "robust": r["robust"]} for r in rows],
               "robust_bands": [
                   {"cell": r["cell"], "params": r["params"],
                    "val_sharpe": r["x1"]["validation"]["sharpe_full"],
                    "p_sign": r["nulls"].get("p_sign"),
                    "p_block": r["nulls"].get("p_block")} for r in robust],
               "finalized_at": _now_iso(), "finalized_by": _machine_id()}
    _dump(summary, os.path.join(OUT_DIR, f"{family}_summary.json"))
    import csv
    with open(os.path.join(OUT_DIR, f"{family}_cells.csv"), "w",
              encoding="utf-8", newline="") as f:
        wtr = csv.writer(f)
        wtr.writerow(["cell", "val_sharpe", "val_ann", "val_dd", "disc_ann",
                      "x2_val_sharpe", "beat_val", "p_sign", "p_block",
                      "robust"])
        for r in summary["ranked"]:
            wtr.writerow([r["cell"], r["val_sharpe"], r["val_ann"],
                          r["val_dd"], r["disc_ann"], r["x2_val_sharpe"],
                          r["beat_val"], r["p_sign"], r["p_block"],
                          r["robust"]])
    print(f"finalize: {family} n={len(rows)} robust={len(robust)} "
          f"(expected FP~{summary['expected_false_positives']})")

    all_done = all(os.path.exists(os.path.join(OUT_DIR, f"{fam}_summary.json"))
                   for fam in FAMILIES)
    guard = os.path.join(OUT_DIR, ".ledger_appended")
    if all_done and not os.path.exists(guard):
        res = sg.append_ledger("STOCK_FACE_FURNACE_P1", N_CELLS_TOTAL,
                               "stock_face_furnace",
                               note="T-139 akshare-face exploration furnace "
                                    "(281 cells; supply=trial stock grammar)",
                               evidence_cutoff=EVIDENCE_CUTOFF)
        with open(guard, "w", encoding="utf-8") as f:
            f.write(_now_iso() + "\n")
        print(f"finalize: trials ledger appended -> total {res.get('total')}")
    return 0


# --------------------------------------------------------------------------
# selftest (hermetic; real grammar-key access per r494/r506 laws)
# --------------------------------------------------------------------------
def cmd_selftest(args) -> int:
    import pandas as pd
    checks = []

    def ck(name, cond, detail=""):
        checks.append((name, bool(cond), detail))
        print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")

    rc, lc, mc = rev_cells(), lowamp_cells(), mom_cells()
    ck("rev enumeration 121 (128 minus 7 judged)",
       len(rc) == 121, f"got {len(rc)}")
    ck("lowamp enumeration 144", len(lc) == 144, f"got {len(lc)}")
    ck("mom enumeration 16", len(mc) == 16, f"got {len(mc)}")
    ck("total 281", N_CELLS_TOTAL == 281, f"got {N_CELLS_TOTAL}")
    got = {(c["yang"], c["dwr"], c["gate"], c["tpsl"], c["H"], c["w"]) for c in rc}
    ck("judged cells excluded 7/7", not (got & REV_JUDGED),
       f"overlap {len(got & REV_JUDGED)}")
    ck("cell_index unique 281",
       len({c["cell_index"] for c in rc + lc + mc}) == 281)
    ck("rev H axes {5,7,10,20}", {c["H"] for c in rc} == {5, 7, 10, 20})

    ck("seed key registered", NULLS_SEED_KEY in sg.SEED_REGISTRY,
       f"base {NULLS_SEED}")
    ck("seed band disjoint vs lowamp_p1_nulls",
       NULLS_SEED >= sg.SEED_REGISTRY["lowamp_p1_nulls"] + 2000)
    ck("cost single-source import", COST_X1 == 0.0013041)

    rng = np.random.default_rng(7)
    s = rng.normal(0.001, 0.01, 600)
    n1, n2 = dual_nulls(s, 0), dual_nulls(s, 0)
    ck("nulls deterministic (same seed->same p)", n1 == n2)
    ns = dual_nulls(np.full(10, 0.01), 1)
    ck("nulls insufficient-days leg", ns["p_sign"] is None and ns["n_days"] == 10)
    z = dual_nulls(rng.normal(0.0, 0.01, 2000), 2)
    ck("nulls null-hypothesis p in (0,1)", 0.0 < z["p_sign"] < 1.0,
       f"p={z['p_sign']}")

    ws = win_stats(np.full(252, 0.01))
    ck("win_stats constant leg", abs(ws["ann_ret"] - (1.01 ** 252 - 1)) < 0.1
       and ws["max_dd"] == 0.0, f"ann={ws['ann_ret']}")

    # synthetic panel -> real engine paths (rev + lowamp + mom);
    # dates span both frozen windows (validation + discovery)
    T, N = 900, 6
    idx = pd.bdate_range("2023-01-02", periods=T)
    F = {"open": np.full((T, N), 10.0, np.float32),
         "high": np.full((T, N), 10.2, np.float32),
         "low": np.full((T, N), 9.8, np.float32),
         "close": np.full((T, N), 10.0, np.float32)}
    drift = np.linspace(0.0, -0.30, T).astype(np.float32)   # falling market
    for k in F:
        F[k] = (F[k] * (1.0 + drift)[:, None]).astype(np.float32)
    F["pct_chg"] = np.zeros((T, N), np.float32)
    F["pct_chg"][1:] = (F["close"][1:] / F["close"][:-1] - 1.0)
    F["amount"] = np.full((T, N), 1e8, np.float32)
    P = {"idx": idx, "syms": [f"S{i}" for i in range(N)],
         "board": {f"S{i}": "main" for i in range(N)}, "F": F,
         "fl": np.full((N, T), 0.0975, np.float32),
         "elig": np.ones((T, N), dtype=bool),
         "drop20": F["pct_chg"].copy(), "drop60": F["pct_chg"].copy(),
         "sse": np.linspace(3000, 2500, T), "ma200": np.full(T, 2800.0),
         "ew_ret": np.full(T, float(F["pct_chg"][:, 0].mean()))}
    P["drop20"] = np.vstack([np.full((20, N), np.nan, np.float32),
                             F["close"][20:] / F["close"][:-20] - 1.0]).astype(np.float32)
    P["drop60"] = np.vstack([np.full((60, N), np.nan, np.float32),
                             F["close"][60:] / F["close"][:-60] - 1.0]).astype(np.float32)
    P["col"] = {f: np.ascontiguousarray(F[f].T)
                for f in ("open", "high", "low", "close")}
    revo.T_EXPECT = T
    revo.HOLD_BUFFER = HOLD_BUFFER_FURNACE
    try:
        row = burn_cell(P, "rev", rc[0])
        ck("rev real-path burn leg", "x1" in row and "nulls" in row,
           f"entries={row.get('entries')} val_sharpe="
           f"{row['x1']['validation']['sharpe_full']}")
    except Exception as exc:
        ck("rev real-path burn leg", False, f"exc={type(exc).__name__}:{exc}")
    lc0 = [c for c in lc if c["W"] == 40 and c["N"] == 2
           and c["sizing"] == "eq" and c["gate"] == "none"][0]
    try:
        s1, s2, to = lowamp_sim_faces(P, lc0)
        ck("lowamp real-path leg", s1.shape == (T,) and to > 0,
           f"turnover={to:.1f}")
        ck("lowamp x2 <= x1 (cost order)",
           float(np.nansum(s2)) <= float(np.nansum(s1)) + 1e-12)
    except Exception as exc:
        ck("lowamp real-path leg", False, f"exc={type(exc).__name__}:{exc}")
    try:
        s1, s2, to = mom_sim_faces(P, mc[0])
        ck("mom real-path leg", s1.shape == (T,) and to > 0,
           f"turnover={to:.1f}")
    except Exception as exc:
        ck("mom real-path leg", False, f"exc={type(exc).__name__}:{exc}")

    # hand-value cost leg (r474 law): 2 assets, constant weights, one rebalance
    T2 = 10
    pct2 = np.array([[0.01, -0.01]] * T2, dtype=np.float32)
    w = np.array([[0.5, 0.5]] * T2)
    out = np.zeros(T2)
    prev_w = np.zeros(2)
    for t in range(1, T2):
        if prev_w.any():
            out[t] = float((prev_w * pct2[t]).sum())
        out[t] -= COST_FACES["x1"] * float(np.abs(w[t] - prev_w).sum())
        prev_w = w[t]
    ck("hand-value day1 (cost only)",
       abs(out[1] - (-COST_FACES["x1"])) < 1e-9, f"out1={out[1]:.6f}")
    ck("hand-value day2 (zero drift)",
       abs(out[2] - 0.0) < 1e-9, f"out2={out[2]:.6f}")

    _pool_claim("SELFTEST-ENTRY", "selftest-shard", "selftest", write=False)
    ck("claim write=False no-op",
       not os.path.exists(os.path.join(ROOT, "results", "pool_claims",
                                       "SELFTEST-ENTRY")))
    ck("evidence_cutoff constant", EVIDENCE_CUTOFF == "2026-09-30")

    n_fail = sum(1 for _, ok, _ in checks if not ok)
    print(f"selftest: {len(checks) - n_fail}/{len(checks)} PASS")
    os.makedirs(OUT_DIR, exist_ok=True)
    _dump({"ts": _now_iso(), "machine_id": _machine_id(),
           "n_checks": len(checks), "n_fail": n_fail,
           "checks": [{"name": n, "ok": ok, "detail": d}
                      for n, ok, d in checks]},
          os.path.join(OUT_DIR, "selftest.json"))
    return 1 if n_fail else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("probe")
    sub.add_parser("selftest")
    rn = sub.add_parser("run")
    rn.add_argument("--family", required=True, choices=list(FAMILIES))
    rn.add_argument("--cells", default="0:0",
                    help="cell block a:b (end-exclusive), e.g. 0:31")
    rn.add_argument("--workers", type=int, default=None)
    fn = sub.add_parser("finalize")
    fn.add_argument("--family", required=True, choices=list(FAMILIES))
    args = ap.parse_args()
    if args.cmd == "probe":
        return cmd_probe(args)
    if args.cmd == "selftest":
        return cmd_selftest(args)
    if args.cmd == "run":
        return cmd_run(args)
    return cmd_finalize(args)


if __name__ == "__main__":
    raise SystemExit(main())
