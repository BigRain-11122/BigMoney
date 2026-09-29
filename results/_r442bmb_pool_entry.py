"""r442 bm-b: register TRIAL-LABOR-W11-GENERATE runnable-pool entry
(mirror of the W10-GENERATE canon shape; runner slice-1 landed this
round selftest 47/47, grammar serialized sha16 128962592feeb8d3)."""
import json
import datetime

P = "results/runnable_pool.json"
pool = json.load(open(P, encoding="utf-8"))
now = datetime.datetime.now().astimezone()
stamp = now.strftime("%Y-%m-%d %H:%M:%S")
iso = now.isoformat(timespec="seconds")

assert not any(e["id"] == "TRIAL-LABOR-W11-GENERATE"
              for e in pool["entries"]), "W11-GENERATE already pooled"

entry = {
    "id": "TRIAL-LABOR-W11-GENERATE",
    "ticket_ref": ("T-2026-09-29-123 WAVE-11 generate slice (CEO "
                   "O-2026-09-27-2245 thousand-trader order + "
                   "O-2026-09-27-2250 standing law; prereg FROZEN "
                   "bm-b r441 whole-package adoption of the bm-c r237 "
                   "STD candidate per AMP->W9->W10 lineage [trigger "
                   "MET live: W10 full chain landed 2026-09-29 20:31:29 "
                   "{w10_judge.json 283/283 zero G1/G2 + CEO-REPORT-"
                   "WAVE10 + attrition + pool 123/123 done}; SEED "
                   "berth re-take 20317000/20317500/20318000 "
                   "same freeze-commit R250 one-step law, three-step "
                   "re-verify ALL GREEN no re-pick; runner slice-1 "
                   "built bm-b r442 selftest 47/47 fourteen-tuple "
                   "31,352,832 grammar)"),
    "prereg_ref": ("research/TRIAL_LABOR_W11_PREREG.md FROZEN sec.0 "
                   "TRIAL_LAB_W11_GENERATE (s1 Sobol draws -> "
                   "exclusion -> dedup -> w11_candidates.json + "
                   "TRIAL_GRAMMAR_LEDGER wave-11 row; 5000-ceiling; "
                   "fourteen-tuple grammar sha16 128962592feeb8d3 == "
                   "FROZEN pin; evidence_cutoff 2026-09-22 P-5C "
                   "frozen binding; twenty-source exclusion face incl. "
                   "W10 survivors+judged as real-mom rows, std=none "
                   "padded)"),
    "runner": "scripts/trial_labor_w11.py",
    "runner_args": ["generate"],
    "shards": [{
        "key": "generate-0of1",
        "status": "ready",
        "checkpoint": ("results/trial_labor_w11/w11_candidates.json "
                       "(single-shot product = completion marker; "
                       "refuse-if-exists guard)"),
    }],
    "workers_plan": {
        "workers": 1,
        "priority": "BelowNormal",
        "note": ("LIGHT minutes-scale per prereg sec.0 (W7 ~10min "
                 "n=3704; W8 ~10min n=2834; W9 ~10min n=2515; W10 "
                 "~11min n=2014 raw 5000; W11 raw 5000 draws, "
                 "20-source exclusion face, fourteen-tuple); "
                 "single-process deterministic pre-burn stage (Sobol "
                 "streams + dedup face), zero engine cells burned"),
    },
    "priority": 1,
    "worker_class": "self-contained",
    "lane_owner": "bm-b",
    "data_gates": ("in-runner fail-closed exit 2: (a) "
                   "w11_candidates.json exists -> refuse same-grammar "
                   "rerun TRIAL_LABOR_LAW sec.4; (b) grammar sha drift "
                   "vs FROZEN 128962592feeb8d3 -> refuse; (c) G-MOM "
                   "raw face + G-STD raw face fail-closed anchors "
                   "(r228/r237 probe determinism laws) -> refuse on "
                   "any drift"),
    "entered_at": stamp,
    "finished_at": None,
    "note": ("armed_pending_runner resolved bm-b r442: runner landed "
             "commit f11aea5c3 selftest 47/47; grammar serialized "
             "results/trial_labor_w11/w11_grammar.json same round; "
             "pre-registered TRIAL_LABOR_LAW standing line"),
    "status": "ready",
}
pool["entries"].append(entry)
json.dump(pool, open(P, "w", encoding="utf-8"), ensure_ascii=False,
          indent=1)
pool2 = json.load(open(P, encoding="utf-8"))
assert any(e["id"] == "TRIAL-LABOR-W11-GENERATE"
           and e["status"] == "ready" for e in pool2["entries"])
print(f"pooled TRIAL-LABOR-W11-GENERATE ready at {stamp} "
      f"({len(pool2['entries'])} entries)")
