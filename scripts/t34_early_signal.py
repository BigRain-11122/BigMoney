"""T34_EARLY_SIGNAL: half-step ladder A/B on the T-22 virtual-timepoint
harness (CEO order O-20260924-2030 s3; ticket T-2026-09-24-34 immediate).

Preregistered in research/T34_EARLY_SIGNAL.md BEFORE any run (frozen
pre-run commit; no threshold/seed/param changes after results). Stage A
re-derives the 6 registered members' DAILY equity-return curves on the two
frozen T-22 axes (legacy = core48 cut at 2026-09-23 / deep = t18 panel,
binding cutoff 2026-09-22) at every eligible startpoint -- the same
(member, startpoint) cells T-22 already counted; curves are infrastructure
re-derivation, NOT re-counted trials. Stage B (finalize) composes the
corps envelope (T-33 roster v1 frozen assignment: attack=COMPOSITE-CE-01,
chop=5 registered, defense=empty->cash) under two routing policies per
startpoint and window {6m,12m,24m}:

  CONF   : confirmed-line-only switching (legacy = REGIME_GUARD v3 replay
           4-state; deep = T-22 frozen 3-way proxy, disclosed);
  LADDER : C1 fast line (510300 MA20>MA60 held P=5 bars, asymmetric exit)
           -> attack corps at HALF step before confirmation, full on
           confirmed GREEN/bull; brake T0 authority untouched.

Frozen judgments (prereg s4): J1 pooled 12m beat-passive uplift > 0 on BOTH
axes; J2 worst-start 12m dd >= -0.35 both axes; J3 whipsaw switch counts
disclosed. Honest negative = keep confirmed-only switching. NO paper
activation, zero registration, zero PAPER_LEVELS touch.

Multi-core law O-20260924-2130: ProcessPool, workers=min(cores-2, RAM
guard), BelowNormal priority (O-1136 pool), workers_plan logged.

Usage:
  python scripts/t34_early_signal.py run [--axis all|legacy|deep]
      [--workers N] [--limit K]
  python scripts/t34_early_signal.py finalize      (gates + overlay + verdict)
  python scripts/t34_early_signal.py selftest       (offline)
"""
import argparse
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

from t22_virtual_timepoints import (       # frozen T-22 pipeline primitives
    W6M, W12M, W24M, WARMUP_TD, enumerate_starts, regime_proxy,
    _load_axis_prices, load_done_keys, _slice_metrics,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "results", "t34")
TICKET = "T-2026-09-24-34"
BATCH = "T34_EARLY_SIGNAL"
PREREG_PATH = os.path.join(ROOT, "research", "T34_EARLY_SIGNAL.md")

# ---- frozen batch constants (prereg s2/s3; expected start counts are READ
# from the t22 results file at gate time -- hand-copy prohibited)
LEGACY_CUTOFF = "2026-09-23"     # T-22 legacy axis frozen cutoff
BINDING_CUTOFF = "2026-09-22"    # deep manifest / binding evidence cutoff
ATTACK = ["COMPOSITE-CE-01"]     # T-33 roster v1 frozen assignment
CHOP = ["COMPOSITE-CE-02", "DROUGHT-CE-01", "ENGULF-CE-01",
        "NEEDLE-DE-01", "VOLATILITY-CE-01"]
LADDER_P = 5                     # C1 persistence bars
HALF = 0.5                       # half-step fraction (prereg s3 primary)
SENS_HALF = (0.25, 0.75)         # reporting-only sensitivity
DD_RED_LINE = -0.35              # P-5 frozen (prereg s4 J2)
BOOTSTRAP_B = 2000
BOOTSTRAP_SEED = 20260928        # SEED_REGISTRY["t34_early_signal"]
WINDOWS = {"6m": W6M, "12m": W12M, "24m": W24M}
V3_FILE = os.path.join(ROOT, "results", "regime_calibration_v3.json")
T22_FILE = os.path.join(ROOT, "results", "t22_virtual_timepoints.json")
PROBE_POS = (60, 300, 700, 1100, 1400, 1800, 2200, 2600, 3000, 3400,
             3800, 4200)         # dprobe pattern: 12 cells, axis-mixed


def curve_path(axis: str) -> str:
    return os.path.join(OUT_DIR, f"curves_{axis}.jsonl")


def _log(msg: str) -> None:
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}", flush=True)


# ------------------------------------------------------------------ stage A

_G = {}   # per-worker globals (t22 _init_worker pattern, base face only)


