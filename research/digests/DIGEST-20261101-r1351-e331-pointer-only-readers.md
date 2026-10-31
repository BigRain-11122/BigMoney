# DIGEST 2026-11-01 r1351 bm-b -- E331: pointer-only readers, and the corpus helper's blind tail

**Card** E331. **Face** `results/state_tilt/POINTERONLY-2026-11-01.json` (+ `pointeronly_latest.json`).
**Verdict** `every_pointer_only_reader_raises_at_the_file_or_guards_it_and_every_pointer_it_names_resolves_today`.

## What was asked

E330 named the tree's single two-reference decision (e242's `_face_file`, pointer first, pinned date
second) and found it unpinned. E327 measured which readers go through a `_latest` pointer and whether
the cutoff survives. Neither asked what a **pointer-only** reader does when the pointer is not there:
that reader has no fallback, so a missing file is its whole answer. The card asked for the count and,
for each reader, whether the miss is an explicit branch, a raise, or a failure far from its cause.

## What the tree says (44 pairs, 19 families, 2,284 sources)

| class | pairs | meaning |
|---|---|---|
| pointer-only reader | 24 | loads `<stem>_latest.json`, names no dated cut of that stem |
| reference without a reader | 11 | the name is published in a census/dict and never loaded |
| chain with a variable first | 6 | `for fn in (name, "<stem>_latest.json")` -- E329's chain, not this card |
| writer only | 3 | the source produces the pointer |

Handling of the 24 readers: 9 let the open error name the path, 6 test existence first, 4 wrap the
load in `try`, 2 default to `{}`, 2 branch on the value, 1 has its `None` absorbed by the callee.
**Zero silently swallow a miss.** Disk half: 0 pointers absent, 0 pointers whose stated cut has no
dated sibling, 2 pointers that state no cutoff at all, and 3 families that cannot be judged because
the pointer is their only published form (`_n3r1_probe`, `_n3r2_probe`, `pack`).

## The four rules that each caught their own bug

1. **A helper name is not unique.** `_read`/`_dump`/`_face` are redefined in dozens of studies; a
   corpus-wide name table resolved four *writers* as readers. Resolve through the source's own
   definition first, keep the corpus table as a fallback, and give each helper a `writes` flag so an
   `open(..., "w")` line is never a load site.
2. **The class follows the load site, not the wording.** Bound-but-only-written is a producer
   (3), and named-but-never-loaded is a reference (11). Classifying from the occurrence text alone
   put 14 pairs in the wrong bucket, which is why the study's first headline was a headline about
   its own bug.
3. **A guard must sit on the loaded value's own expression.** `or {}` on a *later* statement is not a
   guard for the load above it: scoping it to the expression moved 10 rows to 2 and flipped two
   "guarded" readers to loud and one to soft-then-callee.
4. **"Missing" has four states, and one of them is not judgeable.** `per_member_gamma_latest.json`
   sits beside `PER-MEMBER-GAMMA-2026-10-30.json` and `call_latest.json` beside `CALL-2026-10-27.md`;
   comparing raw stems across `.json` only reported 5 unresolvable families that all resolve once
   stems are normalized and `.md` is admitted. A family with no dated sibling at all cannot be
   judged at all -- publishing that as "unresolvable" is a false alarm with the shape of a finding.

## The bound this study hit, and it is bigger than the study

The corpus helper (`e326.code_lines`) drops a triple-quoted block "to its end", so an odd number of
`"""` tokens in prose puts the scanner in doc mode for the rest of the file. **22 of 2,284 sources
lose their tail**: `e231_band_path_test.py` 531 of 795 lines, `e312_gate_operand_identity.py` 424 of
743, `e330_unpinned_choice.py` 729 of 835. Every corpus census in this family (E319, E321, E323,
E325, E326, E327, E329, E330) inherits that blind spot; E331 found it because `e312`'s
`up = _read(UPSTREAM)` lives in the invisible part and the row first read as "unresolved". The list
is published in the face rather than fixed in place, because changing the helper silently changes
every upstream count.

## How to apply

- Write a pointer-only read as *either* an existence test or a `try`, never as a bare
  `json.load(open(path))` behind a soft helper: the soft helper is what moves the failure away from
  the file name.
- When a census says "zero", publish the rejected lines (22 prose literals here) and the classes you
  put aside (3 writers, 11 references) -- zero-with-a-cut and zero-with-a-proof are different facts.
- Before trusting any corpus-wide number in this repo's E3xx family, check whether the source is on
  the invisible-tail list.

**Files** scripts/e331_pointer_only_readers.py (selftest 24/24, verify problems=[]) ->
results/state_tilt/POINTERONLY-2026-11-01.json + pointeronly_latest.json; S6 leg
`pointer_only_readers` (~45s); smoke leg "product: every reader that reaches a face only through a
pointer is counted with what a missing pointer does to it, and the scanner's own blind spot is
published".