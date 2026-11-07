# DIGEST 2026-11-07 r1535 bm-b — E506: what the 725 no-date certifications actually witness

**Card**: E506-WHAT-DO-THE-725-CERTIFICATIONS-WITH-NO-PARSEABLE-DATE-ACTUALLY-READ
**Face**: `results/state_tilt/NODATEWITNESS-2026-11-07.json` + `nodatewitness_latest.json`
**Script**: `scripts/e506_nodate_witness.py` (run rc0 / check problems=[] / verify problems=[] / selftest 37/37)
**Chain leg**: `Tools/s6_chain_bmb.py 1535 --only nodate_witness` → rc0 0.05 s (`results/_r1535bmb_s6_chain.json`)
**Smoke leg**: `# E506 (r1535 bm-b)` run standalone 1/1 green; `--doctor` 1/1 red, face byte-identical after restore (sha 5d747486c259)

## Question

E503 priced 2932 (read-only leg, face) relations and published 725 of them as certifying a
face whose payload carries no parseable date, so its age cannot be computed at all. That was
one opaque number. This study reads the 68 distinct faces behind those relations and asks what
each one *does* carry: a date under some other field name, the same witness name one level
down, a date inside a log or a source-text cache, or nothing at all — and whether the face is
also writer-free, which would make it both unageable and unrefreshed.

## Reading (2026-11-07)

68 faces / 739 relations (E503 published 725; the chain grew by 14 relations since, and both
numbers are in the face). The population splits three ways:

| witness class | faces | bytes |
|---|---|---|
| structured date outside the witness list — top-level unlisted name | 15 | 71,151 |
| structured date outside the witness list — witness name below the top level | 5 | 129,680 |
| structured date outside the witness list — nested unlisted name | 1 | 1,349 |
| **structured total** | **21** | **202,180** |
| only incidental dates (log lines, prose, source-text caches) | 12 | 1,559,868 |
| no date anywhere — only `st_mtime` is left | 35 | 2,327,999 |

- **No declared witness: 47 faces / 3,887,867 B.** 35 of them hold no date at all, and for
  those `st_mtime` is not an age either: this tree materialises every file at checkout, so the
  measured mtime floor is 21 days and every such file reads exactly 21 days old (E453).
- **Writer-free: 29 faces / 2,967,295 B.** Nothing in the chain writes them, so "no witness"
  and "no refresh" apply to the same bytes.
- **Certifying legs: 738**, and **738 of them mention a date field name somewhere in their
  script** (`certifying_legs_testing_existence` = 601). The whole-script reliance axis is
  published as `mention_axis_informative: false`: it cannot separate "reads this face's date"
  from "reads the file, or mentions a date field for another face".
- 56 of the 68 faces arrive through a template leg, so one absent file would have been priced
  as one absent face if the templates had not been resolved per match.

The best field samples are unusually clear about what a witness-list fix would buy: `asof`
(4 faces, incl. `market_clock/call_latest.json`, `m6_regime5/latest.json`,
`regime_gate_dualarm/latest.json`), `report_date`, `cutoff_pin`, `generated_for_bar` — but also
`inception` (three `etf_*` state files, values 2024-01-01 / 2024-01-01 / 2026-10-23) and
`is_end` (three `p1e_nulls_M_*` faces, all 2024-12-31). Those last two are **constants that
cannot age anything**; a blanket extension of the witness list would turn them into fresh
dates. That is what E509 is seeded to price.

## Self-caught

The compact-date arm (`\b(?:19|20)\d{6}\b`) matched *inside* longer tokens and left `kind=None`,
so two rows were published as "structured date under a top-level field" while their samples
were `D-20261104-05` (a decision id) and `T-2026-10-01-141 s1+s3` (a citation). The fix is the
rule the arm should have had: a date is structured **only when it is the whole value**. After
the fix 6 faces left the hidden bucket and 12 more moved into incidental-only — the published
numbers above are the corrected ones, and three selftest legs plus a gate check pin the rule
(a hit with no usable kind, or a hidden class resting on a prose hit, fails the guard).

Second self-caught, about the round's own tooling rather than the study:
`python Tools/s6_chain_bmb.py nodate_witness` does not select the `nodate_witness` leg — the
first positional argument is the **round number**, so that call started three full-chain runs
(20:19 / 20:24 / 20:30). They were killed in-window; the correct form is
`s6_chain_bmb.py <round> --only <leg>`.

## Reusable conclusions

1. **"No date" is not one bucket.** Splitting it into structured-hidden / incidental / none
   changes the remedy completely: 21 faces would be aged by a witness fix, 35 cannot be aged by
   any field rule, and 12 need a parser rather than a key.
2. **A date in the payload is not a freshness witness.** One of the seventeen candidate fields
   (`inception`) is a literal constant; extending a witness list without reading the writer
   turns a constant into a fake age.
3. **The cheapest-hit sample is the evidence, so publish it.** The two false positives above are
   visible in one line of the face; without the sample they would have been invisible.
4. **A reliance axis that fires 738/738 is not an axis.** Publishing
   `mention_axis_informative: false` is the honest form of "we tried to measure this and the
   measurement is uninformative", and the verdict does not rest on it.