# DIGEST — r1644 bm-b · E626: does the callee handed the object write the key the dead line read?

**Face** `results/state_tilt/HANDOVERWRITE.json` (+ `handoverwrite_latest.json`), cutoff 2026-11-09.
**Script** `scripts/e626_handover_write.py` (selftest 32/32; `run`/`check`/`verify` `problems=[]`).
**Legs** `scripts/run_e626_smoke_leg.py` (1/1 PASS, `--doctor` 1/1 red, face restored byte-identically),
smoke_test.py leg `E626`, S6 leg `handover_write` (rc=0, 0.05s, receipt `results/_r1644bmb_s6_chain.json`).
**Pool** E626 done, E627 seeded (alias binding — the hole E625 and E626 both declare).

## The question

E625 closed the third test in the key/object/value stack and wrote its own hole into `limits`: *f(m) could write
anything, so the object being handed to a call leaves the value undecided*. One of its four same-object duplicate
rows was published exactly that way. This card follows that handover **one hop** into the callee.

## Readings

Population is unchanged (1,099 modules, 34 live dead face-key lines, 4 same-object duplicate rows); the 2 inert
lines stay inert. E625 left **1 duplicate row / 2 handover instances** open:

| module / function / line | key | handover | callee | what it does to the key |
|---|---|---|---|---|
| `scripts/cn_core_ddctl_p1.py` `run` L367 | `days` | L372 | `build_dd_axis` (L148, param `P`) | reads `P["days"]` into `reindex`; **writes nothing** |
| same | same | L373 | `active_rebals` (L164, param `P`) | reads `P["days"]` / `P["rebal_days"]`; **writes nothing** |

- Handover classes: 2 × `the_callee_does_not_write_the_key_on_its_parameter`, 0 naming, 0 unnamed, 0 handed on
  again, 0 outside the module, 0 attribute calls, 0 missing call, 0 outside the signature.
- Post-hop read classes: 1 × `the_read_settles_on_the_value_the_dead_line_saw`, 0 different, 0 undecided.
- Duplicates: **4 survive / 0 stored / 0 undecided** (E625 published 3 / 0 / 1).
- Verdict `all_1_duplicate_reads_left_undecided_by_a_handover_settle_to_the_value_the_dead_line_saw`.
- Cross-check: the re-derived rows are E625's 34 published rows, row for row and value-class for value-class
  (0 class diffs, 0 value-class-list diffs, 0 rows only on either side).

## What it means

"Handed to a call" is a **measurement boundary, not a verdict**. The callee was module source one hop away, so the
question was answerable all along; publishing it as undecided was honest but conservative, and the conservative
reading cost exactly one row. The stack is now key → object → value → **callee body**, and each step's remaining
hole is named:

| remaining hole | published as | closed by |
|---|---|---|
| a write through another name bound to the same dict | `limits` of E625/E626 | **E627 (seeded this round)** |
| a callee outside this module, an attribute call, a parameter handed on again, an unnamed write | explicit `handover_class` values with a `why` field | next card if it ever shows up in the population (0 today) |

## Pitfalls measured this round

1. **The denominator has to follow the question.** The first build of the verdict said
   `4_of_the_1_duplicate_reads_left_undecided...` — it compared the *whole population's* survivors (4) against the
   *handover sub-population's* size (1). The face's own `face_problems` caught it on `verify`; the fix was a second
   split (`duplicates_leaving_a_handover_that_settle_to_*`) rather than a reworded sentence.
2. **`verify` run against a stale face reports the checker, not the face.** The first batch wrote the face, then ran
   `check` (green) and `verify` (red) — the red was the *old* face meeting the *new* checker. Both arms have to be
   run after the last write; the round read the first task's output rather than trusting the exit code.
3. `PYTHONIOENCODING`/console GBK mangles the Chinese cards on screen but not on disk; the registries were verified by
   `git diff --numstat` (28/1 and 1/0) rather than by eye.
4. PowerShell has no heredoc — the patch scripts went through `_patch626*.py` files instead of `python - <<'PY'`.

## Not claimed

The full smoke suite was not launched (no leg filter, r1499); only the new leg and its standalone mirror are green
(and red under `--doctor`). No GPU work (parked, C-20261014-01 §3), no cloud call, nothing deleted, no queue head
claimed from `fleet/backlog.md`.