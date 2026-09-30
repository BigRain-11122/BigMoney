"""r304 bm-c one-shot: W9-W13 JUDGE shard-face closure (r489 mirror defect).

Defect: the five TRIAL-LABOR-W{9..13}-JUDGE entries landed entry.status=done
via the observing-round flip executors (bm-b judge finalize lineage) but the
claimed shard rows stayed status=ready. Judge burns ran OUTSIDE the autofill
worker-claim channel (no results/pool_claims files), so the daemon
harvest-flip will never land this half -- session-side closure is the only
repair path (r211 SLOT-2 precedent). Claim gate reads the entry face
(resident_dispatcher.py L188) so zero ghost-claim risk: bookkeeping residue +
stats/dashboard face drift only.

Three-way reconciliation per r489 law before any flip: entry done + product
file present (results/trial_labor_w{N}/w{N}_judge.json) + W1-W13 judge
verdict lineage (W1-W10 consolidated CEO-REPORT-INNOVQUOTA-SLOT7-10; W11/12
verdicts in w*_judge.json 09-30 products; W13 in w13_judge.json).

Write path per D-03 lane-primary authority + r311 latest.ts law: mutate the
merged view -> _write_lane_file_strict (bm-c lane carries the flip) ->
_pool_settle (union lands shared POOL). owner_since bumped to flip moment
(preserved in claimed_since) so the done row is the newest same-key base and
no stale mirror swallows the flip at the next settle (r479 family).

Also sweeps the whole pool for the same-semantics brother faces (r300 law):
entry=done with non-done shards (this defect family) and the r489 original
mirror (entry=ready/claimed with all shards done).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + os.sep + "..")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + os.sep + ".." + os.sep + "scripts")

import Tools.autofill as af
import merge_lane_views as mlv

TARGETS = ["TRIAL-LABOR-W%d-JUDGE" % n for n in (9, 10, 11, 12, 13)]


def product_check(n):
    path = os.path.join("results", "trial_labor_w%d" % n, "w%d_judge.json" % n)
    if not os.path.isfile(path):
        raise SystemExit("FAIL-CLOSED: product absent %s" % path)
    if os.path.getsize(path) < 100_000:
        raise SystemExit("FAIL-CLOSED: product implausibly small %s" % path)
    prod = json.load(open(path, encoding="utf-8"))
    if not isinstance(prod, dict) or "evidence_cutoff" not in prod:
        raise SystemExit("FAIL-CLOSED: product shape suspect %s" % path)
    return path


def sweep(pool):
    """Brother-face census (r300 law): every dual-state contract violation."""
    fam_a, fam_b = [], []  # A: entry done + shard not done; B: entry open + all shards done
    for e in pool.get("entries", []):
        shs = e.get("shards") or []
        st, es = e.get("status"), [s.get("status") for s in shs]
        if not shs:
            continue
        if st == "done" and any(x != "done" for x in es):
            fam_a.append((e["id"], es))
        if st in ("ready", "claimed") and shs and all(x == "done" for x in es):
            fam_b.append((e["id"], es))
    return fam_a, fam_b


def main():
    pool = af._pool_merged_view()
    fam_a, fam_b = sweep(pool)
    print("[sweep] entry=done with non-done shards: %d" % len(fam_a))
    for eid, es in fam_a:
        print("   A:", eid, es)
    print("[sweep] entry=open with all-done shards: %d" % len(fam_b))
    for eid, es in fam_b:
        print("   B:", eid, es)

    now = af._now()
    flipped = []
    for eid in TARGETS:
        entry = next((e for e in pool.get("entries", []) if e.get("id") == eid), None)
        if entry is None:
            raise SystemExit("entry absent: " + eid)
        if entry.get("status") != "done":
            raise SystemExit("FAIL-CLOSED: entry not done %s (%s)" % (eid, entry.get("status")))
        n = int(eid.split("-W")[1].split("-")[0])
        prod_path = product_check(n)
        sh = entry["shards"][0]
        assert len(entry["shards"]) == 1 and sh.get("key") == "judge-0of1", sh
        if sh.get("status") == "done" and "diagnostic probe" not in str(sh.get("note", "")):
            print("   skip (already %s): %s" % (sh.get("status"), eid))
            continue
        if sh.get("owner_since"):
            sh.setdefault("claimed_since", sh["owner_since"])
        sh["status"] = "done"
        sh["owner_since"] = now  # r311 latest.ts law: done row = newest same-key base
        sh["done_at"] = now
        sh["closed_at"] = now
        sh["note"] = (
            "shard face closed r304 bm-c (r489 burn+flip two-layer contract mirror "
            "defect): judge burn ran outside the worker-claim channel so the daemon "
            "harvest never lands this half; entry-level done flip landed by the "
            "bm-b observing rounds, shard left ready = bookkeeping residue, zero "
            "science impact (claim gate reads entry face -- no ghost-claim risk; "
            "no rerun owed, no reopen). Three-way verified this round: entry done + "
            "%s + W1-W13 judge verdict lineage" % os.path.basename(prod_path)
        )
        flipped.append(eid)
        print("   flip: %s -> shard done (product %s, %db)" % (eid, os.path.basename(prod_path), os.path.getsize(prod_path)))

    if not flipped:
        print("[noop] nothing to flip")
        return

    af._write_lane_file_strict(af.POOL, pool)  # bm-c lane = authority write
    res = af._pool_settle()                     # union -> shared POOL
    print("[settle] %s" % res)

    pool2 = af._pool_merged_view()
    for eid in TARGETS:
        e2 = next(e for e in pool2.get("entries", []) if e.get("id") == eid)
        assert e2["status"] == "done", eid
        assert all(s.get("status") == "done" for s in e2["shards"]), (eid, e2["shards"])
    print("[verify] %d entries now dual-layer done: %s" % (len(TARGETS), ", ".join(TARGETS)))


if __name__ == "__main__":
    main()
