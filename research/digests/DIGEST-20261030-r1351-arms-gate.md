# r1351 — the arms face is re-read every round, and "stale" is not "edited"

**Pos:** `scripts/etf_book_phase_atlas_arms.py` (`--check`, selftest 19 → 25) ·
`Tools/s6_chain_bmc.py` leg `etf_book_phase_atlas_arms` · `smoke_test.py` leg
`product: etf_book_phase_atlas_arms`.

## What happened before this round

Two windows did the same work. bm-c's dead window priced the three atlas follow-ups
(buffer k=0.05, 5bp/side, 20bp/side) inline in `etf_book_phase_atlas.py` (+358 lines) and left
it uncommitted; bm-a shipped the same reading as `scripts/etf_book_phase_atlas_arms.py` and
published it at r1163. The readings agree to the last digit on the numbers that matter
(min per-cell delta −0.355pp, max +0.395pp, buffer median −0.030pp, 0 of 12 cells beyond their
own band), so this is one measurement written twice, not two disagreements.

Resolution followed r1314: keep the version that is already wired upstream, and let this window
supply only the half that is missing. The dead window's version is quarantined verbatim at
`K:\Fluxgroup\.codely-cli\quarantine\r1351-atlas-arms-dup\` (diff + 4 faces + 4 research pages
+ digest) rather than deleted, because "we already had that" is a claim that should be checkable.

## The missing half

Nothing read the published arms face back. The atlas had a chain leg; its three arms did not,
and no smoke leg covered either. That is the r1266 line: a verdict that lives only in a file
nobody consumes is not a gate.

`--check` re-derives the whole payload from the four source faces (base + three arms) and
compares it to the face on disk. The interesting part is *which* red it reports:

| state | rc | chain behaviour |
|---|---|---|
| face == re-derivation | 0 | green, 0.1s |
| drift, and a source face is newer than the published one | 2 (`stale`) | pays the declared refresh (a JSON re-read, not an engine), then re-runs the probe |
| drift, and no source moved | 1 (`inconsistent`) | stays red — re-deriving would launder a hand edit |
| published criteria != the rule in the file | 1 (`inconsistent`) | stays red |

Both branches were fired live, not argued: editing one `median_cagr_pp` in
`results/etf_book_phase_atlas_cost05.json` produced
`face is stale: ... drift=.arms.cost05.rows[0].delta_pp (1.37 vs 1.87)` → rc 2, and the chain
leg printed `+refresh(rc=0,0.1s)` and came back green on the restored source.

## The fourth arm: where the toll ceiling is not

The dead window's pool rows asked the next question ("does 'the cadence is quotable' have a toll
ceiling?"). One of them was ignited this round -- 40bp/side, 4x the production toll, 280 engine
runs, 5 workers, 3.5 min -- and added to the same face as a fourth arm (the frozen rule is
untouched; only an arm was added):

| toll | median per-cell delta | between-cell spread | R10 band | R40 band |
|---|---|---|---|---|
| 5bp | +0.71pp | 6.06pp | 3.47pp | 9.00pp |
| 10bp (base) | 0 | 5.22pp | 3.38pp | 9.01pp |
| 20bp | -1.41pp | 3.55pp | 3.29pp | 8.95pp |
| 40bp | -4.19pp | 3.01pp | 3.08pp | 8.86pp |

The toll moves the LEVEL monotonically and dissolves the ORDERING monotonically (the spread
walks toward the band), while the BAND barely moves -- and the R40:R10 ratio rises (2.60 ->
2.88), so the cadence reading survives 4x the toll. There is no toll ceiling for "the cadence is
quotable"; what a higher toll kills first is the difference between configurations.

## Two things this round learned about the gate itself

1. **Compare what a reader sees, not Python types.** `band_by_cadence` keys are ints in memory
   and strings once written to JSON, so a naive deep-compare reported drift on every run.
   The gate round-trips the rebuilt payload through `json.dumps/loads` before diffing.
2. **A relative or out-of-tree fixture path is a crash, not a red.** `os.path.relpath` raises
   `ValueError` across Windows drives, so the fixture legs run through `_rel()`, which falls
   back to the bare filename. A gate that throws is a gate that gets loosened.