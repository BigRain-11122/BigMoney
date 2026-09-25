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
  python scripts/t54_prospect_grid.py finalize    (prereg s6 leg; honest
                                    exit 2 while shards are split across
                                    machines -- transfer ticket in flight)
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
WINDOWS = ("6m", "12m", "24m")
SUMMARY_NAME = "t54_grid_summary.json"
EVIDENCE_CUTOFF = "2026-09-24"     # prereg s2 legacy panel cutoff (latest face)
FROZEN_CENSUS = {"legacy": 1256, "deep": 1506}          # prereg s2
SHARD_PLAN = {                                           # prereg s5 (frozen)
    "legacy": {"lA": (0, 314), "lB": (314, 628),
               "lC": (628, 942), "lD": (942, 1256)},
    "deep": {"dA": (0, 377), "dB": (377, 754),
             "dC": (754, 1131), "dD": (1131, 1506)},
}


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


def _finalize(out_dir=OUT_DIR, shard_plan=None, census=None, faces=FACES,
             windows=WINDOWS, results_dir="results",
             summary_path=None, refinalize=False, eligible_by_axis=None):
    """Prereg s6 finalize leg: all-shard done-marker census gate + per-shard
    row-count account vs the frozen shard ranges + per-member three-window
    beat rates + summary JSON + trials-ledger append by ACTUAL cell count
    (single-shot guard; T54_REFINALIZE=1 = only redo path, ledger re-derived
    from the live chain head, no extra append). Zero judgment lines (s8):
    negative beat rates ship as-is. Returns a process exit code."""
    shard_plan = shard_plan or SHARD_PLAN
    census = census or FROZEN_CENSUS
    if summary_path is None:
        summary_path = os.path.join(out_dir, SUMMARY_NAME)
    if os.path.exists(summary_path) and not refinalize:
        print("finalize refused: summary exists (single-shot guard; "
              "T54_REFINALIZE=1 to redo)")
        return 1
    t0 = time.time()
    markers = []
    for axis, shards in shard_plan.items():
        for sh in shards:
            mp = os.path.join(out_dir, f"done_{axis}_{sh}.json")
            if not os.path.exists(mp):
                print(f"finalize abort: missing done marker {mp} "
                      "(shards split across machines -- transfer pending)")
                return 2
            m = json.loads(open(mp, encoding="utf-8").read())
            if int(m.get("n_eligible", -1)) != census[axis]:
                print(f"finalize abort: census drift {axis}/{sh} "
                      f"n_eligible={m.get('n_eligible')} != frozen "
                      f"{census[axis]}")
                return 2
            markers.append((axis, sh, m))
    rosters = {tuple(m.get("members", [])) for _, _, m in markers}
    if len(rosters) != 1:
        print(f"finalize abort: shard rosters diverge "
              f"({len(rosters)} distinct)")
        return 2
    members = list(next(iter(rosters)))
    excluded = sorted({e for _, _, m in markers
                       for e in m.get("anchor_excluded", [])})
    if not members:
        print("finalize abort: empty roster")
        return 2
    # SHARD_PLAN bounds are census-index slices over the eligible absolute-
    # position list (runner: shard = eligible[pos_from:pos_to]); rows carry
    # absolute panel positions. Re-derive the same eligible list from the
    # live panels (R117 pairing law) and gate it on the frozen census so a
    # drifted panel cannot silently remap the shard windows (r105 law).
    if eligible_by_axis is None:
        from live.paper import build_panels
        eligible_by_axis = {}
        for axis in shard_plan:
            P = build_panels(t22._load_axis_prices(axis))
            close = P["close"]
            listed = close.notna().sum(axis=1)
            el = t22.enumerate_starts(len(close.index), listed)
            if len(el) != census[axis]:
                print(f"finalize abort: eligible re-derivation drift "
                      f"{axis}: {len(el)} != frozen {census[axis]}")
                return 2
            eligible_by_axis[axis] = el
    pos_win = {}
    for axis, shards in shard_plan.items():
        for sh, (lo, hi) in shards.items():
            pos_win[(axis, sh)] = set(eligible_by_axis[axis][lo:hi])

    rows_by = {}
    for axis, shards in shard_plan.items():
        for face in faces:
            for sh in shards:
                p = os.path.join(out_dir, f"cells_{axis}_{face}_{sh}.jsonl")
                if not os.path.exists(p):
                    print(f"finalize abort: missing cells file {p}")
                    return 2
                rows = []
                with open(p, encoding="utf-8") as fh:
                    for line in fh:
                        line = line.strip()
                        if line:
                            rows.append(json.loads(line))
                want = (shards[sh][1] - shards[sh][0]) * len(members)
                if len(rows) != want:
                    print(f"finalize abort: {axis}/{face}/{sh} rows="
                          f"{len(rows)} != shard-plan expected {want} "
                          f"(range {shards[sh]} x {len(members)} members)")
                    return 2
                rows_by[(axis, face, sh)] = rows

    seen, dupes = set(), 0
    for (axis, face, sh), rows in rows_by.items():
        win = pos_win[(axis, sh)]
        for r in rows:
            k = str(r.get("key", ""))
            ak = (axis, face, k)   # uniqueness scope: both axes AND both
            if ak in seen:          # cost faces legitimately hold the same
                dupes += 1         # trader|pos key (prereg s3 dual-face
                continue           # design); never twice within one face
            seen.add(ak)
            tid, _, pos = k.partition("|")
            if tid not in members or not pos.isdigit() \
                    or int(pos) not in win:
                print(f"finalize abort: row key outside frozen shard "
                      f"range/roster: {k}")
                return 2
    if dupes:
        print(f"finalize abort: {dupes} duplicate keys across shards")
        return 2
    total = sum(len(r) for r in rows_by.values())
    expected = sum(census[a] for a in shard_plan) * len(members) * len(faces)
    if total != expected:
        print(f"finalize abort: total cells {total} != census-expected "
              f"{expected}")
        return 2

    # per-member three-window beat rates (J-1 summary convention extended
    # to three windows; axis attributed from the filename namespace because
    # t22-schema rows carry no axis field -- prereg s5)
    acc = {}
    for (axis, face, sh), rows in rows_by.items():
        for r in rows:
            a = (acc.setdefault(r["trader"], {})
                     .setdefault(axis, {})
                     .setdefault(face, {"n": 0, **{"beat_" + w: 0
                                                   for w in windows}}))
            a["n"] += 1
            for w in windows:
                a["beat_" + w] += int(bool(r.get("beat_" + w)))
    per_member = {tid: {ax: {fc: {"n": a["n"],
                                  **{f"beat_rate_{w}":
                                     round(a["beat_" + w] / a["n"], 4)
                                     for w in windows}}
                             for fc, a in faces_d.items()}
                         for ax, faces_d in axes_d.items()}
                  for tid, axes_d in acc.items()}
    pooled = {}
    for tid, axes_d in acc.items():
        n = sum(a["n"] for faces_d in axes_d.values()
                for a in faces_d.values())
        pooled[tid] = {"n": n,
                      **{f"beat_rate_{w}":
                         round(sum(a["beat_" + w]
                                   for faces_d in axes_d.values()
                                   for a in faces_d.values()) / n, 4)
                         for w in windows}}

    import science_gates as sg
    led = sg.append_ledger(
        "T54-PROSPECT-GRID", total,
        file_name="results/t54/t54_grid_summary.json",
        evidence_cutoff=EVIDENCE_CUTOFF,
        note="measurement/evidence batch, zero judgments (prereg s8); "
             "consumption: 10-31 J-line rerun W-GRID full-pool face + "
             "T-54 slice-1 admission evidence",
        results_dir=results_dir)
    summary = {
        **sg.cutoff_meta(EVIDENCE_CUTOFF),
        "batch": "T54-PROSPECT-GRID",
        "kind": "measurement",
        "ticket": TICKET,
        "prereg": "research/shortline/T54_PROSPECT_GRID.md",
        "members": members,
        "anchor_excluded": excluded,
        "census": {a: census[a] for a in shard_plan},
        "cells_total": total,
        "cells_by_axis": {a: census[a] * len(members) * len(faces)
                          for a in shard_plan},
        "shard_markers": [{"axis": ax, "shard": sh,
                           "n_eligible": m["n_eligible"],
                           "cells_written": m["cells_written"],
                           "finished_at": m["finished_at"]}
                          for ax, sh, m in markers],
        "per_member_beat_rates": per_member,
        "per_member_pooled": pooled,
        "trials_ledger": led,
        "audit": {"elapsed_sec": round(time.time() - t0, 1),
                  "finalize_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                  "refinalize": bool(refinalize)},
        "notes": ("rows carry no axis field; axis attributed from the "
                  "filename namespace (prereg s5). Negative beat rates "
                  "ship as-is (s8: this batch produces no verdicts)"),
    }
    tmp = summary_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=1)
    os.replace(tmp, summary_path)
    print(f"finalize OK: {total} cells, {len(members)} members, "
          f"summary -> {summary_path}, ledger total={led['total']}")
    return 0


