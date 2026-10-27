# E172 -- the deadband is a sweep, not a constant (r1207 bm-b)

Face: `results/e43_tilt_4member/TILT3SIGNBAND-20261027.json`
Code: `scripts/e39_panel_census.py` (mode `tilt3signband`; `run_tilt3signsign`'s
burn path reused via the new `deadband_bp=` seam, selftest 521 -> 552).
Pool row: `E172-TILT3SIGN-DEADBAND-SWEEP` (watermark red lane, pool batch).

## The question

E169 (r1205) declared a 10bp monthly deadband and published raw vs deadband
agreement side by side. On `2024_now` the deadband rate came out *worse* than the
raw rate (23.5% -> 18.8%). One constant cannot tell an anti-correlated era from a
noisy one, because dropping months removes evidence as readily as it removes
noise. So the deadband is swept 0 / 10 / 25 / 50 bp and the number of months that
survived each band is published beside every rate.

## Result

| era | months | 0bp | 10bp | 25bp | 50bp | months kept | verdict |
|---|---|---|---|---|---|---|---|
| pre2017 | 44 | 56.8 | 61.5 | 63.9 | 67.9 | 44 / 39 / 36 / 28 | aligned at every band |
| 2017_2020 | 48 | 45.8 | 44.4 | 42.1 | 40.7 | 48 / 45 / 38 / 27 | anti at every band |
| 2021_2023 | 36 | 44.4 | 39.4 | 33.3 | 20.0 | 36 / 33 / 27 / 20 | anti at every band |
| 2024_now | 34 | 23.5 | 18.8 | 17.2 | 17.4 | 34 / 32 / 29 / 23 | anti at every band |
| full | 162 | 43.8 | 42.3 | 40.8 | 38.8 | 162 / 149 / 130 / 98 | anti at every band |

* **No era goes thin at any band** (`first_band_with_any_thin_era = null`; the
  6-month floor never bites, 23 months survive the widest band even in the
  shortest era). 2024_now's low rate is therefore not the band choosing its
  sample: it is low at 0bp over all 34 months.
* **The widest lever is 2021_2023**: 44.4 -> 20.0 (span 24.4pp) while its verdict
  never crosses the 50% line. The band moves the number a lot and the reading not
  at all -- both are published.
* **Direction differs by era**: pre2017's agreement *rises* with the band
  (56.8 -> 67.9), the other three fall. pre2017's agreement is carried by its
  large months; 2021_2023's and 2024_now's by their small ones.
* Era levels (`tilt_sign`, `engine_sign`, `signs_agree`) are identical at all
  four bands **by construction** -- a deadband filters months and never edits a
  return. The face says so per era (`signs_band_invariant`), so four identical
  sign rows cannot be read as four findings.

## Controls

* **Zero-band identity**: band 0 reproduces E169's published raw rate and month
  count exactly (`abs(x) >= 0` always holds), pinned in the selftest.
* **Support disclosure**: every band carries `months_outside_deadband`, and a
  cell under the floor is labelled `thin` rather than quoted.
* **One burn path**: the sweep calls `run_tilt3sign(..., deadband_bp=)` -- no
  second implementation.

## Honest limits

* Descriptive census: no gate, no verdict on the book, no prereg, no trial count.
* The sweep is a sensitivity table on an already-published reading; it selects no
  band. The quoted band remains the one declared before the first burn (10bp).
* The deadband cannot speak to whether the era *level* differs -- that is E169's
  era table and E171's screened twin.

Selftest: `python scripts\e39_panel_census.py selftest` -> 552/552 PASS.