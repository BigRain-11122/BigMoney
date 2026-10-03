"""FUND-DIVLOWVOL-P1 ignition-gate probes (data side, fail-closed, zero-network).

Dividend-low-vol family = T-145 leg(c) third fundamental family
(O-20261002-2115 CEO direct order; A-share classic defensive per CEO
research-orientation law 2026-09-28). Mirrors scripts/fund_quality_p1_probe.py
(second family piece) with the divlowvol-specific deltas:

  * data face = div_events (corporate-action event face, NOT a filing face):
    PIT anchor = ex_date (the dividend is certain only at ex-date; announced
    but unpaid dividends can be cancelled -- ex-date anchoring removes that
    risk by construction). STATUTORY ANCHORING (Q1/H1/Q3/FY availability
    dates, T-145 leg(a) law) is N/A for this batch -- declared in the prereg.
  * TTM yield derive (the family's core increment, prereg sec.2/3):
      yield_ttm(t) = sum(cash_div_per_10/10 for ex_date in (t-365d, t])
                     / P_raw_close(t)
      P_raw_close(t) = close_qfq(t) * f(t)      [factor sidecar recovery]
    where f(t) = stepwise factor at the latest sidecar event date d <= t
    (sidecar Money02/data/bars/<sym>.factor.json, f(latest)==1.0). The p1c
    panel is qfq (meta adj_convention); dividend cash is in RAW terms, so the
    yield denominator MUST be recovered to raw -- using qfq directly would
    distort the cross-sectional rank per-symbol by 1/f_i(t).
  * low-vol screen (frozen family design): sigma_252 = sample std (ddof=1)
    of qfq daily returns (pct_chg) over trailing 252 trading days, min 126
    valid bars (else un-screenable, excluded honestly); keep bottom half
    (sigma <= cross-sectional median WITHIN the yield>0 masked universe);
    Top-N=20 by TTM yield desc within the low-vol half.

Legs (live `run`):
  leg1  price panel gate (p1c_stock canonical loader, single source):
        n_bars==8792, last bar==2026-09-22, n_syms>=5100
  leg2  div_events TRANSFER landing + export gate (T-2026-10-03-154 spec):
        n_symbols_nonempty >= 5100 AND per-symbol event median >= 3
        AND ex_date span d1 >= 2026-01-01 AND zero null cash
        AND zero unsorted (code, ex_date) AND dtype contract
        AND 5 quarantined symbols absent AND sha256 == manifest sampled entry
  leg3  factor sidecar census + raw-price recovery known-answer:
        sidecar coverage over div symbols present in the panel;
        pure-cash events 2015+: implied drop ratio f(s)/f(s-1) vs exchange
        ex-rights formula (P_prev-d)/P_prev (median rel dev < 2%, n>=50);
        wrong-direction (raw = qfq / f) median reported for discrimination.
  leg4  monthly yield census + start census + universe floor + t0 pin:
        starts == 401 (T-22 monthly enumeration, family frozen number);
        per start: base mask (close/vol/amt>0, amt20 median >= 1e7,
        pos>=252) -> yield>0 count, screenable count, rank-universe count;
        UNIVERSE_FLOOR=60 (3N pre-screen; post-screen >= 30 >= N=20);
        t0 = earliest start from which EVERY start meets the floor.
  leg5  seed-band scan for fund_divlowvol_p1_nulls=20520000 /
        fund_divlowvol_p1_sens=20520500 (exact-base disjointness vs full
        SEED_REGISTRY + stock_face_furnace band + proximity >= 2000).

`selftest` = offline known-answer legs on synthetic fixtures (no data files):
  S1 TTM window boundary (t-365 excluded, t-364/t included)
  S2 sidecar stepwise recovery (ladder + latest-d<=t semantics)
  S3 yield two-component same-day sum + per-10 -> per-share /10
  S4 vol median split + min-bars screenability
  S5 seed-band collision case (base inside furnace band rejected)
  S6 floor / t0 definition (skip-months honesty)

Output: results/_fund_divlowvol_p1_transfer_probe.json (probe facts only).
Exit 0 = all gates green; exit 2 = any gate red (honest, no masking).
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, ".")          # repo root (science_gates imports knowledge.cost_spec)
sys.path.insert(0, "scripts")
import numpy as np
import pandas as pd

PARQUET = "data/fund_history_export/div_events_faces.parquet"
MANIFEST = "fleet/transfers/T-2026-10-03-154-sender.json"
SIDECAR_FMT = "Money02/data/bars/{sym}.factor.json"
OUT = "results/_fund_divlowvol_p1_transfer_probe.json"
TZ = timezone(timedelta(hours=8))

QUARANTINED = ["001235", "001381", "301569", "301660", "301718"]  # T-131 status
N_TOP = 20                        # prereg sec.3 Top-N (frozen family design)
UNIVERSE_FLOOR = 60               # 3N pre-screen monthly floor (frozen)
TTM_DAYS = 365                    # TTM calendar window (frozen)
VOL_WIN = 252                     # sigma window in trading days (frozen)
VOL_MIN_BARS = 126                # min valid return bars else un-screenable (frozen)
AMT20_FLOOR = 10_000_000.0        # family mask (amt20 median, yuan)
COV_FLOOR_MONTHS = 0              # reserved (divlowvol uses count floor, not ratio)

# r596 band-level law constants (stock_face_furnace occupied band, registry-documented)
FURNACE_BAND = (20_333_000, 20_445_400)   # open interval, base+cell_idx*4000+k stretch
PROXIMITY_GATE = 2_000                    # min distance from any registered base
SEED_NULLS = 20_520_000                   # candidate fund_divlowvol_p1_nulls (K=2000)
SEED_SENS = 20_520_500                    # candidate fund_divlowvol_p1_sens     (N=500)


def _now() -> str:
    return datetime.now(TZ).strftime("%Y-%m-%dT%H:%M:%S+08:00")


# ----------------------------------------------------------------------------
# shared derive kernels (single source for probe; the runner re-implements
# nothing -- it imports these exact functions from this module)
# ----------------------------------------------------------------------------
def ttm_cash_sum(ex_int: np.ndarray, cum_cash: np.ndarray, t_int: int, ws_int: int) -> float:
    """Cash per share summed over ex_date in (ws_int, t_int] (YYYYMMDD ints).

    cum_cash[k] = sum(cash_per_share[0..k]); both arrays sorted by ex date.
    """
    i_r = int(np.searchsorted(ex_int, t_int, side="right")) - 1
    if i_r < 0:
        return 0.0
    i_l = int(np.searchsorted(ex_int, ws_int, side="right")) - 1
    return float(cum_cash[i_r] - (cum_cash[i_l] if i_l >= 0 else 0.0))


def sidecar_f_at(d_list, f_list, t_int: int) -> float:
    """Stepwise factor at the latest sidecar event date d <= t (YYYYMMDD int).

    Empty sidecar (no adjustment events ever) -> f = 1.0 (raw == qfq).
    """
    import bisect
    if len(d_list) == 0 or len(f_list) == 0:
        return 1.0
    j = bisect.bisect_right(d_list, t_int) - 1
    if j < 0:
        return float(f_list[0])
    return float(f_list[j])


def _leg5_band_scan(facts: dict, gates: dict) -> None:
    import science_gates as SG
    reg = {k: v for k, v in SG.SEED_REGISTRY.items() if isinstance(v, int)}
    candidates = {"fund_divlowvol_p1_nulls": SEED_NULLS, "fund_divlowvol_p1_sens": SEED_SENS}
    exact_hits = {k: b for k, b in candidates.items() if b in reg.values()}
    in_band = {k: b for k, b in candidates.items() if FURNACE_BAND[0] < b < FURNACE_BAND[1]}
    too_close = {
        k: (b, rb) for k, b in candidates.items()
        for rb in reg.values() if abs(b - rb) < PROXIMITY_GATE
    }
    facts["seed_band_scan"] = {
        "candidates": candidates,
        "n_registry_bases": len(reg),
        "exact_hits": exact_hits,
        "furnace_band": list(FURNACE_BAND),
        "in_furnace_band": in_band,
        "proximity_violations": {k: list(v) if isinstance(v, tuple) else v for k, v in too_close.items()},
        "k_stretch_disclosure": {
            "nulls": f"rng([{SEED_NULLS}, k]) k=0..1999 (pair-seed sub-stream law)",
            "sens": f"rng([{SEED_SENS}, k]) k=0..499 (pair-seed sub-stream law)",
        },
        "gap_to_fund_quality_block": SEED_NULLS - 20_510_000,  # >= 8000 clear of quality block
    }
    gates["leg5_seed_band"] = bool(not exact_hits and not in_band and not too_close)


def main() -> int:
    facts: dict = {"probe": "FUND-DIVLOWVOL-P1 ignition data-side probes",
                   "generated": _now(), "machine": "bm-b",
                   "prereg": "research/FUND-DIVLOWVOL-P1.md (DRAFT-NOT-FROZEN)",
                   "transfer_ticket": "T-2026-10-03-154-P1",
                   "frozen_design": {"n_top": N_TOP, "universe_floor": UNIVERSE_FLOOR,
                                      "ttm_days": TTM_DAYS, "vol_win": VOL_WIN,
                                      "vol_min_bars": VOL_MIN_BARS, "amt20_floor": AMT20_FLOOR}}
    gates: dict[str, bool] = {}

    # ---- leg1 price panel via canonical loader ----
    try:
        import p1c_stock_ic_batch as P1C
        idx, syms, meta = P1C.load_universe()
        close_q = np.load(f"{P1C.CACHE_DIR}/close.npy", mmap_mode="r")
        pct = np.load(f"{P1C.CACHE_DIR}/pct_chg.npy", mmap_mode="r")
        amt = np.load(f"{P1C.CACHE_DIR}/amount.npy", mmap_mode="r")
        vol = np.load(f"{P1C.CACHE_DIR}/volume.npy", mmap_mode="r")
        n_bars = len(idx)
        facts["panel"] = {"n_bars": n_bars, "n_syms_panel": len(syms),
                          "first": str(idx[0].date()), "last": str(idx[-1].date()),
                          "ok_universe": meta.get("ok_universe")}
        gates["leg1_price_panel"] = bool(
            n_bars == 8792 and str(idx[-1].date()) == "2026-09-22" and len(syms) >= 5100)
    except Exception as exc:  # panel absent -> honest fail-closed
        facts["panel"] = {"error": repr(exc)}
        gates["leg1_price_panel"] = False
        idx = syms = close_q = pct = amt = vol = None

    # ---- leg2 div_events TRANSFER landing + export gate ----
    import os
    if not os.path.exists(PARQUET):
        facts["div_face"] = {"absent": True, "path": PARQUET,
                             "note": "T-154 TRANSFER not landed -- fail-closed."}
        gates["leg2_transfer_export"] = False
    else:
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
        per = df.groupby("code")["ex_date"]
        ev_median = float(per.size().median())
        span_min = str(df["ex_date"].min())[:10]
        span_max = str(df["ex_date"].max())[:10]
        null_cash = int(df["cash_div_per_10"].isna().sum())
        srt = df.sort_values(["code", "ex_date"])
        unsorted_rows = int((df.index != srt.index).sum())
        dtypes = {c: str(df[c].dtype) for c in df.columns}
        quarantined_present = sorted(set(QUARANTINED) & set(df["code"].astype(str)))
        import pyarrow.parquet as pq
        sch = {f.name: str(f.type) for f in pq.read_schema(PARQUET)}
        dtype_ok = bool(
            ("string" in sch.get("code", "") or sch.get("code") == "str")
            and sch.get("ex_date") == "date32[day]"
            and sch.get("record_date") == "date32[day]"
            and sch.get("cash_div_per_10") == "double")
        facts["parquet_schema"] = sch
        facts["div_face"] = {
            "rows": int(len(df)), "n_symbols_nonempty": n_symbols,
            "per_symbol_event_median": ev_median,
            "ex_date_span": [span_min, span_max],
            "null_cash_rows": null_cash, "unsorted_rows": unsorted_rows,
            "dtypes": dtypes, "columns": list(df.columns),
            "quarantined_present": quarantined_present,
            "sha256": sha, "manifest_sha256": man_sha, "manifest_bytes_ok": man_ok,
        }
        gates["leg2_transfer_export"] = bool(
            n_symbols >= 5100 and ev_median >= 3 and span_max >= "2026-01-01"
            and null_cash == 0 and unsorted_rows == 0 and dtype_ok
            and not quarantined_present and man_ok and sha == man_sha)

    # ---- leg3 sidecar census + raw-price recovery known-answer ----
    if gates.get("leg1_price_panel") and os.path.exists(PARQUET):
        df = pd.read_parquet(PARQUET)
        sym_pos = {s: j for j, s in enumerate(syms)}
        sidecars: dict[str, tuple[np.ndarray, np.ndarray]] = {}
        n_div_in_panel = 0
        for code in df["code"].astype(str).unique():
            if code in sym_pos:
                n_div_in_panel += 1
        missing_sidecar = []
        for code in df["code"].astype(str).unique():
            p = SIDECAR_FMT.format(sym=code)
            if not os.path.exists(p):
                if code in sym_pos:
                    missing_sidecar.append(code)
                continue
            sd = json.load(open(p, encoding="utf-8"))
            d = np.array([int(x.replace("-", "")) for x in sd["d"]], dtype=np.int64)
            f = np.array(sd["f"], dtype=np.float64)
            sidecars[code] = (d, f)
        facts["sidecar_census"] = {
            "n_div_symbols_in_panel": n_div_in_panel,
            "n_sidecar_loaded": len(sidecars),
            "n_panel_div_missing_sidecar": len(missing_sidecar),
            "missing_sample": sorted(missing_sidecar)[:10],
        }

        # recovery known-answer: pure-cash events 2015+
        df2 = df.copy()
        df2["code_s"] = df2["code"].astype(str)
        df2["ex_s"] = df2["ex_date"].astype(str).str.slice(0, 10)
        ev = df2.groupby(["code_s", "ex_s"], sort=True)["cash_div_per_10"].sum().reset_index()
        ev = ev[ev["cash_div_per_10"] > 0]
        ev = ev[ev["ex_s"] >= "2015-01-01"]
        date_pos = {str(d.date()): p for p, d in enumerate(idx)}
        devs, wrong_devs, n_tested = [], [], 0
        n_mixed_or_absent = 0
        for _, r in ev.iterrows():
            code, ex_s, d10 = r["code_s"], r["ex_s"], float(r["cash_div_per_10"])
            sc = sidecars.get(code)
            s_pos = date_pos.get(ex_s)
            if sc is None or s_pos is None or s_pos < 1:
                n_mixed_or_absent += 1
                continue
            d_list, f_list = sc
            ex_int = int(ex_s.replace("-", ""))
            js = int(np.searchsorted(d_list, ex_int, side="left"))
            # require the sidecar to carry this exact event date, alone in +/-10td
            if js >= len(d_list) or int(d_list[js]) != ex_int:
                n_mixed_or_absent += 1
                continue
            if js == 0:
                n_mixed_or_absent += 1
                continue
            win = d_list[(d_list > ex_int - 100) & (d_list < ex_int + 100)]
            if len(win) != 1:
                n_mixed_or_absent += 1   # neighbor event within ~+/-100d: possibly mixed
                continue
            f_s, f_prev = float(f_list[js]), float(f_list[js - 1])
            q_prev = float(close_q[s_pos - 1, sym_pos[code]])
            if not np.isfinite(q_prev) or f_prev <= 0:
                n_mixed_or_absent += 1
                continue
            d_ps = d10 / 10.0
            p_prev_raw = q_prev * f_prev            # correct-direction recovery
            r_implied = f_s / f_prev
            r_expected = (p_prev_raw - d_ps) / p_prev_raw
            if r_expected <= 0:
                n_mixed_or_absent += 1
                continue
            devs.append(abs(r_implied / r_expected - 1.0))
            # wrong-direction discrimination face (raw = qfq / f)
            p_prev_wrong = q_prev / f_prev
            r_expected_wrong = (p_prev_wrong - d_ps) / p_prev_wrong
            if r_expected_wrong > 0:
                wrong_devs.append(abs(r_implied / r_expected_wrong - 1.0))
            n_tested += 1
        med_dev = float(np.median(devs)) if devs else None
        med_wrong = float(np.median(wrong_devs)) if wrong_devs else None
        facts["recovery_known_answer"] = {
            "formula": "P_raw(t) = close_qfq(t) * f(t), f stepwise at latest sidecar d <= t",
            "n_events_tested": n_tested,
            "n_excluded_mixed_or_absent": n_mixed_or_absent,
            "median_rel_dev": med_dev,
            "frac_exact_lt_1e-6": float(np.mean(np.array(devs) < 1e-6)) if devs else None,
            "p90_rel_dev": float(np.percentile(devs, 90)) if devs else None,
            "wrong_direction_median_rel_dev": med_wrong,
            "tolerance": 0.02,
            "p90_note": "p90 tail = mixed cash+share events leaking the pure-cash "
                        "filter (share component in the same factor date, div face "
                        "carries cash only) -- disclosed, median is the machine answer",
        }
        gates["leg3_sidecar_recovery"] = bool(
            len(sidecars) >= 5000 and len(missing_sidecar) == 0
            and n_tested >= 50 and med_dev is not None and med_dev < 0.02
            and facts["recovery_known_answer"]["frac_exact_lt_1e-6"] >= 0.5)
    else:
        gates["leg3_sidecar_recovery"] = False

    # ---- leg4 monthly yield census + starts + floor + t0 ----
    if gates.get("leg1_price_panel") and gates.get("leg2_transfer_export"):
        df = pd.read_parquet(PARQUET)
        df["code_s"] = df["code"].astype(str)
        df["_ex"] = df["ex_date"].astype(str).str.replace("-", "", regex=False).astype("int64")
        df["_cps"] = df["cash_div_per_10"].astype("float64") / 10.0
        df = df.sort_values(["code_s", "_ex"])
        by_sym: dict[str, tuple[np.ndarray, np.ndarray]] = {}
        for code, g in df.groupby("code_s", sort=False):
            by_sym[str(code)] = (g["_ex"].to_numpy(), np.cumsum(g["_cps"].to_numpy()))

        mask_win = (idx >= pd.Timestamp("1992-09-01")) & (idx <= pd.Timestamp("2026-03-02"))
        sub = idx[mask_win]
        mk = sub.strftime("%Y-%m")
        month_first_pos: list[int] = []
        prev = None
        for p, k in zip(np.where(mask_win)[0], mk):
            if k != prev:
                month_first_pos.append(int(p)); prev = k
        starts: list[int] = []
        for p in month_first_pos:
            if p < 252 or (n_bars - 1 - p) < 126:
                continue
            if int((~np.isnan(close_q[p])).sum()) < 24:
                continue
            starts.append(p)
        facts["start_census"] = {"months_in_window": len(month_first_pos),
                                 "eligible_starts": len(starts), "expected": 401}

        rows = []
        for p in starts:
            t_ts = idx[p]
            t_int = int(t_ts.strftime("%Y%m%d"))
            ws_int = int((t_ts - pd.Timedelta(days=TTM_DAYS)).strftime("%Y%m%d"))
            c_row = np.asarray(close_q[p], dtype="float64")
            v_row = np.asarray(vol[p], dtype="float64")
            a_row = np.asarray(amt[p], dtype="float64")
            amt20 = np.nanmedian(np.asarray(amt[max(0, p - 19):p + 1], dtype="float64"), axis=0)
            base_ok = (np.isfinite(c_row) & (v_row > 0) & (a_row > 0)
                       & np.isfinite(amt20) & (amt20 >= AMT20_FLOOR))
            pct_win = np.asarray(pct[max(0, p - VOL_WIN + 1):p + 1], dtype="float64")
            with np.errstate(invalid="ignore"):
                sigma = np.nanstd(pct_win, axis=0, ddof=1)
            valid = np.sum(np.isfinite(pct_win), axis=0)
            screenable = valid >= VOL_MIN_BARS
            n_base = int(base_ok.sum())
            n_ypos = n_screenable_ypos = n_rank = 0
            yvals = []
            sig_rank = []
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
                if screenable[j] and np.isfinite(sigma[j]):
                    n_screenable_ypos += 1
                    sig_rank.append((sigma[j], y))
            if sig_rank:
                med_s = float(np.median([s for s, _ in sig_rank]))
                n_rank = int(sum(1 for s, _ in sig_rank if s <= med_s))
            rows.append({"t": t_int, "n_base_mask": n_base,
                         "n_yield_pos": n_ypos,
                         "n_yield_pos_screenable": n_screenable_ypos,
                         "n_rank_universe": n_rank,
                         "yield_median": float(np.median(yvals)) if yvals else None,
                         "yield_p90": float(np.percentile(yvals, 90)) if yvals else None,
                         "floor_met": bool(n_screenable_ypos >= UNIVERSE_FLOOR)})
        ok = [r for r in rows if r["floor_met"]]
        # t0 = earliest start such that EVERY later start meets the floor
        t0 = None
        for i, r in enumerate(rows):
            if all(x["floor_met"] for x in rows[i:]):
                t0 = r["t"]
                break
        below_after = [r["t"] for r in rows if t0 and r["t"] >= t0 and not r["floor_met"]]
        post_t0 = [r for r in rows if t0 and r["t"] >= t0]
        facts["yield_census"] = {
            "months_evaluated": len(rows),
            "n_months_meeting_floor": len(ok),
            "first_signal_date_t0": t0,
            "months_below_floor_after_t0": below_after,
            "rank_universe_median_after_t0": (float(np.median([r["n_rank_universe"] for r in post_t0]))
                                              if post_t0 else None),
            "rank_universe_min_after_t0": (min([r["n_rank_universe"] for r in post_t0])
                                           if post_t0 else None),
            "yield_median_of_medians_after_t0": (float(np.median([r["yield_median"] for r in post_t0
                                                                  if r["yield_median"]]))
                                                 if post_t0 else None),
            "worst_five": sorted(rows, key=lambda r: r["n_yield_pos_screenable"])[:5],
        }
        gates["leg4_yield_census"] = bool(
            len(starts) == 401 and t0 is not None and len(below_after) == 0
            and facts["yield_census"]["rank_universe_min_after_t0"] is not None
            and facts["yield_census"]["rank_universe_min_after_t0"] >= 30)  # post-screen >= 1.5N
    else:
        gates["leg4_yield_census"] = False

    # ---- leg5 seed-band scan (data-independent) ----
    _leg5_band_scan(facts, gates)

    facts["gates"] = gates
    facts["verdict"] = "GREEN" if all(gates.values()) else "RED"
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(facts, f, ensure_ascii=False, indent=1)
    print(json.dumps({"verdict": facts["verdict"], "gates": gates}, ensure_ascii=False))
    return 0 if facts["verdict"] == "GREEN" else 2


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

    # S1 TTM window boundary: (t-365d, t]
    ex = np.array([20200101, 20210101, 20210102, 20220101], dtype=np.int64)
    cash = np.array([1.0, 2.0, 4.0, 8.0])
    cum = np.cumsum(cash)
    # t = 2022-01-01, ws = 2021-01-01 -> window excludes 20210101? (ws, t] excludes ws itself
    s = ttm_cash_sum(ex, cum, 20220101, 20210101)
    check("S1a window (t-365, t] excludes boundary ws day", abs(s - 12.0) < 1e-12)  # 0102 + 2022
    s = ttm_cash_sum(ex, cum, 20210102, 20200103)   # ws=2020-01-03: excludes 20200101
    check("S1b ws-day event excluded", abs(s - 6.0) < 1e-12)                        # 0101(2021)+0102
    s = ttm_cash_sum(ex, cum, 20200101, 20190101)
    check("S1c t-day event included", abs(s - 1.0) < 1e-12)
    s = ttm_cash_sum(ex, cum, 20190101, 20180101)
    check("S1d empty window -> 0.0", abs(s - 0.0) < 1e-12)

    # S2 sidecar stepwise recovery
    d_list = [20000101, 20100101, 20200101, 20260626]
    f_list = [8.8, 4.4, 2.2, 1.0]
    check("S2a pre-first uses f[0]", abs(sidecar_f_at(d_list, f_list, 19991231) - 8.8) < 1e-12)
    check("S2b at event date uses that f", abs(sidecar_f_at(d_list, f_list, 20100101) - 4.4) < 1e-12)
    check("S2c between events uses latest prior", abs(sidecar_f_at(d_list, f_list, 20150601) - 4.4) < 1e-12)
    check("S2d latest", abs(sidecar_f_at(d_list, f_list, 20260922) - 1.0) < 1e-12)

    # S3 two-component same-day sum + per-10 -> per-share
    ex3 = np.array([20060519, 20060519], dtype=np.int64)
    cum3 = np.cumsum(np.array([1.0, 2.0]))     # cash_div_per_10 already /10 per share
    s3 = ttm_cash_sum(ex3, cum3, 20060601, 20050601)
    check("S3 same-day two-component sums", abs(s3 - 3.0) < 1e-12)

    # S4 vol median split + min bars
    sig = np.array([0.10, 0.02, 0.30, 0.25])
    valid = np.array([200, 200, 200, 100])
    scr = valid >= VOL_MIN_BARS
    cand = [sig[j] for j in range(4) if scr[j]]
    med = float(np.median(cand))
    keep = sum(1 for v in cand if v <= med)
    check("S4 min-bars excludes, median split keeps half", scr.tolist() == [True, True, True, False]
          and keep == 2)

    # S5 seed-band collision case
    check("S5a candidate outside furnace band",
          not (FURNACE_BAND[0] < SEED_NULLS < FURNACE_BAND[1])
          and not (FURNACE_BAND[0] < SEED_SENS < FURNACE_BAND[1]))
    check("S5b gap to quality block >= 8000", SEED_NULLS - 20_510_000 >= 8000)

    # S6 floor / t0 definition
    rows6 = [False, True, True, False, True, True, True]
    t0_6 = None
    for i in range(len(rows6)):
        if all(rows6[i:]):
            t0_6 = i
            break
    check("S6 t0 = first clean-tail month", t0_6 == 4)

    print(f"selftest: {'PASS' if n_fail == 0 else 'FAIL'} ({n_fail} failures)")
    return 0 if n_fail == 0 else 2


# ----------------------------------------------------------------------------
# D6 same-family admission face (probe-level lightweight sim, disclosed)
# ----------------------------------------------------------------------------
D6_OUT_DIR = "results/fund_divlowvol_p1"
D6_JSON = "results/fund_divlowvol_p1/d6.json"
D6_REJECT = 0.7
SIBLING_CONTS = {
    "FUND-VALUE-P1 headline (VALUE-PE x1 cont)": "results/fund_value_p1/cont_VALUE-PE_x1.json",
    "FUND-QUALITY-P1 headline (QUALITY-ROE x1 cont)": "results/fund_quality_p1/cont_QUALITY-ROE_x1.json",
}


def _d6() -> int:
    """D6 admission face (sec.1): headline DIVLOWVOL-YIELDVOL x1 sleeve daily
    returns vs ALL six registered members (cn_rev_tilt_p1.REG6 single source);
    max|corr| >= 0.7 -> REJECT (fail-closed). Probe-level lightweight sim:
    eq-weight Top-20 monthly rotation on qfq close ratios, no engine, no cost
    -- correlation structure is the gate input, levels are not (disclosed)."""
    os.makedirs(D6_OUT_DIR, exist_ok=True)
    t_start = __import__("time").time()
    import p1c_stock_ic_batch as P1C
    idx, syms, meta = P1C.load_universe()
    close_q = np.load(f"{P1C.CACHE_DIR}/close.npy", mmap_mode="r")
    pct = np.load(f"{P1C.CACHE_DIR}/pct_chg.npy", mmap_mode="r")
    amt = np.load(f"{P1C.CACHE_DIR}/amount.npy", mmap_mode="r")
    volm = np.load(f"{P1C.CACHE_DIR}/volume.npy", mmap_mode="r")
    n_bars = len(idx)
    sym_pos = {s: j for j, s in enumerate(syms)}
    df = pd.read_parquet(PARQUET)
    df["code_s"] = df["code"].astype(str)
    df["_ex"] = df["ex_date"].astype(str).str.replace("-", "", regex=False).astype("int64")
    df["_cps"] = df["cash_div_per_10"].astype("float64") / 10.0
    df = df.sort_values(["code_s", "_ex"])
    by_sym: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for code, g in df.groupby("code_s", sort=False):
        by_sym[str(code)] = (g["_ex"].to_numpy(), np.cumsum(g["_cps"].to_numpy()))
    sidecars: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for code in by_sym:
        p = SIDECAR_FMT.format(sym=code)
        if os.path.exists(p):
            sd = json.load(open(p, encoding="utf-8"))
            sidecars[code] = (
                np.array([int(x.replace("-", "")) for x in sd["d"]], dtype=np.int64),
                np.array(sd["f"], dtype=np.float64))

    # monthly starts (family enumeration) + t0 (floor clean tail)
    mask_win = (idx >= pd.Timestamp("1992-09-01")) & (idx <= pd.Timestamp("2026-03-02"))
    sub = idx[mask_win]; mk = sub.strftime("%Y-%m")
    starts: list[int] = []
    prev = None
    for p, k in zip(np.where(mask_win)[0], mk):
        if k != prev:
            prev = k
            if p >= 252 and (n_bars - 1 - p) >= 126 and int((~np.isnan(close_q[p])).sum()) >= 24:
                starts.append(int(p))

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
            if pack is None or sc is None:
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

    # t0 = first clean-tail start (mirror leg4 definition, machine re-derive)
    sel_all: dict[int, list | None] = {p: _rank_universe(p) for p in starts}
    floor_flags = [sel_all[p] is not None for p in starts]
    t0_i = next((i for i in range(len(starts)) if all(floor_flags[i:])), None)
    if t0_i is None:
        _dump_d6({"verdict": "REJECT", "error": "no clean-tail t0 in D6 pass"})
        return 3
    t0_pos = starts[t0_i]

    # sleeve daily returns (eq Top-20 monthly rotation, qfq close ratios)
    sig_pos = [p for p in starts[t0_i:] if sel_all[p] is not None]
    sel = {p: sel_all[p] for p in sig_pos}
    rets = np.full(n_bars, np.nan)
    for m, p in enumerate(sig_pos):
        nxt = sig_pos[m + 1] if m + 1 < len(sig_pos) else n_bars - 1
        members = sel[p]
        for t in range(p + 1, nxt + 1):
            vals = []
            for j in members:
                c1 = close_q[t, j]; c0 = close_q[t - 1, j]
                if np.isfinite(c1) and np.isfinite(c0) and c0 > 0:
                    vals.append(c1 / c0 - 1.0)
            if vals:
                rets[t] = float(np.mean(vals))
    h_rets = pd.Series(rets[t0_pos + 1:], index=idx[t0_pos + 1:])
    h_rets = h_rets.dropna()

    facts: dict = {"batch": "FUND-DIVLOWVOL-P1", "gate": "d6_same_family",
                   "reject_line": D6_REJECT,
                   "sim_basis": "probe-level lightweight: eq Top-20 monthly rotation "
                                 "on qfq close ratios, no engine, no cost (correlation "
                                 "gate input; levels non-judgmental, disclosed)",
                   "headline_cont": {"t0": str(idx[t0_pos].date()),
                                     "n_days": int(len(h_rets)),
                                     "n_signal_months": len(sig_pos)},
                   "generated": _now(), "machine": "bm-b"}
    try:
        from cn_rev_tilt_p1 import REG6, load_member_rets
        mrets, _ = load_member_rets()
        pairs = []
        worst = None
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
        # sibling-family disclosure (no gate; prereg sec.1 另列披露)
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
        facts["sibling_family_disclosure"] = disc
    except Exception as ex:      # fail-closed: no D6 face = no ignition
        facts.update({"verdict": "REJECT", "error": str(ex)[:300]})
    facts["runtime_sec"] = round(__import__("time").time() - t_start, 1)
    os.makedirs(D6_OUT_DIR, exist_ok=True)
    with open(D6_JSON, "w", encoding="utf-8") as f:
        json.dump(facts, f, ensure_ascii=False, indent=1)
    print(f"d6 verdict={facts['verdict']} max|corr|={facts.get('max_abs_corr')} -> {D6_JSON}")
    return 0 if facts["verdict"] == "ADMIT" else 3


def _dump_d6(facts: dict) -> None:
    os.makedirs(D6_OUT_DIR, exist_ok=True)
    facts.setdefault("generated", _now())
    facts.setdefault("machine", "bm-b")
    with open(D6_JSON, "w", encoding="utf-8") as f:
        json.dump(facts, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "run"
    if mode == "selftest":
        raise SystemExit(_selftest())
    if mode == "d6":
        raise SystemExit(_d6())
    raise SystemExit(main())
