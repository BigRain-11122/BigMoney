"""r424 bm-c: enroll MASS-TRIAL-W2-JUDGE 4 shards into runnable_pool.json.

Raw-text surgical insert (r509 pool byte-edit law: NEVER re-serialize the
pool; flat-0-key + CRLF daemon writer shape). Single-purpose: append four
entries before the closing bracket, validate, assert. Zero science faces
touched -- enrollment only (long-burn law O-20260924-2100: the burn itself
is pool-face, ignited by daemons/saturation engine, never inline)."""
import json
import os
import sys

POOL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "results", "runnable_pool.json")

ENTERED_AT = "2026-10-03 18:38:00"

PREREG = ("research/MASS_TRIAL_W2_PREREG.md sec.9.1 FROZEN 2026-10-03 r423 "
          "commit 4796399f3 (806 stage-1 survivors -> |corr|>=0.999 leg-L "
          "collapse 1 cluster (rep W2-18013 <- W2-18025) -> N_judge=805; "
          "candidates sha16 1a8751ed16a9c641; grid = p5c FROZEN_CENSUS "
          "dual-leg L 1253/1127/875 + D 3104/2978/2726 x windows "
          "{126,252,504} x cost {x1, x2=CostPatch(2.0)} x regime segs "
          "bear/bull/chop+na x dual nulls B=2000/P=2000 seed [20285200,i]; "
          "G1v2/G2 via science_gates shared lib; family PBO CSCV 11 modules; "
          "seed mass_trial_w2_judge=20285200 registered r423 R250 one-step; "
          "N_eff cross-wave ledger-head read never reset; E[FP]=0.05*N_judge)")

TICKET = ("T-2026-10-03-158 s3 full-judgment batch (O-20261002-2115 sec.1 "
          "line-3 CEO order wave-2 + O-2026-09-27-2250 standing law; ticket "
          "claimed bm-c r422; s3 judge face FROZEN bm-c r423 commit 4796399f3 "
          "prereg sec.9.1 R99 freeze-before-burn; judge-prep landed "
          "N_judge=805 same round detached 1131s, manifest PASS)")

GATES = ("in-runner fail-closed exit 2: w2_judge_state.json required "
         "(committed r424 d34a7d071), candidates sha anchor 1a8751ed16a9c641, "
         "dual-leg census == p5c FROZEN_CENSUS abort, t18 deep manifest PASS, "
         "per-cell jsonl checkpoint cross-kill resume; finalize single-shot "
         "ledger guard + MASS_TRIAL_W2_JUDGE_REFINALIZE byte-stable redo "
         "override (w1 r259 pattern)")

WP = {
    "workers": ("worker_cap() pool BelowNormal (16-core box: 12 observed; "
                "RAM-flip-gated)"),
    "priority": "BelowNormal",
    "note": ("~202 judged cells/shard (805/4 = 202/201/201/201) x ~10s/cell "
             "w1-real-fire measured (dual-leg dual-cost full curves + "
             "sliced window grids + dual nulls) -> ~34min serial/shard, "
             "~3-6min on 12 workers; worker RAM ~500-700MB (ctx_L+ctx_D "
             "panels); NO waiting gate -- prep artifact committed (r424), "
             "claim-time host gate = t18 deep cache 48 parquets (prep "
             "verified locally); runner lacks worker-side pool_claims "
             "handshake (w1 r351 precedent, zero-touch frozen face) -- "
             "done-flip duty = burner-side session adopts checkpoint rows "
             "(805 cells total) and lands shard+entry done per r488/r489 "
             "two-layer law; idempotent resume (done-set cell_id skip) "
             "makes stale-owner takeover safe; deterministic runner = "
             "duplicate rows byte-identical, finalize dedups by cell_id"),
}


def _j(s):
    return json.dumps(s, ensure_ascii=False)


