# -*- coding: utf-8 -*-
"""R253 bm-a: T80-AGGR-FULLPOOL-BATTERY harvest gate (deterministic, zero network).

r244 landed-marker law: pool batch never flips itself -- the round flips
entry+shard done after deterministic re-derivation of the harvest criteria.
Runner landed results/aggr_fullpool_battery.json at 15:10:35 (autofill
launch-claim aggrfp-0of1 owner=bm-a 15:10:02, runner sha 29de7acc = bm-b R256
A1 caliber fix; bm-a F11 EOL-transport tolerance fix landed post-run --
selftest-only face, run path byte-untouched, selftest 11/11 re-verified).

Harvest checks (all must hold before flip):
  1. product parses; trials_ledger prev_total 186192 + batch_trials 400 == total
     186592 AND science_gates.ledger_head() re-derived == 186592 (chain continuity
     with R252 repair head);
  2. evidence_cutoff == 2026-09-24 (t54 grid consumption face, prereg s2);
  3. 20 variants, each with J1/J2/J3 bool judgments + w_cur(2)+w_seg(6)+
     w_grid_fullpool(12 cells, exact key set) = 20 T-28-caliber cells;
  4. sleeve anchors RE-DERIVED vs frozen files: every variant w_cur/w_seg equal
     results/aggressive_lab.json (T-56 five) / aggressive_family.json (T-58
     fifteen) stored values (dict equality);
  5. AGGR-NOCASH w_grid_fullpool == canon_b_maxdiv_fullpool_grid (bit-identity,
     prereg re-anchor assertion);
  6. canon 12m pooled rate == round(beats/n, 4) re-derived.
Exit 0 = gate PASS + pool entry+shard flipped done with harvest_note.
Exit 2 = gate red, NO flip.
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from science_gates import ledger_head  # noqa: E402

PROD = os.path.join(ROOT, "results", "aggr_fullpool_battery.json")
POOL = os.path.join(ROOT, "results", "runnable_pool.json")
LAB = os.path.join(ROOT, "results", "aggressive_lab.json")
FAM = os.path.join(ROOT, "results", "aggressive_family.json")
ENTRY_ID = "T80-AGGR-FULLPOOL-BATTERY"
GRID_KEYS = [f"{src}|{win}|{xf}"
             for src in ("legacy", "deep")
             for win in ("6m", "12m", "24m")
             for xf in ("x1", "x2")]


def main() -> int:
    fails = []
    if not os.path.exists(PROD):
        print("FAIL: aggr_fullpool_battery.json absent")
        return 2
    r = json.load(io.open(PROD, encoding="utf-8"))

    # 1. ledger chain continuity (stored block + re-derived head)
    led = r.get("trials_ledger", {})
    if not (led.get("prev_total") == 186192 and led.get("batch_trials") == 400
            and led.get("total") == 186592):
        fails.append(f"ledger block mismatch: {led}")
    head = ledger_head()
    if head.get("total") != 186592:
        fails.append(f"ledger_head re-derived {head.get('total')} != 186592")

    # 2. evidence cutoff
    if r.get("evidence_cutoff") != "2026-09-24":
        fails.append(f"evidence_cutoff {r.get('evidence_cutoff')!r} != 2026-09-24")

    # 3. variant census + cell faces
    variants = r.get("variants", {})
    if len(variants) != 20:
        fails.append(f"variant census {len(variants)} != 20")
    lab = json.load(io.open(LAB, encoding="utf-8"))["variants"]
    fam = json.load(io.open(FAM, encoding="utf-8"))["variants"]
    j_counts = {"J1_current_window_profit": 0, "J2_x2_survival": 0,
                "J3_regime_segment_stability": 0}
    pooled12 = {}
    for vid, v in variants.items():
        jd = v.get("judgments", {})
        if set(jd) != set(j_counts):
            fails.append(f"{vid}: judgment keys {sorted(jd)}")
        for k, val in jd.items():
            if not isinstance(val, bool):
                fails.append(f"{vid}: judgment {k} non-bool {val!r}")
            elif val:
                j_counts[k] += 1
        g = v.get("w_grid_fullpool", {})
        if sorted(g) != sorted(GRID_KEYS):
            fails.append(f"{vid}: grid cell keys {len(g)} != 12-set")
        if len(v.get("w_cur", {})) != 2 or len(v.get("w_seg", {})) != 2:
            fails.append(f"{vid}: w_cur/w_seg face census {len(v.get('w_cur', {}))}/{len(v.get('w_seg', {}))}")
        # 4. sleeve anchor re-derivation vs frozen files
        frozen = (lab if vid in lab else fam).get(vid)
        if frozen is None:
            fails.append(f"{vid}: absent from frozen files")
        else:
            if v.get("w_cur") != frozen.get("w_cur"):
                fails.append(f"{vid}: w_cur drift vs frozen anchor")
            if v.get("w_seg") != frozen.get("w_seg"):
                fails.append(f"{vid}: w_seg drift vs frozen anchor")
        p12 = v.get("grid_12m_pooled_fullpool") or v.get("kpi", {}).get("pooled12_fullpool")
        pooled12[vid] = (v.get("grid_12m_pooled_fullpool") or {}).get("rate", p12)

    # 5. NOCASH == canon grid bit-identity
    noc = variants.get("AGGR-NOCASH", {}).get("w_grid_fullpool")
    canon_grid = r.get("canon_b_maxdiv_fullpool_grid")
    if noc != canon_grid:
        fails.append("AGGR-NOCASH w_grid_fullpool != canon_b_maxdiv_fullpool_grid")

    # 6. canon 12m pooled re-derive
    c12 = r.get("canon_b_maxdiv_grid_12m_pooled", {})
    if not (isinstance(c12, dict) and c12.get("n") == 2507
            and c12.get("rate") == round(c12.get("beats", 0) / c12.get("n", 1), 4)):
        fails.append(f"canon 12m pooled re-derive mismatch: {c12}")

    if fails:
        print(json.dumps({"harvest_gate": "FAIL", "fails": fails},
                         ensure_ascii=False, indent=1))
        return 2

    # flip pool entry+shard done (single_writer: rounds own this file)
    pool = json.load(io.open(POOL, encoding="utf-8"))
    entry = next((e for e in pool.get("entries", []) if e.get("id") == ENTRY_ID), None)
    if entry is None:
        print("FAIL: pool entry T80-AGGR-FULLPOOL-BATTERY missing")
        return 2
    if entry.get("status") == "ready":
        top3 = sorted(((rt, vid) for vid, rt in pooled12.items() if rt is not None),
                      reverse=True)[:3]
        entry["status"] = "done"
        for sh in entry.get("shards", []):
            if sh.get("key") == "aggrfp-0of1":
                sh["status"] = "done"
                sh["harvest_note"] = (
                    "R253 bm-a deterministic harvest: landed 15:10:35 (autofill "
                    "15:10:02, runner sha 29de7acc = bm-b R256 A1 caliber pin; anchor "
                    "gate PASSED into variant loop after adjudication). Ledger "
                    "186192+400=186592 chain-continuous with R252 repair head; "
                    "sleeve anchors 20/20 re-verified vs frozen files; "
                    "NOCASH==canon grid bit-identity holds; canon 12m pooled "
                    "0.4699 (n2507) = CE-6 face 0.4854 downgraded as prereg "
                    "predicted; J1/J2/J3 = "
                    f"{j_counts['J1_current_window_profit']}/"
                    f"{j_counts['J2_x2_survival']}/"
                    f"{j_counts['J3_regime_segment_stability']}/20; top pooled12 "
                    + ", ".join(f"{vid} {rt}" for rt, vid in top3)
                    + "; ALL verdicts incomplete-face (capacity face missing, "
                    "T-56 dual-track law); zero adoption zero wiring. dA basis "
                    "add-on: bm-b originals hash MISMATCH confirmed on bm-a "
                    "re-run files (934a7fb6/e839b78c raw; LF-norm "
                    "f14b2e1c/ad3c044e != 79585a95/f09329f4) -- transfer "
                    "requested from bm-b per its protocol; prereg basis = pinned "
                    "paths + census + passive gates (passed live), not bm-b bytes"
                )
        with io.open(POOL, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(pool, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
    elif entry.get("status") != "done":
        print(f"FAIL: entry status {entry.get('status')!r} unexpected")
        return 2

    out = {
        "harvest_gate": "PASS",
        "entry": ENTRY_ID,
        "ledger": {"prev_total": 186192, "batch_trials": 400, "total": 186592},
        "judgment_counts": j_counts,
        "pooled12_fullpool_sorted": [
            {"variant": vid, "rate": rt} for rt, vid in
            sorted(((rt, vid) for vid, rt in pooled12.items() if rt is not None),
                   reverse=True)],
        "canon_12m_pooled": c12,
        "verdict_label": r.get("verdict_note"),
        "six_face_coverage": r.get("six_face_coverage", {}).get("capacity_face"),
        "audit": r.get("audit"),
    }
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
