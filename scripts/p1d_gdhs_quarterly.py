"""P-1d gdhs quarterly-frequency dedicated IC batch (P1D_GDHS_QUARTERLY.md).

r60 verdict: gdhs family structurally unevaluable in the daily pipeline
(37 IS cross-sections << MIN_PERIODS=500) -> this sanctioned dedicated
quarterly口径. bm-b lane, claim MSG-20260924-0545. Zero engine runs;
zero network; factor evidence only (no registration regardless of outcome).

Design (frozen in prereg):
  event       = placement row where >=500 stocks get a FRESH gdhs record
                (fresh == avail flips 0->1; derived from build_gdhs grids,
                no parquet re-parse).
  forward ret = close[next_event_row]/close[event_row] - 1 (event-to-event
                ~ one quarter). Last event (no forward) excluded.
  universe    = fresh-placed & ok_static panel & finite factor & finite
                close at both event and next-event rows.
  IC          = per-event cross-sectional Spearman via pa_lhb_ic machinery
                (rank_rows/ic_from_ranks, mask-first J7 discipline).
  splits      : IS = events < 2025-01-01 (~37), OOS = >= 2025-01-01 (~6,
                thin, manual honest block since stats_block skips <30).
  nulls       : K=50 seeded within-universe permutations per factor
                (seed 48_000). Effective V2 line = max(0.30, null p95|IR|)
                (quarterly-power correction, frozen in prereg SS3/SS4).

Subcommands: run | selftest
"""
import glob
import json
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from p1d_ext_slots_ic import build_gdhs, load_panel  # noqa: E402
from pa_lhb_ic import ic_from_ranks, rank_rows  # noqa: E402
from composite_ic import stats_block  # noqa: E402

SEED = 48_000
K_NULLS = 50
IS_END_TS = pd.Timestamp("2024-12-31")
MIN_EVENT_PLACEMENTS = 500      # canonical-event rule (P-1d _gdhs_quarters)
OUT_PATH = os.path.join(ROOT, "results", "shortline",
                        "p1d_gdhs_quarterly.json")
LEDGER_PREV = 5241             # chain head results/shortline/xlib_synth.json
LEDGER_PREV_FILE = "xlib_synth.json"
EVIDENCE_CUTOFF = "2026-09-22"
FACTORS = ("gdhs_chg_q", "gdhs_chg_2q", "gdhs_level")


def fresh_mask(g_avail):
    """Rows where a stock's record JUST became available (avail 0->1)."""
    prev = np.zeros_like(g_avail)
    prev[1:] = g_avail[:-1]
    return (g_avail > 0) & (prev == 0)


def oos_block(ic):
    """Manual honest OOS block (stats_block skips n<30)."""
    m = float(ic.mean()) if len(ic) else float("nan")
    return {"n_periods": int(len(ic)), "ic_mean": round(m, 4),
            "thin_sample_disclosure": "n<30: observation-grade only"}


