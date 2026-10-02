# r606 bm-b: FUND-QUALITY-P1 pool registration (4 entries) into bm-b lane file.
# Value-family r598 precedent schema verbatim-mirror with quality deltas.
# Idempotent: skips ids already present. Bytes-safe: CRLF preserved (r530/r600).
import json, sys

LANE = "results/runnable_pool.bm-b.json"
raw = open(LANE, "rb").read()
pool = json.loads(raw.decode("utf-8"))
existing = {e.get("id") for e in pool["entries"]}

TICKET = ("T-2026-10-03-153-P1 (O-20261002-2115 fundamental quality NEW FAMILY "
          "second piece, monthly cross-sectional Top-20 highest statutory-anchored "
          "roe_q; prereg FROZEN bm-b r606; ignition gates ALL GREEN r606: TRANSFER "
          "T-152 PASS 7/7 sha256 ef35c733..acf9735 + probe leg1-4 GREEN (amended "
          "dual gate median 52>=50 p10 26>=20, dup period_end 0) + D6 ADMIT "
          "max|corr|=0.2407 + banned_direction_gate ADMIT rc0 + selftest ALL PASS)")
PREREG = ("research/FUND-QUALITY-P1.md FROZEN (judged cells QUALITY-ROE x faces "
          "x1/x2 + nulls 2000 rng([20510000,k]) + sens 500 rng([20510500,k]); "
          "evidence_cutoff 2026-09-22 D2 lockbox; t0=2001-09-03 frozen; exit-axis "
          "hold-through dual-channel default-stack disable + law-A census block "
          "20%; workers 32 BelowNormal per O-2158 width law; seeds band-extent-"
          "checked vs furnace [20333000,20445400) r601 probe leg4)")
HOST_GATES = [{"kind": "dir_nonempty", "path": "Money02/data/cache/p1c_stock",
               "pattern": "*.npy"}]
WORKERS = {"workers": 32, "priority": "BelowNormal"}


def entry(eid, args, shard_key, note):
    return {
        "id": eid,
        "ticket_ref": TICKET,
        "prereg_ref": PREREG,
        "runner": "scripts/fund_quality_p1.py",
        "runner_args": args,
        "shards": [{
            "key": shard_key,
            "status": "ready",
            "checkpoint": "results/fund_quality_p1/ JSONL checkpoint resume (done-key skip)",
            "note": note,
        }],
        "workers_plan": WORKERS,
        "status": "ready",
        "host_gates": HOST_GATES,
    }


new = [
    entry("FUND-QUALITY-P1-CELL-QUALITYROE-X1",
          ["run", "--cell", "QUALITY-ROE", "--face", "x1"],
          "fund-quality-p1-cell-qualityroe-x1-0of1",
          "401 census starts (G-CENSUS bit-exact) full-window judged cell, "
          "t0=2001-09-03 pre-t0 flat, hold-through exit axis, checkpoint done-key "
          "skip; cont face; x1 cost 13.041bp/edge"),
    entry("FUND-QUALITY-P1-CELL-QUALITYROE-X2",
          ["run", "--cell", "QUALITY-ROE", "--face", "x2"],
          "fund-quality-p1-cell-qualityroe-x2-0of1",
          "401 census starts (G-CENSUS bit-exact) full-window judged cell, "
          "t0=2001-09-03 pre-t0 flat, hold-through exit axis, checkpoint done-key "
          "skip; cont face; x2 cost-stress 26.082bp/edge"),
    entry("FUND-QUALITY-P1-NULLS",
          ["run", "--nulls"],
          "fund-quality-p1-nulls-0of1",
          "K=2000 same-mask random-selection nulls (headline QUALITY-ROE mask, "
          "eq weights, N=20), rng([20510000,k]); feeds skill_line_v2 null_pool"),
    entry("FUND-QUALITY-P1-SENS",
          ["run", "--sensitivity"],
          "fund-quality-p1-sens-0of1",
          "K=500 space-filling draws over N{10,15,20}/roe_cap{50,100} rule=roe "
          "fixed, rng([20510500,k]); descriptive face only, no verdict"),
]

added = []
for e in new:
    if e["id"] in existing:
        print("SKIP (already present):", e["id"])
        continue
    pool["entries"].append(e)
    added.append(e["id"])

if added:
    # preserve incumbent format: utf-8 no BOM, indent=2, CRLF (r530/r600)
    out = json.dumps(pool, indent=2, ensure_ascii=False)
    open(LANE, "wb").write(out.replace("\n", "\r\n").encode("utf-8"))
    print("ADDED:", added)
    print("lane entries total:", len(pool["entries"]))
else:
    print("NO-OP (all present)")
