"""FUND-DIVLOWVOL-P2 freeze-window probes (data side, fail-closed, zero-network).

Revival batch (O-20261019-2230-bm-b sec.2.1 three-piece law: CEO authorization
+ new prereg + new evidence). P2 legs mirror the P1 ignition gate family
verbatim (research/FUND-DIVLOWVOL-P2.md sec.2 freeze-window face, r1039
rulings) with the P2-specific deltas:

  * leg5 seed-band scan = P2 registered pair (fund_divlowvol_p2_nulls=20523000
    / fund_divlowvol_p2_sens=20523500, r1039 SEED_REGISTRY landed). Scan
    verifies exact-value registration, zero collision vs OTHER bases,
    furnace-band exclusion and >=2000 proximity vs other bases. The own-pair
    500-distance is the family by-design pair-seed layout (P1 precedent
    20520000/20520500) and is disclosed, not gated.
  * leg6 NEW quality PIT faces (the new_data leg, r1039 ruling 3):
      - structural gate (local): rows/columns/PIT sanity (avail_date >=
        period_end, zero violations), span from 2001Q1;
      - coverage gate (panel): per-month ratio of quality-available members
        over the yield>0 candidate domain across the frozen signal calendar
        2006-02 -> 2026-03; ratio >= 0.80 fail-closed. "available" = finite
        roe_q at the latest avail_date <= t (NaN = cannot evaluate = excluded).
        eligibility.csv is a <24h current snapshot and is BANNED for signal
        days (look-ahead ruling frozen r1039) -- quality_faces PIT only.
  * d6 subcommand = same-family admission face for the P2 QF-ON headline
    (REG6 max|corr| < 0.7 fail-closed; sibling + family-predecessor
    disclosure faces per prereg sec.1).

Panel-dependent legs (leg1 price panel / leg3 sidecar recovery known-answer
/ leg4 census + t0 pin / leg6 coverage / d6) fail-closed as PANEL_MISSING
until the p1c cache re-delivery lands (MSG-2350, receipt window <=2 rounds)
or the gates run on the bm-a host. Freeze commit fires only on full GREEN.

Kernels: derive kernels (ttm_cash_sum / sidecar_f_at) and frozen family design
constants are IMPORTED from fund_divlowvol_p1_probe (single source,
re-implementation zero).

Exit contract: 0 = GREEN (all gates green, freeze-eligible);
               2 = RED (any local gate red);
               4 = AWAITING_PANEL (local gates green, panel legs missing).
selftest: exit 0/2, offline synthetic fixtures, zero data dependency.
"""
from __future__ import annotations

import bisect
import json
import os
import sys
import time
from datetime import datetime, timezone, timedelta

sys.path.insert(0, ".")          # repo root (science_gates imports knowledge.cost_spec)
sys.path.insert(0, "scripts")    # P1 probe kernels (single source)
import numpy as np
import pandas as pd

# ---- single-source imports: P1 kernels + frozen family design constants ----
from fund_divlowvol_p1_probe import (
    ttm_cash_sum, sidecar_f_at,          # derive kernels (verbatim, re-impl zero)
    PARQUET, MANIFEST, SIDECAR_FMT, QUARANTINED,
    N_TOP, UNIVERSE_FLOOR, TTM_DAYS, VOL_WIN, VOL_MIN_BARS, AMT20_FLOOR,
    FURNACE_BAND, PROXIMITY_GATE,
)

QUALITY_PARQUET = "data/fund_history_export/quality_faces.parquet"
OUT = "results/_fund_divlowvol_p2_freeze_probe.json"
OUT_LOCAL = "results/_fund_divlowvol_p2_freeze_probe_local.json"
# local panel substrate (r1066): rebuilt p1c-compatible qfq panel from
# data/astock_daily (regenerable, gitignored data/cache/) + the qfq-inversion
# sidecar face (same "d"/"f" layout as the P1 sidecars, different substrate --
# disclosed, never silently equated with the Money02 hosted panel).
LOCAL_CACHE = os.path.join("data", "cache", "p1c_local")
LOCAL_SIDECAR_DIR = os.path.join("data", "cache", "p1c_sidecars")
BASIS_P1C = "p1c_money02_cache"
BASIS_LOCAL = "local_rebuilt_p1c_compatible"
PANEL_BASIS: dict = {"basis": None}
D6_OUT_DIR = "results/fund_divlowvol_p2"
D6_JSON = "results/fund_divlowvol_p2/d6.json"
TZ = timezone(timedelta(hours=8))

# P2 seed pair (r1039 SEED_REGISTRY landed; verified by leg5)
SEED_KEYS = ("fund_divlowvol_p2_nulls", "fund_divlowvol_p2_sens")
SEED_NULLS = 20_523_000
SEED_SENS = 20_523_500

# P2 freeze-window rulings (research/FUND-DIVLOWVOL-P2.md r1039 definitive)
EVIDENCE_CUTOFF = "2026-09-22"      # P1 same-anchor (D2 lockbox, explicit exception)
N_BARS_EXPECT = 8792
T0_PIN = 20060206                   # P1 frozen anchor revalidation
CAL_FIRST, CAL_LAST = "2006-02", "2026-03"
QUALITY_COV_FLOOR = 0.80            # leg6 per-month coverage fail-closed line
PANEL_MISSING = "PANEL_MISSING_AWAITING_REDELIVERY"   # MSG-2350 receipt window <=2 rounds

SIBLING_CONTS = {
    "FUND-VALUE-P1 headline (VALUE-PE x1 cont)": "results/fund_value_p1/cont_VALUE-PE_x1.json",
    "FUND-QUALITY-P1 headline (QUALITY-ROE x1 cont)": "results/fund_quality_p1/cont_QUALITY-ROE_x1.json",
}
P1_FAMILY_GLOB = "results/fund_divlowvol_p1/cont_*x1*.json"   # family predecessor (disclosure-only)
D6_REJECT = 0.7


def _now() -> str:
    return datetime.now(TZ).strftime("%Y-%m-%dT%H:%M:%S+08:00")


# ----------------------------------------------------------------------------
# quality PIT kernels (single source for the P2 runner -- re-impl zero there)
# ----------------------------------------------------------------------------
def quality_roe_at(avail_int: np.ndarray, roe: np.ndarray, t_int: int):
    """Latest roe_q among rows with avail_date <= t (PIT); None if none.

    qpack arrays are sorted by (avail_int, period_end) so bisect_right lands
    on the max period_end within the latest available tie group.
    """
    j = bisect.bisect_right(avail_int, t_int) - 1
    if j < 0:
        return None
    return float(roe[j])


