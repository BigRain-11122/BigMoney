# r1380 — an identity check whose two sides are one literal is a spelling check

bm-c, 2026-10-31. Follows r1379's closing pointer: "read the 19 identity-checked rows for
the opposite defect — an identity check that pins the wrong key is as blind as none —
starting with the `wild_route_lab` pair."

## What was asked, and what `wild_route_lab` actually does

`wild_route_lab.build_panels_from_cache()` was the smallest key set in the census (`shape`
only). Reading it ended the question in the face's favour: it asserts
`meta["generated"] == "2026-09-24 03:42:50"` before returning any panel, so a regenerated
cache aborts rather than serving. The census had the wrong key list for it (it lists the
literal keys it reads for the shape assertion, not the provenance gate), which is a
census limit, not a defect in the face.

## The defect, one row over: `p1e_neighbor_corr.run`

```python
CUTOFF = "2026-09-22"
def _selfconsistent(path):
    d = json.load(open(path))
    return (... and d.get("evidence_cutoff") == CUTOFF)
...
out = {"evidence_cutoff": CUTOFF, ...}   # the writer writes the same constant
```

The reader compares the stored field against `CUTOFF`; the writer wrote `CUTOFF` into that
field. Both sides are one literal. The guard can catch a hand-edited file and nothing else:
a moved `REJECT_LINE`, a moved `ANCHOR_TOL`, an added verdict pair, a changed `MATERIALS`
list, or a repaired bar in the bm-b lane panel all leave it green, and the 2026-09-26
product is then reused as a checkpoint for a rule it was never computed under.

This is the r1374/r1377 shape (a replay keyed on something that does not move with the
world) with the key replaced by a constant instead of a date. A date at least moves with
the calendar; a constant moves with nothing.

## Cure

`inputs_sha256()` digests exactly what the verdict is a function of: the frozen constant
block (`CUTOFF`, `IS_END`, `REJECT_LINE`, `ANCHOR_TOL`, `F2_MIN_COMMON`, `MATERIALS`,
`VERDICT_PAIRS`, `ADVISORY_PAIRS`, `PROBE_ANCHORS`) plus the panel it reads — every `.npy`
and `.json` under the bm-b lane cache, by size and sha256 of the bytes.

`_selfconsistent()` now requires: digest present and equal, `probe_anchor.all_ok` true,
`pairs` non-empty, and the cutoff. An unreadable panel returns `None` and `None` is never
clean — on this host (no bm-b lane cache) the old product is a MISS, not a cache hit. The
published 2026-09-26 verdict is therefore **not** silently reusable any more; bm-b's next
run recomputes it. The constant block has not changed, so nothing contradicts the recorded
`pass` (max|corr| 0.4829 vs the 0.7 line) — what changed is that it can no longer stand in
for a rule it was not computed under.

Stated limit, not papered over: the digest covers the inputs, not the conclusion. A
hand-edited verdict with an untouched `inputs_sha256` still reads as clean.

## The reusable class, measured

`Tools/live_value_cache_audit.py` gained a fourth evidence class: a function is
`identity_pin_is_self_written` when it compares a stored identity field against a
module-level literal that the same module also bakes into a payload it writes. New field
`identity_pins` per row, new summary counters `identity_checked_against_own_constant` and
`faces_with_a_self_written_identity_pin`.

Two refinements were needed to keep the number honest, and both were caught by the fixture
rather than by the live scan:

1. **Reading the helper, not only the caller.** The tautology in `p1e_neighbor_corr` lives
   in `_selfconsistent`, which `run` calls — the same delegation blind spot r1379 fixed for
   key detection, one layer down.
2. **Fixing a face must move the number that measured it.** After the fix, `p1e` still keeps
   its cutoff pin (it is still a legitimate first check), so the naive rule kept calling it
   tautological. A pin now carries `guarded_by_computed`: if the same stored value is also
   compared against anything that is not a module literal (a digest, a parameter, today's
   panel), the pin is a first filter, not the whole gate.

Live readings (2026-10-31, 699 files, 31 cache decisions):

| | before the guard refinement | published |
|---|---|---|
| identity-checked rows | 19 | 19 |
| of those, self-written pins | 9 | **5** |
| live faces among them (serve a value to a caller, not a fixture) | — | **2** |

The five: `alphagen_rg_census.cmd_run` (`cutoff == CAL_LAST`, a literal `"2026-10-09"`),
`member_reinforce_p1.finalize` (`batch`/`evidence_cutoff`), and three selftest fixtures
(`cn_mkneutral_p1.cmd_selftest`, `innovation_quota_w7/w9.cmd_selftest`) which cannot serve
anything by construction. The two live ones were r1381's worklist.

## Closed in the same round: the biggest panel cache

