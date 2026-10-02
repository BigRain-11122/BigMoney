"""PERPETUAL-N4-B1 runner (T-2026-10-03-151-P1, N4 face wave-1;
O-20261002-2155 P0 engine-supply completion seat).

Bootstrap alternate-history replay on the REGISTERED members (canon
research/PERPETUAL_FACES.md v1.0 sec.2 N4 row): moving-block resample
of the joint bar history TRUNCATED at evidence_cutoff (forward-history
untouched by construction) -> K parallel-universe histories -> verbatim
same-source member replay (live.paper anchor-gate convention verbatim:
SIGNAL_BUILDERS + params-minus-entry + ExitPatch + dd_control +
engine.run_backtest; member's OWN exit axis replayed, engine default
exit stack never rewritten). Measurement-deepening face: products are
deeper confidence faces only -- zero registration, zero funnel, zero
promotion lines (law sec.2 L24).

PRE-REGISTERED: research/PERPETUAL_N4_B1_PREREG.md -- FROZEN 2026-10-03
r602 bm-a (five-condition freeze gate, receipts in the prereg head; band-
scan freeze rerun + banned-gate ADMIT + SEED_REGISTRY perpetual_n4_b1
base landed in the same commit, R250 one-step). Pre-freeze the runner
mechanically refused burns (R99/R250); post-freeze cmd_run unlocks and
reads PINNED-L / PINNED-K from the prereg fail-closed.

Seed bands (prereg sec.5 draft receipt results/_r600bma_n4b1_band_scan.py,
re-run at freeze per R99/R250): gen 68_501..68_999 / scrnull 69_000..
69_499 / unc 69_500..69_999. Registry landing = freeze commit only
(one-step R250). Skeleton + probe use ZERO band seeds: probe/design
seeds are out-of-band 95_006+ (N2-W15 95_004/95_005 law, N3 95_000..
95_003 cluster adjacent). K universes are MEMBER-PAIRED (same universe
seed k -> same synthetic history for every member; prereg sec.3
"seed=band position + universe index").

Resample layer (prereg sec.1 alpha; L pinned at freeze from probe
facts): circular moving-block bootstrap on the JOINT date axis (same
sampled date sequence for all symbols -- cross-sectional structure
preserved within and across blocks). Per sampled source date d the bar
carries its per-symbol return r=close(d)/close(prev source date), its
intra-bar shape ratios open/high/low vs close, and its volume/amount;
the synthetic close path = anchor_close * cumprod(1+r); open/high/low
rebuilt from the carried ratios (high>=max(open,close), low<=min(open,
close) hold by construction -- source-bar coherence is ratio-invariant).

Products:
  results/perpetual_faces/n4_b1/probe.json          probe facts (prereg sec.2)
  results/perpetual_faces/n4_b1/universes-<ID>.jsonl  append-only per-member
      per-universe rows (checkpoint; presence=done; rerun byte-equal:
      rows carry NO wall-clock fields)
  results/p2cal_ext/n4_b1/shard-<i>-of-6.json       SatEngine shard receipt
      (engine-lane checkpoint; presence=done via _shard_valid = k-set
      completeness against the frozen prereg pins)
  results/perpetual_faces/n4_b1_results.json        finalize merge (post-burn)

Usage:
  python scripts/perpetual_faces_n4.py probe              # read-only facts
  python scripts/perpetual_faces_n4.py run --member <ID>  # post-freeze only
  python scripts/perpetual_faces_n4.py run --shard i --of 6 --wave B1 \
      [--workers P] [--lane engine]   # SatEngine lane (shard=member;
                                      # SATURATION_ENGINE_LAW sec.1/2)
  python scripts/perpetual_faces_n4.py status
  python scripts/perpetual_faces_n4.py finalize    # post-burn §4 merge
  python scripts/perpetual_faces_n4.py selftest
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

from config import PATHS
from knowledge import cost_spec
import science_gates as sg
from science_gates import SEED_REGISTRY

# same-source replay convention (live.paper module import = zero
# re-implementation of the anchor-gate replay pipeline)
from live.paper import (SIGNAL_BUILDERS, ExitPatch, build_panels, load_core)
from firm.hr import TRADERS_DIR
from engine import run_backtest
import engine.backtester as _eb

EVIDENCE_CUT = "2026-09-22"           # prereg sec.2 hard cutoff (six members)
BATCH = "PERPETUAL-N4-B1"
WAVE_DIR = os.path.join(PATHS.results_dir, "perpetual_faces", "n4_b1")
BATCH_JSON = os.path.join(PATHS.results_dir, "perpetual_faces",
                          "n4_b1_results.json")
PROBE_JSON = os.path.join(WAVE_DIR, "probe.json")
PREREG = os.path.join(PATHS.root, "research", "PERPETUAL_N4_B1_PREREG.md")
DRAFT_MARKER = "DRAFT-NOT-FROZEN"

# seed bands (prereg sec.5 DRAFT; registry landing = freeze commit only)
BAND_GEN = (68_501, 68_999)
BAND_SCRNULL = (69_000, 69_499)
BAND_UNC = (69_500, 69_999)
PROBE_SEED = 95_006                   # out-of-band (N2 95_004/95_005 law)
PROBE_L_DEFAULT = 20                  # probe smoke block length (facts only)

# prereg sec.2 OPEN pins -> probe facts -> freeze writes them into the
# prereg verbatim; runner defaults below are PROBE-ONLY values
K_DEFAULT = 200                       # proposal; freeze pins real K
MEMBERS = ("COMPOSITE-CE-01", "COMPOSITE-CE-02", "DROUGHT-CE-01",
           "ENGULF-CE-01", "NEEDLE-DE-01", "VOLATILITY-CE-01")

# --- SatEngine FAMILIES adapter (T-151 deliverable (5); O-20261002-2155
# seat (b) family contract as landed for N1: the engine queue/orphan/
# ignite generators consume WAVE_CONFIGS + _set_wave + _shard_valid from
# the family module -- zero engine knowledge of the N4 face itself).
NSHARDS = len(MEMBERS)                 # N4 shard space = members (6)
WAVE_NAME = "B1"
SHARD_CKPT_DIR = os.path.join(PATHS.results_dir, "p2cal_ext", "n4_b1")
WAVE_CONFIGS = {
    WAVE_NAME: {
        "batch": BATCH,
        "prereg": PREREG,
        "shard_subdir": "n4_b1",       # engine _shard_path layout
        "engine_owner": "bm-a",        # prereg freeze: local SatEngine lane
        "nshards": NSHARDS,
        "members": MEMBERS,
        "rows_dir": WAVE_DIR,
    },
}
WAVE = WAVE_NAME                       # active wave face (_set_wave pin)


def _set_wave(w) -> None:
    """Engine family contract: pin the active wave (BATCH/PREREG are
    module constants in this single-wave module; the pin exists so the
    engine's probe/reset pattern stays one shape across families).
    Foreign wave key = KeyError = honest fail, never a silent default."""
    global WAVE
    if w not in WAVE_CONFIGS:
        raise KeyError(f"unknown N4 wave: {w!r} "
                       f"(registered: {tuple(WAVE_CONFIGS)})")
    WAVE = w


def shard_member(shard: int, nshards: int) -> str:
    """Shard space = the six registered members (prereg sec.2); shard i
    burns member MEMBERS[i] -- the CLI --shard shim resolves here."""
    if nshards != NSHARDS:
        raise ValueError(f"N4 shard space is {NSHARDS} members, "
                         f"got --of {nshards}")
    if not (0 <= shard < NSHARDS):
        raise ValueError(f"shard {shard} out of range 0..{NSHARDS - 1}")
    return MEMBERS[shard]


def _shard_valid(path: str, shard: int, nshards: int) -> bool:
    """Engine checkpoint validator (presence=done law, N1 contract shape):
    the receipt parses, identity fields match the wave face, the pins
    agree with the FROZEN prereg (fail-closed parse), and the rows file
    carries the complete k-set 0..K-1 -- a truncated burn never counts
    as done."""
    try:
        with open(path, encoding="utf-8") as fh:
            d = json.load(fh)
    except Exception:
        return False
    try:
        k_exp, l_exp = _frozen_K(), _frozen_L()
    except RuntimeError:
        return False
    if d.get("batch") != BATCH or d.get("shard") != shard \
            or d.get("nshards") != nshards or nshards != NSHARDS:
        return False
    if d.get("member") != MEMBERS[shard]:
        return False
    if d.get("L") != l_exp or d.get("k_expected") != k_exp \
            or d.get("evidence_cutoff") != EVIDENCE_CUT:
        return False
    ks = {r.get("k") for r in read_rows(d.get("member"))}
    return ks == set(range(k_exp))


def _machine_id() -> str:
    try:
        with open(os.path.join(PATHS.root, "fleet", "machine.json"),
                  encoding="utf-8") as fh:
            return json.load(fh)["machine_id"]
    except Exception:
        return "unknown"


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S+08:00")


def load_member(mid: str) -> dict:
    fp = os.path.join(TRADERS_DIR, mid + ".json")
    if not os.path.exists(fp):
        raise FileNotFoundError(mid)
    with open(fp, encoding="utf-8") as fh:
        return json.load(fh)


def source_panel() -> dict:
    """Full in-service panel truncated at EVIDENCE_CUT (forward-history
    untouched by construction; RW-4 gate rides inside load_core)."""
    prices = load_core()
    cut = pd.Timestamp(EVIDENCE_CUT)
    return {s: df[df.index <= cut] for s, df in prices.items()}


# ------------------------------------------------------------- resample
# alpha: circular moving-block bootstrap on the joint date axis.
# AXIS POLICY (prereg sec.2 OPEN pin -- probe reports both lengths, the
# freeze commit pins the axis into the prereg verbatim): "intersection"
# = common fully-listed era (every core symbol has a real bar on every
# sampled date; zero NaN/flat-stretch artifacts in the synthetic panel;
# cost = the pre-listing era drops out of the alternate history).

def _common_index(prices: dict) -> pd.DatetimeIndex:
    idx = None
    for df in prices.values():
        idx = df.index if idx is None else idx.intersection(df.index)
    return idx.sort_values()


def resample_history(prices: dict, L: int, seed: int,
                     axis: str = "intersection") -> dict:
    """One parallel-universe bar history from the truncated source panel.

    Same DatetimeIndex as the (axis-restricted) source; per-symbol
    OHLCV+amount DataFrames in the load_core schema. Deterministic in
    (L, seed) on a fixed source panel.
    """
    if L < 2:
        raise ValueError("block length L must be >= 2")
    if axis == "intersection":
        cidx = _common_index(prices)
        prices = {s: df.loc[cidx] for s, df in prices.items()}
    idx = None
    for s, df in prices.items():
        if idx is None:
            idx = df.index
        elif not df.index.equals(idx):
            raise ValueError("panel index drift across symbols")
    T = len(idx)
    if T < 2 * L:
        raise ValueError(f"history too short for L={L}: T={T} < 2L")
    rng = np.random.default_rng(seed)
    # block-start draws: ceil(T/L) blocks, each L source dates, wraparound
    n_blocks = -(-T // L)
    starts = rng.integers(0, T, size=n_blocks)
    dates = [int((st + j) % T) for st in starts for j in range(L)][:T]
    pos = np.asarray(dates)
    # per-symbol source return/shape faces (vectorized, date-aligned;
    # axis-restricted source has no NaN cells by construction)
    out = {}
    for s, df in prices.items():
        c = df["close"].to_numpy(dtype=float)
        r = np.empty(T)
        r[0] = 0.0                                   # anchor bar
        r[1:] = c[1:] / c[:-1] - 1.0
        oc = df["open"].to_numpy(dtype=float) / c
        hc = df["high"].to_numpy(dtype=float) / c
        lc = df["low"].to_numpy(dtype=float) / c
        close = c[0] * np.cumprod(1.0 + r[pos])
        out[s] = pd.DataFrame({
            "open": close * oc[pos], "high": close * hc[pos],
            "low": close * lc[pos], "close": close,
            "volume": df["volume"].to_numpy(dtype=float)[pos],
            "amount": df["amount"].to_numpy(dtype=float)[pos]}, index=idx)
    return out


def _bar_coherence_ok(prices: dict) -> tuple[bool, str]:
    for s, df in prices.items():
        if not ((df["high"] >= df[["open", "close"]].max(axis=1) - 1e-9).all()
                and (df["low"] <= df[["open", "close"]].min(axis=1) + 1e-9).all()):
            return False, s
        if (df["volume"] < 0).any() or (df["close"] <= 0).any():
            return False, s
    return True, ""


# ------------------------------------------------------------- replay

def replay_universe(t: dict, prices_synth: dict) -> dict:
    """Same-source member replay on one universe (anchor-gate convention
    verbatim; member's OWN exit axis -- ExitPatch + exit_signal=(entry<=0)
    + dd_control passthrough; engine default cost = X1, bite-checked)."""
    entry_key = t["params"]["entry"]
    builder = SIGNAL_BUILDERS.get(entry_key)
    if builder is None:
        raise KeyError(f"entry not in SIGNAL_BUILDERS: {entry_key!r}")
    P = build_panels(prices_synth)
    entry = builder(P)
    params = {k: v for k, v in t["params"].items() if k != "entry"}
    with ExitPatch(t.get("exit_overrides")):
        res = run_backtest(prices_synth, params, entry_signal=entry,
                           exit_signal=(entry <= 0),
                           dd_control=t.get("dd_control"),
                           evidence_cutoff=EVIDENCE_CUT)
    m = res["metrics"]
    eq = pd.Series(res["equity_curve"], index=P["close"].index[:len(res["equity_curve"])])
    rets = eq.pct_change().dropna().tolist()
    return {"sharpe": round(float(m["sharpe"]), 6),
            "annual_return": round(float(m["annual_return"]), 6),
            "max_drawdown": round(float(m["max_drawdown"]), 6),
            "num_trades": int(m["num_trades"]), "bars": int(len(eq)),
            "final_equity": round(float(eq.iloc[-1]), 2) if len(eq) else None,
            "daily_returns": rets}


def _fee_x1_ok() -> bool:
    fee = _eb.FeeSchedule()
    rate = (fee.commission_rate + fee.handling_fee
            + fee.supervision_fee + fee.slippage_a)
    return abs(rate - cost_spec.X1_RATE) < 1e-9


# ------------------------------------------------------------- checkpoints

def member_rows_path(mid: str) -> str:
    return os.path.join(WAVE_DIR, f"universes-{mid}.jsonl")


def read_rows(mid: str) -> list:
    rows = []
    fp = member_rows_path(mid)
    if os.path.exists(fp):
        with open(fp, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue                     # corrupt tail tolerated
                if isinstance(rec, dict):
                    rows.append(rec)
    return rows


def _append_row(mid: str, rec: dict):
    os.makedirs(WAVE_DIR, exist_ok=True)
    with open(member_rows_path(mid), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _prereg_frozen() -> bool:
    try:
        with open(PREREG, encoding="utf-8") as fh:
            head = fh.read(2000)
    except OSError:
        return False
    return DRAFT_MARKER not in head


# ------------------------------------------------------------- commands

def cmd_probe() -> int:
    """Read-only facts for prereg sec.2 backfill (T/L/K distribution
    evidence). Zero band seeds, zero ledger writes, zero member JSON
    touches. Six-member real-engine smoke at ONE out-of-band universe."""
    t0 = time.time()
    prices = source_panel()
    union_idx = next(iter(prices.values())).index
    cidx = _common_index(prices)
    prices = {s: df.loc[cidx] for s, df in prices.items()}
    T = len(cidx)
    P = build_panels(prices)
    ew = P["close"].mean(axis=1)
    rets = ew.pct_change().dropna()
    acfs = {f"lag{lag}": round(float(rets.autocorr(lag)), 5)
            for lag in range(1, 11)}
    band = 2.0 / (len(rets) ** 0.5)
    l_cands = [lag for lag in range(2, 41)
               if abs(acfs.get(f"lag{lag}", 0.0)) < band]
    out = {"batch": BATCH, "evidence_cutoff": EVIDENCE_CUT,
           "probe_seed": PROBE_SEED, "probe_L": PROBE_L_DEFAULT,
           "axis_policy": "intersection (prereg sec.2 OPEN pin -- freeze "
                          "commits the axis choice from these facts)",
           "bars_T_intersection": int(T),
           "bars_T_union": int(len(union_idx)),
           "n_symbols": len(prices),
           "first_bar": str(cidx[0].date()), "last_bar": str(cidx[-1].date()),
           "return_acf": acfs, "white_noise_band": round(band, 5),
           "L_candidates_in_band": l_cands[:10],
           "K_proposal": K_DEFAULT, "engine_cost_x1_bite": _fee_x1_ok(),
           "machine": _machine_id(), "generated": _now_iso(),
           "members": {}}
    sm_start = time.time()
    for mid in MEMBERS:
        t = load_member(mid)
        synth = resample_history(prices, PROBE_L_DEFAULT, PROBE_SEED)
        t1 = time.time()
        r = replay_universe(t, synth)
        dur = round(time.time() - t1, 3)
        out["members"][mid] = {
            "entry": t["params"]["entry"],
            "has_dd_control": bool(t.get("dd_control")),
            "smoke_L20_seed95006": {k: v for k, v in r.items()
                                    if k != "daily_returns"},
            "smoke_duration_sec": dur}
    out["six_member_smoke_wall_sec"] = round(time.time() - sm_start, 2)
    out["probe_wall_sec"] = round(time.time() - t0, 2)
    os.makedirs(WAVE_DIR, exist_ok=True)
    with open(PROBE_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "members"},
                     ensure_ascii=False, indent=1))
    print("probe facts ->", PROBE_JSON)
    return 0


def _cap_blas_threads():
    """n1 _cap_blas_threads verbatim (CEO foreground-reserve law: BLAS
    threads capped at 1 per pool worker)."""
    for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                "NUMEXPR_NUM_THREADS"):
        os.environ.setdefault(var, "1")


def _row(member_id: str, k: int, seed: int, L: int, r: dict) -> dict:
    """Deterministic per-universe row (NO wall-clock fields -- rerun
    byte-equal; serial/pool drivers produce identical rows)."""
    return {"id": f"{member_id}::u{k:03d}", "member": member_id, "k": k,
            "seed": seed, "L": L, "batch": BATCH,
            "evidence_cutoff": EVIDENCE_CUT,
            "sharpe": r["sharpe"], "annual_return": r["annual_return"],
            "max_drawdown": r["max_drawdown"],
            "num_trades": r["num_trades"], "bars": r["bars"]}


_N4_CTX = None        # per-process burn context (spawn-safe global)
_LAST_BURN = {}       # last cmd_run facts (workers_actual/n) -> receipt audit


def _n4_worker_init(member_id: str, t: dict, prices: dict, L: int):
    """Pool initializer (r511 law: parent assembles the fixture ONCE --
    member json + source panel; workers re-attach, never rebuild)."""
    global _N4_CTX
    _N4_CTX = (member_id, t, prices, L)


def _n4_run_universe(k: int) -> dict:
    member_id, t, prices, L = _N4_CTX
    seed = BAND_GEN[0] + k
    r = replay_universe(t, resample_history(prices, L, seed))
    return _row(member_id, k, seed, L, r)


def _burn_rows(member_id: str, t: dict, prices: dict, todo: list,
               workers: int = 1) -> tuple:
    """Burn the todo k-list for one member; rows append as EACH universe
    completes (r340 incremental-checkpoint law -- mid-kill re-burn only
    costs the un-burned tail). workers>1 = ProcessPool via the shared
    parallel_runner (O-2355 multicore; single-source, no hand-rolled
    loop); each universe is an independent rng draw, so results are
    deterministic per k regardless of scheduling. Returns (n_burned,
    workers_actual) -- the audit face records the CLAMPED pool width,
    never the raw request."""
    L = _frozen_L()
    if workers <= 1:
        for k in todo:
            seed = BAND_GEN[0] + k
            r = replay_universe(t, resample_history(prices, L, seed))
            _append_row(member_id, _row(member_id, k, seed, L, r))
            print(f"{member_id}::u{k:03d} seed={seed} "
                  f"sharpe={r['sharpe']} trades={r['num_trades']}",
                  flush=True)
        return len(todo), 1
    _cap_blas_threads()
    from parallel_runner import run_cells_parallel, worker_cap
    w = max(1, min(workers, worker_cap()))   # s6 policy cap + RAM guard
    run_cells_parallel(
        [(k, _n4_run_universe, (k,)) for k in todo],
        workers=w, desc=f"n4 {member_id}",
        initializer=_n4_worker_init, initargs=(member_id, t, prices, L),
        on_result=lambda key, row: _append_row(member_id, row))
    return len(todo), w


def cmd_run(member_id: str, universes: int | None = None,
            workers: int = 1) -> int:
    """Post-freeze wave burn (one member shard). Mechanically refuses
    while the prereg head carries the DRAFT marker (R99/R250: no burn
    before the freeze commit)."""
    if not _prereg_frozen():
        print("REFUSED: prereg head still carries " + DRAFT_MARKER +
              " -- freeze commit (five-condition gate) precedes any burn "
              "(R99/R250). Honest exit, zero burn, zero rows.")
        return 2
    if member_id not in MEMBERS:
        print(f"unknown member {member_id}; members: {MEMBERS}")
        return 2
    t = load_member(member_id)
    prices = source_panel()
    k_max = universes or _frozen_K()
    if k_max > (BAND_GEN[1] - BAND_GEN[0] + 1):
        print(f"K={k_max} exceeds gen band width "
              f"{BAND_GEN[1] - BAND_GEN[0] + 1}")
        return 2
    done = {r["k"] for r in read_rows(member_id)}
    todo = [k for k in range(k_max) if k not in done]
    if not todo:
        print(f"{member_id}: all {k_max} universes already done (idempotent)")
        return 0
    n, w_actual = _burn_rows(member_id, t, prices, todo, workers)
    _LAST_BURN.clear()
    _LAST_BURN.update({"n": n, "workers_actual": w_actual,
                       "requested": workers})
    print(f"{member_id}: burn complete {n} rows "
          f"(total {len(done) + n}/{k_max}, workers={w_actual})")
    return 0


def cmd_run_shard(shard: int, nshards: int, workers: int = 1,
                  lane: str = "engine") -> int:
    """Engine-lane shim (SatEngine runner_args contract): shard i =
    member MEMBERS[i]; after the burn, the engine receipt lands at
    results/p2cal_ext/n4_b1/shard-<i>-of-<nshards>.json (presence=done
    via _shard_valid). Engine lane is claim-exempt (law sec.2) -- the
    receipt + rows files are the record; no pool handshake exists for
    the N4 face in any lane."""
    if lane not in ("engine", "pool"):
        print(f"unknown lane {lane!r} (engine|pool)")
        return 2
    try:
        member_id = shard_member(shard, nshards)
    except ValueError as exc:
        print(f"REFUSED: {exc}")
        return 2
    t0 = time.time()
    _LAST_BURN.clear()
    rc = cmd_run(member_id, None, workers)
    if rc != 0:
        return rc
    w_actual = _LAST_BURN.get("workers_actual")
    n_burned = _LAST_BURN.get("n", 0)
    k_exp = _frozen_K()
    rows = read_rows(member_id)
    ks = {r.get("k") for r in rows}
    if ks != set(range(k_exp)):
        print(f"REFUSED receipt: {member_id} k-set incomplete "
              f"({len(ks)}/{k_exp}) -- no checkpoint written")
        return 2
    os.makedirs(SHARD_CKPT_DIR, exist_ok=True)
    ckpt = os.path.join(SHARD_CKPT_DIR, f"shard-{shard}-of-{nshards}.json")
    if w_actual is None:                       # idempotent skip (no burn)
        parallel_face = "no new burn (idempotent skip; rows already complete)"
    elif w_actual > 1:
        parallel_face = f"multiprocess (parallel_runner, {w_actual} workers, O-2355)"
    else:
        parallel_face = "serial (single-process)"
    out = {"batch": BATCH, "face": "N4", "wave": WAVE_NAME,
           "preregistered_doc": PREREG,
           "shard": shard, "nshards": nshards, "member": member_id,
           "k_expected": k_exp, "k_burned": len(ks), "L": _frozen_L(),
           "evidence_cutoff": EVIDENCE_CUT,
           "rows_file": os.path.relpath(member_rows_path(member_id),
                                        PATHS.root),
           "audit": {"elapsed_sec": round(time.time() - t0, 1),
                     "workers": w_actual,
                     "workers_requested": workers,
                     "n_universes_burned": n_burned,
                     "cpu_parallel": parallel_face,
                     "lane": lane, "machine": _machine_id()}}
    with open(ckpt, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(f"saved: {ckpt} ({out['audit']['elapsed_sec']}s, "
          f"k={len(ks)}/{k_exp})")
    return 0


def _frozen_L() -> int:
    """L is pinned at the freeze commit into the prereg sec.1 verbatim;
    this reads the pinned value from the prereg (fail-closed if absent)."""
    import re
    with open(PREREG, encoding="utf-8") as fh:
        src = fh.read()
    m = re.search(r"PINNED-L\s*=\s*(\d+)", src)
    if not m:
        raise RuntimeError("PINNED-L not found in prereg -- freeze must "
                           "write the probe-fact-selected L (sec.1)")
    return int(m.group(1))


def _frozen_K() -> int:
    """K is pinned at the freeze commit into the prereg sec.3 verbatim
    (PINNED-K = 200); fail-closed if absent (same law as _frozen_L)."""
    import re
    with open(PREREG, encoding="utf-8") as fh:
        src = fh.read()
    m = re.search(r"PINNED-K\s*=\s*(\d+)", src)
    if not m:
        raise RuntimeError("PINNED-K not found in prereg -- freeze must "
                           "write the universe count (sec.3)")
    return int(m.group(1))


def _quantile(sorted_vals: list, q: float) -> float:
    """Nearest-rank quantile on an ascending list -- the science_gates
    bootstrap_ci_sharpe indexing convention (int(q*(n-1))), one shape
    across the §4 faces."""
    n = len(sorted_vals)
    return float(sorted_vals[int(q * (n - 1))])


def _member_faces(rows: list, center_rets: list,
                  center_sharpe: float) -> dict:
    """Per-member §4 product faces (prereg FROZEN wording, science_gates
    verbatim import -- thresholds never hand-copied): K-universe Sharpe
    distribution (pure math, zero engine re-run) + real-history center
    stationary-bootstrap CI95 (seed=own scrnull band base 69_000, block
    10.0, n_resamples 1000 = function defaults) + DSR from stored stats
    (sr=center replay Sharpe, sigma=K-universe sample std ddof=1,
    n_trials=K). Pure in (rows, center_rets, center_sharpe)."""
    sharpes = sorted(float(r["sharpe"]) for r in rows)
    n = len(sharpes)
    import statistics
    sigma_sr = statistics.stdev(sharpes)          # sample std (ddof=1)
    ci = sg.bootstrap_ci_sharpe(center_rets, seed=BAND_SCRNULL[0])
    dsr = sg.dsr_from_stats(sr_annualized=center_sharpe,
                           sigma_sr=sigma_sr, n_trials=n)
    return {
        "k_universe_sharpe": {
            "n": n,
            "median": round(_quantile(sharpes, 0.5), 6),
            "p10": round(_quantile(sharpes, 0.10), 6),
            "p90": round(_quantile(sharpes, 0.90), 6),
            "ci95_low": round(_quantile(sharpes, 0.025), 6),
            "ci95_high": round(_quantile(sharpes, 0.975), 6),
            "positive_fraction": round(
                sum(1 for s in sharpes if s > 0.0) / n, 4),
            "sample_std": round(sigma_sr, 6)},
        "bootstrap_ci_sharpe": ci,
        "dsr_from_stats": dsr,
    }


def cmd_finalize() -> int:
    """Post-burn finalize merge (prereg §4 three-product face -> results/
    perpetual_faces/n4_b1_results.json; §6 backfill pointer). FAIL-CLOSED
    unless every member carries the complete k-set (presence=done law).
    Zero registration, zero funnel, zero promotion lines (law sec.2 L24
    measurement-deepening face); honest negatives (CI lower bound <= 0 /
    DSR <= 0.5) are reported, never blocked."""
    K = _frozen_K()
    rows_by_member = {}
    for mid in MEMBERS:
        rows = read_rows(mid)
        ks = {r.get("k") for r in rows}
        if ks != set(range(K)):
            print(f"FAIL-CLOSED: {mid} k-set incomplete "
                  f"({len(ks)}/{K}) -- finalize refuses on a partial wave")
            return 2
        rows_by_member[mid] = rows
    prices = source_panel()
    cidx = _common_index(prices)
    prices_i = {s: df.loc[cidx] for s, df in prices.items()}
    t0 = time.time()
    out = {"batch": BATCH, "face": "N4", "wave": WAVE_NAME,
           "preregistered_doc": PREREG,
           "evidence_cutoff": EVIDENCE_CUT,
           "pins": {"K": K, "L": _frozen_L(),
                    "axis": "intersection",
                    "seed_gen_base": BAND_GEN[0],
                    "seed_scrnull_base": BAND_SCRNULL[0]},
           "members": {}}
    for mid in MEMBERS:
        t = load_member(mid)
        center = replay_universe(t, prices_i)
        faces = _member_faces(rows_by_member[mid],
                              center["daily_returns"], center["sharpe"])
        out["members"][mid] = {
            "center_replay": {k: center[k] for k in
                              ("sharpe", "annual_return", "max_drawdown",
                               "num_trades", "bars")},
            **faces}
        ku = faces["k_universe_sharpe"]
        ci = faces["bootstrap_ci_sharpe"]
        print(f"{mid}: universe median={ku['median']} "
              f"CI95=[{ku['ci95_low']},{ku['ci95_high']}] "
              f"pos={ku['positive_fraction']} | center Sharpe="
              f"{center['sharpe']} bootstrap CI95=[{ci['ci95_low']},"
              f"{ci['ci95_high']}] | DSR={faces['dsr_from_stats']['dsr']}")
    out["audit"] = {"elapsed_sec": round(time.time() - t0, 1),
                    "machine": _machine_id(),
                    "n_universe_rows": sum(len(v) for v in
                                          rows_by_member.values())}
    os.makedirs(os.path.dirname(BATCH_JSON), exist_ok=True)
    with open(BATCH_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(f"saved: {BATCH_JSON} ({out['audit']['elapsed_sec']}s, "
          f"{out['audit']['n_universe_rows']} universe rows)")
    return 0


def cmd_status() -> int:
    print(f"batch={BATCH} cutoff={EVIDENCE_CUT} "
          f"bands gen{BAND_GEN}/scrnull{BAND_SCRNULL}/unc{BAND_UNC} "
          f"prereg_frozen={_prereg_frozen()}")
    probe = ("probe.json present" if os.path.exists(PROBE_JSON)
             else "probe.json absent")
    print(f"probe: {probe}")
    for mid in MEMBERS:
        rows = read_rows(mid)
        ks = sorted({r["k"] for r in rows})
        span = f"{ks[0]}..{ks[-1]}" if ks else "-"
        print(f"  {mid}: {len(rows)} rows, k-span {span}")
    return 0


def _synth_panel(n: int = 900, seed: int = 20260924) -> dict:
    """Synthetic OHLCV+amount panel (selftest-only; N3 _synth_panel
    convention: geometric walk, coherent bars)."""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2020-01-01", periods=n)
    out = {}
    for s in ("SYM1", "SYM2", "SYM3", "SYM4"):
        r = rng.normal(0.0003, 0.012, n)
        close = 10.0 * np.cumprod(1 + r)
        spread = np.abs(rng.normal(0.005, 0.003, n))
        open_ = close * (1 + rng.normal(0, 0.004, n))
        high = np.maximum(open_, close) * (1 + spread)
        low = np.minimum(open_, close) * (1 - spread)
        vol = rng.integers(1_000, 1_000_000, n).astype(float)
        out[s] = pd.DataFrame({"open": open_, "high": high, "low": low,
                              "close": close, "volume": vol,
                              "amount": vol * close}, index=idx)
    return out


def cmd_selftest() -> int:
    """Offline legs (zero shared writes, zero band seeds, zero panel I/O:
    synth panel only). Determinism/idempotence/coherence/truncation/
    replay smoke/freeze-gate guard/seed disjointness."""
    fails = []

    def leg(name: str, ok: bool, note: str = ""):
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" | {note}" if note else ""))
        if not ok:
            fails.append(name)

    print("PERPETUAL-N4-B1 runner selftest (offline legs; freeze-gate S8 two-state):")
    panel = _synth_panel(600, 20260924)

    # S1 resample determinism (same L+seed -> identical panel bytes)
    a = resample_history(panel, 20, 95_006)
    b = resample_history(panel, 20, 95_006)
    ok = all(a[s].equals(b[s]) for s in a)
    leg("S1 resample determinism (same L+seed -> frame-equal)", ok)

    # S2 seed sensitivity (different seed -> different history)
    c = resample_history(panel, 20, 95_007)
    ok = not a["SYM1"]["close"].equals(c["SYM1"]["close"])
    leg("S2 seed sensitivity (95_006 vs 95_007 differ)", ok)

    # S3 bar coherence (high/low envelope + positive close/volume)
    ok, who = _bar_coherence_ok(a)
    leg("S3 bar coherence (H>=max(O,C), L<=min(O,C), C>0)", ok, who)

    # S4 forward-immutability (synthetic timeline == source timeline;
    #     source was truncated at EVIDENCE_CUT by construction)
    src = {s: df[df.index <= pd.Timestamp(EVIDENCE_CUT)]
           for s, df in panel.items()}
    src_idx = next(iter(src.values())).index
    ok = (next(iter(a.values())).index.equals(panel["SYM1"].index)
          and len(src_idx) == len(panel["SYM1"].index))
    leg("S4 index preservation (synthetic keeps source DatetimeIndex)", ok)

    # S5 replay smoke on synth panel (real engine, one member, X1 bite)
    t = load_member("COMPOSITE-CE-01")
    r = replay_universe(t, a)
    ok = (isinstance(r["num_trades"], int) and r["bars"] > 0
          and _fee_x1_ok())
    leg("S5 replay smoke (engine run + metrics + X1 fee bite)", ok,
        f"trades={r['num_trades']} sharpe={r['sharpe']} bars={r['bars']}")

    # S6 double-run identity (same universe -> identical metrics)
    r2 = replay_universe(t, resample_history(panel, 20, 95_006))
    ok = (r["sharpe"] == r2["sharpe"] and r["num_trades"] == r2["num_trades"]
          and r["max_drawdown"] == r2["max_drawdown"])
    leg("S6 replay double-run identity", ok)

    # S7 six-member entry keys all resolve in SIGNAL_BUILDERS
    missing = [m for m in MEMBERS
               if load_member(m)["params"]["entry"] not in SIGNAL_BUILDERS]
    leg("S7 SIGNAL_BUILDERS coverage (six members)", not missing,
        ",".join(missing))

    # S8 freeze-gate guard (two-state, r307 law: pre-freeze the DRAFT
    # marker must hold cmd_run closed; post-freeze the pins must parse)
    if _prereg_frozen():
        try:
            ok = _frozen_L() >= 2 and _frozen_K() >= 2
            note = (f"frozen: PINNED-L={_frozen_L()} PINNED-K={_frozen_K()} "
                    "parse fail-closed; cmd_run unlocked")
        except RuntimeError as exc:
            ok = False
            note = f"pins missing: {exc}"
        leg("S8 prereg freeze-gate state (post-freeze)", ok, note)
    else:
        leg("S8 prereg freeze-gate state (pre-freeze)", True,
            "DRAFT marker present -> burn refuses (R99/R250)")

    # S9 seed-band disjointness (three bands vs SEED_REGISTRY ints; the
    # face's OWN registered base perpetual_n4_b1 == BAND_GEN[0] is the
    # R250 one-step landing, not a collision -- post-freeze it is the
    # only allowed in-band hit; pre-freeze zero hits expected)
    own = SEED_REGISTRY.get("perpetual_n4_b1")
    hit = []
    for name, (lo, hi) in (("gen", BAND_GEN), ("scrnull", BAND_SCRNULL),
                           ("unc", BAND_UNC)):
        for k, v in SEED_REGISTRY.items():
            if isinstance(v, int) and lo <= v <= hi and v != own:
                hit.append(f"{k}={v} x {name}")
    ok = (not hit) and (own is None or own == BAND_GEN[0])
    leg("S9 seed bands disjoint vs SEED_REGISTRY (own base exempt)", ok,
        "; ".join(hit[:3]) or (f"own base={own}" if own is not None
                               else "no own key yet (pre-freeze state)"))

    # S10 block-length guard (L<2 or 2L>T refuse)
    ok = False
    try:
        resample_history(panel, 1, 95_006)
    except ValueError:
        ok = True
    try:
        resample_history({s: df.iloc[:30] for s, df in panel.items()},
                         20, 95_006)
        ok = False
    except ValueError:
        pass
    leg("S10 block-length guard (L>=2, T>=2L)", ok)

    # --- SatEngine FAMILIES adapter legs (T-151 deliverable (5)) --------
    import tempfile
    tmp = tempfile.mkdtemp(prefix="_n4b1_st_")

    # S11 WAVE_CONFIGS contract (engine registry row source of truth)
    cfg = WAVE_CONFIGS.get(WAVE_NAME)
    ok = (cfg is not None and cfg["batch"] == BATCH
          and cfg["engine_owner"] == "bm-a" and cfg["nshards"] == 6
          and cfg["members"] == MEMBERS
          and cfg["shard_subdir"] == "n4_b1"
          and os.path.exists(cfg["prereg"]))
    leg("S11 WAVE_CONFIGS contract (owner/nshards/members/prereg)", ok)

    # S12 _set_wave two-state (pin ok; foreign wave = honest KeyError)
    try:
        _set_wave(WAVE_NAME)
        ok = WAVE == WAVE_NAME
        try:
            _set_wave(999)
            ok = False
        except KeyError:
            pass
    except KeyError:
        ok = False
    leg("S12 _set_wave pin + foreign-wave KeyError", ok)

    # S13 _shard_valid crafted receipts (hermetic rows via WAVE_DIR patch;
    #     zero shared-tree writes -- tmp rows file only)
    global WAVE_DIR
    real_dir = WAVE_DIR
    try:
        mid = MEMBERS[0]
        k_exp, l_exp = _frozen_K(), _frozen_L()
        WAVE_DIR = tmp
        with open(member_rows_path(mid), "w", encoding="utf-8") as fh:
            for k in range(k_exp):
                fh.write(json.dumps({"k": k, "member": mid}) + "\n")
        good = os.path.join(tmp, "shard-0-of-6.json")
        json.dump({"batch": BATCH, "shard": 0, "nshards": 6, "member": mid,
                   "k_expected": k_exp, "k_burned": k_exp, "L": l_exp,
                   "evidence_cutoff": EVIDENCE_CUT},
                  open(good, "w", encoding="utf-8"))
        ok = _shard_valid(good, 0, 6)
        # truncated k-set (K-1 rows) must fail (presence=done is earned)
        with open(member_rows_path(mid), "w", encoding="utf-8") as fh:
            for k in range(k_exp - 1):
                fh.write(json.dumps({"k": k}) + "\n")
        ok = ok and not _shard_valid(good, 0, 6)
        # wrong member / wrong batch / wrong nshards must fail
        bad = dict(json.load(open(good, encoding="utf-8")))
        bad["member"] = MEMBERS[1]
        p2 = os.path.join(tmp, "shad-0-of-6.json")
        json.dump(bad, open(p2, "w", encoding="utf-8"))
        ok = ok and not _shard_valid(p2, 0, 6)
        bad = dict(json.load(open(good, encoding="utf-8")))
        bad["batch"] = "OTHER"
        json.dump(bad, open(p2, "w", encoding="utf-8"))
        ok = ok and not _shard_valid(p2, 0, 6)
        ok = ok and not _shard_valid(good, 0, 12)
    finally:
        WAVE_DIR = real_dir
    leg("S13 _shard_valid receipts (complete k-set/wrong-face rejects)", ok)

    # S14 shard-member resolution (shard=member shim + range guards)
    try:
        ok = (shard_member(0, 6) == MEMBERS[0]
              and shard_member(5, 6) == MEMBERS[5])
        for bad_args in ((6, 6), (-1, 6), (0, 12)):
            try:
                shard_member(*bad_args)
                ok = False
            except ValueError:
                pass
    except Exception:
        ok = False
    leg("S14 shard_member resolution + range guards", ok)

    # S15 burn determinism: serial vs pool drivers produce identical
    #     rows (insertion-order result lane -> k-ascending appends in both;
    #     hermetic tmp WAVE_DIR, zero shared-tree writes)
    real_dir = WAVE_DIR
    try:
        t = load_member("COMPOSITE-CE-01")
        WAVE_DIR = os.path.join(tmp, "serial")
        _burn_rows("COMPOSITE-CE-01", t, panel, [0, 1, 2], workers=1)
        rows_a = read_rows("COMPOSITE-CE-01")
        WAVE_DIR = os.path.join(tmp, "pool")
        _burn_rows("COMPOSITE-CE-01", t, panel, [0, 1, 2], workers=2)
        rows_b = read_rows("COMPOSITE-CE-01")
        ok = (len(rows_a) == 3 and len(rows_b) == 3 and rows_a == rows_b
              and [r["k"] for r in rows_a] == [0, 1, 2])
    except Exception as exc:
        ok = False
        print(f"    (S15 fault: {exc})")
    finally:
        WAVE_DIR = real_dir
    leg("S15 serial vs pool burn determinism (rows equal, k-order)", ok)

    # S16 finalize math face (hermetic: crafted rows + synth returns;
    #     §4 wiring via science_gates verbatim, zero panel I/O)
    try:
        fake_rows = [{"sharpe": round(0.5 + 0.01 * k, 6)}
                     for k in range(200)]
        rets = [0.001 * ((k % 7) - 3) for k in range(300)]
        faces = _member_faces(fake_rows, rets, 1.234)
        ku = faces["k_universe_sharpe"]
        ci = faces["bootstrap_ci_sharpe"]
        ok = (ku["n"] == 200
              and ku["ci95_low"] <= ku["median"] <= ku["ci95_high"]
              and ku["positive_fraction"] == 1.0
              and ci["seed"] == BAND_SCRNULL[0]
              and ci["n_resamples"] == 1000 and ci["block_days"] == 10.0
              and faces["dsr_from_stats"]["n_trials"] == 200
              and "dsr" in faces["dsr_from_stats"])
    except Exception as exc:
        ok = False
        print(f"    (S16 fault: {exc})")
    leg("S16 finalize math face (distribution/CI/DSR wiring)", ok)

    n = 16 - len(fails)
    print(f"selftest: {n}/16 PASS, {len(fails)} FAIL")
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser(description="PERPETUAL-N4-B1 runner")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("probe")
    runp = sub.add_parser("run")
    runp.add_argument("--member", default=None,
                       help="manual lane: burn one member by id")
    runp.add_argument("--universes", type=int, default=None)
    runp.add_argument("--shard", type=int, default=None,
                      help="engine lane: shard i = MEMBERS[i]")
    runp.add_argument("--of", type=int, default=None)
    runp.add_argument("--wave", default=None)
    runp.add_argument("--workers", type=int, default=1)
    runp.add_argument("--lane", default="pool")
    sub.add_parser("status")
    sub.add_parser("finalize")
    sub.add_parser("selftest")
    args = ap.parse_args()
    if args.cmd == "probe":
        return cmd_probe()
    if args.cmd == "run":
        if args.shard is not None:
            if args.member is not None:
                print("REFUSED: --shard and --member are exclusive")
                return 2
            if args.wave not in (None, WAVE_NAME):
                print(f"REFUSED: unknown wave {args.wave!r} "
                      f"(this module burns {WAVE_NAME} only)")
                return 2
            nsh = args.of if args.of is not None else NSHARDS
            return cmd_run_shard(args.shard, nsh, args.workers, args.lane)
        if args.member is None:
            print("usage: run --member <ID> | run --shard i --of "
                  f"{NSHARDS} [--wave {WAVE_NAME}] [--workers P]")
            return 2
        return cmd_run(args.member, args.universes, args.workers)
    if args.cmd == "status":
        return cmd_status()
    if args.cmd == "finalize":
        return cmd_finalize()
    return cmd_selftest()


if __name__ == "__main__":
    sys.exit(main())
