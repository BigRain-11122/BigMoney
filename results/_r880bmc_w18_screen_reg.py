# _r880bmc_w18_screen_reg.py -- r880 bm-c: register TRIAL-LABOR-W18-SCREEN-SHARD-0..7
# pool entries (W17 8-shard precedent, lane pinned bm-c for checkpoint
# locality; double-file law: shared + lane same bytes in one operation).
# Idempotent: entries already present (any status) are never re-added.
import json
import datetime

ROOT = "."
SHARED = "results/runnable_pool.json"
LANE = "results/runnable_pool.bm-c.json"
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

TICKET = ("T-2026-10-11-185 wave ticket lineage (W8=T-120/W9=T-121/W10=T-122/"
          "W11=T-123/W12=T-124/W13=T-125/W14=T-128/W16=T-172/W17=T-178); "
          "W18 = sizing-axis 4-arm full-cross paired isolation, freeze "
          "commit 0c6213e2e (r879), runner landed 28a23966a (r880), "
          "generate done + screen-prep done (prep_state 1253 starts)")
PREREG = ("research/TRIAL_LABOR_W18_PREREG.md FROZEN 2026-10-11 sec.3 "
          "screen (692 paired cells + K=200 nulls = 892 screen trials; "
          "sec.9 pool sequencing; sizing-axis complete-block PAIRED "
          "isolation; control arm = per-cell as-burned axis[2] face)")
CONSUMER = ("TRIAL-LABOR-W18 chain: 8 screen shards -> screen-finalize "
            "(survival line + G-face battery + ledger append) -> "
            "judge-prep -> judge -> judge-finalize (verdicts + reform face "
            "+ w18_paired_deltas.json) -> s4 intake; 48h CEO report clock "
            "starts at judge landing")
WORKERS = {"workers": "worker_cap() pool BelowNormal",
           "priority": "BelowNormal",
           "note": ("W17 screen machinery precedent (run_cells_parallel "
                    "multiproc); stride i%8 of 892 cells; RAM gate 4GB "
                    "r354 honest-refuse retry")}
DEPS = ["results/trial_labor_w18/w18_cells.json",
        "results/trial_labor_w18/prep_state.json"]
GATES = ("fail-closed rc2 until data_deps present (cells + prep_state; "
         "both landed r880 bm-c; determinism cross-door = as-burned arm "
         "173 pairs vs w17_screen_cells.csv control rows hard VOID)")

def build(i, n):
    return {
        "id": "TRIAL-LABOR-W18-SCREEN-SHARD-%d" % i,
        "ticket_ref": TICKET,
        "prereg_ref": PREREG,
        "runner": "scripts/trial_labor_w18.py",
        "runner_args": ["screen", str(i), str(n)],
        "lane_owner": "bm-c",
        "priority": 1,
        "consumer_plan": CONSUMER,
        "workers_plan": WORKERS,
        "data_gates": GATES,
        "data_deps": DEPS,
        "status": "ready",
        "shards": [{
            "key": "w18-screen-%dof%d" % (i, n),
            "status": "ready",
            "checkpoint": ("results/trial_labor_w18/checkpoint/"
                           "screen_shard_%dof%d.jsonl (MACHINE-LOCAL "
                           "r429 gitignored; lane pinned bm-c -- "
                           "screen-finalize reads local CKPT_DIR; "
                           "stride i%%%d)" % (i, n, n)),
            "owner": None,
            "note": ("stride i%%%d of 892 cells (692 paired + 200 nulls); "
                     "RAM gate 4GB r354 honest-refuse retry" % n),
        }],
        "entered_at": NOW,
        "entered_by": "bm-c",
    }

def reg(path, new_ents):
    with open(path, encoding="utf-8") as fh:
        d = json.load(fh)
    have = {e.get("id") for e in d.get("entries", [])}
    added = 0
    for e in new_ents:
        if e["id"] not in have:
            d["entries"].append(e)
            added += 1
    d["updated_at"] = NOW
    s = json.dumps(d, indent=1, ensure_ascii=False)
    s = s.replace("\n", "\r\n")
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(s)
    return added

ents = [build(i, 8) for i in range(8)]
a1 = reg(SHARED, ents)
a2 = reg(LANE, ents)
# byte-identity assertion (double-file law)
b1 = open(SHARED, "rb").read()
b2 = open(LANE, "rb").read()
assert b1 == b2, "double-file law violated: shared/lane bytes differ"
print("registered shared=+%d lane=+%d byte-identity OK (%d bytes)"
      % (a1, a2, len(b1)))
