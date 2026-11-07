# DIGEST 2026-11-07 r1525 bm-b -- E499, pricing the read sites the class delta did not show

**Card** E499-PRICE-THE-READ-SITES-THE-CLASS-DELTA-DID-NOT-SHOW (seeded by r1524 after E498).
**Product** scripts/e499_helperprice.py, results/state_tilt/HELPERPRICE-2026-11-07.json +
helperprice_latest.json, S6 leg `helper_price`, smoke leg E499, scripts/run_e499_smoke_leg.py.

## What was measured
E498 counted 24 read sites a literal census cannot see and left them unpriced. This study prices
all 90 read sites the helper arm attributes to E479's 36 frozen twins, using E483's vocabulary,
and then recomputes each twin's retirement status under four counting sets.

## Readings
- 90 sites priced: pin 49, existence 4, reads-fields-without-asserting 18, bytes-vs-copy 4,
  presence 2, re-derive 4, no-field 9. Strict reader classes (re-derive + pin) = 53; outside = 37.
  Of the 21 helper sites only 4 count.
- Retirement ladder (narrow to wide counting set): strict 34 kept / 2 retirable / 665,250 B;
  +faulting same; +presence and republishing 35 kept / 1 retirable / 94,798 B; every read site
  35 / 1 / 94,798 B.
- The one twin that moves under the strict rule is results/state_tilt/COSTCURVE_latest.json
  (7 members, 570,452 B in its family) whose only reader is smoke_test.py:2830 -- a presence
  assertion on 5 fields. results/state_tilt/BASISRECOVERY_latest.json is retirable under every
  rule, which agrees with E498 leaving it unread.

## Three reusable rules
1. A site price must publish its assertion block: 28 of 90 sites were first priced against the
   whole module because a helper line has no opener to climb from. Resolving the block from the
   line moved re-derive 19 -> 4 and helper readers 14 -> 4.
2. A helper site's payload root is the name bound to the call; only the helper's own body says
   whether that name carries fields. A block that reads fields and asserts nothing had no class
   in the inherited vocabulary and is published as its own (18 sites).
3. "N retirable / X bytes" must ship with its counting set and the intermediate arms -- both
   reader rules are defensible and they differ by 570,452 B, and the strict one would retire the
   family whose last consumer is the smoke suite.

## Pits hit in-window
- `asserting_block()` climbs from an open call; on a helper site it returned the Module, so a
  file-wide scope was answering for one line. Publish the block kind/start/end/resolution per site.
- `e483.payload_roots()` knows only `load/loads/read/read_text/read_bytes`, so `x = _read_json(p)`
  read as "no field is read" -- the exact false negative this study exists to price.
- The ladder is only monotone if it is ordered from the narrowest counting set; the first version
  listed E479's arm first and the monotonicity leg correctly failed.

## Verification
run rc0 | check problems=[] | verify problems=[] (rebuild identical) | selftest 13/13 |
S6 helper_price rc0 0.07 s | standalone leg 6/6 (two doctored arms red).
