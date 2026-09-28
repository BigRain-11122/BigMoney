"""Pool dual-run reconciliation evidence harness (T-2026-09-29-116 s3
wave-1, bm-c r196).

D-20260928-03(1) structural end-state migration instrument: before any
wave-1 decision-read switch (autofill tick/claim/keepalive/harvest,
fill_ladder read side, compute_audit ready scan -> lane-merged view),
the s3 spec demands dual-run evidence -- "read both faces, assert
zero drift for 3 consecutive ticks, then flip".  This leg samples the
equivalence property ONCE PER S6 CHAIN RUN (before compute_audit's
sync_face settle -- running after it would be vacuous, the settle
heals any drift before the sample) and appends one evidence row to
this machine's jsonl lane file.

Comparison semantics = the merger itself (scripts/merge_lane_views:
load_sources fixed-order + merge_runnable_pool recipes) -- ZERO
reimplementation; the row records merged-view == shared-blob at the
sample instant.  Drift during the observation phase is DATA, not a
fault (mid-tick lane-ahead windows are lawful and self-heal at settle;
the flip gate reads the consecutive-green counter, which drift
resets).

Output: results/pool_dualrun.<machine>.jsonl (per-machine lane
pattern, D-03(2) anti-UU-treadmill; each machine appends ONLY its own
file).  Tail-capped at TAIL_KEEP rows -- this is a bounded
migration-window instrument, not a permanent ledger; the s4
disposition retires it with the shared face itself.  Rows carry
evidence_cutoff (= shared face updated_at) per the results-JSON
cutoff law.

Usage:
  python scripts/pool_dualrun_reconcile.py run       # sample + append row
  python scripts/pool_dualrun_reconcile.py status   # flip-gate read-only
  python scripts/pool_dualrun_reconcile.py selftest # hermetic fixtures

Exit codes: 0 = evidence row appended (green or drift, both honest);
2 = mechanism fault (unreadable source / merge fault / identity
contradiction) -- report honestly, never mask.  status is read-only
(exit 0 with the verdict print; gate enforcement stays a session
decision, this leg never flips a reader by itself).
"""
import argparse
import datetime as _dt
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import merge_lane_views as _mlv                    # noqa: E402
from config.lane_io import machine_id as _own_id  # noqa: E402

FACE = "runnable_pool"
TAIL_KEEP = 50          # bounded migration-window instrument
GATE_GREEN_MIN = 3       # s3 spec: 3 consecutive ticks zero-drift


def _now():
    return _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _lane_jsonl_path(results_dir):
    mid = _own_id()
    if not mid:
        raise SystemExit("pool_dualrun: machine_id unreadable "
                         "(fleet/machine.json) -- refuse (r98 identity law)")
    return os.path.join(results_dir, f"pool_dualrun.{mid}.jsonl")


def _load_rows(path):
    if not os.path.exists(path):
        return []
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def _first_divergence(a, b, path="$"):
    """First differing path (bounded probe for the drift detail field;
    not a full diff -- the flip gate only needs drift bool + a pointer)."""
    if type(a) is not type(b):
        return f"{path} (type {type(a).__name__} vs {type(b).__name__})"
    if isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a:
                return f"{path}.{k} (missing left)"
            if k not in b:
                return f"{path}.{k} (missing right)"
            d = _first_divergence(a[k], b[k], f"{path}.{k}")
            if d:
                return d
        return ""
    if isinstance(a, list):
        if len(a) != len(b):
            return f"{path} (len {len(a)} vs {len(b)})"
        for i, (x, y) in enumerate(zip(a, b)):
            d = _first_divergence(x, y, f"{path}[{i}]")
            if d:
                return d
        return ""
    return "" if a == b else f"{path} ({a!r} vs {b!r})"[:200]


def _sample(results_dir):
    """One dual-run sample: shared blob vs lane-merged view, same
    merger recipes consumers will read post-flip.  Fail-closed on any
    source fault (identity contradiction / shape surprise -> the
    caller exits 2; never record a row from a half-loaded union)."""
    sources = _mlv.load_sources(FACE, results_dir)
    if not any(lbl == "legacy" for lbl, _ in sources):
        return None        # no shared face = nothing to reconcile (skip)
    merged, _notes = _mlv.merge_face(FACE, sources)
    shared = dict(next(d for lbl, d in sources if lbl == "legacy"))
    drift = merged != shared
    row = {
        "ts": _now(),
        "machine": _own_id(),
        "sources": [lbl for lbl, _ in sources],
        "n_entries_shared": len(shared.get("entries", [])),
        "n_entries_merged": len(merged.get("entries", [])),
        "drift": drift,
        "drift_detail": _first_divergence(shared, merged) if drift else "",
        "evidence_cutoff": str(shared.get("updated_at", "")),
        "law_ref": "T-2026-09-29-116 s3 dual-run (D-20260928-03(1))",
    }
    return row


