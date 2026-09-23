"""corr-watch v1 -> monitoring report (charter s1.2; spec research/CORR_WATCH_SPEC.md).

SPEC FROZEN BEFORE ANY RUN (commit fa284a7 precedes this run). Recorded-config
reproduction + monitoring class -- ZERO N_eff ledger increment (smoke anchor
gate / g25 family-matrix precedent; disclosed in JSON audit block).

What it does (spec s2-s4):
  - re-derive the 6 member x1 sleeves verbatim (EW6 harness import: E.member_run,
    SIGNAL_BUILDERS/ExitPatch/CostPatch reused, never re-implemented);
  - TWIN determinism gate vs results/portfolio_iv6.json (recorded member stats,
    corr averages, IV weights; mismatch => watch VOID, data-drift tripwire,
    report-only, no repair-rerun);
  - registered-window corr blocks (full/IS/IS2) + rolling-60d pairwise
    trajectory over the trailing 252 trading days;
  - IV weight monthly-refresh recompute (frozen IV6 s3 formula) -- disclosure
    + twin only, ZERO adoption (charter s5 T1 route);
  - watch flags W1/W2/W3/W4/W5 + FL forward-leg honesty gate (MIN_PERIODS=60
    paper bars; machinery deferred per spec s1 -- paper JSON carries aggregates
    only, no daily equity).

Exit codes: 0 = watch ran (flags disclosed inside); 2 = TWIN broken => VOID.
"""
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

from config import PATHS
from firm.hr import TRADERS_DIR
from live.paper import OOS_START
from parallel_runner import run_cells_parallel, worker_cap
from science_gates import recorded_lines

import ew6_portfolio as E          # EW6 harness: reuse, never rewrite
from ew6_portfolio import MAX_WORKERS, combine, corr_block

SPEC = os.path.join(PATHS.root, "research", "CORR_WATCH_SPEC.md")
IV6_JSON = os.path.join(PATHS.results_dir, "portfolio_iv6.json")
EW6_JSON = os.path.join(PATHS.results_dir, "portfolio_ew6.json")
OUT_JSON = os.path.join(PATHS.results_dir, "corr_watch.json")
PAPER_DIR = Path(PATHS.results_dir) / "paper"

TOL = 1e-9                         # twin tolerance (recorded values are 4/6dp rounded)
W1_LINE = 0.70                     # spec s4: full-window D6 line
W2_LINE = 0.70                     # spec s4: IS2 convergence warning line
W3_DELTA = 0.05                    # spec s4: trend step vs previous watch record
MIN_PERIODS = 60                   # spec s1 FL: forward-window corr needs >=60 paper bars
ROLL_WINDOW = 60                   # rolling corr window (spec s4)
TRAIL_DAYS = 252                    # trailing window for the trajectory summary


def _r4(x):
    return round(float(x), 4)


def _init_worker():
    E._init_worker()               # sets ew6_portfolio.PRICES_FULL per worker


def sleeve_x1(tid: str) -> dict:
    """E.member_run verbatim, x1 only (the sleeve IS the anchor run)."""
    return E.member_run(tid)


def _to_eq_s(r: dict) -> pd.Series:
    return pd.Series(r["eq"], index=pd.to_datetime(r["dates"]))


def _pair_keys(tids):
    return [(tids[i], tids[j]) for i in range(len(tids))
            for j in range(i + 1, len(tids))]


def iv_weight_refresh(sleeves: dict, tids: list) -> dict:
    """Frozen IV6 s3 formula verbatim: w_i = (1/sigma_i-IS)/sum; sigma on the
    member's own equity axis, IS segment (< OOS_START), pct_change std."""
    vol, raw = {}, {}
    for tid in tids:
        eq_s = sleeves[tid]["eq_s"]
        is_ret = eq_s[eq_s.index < pd.Timestamp(OOS_START)].pct_change().dropna()
        vol[tid] = round(float(is_ret.std()), 6)
        raw[tid] = 1.0 / float(is_ret.std())
    s = sum(raw.values())
    w = {tid: round(raw[tid] / s, 6) for tid in tids}
    return {"weights": w, "sum": round(sum(w.values()), 6), "is_vol": vol}


