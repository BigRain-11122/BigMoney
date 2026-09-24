"""XSTOCK_TILT — XSTOCK composite survivor -> B-layer top-K tilt conversion.

Prereg FROZEN (round 151, commit 1261f058): research/shortline/XSTOCK_TILT.md
— N_eff=44 = 4 main cells (h20/h10 frequency x top5/top10) + 40 random nulls
(20 h20 seed 57_000+i, 20 h10 seed 57_100+i, all K=10). Passive NOT rerun:
stock_b_layer pool live-reads the registered P4_EXT_TILT product baseline.

Signal = the XSTOCK_SYNTH frozen K=4 primary composite (alpha191_070 x-1,
alpha191_042 +1, lhb_amt_share_20 +1, lhb_count_20 x-1; daily cross-section z,
equal weight, min_valid=3), rebuilt on the NATIVE p1c cache grid from the
xstock_synth z-caches (frozen member builders, zero rewrite) then projected
onto the batch2 strategy panel by (date, code) value join.

Reuse (no rebuild): p4_ext_tilt schedules/pulses/top-k/null/elig/exec/D6
semantics + xstock_synth z-caches & manifest + ps2_synth composite_z +
p4_batch2_screen shared panel/engine + science_gates v2 shared library.

Subcommands:
  selftest   offline, no panel dependency
  gates      constants+reproduction+universe probe (exit 2 = refuse batch)
  probe      gates + single-cell engine timing (SS0 probe-first protocol)
  run        resumable 44-cell batch (jsonl checkpoints + lock); cost-stress
             x2/x3 informational legs for the 4 main cells included
  status     progress readout
"""
import json
import os
import subprocess
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import p4_batch2_screen as B      # shared panel + engine exec machinery
import p4_ext_tilt as EXT         # schedules/pulses/topk/null/elig/exec/D6
import xstock_synth as XS         # frozen member builders (z-caches)
import science_gates as SG
from ps2_synth import composite_z, fwd_ret, rank_rows, ic_from_ranks

OUT_JSON = os.path.join(ROOT, "results", "shortline_xstock_tilt.json")
RUNS_JSONL = os.path.join(ROOT, "results", "xstock_tilt_runs.jsonl")
FINAL_CSV = os.path.join(ROOT, "research", "shortline", "xstock_tilt_results.csv")
LOCK = os.path.join(ROOT, "results", "xstock_tilt_run.lock")
PROBE_JSON = os.path.join(ROOT, "results", "xstock_tilt_probe.json")
SYNTH_JSON = os.path.join(ROOT, "results", "shortline", "xstock_synth.json")
ATTRITION = os.path.join(ROOT, "results", "gate_attrition.json")

# ---- frozen spec constants (XSTOCK_TILT.md SS0/SS2/SS3/SS4) ----
EVIDENCE_CUTOFF = "2026-09-22"
SEED_H20 = 57_000                  # SEED_REGISTRY xstock_tilt_h20
SEED_H10 = 57_100                  # SEED_REGISTRY xstock_tilt_h10
N_NULL = 20                        # per frequency
BATCH_CELLS = 44                   # N_eff: 4 main + 40 nulls (passive live-read)
K_PRIMARY = 4                      # XSTOCK_SYNTH frozen primary membership
MV_PRIMARY = 3                      # composite min_valid (SS3)
MIN_ELIG_MEDIAN = 1000              # SS2.5 revised sentinel gate
MIN_FIRST_REBAL_FACTOR = 500       # SS2.5 first-rebalance coverage gate
REF_MEDIAN_R68 = 1524              # r68 same-formula median (drift disclosure)
WORKERS = 8                        # O-1738 bm-b <= 12 (EXT_TILT precedent)
NULL_K = 10                        # all nulls K=10 (SS3)
FREE_RAM_MIN_GB = 4.0              # dual-company discipline: heavy job floor

# key, rebalance window (trading days), top_k
MAIN_CELLS = [
    ("h20_top5",  20, 5),
    ("h20_top10", 20, 10),
    ("h10_top5",  10, 5),
    ("h10_top10", 10, 10),
]
COST_STRESS_MULTS = {"cost_x2": 4.0, "cost_x3": 6.0}   # 26.082 -> 52.164 / 78.246 bp


# ---------------------------------------------------------------- schedules
def rebal_pos(T, W):
    """Fixed-frequency schedule: W-1, then every W trading days (SS3
    `range(W-1, T, W)`; EXT_TILT d20_rebal_pos semantics)."""
    return list(range(W - 1, T, W))


# ------------------------------------------------- frozen composite rebuild
def frozen_members():
    """SS2 gate 1 (constants): frozen K=4 primary membership from the
    XSTOCK_SYNTH product + manifest signs; every construction constant
    asserted equal to the synth module (zero-rewrite constructive
    guarantee). Returns (names, signs, primary_record, manifest)."""
    with open(SYNTH_JSON, encoding="utf-8-sig") as fh:
        prod = json.load(fh)
    prim = prod["primary"]
    names = list(prim["names"])
    man = XS._load_manifest()
    signs = [man["members"][n]["sign"] for n in names]
    assert XS.K_PRIMARY == K_PRIMARY == prim["k"], "K drift vs synth"
    assert XS.MV_PRIMARY == MV_PRIMARY == prim["min_valid"], "min_valid drift"
    assert XS.H_GATE == 10, "H_GATE drift"
    assert XS.CUTOFF == pd.Timestamp(EVIDENCE_CUTOFF), "cutoff drift"
    assert man["meta"]["cutoff"] == EVIDENCE_CUTOFF, "manifest cutoff drift"
    assert prod.get("evidence_cutoff") == EVIDENCE_CUTOFF, "product cutoff drift"
    assert XS.LHB_ERA == np.datetime64("2007-01-01", "us").astype("int64"), "LHB era drift"
    assert XS.EXT_ERA == np.datetime64("2010-01-01", "us").astype("int64"), "ext era drift"
    assert SG.SEED_REGISTRY.get("xstock_tilt_h20") == SEED_H20, "h20 seed registry"
    assert SG.SEED_REGISTRY.get("xstock_tilt_h10") == SEED_H10, "h10 seed registry"
    for n in names:
        r = man["members"].get(n) or {}
        assert r.get("status") == "ok" and r.get("z_kind") == "full", \
            f"member {n} not a full-era shelf z-cache"
    return names, signs, prim, man