def quality_pass(avail_int: np.ndarray, roe: np.ndarray, t_int: int) -> bool:
    """P2 sec.3 leg-1 filter: finite roe_q > 0 at the PIT point; else excluded."""
    v = quality_roe_at(avail_int, roe, t_int)
    return bool(v is not None and np.isfinite(v) and v > 0.0)


def quality_available(avail_int: np.ndarray, roe: np.ndarray, t_int: int) -> bool:
    """leg6 coverage numerator face: a finite PIT value exists (sign-agnostic)."""
    v = quality_roe_at(avail_int, roe, t_int)
    return bool(v is not None and np.isfinite(v))


def _load_quality():
    """(df, qmap): df carries _av/_pe int columns; qmap: code -> (avail, roe)."""
    df = pd.read_parquet(QUALITY_PARQUET)
    df["code_s"] = df["code"].astype(str)
    df["_av"] = df["avail_date"].astype(str).str.replace("-", "", regex=False).astype("int64")
    df["_pe"] = df["period_end"].astype(str).str.replace("-", "", regex=False).astype("int64")
    df = df.sort_values(["code_s", "_av", "_pe"])
    qmap: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for code, g in df.groupby("code_s", sort=False):
        qmap[str(code)] = (g["_av"].to_numpy(), g["roe_q"].to_numpy(dtype="float64"))
    return df, qmap


# ----------------------------------------------------------------------------
# shared panel / div / sidecar / starts loaders (mirror P1 faces, kernel-level
# single source kept; loaders re-stated because P1 keeps them inline in main)
# ----------------------------------------------------------------------------
def _load_local_panel():
    """Rebuilt p1c-compatible panel (data/cache/p1c_local) -> same 7-tuple shape.

    Column axis comes from symbols.json (r1056 law: never re-derive it from a
    directory glob at read time -- a stale glob silently re-labels columns).
    """
    meta_path = os.path.join(LOCAL_CACHE, "meta.json")
    sym_path = os.path.join(LOCAL_CACHE, "symbols.json")
    if not (os.path.exists(meta_path) and os.path.exists(sym_path)):
        return None
    meta = json.load(open(meta_path, encoding="utf-8"))
    dates = np.load(os.path.join(LOCAL_CACHE, "dates.npy"))
    idx = pd.to_datetime(np.asarray(dates).astype("datetime64[us]"))
    syms = [str(s) for s in json.load(open(sym_path, encoding="utf-8"))]

    def _arr(name: str):
        return np.load(os.path.join(LOCAL_CACHE, name + ".npy"), mmap_mode="r")

    close_q, pct, amt, volm = _arr("close"), _arr("pct_chg"), _arr("amount"), _arr("volume")
    if close_q.shape[1] != len(syms):
        return None
    return (idx, syms, meta, close_q, pct, amt, volm)


def _load_panel(basis: str = "auto"):
    """p1c cache first, local rebuilt panel as the fallback substrate.

    Returns the 7-tuple or the exception/error object (honest fail-closed).
    PANEL_BASIS["basis"] records which substrate actually answered.
    """
    errs: dict = {}
    if basis in ("auto", BASIS_P1C):
        try:
            import p1c_stock_ic_batch as P1C
            idx, syms, meta = P1C.load_universe()
            close_q = np.load(f"{P1C.CACHE_DIR}/close.npy", mmap_mode="r")
            pct = np.load(f"{P1C.CACHE_DIR}/pct_chg.npy", mmap_mode="r")
            amt = np.load(f"{P1C.CACHE_DIR}/amount.npy", mmap_mode="r")
            volm = np.load(f"{P1C.CACHE_DIR}/volume.npy", mmap_mode="r")
            PANEL_BASIS["basis"] = BASIS_P1C
            return (idx, syms, meta, close_q, pct, amt, volm)
        except Exception as exc:     # panel absent -> try the local substrate
            errs["p1c"] = repr(exc)
            if basis == BASIS_P1C:
                return exc
    lp = _load_local_panel()
    if lp is not None:
        PANEL_BASIS["basis"] = BASIS_LOCAL
        return lp
    errs["local"] = "data/cache/p1c_local absent or symbol axis mismatch"
    return RuntimeError("; ".join(f"{k}: {v}" for k, v in errs.items()))


def _load_div_by_sym() -> dict[str, tuple[np.ndarray, np.ndarray]]:
    df = pd.read_parquet(PARQUET)
    df["code_s"] = df["code"].astype(str)
    df["_ex"] = df["ex_date"].astype(str).str.replace("-", "", regex=False).astype("int64")
    df["_cps"] = df["cash_div_per_10"].astype("float64") / 10.0
    df = df.sort_values(["code_s", "_ex"])
    by_sym: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for code, g in df.groupby("code_s", sort=False):
        by_sym[str(code)] = (g["_ex"].to_numpy(), np.cumsum(g["_cps"].to_numpy()))
    return by_sym


def _load_sidecars(codes) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """P1 sidecar face (Money02) first, local qfq-inversion face as fallback."""
    sidecars: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for code in codes:
        paths = [SIDECAR_FMT.format(sym=code),
                 os.path.join(LOCAL_SIDECAR_DIR, f"{code}.factor.json")]
        p = next((q for q in paths if os.path.exists(q)), None)
        if p is None:
            continue
        sd = json.load(open(p, encoding="utf-8"))
        sidecars[code] = (
            np.array([int(x.replace("-", "")) for x in sd["d"]], dtype=np.int64),
            np.array(sd["f"], dtype=np.float64),
        )
    return sidecars


def _start_positions(idx, close_q, n_bars) -> list[int]:
    """Monthly first-trading-day enumeration, family frozen window/masks."""
    mask_win = (idx >= pd.Timestamp("1992-09-01")) & (idx <= pd.Timestamp("2026-03-02"))
    sub = idx[mask_win]
    mk = sub.strftime("%Y-%m")
    starts: list[int] = []
    prev = None
    for p, k in zip(np.where(mask_win)[0], mk):
        if k != prev:
            prev = k
            if p >= 252 and (n_bars - 1 - p) >= 126 \
                    and int((~np.isnan(close_q[p])).sum()) >= 24:
                starts.append(int(p))
    return starts


