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
  python scripts/prospect_regime_segments.py selftest      (offline)
"""
import argparse
import glob
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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
    sub.add_parser("selftest")
    args = ap.parse_args()
    if args.cmd == "run":
        return cmd_run(args)
    if args.cmd == "status":
        return cmd_status(args)
    return cmd_selftest(args)


if __name__ == "__main__":
    sys.exit(main())