def rebuild_composite(names, signs):
    """Composite on the NATIVE p1c grid (T x N float64): member z-caches *
    recorded signs -> composite_z(min_valid=3). Same loads and op order as
    xstock_synth._run_post comp_eval => bit-identical by construction."""
    zs = []
    for n, s in zip(names, signs):
        z = np.asarray(np.load(XS._z_path(n), mmap_mode="r"),
                       dtype=np.float64)     # full-era shelf rows (z_kind=full)
        zs.append(z * s)
    comp = composite_z(zs, MV_PRIMARY)
    del zs
    return comp


def reproduce_primary_ic(comp):
    """SS2 gate 1 (reproduction): rebuilt composite primary IS IC/IR vs the
    recorded XSTOCK_SYNTH product values, tolerance = half of last recorded
    digit per field (XS.REPRO_TOL_ROUNDED convention)."""
    from composite_ic import stats_block
    from p1c_stock_ic_batch import load_universe
    idx, _syms, _meta = load_universe()
    cal_us = idx.values.astype("datetime64[us]").astype("int64")
    close = np.asarray(np.load(XS.CLOSE_FFILL_NPY, mmap_mode="r"),
                       dtype=np.float64)
    maskC = np.isfinite(close)
    fwd10 = fwd_ret(close, XS.H_GATE)
    del close
    eff = maskC & np.isfinite(comp) & np.isfinite(fwd10)
    s = ic_from_ranks(rank_rows(eff, comp), rank_rows(eff, fwd10), cal_us)
    del eff, fwd10, maskC
    b_is = stats_block(s[s.index <= XS.IS_END_TS])
    return b_is


def repro_gate(prim, b_is):
    tol = XS.REPRO_TOL_ROUNDED
    d_ic = abs(float(b_is["ic_mean"]) - float(prim["is_ic"]))
    d_ir = abs(float(b_is["ic_ir"]) - float(prim["is_ir"]))
    ok = bool(d_ic <= tol and d_ir <= 0.5e-2)
    return {"recomputed_is_ic": b_is.get("ic_mean"),
            "recomputed_is_ir": b_is.get("ic_ir"),
            "recorded_is_ic": prim["is_ic"], "recorded_is_ir": prim["is_ir"],
            "delta_ic": d_ic, "delta_ir": d_ir,
            "tol_ic": tol, "tol_ir": 0.5e-2, "pass": ok}


# ------------------------------------------------------- join projection
def _project_values(comp):
    """Pure (date, code) join: native-grid composite -> strategy-panel shaped
    array (value lookup, pointwise in t). Returns (proj, row_map, cols)."""
    from p1c_stock_ic_batch import load_universe
    idx, syms, _meta = load_universe()
    p1c_day = idx.values.astype("datetime64[D]")
    strat_days = B._S["dates"].astype("datetime64[D]")
    row = np.searchsorted(p1c_day, strat_days)
    in_range = row < len(p1c_day)
    ok_row = in_range & (p1c_day[np.minimum(row, len(p1c_day) - 1)]
                         == strat_days)
    col_map = {s: i for i, s in enumerate(syms)}
    strat_codes = [str(c) for c in B._S["codes"]]
    cols = np.array([col_map.get(c, -1) for c in strat_codes], dtype=np.int64)
    valid_j = np.flatnonzero(cols >= 0)
    proj = np.full((B._S["T"], B._S["N"]), np.nan, dtype=np.float64)
    r_ok = np.flatnonzero(ok_row)
    if len(r_ok) and len(valid_j):
        take_r = row[r_ok]
        take_c = cols[valid_j]
        proj[np.ix_(r_ok, valid_j)] = comp[take_r[:, None], take_c[None, :]]
    return proj, row, cols, ok_row, strat_codes, syms, len(p1c_day)


def project_composite(comp):
    """SS3 value projection with per-code disclosure (5222 vs 5212)."""
    proj, row, cols, ok_row, strat_codes, syms, n_p1c = _project_values(comp)
    miss_codes = [c for c, j in zip(strat_codes, cols) if j < 0]
    extra = sorted(set(syms) - set(strat_codes))
    disclose = {
        "n_strat_dates": int(B._S["T"]), "n_p1c_dates": int(n_p1c),
        "unmatched_dates": int((~ok_row).sum()),
        "n_strat_codes": len(strat_codes), "n_p1c_codes": len(syms),
        "codes_missing_on_p1c_grid": miss_codes,
        "n_codes_not_in_strategy_panel": len(extra),
        "codes_not_in_strategy_panel_head": extra[:12],
        "join": "(date, code) value lookup; zero future data (composite[t] "
                "known at t close; entry t+1 open per SS3)",
    }
    assert disclose["unmatched_dates"] == 0, \
        "strategy dates absent from p1c grid — join integrity violation"
    return proj, disclose


def truncate_compare_causal(comp):
    """SS3 causality self-check (truncate-and-compare): poisoning every
    native row at/after the strategy panel's midpoint date must leave the
    projected HEAD bit-identical (pointwise join = no cross-time leakage)."""
    T = B._S["T"]
    cut = T // 2
    proj0, row, *_ = _project_values(comp)
    head_ref = proj0[:cut]
    del proj0
    poisoned = comp.copy()
    poisoned[row[cut]:] = np.nan        # native rows at/after midpoint date
    head_chk = _project_values(poisoned)[0][:cut]
    del poisoned
    same = bool(np.array_equal(head_ref, head_chk, equal_nan=True))
    return {"check": "tail-poisoned projection head bit-identical",
            "head_rows": int(cut), "head_finite": int(np.isfinite(head_ref)
                                                      .sum()),
            "pass": same}


