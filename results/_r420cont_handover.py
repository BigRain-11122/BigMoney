entry = ("- [2026-09-29 08:5x r420-cont bm-a] HANDOVER 5x window entry (OVERDUE BACKLOG DISCLOSED): bm-a last signed window was round 340 (2026-09-27 17:5x, covering R321-340); "
"rounds R341-R420 carried NO bm-a-signed 5x window (cause: r400-419 S0-conflict demotion chain + dead sessions, rounds ran maintenance-only with zero claims; honest disclosure, no backfill fabrication). "
"CROSS-WINDOW RECONCILIATION BACKBONE (already on-file, cross-read not re-derived): bm-b r410 5x entry did the three-machine full-window reconciliation 2026-09-28 09:00 -> 2026-09-29 05:4x "
"(ledger head 301,180->328,987; bm-a products therein: R394/395 W3-SCREEN burns, R338 SINA-CONSTRUCT-P1 finalize, T-91 full-system chain, MINUTE_FEED/ETF_DAILY/SENTIMENT-AXES family per window listing); "
"bm-b r415 + rider (08:26/08:32) closed W6-JUDGE full-chain (293 judged, G1 total-zero 0/293, E[FP]=14.65, G2 0) and pool 110/110 first full-clear. "
"bm-a THIS-WINDOW FACTS (R416-420, direct session knowledge): r416-418 = merge-back escape branches machine/bm-a-r416/r417/r418 (S0 conflict demotions per r400 playbook, zero claims); "
"r419 closeout = dead-session S7 product harvest + 21-face canonical merge-back LANDED on main (12fa3e709..6eb3da16f FF) + W6-SCREEN prep salvage + pit-89 W6-SCREEN fix-first; "
"r420 (dead, killed pre-S7 by task timeout) + r420-cont (this round) = S6 chain harvest (51 faces), pit-93 two-step merge vs bm-b r415 (18 UU canon-resolved), escape branch machine/bm-a-r420 + atomic FF main push (076c1ba46..7bd9be1fe..2b19933fb), post-merge pool face sync_face settle; "
"REGIME_GUARD v3 T-21 wiring face armed in paper jsons (active=false pre-10-01 date gate, tri-gate law intact). "
"LEDGER LIVE-READ ANCHOR: trials ledger head = 333,432 (results/trial_labor_w6/w6_judge.json trials_ledger.total=333432, prev 333139+293 batch linear, evidence_cutoff 2026-09-22) - read live this round, matching bm-b r415 rider claim 333432. "
"NEXT 5x = round 425 bm-a.")
with open("research/HANDOVER.md", "a", encoding="utf-8", newline="") as fh:
    fh.write(entry + "\n")
print("HANDOVER entry appended", len(entry), "chars")
