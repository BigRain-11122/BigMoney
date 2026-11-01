# E353 -- a guard on a field nobody writes is not automatically dead: 23 of 131 would raise before they run

Round r1375 (bm-b). E353 from the pool (seeded at E350 close, entered 2026-11-01 21:58).

## The question E350 could not answer

E350 counted *fields*: of 2289 (face, field) pairs read across the corpus, 230 are read by a guard,
and **131 of those have no writer anywhere in the corpus**. Its consequence sentence was a claim
about code, not about the tree: *the guard can only fire on a missing value*. Whether that is an
alert, a silent pass, or a read error depends on what the face looks like on disk right now. This
study asks the disk.

## Measurement

Population = E350's unwritten-guard pairs, **rebuilt by importing E350**, not re-read from its
published face: that face truncates its list to 40 rows (`rows_truncated: 2249`), so half the
population is not in the artifact. Build pays E350's ~100 s AST scan; verify does not.

Per pair, the face key is resolved to a file:

| resolution | meaning |
|---|---|
| `named` | a path key, on disk |
| `path_moved` | a path key that is not on disk; every file of that basename is published |
| `basename` | a bare key (E350's fallback when it cannot fold the path) with exactly one file |
| `ambiguous` | a bare key shared by several files -- **refused, not first-matched** |
| `missing` | no file of that name anywhere |

Then the field is looked for at the top level of the loaded object, and the guard is classified by
what its read does today.

## Readings

| | |
|---|---|
| pairs classified | **131** over **45** distinct faces (99 named, 9 basename, 7 ambiguous, 16 missing) |
| `guard_unreachable` -- the read raises first | **23** (16 no file anywhere, 7 name shared by 2/14/20 files) |
| `guard_is_the_alert` -- field absent or null | **5** |
| `guard_never_fires` -- field present, read yields a value | **103**, of which **34 read a falsy value** |
| write list | **4** faces, one writer each, close all 5 alert pairs |
| fix list | **10** faces no writer can reach, 23 pairs |
| E346's 17 latches | **1** name coincides (`panel`), **0** identities coincide |
| verdict | `of_131_guards_on_a_field_no_source_writes_23_raise_before_the_guard_runs_5_read_a_missing_or_null_field_and_103_read_a_value_of_which_34_read_falsy` |

The five alert pairs are legible one by one: `p2_calibration_v2_ext.json` lacks `nshards` and
`shard`; `_r899bma_f1_bull_cond_selftest.json` and `REGIME5-VALIDATION-2026-09-30.json` lack
`cutoff`; `futures_tsmom_probe.json` lacks `overall_verdict`. Four faces, five fields, one writer
each -- that is the whole actionable surface of E350's 131.

The unreachable half is the sharper reading. Sixteen pairs name files that are nowhere on disk
(`FZ.json`, `_chunk_.json`, `bm-x.json`, `census.json`, `xcc.json`, `idle_trigger.bm-c.json`,
`json`) and seven name a basename several real files share -- `probe.json` 14 candidates,
`manifest.json` 20, `meta.json` 2. A guard whose subject is a basename cannot be shown to read
anything, because this tree has 20 files called `manifest.json`. Refusing the ambiguity is the
whole point: taking the first would have produced seven confident readings out of nothing.

The falsy 34 are not noise and are not one group. The bulk is the closeout ledgers:
`dec_delta` 8, `ord_delta` 8, `unacked` 8, `unacked_count` 6, `inbox_unread` 4 -- counts that are
**0 when the round is clean**. So a guard on them sits on the good news: if it is `not`-shaped it
fires every time the ledger is clean, and if it is `is None`-shaped it never fires at all. The
field cannot tell the two apart, and that is why they are published as a state rather than folded
into "never fires".

## Reconciliation with E346

E346's 17 latches are the other direction: fields a producer **writes and then branches on
itself**. Exactly one name coincides (`panel`, in `update_sina_mf` / `update_moneyflow`), and none
of the 17 is the same face-and-field as an unwritten guard, because E346's population is by
construction written. The two counts answer two questions -- "a field its own writer re-reads" vs
"a field no writer produces" -- and the honest sentence is that they do not overlap.

## Pitfalls

1. **The published face is not the population.** E350 truncates to 40 rows; a study that reads the
   artifact instead of importing the producer silently measures a third of its subject.
2. **A basename is not an identity.** 32 of the 131 keys are E350's fallback (no path), and 7 of
   those name files this tree has several of. Resolve-or-refuse, never first-match.
3. **`nested_hit` is a hint, not a presence.** One-level search found 0 of the 5 alert fields
   nested; the alert stands on the top-level key the corpus actually reads.
4. **Fixture names are in the population.** `FZ.json`, `_chunk_.json`, `json` are temporary files a
   selftest writes -- so part of E350's 131 is test scaffolding, not production defence. That is
   the next study's subject, not a correction to this one.

Evidence: scripts/e353_unwritten_guard_presence.py (selftest 21/21, verify 0 problems) ->
results/state_tilt/GUARDPRESENCE-2026-11-02.json + guardpresence_latest.json; S6 leg
`unwritten_guard_presence`; smoke leg E353 (scripts/run_e353_smoke_leg.py, standalone PASS);
knowledge/METHODOLOGY_ASSETS.md card E353