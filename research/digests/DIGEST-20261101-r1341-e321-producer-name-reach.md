# DIGEST 2026-11-01 r1341 bm-b -- E321 producer-side name reach

**Question.** E320 left 134 unresolved and 62 ambiguous gates whose face publishes nothing that names
or fingerprints the gated quantity. If the face is silent, is the producer too?

**Method.** Population = `DECOYRESOLVE-2026-10-31.json` rows with class unresolved|ambiguous (196).
Producer lookup, publish-site location and constant definition come from E312
(`producers_for` / `publish_sites` / `constant_definition` / `code_tokens`); E321 adds only the
template fallback for dated filenames and the quantity-word reading of the definition.

**Reading.**

| class | rows |
|---|---|
| named by the producer, constant names a quantity | 21 |
| ... of which module-level (publishable as-is) | 7 |
| constant published but names nothing | 139 |
| no producer publishes the key | 31 |
| face unreadable / no producer names the face | 5 |

Verdict `the_producer_names_more_than_the_face_does_but_not_all_of_it`. Note that "named" is not
"unambiguous": a named constant narrows the span only if its own definition is the only reading.

**Pit.** The first run reported 154/196 producer-less because the needle was the dated basename while
writers emit `NAME-<cutoff>.json` templates. A search bug that looks exactly like a finding.

**Files.** scripts/e321_quantity_name_reach.py (selftest 12/12, verify 0 problems),
results/state_tilt/QUANTITYNAME-2026-10-31.json, quantityname_latest.json, smoke_test.py leg
`_name306`, knowledge/METHODOLOGY_ASSETS.md card E321.