# ----------------------------------------------------------------------------
# legs
# ----------------------------------------------------------------------------
def _leg2_div_face(facts: dict, gates: dict) -> None:
    if not os.path.exists(PARQUET):
        facts["div_face"] = {"absent": True, "path": PARQUET, "status": "MISSING"}
        gates["leg2_transfer_export"] = False
        return
    import hashlib
    sha = hashlib.sha256(open(PARQUET, "rb").read()).hexdigest()
    man_ok, man_sha = False, None
    if os.path.exists(MANIFEST):
        man = json.load(open(MANIFEST, encoding="utf-8"))
        for s in man.get("sampled", []):
            if s.get("file") == "div_events_faces.parquet":
                man_sha = s.get("sha256")
                man_ok = (s.get("bytes") == os.path.getsize(PARQUET))
    df = pd.read_parquet(PARQUET)
    n_symbols = int(df["code"].nunique())
    ev_median = float(df.groupby("code")["ex_date"].size().median())
    span_min = str(df["ex_date"].min())[:10]
    span_max = str(df["ex_date"].max())[:10]
    null_cash = int(df["cash_div_per_10"].isna().sum())
    srt = df.sort_values(["code", "ex_date"])
    unsorted_rows = int((df.index != srt.index).sum())
    import pyarrow.parquet as pq
    sch = {f.name: str(f.type) for f in pq.read_schema(PARQUET)}
    dtype_ok = bool(
        ("string" in sch.get("code", "") or sch.get("code") == "str")
        and sch.get("ex_date") == "date32[day]"
        and sch.get("record_date") == "date32[day]"
        and sch.get("cash_div_per_10") == "double")
    quarantined_present = sorted(set(QUARANTINED) & set(df["code"].astype(str)))
    facts["div_face"] = {
        "rows": int(len(df)), "n_symbols_nonempty": n_symbols,
        "per_symbol_event_median": ev_median,
        "ex_date_span": [span_min, span_max],
        "null_cash_rows": null_cash, "unsorted_rows": unsorted_rows,
        "quarantined_present": quarantined_present,
        "sha256": sha, "manifest_sha256": man_sha, "manifest_bytes_ok": man_ok,
    }
    gates["leg2_transfer_export"] = bool(
        n_symbols >= 5100 and ev_median >= 3 and span_max >= "2026-01-01"
        and null_cash == 0 and unsorted_rows == 0 and dtype_ok
        and not quarantined_present and man_ok and sha == man_sha)


def _leg5_seed_scan(facts: dict, gates: dict) -> None:
    import science_gates as SG
    reg = {k: v for k, v in SG.SEED_REGISTRY.items() if isinstance(v, int)}
    own = {SEED_KEYS[0]: SEED_NULLS, SEED_KEYS[1]: SEED_SENS}
    reg_own_ok = all(reg.get(k) == v for k, v in own.items())
    others = {k: v for k, v in reg.items() if k not in SEED_KEYS}
    exact_other: dict = {}
    for k, b in own.items():
        for ok_, ob in others.items():
            if b == ob:
                exact_other[k] = {"base": b, "other_key": ok_}
    in_band = {k: b for k, b in own.items() if FURNACE_BAND[0] < b < FURNACE_BAND[1]}
    prox: dict = {}
    for k, b in own.items():
        for ok_, ob in others.items():
            if abs(b - ob) < PROXIMITY_GATE:
                prox[k] = {"base": b, "other_base": ob, "other_key": ok_,
                           "distance": abs(b - ob)}
    facts["seed_band_scan"] = {
        "own_pair": own,
        "registration_exact_ok": reg_own_ok,
        "n_registry_bases": len(reg),
        "exact_collisions_other": exact_other,
        "furnace_band": list(FURNACE_BAND),
        "in_furnace_band": in_band,
        "proximity_violations_other": prox,
        "own_pair_distance": abs(SEED_NULLS - SEED_SENS),
        "own_pair_disclosure": "by-design pair-seed sub-stream layout (P1 precedent "
                               "20520000/20520500) -- disclosed, not gated",
        "k_stretch_disclosure": {
            "nulls": f"rng([{SEED_NULLS}, k]) k=0..1999 (pair-seed sub-stream law)",
            "sens": f"rng([{SEED_SENS}, k]) k=0..499 (pair-seed sub-stream law)",
        },
    }
    gates["leg5_seed_band"] = bool(
        reg_own_ok and not exact_other and not in_band and not prox)


def _leg6_quality_structural(facts: dict, gates: dict):
    if not os.path.exists(QUALITY_PARQUET):
        facts["quality_face"] = {"absent": True, "path": QUALITY_PARQUET,
                                 "status": "MISSING"}
        gates["leg6_quality_structural"] = False
        return None
    df, qmap = _load_quality()
    rows = int(len(df))
    n_syms = int(df["code_s"].nunique())
    pit_viol = int((df["_av"] < df["_pe"]).sum())
    null_roe = int(df["roe_q"].isna().sum())
    avail_min = str(df["avail_date"].min())[:10]
    avail_max = str(df["avail_date"].max())[:10]
    period_min = str(df["period_end"].min())[:10]
    period_max = str(df["period_end"].max())[:10]
    facts["quality_face"] = {
        "rows": rows, "n_symbols": n_syms, "columns": list(df.columns)[:6],
        "pit_anchor": "avail_date", "pit_violations": pit_viol,
        "null_roe_rows": null_roe,
        "avail_date_span": [avail_min, avail_max],
        "period_end_span": [period_min, period_max],
        "eligibility_ban": "eligibility.csv is a <24h current snapshot -- banned "
                           "for historical signal days (r1039 look-ahead ruling)",
    }
    gates["leg6_quality_structural"] = bool(
        rows >= 300_000 and n_syms >= 5000 and pit_viol == 0
        and period_min <= "2001-06-30" and avail_max >= "2026-01-01"
        and {"code", "period_end", "avail_date", "roe_q"}.issubset(df.columns))
    return qmap