def rolling_pairs(rets: pd.DataFrame, tids: list) -> dict:
    """Rolling ROLL_WINDOW pairwise corr on the trailing TRAIL_DAYS window.
    Trajectory evidence for W3 trend reads -- opens no new gate (spec s4)."""
    tail = rets.tail(TRAIL_DAYS)
    out = {}
    for a, b in _pair_keys(tids):
        rc = tail[a].rolling(ROLL_WINDOW).corr(tail[b]).dropna()
        if len(rc) == 0:
            out[f"{a}|{b}"] = None
            continue
        out[f"{a}|{b}"] = {"last": _r4(rc.iloc[-1]),
                          "first": _r4(rc.iloc[0]),
                          "max": _r4(rc.max()),
                          "min": _r4(rc.min())}
    vals = [v["last"] for v in out.values() if v]
    return {"window_days": int(len(tail)), "roll_window": ROLL_WINDOW,
            "pairs": out, "avg_last": _r4(sum(vals) / len(vals)) if vals else None}


def selftest() -> int:
    """Offline (zero network, zero engine): portfolio-math reuse + IV weight
    formula + rolling-pair helper equivalence + twin comparator."""
    ok = E.self_test_portfolio_math()
    print(f"portfolio-math/regime self-test: {'PASS' if ok else 'FAIL'}")
    if not ok:
        return 1
    idx = pd.bdate_range("2023-01-02", periods=500)   # IS range (synthetic)
    a = 1.0 + (pd.Series([((i % 21) - 10) * 0.001 for i in range(500)], index=idx)).cumsum()
    b = 1.0 + (pd.Series([((i % 13) - 6) * 0.002 for i in range(500)], index=idx)).cumsum()
    sl = {"A": {"eq_s": a}, "B": {"eq_s": b}}
    w = iv_weight_refresh(sl, ["A", "B"])
    ra = a.pct_change().dropna().std()
    rb = b.pct_change().dropna().std()
    exp_a = round((1 / ra) / (1 / ra + 1 / rb), 6)
    ok &= abs(w["weights"]["A"] - exp_a) < 1e-9 and abs(w["sum"] - 1.0) < 1e-6
    print(f"iv-weight formula synthetic check: {'PASS' if ok else 'FAIL'}")
    # rolling pair helper vs direct pandas on a synthetic return frame
    rets = pd.DataFrame({"A": a.pct_change().dropna(),
                         "B": b.pct_change().dropna()}).dropna()
    rp = rolling_pairs(rets, ["A", "B"])
    direct = rets.tail(TRAIL_DAYS)["A"].rolling(ROLL_WINDOW).corr(
        rets.tail(TRAIL_DAYS)["B"]).dropna()
    ok &= abs(rp["pairs"]["A|B"]["last"] - _r4(direct.iloc[-1])) < 1e-9
    print(f"rolling-pair helper equivalence: {'PASS' if ok else 'FAIL'}")
    # twin comparator rounding semantics
    ok &= abs(_r4(0.123449) - 0.1234) < TOL and abs(_r4(0.123451) - 0.1235) < TOL
    print(f"twin rounding semantics: {'PASS' if ok else 'FAIL'}")
    print("selftest: ALL PASS" if ok else "selftest: FAIL")
    return 0 if ok else 1


