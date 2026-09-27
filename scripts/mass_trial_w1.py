"""MASS_TRIAL_W1 -- thousand-trader mass candidate trial, wave-1 (T-2026-09-27-94,
CEO direct order O-2026-09-27-2245 + standing law O-2026-09-27-2250 /
firm/TRIAL_LABOR_LAW.md v1.0).

Three-layer funnel (prereg research/MASS_TRIAL_W1_PREREG.md, FROZEN before any
run per R99; seed base mass_trial_w1=20283000 registered in science_gates
SEED_REGISTRY at the same freeze commit):

  generate  enumerate the FROZEN grammar (75 factory signal families across 11
            modules, zero invention -- source-sha anchored) x generic mechanical
            param ranges x refine-bench axes (regime gate x exit x sizing x
            timing) x per-family Sobol 500-draw frames -> signal-hash dedup ->
            enroll <=13/family (<=975 candidates, ceiling-not-quota per CEO order)
  screen    stage-1 funnel face: ONE full-history base-face engine run per
            candidate (2020-01-02..cutoff, T+1, V1 legacy cost always on,
            engine default sizing) -> rolling 6m-window beat-rate vs same-window
            EW48 passive + descriptive stats; CHEAP SCREEN FACE, disclosed as a
            funnel stage (survivors get the real s3 full-judgment funnel -- a
            separate per-stage freeze before that burn)
  selftest  offline machinery assertions (zero network, zero engine runs)

s3 JUDGE face (prereg sec.9.1 FROZEN 2026-09-28 r350 bm-b, commit-before-burn;
seed mass_trial_w1_judge=20285000 registered at the same freeze window):

  judge-prep        dual-leg census gates (p5c FROZEN_CENSUS wholesale import,
                    sec.9.3 caliber) + candidates-sha anchor gate + t18
                    manifest gate + |corr|>=0.999 leg-L daily-returns dedup
                    (representative = deterministic lowest candidate_id) ->
                    results/mass_trial/judge_state.json (starts + passive per
                    (leg, window, start) + collapse audit)
  judge             sharded judged-cell burn: per collapsed survivor = frozen
                    config replay through BOTH legs (L 2020-01-02..cutoff, D
                    t18 deep cache 2013-06-17..cutoff) x BOTH cost faces
                    (x1 engine default, x2 CostPatch(2.0)) x window grid
                    {126,252,504} sliced from full curves (P-5 slicing caliber,
                    wave-1b sec.9.3 same-source) + regime segments
                    (T-22 sec.3 frozen 3-way proxy) + dual nulls (B=2000
                    block bootstrap block=20 circular + P=2000 sign-flip,
                    rng=[20285000, cell_idx], resample faces only) + G1'/DSR
                    inputs + descriptive clauses; jsonl checkpoint per cell
  judge-finalize    family PBO (CSCV 8 blocks, family = 11 strategy modules,
                    <8 cells -> honest n/a) + G2 via science_gates shared lib
                    + E[FP]=0.05*N_judge + ledger append MASS_TRIAL_W1_JUDGE
                    (N_judge = post-collapse cells) + w1_judge.json product

Class per prereg: candidate-search funnel (stage-1 = screen, NOT a judgment
face; zero registration effect from stage-1 alone). Ledger append happens at
screen finalize with actual enrolled-candidate counts only; the JUDGE batch
appends its own N_judge cells at judge-finalize (chain-linear, live head read,
never hand-copied).

Cross-round discipline: detached/pool burn, JSONL checkpoint per candidate
(append-only, resume = skip recorded ids), shard by --pos-from/--pos-to over
the deterministic combined list (candidates + family-default controls +
random-entry nulls). Workers = floor(cores x 0.8) at BelowNormal per O-1136.
"""
import argparse
import hashlib
import inspect
import importlib
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

from config import PATHS
from engine import run_backtest
from engine.metrics import max_drawdown, sharpe
from live.paper import v3_state_series
from p5_random_entry import WARMUP_TD, passive_rel
from parallel_runner import run_cells_parallel, worker_cap
from p5c_virtual_timepoint import (EVIDENCE_CUTOFF_GRID, FROZEN_CENSUS,
                                   LEG_D_CACHE, LEG_D_FLOOR, LEG_L_FLOOR,
                                   MIN_LISTED, REGIME_MAP, WINDOWS, _load_leg)
from screening.pbo import align_returns, cscv_pbo
from scripts import science_gates as sg

BATCH = "MASS_TRIAL_W1"
TICKET = "T-2026-09-27-94"
CUTOFF = "2026-09-22"                # frozen evidence_cutoff anchor (prereg sec.2)
WARMUP = 252                        # eligible 6m-window start positions (T-22 caliber)
W6M, STRIDE = 126, 21               # 6m window / monthly stride
BEAT_LINE = 0.60                    # frozen stage-1 funnel line (prereg sec.4)
DD_LINE = -0.35
TRADES_GATE = 30
QUOTA_PER_FAMILY = 13               # 75 x 13 = 975 <= 1000 ceiling
N_DRAWS = 512                       # per-family space-filling frame (RLSL sec.2,
                                    # 2^9 power-of-two Sobol balance >= 500)
MODULES = ["trend", "mean_reversion", "momentum", "volatility", "sentiment",
           "seasonal", "event", "macro", "ta", "patterns", "folk"]
SEED_BASE = sg.SEED_REGISTRY["mass_trial_w1"]          # 20283000 band
NULL_SEED_OFF = 100                                   # nulls: base+100..+119
# ---- s3 judge face (prereg sec.9.1 FROZEN; seed band 20285000..20285199)
JUDGE_BATCH = "MASS_TRIAL_W1_JUDGE"
JUDGE_SEED = sg.SEED_REGISTRY["mass_trial_w1_judge"]    # 20285000
CANDIDATES_SHA_FROZEN = "907e44d56999b0ab"             # w1_candidates.json anchor
OOS_START_TS = pd.Timestamp("2025-01-01")              # OOS blind face
CRASH_YEAR = -0.30                                     # ce_transfer convention
T18_MANIFEST = os.path.join(PATHS.results_dir, "shortline",
                            "t18_deep_manifest.json")
DATA_ARGS = ("close", "high", "low", "open", "open_", "volume", "amount", "bench")
# frozen generic range rules (prereg sec.3 -- mechanical, zero semantic guessing)
ENUM_RANGES = {"month": (1, 12), "weekday": (0, 4), "oversold": (15, 40),
               "overbought": (60, 85), "entry_j": (15, 35), "exit_j": (65, 85)}
PAIR_ORDER = [("fast", "slow"), ("n1", "n2"), ("n2", "n3"),
              ("oversold", "overbought"), ("entry_j", "exit_j")]
AX_R = ["none", "bull", "bear"]      # 510300-vs-MA200 entry gate
AX_X = ["own", "t5", "t7", "t10", "t20"]   # own paired exit | rising-edge + N-day time exit
AX_S = ["full", "delever"]           # full nominal | 0.5 when bear (engine entry_size_scale)
AX_T = ["daily", "weekly"]           # daily eval | first-trading-day-of-week only
OUT_DIR = os.path.join("results", "mass_trial")
JUDGE_STATE = os.path.join(OUT_DIR, "judge_state.json")
JUDGE_OUT = os.path.join(OUT_DIR, "w1_judge.json")


# --------------------------------------------------------------- panel loading

def _load_bench():
    """csi300 index series truncated to CUTOFF (single source, screen face
    verbatim; extracted so the judge legs reuse the exact same bench)."""
    bench = pd.read_csv(os.path.join(PATHS.basic_dir, "csi300.csv"),
                        parse_dates=["date"]).set_index("date")["close"].sort_index()
    return bench[bench.index <= pd.Timestamp(CUTOFF)]


def load_panel():
    """core48 bare-code panel truncated to CUTOFF + bench + prices dict.
    Mirrors p1_strategy_screen.load_core verbatim (J6 definition) + cutoff
    truncation (prereg sec.2 forward lockbox)."""
    out, prices = {}, {}
    for f in sorted(os.listdir(PATHS.daily_dir)):
        if not (f.endswith(".csv") and f[:-4].isdigit()):
            continue
        df = pd.read_csv(os.path.join(PATHS.daily_dir, f), parse_dates=["date"])
        df = df.set_index("date").sort_index()
        df = df[df.index <= pd.Timestamp(CUTOFF)]          # cutoff lock
        if len(df) < 60:
            continue
        if "open" not in df.columns:
            df["open"] = df["close"]
        if "amount" not in df.columns:
            df["amount"] = df["volume"] * df["close"]
        sym = f[:-4]
        out[sym] = df[["open", "high", "low", "close", "volume", "amount"]]
        prices[sym] = out[sym]
    return out, prices, _load_bench()


