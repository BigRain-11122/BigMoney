# DIGEST 2026-10-29 — E210/E209: the pages the CEO reads, and the counts that prove themselves

Round r1237, bm-b. Both cards were the only two `ready` entries in the runnable pool, which is
what the open-time watermark red was pointing at (`pool-batch-runnable-idle-low-cpu`).

## E210 — `docquotes` (results/e79/DOCQUOTES-2026-10-29.json)

The count-vs-quote family (E207/E208) audited `results/`. This leg audits the reader side, `docs/`,
because that is what the CEO actually opens.

Five page families, newest page each, its own JSON twin as first trace source, then a bounded
1,200-face corpus:

| measure | value |
|---|---|
| numbers on the pages | 534 |
| sourced from the page's own twin | 471 |
| sourced from the bounded corpus | 61 |
| unsourced | 2 |
| count cell wearing a unit (candidate) | 5 |
| integral value under a unit (ambiguity, not a defect) | 12 |

The two unsourced numbers are both counts (`-701 份`, `4920 … 0 个`) whose producing face sits
outside the 1,200-face bound — the bound is the finding, not a defect.

All five candidates were triaged and all five are value coincidence: a printed "RED: 20% cap"
matching `n_holdings: 20`, and a printed "-86% ~ -14%" return range matching `n_evidence_missing:
14`. On CJK pages there is no shared token to check, so the face publishes the candidate with the
cell that explains it and names the coincidence in its caveats instead of calling it an error.

Wired into `Tools/s6_chain_bmb.py` **after** `daily_report` and `ceo_live_usage`, with a smoke leg
that asserts the ordering (a leg in front of its subject audits yesterday's file and reports clean).

## E209 — `countwitness` (results/e79/COUNTWITNESS-2026-10-28.json)

E207's guard is a word test. This leg supplies the value-level witness: a numeric leaf equal to
`len()` of a sibling list/dict in the same parent.

| measure | value |
|---|---|
| faces scanned | 1,200 |
| counts that prove themselves | 4,702 |
| of which measurement-named | 373 |
| …already caught by the count-word test | 299 (80.2%) |
| …invisible to the word test | 74 |
| witnessed under a non-measurement name | 4,329 |
| leaves skipped below the floor of 2 | 62,372 |

Self-inclusion caught the leg on its first publish: run one wrote 4,702, run two wrote 5,406,
because the face published in between was scanned as input — the study name on disk still carried
the old id so the exclusion list did not match. Renaming to the declared id restored idempotency
(4,702 twice). Both faces are excluded from their own corpora and registered in
`LEVELQUOTE_EXCLUDE_STUDIES` (the E180 pattern: their own names carry measurement tokens, so the
live level-quote leg would read them as quoting faces with no producer).

## Pit 4 — "format preserved" must be compared to the blob, not to a round-trip

The closeout asserted `json.dumps(load(s)) == s` before writing `state.json`, and still churned all
757 lines into a fake diff: the assertion compares the *load/dump* pair, so a line-ending change it
introduces is invisible to it. `state.json` is LF in the repo; the writer had been told CRLF. The
cheap general test is a numstat self-check after every whole-file write — a rewrite that should touch
20 lines and reports 757 is wrong no matter what the in-process assertion said.