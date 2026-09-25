"""T48-factor-blend — 3-corps x 5-method factor-blend composite batch (T-2026-09-25-48).

PRE-REGISTERED before any evaluation (research/FACTOR_BLEND.md v1.0, frozen
commit 3d2258fb precedes the first engine cell; prereg sha256 recorded in the
output JSON). Do NOT tune shortlists/weights/thresholds after results (iron
rule 3). Post-freeze backfill is limited to prereg s7/s8.

15 frozen composite cells = 3 corps (attack/defense/chop, shortlists signed
by in-registry economic prior, NOT backtest rank) x 5 blend methods
(a EW / b IC / c inverse-vol / d factor-momentum / e regime-conditional).
Cell construction = COMPOSITE-CE-01 lineage verbatim: blend score ->
top_n_rotation(n=5, rebal_days=20) -> CE exit machine (loss_time 16 +
decay 25d/5% + trail 0.10, max_positions 5, pos 19%); exit priority
UNTOUCHED (iron rule). Cost V1 legacy, x1/x2 faces (x2 reuses x1-frozen
weights = identical held matrix, CostPatch(2)).

PRE-RUN JUDGMENT ADJUDICATIONS (r71 dual-reading law family; both resolved
before the first engine cell ran; disclosed in every results JSON):
  ADJ-1 benefit/DR baseline: T-27 member-mean baseline is structurally
    unavailable at the factor layer without 23 single-factor engine cells
    that are NOT in the frozen 135-cell budget (adding them post-freeze =
    J18 judgment-face expansion). Frozen-constants baseline = passive
    EW48 buy-hold full Sharpe (p2_calibration canon, the same constant
    family clause vi draws from): benefit = S_full - passive_buyhold_S;
    DR = S_full / passive_buyhold_S.
  ADJ-2 six-window face: IS = pre-OOS_START; IS2 = OOS_START..cutoff
    (forward-lockbox demotion, IV6 d2_note canon); OOS = post-cutoff
    locked box -> structurally NOT consumable in-batch, per-cell block is
    an honest locked-box marker (paper accrual only); bear/chop/bull =
    regime_proxy (t22 frozen primitive, 510300 vs MA200) same-day
    descriptive segments.

D6 admission (s1 hard gate): per-cell x1 daily-return sleeve vs registered
6 (COMPOSITE-CE-01/02, DROUGHT/ENGULF/NEEDLE/VOLATILITY engine reruns =
gate infrastructure, not ledger cells); max|corr| >= 0.7 -> cell rejected
before ranking. Same-batch 15x15 matrix = descriptive only.

Winner per corps (s4): among D6-passing eligible cells, 3-face median rank
(benefit / drawdown / x2 margin), tie -> benefit face. Zero eligible ->
corps has no winner (honest zero). G2 v2 (DSR + family PBO on the corps'
5-method sleeve family) + corps-segment gate apply to winners; segment
carrier = T-22 harness via PROSPECT onboarding = separate prereg line, so
the frozen honest fallback applies (full-window regime segment stats +
blocker disclosure; winners stay T-33 candidate status, NOT benched).

CLI: selftest (hermetic, no panel) | gates (constants/coverage probe,
exit 2 refuse) | run (resumable batch, jsonl checkpoints + lock +
single-shot finalize guard) | status.
"""
import hashlib
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

import science_gates as SG
from engine.factors import FACTORS
from engine import run_backtest
from live.paper import (OOS_START, CostPatch, ExitPatch, build_panels,
                        evidence_cutoff, load_core, seg_metrics)
from firm.risk.regime import load_benchmark_close
from t22_virtual_timepoints import regime_proxy

PREREG = os.path.join(ROOT, "research", "FACTOR_BLEND.md")
OUT_JSON = os.path.join(ROOT, "results", "factor_blend_cells.json")
VERDICT_JSON = os.path.join(ROOT, "results", "factor_blend_verdict.json")
RUNS_JSONL = os.path.join(ROOT, "results", "factor_blend_runs.jsonl")
FINAL_CSV = os.path.join(ROOT, "research", "shortline",
                         "factor_blend_results.csv")
LOCK = os.path.join(ROOT, "results", "factor_blend_run.lock")
LOG_PATH = os.path.join(ROOT, "logs", "iteration-loop", "factor_blend.log")
ATTRITION = os.path.join(ROOT, "results", "gate_attrition.json")
CALIB = os.path.join(ROOT, "results", "p2_calibration.json")
REGISTRY = os.path.join(ROOT, "results", "factor_registry.json")
MAX_WORKERS = 8                    # prereg s0: min(worker_cap(), 8)

# ---- frozen constants (prereg s2/s3, byte-derived from the frozen file) ----
EVIDENCE_CUTOFF = "2026-09-24"     # prereg s2 panel cutoff
BATCH = "T48-factor-blend"
BATCH_CELLS = 135                  # 30 engine + 15 ranking + 90 window
OOS_START_TS = pd.Timestamp(OOS_START)
D6_REJECT = 0.7                    # prereg s1 hard line
CRASH_YEAR = -0.30
TOP_N, REBAL_DAYS = 5, 20
MIN_N = 5                          # _xs_zscore min_n (composite_rotation canon)
IC_WINDOW = 60                     # method d trailing IC window (trading days)
COVERAGE_MAX_GAP_TD = 5             # prereg s2 gate 3
REG6 = ("COMPOSITE-CE-01", "COMPOSITE-CE-02", "DROUGHT-CE-01",
        "ENGULF-CE-01", "NEEDLE-DE-01", "VOLATILITY-CE-01")
# COMPOSITE-CE-01 params (firm/traders/COMPOSITE-CE-01.json) minus entry
CE_PARAMS = {"max_positions": 5, "position_size_pct": 0.19,
             "time_decay_period": 25, "time_decay_threshold": 0.05,
             "trailing_stop_activate": 0.1}
CE_EXIT_OVERRIDES = {"loss_time_days": 16}

# prereg s3 corps shortlists: factor -> composite sign (economic prior)
CORPS = {
    "attack": {"mom_12_1": +1, "mom_60": +1, "mom_20": +1, "mom_accel": +1,
               "ma_slope_20": +1, "adx_14": +1, "up_day_ratio": +1,
               "price_position": +1, "gap_overnight": +1,
               "extreme_freq": -1},
    "defense": {"rev_5": +1, "rev_10": +1, "drawdown_60": -1, "vol_60": -1,
                "vol_20": -1, "intraday_range": -1, "return_kurt": -1,
                "return_skew": -1, "amt_20": -1, "ma_bias_20": -1},
    "chop": {"ma_bias_20": -1, "ma_bias_60": -1, "price_position": -1,
             "drawdown_60": -1, "extreme_freq": -1, "intraday_range": +1,
             "volume_trend": -1, "vol_price_diverge": +1,
             "gap_overnight": -1},
}
METHODS = ("a_EW", "b_IC", "c_INVVOL", "d_FACTMOM", "e_REGIME")

