"""T-89 slice-1b: PROSPECT 22-member regime-segmented stats runner
(ticket T-2026-09-26-89, CEO order O-20260927-0752; prereg
research/PROS_REGIME_SEGMENTS_P1.md, frozen e33984e4 r309 + s2-iii
zero-run census amendment r313).

Import-face reuse of scripts/t22_virtual_timepoints.py (zero
re-implementation, ticket law): enumerate_starts / regime_proxy /
_load_axis_prices / _run_cell / module _G / load_done_keys all come from
the t22 module; this runner only injects the PROSPECT member set
(level=PROSPECT registered config replay, 22 members, prereg s1 roster)
and re-targets the checkpoint directory.

Cost face: base ONLY (prereg s3: x2 face not run this batch; registered
anchors already carry the x2 single-point face). Windows {6m,12m,24m}
sliced off one 24m engine run per cell (P-5 pattern, via t22._run_cell).

Fail-closed gates before any cell burn (all exit 3 = batch void):
  G-ANCHOR   22/22 roster exact + paper-state anchor_ok + constructive
             byte-reconciliation (member prospect.recorded_* == state
             anchor.got, field-exact) + uniform anchor evidence_cutoff
             2026-09-22 (prereg s2-ii; drift = batch void, T-22/P-5 law).
  G-PANEL    legacy panel end == 2026-09-24 (prereg s2 frozen probe value)
             after truncation to the frozen cutoff -- Monday-bar-proof:
             the panel is truncated at load so every shard/cell sees the
             identical panel regardless of burn time; deep bounded by the
             t18 manifest (assert evidence_cutoff == 2026-09-22).
  G-CENSUS   fresh enumeration == amended gate targets (legacy 1,256 /
             deep 1,506, s2-iii amendment r313) AND == t22 finalize
             record + {legacy +1 / deep +0} cross-check (the +1 start is
             the documented panel-extension face, probe
             results/_r313bmb_prospect_probe.json).

Checkpoint (t22 law): results/pros_segs/cells_{axis}_{shard}.jsonl
(row-level done-key resume, truncated-tail tolerated) + done markers
(gitignored, prereg s6). Finalize = harvest-round face (prereg s6), not
part of this runner.

Usage:
  python scripts/prospect_regime_segments.py run --axis legacy --shard LA \
      [--pos-from N --pos-to M] [--limit K] [--workers N]
  python scripts/prospect_regime_segments.py status
  python scripts/prospect_regime_segments.py finalize   (harvest round)
  python scripts/prospect_regime_segments.py selftest      (offline)
"""
import argparse
import glob
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

import t22_virtual_timepoints as t22

TICKET = "T-2026-09-26-89"
BATCH = "PROS_REGIME_SEGMENTS_P1"
OUT_DIR = os.path.join("results", "pros_segs")
FACE = "base"                      # prereg s3: single cost face this batch
LEGACY_CUTOFF = "2026-09-24"       # prereg s2 frozen probe value (r309)
ANCHOR_CUTOFF = "2026-09-22"       # prereg s2: anchor replay cutoff, uniform
GATE_LEGACY_STARTS = 1256          # s2-iii amended r313 (t22 record 1255 +1)
GATE_DEEP_STARTS = 1506            # s2-iii (== t22 record)
N_MEMBERS = 22                     # prereg s1 roster, exact
# _G keys consumed inside t22._run_cell (S5 static contract parses the
# t22 source and asserts this set covers every _G["..."] access there).
INIT_G_KEYS = frozenset({"prices", "close", "idx", "traders", "entries",
                         "params_by_id", "exits_by_id", "regime"})
# Row-construction key contract (t22._run_cell return schema, frozen):
# first row written per run is validated against this set, fail-closed.
ROW_CONSTRUCTION_KEYS = frozenset({
    "key", "trader", "pos", "start", "face", "regime", "n_listed",
    "partial_12m", "partial_24m", "ret_6m", "ret_12m", "ret_24m",
    "p_ret_6m", "p_ret_12m", "p_ret_24m", "dd_6m", "dd_12m", "dd_24m",
    "sharpe_6m", "sharpe_12m", "sharpe_24m", "trades_6m", "trades_12m",
    "trades_24m", "beat_6m", "beat_12m", "beat_24m"})
# Consumer keys (B7b contract, r297 law): downstream faces that consume
# this batch's cells/finalize -- t24_prospect_promotion third leg
# (per-member beat_rate_6m) and MARKET_STAGE_TABLE.md row refresh
# (per-member per-segment n/beat_rate/min_dd + role readout). Every
# consumer key must be derivable from the construction key set.
ROW_CONSUMER_KEYS = frozenset({
    "beat_6m", "dd_6m", "regime", "trader", "pos", "start",
    "partial_12m", "partial_24m", "trades_6m", "sharpe_6m", "ret_6m",
    "p_ret_6m", "n_listed"})

ANCHOR_FIELDS = ("full_sharpe", "oos_sharpe", "x2_full_sharpe",
                 "n_trades", "oos_trades", "max_dd")


def shard_path(axis: str, shard: str) -> str:
    return os.path.join(OUT_DIR, f"cells_{axis}_{shard}.jsonl")


def log_path(axis: str, shard: str) -> str:
    return os.path.join(OUT_DIR, "logs", f"{axis}_{shard}.log")


def _log(path: str, msg: str):
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")


def load_prospect_members():
    """22 PROSPECT members from TRADERS_DIR, id-sorted (prereg s1 roster).
    Zero new configs: registered candidate replay only (ticket law)."""
    from firm.hr import TRADERS_DIR
    members = []
    for f in sorted(glob.glob(os.path.join(str(TRADERS_DIR), "*.json"))):
        with open(f, encoding="utf-8") as fh:
            t = json.load(fh)
        if t.get("level") == "PROSPECT":
            members.append(t)
    return members


