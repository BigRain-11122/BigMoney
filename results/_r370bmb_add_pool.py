# -*- coding: utf-8 -*-
"""r370 bm-b pool entry add: TRIAL-LABOR-W3-JUDGE (waiting; judge slice
landed this round per MSG-20260928-0905 claim).

Mirror of the bm-c r150 add pattern (_r150bmc_resolve_pool.py face-1):
append exactly ONE entry + bump updated_at; every other top-level field
asserted byte-identical; refuses if the entry already exists (idempotent
guard)."""
import io
import json
import time

SRC = "results/runnable_pool.json"
MY_ID = "TRIAL-LABOR-W3-JUDGE"

entry = {
    "id": MY_ID,
    "ticket_ref": "T-2026-09-28-97 WAVE-3 judge slice (CEO "
                  "O-2026-09-27-2245 thousand-trader order + "
                  "O-2026-09-27-2250 standing law; prereg FROZEN r391; "
                  "grammar frozen r392 sha16=cc59eab79db53436; screen "
                  "slice r150 bmc; judge slice built bm-b r370 per "
                  "MSG-20260928-0905 single-writer claim, selftest 72/72 "
                  "hermetic + double-run stdout byte-identical rc=0; "
                  "judge-prep CLI gate honest rc=2 verified)",
    "prereg_ref": "research/TRIAL_LABOR_W3_PREREG.md FROZEN sec.3 s3 "
                  "(judged face = dual-leg P-5C grid L/D x {6m,12m,24m} "
                  "x cost {base x1, x2=CostPatch(2)} full curves WITH "
                  "the gate overlay + initial-stop overlay carried per "
                  "cell, frozen composition signal -> filter -> timing "
                  "-> GATE -> initial-stop + regime segments + dual "
                  "nulls B=2000/P=2000 seed trial_labor_w3_unc=20288500 "
                  "[20288500, cell_idx]) + sec.4 (g1_prime_v2/"
                  "g2_registration_v2 shared lib zero hand-copy, DSR "
                  "n_trials = live chain head cross-wave no-reset, "
                  "family PBO CSCV 8 blocks family=strategy-module, "
                  "E[FP]=0.05*N_judged) + sec.5.6 (crisis-day + "
                  "stop-trigger-day + gate-flip-day per-cell disclosure "
                  "columns; gate_flip_days_legL = panel-level flip-day "
                  "count of the cell's OWN gate face, gate=none -> "
                  "null, disclosure-only zero gate weight)",
    "runner": "scripts/trial_labor_w3.py",
    "runner_args": ["judge", "--shard", "0", "--shards", "1"],
    "lane_owner": None,
    "priority": 1,
    "status": "waiting",
    "entered_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    "workers_plan": {
        "workers": "worker_cap() pool BelowNormal",
        "priority": "BelowNormal",
        "note": "judge initargs carry BOTH leg panels + per-leg ATR20 + "
                "per-leg gate_state faces = heaviest per-worker state "
                "in the fleet (worker_cap RAM guard applies); 4 engine "
                "curves/cell (dual-leg x base/x2) each carrying the "
                "gate+stop overlays ~4-6x screen-cell weight + "
                "vectorized dual nulls; W2 judge same-machinery "
                "precedent; flip executor = deep-panel machine round "
                "(bm-b) post screen-finalize + judge-prep + RAM "
                "3-sample gate (W1-JUDGE r357 defer precedent)",
    },
    "data_gates": "WAITING DEPS (flip to ready upon ALL, W1-JUDGE r346 "
                  "precedent): (1) screen-finalize done -> w3_screen. "
                  "json survivors (burn COMPLETE 3752/3752 checkpoint "
                  "committed bm-a round-394-close; finalize = separate "
                  "round work by the screen-line owner, NOT pooled "
                  "autofill); (2) judge-prep run on the deep-panel "
                  "machine (physical = bm-b, t18 sidecar family; "
                  "cache-less machines exit-2 honest seconds per W1 "
                  "precedent) -> judge_state.json t18 manifest verdict "
                  "PASS + dual-leg census == frozen L{1253,1127,875}/"
                  "D{3104,2978,2726} + per-leg gate meta; (3) machine "
                  "free RAM >= 4GB three-sample across >=30s (r354 law; "
                  "census W2B burn on bm-b gates it until finalize). "
                  "IN-RUNNER fail-closed: judge_state/w3_screen absent "
                  "exit 2; grammar sha != cc59eab79db53436 refuse; "
                  "per-leg census drift refuse; 510300 missing from a "
                  "leg panel refuse (gate series underivable); "
                  "zero-survivor vacuous face = judge no-op + "
                  "judge-finalize lawful zero product + ledger 0 "
                  "(prereg sec.5 pred.3 modal-zero). After shards: "
                  "judge-finalize = separate round work (ledger "
                  "TRIAL_LAB_W3_JUDGE batch_trials=survivors literal + "
                  "w3_judge.json G1/G2/DSR/PBO/E[FP]/gate-face "
                  "judgment summary/descriptive-summary; intake slice "
                  "lands next per prereg sec.6)",
    "shards": [
        {
            "key": "judge-0of1",
            "status": "waiting",
            "owner": None,
            "owner_since": None,
            "checkpoint": "results/trial_labor_w3/checkpoint/"
                          "judge_shard_0of1.jsonl (row-level done-set "
                          "resume, cross-kill W1 law)",
            "note": "single shard W1/W2-JUDGE precedent; multi-shard "
                    "i%shards split legal per shard law on partial "
                    "claim; cell enumeration = sorted survivors global "
                    "index i = dual-nulls seed binding face (stable "
                    "across shard counts); judged-cell burn order = "
                    "L-base, L-x2, D-base, D-x2 + dual nulls + "
                    "disclosures per cell",
        }
    ],
    "entered_by": "bm-b r370",
}

raw = io.open(SRC, "r", encoding="utf-8", newline="").read()
d = json.loads(raw)
assert set(d) == {"version", "law_ref", "schema", "updated_at",
                 "_stamp_note", "entries"}, f"shape drift: {list(d)}"
ids = [e.get("id") for e in d["entries"]]
assert MY_ID not in ids, f"{MY_ID} already present -- idempotent refuse"
d["entries"].append(entry)
d["updated_at"] = entry["entered_at"]
with io.open(SRC, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(d, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
chk = json.load(io.open(SRC, encoding="utf-8"))
mine = [e for e in chk["entries"] if e["id"] == MY_ID]
assert len(mine) == 1 and mine[0]["status"] == "waiting"
print(f"[r370] pool entry added: {MY_ID} status=waiting "
      f"(total entries {len(chk['entries'])}, updated_at "
      f"{chk['updated_at']})")
