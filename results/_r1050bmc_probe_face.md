verdict: ADMIT
bands: {"A": [569701, 571700], "B": [571701, 571900], "a_lo": 569701, "a_hi": 571700, "b_lo": 571701, "b_hi": 571900}
leg0: {"rows": 249, "tail": "W251-registered+FINALIZED (bm-c own-wave complete)", "w251_splice_landed": true, "w251_bands": {"A": [567501, 569500], "B": [569501, 569700]}, "w250_bands": {"A": [565501, 567500], "B": [545101, 545300]}, "w251_finalize_landed": true, "w251_finalize_anchors": {"ledger_total": 976535, "merged_n": 550120, "skill_line_delta_k_lift": 0.0001}, "chain_relation": {"w250_total": 974335, "w251_total": 976535, "ledger_delta": 2200, "k_delta": 2200}, "inflight_upstream": false, "waits_upstream": "NONE (W251 complete: registered+FINALIZED; the W252 FREEZE is UNBLOCKED at seat time -- prereg derive = next window FIRST ACTION on the post-W251 universe)", "owner_rows": 241, "bmc_rows": 71, "bma_rows": 129, "bmb_rows": 41, "ordinal": 242, "bmc_ordinal": 72, "bmc_ordinal_note": "bm-c

leg1: {
 "ARITH_A": [
  569501,
  571500
 ],
 "ARITH_B": [
  569701,
  569900
 ],
 "A": [
  569701,
  571700
 ],
 "hops_A": 1,
 "A_hop_chain": [
  {
   "hop": 1,
   "window": [
    569501,
    571500
   ],
   "jump_to": 569701,
   "refuser_pts": [],
   "refuser_bands": [
    [
     569501,
     569700
    ]
   ]
  }
 ],
 "B": [
  571701,
  571900
 ],
 "hops_B": 1,
 "B_hop_chain": [
  {
   "hop": 1,
   "window": [
    569701,
    569900
   ],
   "jump_to": 571701,
   "refuser_pts": [],
   "refuser_bands": [
    [
     569701,
     571700
    ]
   ]
  }
 ],
 "B_naive": [
  569701,
  569900
 ],
 "B_naive_refused_at_start": true,
 "B_hop_lands_inside_A": false,
 "B_lands_above_own_A": true,
 "A_semantics": "A arithmetic continuation from the REGISTERED W251 A tail 569_500+1 = 569_501..571_500 is REFUSED at naive start on the post-W251-REGISTERED universe (the REGISTERED W251 B band 569_501..569_700 sits INSIDE the naive A window = staircase re-emergence affects A too; the W251 prereg sec.5 item5 A-CLEAN projection was a pre-W251-universe face, superseded live per r587); the walk hops past the W251 B tail 569_700 -> A first-clean 569_701..571_700 (hops=1, first A-hop since the W239 staircase era); forward-monotone non-rotational r587 enforced in-walk; A base >= registered prior-wave B tail+1 floor relation",
 "B_semantics": "B walk from the REGISTERED W251 B tail 569_700+1 = 569_701 is CLEAN at naive start but the naive window 569_701..569_900 lands INSIDE the own-wave W252 A first-clean window 569_701..571_700 (staircase re-emergence face, per the W251 prereg sec.5 item5 projection face superseded live) -- the own-A reservation standard leg hops B past the own-wave A tail 571_700 to the staircase landing 571_701..571_900 (B lands above own-A, base==own-A tail+1 face re-emerges); B_hop lands-inside-A=false leg; live trace recorded verbatim",
 "relation_asserts": {
  "A_clean_at_naive_start": false,
  "A_staircase_hop_past_W251_B": true,
  "A_base_ge_priorB_tail_plus1": true,
  "B_clean_at_naive_start": false,
  "B_base_above_W251_tail": true,
  "AB_mutual_exclusion": true,
  "B_hop_lands_inside_A": false,
  "B_lands_above_own_A": true,
  "W250_W251_bands_respected_A": true,
  "W250_W251_bands_respected_B": true
 }
}

leg2: {"conflicts": 0, "seed_admit_gate": ["seed_admit_gate rc0 base=569701 span=2000 checked=2000 verdict=FREE", "seed_admit_gate rc0 base=571701 span=200 checked=200 verdict=FREE"]}

leg3: {"origin_vacancy": true}

leg4: {
 "W253p_A_naive": "571701..573700",
 "W253p_A_first_clean": "571701..573700",
 "hops_A": 0,
 "W253p_A_naive_refusers_seeds": [],
 "W253p_B_naive": "571901..572100",
 "W253p_B_first_clean": "571901..572100",
 "hops_B": 0,
 "W253p_B_lands_inside_W253p_A_naive": true,
 "note": "W253+ projection on the pre-W252 universe (assuming the W252 seat bands declared here register verbatim). The W253 freezer MUST re-derive on the post-W252 universe AND reserve the own-wave A window when deriving B -- never transcribe r587; staircase face re-emergent since W251 (B lands above own-A): re-read the live trace, do NOT assume the A-base==prior-B-tail+1 or B-base==own-A-tail+1 equalities."
}