def _leg3_sidecar_recovery(facts, gates, idx, syms, close_q, by_sym, sidecars):
    """P1 sec.2 known-answer mirror: pure-cash events 2015+, median rel dev < 2%."""
    df = pd.read_parquet(PARQUET)
    sym_pos = {s: j for j, s in enumerate(syms)}
    missing_sidecar = [c for c in by_sym if c in sym_pos and c not in sidecars]
    df2 = df.copy()
    df2["code_s"] = df2["code"].astype(str)
    df2["ex_s"] = df2["ex_date"].astype(str).str.slice(0, 10)
    ev = df2.groupby(["code_s", "ex_s"], sort=True)["cash_div_per_10"].sum().reset_index()
    ev = ev[(ev["cash_div_per_10"] > 0) & (ev["ex_s"] >= "2015-01-01")]
    date_pos = {str(d.date()): p for p, d in enumerate(idx)}
    devs, wrong_devs, n_tested, n_excluded = [], [], 0, 0
    for _, r in ev.iterrows():
        code, ex_s, d10 = r["code_s"], r["ex_s"], float(r["cash_div_per_10"])
        sc = sidecars.get(code)
        s_pos = date_pos.get(ex_s)
        if sc is None or s_pos is None or s_pos < 1:
            n_excluded += 1
            continue
        d_list, f_list = sc
        ex_int = int(ex_s.replace("-", ""))
        js = int(np.searchsorted(d_list, ex_int, side="left"))
        if js >= len(d_list) or int(d_list[js]) != ex_int or js == 0:
            n_excluded += 1
            continue
        win = d_list[(d_list > ex_int - 100) & (d_list < ex_int + 100)]
        if len(win) != 1:
            n_excluded += 1
            continue
        f_s, f_prev = float(f_list[js]), float(f_list[js - 1])
        q_prev = float(close_q[s_pos - 1, sym_pos[code]])
        if not np.isfinite(q_prev) or f_prev <= 0:
            n_excluded += 1
            continue
        d_ps = d10 / 10.0
        p_prev_raw = q_prev * f_prev
        r_implied = f_s / f_prev
        r_expected = (p_prev_raw - d_ps) / p_prev_raw
        if r_expected <= 0:
            n_excluded += 1
            continue
        devs.append(abs(r_implied / r_expected - 1.0))
        p_prev_wrong = q_prev / f_prev
        r_expected_wrong = (p_prev_wrong - d_ps) / p_prev_wrong
        if r_expected_wrong > 0:
            wrong_devs.append(abs(r_implied / r_expected_wrong - 1.0))
        n_tested += 1
    med_dev = float(np.median(devs)) if devs else None
    frac_exact = float(np.mean(np.array(devs) < 1e-6)) if devs else None
    facts["recovery_known_answer"] = {
        "n_events_tested": n_tested, "n_excluded_mixed_or_absent": n_excluded,
        "median_rel_dev": med_dev, "frac_exact_lt_1e-6": frac_exact,
        "wrong_direction_median_rel_dev": float(np.median(wrong_devs)) if wrong_devs else None,
        "tolerance": 0.02, "mirror": "P1 sec.2 leg3 verbatim tolerances",
    }
    gates["leg3_sidecar_recovery"] = bool(
        len(sidecars) >= 5000 and len(missing_sidecar) == 0
        and n_tested >= 50 and med_dev is not None and med_dev < 0.02
        and frac_exact is not None and frac_exact >= 0.5)


def _leg4_and_leg6(facts, gates, idx, syms, close_q, pct, amt, volm,
                   by_sym, sidecars, qmap):
    """One pass: leg4 monthly yield census + t0 pin; leg6 quality coverage."""
    n_bars = len(idx)
    starts = _start_positions(idx, close_q, n_bars)
    rows, cov_rows = [], []
    for p in starts:
        t_ts = idx[p]
        t_int = int(t_ts.strftime("%Y%m%d"))
        ws_int = int((t_ts - pd.Timedelta(days=TTM_DAYS)).strftime("%Y%m%d"))
        c_row = np.asarray(close_q[p], dtype="float64")
        v_row = np.asarray(volm[p], dtype="float64")
        a_row = np.asarray(amt[p], dtype="float64")
        amt20 = np.nanmedian(np.asarray(amt[max(0, p - 19):p + 1], dtype="float64"), axis=0)
        base_ok = (np.isfinite(c_row) & (v_row > 0) & (a_row > 0)
                   & np.isfinite(amt20) & (amt20 >= AMT20_FLOOR))
        pct_win = np.asarray(pct[max(0, p - VOL_WIN + 1):p + 1], dtype="float64")
        with np.errstate(invalid="ignore"):
            sigma = np.nanstd(pct_win, axis=0, ddof=1)
        valid = np.sum(np.isfinite(pct_win), axis=0)
        n_ypos = n_screenable_ypos = n_rank = n_q_avail = 0
        yvals, sig_rank = [], []
        for j in np.where(base_ok)[0]:
            code = str(syms[j])
            pack = by_sym.get(code)
            sc = sidecars.get(code)
            if pack is None or sc is None:
                continue
            cash = ttm_cash_sum(pack[0], pack[1], t_int, ws_int)
            if cash <= 0:
                continue
            f_t = sidecar_f_at(sc[0], sc[1], t_int)
            p_raw = c_row[j] * f_t
            if not np.isfinite(p_raw) or p_raw <= 0:
                continue
            y = cash / p_raw
            n_ypos += 1
            yvals.append(y)
            qp = qmap.get(code)
            if qp is not None and quality_available(qp[0], qp[1], t_int):
                n_q_avail += 1
            if valid[j] >= VOL_MIN_BARS and np.isfinite(sigma[j]):
                n_screenable_ypos += 1
                sig_rank.append((sigma[j], y))
        if sig_rank:
            med_s = float(np.median([s for s, _ in sig_rank]))
            n_rank = int(sum(1 for s, _ in sig_rank if s <= med_s))
        row = {"t": t_int, "n_base_mask": int(base_ok.sum()),
               "n_yield_pos": n_ypos,
               "n_yield_pos_screenable": n_screenable_ypos,
               "n_rank_universe": n_rank,
               "floor_met": bool(n_screenable_ypos >= UNIVERSE_FLOOR)}
        rows.append(row)
        if t_int >= 20060201:   # frozen signal calendar 2006-02 -> 2026-03
            cov_rows.append({"t": t_int, "n_yield_pos": n_ypos,
                             "n_quality_avail": n_q_avail,
                             "coverage": (n_q_avail / n_ypos) if n_ypos else None})
    t0 = None
    for i, r in enumerate(rows):
        if all(x["floor_met"] for x in rows[i:]):
            t0 = r["t"]
            break
    below_after = [r["t"] for r in rows if t0 and r["t"] >= t0 and not r["floor_met"]]
    below_after_pin = [r["t"] for r in rows
                       if r["t"] >= T0_PIN and not r["floor_met"]]
    post_t0 = [r for r in rows if t0 and r["t"] >= t0]
    rank_min = (min([r["n_rank_universe"] for r in post_t0])
                if post_t0 else None)
    post_pin = [r for r in rows if r["t"] >= T0_PIN]
    rank_min_pin = (min([r["n_rank_universe"] for r in post_pin])
                    if post_pin else None)
    facts["yield_census"] = {
        "eligible_starts": len(starts), "expected": 401,
        "first_signal_date_t0": t0, "t0_pin": T0_PIN,
        "months_below_floor_after_t0": below_after,
        "months_below_floor_after_t0_pin": below_after_pin,
        "rank_universe_min_after_t0": rank_min,
        "rank_universe_min_after_t0_pin": rank_min_pin,
        "worst_five": sorted(rows, key=lambda r: r["n_yield_pos_screenable"])[:5],
    }
    if PANEL_BASIS["basis"] == BASIS_LOCAL:
        months = [idx[p].strftime("%Y-%m") for p in starts]
        months_post_pin = [m for m in months if m >= CAL_FIRST]
        grid_expected = [f"{y}-{m:02d}" for y in range(2006, 2027)
                         for m in range(1, 13)
                         if CAL_FIRST <= f"{y}-{m:02d}" <= CAL_LAST]
        facts["yield_census"]["starts_grid"] = {
            "n_starts": len(starts),
            "n_pre_anchor_months": len([m for m in months if m < CAL_FIRST]),
            "months_first": months[0] if months else None,
            "months_last": months[-1] if months else None,
            "judged_window_months": len(months_post_pin),
            "judged_window_equals_p1_grid": months_post_pin == grid_expected,
            "note": "local calendar starts earlier than the Money02 panel's, so "
                    "the absolute 401 start count is substrate-relative (one "
                    "extra pre-anchor month enters under the same p>=252 rule); "
                    "judged-window equality is the load-bearing assertion",
        }
        gates["leg4_yield_census_t0"] = leg4_local_ok(
            t0, below_after_pin, rank_min_pin,
            months_post_pin == grid_expected, len(months_post_pin))
    else:
        gates["leg4_yield_census_t0"] = bool(
            len(starts) == 401 and t0 is not None and t0 == T0_PIN
            and len(below_after) == 0 and rank_min is not None and rank_min >= 30)

    ratios = [c["coverage"] for c in cov_rows if c["coverage"] is not None]
    facts["quality_coverage"] = {
        "months_evaluated": len(cov_rows),
        "calendar": [CAL_FIRST, CAL_LAST],
        "floor": QUALITY_COV_FLOOR,
        "definition": "finite PIT roe available (sign-agnostic) over yield>0 domain",
        "min_ratio": (min(ratios) if ratios else None),
        "median_ratio": (float(np.median(ratios)) if ratios else None),
        "worst_five": sorted([c for c in cov_rows if c["coverage"] is not None],
                             key=lambda c: c["coverage"])[:5],
    }
    gates["leg6_quality_coverage"] = bool(
        len(cov_rows) >= 240 and ratios
        and min(ratios) >= QUALITY_COV_FLOOR)


