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

Class per prereg: candidate-search funnel (stage-1 = screen, NOT a judgment
face; zero registration effect from stage-1 alone). Ledger append happens at
screen finalize with actual enrolled-candidate counts only.

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
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

from config import PATHS
from engine import run_backtest
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


# --------------------------------------------------------------- panel loading

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
    bench = pd.read_csv(os.path.join(PATHS.basic_dir, "csi300.csv"),
                        parse_dates=["date"]).set_index("date")["close"].sort_index()
    bench = bench[bench.index <= pd.Timestamp(CUTOFF)]
    return out, prices, bench


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


# --------------------------------------------------------------- selftest

def cmd_selftest(args):
    ok = 0

    def check(name, cond):
        nonlocal ok
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
    print(f"selftest: {ok}/11 PASS")
    return 0 if ok == 11 else 1


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
    t = sub.add_parser("selftest")
    t.set_defaults(func=cmd_selftest)
    args = ap.parse_args()
    if getattr(args, "workers", 0) == 0:
        from scripts.parallel_runner import worker_cap
        args.workers = max(1, worker_cap())
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
