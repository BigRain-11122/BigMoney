"""r710 bm-a N2-W15-JUDGE finalize adoption verify chain (one-command
executor for the landing round). Copy-adapt of _r487bmc_w3_judge_verify.py
(W3-JUDGE ADOPT_PASS precedent, bm-c r508). Laws: r668 pool-double-flip
recheck / r482+r685 same-window id-dup probe / r641 evidence-before-
assertion / r446 probe-to-file. Read-only + receipt write; zero pool/
ledger mutation.

Faces (product already landed 05:38:14, leg A PID 103532 dead -- r708
active-process probe law already applied, no respawn):
  1. artifact: results/n2_w15/n2_w15_judge.json complete=true + caliber
     assertions (prev_total==648730, batch_trials==281, total==649011;
     n_trials_head_at_finalize==648730 == prev_total -> no same-window
     foreign insert this time, simple chain case).
  2. chain: exactly ONE results/**/*.json block with
     trials_ledger.batch=="PERPETUAL-N2-W15-JUDGE" (skip _quarantine);
     live ledger_head total==649011 after landing.
  3. checkpoint re-probe: n2_w15_judge_shard_*.jsonl union unique cell
     ids ==281, id_dup==0 (post-merge same-window law r685).
  4. pool: 12/12 PERPETUAL-N2-W15-JUDGE-SHARD-* entries status==done
     (+PREP entry done informational) (r668).
  5. frozen-caliber: seed_judge==545500 (prereg sec.9.1 frozen commit),
     evidence_cutoff=="2026-09-22", E[FP]==281*0.05==14.05.
"""
import glob as _glob
import json
import os
import sys

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, "..", "scripts"))
sys.path.insert(0, os.path.join(_here, ".."))  # knowledge pkg (cost_spec)
import science_gates as sg  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO, "results", "n2_w15")
PRODUCT = os.path.join(OUT_DIR, "n2_w15_judge.json")
POOL = os.path.join(REPO, "results", "runnable_pool.json")
RECEIPT = os.path.join(REPO, "results", "_r710bma_n2_judge_verify.json")
EXPECT = {
    "batch": "PERPETUAL-N2-W15-JUDGE",
    "n_judge_cells": 281,
    "seed_judge": 545500,
    "prev_total": 648730,   # live head at landing == head at finalize start
    "new_total": 649011,
    "e_fp": 14.05,
}


def face_checkpoint():
    ids = []
    dup = 0
    files = sorted(f for f in os.listdir(os.path.join(OUT_DIR, "checkpoint"))
                   if f.startswith("n2_w15_judge_shard")
                   and f.endswith(".jsonl"))
    for f in files:
        with open(os.path.join(OUT_DIR, "checkpoint", f),
                  encoding="utf-8") as fh:
            for ln in fh:
                if not ln.strip():
                    continue
                r = json.loads(ln)
                cid = r.get("cell_id")
                if cid in ids:
                    dup += 1
                else:
                    ids.append(cid)
    return {"files": len(files), "union_unique": len(ids),
            "id_dup": dup, "sample_ok":
            all(x.startswith("JUDGE|W15-") for x in ids[:5]) if ids else False}


def face_pool():
    pool = json.load(open(POOL, encoding="utf-8"))
    out = {}
    for e in pool.get("entries", []):
        eid = e.get("id", "")
        if eid.startswith("PERPETUAL-N2-W15-JUDGE"):
            out[eid] = {"entry": e.get("status"),
                        "shards": {s.get("key"): s.get("status")
                                   for s in e.get("shards", [])}}
    return out


def face_chain_blocks():
    hits = []
    for path in sorted(_glob.glob(os.path.join(REPO, "results", "**",
                                               "*.json"), recursive=True)):
        if os.sep + "_quarantine" + os.sep in path:
            continue
        try:
            with open(path, encoding="utf-8") as fh:
                d = json.load(fh)
        except (OSError, ValueError):
            continue
        tl = d.get("trials_ledger") if isinstance(d, dict) else None
        if isinstance(tl, dict) and tl.get("batch") == EXPECT["batch"]:
            hits.append({"file": os.path.relpath(path, REPO),
                         "prev_total": tl.get("prev_total"),
                         "batch_trials": tl.get("batch_trials"),
                         "total": tl.get("total")})
    return hits


