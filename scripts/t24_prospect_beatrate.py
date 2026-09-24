"""T-24 slice (c): PROSPECT virtual-timepoint beat-rate cells (T-26 J-1).

Measurement leg feeding promotion-gate leg 3 (t24_prospect_promotion.py):
P-5/P-5B frozen caliber beat_rate_6m >= 0.70 over the T-22 leg-L virtual
timepoint grid, extended to the PROSPECT members (T-26
fleet/EXPANSION_ACCEPTANCE.md J-1 first-job designation; grid semantics
frozen by research/shortline/P5C_VIRTUAL_TIMEPOINT.md s2/s3 -- same
census, same warmup, same windows; zero new judgment lines, PROSPECT
cells are report-only evidence for the promotion evaluator).

Reuse law (no-duplicate): imports the p5c runner's frozen primitives
(_load_leg census-gated panel, _cell_worker pool cell, _init_worker
BelowNormal initializer, _passive_worker). PASSIVE 6m returns are REUSED
from the existing leg-L checkpoint (sha-verified at T-22 finalize r90) --
no passive recompute; same-prereg-same-grid no-rerun law honored. Only
PROSPECT (trader x start x face) cells are computed.

Output (consumer schema, t24_prospect_promotion._beat_stats): face is
read from the FILENAME ("x2" in name -> x2 face, else base):
  results/t22/cells_prospect_base.jsonl  {"trader","p","start","face":
        "base","ret_6m","passive_6m","beat_6m"}
  results/t22/cells_prospect_x2.jsonl    same, face "x2" (CostPatch(2.0)
        inside _cell_worker; disclosed-only face per P-5 caliber)
Resume: output files double as checkpoints (done set keyed
trader|p|face; corrupt tail tolerated -> recompute; final compaction
rewrites deduped so the evaluator's row counts stay exact).

Gates (abort before any engine run):
  G1 patch self-test (live.paper.self_test_patches, P-5 precedent)
  G2 panel census == FROZEN_CENSUS["L"] (r105 grid-drift law)
  G3 6m start count == 1253 (frozen probe re-derivation)
  G4 passive coverage: every start has a passive 6m ret (reuse or
     compute-missing, never fabricate)
Ledger: one measurement append at successful end = cells computed this
invocation (delta; killed+resumed runs sum to total, never double-count).
"""
import argparse
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import PATHS
from firm.hr import TRADERS_DIR, load_trader
from live.paper import SIGNAL_BUILDERS, self_test_patches
from parallel_runner import worker_cap
from p5c_virtual_timepoint import (FROZEN_CENSUS, LEG_L_FLOOR, MIN_LISTED,
                                   WARMUP_TD, WINDOWS, CKPT_DIR,
                                   EVIDENCE_CUTOFF_GRID, _cell_worker,
                                   _init_worker, _load_leg,
                                   _load_registry_events, _passive_worker)
from science_gates import append_ledger

T22_DIR = os.path.join(PATHS.results_dir, "t22")
OUT_BASE = os.path.join(T22_DIR, "cells_prospect_base.jsonl")
OUT_X2 = os.path.join(T22_DIR, "cells_prospect_x2.jsonl")
SUMMARY = os.path.join(T22_DIR, "prospect_beatrate.json")
ORDER_REF = "O-20260924-2100 (T-36 pool J-1) / T-26 EXPANSION_ACCEPTANCE J-1"
TICKET = "T-2026-09-24-24"


def _prospect_members():
    """PROSPECT roster, mirror of p5c slice-o1600 enumeration."""
    out, skipped = [], []
    for path in sorted(TRADERS_DIR.glob("*.json")):
        if path.name.startswith("_"):
            continue
        t = load_trader(path.stem)
        if t.get("level") != "PROSPECT":
            continue
        if t["params"]["entry"] not in SIGNAL_BUILDERS:
            skipped.append(t["id"])
            continue
        out.append(t)
    return out, skipped


def _legL_starts(idx, listed):
    """Frozen leg-L 6m start grid (probe convention; use_ml=True)."""
    n = len(idx)
    return [p for p in range(n)
            if idx[p] >= LEG_L_FLOOR and p >= WARMUP_TD
            and p <= n - 1 - WINDOWS["6m"]
            and listed.iloc[p] >= MIN_LISTED]


