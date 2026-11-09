# DIGEST 2026-11-09 r1630 bm-b — E601 does a duplicated row show anywhere in the face that counts?

**Question.** E597 (r1626) measured that all 542 annualisation blocks carry a bar count and nothing
else, so a duplicated row moves a published CAGR silently. That is a statement about a missing
witness. It never asked whether the witness exists somewhere else in the same face, or whether it
agrees with the number the face prints.

**Population.** All 13,650 JSON faces under `results/**` and `docs/**` (461 unreadable, above the
1 MB read cap or malformed), of which **501 state a bar count** — the same count vocabulary E597
graded, so the two faces can be read against each other.

**Measurement.** Per counted face: the witness it carries (dedupe field / first-last bar identity /
count only), the series it publishes beside that count (measured, not guessed: rows, distinct rows,
duplicate rows, and the bar-key distinct count), and how its count lines up with those rows.

**Readings.**

| | faces |
|---|---|
| state a bar count | 501 |
| also publish the rows that count is about | 295 (58.9%) |
| publish a number no published data can contradict | **206 (41.1%)** |
| publish a dedupe field or a distinct count | 3 |
| publish first+last bar identity | 20 |
| publish a count key and nothing else | 478 |
| already publishing a duplicated row right now | **0** |

Count-vs-rows: of 894 measured series, 198 sit under a block whose count equals neither the row
count nor the distinct-row count, and 696 sit beside no count at all. Zero series have a count that
equals the row count; zero have a count that equals the distinct count. So where a count and rows
coexist they already disagree, which is the opposite failure to the one E597 feared.

**Finding.** The count is not a witness. It is computed from the rows, so a duplicated row enters
the count by the same path and the receipt cannot fail. The only shapes that can self-check are
(a) publishing the rows (a duplicate is then visible *in the rows*, though never in the count) and
(b) a dedupe or distinct count (3 faces). First/last bar identity is **not** a witness for an
interior duplicate — the ends do not move — which is why `face_class()` asks only whether the rows
are published and does not credit identity.

**Limits, published on the face.** Count vocabulary and block walker are E597's (a count under
another name is outside the population). A duplicated row is a whole-object repeat after a json
round-trip; two rows sharing a bar with different values are two rows (selftest arm 8 pins it). At
most 5,000 rows per series and 6 series per face are measured, declared in `limits`; the first
draft published all 22,460 series and produced an 11 MB face, so the cap is a size decision written
down rather than a silent truncation.

**Wiring.** `scripts/e601_dup_witness.py` (selftest 30/30, `verify=identical`), face
`results/state_tilt/DUPWITNESS.json`, S6 leg `dup_witness` (rc0 11.3s), smoke leg E601 which
re-derives every class and every count match from the published rows and refuses a verdict the
counts do not force. Methodology card E605.

**Window pit.** `e597.walk_blocks` returns `(at, node)` pairs; handing the list straight to
`witness_class` feeds a dict to a regex (`TypeError: expected string or bytes-like object`) — the
same tuple-blindness that costs a debug cycle every time this walker is reused.