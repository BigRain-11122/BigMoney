"""r391 bm-b: TRIAL_LABOR_W3 judge harvest -- entry done-flip (shared + bm-b
lane mirror, r387 dual-face law) + w3_intake.json zero-face (prereg sec.6 s4).

Facts on record:
- burn complete 513/513 @2026-09-28 15:13:44 (bm-b r389, checkpoint committed)
- judge-finalize receipt results/trial_labor_w3/w3_judge.json @15:51:55
  (detached pid 28400, log logs/w3_judge_finalize_r389.log): 513 judged
  cells, E[FP]=25.65, G2 eligible 0, gate-face {bear 0/218, bull 0/132,
  none 2/163 G1-pass}
- trials chain head 311,363 -> 311,876 (+513, TRIAL_LAB_W3_JUDGE)
- bm-c shard claim 15:50:05 predates NOTHING (work complete 15:13:44,
  finalize in flight since 15:21:53): superseded by completed work;
  any bm-c judge-stage re-run = full-checkpoint no-op resume, zero cells
  re-burned; zero double-count risk (trials ledger = derived chain head).
"""
import datetime as dt
import json

POOL = r"results\runnable_pool.json"
POOL_BMB = r"results\runnable_pool.bm-b.json"
JUDGE = r"results\trial_labor_w3\w3_judge.json"
INTAKE = r"results\trial_labor_w3\w3_intake.json"
WAVE = "TRIAL_LABOR_W3"
ENTRY = "TRIAL-LABOR-W3-JUDGE"

now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
today = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
j = json.load(open(JUDGE, encoding="utf-8"))
assert j["n_judged_cells"] == 513 and j["n_eligible_g2"] == 0, \
    (j["n_judged_cells"], j["n_eligible_g2"])
assert j["trials_ledger"]["total"] == 311876, j["trials_ledger"]

DONE_NOTE = (
    "r391 bm-b harvest: finalize receipt w3_judge.json @2026-09-28 15:51:55 "
    "(513 judged, E[FP]=25.65, G2 eligible 0, gate-face bear 0/218 bull 0/132 "
    "none 2/163; chain head 311363->311876) -> entry done-flip this round; "
    "w3_intake.json zero-face per prereg sec.6 s4 (zero survivors = lawful "
    "reading, zero library/paper-desk writes); bm-c shard claim 15:50:05 "
    "superseded by completed work (burn 15:13:44 + finalize in-flight since "
    "15:21:53), no cells re-burned (full-checkpoint no-op resume); 48h CEO "
    "verdict report clock running (standing deadline 09-29 22:45)"
)

for path in (POOL, POOL_BMB):
    d = json.load(open(path, encoding="utf-8"))
    items = d if isinstance(d, list) else d.get("entries", [])
    e = next(x for x in items if x.get("id") == ENTRY)
    assert e["status"] == "ready", (path, e["status"])
    e["status"] = "done"
    e["done_at"] = now
    e["done_note"] = DONE_NOTE
    sh = e["shards"][0]
    assert sh["key"] == "judge-0of1" and sh["status"] == "waiting"
    sh["status"] = "done"
    sh["owner"] = "bm-b"          # actual performer (autofill claim 15:03:31)
    sh["owner_since"] = "2026-09-28 15:03:31"
    sh["done_note"] = DONE_NOTE
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    d2 = json.load(open(path, encoding="utf-8"))
    items2 = d2 if isinstance(d2, list) else d2.get("entries", [])
    e2 = next(x for x in items2 if x.get("id") == ENTRY)
    assert e2["status"] == "done" and e2["shards"][0]["status"] == "done"
    print(f"{path}: {ENTRY} -> done (dual-face synced)")

# w3_intake.json -- zero-G2-eligible face, W2 zero-wave precedent
# (results/trial_labor_w2/w2_intake.json @15:03:10)
intake = {
    "wave": WAVE,
    "stage": "intake",
    "prereg": "research/TRIAL_LABOR_W3_PREREG.md",
    "evidence_cutoff": j["evidence_cutoff"],
    "grammar_sha256": j["grammar_sha256"],
    "n_eligible": 0,
    "admitted": [],
    "rejected": [],
    "d6_binding": {},
    "intake": [],
    "note": "zero G2-eligible survivors = lawful outcome, reported as-is "
            "(prereg sec.6 s4 actual-count clause; gate-face G1 passes "
            "bear 0/218, bull 0/132, none 2/163 -> none cleared G2)",
    "audit": {
        "n_engine_runs": 0,
        "ledger_trials_added": 0,
        "note": "intake = judgment face, zero ledger rows; zero eligible "
                "-> D6 binding / STRATEGY_LIBRARY registration / TRIAL-* "
                "paper-desk onboarding / smoke anchor re-run all "
                "zero-surface per prereg sec.6 s4 (dead path this wave); "
                "runner cmd_intake subcommand not built this wave -- zero "
                "survivors made the registration path dead code; W2 "
                "runner cmd_intake (scripts/trial_labor_w2.py) is the "
                "reusable precedent for any wave with survivors",
        "judge_receipt": "results/trial_labor_w3/w3_judge.json "
                         "(513 judged, E[FP]=25.65, n_eligible_g2=0)",
    },
    "generated": today,
}
with open(INTAKE, "w", encoding="utf-8") as f:
    json.dump(intake, f, ensure_ascii=False, indent=1)
d = json.load(open(INTAKE, encoding="utf-8"))
assert d["n_eligible"] == 0 and d["intake"] == []
print(f"{INTAKE}: zero-face written (n_eligible=0, lawful)")
