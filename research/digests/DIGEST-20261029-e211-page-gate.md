# DIGEST 2026-10-29 — E211: the page audit becomes a gate

Round r1238, bm-b. Open state: watermark green (`py_low_board_clear`), pool 0 ready, smoke 125/125.
The round's product is a guard, not a measurement — E210's 534-number audit only ever ran when a
round happened to call it.

## What shipped

| piece | path |
|---|---|
| leg + ratchet | `scripts/e97_routing.py` mode `pagegate` (selftest 123 → 128, legs L121–L125) |
| gate face | `results/e79/PAGEGATE-2026-10-29.json` |
| declared baseline | `results/e79/DOCQUOTES-BASELINE.json` (2 signatures, `corpus_bound` 1200) |
| chain wiring | `Tools/s6_chain_bmb.py` — `pagegate` immediately after `docquotes` |
| smoke leg | asserts the ordering **and** that a baseline file exists with a `signatures` map |

Live reading: `pages=5 numbers=534 unsourced=2 signatures=2 grown=0 shrunk=0`,
verdict `2_of_534_numbers_on_the_pages_the_ceo_reads_have_no_producer_and_0_new_ones_appeared`, rc 0.
The two are the counts E210 already named (`-701 份`, `4920 中 0 个`), both producers outside the
1,200-face bound.

## Why the signature masks digits

`family | unit context | digit-masked snippet`. `REPORT-2026-10-29.md` and `REPORT-2026-10-30.md`
collapse to one family; `-701 份` and `-702 份` in the same sentence collapse to one signature. This
is the whole reason the leg can sit in the S6 chain: pages churn their values daily, and a ratchet
keyed on values would be red every morning and gone by the end of the week. Growth therefore means
"a sentence that never quoted an untraceable number now does", which is the only thing worth a red.

## Three things kept honest

- **Shrink is permitted and published.** A fix must not trip the gate; `shrunk` reports the
  disappearing signature with both counts and the leg stays green.
- **The bound goes into the baseline.** `corpus_bound = 1200` is stored beside the signatures because
  the trace corpus is a newest-1,200-face window: a face rotating out can un-source a number without
  any page changing, and that must be readable as bound rotation rather than read as a new defect.
- **A missing baseline says `baseline_seeded`, never silence.** First run declares what it found; a
  gate that re-seeds silently is a gate that always passes.

## Self-inclusion, once more

`results/e79/PAGEGATE-*.json` and `DOCQUOTES-BASELINE.json` both live inside the corpus the sweep
scans, so the gate's own numbers would be trace sources for tomorrow's page. Both are excluded from
the trace corpus by study name — the same defect E209 hit on its first publish (4,702 → 5,406) and
E210 recorded; publishing twice and comparing is the cheap test that caught both.