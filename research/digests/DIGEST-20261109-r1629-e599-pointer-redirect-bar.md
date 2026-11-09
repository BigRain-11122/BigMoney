# DIGEST r1629 — E599: does a redirect target carry the bar the pointer declares?

- **Round**: r1629 (bm-b) · 2026-11-09
- **Study**: `scripts/e599_pointer_redirect_bar.py` (selftest 59/59)
- **Face**: `results/state_tilt/POINTERREDIRECTBAR.json` (+ `-latest.json`)
- **Card**: `knowledge/METHODOLOGY_ASSETS.md` E602
- **Chain leg**: `pointer_redirect_bar` in `Tools/s6_chain_bmb.py` (rc=0, 1.2s)
- **Smoke leg**: `smoke_test.py` E599 block + `scripts/run_e599_smoke_leg.py` (PASS; `--doctor` 1/1 red)

## Question

E598 (r1625) found exactly one reader in the repo that follows a pointer redirect: it opens
`docs/live_book/latest.json` and then loads `ptr["json"]`. That raised a question E598 could not
answer, because it graded only the keys asked OF the pointer: **does the bar at the far end of a
redirect match the bar the pointer declares?**

## Method

Every `latest.json` face in the repo (28), every string field whose basename ends in an artifact
suffix is a candidate redirect edge (12 edges over 9 faces). Each edge is resolved in order —
absolute, the face's own directory, the repo root, the face's directory by basename — and both
ends are read for a date-stating field (`as_of`, `evidence_cutoff`, `pricing_bar`, `ticket_bar`,
`cutoff`, …). `bar`/`bars` are deliberately not in the vocabulary: a field called `bars` holds a
count (E207).

The key distinction: two dates are only compared when they are stated **under the same field
name**. `cutoff` and `evidence_cutoff` are different quantities; a difference between them is
published as `the_two_ends_state_their_bar_in_different_fields`, never as a disagreement.

## Reading (final, after the repair below)

| | count |
|---|---|
| pointer faces | 28 |
| faces that redirect | 9 |
| redirect edges | 12 (12 resolving) |
| edges → JSON payload | 6 · → non-JSON artifact 6 |
| edges written as absolute paths | 0 |
| edges stating a bar at both ends | 4 |
| agree on the same field | 0 |
| disagree on the same field | 0 |
| stated in two different fields | 4 (2 dates match, 2 do not) |
| pointer states no bar / target states no bar | 1 / 1 |
| modules opening both ends / comparing both bars | 0 / 0 |

The two differing pairs:

- `results/divlowvol_live/latest.json[nulls_evidence]` — `as_of=2026-10-19` vs
  `evidence_cutoff=2026-09-22` (27 days), reference relation, different quantities.
- `results/regime_matrix_p0/latest.json[matrix]` — `cutoff=2026-09-30` vs
  `evidence_cutoff=2026-09-22` (8 days), payload relation. The pointer's 09-30 is the
  **label** cutoff (`regime_axis.label_cutoff`), the payload's 09-22 is the bars cutoff. Both
  statements are true of different quantities; reading the 8-day gap as a regression would be the
  E206 family mistake.

**Nobody checks.** 0 modules open both ends of any edge, so the second half of the card's question
("is the far end checked against the near end") has a plain answer: it is not checked anywhere, by
anyone. The one redirect-following reader E598 found (`smoke_test.py` → `docs/live_book` json) reads
only the target's page, not both bars.

## Defect found and repaired in-round

`results/regime_matrix_p0/latest.json` wrote both redirects as absolute
`K:\Fluxgroup\...\P0-MATRIX-v1-2026-09-30.{json,md}`. This checkout lives on `C:`, so **both edges
dangled** — but the same basenames sit right next to the pointer. That is not a missing payload,
it is a pointer pinned to another root; on any machine whose tree is not at `K:` the face's own
payload is unreachable through its own pointer.

- writer fixed: `scripts/regime_matrix_p0.py` now publishes repo-relative posix paths
- live pointer repaired to the exact value the fixed writer emits (same `cutoff`, same `generated`)
- re-derived: dangling 2 → 0, verdict
  `a_redirect_pins_a_root_that_does_not_exist_and_its_own_payload_sits_next_to_the_pointer`
  → `every_checkable_redirect_states_its_bar_in_a_different_field_and_at_least_one_of_those_bars_differs`

No consumer reads the pointer's `matrix`/`md` fields (grep over `scripts/`, `Tools/`, `firm/`,
`live/`, `monitor/`, `smoke_test.py`: only the writer names them), so the path form change is safe.

## Limitations (published on the face)

- a redirect is a string value whose basename ends in an artifact suffix; a path composed at
  runtime is invisible
- payload vs reference is decided by the key name, and that basis is published per row — a
  payload key carrying evidence would be mis-split
- two ends stating different bars is not by itself a defect: a reference edge names a different
  object by design, which is why the two relations are counted apart
- the reader arm needs the module to name the target basename in its own source; a target path
  built at runtime is not counted