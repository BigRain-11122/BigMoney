# DIGEST 2026-11-02 r1383 -- the corpus a census counts is not in git

## What this round opened on

r1382's digest closed with the honest line that names the next repair:

> Reproduction of a published census on today's disk remains **unmeasurable**, not verified.
> Pinning a corpus by content digest (and teaching `build()` to accept a snapshot) is the real
> repair and is not in this round.

This round does the first half and prices what it finds.

## The pin

`scripts/e361_census_corpus_pin.py` imports the study's own `corpus()` (E323's walk of
`scripts/Tools/live/monitor/firm` for `*.py`, itself excluded) and records every member as
`(path, sha256 of LF-normalised text, bytes)`. `pin_id` is sha256 over the sorted
`path<TAB>sha256` lines: two runs that read the same bytes carry the same address, and a run that
read different bytes cannot be mistaken for a reproduction. 15 selftest legs pin the accounting --
CRLF/LF equivalence, order independence, one changed file is exactly one `changed` row, rename is
`removed`+`added`, an empty corpus and a duplicated path both refuse instead of publishing a green
zero.

Each member is then checked against `HEAD` (one `ls-tree` for blobs, one `hash-object
--stdin-paths` for the working tree), so "git cannot supply this byte" is a measurement rather
than an assumption.

## What it found

    corpus        2362 sources, 44 MB of text
    tracked       2258   not in HEAD 104 (4.40%)   tracked-but-dirty 3
    git supplies  2255 clean blobs (95.47%)   cannot supply 107
    dirty         Tools/gpu_face.py, Tools/s6_chain_bmb.py, scripts/e321_quantity_name_reach.py

Every published corpus count in this repo -- 2337 (REFUSALCAUSE-2026-10-31), 2341 (REACHWIDE),
2354 (POINTERONLY), 2355 (INVISIBLETAIL) -- is **above** what git can supply. So no
checkout of any commit reproduces any published corpus count, and the "summary does not re-derive"
family was never only a leg problem.

The composition of the 104 is the part that changes the conclusion: **101 match
`.gitignore:_r[0-9]*`** -- round scripts are machine-local by standing law (r1081 repo-slim birth
gate), so their absence from git is policy, not a lapse. The other **3 are study producers that
are neither ignored nor committed**: `e230_hysteresis_toll.py`, `e359_census_scaffolding_split.py`
(both published studies; E359's face `SCAFFOLD-2026-11-02.json` was untracked too) and this study.
The two real gaps are closed in this commit.

Which means the durable finding is a counting defect, not a delivery one: a census that walks the
filesystem counts the machine's scratch pile, and the scratch pile grows every round by
construction -- so the published number is a property of this disk, not of the repository.

The same classifier was pointed at the outputs, because a face has the identical question. Before
the delivery below: of 148 dated faces, 23 untracked and **36 tracked-but-dirty**. After it:

    results/state_tilt dated faces   149
    tracked 149   untracked 0   tracked-but-dirty 36

36 of 149 dated faces -- statements about a fixed day -- are not the bytes HEAD holds.

Reproduction is now measurable rather than argued. `verify` fired on the round's own work before
the repin (`added 3`: the three helper scripts written after the pin), then after the repin:
`pin_id 7ce257a3ca23eb63 ... reproduces=True, added 0 removed 0 changed 0`.

## What this round does NOT claim

* `build()` does not accept a snapshot yet: the pin exists, but a census cannot be re-run *against*
  it. `hydrate` lays the pinned text down for a future round; nothing consumes it yet.
* The 36 dirty faces are **not** healed here. Which of them is today's face rewritten by a later
  round and which is a restore is not distinguished -- that needs the same per-path treatment this
  study gives the corpus, and it is the named next step.
* The full smoke suite was launched detached at 14:03 and had not finished inside the round wall;
  the new E361 leg was executed verbatim out of `smoke_test.py` (E355 rule) and PASSes.
* The pin is a snapshot of one instant. It is deliberately not on the S6 chain: it costs ~3 s but
  its answer changes with every file any lane writes, and a leg demanding today's corpus equal
  yesterday's pin would be E360's defect one layer up.