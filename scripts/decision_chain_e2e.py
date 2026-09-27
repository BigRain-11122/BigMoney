"""DECISION_CHAIN_E2E_P1 (T-90 · CEO order O-20260927-0758: judge market
temperature FIRST, then deploy matching strategies, THEN backtest the chain
itself). Four-arm end-to-end replay on the T-22 virtual-timepoint harness:

  A1 = full-chain confirmed-line routing (t34 CONF arm verbatim),
  A2 = chain + half-step ladder (t34 LADDER C1 arm verbatim),
  B  = best single strategy no-switch (COMPOSITE-CE-01 all-weather),
  C  = passive EW buy&hold baseline,
  D  = six-member static equal-weight, no routing.

Prereg research/DECISION_CHAIN_E2E_P1.md v1.1 (re-frozen r311, GM RULING
MSG-0814) precedes this runner (R99 law). Stage A re-derives the 6 members'
daily equity-return curves on both frozen axes at the x2 cost face ONLY
(base face = t34 checkpoint reuse, zero re-derivation); curves are
infrastructure re-derivation, NOT counted trials. Stage B (finalize)
composes the four-arm envelope x {6m,12m,24m} x faces {base,x2} and reads
the frozen judgments J-C1..C4 / J-L1..L2 / J-TARGET (two-tier disclosure),
plus the four-ring broken-chain localization when the chain loses.

Frozen reuse (prereg s6, zero rewrite): enumeration/anchor/census/envelope
primitives are IMPORTED from t22_virtual_timepoints and t34_early_signal;
the x2 cell body is t34._run_cell_curve executed under science_gates
CostPatch(2.0) (t22 Erratum-1 multiplier law -- never COST_X2_RATE).

Construction disclosures (frozen envelope formula, prereg s3):
- B/D arms hold constant corps weights -> zero envelope turnover by
  construction; the member-level daily EW re-anchor inside a corps is the
  frozen t34 construction and carries no envelope fee (D bias direction =
  optimistic for D = conservative for chain claims, disclosed).
- A1/A2 GREEN-segment attack seat = T-33 roster v1 single-seat historical
  replay + vacancy flag (attack corps live count 0, honest annotation).
- Envelope single-side rate = COST_X2_RATE/2 at base face, x COST_X2_RATE
  at x2 face (x2 survival doubles friction too; runtime-derived).

Usage:
  python scripts/decision_chain_e2e.py run --face x2 --axis legacy \
      --shard lA --pos-from 0 --pos-to 314 [--workers N] [--limit K]
  python scripts/decision_chain_e2e.py finalize
  python scripts/decision_chain_e2e.py repro        (base-face G-REPRO probe)
  python scripts/decision_chain_e2e.py status
  python scripts/decision_chain_e2e.py selftest     (hermetic, offline)
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

import t34_early_signal as t34                      # frozen pipeline parent
from t22_virtual_timepoints import (               # frozen T-22 primitives
    W6M, W12M, W24M, enumerate_starts, regime_proxy, load_done_keys,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "results", "decision_chain")
TICKET = "T-2026-09-27-90"
BATCH = "DECISION_CHAIN_E2E_P1"
PREREG_PATH = os.path.join(ROOT, "research", "DECISION_CHAIN_E2E_P1.md")
OUT_JSON = os.path.join(ROOT, "results", "decision_chain_e2e.json")
OUT_CSV = os.path.join(ROOT, "research", "shortline",
                       "decision_chain_e2e_results.csv")
DD_RED_LINE = t34.DD_RED_LINE        # -0.35 frozen (J-C4 / J-L2)
DD_TARGET_LINE = -0.10               # J-TARGET CEO line (O-0809 s2 verbatim)
BOOTSTRAP_B = t34.BOOTSTRAP_B        # 2000 frozen
BOOTSTRAP_SEED = 20261001            # SEED_REGISTRY['decision_chain_e2e']
SUBSAMPLE_STEP = 25                  # D7 25td de-overlap disclosure
FACES = ("base", "x2")
WINDOWS = {"6m": W6M, "12m": W12M, "24m": W24M}
ARMS = ("A1", "A2", "B", "D")        # C = passive baseline (not an overlay)
T22_FILE = t34.T22_FILE               # frozen start counts live-read source


def _log(msg: str) -> None:
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}", flush=True)


def _seed_check():
    from science_gates import SEED_REGISTRY
    got = SEED_REGISTRY.get("decision_chain_e2e")
    assert got == BOOTSTRAP_SEED, (
        f"seed law: SEED_REGISTRY['decision_chain_e2e']={got} != "
        f"{BOOTSTRAP_SEED} (prereg s3 order law + s9.2 zero-run amendment)")


def _ci_boot(k: int, n: int):
    """Binomial bootstrap 95% CI, fresh seeded rng per call (t22 caliber,
    seed base 20261001 per prereg s3 + s9.2 zero-run amendment)."""
    if n == 0:
        return None, None
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    draws = rng.binomial(n, k / n, BOOTSTRAP_B) / n
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return round(float(lo), 4), round(float(hi), 4)


def rate_side(face: str) -> float:
    """Envelope single-side rate, runtime-derived (prereg s3: base =
    COST_X2_RATE/2; x2 survival doubles friction -> COST_X2_RATE)."""
    from science_gates import COST_X2_RATE
    return COST_X2_RATE if face == "x2" else COST_X2_RATE / 2.0


# ------------------------------------------------------------------ stage A

def shard_path(axis: str, shard: str) -> str:
    return os.path.join(OUT_DIR, f"curves_x2_{axis}_{shard}.jsonl")


def _init_worker_x2(axis: str):
    t34._init_worker(axis)           # frozen t34 worker init (panels+signals)


def _run_cell_x2(member: str, pos: int) -> dict:
    """x2 face cell = t34 frozen cell body under CostPatch(2.0) multiplier
    (t22 Erratum-1 law). Import-face reuse: the exact t34 function object."""
    from science_gates import CostPatch
    with CostPatch(2.0):
        row = t34._run_cell_curve(member, pos)
    row["face"] = "x2"
    return row


def _anchor_gate(log=_log) -> int:
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
        log(f"anchor {t['id']}: {'PASS' if a['ok'] else 'FAIL'}")
        n_fail += 0 if a["ok"] else 1
    return n_fail


def _axis_eligible(axis: str, expected: dict, log=_log):
    """Panel + census gate (r105 drift law): re-enumeration must equal the
    t22 finalize record read live (hand-copy prohibited)."""
    P = t34._axis_panel(axis)
    close = P["close"]
    listed = close.notna().sum(axis=1)
    eligible = enumerate_starts(len(close.index), listed)
    if len(eligible) != expected[axis]:
        log(f"G-CENSUS FAIL [{axis}]: {len(eligible)} != {expected[axis]} "
            f"(t22 frozen) -- batch void")
        return None, None
    return close, eligible


def cmd_run(args) -> int:
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUT_DIR, "logs"), exist_ok=True)
    log_path = os.path.join(OUT_DIR, "logs",
                            f"run_x2_{args.axis}_{args.shard}.log")
    if os.environ.get("DC_E2E_DETACHED") == "1":
        sys.stdout = open(log_path, "a", buffering=1, encoding="utf-8")
        sys.stderr = sys.stdout
    t0 = time.time()
    _seed_check()
    if args.face != "x2":
        _log("run mode is the x2 re-derivation leg only (base face = t34 "
             "checkpoint reuse, zero re-derivation per prereg s0)")
        return 2
    if _anchor_gate():
        _log("G-ANCHOR FAIL -- batch void")
        return 3
    expected = t34._expected_starts()
    close, eligible = _axis_eligible(args.axis, expected)
    if eligible is None:
        return 3
    shard = eligible[args.pos_from:args.pos_to]
    if args.limit:
        shard = shard[:args.limit]
    if not shard:
        _log("nothing to do (empty shard range)")
        return 0
    members = t34.ATTACK + t34.CHOP
    path = shard_path(args.axis, args.shard)
    done = load_done_keys(path)
    jobs = [(m, p) for p in shard for m in members
            if f"{m}|{p}" not in done]
    _log(f"[{args.axis}/{args.shard}] census PASS {len(eligible)} starts; "
         f"shard={len(shard)} cells todo={len(jobs)} resume-skipped="
         f"{len(shard) * len(members) - len(jobs)}")
    if not jobs:
        _log("all cells already checkpointed -- no-op")
        return 0
    import psutil
    cores = psutil.cpu_count(logical=True)
    free_gb = psutil.virtual_memory().available / 1e9
    ram_guard = max(4, min(14, int(free_gb // 1.2)))   # t34 worker budget
    workers = args.workers or min(cores - 2, ram_guard)  # O-2130 formula
    _log(f"workers_plan={workers} (min(cores-2={cores - 2}, "
         f"ram_guard={ram_guard})) free_ram={free_gb:.1f}GB")
    from concurrent.futures import ProcessPoolExecutor, as_completed
    n_done, t_last = 0, time.time()
    with open(path, "a", encoding="utf-8") as fh:
        with ProcessPoolExecutor(max_workers=workers,
                                 initializer=_init_worker_x2,
                                 initargs=(args.axis,)) as pool:
            futs = {pool.submit(_run_cell_x2, m, p): (m, p)
                    for m, p in jobs}
            for fut in as_completed(futs):
                row = fut.result()
                fh.write(json.dumps(row, default=bool) + "\n")
                fh.flush()
                n_done += 1
                if time.time() - t_last > 30:
                    _log(f"progress {n_done}/{len(jobs)}")
                    t_last = time.time()
    marker = {"shard": args.shard, "axis": args.axis, "face": "x2",
              "cells_written": n_done, "cells_total": len(jobs),
              "n_eligible": len(eligible), "workers": workers,
              "runtime_sec": round(time.time() - t0, 1),
              "finished_at": time.strftime("%Y-%m-%d %H:%M:%S"),
              "ticket": TICKET}
    with open(os.path.join(OUT_DIR,
                           f"done_x2_{args.axis}_{args.shard}.json"),
              "w", encoding="utf-8") as fh:
        json.dump(marker, fh, indent=2)
    _log(f"DONE {n_done}/{len(jobs)} cells in "
         f"{round(time.time() - t0, 1)}s workers={workers}")
    return 0


# ------------------------------------------------------------- curve loading

def _load_x2_curves(axis: str):
    """Union over all shard files (t22 finalize canon pattern); corrupt
    mid-file = integrity abort; duplicate keys reported."""
    rows, dup = {}, []
    if not os.path.isdir(OUT_DIR):
        return rows, dup
    for name in sorted(os.listdir(OUT_DIR)):
        if not (name.startswith(f"curves_x2_{axis}_")
                and name.endswith(".jsonl")):
            continue
        fpath = os.path.join(OUT_DIR, name)
        lines = open(fpath, encoding="utf-8").read().splitlines()
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                if i == len(lines) - 1:
                    continue        # crash-truncated tail: skip honestly
                raise
            if r["key"] in rows:
                dup.append(r["key"])
                continue
            rows[r["key"]] = r
    return rows, dup


def _face_curves(axis: str, face: str):
    if face == "base":
        return t34._load_curves(axis), []     # frozen t34 checkpoint
    return _load_x2_curves(axis)


# ------------------------------------------------------------------ overlay

def _arm_cells(W, att, chop, close, eligible, curves, rate, axis_reg):
    """Per-startpoint envelope metrics for one arm (weights matrix W).
    Windows {6m,12m,24m} sliced off the same envelope path (P-5 law);
    12m passive = curve row p_ret_12m (t34 verbatim), 6m/24m = t34
    _passive_window caliber."""
    idx = close.index
    cells = {}
    for p in eligible:
        n = min(W24M, len(idx) - p)
        Wp = W[p:p + n]
        r = t34.env_daily(att[p], chop[p], Wp, rate)
        row = curves[f"{t34.ATTACK[0]}|{p}"]
        m6 = t34._win_metrics(r, W6M, t34._passive_window(close, p, W6M))
        m12 = t34._win_metrics(r, W12M, row["p_ret_12m"])
        m24 = t34._win_metrics(r, W24M, t34._passive_window(close, p, W24M))
        sw = int((np.abs(np.diff(Wp, axis=0, prepend=Wp[:1])).sum(axis=1)
                  > 0).sum())
        sdate = idx[p]
        cells[p] = {"pos": p, "start": str(sdate.date()),
                    "regime": str(axis_reg.loc[sdate]),
                    "n_bars": int(len(r)),
                    "partial_12m": m12["n_bars"] < W12M,
                    "partial_24m": m24["n_bars"] < W24M,
                    "ret_6m": m6["ret"], "ret_12m": m12["ret"],
                    "ret_24m": m24["ret"],
                    "dd_6m": m6["dd"], "dd_12m": m12["dd"],
                    "dd_24m": m24["dd"],
                    "beat_6m": m6["beat"], "beat_12m": m12["beat"],
                    "beat_24m": m24["beat"], "switches": sw,
                    "p_ret_12m": row["p_ret_12m"]}
    return cells


def _agg_arm(cells, wname):
    """One arm aggregate on the COMPLETE-window subset (prereg s3); D7 four
    fields + 25td subsample + per-segment buckets (t22 caliber)."""
    pflag = {"6m": None, "12m": "partial_12m", "24m": "partial_24m"}[wname]
    full = [c for c in cells.values() if pflag is None or not c[pflag]]
    n = len(full)
    k = sum(1 for c in full if c[f"beat_{wname}"])
    dds = [c[f"dd_{wname}"] for c in full]
    sws = [c["switches"] for c in full]
    rate = k / n if n else None
    lo, hi = _ci_boot(k, n)
    seg = {}
    for c in full:
        b = seg.setdefault(c["regime"], {"n": 0, "k": 0, "dds": []})
        b["n"] += 1
        b["k"] += int(bool(c[f"beat_{wname}"]))
        b["dds"].append(c[f"dd_{wname}"])
    starts = sorted(c["start"] for c in full)
    n_reg, last = 0, None
    for c in sorted(full, key=lambda c: c["pos"]):
        if c["regime"] != last:
            n_reg += 1
            last = c["regime"]
    sub = [c for c in full if c["pos"] % SUBSAMPLE_STEP == 0]
    all_k = sum(1 for c in cells.values() if c[f"beat_{wname}"])
    return {"n": n, "beats": k,
            "beat_rate": round(rate, 4) if rate is not None else None,
            "ci95": [lo, hi], "ci95_width":
            None if lo is None else round(hi - lo, 4),
            "min_dd": round(min(dds), 4) if dds else None,
            "mean_dd": round(sum(dds) / len(dds), 4) if dds else None,
            "oos_trades": int(sum(sws)),
            "switches_mean": round(sum(sws) / len(sws), 2) if sws else None,
            "covered_years": (round((pd.Timestamp(starts[-1])
                                     - pd.Timestamp(starts[0])).days
                                    / 365.25, 2) if starts else None),
            "independent_regime_windows": n_reg,
            "partial_n": len(cells) - n,
            "all_windows": {"n": len(cells),
                            "beat_rate": round(all_k / len(cells), 4)
                            if cells else None},
            "subsample_25td": (round(sum(1 for c in sub
                                          if c[f"beat_{wname}"]) / len(sub),
                                     4) if sub else None),
            "segments": {s: {"n": b["n"],
                             "beat_rate": round(b["k"] / b["n"], 4),
                             "min_dd": round(min(b["dds"]), 4)}
                         for s, b in sorted(seg.items())}}


def _pairwise(cells_a, cells_b, wname):
    """Arm-vs-arm pairwise window win rate + CI (J-C1..C3 caliber)."""
    pflag = {"6m": None, "12m": "partial_12m", "24m": "partial_24m"}[wname]
    full = [p for p, c in cells_a.items() if pflag is None or not c[pflag]]
    k = sum(1 for p in full
            if cells_a[p][f"ret_{wname}"] > cells_b[p][f"ret_{wname}"])
    n = len(full)
    lo, hi = _ci_boot(k, n)
    return {"n": n, "wins": k,
            "rate": round(k / n, 4) if n else None,
            "ci95": [lo, hi]}


def _overlay_axis_face(axis, face, close, eligible, dep_exec, fast_exec,
                       log=_log):
    """Four-arm overlay on one (axis, face). Weights depend on state series
    only (built once per axis upstream)."""
    curves, dup = _face_curves(axis, face)
    if dup:
        log(f"[{axis}/{face}] {len(dup)} duplicate x2 curve keys -- "
            f"integrity abort (e.g. {dup[:3]})")
        return None
    need = {f"{m}|{p}" for p in eligible for m in t34.ATTACK + t34.CHOP}
    missing = sorted(need - set(curves))
    if missing:
        log(f"[{axis}/{face}] coverage FAIL: {len(missing)} cells missing "
            f"(e.g. {missing[:3]}) -- run stage A x2 first")
        return None
    rate = rate_side(face)
    att = {p: np.asarray(curves[f"{t34.ATTACK[0]}|{p}"]["curve"], dtype=float)
           for p in eligible}
    chop = {p: np.mean([np.asarray(curves[f"{m}|{p}"]["curve"], dtype=float)
                        for m in t34.CHOP], axis=0) for p in eligible}
    W = {
        "A1": t34.conf_weights(dep_exec),
        "A2": t34.weights_matrix(dep_exec, fast_exec, t34.HALF),
    }
    n = len(dep_exec)
    W["B"] = np.tile([1.0, 0.0, 0.0], (n, 1))
    W["D"] = np.tile([1.0 / 6.0, 5.0 / 6.0, 0.0], (n, 1))
    axis_reg = regime_proxy(close["510300"])
    cells = {arm: _arm_cells(W[arm], att, chop, close, eligible, curves,
                            rate, axis_reg) for arm in ARMS}
    # friction counterfactual A1' (rate=0) for ring-3
    a1_prime = _arm_cells(W["A1"], att, chop, close, eligible, curves,
                          0.0, axis_reg)
    return {"cells": cells, "a1_prime": a1_prime, "rate_side": rate}


# ------------------------------------------------------------------- gates

def _leg2_verdict(replay_last_day, replay_state, rs_asof, rs_state):
    """Amended G-V3 leg-2 decision core (prereg s9.3): freshness (the v1
    LIVE defense-line face must cover the replay's last bench date) +
    4-state alphabet on both faces. Equality between the two faces is
    NEVER asserted -- they are different regime versions by law (v1 live
    probe keeps #10 below_ma200 collected until amendment; v3 calibration
    layer de-collected it per the v2 ruling)."""
    alphabet = ("GREEN", "YELLOW", "ORANGE", "RED")
    fresh = bool(rs_asof == str(replay_last_day))
    alpha = bool(replay_state in alphabet and rs_state in alphabet)
    return {"ok": bool(fresh and alpha), "fresh": fresh, "alphabet_ok": alpha,
            "replay_last_day": str(replay_last_day),
            "replay_state": replay_state, "v1_live_asof": rs_asof,
            "v1_live_state": rs_state,
            "divergence_note": ("v1 live probe vs v3 calibration-layer "
                                "replay are different regime versions by "
                                "law (s9.3); both readings disclosed, "
                                "equality never asserted")}


def _gate_v3_leg2():
    """G-V3 leg-2 (prereg s2, amended s9.3): the v1 LIVE defense-line face
    and the v3 calibration-layer replay are DIFFERENT regime versions --
    v1.1's equality assertion was a false premise (r312 live evidence:
    probe triggers carry 'hs300<MA200 (#10 collected)' = v1 matrix).
    Amended: freshness + alphabet + both readings disclosed."""
    from live.paper import v3_state_series
    rs = json.load(open(os.path.join(ROOT, "results", "regime_state.json"),
                        encoding="utf-8-sig"))
    st = v3_state_series()
    if len(st) == 0:
        return {"ok": False, "error": "empty v3 replay series"}
    return _leg2_verdict(str(st.index[-1].date()), str(st.iloc[-1]),
                          str(rs.get("asof")), str(rs.get("state")))


def _repro_compare(mine, ref):
    """Bit-level A1/A2 base-face comparators vs t34 verdict live values."""
    checks = {}
    for axis in ("legacy", "deep"):
        v = ref["axes"][axis]
        for arm, key in (("A1", "conf"), ("A2", "ladder_C1")):
            m = mine[axis]["base"]["12m"][arm]
            checks[f"{axis}.{arm}.beat_rate_12m"] = (
                m["beat_rate"] == v[key]["beat_rate_12m"])
            checks[f"{axis}.{arm}.min_dd_12m"] = (
                m["min_dd"] == v[key]["min_dd_12m"])
            checks[f"{axis}.{arm}.switches_mean"] = (
                m["switches_mean"] == v[key]["switches_mean"])
    return checks


# ---------------------------------------------------------------- judgment

def _arm_corr(pack, eligible):
    """Arm-pairwise correlation on window-level returns (6m/12m/24m), all
    startpoints (overlapping windows inflate n mechanically; disclosure
    column only, never a gate)."""
    out = {}
    for wname in WINDOWS:
        for i, a in enumerate(ARMS):
            for b in ARMS[i + 1:]:
                va = np.array([pack["cells"][a][p][f"ret_{wname}"]
                               for p in eligible], dtype=float)
                vb = np.array([pack["cells"][b][p][f"ret_{wname}"]
                               for p in eligible], dtype=float)
                if va.std() > 0 and vb.std() > 0:
                    c = round(float(np.corrcoef(va, vb)[0, 1]), 4)
                else:
                    c = None
                out[f"{a}-{b}_{wname}"] = c
    return out


def _judge_axis(packs, face):
    """Full judgment pack for one (axis, face): per-window arm tables +
    pairwise win rates + J-C (12m primary window) + J-TARGET cells."""
    cells = packs[face]["cells"]
    tables = {w: {arm: _agg_arm(cells[arm], w) for arm in ARMS}
              for w in WINDOWS}
    pairwise = {}
    for w in WINDOWS:
        pairwise[w] = {
            "A1_vs_B": _pairwise(cells["A1"], cells["B"], w),
            "A1_vs_D": _pairwise(cells["A1"], cells["D"], w),
            "A1_vs_C": {"n": tables[w]["A1"]["n"],
                        "wins": tables[w]["A1"]["beats"],
                        "rate": tables[w]["A1"]["beat_rate"],
                        "ci95": tables[w]["A1"]["ci95"]},
        }
    pw12 = pairwise["12m"]

    def _lo(d):
        return d["ci95"][0]

    jc = {
        "J_C1_chain_vs_best_single": bool(
            _lo(pw12["A1_vs_B"]) is not None and _lo(pw12["A1_vs_B"]) > 0.50),
        "J_C2_chain_vs_static_ew": bool(
            _lo(pw12["A1_vs_D"]) is not None and _lo(pw12["A1_vs_D"]) > 0.50),
        "J_C3_chain_vs_passive": bool(
            _lo(pw12["A1_vs_C"]) is not None and _lo(pw12["A1_vs_C"]) > 0.50),
        "J_C4_dd_redline": bool(all(
            tables["12m"][arm]["min_dd"] is not None
            and tables["12m"][arm]["min_dd"] >= DD_RED_LINE
            for arm in ARMS)),
    }
    jc["chain_win"] = bool(jc["J_C1_chain_vs_best_single"]
                           and jc["J_C2_chain_vs_static_ew"]
                           and jc["J_C3_chain_vs_passive"]
                           and jc["J_C4_dd_redline"])
    j_target = {}
    for w in WINDOWS:
        a1, b_ = tables[w]["A1"], tables[w]["B"]
        beat_gt = bool(a1["beat_rate"] is not None and b_["beat_rate"]
                       is not None and a1["beat_rate"] > b_["beat_rate"])
        dd_ok = bool(a1["min_dd"] is not None
                     and a1["min_dd"] >= DD_TARGET_LINE)
        j_target[w] = {"a1_beat_rate": a1["beat_rate"],
                       "b_beat_rate": b_["beat_rate"],
                       "a1_min_dd": a1["min_dd"],
                       "beat_gt_b": beat_gt, "dd_ok": dd_ok,
                       "pass": bool(beat_gt and dd_ok)}
    return {"tables": tables, "pairwise": pairwise, "j_c": jc,
            "j_target": j_target}


def _broken_rings(pack, proxy_map, dep_state, close, eligible):
    """Four-ring localization (prereg s4; legacy axis, 12m face)."""
    cells_a1 = pack["cells"]["A1"]
    cells_b = pack["cells"]["B"]
    cells_d = pack["cells"]["D"]
    a1p = pack["a1_prime"]
    valid = proxy_map.notna()
    dis = (dep_state != proxy_map) & valid
    dis_days = int(dis.sum())
    dis_rate = round(float(dis[valid].mean()), 4) if int(valid.sum()) else None
    dis_starts = [c for c in cells_a1.values()
                  if dis.loc[pd.Timestamp(c["start"])]]
    agr_starts = [c for c in cells_a1.values()
                  if not dis.loc[pd.Timestamp(c["start"])]]
    seg_diff = {}
    for c in cells_a1.values():
        s = c["regime"]
        b = seg_diff.setdefault(s, {"n": 0, "a1d": 0.0})
        b["n"] += 1
        b["a1d"] += c["ret_12m"] - cells_d[c["pos"]]["ret_12m"]
    fr = [cells_a1[c]["ret_12m"] - a1p[c]["ret_12m"]
          for c in cells_a1 if not cells_a1[c]["partial_12m"]]
    gross = [abs(a1p[c]["ret_12m"]) for c in cells_a1
             if not cells_a1[c]["partial_12m"]]
    att_days = int((dep_state == "attack").sum())
    att_share = round(att_days / len(dep_state), 4)
    att_w = [c for c in cells_a1.values()
             if dep_state.loc[pd.Timestamp(c["start"])] == "attack"]
    oth_w = [c for c in cells_a1.values()
             if dep_state.loc[pd.Timestamp(c["start"])] != "attack"]

    def _m(rows, other):
        if not rows:
            return None
        vals = [c["ret_12m"] - other[c["pos"]]["ret_12m"] for c in rows]
        return round(sum(vals) / len(vals), 4)

    return {
        "ring1_temperature": {
            "day_disagreement_rate": dis_rate, "disagreement_days": dis_days,
            "a1_mean_ret_12m_disagreement_starts":
                round(sum(c["ret_12m"] for c in dis_starts) / len(dis_starts),
                      4) if dis_starts else None,
            "a1_mean_ret_12m_agreement_starts":
                round(sum(c["ret_12m"] for c in agr_starts) / len(agr_starts),
                      4) if agr_starts else None},
        "ring2_routing": {s: {"n": b["n"],
                              "mean_a1_minus_d_12m": round(b["a1d"] / b["n"],
                                                            4)}
                          for s, b in sorted(seg_diff.items())},
        "ring3_friction": {
            "switches_mean": round(
                sum(c["switches"] for c in cells_a1.values())
                / len(cells_a1), 2),
            "mean_friction_pp_12m": round(sum(fr) / len(fr), 4)
            if fr else None,
            "friction_share_of_gross": (round(sum(fr) / sum(gross), 4)
                                        if gross and sum(gross) > 0
                                        else None),
            "counterfactual": "A1' = same weights, rate=0 (zero rebalance "
                              "fee)"},
        "ring4_seat": {
            "attack_day_share": att_share, "attack_days": att_days,
            "green_start_a1_minus_b_12m": _m(att_w, cells_b),
            "other_start_a1_minus_b_12m": _m(oth_w, cells_b),
            "vacancy_note": ("attack corps live count 0; GREEN seat = T-33 "
                             "roster v1 single-seat historical replay "
                             "(prereg s3 vacancy annotation)")},
    }


# ----------------------------------------------------------------- finalize

def _payload_skeleton():
    """Construction key set (B7b contract: consumer keys subset assert)."""
    return {"batch": None, "ticket": None, "prereg": None,
            "prereg_sha256": None, "evidence_cutoff": None,
            "cutoff_meta": None, "faces": None, "windows": None,
            "bootstrap": None, "rate_side": None, "gates": None,
            "axes": None, "pairwise": None, "verdict": None,
            "ring_table": None, "corr": None, "seat_vacancy": None,
            "trials_ledger": None, "audit": None,
            "finalize_runtime_sec": None}


CONSUMER_KEYS = ("batch", "ticket", "prereg_sha256", "evidence_cutoff",
                 "cutoff_meta", "gates", "axes", "pairwise", "verdict",
                 "ring_table", "corr", "trials_ledger", "audit")


def cmd_finalize(_) -> int:
    if os.path.exists(OUT_JSON) and \
            os.environ.get("DECISION_CHAIN_E2E_REFINALIZE") != "1":
        _log(f"finalize already landed ({OUT_JSON}); "
             f"DECISION_CHAIN_E2E_REFINALIZE=1 = only redo path")
        return 0
    t0 = time.time()
    _seed_check()
    _log("=== DECISION_CHAIN_E2E finalize: gates -> overlay -> verdict ===")
    from science_gates import append_ledger, cutoff_meta

    # ---- gates
    v3g = t34._gate_v3()
    _log(f"G-V3 leg1 {'PASS' if v3g['ok'] else 'FAIL'} {v3g['got']}")
    if not v3g["ok"]:
        return 2
    v3l2 = _gate_v3_leg2()
    _log(f"G-V3 leg2 {'PASS' if v3l2.get('ok') else 'FAIL'} {v3l2}")
    if not v3l2.get("ok"):
        return 2
    n_anchor_fail = _anchor_gate()
    if n_anchor_fail:
        _log(f"G-ANCHOR FAIL x{n_anchor_fail} -- batch void")
        return 2
    anchor_gate_note = "6/6 PASS (re-run at finalize)"
    expected = t34._expected_starts()
    man = json.load(open(os.path.join(ROOT, "results", "shortline",
                                      "t18_deep_manifest.json"),
                         encoding="utf-8-sig"))
    g_manifest = {"ok": bool(man.get("verdict") == "PASS"
                             and len(man.get("members", {})) == 48)}
    if not g_manifest["ok"]:
        _log(f"G-MANIFEST FAIL {g_manifest}")
        return 2

    # audit block (prereg s0: no CLEAN audit -> not ledgered)
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

    t34_verdict = json.load(open(os.path.join(
        ROOT, "results", "t34_early_signal_verdict.json"),
        encoding="utf-8-sig"))

    # ---- overlay both axes x both faces (packs kept for ring/corr math)
    panels, packs_all, judge_all, dep_states = {}, {}, {}, {}
    for axis in ("legacy", "deep"):
        close, eligible = _axis_eligible(axis, expected)
        if eligible is None:
            return 2
        panels[axis] = (close, eligible)
        dep_state = t34.deploy_series(axis, close)
        dep_states[axis] = dep_state
        dep_exec = t34.exec_shift(dep_state)
        fast_exec = t34.exec_shift(t34.ladder_state(close["510300"]))
        packs = {}
        for face in FACES:
            pack = _overlay_axis_face(axis, face, close, eligible,
                                      dep_exec, fast_exec)
            if pack is None:
                return 2
            packs[face] = pack
        packs_all[axis] = packs
        judge_all[axis] = {face: _judge_axis(packs, face)
                           for face in FACES}
        _log(f"[{axis}] overlay done both faces "
             f"({round(time.time() - t0, 1)}s cumulative)")

    # ---- G-REPRO (base face, bit-level vs t34 verdict live values)
    repro_mine = {axis: {"base": {"12m": {
        arm: judge_all[axis]["base"]["tables"]["12m"][arm]
        for arm in ("A1", "A2")}}} for axis in ("legacy", "deep")}
    repro_checks = _repro_compare(repro_mine, t34_verdict)
    repro_ok = all(repro_checks.values())
    _log(f"G-REPRO {'PASS' if repro_ok else 'FAIL'} {repro_checks}")
    if not repro_ok:
        return 2

    # ---- verdicts (J-C legacy 12m per face; J-L; J-TARGET per axis x w x f)
    jc_faces = {face: judge_all["legacy"][face]["j_c"] for face in FACES}
    chain_win = bool(all(jc_faces[f]["chain_win"] for f in FACES))
    jl = {}
    for face in FACES:
        up = {}
        for axis in ("legacy", "deep"):
            t12 = judge_all[axis][face]["tables"]["12m"]
            ra, rb = t12["A2"]["beat_rate"], t12["A1"]["beat_rate"]
            up[axis] = (ra - rb) if (ra is not None and rb is not None) \
                else None
        dd_ok = bool(all(
            judge_all[axis][face]["tables"]["12m"]["A2"]["min_dd"] is not None
            and judge_all[axis][face]["tables"]["12m"]["A2"]["min_dd"]
            >= DD_RED_LINE for axis in ("legacy", "deep")))
        jl[face] = {"uplift_legacy_12m": up["legacy"],
                    "uplift_deep_12m": up["deep"],
                    "J_L1_uplift_positive_both_axes": bool(
                        up["legacy"] is not None and up["deep"] is not None
                        and up["legacy"] > 0 and up["deep"] > 0),
                    "J_L2_dd_ok": dd_ok}
        jl[face]["pass"] = bool(jl[face]["J_L1_uplift_positive_both_axes"]
                                and jl[face]["J_L2_dd_ok"])
    ladder_pass = bool(all(jl[f]["pass"] for f in FACES))
    j_target = {axis: {face: judge_all[axis][face]["j_target"]
                       for face in FACES}
                for axis in ("legacy", "deep")}
    j_target_pass = bool(all(
        j_target[axis][face][w]["pass"]
        for axis in ("legacy", "deep") for face in FACES for w in WINDOWS))

    # ---- broken-ring localization + corr (legacy axis, per face)
    close_l, eligible_l = panels["legacy"]
    dep_state_l = dep_states["legacy"]
    prox_map = regime_proxy(close_l["510300"]).map(
        {"bull": "attack", "chop": "chop", "bear": "cash", "na": None})
    ring_table, corr_out = {}, {}
    for face in FACES:
        ring_table[face] = _broken_rings(packs_all["legacy"][face],
                                         prox_map, dep_state_l, close_l,
                                         eligible_l)
        corr_out[face] = _arm_corr(packs_all["legacy"][face], eligible_l)

    # ---- ledger (s9(a): 6 arm-faces x n_starts; A1/A2 base = t34-counted
    # re-derivation not re-counted; curves never re-counted)
    n_starts_total = sum(len(panels[a][1]) for a in panels)
    batch_trials = 6 * n_starts_total
    if audit_clean:
        ledger = append_ledger(
            BATCH, batch_trials, file_name="decision_chain_e2e.json",
            evidence_cutoff=t34.BINDING_CUTOFF,
            note=(f"four-arm envelope cells (A1-x2 + A2-x2 + "
                  f"B-{{base,x2}} + D-{{base,x2}}) x {n_starts_total} "
                  f"starts; A1/A2 base face = T-34-counted 5,522 cells "
                  f"re-derivation not re-counted; member curves = "
                  f"infrastructure re-derivation (T-22 lineage, zero "
                  f"re-count); x2 member curves re-derived per t22/t34 "
                  f"primitives under CostPatch(2)"))
    else:
        ledger = {"prev_total": None, "batch_trials": batch_trials,
                  "total": None,
                  "note": "audit not CLEAN - not counted per prereg s0"}

    axes_out = {axis: {
        "n_starts": len(panels[axis][1]),
        "confirmed_line": ("REGIME_GUARD v3 import-replay"
                           if axis == "legacy" else
                           "T-22 3-way proxy (disclosed, non-v3)"),
        "judge": judge_all[axis],
        "rate_side": {f: packs_all[axis][f]["rate_side"]
                      for f in FACES}} for axis in ("legacy", "deep")}

    with open(PREREG_PATH, "rb") as f:
        prereg_sha = hashlib.sha256(f.read()).hexdigest()
    payload = _payload_skeleton()
    payload.update({
        "batch": BATCH, "ticket": TICKET,
        "prereg": "research/DECISION_CHAIN_E2E_P1.md",
        "prereg_sha256": prereg_sha,
        "evidence_cutoff": t34.BINDING_CUTOFF,
        "cutoff_meta": cutoff_meta(t34.BINDING_CUTOFF),
        "faces": list(FACES), "windows": WINDOWS,
        "bootstrap": {"B": BOOTSTRAP_B, "seed": BOOTSTRAP_SEED,
                      "method": "binomial percentile 95% CI",
                      "seed_note": ("prereg s3 named 20260929 (taken by "
                                    "t11_negday_ic, registered 09-24); "
                                    "zero-run amendment s9.2 -> 20261001 "
                                    "next clean date-style one-step, rg "
                                    "verified free")},
        "rate_side": {"base": rate_side("base"), "x2": rate_side("x2"),
                      "derivation": ("science_gates.COST_X2_RATE/2 at "
                                     "base; x COST_X2_RATE at x2 (survival "
                                     "doubling), runtime-derived")},
        "gates": {"G_V3_leg1": v3g, "G_V3_leg2": v3l2,
                  "G_CENSUS_expected": expected,
                  "G_ANCHOR": anchor_gate_note,
                  "G_MANIFEST": g_manifest,
                  "G_REPRO": {"ok": repro_ok, "checks": repro_checks},
                  "x2_coverage": "complete both axes (overlay coverage "
                                 "gate passed)"},
        "axes": axes_out,
        "pairwise": {axis: {face: judge_all[axis][face]["pairwise"]
                            for face in FACES}
                     for axis in ("legacy", "deep")},
        "verdict": {"j_c_faces": jc_faces, "chain_win": chain_win,
                    "j_l": jl, "ladder_pass": ladder_pass,
                    "j_target": j_target, "j_target_pass": j_target_pass,
                    "two_tier_note": ("J-C series = per-run scientific "
                                      "readings; J-TARGET = CEO frozen "
                                      "iteration line (O-0809 s2); two "
                                      "tiers disclosed separately, never "
                                      "merged"),
                    "disposition": (
                        "chain WINS the machine test (J-C conjunction on "
                        "legacy 12m, both faces)" if chain_win else
                        "chain does NOT win -- honest report + four-ring "
                        "localization (prereg s4); J-C1 pass with J-C2 "
                        "fail = no routing value (member-book effect), "
                        "read separately")},
        "ring_table": ring_table,
        "corr": corr_out,
        "seat_vacancy": {"attack_corps_live_count": 0,
                         "note": ("GREEN face = half-ladder/confirmed "
                                  "single-seat historical replay per "
                                  "T-33 roster v1; full-chain rerun queued "
                                  "when attack corps seats fill (ticket "
                                  "honest boundary)")},
        "trials_ledger": ledger,
        "audit": audit,
        "finalize_runtime_sec": round(time.time() - t0, 1),
    })
    json.dumps(payload, default=bool)          # parse-validate pre-write
    assert all(k in payload for k in CONSUMER_KEYS), (
        "B7b contract: consumer keys must be subset of construction keys")
    tmp = OUT_JSON + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, indent=1, ensure_ascii=False, default=bool)
    os.replace(tmp, OUT_JSON)
    _log(f"verdict chain_win={chain_win} j_target_pass={j_target_pass} "
         f"-> {OUT_JSON}")

    # aggregated CSV (small, git)
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    n_csv = 0
    with open(OUT_CSV, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("axis,face,window,arm,n,beat_rate,ci95_lo,ci95_hi,min_dd,"
                "mean_dd,switches_mean,oos_trades,covered_years,"
                "indep_regime_windows,ci95_width,subsample_25td\n")
        for axis in ("legacy", "deep"):
            for face in FACES:
                for wname in WINDOWS:
                    for arm in ARMS:
                        a = judge_all[axis][face]["tables"][wname][arm]
                        fh.write(",".join(str(x) for x in (
                            axis, face, wname, arm, a["n"], a["beat_rate"],
                            a["ci95"][0], a["ci95"][1], a["min_dd"],
                            a["mean_dd"], a["switches_mean"], a["oos_trades"],
                            a["covered_years"],
                            a["independent_regime_windows"], a["ci95_width"],
                            a["subsample_25td"])) + "\n")
                        n_csv += 1
    _log(f"csv -> {OUT_CSV} ({n_csv} rows)")

    # attrition row (s7-T)
    attr = os.path.join(ROOT, "results", "gate_attrition.json")
    d = json.load(open(attr, encoding="utf-8-sig"))
    d["entries"].append({
        "batch": BATCH, "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "kind": "measurement", "retro_fill": False,
        "cells_ledger_delta": batch_trials if audit_clean else 0,
        "ledger_total_after": (ledger or {}).get("total"),
        "gates": {"g_repro_ok": repro_ok, "g_v3": v3g["ok"],
                  "chain_win": chain_win, "j_target_pass": j_target_pass,
                  "void": False},
        "eliminated": None,
        "refs": {"results": "results/decision_chain_e2e.json",
                 "prereg": "research/DECISION_CHAIN_E2E_P1.md",
                 "csv": "research/shortline/decision_chain_e2e_results.csv",
                 "ticket": f"fleet/tasks/{TICKET}-P1.json"},
        "note": "four-arm chain E2E envelope cells; curves/anchors = "
                "T-22/T-34 lineage re-derivation, not re-counted"})
    json.dumps(d)
    with open(attr, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    _log(f"finalize DONE in {round(time.time() - t0, 1)}s")
    return 0


# -------------------------------------------------------------------- repro

def cmd_repro(_) -> int:
    """Base-face G-REPRO dry probe: census + G-V3(leg1+leg2) + A1/A2 12m
    aggregates bit-level vs the t34 verdict. No ledger, no verdict write."""
    t0 = time.time()
    _seed_check()
    v3g = t34._gate_v3()
    print(f"G-V3 leg1 {'PASS' if v3g['ok'] else 'FAIL'} {v3g['got']}")
    v3l2 = _gate_v3_leg2()
    print(f"G-V3 leg2 {'PASS' if v3l2.get('ok') else 'FAIL'} {v3l2}")
    if not (v3g["ok"] and v3l2.get("ok")):
        return 2
    expected = t34._expected_starts()
    t34_verdict = json.load(open(os.path.join(
        ROOT, "results", "t34_early_signal_verdict.json"),
        encoding="utf-8-sig"))
    repro_mine = {}
    for axis in ("legacy", "deep"):
        close, eligible = _axis_eligible(axis, expected)
        if eligible is None:
            return 2
        dep_exec = t34.exec_shift(t34.deploy_series(axis, close))
        fast_exec = t34.exec_shift(t34.ladder_state(close["510300"]))
        pack = _overlay_axis_face(axis, "base", close, eligible,
                                  dep_exec, fast_exec)
        if pack is None:
            return 2
        repro_mine[axis] = {"base": {"12m": {
            arm: _agg_arm(pack["cells"][arm], "12m")
            for arm in ("A1", "A2")}}}
    checks = _repro_compare(repro_mine, t34_verdict)
    ok = all(checks.values())
    for k, v in checks.items():
        print(f"  {'=' if v else 'X'} {k}")
    print(f"G-REPRO {'PASS' if ok else 'FAIL'} "
          f"({round(time.time() - t0, 1)}s) -- pipeline "
          f"{'intact' if ok else 'DRIFT (VOID risk)'}")
    return 0 if ok else 2


# ------------------------------------------------------------------- status

def cmd_status(_) -> int:
    if not os.path.isdir(OUT_DIR):
        print("no results/decision_chain yet")
        return 0
    for name in sorted(os.listdir(OUT_DIR)):
        path = os.path.join(OUT_DIR, name)
        if name.startswith("curves_x2_") and name.endswith(".jsonl"):
            print(f"{name}: {sum(1 for _ in open(path, encoding='utf-8'))} "
                  f"cells")
        elif name.startswith("done_"):
            print(f"{name}: landed")
    print(f"verdict: "
          f"{'landed' if os.path.exists(OUT_JSON) else 'pending (finalize)'}")
    return 0


# ----------------------------------------------------------------- selftest

def cmd_selftest(_) -> int:
    """Hermetic offline selftest (r116 law): no engine run, no real panel,
    no network. B7b contract leg included (r297 law)."""
    fails = []

    def t(name, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")
        if not ok:
            fails.append(name)

    # S1: seed law (prereg s3 + s9.2)
    from science_gates import SEED_REGISTRY, COST_X2_RATE, CostPatch
    t("S1 seed registered + module constant agree",
      SEED_REGISTRY.get("decision_chain_e2e") == BOOTSTRAP_SEED == 20261001
      and BOOTSTRAP_B == 2000)

    # S2: face rate derivation (runtime, zero hand-copy)
    t("S2 rate_side faces",
      abs(rate_side("base") - COST_X2_RATE / 2) < 1e-15
      and abs(rate_side("x2") - COST_X2_RATE) < 1e-15
      and abs(rate_side("x2") - 2 * rate_side("base")) < 1e-15)

    # S3/S4: B/D arm identities under the frozen envelope primitive
    r_att = np.array([0.01, -0.02, 0.03, 0.0])
    r_chop = np.array([0.005, 0.01, -0.01, 0.02])
    Wb = np.tile([1.0, 0.0, 0.0], (4, 1))
    Wd = np.tile([1.0 / 6.0, 5.0 / 6.0, 0.0], (4, 1))
    rb = t34.env_daily(r_att, r_chop, Wb, 0.0013)
    rd = t34.env_daily(r_att, r_chop, Wd, 0.0013)
    t("S3 B arm == member curve verbatim (zero envelope turnover)",
      bool(np.allclose(rb, r_att, atol=1e-15)))
    t("S4 D arm == 1/6 attack + 5/6 chop EW (frozen corps formula)",
      bool(np.allclose(rd, (r_att + 5 * r_chop) / 6.0, atol=1e-15)))

    # S5/S6: A1/A2 weight construction (imported t34 functions, with the
    # T+1 exec shift applied as in the real overlay: state flip at row k
    # lands at row k+1; first row keeps its own state per t34 exec_shift)
    dep = pd.Series(["chop", "cash", "attack", "chop"], index=range(4))
    dep_exec = t34.exec_shift(dep)          # [chop, chop, cash, attack]
    Wc = t34.conf_weights(dep_exec)
    t("S5 A1 = t34 CONF weights (zero attack pre-step)",
      Wc[0].tolist() == [0.0, 1.0, 0.0]
      and Wc[2].tolist() == [0.0, 0.0, 1.0]
      and Wc[3].tolist() == [1.0, 0.0, 0.0])
    fast = pd.Series([True, False, False, False], index=range(4))
    fast_exec = t34.exec_shift(fast)        # [T(fill), T, F, F]
    Wl = t34.weights_matrix(dep_exec, fast_exec, t34.HALF)
    t("S6 A2 = t34 LADDER C1 half-step blend",
      Wl[0].tolist() == [0.5, 0.5, 0.0]     # chop + fast -> half blend
      and Wl[1].tolist() == [0.5, 0.5, 0.0]  # fast at T lands at T+1 exec
      and Wl[2].tolist() == [0.0, 0.0, 1.0]  # cash, no fast
      and Wl[3].tolist() == [1.0, 0.0, 0.0]  # confirmed attack dominates
      and t34.HALF == 0.5)

    # S7: CostPatch multiplier law (t22 Erratum-1) -- doubles + restores
    import engine.backtester as eb
    base_fee = eb.FeeSchedule()
    with CostPatch(2.0):
        with_cost = eb.FeeSchedule()
    t("S7 CostPatch(2.0) doubles fee fields + restores",
      with_cost.commission_rate == base_fee.commission_rate * 2
      and with_cost.slippage_a == base_fee.slippage_a * 2
      and eb.FeeSchedule().commission_rate == base_fee.commission_rate)

    # S8: x2 cell wrapper adds face field under the patch (stubbed body)
    orig = t34._run_cell_curve
    try:
        seen = {}

        def stub(member, pos):
            f = eb.FeeSchedule()
            seen["doubled"] = (f.commission_rate
                               == base_fee.commission_rate * 2)
            seen["inside"] = True
            return {"key": f"{member}|{pos}", "curve": [0.0, 0.01]}

        t34._run_cell_curve = stub
        row = _run_cell_x2("COMPOSITE-CE-01", 7)
    finally:
        t34._run_cell_curve = orig
    t("S8 x2 wrapper = t34 cell body under CostPatch + face tag",
      row["face"] == "x2" and row["key"] == "COMPOSITE-CE-01|7"
      and seen.get("doubled") is True
      and eb.FeeSchedule().commission_rate == base_fee.commission_rate)

    # S9: bootstrap determinism (seed 20261001)
    c1 = _ci_boot(7, 10)
    c2 = _ci_boot(7, 10)
    t("S9 bootstrap deterministic + sane",
      c1 == c2 and c1[0] < 0.7 < c1[1] and _ci_boot(10, 10)[1] == 1.0)

    # S10: pairwise win-rate CI semantics
    t("S10 pairwise CI: all-win -> lo>0.5; all-lose -> hi<0.5",
      _ci_boot(10, 10)[0] > 0.5 and _ci_boot(0, 10)[1] < 0.5)

    # S11: J-C conjunction semantics
    jc = {"J_C1_chain_vs_best_single": True,
          "J_C2_chain_vs_static_ew": True,
          "J_C3_chain_vs_passive": False,
          "J_C4_dd_redline": True}
    win = (jc["J_C1_chain_vs_best_single"]
           and jc["J_C2_chain_vs_static_ew"]
           and jc["J_C3_chain_vs_passive"]
           and jc["J_C4_dd_redline"])
    t("S11 chain_win conjunction (one negative kills)", win is False)

    # S12: J-TARGET cell semantics (rate > rate AND dd >= -0.10)
    cell = {"beat_gt_b": True, "dd_ok": False}
    t("S12 J-TARGET pass needs BOTH beat and dd line",
      bool(cell["beat_gt_b"] and cell["dd_ok"]) is False
      and DD_TARGET_LINE == -0.10)

    # S13: ring-3 friction counterfactual (rate=0 >= rated, exact cost)
    Wx = np.array([[0.0, 1.0, 0.0], [1.0, 0.0, 0.0]])
    r_rated = t34.env_daily(r_att[:2], r_chop[:2], Wx, 0.0013)
    r_free = t34.env_daily(r_att[:2], r_chop[:2], Wx, 0.0)
    fric = float(np.sum(r_free - r_rated))
    t("S13 friction counterfactual: rate=0 strictly >= rated, exact sum",
      fric > 0 and abs(fric - 2 * 0.0013) < 1e-9)

    # S14: segment bucketing on synthetic cells
    cells = {1: {"pos": 1, "start": "2021-01-04", "regime": "bull",
                 "partial_12m": False, "beat_12m": True, "dd_12m": -0.01,
                 "switches": 2, "ret_6m": 0.1, "ret_12m": 0.2,
                 "ret_24m": 0.3, "beat_6m": True, "beat_24m": False,
                 "dd_6m": -0.01, "dd_24m": -0.02, "partial_24m": False,
                 "n_bars": 504, "p_ret_12m": 0.1},
             2: {"pos": 2, "start": "2021-01-05", "regime": "bear",
                 "partial_12m": False, "beat_12m": False, "dd_12m": -0.20,
                 "switches": 3, "ret_6m": 0.1, "ret_12m": 0.2,
                 "ret_24m": 0.3, "beat_6m": True, "beat_24m": False,
                 "dd_6m": -0.01, "dd_24m": -0.02, "partial_24m": False,
                 "n_bars": 504, "p_ret_12m": 0.1}}
    a = _agg_arm(cells, "12m")
    t("S14 agg + segments + D7 fields",
      a["n"] == 2 and a["beats"] == 1 and abs(a["beat_rate"] - 0.5) < 1e-9
      and a["segments"]["bull"]["n"] == 1
      and a["independent_regime_windows"] == 2
      and a["switches_mean"] == 2.5 and a["oos_trades"] == 5)

    # S15: partial-window split
    cells[2]["partial_24m"] = True
    a24 = _agg_arm(cells, "24m")
    t("S15 partial split (24m full=1, partial_n=1)",
      a24["n"] == 1 and a24["partial_n"] == 1)
    cells[2]["partial_24m"] = False

    # S16: switches counting (const W -> 0; one flip -> 1)
    Wconst = np.tile([0.0, 1.0, 0.0], (3, 1))
    sw0 = int((np.abs(np.diff(Wconst, axis=0,
                             prepend=Wconst[:1])).sum(axis=1) > 0).sum())
    Wflip = np.array([[0.0, 1.0, 0.0], [1.0, 0.0, 0.0],
                      [1.0, 0.0, 0.0]])
    sw1 = int((np.abs(np.diff(Wflip, axis=0,
                              prepend=Wflip[:1])).sum(axis=1) > 0).sum())
    t("S16 switches: const=0, single flip=1", sw0 == 0 and sw1 == 1)

    # S17: repro comparator semantics (bit-level, drift caught)
    mine = {"legacy": {"base": {"12m": {
        "A1": {"beat_rate": 0.4296, "min_dd": -0.1249,
               "switches_mean": 48.3},
        "A2": {"beat_rate": 0.4659, "min_dd": -0.124,
               "switches_mean": 52.74}}}},
        "deep": {"base": {"12m": {
            "A1": {"beat_rate": 0.3942, "min_dd": -0.1041,
                   "switches_mean": 17.66},
            "A2": {"beat_rate": 0.4304, "min_dd": -0.104,
                   "switches_mean": 23.63}}}}}
    ref = {"axes": {
        "legacy": {"conf": {"beat_rate_12m": 0.4296, "min_dd_12m": -0.1249,
                            "switches_mean": 48.3},
                   "ladder_C1": {"beat_rate_12m": 0.4659,
                                 "min_dd_12m": -0.1240,
                                 "switches_mean": 52.74}},
        "deep": {"conf": {"beat_rate_12m": 0.3942, "min_dd_12m": -0.1041,
                          "switches_mean": 17.66},
                 "ladder_C1": {"beat_rate_12m": 0.4304,
                               "min_dd_12m": -0.1040,
                               "switches_mean": 23.63}}}}
    ok_all = all(_repro_compare(mine, ref).values())
    mine["legacy"]["base"]["12m"]["A1"]["beat_rate"] = 0.4297
    ok_drift = all(_repro_compare(mine, ref).values())
    t("S17 repro comparator: equal passes, 1bp drift caught",
      ok_all is True and ok_drift is False)

    # S18: checkpoint resume (truncated tail tolerated, t22 law)
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "_selftest_ckpt.jsonl")
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(json.dumps({"key": "A|1"}) + "\n")
        fh.write('{"key": "A|2", "trun')
    keys = load_done_keys(tmp)
    t("S18 resume keys skip truncated tail", keys == {"A|1"})
    os.remove(tmp)

    # S19: passive caliber == t22/t34 formula (t34 S10 reuse)
    cl = pd.DataFrame({"A": np.linspace(100, 120, 300),
                        "B": np.linspace(50, 60, 300)},
                       index=pd.bdate_range("2020-01-01", periods=300))
    mine_p = t34._passive_window(cl, 10, 126)
    idxs = cl.index
    sdate = idxs[10]
    e = idxs[min(10 + 126 - 1, len(idxs) - 1)]
    syms = cl.columns[cl.loc[sdate].notna()]
    base = cl.loc[sdate, syms]
    ref_p = float((cl.loc[sdate:e, syms] / base).mean(axis=1).iloc[-1] - 1.0)
    t("S19 passive caliber == frozen formula", abs(mine_p - ref_p) < 1e-12)

    # S20: windows/constants frozen
    t("S20 frozen constants",
      WINDOWS == {"6m": 126, "12m": 252, "24m": 504}
      and FACES == ("base", "x2") and ARMS == ("A1", "A2", "B", "D")
      and DD_RED_LINE == -0.35 and t34.ATTACK == ["COMPOSITE-CE-01"]
      and len(t34.CHOP) == 5 and SUBSAMPLE_STEP == 25
      and t34.LEGACY_CUTOFF == "2026-09-23"
      and t34.BINDING_CUTOFF == "2026-09-22")

    # S21: B7b contract leg (r297 law): consumer keys ⊆ construction keys
    skeleton = _payload_skeleton()
    t("S21 B7b consumer keys subset of construction keys",
      all(k in skeleton for k in CONSUMER_KEYS))

    # S22: J-L semantics (uplift both axes + dd line)
    jl = {"J_L1_uplift_positive_both_axes": True, "J_L2_dd_ok": False}
    t("S22 J-L pass needs uplift AND dd line",
      bool(jl["J_L1_uplift_positive_both_axes"] and jl["J_L2_dd_ok"])
      is False)

    # S23: amended G-V3 leg-2 (prereg s9.3): freshness + alphabet, equality
    # NEVER asserted (v1 live face vs v3 calibration-layer replay)
    v_ok = _leg2_verdict("2026-09-24", "YELLOW", "2026-09-24", "ORANGE")
    v_stale = _leg2_verdict("2026-09-24", "YELLOW", "2026-09-23", "ORANGE")
    v_alpha = _leg2_verdict("2026-09-24", "PURPLE", "2026-09-24", "ORANGE")
    t("S23 leg-2 amended: divergent states PASS (fresh+alphabet), "
      "stale/aliien FAIL",
      v_ok["ok"] is True and v_stale["ok"] is False
      and v_alpha["ok"] is False
      and v_ok["replay_state"] == "YELLOW"
      and v_ok["v1_live_state"] == "ORANGE")

    print(f"\nselftest: "
          f"{'ALL PASS' if not fails else 'FAIL x' + str(len(fails))}")
    return 0 if not fails else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--face", choices=["x2"], default="x2")
    r.add_argument("--axis", choices=["legacy", "deep"], required=True)
    r.add_argument("--shard", required=True)
    r.add_argument("--pos-from", type=int, default=0)
    r.add_argument("--pos-to", type=int, default=10**9)
    r.add_argument("--limit", type=int, default=0)
    r.add_argument("--workers", type=int, default=0)
    sub.add_parser("finalize")
    sub.add_parser("repro")
    sub.add_parser("status")
    sub.add_parser("selftest")
    args = ap.parse_args()
    if args.cmd == "run":
        return cmd_run(args)
    if args.cmd == "finalize":
        return cmd_finalize(args)
    if args.cmd == "repro":
        return cmd_repro(args)
    if args.cmd == "status":
        return cmd_status(args)
    return cmd_selftest(args)


if __name__ == "__main__":
    sys.exit(main())