`alphagen_rg_census.ensure_cache` validated the census panel cache on `meta["cutoff"] ==
CAL_LAST` — again both sides one literal — and every shard resumed on it. A bar repaired
inside the frozen window moves the cache's name, its row count and its cutoff stamp by
nothing, so K=12 shards could finish on a mixture of two worlds and publish it as one
product (the same class as r1378's `cn_mkneutral_p1`, at the largest cache in the repo).

`_prefix_fingerprint(path, cutoff)` hashes only the file prefix the census actually
consumes, which is the load-bearing split: an APPENDED bar must not invalidate the cache
(shards would rebuild hourly, S6 would never converge) while a REPAIRED bar inside the
window must. `_rule_fingerprint()` covers the frozen constants `build_cache` reads, so a
moved gate rebuilds too. A cache written before the digest is a MISS with a named reason,
never a hit. Selftest 37/37, legs s9a-s9d: append does not move the identity, repair does,
a moved constant does, and a matching digest is a hit while a pre-digest cache and a
repaired member are named MISSes.

Published face after the cure: 18 identity-checked rows, **4** self-written pins, **1** of
them a live face. The number fell because the face changed, and the census is now watched
by a smoke leg that runs its selftest — a detector whose own fix it cannot see is a
detector that reports the fix forever.

## Verification

- `scripts/p1e_neighbor_corr.py selftest` — 7 sections PASS, including six guard legs: a
  matching digest skips, a moved constant recomputes, a legacy product is a MISS, a failed
  anchor record is never clean, zero pairs is not a verdict, unreadable inputs are a MISS.
- `Tools/live_value_cache_audit.py selftest` — 41/41 legs PASS (L38/L39/L40/L41 new).
- `smoke_test.py` — one new leg running the p1e selftest.

## Second half of r1380 (inherited estate, re-verified): a shared sentence with no observer

The window that wrote the sections above died at ~07:36 with its estate uncommitted. This
window re-ran every leg before adopting anything (census 37/37, cache-audit 41/41, p1e
selftest PASS, audit face republished by hand, card renumbered E300 after bm-a landed E299
on origin) -- and then the full smoke the dead window left behind reported **1 FAIL**, which
is where the reusable defect was.

**The red leg:** product: whose disk the lane numbers are on reaches both human faces. Its
detail read offhost=9==6 -- the daily report said 9 lanes off "本机", the freshness board
now says 6. Both sentences are TRUE. 
`results/data_lane_freshness.json` is one shared file
written by whichever machine last ran the chain, and disk_face() counts lanes relative to
the machine that computed it: the report was built on bm-c at 00:18 (9 off-host: 6 bm-b +
3 bm-a), the board was refreshed by bm-a at 07:28 (6 off-host: bm-b's six). The leg demanded
numeric equality across two different observers, i.e. it demanded that the other machine
stop writing its own board.

**Why this is not just a flaky test.** The operator-facing defect is real and independent of
the leg: the page printed "9 条在役车道里有 9 条的数字不在**本机**盘上" with nothing saying
whose disk "本机" is. Read on bm-a, that sentence is about somebody else's machine; read on
bm-c, it is a day-old sample. Two hosts' boards become two contradictory-looking sentences
that a reader cannot reconcile -- the r1262 family (compare like with like) one level up,
where the mismatching input is not a parameter but the *observer*.

**Fix, product side (third pass, rebuilt on origin's files):** `disk_face()` now returns
`observer` and prefixes its own sentence with 以本机 <id> 的盘为基准, so the sentence cannot
be read without knowing whose disk it is about (selftest leg L16: the same rows read from
bm-a and from bm-c must give DIFFERENT sentences, and an unknown observer must not print a
name). `_lane_authority_face()` carries the name through into the report's JSON, because a
copy of a sentence is the next defect. Today's REPORT-2026-10-31.md is bm-a's, written
before the tag existed: the leg passes it with the word `report-predates-observer-tag` and
refuses to judge its counts -- an old artifact is un-attributable, not a contradiction --
and the next host that runs the chain prints the name. A missing observer is never silently
equal; it is a named third state (E208 rule: absence is not clean).

**Fix, gate side:** the smoke leg compares like with like -- same observer: counts must be
equal; different observer: both faces must name themselves, and the reason line prints
`observers differ (report=bm-a board=bm-c)` instead of a fake inequality. A report with no
observer tag at all is passed with the note `report-predates-observer-tag` and its counts
are not judged. So the leg still fails if the report drops its own sentence, and it no
longer fails because two machines each wrote a true board.

**Pit worth more than the fix:** a full smoke run is a whole-population assertion, and this
leg had been green for weeks because every board it had seen so far was written by the host
that also built the report. The failure only appeared on the first morning when two machines
took turns running the chain -- a per-host statistic agreed with itself until it was read
across machines.