def panels_from(raw: dict):
    close = pd.DataFrame({s: d["close"] for s, d in raw.items()}).sort_index()
    high = pd.DataFrame({s: d["high"] for s, d in raw.items()}).reindex(close.index)
    low = pd.DataFrame({s: d["low"] for s, d in raw.items()}).reindex(close.index)
    opn = pd.DataFrame({s: d["open"] for s, d in raw.items()}).reindex(close.index)
    vol = pd.DataFrame({s: d["volume"] for s, d in raw.items()}).reindex(close.index)
    amt = pd.DataFrame({s: d["amount"] for s, d in raw.items()}).reindex(close.index)
    return {"close": close, "high": high, "low": low, "open": opn,
            "volume": vol, "amount": amt}


# ------------------------------------------------------------- grammar roster

def _series_annotated(p) -> bool:
    a = p.annotation
    return a is not inspect.Parameter.empty and getattr(a, "__name__", "") == "Series"


def _frame_annotated(p) -> bool:
    a = p.annotation
    return a is not inspect.Parameter.empty and getattr(a, "__name__", "") == "DataFrame"


def _param_range(name, default):
    """Frozen mechanical range rule (prereg sec.3). Returns (low, high, is_int)
    or None when the parameter is outside the rule table -> family excluded."""
    if name in ENUM_RANGES:
        lo, hi = ENUM_RANGES[name]
        if default is inspect.Parameter.empty or isinstance(default, int):
            return lo, hi, True
        return lo, hi, float(default).is_integer()
    if default is None:
        # None-default params are HELD at the function-internal default (not
        # sampled) -- frozen mechanical rule, disclosed in prereg sec.3
        return None, None, False
    if default is inspect.Parameter.empty or isinstance(default, bool):
        return None
    if isinstance(default, int):
        return max(2, -(-default // 2)), 2 * default, True
    if isinstance(default, float):
        lo, hi = 0.5 * default, 2.0 * default
        if lo > hi:
            lo, hi = hi, lo
        return lo, hi, False
    return None


def build_roster():
    """Deterministic family roster: 75 factory functions, mechanical kind
    detection (macro module = P1 macro_panel overlay semantics), generic
    param ranges, source sha anchor. Excluded families listed with reasons."""
    roster, excluded = [], []
    for mname in MODULES:
        mod = importlib.import_module("strategies." + mname)
        fns = [(n, f) for n, f in sorted(vars(mod).items())
               if inspect.isfunction(f) and not n.startswith("_")
               and getattr(f, "__module__", "").endswith(mname)]
        for fname, fn in fns:
            sig = inspect.signature(fn)
            data_args = [p for p in sig.parameters.values()
                         if p.name in DATA_ARGS]
            params = [p for p in sig.parameters.values()
                     if p.name not in DATA_ARGS]
            ranges, ok = {}, True
            for p in params:
                r = _param_range(p.name, p.default)
                if r is None:
                    ok = False
                    excluded.append({"family": f"{mname}.{fname}",
                                     "reason": f"param {p.name}="
                                               f"{getattr(p.default, 'name', repr(p.default))} "
                                               "outside frozen rule table"})
                    break
                if r[0] is None:      # None-default -> held at internal default
                    ranges[p.name] = {"held_none": True,
                                       "default": p.default}
                else:
                    ranges[p.name] = {"default": None if p.default is inspect.Parameter.empty
                                      else p.default, "low": r[0],
                                      "high": r[1], "int": r[2]}
            if not ok:
                continue
            if mname == "macro":
                kind = "macro"
            elif data_args and _series_annotated(data_args[0]):
                kind = "sym"
            elif data_args and _frame_annotated(data_args[0]):
                ret = sig.return_annotation
                ret_name = getattr(ret, "__name__", str(ret))
                kind = "panel" if "DataFrame" in ret_name else "mask"
            else:
                excluded.append({"family": f"{mname}.{fname}",
                                 "reason": "unannotated first data arg"})
                continue
            src = inspect.getsource(fn).encode("utf-8")
            roster.append({"idx": len(roster), "family": f"{mname}.{fname}",
                           "module": mname, "fn": fname, "kind": kind,
                           "ranges": ranges,
                           "src_sha256": hashlib.sha256(src).hexdigest()[:16],
                           "needs_bench": any(p.name == "bench" for p in data_args)})
    return roster, excluded


# ---------------------------------------------------------------- sampling

def sample_draws(fam, n=N_DRAWS):
    """Per-family deterministic 500-draw frame: Sobol over the normalized
    param box (seed = SEED_BASE + family idx, RLSL sec.2 space filling) +
    axis draws from a seeded RNG stream. Yields (draw_idx, params, axes).
    held_none params are NOT sampled (stay at function-internal default)."""
    from scipy.stats import qmc
    names = sorted(nm for nm in fam["ranges"]
                   if not fam["ranges"][nm].get("held_none"))
    if names:
        sob = qmc.Sobol(len(names), scramble=True,
                        seed=SEED_BASE + fam["idx"])
        box = sob.random(n)
    else:
        box = np.zeros((n, 0))
    rng = np.random.default_rng([SEED_BASE + fam["idx"], 7919])
    axes = list(zip(rng.integers(0, len(AX_R), n),
                    rng.integers(0, len(AX_X), n),
                    rng.integers(0, len(AX_S), n),
                    rng.integers(0, len(AX_T), n)))
    for i in range(n):
        params = {}
        for j, nm in enumerate(names):
            r = fam["ranges"][nm]
            v = r["low"] + box[i, j] * (r["high"] - r["low"])
            params[nm] = int(round(v)) if r["int"] else round(float(v), 6)
        r_, x_, s_, t_ = axes[i]
        yield i, params, {"R": AX_R[r_], "X": AX_X[x_],
                          "S": AX_S[s_], "T": AX_T[t_]}


def draw_valid(fam, params) -> bool:
    """Frozen pairwise ordering validity (prereg sec.3)."""
    r = fam["ranges"]
    for a, b in PAIR_ORDER:
        if a in params and b in params:
            if not (params[a] < params[b]):
                # range-table disjointness normally guarantees this; reject
                # any residual overlap draws honestly
                return False
    return True


def param_hash(fam, params, axes):
    return hashlib.sha256(json.dumps(
        [fam["family"], params, axes], sort_keys=True,
        default=str).encode()).hexdigest()[:24]


# ------------------------------------------------------------ signal dispatch

class Ctx:
    """Panel context shared by the dispatcher (built once per process)."""

    def __init__(self):
        raw, self.prices, self.bench = load_panel()
        self._build(raw)

    @classmethod
    def from_raw(cls, raw, bench):
        """Judge-leg panel context (prereg sec.9.1: same mask machinery as
        the screen face, zero rewrite -- leg-L / leg-D replay caliber)."""
        obj = object.__new__(cls)
        obj.prices = raw
        obj.bench = bench
        obj._build(raw)
        return obj

    def _build(self, raw):
        P = panels_from(raw)
        self.P = P
        self.close, self.high, self.low = P["close"], P["high"], P["low"]
        self.opn, self.vol, self.amt = P["open"], P["volume"], P["amount"]
        self.syms = list(self.close.columns)
        self.idx = self.close.index
        bench = self.bench.reindex(self.idx).ffill()
        ma200 = bench.rolling(200).mean()
        self.bull_mask = (bench >= ma200)
        self.bear_mask = (bench < ma200)
        self.week_mask = pd.Series(
            np.r_[True, np.diff(self.idx.dayofweek) < 0], index=self.idx)
        # S-axis scale indexed at EXECUTION day E reflects info through close
        # E-1 (engine T-21 contract) -> shift(1) of the bear state
        self.delever_scale = (pd.Series(
            np.where(self.bear_mask, 0.5, 1.0), index=self.idx)).shift(1).fillna(1.0)
        f, s = self.close.rolling(5).mean(), self.close.rolling(20).mean()
        self.ma_entry = ((f > s) & (f.shift(1) <= s.shift(1))).fillna(False)
        self.ma_exit = ((f < s) & (f.shift(1) >= s.shift(1))).fillna(False)
        rets = self.close.pct_change().fillna(0.0)
        self.ew_curve = (1.0 + rets.mean(axis=1)).cumprod()
        self.roster, self.excluded = build_roster()

    # -- raw family call (kind dispatch mirrors p1_strategy_screen verbatim) --

    def call_family(self, fam, params):
        mod = importlib.import_module("strategies." + fam["module"])
        fn = getattr(mod, fam["fn"])
        kw = dict(params)
        if fam["kind"] == "macro":
            # P1 macro_panel pattern: benchmark series into every Series data
            # arg (1 or 2 args per signature), market-level mask overlay
            n_series = len([nm for nm in inspect.signature(fn).parameters
                            if nm in DATA_ARGS])
            pos = fn(*([self.bench] * n_series), **kw)
            m = pos.reindex(self.idx).fillna(False).astype(bool)
            e = pd.DataFrame(np.tile(m.values[:, None], (1, len(self.syms))),
                             index=self.idx, columns=self.syms)
            return e, ~e
        if fam["kind"] == "sym":
            series_map = {"close": self.close, "high": self.high,
                          "low": self.low, "open": self.opn, "open_": self.opn,
                          "volume": self.vol, "amount": self.amt}
            fn_params = inspect.signature(fn).parameters
            data_args = [nm for nm, p in fn_params.items()
                         if nm in DATA_ARGS and nm != "bench"]
            cols = {}
            for sm in self.syms:
                args = [series_map[a][sm] for a in data_args]
                if "bench" in fn_params:
                    args.append(self.bench)
                cols[sm] = fn(*args, **kw)
            pos = pd.DataFrame(cols, index=self.idx).fillna(0)
            return (pos > 0), (pos <= 0)
        # panel / mask kinds: first data arg is a panel frame
        fn_params = inspect.signature(fn).parameters
        data_args = [nm for nm, p in fn_params.items()
                     if nm in DATA_ARGS and nm != "bench"]
        frames = {"close": self.close, "high": self.high, "low": self.low,
                  "open": self.opn, "open_": self.opn, "volume": self.vol,
                  "amount": self.amt}
        args = [frames[a] for a in data_args]
        if "bench" in fn_params:
            args.append(self.bench)
        out = fn(*args, **kw)
        if fam["kind"] == "mask":
            m = out.reindex(self.idx).fillna(False).astype(bool)
            e = pd.DataFrame(np.tile(m.values[:, None], (1, len(self.syms))),
                             index=self.idx, columns=self.syms)
            return e, ~e
        w = out.reindex(index=self.idx, columns=self.syms).fillna(0.0)
        return (w > 0).fillna(False), (w <= 0)

    # -- axis application (prereg sec.3) --

    def build_signals(self, fam, params, axes):
        e, x = self.call_family(fam, params)
        if axes["R"] == "bull":
            e = e & pd.DataFrame(np.tile(self.bull_mask.values[:, None],
                                         (1, len(self.syms))), index=self.idx,
                                 columns=self.syms)
        elif axes["R"] == "bear":
            e = e & pd.DataFrame(np.tile(self.bear_mask.values[:, None],
                                         (1, len(self.syms))), index=self.idx,
                                 columns=self.syms)
        if axes["T"] == "weekly":
            e = e & pd.DataFrame(np.tile(self.week_mask.values[:, None],
                                         (1, len(self.syms))), index=self.idx,
                                 columns=self.syms)
        if axes["X"] != "own":
            n = int(axes["X"][1:])
            edges = e & ~e.shift(1).fillna(False)
            e, x = edges, edges.shift(n).fillna(False)
        scale = self.delever_scale if axes["S"] == "delever" else None
        return e.fillna(False), x.fillna(False), scale


def signal_hash(e: pd.DataFrame, x: pd.DataFrame) -> str:
    b = np.ascontiguousarray(e.values).tobytes() + \
        np.ascontiguousarray(x.values).tobytes()
    return hashlib.sha256(b).hexdigest()[:24]


# --------------------------------------------------------------- generate

def cmd_generate(args):
    os.makedirs(OUT_DIR, exist_ok=True)
    ctx = Ctx()
    roster, excluded = ctx.roster, ctx.excluded
    candidates, stats = [], {"rejections": 0, "param_dupes": 0,
                            "signal_dupes": 0, "dead_signal": 0}
    seen_phash, seen_shash = set(), set()
    for fam in roster:
        got, tries = 0, 0
        for d_idx, params, axes in sample_draws(fam):
            if got >= QUOTA_PER_FAMILY or tries >= N_DRAWS:
                break
            tries += 1
            if not draw_valid(fam, params):
                stats["rejections"] += 1
                continue
            ph = param_hash(fam, params, axes)
            if ph in seen_phash:
                stats["param_dupes"] += 1
                continue
            try:
                e, x, _scale = ctx.build_signals(fam, params, axes)
            except Exception:
                stats["dead_signal"] += 1
                continue
            if not bool(e.any().any()):
                stats["dead_signal"] += 1
                continue
            sh = signal_hash(e, x)
            if sh in seen_shash:
                stats["signal_dupes"] += 1
                continue
            seen_phash.add(ph)
            seen_shash.add(sh)
            candidates.append({"id": f"W1-{fam['idx']:02d}{d_idx:03d}",
                              "family": fam["family"], "kind": fam["kind"],
                              "params": params, "axes": axes,
                              "signal_sha256": sh})
            got += 1
        if got < QUOTA_PER_FAMILY:
            stats.setdefault("quota_short", {})[fam["family"]] = got
    roster_path = os.path.join(OUT_DIR, "w1_roster.json")
    cand_path = os.path.join(OUT_DIR, "w1_candidates.json")
    with open(roster_path, "w", encoding="utf-8") as f:
        json.dump({"batch": BATCH, "roster": roster, "excluded": excluded,
                   "cutoff": CUTOFF, "seed_base": SEED_BASE,
                   "quota_per_family": QUOTA_PER_FAMILY, "n_draws": N_DRAWS,
                   "axes": {"R": AX_R, "X": AX_X, "S": AX_S, "T": AX_T}},
                  f, indent=1, ensure_ascii=False)
    with open(cand_path, "w", encoding="utf-8") as f:
        json.dump({"batch": BATCH, "n": len(candidates),
                   "evidence_cutoff": CUTOFF, "candidates": candidates},
                  f, ensure_ascii=False)
    stats.update({"enrolled": len(candidates), "families": len(roster),
                  "excluded_families": len(excluded)})
    with open(os.path.join(OUT_DIR, "w1_generate_summary.json"), "w",
              encoding="utf-8") as f:
        json.dump({"batch": BATCH, **stats, "evidence_cutoff": CUTOFF}, f,
                  indent=1, ensure_ascii=False)
    # append-only grammar-consumption registry (TRIAL_LABOR_LAW sec.4)
    with open(os.path.join(OUT_DIR, "grammar_registry.jsonl"), "a",
              encoding="utf-8") as f:
        f.write(json.dumps({
            "wave": "w1", "batch": BATCH, "seed_base": SEED_BASE,
            "roster_sha256_16": hashlib.sha256(
                open(roster_path, "rb").read()).hexdigest()[:16],
            "candidates_sha256_16": hashlib.sha256(
                open(cand_path, "rb").read()).hexdigest()[:16],
            "families": len(roster), "draw_frame": N_DRAWS,
            "enrolled": len(candidates), "consumed_at": time.strftime(
                "%Y-%m-%dT%H:%M:%S%z")}, ensure_ascii=False) + "\n")
    print(f"generate: {len(candidates)} candidates / {len(roster)} families; "
          f"stats={json.dumps(stats)}; excluded={len(excluded)}")
    return 0


# --------------------------------------------------------------- screen

def _combined_rows(ctx):
    rows = json.load(open(os.path.join(OUT_DIR, "w1_candidates.json"),
                         encoding="utf-8"))["candidates"]
    for r in rows:
        r["row_type"] = "candidate"
    for fam in ctx.roster:                      # family-default calibration controls
        rows.append({"id": f"DEF-{fam['idx']:02d}", "family": fam["family"],
                     "kind": fam["kind"], "params": {}, "axes": None,
                     "row_type": "control"})
    for i in range(20):                          # random-entry nulls (RLSL iron rule)
        rows.append({"id": f"NULL-{i:02d}", "family": "random_entry",
                     "kind": "null", "params": {"p": [0.02, 0.05][i % 2],
                                                "seed": SEED_BASE + NULL_SEED_OFF + i},
                     "axes": None, "row_type": "null"})
    return rows


def _screen_one(ctx, row):
    t0 = time.time()
    fam = next(f for f in ctx.roster if f["family"] == row["family"]) \
        if row["row_type"] != "null" else None
    if row["row_type"] == "null":
        rng = np.random.default_rng(row["params"]["seed"])
        e = pd.DataFrame(rng.random((len(ctx.idx), len(ctx.syms))) <
                         row["params"]["p"], index=ctx.idx, columns=ctx.syms)
        x = pd.DataFrame(False, index=ctx.idx, columns=ctx.syms)
        scale = None
    else:
        axes = row["axes"] or {"R": "none", "X": "own", "S": "full", "T": "daily"}
        e, x, scale = ctx.build_signals(fam, row["params"], axes)
    res = run_backtest(ctx.prices, {}, entry_signal=e, exit_signal=x,
                       entry_size_scale=scale)
    eq = pd.Series(res["equity_curve"], index=ctx.idx[:len(res["equity_curve"])])
    n = len(eq)
    starts = range(WARMUP, n - W6M + 1, STRIDE)
    beats = 0
    for i in starts:
        s_r = eq.iloc[i + W6M] / eq.iloc[i] - 1.0
        b_r = ctx.ew_curve.iloc[i + W6M] / ctx.ew_curve.iloc[i] - 1.0
        beats += int(s_r > b_r)
    n_win = max(len(list(starts)), 1)
    beat_rate = beats / n_win
    m = res["metrics"]
    out = {"id": row["id"], "row_type": row["row_type"], "family": row["family"],
           "axes": row["axes"], "params": row["params"],
           "beat_rate_6m": round(beat_rate, 4), "n_windows": n_win,
           "n_trades": m.get("num_trades", 0),
           "sharpe_full": m.get("sharpe"), "max_dd": m.get("max_drawdown"),
           "elapsed_s": round(time.time() - t0, 2)}
    out["screen_pass"] = bool(beat_rate >= BEAT_LINE
                             and out["n_trades"] >= TRADES_GATE
                             and (out["max_dd"] is None or out["max_dd"] >= DD_LINE))
    return out


_CTX = None


def _worker_init():
    global _CTX
    _CTX = Ctx()


def _worker_run(row):
    try:
        return _screen_one(_CTX, row)
    except Exception as ex:
        return {"id": row["id"], "row_type": row.get("row_type"),
                "family": row.get("family"), "status": "signal_error",
                "error": f"{type(ex).__name__}: {ex}"[:200]}


def cmd_screen(args):
    os.makedirs(OUT_DIR, exist_ok=True)
    ctx = Ctx()                      # roster needed for controls in all modes
    rows = _combined_rows(ctx)
    ckpt = os.path.join(OUT_DIR, "screen_checkpoint.jsonl")
    done = set()
    if os.path.exists(ckpt):
        with open(ckpt, encoding="utf-8") as f:
            for line in f:
                try:
                    done.add(json.loads(line)["id"])
                except Exception:
                    pass
    todo = [r for i, r in enumerate(rows)
            if args.pos_from <= i < args.pos_to and r["id"] not in done]
    print(f"screen: {len(todo)} rows in shard "
          f"[{args.pos_from}:{args.pos_to}) of {len(rows)}; "
          f"{len(done)} already checkpointed; workers={args.workers}")
    t0 = time.time()
    if args.workers <= 1:
        for i, row in enumerate(todo):
            out = _screen_one_wrap(ctx, row)
            with open(ckpt, "a", encoding="utf-8") as f:
                f.write(json.dumps(out, ensure_ascii=False) + "\n")
            if (i + 1) % 25 == 0:
                print(f"  {i+1}/{len(todo)} ({time.time()-t0:.0f}s)", flush=True)
    else:
        import multiprocessing as mp
        with mp.Pool(args.workers, initializer=_worker_init) as pool:
            for j, out in enumerate(pool.imap_unordered(_worker_run, todo, chunksize=4), 1):
                with open(ckpt, "a", encoding="utf-8") as f:
                    f.write(json.dumps(out, ensure_ascii=False) + "\n")
                if j % 50 == 0:
                    print(f"  {j}/{len(todo)} ({time.time()-t0:.0f}s)", flush=True)
    print(f"screen: shard done ({time.time()-t0:.0f}s) -> {ckpt}")
    return 0


def _screen_one_wrap(ctx, row):
    try:
        return _screen_one(ctx, row)
    except Exception as ex:
        return {"id": row["id"], "row_type": row.get("row_type"),
                "family": row.get("family"), "status": "signal_error",
                "error": f"{type(ex).__name__}: {ex}"[:200]}


def cmd_finalize(args):
    """Aggregate checkpoint -> stage-1 survivors + honest funnel accounting.
    Ledger entry embedded under trials_ledger (r252 law); one-chain
    idempotency: an existing complete summary's ledger entry is never
    recomputed (re-run would double-count the chain)."""
    ckpt = os.path.join(OUT_DIR, "screen_checkpoint.jsonl")
    rows = [json.loads(line) for line in open(ckpt, encoding="utf-8")]
    cand = [r for r in rows if r.get("row_type") == "candidate"]
    ctrl = [r for r in rows if r.get("row_type") == "control"]
    null = [r for r in rows if r.get("row_type") == "null"]
    err = [r for r in rows if r.get("status") == "signal_error"]
    surv = [r for r in cand if r.get("screen_pass")]
    null_br = sorted(r.get("beat_rate_6m", 0.0) for r in null if "beat_rate_6m" in r)
    n_expected = json.load(open(os.path.join(OUT_DIR, "w1_candidates.json"),
                                encoding="utf-8"))["n"]
    out_path = os.path.join(OUT_DIR, "w1_screen_summary.json")
    prev = None
    if os.path.exists(out_path):
        prev = json.load(open(out_path, encoding="utf-8"))
        if prev.get("complete") and "trials_ledger" in prev:
            ledger = prev["trials_ledger"]     # chain linearity: keep as-is
        else:
            ledger = sg.append_ledger(
                BATCH, len(cand), file_name="mass_trial/w1_screen_summary.json",
                evidence_cutoff=CUTOFF,
                note=f"T-94 wave-1 stage-1 screen: {len(cand)} candidate cells, "
                     f"{len(surv)} survivors")
    else:
        ledger = sg.append_ledger(
            BATCH, len(cand), file_name="mass_trial/w1_screen_summary.json",
            evidence_cutoff=CUTOFF,
            note=f"T-94 wave-1 stage-1 screen: {len(cand)} candidate cells, "
                 f"{len(surv)} survivors")
    summary = {
        "batch": BATCH, "evidence_cutoff": CUTOFF,
        **sg.cutoff_meta(CUTOFF),
        "trials_ledger": ledger,
        "n_candidates_checkpointed": len(cand), "n_controls": len(ctrl),
        "n_nulls": len(null), "n_signal_error": len(err),
        "n_stage1_survivors": len(surv),
        "screen_line": {"beat_rate_6m": BEAT_LINE, "trades": TRADES_GATE,
                        "max_dd": DD_LINE},
        "null_beat_rate_p50": null_br[len(null_br) // 2] if null_br else None,
        "null_beat_rate_p95": null_br[int(0.95 * (len(null_br) - 1))] if null_br else None,
        "candidates_expected": n_expected,
        "complete": len(cand) == n_expected,
        "survivor_ids": [r["id"] for r in surv],
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in summary.items()
                      if k != "survivor_ids"}, ensure_ascii=False, indent=1))
    return 0 if summary["complete"] else 2


# ---------------------------------------------------------------- judge (s3)

def _leg_raw(leg):
    """p5c leg panel (wholesale import, sec.9.3 caliber) + mass Ctx column
    imputation (identical to load_panel rules)."""
    prices, P, idx, listed, cen = _load_leg(leg)
    raw = {}
    for s, df in prices.items():
        d = df.copy()
        if "open" not in d.columns:
            d["open"] = d["close"]
        if "amount" not in d.columns:
            d["amount"] = d["volume"] * d["close"]
        raw[s] = d
    return raw, P, idx, listed, cen


def _leg_ctx(leg, bench):
    """Leg Ctx + census fail-closed: the mass panel-union index must equal
    the p5c census face index or the batch refuses to run."""
    raw, P, idx, listed, cen = _leg_raw(leg)
    ctx = Ctx.from_raw(raw, bench)
    if not ctx.idx.equals(P["close"].index):
        raise SystemExit(f"JUDGE-GATE: leg-{leg} panel index drift vs p5c "
                         "census face (data moved under the batch)")
    return ctx, P, idx, listed, cen


def _collapse_survivors(rets: pd.DataFrame, line: float = 0.999):
    """sec.9.1 entry gate: pairwise |corr|>=line daily-returns collapse.
    Representative = deterministic lowest candidate_id (greedy ascending);
    original variants retained in the returned audit block."""
    order = list(rets.columns)
    corr = rets.corr()
    eliminated, clusters = set(), {}
    for a in order:
        if a in eliminated:
            continue
        for b in order:
            if b <= a or b in eliminated:
                continue
            if abs(float(corr.loc[a, b])) >= line:
                clusters.setdefault(a, []).append(b)
                eliminated.add(b)
    kept = [c for c in order if c not in eliminated]
    return kept, clusters, sorted(eliminated)


def _yearly_returns(eq: pd.Series) -> dict:
    out = {}
    for year, seg in eq.groupby(eq.index.year):
        out[int(year)] = round(float(seg.iloc[-1] / seg.iloc[0] - 1.0), 4)
    return out


def _dual_nulls(returns, cell_idx):
    """Block bootstrap B=2000 (block=20 circular) + sign-flip P=2000 on the
    cell's mean daily return, two-sided (RANDOM_LARGE_SAMPLE_LAW sec.3;
    wave-1b reference formula). rng=[JUDGE_SEED, i] -- stream pinned to the
    two resample faces only (census sec.9.1 usage-pinning precedent)."""
    rng = np.random.default_rng([JUDGE_SEED, cell_idx])
    r = np.asarray(returns, dtype=float)
    n = len(r)
    mu = float(r.mean())
    B, block = 2000, 20
    n_blocks = int(math.ceil(n / block))
    idx0 = rng.integers(0, max(1, n), size=(B, n_blocks))
    offs = np.arange(block)[None, None, :]
    gather = (idx0[:, :, None] + offs) % n
    boots = r[gather].reshape(B, -1)[:, :n].mean(axis=1)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    P = 2000
    signs = rng.choice([-1.0, 1.0], size=(P, n))
    perms = (r[None, :] * signs).mean(axis=1)
    p_two = float((np.abs(perms) >= abs(mu)).mean())
    return {"bootstrap_ci": [round(float(lo), 8), round(float(hi), 8)],
            "ci_lower_positive": bool(lo > 0),
            "signflip_p": round(p_two, 6), "B": B, "P": P, "block": block}


def cmd_judge_prep(args):
    """sec.9.1 prep: frozen-product gates + dual-leg census gates + manifest
    gate + corr-dedup (leg-L base daily returns) + passive precompute."""
    os.makedirs(OUT_DIR, exist_ok=True)
    t0 = time.time()
    spath = os.path.join(OUT_DIR, "w1_screen_summary.json")
    cpath = os.path.join(OUT_DIR, "w1_candidates.json")
    for p in (spath, cpath):
        if not os.path.exists(p):
            print(f"JUDGE-PREP-GATE FAIL: {p} absent")
            return 1
    summary = json.load(open(spath, encoding="utf-8"))
    if not summary.get("complete"):
        print("JUDGE-PREP-GATE FAIL: screen summary not complete")
        return 1
    sha = hashlib.sha256(open(cpath, "rb").read()).hexdigest()[:16]
    if sha != CANDIDATES_SHA_FROZEN:
        print(f"JUDGE-PREP-GATE FAIL: candidates sha drift {sha} != "
              f"{CANDIDATES_SHA_FROZEN} (frozen anchor)")
        return 1
    survivors = list(summary["survivor_ids"])
    if not survivors:
        print("JUDGE-PREP-GATE FAIL: zero stage-1 survivors")
        return 1
    cands = {c["id"]: c for c in json.load(
        open(cpath, encoding="utf-8"))["candidates"]}
    missing = [s for s in survivors if s not in cands]
    if missing:
        print(f"JUDGE-PREP-GATE FAIL: {len(missing)} survivors absent from "
              "frozen candidates file")
        return 1
    man = json.load(open(T18_MANIFEST, encoding="utf-8"))
    if man.get("verdict") != "PASS":
        print("JUDGE-PREP-GATE FAIL: t18 deep-panel manifest != PASS")
        return 1
    bench = _load_bench()
    bench_cov = {"from": str(bench.index.min().date()),
                 "to": str(bench.index.max().date()),
                 "note": "single-source csi300.csv (screen face verbatim); "
                         "leg-D R-axis/macro/bench-arg signals honestly "
                         "dead pre-2020, disclosed per sec.9.1"}
    ctxs, starts, passive, legs_meta = {}, {}, {}, {}
    for leg in ("L", "D"):
        ctx, P, idx, listed, cen = _leg_ctx(leg, bench)
        if cen != FROZEN_CENSUS[leg]:
            print(f"JUDGE-PREP-GATE FAIL: leg-{leg} census drift {cen} != "
                  f"{FROZEN_CENSUS[leg]}")
            return 1
        ctxs[leg] = ctx
        close = P["close"]
        n = len(idx)
        starts[leg], passive[leg] = {}, {}
        for wname, w in WINDOWS.items():
            st = [p for p in range(n)
                  if idx[p] >= (LEG_L_FLOOR if leg == "L" else LEG_D_FLOOR)
                  and p >= WARMUP_TD and p <= n - 1 - w
                  and (listed.iloc[p] >= MIN_LISTED if leg == "L" else True)]
            if len(st) != FROZEN_CENSUS[leg][wname]:
                print(f"JUDGE-PREP-GATE FAIL: leg-{leg} {wname} starts "
                      f"{len(st)} != {FROZEN_CENSUS[leg][wname]}")
                return 1
            starts[leg][wname] = st
            passive[leg][wname] = {}
            for p in st:
                sdate, edate = idx[p], idx[p + w - 1]
                syms = close.columns[close.loc[sdate].notna()]
                rel = passive_rel(close, syms, sdate, edate)
                passive[leg][wname][str(p)] = round(
                    float(rel.iloc[-1] - 1.0), 6)
        legs_meta[leg] = {"census": cen, "n_days": n,
                          "first": str(idx[0].date()),
                          "last": str(idx[-1].date()),
                          "members": len(close.columns)}
    # ---- corr-dedup on leg-L base-face daily returns (entry gate)
    roster_by_family = {f["family"]: f for f in ctxs["L"].roster}
    rets = {}
    for cid in sorted(survivors):
        c = cands[cid]
        fam = roster_by_family[c["family"]]
        e, x, scale = ctxs["L"].build_signals(fam, c["params"], c["axes"])
        res = run_backtest(ctxs["L"].prices, {}, entry_signal=e,
                           exit_signal=x, entry_size_scale=scale)
        eq = pd.Series(res["equity_curve"],
                       index=ctxs["L"].idx[:len(res["equity_curve"])])
        rets[cid] = eq.pct_change().fillna(0.0)
    kept, clusters, eliminated = _collapse_survivors(
        pd.DataFrame({c: rets[c] for c in sorted(rets)}))
    state = {
        "batch": JUDGE_BATCH, "evidence_cutoff": CUTOFF,
        **sg.cutoff_meta(CUTOFF),
        "g_manifest": {"verdict": man.get("verdict"),
                       "members": len(man.get("members", {}))},
        "candidates_sha256_16": sha,
        "n_stage1_survivors": len(survivors),
        "n_judge_cells": len(kept),
        "collapse": {"line": 0.999, "kept": kept, "clusters": clusters,
                     "eliminated": eliminated,
                     "note": "representative = deterministic lowest "
                             "candidate_id; original variants retained in "
                             "this audit block (sec.9.1)"},
        "starts": starts, "passive": passive,
        "legs": legs_meta, "bench_coverage": bench_cov,
        "seed_judge": JUDGE_SEED,
    }
    with open(JUDGE_STATE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=1, ensure_ascii=False)
    print(f"judge-prep PASS: survivors {len(survivors)} -> N_judge "
          f"{len(kept)} (collapsed {len(eliminated)}); census L/D == frozen; "
          f"manifest {man.get('verdict')} ({time.time()-t0:.0f}s)")
    return 0


_JST = None


def _judge_init(state):
    global _JST
    _JST = state


def _j(o):
    """JSON-safe scrub (numpy scalars -> python primitives)."""
    if isinstance(o, dict):
        return {k: _j(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_j(v) for v in o]
    if isinstance(o, (bool, np.bool_)):
        return bool(o)
    if isinstance(o, (int, np.integer)):
        return int(o)
    if isinstance(o, (float, np.floating)):
        return float(o)
    return o


def _judge_cell(cell):
    """One collapsed-survivor judged cell (pool worker; sec.9.1 grid:
    legs L/D x cost x1/x2 x windows {126,252,504} sliced from full curves +
    regime segments + dual nulls + G1'/DSR inputs + descriptive clauses)."""
    st = _JST
    cand = cell["cand"]
    fam = st["roster_by_family"][cand["family"]]
    out = {"cell_id": cell["cell_id"], "candidate_id": cand["id"],
           "family": cand["family"], "i": cell["i"]}
    legs = {}
    legL_daily = None
    for leg in ("L", "D"):
        ctx = st["ctx_" + leg]
        idx = st["idx_" + leg]
        e, x, scale = ctx.build_signals(fam, cand["params"], cand["axes"])
        faces = {}
        for face in ("x1", "x2"):
            params = {"report_num_entries": True}
            if face == "x2":
                cmgr = sg.CostPatch(2.0)
                cmgr.__enter__()
            try:
                res = run_backtest(ctx.prices, params, entry_signal=e,
                                   exit_signal=x, entry_size_scale=scale)
            finally:
                if face == "x2":
                    cmgr.__exit__(None, None, None)
            eq = pd.Series(res["equity_curve"],
                           index=idx[:len(res["equity_curve"])])
            m = res["metrics"]
            beat = {}
            for wname, w in WINDOWS.items():
                k = tot = 0
                for p in st["starts"][leg][wname]:
                    if p + w - 1 >= len(eq):
                        continue
                    tot += 1
                    cret = float(eq.iloc[p + w - 1] / eq.iloc[p] - 1.0)
                    if cret > st["passive"][leg][wname][str(p)]:
                        k += 1
                beat[wname] = {"k": k, "n": tot,
                               "rate": round(k / tot, 6) if tot else 0.0}
            faces[face] = {
                "sharpe_full": round(float(sharpe(eq)), 4),
                "n_trades": int(m.get("num_trades", 0)),
                "n_entries": int(m.get("num_entries", 0)),
                "max_dd": round(float(max_drawdown(eq)), 4),
                "yearly": _yearly_returns(eq), "beat": beat,
            }
            if leg == "L" and face == "x1":
                legL_daily = eq.pct_change().fillna(0.0)
        # regime segments at window starts (T-22 sec.3 frozen 3-way proxy)
        s_series = st["states"].reindex(idx)
        segs = {"bear": 0, "bull": 0, "chop": 0, "na": 0}
        for wname in WINDOWS:
            for p in st["starts"][leg][wname]:
                d = s_series.iloc[p] if p < len(s_series) else None
                st_ = REGIME_MAP.get(d, "na") if d == d else "na"
                segs[st_] += 1
        legs[leg] = {"x1": faces["x1"], "x2": faces["x2"],
                     "regime_start_windows": segs}
    out["legs"] = legs
    daily = [round(float(v), 8) for v in legL_daily.values]
    out["legL_daily_returns"] = daily
    eq_l = (1.0 + legL_daily).cumprod()           # reconstruct for OOS split
    oos = eq_l[eq_l.index >= OOS_START_TS]
    oos_sharpe = float(sharpe(oos)) if len(oos) > 2 else 0.0
    oos_ret = float(oos.iloc[-1] / oos.iloc[0] - 1.0) if len(oos) > 1 else 0.0
    n_days = max(len(eq_l), 1)
    ann = float(eq_l.iloc[-1] / eq_l.iloc[0]) ** (252.0 / n_days) - 1.0
    yearly = legs["L"]["x1"]["yearly"]
    x2_yearly = legs["L"]["x2"]["yearly"]
    worst_year = min(yearly.values()) if yearly else 0.0
    x2_worst = min(x2_yearly.values()) if x2_yearly else 0.0
    out["legL_oos"] = {"oos_sharpe": round(oos_sharpe, 4),
                       "oos_ret": round(oos_ret, 6)}
    out["descriptive"] = {
        "ann_pos": bool(ann > 0),
        "oos_dual_pos": bool(oos_sharpe > 0 and oos_ret > 0),
        "dd_ok": bool(legs["L"]["x1"]["max_dd"] >= -0.35),
        "no_crash_year": bool(worst_year > CRASH_YEAR),
        "x2_yearly_stable": bool(x2_worst > CRASH_YEAR),
    }
    out["crisis_days_gt8pct"] = int(
        (np.abs(legL_daily) > 0.08).sum())
    out["dual_nulls"] = _dual_nulls(daily, cell["i"])
    n_eff = sum(legs[lg]["regime_start_windows"][s]
                for lg in legs for s in ("bear", "bull", "chop"))
    out["n_eff_start_windows"] = n_eff
    out["sample_sufficient"] = bool(
        n_eff >= 500 and all(legs[lg]["regime_start_windows"][s] >= 100
                             for lg in legs
                             for s in ("bear", "bull", "chop")))
    return out


def cmd_judge(args):
    """Sharded judged-cell burn (checkpoint jsonl per cell, cross-kill
    resume = skip recorded cell_ids)."""
    os.makedirs(OUT_DIR, exist_ok=True)
    if not os.path.exists(JUDGE_STATE):
        print(f"JUDGE-GATE: judge-prep required first ({JUDGE_STATE} absent)")
        return 2
    state = json.load(open(JUDGE_STATE, encoding="utf-8"))
    cpath = os.path.join(OUT_DIR, "w1_candidates.json")
    cands = {c["id"]: c for c in json.load(
        open(cpath, encoding="utf-8"))["candidates"]}
    kept = sorted(state["collapse"]["kept"])
    cells = [{"cell_id": f"JUDGE|{cid}", "candidate_id": cid, "i": i,
              "cand": cands[cid]} for i, cid in enumerate(kept)]
    mine = [c for i, c in enumerate(cells) if i % args.shards == args.shard]
    bench = _load_bench()
    ctx_L, P_L, idx_L, listed_L, cen_L = _leg_ctx("L", bench)
    ctx_D, P_D, idx_D, listed_D, cen_D = _leg_ctx("D", bench)
    st = {"ctx_L": ctx_L, "ctx_D": ctx_D, "idx_L": idx_L, "idx_D": idx_D,
          "roster_by_family": {f["family"]: f for f in ctx_L.roster},
          "starts": state["starts"], "passive": state["passive"],
          "states": v3_state_series()}
    ck = os.path.join(OUT_DIR, f"judge_shard_{args.shard}of{args.shards}.jsonl")
    done = set()
    if os.path.exists(ck):
        with open(ck, encoding="utf-8") as fh:
            for ln in fh:
                try:
                    done.add(json.loads(ln)["cell_id"])
                except Exception:
                    pass
    todo = [c for c in mine if c["cell_id"] not in done]
    print(f"judge: shard {args.shard}of{args.shards} cells {len(mine)}, "
          f"done {len(done)}, todo {len(todo)}")
    t0 = time.time()

    def on_result(key, payload):
        with open(ck, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(_j(payload), ensure_ascii=False) + "\n")

    if todo:
        jobs = [(c["cell_id"], _judge_cell, (c,)) for c in todo]
        run_cells_parallel(jobs, workers=args.workers or worker_cap(),
                           desc="judge cells", initializer=_judge_init,
                           initargs=(st,), on_result=on_result)
    print(f"judge: shard {args.shard}of{args.shards} complete "
          f"({time.time()-t0:.0f}s) -> {ck}")
    return 0


def cmd_judge_finalize(args):
    """Aggregate shards -> G1'v2 + DSR + family PBO + G2 + E[FP] + verdicts
    + ledger append (single-shot guard: a complete product is never
    re-appended; MASS_TRIAL_W1_JUDGE_REFINALIZE=1 = only redo, byte-stable
    via own-chain-position overrides per r259 prev-echo guard)."""
    if not os.path.exists(JUDGE_STATE):
        print(f"FINALIZE-GATE: {JUDGE_STATE} absent (judge-prep first)")
        return 2
    n_eff_override = None
    redo_dsr_trials = None
    if os.path.exists(JUDGE_OUT):
        prev = json.load(open(JUDGE_OUT, encoding="utf-8"))
        if prev.get("complete") and "trials_ledger" in prev:
            if not os.environ.get("MASS_TRIAL_W1_JUDGE_REFINALIZE"):
                print("judge-finalize: complete product exists (idempotent "
                      "no-op; MASS_TRIAL_W1_JUDGE_REFINALIZE=1 to redo)")
                return 0
            n_eff_override = (int(prev["trials_ledger"]["prev_total"])
                              + int(prev["trials_ledger"]["batch_trials"]))
            redo_dsr_trials = int(prev["trials_ledger"]["prev_total"])
    state = json.load(open(JUDGE_STATE, encoding="utf-8"))
    screen = json.load(open(os.path.join(OUT_DIR, "w1_screen_summary.json"),
                            encoding="utf-8"))
    kept = sorted(state["collapse"]["kept"])
    rows = []
    for f in sorted(os.listdir(OUT_DIR)):
        if f.startswith("judge_shard_") and f.endswith(".jsonl"):
            with open(os.path.join(OUT_DIR, f), encoding="utf-8") as fh:
                for ln in fh:
                    if ln.strip():
                        rows.append(json.loads(ln))
    by_id = {r["cell_id"]: r for r in rows}
    missing = [f"JUDGE|{cid}" for cid in kept if f"JUDGE|{cid}" not in by_id]
    if missing:
        print(f"FINALIZE-GATE: {len(missing)} judged cells incomplete; "
              "refused (checkpoints retained)")
        return 2
    judged = [by_id[f"JUDGE|{cid}"] for cid in kept]
    n_judge = len(judged)
    n_trials = redo_dsr_trials if redo_dsr_trials is not None \
        else sg.ledger_head()["total"]
    for r in judged:
        rets = r["legL_daily_returns"]
        g1 = sg.g1_prime_v2(r["legs"]["L"]["x1"]["sharpe_full"], rets,
                            n_judge, pool="core48",
                            n_trades=r["legs"]["L"]["x1"]["n_trades"],
                            n_entries=r["legs"]["L"]["x1"]["n_entries"],
                            n_eff_override=n_eff_override)
        dsr = sg.deflated_sharpe_ratio(rets, n_trials=n_trials)
        r["g1_prime_v2"] = g1
        r["dsr"] = dsr
        r["g1_pass"] = g1["pass_v2"]
        r["verdict"] = ("pass" if (g1["pass_v2"] and r["sample_sufficient"])
                        else "insufficient-sample"
                        if not r["sample_sufficient"] else "fail")
    # family PBO (CSCV 8 blocks; family = strategy module; <8 cells -> n/a)
    fam_map = {}
    for r in judged:
        fam_map.setdefault(r["family"].split(".")[0], []).append(r)
    pbos = {}
    for fam, rs in fam_map.items():
        if len(rs) < 8:
            pbos[fam] = {"pbo": None, "n_cells": len(rs),
                         "note": "insufficient (<8) -- G2 cannot pass"}
            for r in rs:
                r["family_pbo"] = None
            continue
        series = {r["candidate_id"]: pd.Series(r["legL_daily_returns"])
                  for r in rs}
        pbo = cscv_pbo(align_returns(series))
        pbo_val = pbo["pbo"] if isinstance(pbo, dict) else pbo
        pbos[fam] = {"pbo": round(float(pbo_val), 4), "n_cells": len(rs)}
        for r in rs:
            r["family_pbo"] = pbos[fam]["pbo"]
    for r in judged:
        r["g2_registration_v2"] = sg.g2_registration_v2(
            r["g1_pass"], r["dsr"], r.get("family_pbo"))
    eligible = [r["candidate_id"] for r in judged
                if r["g2_registration_v2"]["eligible_v2"]]
    e_fp = round(0.05 * n_judge, 2)
    ledger = sg.append_ledger(JUDGE_BATCH, n_judge,
                              file_name="mass_trial/w1_judge.json",
                              evidence_cutoff=CUTOFF,
                              note=f"T-94 s3 judge: {n_judge} collapsed cells "
                                   f"from {state['n_stage1_survivors']} "
                                   "stage-1 survivors")
    desc_agg = {cl: sum(1 for r in judged if r["descriptive"][cl])
                for cl in ("ann_pos", "oos_dual_pos", "dd_ok",
                           "no_crash_year", "x2_yearly_stable")}
    summary = {
        "batch": JUDGE_BATCH, "evidence_cutoff": CUTOFF,
        **sg.cutoff_meta(CUTOFF),
        "trials_ledger": ledger,
        "n_judge_cells": n_judge,
        "n_stage1_survivors": state["n_stage1_survivors"],
        "collapse_audit": {"line": 0.999,
                           "eliminated": state["collapse"]["eliminated"],
                           "clusters": state["collapse"]["clusters"]},
        "n_wave_disclosure": {
            "screen_cells": int(screen["trials_ledger"]["batch_trials"]),
            "judged_cells": n_judge, "E_FP_nominal_5pct": e_fp,
            "note": "DSR>=0.95 gate IS the multiple-testing correction "
                    "(cumulative N deflation); E[FP] disclosed at nominal "
                    "5% caliber; sibling wave-1b (trial_labor_w1) tracked "
                    "under its own prereg/ticket"},
        "n_trials_head_at_finalize": n_trials,
        "family_pbo": pbos,
        "descriptive_counts": desc_agg,
        "eligible_g2": eligible, "n_eligible_g2": len(eligible),
        "verdicts": {v: sum(1 for r in judged if r["verdict"] == v)
                     for v in ("pass", "fail", "insufficient-sample")},
        "cells": [{k: v for k, v in r.items()
                   if k != "legL_daily_returns"} for r in judged],
        "audit": {
            "judged_face": "legs L/D x cost x1/x2 x windows {126,252,504} "
                           "sliced from full curves (P-5 slicing caliber, "
                           "wave-1b sec.9.3 same-source) + regime segments "
                           "(T-22 sec.3 3-way proxy) + dual nulls (B=2000 "
                           "block=20 circular + P=2000 sign-flip, rng="
                           "[20285000, i]); Sharpe gates on leg-L x1; x2 = "
                           "cost-stability descriptive; bench single-source "
                           "csi300.csv (leg-D coverage 2020+ disclosed)",
            "seed_judge": JUDGE_SEED,
            "g_manifest": state["g_manifest"],
            "legs": state["legs"], "bench_coverage": state["bench_coverage"],
        },
        "complete": True,
    }
    with open(JUDGE_OUT, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1, ensure_ascii=False)
    print(f"judge-finalize: {n_judge} judged cells, E[FP]={e_fp}, "
          f"G2 eligible {len(eligible)} -> {eligible[:10]}")
    return 0


# --------------------------------------------------------------- selftest

def cmd_selftest(args):
    ok = 0
    n_checks = 0

    def check(name, cond):
        nonlocal ok, n_checks
        n_checks += 1
        ok += int(bool(cond))
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")

    roster, excluded = build_roster()
    check("roster families == 75", len(roster) == 75)
    check("roster deterministic",
          [f["family"] for f in build_roster()[0]] == [f["family"] for f in roster])
    kinds = {}
    for f in roster:
        kinds[f["kind"]] = kinds.get(f["kind"], 0) + 1
    check("kinds cover sym/panel/mask/macro", set(kinds) ==
          {"sym", "panel", "mask", "macro"})
    check("zero families excluded by rule gaps", len(excluded) == 0)
    fam = roster[0]
    d1 = list(sample_draws(fam, 8))
    d2 = list(sample_draws(fam, 8))
    check("per-family draw frame reproducible", d1 == d2)
    check("draws distinct", len({param_hash(fam, p, a) for _, p, a in d1}) == len(d1))
    # axis machinery on synthetic data
    idx = pd.bdate_range("2024-01-02", periods=300)
    e = pd.DataFrame(np.zeros((300, 2), dtype=bool), index=idx,
                    columns=["a", "b"])
    e.iloc[10, 0] = True
    edges = e & ~e.shift(1).fillna(False)
    x = edges.shift(5).fillna(False)
    check("rising-edge time-exit lands at t+5", bool(x.iloc[15, 0]) and
          not bool(x.iloc[14, 0]) and not bool(x.iloc[16, 0]))
    wk = pd.Series(np.r_[True, np.diff(idx.dayofweek) < 0], index=idx)
    n_iso_weeks = len(set(zip(idx.isocalendar().year, idx.isocalendar().week)))
    check("weekly mask = first trading day of week",
          int(wk.sum()) == n_iso_weeks and bool(wk.iloc[0]) and not bool(wk.iloc[1]))
    bench = pd.Series(np.linspace(2.0, 1.0, 300), index=idx)   # falling -> bear
    ma200 = bench.rolling(200).mean()
    check("bear mask fires only after MA200 warmup",
          bool((bench < ma200).iloc[250:].any()) and
          bool(pd.isna(ma200.iloc[198])) and not bool(pd.isna(ma200.iloc[199])))
    check("window enumeration count (500-bar synthetic)",
          len(list(range(WARMUP, 500 - W6M + 1, STRIDE))) == 6)
    check("seed band registered", "mass_trial_w1" in sg.SEED_REGISTRY)

    # ---- s3 judge face (hermetic: synthetic fixtures, zero repo data) ----
    check("judge seed band registered + value",
          sg.SEED_REGISTRY.get("mass_trial_w1_judge") == 20285000)
    check("frozen census import intact (p5c wholesale, sec.9.3 binding)",
          FROZEN_CENSUS == {"L": {"6m": 1253, "12m": 1127, "24m": 875},
                            "D": {"6m": 3104, "12m": 2978, "24m": 2726}}
          and EVIDENCE_CUTOFF_GRID == CUTOFF == "2026-09-22")
    check("regime 3-way proxy map intact (T-22 sec.3)",
          REGIME_MAP == {"GREEN": "bull", "YELLOW": "chop",
                         "ORANGE": "bear", "RED": "bear"})
    # synthetic panel + bench -> Ctx.from_raw mask machinery
    n_syn, rng = 700, np.random.default_rng(20285001)
    idx_syn = pd.bdate_range("2022-01-03", periods=n_syn)
    raw_syn = {}
    for s in ("a", "b"):
        px = 10.0 * np.cumprod(1.0 + rng.normal(0.0005, 0.012, n_syn))
        raw_syn[s] = pd.DataFrame({
            "open": px, "high": px * 1.01, "low": px * 0.99,
            "close": px, "volume": np.full(n_syn, 1e6),
            "amount": np.full(n_syn, 1e7)}, index=idx_syn)
    bench_syn = pd.Series(np.linspace(4000.0, 5000.0, n_syn), index=idx_syn)
    ctx_syn = Ctx.from_raw(raw_syn, bench_syn)
    ctx_syn2 = Ctx.from_raw(raw_syn, bench_syn)
    check("Ctx.from_raw masks deterministic",
          ctx_syn.bull_mask.equals(ctx_syn2.bull_mask)
          and ctx_syn.delever_scale.equals(ctx_syn2.delever_scale))
    ma200 = bench_syn.rolling(200).mean()
    check("from_raw bull/bear masks == screen-face semantics",
          bool(ctx_syn.bull_mask.iloc[250:].equals(
              (bench_syn >= ma200).iloc[250:]))
          and not bool(ctx_syn.bear_mask.iloc[:199].any()))
    # dual nulls (formula + determinism + positive-mean face)
    r_pos = np.abs(rng.normal(0.001, 0.01, 300))
    dn1 = _dual_nulls(r_pos, 0)
    dn2 = _dual_nulls(r_pos, 0)
    check("dual nulls deterministic + spec fields",
          dn1 == dn2 and dn1["B"] == 2000 and dn1["P"] == 2000
          and dn1["block"] == 20 and dn1["ci_lower_positive"])
    # CostPatch x2 single-source + restore (p5c selftest #7 mirror)
    eb = sys.modules["engine.backtester"]
    orig_cls = eb.FeeSchedule
    with sg.CostPatch(2.0):
        fee2 = eb.FeeSchedule()
        rate2 = (fee2.commission_rate + fee2.handling_fee
                 + fee2.supervision_fee + fee2.slippage_a)
    check("CostPatch x2 == COST_X2_RATE + name restored",
          abs(rate2 - sg.COST_X2_RATE) < 1e-12
          and eb.FeeSchedule is orig_cls and orig_cls.__name__ == "FeeSchedule")
    # collapse gate: representative = lowest candidate_id
    base = rng.normal(0.0, 0.01, 200)
    rets_df = pd.DataFrame({
        "W1-01": base,
        "W1-02": base * 1.0000001,          # |corr| ~1.0 -> collapses
        "W1-03": rng.normal(0.0, 0.01, 200)  # independent -> kept
    })
    kept_c, clusters_c, elim_c = _collapse_survivors(rets_df)
    check("corr-dedup collapse: lowest id kept, variants audited",
          kept_c == ["W1-01", "W1-03"] and clusters_c.get("W1-01") == ["W1-02"]
          and elim_c == ["W1-02"])
    # passive_rel EW buy&hold zero-rebalance
    close_syn = pd.DataFrame({"a": [10.0, 11.0, 12.0],
                              "b": [5.0, 5.0, 6.0]},
                             index=pd.bdate_range("2024-01-01", periods=3))
    rel = passive_rel(close_syn, ["a", "b"], close_syn.index[0],
                      close_syn.index[-1])
    hand = (12.0 / 10.0 + 6.0 / 5.0) / 2.0      # member relatives at end
    check("passive_rel == EW buy&hold zero-rebalance",
          abs(float(rel.iloc[-1]) - hand) < 1e-12)
    # yearly returns + crash-year line
    eq_syn = pd.Series(np.linspace(1.0, 1.5, 260),
                       index=pd.bdate_range("2023-01-02", periods=260))
    yr = _yearly_returns(eq_syn)
    check("yearly returns + crash line", len(yr) == 1
          and yr[2023] == round(0.5, 4) and -0.5 <= CRASH_YEAR == -0.30)
    # _judge_cell hermetic: synthetic legs + starts/passive/states + determinism
    fam0 = ctx_syn.roster[0]
    d0 = next(sample_draws(fam0, 4))
    cand_syn = {"id": "W1-SYN0", "family": fam0["family"],
                "params": d0[1], "axes": d0[2]}
    starts_syn = {"L": {"6m": [260, 300], "12m": [260], "24m": []},
                  "D": {"6m": [260], "12m": [], "24m": []}}
    passive_syn = {"L": {"6m": {"260": 0.01, "300": 0.02},
                        "12m": {"260": 0.03}, "24m": {}},
                  "D": {"6m": {"260": 0.01}, "12m": {}, "24m": {}}}
    states_syn = pd.Series(rng.choice(["GREEN", "YELLOW", "ORANGE"],
                                      n_syn), index=idx_syn)
    st_syn = {"ctx_L": ctx_syn, "ctx_D": ctx_syn2, "idx_L": idx_syn,
              "idx_D": idx_syn,
              "roster_by_family": {f["family"]: f for f in ctx_syn.roster},
              "starts": starts_syn, "passive": passive_syn,
              "states": states_syn}
    _judge_init(st_syn)
    cell_syn = {"cell_id": "JUDGE|W1-SYN0", "candidate_id": "W1-SYN0",
                "i": 0, "cand": cand_syn}
    row1 = _j(_judge_cell(cell_syn))
    row2 = _j(_judge_cell(cell_syn))
    need = {"cell_id", "candidate_id", "family", "i", "legs",
            "legL_daily_returns", "legL_oos", "descriptive",
            "crisis_days_gt8pct", "dual_nulls", "n_eff_start_windows",
            "sample_sufficient"}
    check("_judge_cell schema keys (B7b consumer contract)",
          need.issubset(set(row1))
          and {"x1", "x2", "regime_start_windows"}.issubset(
              set(row1["legs"]["L"]))
          and {"sharpe_full", "n_trades", "n_entries", "max_dd", "yearly",
               "beat"}.issubset(set(row1["legs"]["L"]["x1"])))
    check("_judge_cell byte-stable double-run (synthetic)",
          json.dumps(row1, sort_keys=True) == json.dumps(row2, sort_keys=True)
          and eb.FeeSchedule is orig_cls)
    check("sample sufficiency honest on tiny synthetic",
          row1["sample_sufficient"] is False
          and row1["n_eff_start_windows"] == 4)   # 3 leg-L + 1 leg-D starts
    print(f"selftest: {ok}/{n_checks} PASS")
    return 0 if ok == n_checks else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("generate")
    g.set_defaults(func=cmd_generate)
    s = sub.add_parser("screen")
    s.add_argument("--pos-from", type=int, default=0)
    s.add_argument("--pos-to", type=int, default=10 ** 9)
    s.add_argument("--workers", type=int, default=0)
    s.set_defaults(func=cmd_screen)
    f = sub.add_parser("finalize")
    f.set_defaults(func=cmd_finalize)
    jp = sub.add_parser("judge-prep")
    jp.set_defaults(func=cmd_judge_prep)
    js_ = sub.add_parser("judge")
    js_.add_argument("--shard", type=int, default=0)
    js_.add_argument("--shards", type=int, default=1)
    js_.add_argument("--workers", type=int, default=0)
    js_.set_defaults(func=cmd_judge)
    jf = sub.add_parser("judge-finalize")
    jf.set_defaults(func=cmd_judge_finalize)
    t = sub.add_parser("selftest")
    t.set_defaults(func=cmd_selftest)
    args = ap.parse_args()
    if getattr(args, "workers", 0) == 0:
        from scripts.parallel_runner import worker_cap
        args.workers = max(1, worker_cap())
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
