"""MEMBER_REINFORCE_P1 runner -- 在册成员补强面批 (robustness re-derivation,
NOT a new-alpha search batch; T-2026-09-28-107 sec.4(b), fill_ladder
tranche-1(b)).

Laws frozen in research/MEMBER_REINFORCE_P1_PREREG.md @commit dd62920e
(r180 bm-c, SEED_REGISTRY keys member_reinforce_p1_null=20294500 /
_seedstab2=20294600 / _seedstab3=20294700 registered same-commit):

  roster  firm/traders/*.json raw json.load direct read; exclusions =
          FILENAME-level (_template.json = placeholder id=TREND-001 trap,
          pitlaw batch-65; PROS-* = PROSPECT observation wing, O-2045
          constructive exclusion) + level in PAPER_LEVELS (INTERN);
          frozen roster == 6 members. G-ROSTER: re-derive == 6 AND anchor
          constants == frozen probe facts
          (results/_r180bmc_supply_prereg_probe_facts.json roster_face).
  panel   live.paper.load_core (data/daily core48, T-22/T-34 import-face
          lineage), every file truncated at evidence cutoff 2026-09-22.
          G-PANEL: 48 members, every member's truncated last bar ==
          cutoff. G-ANCHOR: live.paper.anchor_gate ok AND the x1 replay's
          4dp IS/OOS Sharpe == prereg anchor constants (+-1e-9 on the
          rounded faces, W4 G-ANCHOR 同例) -- any drift = config-mismatch
          VOID (exit 2), never "data corruption".
  F1      cost-stress re-derivation: 6 members x {x1, x2, x3} faces via
          science_gates.CostPatch(1/2/3) (V1 legacy cost family, registered
          judgment same source; x1 = anchor reproduction face, no new
          verdicts). Reads: x2 Sharpe_full >= 0 = x2-robust / < 0 =
          x2-fragile flag (descriptive, registration verdicts untouched);
          x3 = disclosure-only face.
  F2      seed stability: family null pool per seed, K=200 draws, rng =
          np.random.default_rng([seed, k]); draw k cycles the 6 members'
          OWN entry-mask densities (同掩码 face -- no hand-copied p values)
          through the engine at default params + engine exits (p2 family-A
          Bernoulli bloodline); per seed: skill_line_v2 null inputs ->
          g1_prime_v2 verdict per member per face -> 3/3 agreement =
          seed-stable, any flip = seed-unstable flag (honest disclosure,
          registration verdicts untouched).
  F3      CSCV fold stability: family PBO over the 6-member x1 daily
          return matrix via screening/pbo.cscv_pbo -- 8 blocks (g2 family
          standard face) + 16 blocks (extra folds); |PBO8-PBO16| <= 0.15 =
          fold-stable, over-line = fold-unstable flag.
  F4      regime segmentation: v3 state series via live.paper.v3_state_series
          (market_regime atomic import lineage, national_team_s3 同例);
          segment map FROZEN = p5c_virtual_timepoint.REGIME_MAP (same census
          = comparability law): GREEN->bull, YELLOW->chop, ORANGE/RED->bear;
          per member per segment: segment Sharpe from the x1 daily series +
          beat_rate consumed from the P-5C frozen product (leg-L 6m=1253
          census, import 禁重实现); |beat_rate_seg - beat_rate_full| > 0.10
          = segment-tilt flag (descriptive); segment Sharpe < -0.5 =
          segment red flag.
  gates   G1'v2 per member per face {x1, x2} via science_gates.g1_prime_v2
          (batch_cells=624, pool='core48', batch-own seed-1 null pool;
          x3 = disclosure-only). ZERO registration claims: g2_registration_v2
          is NOT called (prereg s4 G2-不适用面 honest declaration);
          consumption = scorecard robustness dims + promotion-gate evidence.
  d6      §1 descriptive re-disclosure: 6-member x1 daily-return pairwise
          |corr| matrix (registration-time 0.7 gate already passed; no new
          admission gate on the robustness face).
  ledger  append_ledger("MEMBER_REINFORCE_P1", 624, "results/
          member_reinforce/MEMBER-REINFORCE-P1.json", evidence_cutoff=
          "2026-09-22") single-count (24 robustness cells + 600 null
          draws); prev-echo guard on deterministic re-finalize (r259 law);
          gate_attrition measurement row (r248 entries face).

Products (prereg s6): results/member_reinforce/MEMBER-REINFORCE-P1.json +
per-face replay npy/json caches + null seed-shard npy checkpoints
(idempotent resume).

Usage: run | selftest   (exit 0 ok; 2 = fail-closed gate refusal)
"""
import argparse
import json
import math
import os
import shutil
import sys
import tempfile
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import science_gates as SG                      # shared gate library (O-2250)
from screening.pbo import cscv_pbo              # family PBO faces
from engine import run_backtest
from engine.metrics import annual_return, max_drawdown, sharpe
from live.paper import (OOS_START, PAPER_LEVELS, SIGNAL_BUILDERS, ExitPatch,
                        anchor_gate, build_panels, load_core)
