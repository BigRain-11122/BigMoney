# DIGEST 2026-11-10 r1649 bm-b — E630: the callee the caller hands the object to

**Question** — E629 closed the caller arm with a residue: 6 of its 9 call sites hand the receiver
object to *another call inside the caller* (`random_masks(P, ...)`, `rev_masks(P, W_)` before
`simulate(P, ...)`). A write inside that callee happens before the holder is entered, so E629 could
neither see it nor rule it out. Does that callee write the key?

**Reading** — 2 rows / 9 call sites in the population, 11 handoffs once the holder's own self-calls
(3) are separated out. 11 of 11 resolve to a definition in the same module; 0 of them writes the key
on the parameter it receives, 0 touches it in a way the study cannot name, 0 hands it further on, 11
never touch it. All 11 sit before the holder call, so even a write would reach both reads. The callee
arm closes 0 of the 2 rows.

**Verdict** — `none_of_the_11_handoffs_reaches_a_callee_that_writes_the_key_so_the_callee_arm_closes_none_of_the_2_row`

**Lessons**

1. *A handoff list must not contain the holder's own call.* E625's marks fire on any call that
   carries the receiver text, including `simulate(P, ...)` itself, so 14 "handoffs" became 11 real
   ones plus 3 self-calls. Counting them as "the callee is the holding function" would have written
   an unresolvable residue into the face that does not exist; they are published in their own field.
2. *"No handoff in this row" is not "a handoff that cannot be resolved".* Row 2 (`ew6_portfolio.py`)
   has no handoff at all — its callers pass `None` or a name they never write — and an earlier draft
   printed both as "untraced". The row classes now separate them, so the untraced count is a
   statement about a failed trace rather than about silence.
3. *The hop's consequence is the same as the previous one.* A write from the caller side, or from a
   callee the caller hands the object to, happens before the holder is entered, so it reaches the
   dead line and its sibling read alike. `rows_closed_by_the_callee_arm` is frozen at 0 and
   re-derived by the leg.

**Evidence** — `scripts/e630_callee_write.py` (selftest 25/25, build/check/verify `problems=[]`) +
`results/state_tilt/HANDEDWRITE.json` + `handedwrite_latest.json` + `scripts/run_e630_smoke_leg.py`
(1/1 PASS, `--doctor` 1/1 red, face restored byte-identically) + `smoke_test.py` leg E630 +
`Tools/s6_chain_bmb.py` leg `callee_write` (rc0 0.05s) + pool E630 done / E631 seeded.

**Next card (E631, seeded)** — is the sibling read E625 counted the *only* read of that key after the
dead line? If a function has three or more reads, "one duplicate" understates the count and every
downstream face inherits the same denominator.