def _census_gate(cen, n_starts):
    """G2+G3: grid drift abort (r105 law: live panel must reproduce the
    frozen probe counts, else the batch is void before any engine run)."""
    if cen != FROZEN_CENSUS["L"]:
        print(f"BEAT-GATE FAIL: census {cen} != frozen {FROZEN_CENSUS['L']}")
        return False
    if n_starts != FROZEN_CENSUS["L"]["6m"]:
        print(f"BEAT-GATE FAIL: 6m starts {n_starts} != "
              f"{FROZEN_CENSUS['L']['6m']}")
        return False
    return True


def _passive_map(starts, close, idx):
    """G4: passive 6m ret per start, REUSED from the leg-L checkpoint
    (bm-b 16,289 cells, sha-verified at T-22 finalize); missing starts
    computed via the p5c primitive (never fabricated)."""
    import glob
    pmap = {}
    for path in glob.glob(os.path.join(CKPT_DIR, "legL", "*.jsonl")):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if r.get("face") != "passive":
                    continue
                ret = (r.get("windows", {}).get("6m", {}) or {}).get("ret")
                if ret is not None:
                    pmap[int(r["p"])] = float(ret)
    missing = [p for p in starts if p not in pmap]
    if missing:
        print(f"passive reuse: {len(pmap)} from checkpoint, "
              f"computing {len(missing)} missing via p5c primitive")
        state = {"close": close, "idx": idx}
        _init_worker(state)
        for p in missing:
            r = _passive_worker(p)
            pmap[p] = float(r["windows"]["6m"]["ret"])
    return pmap, len(missing)


def _key(tid, p, face):
    """Internal resume key; on-disk rows carry 'base' for the x1 face
    (consumer schema reads face from the filename, not the row)."""
    f = "x1" if face == "base" else face
    return f"{tid}|{p}|{f}"


def _load_done(path):
    """Resume set from one output file; corrupt tail tolerated."""
    done = set()
    if not os.path.exists(path):
        return done, 0
    n = 0
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            done.add(_key(r["trader"], r["p"], r.get("face", "base")))
            n += 1
    return done, n