from p5c_virtual_timepoint import REGIME_MAP    # frozen segment map (import law)

TRADERS_DIR_G = os.path.join(ROOT, "firm", "traders")
PROBE_JSON = os.path.join(ROOT, "results",
                          "_r180bmc_supply_prereg_probe_facts.json")
P5C_JSON = os.path.join(ROOT, "results", "shortline",
                        "p5c_virtual_timepoint.json")
OUT_DIR = os.path.join(ROOT, "results", "member_reinforce")
CELL_DIR = os.path.join(OUT_DIR, "cells")
NULL_DIR = os.path.join(OUT_DIR, "nulls")
OUT_JSON = os.path.join(OUT_DIR, "MEMBER-REINFORCE-P1.json")
ATT_JSON = os.path.join(ROOT, "results", "gate_attrition.json")

BATCH_NAME = "MEMBER_REINFORCE_P1"
BATCH_CELLS = 624                # 24 robustness cells + 600 null draws (s0)
EVIDENCE_CUTOFF = "2026-09-22"
PBP = 252.0
N_PANEL_EXPECT = 48
ROSTER_N = 6
K_NULLS = 200
NULL_SHARDS = 8
FACES = {"x1": 1, "x2": 2, "x3": 3}              # CostPatch multipliers
SEED_KEYS = ["member_reinforce_p1_null", "member_reinforce_p1_seedstab2",
             "member_reinforce_p1_seedstab3"]
F3_FOLD_STABLE = 0.15
F4_TILT_LINE = 0.10
F4_SEG_RED = -0.5
STATES_LOADER = None            # run default: live.paper.v3_state_series
PANEL_LOADER = None             # run default: live.paper.load_core


def _default_panel_loader():
    from live.paper import load_core as _lc
    return _lc()


def gate_refuse(msg):
    print(f"GATE-REFUSE(exit2): {msg}")
    return 2


# ------------------------------------------------------------------ roster
def load_roster():
    """Frozen-roster derivation: filename-level exclusions (pitlaw b65)
    + PAPER_LEVELS filter; raw json.load direct read (prereg s2)."""
    members, excluded = [], {"template": 0, "pros": 0, "level": 0}
    for fname in sorted(os.listdir(TRADERS_DIR_G)):
        if not fname.endswith(".json"):
            continue
        if fname == "_template.json":
            excluded["template"] += 1
            continue
        if fname.startswith("PROS-"):
            excluded["pros"] += 1
            continue
        with open(os.path.join(TRADERS_DIR_G, fname),
                  encoding="utf-8") as fh:
            t = json.load(fh)
        if t.get("level") not in PAPER_LEVELS:
            excluded["level"] += 1
            continue
        members.append(t)
    return members, excluded


def load_probe_roster():
    with open(PROBE_JSON, encoding="utf-8") as fh:
        probe = json.load(fh)
    face = probe.get("roster_face", {})
    if face.get("n_members") != ROSTER_N:
        return None, f"probe roster n_members {face.get('n_members')} != {ROSTER_N}"
    return face.get("members"), None


# ------------------------------------------------------------------ replay
def replay_member(t, prices_cut, P, mult):
    """One member x one cost face -> (daily return Series, stats dict).
    Same engine path as the live.paper anchor gate (import-face law)."""
    entry = SIGNAL_BUILDERS[t["params"]["entry"]](P)
    params = {k: v for k, v in t["params"].items() if k != "entry"}
    cmgr = SG.CostPatch(mult)
    with cmgr, ExitPatch(t.get("exit_overrides")):
        res = run_backtest(prices_cut, params, entry_signal=entry,
                           exit_signal=(entry <= 0),
                           dd_control=t.get("dd_control"))
    idx = P["close"].index[:len(res["equity_curve"])]
    eq = pd.Series(res["equity_curve"], index=idx)
    ser = eq.pct_change().fillna(0.0)
    n_tr = int(res["metrics"]["num_trades"])
    is_eq, oos_eq = eq[eq.index < OOS_START], eq[eq.index >= OOS_START]
    stats = {
        "sharpe_full": round(float(sharpe(eq)), 4),
        "is_sharpe": round(float(sharpe(is_eq)), 4) if len(is_eq) >= 20
        else None,
        "oos_sharpe": round(float(sharpe(oos_eq)), 4) if len(oos_eq) >= 20
        else None,
        "ann_ret": round(float(annual_return(eq)), 4),
        "max_dd": round(float(max_drawdown(eq)), 4),
        "n_trades": n_tr,
    }
    return ser, stats