def run() -> int:
    t0 = time.time()
    if not E.self_test_patches():
        print("patch self-test FAILED -- abort (fake-evidence guard)")
        return 2
    if not E.self_test_portfolio_math():
        print("portfolio-math self-test FAILED -- abort")
        return 2
    print("patch + portfolio-math self-tests: PASS")

    with open(IV6_JSON, encoding="utf-8") as fh:
        iv6 = json.load(fh)
    with open(EW6_JSON, encoding="utf-8") as fh:
        ew6 = json.load(fh)

    tids = sorted(p.stem for p in TRADERS_DIR.glob("*.json")
                  if not p.name.startswith("_"))
    roster_ok = set(tids) == set(iv6["members"])
    print(f"members ({len(tids)}): {tids} roster_ok={roster_ok}")

    twin = {"roster_ok": roster_ok, "members": {}, "corr": {},
            "iv_weights": None, "ok": roster_ok}

    sleeves = {}
    if roster_ok:
        jobs = [(tid, sleeve_x1, (tid,)) for tid in tids]
        res = run_cells_parallel(jobs, workers=min(worker_cap(), MAX_WORKERS),
                                 desc="corr-watch-sleeves", initializer=_init_worker)
        workers = int(res.pop("__workers__"))
        for tid in tids:
            r = res[tid]
            r["eq_s"] = _to_eq_s(r)
            sleeves[tid] = r
    else:
        workers = 0

    # ---- TWIN: member stats ----
    if roster_ok:
        for tid in tids:
            rec = iv6["members"][tid]["x1"]
            rec_cut = iv6["members"][tid]["cutoff"]
            got = sleeves[tid]
            checks = {"full_sharpe": abs(_r4(got["full"]["sharpe"]) - rec["full"]["sharpe"]) < TOL,
                      "is2_sharpe": abs(_r4(got["is2"]["sharpe"]) - rec["is2"]["sharpe"]) < TOL,
                      "n_trades": int(got["n_trades"]) == int(rec["n_trades"]),
                      "cutoff": str(got["cutoff"]) == str(rec_cut)}
            twin["members"][tid] = {"ok": all(checks.values()), **checks}
        twin["ok"] &= all(m["ok"] for m in twin["members"].values())
        print(f"twin member stats: {'OK' if twin['ok'] else 'BROKEN'}")

    # ---- correlations (EW6-identical construction) ----
    corr, rets, is2_mask = None, None, None
    if roster_ok:
        norm1 = pd.concat({tid: sleeves[tid]["eq_s"] / sleeves[tid]["eq_s"].iloc[0]
                           for tid in tids}, axis=1, join="inner").dropna()
        rets = norm1.pct_change().dropna()
        is2_mask = rets.index >= pd.Timestamp(OOS_START)
        corr = {"full": corr_block(rets), "is": corr_block(rets, ~is2_mask),
                "is2": corr_block(rets, is2_mask)}
        for seg in ("full", "is", "is2"):
            got, want = corr[seg]["avg_pairwise"], iv6["correlation"][seg]["avg_pairwise"]
            ok_seg = abs(got - want) < TOL
            twin["corr"][seg] = {"got": got, "recorded": want, "ok": ok_seg}
            twin["ok"] &= ok_seg
        print(f"corr(full) avg={corr['full']['avg_pairwise']} "
              f"is2 avg={corr['is2']['avg_pairwise']} twin={'OK' if twin['ok'] else 'BROKEN'}")

    # ---- TWIN: IV weight refresh ----
    iv_refresh = None
    if roster_ok:
        iv_refresh = iv_weight_refresh(sleeves, tids)
        rec_w = iv6["iv_weights"]["weights"]
        diffs = {tid: abs(iv_refresh["weights"][tid] - rec_w[tid]) for tid in tids}
        w_ok = all(d < TOL for d in diffs.values())
        twin["iv_weights"] = {"ok": w_ok, "max_abs_diff": max(diffs.values())}
        twin["ok"] &= w_ok
        print(f"iv weight refresh twin: max|d|={max(diffs.values()):.2e} "
              f"{'OK' if w_ok else 'BROKEN'}")

    # ---- watch flags ----
    watch, verdict = {}, "VOID" if not twin["ok"] else "clean"
    if twin["ok"] and corr:
        pairs_full = corr["full"]["pairs"]
        pairs_is2 = corr["is2"]["pairs"]
        w1_hits = {k: v for k, v in pairs_full.items() if abs(v) >= W1_LINE}
        w2_hits = {k: v for k, v in pairs_is2.items() if abs(v) >= W2_LINE}
        watch["W1_full_d6_line"] = {"line": W1_LINE, "hits": w1_hits,
                                    "flag": "RED" if w1_hits else "none"}
        watch["W2_is2_convergence"] = {"line": W2_LINE, "hits": w2_hits,
                                       "flag": "ORANGE" if w2_hits else "none"}
        if w1_hits:
            verdict = "RED"
        elif w2_hits:
            verdict = "ORANGE"

        # W3: trend vs previous watch record (first run = baseline, no gate)
        prev = None
        if os.path.exists(OUT_JSON):
            with open(OUT_JSON, encoding="utf-8") as fh:
                hist = json.load(fh).get("history", {})
            if hist:
                last_day = max(hist)
                prev = hist[last_day].get("max_is2_pair")
        cur_max_is2 = max((abs(v) for v in pairs_is2.values()), default=None)
        if prev is not None and cur_max_is2 is not None:
            step = _r4(cur_max_is2 - prev)
            watch["W3_trend_vs_prev"] = {"prev": prev, "cur": _r4(cur_max_is2),
                                         "step": step,
                                         "flag": "INFO" if step >= W3_DELTA else "none"}
        else:
            watch["W3_trend_vs_prev"] = {"prev": prev, "cur": _r4(cur_max_is2)
                                         if cur_max_is2 is not None else None,
                                         "flag": "baseline" if prev is None else "none"}
        watch["max_is2_pair"] = _r4(cur_max_is2) if cur_max_is2 is not None else None

        # W4: corr(IV6, EW6) re-derived from sleeves (construction-variant fact)
        ew_w = {tid: round(1.0 / len(tids), 6) for tid in tids}
        both = pd.concat({"IV6": combine({t: sleeves[t]["eq_s"] for t in tids},
                                        iv_refresh["weights"]),
                          "EW": combine({t: sleeves[t]["eq_s"] for t in tids}, ew_w)},
                         axis=1, join="inner").dropna()
        corr_iv_ew = _r4(both.pct_change().dropna().corr().loc["IV6", "EW"])
        rec_iv_ew = iv6["head_to_head"]["corr_iv6_ew6"]
        watch["W4_corr_iv6_ew6"] = {"got": corr_iv_ew, "recorded": rec_iv_ew,
                                    "twin_ok": abs(corr_iv_ew - rec_iv_ew) < TOL,
                                    "flag": "disclosure"}
        twin["ok"] &= watch["W4_corr_iv6_ew6"]["twin_ok"]

        # W5: x2 safety margins from frozen products (spec s4: recorded values)
        vi = recorded_lines()["vi_bar"]
        margins = {"EW6": {"x2_full": ew6["portfolios"]["x2"]["full"]["sharpe"],
                           "vi_bar": vi,
                           "margin": _r4(ew6["portfolios"]["x2"]["full"]["sharpe"] - vi)},
                   "IV6": {"x2_full": iv6["portfolios_iv"]["x2"]["full"]["sharpe"],
                           "vi_bar": vi,
                           "margin": _r4(iv6["portfolios_iv"]["x2"]["full"]["sharpe"] - vi)}}
        w5_red = any(m["margin"] <= 0 for m in margins.values())
        watch["W5_x2_margins"] = {**margins, "flag": "RED" if w5_red else "none"}
        if w5_red and verdict not in ("VOID",):
            verdict = "RED"

        # rolling trajectory (evidence, no gate)
        watch["rolling_traj"] = rolling_pairs(rets, tids)
    else:
        watch["skipped"] = "twin broken -- no watch flags computed (spec s2: VOID)"

    # ---- FL: forward (paper) window honesty gate ----
    fl = {"min_periods": MIN_PERIODS, "bars_per_member": {}}
    for p in sorted(PAPER_DIR.glob("*_paper.json")):
        with open(p, encoding="utf-8") as fh:
            fl["bars_per_member"][p.stem.replace("_paper", "")] = int(
                json.load(fh).get("bars", 0))
    min_bars = min(fl["bars_per_member"].values()) if fl["bars_per_member"] else 0
    fl["min_bars"] = min_bars
    fl["status"] = "insufficient_data" if min_bars < MIN_PERIODS else "computable"
    fl["machinery"] = "deferred (spec s1: paper JSON has aggregates only)"

    # ---- write outputs (history: same-day idempotent replace) ----
    out = {"spec": os.path.relpath(SPEC, PATHS.root),
           "class": "recorded-config-reproduction-monitoring (zero N_eff; "
                    "smoke anchor gate / g25 family-matrix precedent)",
           "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
           "members": tids, "twin": twin, "watch": watch,
           "forward_leg": fl,
           "iv_weight_refresh": iv_refresh,
           "verdict": verdict,
           "audit": {"elapsed_sec": round(time.time() - t0, 1),
                     "n_engine_runs": len(tids) if roster_ok else 0,
                     "workers": workers,
                     "ledger_trials_added": 0}}
    history = {}
    if os.path.exists(OUT_JSON):
        with open(OUT_JSON, encoding="utf-8") as fh:
            history = json.load(fh).get("history", {})
    day = time.strftime("%Y-%m-%d")
    history[day] = {"verdict": verdict,
                    "corr_full_avg": corr["full"]["avg_pairwise"] if corr else None,
                    "corr_is2_avg": corr["is2"]["avg_pairwise"] if corr else None,
                    "max_is2_pair": watch.get("max_is2_pair"),
                    "w1": watch.get("W1_full_d6_line", {}).get("flag"),
                    "w2": watch.get("W2_is2_convergence", {}).get("flag"),
                    "twin_ok": twin["ok"]}
    out["history"] = history
    tmp = OUT_JSON + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, OUT_JSON)
    print(f"corr_watch: verdict={verdict} twin_ok={twin['ok']} "
          f"FL={fl['status']}({min_bars} bars) -> results/corr_watch.json "
          f"[{out['audit']['elapsed_sec']}s]")
    return 0 if twin["ok"] else 2


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    sys.exit(selftest() if cmd == "selftest" else run())