def main():
    rec = {"ts_probe": __import__("time").strftime("%Y-%m-%dT%H:%M:%S"),
           "round": "r710 bm-a", "expect": EXPECT}
    rec["liveness"] = {"pid": 103532, "alive": False,
                       "note": "leg A landed 05:38:14 then exited; "
                               "active-process probe done at round start "
                               "(r708 law), no respawn"}
    rec["pool"] = face_pool()
    shard_entries = {k: v for k, v in rec["pool"].items()
                     if "-SHARD-" in k}
    rec["pool_12of12_done"] = (len(shard_entries) == 12 and all(
        v["entry"] == "done" and all(s == "done"
                                     for s in v["shards"].values())
        for v in shard_entries.values()))
    rec["pool_prep_done"] = rec["pool"].get(
        "PERPETUAL-N2-W15-JUDGE-PREP", {}).get("entry") == "done"
    rec["checkpoint"] = face_checkpoint()

    if not os.path.exists(PRODUCT):
        rec["verdict"] = "DEAD_NO_PRODUCT"
    else:
        d = json.load(open(PRODUCT, encoding="utf-8"))
        tl = d.get("trials_ledger", {})
        rec["product"] = {
            "complete": d.get("complete"),
            "n_judge_cells": d.get("n_judge_cells"),
            "batch": tl.get("batch"),
            "prev_total": tl.get("prev_total"),
            "batch_trials": tl.get("batch_trials"),
            "total": tl.get("total"),
            "n_trials_head_at_finalize": d.get("n_trials_head_at_finalize"),
            "seed_judge": d.get("audit", {}).get("seed_judge"),
            "evidence_cutoff": d.get("evidence_cutoff"),
            "verdicts": d.get("verdicts"),
            "n_eligible_g2_d6": d.get("n_eligible_g2_d6"),
            "e_fp": d.get("n_wave_disclosure", {}).get("E_FP_nominal_5pct"),
            "family_pbo": d.get("family_pbo"),
            "collapse_eliminated":
                len(d.get("collapse_audit", {}).get("eliminated", [])),
        }
        rec["chain_blocks"] = face_chain_blocks()
        rec["ledger_head_live"] = sg.ledger_head()["total"]
        v = rec["product"]
        checks = {
            "complete": v["complete"] is True,
            "n_cells": v["n_judge_cells"] == EXPECT["n_judge_cells"],
            "batch": v["batch"] == EXPECT["batch"],
            "prev_total_true_head":
                v["prev_total"] == EXPECT["prev_total"],
            "batch_trials": v["batch_trials"] == EXPECT["n_judge_cells"],
            "total_arith": v["total"] == EXPECT["new_total"],
            "head_at_finalize": v["n_trials_head_at_finalize"]
            == EXPECT["prev_total"],
            "no_same_window_insert":
                v["n_trials_head_at_finalize"] == v["prev_total"],
            "seed": v["seed_judge"] == EXPECT["seed_judge"],
            "evidence_cutoff":
                v["evidence_cutoff"] == "2026-09-22",
            "verdicts_sum": sum(v["verdicts"].values())
            == EXPECT["n_judge_cells"],
            "single_chain_block": len(rec["chain_blocks"]) == 1,
            "chain_block_matches": len(rec["chain_blocks"]) == 1
            and rec["chain_blocks"][0]["total"] == EXPECT["new_total"],
            "ledger_head_live_advance":
            rec["ledger_head_live"] == EXPECT["new_total"],
            "ckpt_no_dup": rec["checkpoint"]["id_dup"] == 0
            and rec["checkpoint"]["union_unique"]
            == EXPECT["n_judge_cells"],
            "pool_12of12_done": rec["pool_12of12_done"],
            "pool_prep_done": rec["pool_prep_done"],
            "collapse_zero_elim":
                v["collapse_eliminated"] == 0
            and v["n_judge_cells"] == 281,
            "e_fp_caliber": abs(v["e_fp"] - EXPECT["e_fp"]) < 1e-9,
        }
        rec["checks"] = checks
        rec["verdict"] = ("ADOPT_PASS" if all(checks.values())
                          else "ADOPT_FAIL")
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(rec, f, ensure_ascii=False, indent=1)
    print("VERIFY_VERDICT", rec["verdict"])
    if rec["verdict"] != "DEAD_NO_PRODUCT":
        print(json.dumps(rec.get("checks", {}), ensure_ascii=False))
    print("receipt ->", os.path.relpath(RECEIPT, REPO))


if __name__ == "__main__":
    main()