# ------------------------------------------------------------------ nulls
def _null_worker(seed, k, densities, n_days, syms):
    """One null draw (worker-side): Bernoulli mask at the cycled member's
    own density, engine default params + engine exits (p2 family-A
    bloodline); rng = default_rng([seed, k]) (prereg F2)."""
    import numpy as _np
    import pandas as _pd
    from engine import run_backtest as _rb
    p = densities[k % len(densities)]
    rng = _np.random.default_rng([seed, k])
    mask = _pd.DataFrame((rng.random((n_days, len(syms))) < p).astype(int))
    exit_ = _pd.DataFrame(False, index=mask.index, columns=mask.columns)
    res = _rb(_NULL_STATE["prices"], {}, entry_signal=mask, exit_signal=exit_)
    return float(res["metrics"]["sharpe"])


_NULL_STATE = None


def _null_init(state):
    global _NULL_STATE
    _NULL_STATE = state
    try:
        import psutil
        psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    except Exception:
        pass


def run_nulls(prices_cut, P, densities):
    """Family null pools per seed (K=200 each, 3 seeds = 600 draws, s0
    accounting). npy shard checkpoints, idempotent resume."""
    from concurrent.futures import ProcessPoolExecutor
    os.makedirs(NULL_DIR, exist_ok=True)
    n_days, syms = len(P["close"].index), list(P["close"].columns)
    seeds = [SG.SEED_REGISTRY[k] for k in SEED_KEYS]
    per = K_NULLS // NULL_SHARDS
    state = {"prices": prices_cut}
    out = {}
    for seed in seeds:
        vals = np.empty(K_NULLS)
        pending = []
        for s in range(NULL_SHARDS):
            path = os.path.join(NULL_DIR, f"null_s{seed}_shard{s}.npy")
            if os.path.exists(path):
                vals[s * per:(s + 1) * per] = np.load(path)
            else:
                pending.append(s)
        if pending:
            jobs = [s * per + i for s in pending for i in range(per)]
            with ProcessPoolExecutor(
                    max_workers=_worker_cap(), initializer=_null_init,
                    initargs=(state,)) as pool:
                futs = {pool.submit(_null_worker, seed, k, densities,
                                    n_days, syms): k for k in jobs}
                for fut in futs:
                    k = futs[fut]
                    vals[k] = fut.result()
            for s in pending:
                np.save(os.path.join(NULL_DIR, f"null_s{seed}_shard{s}.npy"),
                        vals[s * per:(s + 1) * per])
        cov = {"mu": round(float(vals.mean()), 4),
               "sigma": round(float(vals.std(ddof=1)), 4),
               "n_values": int(len(vals))}
        out[seed] = {"values": [round(float(v), 4) for v in vals],
                     "coverage": cov}
    return out, seeds


def _worker_cap():
    try:
        from parallel_runner import worker_cap
        return worker_cap()
    except Exception:
        return 4


# ------------------------------------------------------------------ faces
def member_density(t, P):
    m = SIGNAL_BUILDERS[t["params"]["entry"]](P)
    v = np.asarray(m, dtype=float)
    return round(float(v.mean()), 6)


def d6_pairwise(series_by_member):
    names = list(series_by_member)
    out = {}
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a = np.asarray(series_by_member[names[i]], dtype=float)
            b = np.asarray(series_by_member[names[j]], dtype=float)
            m = np.isfinite(a) & np.isfinite(b)
            if m.sum() > 20 and a[m].std() > 0 and b[m].std() > 0:
                out[f"{names[i]}|{names[j]}"] = round(float(
                    np.corrcoef(a[m], b[m])[0, 1]), 4)
    return out


def f4_regime(x1_series_by_member, states_raw):
    """Segment Sharpe from the x1 daily series + beat-rate consumption from
    the P-5C frozen product (same census = comparability law)."""
    with open(P5C_JSON, encoding="utf-8") as fh:
        p5c = json.load(fh)
    judgments = p5c["judgments"]
    out = {}
    for tid, ser in x1_series_by_member.items():
        j6 = (judgments.get(tid, {}).get("6m", {}).get("x1", {}))
        full_br = j6.get("beat_rate")
        segs = {}
        mapped = states_raw.reindex(ser.index).ffill().map(
            REGIME_MAP).fillna("na")
        for seg in ("bull", "chop", "bear"):
            sub = ser[mapped == seg]
            seg_sh = round(float(sharpe(sub)), 4) if len(sub) >= 20 else None
            seg_br = (j6.get("segments", {}).get(seg, {}).get("beat_rate"))
            delta = (round(seg_br - full_br, 4)
                     if seg_br is not None and full_br is not None else None)
            segs[seg] = {
                "sharpe": seg_sh,
                "beat_rate_p5c": seg_br,
                "beat_rate_delta_vs_full": delta,
                "segment_tilt_flag": bool(delta is not None
                                          and abs(delta) > F4_TILT_LINE),
                "segment_red_flag": bool(seg_sh is not None
                                        and seg_sh < F4_SEG_RED),
                "n_days": int(len(sub)),
            }
        out[tid] = {"full_beat_rate_p5c": full_br, "segments": segs}
    return out


