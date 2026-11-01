# DIGEST 2026-11-01 r1360 (bm-b) — E340: the tree awards itself allowances off its own faces, and 17 of the 18 grants it takes are customary

**Card:** E340 → **Face:** `results/state_tilt/ALLOWANCE-2026-11-01.json` → **Script:** `scripts/e340_who_authorizes_whose_allowance.py`

## The question

E337's repair let a consumer study read an opt-in allowlist out of the producing study's **published face**, so
that "a study cannot award itself an allowance" — while the allowance itself stayed a frozen constant in source.
That is one hop from self-authorization: any permission-shaped field on a face can be read back by the script
that wrote it, and a producer that reads its own output grants itself whatever it last wrote. The card asked for a
census of every permission-shaped field, its readers, and whether the grants are pinned by mechanism.

## What was measured

| axis | reading |
|---|---|
| faces parsed | **12,519** (≤4 MB, quarantine excluded, this study's own face and mirror excluded) |
| faces carrying a permission key | **316** |
| permission-shaped entries | **409** over **98** distinct keys |
| python files scanned | **3,044** |
| read back by the publishing script | **22 entries over 22 faces** |
| split by access shape | compared against a freshly computed value **4** · asserted **0** · gated **0** · **bound 18** |
| grants with no selftest leg quoting the key | **17 of 18** |
| self reads from a durable study / from scratch only | **21 / 1** |
| self entries where the value is also a frozen source literal | **2** |

Class histogram over all 409: `self_compared 4 | self_bound 18 | foreign 224 | producer_unread 159 | unread 4`.

The family split is the first correction: the card named six word families as "permissions", but **expected 121,
tolerance 124 and baseline 73 dominate** the population while the actually permissive words are small — allow 20,
whitelist 36, permit 28, exempt 15, optin 8. A tolerance is a quantity, not a grant; counting them as allowances
would have inflated the "self-authorized" headline by an order of magnitude.

## The verdict, and why "customary" is the finding

`the_tree_awards_itself_allowances_by_reading_its_own_faces_and_some_of_those_grants_are_only_customary`

22 of the 409 entries are read back by the script that publishes them — the exact shape E337 guarded against, one
hop over. Of those, **4 compare the disk value against a freshly computed one** (that is a real check), **0 assert
it**, **0 gate on it**, and **18 merely bind it to a name whose use is downstream and invisible on that line**.

Those 18 are the risk: a bound value is a grant whose decision lives somewhere the face cannot show, and the pin
is the only remaining mechanism. **17 of the 18 have no selftest leg quoting the key or its frozen literal** —
so the grant survives by custom, not by machinery. Only `baselines` in the allocation/guardrail studies carries a
pin. The named list is published (`self_granted_and_customary`, capped at 10 rows) so a reader can find them.

## Defects caught in this round

1. **The census read its own output back in.** The face publishes `by_family = {"permit": 28, ...}`, so an
   unexcluded face is itself "a face that publishes a permit key": the first two rebuilds carried **16 self rows**
   (8 family keys × itself and its `_latest` mirror), inflating entries 425 → 409 once excluded. Fixed with
   `OWN_FACE_PREFIXES` and a selftest leg on a temp fixture (E207/E332 family).
2. **`asof_head` inside a deterministic face.** It names the commit the corpus was read at, so it moves on every
   commit — the S6 leg would have gone red the moment the study landed (E338 family). It is now excluded from
   re-derivation, still published, and its shape is pinned by a selftest leg instead of its value.
3. **The smoke leg was wrong, not the face.** It required `reading_producer ∈ producer`, but `producer` is the
   name/path-match set and `per_producer` is the file actually seen on the face's write path; `reading_producer`
   legitimately lives in the second. Re-read, not silenced (E336 pit 3 family).

## Verification

- `selftest 35/35`; `run` → dated face + `allowance_latest.json`; `verify` → **0 problems** (re-derives off disk,
  ~90 s: 12.5k json parses + 3k source scans).
- Smoke leg extracted verbatim (`scripts/run_e340_smoke_leg.py`): PASS; a doctored face (`unpinned_grants: 99`,
  verdict swapped) was caught with two named problems and the published bytes were restored identically
  (sha256 equal).
- Chain leg `permission_allowances` wired into `Tools/s6_chain_bmb.py`.

## What a reader should take away

A permission-shaped name on a face is not a mechanism. The tree has 409 of them; 224 are read by somebody other
than their producer (that half is healthy), 159 by nobody at all, and 22 by their own producer — of which the
**18 bound grants, 17 unpinned**, are the set where "the value I wrote is the value I read" is the only thing
standing between a study and its own allowance.