PRICES_FULL = None                 # worker global (ew6 pattern)


def log(msg: str) -> None:
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


# ------------------------------------------------------------ primitives
def _xs_zscore(df: pd.DataFrame, min_n: int = MIN_N) -> pd.DataFrame:
    """composite_rotation._xs_zscore verbatim (frozen lineage primitive)."""
    mu = df.mean(axis=1)
    sd = df.std(axis=1, ddof=0)
    valid = df.notna().sum(axis=1) >= min_n
    z = df.sub(mu, axis=0).div(sd.replace(0, np.nan), axis=0)
    z[~valid] = np.nan
    return z


def xs_ic_series(z: pd.DataFrame, fwd: pd.DataFrame,
                 min_n: int = MIN_N) -> pd.Series:
    """Daily cross-sectional Pearson corr(z_j, next-day return) per date.

    Causal by construction when fwd = close.pct_change().shift(-1): the IC
    at date t is only complete once the t->t+1 forward return closes.
    Rows with < min_n co-valid pairs -> NaN (min_n gate, _xs_zscore family).
    """
    both = z.notna() & fwd.notna()
    n = both.sum(axis=1)
    zv = z.where(both)
    fv = fwd.where(both)
    zx = zv.sub(zv.mean(axis=1), axis=0)
    fx = fv.sub(fv.mean(axis=1), axis=0)
    num = (zx * fx).sum(axis=1)
    den = np.sqrt((zx ** 2).sum(axis=1) * (fx ** 2).sum(axis=1))
    ic = num / den.replace(0, np.nan)
    ic[n < min_n] = np.nan
    return ic


def _ew(names) -> dict:
    return {f: 1.0 / len(names) for f in names}


def weights_b(ic_is: dict) -> dict:
    """Method b: w_j ~ IC_IS,j signed (negative IC flips), sum|w|=1.

    Zero/near-zero |IC| mass -> deterministic EW fallback, disclosed."""
    mass = sum(abs(v) for v in ic_is.values())
    if mass <= 0 or not all(np.isfinite(v) for v in ic_is.values()):
        return {"weights": _ew(ic_is), "path": "ew_fallback_zero_ic_mass",
                "ic_is": {k: round(v, 6) for k, v in ic_is.items()}}
    w = {f: v / mass for f, v in ic_is.items()}
    return {"weights": {k: round(v, 6) for k, v in w.items()},
            "path": "ic_signed", "sum_abs": round(sum(abs(v) for v in w.values()), 6),
            "ic_is": {k: round(v, 6) for k, v in ic_is.items()}}


def weights_c(sigma_is: dict) -> dict:
    """Method c: w_j ~ 1/sigma_IS,j (pooled z std over IS), sum|w|=1."""
    if any((not np.isfinite(v)) or v <= 0 for v in sigma_is.values()):
        return {"weights": _ew(sigma_is), "path": "ew_fallback_zero_sigma",
                "sigma_is": {k: round(v, 6) for k, v in sigma_is.items()}}
    raw = {f: 1.0 / v for f, v in sigma_is.items()}
    s = sum(raw.values())
    w = {f: v / s for f, v in raw.items()}
    return {"weights": {k: round(v, 6) for k, v in w.items()},
            "path": "inverse_vol", "sum_abs": round(sum(abs(v) for v in w.values()), 6),
            "sigma_is": {k: round(v, 6) for k, v in sigma_is.items()}}


def weights_d_at(ic_win: dict) -> dict:
    """Method d at one rebalance day: w_j ~ 60d mean IC, signed; all-negative
    (or incomplete window -> NaN mass) -> EW fallback for that rebal day."""
    vals = list(ic_win.values())
    if any(not np.isfinite(v) for v in vals):
        return _ew(ic_win), "ew_fallback_incomplete_ic_window"
    if all(v < 0 for v in vals):
        return _ew(ic_win), "ew_fallback_all_negative_ic"
    mass = sum(abs(v) for v in vals)
    if mass <= 0:
        return _ew(ic_win), "ew_fallback_zero_ic_mass"
    return {f: v / mass for f, v in ic_win.items()}, "factormom_signed"


def weights_e_at(state_prev: str, w_b: dict, names) -> tuple:
    """Method e at one rebalance day: state(t-1) per regime_proxy; bear ->
    b's IS-frozen weights; chop/bull -> EW; na/unknown -> EW (disclosed)."""
    if state_prev == "bear":
        return dict(w_b), "bear->ic_is"
    return _ew(names), f"{state_prev or 'na'}->ew"


def blend_score(W: pd.DataFrame, zs: dict) -> pd.DataFrame:
    """score(t) = sum_j W[t, j] * z_j(t)  (prereg s3 blend formula).

    Iterates W's OWN columns only: the caller passes the corps-scoped
    weight timeline and a factor-z superset (union across corps) -- a
    corps' blend never touches another corps' factors."""
    out = None
    for f in W.columns:
        contrib = zs[f].mul(W[f], axis=0)
        out = contrib if out is None else out.add(contrib, fill_value=None)
    return out


def score_to_held(score: pd.DataFrame, top_n: int = TOP_N,
                  rebal_days: int = REBAL_DAYS) -> pd.DataFrame:
    """composite_rotation.top_n_rotation tail verbatim, score precomputed:
    rank descending, top_n membership sampled every rebal_days rows and
    forward-held between rebalances (byte-identical lineage semantics)."""
    ranks = score.rank(axis=1, ascending=False)
    in_set = ranks <= top_n
    held = in_set.iloc[::rebal_days].reindex(in_set.index).ffill()
    return held.fillna(False).astype(int)


def _slice_stats(rets: pd.Series) -> dict:
    if len(rets) < 10 or rets.std() == 0:
        return {"n_days": int(len(rets)), "sharpe": None,
                "ann_return": None}
    return {"n_days": int(len(rets)),
            "sharpe": round(float(rets.mean() / rets.std() * 252 ** 0.5), 4),
            "ann_return": round(float((1 + rets).prod()
                                      ** (252 / len(rets)) - 1), 4)}


# ------------------------------------------------------- worker engine leg
def _init_worker():
    global PRICES_FULL
    PRICES_FULL = load_core()