def _init_worker(axis: str):
    import psutil
    pri = getattr(psutil, "BELOW_NORMAL_PRIORITY_CLASS", None)
    if pri is not None:
        try:
            psutil.Process().nice(pri)       # O-1136 low-priority pool
        except Exception:
            pass
    from live.paper import PAPER_LEVELS, SIGNAL_BUILDERS, build_panels
    from firm.hr import TRADERS_DIR, load_trader
    prices = _load_axis_prices(axis)
    if axis == "legacy":                     # frozen cutoff truncation
        hi = pd.Timestamp(LEGACY_CUTOFF)
        prices = {s: df[df.index <= hi] for s, df in prices.items()}
    P = build_panels(prices)
    entries, params_by_id, exits_by_id = {}, {}, {}
    traders = []
    for path in sorted(TRADERS_DIR.glob("*.json")):
        if path.name.startswith("_"):
            continue
        t = load_trader(path.stem)
        if t.get("level") not in PAPER_LEVELS:
            continue
        traders.append(t["id"])
        entries[t["id"]] = SIGNAL_BUILDERS[t["params"]["entry"]](P)
        params_by_id[t["id"]] = {k: v for k, v in t["params"].items()
                                 if k != "entry"}
        exits_by_id[t["id"]] = t.get("exit_overrides")
    _G.update(prices=prices, idx=P["close"].index, close=P["close"],
              traders=traders, entries=entries, params_by_id=params_by_id,
              exits_by_id=exits_by_id)


def _run_cell_curve(member: str, pos: int) -> dict:
    """One (member, startpoint) cell: T-22 _run_cell body (base face, frozen
    pipeline) + daily-return curve extraction. Deterministic; kill-safe via
    per-cell checkpoint keyed 'member|pos'."""
    from engine import run_backtest
    from live.paper import ExitPatch
    prices, idx = _G["prices"], _G["idx"]
    entry = _G["entries"][member]
    params = _G["params_by_id"][member]
    sdate = idx[pos]
    e = idx[min(pos + W24M - 1, len(idx) - 1)]
    window = {s: df[(df.index >= sdate) & (df.index <= e)]
              for s, df in prices.items()}
    with ExitPatch(_G["exits_by_id"][member]):
        res = run_backtest(window, params, entry_signal=entry,
                           exit_signal=entry <= 0)
    widx = idx[pos:pos + W24M][:len(res["equity_curve"])]
    eq = pd.Series(res["equity_curve"], index=widx)
    rets = eq.pct_change().fillna(0.0)          # first bar = deployment
    n_bars = int(len(eq))
    m12 = _slice_metrics(eq, res["trades"], W12M)
    close = _G["close"]
    syms = close.columns[close.loc[sdate].notna()]
    base = close.loc[sdate, syms]
    rel = (close.loc[sdate:e, syms] / base).mean(axis=1)
    p12 = _slice_metrics(rel, [], W12M)
    return {"key": f"{member}|{pos}", "member": member, "pos": pos,
            "start": str(sdate.date()), "n_bars": n_bars,
            "partial_12m": n_bars < W12M, "partial_24m": n_bars < W24M,
            "ret_12m": m12["ret"], "dd_12m": m12["dd"],
            "p_ret_12m": p12["ret"],
            "curve": [round(float(x), 8) for x in rets.to_numpy()]}


def _axis_panel(axis: str):
    prices = _load_axis_prices(axis)
    if axis == "legacy":
        hi = pd.Timestamp(LEGACY_CUTOFF)
        prices = {s: df[df.index <= hi] for s, df in prices.items()}
    from live.paper import build_panels
    return build_panels(prices)


def _trader_ids():
    from live.paper import PAPER_LEVELS
    from firm.hr import TRADERS_DIR, load_trader
    out = []
    for path in sorted(TRADERS_DIR.glob("*.json")):
        if path.name.startswith("_"):
            continue
        t = load_trader(path.stem)
        if t.get("level") in PAPER_LEVELS:
            out.append(t["id"])
    return out


def _expected_starts() -> dict:
    d = json.load(open(T22_FILE, encoding="utf-8-sig"))
    return {"legacy": int(d["axes"]["legacy"]["n_starts"]),
            "deep": int(d["axes"]["deep"]["n_starts"])}


