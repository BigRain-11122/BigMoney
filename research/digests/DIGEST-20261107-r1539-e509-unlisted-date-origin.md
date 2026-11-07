# E509 — the unlisted date fields, read against other vintages of their own face (r1539 bm-b)

**Card**: `E509-WHICH-OF-THE-17-UNLISTED-DATE-FIELDS-IS-A-FRESHNESS-WITNESS-AND-WHICH-IS-A-CONSTANT`
**Face**: `results/state_tilt/UNLISTEDDATEORIGIN-2026-11-07.json` + `unlisteddateorigin_latest.json`
**Script**: `scripts/e509_unlisted_date_origin.py` (run / check / verify / selftest 20/20)
**Upstream**: E506's published `NODATEWITNESS-2026-11-07.json`

## The question E506 left open

E506 split 68 no-witness faces by what their payload actually holds. One class — faces carrying a
*structured* date under a name outside the witness vocabulary — was a fact about the **name**:
`report_date` and `inception` land in the same bucket although one is the day the face was built and
the other is a frozen literal (`2024-01-01`). E509 asks the counterfactual question the name cannot
answer: **does the value move when the face is rebuilt over new data?**

## How it is read

Two arms, both published per row:

* **vintage arm** — other versions of the same face: dated siblings and archival copies on disk
  (166 readings) and the committed versions of the same path in git history (63 readings). 249
  readings over 20 (face, field) pairs.
* **writing arm** — dict literals / subscript assignments in `scripts/` and `Tools/` that write the
  field name, restricted to files that also name the face (a literal in an unrelated one-off study
  says nothing about this face; the rejected sites are counted, not silently dropped).

A reading is compared with **the newest date anywhere else in the same payload** — what the face
knows about its own data — and the gap is published in days.

## Readings (16 faces, 20 pairs, 8 distinct field names)

| class | pairs |
|---|---|
| freshness witness (ties the anchor in every vintage) | **1** |
| partial (ties in some vintages only) | 5 |
| moves but never ties the anchor | 1 |
| a constant the face was rebuilt under and it did not move | 3 |
| a constant with the axis unexercised (the face itself never moved) | 10 |

* The only strict witness is `asof` in `results/regime_gate_dualarm/latest.json` — it equals the
  newest other date in all four readings (0 days behind every time).
* `asof` in `results/market_clock/call_latest.json` moves, but never ties: the face carries a newer
  `regime_v3.asof`, so the top-level `asof` is the **bar** date, not the face's freshness.
* `report_date` in the two archived `docs/daily_report/REPORT-*.json` copies is partial: 48 readings
  each, ties the anchor in some and lags in others.
* **10 faces (18,198 of 72,500 bytes, 25%) have no unlisted date that ever certifies their freshness.**
  `inception` = `2024-01-01` is the clearest: two books and one composite book carry it, and in
  `results/etf_composite_live/state.json` `inception` equals `last_bar` — a single-vintage equality
  would have read that as a witness, and the second vintage shows it never moved.

## Population: the card said 17, the tree gives 20

E506's own summary counts 16 faces in this class, and the per-row hits yield **20 (face, field)
pairs** over 8 names. The published numbers are the re-derived ones; the delta (+3 vs the card) is
carried in the summary rather than reconciled by hand.

## Two defects caught in-window

1. **Name-global literal attribution.** The first run classed 14 of 20 pairs as "a constant written
   as a string literal" because a literal `"asof": "2026-10-29"` exists somewhere in the tree. The
   writing arm is now scoped to files that name the face, and the vintage arm outranks it: a field a
   committed vintage shows moving is not a constant.
2. **Per-row byte double count.** The first summary summed `bytes` once per row, so a face with two
   unlisted dates counted twice (74,507 → 72,500 after dedupe by face). The smoke leg now asserts
   that the byte total equals the sum over *distinct* faces.

## Verification

`run` rc0 · `check problems=[]` · `verify problems=[]` · **selftest 20/20** (5 of them are the gate
refusing a doctored reading) · S6 leg `unlisted_date_origin` rc0 0.05s · smoke leg `# E509`
standalone 1/1 green and 1/1 red on a doctored face (sha restored `ddc6f0de984f`).

Limits published with the face: a promisor-clone blob that is not local is counted as unread, never
as unchanged; a face written by pandas/JSON templates shows no writing site; an archival copy is a
vintage of the live face and is labelled as such.