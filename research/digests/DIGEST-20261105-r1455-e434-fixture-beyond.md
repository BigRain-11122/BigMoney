# DIGEST 2026-11-05 r1455 bm-b — E434: the fixture-shaped population is 30 of 310, not 21

**Card.** `E434-WHICH-PARAMETER-SITE-OUTSIDE-E428-UNPLACED-SET-IS-FIXTURE-SHAPED` (cpu-only).
**Face.** `results/state_tilt/FIXTUREBEYOND-2026-11-04.json` + `fixturebeyond_latest.json`.
**Producer.** `scripts/e434_fixture_beyond.py` (run / verify / selftest).

## The question

E428 published "21 fixture-shaped parameter-directory write sites among its 310". The 21 were
counted over the **35 rows its narrow index could not place**, not over the 310 sites it scanned.
E432 priced those 21 and left the other 289 unexamined. E434 asks: how many of the whole
population are fixture-shaped, and where do the callers of the ones outside the published rows
point them?

## Readings

| reading | value |
|---|---|
| parameter-directory write sites in the scan | 310 |
| fixture-shaped over the whole population (E428's own heuristic) | **30** |
| inside the rows E428 could not place | 21 |
| outside them (priced here) | **9** |
| → temp directory | 6 |
| → runtime name | 3 |
| → repository directory the caller spells | **0** |
| reachable from a production caller | 5 (of 9) |
| a reader could open what is written | **0** |
| a reader spells the same file name only | 2 |

Verdict (recomputed by the gate, never carried):
`the_fixture_shaped_sites_outside_the_unplaced_rows_all_take_a_temp_or_a_runtime_directory_and_no_reader_opens_what_they_write`.

The nine rows (file:function:line — class — reach):

```
scripts/e388_schema_accretion.py:_fixture:469            runtime_constant  selftest
scripts/options_iv_freeze_counter.py:_mk_archive:205     runtime_constant  selftest
scripts/sina_mf_accept.py:_write_panel_rows:335          runtime_constant  selftest
Tools/heartbeat_write.py:_fixture:324                    temp              production
Tools/lane_round_liveness.py:_fixture:289                temp              production
scripts/e303_recover_unmeasurable_basis.py:_fixture:487   temp              production
scripts/e395_conditional_write.py:_fixture:654            temp              production
scripts/e396_face_basename_suffix.py:_fixture:543         temp              production
scripts/mass_trial_report.py:_write_fixture:261          temp              selftest
```

## Three rules

1. **A count is only a population statement if it was taken over the population.** The published
   sentence mixed a 35-row universe with a 310-site universe — a factor of 10.33 — and every
   downstream reader would have inherited it as a fact about the 310.
2. **The priced set must be a union read from both upstream faces** (E432's rows + E428's own
   fixture rows, keyed by file/function/line). A hand-written list of 21 drifts the first time a
   helper moves, and a row E432 dropped would reappear as newly found.
3. **A name class is not a reach class.** "Fixture-shaped" is a name heuristic: 5 of these 9 are
   reached from production callers, and still none of them writes anywhere a reader can open.

## Wiring

- smoke leg `# E434 (r1455 bm-b)` — closes the class/reach/inside+outside partition against the
  published face and refuses a row that either upstream face already priced.
- `scripts/run_e434_smoke_leg.py` — 1/1 green, and 1/1 red on a doctored fixture-shaped total
  with the face restored byte-identical (`67e59556d790c4e3`).
- S6 leg `fixture_beyond` in `Tools/s6_chain_bmb.py` — full re-derivation over the live corpus.
- methodology card `E434` in `knowledge/METHODOLOGY_ASSETS.md`.

## Bounds (published, not claimed)

The heuristic is E428's, deliberately: this study measures the population the sentence was about
and does not re-cut the class. `runtime_constant` means "the caller passes a name", not "the
directory is unknown". A reader that composes the name from parts does not match, so `no_reader`
means "no reader spells this name". No writer and no reader was edited or executed by this study.