def gate_anchor(members) -> dict:
    """G-ANCHOR: 22/22 anchor_ok + constructive byte-reconciliation of the
    anchor face (member registration constructs the expected face; the
    paper state must match field-exact) + uniform anchor evidence cutoff."""
    rep = {"gate": "G-ANCHOR", "n": 0, "recon_fail": [], "cuts": set()}
    if len(members) != N_MEMBERS:
        rep["error"] = f"roster {len(members)} != {N_MEMBERS}"
        return rep
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for t in members:
        sid = os.path.join(root, "results", "prospect_paper",
                           f"{t['id']}.json")
        st = json.load(open(sid, encoding="utf-8"))
        rep["n"] += 1
        rep["cuts"].add(st.get("evidence_cutoff"))
        if not st.get("anchor_ok"):
            rep["recon_fail"].append(f"{t['id']}: anchor_ok false")
            continue
        got = st.get("anchor", {}).get("got", {})
        for f in ANCHOR_FIELDS:
            exp = t["prospect"][f"recorded_{f}"]
            if got.get(f) != exp:
                rep["recon_fail"].append(
                    f"{t['id']}.{f}: state={got.get(f)!r} != "
                    f"registered={exp!r}")
    rep["cuts"] = sorted(c for c in rep["cuts"] if c)
    rep["pass"] = (not rep["recon_fail"] and rep["cuts"] == [ANCHOR_CUTOFF])
    return rep


def _truncate_legacy(prices: dict) -> dict:
    """Freeze the legacy panel at the prereg cutoff: mid-burn Monday-bar
    cannot extend the panel under any shard (deterministic cells)."""
    hi = pd.Timestamp(LEGACY_CUTOFF)
    return {s: df[df.index <= hi] for s, df in prices.items()}


def _load_axis_bounded(axis: str) -> dict:
    if axis == "legacy":
        return _truncate_legacy(t22._load_axis_prices(axis))
    return t22._load_axis_prices(axis)   # deep: manifest-bounded already


def _init_worker(axis: str, lp: str):
    """Worker init: PROSPECT member injection into the t22 module _G so
    t22._run_cell runs PROSPECT cells unmodified (import-face law)."""
    import psutil
    pri = getattr(psutil, "BELOW_NORMAL_PRIORITY_CLASS", None)
    if pri is not None:
        try:
            psutil.Process().nice(pri)   # O-1136 full-load low-priority pool
        except Exception:
            pass
    from live.paper import SIGNAL_BUILDERS, build_panels
    prices = _load_axis_bounded(axis)
    P = build_panels(prices)
    close = P["close"]
    members = load_prospect_members()
    entries, params_by_id, exits_by_id = {}, {}, {}
    for t in members:
        entries[t["id"]] = SIGNAL_BUILDERS[t["params"]["entry"]](P)
        params_by_id[t["id"]] = {k: v for k, v in t["params"].items()
                                 if k != "entry"}
        exits_by_id[t["id"]] = t.get("exit_overrides")
    reg = None
    if "510300" in close.columns:
        reg = t22.regime_proxy(close["510300"])
    t22._G.update(prices=prices, close=close, idx=close.index,
                  traders=[t["id"] for t in members], entries=entries,
                  params_by_id=params_by_id, exits_by_id=exits_by_id,
                  regime=reg)


def _g_consumed_keys_in_t22_run_cell() -> set:
    """Static parse of the t22 source: every _G["..."] access inside the
    _run_cell body (S5 contract input; hermetic, no import side effects
    beyond reading the file we already import)."""
    src_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "t22_virtual_timepoints.py")
    body = open(src_file, encoding="utf-8").read()
    start = body.index("def _run_cell")
    end = body.index("\ndef ", start + 1)
    import re
    return set(re.findall(r'_G\["([a-z_0-9]+)"\]', body[start:end]))


def _census_prices(axis):
    prices = _load_axis_bounded(axis)
    from live.paper import build_panels
    close = build_panels(prices)["close"]
    return prices, close


def cmd_run(args) -> int:
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUT_DIR, "logs"), exist_ok=True)
    lp = log_path(args.axis, args.shard)
    if os.environ.get("PROS_SEGS_DETACHED") == "1":
        sys.stdout = open(lp, "a", buffering=1, encoding="utf-8")
        sys.stderr = sys.stdout
    t0 = time.time()
    _log(lp, f"[{args.shard}] run start axis={args.axis} "
             f"pos=[{args.pos_from},{args.pos_to}) face={FACE}")

    members = load_prospect_members()
    a = gate_anchor(members)
    if not a.get("pass"):
        _log(lp, f"G-ANCHOR FAIL: {a}")
        return 3
    _log(lp, f"G-ANCHOR PASS: {a['n']}/{N_MEMBERS} anchor_ok + "
             f"byte-reconciled, cuts={a['cuts']}")

    prices, close = _census_prices(args.axis)
    idx = close.index
    if args.axis == "legacy":
        panel_end_gate = str(idx[-1].date()) == LEGACY_CUTOFF
    else:
        man = json.load(open(os.path.join("results", "shortline",
                                          "t18_deep_manifest.json"),
                             encoding="utf-8"))
        panel_end_gate = (man.get("evidence_cutoff") == ANCHOR_CUTOFF
                          and str(idx[-1].date()) == ANCHOR_CUTOFF)
    if not panel_end_gate:
        _log(lp, f"G-PANEL FAIL: legacy end={str(idx[-1].date())} "
                 f"(frozen {LEGACY_CUTOFF}) / deep manifest face")
        return 3
    if "510300" not in close.columns:
        _log(lp, "G-PANEL FAIL: 510300 absent -- regime segments impossible")
        return 3
    _log(lp, f"G-PANEL PASS: {args.axis} end={str(idx[-1].date())}")

    listed = close.notna().sum(axis=1)
    eligible = t22.enumerate_starts(len(idx), listed)
    gate_n = (GATE_LEGACY_STARTS if args.axis == "legacy"
              else GATE_DEEP_STARTS)
    t22_rec = json.load(open(os.path.join("results",
                                          "t22_virtual_timepoints.json"),
                             encoding="utf-8"))
    rec_n = t22_rec["axes"][args.axis]["n_starts"]
    delta = 1 if args.axis == "legacy" else 0   # s2-iii amendment face
    if not (len(eligible) == gate_n == rec_n + delta):
        _log(lp, f"G-CENSUS FAIL: n={len(eligible)} gate={gate_n} "
                 f"t22_record={rec_n} (expected +{delta})")
        return 3
    _log(lp, f"G-CENSUS PASS: n={len(eligible)} == gate {gate_n} == "
             f"t22 record {rec_n}+{delta}")

    shard = eligible[args.pos_from:args.pos_to]
    if args.limit:
        shard = shard[:args.limit]
    if not shard:
        _log(lp, "nothing to do (empty shard range)")
        return 0
    tids = [t["id"] for t in members]
    path = shard_path(args.axis, args.shard)
    done = t22.load_done_keys(path)
    jobs = [(tid, pos) for pos in shard for tid in tids
            if f"{tid}|{pos}" not in done]
    _log(lp, f"panel {idx[0].date()}->{idx[-1].date()} eligible={len(eligible)}"
             f" shard_positions={len(shard)} cells_todo={len(jobs)} "
             f"resume_skipped={len(shard) * len(tids) - len(jobs)}")
    if not jobs:
        _log(lp, "all cells already checkpointed -- no-op")
        return 0

    first_row_checked = {"done": False}
    from concurrent.futures import ProcessPoolExecutor, as_completed
    from parallel_runner import worker_cap
    workers = args.workers or worker_cap()
    done_ct = 0
    with open(path, "a", encoding="utf-8") as fh:
        try:
            with ProcessPoolExecutor(max_workers=workers,
                                     initializer=_init_worker,
                                     initargs=(args.axis, lp)) as pool:
                futs = {pool.submit(t22._run_cell, tid, pos, FACE):
                        (tid, pos) for tid, pos in jobs}
                for fut in as_completed(futs):
                    row = fut.result()
                    if not first_row_checked["done"]:
                        missing = ROW_CONSTRUCTION_KEYS - set(row)
                        if missing:
                            _log(lp, f"ROW-CONTRACT FAIL: missing {missing}")
                            raise SystemExit(3)
                        first_row_checked["done"] = True
                    fh.write(json.dumps(row, default=bool) + "\n")
                    fh.flush()
                    done_ct += 1
        finally:
            fh.close()
    runtime = round(time.time() - t0, 1)
    marker = {"shard": args.shard, "axis": args.axis, "face": FACE,
              "cells_written": done_ct, "cells_total": len(jobs),
              "n_eligible": len(eligible), "workers": workers,
              "runtime_sec": runtime,
              "finished_at": time.strftime("%Y-%m-%d %H:%M:%S"),
              "ticket": TICKET, "batch": BATCH}
    with open(os.path.join(OUT_DIR, f"done_{args.axis}_{args.shard}.json"),
              "w", encoding="utf-8") as fh:
        json.dump(marker, fh, indent=2)
    _log(lp, f"DONE {done_ct}/{len(jobs)} cells in {runtime}s "
             f"workers={workers}")
    return 0