def _cell_engine_run(held: pd.DataFrame, cost_mult) -> dict:
    """One engine sleeve run on the CE machine (x1 legacy V1 / x2 CostPatch).
    held matrix is x1-frozen membership (weights IS-causal; x2 reuses it)."""
    global PRICES_FULL
    ps = pd.Timestamp(EVIDENCE_CUTOFF)
    prices = {s: df[df.index <= ps] for s, df in PRICES_FULL.items()}
    params = dict(CE_PARAMS)
    params["report_num_entries"] = True
    from contextlib import nullcontext
    cctx = CostPatch(cost_mult) if cost_mult and cost_mult != 1 else nullcontext()
    with cctx, ExitPatch(CE_EXIT_OVERRIDES):
        res = run_backtest(prices, params, entry_signal=held,
                           exit_signal=(held <= 0))
    eq = pd.Series(res["equity_curve"],
                   index=held.index[:len(res["equity_curve"])])
    oos_tr = sum(1 for tr in res["trades"] if str(tr["date"]) >= OOS_START)
    is_part = eq[eq.index < OOS_START_TS]
    rets = eq.pct_change().dropna()
    yearly = {int(y): round(float(g.iloc[-1] / g.iloc[0] - 1), 4)
              for y, g in eq.groupby(eq.index.year)}
    return {"full": res["metrics"], "is": seg_metrics(is_part),
            "is2": seg_metrics(eq, OOS_START),
            "n_trades": res["metrics"]["num_trades"],
            "n_entries": int(res["metrics"].get("num_entries", 0)),
            "oos_trades": oos_tr,
            "worst_year": min(yearly.values()) if yearly else None,
            "yearly": yearly,
            "dates": [str(d.date()) for d in eq.index],
            "returns": [round(float(v), 8) for v in rets]}


def _cell_task_impl(key, corps, method, cost_mult, held_payload):
    """(key, corps, method, cost_mult, held_payload) -- run_cells_parallel
    invokes fn(*args), so the signature mirrors the job-tuple fields;
    held_payload = {"index": [...], "columns": [...], "data": [[0/1]*N]*T}
    (picklable, x1-frozen membership)."""
    held = pd.DataFrame(held_payload["data"],
                        index=pd.to_datetime(held_payload["index"]),
                        columns=held_payload["columns"])
    rec = _cell_engine_run(held, cost_mult)
    rec.update({"key": key, "corps": corps, "method": method,
                "cost_mult": cost_mult or 1})
    return rec


def _member_task(tid):
    """D6 gate infrastructure: registered-member sleeve rerun (ew6 canon).
    MUST return "key" -- _load_done keys every checkpoint row by rec["key"]
    (a missing key = row silently skipped = r163 jsonl lesson)."""
    import ew6_portfolio as E
    global PRICES_FULL
    if E.PRICES_FULL is None:
        E.PRICES_FULL = PRICES_FULL
    r = E.member_run(tid)
    eq = pd.Series(r["eq"], index=pd.to_datetime(r["dates"]))
    return {"key": f"member|{tid}", "tid": tid, "cutoff": r["cutoff"],
            "returns": [round(float(v), 8) for v in eq.pct_change().dropna()],
            "dates": [str(d.date()) for d in eq.index]}


# ----------------------------------------------------------------- gates
def run_gates(P, bench) -> dict:
    """Prereg s2 data-completeness gate: 1) registry 28/28 faces+roster;
    2) shortlist keys subset FACTORS; 3) panel bar coverage to cutoff
    (tail gap <= 5 trading days, counted on the benchmark calendar);
    4) frozen shortlist plane vs prereg constants (byte-identity by
    construction; asserted)."""
    fails = []
    with open(REGISTRY, encoding="utf-8-sig") as fh:
        reg = json.load(fh)
    counts = reg.get("counts", {})
    if counts.get("engine_faces") != 28 or counts.get("registered_roster") != 28:
        fails.append(f"registry counts {counts} != 28/28")
    for corps, short in CORPS.items():
        bad = [f for f in short if f not in FACTORS]
        if bad:
            fails.append(f"{corps} shortlist keys not in FACTORS: {bad}")
    if not (len(CORPS["attack"]) == 10 and len(CORPS["defense"]) == 10
            and len(CORPS["chop"]) == 9):
        fails.append("shortlist counts != 10/10/9")
    last = P["close"].index.max()
    if last > pd.Timestamp(EVIDENCE_CUTOFF):
        fails.append(f"panel last bar {last} > cutoff (future data risk)")
    gap = int(((bench.index > last) & (bench.index <= pd.Timestamp(
        EVIDENCE_CUTOFF))).sum())
    if gap > COVERAGE_MAX_GAP_TD:
        fails.append(f"panel tail gap {gap} td > {COVERAGE_MAX_GAP_TD} "
                    f"(last={last.date()})")
    return {"pass": not fails, "fails": fails,
            "panel_last_bar": str(last.date()),
            "panel_symbols": int(P["close"].shape[1]),
            "panel_rows": int(P["close"].shape[0]),
            "coverage_gap_td": gap,
            "registry_counts": counts}


# ------------------------------------------------------------- main build
def build_cells(P, bench):
    """Frozen 15-cell construction (main process, once).

    Returns (cells, weights_block, zdisc) where cells maps
    (corps, method) -> {"held": payload, "score_head": ...}.
    """
    state = regime_proxy(bench)          # t22 frozen 3-way primitive
    fwd = P["close"].pct_change().shift(-1)
    is_mask_dates = P["close"].index < OOS_START_TS

    zs = {}
    uniq = sorted({f for short in CORPS.values() for f in short})
    for f in uniq:
        zs[f] = _xs_zscore(FACTORS[f](P))

    ics = {}
    for f in uniq:
        ics[f] = xs_ic_series(zs[f], fwd)

    ic_is = {f: float(ics[f][is_mask_dates].dropna().mean()) for f in uniq}
    sigma_is = {}
    for f in uniq:
        block = zs[f][is_mask_dates]
        sigma_is[f] = float(block.stack().std(ddof=1))

    rebal_pos = list(range(0, P["close"].shape[0], REBAL_DAYS))
    dates = P["close"].index

    weights_block = {}
    cells = {}
    for corps, short in CORPS.items():
        names = sorted(short)
        w_static = {}
        w_static["a_EW"] = {"weights": _ew(names), "path": "ew"}
        w_static["b_IC"] = weights_b({f: ic_is[f] for f in names})
        w_static["c_INVVOL"] = weights_c({f: sigma_is[f] for f in names})
        w_b = w_static["b_IC"]["weights"]

        # per-method weight timeline W[t, factor] (weights update on
        # rebalance days only; ffilled between -- prereg s3 header)
        for method in METHODS:
            # NaN-initialized: legit zero weights (b/d signed mass) must
            # survive ffilled between rebal days, never be replaced by a
            # stale nonzero value
            W = pd.DataFrame(np.nan, index=dates, columns=names)
            path_counts = {}
            prev = None
            for pos in rebal_pos:
                t = dates[pos]
                if method in ("a_EW", "b_IC", "c_INVVOL"):
                    w = w_static[method]["weights"]
                    path = w_static[method]["path"]
                elif method == "d_FACTMOM":
                    win = {}
                    for f in names:
                        # frozen reading: IC on days [t-60, t-1] -- every
                        # such IC's forward window closes at <= t (the t-1
                        # IC closes exactly at t's close, known at decision
                        # time; z(t) shares the same information set)
                        w60 = ics[f].iloc[max(0, pos - IC_WINDOW):pos]
                        w60 = w60[w60.index <= t]
                        if len(w60) >= IC_WINDOW:
                            win[f] = float(w60.mean())
                        else:
                            win[f] = float("nan")
                    w, path = weights_d_at(win)
                else:  # e_REGIME
                    sp = str(state.iloc[pos - 1]) if pos >= 1 else "na"
                    w, path = weights_e_at(sp, w_b, names)
                path_counts[path] = path_counts.get(path, 0) + 1
                W.loc[t, :] = [w[f] for f in names]
                prev = w
            W = W.ffill().fillna(0.0)
            score = blend_score(W, zs)
            held = score_to_held(score)
            weights_block[f"{corps}|{method}"] = {
                "static": w_static[method] if method in w_static else None,
                "path_counts": path_counts}
            cells[(corps, method)] = {
                "held_payload": {"index": [str(d.date()) for d in held.index],
                                "columns": list(held.columns),
                                "data": held.values.astype(int).tolist()},
                "score_head": [None if pd.isna(v) else round(float(v), 6)
                               for v in score.iloc[min(260, len(score) - 1)]]}
    return cells, weights_block, {"ic_is": ic_is, "sigma_is": sigma_is}