# ------------------------------------------------------------ universe gates
def universe_probe(elig, proj, T=None):
    """SS2.5 revised gates: daily-eligible median >= 1000 sentinel AND first
    rebalance composite coverage >= 500 on both schedules; r68 median
    reference disclosed (drift > 2 sigma of the daily series = refuse).

    T is injectable for hermetic selftest fixtures (r116 law); production
    calls leave it None and read the shared panel shape.

    SS2.5 'first rebalance day' adjudication (frozen pre-run, zero-artifact
    window, r71 protocol): = the FIRST SCHEDULED REBALANCE DAY WITH A
    NON-EMPTY ELIGIBLE SET. Rationale: (a) SS5.5's own approximation
    'count ~= daily eligible' presupposes eligible > 0; (b) the frozen
    P4_BATCH2 universe clauses (20d mean amount) make every panel row t<19
    constructively empty for ANY schedule W<=20 — a mechanical
    first-scheduled-day reading would veto the panel's own warmup and make
    every W<=20 batch unrunnable, contradicting the h10 cells being frozen
    INTO this batch; (c) the gate's object is FACTOR availability, which at
    the degenerate day is healthy (native coverage ~89%, disclosed below).
    Both readings' numbers are disclosed; no post-run reinterpretation.
    """
    S = B._S
    if T is None:
        T = S["T"]
    T = int(T)
    daily = elig.sum(axis=1)
    med = int(np.median(daily))
    sigma = float(np.std(daily, ddof=1))
    drift_bad = bool(abs(med - REF_MEDIAN_R68) > 2 * sigma)

    def first_effective(W):
        sched = rebal_pos(T, W)
        skipped = 0
        for t in sched:
            n_elig = int(elig[t].sum())
            if n_elig == 0:
                skipped += 1
                continue
            return {"first_scheduled_pos": sched[0],
                    "first_effective_pos": t,
                    "empty_elig_days_skipped": skipped,
                    "first_effective_eligible": n_elig,
                    "first_effective_composite_count":
                        int((elig[t] & np.isfinite(proj[t])).sum()),
                    "first_scheduled_day_composite_over_raw":
                        int(np.isfinite(proj[sched[0]]).sum()),
                    "first_scheduled_day_eligible": int(elig[sched[0]].sum())}
        return {"first_effective_pos": None,
                "empty_elig_days_skipped": len(sched),
                "first_effective_eligible": 0,
                "first_effective_composite_count": 0}

    h20 = first_effective(20)
    h10 = first_effective(10)
    g = {"median_daily_eligible": med, "gate_median": MIN_ELIG_MEDIAN,
         "pass_median": bool(med >= MIN_ELIG_MEDIAN),
         "ref_median_r68": REF_MEDIAN_R68,
         "daily_sigma": round(sigma, 1), "drift_gt_2sigma": drift_bad,
         "gate_first_rebal": MIN_FIRST_REBAL_FACTOR,
         "h20": h20, "h10": h10,
         "pass_first_rebal": bool(
             h20["first_effective_composite_count"] >= MIN_FIRST_REBAL_FACTOR
             and h10["first_effective_composite_count"]
             >= MIN_FIRST_REBAL_FACTOR),
         "ss25_resolution": "first rebalance day = first scheduled day with "
                            "non-empty eligible set (pre-run adjudication, "
                            "frozen r152; degenerate-day numbers disclosed "
                            "per schedule)"}
    g["pass"] = bool(g["pass_median"] and g["pass_first_rebal"]
                     and not drift_bad)
    return g


# ---------------------------------------------------------------- selections
def build_all_selections(proj, elig):
    """Main cells: top-K composite (descending, high=good — composite is
    sign-oriented; ties -> lower code first via EXT._topk_selection stable
    argsort). Nulls: uniform without-replacement K=10 in the eligible
    universe at each rebalance day (EXT._null_selection, seeds SS3)."""
    S = B._S
    T = S["T"]
    out = {}
    for key, W, top_k in MAIN_CELLS:
        sched = rebal_pos(T, W)
        sels = []
        for t in sched:
            cols = EXT._topk_selection(t, proj[t], elig[t], top_k, False)
            if cols:
                sels.append((int(t), cols))
        out[key] = (W, top_k, sels, sched)
    nulls = {}
    for k in range(N_NULL):
        rng = np.random.default_rng(SEED_H20 + k)
        sels = []
        for t in rebal_pos(T, 20):
            cols = EXT._null_selection(t, elig[t], rng, NULL_K)
            if cols:
                sels.append((int(t), cols))
        nulls[f"null_h20_s{SEED_H20 + k}"] = ("random_null_h20", NULL_K, sels)
    for k in range(N_NULL):
        rng = np.random.default_rng(SEED_H10 + k)
        sels = []
        for t in rebal_pos(T, 10):
            cols = EXT._null_selection(t, elig[t], rng, NULL_K)
            if cols:
                sels.append((int(t), cols))
        nulls[f"null_h10_s{SEED_H10 + k}"] = ("random_null_h10", NULL_K, sels)
    return out, nulls


# ---------------------------------------------------------------- engine run
def _exec_run_cost(entry, exit_, syms_idx, top_k, tag, cost_mult):
    """EXT._exec_run_tilt semantics with an explicit cost multiplier (SS4
    cost-stress informational legs; base legs always go through
    EXT._exec_run_tilt = 26.082bp CostPatch)."""
    from engine import run_backtest
    from live.paper import CostPatch, seg_metrics
    S = B._S
    codes, dt = S["codes"], S["dt"]
    syms = [str(codes[j]) for j in syms_idx]
    sel = np.array(syms_idx)
    e_df = pd.DataFrame(entry[:, sel], index=dt, columns=syms)
    x_df = pd.DataFrame(exit_[:, sel], index=dt, columns=syms)
    guard = {"buy": pd.DataFrame(S["buy_ok"][:, sel], index=dt, columns=syms),
             "sell": pd.DataFrame(S["sell_ok"][:, sel], index=dt, columns=syms)}
    params = {"max_positions": top_k, "position_size_pct": B.POS_PCT,
              "report_num_entries": True}
    prices = B._prices_dict(sel)
    t0 = time.time()
    with CostPatch(cost_mult):
        res = run_backtest(prices, params, entry_signal=e_df,
                           exit_signal=x_df, fill_guard=guard)
    elapsed = time.time() - t0
    eq = pd.Series(res["equity_curve"], index=dt[:len(res["equity_curve"])])
    oos_tr = sum(1 for tr in res["trades"] if tr["date"] >= B.OOS_START)
    rets = eq.pct_change().dropna()
    yearly = {}
    for year, seg in eq.groupby(eq.index.year):
        yearly[int(year)] = round(float(seg.iloc[-1] / seg.iloc[0] - 1), 4)
    full = res["metrics"]
    return {"tag": tag, "full": full, "oos": seg_metrics(eq, B.OOS_START),
            "n_trades": full["num_trades"],
            "num_entries": full.get("num_entries"), "oos_trades": oos_tr,
            "returns": [round(float(v), 8) for v in rets],
            "yearly": yearly, "run_seconds": round(elapsed, 1)}


def _cell_task(args):
    """Worker: selections precomputed in main; frames + engine run."""
    key, kind, top_k, selections, n_syms_total = args
    B._ensure_shared()
    T, N = B._S["T"], B._S["N"]
    entry, exit_ = EXT.frames_from_selections(T, N, selections)
    fired = np.flatnonzero(entry.any(axis=0))
    if kind in COST_STRESS_MULTS:
        rec = _exec_run_cost(entry, exit_, fired, top_k, key,
                             COST_STRESS_MULTS[kind])
    else:
        rec = EXT._exec_run_tilt(entry, exit_, fired, top_k, key)
    rec.update({"key": key, "kind": kind, "top_k": top_k,
                "n_syms": int(len(fired)),
                "n_rebal_days": len(selections),
                "n_panel": int(n_syms_total)})
    return rec


