# -*- coding: utf-8 -*-
"""r472 bm-b: TRIAL-LABOR-W14-GENERATE pool entry submission (fill_
ladder_catalog pre-armed entry consumed after gates MET: prereg_
frozen MET [bm-b r471 freeze] + runner_exists MET [this round:
scripts/trial_labor_w14.py landed, selftest 53/53, three-command
identity first-runs honest rc=2, grammar sha16 a231bf10940e7878
pinned] + standing_no_judge_inflight MET [pool zero running judge
faces; W13 chain landed 12:28]; double-file law r399: shared + lane
bm-b same bytes same operation)."""
import json
import time

P_SHARED = "results/runnable_pool.json"
P_LANE = "results/runnable_pool.bm-b.json"
pool = json.load(open(P_SHARED, encoding="utf-8"))
if any(e.get("id") == "TRIAL-LABOR-W14-GENERATE"
       for e in pool["entries"]):
    print("refuse: entry exists")
    raise SystemExit(2)

entry = {
 "id": "TRIAL-LABOR-W14-GENERATE",
 "ticket_ref": "T-2026-09-30-128 wave ticket (opened+claimed same "
   "freeze commit per O-1730 immediate law, W8=T-120/W9=T-121/W10="
   "T-122/W11=T-123/W12=T-124/W13=T-125 lineage); W14 candidate = "
   "bm-c r276 supply step first-to-origin (RESI trend-extension "
   "position + CNT yang-day density dual new axes, MSG-20260930-1525 "
   "dual-signal + commit 04759cf69; bm-b r470 same-window independent "
   "dual draft zero-collusion cross-validation yield/adoption "
   "MSG-20260930-154x, bm-b takes freeze step per berth open-"
   "adoption clause; bm-c r277 gap probe resi30/cntd10 facts "
   "MSG-20260930-155x + twin cross-val 39/39; member-set "
   "adjudication GATE-RECHECK evidence-forced RESI{resi60_hi} x "
   "CNT{cntd5_hi,cntn20_lo} = 6 multiplier; seeds 20327500/20328000/"
   "20328500 three-step law ALL GREEN facts results/"
   "_r471bmb_w14_seed_law_facts.json)",
 "prereg_ref": "research/TRIAL_LABOR_W14_PREREG.md (FROZEN 2026-09-30 "
   "16:5x bm-b r471 adoption freeze window per berth-first-to-hold + "
   "open-adoption clause, W13 timeline mirror; NOT the candidate "
   "DRAFT files)",
 "runner": "scripts/trial_labor_w14.py",
 "runner_args": ["generate"],
 "lane_owner": None,
 "priority": 1,
 "consumer_plan": "TRIAL-LABOR-W14-GENERATE/SCREEN/JUDGE -> judged "
   "verdict face (w14_judge.json, reform-face first wave: "
   "eligible_reform + top-3 dual face per O-1058 five-step chain) -> "
   "s4 intake -> STRATEGY_LIBRARY + TRIAL-RESICNT-* paper accounts "
   "-> 48h CEO report + scorecard CEO face; screen null p95 -> "
   "next-wave (W15) prereg reference band",
 "workers_plan": {
   "workers": "worker_cap() pool BelowNormal",
   "priority": "BelowNormal",
   "note": "generation leg = CPU-light census build, W2-W13 machinery "
           "precedent; eighteen-tuple axis grid 1,693,052,928 combos "
           "(W13 282,175,488 x6: RESI 2-value x CNT 3-value "
           "adjudicated member set), 10,000-draw Sobol per candidate "
           "sec.3 (O-1132 expansion)"
 },
 "data_gates": "runner fail-closed if frozen prereg absent or grammar "
   "sha mismatch vs registry (exit 2 honest); append-only grammar "
   "registry, same-grammar rerun refused; evidence_cutoff=2026-09-22 "
   "(P-5C binding); G-RESI/G-CNT runner door asserts probe anchor "
   "faces resi60 decidable 3363/open 390/first-decidable 120 + "
   "cntd5 3364/137/119 + cntn20 3364/265/119 per frozen sec.3 "
   "(three-probe closure: bm-b r470 facts + r471 supplement facts + "
   "bm-c r277 gap facts, twin cross-val 39/39 byte-level)",
 "note": "runner LANDED bm-b r472 (dead r472-session half-work "
   "adopted wholesale per r471 attrition law + Slice-B completed: "
   "selftest 53/53 incl. W14 own faces [eighteen-tuple grammar "
   "1,693,052,928 / resi+cnt stream append zero disturbance / "
   "28-source exclusion loader / G-RESI+G-CNT real-face fail-closed "
   "anchors / mask+engine parity vs W9+W13 / screen CSV contract "
   "resi/cnt columns]; three-command identity first-runs real-data "
   "rc=2 honest [screen-prep ALL gates PASS + candidates-absent tail "
   "refusal; screen-finalize generate-pending refusal; judge-prep "
   "screen-absent refusal]; grammar sha16 a231bf10940e7878 pinned at "
   "w14_grammar.json serialization)",
 "status": "ready",
 "shards": [
  {"key": "generate-0of1",
   "status": "ready",
   "checkpoint": "results/trial_labor_w14/w14_candidates.json "
                 "(single-shot product = completion marker; "
                 "refuse-if-exists guard)",
   "owner": None,
   "owner_since": None}
 ],
 "entered_at": time.strftime("%Y-%m-%d %H:%M:%S"),
 "entered_by": "bm-b",
 "worker_class": "self-contained"
}
pool["entries"].append(entry)
pool["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
dump = json.dumps(pool, ensure_ascii=False, indent=1)
for path in (P_SHARED, P_LANE):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(dump)
print("pool entry submitted (double-file law): TRIAL-LABOR-W14-"
      "GENERATE ready entries=%d" % len(pool["entries"]))