def _append_row(row, results_dir):
    path = _lane_jsonl_path(results_dir)
    rows = _load_rows(path)
    prev_green = 0
    for r in reversed(rows):
        if r.get("drift"):
            break
        prev_green += 1
    row["consecutive_green"] = 0 if row["drift"] else prev_green + 1
    rows.append(row)
    if len(rows) > TAIL_KEEP:
        rows = rows[-TAIL_KEEP:]
    tmp = path + ".tmp"
    os.makedirs(results_dir, exist_ok=True)
    with open(tmp, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(tmp, path)
    return row


def cmd_run(results_dir):
    row = _sample(results_dir)
    if row is None:
        print(f"[pool_dualrun] SKIP: no shared {FACE} face to reconcile "
              "against (lane-only bootstrap) -- no row recorded")
        return 0
    row = _append_row(row, results_dir)
    if row["drift"]:
        print(f"[pool_dualrun] DRIFT: {row['drift_detail']} -- recorded "
              f"as observation-phase data (flip-gate streak reset), "
              f"entries {row['n_entries_shared']} vs "
              f"{row['n_entries_merged']}, cutoff "
              f"{row['evidence_cutoff']}")
    else:
        print(f"[pool_dualrun] ZERO-DRIFT (merged view == shared blob, "
              f"{row['n_entries_merged']} entries, streak "
              f"{row['consecutive_green']}/{GATE_GREEN_MIN}, cutoff "
              f"{row['evidence_cutoff']})")
    return 0


def cmd_status(results_dir):
    """Read-only flip-gate verdict over ALL machine jsonl lanes visible
    in this tree (each machine records its own; a missing file means
    that machine has not adopted the leg yet -- reported honestly)."""
    import merge_lane_views as mlv
    ok, detail = True, []
    for machine in mlv.MACHINES:
        path = os.path.join(results_dir, f"pool_dualrun.{machine}.jsonl")
        rows = _load_rows(path)
        if not rows:
            ok = False
            detail.append(f"{machine}: NO EVIDENCE (leg not yet adopted "
                          "or no rows)")
            continue
        streak = 0
        for r in reversed(rows):
            if r.get("drift"):
                break
            streak += 1
        last = rows[-1]
        met = streak >= GATE_GREEN_MIN
        ok = ok and met
        detail.append(
            f"{machine}: streak {streak} (gate {GATE_GREEN_MIN}) "
            f"{'MET' if met else 'NOT-MET'}, last drift="
            f"{str(last.get('drift')).lower()}, ts={last.get('ts')}, "
            f"cutoff={last.get('evidence_cutoff')}")
    for line in detail:
        print(f"[pool_dualrun/status] {line}")
    print(f"[pool_dualrun/status] wave-1 flip gate: "
          f"{'READY (all lanes >=%d consecutive green)' % GATE_GREEN_MIN if ok else 'NOT READY'}")
    return 0


def _selftest():
    """Hermetic offline fixtures (tmp results dir; zero fleet reads via
    monkeypatched machine_id; zero network)."""
    import tempfile
    import merge_lane_views as mlv
    fails = []

    def check(name, cond):
        print(f"  [{name}] {'PASS' if cond else 'FAIL'}")
        if not cond:
            fails.append(name)

    saved_own_id = _own_id
    tmpd = tempfile.mkdtemp(prefix="pool_dualrun_selftest_")
    try:
        import pool_dualrun_reconcile as h   # self import for monkeypatch

        # fixture A: settled state -- shared == union -> ZERO-DRIFT row
        base = {"version": 1, "updated_at": "2026-09-29 03:00:00",
                "entries": [{"id": "E1", "status": "ready",
                             "shards": [{"key": "s0", "status": "ready",
                                         "owner": "bm-a",
                                         "owner_since":
                                         "2026-09-29 02:00:00"}]}]}
        with open(os.path.join(tmpd, f"{FACE}.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(base, fh)
        lane = dict(base)
        lane["lane_machine"] = "bm-a"
        with open(os.path.join(tmpd, f"{FACE}.bm-a.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(lane, fh)
        h.__dict__["_own_id"] = lambda: "bm-a"
        globals()["_own_id"] = lambda: "bm-a"
        row_a = h._sample(tmpd)
        check("A1 settled zero-drift",
              row_a is not None and row_a["drift"] is False)
        h._append_row(row_a, tmpd)
        p = os.path.join(tmpd, "pool_dualrun.bm-a.jsonl")
        check("A2 row recorded with cutoff",
              _load_rows(p)[0].get("evidence_cutoff")
              == "2026-09-29 03:00:00")
        check("A3 streak counts from 1",
              _load_rows(p)[0].get("consecutive_green") == 1)

        # fixture B: lane-ahead (own lane holds a fresher owner_since
        # the shared face lacks) -> DRIFT row, honest exit path, streak
        # resets to 0
        lane2 = json.loads(json.dumps(base))
        lane2["entries"][0]["shards"][0]["owner_since"] = \
            "2026-09-29 03:30:00"
        lane2["lane_machine"] = "bm-a"
        with open(os.path.join(tmpd, f"{FACE}.bm-a.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(lane2, fh)
        row_b = h._sample(tmpd)
        check("B1 lane-ahead drift detected",
              row_b is not None and row_b["drift"] is True)
        check("B2 drift detail non-empty",
              bool(row_b.get("drift_detail")))
        h._append_row(row_b, tmpd)
        rows_b = _load_rows(p)
        check("B3 drift resets streak",
              rows_b[-1].get("consecutive_green") == 0)

        # fixture B4: green after drift rebuilds streak from 1
        with open(os.path.join(tmpd, f"{FACE}.bm-a.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(json.loads(json.dumps(lane)), fh)
        # re-settle shared to the union by hand (simulating a settle)
        settled = json.loads(json.dumps(base))
        settled["entries"][0]["shards"][0]["owner_since"] = \
            "2026-09-29 03:30:00"
        with open(os.path.join(tmpd, f"{FACE}.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(settled, fh)
        row_c = h._sample(tmpd)
        check("B4 re-settled green",
              row_c is not None and row_c["drift"] is False)
        h._append_row(row_c, tmpd)
        check("B5 streak rebuilds from 1",
              _load_rows(p)[-1].get("consecutive_green") == 1)

        # fixture C: identity contradiction -> fail-closed exit 2 face
        bad = json.loads(json.dumps(base))
        bad["lane_machine"] = "bm-b"        # filename says bm-a
        with open(os.path.join(tmpd, f"{FACE}.bm-a.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(bad, fh)
        try:
            h._sample(tmpd)
            check("C1 identity contradiction fail-closed", False)
        except SystemExit:
            check("C1 identity contradiction fail-closed", True)

        # fixture D: tail cap
        for i in range(TAIL_KEEP + 5):
            r = dict(row_c)
            r["ts"] = f"2026-09-29 04:{i:02d}:00"
            h._append_row(r, tmpd)
        check("D1 tail capped at keep-window",
              len(_load_rows(p)) == TAIL_KEEP)
    finally:
        globals()["_own_id"] = saved_own_id
        h = sys.modules.get("pool_dualrun_reconcile")
        if h is not None:
            h._own_id = saved_own_id
        import shutil
        shutil.rmtree(tmpd, ignore_errors=True)
    print(f"pool_dualrun selftest: "
          f"{len(fails) == 0 and 'ALL PASS' or 'FAIL ' + str(fails)}")
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "status", "selftest"])
    args = ap.parse_args()
    if args.cmd == "selftest":
        return _selftest()
    from config import PATHS
    results_dir = PATHS.results_dir
    if args.cmd == "status":
        return cmd_status(results_dir)
    try:
        return cmd_run(results_dir)
    except SystemExit as ex:
        print(f"[pool_dualrun] MECHANISM FAULT (fail-closed): {ex} "
              "-- no row recorded from a half-loaded union")
        return 2
    except Exception as ex:
        print(f"[pool_dualrun] MECHANISM FAULT: {ex} -- no row recorded")
        return 2


if __name__ == "__main__":
    sys.exit(main())