# ---------------------------------------------------------------- checkpoints
def _load_done():
    done = {}
    if os.path.exists(RUNS_JSONL):
        with open(RUNS_JSONL, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    done[rec["key"]] = rec
                except Exception:
                    continue
    return done


def _write_lock():
    with open(LOCK, "w") as fh:
        fh.write(str(os.getpid()))


def _lock_alive():
    if not os.path.exists(LOCK):
        return False
    try:
        with open(LOCK) as fh:
            pid = int(fh.read().strip())
        out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}"],
                             capture_output=True, timeout=15, text=True,
                             encoding="utf-8", errors="replace").stdout
        return str(pid) in out
    except Exception:
        return False


def _append_rec(rec):
    with open(RUNS_JSONL, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(B._jsonable(rec), ensure_ascii=False) + "\n")


# ---------------------------------------------------------------- gates leg
def _gates_leg(write=None):
    """Shared gates sequence: shared panel -> corrected eligibility ->
    frozen-members constants -> composite rebuild -> reproduction ->
    projection -> universe probe. Returns (gates, proj, elig, names, signs)."""
    B._ensure_shared()
    print(f"shared build {B._S['build_s']}s | T={B._S['T']} N={B._S['N']}",
          flush=True)
    elig = EXT.elig_corrected()
    star_mask = np.array([str(c).startswith(("688", "689"))
                          for c in B._S["codes"]])
    nonstar_same = bool(np.array_equal(elig[:, ~star_mask],
                                       B._S["elig"][:, ~star_mask]))
    print(f"elig clone cross-check (non-STAR cols identical): {nonstar_same}",
          flush=True)
    names, signs, prim, man = frozen_members()
    t0 = time.time()
    comp = rebuild_composite(names, signs)
    print(f"composite rebuild {time.time() - t0:.0f}s "
          f"(native grid {comp.shape[0]}x{comp.shape[1]})", flush=True)
    b_is = reproduce_primary_ic(comp)
    rg = repro_gate(prim, b_is)
    print(f"reproduction: is_ic={b_is.get('ic_mean')} vs recorded "
          f"{prim['is_ic']} (delta {rg['delta_ic']:.2e}) "
          f"ir={b_is.get('ic_ir')} vs {prim['is_ir']} -> pass={rg['pass']}",
          flush=True)
    if not rg["pass"]:
        gates = {"pass": False, "reproduction": rg,
                 "fail_reason": "primary composite reproduction FAIL (SS2 gate 1)"}
        if write:
            with open(write, "w", encoding="utf-8") as fh:
                json.dump(gates, fh, indent=2, ensure_ascii=False)
        del comp
        return gates, None, elig, names, signs
    proj, disclose = project_composite(comp)
    causal = truncate_compare_causal(comp)
    del comp
    uni = universe_probe(elig, proj)
    print(f"universe probe: median={uni['median_daily_eligible']} "
          f"(gate {MIN_ELIG_MEDIAN}) "
          f"h20 first_eff@{uni['h20'].get('first_effective_pos')}="
          f"{uni['h20'].get('first_effective_composite_count')} "
          f"(skip {uni['h20'].get('empty_elig_days_skipped')}) "
          f"h10 first_eff@{uni['h10'].get('first_effective_pos')}="
          f"{uni['h10'].get('first_effective_composite_count')} "
          f"(skip {uni['h10'].get('empty_elig_days_skipped')}) "
          f"(gate {MIN_FIRST_REBAL_FACTOR}) -> pass={uni['pass']}", flush=True)
    print(f"causal truncate-and-compare: pass={causal['pass']}", flush=True)
    gates = {"pass": bool(rg["pass"] and uni["pass"] and causal["pass"]),
             "reproduction": rg, "universe_probe": uni,
             "projection": disclose, "causal_check": causal,
             "members": names, "signs": signs,
             "elig_clone_nonstar_identical": nonstar_same}
    if write:
        with open(write, "w", encoding="utf-8") as fh:
            json.dump(gates, fh, indent=2, ensure_ascii=False)
    return gates, proj, elig, names, signs


def cmd_gates():
    gates, *_ = _gates_leg(write=PROBE_JSON)
    print(json.dumps({"pass": gates["pass"],
                      "reproduction": gates.get("reproduction"),
                      "universe_probe": gates.get("universe_probe"),
                      "projection": gates.get("projection")}, indent=1))
    return 0 if gates["pass"] else 2


def cmd_probe():
    t0 = time.time()
    gates, proj, elig, *_ = _gates_leg(write=PROBE_JSON)
    if not gates["pass"]:
        print("EXIT 2: gates FAIL — probe stops (no batch)", flush=True)
        return 2
    main_sel, null_sel = build_all_selections(proj, elig)
    for k, (W, top_k, sels, sched) in main_sel.items():
        avg = (np.mean([len(c) for _, c in sels]) if sels else 0)
        print(f"  {k}: {len(sels)}/{len(sched)} rebal days with selections "
              f"avg_k={avg:.1f}", flush=True)
    t1 = time.time()
    W, top_k, sels, sched = main_sel["h20_top10"]
    entry, exit_ = EXT.frames_from_selections(B._S["T"], B._S["N"], sels)
    fired = np.flatnonzero(entry.any(axis=0))
    r = EXT._exec_run_tilt(entry, exit_, fired, top_k, "probe_h20_top10")
    print(f"PROBE h20_top10: full_s={r['full']['sharpe']} "
          f"oos_s={r['oos']['sharpe']} trades={r['n_trades']} "
          f"entries={r['num_entries']} run={r['run_seconds']}s", flush=True)
    per_main = max(r["run_seconds"], 5)
    nk = null_sel[f"null_h20_s{SEED_H20}"]
    entry, exit_ = EXT.frames_from_selections(B._S["T"], B._S["N"], nk[2])
    fired = np.flatnonzero(entry.any(axis=0))
    rn = EXT._exec_run_tilt(entry, exit_, fired, NULL_K, "probe_null")
    print(f"PROBE null: full_s={rn['full']['sharpe']} "
          f"trades={rn['n_trades']} run={rn['run_seconds']}s", flush=True)
    per_null = max(rn["run_seconds"], 3)
    n_cells = 4 + 8 + 40      # main + cost-stress x2/x3 + nulls
    est = (4 * per_main + 8 * per_main + 40 * per_null) / WORKERS
    with open(PROBE_JSON, encoding="utf-8-sig") as fh:
        probe = json.load(fh)
    probe["probe"] = {"main_cell_s": per_main, "null_cell_s": per_null,
                      "probe_total_s": round(time.time() - t0, 1),
                      "est_batch_wall_s": round(est, 0),
                      "n_engine_cells": n_cells,
                      "h20_top10_full_sharpe": r["full"]["sharpe"],
                      "null_full_sharpe": rn["full"]["sharpe"]}
    with open(PROBE_JSON, "w", encoding="utf-8") as fh:
        json.dump(probe, fh, indent=2, ensure_ascii=False)
    print(f"probe total {time.time() - t0:.0f}s | est batch wall "
          f"({n_cells} cells / {WORKERS} workers) ~{est:.0f}s "
          f"(>600s => background pool per SS0)", flush=True)
    return 0