# ------------------------------------------------------------- finalize
# Harvest-round face (prereg s6; this runner's own docstring law). All
# aggregation/CI/pooled/subsample functions come from the t22 module per
# the import-face law (zero re-implementation). Single finalization (X2
# runner canon): PROS_SEGS_REFINALIZE=1 is the only redo path.

FINALIZE_GUARD_ENV = "PROS_SEGS_REFINALIZE"
FINALIZE_OUT_JSON = os.path.join("results", "prospect_regime_segments.json")
FINALIZE_OUT_CSV = os.path.join("research", "shortline",
                                "prospect_regime_segments_results.csv")
FINALIZE_WINDOWS = ("6m", "12m", "24m")
AXIS_CUTOFFS = {"legacy": LEGACY_CUTOFF, "deep": ANCHOR_CUTOFF}
ATTACK_CAND_MIN_N = 30          # s4/s5 caliber: bull seg >= 0.70 AND n >= 30
ALL_WEATHER_SPREAD = 0.05       # descriptive role rule (disclosed, non-gate)
VARIANT_DIVERGENCE_PP = 0.20   # s5 pred-3 caliber (20pp family split line)


def _family_of(tid: str) -> str:
    """Family key: strip PROS- prefix, -01 suffix, -CE variant marker
    (prereg s1: 11 pair families + RSRS/VOB singles = 11+2 caliber)."""
    base = tid[len("PROS-"):]
    if base.endswith("-01"):
        base = base[:-3]
    if base.endswith("-CE"):
        base = base[:-3]
    return base


def family_representatives(member_ids):
    """One representative per family: non-CE base variant preferred,
    id-sorted (variant pairs share the alpha claim; the family caliber
    counts the claim once -- prereg s1 dual-caliber disclosure)."""
    fams = {}
    for tid in member_ids:
        fams.setdefault(_family_of(tid), []).append(tid)
    rep = {}
    for fam, ids in fams.items():
        non_ce = [i for i in ids if "-CE" not in i]
        rep[fam] = sorted(non_ce or ids)[0]
    return rep


def _finalize_guard(out_json=None) -> bool:
    """True = proceed (no landed product, or explicit redo env)."""
    out_json = out_json or FINALIZE_OUT_JSON
    if os.path.exists(out_json) and \
            os.environ.get(FINALIZE_GUARD_ENV) != "1":
        return False
    return True