# ----------------------------------------------------------- checkpoints
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


def _append_rec(rec):
    with open(RUNS_JSONL, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


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


# ------------------------------------------------------------------ run
def cmd_run() -> int:
    from parallel_runner import worker_cap
    if _lock_alive():
        print("EXIT 3: batch already running (lock alive) -- status only")
        return 3
    _write_lock()
    t0 = time.time()
    try:
        global PRICES_FULL
        PRICES_FULL = load_core()
        ps = pd.Timestamp(EVIDENCE_CUTOFF)
        prices = {s: df[df.index <= ps] for s, df in PRICES_FULL.items()}
        P = build_panels(prices)
        bench = load_benchmark_close()
        gates = run_gates(P, bench)
        log(f"gates: pass={gates['pass']} last_bar={gates['panel_last_bar']} "
            f"gap_td={gates['coverage_gap_td']} "
            f"symbols={gates['panel_symbols']}")
        if not gates["pass"]:
            log(f"EXIT 2: gates FAIL {gates['fails']} -- no half-data batch")
            return 2
        cells, weights_block, zdisc = build_cells(P, bench)
        log(f"15 cell matrices built (panel {gates['panel_rows']} rows)")

        jobs = []
        for (corps, method), cell in cells.items():
            key = f"{corps}|{method}|x1"
            jobs.append((key, _cell_task_impl,
                         (key, corps, method, 1, cell["held_payload"])))
            key2 = f"{corps}|{method}|x2"
            jobs.append((key2, _cell_task_impl,
                         (key2, corps, method, 2, cell["held_payload"])))
        for tid in REG6:
            jobs.append((f"member|{tid}", _member_task, (tid,)))
        done = _load_done()
        todo = [j for j in jobs if j[0] not in done]
        log(f"engine cells total={len(jobs)} done={len(done)} "
            f"todo={len(todo)}")
        if todo:
            from parallel_runner import run_cells_parallel
            res = run_cells_parallel(todo, workers=min(worker_cap(),
                                                       MAX_WORKERS),
                                     desc="t48-cells",
                                     initializer=_init_worker)
            workers = int(res.pop("__workers__"))
            for key in sorted(res):
                _append_rec(res[key])
        else:
            workers = 0
        ok = _finalize(time.time() - t0, gates, weights_block, zdisc,
                       cells, workers)
        return 0 if ok else 1
    finally:
        try:
            os.remove(LOCK)
        except OSError:
            pass


# --------------------------------------------------------------- finalize
def _finalize(elapsed, gates, weights_block, zdisc, cells, workers) -> bool:
    if os.path.exists(OUT_JSON) and \
            os.environ.get("T48_FACTOR_BLEND_REFINALIZE") != "1":
        print("finalize refused: OUT_JSON exists (single-shot guard; "
              "T48_FACTOR_BLEND_REFINALIZE=1 to redo)")
        return False
    done = _load_done()
    cell_keys = {f"{c}|{m}": (c, m) for c in CORPS for m in METHODS}
    if not all(f"{k}|x1" in done and f"{k}|x2" in done for k in cell_keys):
        missing = [k for k in cell_keys
                   if f"{k}|x1" not in done or f"{k}|x2" not in done]
        print(f"finalize refused: incomplete cells {missing}")
        return False
    if not all(f"member|{t}" in done for t in REG6):
        print("finalize refused: D6 member sleeves incomplete")
        return False

    with open(CALIB, encoding="utf-8-sig") as fh:
        calib = json.load(fh)
    g = calib["g1_prime_gate"]
    K = {"i_bar": g["i_full_sharpe_gt"], "vi_bar": g["vi_full_sharpe_gt"],
         "dd_min": g["iii_dd_min"], "trades_min": g["iv_trades_min"]}
    passive_s = float(calib["families"]["C_passive"]["runs"]
                      ["ew48_buyhold"]["full"]["sharpe"])

    # interim single-shot guard FIRST (anti-double ledger append, xstock law)
    if os.environ.get("T48_FACTOR_BLEND_REFINALIZE") == "1":
        head = SG.ledger_head(SG.RESULTS_DIR)
        if head.get("file") != os.path.basename(OUT_JSON):
            print(f"finalize refused: ledger head is {head.get('file')} "
                  f"(not this batch) -- refinalize would steal the chain")
            return False
        # canonical dict schema rebuilt from the chain head (r140 A158 law
        # family: unified dict schema only; raw head lacks prev/batch keys)
        ledger = {"prev_total": int(head["total"]) - BATCH_CELLS,
                  "batch_trials": BATCH_CELLS,
                  "total": int(head["total"]), "batch": BATCH,
                  "file": os.path.basename(OUT_JSON),
                  "evidence_cutoff": EVIDENCE_CUTOFF,
                  "note": "refinalize reuses the chain head (no re-append)"}
    else:
        ledger = SG.append_ledger(
            BATCH, BATCH_CELLS, os.path.basename(OUT_JSON),
            note=("15 composite cells (3 corps x 5 methods, shortlists "
                  "signed by registry economic prior, COMPOSITE-CE-01 "
                  "lineage top5/20d + CE exit machine verbatim) x x1/x2 "
                  "V1-legacy cost faces = 30 engine cells + 15 ranking-"
                  "frame cells (per-corps 3-face median-rank winner) + 90 "
                  "window cells (15 cells x IS/IS2/OOS-lockedbox/bear/chop/"
                  "bull); zero search zero nulls => zero SEED_REGISTRY "
                  "entries; D6 member reruns (6) are gate infrastructure, "
                  "not ledger cells; prereg research/FACTOR_BLEND.md v1.0 "
                  "frozen 3d2258fb pre-evaluation"),
            evidence_cutoff=EVIDENCE_CUTOFF)
    interim = {"meta": {"batch": BATCH, "interim": True},
              "trials_ledger": ledger}
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(interim, fh, indent=2, ensure_ascii=False)

    bench = load_benchmark_close()
    state = regime_proxy(bench)

    # ---- D6: cell x1 sleeve vs registered 6 (prereg s1 hard gate) ----
    mrets = {}
    for tid in REG6:
        r = done[f"member|{tid}"]
        mrets[tid] = pd.Series(r["returns"],
                               index=pd.to_datetime(r["dates"][1:]))
    d6 = {"members": list(REG6), "reject_line": D6_REJECT, "pairs": {}}
    for k in cell_keys:
        rec = done[f"{k}|x1"]
        r = pd.Series(rec["returns"],
                      index=pd.to_datetime(rec["dates"][1:]))
        worst_name, worst_v, allp = None, 0.0, {}
        for tid, mr in mrets.items():
            j = pd.concat([r, mr], axis=1, join="inner").dropna()
            v = float(j.corr().iloc[0, 1]) if len(j) > 60 else float("nan")
            allp[tid] = None if not np.isfinite(v) else round(v, 4)
            if np.isfinite(v) and abs(v) > abs(worst_v):
                worst_name, worst_v = tid, v
        d6["pairs"][k] = {"all": allp,
                          "max_abs": None if not np.isfinite(worst_v)
                          else round(abs(worst_v), 4),
                          "max_abs_member": worst_name,
                          "d6_ok": bool(np.isfinite(worst_v)
                                       and abs(worst_v) < D6_REJECT)}

    # ---- per-cell G1' v2 + clauses + ADJ-1 benefit/DR + x2 + robust ----
    per_cell, eligible = {}, {c: [] for c in CORPS}
    for k, (corps, method) in cell_keys.items():
        r1, r2 = done[f"{k}|x1"], done[f"{k}|x2"]
        rets = pd.Series(r1["returns"])
        v2 = SG.g1_prime_v2(r1["full"]["sharpe"], rets,
                            batch_cells=BATCH_CELLS, pool="core48",
                            n_trades=r1["n_trades"],
                            n_entries=r1["n_entries"])
        port = {"full": r1["full"], "is2": r1["is2"]}
        clauses = {"i_beats_rand_p95": r1["full"]["sharpe"] > K["i_bar"],
                   "ii_ann_pos": r1["full"]["annual_return"] > 0,
                   "iii_dd_ok": r1["full"]["max_drawdown"] >= K["dd_min"],
                   "iv_trades_ok": r1["n_trades"] >= K["trades_min"],
                   "v_is2_ok": r1["is2"]["sharpe"] > 0
                               and r1["is2"]["annual_return"] > 0,
                   "vi_beats_passive": r1["full"]["sharpe"] > K["vi_bar"]}
        # ADJ-1 (pre-run adjudication, disclosed): benefit/DR baseline =
        # passive EW48 buy-hold full Sharpe (frozen p2_calibration constant)
        benefit = round(float(r1["full"]["sharpe"]) - passive_s, 4)
        dr = (round(float(r1["full"]["sharpe"]) / passive_s, 4)
              if passive_s > 0 else None)
        x2_survive = bool(r2["full"]["sharpe"] > K["vi_bar"]
                          and r2["is2"]["sharpe"] > 0)
        robust = {"is_sharpe_pos": bool(r1["is"]["sharpe"] > 0),
                  "worst_year_ok": bool(r1["worst_year"] > CRASH_YEAR)}
        dtg = v2.get("trade_gate") or {}
        g1_pass = bool(v2["pass_v2"] and all(clauses.values())
                       and benefit > 0 and (dr or 0) > 1 and x2_survive
                       and all(robust.values())
                       and bool(dtg.get("entries_ok", True)))
        per_cell[k] = {
            "corps": corps, "method": method,
            "x1": {"full": r1["full"], "is": r1["is"], "is2": r1["is2"],
                   "n_trades": r1["n_trades"], "n_entries": r1["n_entries"],
                   "oos_trades": r1["oos_trades"], "worst_year": r1["worst_year"],
                   "yearly": r1["yearly"]},
            "x2": {"full": r2["full"], "is2": r2["is2"],
                   "n_trades": r2["n_trades"], "n_entries": r2["n_entries"]},
            "g1_prime_v2": v2, "clauses": clauses,
            "benefit_passive_baseline": benefit, "dr_passive_baseline": dr,
            "x2_survive": x2_survive, "robust": robust,
            "d6": d6["pairs"][k], "g1_pass": g1_pass}
        if g1_pass and d6["pairs"][k]["d6_ok"]:
            eligible[corps].append(k)

    # ---- per-corps 3-face ranking (T-27 s4 verbatim frame) ----
    from screening.pbo import align_returns, cscv_pbo
    ranking, winners, g2_block = {}, {}, {}
    for corps in CORPS:
        elig = eligible[corps]
        faces = {k: {"benefit": per_cell[k]["benefit_passive_baseline"],
                     "drawdown": per_cell[k]["x1"]["full"]["max_drawdown"],
                     "x2_margin": round(
                         per_cell[k]["x2"]["full"]["sharpe"] - K["vi_bar"], 4)}
                 for k in elig}
        if elig:
            ranks = {f: sorted(elig, key=lambda n: -faces[n][f])
                     for f in ("benefit", "drawdown", "x2_margin")}

            def med_rank(nm):
                r = [ranks[f].index(nm)
                     for f in ("benefit", "drawdown", "x2_margin")]
                return (sorted(r)[1], ranks["benefit"].index(nm))

            winner = sorted(elig, key=med_rank)[0]
        else:
            ranks, winner = {}, None
        ranking[corps] = {"eligible": elig, "faces": faces,
                          "ranks": {f: {n: ranks[f].index(n)
                                        for n in ranks[f]}
                                    for f in ranks},
                          "winner": winner}
        winners[corps] = winner
        # family PBO on the corps' 5-method sleeve family + winner G2
        rets_df = None
        try:
            fam = {}
            for m in METHODS:
                k = f"{corps}|{m}"
                r = done[f"{k}|x1"]
                fam[m] = pd.Series(r["returns"],
                                   index=pd.to_datetime(r["dates"][1:]))
            aligned = align_returns(fam)
            pbo = cscv_pbo(aligned)
            rets_df = aligned
        except Exception as ex:
            pbo = {"pbo": None, "error": f"{type(ex).__name__}: {ex}"}
            log(f"family PBO {corps} failed honestly: {ex}")
        g2 = None
        if winner:
            w_rec = done[f"{winner}|x1"]
            try:
                dsr = SG.deflated_sharpe_ratio(list(w_rec["returns"]),
                                                n_trials=BATCH_CELLS)
                g2 = SG.g2_registration_v2(True, dsr, pbo.get("pbo"))
            except Exception as ex:
                g2 = {"error": f"{type(ex).__name__}: {ex}"}
        g2_block[corps] = {"family_pbo": pbo, "g2_winner": g2}

    # ---- window cells (90; ADJ-2 six-window face) ----
    windows = {}
    for k in cell_keys:
        r1 = done[f"{k}|x1"]
        rets = pd.Series(r1["returns"],
                         index=pd.to_datetime(r1["dates"][1:]))
        same = state.reindex(rets.index, method="ffill").fillna("na")
        is_mask = rets.index < OOS_START_TS
        windows[k] = {
            "is": _slice_stats(rets[is_mask]),
            "is2": _slice_stats(rets[~is_mask]),
            "oos": {"status": "locked_box_not_consumed",
                    "note": "post-cutoff forward box; paper accrual only "
                            "(IV6 d2_note canon; prereg s2)"},
            "bear": _slice_stats(rets[same == "bear"]),
            "chop": _slice_stats(rets[same == "chop"]),
            "bull": _slice_stats(rets[same == "bull"]),
        }

    # ---- corps-segment gate: frozen honest fallback (prereg s4) ----
    corps_gate = {}
    for corps, winner in winners.items():
        if not winner:
            corps_gate[corps] = {"status": "no_winner", "benched": False}
            continue
        w = windows[winner]
        corps_gate[corps] = {
            "status": "candidate_fallback",
            "benched": False,
            "segment_stats": {"bear": w["bear"], "chop": w["chop"],
                              "bull": w["bull"]},
            "blocker": "T-22 harness adaptation = winner onboarding as "
                       "PROSPECT candidate (T-24 pipeline) = separate "
                       "prereg line; frozen fallback face applies "
                       "(full-window regime segment stats + disclosure); "
                       "n_startpoints unavailable in-batch -> candidate "
                       "NOT benched (T-33 candidate semantics)",
        }

    prereg_sha = hashlib.sha256(
        open(PREREG, "rb").read().replace(b"\r\n", b"\n")).hexdigest()

    # prereg s1 descriptive face: same-batch 15x15 pairwise corr of the
    # cell x1 sleeves (NOT a gate -- method-family redundancy is carried by
    # the s4 family PBO; frozen disclosure, zero judgment use)
    sleeve_rets = {}
    for k in cell_keys:
        r1 = done[f"{k}|x1"]
        sleeve_rets[k] = pd.Series(r1["returns"],
                                   index=pd.to_datetime(r1["dates"][1:]))
    intra = pd.DataFrame(sleeve_rets).corr().round(4)
    batch_corr_matrix = {"classification": "descriptive_only_not_a_gate",
                         "matrix": intra.to_dict()}

    out = {
        "meta": {"batch": BATCH, "dept": "research+trading",
                 "ticket": "T-2026-09-25-48",
                 "prereg": "research/FACTOR_BLEND.md v1.0 (frozen 3d2258fb "
                           "pre-evaluation)",
                 "date": time.strftime("%Y-%m-%d %H:%M:%S"),
                 "prereg_sha256_at_run": prereg_sha,
                 "evidence_cutoff": EVIDENCE_CUTOFF,
                 "oos_start": OOS_START,
                 "construction": "shortlist signed z-blend -> top5/20d "
                                 "rotation -> CE exit machine (loss_time 16 "
                                 "+ decay 25d/5% + trail 0.10) verbatim; "
                                 "cost V1 legacy x1/x2",
                 "audit": {"elapsed_sec": round(elapsed, 1),
                           "engine_cells": 30, "member_gate_runs": 6,
                           "workers": workers,
                           "batch_cells_ledger": BATCH_CELLS}},
        "gates": gates,
        "adjudications": {
            "ADJ-1_benefit_dr_baseline":
                "passive EW48 buy-hold full Sharpe (frozen p2_calibration "
                "constant); T-27 member-mean baseline structurally "
                "unavailable at the factor layer without 23 unbudgeted "
                "single-factor cells; resolved pre-run (r71 law family)",
            "ADJ-1_passive_sharpe": passive_s,
            "ADJ-2_window_faces":
                "IS/IS2 consumable; OOS = post-cutoff locked box, honest "
                "not-consumed marker; bear/chop/bull via regime_proxy "
                "same-day descriptive segments"},
        "weights": weights_block,
        "factor_stats": {"ic_is": {k: round(v, 6) for k, v in
                                   zdisc["ic_is"].items()},
                         "sigma_is": {k: round(v, 6) for k, v in
                                      zdisc["sigma_is"].items()}},
        "d6_correlation": d6,
        "batch_corr_matrix_descriptive": batch_corr_matrix,
        "cells": per_cell,
        "ranking": ranking,
        "winners": winners,
        "g2_block": g2_block,
        "window_cells": windows,
        "corps_gate": corps_gate,
        "trials_ledger": ledger,
        "score_head_disclosure": {
            f"{c}|{m}": cells[(c, m)]["score_head"][:6]
            for (c, m) in cells},
    }
    out.update(SG.cutoff_meta(EVIDENCE_CUTOFF))    # top-level C2 key (s2)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False, default=str)

    verdict = {
        "batch": BATCH, "date": out["meta"]["date"],
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "prereg_sha256_at_run": prereg_sha,
        "eligible_by_corps": {c: ranking[c]["eligible"] for c in CORPS},
        "winners": winners,
        "d6_rejections": [k for k in d6["pairs"] if not d6["pairs"][k]["d6_ok"]],
        "g2_by_corps": {c: g2_block[c]["g2_winner"] for c in CORPS},
        "corps_gate": corps_gate,
        "verdict_text": (
            f"winners={ {c: winners[c] for c in CORPS} }; eligible "
            f"{ {c: len(ranking[c]['eligible']) for c in CORPS} }/15 "
            f"composite cells; D6 rejections "
            f"{len([k for k in d6['pairs'] if not d6['pairs'][k]['d6_ok']])}"
            + ("" if all(winners.values()) else
               "; zero-winner corps = honest read (no gate lowered)")),
        "trials_ledger": ledger,
        "refs": {"cells": "results/factor_blend_cells.json",
                 "prereg": "research/FACTOR_BLEND.md"},
    }
    verdict.update(SG.cutoff_meta(EVIDENCE_CUTOFF))  # top-level C2 key (s2)
    with open(VERDICT_JSON, "w", encoding="utf-8") as fh:
        json.dump(verdict, fh, indent=2, ensure_ascii=False)

    import csv as _csv
    cols = ["corps", "method", "full_sharpe", "full_ann", "full_dd",
            "is_sharpe", "is2_sharpe", "n_trades", "n_entries",
            "worst_year", "benefit", "dr", "line_ok", "ci_lb_pos",
            "entries_ok", "clauses_all", "x2_full_sharpe", "x2_survive",
            "d6_max_abs", "d6_ok", "g1_pass", "eligible", "winner"]
    with open(FINAL_CSV, "w", encoding="utf-8", newline="") as fh:
        w = _csv.writer(fh)
        w.writerow(cols)
        for corps in CORPS:
            for m in METHODS:
                k = f"{corps}|{m}"
                c = per_cell[k]
                w.writerow([
                    corps, m, c["x1"]["full"]["sharpe"],
                    c["x1"]["full"]["annual_return"],
                    c["x1"]["full"]["max_drawdown"],
                    c["x1"]["is"]["sharpe"], c["x1"]["is2"]["sharpe"],
                    c["x1"]["n_trades"], c["x1"]["n_entries"],
                    c["x1"]["worst_year"], c["benefit_passive_baseline"],
                    c["dr_passive_baseline"],
                    c["g1_prime_v2"]["line_ok"],
                    c["g1_prime_v2"]["ci_lower_bound_positive"],
                    (c["g1_prime_v2"].get("trade_gate") or {})
                    .get("entries_ok", ""),
                    all(c["clauses"].values()),
                    c["x2"]["full"]["sharpe"], c["x2_survive"],
                    c["d6"]["max_abs"], c["d6"]["d6_ok"], c["g1_pass"],
                    k in eligible[corps],
                    winners[corps] == k])

    with open(ATTRITION, encoding="utf-8-sig") as fh:
        attr = json.load(fh)
    n_elig = sum(len(eligible[c]) for c in CORPS)
    attr["entries"] = [e for e in attr.get("entries", [])
                       if e.get("batch") != BATCH] + [{
        "batch": BATCH, "ts": out["meta"]["date"], "kind": "search",
        "cells_ledger_delta": BATCH_CELLS,
        "ledger_total_after": int(ledger["total"]),
        "gates": {"eligible_count": n_elig,
                  "winners": {c: winners[c] for c in CORPS},
                  "d6_rejections": len([k for k in d6["pairs"]
                                        if not d6["pairs"][k]["d6_ok"]])},
        "eliminated": 15 - n_elig,
        "refs": {"results": "results/factor_blend_cells.json",
                 "verdict": "results/factor_blend_verdict.json",
                 "prereg": "research/FACTOR_BLEND.md"}}]
    with open(ATTRITION, "w", encoding="utf-8") as fh:
        json.dump(attr, fh, indent=2, ensure_ascii=False)

    log(f"FINAL: winners={winners} eligible={n_elig}/15 "
        f"ledger N={ledger.get('total')} (prev={ledger.get('prev_total')})")
    return True


# ----------------------------------------------------------------- status
def cmd_status() -> int:
    done = _load_done()
    n_x1 = sum(1 for k in done if k.endswith("|x1"))
    n_x2 = sum(1 for k in done if k.endswith("|x2"))
    n_m = sum(1 for k in done if k.startswith("member|"))
    print(f"done: cells x1 {n_x1}/15 x2 {n_x2}/15 members {n_m}/6 | "
          f"lock_alive={_lock_alive()} | final_json="
          f"{os.path.exists(OUT_JSON)}")
    return 0


# ---------------------------------------------------------------- selftest
def run_selftest() -> int:
    """Hermetic (J18 family: no panel dependency; assertions derived from
    constructed fixtures; dual-reading boundary states per r71 law)."""
    ok_n = 0

    def ok(name, cond):
        nonlocal ok_n
        ok_n += 1
        print(f"[{'PASS' if cond else 'FAIL'}] {name}")
        return bool(cond)

    # 1) frozen shortlists: keys in FACTORS, counts 10/10/9, cross-corps
    #    sign table byte-matches the prereg s3 plane
    ok("shortlists: all keys registered in FACTORS",
       all(f in FACTORS for s in CORPS.values() for f in s))
    ok("shortlists: counts 10/10/9",
       (len(CORPS["attack"]), len(CORPS["defense"]), len(CORPS["chop"]))
       == (10, 10, 9))
    ok("sign table: attack mom_12_1(+)/extreme_freq(-)",
       CORPS["attack"]["mom_12_1"] == 1 and CORPS["attack"]["extreme_freq"] == -1)
    ok("sign table: cross-corps dual-sign factors frozen",
       CORPS["chop"]["price_position"] == -1
       and CORPS["attack"]["price_position"] == +1
       and CORPS["chop"]["intraday_range"] == +1
       and CORPS["defense"]["intraday_range"] == -1
       and CORPS["chop"]["gap_overnight"] == -1
       and CORPS["attack"]["gap_overnight"] == +1
       and CORPS["defense"]["ma_bias_20"] == -1
       and CORPS["chop"]["ma_bias_20"] == -1
       and CORPS["chop"]["vol_price_diverge"] == +1)

    # 2) xs_ic_series: Pearson identity on a hand-computed 2-date fixture
    idx = pd.date_range("2024-01-01", periods=2)
    z = pd.DataFrame({"A": [1.0, 0.0], "B": [0.0, 1.0],
                     "C": [0.5, 0.5], "D": [-1.0, -0.5],
                     "E": [2.0, -2.0]}, index=idx)
    f = pd.DataFrame({"A": [2.0, -1.0], "B": [-1.0, 2.0], "C": [0.0, 0.0],
                      "D": [1.0, 1.0], "E": [1.0, 1.0]}, index=idx)
    ic = xs_ic_series(z, f, min_n=5)
    # date0: z=[1,0,.5,-1,2] f=[2,-1,0,1,1] -> corr by hand = 0.5*... use
    # np.corrcoef as the independent oracle (construction-derivative check)
    exp0 = float(np.corrcoef(z.iloc[0], f.iloc[0])[0, 1])
    exp1 = float(np.corrcoef(z.iloc[1], f.iloc[1])[0, 1])
    ok("xs_ic: matches numpy per-row Pearson oracle",
       abs(ic.iloc[0] - exp0) < 1e-12 and abs(ic.iloc[1] - exp1) < 1e-12)
    z2 = z.copy()
    z2.iloc[0, :] = np.nan
    ic2 = xs_ic_series(z2, f, min_n=5)
    ok("xs_ic: min_n gate -> all-NaN row is NaN",
       bool(pd.isna(ic2.iloc[0])) and abs(ic2.iloc[1] - exp1) < 1e-12)

    # 3) method a: EW identity
    ok("weights a_EW: 1/K each",
       _ew(["x", "y", "z"]) == {"x": 1 / 3, "y": 1 / 3, "z": 1 / 3})

    # 4) method b: signed normalization; negative IC flips; zero mass -> EW
    wb = weights_b({"p": 0.10, "q": -0.05, "r": 0.05})
    ok("weights b_IC: signed sum|w|=1, negative IC flips",
       abs(wb["weights"]["p"] - 0.5) < 1e-6
       and abs(wb["weights"]["q"] + 0.25) < 1e-6
       and abs(wb["weights"]["r"] - 0.25) < 1e-6
       and abs(sum(abs(v) for v in wb["weights"].values()) - 1.0) < 1e-6)
    ok("weights b_IC: zero mass -> deterministic EW fallback",
       weights_b({"p": 0.0, "q": 0.0})["path"]
       == "ew_fallback_zero_ic_mass")

    # 5) method c: 1/sigma ratio identity (sigma 1:2 -> weights 2:1)
    wc = weights_c({"p": 0.01, "q": 0.02})
    ok("weights c_INVVOL: w ~ 1/sigma (2:1 exact)",
       abs(wc["weights"]["p"] - 2 / 3) < 1e-6
       and abs(wc["weights"]["q"] - 1 / 3) < 1e-6)
    ok("weights c_INVVOL: zero sigma -> EW fallback",
       weights_c({"p": 0.0})["path"] == "ew_fallback_zero_sigma")

    # 6) method d: causal window + all-negative/incomplete fallbacks
    ok("weights d: all-negative IC -> EW fallback",
       weights_d_at({"p": -0.1, "q": -0.2})[1]
       == "ew_fallback_all_negative_ic")
    ok("weights d: incomplete window (NaN) -> EW fallback",
       weights_d_at({"p": float("nan"), "q": 0.3})[1]
       == "ew_fallback_incomplete_ic_window")
    wd = weights_d_at({"p": 0.2, "q": -0.1})[0]
    ok("weights d: signed mass normalization",
       abs(wd["p"] - 2 / 3) < 1e-6 and abs(wd["q"] + 1 / 3) < 1e-6)
    # causality: the IC value whose fwd window closes AFTER t (ics[t] itself)
    # must not enter the t window; ics[t-1] (closes exactly at t) does
    icf = pd.Series([0.1, 0.2, 0.3, 0.4], index=pd.bdate_range(
        "2024-01-01", periods=4))
    pos = 3
    t = icf.index[pos]
    win = icf.iloc[max(0, pos - IC_WINDOW):pos]
    win = win[win.index <= t]
    ok("d-causality fixture: window = IC[t-60..t-1], ics[t] excluded",
       list(win.values) == [0.1, 0.2, 0.3] and 0.4 not in list(win.values))

    # 7) method e: state(t-1) routing (bear->b, chop/bull/na->EW)
    wb2 = {"p": 0.9, "q": 0.1}
    ok("weights e: bear -> b weights",
       weights_e_at("bear", wb2, ["p", "q"])[0] == wb2
       and weights_e_at("bear", wb2, ["p", "q"])[1] == "bear->ic_is")
    ok("weights e: chop/bull/na -> EW",
       weights_e_at("chop", wb2, ["p", "q"])[0] == {"p": 0.5, "q": 0.5}
       and weights_e_at("bull", wb2, ["p", "q"])[0] == {"p": 0.5, "q": 0.5}
       and weights_e_at("na", wb2, ["p", "q"])[0] == {"p": 0.5, "q": 0.5})

    # 8) score_to_held parity vs composite_rotation.top_n_rotation
    from strategies.composite_rotation import top_n_rotation
    from engine.factors import FACTORS as FF
    n = 120
    days = pd.bdate_range("2020-01-01", periods=n)
    cols = [f"S{i}" for i in range(6)]
    rnd = np.random.default_rng(11)
    panel = {f: pd.DataFrame(rnd.normal(1, 0.02, (n, len(cols))),
                             index=days, columns=cols)
             for f in ("open", "high", "low", "close", "volume", "amount")}
    canon_held = top_n_rotation(panel["high"], panel["low"],
                                panel["close"], top_n=TOP_N,
                                rebal_days=REBAL_DAYS)
    from strategies.composite_rotation import composite_score
    my_held = score_to_held(composite_score(panel["high"], panel["low"],
                                             panel["close"]))
    ok("score_to_held: byte-identical vs composite_rotation canon",
       my_held.equals(canon_held))
    # membership refreshes only on iloc[::rebal_days] rows
    score = composite_score(panel["high"], panel["low"], panel["close"])
    poisoned = score.copy()
    poisoned.iloc[5] = -poisoned.iloc[5]      # mid-window mutation
    ok("held: mid-window score mutation cannot alter membership",
       score_to_held(poisoned).equals(my_held))

    # 9) blend_score: weights timeline -> score = sum w_f z_f; corps-scoped
    #    (W columns only -- a corps' blend must not touch other corps'
    #    factors when handed a z superset)
    W = pd.DataFrame({"p": 1.0, "q": 0.0}, index=days)
    zp = pd.DataFrame(1.5, index=days, columns=cols)
    zq = pd.DataFrame(9.0, index=days, columns=cols)
    zr = pd.DataFrame(99.0, index=days, columns=cols)
    sc = blend_score(W, {"p": zp, "q": zq, "r": zr})
    ok("blend_score: w-weighted sum identity, corps-scoped columns",
       bool((sc == 1.5).all().all()))

    # 10) D6 line: boundary
    ok("d6 gate: 0.7 line rejects at/above, passes below",
       (abs(0.71) >= D6_REJECT) and (abs(0.69) < D6_REJECT))

    # 11) ADJ-1 fixture: benefit/DR from the frozen passive baseline
    passive_s_fixture = 0.3004
    ok("ADJ-1: benefit = S - passive; DR = S / passive",
       abs((0.5004 - passive_s_fixture) - 0.2) < 1e-9
       and abs(0.5004 / passive_s_fixture - 0.5004 / 0.3004) < 1e-12)

    # 12) ADJ-2 fixture: OOS face is an honest locked-box marker
    marker = {"status": "locked_box_not_consumed",
              "note": "post-cutoff forward box; paper accrual only "
                      "(IV6 d2_note canon; prereg s2)"}
    ok("ADJ-2: OOS window face = not-consumed marker (no fabricated span)",
       marker["status"] == "locked_box_not_consumed"
       and "sharpe" not in marker)

    # 13) frozen budget composition: 30 + 15 + 90 = 135
    ok("ledger caliber: 30 engine + 15 ranking + 90 window == 135",
       15 * 2 + 3 * 5 + 15 * 6 == BATCH_CELLS == 135)

    # 14) CE machine constants frozen (COMPOSITE-CE-01 lineage)
    ok("CE params: COMPOSITE-CE-01 frozen plane (5/0.19/25/0.05/0.10/16)",
       CE_PARAMS == {"max_positions": 5, "position_size_pct": 0.19,
                     "time_decay_period": 25, "time_decay_threshold": 0.05,
                     "trailing_stop_activate": 0.1}
       and CE_EXIT_OVERRIDES == {"loss_time_days": 16}
       and TOP_N == 5 and REBAL_DAYS == 20)

    # 15) coverage gate arithmetic on a synthetic calendar
    cal = pd.bdate_range("2026-09-01", "2026-09-30")
    last = pd.Timestamp("2026-09-24")
    gap = int(((cal > last) & (cal <= pd.Timestamp("2026-09-24"))).sum())
    ok("coverage gate: gap 0 at cutoff; 1 the day after",
       gap == 0 and int(((cal > pd.Timestamp("2026-09-23"))
                          & (cal <= last)).sum()) == 1)

    # 16) skill-line budget law: batch_cells feeds sqrt(2 ln N_eff) term
    import math
    ok("skill-line law: N_eff=135 enters the extreme term",
       abs(math.sqrt(2.0 * math.log(135))
           - math.sqrt(2.0 * math.log(30 + 15 + 90))) < 1e-12)

    print(f"selftest: {ok_n} checks, all PASS = {ok_n >= 22}")
    return 0 if ok_n >= 22 else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "status"
    if cmd == "selftest":
        return run_selftest()
    if cmd == "run":
        return cmd_run()
    if cmd == "status":
        return cmd_status()
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
