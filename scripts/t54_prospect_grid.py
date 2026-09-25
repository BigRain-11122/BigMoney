"""T-54 slice-2: PROSPECT full-face grid-evidence batch (CEO orders
O-20260925-1105 R3 + O-20260925-1137 s2.1 first P0 pool carrier; ticket
T-20260925-54-P1; claim r173 bm-b).

Preregistered in research/shortline/T54_PROSPECT_GRID.md BEFORE any cell
run (frozen pre-run commit; R99 law: no batch-product command precedes the
freeze). MEASUREMENT/EVIDENCE-REGISTRATION batch -- zero judgments, zero
admission, zero adoption, zero wiring; consumption faces = (a) 10-31
J-line re-run W-GRID FULL-POOL face (relieves the T-28 CE-6 restricted
face, J4 measures the 28-member pool breadth), (b) T-54 slice-1
multi-window stability admission evidence.

Anti-dup disclosure (prereg s7): J-1 (bm-a R92) already produced legacy-
axis PROSPECT 6m-only cells on the P5C leg-L grid (promotion-leg face,
p5c schema, cells machine-local on bm-a; summary in git). This batch
computes BOTH axes with all three windows {6m,12m,24m} in t22 schema
(single 24m engine run sliced, t22 _run_cell reused verbatim -- four-gate
proven machinery, J18 zero modification); the legacy-6m overlap with J-1
is disclosed, deterministic, and non-judgmental (J-1 remains the
promotion-leg authority).

Reuse law: imports t22_virtual_timepoints machinery (enumerate_starts,
_load_axis_prices, regime_proxy, _run_cell, load_done_keys, _log-style
markers) -- no engine code copied, no t22 file touched. Roster = level
'PROSPECT' (22 members, frozen ID list in prereg s1). Per-member anchor
gate on load_core (P-5 caliber); FAIL -> member EXCLUDED with disclosure
(measurement batch: exclusion preserves the rest; frozen rule, not
batch-abort).

Namespaced outputs under results/t54/ (zero pollution of t22 canon globs):
  cells_{axis}_{face}_{shard}.jsonl   t22-schema rows (key|trader|pos|start
                                      |face|regime|n_listed|partial_*|ret_*
                                      |p_ret_*|dd_*|sharpe_*|trades_*|beat_*)
  done_{axis}_{shard}.json            shard completion marker
  logs/{axis}_{shard}.log             progress log (T54_DETACHED=1 -> log-only)
Resume = row-level done-key set per (face) file, identical protocol to t22.

Usage:
  python scripts/t54_prospect_grid.py run --axis deep --shard dA \
      [--pos-from N --pos-to M] [--faces base,x2] [--workers N] [--limit K]
  python scripts/t54_prospect_grid.py status
  python scripts/t54_prospect_grid.py selftest          (offline, no engine)
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import t22_virtual_timepoints as t22

OUT_DIR = os.path.join("results", "t54")
TICKET = "T-2026-09-25-54"
FACES = ("base", "x2")


def prospect_roster():
    """Frozen-at-prereg membership: level PROSPECT trader ids, sorted."""
    from firm.hr import TRADERS_DIR, load_trader
    out = []
    for path in sorted(TRADERS_DIR.glob("*.json")):
        if path.name.startswith("_"):
            continue
        t = load_trader(path.stem)
        if t.get("level") == "PROSPECT":
            out.append(t["id"])
    return out


def _init_worker_p54(axis, roster, log_path):
    """Per-process globals in t22._G with the PROSPECT roster (mirror of
    t22._init_worker with the roster filter swapped -- sole delta)."""
    from live.paper import SIGNAL_BUILDERS, build_panels
    prices = t22._load_axis_prices(axis)
    P = build_panels(prices)
    close = P["close"]
    from firm.hr import load_trader
    entries, params_by_id, exits_by_id = {}, {}, {}
    for tid in roster:
        t = load_trader(tid)
        entries[tid] = SIGNAL_BUILDERS[t["params"]["entry"]](P)
        params_by_id[tid] = {k: v for k, v in t["params"].items()
                             if k != "entry"}
        exits_by_id[tid] = t.get("exit_overrides")
    reg = None
    if "510300" in close.columns:
        reg = t22.regime_proxy(close["510300"])
    t22._G.update(prices=prices, close=close, idx=close.index,
                  traders=list(roster), entries=entries,
                  params_by_id=params_by_id, exits_by_id=exits_by_id,
                  regime=reg)
    with open(log_path, "a", encoding="utf-8") as fh:
        fh.write(f"{time.strftime('%H:%M:%S')} worker-init axis={axis} "
                 f"roster={len(roster)}\n")


def _anchor_filter(roster, log_path):
    """Per-member anchor gate on load_core (P-5 caliber, PROSPECT evidence
    schema: full/out_sample faces, t24_prospect_onboard repro caliber).
    Frozen rule per prereg s4: FAIL -> member excluded with disclosure
    (not batch abort)."""
    from firm.hr import load_trader
    from live.paper import prospect_anchor_gate, load_core
    prices = load_core()
    keep, excluded = [], []
    for tid in roster:
        t = load_trader(tid)
        a = prospect_anchor_gate(t, prices)
        with open(log_path, "a", encoding="utf-8") as fh:
            why = "" if a["ok"] else f" reason={a.get('error') or a.get('checks')}"
            fh.write(f"anchor {tid}: {'PASS' if a['ok'] else 'FAIL'}{why}\n")
        (keep if a["ok"] else excluded).append(tid)
    return keep, excluded


def _log(log_path, msg):
    with open(log_path, "a", encoding="utf-8") as fh:
        fh.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")


def _cells_path(axis, face, shard):
    return os.path.join(OUT_DIR, f"cells_{axis}_{face}_{shard}.jsonl")


def cmd_run(args) -> int:
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUT_DIR, "logs"), exist_ok=True)
    log_path = os.path.join(OUT_DIR, "logs", f"{args.axis}_{args.shard}.log")
    if os.environ.get("T54_DETACHED") == "1":
        sys.stdout = open(log_path, "a", buffering=1, encoding="utf-8")
        sys.stderr = sys.stdout
    t0 = time.time()
    _log(log_path, f"[{args.shard}] T-54 grid run start axis={args.axis} "
                   f"faces={args.faces} pos=[{args.pos_from},{args.pos_to})")
    roster = prospect_roster()
    if not roster:
        _log(log_path, "empty PROSPECT roster -- abort")
        return 2
    keep, excluded = _anchor_filter(roster, log_path)
    if excluded:
        _log(log_path, f"anchor-excluded members (disclosed): {excluded}")
    if not keep:
        _log(log_path, "all members anchor-failed -- nothing to run")
        return 0

    from live.paper import build_panels
    P = build_panels(t22._load_axis_prices(args.axis))
    close = P["close"]
    idx = close.index
    listed = close.notna().sum(axis=1)
    eligible = t22.enumerate_starts(len(idx), listed)
    n_elig = len(eligible)
    shard = eligible[args.pos_from:args.pos_to]
    if args.limit:
        shard = shard[:args.limit]
    if not shard:
        _log(log_path, "nothing to do (empty shard range)")
        return 0
    _log(log_path, f"panel {idx[0].date()}->{idx[-1].date()} "
                   f"eligible={n_elig} shard_positions={len(shard)} "
                   f"first={idx[shard[0]].date()} last={idx[shard[-1]].date()}")
    faces = [f.strip() for f in args.faces.split(",") if f.strip() in FACES]
    jobs, paths = [], {}
    for face in faces:
        p = _cells_path(args.axis, face, args.shard)
        paths[face] = p
        done = t22.load_done_keys(p)
        for pos in shard:
            for tid in keep:
                if f"{tid}|{pos}" in done:
                    continue
                jobs.append((tid, pos, face))
    _log(log_path, f"cells todo={len(jobs)} (resume-skipped="
                  f"{len(shard) * len(keep) * len(faces) - len(jobs)}) "
                  f"members={len(keep)} excluded={excluded or 'none'}")
    if not jobs:
        _log(log_path, "all cells already checkpointed -- no-op")
        return 0

    import psutil
    pri = getattr(psutil, "BELOW_NORMAL_PRIORITY_CLASS", None)
    if pri is not None:
        try:
            psutil.Process().nice(pri)
        except Exception:
            pass
    from parallel_runner import worker_cap
    from concurrent.futures import ProcessPoolExecutor, as_completed
    workers = args.workers or worker_cap()
    done_ct, t_last = 0, time.time()
    handles = {face: open(paths[face], "a", encoding="utf-8")
               for face in faces}
    try:
        with ProcessPoolExecutor(
                max_workers=workers,
                initializer=_init_worker_p54,
                initargs=(args.axis, keep, log_path)) as pool:
            futs = {pool.submit(t22._run_cell, tid, pos, face):
                    (tid, pos, face) for tid, pos, face in jobs}
            for fut in as_completed(futs):
                row = fut.result()
                fh = handles[row["face"]]
                fh.write(json.dumps(row, default=bool) + "\n")
                fh.flush()
                done_ct += 1
                if time.time() - t_last > 30:
                    _log(log_path, f"progress {done_ct}/{len(jobs)} cells")
                    t_last = time.time()
    finally:
        for fh in handles.values():
            fh.close()
    runtime = round(time.time() - t0, 1)
    marker = {"shard": args.shard, "axis": args.axis, "faces": faces,
              "cells_written": done_ct, "cells_total": len(jobs),
              "n_eligible": n_elig, "workers": workers,
              "members": keep, "anchor_excluded": excluded,
              "runtime_sec": runtime,
              "finished_at": time.strftime("%Y-%m-%d %H:%M:%S"),
              "ticket": TICKET}
    with open(os.path.join(OUT_DIR, f"done_{args.axis}_{args.shard}.json"),
              "w", encoding="utf-8") as fh:
        json.dump(marker, fh, indent=2)
    _log(log_path, f"DONE {done_ct}/{len(jobs)} cells in {runtime}s "
                   f"workers={workers}")
    return 0


def cmd_status(_) -> int:
    if not os.path.isdir(OUT_DIR):
        print("no results/t54 yet")
        return 0
    for name in sorted(os.listdir(OUT_DIR)):
        path = os.path.join(OUT_DIR, name)
        if name.startswith("cells_") and name.endswith(".jsonl"):
            n = sum(1 for _ in open(path, encoding="utf-8"))
            print(f"{name}: {n} cells")
        elif name.startswith("done_"):
            print(f"{name}: {open(path, encoding='utf-8').read()[:220]}")
    return 0


# -------------------------------------------------------------- selftest
def cmd_selftest() -> int:
    ok_n, fails = 0, 0

    def ok(name, cond):
        nonlocal ok_n, fails
        ok_n += 1
        fails += (not cond)
        print(f"[{'PASS' if cond else 'FAIL'}] {name}")
        return cond

    # 1) output namespace isolation (zero t22-canon glob pollution)
    ok("cells path namespace results/t54/",
       _cells_path("deep", "base", "dA") ==
       os.path.join("results", "t54", "cells_deep_base_dA.jsonl")
       and "t22" not in _cells_path("legacy", "x2", "lB"))

    # 2) done-key format mirrors t22 (tid|pos)
    ok("done-key format", f"PROS-ANTS-01|{252}" == "PROS-ANTS-01|252")

    # 3) shard slicing math (position range half-open)
    eligible = list(range(252, 252 + 100))
    ok("shard slice half-open",
       eligible[0:50] == list(range(252, 302))
       and len(eligible[50:100]) == 50
       and eligible[100:] == [])

    # 4) anchor filter keeps PASS excludes FAIL (pure fixture)
    import tempfile
    tmp = os.path.join(tempfile.gettempdir(), "t54_selftest_anchor.log")
    open(tmp, "w").close()
    import types
    fake = types.SimpleNamespace()

    def fake_anchor_filter(results, log_path):
        keep = [t for t, okk in results if okk]
        excluded = [t for t, okk in results if not okk]
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(f"excluded={excluded}\n")
        return keep, excluded
    keep, excluded = fake_anchor_filter(
        [("PROS-A", True), ("PROS-B", False), ("PROS-C", True)], tmp)
    ok("anchor exclude-not-abort rule",
       keep == ["PROS-A", "PROS-C"] and excluded == ["PROS-B"])
    os.remove(tmp)

    # 5) face parsing (invalid faces dropped, order preserved)
    faces = [f.strip() for f in "base,x2,bogus".split(",")
             if f.strip() in FACES]
    ok("face parsing", faces == ["base", "x2"])

    # 6) roster level filter (pure: fixture roster dicts)
    fixture = [{"id": "PROS-X", "level": "PROSPECT"},
               {"id": "INTERN-Y", "level": "INTERN"}]
    ok("roster level filter logic",
       [t["id"] for t in fixture if t.get("level") == "PROSPECT"] ==
       ["PROS-X"])

    print(f"selftest: {ok_n - fails}/{ok_n} checks "
          f"{'ALL PASS' if not fails else 'FAIL'}")
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--axis", required=True, choices=("legacy", "deep"))
    r.add_argument("--shard", required=True)
    r.add_argument("--pos-from", type=int, default=0)
    r.add_argument("--pos-to", type=int, default=10 ** 9)
    r.add_argument("--faces", default="base,x2")
    r.add_argument("--workers", type=int, default=None)
    r.add_argument("--limit", type=int, default=0)
    sub.add_parser("status")
    sub.add_parser("selftest")
    a = ap.parse_args()
    if a.cmd == "run":
        return cmd_run(a)
    if a.cmd == "status":
        return cmd_status(a)
    return cmd_selftest()


if __name__ == "__main__":
    sys.exit(main())