def _append_rows(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")


def _compact(path):
    """Final dedupe (keep last per cell) so consumer row counts stay
    exact across kill/resume cycles."""
    if not os.path.exists(path):
        return 0
    best = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            best[_key(r["trader"], r["p"], r.get("face", "base"))] = r
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        for r in best.values():
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(tmp, path)
    return len(best)


def _beat_row(tid, p, face, cell, pmap):
    ret = float(cell["windows"]["6m"]["ret"])
    pas = float(pmap[p])
    return {"trader": tid, "p": int(p),
            "start": cell.get("start"), "face": face,
            "ret_6m": ret, "passive_6m": pas,
            "beat_6m": bool(ret > pas)}


def cmd_run(shard, shards, workers, limit):
    t0 = time.time()
    print(f"=== T-24 PROSPECT beat-rate cells (shard {shard}/{shards}) ===")
    if not self_test_patches():
        print("BEAT-GATE FAIL: patch self-test")
        return 2
    prices, P, idx, listed, cen = _load_leg("L")
    starts = _legL_starts(idx, listed)
    if not _census_gate(cen, len(starts)):
        return 2
    print(f"panel {idx[0].date()} -> {idx[-1].date()} | {len(idx)} td | "
          f"census {cen} == frozen (PASS) | starts {len(starts)}")

    members, skipped = _prospect_members()
    print(f"PROSPECT pool {len(members)} (skipped {len(skipped)}: "
          f"entry not in SIGNAL_BUILDERS)")
    if not members:
        print("no eligible PROSPECT members -- nothing to do")
        return 0

    pmap, n_missing = _passive_map(starts, P["close"], idx)
    if any(p not in pmap for p in starts):
        print("BEAT-GATE FAIL: passive coverage incomplete")
        return 2

    entry, params, ovr = {}, {}, {}
    for t in members:
        entry[t["id"]] = SIGNAL_BUILDERS[t["params"]["entry"]](P)
        params[t["id"]] = {k: v for k, v in t["params"].items() if k != "entry"}
        ovr[t["id"]] = t.get("exit_overrides") or {}
    state = {"prices": prices, "close": P["close"], "idx": idx,
             "params": params, "ovr": ovr, "entry": entry,
             "events": _load_registry_events()}

    done_base, _ = _load_done(OUT_BASE)
    done_x2, _ = _load_done(OUT_X2)
    jobs = []
    for p in starts:
        for t in members:
            for face in ("x1", "x2"):
                cid = f"{t['id']}|{p}|{face}"
                if face == "x1" and cid in done_base:
                    continue
                if face == "x2" and cid in done_x2:
                    continue
                jobs.append((cid, face, (t["id"], p, face)))
    chunk = (len(jobs) + shards - 1) // shards
    jobs = jobs[shard * chunk:(shard + 1) * chunk]
    if limit:
        jobs = jobs[:limit]
    print(f"jobs to run: {len(jobs)} (workers={workers or worker_cap()})")
    if not jobs:
        n_b, n_x = _compact(OUT_BASE), _compact(OUT_X2)
        print(f"nothing to do; compacted base={n_b} x2={n_x} rows")
        return 0

    n_done = {"x1": 0, "x2": 0}
    buf = {"x1": [], "x2": []}
    t_pool = time.time()
    with ProcessPoolExecutor(max_workers=workers or worker_cap(),
                             initializer=_init_worker, initargs=(state,)) as pool:
        futs = {pool.submit(_cell_worker, *args): (cid, face)
                for cid, face, args in jobs}
        for fut in futs:
            cid, face = futs[fut]
            cell = fut.result()
            if "error" in cell:
                print(f"cell error {cid}: {cell['error']}")
                continue
            out_face = "base" if face == "x1" else "x2"
            parts = cid.split("|")
            tid, p = parts[0], int(parts[1])
            buf[face].append(_beat_row(tid, p, out_face, cell, pmap))
            n_done[face] += 1
            total = n_done["x1"] + n_done["x2"]
            if total % 200 == 0:
                if buf["x1"]:
                    _append_rows(OUT_BASE, buf["x1"])
                if buf["x2"]:
                    _append_rows(OUT_X2, buf["x2"])
                buf = {"x1": [], "x2": []}
                print(f"  [pool] {total}/{len(jobs)} cells "
                      f"({time.time()-t_pool:.0f}s)")
    if buf["x1"]:
        _append_rows(OUT_BASE, buf["x1"])
    if buf["x2"]:
        _append_rows(OUT_X2, buf["x2"])

    n_b, n_x = _compact(OUT_BASE), _compact(OUT_X2)
    n_cells = n_done["x1"] + n_done["x2"]
    runtime = time.time() - t0
    print(f"done: {n_cells} cells this run; compacted base={n_b} "
          f"x2={n_x} rows; runtime {runtime:.1f}s")

    # summary + ledger (delta = cells computed THIS invocation)
    rates = {}
    for path, face in ((OUT_BASE, "base"), (OUT_X2, "x2")):
        acc = {}
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                a = acc.setdefault(r["trader"], {"n": 0, "beat": 0})
                a["n"] += 1
                if r["beat_6m"]:
                    a["beat"] += 1
        for tid, a in acc.items():
            d = rates.setdefault(tid, {})
            if a["n"]:
                d[face] = {"beat_rate_6m": round(a["beat"] / a["n"], 4),
                           "n_timepoints": a["n"]}
    out = {"order": ORDER_REF, "ticket": TICKET,
           "evidence_cutoff": EVIDENCE_CUTOFF_GRID,
           "census": {"frozen": FROZEN_CENSUS["L"], "gate": "PASS"},
           "n_members": len(members), "skipped": skipped,
           "passive_reuse": {"from_checkpoint": len(starts) - n_missing,
                             "computed_missing": n_missing},
           "cells_this_run": n_cells,
           "rows_after_compact": {"base": n_b, "x2": n_x},
           "per_member_beat_rates": rates,
           "runtime_s": round(runtime, 1)}
    os.makedirs(T22_DIR, exist_ok=True)
    with open(SUMMARY, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    append_ledger("T24_PROSPECT_BEATRATE", n_cells,
                  file_name="t22/prospect_beatrate.json",
                  note=f"PROSPECT leg-L virtual-timepoint beat cells "
                       f"({len(members)} members x {len(starts)} starts "
                       f"x x1/x2, P-5 caliber beat_6m; passive reused from "
                       f"leg-L checkpoint; delta=this-invocation cells; "
                       f"T-26 J-1 via T-36 pool)",
                  evidence_cutoff=EVIDENCE_CUTOFF_GRID)
    print(f"summary -> {SUMMARY}; ledger +{n_cells}")
    return 0


def cmd_status():
    for path in (OUT_BASE, OUT_X2):
        if not os.path.exists(path):
            print(f"{os.path.basename(path)}: absent")
            continue
        _, n = _load_done(path)
        print(f"{os.path.basename(path)}: {n} rows")
    if os.path.exists(SUMMARY):
        with open(SUMMARY, encoding="utf-8") as fh:
            s = json.load(fh)
        print(f"summary: cells_this_run={s['cells_this_run']} "
              f"members={s['n_members']}")


def selftest():
    import tempfile
    ok_all = True

    def ok(name, cond):
        nonlocal ok_all
        ok_all &= bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")

    print("T-24 beat-rate selftest:")
    # S1 beat arithmetic: strict > (P-5 caliber), boundary equal -> False
    ok("S1 beat arithmetic strict->", _beat_row("T", 3, "base",
        {"windows": {"6m": {"ret": 0.05}}, "start": "d"}, {3: 0.03})
        ["beat_6m"] is True
        and _beat_row("T", 3, "base", {"windows": {"6m": {"ret": 0.03}},
        "start": "d"}, {3: 0.03})["beat_6m"] is False)
    # S2 resume done-set + corrupt tail tolerated
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "cells_prospect_base.jsonl")
        _append_rows(p, [{"trader": "A", "p": 1, "face": "base",
                          "beat_6m": True}])
        with open(p, "a", encoding="utf-8") as fh:
            fh.write('{"trader": "A", "p": 2, "fac\n')   # corrupt tail
        done, n = _load_done(p)
        ok("S2 resume set + corrupt tail tolerated",
           done == {_key("A", 1, "base")} and n == 1)
        # S3 compaction dedupes keep-last
        _append_rows(p, [{"trader": "A", "p": 1, "face": "base",
                          "beat_6m": False}])
        n_after = _compact(p)
        rows = [json.loads(l) for l in open(p, encoding="utf-8")]
        ok("S3 compaction dedupe keep-last",
           n_after == 1 and rows[0]["beat_6m"] is False)
    # S4 passive map from fixture checkpoint line (reuse path)
    with tempfile.TemporaryDirectory() as tmp:
        ck = os.path.join(tmp, "shard_0of1.jsonl")
        with open(ck, "w", encoding="utf-8") as fh:
            fh.write(json.dumps({"face": "passive", "p": 7,
                                 "windows": {"6m": {"ret": 0.11}}}) + "\n")
            fh.write(json.dumps({"face": "x1", "p": 7,
                                 "windows": {"6m": {"ret": 0.2}}}) + "\n")
        global CKPT_DIR
        orig = CKPT_DIR
        CKPT_DIR = tmp
        try:
            # _passive_map globs CKPT_DIR/legL/*.jsonl
            os.makedirs(os.path.join(tmp, "legL"), exist_ok=True)
            os.replace(ck, os.path.join(tmp, "legL", "shard_0of1.jsonl"))
            pm, nmiss = _passive_map([7], None, None)
            ok("S4 passive reuse from checkpoint", pm == {7: 0.11}
               and nmiss == 0)
        finally:
            CKPT_DIR = orig
    # S5 census gate: mismatch aborts
    ok("S5 census gate abort",
       _census_gate({"6m": 1, "12m": 1, "24m": 1}, 1) is False
       and _census_gate(FROZEN_CENSUS["L"], FROZEN_CENSUS["L"]["6m"]) is True
       and _census_gate(FROZEN_CENSUS["L"], 999) is False)
    # S6 start-grid boundary: independent re-derivation via searchsorted
    import pandas as pd
    idx = pd.date_range("2019-01-02", periods=700, freq="B")
    listed = pd.Series([48] * 700, index=idx)
    st = _legL_starts(idx, listed)
    floor_pos = int(idx.searchsorted(LEG_L_FLOOR))
    expected = list(range(max(WARMUP_TD, floor_pos), 700 - WINDOWS["6m"]))
    ok("S6 leg-L start grid boundary (searchsorted re-derive)",
       st == expected and len(st) > 0)
    print("SELFTEST", "ALL PASS" if ok_all else "FAIL")
    return 0 if ok_all else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--shard", type=int, default=0)
    r.add_argument("--shards", type=int, default=1)
    r.add_argument("--workers", type=int, default=None)
    r.add_argument("--limit", type=int, default=None)
    sub.add_parser("status")
    sub.add_parser("selftest")
    a = ap.parse_args()
    if a.cmd == "run":
        sys.exit(cmd_run(a.shard, a.shards, a.workers, a.limit))
    if a.cmd == "status":
        cmd_status()
        sys.exit(0)
    sys.exit(selftest())


if __name__ == "__main__":
    main()