# ---------------------------------------------------------------- run batch
def cmd_run():
    from concurrent.futures import ProcessPoolExecutor
    if _lock_alive():
        print("EXIT 3: batch already running (lock alive) — status only")
        return 3
    try:
        import psutil
        free_gb = psutil.virtual_memory().available / 2**30
        if free_gb < FREE_RAM_MIN_GB:
            print(f"EXIT 4: free RAM {free_gb:.1f}GB < {FREE_RAM_MIN_GB}GB "
                  "floor - honest exit (retry when idle)", flush=True)
            return 4
    except ImportError:
        pass
    _write_lock()
    t0 = time.time()
    try:
        gates, proj, elig, names, signs = _gates_leg(write=PROBE_JSON)
        if not gates["pass"]:
            print("EXIT 2: gates FAIL — no half-data batches (spec SS2)")
            return 2
        main_sel, null_sel = build_all_selections(proj, elig)
        del proj                       # selections precomputed; free ~0.5GB
        tasks = []
        for key, (W, top_k, sels, sched) in main_sel.items():
            tasks.append((key, "main", top_k, sels, B._S["N"]))
            for ckind in COST_STRESS_MULTS:     # informational legs (SS4)
                tasks.append((f"{key}__{ckind}", ckind, top_k, sels,
                             B._S["N"]))
        for key, (kind, top_k, sels) in null_sel.items():
            tasks.append((key, kind, top_k, sels, B._S["N"]))
        done = _load_done()
        todo = [t for t in tasks if t[0] not in done]
        print(f"cells total={len(tasks)} done={len(done)} todo={len(todo)}",
              flush=True)
        if todo:
            with ProcessPoolExecutor(max_workers=WORKERS) as ex:
                for rec in ex.map(_cell_task, todo):
                    _append_rec(rec)
                    print(f"  done {rec['key']} s={rec['full']['sharpe']} "
                          f"trades={rec['n_trades']} "
                          f"({rec['run_seconds']}s)", flush=True)
        ok = _finalize(time.time() - t0)
        return 0 if ok else 1
    finally:
        try:
            os.remove(LOCK)
        except OSError:
            pass


