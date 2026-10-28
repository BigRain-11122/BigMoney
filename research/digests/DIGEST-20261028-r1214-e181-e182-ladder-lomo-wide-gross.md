# E181 + E182 - the fixed leg survives every drop, the rotating leg's net is 56% cancelled movement

Round r1214 (bm-b), 2026-10-28. Two pool units burned on the shared E179 load path
(`_tilt3signname_burn`, one panel load per leg, no new engine pass).

- Faces: `results/e43_tilt_4member/LADDERLEVELS-20261027.json`,
  `results/e43_tilt_4member/WIDESIDEGROSS-20261027.json`
- Legs: `scripts/e39_panel_census.py` modes `tilt3ladderlomo` / `tilt3widesplit`
  (selftest 590 -> 605, +15 hermetic legs)
- Cutoff: 2026-10-27. Descriptive census: no gate, no prereg, no trial count.

## E181 - the ladder levels survive every single-member drop; pre2017 is the only single-member level

E179 published the ladder side per holding and its shares (510500 owns 61.89% of
pre2017's +1018.2bp, 588000 owns 32.3% of 2021_2023's -923.5bp and 41.1% of
2024_now's +1088.6bp). The open question was whether those era LEVELS are that
holding in disguise. Answer: no.

Leave-one-member-out, re-weighting the survivors to stay fully invested and
re-annualising on the months that survive the drop:

| era | full level bp | biggest member | share | survival |
|---|---|---|---|---|
| pre2017 | +1018.2 | sh510500 | 61.89% | survives_every_drop |
| 2017_2020 | +1004.8 | sh510050 | 38.08% | survives_every_drop |
| 2021_2023 | -923.5 | sh588000 | 32.33% | survives_every_drop |
| 2024_now | +1088.6 | sh588000 | 41.14% | survives_every_drop |
| full | +597.5 | sh510500 | 37.21% | survives_every_drop |

`eras_level_is_single_member = ["pre2017"]`, `eras_level_flips_under_drop = []`.
So the ladder's four era signs are book statements, and pre2017 is the one level
that is a single holding's level (a concentration disclosure, not a flip: dropping
510500 still leaves +388bp). Join against E179's published ladder level:
max abs diff 0.000216 bp, i.e. the same computation.

Honest: the re-weighting makes the drop a DIFFERENT book (four names at 1/4
instead of five at 1/5). Subtracting the dropped contribution instead would
compare a partially invested book against a fully invested one and understate
every drop by exactly the dropped weight. A month whose only member is the
dropped name is excluded from both sides and published as `months_unholdable`
(empty here), never read as a zero return.

## E182 - the wide side's net is 0.44 of its gross, and the biggest carrier moves against it

E176 published the wide book's net repair delta only. Per holding:

| era | net bp | gross abs bp | net/gross | names moved |
|---|---|---|---|---|
| pre2017 | 0.0 | 0.0 | - | 0 |
| 2017_2020 | 0.0 | 0.0 | - | 0 |
| 2021_2023 | +30.2 | 42.4 | 0.71 | 7 |
| 2024_now | +49.6 | 113.1 | 0.4387 | 45 |
| full | +17.1 | 33.1 | 0.5175 | 52 |

Nothing cancels to zero (`eras_cancelling = []`) and no single name's removal
flips the net sign (`names_whose_removal_flips_the_net = {}`), so this is not a
single-name story in either direction. But 2024_now's +49.6bp is a residual over
twice as much gross movement, and **its largest single carrier is negative**:
sh510580 -14.5bp (-29.3% of the net), then sh510310 -6.4, sz159925 -5.6,
sh510100 -4.6, against sh561980 +4.1. The net is a thin sum of 45 offsetting
repairs, which is precisely what a reader of "+49.6bp" cannot see.

Join against E176's `wide_book_delta_bp`: exact, 0.0 bp in every era.

Honest: the wide book re-picks every month, so a per-name delta mixes a holding
that was repaired with a name that entered or left on a different date -- the
same membership caveat E176 carries, and the reason this face is descriptive.

## Why the pair belongs together

Both legs ask the same question of two different book shapes. The fixed leg's
answer is "one level, four signs, one concentration": a zero delta there is five
zeros (E179) and its levels survive any single drop (E181). The rotating leg's
answer is the opposite failure mode: its delta is real but thin, and per-holding
detail is what shows that half the movement cancels.