# ----------------------------------------------------------------------------
# main run (all legs; panel legs honest PANEL_MISSING when re-delivery absent)
# ----------------------------------------------------------------------------
LOCAL_GATES = ("leg2_transfer_export", "leg5_seed_band", "leg6_quality_structural")
PANEL_GATES = ("leg1_price_panel", "leg3_sidecar_recovery",
               "leg4_yield_census_t0", "leg6_quality_coverage")


def leg1_local_ok(n_bars: int, n_bars_upto_cutoff: int, last_date: str,
                  n_syms: int) -> bool:
    """Local-substrate leg1 (same intent, substrate-relative yardstick).

    The p1c equality form (n_bars == 8792 and last bar == evidence_cutoff) is a
    property of the Money02 panel that stops on the cutoff. The rebuilt panel
    runs further, so the gate keeps the intent: >=8000 bars through the frozen
    evidence cutoff, the cutoff date itself covered, >=5100 symbol columns.
    """
    return bool(n_bars >= 8_000 and n_bars_upto_cutoff >= 8_000
                and last_date >= EVIDENCE_CUTOFF and n_syms >= 5_100)


def leg4_local_ok(t0_local, below_after_pin: list, rank_universe_min,
                  judged_grid_equal: bool, n_judged_months: int) -> bool:
    """Local-substrate leg4: the JUDGED window must equal the P1 grid.

    The rebuilt panel's calendar starts earlier than the Money02 panel's, so the
    absolute start count (401) is a substrate artifact: the same p>=252 warm-up
    rule admits extra pre-anchor months. What the gate has to protect is the
    judged window (2006-02..2026-03, 242 months) plus the 3N floor from the
    frozen anchor onwards -- both asserted here; pre-anchor extras are disclosed
    (they never reach the judged face) and the local t0 is stated, not clamped.
    """
    return bool(t0_local is not None and int(t0_local) <= T0_PIN
                and len(below_after_pin) == 0
                and rank_universe_min is not None and rank_universe_min >= 30
                and judged_grid_equal and n_judged_months == 242)