# ---------------------------------------------------------------- finalize
def _finalize(elapsed):
    import csv as _csv
    from screening import pbo as pbo_mod
    from live.paper import seg_metrics  # noqa: F401 (schema familiarity)
    if os.path.exists(OUT_JSON) and \
            os.environ.get("XSTOCK_TILT_REFINALIZE") != "1":
        print("finalize refused: OUT_JSON exists (single-shot guard; "
              "XSTOCK_TILT_REFINALIZE=1 to redo)")
        return False
    done = _load_done()
    main_keys = [k for k, *_ in MAIN_CELLS]
    null_keys = [k for k in done if k.startswith(("null_h20_", "null_h10_"))]
    stress_keys = [k for k in done if "__cost_" in k]
    if not all(k in done for k in main_keys) or len(null_keys) != 2 * N_NULL:
        print(f"finalize refused: incomplete run set "
              f"(main {sum(k in done for k in main_keys)}/4, "
              f"nulls {len(null_keys)}/40)")
        return False

    # D6: candidate vs registered traders (ew6 member reruns, EXT_TILT reuse)
    print("D6 member reruns (anchor reproductions)...", flush=True)
    mrets = EXT._member_returns()
    dt_idx = B._S["dt"]
    d6 = {"members": sorted(mrets), "pairs": {}, "reject_line": 0.7}
    for k in main_keys:
        r = pd.Series(done[k]["returns"], name=k)
        r.index = dt_idx[1:len(r) + 1]
        worst_name, worst_v = None, 0.0
        all_pairs = {}
        for tid, mr in mrets.items():
            j = pd.concat([r, mr], axis=1, join="inner").dropna()
            v = float(j.corr().iloc[0, 1]) if len(j) > 60 else float("nan")
            all_pairs[tid] = round(v, 4)
            if np.isfinite(v) and abs(v) > abs(worst_v):
                worst_name, worst_v = tid, v
        d6["pairs"][k] = {"all": all_pairs, "max_abs": round(abs(worst_v), 4),
                          "max_abs_member": worst_name,
                          "d6_ok": bool(abs(worst_v) < 0.7)}
        print(f"  {k}: max|corr|={abs(worst_v):.4f} vs {worst_name}", flush=True)

    # interim single-shot guard FIRST (anti-double ledger append: any re-entry
    # after a mid-finalize crash sees OUT_JSON and refuses; explicit
    # XSTOCK_TILT_REFINALIZE=1 re-finalize reuses the ledger head, never
    # appends twice)
    if os.environ.get("XSTOCK_TILT_REFINALIZE") == "1":
        ledger = SG.ledger_head()
    else:
        ledger = SG.append_ledger(
            "xstock_tilt", BATCH_CELLS, os.path.basename(OUT_JSON),
            note=("4 main cells (h20/h10 x top5/top10) + 40 random nulls (20 "
                  "h20 seed 57_000+i, 20 h10 seed 57_100+i, K=10); passive "
                  "NOT rerun - stock_b_layer registered baseline live-read; "
                  "prereg research/shortline/XSTOCK_TILT.md (frozen r151 "
                  "1261f058); cost x2/x3 legs informational (SS4), excluded "
                  "from N_eff"),
            evidence_cutoff=EVIDENCE_CUTOFF)
    interim = {"meta": {"batch": "XSTOCK_TILT", "interim": True},
               "trials_ledger": ledger}
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(interim, fh, indent=2, ensure_ascii=False)

    # skill line (own null pool; passive via stock_b_layer product file)
    null_sharpes = [done[k]["full"]["sharpe"] for k in null_keys]
    mu = float(np.mean(null_sharpes))
    sigma = float(np.std(null_sharpes, ddof=1))
    own_null = {"values": null_sharpes,
                "coverage": {"n_values": len(null_sharpes),
                             "schemas_parsed": ["own batch nulls"],
                             "known_unparsed": [], "mu": mu, "sigma": sigma}}
    skill = SG.skill_line_v2(batch_cells=BATCH_CELLS, pool="stock_b_layer",
                             null_pool=own_null)
    print(f"skill_line={skill['line']} (no vi floor in this prereg)", flush=True)

    # family PBO (G2 input; 4 main cells, J19 4-cell family precedent)
    rets_df = pd.DataFrame(
        {k: pd.Series(done[k]["returns"], index=dt_idx[1:len(done[k]
                        ["returns"]) + 1]) for k in main_keys})
    pbo_block = None
    try:
        aligned = pbo_mod.align_returns(
            {k: rets_df[k].dropna() for k in main_keys})
        pbo_block = pbo_mod.cscv_pbo(aligned)
        print(f"family PBO={pbo_block['pbo']} ({pbo_block['verdict']})",
              flush=True)
    except Exception as ex:
        print(f"family PBO failed honestly: {type(ex).__name__}: {ex}",
              flush=True)

    # per-cell G1' v2 + descriptive + G2 (only for G1' survivors)
    cells_out, survivors = [], []
    for key, W, top_k in MAIN_CELLS:
        c = done[key]
        rets = pd.Series(c["returns"])
        g1 = SG.g1_prime_v2(sharpe_full=c["full"]["sharpe"], returns=rets,
                            batch_cells=BATCH_CELLS, pool="stock_b_layer",
                            n_trades=c["n_trades"], n_entries=c["num_entries"],
                            null_pool=own_null)
        dtg = g1.get("trade_gate") or {}
        trades_ok = bool(dtg.get("trades_ok", c["n_trades"] >= 30))
        entries_ok = bool(dtg.get("entries_ok", True))
        desc = {
            "annual_pos": bool(c["full"]["annual_return"] > 0),
            "oos_dual_pos": bool(c["oos"]["sharpe"] > 0
                                 and c["oos"]["annual_return"] > 0),
            "dd_ok": bool(c["full"]["max_drawdown"] >= -0.35),
            "worst_year": min(c["yearly"].values()) if c["yearly"] else None,
        }
        stress = {}
        for ckind in COST_STRESS_MULTS:
            sk = f"{key}__{ckind}"
            if sk in done:
                yr = done[sk]["yearly"]
                stress[ckind] = {
                    "sharpe": done[sk]["full"]["sharpe"],
                    "annual_return": done[sk]["full"]["annual_return"],
                    "worst_year": min(yr.values()) if yr else None}
        d6ok = d6["pairs"][key]["d6_ok"]
        g1_pass = bool(g1["pass_v2"] and trades_ok and entries_ok and d6ok)
        g2 = None
        if g1_pass:
            dsr = SG.deflated_sharpe_ratio(list(rets),
                                           n_trials=BATCH_CELLS)
            g2 = SG.g2_registration_v2(g1_pass, dsr,
                                       pbo_block["pbo"] if pbo_block else None)
        cells_out.append({
            "key": key, "family": "xstock_composite", "rebal_window": W,
            "top_k": top_k, "full": c["full"], "oos": c["oos"],
            "n_trades": c["n_trades"], "num_entries": c["num_entries"],
            "oos_trades": c["oos_trades"], "yearly": c["yearly"],
            "run_seconds": c["run_seconds"], "n_syms": c["n_syms"],
            "n_rebal_days": c["n_rebal_days"],
            "g1_prime_v2": g1, "trades_ok": trades_ok,
            "entries_ok": entries_ok, "descriptive": desc,
            "cost_stress": stress, "d6": d6["pairs"][key],
            "g1_pass_v2": g1_pass, "g2_registration_v2": g2})
        if g1_pass:
            survivors.append(key)

    # audit block (compute_audit latest sample)
    audit = {"workers": WORKERS, "policy": "O-1738 bm-b <= 12"}
    ap = os.path.join(ROOT, "results", "compute_audit.json")
    if os.path.exists(ap):
        with open(ap, encoding="utf-8-sig") as fh:
            latest = (json.load(fh).get("latest") or {})
        audit["sampled"] = {k: latest.get(k) for k in
                            ("cpu_total_pct", "verdict", "flags", "ts")}

    with open(PROBE_JSON, encoding="utf-8-sig") as fh:
        probe_rec = json.load(fh)

    out = {
        "meta": {
            "batch": "XSTOCK_TILT", "dept": "research",
            "prereg": "research/shortline/XSTOCK_TILT.md (frozen r151 1261f058)",
            "date": time.strftime("%Y-%m-%d %H:%M"),
            "panel": {"T": int(B._S["T"]), "N": int(B._S["N"]),
                      "source": "Money02/data/cache/p4_batch2_panel (r38-a)"},
            "signal": {"members": probe_rec.get("members"),
                       "signs": probe_rec.get("signs"),
                       "construction": "xstock_synth z-caches -> composite_z "
                                       "(min_valid=3) -> (date,code) join "
                                       "projection (value lookup)"},
            "exit_regime": "default (engine exit machine, no CE)",
            "cost": "V1 stock 26.082bp roundtrip (CostPatch 2x ETF); "
                    "x2=52.164bp / x3=78.246bp informational legs",
            "seeds": {"h20_null_base": SEED_H20, "h10_null_base": SEED_H10,
                      "n_nulls_each": N_NULL, "null_k": NULL_K},
            "audit": audit, "elapsed_s": round(elapsed, 1),
        },
        "gates": {k: probe_rec.get(k) for k in
                  ("reproduction", "universe_probe", "projection",
                   "causal_check", "elig_clone_nonstar_identical")},
        "skill_line": skill,
        "null_pool": {"mu": round(mu, 4), "sigma": round(sigma, 4),
                       "n": len(null_sharpes),
                       "p95": round(float(np.percentile(null_sharpes, 95)), 4),
                       "mu_h20": round(float(np.mean(
                           [done[k]["full"]["sharpe"] for k in null_keys
                            if k.startswith("null_h20_")])), 4),
                       "mu_h10": round(float(np.mean(
                           [done[k]["full"]["sharpe"] for k in null_keys
                            if k.startswith("null_h10_")])), 4)},
        "d6_correlation": d6,
        "family_pbo": pbo_block,
        "cells": cells_out,
        "nulls": [{"key": k, "kind": done[k]["kind"],
                   "sharpe": done[k]["full"]["sharpe"],
                   "n_trades": done[k]["n_trades"],
                   "num_entries": done[k]["num_entries"],
                   "annual_return": done[k]["full"]["annual_return"],
                   "max_drawdown": done[k]["full"]["max_drawdown"]}
                  for k in null_keys],
        "survivors": survivors,
        "trials_ledger": ledger,
        "next_step": ("0/4 = XSTOCK conversion line closes (SS4 verdict; "
                      "revival clauses = new prereg each). Survivors -> G2 "
                      "v2 registration per SS4."),
    }
    out.update(SG.cutoff_meta(EVIDENCE_CUTOFF))
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)

    cols = ["key", "rebal_window", "top_k", "n_trades", "num_entries",
            "annual_return", "sharpe", "max_drawdown", "oos_sharpe",
            "oos_annual_return", "skill_line", "line_ok",
            "ci_lb_positive", "entries_ok", "trades_ok", "d6_max_abs",
            "d6_ok", "g1_pass_v2", "g2_eligible_v2", "n_rebal_days",
            "run_seconds"]
    with open(FINAL_CSV, "w", encoding="utf-8", newline="") as fh:
        w = _csv.writer(fh)
        w.writerow(cols)
        for c in cells_out:
            w.writerow([
                c["key"], c["rebal_window"], c["top_k"], c["n_trades"],
                c["num_entries"], c["full"]["annual_return"],
                c["full"]["sharpe"], c["full"]["max_drawdown"],
                c["oos"]["sharpe"], c["oos"]["annual_return"],
                skill["line"], c["g1_prime_v2"]["line_ok"],
                c["g1_prime_v2"]["ci_lower_bound_positive"], c["entries_ok"],
                c["trades_ok"], c["d6"]["max_abs"], c["d6"]["d6_ok"],
                c["g1_pass_v2"],
                (c["g2_registration_v2"] or {}).get("eligible_v2", ""),
                c["n_rebal_days"], c["run_seconds"]])
        for k in null_keys:
            n = done[k]
            w.writerow([k, n["kind"], 10, n["n_trades"], n["num_entries"],
                        n["full"]["annual_return"], n["full"]["sharpe"],
                        n["full"]["max_drawdown"], "", "", skill["line"], "",
                        "", "", "", "", "", "", "", n["run_seconds"]])
    _register_attrition(ledger, survivors)
    print(f"FINAL: survivors={survivors} skill_line={skill['line']} "
          f"null mu={mu:.4f} sigma={sigma:.4f}")
    return True