def entry_text(i, ncells):
    args = ",\r\n".join(
        '    "%s"' % a for a in
        ["judge", "--wave", "2", "--shard", str(i), "--shards", "4"])
    wp = (
        "   \"workers_plan\": {\r\n"
        f"    \"workers\": {_j(WP['workers'])},\r\n"
        f"    \"priority\": {_j(WP['priority'])},\r\n"
        f"    \"note\": {_j(WP['note'])}\r\n"
        "   },\r\n"
    )
    return (
        '  {\r\n'
        f'   "id": "MASS-TRIAL-W2-JUDGE-SHARD-{i}",\r\n'
        '   "host_gates": [\r\n'
        '    {\r\n'
        '     "kind": "dir_nonempty",\r\n'
        '     "path": "Money02/data/cache/t18_deep_panel/ohlcv",\r\n'
        '     "pattern": "*.parquet"\r\n'
        '    }\r\n'
        '   ],\r\n'
        f'   "ticket_ref": "{TICKET}",\r\n'
        f'   "prereg_ref": "{PREREG}",\r\n'
        '   "runner": "scripts/mass_trial_w1.py",\r\n'
        f'   "runner_args": [\r\n{args}\r\n   ],\r\n'
        '   "lane_owner": null,\r\n'
        '   "priority": 1,\r\n'
        '   "status": "ready",\r\n'
        f'   "entered_at": "{ENTERED_AT}",\r\n'
        f'{wp}'
        f'   "data_gates": "{GATES}",\r\n'
        '   "shards": [\r\n'
        '    {\r\n'
        f'     "key": "w2-judge-{i}of4",\r\n'
        '     "status": "ready",\r\n'
        f'     "checkpoint": "results/mass_trial/w2_judge_shard_{i}of4.jsonl'
        ' (row-level cell_id done-set resume)",\r\n'
        f'     "note": "cells i%4=={i} of sorted 805 collapsed survivors'
        f' ({ncells} cells); multi-machine shard-claim legal (ticket lock'
        ' holds science face only); stale-owner takeover >20min per fleet'
        ' law; wave-level finalize = separate round work'
        ' (judge-finalize --wave 2 after all 4 shards done + 805-cell'
        ' completeness probe)"\r\n'
        '    }\r\n'
        '   ],\r\n'
        '   "worker_class": "self-contained"\r\n'
        '  }'
    )


def main():
    raw = open(POOL, "rb").read()
    if b"MASS-TRIAL-W2-JUDGE" in raw:
        print("REFUSE: MASS-TRIAL-W2-JUDGE already present (double-enroll)")
        return 2
    pool = json.loads(raw.decode("utf-8"))
    n0 = len(pool["entries"])
    closer = b'  }\r\n ]\r\n}'
    trail = b""
    if raw.endswith(closer + b"\r\n"):
        trail = b"\r\n"
    elif not raw.endswith(closer):
        print("REFUSE: unexpected pool tail bytes")
        print(repr(raw[-40:]))
        return 2
    # cells: sorted kept 805 -> i%4
    counts = [sum(1 for i in range(805) if i % 4 == s) for s in range(4)]
    assert counts == [202, 201, 201, 201], counts
    assert sum(counts) == 805
    parts = [entry_text(i, counts[i]) for i in range(4)]
    block = (",\r\n".join(parts) + "\r\n").encode("utf-8")
    new = raw[: -len(closer) - len(trail)] + b'  },\r\n' + block \
        + b' ]\r\n}' + trail
    pool2 = json.loads(new.decode("utf-8"))
    n2 = len(pool2["entries"])
    ids = [e["id"] for e in pool2["entries"][-4:]]
    want = [f"MASS-TRIAL-W2-JUDGE-SHARD-{i}" for i in range(4)]
    assert n2 == n0 + 4, (n0, n2)
    assert ids == want, ids
    for e in pool2["entries"][-4:]:
        assert e["status"] == "ready" and e["lane_owner"] is None
        assert e["priority"] == 1 and e["workers_plan"] and e["shards"][0][
            "status"] == "ready"
        assert e["runner_args"] == ["judge", "--wave", "2", "--shard",
                                     e["id"][-1], "--shards", "4"]
        assert e["host_gates"][0]["path"] == \
            "Money02/data/cache/t18_deep_panel/ohlcv"
    with open(POOL, "wb") as fh:
        fh.write(new)
    print(f"ENROLL OK: {n0} -> {n2} entries; ids {want}; "
          f"cells/shard {counts} (sum 805); tail-surgical insert landed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
