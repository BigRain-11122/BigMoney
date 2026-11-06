# DIGEST 2026-11-07 r1509 bm-b — E484: the 201 vintage names with no ISO date were a spelling fact

Card: `knowledge/METHODOLOGY_ASSETS.md` E484.
Producer: `scripts/e484_undated_vintage.py` (run / check / verify / selftest).
Faces: `results/state_tilt/undatedvintage_latest.json`, `UNDATEDVINTAGE-2026-11-07.json`.

## Reading

Population: E480's 201 `no_date_in_name` members (35 families) — the rows that study classified and
then dropped without opening the file.

| payload class | files | bytes |
|---|---|---|
| datable from a frozen field | 123 | 7,589,943 |
| datable only from a non-frozen field | 5 | 12,517 |
| undatable | **0** | 0 |
| not a JSON object (csv/md/jsonl) | 73 | 2,065,270 |

`payload_comparable_files` = 128, so the "0 undatable" is stated over the population that can be
asked, and the 73 non-JSON rows are named rather than folded in. Verdict:
`every_undated_vintage_name_can_be_dated_from_its_payload`.

**The headline is the name census, not the payload.** All **201/201** of these names carry a date —
in the compact `YYYYMMDD` spelling (`PROFILE-20261028.json`). E480's ISO regex only accepts the
dashed form, so an entire spelling was invisible and the whole population read as "no date in the
name". Nothing was missing from the names; one parser was.

Span check (the date placed against the min..max of the dates the family's own member names state,
either spelling): **125 in span / 3 outside / 0 unmeasurable**. All three outsiders are witnessed by
a field called `first` holding `2005-02-23` — the start of the backtested series, not a write stamp.

The same lens finds what E480 could not see: **123 payload dates equal the compact name date and 5
differ**; of those 5, three are the data dates above and two are real one-day disagreements —
`results/_w280bmc_20261021_probe_receipt.json` and `results/e24_ladder_weighting/WEIGHTING-20261021.json`
both state `2026-10-20` in a payload named for the 21st.

## Why it matters

The retention question E477/E479 kept deferring rests on "can this file be placed in time". For these
201 the answer is yes, twice over: the name places them (compact) and the payload places them (128 of
128 comparable), and the two agree 123 times. A name-based rule does not need an exception for this
segment; it needs a second pattern.

The two one-day disagreements are the only real defect the population contains, and they are exactly
the files E480's own method was structurally unable to audit.

## Pits

1. **A regex that accepts one spelling silently becomes a population filter.** "No ISO date in the
   name" was published as a property of the files; it was a property of the parser. Any "this field
   is empty" census must first ask what spellings the extractor refuses.
2. **A non-frozen witness can be a data date.** `first` = 2005-02-23 makes three files "datable" while
   dating the *series*, not the write. The fix was not a hand-maintained vocabulary of write-stamp
   field names: publish the witness field name verbatim and check the payload date against the name
   date. Disagreement separates the two kinds by itself.
3. **A denominator must be named on the face.** 73 of 201 are not JSON objects. Reporting "0 undatable"
   without `payload_comparable_files` = 128 would let "every file is datable" be read as 201.
4. **A span built from sibling payloads is not the span the names state.** The span here comes from
   member *names* only; a family whose names carry no date at all reads `no_span` (unmeasurable), never
   "outside".

## Cost

`run` re-reads 201 payloads (~1 s); `check` re-derives every tally from the published rows and never
touches the disk; `verify` rebuilds and compares 16 summary keys plus both verdicts.