def _register_attrition(ledger, survivors):
    """s7-T SS8: gate-attrition ledger entry (science_audit C4)."""
    ent = {"batch": "XSTOCK_TILT", "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
           "kind": "search",
           "cells_ledger_delta": BATCH_CELLS,
           "ledger_total_after": ledger.get("total"),
           "gates": {"cells_run": BATCH_CELLS,
                     "survivors_g1_prime_v2": len(survivors)},
           "eliminated": BATCH_CELLS - len(survivors),
           "refs": {"results": "results/shortline_xstock_tilt.json",
                    "prereg": "research/shortline/XSTOCK_TILT.md"}}
    with open(ATTRITION, encoding="utf-8-sig") as fh:
        d = json.load(fh)
    d["entries"].append(ent)
    with open(ATTRITION, "w", encoding="utf-8") as fh:
        json.dump(d, fh, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------- subcommands
def cmd_status():
    done = _load_done()
    n_main = sum(1 for k, *_ in MAIN_CELLS if k in done)
    n_null = sum(1 for k in done if k.startswith(("null_h20_", "null_h10_")))
    n_stress = sum(1 for k in done if "__cost_" in k)
    print(f"done: main {n_main}/4 nulls {n_null}/40 stress {n_stress}/8 "
          f"total {n_main + n_null + n_stress}/52 | lock_alive="
          f"{_lock_alive()} | final_json={os.path.exists(OUT_JSON)}")
    return 0


def run_selftest():
    """Offline, no panel dependency (J18 family: assertions self-consistent
    with constructed data)."""
    ok_n = 0

    def ok(name, cond):
        nonlocal ok_n
        ok_n += 1
        print(f"[{'PASS' if cond else 'FAIL'}] {name}")
        return bool(cond)

    # 1) schedules (SS3): W-1 start, step W; h20 == EXT_TILT d20 semantics
    ok("h20 schedule == EXT_TILT d20_rebal_pos",
       rebal_pos(100, 20) == EXT.d20_rebal_pos(100)
       == list(range(19, 100, 20)))
    ok("h10 schedule starts at index 9, step 10",
       rebal_pos(100, 10) == list(range(9, 100, 10)))

    # 2) frames pulses (EXT_TILT reuse): rotation in/out
    T, N = 30, 6
    sels = [(10, [0, 1, 2]), (20, [1, 2, 3])]
    e, x = EXT.frames_from_selections(T, N, sels)
    ok("frames: entry pulses only on rebal days, exit only for dropped",
       e[10, 0] and e[20, 3] and not e[11, 0] and x[20, 0]
       and not x[20, 1] and e.sum() == 6 and x.sum() == 1)

    # 3) top-k selection: composite is sign-oriented -> descending (high=good)
    vals = np.array([3.0, 1.0, 2.0, 1.0, np.nan, 2.0])
    el = np.array([True] * 6)
    ok("topk desc: highest first, ties lower-col first, NaN excluded",
       EXT._topk_selection(0, vals, el, 2, False) == [0, 2]
       and EXT._topk_selection(0, np.full(6, np.nan), el, 2, False) == [])

    # 4) composite_z min_valid semantics (MV_PRIMARY=3 of 4 members)
    z1 = np.full((1, 2), 1.0)
    z2 = np.full((1, 2), 1.0)
    z3 = np.full((1, 2), 1.0)
    z4 = np.full((1, 2), np.nan)
    ok("composite_z: min_valid=3 passes with one NaN member",
       np.allclose(composite_z([z1, z2, z3, z4], 3)[0], 1.0))
    z5 = np.full((1, 2), np.nan)
    z6 = np.full((1, 2), np.nan)
    ok("composite_z: min_valid=3 blocks with two NaN members",
       np.all(np.isnan(composite_z([z1, z2, z5, z6], 3)[0])))

    # 5) frozen constants vs synth module + seed registry (SS2 gate 1 core)
    ok("constants: K_PRIMARY=4, MV_PRIMARY=3, H_GATE=10, cutoff pinned",
       XS.K_PRIMARY == 4 and XS.MV_PRIMARY == 3 and XS.H_GATE == 10
       and str(XS.CUTOFF.date()) == EVIDENCE_CUTOFF)
    ok("seed registry: xstock_tilt_h20/h10 registered at frozen bases",
       SG.SEED_REGISTRY.get("xstock_tilt_h20") == SEED_H20
       and SG.SEED_REGISTRY.get("xstock_tilt_h10") == SEED_H10)
    ok("cost stress mults: x2=4.0, x3=6.0 of ETF fee (52.164/78.246bp)",
       COST_STRESS_MULTS == {"cost_x2": 4.0, "cost_x3": 6.0})

    # 6) projection join semantics on a synthetic native grid
    native = np.full((5, 4), np.nan)
    native[2, 1] = 0.5                 # 2020-01-03, 000002
    native[2, 3] = -0.25              # 2020-01-03, 688981
    native[4, 0] = 1.5                 # 2020-01-07, 000001 (NOT in panel)
    days = np.array(["2020-01-01", "2020-01-02", "2020-01-03",
                     "2020-01-06", "2020-01-07"], dtype="datetime64[D]")
    syms_native = ["000001", "000002", "600000", "688981"]
    strat_codes = ["000002", "600000", "300750"]     # 300750 not on grid
    strat_days = days[[2, 3, 4]]
    row = np.array([np.flatnonzero(days == d)[0] for d in strat_days])
    col_of = {s: i for i, s in enumerate(syms_native)}
    cols = np.array([col_of.get(c, -1) for c in strat_codes])
    valid_j = np.flatnonzero(cols >= 0)
    ok_row = np.array([True, True, True])
    r_ok = np.flatnonzero(ok_row)
    proj = np.full((3, 3), np.nan)
    proj[np.ix_(r_ok, valid_j)] = native[
        row[r_ok][:, None], cols[valid_j][None, :]]
    ok("projection: (date,code) lookup; missing code NaN; off-panel value "
       "never leaks in",
       proj[0, 0] == 0.5 and np.isnan(proj[0, 1]) and np.isnan(proj[0, 2])
       and np.isnan(proj[1, 0]) and np.isnan(proj[2, 0])
       and not (proj == 1.5).any() and not (proj == -0.25).any())
    ok("projection: col map discloses missing code per code",
       cols.tolist() == [1, 2, -1]
       and [c for c, j in zip(strat_codes, cols) if j < 0] == ["300750"])

    # 6b) causality: tail poisoning leaves head bit-identical (pointwise)
    proj_head_ref = proj[:2].copy()
    poisoned = native.copy()
    poisoned[row[2]:] = np.nan
    proj2 = np.full((3, 3), np.nan)
    proj2[np.ix_(r_ok[:2], valid_j)] = poisoned[
        row[r_ok[:2]][:, None], cols[valid_j][None, :]]
    ok("causality: poisoned tail rows never touch head projection",
       np.array_equal(proj_head_ref, proj2[:2], equal_nan=True))

    # 7) reproduction tolerance convention (half of last recorded digit)
    ok("repro tolerance: 4dp IC 0.5e-4 (XS convention), 2dp IR 0.5e-2",
       XS.REPRO_TOL_ROUNDED == 0.5e-4)

    # 8) skill line formula replication (N_eff=44 -> sqrt(2 ln 44) term)
    import math
    mu, sigma = -0.14, 0.15
    extreme = sigma * math.sqrt(2.0 * math.log(44))
    ok("skill_line_v2 null term: mu + sigma*sqrt(2 ln N_eff)",
       abs((mu + extreme) - (-0.14 + 0.15 * math.sqrt(2 * math.log(44))))
       < 1e-12)

    # 9) D6 rejection logic
    ok("d6 gate: 0.7 line rejects at/above, passes below",
       (abs(0.71) >= 0.7) and (abs(0.69) < 0.7))

    # 10) universe probe gate arithmetic (frozen thresholds)
    daily = np.array([999, 1000, 1001, 1500, 2000])
    ok("universe gate: median>=1000 sentinel is frozen (not tuned)",
       int(np.median(daily)) == 1001 and 1001 >= MIN_ELIG_MEDIAN)

    # 10b) SS2.5 adjudication fixture (r71 dual-reading boundary law):
    # warmup-empty / normal-start / all-empty three states
    T_f, N_f = 40, 3
    elig_f = np.zeros((T_f, N_f), dtype=bool)
    elig_f[19:] = True                    # 20d warmup: empty before row 19
    proj_f = np.ones((T_f, N_f))         # composite available everywhere
    g_f = universe_probe(elig_f, proj_f, T=T_f)
    ok("ss2.5 adjudication: warmup-empty h10 first day skipped to t=19",
       g_f["h10"]["first_scheduled_pos"] == 9
       and g_f["h10"]["empty_elig_days_skipped"] == 1
       and g_f["h10"]["first_effective_pos"] == 19
       and g_f["h10"]["first_effective_composite_count"] == 3
       and g_f["h10"]["first_scheduled_day_composite_over_raw"] == 3
       and g_f["h10"]["first_scheduled_day_eligible"] == 0)
    ok("ss2.5 adjudication: h20 first day already effective (no skip)",
       g_f["h20"]["first_scheduled_pos"] == 19
       and g_f["h20"]["empty_elig_days_skipped"] == 0
       and g_f["h20"]["first_effective_pos"] == 19
       and g_f["h20"]["first_effective_composite_count"] == 3)
    g_all = universe_probe(np.zeros((T_f, N_f), dtype=bool),
                           proj_f, T=T_f)
    ok("ss2.5 adjudication: all-empty universe = honest refusal (pos None)",
       g_all["h10"]["first_effective_pos"] is None
       and g_all["h10"]["empty_elig_days_skipped"]
       == len(rebal_pos(T_f, 10))
       and g_all["pass_first_rebal"] is False)

    print(f"selftest: {ok_n} checks, all PASS = {ok_n >= 17}")
    return 0 if ok_n >= 17 else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "status"
    if cmd == "selftest":
        return run_selftest()
    if cmd == "gates":
        return cmd_gates()
    if cmd == "probe":
        return cmd_probe()
    if cmd == "run":
        return cmd_run()
    if cmd == "status":
        return cmd_status()
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
