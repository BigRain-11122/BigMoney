# DIGEST 2026-11-07 r1508 bm-b -- E480: does a dated vintage's payload state the same day?

## What was measured

E477 (bytes), E478 (semantics after clock strip) and E479 (who opens the twin) all took the date of
a vintage **from its file name**. Nobody had checked that the payload agrees. Population: E472's 97
unread vintage families, 571 member files (the twin is the reference and is excluded, as in E478).

Verdict: `every_dated_vintage_file_name_agrees_with_the_date_its_payload_states`.

| class | files |
|---|---|
| `date_agrees` | 269 |
| `date_disagrees` | 0 |
| `no_date_in_payload` | 9 |
| `not_a_json_object` | 92 |
| `no_date_in_name` | 201 |
| `ambiguous_name_date` | 0 |
| `unreadable_member` | 0 |

370 names carry exactly one ISO date; 269 of those have a payload that states a date, and every one
of them is the same day (share 1.0). 9 dated names sit in payloads whose only timestamp is spelled
outside the frozen seven (`run_at` style) -- published as unmeasured, never as a disagreement.

## Method notes worth carrying

* The question is index integrity, not retention: it licenses using the name as the file's date,
  nothing more.
* Date granularity is frozen at YYYY-MM-DD; a payload timestamp with an hour suffix agrees with the
  same-day name. That limit is printed on the face.
* A name with two distinct ISO dates (a range) is `ambiguous_name_date` and never silently resolved
  to the first one; this population has zero of them, so the rule was proven only in the selftest.

## Wiring

* `scripts/e480_vintage_date_agree.py` -- run rc0, check problems=0, verify identical rebuild,
  selftest 36/36.
* Face: `results/state_tilt/VINTAGEDATE-2026-11-07.json` + `vintagedate_latest.json`.
* S6 leg `vintage_date_agree` (0.05s) and smoke leg proven standalone 1/1 green, 1/1 red on a
  doctored face, sha restored.
* Card E480 appended to `knowledge/METHODOLOGY_ASSETS.md`.
* Pool: E480 done; E484 (the 201 undated names -- a name index cannot reach them) seeded.

## Honest wall note

The full smoke suite (~350 legs, 20-30 min) was not relaunched this window; the new leg was proved
standalone in both directions. One accidental full S6 chain start (a `--leg` typo resolving to a
round name) ran ~5 minutes before cancellation, so some downstream faces may carry re-derived bytes
this window -- disclosed, not claimed as this round's work.