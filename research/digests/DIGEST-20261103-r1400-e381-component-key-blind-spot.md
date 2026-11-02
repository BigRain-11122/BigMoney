# r1400 / E381 -- the census keys a join by its operands

**Card.** `E381-WHY-DOES-THE-UPSTREAM-READER-CENSUS-MISS-A-LITERAL-READ` (cpu-only, entered by
bm-b r1398). `scripts/etf_book_bridge.py:369` reads `results/etf_book_production/latest.json` through
`json.load(open(os.path.join(OUT_DIR, "etf_book_production", "latest.json"), encoding="utf-8"))`, and
every operand of that join folds to a string. E377 nevertheless published the face among the faces
"no resolved sink keys". Which side is wrong?

**Decision.** The census is wrong, and not where the card guessed. The universe rule is intact -- the
site *is* inside it. The path is lost one step later, in the key projection.

```
e347.values_in :133    join(...) -> ['results', 'etf_book_production', 'latest.json', 'utf-8']
e350._face_bindings :139   keeps the operand ending .json -> ['latest.json']
e350._face_key              no known root survives -> basename fallback -> 'latest.json'
```

So the face is keyed; it is just keyed under a name that is not its path, which is the ambiguity
`_face_key`'s own docstring calls "the unsafe direction".

**Measured, not decreed.** Corpus 2,418 sources / 5,231 load rows. The published keying names 857
faces (E377's union of dump sinks and load bindings); re-keying each load row from its own operands
names 635, of which 12 published-on-disk faces are named only by the second reading, split by cause:

| cause | count | repair |
|---|---|---|
| `the_published_keying_names_it_by_its_basename_only` | 6 | key the joined path, not its operands |
| `the_published_keying_never_names_it_because_both_helpers_accept_only_._json` | 6 | widen the suffix filter (e350:139 and :187) |
| `the_published_keying_never_names_it_and_no_suffix_rule_explains_that` | 0 | -- |

Rolling those into one number would have shipped "component keying hides 12 faces", and half of them
would have survived any fix to the key projection -- hence the split into two named causes with the
site published beside each one.

Of E377's 36 blind-spot faces exactly 2 move under the joined keying:
`results/etf_book_production/latest.json` (the card's own, basename cause) and
`results/im_ic_pair_runs.jsonl` (suffix cause). The other 34 stand: E377's bill is real for them.

**Evidence.** `scripts/etf_book_bridge.py:369` binding `card`, operands
`['results', 'etf_book_production', 'latest.json', 'utf-8']`, published key `['latest.json']`, joined
key `results/etf_book_production/latest.json`, face present on disk.

**Pits recorded.**

1. A key that resolves is not a key that keeps the path -- the fold happens in `constants()`, the loss
   happens in the projection, and only the second one is a defect.
2. Two causes with one symptom: a basename-keyed `.json` and an unkeyed `.jsonl` both read as "no
   reader". A single counter would have merged them and named the wrong repair.
3. `python -c` under Windows PowerShell loses every double quote in the argument, so a probe written
   with `"..."` arrives as bare names (`NameError: name 'scripts' is not defined`). Single-quote
   probes, or write a file.

**Wiring.** `scripts/e381_component_key_blind_spot.py` (run / verify 0 problems / selftest 15/15);
smoke leg E381 executed verbatim out of `smoke_test.py` (1/1 PASS); S6 chain leg
`component_key_blind_spot` (verify, no corpus scan); face
`results/state_tilt/COMPONENTKEY-2026-11-03.json` + `componentkey_latest.json`; methodology card E381.