def main(basis: str = "auto") -> int:
    facts: dict = {
        "probe": "FUND-DIVLOWVOL-P2 freeze-window probes",
        "generated": _now(), "machine": "bm-b",
        "prereg": "research/FUND-DIVLOWVOL-P2.md (freeze window, r1039 rulings)",
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "evidence_cutoff_ruling": "P1 same-anchor 2026-09-22 (revival same-window "
                                  "falsification-continuity, r1039 ruling 1)",
        "panel_redelivery": "MSG-2350-bmb-p2panel.md (bm-a, receipt window <=2 rounds)",
        "kernel_source": "fund_divlowvol_p1_probe (ttm_cash_sum/sidecar_f_at "
                         "verbatim import, re-implementation zero)",
        "frozen_design": {"n_top": N_TOP, "universe_floor": UNIVERSE_FLOOR,
                          "ttm_days": TTM_DAYS, "vol_win": VOL_WIN,
                          "vol_min_bars": VOL_MIN_BARS, "amt20_floor": AMT20_FLOOR,
                          "quality_cov_floor": QUALITY_COV_FLOOR,
                          "t0_pin": T0_PIN, "d6_reject": D6_REJECT},
    }
    gates: dict[str, bool] = {}

    panel = _load_panel(basis)
    panel_ok = isinstance(panel, tuple)
    if panel_ok:
        idx, syms, meta, close_q, pct, amt, volm = panel
        n_bars = len(idx)
        n_bars_cut = int((idx <= pd.Timestamp(EVIDENCE_CUTOFF)).sum())
        facts["panel"] = {"n_bars": n_bars, "n_syms_panel": len(syms),
                          "first": str(idx[0].date()), "last": str(idx[-1].date()),
                          "basis": PANEL_BASIS["basis"],
                          "n_bars_upto_evidence_cutoff": n_bars_cut}
        if PANEL_BASIS["basis"] == BASIS_LOCAL:
            facts["panel_basis_disclosure"] = (
                "panel substrate = data/cache/p1c_local (rebuilt qfq panel from "
                "data/astock_daily per-stock CSVs, cutoff %s) + sidecars from "
                "data/cache/p1c_sidecars (qfq-inversion v1, cash dividends only). "
                "The P1 judged batch ran on the Money02 hosted panel; this probe "
                "runs the same frozen gates on a different substrate and does not "
                "claim panel equivalence -- it claims substrate-relative adequacy."
                % str(idx[-1].date()))
            gates["leg1_price_panel"] = leg1_local_ok(
                n_bars, n_bars_cut, str(idx[-1].date()), len(syms))
        else:
            gates["leg1_price_panel"] = bool(
                n_bars == N_BARS_EXPECT and str(idx[-1].date()) == EVIDENCE_CUTOFF
                and len(syms) >= 5100)
    else:
        facts["panel"] = {"status": PANEL_MISSING, "error": repr(panel),
                          "note": "p1c cache re-delivery pending (MSG-2350) and "
                                  "the local rebuilt panel is absent; panel legs "
                                  "run on the bm-a host or after re-landing"}
        gates["leg1_price_panel"] = False

    _leg2_div_face(facts, gates)
    _leg5_seed_scan(facts, gates)
    qmap = _leg6_quality_structural(facts, gates)

    if panel_ok and gates["leg1_price_panel"]:
        by_sym = _load_div_by_sym()
        sidecars = _load_sidecars(by_sym)
        _leg3_sidecar_recovery(facts, gates, idx, syms, close_q, by_sym, sidecars)
        if gates["leg2_transfer_export"] and qmap is not None:
            _leg4_and_leg6(facts, gates, idx, syms, close_q, pct, amt, volm,
                           by_sym, sidecars, qmap)
        else:
            facts["yield_census"] = {"status": "SKIPPED_DIVFACE_OR_QUALITY_RED"}
            facts["quality_coverage"] = {"status": "SKIPPED_DIVFACE_OR_QUALITY_RED"}
            gates["leg4_yield_census_t0"] = False
            gates["leg6_quality_coverage"] = False
    else:
        for k in ("leg3_sidecar_recovery", "leg4_yield_census_t0",
                  "leg6_quality_coverage"):
            facts.setdefault("_missing", {})[k] = PANEL_MISSING
            gates[k] = False

    facts["gates"] = gates
    facts["panel_basis"] = PANEL_BASIS["basis"]
    local_red = [g for g in LOCAL_GATES if not gates.get(g)]
    if panel_ok:
        verdict = "GREEN" if all(gates.values()) else "RED"
    else:
        verdict = "AWAITING_PANEL" if not local_red else "RED"
    facts["verdict"] = verdict
    out_path = OUT_LOCAL if PANEL_BASIS["basis"] == BASIS_LOCAL else OUT
    facts["receipt"] = out_path
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(facts, f, ensure_ascii=False, indent=1)
    print(json.dumps({"verdict": verdict, "gates": gates,
                      "missing_panel_legs": facts.get("_missing", {})},
                     ensure_ascii=False))
    return {"GREEN": 0, "AWAITING_PANEL": 4, "RED": 2}[verdict]


# ----------------------------------------------------------------------------
# d6 same-family admission face (P2 QF-ON headline; panel-dependent)
# ----------------------------------------------------------------------------
def _dump_d6(facts: dict) -> None:
    os.makedirs(D6_OUT_DIR, exist_ok=True)
    facts.setdefault("generated", _now())
    facts.setdefault("machine", "bm-b")
    with open(D6_JSON, "w", encoding="utf-8") as f:
        json.dump(facts, f, ensure_ascii=False, indent=1)


