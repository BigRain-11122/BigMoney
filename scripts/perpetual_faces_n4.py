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
  results/perpetual_faces/n4_b1_results.json        finalize merge (post-burn)

Usage:
  python scripts/perpetual_faces_n4.py probe              # read-only facts
  python scripts/perpetual_faces_n4.py run --member <ID>  # post-freeze only
  python scripts/perpetual_faces_n4.py status
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


def cmd_run(member_id: str, universes: int | None = None) -> int:
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
    for k in todo:
        seed = BAND_GEN[0] + k
        synth = resample_history(prices, _frozen_L(), seed)
        r = replay_universe(t, synth)
        row = {"id": f"{member_id}::u{k:03d}", "member": member_id, "k": k,
               "seed": seed, "L": _frozen_L(), "batch": BATCH,
               "evidence_cutoff": EVIDENCE_CUT,
               "sharpe": r["sharpe"], "annual_return": r["annual_return"],
               "max_drawdown": r["max_drawdown"],
               "num_trades": r["num_trades"], "bars": r["bars"]}
        _append_row(member_id, row)
        print(f"{row['id']} seed={seed} sharpe={r['sharpe']} "
              f"trades={r['num_trades']}")
    print(f"{member_id}: burn complete {len(todo)} rows "
          f"(total {len(done) + len(todo)}/{k_max})")
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

    n = 10 - len(fails)
    print(f"selftest: {n}/10 PASS, {len(fails)} FAIL")
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser(description="PERPETUAL-N4-B1 runner")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("probe")
    runp = sub.add_parser("run")
    runp.add_argument("--member", required=True)
    runp.add_argument("--universes", type=int, default=None)
    sub.add_parser("status")
    sub.add_parser("selftest")
    args = ap.parse_args()
    if args.cmd == "probe":
        return cmd_probe()
    if args.cmd == "run":
        return cmd_run(args.member, args.universes)
    if args.cmd == "status":
        return cmd_status()
    return cmd_selftest()


if __name__ == "__main__":
    sys.exit(main())
