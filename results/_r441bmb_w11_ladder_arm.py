# Pre-arm TRIAL-LABOR-W11-GENERATE ladder entry (W10 entry template,
# fourteen-tuple STD axis). Auto-arms only after freeze steps land;
# prereg_frozen gate refuses the candidate DRAFT head by design.
import io, json, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

p = "Tools/fill_ladder_catalog.json"
d = json.load(io.open(p, encoding="utf-8"))
assert not any(e["id"] == "TRIAL-LABOR-W11-GENERATE" for e in d["entries"]), "W11 entry already present"
entry = {
    "id": "TRIAL-LABOR-W11-GENERATE",
    "ticket_ref": "T-2026-09-29-123 wave ticket (opened+claimed same freeze commit per O-1730 immediate law, W8=T-120/W9=T-121/W10=T-122 lineage); W11 candidate = bm-c r237 supply step (STD high-dispersion confirm gate axis std20_hi/std10_hi, MSG-20260929-2015 dual-signal + commit; candidate skeleton = research/TRIAL_LABOR_W11_CANDIDATE_STD_PREREG_DRAFT.md with 10-item adopter checklist; freeze steps per checklist: W10 full-chain consumption trigger + frozen prereg + SEED_REGISTRY three keys 20317000/20317500/20318000 (draft berth 20316000/20316500 collided with bm-a r445 A12 -> +500 re-take per draft clause-5, W9 precedent) + wave ticket same-round claim per O-1730)",
    "prereg_ref": "research/TRIAL_LABOR_W11_PREREG.md (FROZEN 2026-09-29 21:1x bm-b r441 whole-package adoption per W8->W9->W10 adoption lineage; NOT the candidate DRAFT file)",
    "runner": "scripts/trial_labor_w11.py",
    "runner_args": ["generate"],
    "lane_owner": None,
    "priority": 1,
    "enqueue_gates": [
        "prereg_frozen:research/TRIAL_LABOR_W11_PREREG.md",
        "runner_exists",
        "standing_no_judge_inflight"
    ],
    "consumer_plan": "TRIAL-LABOR-W11-GENERATE/SCREEN/JUDGE -> judged verdict face (w11_judge.json) -> s4 intake -> STRATEGY_LIBRARY + TRIAL-* paper accounts -> 48h CEO report + scorecard CEO face; screen null p95 -> next-wave (W12) prereg reference band (verbatim from candidate sec.6 draft plan)",
    "workers_plan": {
        "workers": "worker_cap() pool BelowNormal",
        "priority": "BelowNormal",
        "note": "generation leg = CPU-light census build, W2-W10 machinery precedent; fourteen-tuple axis grid 31,352,832 combos (W10 10,450,944 x3 STD three-value axis), 5,000-draw Sobol per candidate sec.3"
    },
    "data_gates": "runner fail-closed if frozen prereg absent or grammar sha mismatch vs registry (exit 2 honest); append-only grammar registry, same-grammar rerun refused; evidence_cutoff=2026-09-22 (P-5C binding); G-STD runner door asserts probe anchor face decidable 3,363/open 391/std10 399/first-decidable 120 per frozen sec.3",
    "note": "ladder (a) tranche-2 pre-arm: W11 candidate parked 2026-09-29 r237 (bm-c); STD axis = fourteen-tuple cell key per frozen sec.3; entry auto-arms ONLY after freeze steps land (frozen prereg + runner build + SEED_REGISTRY + wave ticket) -- prereg_frozen gate refuses the candidate DRAFT head by design (mirrors W5 r162 draft-head convention); judge pipeline must drain first (standing_no_judge_inflight; W10 judge drained 20:31:29, pool 123/123 done at r441 freeze live-read)"
}
d["entries"].append(entry)
d["consumption_state"]["TRIAL-LABOR-W11-GENERATE"] = {
    "state": "armed_pending_runner",
    "evidence": "freeze commit r441 bm-b: frozen prereg research/TRIAL_LABOR_W11_PREREG.md + SEED_REGISTRY three keys 20317000/20317500/20318000 + wave ticket T-2026-09-29-123; runner scripts/trial_labor_w11.py NOT yet built (runner_exists gate holds); claim-side three-step check still mandatory per r233 pitfall law"
}
d["version"] = "tranche-2 + consumption_state face (bm-c r234) + W11 pre-arm (bm-b r441: TRIAL-LABOR-W11-GENERATE entry added per frozen W11 prereg; tranche-1 five faces all consumed; W10 face consumed 19:42:03)"
io.open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(d, ensure_ascii=False, indent=2) + "\n")
print("ladder entry appended: TRIAL-LABOR-W11-GENERATE (armed_pending_runner)")