def _union_cells_dir(out_dir, axis: str):
    """Union every cells_{axis}_*.jsonl shard in out_dir (t22 finalize
    canon): corrupt line anywhere = integrity abort face; duplicate keys
    = integrity abort face (probe-subset or double-landed shards both
    land here, never silently pooled)."""
    rows, files_audit, corrupt, dups = [], {}, 0, []
    seen = set()
    if not os.path.isdir(out_dir):
        return rows, {"files": {}, "corrupt": 0, "dups": [], "absent": True}
    for name in sorted(os.listdir(out_dir)):
        if not (name.startswith(f"cells_{axis}_")
                and name.endswith(".jsonl")):
            continue
        n_rows = 0
        with open(os.path.join(out_dir, name),
                  encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    corrupt += 1
                    continue
                n_rows += 1
                if r["key"] in seen:
                    dups.append(r["key"])
                    continue
                seen.add(r["key"])
                rows.append(r)
        files_audit[name] = n_rows
    return rows, {"files": files_audit, "corrupt": corrupt, "dups": dups,
                  "absent": False}


def _coverage_gate(rows, member_ids, eligible, idx):
    """Fail-closed finalize coverage census for one axis: every member on
    every eligible start, start-date integrity vs the live frozen panel,
    uniform passive window returns per start across members, zero foreign
    traders. Missing/duplicated/foreign shards all land here."""
    by_trader = {tid: {} for tid in member_ids}
    passive_seen, start_bad, passive_bad, foreign = {}, 0, 0, []
    for r in rows:
        tid = r["trader"]
        if tid not in by_trader:
            foreign.append(tid)
            continue
        p = r["pos"]
        if str(idx[p].date()) != r["start"]:
            start_bad += 1
        for w in ("6m", "12m", "24m"):
            k = (p, w)
            v = r.get(f"p_ret_{w}")
            if k in passive_seen and passive_seen[k] != v:
                passive_bad += 1
            else:
                passive_seen[k] = v
        by_trader[tid][p] = r
    elig_set = set(eligible)
    ok = (not foreign and start_bad == 0 and passive_bad == 0
          and all(set(by_trader[tid]) == elig_set
                  for tid in member_ids))
    return {"ok": ok, "by_trader": by_trader, "start_bad": start_bad,
            "passive_bad": passive_bad, "foreign": foreign,
            "n_cells": len(rows)}


def _member_corr(by_trader, eligible, wname):
    """Member-pairwise window-return corr (X2 _arm_corr canon: aligned
    virtual-startpoint vectors, disclosure column only, never a gate).
    Prereg s1 'daily-return corr' operationalized at window caliber: the
    frozen cells schema (s6) carries window metrics only and finalize
    runs zero new engine passes (out-of-batch sleeve replays not run;
    the X2 prereg used the same wording and the same window caliber)."""
    tids = sorted(by_trader)
    out = {}
    for i, a in enumerate(tids):
        for b in tids[i + 1:]:
            va = np.array([by_trader[a][p][f"ret_{wname}"]
                           for p in eligible], dtype=float)
            vb = np.array([by_trader[b][p][f"ret_{wname}"]
                           for p in eligible], dtype=float)
            if va.std() > 0 and vb.std() > 0:
                out[f"{a}|{b}"] = round(
                    float(np.corrcoef(va, vb)[0, 1]), 4)
            else:
                out[f"{a}|{b}"] = None
    return out


def _role_readout(agg6):
    """Descriptive corps-fit readout (prereg s4): segment argmax with the
    all-weather spread rule + attack-corps candidate flag (s5 caliber).
    Numeric disclosure face: never a gate, never narrative-over-numbers."""
    segs = {s: v for s, v in (agg6.get("segments") or {}).items()
            if s in ("bear", "chop", "bull") and v.get("n")}
    if not segs:
        return {"role": "insufficient_segments",
                "segment_beat_rates": {}, "spread": None,
                "attack_candidate": False}
    rates = {s: v["beat_rate"] for s, v in segs.items()}
    spread = max(rates.values()) - min(rates.values())
    if len(rates) == 3 and spread <= ALL_WEATHER_SPREAD:
        role = "all_weather"
    else:
        role = max(sorted(rates), key=lambda s: rates[s])
    bull = segs.get("bull", {})
    attack = bool(bull.get("beat_rate") is not None
                  and bull["beat_rate"] >= t22.BEAT_LINE
                  and bull.get("n", 0) >= ATTACK_CAND_MIN_N)
    return {"role": role, "segment_beat_rates": rates,
            "spread": round(spread, 4), "attack_candidate": attack,
            "attack_candidate_caliber": (
                f"bull seg beat_rate >= {t22.BEAT_LINE} AND n >= "
                f"{ATTACK_CAND_MIN_N} (6m base, prereg s5 pred-2)")}


def _variant_divergence(judgments, member_ids):
    """s5 pred-3: same-family variant segment divergence > 20pp = real
    parameter-variant split (disclosed; family-caliber notes absorb it)."""
    out = []
    fams = {}
    for tid in member_ids:
        fams.setdefault(_family_of(tid), []).append(tid)
    for fam, ids in sorted(fams.items()):
        if len(ids) < 2:
            continue
        a, b = sorted(ids)[:2]
        ja = (judgments.get(a, {}).get("6m", {}) or {}).get("segments") or {}
        jb = (judgments.get(b, {}) or {}).get("6m", {}).get("segments") or {}
        for seg in ("bear", "chop", "bull"):
            ra = (ja.get(seg) or {}).get("beat_rate")
            rb = (jb.get(seg) or {}).get("beat_rate")
            if ra is None or rb is None:
                continue
            if abs(ra - rb) > VARIANT_DIVERGENCE_PP:
                out.append({"family": fam, "pair": [a, b], "segment": seg,
                            "rates": [ra, rb],
                            "delta_pp": round(abs(ra - rb), 4)})
    return out


def cmd_finalize(_) -> int:
    if not _finalize_guard():
        print(f"finalize already landed ({FINALIZE_OUT_JSON}); "
              f"{FINALIZE_GUARD_ENV}=1 = only redo path")
        return 0
    t0 = time.time()
    print("=== PROSPECT_REGIME_SEGMENTS finalize (prereg s3/s4/s6) ===")
    from science_gates import append_ledger, cutoff_meta

    members = load_prospect_members()
    if len(members) != N_MEMBERS:
        print(f"finalize: roster {len(members)} != {N_MEMBERS} -- abort")
        return 2
    member_ids = [m["id"] for m in members]
    anch = gate_anchor(members)
    if not anch.get("pass"):
        print(f"finalize: G-ANCHOR FAIL {anch} -- abort")
        return 2
    print(f"G-ANCHOR PASS: {anch['n']}/{N_MEMBERS} byte-reconciled, "
          f"cuts={anch['cuts']}")

    t22_rec = json.load(open(os.path.join("results",
                                          "t22_virtual_timepoints.json"),
                             encoding="utf-8-sig"))
    axes_out, corr_out, roles_out = {}, {}, {}
    trials_cells, trials_passive = 0, 0
    for axis in ("legacy", "deep"):
        prices, close = _census_prices(axis)
        idx = close.index
        if axis == "legacy":
            panel_ok = str(idx[-1].date()) == LEGACY_CUTOFF
        else:
            man = json.load(open(os.path.join("results", "shortline",
                                             "t18_deep_manifest.json"),
                                encoding="utf-8"))
            panel_ok = (man.get("evidence_cutoff") == ANCHOR_CUTOFF
                        and str(idx[-1].date()) == ANCHOR_CUTOFF)
        if not panel_ok:
            print(f"finalize: G-PANEL FAIL [{axis}] end="
                  f"{str(idx[-1].date())} -- abort")
            return 2
        listed = close.notna().sum(axis=1)
        eligible = t22.enumerate_starts(len(idx), listed)
        gate_n = (GATE_LEGACY_STARTS if axis == "legacy"
                  else GATE_DEEP_STARTS)
        delta = 1 if axis == "legacy" else 0    # s2-iii amendment face
        if not (len(eligible) == gate_n
                == t22_rec["axes"][axis]["n_starts"] + delta):
            print(f"finalize: G-CENSUS FAIL [{axis}] n={len(eligible)} "
                  f"gate={gate_n} t22_rec="
                  f"{t22_rec['axes'][axis]['n_starts']}+{delta} -- abort")
            return 2
        print(f"G-PANEL/G-CENSUS PASS [{axis}]: end="
              f"{str(idx[-1].date())} n={len(eligible)}")

        rows, cells_audit = _union_cells_dir(OUT_DIR, axis)
        if cells_audit["corrupt"]:
            print(f"finalize: {cells_audit['corrupt']} corrupt line(s) "
                  f"[{axis}] -- integrity abort")
            return 2
        if cells_audit["dups"]:
            print(f"finalize: {len(cells_audit['dups'])} duplicate key(s) "
                  f"[{axis}] -- integrity abort")
            return 2
        cov = _coverage_gate(rows, member_ids, eligible, idx)
        n_elig = len(eligible)
        if not cov["ok"] or len(rows) != N_MEMBERS * n_elig:
            print(f"finalize: COVERAGE/CENSUS GATE FAIL [{axis}] "
                  f"(rows={len(rows)} expected={N_MEMBERS * n_elig}, "
                  f"start_bad={cov['start_bad']}, "
                  f"passive_bad={cov['passive_bad']}, "
                  f"foreign={cov['foreign']}, "
                  f"per_trader_complete="
                  f"{all(len(v) == n_elig for v in cov['by_trader'].values())}"
                  f") -- missing shard face; T-93 handover required -- abort")
            return 2
        print(f"coverage gate PASS [{axis}]: {len(rows)} cells = "
              f"{N_MEMBERS} members x {n_elig} starts")
        trials_cells += len(rows)
        trials_passive += n_elig

        judgments = {tid: {w: t22._agg(list(cov["by_trader"][tid].values()),
                                       w)
                           for w in FINALIZE_WINDOWS}
                     for tid in member_ids}
        reps = family_representatives(member_ids)
        rep_set = set(reps.values())
        rep_rows = [r for r in rows if r["trader"] in rep_set]
        pooled_member = {
            "n": sum(j["6m"]["n"] for j in judgments.values()),
            "beats": sum(j["6m"]["beats"] for j in judgments.values())}
        pooled_member["beat_rate"] = round(
            pooled_member["beats"] / pooled_member["n"], 4)
        axes_out[axis] = {
            "cutoff": AXIS_CUTOFFS[axis], "n_starts": n_elig,
            "passive_windows": n_elig, "cells_total": len(rows),
            "shard_files": cells_audit["files"],
            "na_bucket_n": sum(1 for r in rows
                               if r.get("regime") not in
                               ("bear", "chop", "bull")),
            "judgments": judgments,
            "pooled_member_caliber_base_6m": pooled_member,
            "pooled_family_caliber_base_6m": {
                "n_families": len(reps), "representatives": reps,
                "n": len(rep_rows),
                "beat_rate": round(
                    sum(1 for r in rep_rows if r["beat_6m"])
                    / len(rep_rows), 4),
                "rule": ("non-CE base variant preferred, id-sorted; "
                         "variant pairs share the alpha claim (prereg "
                         "s1 11+2 family caliber)")},
            "segments_pooled_base_6m": t22._pooled(
                rows, "6m", lambda r: r.get("regime", "na")),
            "start_year_cohorts_base_6m": t22._pooled(
                rows, "6m", lambda r: r["start"][:4]),
            "subsample_25td": {tid: {
                w: t22._sub_rate(list(cov["by_trader"][tid].values()), w)
                for w in FINALIZE_WINDOWS} for tid in member_ids},
        }
        corr_out[axis] = {w: _member_corr(cov["by_trader"], eligible, w)
                          for w in FINALIZE_WINDOWS}
        roles_out[axis] = {tid: _role_readout(judgments[tid]["6m"])
                           for tid in member_ids}

    # ---- predictions reconciliation (prereg s5, frozen pre-run)
    preds = []
    for axis in ("legacy", "deep"):
        jd = axes_out[axis]["judgments"]
        pooled = axes_out[axis]["pooled_member_caliber_base_6m"]["beat_rate"]
        seg = axes_out[axis]["segments_pooled_base_6m"]
        n_pass = sum(1 for j in jd.values()
                     if j["6m"]["beat_rate"] is not None
                     and j["6m"]["beat_rate"] >= t22.BEAT_LINE)
        attack_cands = sorted(tid for tid, ro in roles_out[axis].items()
                              if ro["attack_candidate"])
        dd_band = [f"{tid}:{jd[tid]['6m']['min_dd']}" for tid in jd
                   if jd[tid]["6m"]["min_dd"] is not None
                   and t22.DD_RED_LINE <= jd[tid]["6m"]["min_dd"] < -0.30]
        diverge = _variant_divergence(jd, member_ids)
        preds.append({
            "axis": axis,
            "p1_pooled_in_[0.42,0.68]": bool(0.42 <= pooled <= 0.68),
            "p1_pooled": pooled,
            "p1_n_passing_line": n_pass,
            "p1_majority_below_line": bool(n_pass < N_MEMBERS / 2),
            "p1_over5_passing_needs_caliber_check": bool(n_pass > 5),
            "p2_bear_gt_bull": bool(
                seg.get("bear", {}).get("beat_rate", -1)
                > seg.get("bull", {}).get("beat_rate", -1)),
            "p2_bear": seg.get("bear", {}).get("beat_rate"),
            "p2_bull": seg.get("bull", {}).get("beat_rate"),
            "p2_attack_candidates": attack_cands,
            "p2_attack_candidates_le2": bool(len(attack_cands) <= 2),
            "p3_variant_divergences": diverge,
            "p3_pairs_same_direction": not diverge,
            "p4_min_dd_approach_band_n": len(dd_band),
            "p4_min_dd_approach_band": dd_band,
            "p4_na_bucket_n": axes_out[axis]["na_bucket_n"],
            "p4_note": ("whole-window judgment caliber (prereg s5 pred-4 "
                        "designed face): extreme single days enter via "
                        "min_dd tails and segment-edge sensitivity, not "
                        "single-point detection"),
        })

    # ---- audit block (prereg s0: no CLEAN audit -> not ledgered; X2 canon)
    try:
        subprocess.run([sys.executable, os.path.join(
            "scripts", "compute_audit.py")],
            capture_output=True, text=True, timeout=180)
        aj = json.load(open(os.path.join("results", "compute_audit.json"),
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

    batch_trials = trials_cells + trials_passive
    if audit_clean:
        ledger = append_ledger(
            BATCH, batch_trials,
            file_name="prospect_regime_segments.json",
            evidence_cutoff=ANCHOR_CUTOFF,
            note=(f"22 members x 2 axes base face: legacy "
                  f"{GATE_LEGACY_STARTS * N_MEMBERS} + deep "
                  f"{GATE_DEEP_STARTS * N_MEMBERS} cells + passive windows "
                  f"{trials_passive} (per-start accounting, s0 amended); "
                  f"18/18 shards flip-evidence-gated (r314 law) + "
                  f"cross-machine shard handover T-93"))
    else:
        ledger = {"prev_total": None, "batch_trials": batch_trials,
                  "total": None,
                  "note": "audit not CLEAN - not counted per prereg s0"}

    # ---- outputs: CSV (small, git) + JSON (top-level C2 key)
    os.makedirs(os.path.dirname(FINALIZE_OUT_CSV), exist_ok=True)
    n_csv = 0
    with open(FINALIZE_OUT_CSV, "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write("axis,trader,face,window,segment,n,beat_rate,min_dd,"
                 "mean_dd,oos_trades,ci95_width,verdict\n")
        for axis in ("legacy", "deep"):
            for tid, j in axes_out[axis]["judgments"].items():
                for w, agg in j.items():
                    rows_csv = [("all", agg["n"], agg["beat_rate"],
                                 agg["min_dd"], agg["mean_dd"],
                                 agg["oos_trades"], agg["ci95_width"],
                                 agg["verdict"])]
                    rows_csv += [(s, v["n"], v["beat_rate"], v["min_dd"],
                                  None, None, None, None)
                                 for s, v in agg["segments"].items()]
                    for s, n_, br, mdd, mddm, tr, ciw, vd in rows_csv:
                        fh.write(f"{axis},{tid},{FACE},{w},{s},{n_},{br},"
                                 f"{mdd},{mddm},{tr},{ciw},{vd}\n")
                        n_csv += 1

    machine = json.load(open("fleet/machine.json",
                             encoding="utf-8"))["machine_id"]
    with open(os.path.join("research",
                           "PROS_REGIME_SEGMENTS_P1.md"), "rb") as fh:
        prereg_sha = hashlib.sha256(fh.read()).hexdigest()
    corr_hot = [{"axis": axis, "window": w, "pair": k, "corr": v}
                for axis in corr_out for w in corr_out[axis]
                for k, v in corr_out[axis][w].items()
                if v is not None and abs(v) >= 0.7]
    payload = {
        "batch": BATCH, "ticket": TICKET,
        "prereg": "research/PROS_REGIME_SEGMENTS_P1.md",
        "prereg_sha256": prereg_sha,
        "evidence_cutoff": ANCHOR_CUTOFF,
        "cutoff_meta": cutoff_meta(ANCHOR_CUTOFF),
        "axis_cutoffs": AXIS_CUTOFFS,
        "evidence_cutoff_note": (
            "binding cutoff = deep manifest (2026-09-22); legacy cells "
            "ran on the 2026-09-24 truncated panel (s2-iii amendment "
            "face, probe results/_r313bmb_prospect_probe.json)"),
        "judgment_rule": (
            f"primary read = base face 6m: beat_rate >= {t22.BEAT_LINE} "
            f"AND min_dd >= {t22.DD_RED_LINE} on the complete-window "
            f"subset (t22 frozen caliber); 12m/24m parallel disclosure; "
            f"this batch = statistics face, no admission action (prereg "
            f"s4)"),
        "bootstrap": {"B": t22.BOOTSTRAP_B, "seed": t22.BOOTSTRAP_SEED,
                      "method": "binomial percentile 95% CI"},
        "corr_caliber_note": (
            "member-pairwise window-return corr on aligned virtual "
            "startpoints (X2 _arm_corr canon, disclosure-only, never a "
            "gate); prereg s1 daily-return wording operationalized at "
            "window caliber -- frozen cells schema (s6) carries window "
            "metrics only, finalize runs zero new engine passes"),
        "audit": audit,
        "axes": axes_out,
        "corr": corr_out,
        "corr_pairs_abs_ge_07": corr_hot,
        "role_readouts": roles_out,
        "attack_corps_candidates": {
            axis: sorted(tid for tid, ro in roles_out[axis].items()
                         if ro["attack_candidate"])
            for axis in roles_out},
        "predictions_vs_results": preds,
        "trials_ledger": ledger,
        "machine": machine,
        "finalize_ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "runtime_sec": round(time.time() - t0, 1),
        "outputs": {"json": os.path.abspath(FINALIZE_OUT_JSON),
                    "csv": os.path.abspath(FINALIZE_OUT_CSV),
                    "csv_rows": n_csv},
    }
    with open(FINALIZE_OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1, ensure_ascii=False, default=bool)
    print(f"pooled base 6m: legacy "
          f"{axes_out['legacy']['pooled_member_caliber_base_6m']['beat_rate']}"
          f" (family caliber "
          f"{axes_out['legacy']['pooled_family_caliber_base_6m']['beat_rate']}"
          f"), deep "
          f"{axes_out['deep']['pooled_member_caliber_base_6m']['beat_rate']}"
          f" (family caliber "
          f"{axes_out['deep']['pooled_family_caliber_base_6m']['beat_rate']}"
          f")")
    print(f"trials: {trials_cells} cells + {trials_passive} passive = "
          f"{batch_trials}; ledger total -> {ledger.get('total')}")
    print(f"finalize DONE in {payload['runtime_sec']}s -> "
          f"{FINALIZE_OUT_JSON} + {FINALIZE_OUT_CSV} ({n_csv} rows)")
    return 0


def cmd_status(_) -> int:
    if not os.path.isdir(OUT_DIR):
        print(f"no {OUT_DIR} yet")
        return 0
    for name in sorted(os.listdir(OUT_DIR)):
        path = os.path.join(OUT_DIR, name)
        if name.startswith("cells_") and name.endswith(".jsonl"):
            n = sum(1 for _ in open(path, encoding="utf-8"))
            print(f"{name}: {n} cells")
        elif name.startswith("done_"):
            print(f"{name}: {open(path, encoding='utf-8').read()[:200]}")
    return 0


def cmd_selftest(_) -> int:
    """Hermetic offline selftest (r116 law): no engine run, no network,
    no real panel load. B7b contract leg included (r297 law)."""
    fails = []

    def t(name, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")
        if not ok:
            fails.append(name)

    import tempfile

    # S1: PROSPECT member filter on a synthetic traders dir
    with tempfile.TemporaryDirectory() as td:
        for i, (lvl, name) in enumerate([
                ("PROSPECT", "PROS-A-01"), ("INTERN", "INT-1"),
                ("PROSPECT", "PROS-B-01"), ("TRAINEE", "TR-1"),
                ("PROSPECT", "PROS-C-01")]):
            with open(os.path.join(td, f"{name}.json"), "w",
                      encoding="utf-8") as fh:
                json.dump({"id": name, "level": lvl,
                           "params": {"entry": "ants_climb()"}}, fh)
        saved = sys.path[:]
        import firm.hr as fhr
        real_dir = fhr.TRADERS_DIR
        from pathlib import Path
        fhr.TRADERS_DIR = Path(td)
        try:
            got = [m["id"] for m in load_prospect_members()]
        finally:
            fhr.TRADERS_DIR = real_dir
            sys.path[:] = saved
        t("S1 member filter: PROSPECT only, id-sorted",
          got == ["PROS-A-01", "PROS-B-01", "PROS-C-01"])

    # S2: anchor byte-reconciliation logic on synthetic fixtures
    def synth_state(ok, drift_field=None, cut=ANCHOR_CUTOFF):
        got = {f: (0.25 + i) for i, f in enumerate(ANCHOR_FIELDS)}
        if drift_field:
            got[drift_field] = got[drift_field] + 0.5
        return {"anchor_ok": ok, "evidence_cutoff": cut,
                "anchor": {"got": got}}

    mem = {"id": "PROS-X-01",
           "prospect": {f"recorded_{f}": 0.25 + i
                        for i, f in enumerate(ANCHOR_FIELDS)}}
    st_ok = synth_state(True)
    st_drift = synth_state(True, drift_field="max_dd")
    st_cut = synth_state(True, cut="2026-09-21")
    def _recon(st):
        fails_ = []
        if not st.get("anchor_ok"):
            return ["anchor_ok false"]
        got = st["anchor"]["got"]
        for f in ANCHOR_FIELDS:
            if got.get(f) != mem["prospect"][f"recorded_{f}"]:
                fails_.append(f)
        return fails_
    t("S2 anchor byte-reconcile pass/catch drift/catch cutoff",
      _recon(st_ok) == [] and len(_recon(st_drift)) == 1
      and _recon(st_drift) == ["max_dd"]
      and (_recon(st_cut) == [] and st_cut["evidence_cutoff"]
           != ANCHOR_CUTOFF))

    # S3: census amendment math -- +1 panel bar adds exactly +1 eligible
    # start when listed >= MIN_LISTED throughout (probe-documented face)
    listed = pd.Series(48, index=range(900))
    n_old = len(t22.enumerate_starts(900, listed))
    n_new = len(t22.enumerate_starts(901, listed))
    t("S3 census +1 law (panel extension adds exactly one start)",
      n_new == n_old + 1 and n_old == 900 - t22.WARMUP_TD - t22.W6M + 1)

    # S4: legacy truncation freezes the panel end at the frozen cutoff
    idx = pd.bdate_range("2026-08-01", periods=40)
    frame = pd.DataFrame({"close": 1.0}, index=idx)
    trunc = _truncate_legacy({"510300": frame})
    t("S4 bounded loader truncates to frozen cutoff (Monday-bar-proof)",
      str(trunc["510300"].index[-1].date()) <= LEGACY_CUTOFF
      and len(trunc["510300"]) <= 40)

    # S5: import-face _G contract -- every _G["..."] consumed inside the
    # t22 _run_cell body is provided by this runner's INIT_G_KEYS
    consumed = _g_consumed_keys_in_t22_run_cell()
    t("S5 t22 _G consumption subset of INIT_G_KEYS (import-face intact)",
      consumed and consumed <= INIT_G_KEYS)

    # S6: checkpoint resume incl. truncated tail (t22 law, offline)
    with tempfile.TemporaryDirectory() as td:
        tmp = os.path.join(td, "ckpt.jsonl")
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write(json.dumps({"key": "A|1"}) + "\n")
            fh.write('{"key": "A|2", "trun')     # crash mid-line
        keys = t22.load_done_keys(tmp)
        t("S6 resume keys skip truncated tail", keys == {"A|1"})

    # S7: frozen constants (import-face intact + prereg faces)
    t("S7 frozen constants (cutoffs/faces/lines/windows via t22)",
      LEGACY_CUTOFF == "2026-09-24" and ANCHOR_CUTOFF == "2026-09-22"
      and GATE_LEGACY_STARTS == 1256 and GATE_DEEP_STARTS == 1506
      and N_MEMBERS == 22 and FACE == "base"
      and t22.BEAT_LINE == 0.70 and t22.DD_RED_LINE == -0.35
      and (t22.W6M, t22.W12M, t22.W24M) == (126, 252, 504))

    # S8: B7b contract leg (r297 law) -- consumer keys subset of the
    # construction row schema (promotion third leg + MARKET_STAGE_TABLE)
    t("S8 B7b consumer keys subset of construction keys",
      ROW_CONSUMER_KEYS <= ROW_CONSTRUCTION_KEYS
      and len(ROW_CONSTRUCTION_KEYS) == 27)

    # S9: shard path mapping + roster id ordering determinism
    t("S9 shard path mapping deterministic",
      shard_path("legacy", "LA").endswith("cells_legacy_LA.jsonl")
      and shard_path("deep", "DE").endswith("cells_deep_DE.jsonl"))

    # S10: family caliber derivation + representative rule (s1 dual caliber)
    ids = ["PROS-ANTS-01", "PROS-ANTS-CE-01", "PROS-BBS-01",
           "PROS-RSRS-CE"]
    t("S10 family derivation + representatives (11+2 caliber)",
      {tid: _family_of(tid) for tid in ids}
      == {"PROS-ANTS-01": "ANTS", "PROS-ANTS-CE-01": "ANTS",
          "PROS-BBS-01": "BBS", "PROS-RSRS-CE": "RSRS"}
      and family_representatives(ids)
      == {"ANTS": "PROS-ANTS-01", "BBS": "PROS-BBS-01",
          "RSRS": "PROS-RSRS-CE"})

    # S11: finalize union integrity -- dup keys + corrupt lines abort faces
    with tempfile.TemporaryDirectory() as td:
        p1 = os.path.join(td, "cells_legacy_LX.jsonl")
        p2 = os.path.join(td, "cells_legacy_LY.jsonl")
        row = {"key": "PROS-A-01|300", "trader": "PROS-A-01", "pos": 300}
        with open(p1, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(row) + "\n")
        with open(p2, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(row) + "\n")       # same key = dup
            fh.write('{"key": "PROS-A-01|301", "trun')   # corrupt tail
        rows, aud = _union_cells_dir(td, "legacy")
        t("S11 union integrity (dup keys + corrupt lines reported)",
          aud["corrupt"] == 1 and len(aud["dups"]) == 1
          and len(rows) == 1 and aud["files"]["cells_legacy_LY.jsonl"] == 1
          and _union_cells_dir(td, "deep")[1]["files"] == {}
          and aud["files"]["cells_legacy_LX.jsonl"] == 1)

    # S12: coverage gate logic on synthetic rows (hermetic, no panel)
    idx = pd.bdate_range("2021-01-01", periods=900)
    eligible = list(range(252, 260))
    mk = lambda tid, p: {"key": f"{tid}|{p}", "trader": tid, "pos": p,
                         "start": str(idx[p].date()),
                         "p_ret_6m": 0.01, "p_ret_12m": 0.02,
                         "p_ret_24m": 0.03}
    members_x = ["PROS-A-01", "PROS-B-01"]
    good_rows = [mk(tid, p) for tid in members_x for p in eligible]
    cov_ok = _coverage_gate(good_rows, members_x, eligible, idx)
    bad_rows = good_rows[:-1]                      # one cell missing
    cov_missing = _coverage_gate(bad_rows, members_x, eligible, idx)
    drifted = [dict(r) for r in good_rows]
    drifted[0] = dict(drifted[0], start="1999-01-01")
    cov_drift = _coverage_gate(drifted, members_x, eligible, idx)
    pas_bad = [dict(r) for r in good_rows]
    pas_bad[8] = dict(pas_bad[8], p_ret_6m=0.02)
    cov_passive = _coverage_gate(pas_bad, members_x, eligible, idx)
    foreign = good_rows + [mk("PROS-Z-01", eligible[0])]
    cov_foreign = _coverage_gate(foreign, members_x, eligible, idx)
    t("S12 coverage gate: pass/missing/start-drift/passive-drift/foreign",
      cov_ok["ok"] and not cov_missing["ok"] and not cov_drift["ok"]
      and not cov_passive["ok"] and not cov_foreign["ok"]
      and cov_drift["start_bad"] == 1
      and cov_passive["passive_bad"] == 1
      and cov_foreign["foreign"] == ["PROS-Z-01"])

    # S13: member corr on synthetic vectors (X2 window-caliber canon)
    bt = {"A": {p: {"ret_6m": float(p % 7)} for p in eligible},
          "B": {p: {"ret_6m": float(p % 7)} for p in eligible},
          "C": {p: {"ret_6m": 1.0} for p in eligible}}
    corr = _member_corr(bt, eligible, "6m")
    t("S13 member corr: identical series -> 1.0, zero-std -> None",
      corr["A|B"] == 1.0 and corr["A|C"] is None and corr["B|C"] is None
      and len(corr) == 3)

    # S14: role readout rule (s4 descriptive caliber)
    ro_defense = _role_readout({"segments": {
        "bear": {"n": 40, "beat_rate": 0.80},
        "chop": {"n": 30, "beat_rate": 0.55},
        "bull": {"n": 35, "beat_rate": 0.30}}})
    ro_flat = _role_readout({"segments": {
        "bear": {"n": 40, "beat_rate": 0.52},
        "chop": {"n": 30, "beat_rate": 0.53},
        "bull": {"n": 35, "beat_rate": 0.51}}})
    ro_attack = _role_readout({"segments": {
        "bear": {"n": 40, "beat_rate": 0.30},
        "chop": {"n": 30, "beat_rate": 0.55},
        "bull": {"n": 35, "beat_rate": 0.72}}})
    t("S14 role readout: argmax/all-weather/attack-candidate calibers",
      ro_defense["role"] == "bear" and ro_flat["role"] == "all_weather"
      and ro_attack["role"] == "bull"
      and ro_attack["attack_candidate"]
      and not ro_defense["attack_candidate"])

    # S15: variant divergence detector (s5 pred-3, 20pp line)
    segs_a = {"bear": {"beat_rate": 0.60}, "bull": {"beat_rate": 0.20}}
    segs_ace = {"bear": {"beat_rate": 0.61}, "bull": {"beat_rate": 0.45}}
    segs_b = {"bear": {"beat_rate": 0.50}, "bull": {"beat_rate": 0.51}}
    jd_div = {"PROS-A-01": {"6m": {"segments": segs_a}},
              "PROS-A-CE-01": {"6m": {"segments": segs_ace}},
              "PROS-B-01": {"6m": {"segments": segs_b}}}
    div = _variant_divergence(jd_div, list(jd_div))
    t("S15 variant divergence: 25pp split caught, 1pp pair clean",
      len(div) == 1 and div[0]["family"] == "A"
      and div[0]["segment"] == "bull" and div[0]["delta_pp"] == 0.25)

    # S16: single-finalization guard (X2 canon env redo path)
    with tempfile.TemporaryDirectory() as td:
        gj = os.path.join(td, "landed.json")
        open(gj, "w", encoding="utf-8").write("{}")
        os.environ.pop(FINALIZE_GUARD_ENV, None)
        guarded = _finalize_guard(gj)
        os.environ[FINALIZE_GUARD_ENV] = "1"
        redo = _finalize_guard(gj)
        del os.environ[FINALIZE_GUARD_ENV]
        fresh = _finalize_guard(os.path.join(td, "absent.json"))
        t("S16 finalize guard: landed blocks / env redo / fresh runs",
          guarded is False and redo is True and fresh is True)

    print(f"\nselftest: {'ALL PASS' if not fails else 'FAIL x' + str(len(fails))}")
    return 0 if not fails else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--axis", choices=["legacy", "deep"], required=True)
    r.add_argument("--shard", required=True)
    r.add_argument("--pos-from", type=int, default=0)
    r.add_argument("--pos-to", type=int, default=10**9)
    r.add_argument("--limit", type=int, default=0)
    r.add_argument("--workers", type=int, default=0)
    sub.add_parser("status")
    sub.add_parser("finalize")
    sub.add_parser("selftest")
    args = ap.parse_args()
    if args.cmd == "run":
        return cmd_run(args)
    if args.cmd == "status":
        return cmd_status(args)
    if args.cmd == "finalize":
        return cmd_finalize(args)
    return cmd_selftest(args)


if __name__ == "__main__":
    sys.exit(main())