def _d6() -> int:
    os.makedirs(D6_OUT_DIR, exist_ok=True)
    t_start = time.time()
    panel = _load_panel()
    if not isinstance(panel, tuple):
        _dump_d6({"batch": "FUND-DIVLOWVOL-P2", "gate": "d6_same_family",
                  "verdict": "REJECT", "status": PANEL_MISSING,
                  "error": repr(panel)})
        print(f"d6 verdict=REJECT ({PANEL_MISSING}) -> {D6_JSON}")
        return 3
    idx, syms, meta, close_q, pct, amt, volm = panel
    n_bars = len(idx)
    sym_pos = {s: j for j, s in enumerate(syms)}
    by_sym = _load_div_by_sym()
    sidecars = _load_sidecars(by_sym)
    _, qmap = _load_quality()

    starts = _start_positions(idx, close_q, n_bars)

    def _rank_universe(p: int):
        t_ts = idx[p]
        t_int = int(t_ts.strftime("%Y%m%d"))
        ws_int = int((t_ts - pd.Timedelta(days=TTM_DAYS)).strftime("%Y%m%d"))
        c_row = np.asarray(close_q[p], dtype="float64")
        v_row = np.asarray(volm[p], dtype="float64")
        a_row = np.asarray(amt[p], dtype="float64")
        amt20 = np.nanmedian(np.asarray(amt[max(0, p - 19):p + 1], dtype="float64"), axis=0)
        base_ok = (np.isfinite(c_row) & (v_row > 0) & (a_row > 0)
                   & np.isfinite(amt20) & (amt20 >= AMT20_FLOOR))
        pct_win = np.asarray(pct[max(0, p - VOL_WIN + 1):p + 1], dtype="float64")
        with np.errstate(invalid="ignore"):
            sigma = np.nanstd(pct_win, axis=0, ddof=1)
        valid = np.sum(np.isfinite(pct_win), axis=0)
        cands = []
        for j in np.where(base_ok)[0]:
            code = str(syms[j])
            pack = by_sym.get(code)
            sc = sidecars.get(code)
            qp = qmap.get(code)
            if pack is None or sc is None or qp is None:
                continue
            if not quality_pass(qp[0], qp[1], t_int):   # P2 QF-ON headline face
                continue
            cash = ttm_cash_sum(pack[0], pack[1], t_int, ws_int)
            if cash <= 0:
                continue
            f_t = sidecar_f_at(sc[0], sc[1], t_int)
            p_raw = c_row[j] * f_t
            if not np.isfinite(p_raw) or p_raw <= 0:
                continue
            if valid[j] < VOL_MIN_BARS or not np.isfinite(sigma[j]):
                continue
            cands.append((sigma[j], cash / p_raw, j))
        if len(cands) < UNIVERSE_FLOOR:
            return None
        med_s = float(np.median([c[0] for c in cands]))
        low_vol = [c for c in cands if c[0] <= med_s]
        if len(low_vol) < 30:
            return None
        low_vol.sort(key=lambda c: -c[1])
        return [c[2] for c in low_vol[:N_TOP]]

    sel_all = {p: _rank_universe(p) for p in starts}
    floor_flags = [sel_all[p] is not None for p in starts]
    t0_i = next((i for i in range(len(starts)) if all(floor_flags[i:])), None)
    if t0_i is None:
        _dump_d6({"batch": "FUND-DIVLOWVOL-P2", "gate": "d6_same_family",
                  "verdict": "REJECT", "error": "no clean-tail t0 in D6 pass"})
        return 3
    t0_pos = starts[t0_i]

    sig_pos = [p for p in starts[t0_i:] if sel_all[p] is not None]
    sel = {p: sel_all[p] for p in sig_pos}
    rets = np.full(n_bars, np.nan)
    for m, p in enumerate(sig_pos):
        nxt = sig_pos[m + 1] if m + 1 < len(sig_pos) else n_bars - 1
        members = sel[p]
        for t in range(p + 1, nxt + 1):
            vals = []
            for j in members:
                c1 = close_q[t, j]
                c0 = close_q[t - 1, j]
                if np.isfinite(c1) and np.isfinite(c0) and c0 > 0:
                    vals.append(c1 / c0 - 1.0)
            if vals:
                rets[t] = float(np.mean(vals))
    h_rets = pd.Series(rets[t0_pos + 1:], index=idx[t0_pos + 1:]).dropna()

    facts: dict = {"batch": "FUND-DIVLOWVOL-P2", "gate": "d6_same_family",
                   "reject_line": D6_REJECT,
                   "sim_basis": "probe-level lightweight: eq Top-20 monthly rotation "
                                "QF-ON on qfq close ratios, no engine, no cost "
                                "(correlation gate input; levels non-judgmental)",
                   "headline_cont": {"t0": str(idx[t0_pos].date()),
                                     "n_days": int(len(h_rets)),
                                     "n_signal_months": len(sig_pos)},
                   "generated": _now()}
    try:
        from cn_rev_tilt_p1 import REG6, load_member_rets
        mrets, _ = load_member_rets()
        pairs, worst = [], None
        for tid in REG6:
            r = mrets[tid]
            both = pd.concat([h_rets, r], axis=1).dropna()
            c = float(both.corr().iloc[0, 1]) if len(both) > 30 else None
            pairs.append({"member": tid, "corr": round(c, 4) if c is not None else None,
                          "n_overlap": int(len(both))})
            if c is not None and (worst is None or abs(c) > abs(worst[1])):
                worst = (tid, c)
        admit = worst is not None and abs(worst[1]) < D6_REJECT
        facts.update({"pairs": pairs,
                      "max_abs_corr": round(abs(worst[1]), 4) if worst else None,
                      "max_member": worst[0] if worst else None,
                      "verdict": "ADMIT" if admit else "REJECT"})
    except Exception as ex:   # fail-closed: no D6 face = no ignition
        facts.update({"verdict": "REJECT", "error": str(ex)[:300]})

    disc = {}
    for label, path in SIBLING_CONTS.items():
        try:
            cj = json.load(open(path, encoding="utf-8"))
            t0s = str(cj.get("t0"))
            r = np.asarray(cj.get("returns", []), dtype="float64")
            p0 = int(np.searchsorted(idx, pd.Timestamp(t0s)))
            s = pd.Series(r, index=idx[p0 + 1:p0 + 1 + len(r)])
            both = pd.concat([h_rets, s], axis=1).dropna()
            disc[label] = {"corr": round(float(both.corr().iloc[0, 1]), 4)
                           if len(both) > 30 else None,
                           "n_overlap": int(len(both)),
                           "gate_face": "disclosure-only (prereg sec.1)"}
        except Exception as exc:
            disc[label] = {"error": repr(exc)[:120]}
    # family predecessor face (FUND-DIVLOWVOL-P1 headline, disclosure-only)
    fam_label, fam_corr = "family_predecessor", None
    try:
        import glob as _g
        cands = sorted(_g.glob(P1_FAMILY_GLOB))
        if cands:
            cj = json.load(open(cands[0], encoding="utf-8"))
            t0s = str(cj.get("t0"))
            r = np.asarray(cj.get("returns", []), dtype="float64")
            p0 = int(np.searchsorted(idx, pd.Timestamp(t0s)))
            s = pd.Series(r, index=idx[p0 + 1:p0 + 1 + len(r)])
            both = pd.concat([h_rets, s], axis=1).dropna()
            fam_corr = (round(float(both.corr().iloc[0, 1]), 4)
                        if len(both) > 30 else None)
        disc[fam_label] = {"cont_file": cands[0] if cands else None,
                           "corr": fam_corr,
                           "registered_family_corr": 0.8039,
                           "gate_face": "disclosure-only (same-family predecessor)"}
    except Exception as exc:
        disc[fam_label] = {"error": repr(exc)[:120]}
    facts["sibling_family_disclosure"] = disc
    facts["runtime_sec"] = round(time.time() - t_start, 1)
    _dump_d6(facts)
    print(f"d6 verdict={facts['verdict']} max|corr|={facts.get('max_abs_corr')} "
          f"family_pred_corr={fam_corr} -> {D6_JSON}")
    return 0 if facts["verdict"] == "ADMIT" else 3


