# DIGEST-20261109-r1633-e606-count-row-compare

**Card** E606 — whether a count that disagrees with its own rows is ever compared.
**Round** r1633 bm-b. **Face** `results/state_tilt/COUNTRYCOMPARE.json` (+`-latest.json`).

## Question

E601 (r1630) measured, on the face side, that 198 of 894 published series sit under a count that
equals neither the row count nor the distinct-row count. That is a statement about the FACE. It
never asked whether any program reads such a face and puts the two numbers side by side — and a
disagreement nobody compares is a number nobody can be contradicted by.

## Instrument

Two existing instruments, reused rather than rewritten (E767 reuse-not-rebuild):

- `e601.scan()` for the population — the same count vocabulary (`e597.COUNT_KEYS`) and the same
  count-block walker, so this face and E601's can be read against each other.
- `e470.sites_for()` for the reader side — the literal opener census (open / io.open /
  Path.read_text / json.load / pandas.read_* / gzip.open, one hop of literal assignment).
- `e468.producer_map()` (by face stem) splits each opener into a writer of the face and a consumer.

Each (face, consumer) pair is graded on two module-level facts: does the module spell any of the
face's count field names, and does it compute a row count anywhere (`len`/`set`/`sorted`,
`.nunique`/`.unique`/`.drop_duplicates`/`.size`/`.shape`/`.count`).

## Reading

| quantity | value |
|---|---|
| published JSON faces scanned | 13,660 |
| faces carrying a count block | 501 |
| series whose count ≠ its own row count | 198 |
| faces carrying such a series | 86 |
| those faces opened by any source | 5 |
| those faces opened by nobody at all | 81 |
| consumer (face, reader) pairs | 4 |
| … that name the count AND compute a row count | 1 |
| … that name the count and never count rows | 0 |
| … that open the face and never name the count | 2 |
| … unreadable (source above the read cap) | 1 |
| faces where at least one consumer compares | 1 |
| writer pairs (excluded from the reader tally, published apart) | 3 |

The single comparing consumer is `scripts/trial_labor_w20.py` on
`results/_r1027bmc_w20_kin_orthogonality.json`, naming `n_bars` and computing `len` — and it counts
rows for its own reason, not to check E601's number.

**Verdict** `some_reader_that_opens_a_disagreeing_face_names_the_count_and_counts_the_rows_so_at_least_one_disagreement_is_checkable_by_a_program`.

The verdict word is weaker than the reading: 85 of the 86 disagreeing faces are unreachable by any
consumer here, and the one that is reachable is reachable by accident. What the face says, the
numbers say: these are publish-to-human faces, not consumed numbers.

## Three self-caught errors

1. **A writer is not a reader.** The first build graded all 7 openers and read "4 of 7 compare" —
   which looks like a working witness. Splitting out the writer (E468 write sites by stem) leaves
   1 of 4. A writer necessarily both names its count and counts its rows: it computed the number
   it printed.
2. **A class must be derived from its own evidence.** The selftest's first fixture hand-set
   `class=C_NAMES_ONLY` while leaving `named_count_fields` empty, and the guard refused it on the
   spot ("grades itself X, the rule says Y"). The fixture now derives its class through
   `reader_class()`, so a fixture cannot claim a class its fields do not support.
3. **"No reader" means "no literal opener".** `e470` also publishes glob landings; this study does
   NOT count them. A sweep like `results/**/*.json` can reach a face no literal names, so 81 must
   not be read as "nothing on this disk could load it". That is written into `limits` and is the
   seeded successor card E609.

## Limits (published on the face)

- population is E601's; a count printed under a name outside `e597.COUNT_KEYS` is not here;
- "disagreement" is `count_value != rows`; a count equal to the row count beside duplicated rows is
  E601's `D_ROWS_DUP` class, not this card;
- readers come from literal openers with one hop of assignment — two hops, a computed base or a
  blob are not seen;
- "names the count" is module-level, so a shared key spelling is graded and flagged
  (`count_key_is_shared_across_faces`);
- "computes a row count" is module-level too: a module that counts rows elsewhere is credited, so
  `COMPARES` is a bound, not a proof of comparison;
- producer attribution is by face stem, so two faces in different directories sharing a stem are
  indistinguishable.

## Evidence

- `scripts/e606_count_row_compare.py` — selftest 18/18; run / check / verify `problems=[]`,
  `verify=identical`.
- `results/state_tilt/COUNTRYCOMPARE.json` + `COUNTRYCOMPARE-latest.json`.
- `scripts/run_e606_smoke_leg.py` — PASS against the published face; `--doctor` 1/1 red with the
  face restored byte-identical (`a630bf5afaaad71b` in and out).
- `smoke_test.py` leg E606 (the full suite was not launched this round — r1499).
- `Tools/s6_chain_bmb.py` leg `count_row_compare` rc=0 93.7s.
- `knowledge/METHODOLOGY_ASSETS.md` card E608.
- Pool: E606 done with `result_ref`; E609 seeded ready.