def cmd_run(args) -> int:
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUT_DIR, "logs"), exist_ok=True)
    log_path = os.path.join(OUT_DIR, "logs", f"run_{args.axis}.log")
    if os.environ.get("T34_DETACHED") == "1":
        sys.stdout = open(log_path, "a", buffering=1, encoding="utf-8")
        sys.stderr = sys.stdout
    t0 = time.time()
    import psutil
    cores = psutil.cpu_count(logical=True)
    free_gb = psutil.virtual_memory().available / 1e9
    ram_guard = max(4, min(14, int(free_gb // 1.2)))   # ~1.2GB/worker budget
    workers = args.workers or min(cores - 2, ram_guard)   # O-2130 formula
    _log(f"[{args.axis}] start cores={cores} free_ram={free_gb:.1f}GB "
         f"workers_plan={workers} (min(cores-2={cores - 2}, ram_guard="
         f"{ram_guard}))")

    # G-ANCHOR (t22 run gate, verbatim sequence)
    from live.paper import PAPER_LEVELS, anchor_gate, load_core
    from firm.hr import TRADERS_DIR, load_trader
    prices = load_core()
    n_fail = 0
    for path in sorted(TRADERS_DIR.glob("*.json")):
        if path.name.startswith("_"):
            continue
        t = load_trader(path.stem)
        if t.get("level") not in PAPER_LEVELS:
            continue
        a = anchor_gate(t, prices)
        _log(f"anchor {t['id']}: {'PASS' if a['ok'] else 'FAIL'}")
        n_fail += 0 if a["ok"] else 1
    del prices
    if n_fail:
        _log(f"G-ANCHOR FAIL x{n_fail} -- batch void")
        return 3

    axes = ["legacy", "deep"] if args.axis == "all" else [args.axis]
    expected = _expected_starts()
    members = ATTACK + CHOP
    for axis in axes:
        P = _axis_panel(axis)
        close = P["close"]
        listed = close.notna().sum(axis=1)
        eligible = enumerate_starts(len(close.index), listed)
        # G-CENSUS drift gate (r105 law): frozen-cutoff re-enumeration must
        # equal the T-22 finalize record exactly
        if len(eligible) != expected[axis]:
            _log(f"G-CENSUS FAIL [{axis}]: {len(eligible)} != "
                 f"{expected[axis]} (t22 frozen) -- batch void")
            return 3
        done = load_done_keys(curve_path(axis))
        jobs = [(m, p) for p in eligible for m in members
                if f"{m}|{p}" not in done]
        if args.limit:
            jobs = jobs[:args.limit]
        _log(f"[{axis}] census PASS {len(eligible)} starts; cells todo="
             f"{len(jobs)} resume-skipped="
             f"{len(eligible) * len(members) - len(jobs)}")
        if not jobs:
            continue
        from concurrent.futures import ProcessPoolExecutor, as_completed
        n_done, t_last = 0, time.time()
        with open(curve_path(axis), "a", encoding="utf-8") as fh:
            with ProcessPoolExecutor(max_workers=workers,
                                     initializer=_init_worker,
                                     initargs=(axis,)) as pool:
                futs = {pool.submit(_run_cell_curve, m, p): (m, p)
                        for m, p in jobs}
                for fut in as_completed(futs):
                    row = fut.result()
                    fh.write(json.dumps(row) + "\n")
                    fh.flush()
                    n_done += 1
                    if time.time() - t_last > 30:
                        _log(f"[{axis}] progress {n_done}/{len(jobs)}")
                        t_last = time.time()
        _log(f"[{axis}] DONE {n_done}/{len(jobs)} cells "
             f"({round(time.time() - t0, 1)}s cumulative)")
    _log(f"stage A complete in {round(time.time() - t0, 1)}s")
    return 0


# ------------------------------------------------------- fast/confirmed lines

def ladder_state(close: pd.Series, p: int = LADDER_P) -> pd.Series:
    """C1 (prereg s3): ma20>ma60 held P consecutive bars; dies the first bar
    ma20<=ma60 (asymmetric exit). Warmup = False."""
    ma20 = close.rolling(20).mean()
    ma60 = close.rolling(60).mean()
    up = (ma20 > ma60).fillna(False)
    held = up.copy()
    for k in range(1, p):
        held = held & up.shift(k, fill_value=False)
    return held.fillna(False).astype(bool)


def breadth_state(close: pd.DataFrame) -> pd.Series:
    """C2: share of members above own MA20 > 0.60 (reporting only)."""
    ma20 = close.rolling(20).mean()
    above = (close > ma20).sum(axis=1)
    valid = close.notna().sum(axis=1)
    return (above / valid.replace(0, np.nan) > 0.60).fillna(False)


def vol_state(close: pd.Series) -> pd.Series:
    """C3: vol20 > vol60 of daily returns (reporting only)."""
    r = close.pct_change()
    return (r.rolling(20).std() > r.rolling(60).std()).fillna(False)


def thrust_state(close: pd.Series) -> pd.Series:
    """C4: 20d return > +5% (reporting only)."""
    return (close / close.shift(20) - 1.0 > 0.05).fillna(False)


def deploy_series(axis: str, close: pd.DataFrame) -> pd.Series:
    """Confirmed deploy state, normalized 3-way: 'attack' / 'chop' / 'cash'.
    legacy = REGIME_GUARD v3 import-replay (GREEN->attack, YELLOW/ORANGE->
    chop, RED->cash); deep = T-22 frozen 3-way proxy (bull->attack,
    chop/na->chop, bear->cash) -- disclosed proxy, distinct from v3."""
    if axis == "legacy":
        from live.paper import v3_state_series
        st = v3_state_series()
        st = st.reindex(close.index).ffill()
        m = {"GREEN": "attack", "YELLOW": "chop", "ORANGE": "chop",
             "RED": "cash"}
        return st.map(lambda s: m.get(s, "chop"))
    prox = regime_proxy(close["510300"])
    return prox.map({"bull": "attack", "chop": "chop", "bear": "cash",
                     "na": "chop"})


def exec_shift(s: pd.Series) -> pd.Series:
    """T close decision -> T+1 open execution: weights at exec day t use the
    state resolved at the PRIOR panel row (shift(1); first row keeps its own
    state = no attack pre-positioning without a prior decision, disclosed)."""
    return s.shift(1, fill_value=s.iloc[0])


def weights_matrix(deploy_exec: pd.Series, fast_exec: pd.Series,
                   half: float = HALF) -> np.ndarray:
    """Full-panel corps weights (n_days x 3: attack/chop/cash), prereg s3:
    confirmed attack -> full; fast without confirmation -> attack at `half`,
    remainder to the confirmed-state corps; else confirmed corps alone."""
    dep = deploy_exec.to_numpy()
    fast = np.asarray(fast_exec, dtype=bool)
    W = np.zeros((len(dep), 3))
    for i, d in enumerate(dep):
        if d == "attack":
            W[i, 0] = 1.0
        elif fast[i]:
            W[i, 0] = half
            if d == "chop":
                W[i, 1] = 1.0 - half
            else:                      # cash or unknown -> cash remainder
                W[i, 2] = 1.0 - half
        elif d == "chop":
            W[i, 1] = 1.0
        else:
            W[i, 2] = 1.0
    return W


def conf_weights(deploy_exec: pd.Series) -> np.ndarray:
    """CONF arm: confirmed line only, zero attack pre-step."""
    dep = deploy_exec.to_numpy()
    W = np.zeros((len(dep), 3))
    for i, d in enumerate(dep):
        if d == "attack":
            W[i, 0] = 1.0
        elif d == "chop":
            W[i, 1] = 1.0
        else:
            W[i, 2] = 1.0
    return W


def env_daily(ret_att: np.ndarray, ret_chop: np.ndarray,
              W: np.ndarray, rate: float) -> np.ndarray:
    """env_ret(t) = sum_c w_c(t) r_c(t) - rate * sum_c |w_c(t)-w_c(t-1)|;
    initial deployment day of each window exempt (prereg s3 cost basis)."""
    core = W[:, 0] * ret_att + W[:, 1] * ret_chop
    dW = np.abs(np.diff(W, axis=0, prepend=W[:1])).sum(axis=1)
    dW[0] = 0.0
    return core - rate * dW


def _win_metrics(rets: np.ndarray, k: int, p_ret: float) -> dict:
    seg = rets[:min(k, len(rets))]
    if len(seg) < 2:
        return {"ret": 0.0, "dd": 0.0, "n_bars": int(len(seg)),
                "beat": False}
    eq = np.cumprod(1.0 + seg)
    peak = np.maximum.accumulate(eq)
    dd = float((eq / peak - 1.0).min())
    ret = float(eq[-1] - 1.0)
    return {"ret": ret, "dd": dd, "n_bars": int(len(seg)),
            "beat": bool(ret > p_ret)}


def _passive_window(close: pd.DataFrame, pos: int, k: int) -> float:
    """Passive window return (t22 passive caliber): EW buy&hold of members
    listed at the start over the window span."""
    idx = close.index
    sdate = idx[pos]
    e = idx[min(pos + k - 1, len(idx) - 1)]
    syms = close.columns[close.loc[sdate].notna()]
    base = close.loc[sdate, syms]
    seg = (close.loc[sdate:e, syms] / base).mean(axis=1).iloc[:k]
    if len(seg) < 2:
        return 0.0
    return float(seg.iloc[-1] - 1.0)


def _ci(k: int, n: int):
    if n == 0:
        return None, None
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    draws = rng.binomial(n, k / n, BOOTSTRAP_B) / n
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return round(float(lo), 4), round(float(hi), 4)


# ------------------------------------------------------------------ finalize

def _load_curves(axis: str):
    rows = {}
    with open(curve_path(axis), encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)     # corrupt mid-file = integrity abort
            rows[r["key"]] = r
    return rows


def _gate_v3() -> dict:
    cal = json.load(open(V3_FILE, encoding="utf-8-sig"))
    expect = {k: int(v) for k, v in cal["state_counts"].items()}
    from live.paper import v3_state_series
    st = v3_state_series()
    # calibration window is the comparison domain: the twin long-history
    # bench (T-18, landed r101) extends the replay back to 2012 -- pre-window
    # states are replay warmup, out of calibration scope; trim BOTH bounds.
    st = st[(st.index >= pd.Timestamp(cal["window"]["start"]))
            & (st.index <= pd.Timestamp(cal["window"]["end"]))]
    got = {k: int(v) for k, v in st.value_counts().items()}
    return {"ok": bool(got == expect), "expected": expect, "got": got,
            "window_days": int(len(st))}


def cmd_finalize(_) -> int:
    t0 = time.time()
    import hashlib
    _log("=== T34 finalize: gates -> overlay -> verdict (prereg s4) ===")
    from science_gates import COST_X2_RATE, append_ledger, cutoff_meta

    v3g = _gate_v3()
    _log(f"G-V3 {'PASS' if v3g['ok'] else 'FAIL'} {v3g['got']}")
    if not v3g["ok"]:
        return 2
    expected = _expected_starts()
    rate_side = COST_X2_RATE / 2.0          # engine base single-side rate
    _log(f"switch cost/side = {rate_side:.7f} (COST_X2_RATE/2, derived)")

    # audit block (prereg s0: no audit row -> not ledgered)
    try:
        subprocess.run([sys.executable, os.path.join(
            ROOT, "scripts", "compute_audit.py")],
            capture_output=True, text=True, timeout=180)
        aj = json.load(open(os.path.join(ROOT, "results",
                                         "compute_audit.json"),
                            encoding="utf-8-sig"))
        latest = aj.get("history", aj)
        if isinstance(latest, list) and latest:
            latest = latest[-1]
        audit = {"verdict": latest.get("verdict"),
                 "flags": latest.get("flags"),
                 "asof": latest.get("ts") or latest.get("asof")}
    except Exception as ex:
        audit = {"verdict": "unavailable", "error": str(ex)[:120]}
    audit_clean = audit.get("verdict") == "CLEAN"

    axes_out, verdicts = {}, {}
    probe_report = {"n": 0, "value_match": 0, "mismatches": []}

    for axis in ("legacy", "deep"):
        P = _axis_panel(axis)
        close = P["close"]
        idx = close.index
        curves = _load_curves(axis)
        listed = close.notna().sum(axis=1)
        eligible = enumerate_starts(len(idx), listed)
        if len(eligible) != expected[axis]:
            _log(f"G-CENSUS FAIL [{axis}] at finalize: {len(eligible)} "
                 f"!= {expected[axis]} -- abort")
            return 2
        need = {f"{m}|{p}" for p in eligible for m in ATTACK + CHOP}
        missing = sorted(need - set(curves))
        if missing:
            _log(f"coverage FAIL [{axis}]: {len(missing)} cells missing "
                 f"(e.g. {missing[:3]}) -- run stage A first")
            return 2

        # G-PROBE: determinism re-run of 12 fixed cells vs batch rows
        elig_set = set(eligible)
        probe_pos = [p for p in PROBE_POS if p in elig_set][:12]
        if len(probe_pos) < 12:
            probe_pos = list(eligible[:12])
        _init_worker(axis)
        for p in probe_pos:
            row = _run_cell_curve(ATTACK[0], p)
            ref = curves[f"{ATTACK[0]}|{p}"]
            probe_report["n"] += 1
            if row == ref:
                probe_report["value_match"] += 1
            else:
                probe_report["mismatches"].append(f"{ATTACK[0]}|{p}")
        _G.clear()
        if probe_report["mismatches"]:
            _log(f"G-PROBE FAIL: {probe_report['mismatches'][:4]} -- abort")
            return 2
        _log(f"G-PROBE PASS {probe_report['value_match']}/"
             f"{probe_report['n']} bit-equal [{axis}]")

        # ---- overlay: full-panel weight matrices once, per-startpoint
        # window slices (weights depend on state series only)
        dep_exec = exec_shift(deploy_series(axis, close))
        anchor = close["510300"]
        fast_exec = {
            "C1": exec_shift(ladder_state(anchor)),
            "C2": exec_shift(breadth_state(close)),
            "C3": exec_shift(vol_state(anchor)),
            "C4": exec_shift(thrust_state(anchor)),
        }
        arms = {"conf": conf_weights(dep_exec)}
        arms["C1"] = weights_matrix(dep_exec, fast_exec["C1"], HALF)
        for k in (2, 3, 4):
            arms[f"C{k}"] = weights_matrix(dep_exec, fast_exec[f"C{k}"],
                                          HALF)
        for h in SENS_HALF:
            arms[f"h{int(h * 100)}"] = weights_matrix(dep_exec,
                                                      fast_exec["C1"], h)

        att_rets = {p: np.asarray(curves[f"{ATTACK[0]}|{p}"]["curve"],
                                  dtype=float) for p in eligible}
        chop_rets = {p: np.mean(
            [np.asarray(curves[f"{m}|{p}"]["curve"], dtype=float)
             for m in CHOP], axis=0) for p in eligible}

        def overlay(arm):
            W = arms[arm]
            cells = {}
            for p in eligible:
                n = min(W24M, len(idx) - p)
                Wp = W[p:p + n]
                r = env_daily(att_rets[p], chop_rets[p], Wp, rate_side)
                m6 = _win_metrics(r, W6M, _passive_window(close, p, W6M))
                m12 = _win_metrics(
                    r, W12M, curves[f"{ATTACK[0]}|{p}"]["p_ret_12m"])
                m24 = _win_metrics(r, W24M, _passive_window(close, p, W24M))
                sw = int((np.abs(np.diff(Wp, axis=0,
                                         prepend=Wp[:1])).sum(axis=1)
                                 > 0).sum())
                cells[p] = {"pos": p,
                            "start": curves[f"{ATTACK[0]}|{p}"]["start"],
                            "n_bars": int(len(r)),
                            "partial_12m": m12["n_bars"] < W12M,
                            "partial_24m": m24["n_bars"] < W24M,
                            "ret_6m": m6["ret"], "ret_12m": m12["ret"],
                            "ret_24m": m24["ret"], "dd_12m": m12["dd"],
                            "dd_24m": m24["dd"],
                            "beat_6m": m6["beat"], "beat_12m": m12["beat"],
                            "beat_24m": m24["beat"], "switches": sw}
            return cells

        def agg(cells):
            full = [c for c in cells.values() if not c["partial_12m"]]
            n = len(full)
            k12 = sum(1 for c in full if c["beat_12m"])
            dds = [c["dd_12m"] for c in full]
            sws = [c["switches"] for c in full]
            rate = k12 / n if n else None
            lo, hi = _ci(k12, n)
            return {"n": n, "beats_12m": k12,
                    "beat_rate_12m": round(rate, 4)
                    if rate is not None else None,
                    "ci95": [lo, hi],
                    "min_dd_12m": round(min(dds), 4) if dds else None,
                    "mean_dd_12m": round(sum(dds) / len(dds), 4),
                    "switches_mean": round(sum(sws) / len(sws), 2),
                    "switches_median": round(float(np.median(sws)), 1),
                    "switches_max": int(max(sws))}

        conf = overlay("conf")
        lad = overlay("C1")
        a_conf, a_lad = agg(conf), agg(lad)
        uplift = (round(a_lad["beat_rate_12m"] - a_conf["beat_rate_12m"], 4)
                  if a_lad["beat_rate_12m"] is not None else None)
        paired = {"L+_R-": 0, "L-_R+": 0}
        for p in eligible:
            c, l = conf[p], lad[p]
            if c["partial_12m"]:
                continue
            if l["beat_12m"] and not c["beat_12m"]:
                paired["L+_R-"] += 1
            elif c["beat_12m"] and not l["beat_12m"]:
                paired["L-_R+"] += 1
        sens = {}
        for name in ("C2", "C3", "C4", "h25", "h75"):
            s = agg(overlay(name))
            sens[name] = {"uplift_12m":
                          round(s["beat_rate_12m"] - a_conf["beat_rate_12m"],
                                4) if s["beat_rate_12m"] is not None
                          else None,
                          "switches_mean": s["switches_mean"],
                          "min_dd_12m": s["min_dd_12m"]}
        n_fires = int((np.diff(fast_exec["C1"].to_numpy().astype(int))
                       > 0).sum())
        axes_out[axis] = {
            "n_starts": len(eligible),
            "confirmed_line": ("REGIME_GUARD v3 import-replay"
                               if axis == "legacy" else
                               "T-22 3-way proxy (disclosed, non-v3)"),
            "conf": a_conf, "ladder_C1": a_lad, "uplift_12m": uplift,
            "paired_discordance_12m": paired,
            "ladder_fires_full_history": n_fires,
            "sensitivity": sens,
            "cells": {"conf": len(conf), "ladder": len(lad)},
        }
        verdicts[axis] = {
            "j1_uplift_positive": bool(uplift is not None and uplift > 0),
            "j2_dd_ok": bool(a_lad["min_dd_12m"] is not None
                             and a_lad["min_dd_12m"] >= DD_RED_LINE),
        }
        _log(f"[{axis}] CONF 12m={a_conf['beat_rate_12m']} LADDER 12m="
             f"{a_lad['beat_rate_12m']} uplift={uplift} minDD(ladder)="
             f"{a_lad['min_dd_12m']} switches "
             f"{a_conf['switches_mean']}->{a_lad['switches_mean']} "
             f"paired={paired}")

    j1 = all(v["j1_uplift_positive"] for v in verdicts.values())
    j2 = all(v["j2_dd_ok"] for v in verdicts.values())
    passed = bool(j1 and j2)

    # ledger: 2 arms x n_starts envelope cells; curves NOT re-counted
    n_starts = sum(axes_out[a]["n_starts"] for a in axes_out)
    batch_trials = 2 * n_starts
    if audit_clean:
        ledger = append_ledger(
            BATCH, batch_trials, file_name="t34_early_signal_verdict.json",
            evidence_cutoff=BINDING_CUTOFF,
            note=(f"envelope A/B cells 2 arms x {n_starts} starts (legacy "
                 f"{axes_out['legacy']['n_starts']} + deep "
                 f"{axes_out['deep']['n_starts']}); stage-A member curves "
                 f"= T-22-counted cells re-derivation, not re-counted; "
                 f"probe {probe_report['n']} not counted (dprobe "
                 f"precedent)"))
    else:
        ledger = {"prev_total": None, "batch_trials": batch_trials,
                  "total": None,
                  "note": "audit not CLEAN - not counted per prereg s0"}

    with open(PREREG_PATH, "rb") as f:
        prereg_sha = hashlib.sha256(f.read()).hexdigest()
    out = {
        "batch": BATCH, "ticket": TICKET,
        "prereg": "research/T34_EARLY_SIGNAL.md",
        "prereg_sha256": prereg_sha,
        "evidence_cutoff": BINDING_CUTOFF,
        "cutoff_meta": cutoff_meta(BINDING_CUTOFF),
        "axis_cutoffs": {"legacy": LEGACY_CUTOFF, "deep": BINDING_CUTOFF},
        "frozen_judgments": {
            "J1": "pooled 12m beat uplift (LADDER-CONF) > 0 on BOTH axes",
            "J2": "worst-start 12m dd (LADDER) >= -0.35 on both axes",
            "J3": "whipsaw switch counts disclosed (no gate)",
            "PASS": "J1 AND J2; FAIL -> keep confirmed-only (O-2030 s3)"},
        "gates": {"G_V3": v3g, "G_CENSUS_expected": expected,
                  "G_PROBE": probe_report,
                  "G_ANCHOR": "6/6 at stage-A start"},
        "half_step": HALF, "ladder_p": LADDER_P,
        "switch_cost_per_side": rate_side,
        "axes": axes_out,
        "verdict": {"j1": j1, "j2": j2, "pass": passed,
                    "per_axis": verdicts,
                    "disposition": (
                        "ladder ENABLED candidate -> T-33 d3 router spec "
                        "+ monthly-boundary wiring batch (NO activation "
                        "here)" if passed else
                        "honest negative -> keep confirmed-only switching "
                        "(O-2030 s3 verbatim)")},
        "bootstrap": {"B": BOOTSTRAP_B, "seed": BOOTSTRAP_SEED,
                      "method": "binomial percentile 95% CI"},
        "trials_ledger": ledger,
        "audit": audit,
        "finalize_runtime_sec": round(time.time() - t0, 1),
    }
    jpath = os.path.join(ROOT, "results", "t34_early_signal_verdict.json")
    tmp = jpath + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False, default=bool)
    os.replace(tmp, jpath)
    _log(f"verdict {'PASS' if passed else 'FAIL'} -> {jpath}")

    # aggregated CSV (small, git)
    csv_path = os.path.join(ROOT, "research", "shortline",
                            "t34_envelope_results.csv")
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("axis,arm,n,beat_rate_12m,ci95_lo,ci95_hi,min_dd_12m,"
                "mean_dd_12m,switches_mean,switches_max,uplift_12m\n")
        rows = []
        for ax, o in axes_out.items():
            for arm, a in (("conf", o["conf"]), ("ladder_C1",
                                                 o["ladder_C1"])):
                rows.append((ax, arm, a["n"], a["beat_rate_12m"],
                             a["ci95"][0], a["ci95"][1], a["min_dd_12m"],
                             a["mean_dd_12m"], a["switches_mean"],
                             a["switches_max"],
                             o["uplift_12m"] if arm == "ladder_C1"
                             else ""))
        for r in rows:
            fh.write(",".join(str(x) for x in r) + "\n")
    _log(f"csv -> {csv_path} ({len(rows)} rows)")

    # attrition row (s7-T)
    attr = os.path.join(ROOT, "results", "gate_attrition.json")
    d = json.load(open(attr, encoding="utf-8-sig"))
    d["entries"].append({
        "batch": BATCH, "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "kind": "measurement", "retro_fill": False,
        "cells_ledger_delta": batch_trials if audit_clean else 0,
        "ledger_total_after": (ledger or {}).get("total"),
        "gates": {"j1_uplift_legacy": axes_out["legacy"]["uplift_12m"],
                  "j1_uplift_deep": axes_out["deep"]["uplift_12m"],
                  "j2_min_dd_ladder_legacy":
                      axes_out["legacy"]["ladder_C1"]["min_dd_12m"],
                  "j2_min_dd_ladder_deep":
                      axes_out["deep"]["ladder_C1"]["min_dd_12m"],
                  "pass": passed, "void": False},
        "eliminated": None,
        "refs": {"results": "results/t34_early_signal_verdict.json",
                 "prereg": "research/T34_EARLY_SIGNAL.md",
                 "csv": "research/shortline/t34_envelope_results.csv",
                 "ticket": f"fleet/tasks/{TICKET}-P1.json"},
        "note": "routing-rule A/B (no member registration); curves = "
                "T-22 cell re-derivation, not re-counted"})
    json.dumps(d)                       # validate before write (r91 law)
    with open(attr, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    _log(f"finalize DONE in {round(time.time() - t0, 1)}s")
    return 0


# ----------------------------------------------------------------- selftest

def cmd_selftest(_) -> int:
    fails = []

    def t(name, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")
        if not ok:
            fails.append(name)

    # S1: C1 ladder state machine (fire on the 5th up-bar; asymmetric die)
    idx = pd.bdate_range("2020-01-01", periods=500)
    up = pd.Series(np.linspace(100, 300, 500), index=idx)
    dn = pd.Series(np.linspace(300, 100, 500), index=idx)
    s_up = ladder_state(up, 5)
    s_dn = ladder_state(dn, 5)
    t("S1 ladder fires on 5th cross-up bar, not before",
      bool(s_up.iloc[63]) and not bool(s_up.iloc[62])
      and not bool(s_dn.iloc[64:].any()))
    # die-immediacy: rise then sustained crash -> held False from the very
    # first ma20<=ma60 bar (no exit persistence, asymmetric by design)
    crash = pd.Series(np.concatenate([
        np.linspace(100, 300, 300), np.linspace(300, 50, 200)]), index=idx)
    up_st = (crash.rolling(20).mean() > crash.rolling(60).mean())
    up_st = up_st.fillna(False)
    first_dn = int(np.argmax(~up_st.to_numpy()[300:])) + 300
    s_crash = ladder_state(crash, 5)
    t("S1b asymmetric exit: dies the first cross-down bar",
      bool(not s_crash.iloc[first_dn])
      and bool(s_crash.iloc[first_dn - 1])
      and not bool(s_crash.iloc[first_dn:].any()))

    # S2: weight construction cases
    dep = pd.Series(["chop", "cash", "attack", "chop", "chop"],
                    index=range(5))
    fast = pd.Series([True, True, True, True, False], index=range(5))
    W = weights_matrix(dep, fast, 0.5)
    t("S2 weights: half-step blend / cash-half / confirmed-dominates / "
      "revert",
      W[0].tolist() == [0.5, 0.5, 0.0]
      and W[1].tolist() == [0.5, 0.0, 0.5]
      and W[2].tolist() == [1.0, 0.0, 0.0]
      and W[4].tolist() == [0.0, 1.0, 0.0])
    Wc = conf_weights(dep)
    t("S2b CONF arm zero attack pre-step",
      Wc[:, 0].sum() == 1.0 and Wc[0].tolist() == [0.0, 1.0, 0.0]
      and Wc[1].tolist() == [0.0, 0.0, 1.0])

    # S3: causality (T close -> T+1 exec)
    st = pd.Series(["chop"] * 10, index=range(10))
    st.iloc[5] = "attack"
    ex = exec_shift(st)
    t("S3 exec shift: state flip at k lands at k+1",
      ex.iloc[5] == "chop" and ex.iloc[6] == "attack")

    # S4: switch-cost arithmetic
    Wx = np.array([[0.0, 1.0, 0.0], [0.5, 0.5, 0.0], [0.5, 0.5, 0.0]])
    r = env_daily(np.zeros(3), np.zeros(3), Wx, 0.0013)
    t("S4 cost: half shift charged once (rate x |dW|=1.0), day0 + flat "
      "days free",
      abs(r[0]) < 1e-12 and abs(r[1] + 0.0013) < 1e-9
      and abs(r[2]) < 1e-12)

    # S5: envelope composition math
    ra = np.array([0.01, 0.02, 0.0])
    rc = np.array([0.0, 0.0, 0.01])
    W5 = np.array([[0.5, 0.5, 0.0]] * 3)
    r5 = env_daily(ra, rc, W5, 0.0)
    t("S5 env rets = weighted blend",
      abs(r5[0] - 0.005) < 1e-12 and abs(r5[2] - 0.005) < 1e-12)
    m = _win_metrics(r5, 2, 0.001)
    t("S5b window metrics + beat flag",
      abs(m["ret"] - ((1.005 * 1.010) - 1)) < 1e-9 and m["beat"] is True)

    # S6: bootstrap determinism
    c1 = _ci(7, 10)
    c2 = _ci(7, 10)
    t("S6 bootstrap deterministic (seed 20260928)",
      c1 == c2 and c1[0] < 0.7 < c1[1])

    # S7: t22 primitive imports intact
    t("S7 frozen window constants",
      W6M == 126 and W12M == 252 and W24M == 504 and WARMUP_TD == 252)

    # S8: J1/J2 semantics
    v = {"legacy": {"j1_uplift_positive": True, "j2_dd_ok": True},
         "deep": {"j1_uplift_positive": False, "j2_dd_ok": True}}
    j1 = all(x["j1_uplift_positive"] for x in v.values())
    j2 = all(x["j2_dd_ok"] for x in v.values())
    t("S8 J1 dual-axis conjunction (one negative kills)",
      j1 is False and j2 is True and (j1 and j2) is False)

    # S9: partial-window semantics (t22 caliber: >=2 bars evaluable, the
    # complete-window gate happens upstream via n_bars < k)
    m9 = _win_metrics(np.array([0.01, 0.02]), 12, 0.0)
    t("S9 partial window: n_bars<12 flag source, 2-bar slice still "
      "evaluable",
      m9["n_bars"] == 2 and m9["n_bars"] < 12 and m9["beat"] is True)

    # S10: passive caliber equals t22 formula on synthetic panel
    cl = pd.DataFrame({"A": np.linspace(100, 120, 300),
                       "B": np.linspace(50, 60, 300)},
                      index=pd.bdate_range("2020-01-01", periods=300))
    mine = _passive_window(cl, 10, 126)
    idxs = cl.index
    sdate = idxs[10]
    e = idxs[min(10 + 126 - 1, len(idxs) - 1)]
    syms = cl.columns[cl.loc[sdate].notna()]
    base = cl.loc[sdate, syms]
    ref = float((cl.loc[sdate:e, syms] / base).mean(axis=1).iloc[-1] - 1.0)
    t("S10 passive caliber == t22 formula", abs(mine - ref) < 1e-12)

    # S11: frozen constants
    t("S11 prereg constants",
      LADDER_P == 5 and HALF == 0.5 and SENS_HALF == (0.25, 0.75)
      and DD_RED_LINE == -0.35 and BOOTSTRAP_B == 2000
      and BOOTSTRAP_SEED == 20260928 and LEGACY_CUTOFF == "2026-09-23"
      and BINDING_CUTOFF == "2026-09-22"
      and ATTACK == ["COMPOSITE-CE-01"] and len(CHOP) == 5)

    print(f"\nselftest: "
          f"{'ALL PASS' if not fails else 'FAIL x' + str(len(fails))}")
    return 0 if not fails else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--axis", choices=["all", "legacy", "deep"],
                   default="all")
    r.add_argument("--workers", type=int, default=0)
    r.add_argument("--limit", type=int, default=0)
    sub.add_parser("finalize")
    sub.add_parser("selftest")
    args = ap.parse_args()
    if args.cmd == "run":
        return cmd_run(args)
    if args.cmd == "finalize":
        return cmd_finalize(args)
    return cmd_selftest(args)


if __name__ == "__main__":
    sys.exit(main())
