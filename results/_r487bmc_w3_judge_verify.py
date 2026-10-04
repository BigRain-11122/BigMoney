"""r487 bm-c W3-JUDGE finalize adoption verify chain (one-command executor
for the landing round). Laws: r668 pool-double-flip recheck / r482+r685
same-window id-dup probe / r641 evidence-before-assertion / r446
probe-to-file. Read-only + receipt write; zero pool/ledger mutation.

Faces:
  1. liveness: psutil pid 33768 (spawn 17:44:04) -- ALIVE burn / DEAD.
  2. artifact: results/mass_trial/w3_judge.json complete=true + caliber
     assertions (prev_total==646799 quarantine-fixed true head, not the
     652840 phantom; batch_trials==777; total==647576).
  3. chain: exactly ONE results/**/*.json block with
     trials_ledger.batch=="MASS_TRIAL_W3_JUDGE" (skip _quarantine); live
     ledger_head total==647576 after landing.
  4. checkpoint re-probe: w3_judge_shard_*.jsonl union unique cell ids
     ==777, id_dup==0 (post-merge same-window law r685).
  5. pool: 4/4 MASS-TRIAL-W3-JUDGE-SHARD-* entries status==done (r668).

If product absent -> IN_FLIGHT receipt with w2-calibrated ETA (805 cells
took 4h44m spawn->product 23:34:14->04:18:26; 777 cells ~= same order;
spawn 17:44:04 -> projected ~22:1x). No assertion failures in that mode.
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
OUT_DIR = os.path.join(REPO, "results", "mass_trial")
PRODUCT = os.path.join(OUT_DIR, "w3_judge.json")
POOL = os.path.join(REPO, "results", "runnable_pool.json")
RECEIPT = os.path.join(REPO, "results", "_r487bmc_w3_judge_verify.json")
FINALIZE_PID = 33768
EXPECT = {
    "batch": "MASS_TRIAL_W3_JUDGE",
    "n_judge_cells": 777,
    "seed_judge": 20285600,
    "prev_total": 646799,   # true head (quarantine fix in tree at spawn)
    "new_total": 647576,
    "e_fp": 38.85,
}


def face_liveness():
    try:
        import psutil
        p = psutil.Process(FINALIZE_PID)
        c = p.cpu_times()
        return {"pid": FINALIZE_PID, "alive": True,
                "cpu_s": round(c.user + c.system, 1),
                "age_min": round((__import__("time").time()
                                  - p.create_time()) / 60, 1)}
    except Exception as e:  # psutil.NoSuchProcess / AccessDenied
        return {"pid": FINALIZE_PID, "alive": False, "err": str(e)[:120]}


def face_checkpoint():
    ids = []
    dup = 0
    files = sorted(f for f in os.listdir(OUT_DIR)
                   if f.startswith("w3_judge_shard") and f.endswith(".jsonl"))
    for f in files:
        with open(os.path.join(OUT_DIR, f), encoding="utf-8") as fh:
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
            all(x.startswith("JUDGE|") for x in ids[:5]) if ids else False}


def face_pool():
    pool = json.load(open(POOL, encoding="utf-8"))
    out = {}
    for e in pool.get("entries", []):
        eid = e.get("id", "")
        if eid.startswith("MASS-TRIAL-W3-JUDGE-SHARD-"):
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
           "round": "r487 bm-c", "expect": EXPECT}
    rec["liveness"] = face_liveness()
    rec["pool"] = face_pool()
    rec["pool_4of4_done"] = (len(rec["pool"]) == 4 and all(
        v["entry"] == "done" and all(s == "done"
                                     for s in v["shards"].values())
        for v in rec["pool"].values()))
    rec["checkpoint"] = face_checkpoint()

    if not os.path.exists(PRODUCT):
        rec["verdict"] = "IN_FLIGHT"
        rec["eta_note"] = ("w2 calibration: 805 cells 4h44m "
                           "(spawn 23:34:14 -> product 04:18:26); this "
                           "spawn 17:44:04 -> projected ~22:1x; adoption "
                           "next round when artifact lands")
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
            "n_eligible_g2": d.get("n_eligible_g2"),
            "eligible_g2": d.get("eligible_g2"),
            "e_fp": d.get("n_wave_disclosure", {}).get("E_FP_nominal_5pct"),
            "family_pbo": d.get("family_pbo"),
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
            "seed": v["seed_judge"] == EXPECT["seed_judge"],
            "evidence_cutoff_present":
                isinstance(v["evidence_cutoff"], str),
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
            "pool_4of4_done": rec["pool_4of4_done"],
        }
        rec["checks"] = checks
        rec["verdict"] = ("ADOPT_PASS" if all(checks.values())
                          else "ADOPT_FAIL")
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(rec, f, ensure_ascii=False, indent=1)
    print("VERIFY_VERDICT", rec["verdict"])
    if rec["verdict"] != "IN_FLIGHT":
        print(json.dumps(rec.get("checks", {}), ensure_ascii=False))
    print("receipt ->", os.path.relpath(RECEIPT, REPO))


if __name__ == "__main__":
    main()