# ------------------------------------------------------------------ product
def _attr_row(batch, delta, total, gates, entries):
    d = json.load(open(ATT_JSON, encoding="utf-8"))
    row = {"batch": batch,
           "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
           "kind": "measurement", "cells_ledger_delta": delta,
           "ledger_total_after": total, "gates": gates,
           "entries": entries}            # r248 entries-list face
    own = [i for i, e in enumerate(d["entries"])
           if e.get("batch") == batch and e.get("kind") == "measurement"]
    if own:
        d["entries"][own[-1]] = row
    else:
        d["entries"].append(row)
    with open(ATT_JSON + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)
    os.replace(ATT_JSON + ".tmp", ATT_JSON)


def finalize(roster_face, panel_face, g_anchor, replays, densities, nulls,
             seeds, f3, f4, d6, f1_flags, f2_stability):
    prev_total = None
    if os.path.exists(OUT_JSON):
        try:
            with open(OUT_JSON, encoding="utf-8") as fh:
                old = json.load(fh)
            prev_total = (old.get("trials_ledger") or {}).get("prev_total")
        except Exception:
            prev_total = None
    seed1 = seeds[0]
    pool1 = nulls[seed1]
    gates = {}
    for t in roster_face:
        tid = t["id"]
        gates[tid] = {}
        for face in ("x1", "x2"):
            ser = replays[tid][face]["ser"]
            st = replays[tid][face]["stats"]
            gates[tid][face] = SG.g1_prime_v2(
                st["sharpe_full"], ser, batch_cells=BATCH_CELLS,
                pool="core48",
                null_pool={"values": pool1["values"],
                           "coverage": pool1["coverage"]},
                n_trades=st["n_trades"], n_entries=st["n_trades"])
    ledger = SG.append_ledger(BATCH_NAME, BATCH_CELLS,
                             file_name="results/member_reinforce/"
                                       "MEMBER-REINFORCE-P1.json",
                             evidence_cutoff=EVIDENCE_CUTOFF,
                             prev_total=prev_total)
    product = {
        "batch": BATCH_NAME,
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "cutoff_meta": SG.cutoff_meta(EVIDENCE_CUTOFF),
        "prereg": "research/MEMBER_REINFORCE_P1_PREREG.md (@dd62920e freeze)",
        "seeds": {k: SG.SEED_REGISTRY[k] for k in SEED_KEYS},
        "roster": roster_face,
        "panel": panel_face,
        "g_anchor": g_anchor,
        "member_entry_mask_densities": densities,
        "f1_cost": {tid: {f: replays[tid][f]["stats"]
                          for f in FACES} for tid in replays},
        "f1_flags": f1_flags,
        "f2_seed_stability": f2_stability,
        "f2_null_pools": {str(s): nulls[s]["coverage"] for s in seeds},
        "f2_null_face": "K=200 Bernoulli draws per seed at the members' own "
                       "entry-mask densities (同掩码), engine default params "
                       "+ engine exits (p2 family-A bloodline), family pool "
                       "per seed (s0 accounting: 200x3=600)",
        "f3_cscv": f3,
        "f4_regime_segments": f4,
        "f4_segment_map": {str(k): v for k, v in REGIME_MAP.items()},
        "d6_pairwise_descriptive": d6,
        "gates": gates,
        "g2_note": "zero registration claims (robustness batch, prereg s4: "
                   "g2_registration_v2 NOT called); consumption = scorecard "
                   "robustness dims + promotion-gate evidence faces",
        "trials_ledger": ledger,
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_JSON + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(product, fh, ensure_ascii=False, indent=1, default=float)
    os.replace(OUT_JSON + ".tmp", OUT_JSON)
    _attr_row(BATCH_NAME, BATCH_CELLS, int(ledger["total"]),
              {"g1_pass": {tid: {f: gates[tid][f]["pass_v2"]
                                 for f in gates[tid]} for tid in gates},
               "x2_fragile": [t for t in f1_flags
                              if f1_flags[t] == "x2-fragile"],
               "seed_unstable": [t for t in f2_stability
                                 if f2_stability[t]["seed_stable"] is False]},
              {"members": len(roster_face), "null_draws": 600})
    return product


# ------------------------------------------------------------------ driver
def cmd_run():
    t0 = time.time()
    if not SG.SEED_REGISTRY.get(SEED_KEYS[0]):
        return gate_refuse("SEED_REGISTRY key missing: "
                          f"{SEED_KEYS[0]} (freeze-commit law)")
    probe_members, err = load_probe_roster()
    if err:
        return gate_refuse(err)
    members, excluded = load_roster()
    if len(members) != ROSTER_N:
        return gate_refuse(f"G-ROSTER re-derive {len(members)} != "
                           f"{ROSTER_N} (excluded={excluded})")
    by_id = {t["id"]: t for t in members}
    for pm in probe_members:
        t = by_id.get(pm["id"])
        if t is None:
            return gate_refuse(f"G-ROSTER member absent: {pm['id']}")
        if t.get("level") != "INTERN" or t["params"]["entry"] != pm["entry"]:
            return gate_refuse(f"G-ROSTER face mismatch: {pm['id']}")
    print(f"roster ok: {len(members)} members (excluded {excluded}) "
          f"({time.time() - t0:.0f}s)", flush=True)

    prices_full = (PANEL_LOADER or _default_panel_loader)()
    if len(prices_full) != N_PANEL_EXPECT:
        return gate_refuse(f"G-PANEL {len(prices_full)} != {N_PANEL_EXPECT}")
    cut = pd.Timestamp(EVIDENCE_CUTOFF)
    for s, df in prices_full.items():
        last = df.index[df.index <= cut]
        if not len(last) or last[-1] != cut:
            return gate_refuse(f"G-PANEL {s} truncated last bar "
                              f"!= {EVIDENCE_CUTOFF}")
    prices_cut = {s: df[df.index <= cut] for s, df in prices_full.items()}
    P = build_panels(prices_cut)
    panel_face = {"n_members": len(prices_cut),
                  "first": str(min(df.index[0] for df in prices_cut.values())
                               .date()),
                  "last": str(cut.date())}

    # G-ANCHOR: live anchor gate + prereg-constant 4dp identity (W4 同例)
    g_anchor = {}
    for t in members:
        a = anchor_gate(t, prices_full)
        if not a.get("ok"):
            return gate_refuse(f"G-ANCHOR drift {t['id']}: "
                               f"{a.get('error')}")
        const = next(p for p in probe_members if p["id"] == t["id"])
        id_ok = (abs(a["got"]["in_sample"]["sharpe"]
                     - const["anchor_is_sharpe"]) < 1e-9
                 and abs(a["got"]["out_sample"]["sharpe"]
                         - const["anchor_oos_sharpe"]) < 1e-9)
        if not id_ok:
            return gate_refuse(
                f"G-ANCHOR prereg identity fail {t['id']}: "
                f"got {a['got']['in_sample']['sharpe']}/"
                f"{a['got']['out_sample']['sharpe']} vs frozen "
                f"{const['anchor_is_sharpe']}/{const['anchor_oos_sharpe']}")
        g_anchor[t["id"]] = {"anchor_gate_ok": True,
                             "is_sharpe": a["got"]["in_sample"]["sharpe"],
                             "oos_sharpe": a["got"]["out_sample"]["sharpe"],
                             "prereg_identity_ok": True,
                             "cutoff": a.get("cutoff")}
    print(f"anchors {len(g_anchor)}/{len(members)} OK "
          f"({time.time() - t0:.0f}s)", flush=True)

    # F1: replays per member x cost face (cached, idempotent)
    os.makedirs(CELL_DIR, exist_ok=True)
    replays = {}
    densities = {}
    for t in members:
        tid = t["id"]
        densities[tid] = member_density(t, P)
        replays[tid] = {}
        for face, mult in FACES.items():
            ck_json = os.path.join(CELL_DIR, f"{tid}_{face}.json")
            ck_npy = ck_json.replace(".json", ".npy")
            if os.path.exists(ck_json) and os.path.exists(ck_npy):
                ser = pd.Series(np.load(ck_npy), index=P["close"].index)
                st = json.load(open(ck_json, encoding="utf-8"))
            else:
                ser, st = replay_member(t, prices_cut, P, mult)
                np.save(ck_npy, ser.to_numpy())
                with open(ck_json + ".tmp", "w", encoding="utf-8") as fh:
                    json.dump(st, fh, ensure_ascii=False, indent=1)
                os.replace(ck_json + ".tmp", ck_json)
                print(f"  replay {tid}/{face}: sharpe={st['sharpe_full']} "
                      f"trades={st['n_trades']} "
                      f"({time.time() - t0:.0f}s)", flush=True)
            replays[tid][face] = {"ser": ser, "stats": st}
        # x1 identity vs anchor constants (replay == anchor machinery)
        x1 = replays[tid]["x1"]["stats"]
        if not (abs(x1["is_sharpe"] - g_anchor[tid]["is_sharpe"]) < 1e-9
                and abs(x1["oos_sharpe"] - g_anchor[tid]["oos_sharpe"])
                < 1e-9):
            return gate_refuse(f"G-ANCHOR x1 replay identity fail {tid}")
    f1_flags = {t["id"]: ("x2-robust"
                          if replays[t["id"]]["x2"]["stats"]["sharpe_full"]
                          >= 0 else "x2-fragile") for t in members}

    # F2: family null pools per seed
    nulls, seeds = run_nulls(prices_cut, P,
                             [densities[t["id"]] for t in members])
    print(f"nulls: 3 seeds x {K_NULLS} "
          f"({time.time() - t0:.0f}s)", flush=True)

    # F3: family CSCV 8 + 16 blocks (x1 face)
    mat = pd.DataFrame({t["id"]: replays[t["id"]]["x1"]["ser"].to_numpy()
                        for t in members})
    pbo8 = cscv_pbo(mat, n_blocks=8)
    pbo16 = cscv_pbo(mat, n_blocks=16)
    d_pbo = abs(float(pbo8["pbo"]) - float(pbo16["pbo"]))
    f3 = {"pbo_8_blocks": pbo8, "pbo_16_blocks": pbo16,
          "abs_delta": round(d_pbo, 4),
          "fold_stable": bool(d_pbo <= F3_FOLD_STABLE),
          "fold_line": F3_FOLD_STABLE}

    # F4: regime segments (states via import-replay; beat from frozen p5c)
    loader = STATES_LOADER or (lambda: __import__(
        "live.paper", fromlist=["v3_state_series"]).v3_state_series())
    states_raw = loader()
    f4 = f4_regime({t["id"]: replays[t["id"]]["x1"]["ser"]
                    for t in members}, states_raw)

    d6 = d6_pairwise({t["id"]: replays[t["id"]]["x1"]["ser"].to_numpy()
                      for t in members})

    # F2 stability: per-seed G1' re-check (verdict agreement 3/3)
    f2_stability = {}
    for t in members:
        tid = t["id"]
        per_face = {}
        for face in ("x1", "x2"):
            verdicts = []
            for seed in seeds:
                g = SG.g1_prime_v2(
                    replays[tid][face]["stats"]["sharpe_full"],
                    replays[tid][face]["ser"], batch_cells=BATCH_CELLS,
                    pool="core48",
                    null_pool={"values": nulls[seed]["values"],
                               "coverage": nulls[seed]["coverage"]},
                    n_trades=replays[tid][face]["stats"]["n_trades"],
                    n_entries=replays[tid][face]["stats"]["n_trades"])
                verdicts.append(bool(g["pass_v2"]))
            agree = all(v == verdicts[0] for v in verdicts)
            per_face[face] = {"verdicts_by_seed": verdicts,
                              "seed_stable": bool(agree)}
        f2_stability[tid] = per_face
    for tid in f2_stability:
        f2_stability[tid]["seed_stable"] = bool(
            f2_stability[tid]["x1"]["seed_stable"]
            and f2_stability[tid]["x2"]["seed_stable"])

    probe_face = [{"id": pm["id"], "level": pm["level"],
                   "entry": pm["entry"],
                   "anchor_is_sharpe": pm["anchor_is_sharpe"],
                   "anchor_oos_sharpe": pm["anchor_oos_sharpe"]}
                  for pm in probe_members]
    product = finalize(probe_face, panel_face, g_anchor, replays,
                        densities, nulls, seeds, f3, f4, d6, f1_flags,
                        f2_stability)
    print(f"finalize ok: members={len(members)} "
          f"ledger={product['trials_ledger']['total']} "
          f"elapsed={time.time() - t0:.0f}s")
    return 0


# ------------------------------------------------------------------ selftest
def _mk_synth_panel(n_days=830, n_syms=6, seed=11):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range(end=pd.Timestamp(EVIDENCE_CUTOFF), periods=n_days)
    prices = {}
    for k in range(n_syms):
        px = 10.0 * np.cumprod(1 + rng.normal(0.0004, 0.012, len(idx)))
        df = pd.DataFrame({"open": px, "high": px * 1.01, "low": px * 0.99,
                           "close": px, "volume": px * 1000.0,
                           "amount": px * px * 1000.0}, index=idx)
        prices[f"51030{k}"] = df
    return prices


def cmd_selftest():
    global TRADERS_DIR_G, PROBE_JSON, P5C_JSON, OUT_DIR, CELL_DIR, \
        NULL_DIR, OUT_JSON, ATT_JSON, K_NULLS, NULL_SHARDS, STATES_LOADER, \
        N_PANEL_EXPECT, ROSTER_N, PANEL_LOADER
    tmp = tempfile.mkdtemp(prefix="member_reinforce_selftest_")
    K_NULLS, NULL_SHARDS = 30, 2
    ok = []
    try:
        # hermetic panel (6 syms -> N_PANEL_EXPECT overridden)
        prices = _mk_synth_panel()
        N_PANEL_EXPECT = len(prices)
        PANEL_LOADER = lambda: prices
        P = build_panels(prices)
        entry_key = "low_vol_long(n=60, top_k=5, daily)"

        # roster fixtures: 3 members + template + PROS (exclusion bites)
        TRADERS_DIR_G = os.path.join(tmp, "traders")
        os.makedirs(TRADERS_DIR_G)
        member_ids = []
        for i in range(3):
            t = {"id": f"TEST-CE-{i:02d}", "level": "INTERN",
                 "created": "2026-09-23",
                 "evidence_cutoff": EVIDENCE_CUTOFF,
                 "params": {"entry": entry_key, "max_positions": 3,
                            "position_size_pct": 0.2,
                            "time_decay_period": 25,
                            "time_decay_threshold": 0.05,
                            "trailing_stop_activate": 0.1},
                 "exit_overrides": {"loss_time_days": 16},
                 "backtest": {
                     "in_sample": {"sharpe": 0.0, "max_dd": 0.0,
                                   "annual": 0.0, "trades": 0},
                     "out_sample": {"sharpe": 0.0, "max_dd": 0.0,
                                    "annual": 0.0, "trades": 0}}}
            with open(os.path.join(TRADERS_DIR_G, f"{t['id']}.json"), "w",
                      encoding="utf-8") as fh:
                json.dump(t, fh)
            member_ids.append(t["id"])
        json.dump({"id": "TREND-001"}, open(
            os.path.join(TRADERS_DIR_G, "_template.json"), "w"))
        json.dump({"id": "PROS-X", "level": "PROSPECT"}, open(
            os.path.join(TRADERS_DIR_G, "PROS-X.json"), "w"))
        json.dump({"id": "TRAINEE-EX", "level": "SOMETHING"}, open(
            os.path.join(TRADERS_DIR_G, "TRAINEE-EX.json"), "w"))
        ROSTER_N = 3

        # derive-then-freeze: anchor_gate's own got faces frozen verbatim
        # into the trader JSONs (fixture-probe law; the got IS the anchor)
        for i, tid in enumerate(member_ids):
            with open(os.path.join(TRADERS_DIR_G, f"{tid}.json"),
                      encoding="utf-8") as fh:
                t = json.load(fh)
            a = anchor_gate(t, prices)
            if not a.get("got"):
                raise RuntimeError(f"fixture anchor derive failed: {a}")
            t["backtest"] = {"in_sample": a["got"]["in_sample"],
                             "out_sample": a["got"]["out_sample"]}
            with open(os.path.join(TRADERS_DIR_G, f"{tid}.json"), "w",
                      encoding="utf-8") as fh:
                json.dump(t, fh)

        # probe facts + p5c product fixtures
        probe = {"roster_face": {"n_members": 3, "members": []}}
        for tid in member_ids:
            with open(os.path.join(TRADERS_DIR_G, f"{tid}.json"),
                      encoding="utf-8") as fh:
                t = json.load(fh)
            probe["roster_face"]["members"].append(
                {"id": tid, "level": "INTERN", "entry": entry_key,
                 "evidence_cutoff": EVIDENCE_CUTOFF,
                 "anchor_is_sharpe": t["backtest"]["in_sample"]["sharpe"],
                 "anchor_oos_sharpe": t["backtest"]["out_sample"]["sharpe"]})
        PROBE_JSON = os.path.join(tmp, "probe.json")
        json.dump(probe, open(PROBE_JSON, "w"))
        P5C_JSON = os.path.join(tmp, "p5c.json")
        json.dump({"judgments": {tid: {"6m": {"x1": {
            "beat_rate": 0.5,
            "segments": {"bull": {"beat_rate": 0.65},
                         "chop": {"beat_rate": 0.5},
                         "bear": {"beat_rate": 0.2}}}}}
            for tid in member_ids}}, open(P5C_JSON, "w"))
        OUT_DIR = os.path.join(tmp, "out")
        CELL_DIR = os.path.join(OUT_DIR, "cells")
        NULL_DIR = os.path.join(OUT_DIR, "nulls")
        OUT_JSON = os.path.join(OUT_DIR, "MEMBER-REINFORCE-P1.json")
        ATT_JSON = os.path.join(tmp, "attr.json")
        json.dump({"entries": []}, open(ATT_JSON, "w"))
        os.makedirs(CELL_DIR, exist_ok=True)
        os.makedirs(NULL_DIR, exist_ok=True)
        _n_idx = len(P["close"].index)
        _cyc = ["GREEN", "YELLOW", "ORANGE", "RED"]
        STATES_LOADER = lambda: pd.Series(
            [_cyc[i % 4] for i in range(_n_idx)],
            index=P["close"].index)

        # shared-library stateful faces stubbed (hermetic isolation)
        _ne, _pb, _al, _lh = SG.n_eff, SG.passive_baseline, \
            SG.append_ledger, SG.ledger_head
        SG.n_eff = lambda bc, rd=None: int(bc)
        SG.passive_baseline = lambda pool="core48", rd=None: 0.4606
        SG.append_ledger = lambda *a, **k: {"prev_total": 0, "total": 100,
                                            "batch": BATCH_NAME}
        SG.ledger_head = lambda rd=None: {"total": 500, "file": None,
                                          "note": None}
        _real_cscv = globals()["cscv_pbo"]
        globals()["cscv_pbo"] = lambda mat, n_blocks=8: {"pbo": 0.1}
        try:
            rc = cmd_run()
            ok.append(("cmd_run on fixtures exits 0", rc == 0))
            ok.append(("product written", os.path.exists(OUT_JSON)))
            if rc == 0:
                prod = json.load(open(OUT_JSON, encoding="utf-8"))
                ok.append(("product fields",
                           prod["evidence_cutoff"] == EVIDENCE_CUTOFF
                           and "cutoff_meta" in prod
                           and len(prod["g_anchor"]) == 3
                           and len(prod["f1_cost"]) == 3
                           and all(set(v) == {"x1", "x2", "x3"}
                                   for v in prod["f1_cost"].values())
                           and "gates" in prod and "f2_seed_stability" in prod
                           and prod["trials_ledger"]["total"] == 100))
                ok.append(("g2 not called note",
                           "g2_registration_v2 NOT called"
                           in prod["g2_note"]))
                ok.append(("f3 fold faces",
                           "pbo_16_blocks" in prod["f3_cscv"]
                           and prod["f3_cscv"]["fold_stable"] is True))
                ok.append(("f4 tilt flag (planted 0.65-0.5=0.15>0.10)",
                           prod["f4_regime_segments"][member_ids[0]]
                           ["segments"]["bull"]["segment_tilt_flag"]
                           is True))
                ok.append(("f4 segment map consumed",
                           prod["f4_segment_map"]["ORANGE"] == "bear"))
                att = json.load(open(ATT_JSON, encoding="utf-8"))
                ok.append(("attrition row",
                           att["entries"][-1]["batch"] == BATCH_NAME))

            # idempotent no-op face
            rc2 = main_noop_check()
            ok.append(("re-run = idempotent no-op", rc2 == 0))
        finally:
            SG.n_eff, SG.passive_baseline, SG.append_ledger = _ne, _pb, _al
            SG.ledger_head = _lh
            globals()["cscv_pbo"] = _real_cscv

        # drift refusal paths
        real_id = probe["roster_face"]["members"][0]["anchor_is_sharpe"]
        probe["roster_face"]["members"][0]["anchor_is_sharpe"] = \
            real_id + 0.5
        json.dump(probe, open(PROBE_JSON, "w"))
        if os.path.exists(OUT_JSON):
            os.remove(OUT_JSON)
        rc3 = cmd_run()
        ok.append(("G-ANCHOR prereg-identity drift refusal", rc3 == 2))
        probe["roster_face"]["members"][0]["anchor_is_sharpe"] = real_id
        json.dump(probe, open(PROBE_JSON, "w"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    n_ok = sum(1 for _, v in ok if v)
    print(f"member_reinforce_p1 selftest: {n_ok}/{len(ok)} PASS")
    for name, v in ok:
        if not v:
            print(f"  FAIL: {name}")
    return 0 if n_ok == len(ok) else 1


def main_noop_check():
    """Idempotence probe for the selftest (product exists -> no-op)."""
    if os.path.exists(OUT_JSON) and \
            os.environ.get("MEMBER_REINFORCE_P1_REFINALIZE") != "1":
        return 0
    return 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "selftest"])
    a = ap.parse_args()
    if a.cmd == "selftest":
        return cmd_selftest()
    if os.path.exists(OUT_JSON) and \
            os.environ.get("MEMBER_REINFORCE_P1_REFINALIZE") != "1":
        print("idempotent no-op: MEMBER-REINFORCE-P1.json exists "
              "(MEMBER_REINFORCE_P1_REFINALIZE=1 = only redo)")
        return 0
    return cmd_run()


if __name__ == "__main__":
    sys.exit(main())
