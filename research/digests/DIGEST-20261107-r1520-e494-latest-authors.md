# DIGEST r1520 bm-b — E494: the other 49 multi-composed latest faces

**Card**: E494-DO-THE-OTHER-49-MULTI-COMPOSED-FACES-CARRY-A-COMPOSER-THAT-AUTHORS-A-PAYLOAD-OF-ITS-OWN
**Face**: `results/state_tilt/LATESTAUTHOR-2026-11-07.json` + `latestauthors_latest.json`
**Instrument**: `scripts/e494_latest_authors.py` (selftest 32/32, check 0, verify [])
**Wiring**: S6 leg `latest_authors` (rc0 0.06s) · smoke leg `E494 ...` (standalone 1/1 green, doctored 1/1 red)
**Card**: `knowledge/METHODOLOGY_ASSETS.md` E494
**Evidence cutoff**: 2026-11-07

## Question

E493 answered "who owns the bytes" for the 2 faces E492 flagged as single-write harnesses.
The other 49 multi-composed names were never asked: does any extra composer (doctor harness
or one-off `_rNNN` repair) write a document it constructed itself into the published path,
and how many of those writes have no restore in the same source?

## Answer

| reading | value |
|---|---|
| faces examined | 49 (of E492's 51; E493's 2 excluded and named) |
| extra composers (harness / one-off repair) | 24 (22 / 2) |
| faces with no extra composer | 25 |
| write sites on the published basename | 47 (24 constructed, 23 backup) |
| composers that author a payload | **24** |
| …that put the original back | **23** (22 of them in a `finally`) |
| …that never restore | **1** |
| faces whose disk payload has no explanation | **0** |

The single unrestored author is `bandswitch_latest.json` ←
`scripts/_r1495_bandswitch_mirror_repair.py`, a one-off repair with one write site at line
21. Its own docstring says the dated face is the evidence and is not rewritten; the mirror
is re-published **from** it with only `generated` moving. The provenance arm confirms it:
the repair reads exactly one other basename (`BANDSWITCH-2026-10-30.json`) and the disk
mirror equals that file once `generated` is removed. So the copy on disk is that dated
payload plus a stamp — a deliberate re-publication, not a leaked mutant.

The producer arm does **not** re-derive it (`e302_universe_switch_backfill.py` builds a
different shape today, 191 faces vs the pinned 195). That is the expected consequence of the
pin, and it is why "differs from a fresh build" is published as a separate reading from
"who wrote it" (E493's rule, second application).

## Reconciliation with the parent face

Compared by **quantity**, not by line: 24/24 write-site counts agree with E492's
`write_site_count`, and 0 restore labels disagree. The first draft compared line lists and
reported 31 "the parent missed this" and 39 "the parent credited something else" — every one
of those was an offset: E492 records the enclosing statement's first line (including `try:`
and read-mode opens), this build records the `open` call's line.

## Rules measured, not assumed

1. "The second write" is not "the restore". E492 decides *mutates then restores* from a
   write-site **count**; that proxy was right on all 24 here, but it cannot tell a restore
   from a second authored payload. Classify the **argument**, not the count.
2. Two instruments counting different units will always disagree line by line. Reconcile on a
   comparable quantity (site count, presence of a restore), and only then call a difference.
3. "No restore" splits into (a) a diagnostic that forgot and (b) a deliberate
   re-publication. Price the second kind with a provenance arm: which files does this
   composer read, and does the disk copy equal one of them beyond the clock fields.

## Bounds

Population is E492's extras only — a writer E492 never saw is outside this study. Recognised
write forms are handle writes, `json.dump`, and the copy/move families; a write performed by
a subprocess or a library call in another file reads as "no static write site", not as
"nothing wrote". Names are traced two hops; three-hop payloads are published as
unclassifiable. The provenance arm compares equality after clock fields are removed and does
not say which copy is correct.