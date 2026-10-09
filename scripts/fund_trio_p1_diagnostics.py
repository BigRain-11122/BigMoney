"""fund_trio_p1_diagnostics.py -- FUND-TRIO P1 post-batch engineering diagnostics.

r811 bm-b. Due <= 2026-10-10 12:00 (r807 disclosure / r808+r809 milestone
lines, state.json next pointer):

  quality-nav       NAV negative-crossing pathology triage for
                    FUND-QUALITY-P1. r807 finalize disclosed: ret_full
                    +2.4844 with sharpe_full -0.3177, max_dd -1.1454
                    (NAV below zero), crash-year 2006 -338x, rolling
                    worst figures unreadable. Root-cause hunt over the
                    stored cont daily-returns face + the shared T-139
                    p1c_stock panel. Read-only.
  divlowvol-exdate  ex-date join + raw-price-recovery probe for
                    FUND-DIVLOWVOL-P1 (prereg sec.5(a) over-band
                    contingency: headline Sharpe 0.8941 above the frozen
                    0.3-0.8 prediction band -> "check the ex-date join
                    and the raw recovery FIRST"). Exercises the exact
                    frozen burn path (runner functions imported, never
                    re-implemented) at sampled firing months, plus a
                    stored-returns ex-day artifact scan and a segment
                    decomposition for the over-band attribution.
  selftest          offline known-answer legs (no panel load).
  run               both probes, one panel load, both artifacts.

Laws: read-only over batch results + data; frozen verdicts NOT touched
(single-read r638 law); kernels/selection imported single-source from
the frozen runner module; findings are reported honestly and never
auto-remediated; exit 0 = mechanics ran (findings in JSON), 2 =
mechanism failure (report, do not mask).
"""
import json
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

RESULTS = os.path.join(ROOT, "results")
FD_PATH = os.path.join(RESULTS, "fund_divlowvol_p1")
FQ_PATH = os.path.join(RESULTS, "fund_quality_p1")
CONT_Q = os.path.join(FQ_PATH, "cont_QUALITY-ROE_x1.json")
CONT_D = os.path.join(FD_PATH, "cont_DIVLOWVOL-YIELDVOL_x1.json")
RESULTS_Q = os.path.join(FQ_PATH, "fund_quality_p1_results.json")
RESULTS_D = os.path.join(FD_PATH, "fund_divlowvol_p1_results.json")
OUT_Q = os.path.join(FQ_PATH, "nav_pathology_triage_r811.json")
OUT_D = os.path.join(FD_PATH, "ex_date_probe_r811.json")

N_SAMPLE_MONTHS = 12
SANE_YIELD_LO = 1e-4      # informational band only (no frozen cap exists)
SANE_YIELD_HI_FLAG = 1.0  # >=100% TTM cash yield = near-certain artifact
CASH_TOL = 1e-9
ANNUAL = np.sqrt(252.0)


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%S+08:00")


def _dump(obj, path):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1, sort_keys=True)