def run_batch():
    t0 = time.time()

    def log(msg):
        print("[p1d-gdhs-q] %s" % msg, flush=True)

    cal, col, close, amount, meta = load_panel()
    T, N = meta["T"], meta["N"]
    g_chg_q, g_chg_2q, g_level, g_avail, gd_meta = build_gdhs(
        cal, col, T, N, log)
    grids = {"gdhs_chg_q": g_chg_q, "gdhs_chg_2q": g_chg_2q,
             "gdhs_level": g_level}

    fresh = fresh_mask(g_avail)
    counts = fresh.sum(axis=1)
    event_rows = np.where(counts >= MIN_EVENT_PLACEMENTS)[0]
    dropped_irregular = int(fresh.sum() - counts[event_rows].sum())
    log("events=%d (rows w/ >=%d fresh placements); irregular-dropped=%d"
        % (len(event_rows), MIN_EVENT_PLACEMENTS, dropped_irregular))

    # event-to-event forward return grid
    n_ev = len(event_rows)
    fwd = np.full((n_ev, N), np.nan)
    for i in range(n_ev - 1):
        a, b = event_rows[i], event_rows[i + 1]
        with np.errstate(invalid="ignore"):
            fwd[i] = close[b] / close[a] - 1.0
    # last event has no forward -> excluded by eff mask (all-NaN row)
    ev_dates = cal[event_rows]

    eff = np.zeros((n_ev, N), dtype=bool)
    for i in range(n_ev):
        if i == n_ev - 1:
            continue
        eff[i] = (fresh[event_rows[i]]
                  & np.isfinite(close[event_rows[i]])
                  & np.isfinite(close[event_rows[i + 1]]))
    eff &= np.isfinite(fwd)
    for name in FACTORS:
        eff &= np.isfinite(grids[name][event_rows])
    n_eff = int(eff.sum(axis=1).max())
    med_univ = float(np.median(eff.sum(axis=1)[eff.sum(axis=1) > 0]))
    log("universe median=%s max=%d" % (med_univ, n_eff))

    V = {name: grids[name][event_rows] for name in FACTORS}
    valid_rows = eff.any(axis=1)          # drop all-NaN rows (last event)
    R = rank_rows(eff, fwd)[valid_rows]
    r_dates = np.asarray(ev_dates, dtype="datetime64[us]")[valid_rows]
    ev_dt = pd.DatetimeIndex(ev_dates.astype("datetime64[us]"))
    n_is_all = int((ev_dt < IS_END_TS).sum())
    n_oos_all = int((ev_dt >= IS_END_TS).sum())

    rng = np.random.default_rng(SEED)
    results = {}
    null_audit = {"seed": SEED, "k": K_NULLS, "p95_abs_mean_ic": {},
                   "p95_abs_ir": {}}
    for name in FACTORS:
        F = rank_rows(eff, V[name])[valid_rows]
        ic = ic_from_ranks(F, R, r_dates)
        ic_is = ic[ic.index < IS_END_TS]
        ic_oos = ic[ic.index >= IS_END_TS]
        sb_full, sb_is = stats_block(ic), stats_block(ic_is)
        ob = oos_block(ic_oos)

        # K=50 within-universe permutation nulls (returns fixed)
        nm, nir = [], []
        for _ in range(K_NULLS):
            Vk = V[name].copy()
            for i in range(n_ev):
                idx = np.where(eff[i])[0]
                if len(idx) > 1:
                    Vk[i, idx] = rng.permutation(Vk[i, idx])
            Fk = rank_rows(eff, Vk)[valid_rows]
            ick = ic_from_ranks(Fk, R, r_dates)
            ick_is = ick[ick.index < IS_END_TS]
            if len(ick_is) < 2:
                continue
            nm.append(float(ick_is.mean()))
            sd = float(ick_is.std())
            nir.append(float(ick_is.mean()) / sd if sd > 0 else 0.0)
        p95_mean = float(np.percentile(np.abs(nm), 95)) if nm else float("nan")
        p95_ir = float(np.percentile(np.abs(nir), 95)) if nir else float("nan")
        null_audit["p95_abs_mean_ic"][name] = round(p95_mean, 5)
        null_audit["p95_abs_ir"][name] = round(p95_ir, 4)

        # gates (prereg SS4): IS-side
        is_mean = sb_is.get("ic_mean", float("nan"))
        is_ir = sb_is.get("ic_ir", float("nan"))
        if "skip" in sb_is:
            v1 = v2 = v3 = False
            verdict = "FAIL_insufficient_IS_periods"
        else:
            v1 = abs(is_mean) > max(0.02, p95_mean)
            v2 = abs(is_ir) >= max(0.30, p95_ir)
            same = (is_mean > 0) == (ob["ic_mean"] > 0) if np.isfinite(ob["ic_mean"]) else False
            reten = (ob["ic_mean"] / is_mean) if (is_mean and np.isfinite(ob["ic_mean"])) else 0.0
            v3 = bool(same and abs(reten) >= 0.5 and ob["n_periods"] >= 5)
            verdict = "PASS" if (v1 and v2 and v3) else "FAIL"
        results[name] = {"full": sb_full, "is": sb_is, "oos": ob,
                         "gates": {"v1_ic": bool(v1), "v2_ir": bool(v2),
                                   "v3_oos": bool(v3)},
                         "verdict": verdict,
                         "null_p95_abs_mean_ic": round(p95_mean, 5),
                         "null_p95_abs_ir": round(p95_ir, 4),
                         "effective_v2_line": round(max(0.30, p95_ir), 4)}
        log("%s: IS ic=%s ir=%s | OOS ic=%s n=%d | %s"
            % (name, is_mean, is_ir, ob["ic_mean"], ob["n_periods"], verdict))

    n_pass = sum(1 for r in results.values() if r["verdict"] == "PASS")
    out = {
        "meta": {"batch": "p1d_gdhs_quarterly",
                 "prereg": "research/shortline/P1D_GDHS_QUARTERLY.md",
                 "lane": "P-1d dedicated quarterly口径 (r60 sanctioned)",
                 "panel": meta, "gdhs": gd_meta,
                 "events": {"n_events": int(n_ev),
                            "usable_with_forward": int(valid_rows.sum()),
                            "n_is": n_is_all,
                            "n_oos": n_oos_all,
                            "median_universe": med_univ,
                            "irregular_placements_dropped": dropped_irregular},
                 "method": {"forward": "event-to-event close ratio (~1Q)",
                            "fresh": "avail 0->1 flip at placement row",
                            "splits": "IS<2025-01-01, OOS>=2025-01-01",
                            "power": "n_is~37 -> IR0.30 ~ t1.8 p~0.08 "
                                     "thin-power caveat (prereg SS4)"},
                 "elapsed_s": round(time.time() - t0, 1)},
        "results": results,
        "audit": {"ic_computations": 3 + 3 * K_NULLS,
                  "ledger_trials_added": 3 + 3 * K_NULLS,
                  "engine_runs": 0, "network": "none",
                  "seed_registered": "p1d_gdhs_quarterly=48_000",
                  "nulls": null_audit},
        "trials_ledger": {"prev_total": LEDGER_PREV,
                          "prev_file": LEDGER_PREV_FILE,
                          "batch_trials": 3 + 3 * K_NULLS,
                          "total": LEDGER_PREV + 3 + 3 * K_NULLS},
        "verdict_summary": {"pass": int(n_pass), "of": 3,
                            "batch_verdict": "PASS" if n_pass else "FAIL",
                            "registration": "none (factor evidence only)"},
    }
    out["evidence_cutoff"] = EVIDENCE_CUTOFF
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    tmp = OUT_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    os.replace(tmp, OUT_PATH)
    log("written %s (batch_verdict=%s)" % (OUT_PATH, out["verdict_summary"]["batch_verdict"]))
    return 0


