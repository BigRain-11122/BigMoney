"""r423 bm-c bookkeeping: state + heartbeat + round-report append (one-shot)."""
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = time.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
EPOCH = int(time.time())

DID = ("r423 bm-c: (1) MAIN DELIVERABLE: MASS_TRIAL_W2 s3 judge-face FROZEN "
       "(commit 4796399f3, R99 freeze-before-burn) -- prereg sec.9.1 append "
       "(806 survivors -> |corr|>=0.999 leg-L collapse -> N_judge zero-claim; "
       "p5c FROZEN_CENSUS grid isomorphic w1 sec.9.1; dual nulls B=2000/P=2000; "
       "N_eff cross-wave via live ledger-head never reset; E[FP]=0.05*N_judge) + "
       "seed mass_trial_w2_judge=20285200 band 20285200..20285499 rg+registry "
       "zero-hit registered same commit (R250 one-step) + runner judge-prep/"
       "judge/judge-finalize --wave 2 via _judge_faces single source (w1 "
       "byte-face intact, ckpt prefix w2_judge_shard_*, refinalize env split), "
       "selftest 33/33 with 3 new w2 legs. (2) judge-prep --wave 2 spawned "
       "detached (Tools/_r423bmc_w2_judge_prep.py, r422 burn protocol) -- "
       "806 serial leg-L backtests ~13min band, in-flight at round close; "
       "r424 adopts: poll artifact -> enroll MASS-TRIAL-W2-JUDGE 4 shards "
       "into runnable_pool (long-burn law). (3) S0: HEAD==origin at r423 "
       "open (behind 13 integrated r422); D-19 4167B784 MATCH zero-consume; "
       "group orders 68947C17 MATCH; orders 152/152 zero-unacked (double-scan). "
       "(4) S1 smoke 47/47; SatEngine rc0 alive (N1 queue in-register); WM "
       "green/insufficient_history. (5) S6 37 legs rc0 (dualrun zero-drift "
       "streak 20; audit CLEAN; golden-week no-op faces; 3 lane_io "
       "stale-takeovers bm-a 43-45min per O-2100 STALE_MIN law). (6) S7 "
       "4/4 self-heal green (loop pin=5 no-op, hooks byte-fresh, attrition "
       "CLEAN).")
ACTIVITY = ("r423: MASS_TRIAL_W2 s3 judge-face FROZEN (4796399f3) + "
            "judge-prep --wave 2 detached in-flight; next: pool enrollment "
            "MASS-TRIAL-W2-JUDGE r424")
NEXT = ("(a) r424: poll w2_judge_state.json (detached prep) -> verify "
        "collapse/N_judge -> enroll MASS-TRIAL-W2-JUDGE 4 shards into "
        "runnable_pool.json (burn in-flight <=10-06 anchor, O-2115 10-08 "
        "acceptance); (b) D-06 full-reconciliation closeout audit 10-07; "
        "(c) T-143 assembly window post-10-09 (deliverable 10-29); "
        "(d) moneyflow GM ruling watch (MSG-1452/1543); (e) W14 line "
        "zero-touch pending GM dual-ruling; (f) merge-window face: origin "
        "+3 (bm-a r633/634 ring-merge + fund-trio rehearsal findings "
        "MSG-1720) integrated this closeout window.")
VERIFY = ("smoke 47/47 rc0; mass_trial selftest 33/33 (3 new w2 judge legs); "
          "freeze commit 4796399f3 landed (3 files, +139/-42); judge-prep "
          "detached alive (psutil) with self-log; S6 37 legs rc0; S7 4/4 "
          "(loop pin=5 no-op, precommit/prepush byte-fresh, attrition CLEAN "
          "rc0); dualrun streak 20 zero-drift; D-19 4167B784 MATCH; orders "
          "152/152 zero-unacked double-scan; push delivery verify post-commit")
TASK = ("r423: MASS_TRIAL_W2 s3 FROZEN (runner --wave 2 + seed 20285200 + "
        "prereg sec.9.1, commit 4796399f3); judge-prep detached in-flight; "
        "next: pool enroll MASS-TRIAL-W2-JUDGE 4 shards (r424) <=10-06")
ARTIFACT = ("scripts/mass_trial_w1.py judge --wave 2 face + research/"
            "MASS_TRIAL_W2_PREREG.md sec.9.1 + SEED_REGISTRY 20285200 "
            "(freeze commit 4796399f3, 17:2x r423); prep log results/"
            "_r423bmc_w2_judge_prep_log.txt")
MILESTONE = ("wave-2 judgment burn in-flight <=10-06 via MASS-TRIAL-W2-JUDGE "
             "pool enrollment (prep detached now; O-2115 by 10-08); D-06 "
             "closeout 10-07")


def main():
    sp = os.path.join(ROOT, "state-bm-c.json")
    st = json.load(open(sp, encoding="utf-8"))
    st.update({"round_no": 423, "machine_id": "bm-c",
               "clock_read": NOW, "last_seen": NOW, "updated": NOW,
               "did": DID, "next": NEXT, "verify": VERIFY,
               "current_task": TASK,
               "last_round": "r423 bm-c: MASS_TRIAL_W2 s3 judge-face FROZEN "
                             "(4796399f3) + judge-prep detached in-flight",
               "last_round_at": NOW, "last_round_ts": NOW, "last_ts": NOW,
               "last_decisions_read_at": NOW,
               "heartbeat_epoch_utc": EPOCH})
    json.dump(st, open(sp, "w", encoding="utf-8"), indent=1,
              ensure_ascii=False)

    hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
    h = json.load(open(hp, encoding="utf-8"))
    h.update({"activity_now": ACTIVITY, "current_task": TASK,
              "latest_artifact": ARTIFACT, "next_milestone": MILESTONE,
              "last_seen": NOW, "last_seen_at": NOW, "updated_at": NOW,
              "round_no": 423, "heartbeat_epoch_utc": EPOCH,
              "clock_read": NOW,
              "prod_lanes": "MASS_TRIAL_W2 s3 FROZEN (judge-prep in-flight, "
                            "pool enrollment r424 <=10-06); moneyflow lane "
                            "GM-ruling pending; D-06 closeout 10-07"})
    json.dump(h, open(hp, "w", encoding="utf-8"), indent=1,
              ensure_ascii=False)
    assert isinstance(h["heartbeat_epoch_utc"], int)

    rp = os.path.join(ROOT, "round_reports-bm-c.md")
    with open(rp, "a", encoding="utf-8", newline="\n") as f:
        f.write(f"{NOW}\t|\tr423\t|\t{DID}\t|\t{VERIFY}\t|\t{NEXT}\n")
    print("bookkeep r423 OK: state + heartbeat + round-report")


if __name__ == "__main__":
    main()