def _load_cont(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _cont_face(cont, idx):
    """Map a stored cont record onto panel dates.

    Returns (dates, returns) where dates[k] (k=1..n_days-1) carries
    returns[k-1]; dates[0] is the t0 anchor day.
    """
    t0 = pd.Timestamp(cont["t0"])
    p0 = int(idx.searchsorted(t0))
    if idx[p0] != t0:
        raise RuntimeError("cont t0 %s not found in panel idx" % t0)
    n = int(cont["n_days"])
    if p0 + n > len(idx):
        raise RuntimeError("cont span overruns panel: p0=%d n=%d len=%d"
                           % (p0, n, len(idx)))
    dates = idx[p0:p0 + n]
    rets = np.asarray(cont["returns"], dtype=np.float64)
    if len(rets) != n - 1:
        raise RuntimeError("returns length %d != n_days-1 %d"
                           % (len(rets), n - 1))
    return p0, dates, rets


def _sharpe(rets, ddof=1):
    s = float(np.std(rets, ddof=ddof))
    if s <= 0:
        return 0.0
    return float(np.mean(rets) / s * ANNUAL)


def _yearly_rets(dates, rets):
    """Calendar-year total returns from a daily sleeve return stream.

    rets[k] is the return OF day dates[k+1] (day-over-day vs the
    previous panel day), so the year of dates[k+1] owns rets[k].
    """
    out = {}
    yrs = dates[1:].year.to_numpy()
    for y in sorted(set(yrs.tolist())):
        r = np.asarray(rets)[yrs == y]
        out[int(y)] = float(np.prod(1.0 + r) - 1.0)
    return out


def _nav_stats(dates, rets):
    nav = np.cumprod(1.0 + rets)
    nav = np.concatenate(([1.0], nav))
    k_neg = np.where(nav < 0)[0]
    first_neg = int(k_neg[0]) if len(k_neg) else None
    worst = np.argsort(rets)[:10]
    return {
        "nav_min": float(nav.min()),
        "nav_last_ratio": float(nav[-1]),
        "first_negative_day": (None if first_neg is None else str(dates[first_neg])),
        "worst_days": [{"date": str(dates[k + 1]), "ret": float(rets[k])}
                       for k in sorted(worst.tolist())],
    }


def _rolling_worst(dates, rets, window_years):
    """Worst trailing calendar-year window total return (approximation:
    trading-day windows of ~244*window_years days)."""
    w = int(round(244 * window_years))
    if len(rets) <= w:
        return None
    c = np.cumprod(1.0 + rets)
    tot = np.empty(len(rets) - w + 1)
    base = np.concatenate(([1.0], c))
    for i in range(len(tot)):
        tot[i] = base[i + w] / base[i]
    j = int(np.argmin(tot))
    return {"worst_window_return": float(tot[j]),
            "window_start": str(dates[j + 1]),
            "window_end": str(dates[j + w])}


def cmd_quality_nav(FD):
    """Root-cause triage of the quality NAV negative-crossing pathology."""
    fq = FD  # panel access via the shared T-139 face (FD._G)
    cont = _load_cont(CONT_Q)
    with open(RESULTS_Q, encoding="utf-8") as fh:
        res = json.load(fh)
    idx = fq._G["idx"]
    syms = list(fq._G["syms"])
    p0, dates, rets = _cont_face(cont, idx)

    # -- reconstruction validation (stored summary vs recomputed faces)
    nav = np.concatenate(([1.0], np.cumprod(1.0 + rets)))
    recon = {
        "nav_ratio_recomputed": float(nav[-1]),
        "ret_full_stored": cont["ret_full"],
        "nav_last_stored_ratio": cont["nav_last"] / cont["nav_first"],
        "sharpe_recomputed_ddof1": _sharpe(rets, 1),
        "sharpe_recomputed_pop": _sharpe(rets, 0),
        "sharpe_stored": cont["sharpe_full"],
        "max_dd_recomputed": None,
    }
    peak = np.maximum.accumulate(nav)
    recon["max_dd_recomputed"] = float((nav / peak - 1.0).min())

    # -- negative-price scan over the shared panel (close and open faces)
    close_np = fq._G["close_np"]
    open_np = fq._G["open_np"]
    neg_close = {}
    neg_open = {}
    sym_neg = {}
    CH = 512
    n_rows = close_np.shape[0]
    for name, mm in (("close", close_np), ("open", open_np)):
        counts = np.zeros(close_np.shape[1], dtype=np.int64)
        mins = np.full(close_np.shape[1], np.inf)
        first = np.full(close_np.shape[1], -1, dtype=np.int64)
        last = np.full(close_np.shape[1], -1, dtype=np.int64)
        for lo in range(0, n_rows, CH):
            arr = np.asarray(mm[lo:lo + CH])
            m = np.isfinite(arr) & (arr <= 0.0)
            if not m.any():
                continue
            counts += m.sum(axis=0)
            np.minimum(mins, np.where(m, arr, np.inf), out=mins)
            fi = np.argmax(m, axis=0)
            has = m.any(axis=0)
            first = np.where(has & (first < 0), lo + fi, first)
            la = (m.shape[0] - 1) - np.argmax(m[::-1], axis=0)
            last = np.where(has, np.maximum(last, lo + la), last)
        for j in np.where(counts > 0)[0]:
            d = {"code": str(syms[j]), "n_cells": int(counts[j]),
                 "min_price": float(mins[j]),
                 "first_date": str(idx[first[j]]),
                 "last_date": str(idx[last[j]])}
            (neg_close if name == "close" else neg_open)[str(syms[j])] = d
            sym_neg.setdefault(str(syms[j]), {})[name] = d

    # -- worst crash days cross-referenced with the panel
    pct_np = fq._G["pct_np"]
    worst_days = []
    order = np.argsort(rets)[:8]
    for k in sorted(order.tolist()):
        day_pos = p0 + k + 1
        row = np.asarray(pct_np[day_pos])
        monsters = [syms[j] for j in np.where(np.isfinite(row)
                                              & (row <= -50.0))[0][:12]]
        crow = np.asarray(close_np[day_pos])
        neg_today = [syms[j] for j in np.where(np.isfinite(crow)
                                               & (crow <= 0.0))[0][:12]]
        worst_days.append({
            "date": str(dates[k + 1]), "sleeve_ret": float(rets[k]),
            "pct_le_-50_syms": monsters,
            "close_le_0_syms": neg_today})

    # -- quality-band membership of the negative-price symbols (era check)
    era_neg = {c: d for c, d in sym_neg.items()
               if d.get("close", d.get("open", {})).get("first_date", "9999") < "2008-01-01"}
    band_hits = {}
    try:
        import fund_quality_p1 as FQ
        df = pd.read_parquet(FQ.PARQUET)
        df["_code"] = df["code"].astype(str)
        sub = df[df["_code"].isin(era_neg)]
        for c, g in sub.groupby("_code"):
            v = g["roe_q"].to_numpy(dtype=np.float64)
            av = g["avail_date"].astype(str)
            ok = v[np.isfinite(v) & (v > 0) & (v <= 100.0)]
            if len(ok):
                band_hits[c] = {"n_band_rows": int(len(ok)),
                                "max_roe_q": float(ok.max()),
                                "avail_min": str(av.min()),
                                "avail_max": str(av.max())}
    except Exception as e:  # honest: band face optional for triage
        band_hits = {"error": str(e)[:120]}

    yearly = _yearly_rets(dates, rets)
    out = {
        "probe": "quality-nav triage (r811)",
        "generated": _now(),
        "machine": "bm-b",
        "due": "2026-10-10T12:00 (r807 disclosure follow-up)",
        "reconstruction": recon,
        "yearly_returns": yearly,
        "crash_years_stored": res["descriptive"]["crash_years_lte_-35pct"],
        "nav_stats": _nav_stats(dates, rets),
        "rolling_worst_stored": res["rolling_worst"],
        "rolling_worst_recomputed": {
            "3y": _rolling_worst(dates, rets, 3),
            "5y": _rolling_worst(dates, rets, 5),
            "10y": _rolling_worst(dates, rets, 10)},
        "worst_days_panel_crossref": worst_days,
        "negative_price_scan": {
            "n_symbols_neg_close": len(neg_close),
            "n_symbols_neg_open": len(neg_open),
            "neg_close_symbols": sorted(neg_close.values(),
                                        key=lambda d: -d["n_cells"])[:20],
            "neg_open_symbols": sorted(neg_open.values(),
                                       key=lambda d: -d["n_cells"])[:20]},
        "era_neg_symbols_pre2008": {c: era_neg[c] for c in
                                    sorted(era_neg)[:30]},
        "quality_band_membership": band_hits,
    }
    _dump(out, OUT_Q)
    return out


def cmd_divlowvol_exdate(FD):
    """Ex-date join + raw-recovery probe (prereg sec.5(a) contingency)."""
    cont = _load_cont(CONT_D)
    with open(RESULTS_D, encoding="utf-8") as fh:
        res = json.load(fh)
    idx = FD._G["idx"]
    p0, dates, rets = _cont_face(cont, idx)

    # -- independent div-event recompute path (same parquet, direct
    #    window filter; different code path than the frozen cumsum kernel)
    df = pd.read_parquet(FD.PARQUET)
    df["_ex"] = df["ex_date"].astype("string").str.replace(
        "-", "", regex=False).astype("int64")
    df["_cps"] = df["cash_div_per_10"].astype("float64") / 10.0
    indep = {}
    for code, g in df.groupby("code", sort=False):
        g = g.sort_values("_ex")
        indep[str(code)] = (g["_ex"].to_numpy(), g["_cps"].to_numpy())

    months = FD._G["month_pos"]
    t0_ts = pd.Timestamp("2006-02-06")   # frozen clean-tail pin (sec.2)
    i0 = next(i for i, p in enumerate(months)
              if idx[p] >= t0_ts)
    picks = np.linspace(i0, len(months) - 1, N_SAMPLE_MONTHS).astype(int)
    picks = sorted(set(int(x) for x in picks))

    month_reports = []
    agg = {"months": len(picks), "cand_total": 0, "cash_mismatch": 0,
           "unsorted_packs": 0, "f_out_of_range": 0,
           "p_raw_nonpos": 0, "sidecar_j_neg_edge": 0,
           "yield_gt_1": 0, "yield_lo": 0, "sel_violations": 0,
           "skipped_months_post_t0": 0}
    top_by_month = {}
    for i in picks:
        p = months[i]
        u = FD._month_universe(p)
        t_int, ws_int = u["t_int"], u["ws_int"]
        rep = {"month": str(idx[p]), "p": int(p), "t_int": t_int,
               "ws_int": ws_int, "n_base": u["n_base"],
               "n_cand": u["n_cand"], "skipped": u["skipped"]}
        if u["skipped"]:
            agg["skipped_months_post_t0"] += 1
        cj = u["cand_j"]
        cy = u["cand_yield"]
        cs = u["cand_sigma"]
        syms = FD._G["syms"]
        bad_cash, bad_f, bad_raw, jneg, yhi = [], [], [], [], []
        unsorted_packs = []
        for n, j in enumerate(cj.tolist()):
            code = str(syms[j])
            ex, cps = indep[code]
            m = (ex > ws_int) & (ex <= t_int)
            cash_check = float(cps[m].sum())
            pack = FD._G["by_sym"][code]
            if not np.all(np.diff(pack[0]) >= 0):
                unsorted_packs.append(code)
            cash_k = FD.ttm_cash_sum(pack[0], pack[1], t_int, ws_int)
            if abs(cash_k - cash_check) > CASH_TOL:
                bad_cash.append(code)
            sc = FD._G["sidecars"].get(code)
            f_t = FD.sidecar_f_at(sc[0], sc[1], t_int)
            # sidecar law: f(latest)=1.0 and f GROWS going back in time
            # (P_raw = close_qfq * f restores the as-traded price; the
            # probe leg3 known answer validated f(s)/f(s-1) drop ratios)
            if not np.isfinite(f_t) or f_t < 1.0 - 1e-9:
                bad_f.append(code)
            j_has = int((sc[0] <= t_int).sum())
            if j_has == 0:
                jneg.append(code)
            close_r = float(np.asarray(FD._G["close_np"][p])[j])
            if not np.isfinite(close_r * f_t) or close_r * f_t <= 0:
                bad_raw.append(code)
            yv = float(cy[n])
            if yv > SANE_YIELD_HI_FLAG:
                yhi.append(code)
        agg["cand_total"] += len(cj)
        agg["cash_mismatch"] += len(set(bad_cash))
        # no-future-event assertion is structural: the kernel window is
        # searchsorted-bounded to (ws, t] and the independent window
        # filter above recomputes the same sum via a different code path;
        # any future/lookahead event would surface as cash_mismatch
        agg["unsorted_packs"] = agg.get("unsorted_packs", 0) + len(
            set(unsorted_packs))
        agg["f_out_of_range"] += len(set(bad_f))
        agg["p_raw_nonpos"] += len(set(bad_raw))
        agg["sidecar_j_neg_edge"] += len(set(jneg))
        agg["yield_gt_1"] += len(set(yhi))

        # selection integrity: low-vol half + top-20 by yield desc
        pj, vals = FD._pick_j(u)
        med = float(np.median(u["cand_sigma"]))
        pos = np.searchsorted(u["cand_j"], pj)
        sig_ok = bool(np.all(u["cand_sigma"][pos] <= med + 1e-12)) \
            if len(pj) else True
        codes_arr = FD._G["codes_arr"]
        order = np.lexsort((codes_arr[pj], -vals))
        top = pj[order[:min(20, len(pj))]]
        top_y = float(vals[order[:min(20, len(pj))]].min()) if len(top) else 0.0
        rest_y = float(np.max(vals[order[20:]])) if len(pj) > 20 else 0.0
        sel_ok = bool(top_y >= rest_y - 1e-12) and sig_ok
        if not sel_ok:
            agg["sel_violations"] += 1
        top_by_month[str(idx[p])] = {
            "n_half": int(len(pj)), "n_top": int(len(top)),
            "top20_min_yield": top_y, "half_rest_max_yield": rest_y,
            "sel_ok": sel_ok,
            "top_codes": [str(syms[j]) for j in top[:20]]}
        rep.update({"cash_mismatch_syms": sorted(set(bad_cash))[:8],
                    "f_bad_syms": sorted(set(bad_f))[:8],
                    "raw_bad_syms": sorted(set(bad_raw))[:8],
                    "sidecar_pre_first_event": sorted(set(jneg))[:8],
                    "yield_gt_1_syms": sorted(set(yhi))[:8],
                    "sel_ok": sel_ok})
        month_reports.append(rep)

    # -- stored-returns faces: reconstruction + ex-day artifact scan
    nav = np.concatenate(([1.0], np.cumprod(1.0 + rets)))
    years = dates[1:].year.to_numpy()
    seg = {}
    for label, lo, hi in (("full", None, None),
                           ("y2013_2015", 2013, 2015),
                           ("y2016_on", 2016, 9999)):
        m = np.ones(len(rets), dtype=bool)
        if lo is not None:
            m &= (years >= lo)
        if hi is not None and hi < 9999:
            m &= (years <= hi)
        seg[label] = {"n_days": int(m.sum()),
                      "sharpe_ddof1": _sharpe(rets[m], 1),
                      "total_ret": float(np.prod(1.0 + rets[m]) - 1.0)}
    absr = np.abs(rets)
    exday = {"max_abs_daily": float(absr.max()),
             "n_days_abs_gt_15pct": int((absr > 0.15).sum()),
             "n_days_abs_gt_10pct": int((absr > 0.10).sum())}

    # sampled-month member ex-dates inside their span windows: sleeve
    # return on those days should be ordinary if returns are qfq-based
    span_days = []
    for i in picks:
        p = months[i]
        end = months[i + 1] if i + 1 < len(months) else len(idx) - 1
        for code in top_by_month[str(idx[p])]["top_codes"]:
            ex, _ = indep.get(code, (np.array([], dtype=np.int64), None))
            for e in ex.tolist():
                ts = pd.Timestamp(str(e).zfill(8)).strftime("%Y-%m-%d")
                q = int(idx.searchsorted(pd.Timestamp(ts)))
                if p < q <= end:
                    span_days.append((q, code))
    day_pos = np.array(sorted(set(q for q, _ in span_days)), dtype=int)
    rel = day_pos - p0 - 1
    rel = rel[(rel >= 0) & (rel < len(rets))]
    ex_rets = rets[rel] if len(rel) else np.array([])
    exday["member_exdays_in_sampled_spans"] = int(len(rel))
    exday["sleeve_mean_ret_on_exdays"] = (float(ex_rets.mean())
                                          if len(ex_rets) else None)
    exday["sleeve_mean_ret_all_days"] = float(rets.mean())

    # -- over-band attribution faces (from the frozen results JSON)
    nulls = res["nulls"]["same_mask"]
    attribution = {
        "headline_sharpe_stored": cont["sharpe_full"],
        "null_mu": nulls["mu"], "null_sigma": nulls["sigma"],
        "headline_minus_null_mu": cont["sharpe_full"] - nulls["mu"],
        "prediction_band": "0.3-0.8 (sec.5(a) frozen)",
        "null_mu_in_band_top_half": bool(nulls["mu"] >= 0.5),
        "note": "same-mask null mu already sits at the band top: the "
                "mask universe (yield>0 + low-vol + liquidity) carries "
                "the defensive beta; headline excess over null mu is "
                "the selection information, reported as-is",
    }
    out = {
        "probe": "divlowvol ex-date join + raw recovery (r811)",
        "generated": _now(),
        "machine": "bm-b",
        "due": "2026-10-10T12:00 (sec.5(a) over-band contingency)",
        "kernel_source": "imported single-source from "
                         "fund_divlowvol_p1_probe/runner (frozen)",
        "months_sampled": month_reports,
        "aggregates": agg,
        "selection_integrity_by_month": top_by_month,
        "stored_returns_faces": {
            "sharpe_recomputed_ddof1": _sharpe(rets, 1),
            "sharpe_recomputed_pop": _sharpe(rets, 0),
            "sharpe_stored": cont["sharpe_full"],
            "nav_ratio_recomputed": float(nav[-1]),
            "segments": seg,
            "exday_faces": exday},
        "over_band_attribution": attribution,
        "verdict_inputs": {
            "join_pit_violations": agg["cash_mismatch"],
            "recovery_violations": agg["f_out_of_range"]
                                   + agg["p_raw_nonpos"],
            "sel_violations": agg["sel_violations"],
            "exday_artifact": exday,
        },
    }
    _dump(out, OUT_D)
    return out


def cmd_quality_cliff(FD):
    """Dissect the root NAV-cliff day: rebuild the held month's frozen
    quality selection, dump raw panel rows per member around the
    cliff, and reconcile a simple mark-to-market approximation against
    the observed sleeve pnl delta (data-vs-accounting attribution)."""
    import fund_quality_p1 as FQ
    FQ._init_worker()
    cont = _load_cont(CONT_Q)
    idx = FQ._G["idx"]
    syms = list(FQ._G["syms"])
    p0, dates, rets = _cont_face(cont, idx)
    nav = np.concatenate(([1.0], np.cumprod(1.0 + rets)))
    k = int(np.argmax(nav < 0))            # first negative NAV day index
    q_star = p0 + k                        # panel position of that day
    pnl = (nav - 1.0) * 1_000_000.0
    months = FQ._G["month_pos"]
    m = max(x for x in months if x <= q_star)
    u = FQ._month_universe(m)
    pj, vals = FQ._pick_j(u)
    codes = FQ._G["codes_arr"]
    order = np.lexsort((codes[pj], -vals))
    top = pj[order[:min(20, len(pj))]]

    lo, hi = max(q_star - 15, 0), min(q_star + 8, len(idx) - 1)
    win = idx[lo:hi + 1]
    members = []
    approx_delta = 0.0
    roe_by_j = dict(zip(pj.tolist(), np.asarray(vals, dtype=float).tolist()))
    for j in top:
        cl = np.asarray(FQ._G["close_np"][lo:hi + 1, j], dtype=np.float64)
        op = np.asarray(FQ._G["open_np"][lo:hi + 1, j], dtype=np.float64)
        pc = np.asarray(FQ._G["pct_np"][lo:hi + 1, j], dtype=np.float64)
        rel = q_star - lo
        # last finite close strictly before the cliff day (engine ffill mark)
        before = np.where(np.isfinite(cl[:rel]))[0]
        prev_mark = float(cl[before[-1]]) if len(before) else float("nan")
        prev_mark_date = str(win[before[-1]]) if len(before) else None
        c_star = float(cl[rel]) if np.isfinite(cl[rel]) else float("nan")
        o_star = float(op[rel]) if np.isfinite(op[rel]) else float("nan")
        pc_star = float(pc[rel]) if np.isfinite(pc[rel]) else float("nan")
        # approximation: 1/20 weight, pnl delta = w*(c_star/prev_mark - 1)
        contrib = None
        if np.isfinite(prev_mark) and prev_mark > 0 and np.isfinite(c_star):
            contrib = (1.0 / max(1, len(top))) * (c_star / prev_mark - 1.0)
            approx_delta += contrib
        n_gap_days = int(np.sum(~np.isfinite(cl[:rel]))) if len(before) else 0
        members.append({
            "code": str(syms[j]), "roe_q": roe_by_j.get(int(j)),
            "close_prev_mark": prev_mark, "prev_mark_date": prev_mark_date,
            "gap_days_in_window": n_gap_days,
            "close_at_cliff": c_star, "open_at_cliff": o_star,
            "pct_at_cliff": pc_star,
            "mark_collapse": (None if contrib is None
                              else float(c_star / prev_mark - 1.0)),
            "approx_pnl_delta_1M": (None if contrib is None
                                     else round(contrib * 1_000_000.0, 1)),
            "nan_pattern_close": "".join(
                "N" if not np.isfinite(x) else "F" for x in cl)})
    obs_delta = float(pnl[k] - pnl[k - 1]) if k >= 1 else None
    out = {
        "probe": "quality NAV cliff dissection (r811)",
        "generated": _now(),
        "machine": "bm-b",
        "root_crossing_day": str(dates[k]),
        "nav_before": float(nav[k - 1]) if k else None,
        "nav_at": float(nav[k]),
        "observed_sleeve_return": float(rets[k - 1]),
        "observed_pnl_delta_1M": obs_delta,
        "held_month": str(idx[m]),
        "n_top": int(len(top)),
        "member_dissection": members,
        "approx_mark_to_market_pnl_delta_1M": round(approx_delta * 1_000_000.0, 1),
        "attribution_note": (
            "approx = sum over held members of w*(close_at_cliff / "
            "last-ffilled-mark - 1); observed ~= approx -> the price data "
            "alone explains the cliff (data face); observed >> approx -> "
            "engine accounting implicated"),
        "nav_path_around": [{"date": str(dates[i]), "nav": float(nav[i]),
                             "pnl_delta": (float(pnl[i] - pnl[i - 1])
                                           if i else None)}
                            for i in range(max(k - 6, 0), min(k + 8, len(nav)))],
    }
    _dump(out, os.path.join(FQ_PATH, "nav_cliff_dissection_r811.json"))
    print("quality-cliff: day=%s nav %.4f->%.4f obs_delta=%.0f approx=%.0f"
          % (out["root_crossing_day"], out["nav_before"], out["nav_at"],
             obs_delta or 0.0, approx_delta * 1_000_000.0))
    return out


def cmd_quality_era(FD):
    """Attribute the 2001-2005 NAV annihilation month by month: rebuild
    each firing month's frozen Top-20 selection, approximate the book's
    simple one-month mark return, and name the worst members per month
    (data-vs-strategy attribution for the pre-crossing destruction)."""
    import fund_quality_p1 as FQ
    FQ._init_worker()
    cont = _load_cont(CONT_Q)
    idx = FQ._G["idx"]
    syms = list(FQ._G["syms"])
    p0, dates, rets = _cont_face(cont, idx)
    nav = np.concatenate(([1.0], np.cumprod(1.0 + rets)))
    k = int(np.argmax(nav < 0))
    era_end = p0 + k                      # attribution window ends at the crossing
    months = [p for p in FQ._G["month_pos"]
              if p0 <= p <= era_end]
    codes = FQ._G["codes_arr"]
    close_np = FQ._G["close_np"]
    monthly = []
    for mi, m in enumerate(months):
        u = FQ._month_universe(m)
        if u["skipped"]:
            continue
        pj, vals = FQ._pick_j(u)
        if not len(pj):
            continue
        order = np.lexsort((codes[pj], -vals))
        top = pj[order[:min(20, len(pj))]]
        nxt = months[mi + 1] if mi + 1 < len(months) else min(m + 32, len(idx) - 1)
        rows = []
        for j in top:
            c0 = float(np.asarray(close_np[m, j]))
            seg = np.asarray(close_np[m:nxt + 1, j], dtype=np.float64)
            fin = np.where(np.isfinite(seg))[0]
            c1 = float(seg[fin[-1]]) if len(fin) else c0
            if not np.isfinite(c0) or c0 <= 0:
                continue
            rows.append({"code": str(syms[j]),
                         "ret_month": float(c1 / c0 - 1.0),
                         "c0": round(c0, 4), "c1": round(c1, 4)})
        rets_m = [r["ret_month"] for r in rows]
        sleeve = float(np.mean(rets_m)) if rets_m else 0.0
        worst = sorted(rows, key=lambda r: r["ret_month"])[:5]
        monthly.append({"month": str(idx[m]), "n": len(rows),
                        "sleeve_ret_mean": sleeve,
                        "worst_members": worst})
    monthly.sort(key=lambda r: r["sleeve_ret_mean"])
    comp = 1.0
    for r in monthly:
        comp *= (1.0 + r["sleeve_ret_mean"])
    out = {
        "probe": "quality era annihilation attribution (r811)",
        "generated": _now(),
        "machine": "bm-b",
        "era": [str(dates[0]), str(dates[k])],
        "n_months_fired": len(monthly),
        "approx_compound_nav": float(comp),
        "nav_at_crossing_stored": float(nav[k]),
        "note": "monthly sleeve_ret_mean = simple EW mean of the Top-20 "
                "members' one-month mark returns (ffilled, no engine "
                "accounting) -- attribution approximation, not the "
                "frozen burn path",
        "worst_months": monthly[:14],
        "best_months": monthly[-3:],
    }
    _dump(out, os.path.join(FQ_PATH, "nav_era_attribution_r811.json"))
    print("quality-era: months=%d approx_nav=%.5f stored_nav=%.5f"
          % (len(monthly), comp, nav[k]))
    return out


def cmd_selftest():
    """Offline known-answer legs (no panel load)."""
    ok = 0

    def chk(name, cond):
        nonlocal ok
        if not cond:
            raise RuntimeError("selftest FAIL: " + name)
        ok += 1

    import fund_divlowvol_p1_probe as P
    ex = np.array([20000101, 20000601, 20010101, 20020101], dtype=np.int64)
    cum = np.cumsum([1.0, 2.0, 3.0, 4.0])
    chk("ttm window (ws,t]",
        abs(P.ttm_cash_sum(ex, cum, 20010601, 20000601) - 3.0) < 1e-12)
    chk("ttm excludes t+ and pre-ws",
        abs(P.ttm_cash_sum(ex, cum, 20000531, 19990101) - 1.0) < 1e-12
        and abs(P.ttm_cash_sum(ex, cum, 20000101, 19990101) - 1.0) < 1e-12)
    chk("ttm empty-before-first", P.ttm_cash_sum(ex, cum, 19990101,
                                                 19980101) == 0.0)
    dl = [20000101, 20050101, 20150101]
    fl = [2.0, 1.4, 1.0]    # f(latest)=1.0, grows back in time
    chk("sidecar stepwise d<=t",
        abs(P.sidecar_f_at(dl, fl, 20150601) - 1.0) < 1e-12
        and abs(P.sidecar_f_at(dl, fl, 20100601) - 1.4) < 1e-12
        and abs(P.sidecar_f_at(dl, fl, 20010601) - 2.0) < 1e-12)
    chk("sidecar pre-first-event edge -> f_list[0]",
        abs(P.sidecar_f_at(dl, fl, 19991231) - 2.0) < 1e-12)
    r = np.array([-0.5, -1.5, 0.25])
    nav = np.concatenate(([1.0], np.cumprod(1.0 + r)))
    chk("nav negative crossing", nav[-1] < 0 and float(nav.min()) < -0.25)
    yrs = pd.DatetimeIndex(["2025-12-31", "2026-01-02", "2026-01-03"])
    chk("yearly bucket owns day k+1",
        _yearly_rets(yrs, np.array([0.10, -0.20]))
        == {2026: float(1.1 * 0.8 - 1.0)})
    print("selftest: %d/%d PASS" % (ok, 7))
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "run"
    t_start = time.time()
    if cmd == "selftest":
        return cmd_selftest()
    import fund_divlowvol_p1 as FD
    FD._init_worker()
    if cmd == "quality-cliff":
        cmd_quality_cliff(FD)
        print("elapsed %.1fs" % (time.time() - t_start))
        return 0
    if cmd in ("quality-nav", "run"):
        q = cmd_quality_nav(FD)
        print("quality-nav: nav_min=%.4f first_neg=%s neg_close_syms=%d"
              % (q["nav_stats"]["nav_min"],
                 q["nav_stats"]["first_negative_day"],
                 q["negative_price_scan"]["n_symbols_neg_close"]))
    if cmd in ("quality-era", "run2"):
        cmd_quality_era(FD)
        print("elapsed %.1fs" % (time.time() - t_start))
        return 0
    if cmd in ("divlowvol-exdate", "run"):
        d = cmd_divlowvol_exdate(FD)
        a = d["aggregates"]
        print("divlowvol-exdate: months=%d cand_total=%d cash_mismatch=%d "
              "f_bad=%d raw_bad=%d sel_viol=%d exdays=%s"
              % (a["months"], a["cand_total"], a["cash_mismatch"],
                 a["f_out_of_range"], a["p_raw_nonpos"],
                 a["sel_violations"],
                 d["stored_returns_faces"]["exday_faces"]
                 ["member_exdays_in_sampled_spans"]))
    print("elapsed %.1fs" % (time.time() - t_start))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print("MECHANISM_FAILURE: %s" % e)
        raise SystemExit(2)