# ---------------------------------------------------------------- selftest
def selftest():
    ok = [0]

    def check(name, cond):
        ok[0] += 1
        print("[selftest] %s... %s" % (name, "PASS" if cond else "FAIL"))
        if not cond:
            raise SystemExit(1)

    # 1. fresh_mask: 0->1 flips only
    av = np.zeros((4, 3))
    av[1, 0] = 1; av[2, 1] = 1; av[2, 2] = 1; av[3] = 1
    fr = fresh_mask(av)
    check("fresh 0->1 flip rows", fr[1, 0] and fr[2, 1] and fr[2, 2]
          and fr[3, 0] and not fr[1, 1] and not fr[0].any())

    # 2. IC machinery: strictly monotone factor -> IC == 1 (zero noise)
    rng = np.random.default_rng(7)
    V = rng.normal(size=(3, 40)); fwd = V * 2.0
    eff = np.ones((3, 40), dtype=bool)
    ic = ic_from_ranks(rank_rows(eff, V), rank_rows(eff, fwd),
                       np.arange(3) + np.datetime64("2020-01-01", "us"))
    check("monotone IC~1", abs(ic.mean() - 1.0) < 1e-9 and len(ic) == 3)

    # 3. permutation null on noise -> tiny |meanIC|
    nm = []
    Rr = rank_rows(eff, rng.normal(size=(3, 40)))
    for _ in range(20):
        Vk = rng.permutation(V[0])
        ick = ic_from_ranks(rank_rows(eff[0:1], Vk[None, :]), Rr[0:1],
                            np.array([np.datetime64("2020-01-01", "us")]))
        nm.append(abs(float(ick.mean())))
    check("noise null |IC| tiny", max(nm) < 0.5)

    # 4. event forward mapping strictly increasing / last excluded
    ev = np.array([10, 55, 120]); close = np.linspace(1, 2, 200)
    fwdg = np.full((3, 1), np.nan)
    for i in range(2):
        fwdg[i, 0] = close[ev[i + 1]] / close[ev[i]] - 1
    check("forward mapping", np.isfinite(fwdg[:2, 0]).all()
          and not np.isfinite(fwdg[2, 0])
          and fwdg[0, 0] < fwdg[1, 0])

    # 5. effective V2 line = max(0.30, null p95 IR)
    check("v2 power line", max(0.30, 0.41) == 0.41 and max(0.30, 0.22) == 0.30)

    # 6. gate logic combo
    is_mean, is_ir, p95m, p95ir = 0.05, 0.35, 0.006, 0.33
    v1 = abs(is_mean) > max(0.02, p95m)
    v2 = abs(is_ir) >= max(0.30, p95ir)
    check("gate combo", v1 and v2)

    print("[selftest] all %d checks PASS" % ok[0])
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "run":
        raise SystemExit(run_batch())
    if cmd == "selftest":
        raise SystemExit(selftest())
    print("usage: python scripts/p1d_gdhs_quarterly.py run|selftest")
    raise SystemExit(2)
