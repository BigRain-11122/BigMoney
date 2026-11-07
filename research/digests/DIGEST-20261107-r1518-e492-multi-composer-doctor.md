# DIGEST 2026-11-07 r1518 bm-b — E492: who the extra composers of a multi-composed `*_latest.json` are

**Card** E492 · **Face** `results/state_tilt/LATESTDOCTOR-2026-11-07.json` (+ `latestdoctor_latest.json`)
**Script** `scripts/e492_multi_composer_doctor.py` (run / check / verify / selftest 29/29)
**Pool row** E492 (seeded r1516, burned r1518)

## Question

E491 published 51 latest names with two or more static composers and called that class
"several composers". A sample of the extras are leg runners (`scripts/run_eXXX_smoke_leg.py`)
that copy a face, change a published count, run the leg, and put the original back. Two
questions follow: how many of the extras are doctor harnesses, and does any of them leave a
mutated face behind?

## Reading (2026-11-07)

| quantity | value |
|---|---|
| multi-composed faces | 51 |
| composer sites | 171 |
| extra composer sites | 41 |
| — doctor harness | **24** |
| — one-off `_rNNN` repair | 2 |
| — another producer | 24 |
| faces whose extras are all harnesses | **19** |
| faces with no producer composer at all | **13** |
| faces with a harness that writes once (no restore in that source) | **2** |
| published copies that do not parse as JSON right now | **0** |
| leftover mutant artefacts (`_mut` / `_bak` / doctored) in state_tilt | **0** |

Verdict: `a_minority_of_the_extra_composers_are_doctor_harnesses` — no face is left in a
mutated state. The two single-write harness faces are `deadprereg_latest.json` and
`dirfield_latest.json`; nothing is on disk from them now.

## Three transferable lessons

1. **"Several composers" is not "several producers".** Label the composer before counting it.
   19 faces have harness-only extras, and for 13 faces the only visible writer is a harness —
   the correct reading there is "the producer folds out of static reach", not "two producers
   maintain this face".
2. **The write site count is what makes a harness safe.** A harness writes the same name
   twice (doctored copy, then the original back); a harness that writes once has no restore
   channel in its own source, so what stays on disk depends on whether that run finished.
   Publishing the count turns a code-reading impression into a checkable field.
3. **The census pollutes its own population.** The first build counted
   `latestdoctor_latest.json` itself: the study's own producer is excluded from the scan, so
   only its harness remained visible and the face was published as "an all-harness face". The
   self face is now excluded and disclosed (`self_faces_excluded`) — the E180/E207 family,
   recurring.

## Limits

Role is a file-name rule (a harness under another name reads as a producer). Two write sites
say a restore is *possible* in that source, not that it ran. `parses_as_json=true` shows the
copy is readable now, not that its content came from the producer. Leftover artefacts are
listed by name, not by provenance.

## Verification

```
python scripts/e492_multi_composer_doctor.py run       # rc0
python scripts/e492_multi_composer_doctor.py check     # problems=[]
python scripts/e492_multi_composer_doctor.py verify    # problems=[]  (rebuild identical)
python scripts/e492_multi_composer_doctor.py selftest  # 29/29
python scripts/run_e492_smoke_leg.py                   # 1/1 green
python scripts/run_e492_smoke_leg.py --doctor          # 1/1 red, face sha restored
python Tools/s6_chain_bmb.py 1518 --only multi_composer_doctor   # rc0 0.07s
```