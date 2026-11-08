# DIGEST — E572: which of the three receipt-vs-sentence disagreements is a different run

Round r1600 (bm-b), 2026-11-09. Card E572 (seeded by r1597, ready in the pool). Lane: cpu-only,
static. Face: `results/state_tilt/RECEIPTRUNID-2026-11-08.json` (+ `receiptrunid_latest.json`).

## Question

E569 joined 38 receipts to the sentence a round report printed about the same run and found three
where the printed numerator differs from a recount of the receipt's own rows
(`_r1246bmb` 25/25 vs 28 rows, `_r1285bmb` 7/7 vs 1 row, `_r406bma` 6/36 vs 36 rows). It published
the difference and declined to say which side was wrong. E572 decides each from the file's own
bytes plus git, and publishes the witness that fired.

## Answer — three files, three different causes, 0 undecidable

| file | printed | derived | class | witness |
|---|---|---|---|---|
| `_r1246bmb_s6_chain.json` | 25/25 | 28 | `wrong_count_in_the_prose` | the sentence cites this receipt's own log token (`r1246bmb_s6`); file ts 12:36:14, sentence commit 12:37:50, mtime == own ts |
| `_r1285bmb_s6_chain.json` | 7/7 | 1 | `family_sentence_against_a_subset_receipt` | the sentence labels itself `--only` and names the family; the receipt holds one leg (`pool_deliverable`) |
| `_r406bma_s6_chain.json` | 6/36 | 36 | `receipt_rewritten_after_the_sentence` | the sentence says "JSON absent"/"had DIED at leg 6/36"; the file on disk is the 36/36 rerun committed as `round 406-cont` |

So one of the three is a real prose defect and two are artifacts of the join: a family count is not
the receipt's row count, and a receipt committed by a *later* round is not the run the sentence
describes.

## Rules measured, not assumed

1. **"Numerators differ" ≠ "the count is wrong."** Align the two scopes first (family vs subset,
   dead run vs rerun). Two of three "defects" here are the instrument's.
2. **When the receipt is untracked, `mtime == its own ts` is the evidence that nobody rewrote it.**
   Two of the three receipts are not in git at all; an empty `git log -- <path>` must not be read as
   "never ran".
3. **A sentence that names the receipt's own log must print the file's own number** — the only
   class in this population that can be decided in one step.
4. **A round number appears in commit messages before the round runs** (`round 1246`'s earliest
   mention is 3.9 days before the receipt), so commit time is a witness about text, never a proof
   of ordering. Published as `commits_naming_the_round` + `span_sec`, and never used in `classify`.

## Bounds published, not claimed

`leg_names_are_a_prefix_of_the_table` is in `unnamed_witnesses`: E568 recovers a leg **count** per
round, not a list of leg names, and none of the three rounds had a table recovered
(`rounds_with_a_recovered_table = 0`). The name-prefix arm is therefore not asserted, and a count
was not passed off as a name list.

## Wiring

- S6 leg `receipt_run_identity` → `python scripts/e572_receipt_run_identity.py check` (rc=0 0.04 s,
  re-derives every class, every witness and the three-way split from the rows).
- `verify` rebuilds the face from the live inputs and compares classes row by row
  (`VERIFY PASS 3 rows re-derived`).
- `selftest 18/18`, including the negative arms: a hand-written verdict, a class without its
  witness, an invented class and a count that does not re-derive are all refused.

## Same window, a red the previous round found and left open

r1598 claimed "smoke #E571" while `smoke_test.py` ended at the E569 block, so the E571 card was
published unguarded. The E571 block is now appended to the suite (mirroring the E568 block: face
verdict re-derivation, population re-derivation, the int-keyed-miss trap, plus two mutation arms).
Exercised standalone in both arms: PASS with `receipts=328 stating=243 int_keyed_miss=231`.
Note that the full suite was **not** launched this window (no leg filter, ~20 min, r1499).

## One honest discrepancy left standing

Appending the block proved a research claim wrong in a small way: `dialect_only_disagreements_here`
is **not** a subset of E561's 17. It counts every stated receipt whose round is written as something
other than an int (210 decimal + 16 label = 226), so the field name promises "disagreements" and
carries "non-int dialects". The smoke leg now re-derives it from the dialect table and publishes
the number as what it is; renaming the field belongs to the next window (it is inside a face other
consumers already read).