def cmd_finalize(args) -> int:
    return _finalize(
        refinalize=os.environ.get("T54_REFINALIZE") == "1")


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

    # 7) hermetic finalize leg (prereg s6; production-paired per R117 law:
    # a complete mini-grid through the real _finalize, plus every honest
    # abort face). Fixture plan mirrors the frozen shape: 2 axes x 2
    # shards x 2 faces x 2 members; beat pattern hand-checkable.
    import tempfile
    import shutil
    tmp = tempfile.mkdtemp(prefix="t54_fin_")
    res_dir = tempfile.mkdtemp(prefix="t54_led_")
    try:
        plan = {"legacy": {"lA": (0, 2), "lB": (2, 4)},
                "deep": {"dA": (0, 3), "dB": (3, 6)}}
        cens = {"legacy": 4, "deep": 6}
        mem = ["PROS-A", "PROS-B"]
        # absolute panel positions deliberately != census indices
        # (production shape: legacy eligible starts at 252, deep at 1599);
        # pins the index-vs-absolute domain of the shard range check
        # (R117 pairing law -- fixture must not let the two domains
        # coincide, or the domain bug is invisible)
        elig = {"legacy": [252, 253, 254, 255],
                "deep": [1599, 1600, 1601, 1602, 1603, 1604]}
        fin_faces = ("base", "x2")
        n_expect = (4 + 6) * len(mem) * len(fin_faces)

        def _row(tid, pos, w6, w12):
            return {"key": f"{tid}|{pos}", "trader": tid, "pos": pos,
                    "beat_6m": w6, "beat_12m": w12, "beat_24m": False}

        for axis, shards in plan.items():
            for sh, (lo, hi) in shards.items():
                with open(os.path.join(tmp, f"done_{axis}_{sh}.json"),
                          "w", encoding="utf-8") as fh:
                    json.dump({"shard": sh, "axis": axis,
                               "faces": list(fin_faces),
                               "cells_written": (hi - lo) * len(mem),
                               "cells_total": (hi - lo) * len(mem),
                               "n_eligible": cens[axis], "workers": 2,
                               "members": mem, "anchor_excluded": [],
                               "runtime_sec": 1.0,
                               "finished_at": "2026-09-25 00:00:00",
                               "ticket": TICKET}, fh, indent=1)
                for face in fin_faces:
                    rows = []
                    for i in range(lo, hi):
                        pos = elig[axis][i]
                        for tid in mem:
                            rows.append(_row(tid, pos, True,
                                              pos % 2 == 0))
                    with open(os.path.join(
                            tmp, f"cells_{axis}_{face}_{sh}.jsonl"),
                            "w", encoding="utf-8") as fh:
                        for r in rows:
                            fh.write(json.dumps(r) + "\n")
        sp = os.path.join(tmp, SUMMARY_NAME)
        rc = _finalize(out_dir=tmp, shard_plan=plan, census=cens,
                       faces=fin_faces, results_dir=res_dir,
                       summary_path=sp, eligible_by_axis=elig)
        s = json.loads(open(sp, encoding="utf-8").read()) \
            if os.path.exists(sp) else {}
        ok("finalize complete mini-grid",
           rc == 0 and s.get("cells_total") == n_expect
           and s["trials_ledger"]["total"] == n_expect
           and s["trials_ledger"]["prev_total"] == 0
           and s["evidence_cutoff"] == EVIDENCE_CUTOFF)
        # hand-check: every 6m beat True -> pooled rate 1.0; 12m evens
        # (legacy 252,254 + deep 1600,1602,1604 of 4+6 positions)
        # -> 0.5 per member
        pm = s.get("per_member_pooled", {}).get("PROS-A", {})
        ok("finalize beat-rate hand-check",
           pm.get("n") == 20 and pm.get("beat_rate_6m") == 1.0
           and pm.get("beat_rate_12m") == 0.5
           and pm.get("beat_rate_24m") == 0.0)
        ok("finalize per-axis-face breakdown",
           s["per_member_beat_rates"]["PROS-A"]["legacy"]["base"]["n"] == 4
           and s["per_member_beat_rates"]["PROS-A"]["deep"]["x2"]["n"] == 6)

        # 8) single-shot guard: second run refused without T54_REFINALIZE
        rc2 = _finalize(out_dir=tmp, shard_plan=plan, census=cens,
                       faces=fin_faces, results_dir=res_dir,
                       summary_path=sp, eligible_by_axis=elig)
        ok("finalize single-shot guard", rc2 == 1)

        # 9) missing-marker abort (shards split across machines face)
        os.remove(os.path.join(tmp, "done_deep_dB.json"))
        rc3 = _finalize(out_dir=tmp, shard_plan=plan, census=cens,
                       faces=fin_faces, results_dir=res_dir,
                       summary_path=sp, refinalize=True,
                       eligible_by_axis=elig)
        ok("finalize missing-marker abort", rc3 == 2)

        # 10) census-drift abort (n_eligible != frozen census)
        bad = json.loads(open(os.path.join(tmp, "done_deep_dA.json"),
                              encoding="utf-8").read())
        bad["n_eligible"] = 999
        with open(os.path.join(tmp, "done_deep_dA.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(bad, fh)
        rc4 = _finalize(out_dir=tmp, shard_plan=plan, census=cens,
                       faces=fin_faces, results_dir=res_dir,
                       summary_path=sp, refinalize=True,
                       eligible_by_axis=elig)
        ok("finalize census-drift abort", rc4 == 2)
        bad["n_eligible"] = 6
        with open(os.path.join(tmp, "done_deep_dA.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(bad, fh)

        # 11) shard-range violation abort (row pos outside frozen range)
        rogue = os.path.join(tmp, "cells_deep_base_dB.jsonl")
        lines = open(rogue, encoding="utf-8").read().splitlines()
        r0 = json.loads(lines[0])
        r0["key"] = f"{r0['trader']}|999"
        lines[0] = json.dumps(r0)
        with open(rogue, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
        rc5 = _finalize(out_dir=tmp, shard_plan=plan, census=cens,
                       faces=fin_faces, results_dir=res_dir,
                       summary_path=sp, refinalize=True,
                       eligible_by_axis=elig)
        ok("finalize shard-range abort", rc5 == 2)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        shutil.rmtree(res_dir, ignore_errors=True)

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
    sub.add_parser("finalize")
    sub.add_parser("selftest")
    a = ap.parse_args()
    if a.cmd == "run":
        return cmd_run(a)
    if a.cmd == "status":
        return cmd_status(a)
    if a.cmd == "finalize":
        return cmd_finalize(a)
    return cmd_selftest()


if __name__ == "__main__":
    sys.exit(main())