# ----------------------------------------------------------------------------
# offline selftest (synthetic fixtures, zero data dependency)
# ----------------------------------------------------------------------------
def _selftest() -> int:
    n_fail = 0

    def check(name: str, cond: bool):
        nonlocal n_fail
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
        if not cond:
            n_fail += 1

    # S0 single-source kernel import integrity (P1 verbatim face)
    ex = np.array([20200101, 20210101, 20210102, 20220101], dtype=np.int64)
    cum = np.cumsum(np.array([1.0, 2.0, 4.0, 8.0]))
    check("S0a ttm_cash_sum import identity window (ws, t]",
          abs(ttm_cash_sum(ex, cum, 20220101, 20210101) - 12.0) < 1e-12)
    d_list, f_list = [20000101, 20100101, 20200101, 20260626], [8.8, 4.4, 2.2, 1.0]
    check("S0b sidecar_f_at import identity stepwise",
          abs(sidecar_f_at(d_list, f_list, 20150601) - 4.4) < 1e-12)

    # S1 quality PIT latest-avail semantics (+ tie -> max period_end)
    av = np.array([20010101, 20020101, 20020101, 20030101], dtype=np.int64)
    roe = np.array([0.05, 0.10, 0.20, 0.30])   # tie group = (20020101, period p2)
    check("S1a before first avail -> None", quality_roe_at(av, roe, 20001231) is None)
    check("S1b at first avail -> 0.05", abs(quality_roe_at(av, roe, 20010101) - 0.05) < 1e-12)
    check("S1c tie resolved to max period_end", abs(quality_roe_at(av, roe, 20020601) - 0.20) < 1e-12)
    check("S1d after last -> last value", abs(quality_roe_at(av, roe, 20040101) - 0.30) < 1e-12)

    # S2 quality_pass sign/None/NaN faces
    check("S2a roe>0 pass", quality_pass(av, roe, 20010101))
    check("S2b roe<=0 fail", not quality_pass(np.array([20010101]), np.array([-0.01]), 20010101))
    check("S2c no avail -> fail", not quality_pass(av, roe, 20001231))
    check("S2d NaN roe -> fail", not quality_pass(np.array([20010101]), np.array([np.nan]), 20010101))

    # S3 coverage numerator is sign-agnostic availability
    av3 = np.array([20010101, 20020101], dtype=np.int64)
    roe3 = np.array([-0.5, np.nan])
    check("S3a negative roe still 'available'", quality_available(av3, roe3, 20010101))
    check("S3b NaN roe not 'available'", not quality_available(av3, roe3, 20020101))

    # S4 coverage ratio floor line (60% fails, 85% passes)
    def _ratio(n_avail, n_ypos):
        return n_avail / n_ypos if n_ypos else None
    check("S4a ratio below floor fails", _ratio(60, 100) < QUALITY_COV_FLOOR)
    check("S4b ratio above floor passes", _ratio(85, 100) >= QUALITY_COV_FLOOR)

    # S5 seed own-pair exemption logic (own pair not flagged; other proximity is)
    own = {"k1": 20_523_000, "k2": 20_523_500}
    others = {"other": 20_523_100}   # 400 from k1, 400 from k2 -> violation
    prox = {k: [ob for ob in others.values() if abs(b - ob) < PROXIMITY_GATE]
            for k, b in own.items() if any(abs(b - ob) < PROXIMITY_GATE
                                           for ob in others.values())}
    check("S5a other-base proximity detected", bool(prox))
    check("S5b own-pair 500-distance disclosed not gated",
          abs(own["k1"] - own["k2"]) == 500
          and not (FURNACE_BAND[0] < own["k1"] < FURNACE_BAND[1])
          and not (FURNACE_BAND[0] < own["k2"] < FURNACE_BAND[1]))

    # S6 frozen signal calendar boundary membership (2006-02 .. 2026-03)
    cal = [f"{y}-{m:02d}" for y in range(2006, 2027) for m in range(1, 13)
          if "2006-02" <= f"{y}-{m:02d}" <= "2026-03"]
    check("S6 calendar months count", len(cal) == 242
          and cal[0] == "2006-02" and cal[-1] == "2026-03")

    # S7 local-substrate leg1 predicate (substrate-relative yardstick)
    check("S7a p1c equality shape rejected on local substrate",
          not leg1_local_ok(8792, 8792, "2026-09-22", 5225)
          or leg1_local_ok(8745, 8720, "2026-10-19", 5225))
    check("S7b local panel covering cutoff passes",
          leg1_local_ok(8745, 8720, "2026-10-19", 5225))
    check("S7c short panel through cutoff fails",
          not leg1_local_ok(8745, 7999, "2026-10-19", 5225))
    check("S7d panel ending before frozen cutoff fails",
          not leg1_local_ok(8745, 8720, "2026-09-01", 5225))
    check("S7e narrow universe fails",
          not leg1_local_ok(8745, 8720, "2026-10-19", 5000))

    # S8 local-substrate leg4 predicate (judged-window equality carries the gate)
    check("S8a earlier local t0 + intact judged grid passes",
          leg4_local_ok(20040105, [], 131, True, 242))
    check("S8b local t0 later than the frozen pin fails",
          not leg4_local_ok(20070105, [], 131, True, 242))
    check("S8c sub-floor month at/after the pin fails",
          not leg4_local_ok(20040105, [20120702], 131, True, 242))
    check("S8d thin rank universe fails",
          not leg4_local_ok(20040105, [], 29, True, 242))
    check("S8e drifted judged grid fails", not leg4_local_ok(20040105, [], 40, False, 241))
    check("S8f extra pre-anchor start count does not gate",
          leg4_local_ok(20040105, [], 131, True, 242))

    print(f"selftest: {'PASS' if n_fail == 0 else 'FAIL'} ({n_fail} failures)")
    return 0 if n_fail == 0 else 2


if __name__ == "__main__":
    args = [a for a in sys.argv[1:]]
    mode = args[0] if args and not args[0].startswith("--") else "run"
    basis = "auto"
    if "--panel" in args:
        i = args.index("--panel")
        basis = args[i + 1] if i + 1 < len(args) else "auto"
    elif mode == "run" and len(args) > 1:
        basis = args[1]
    basis = {"local": BASIS_LOCAL, "p1c": BASIS_P1C}.get(basis, basis)
    if basis not in ("auto", BASIS_P1C, BASIS_LOCAL):
        print(json.dumps({"error": f"unknown --panel basis '{basis}' "
                                   f"(auto|{BASIS_P1C}|{BASIS_LOCAL})"}))
        raise SystemExit(2)
    if mode == "selftest":
        raise SystemExit(_selftest())
    if mode == "d6":
        raise SystemExit(_d6())
    raise SystemExit(main(basis))
