# Digest -- r1424 bm-b: does the reader of a never-produced file fail loudly or silently (E405)

**What was owed.** E404 (r1421) published three in-tree files that no writer produces
(`in_tree_absent_reads: 3`) and stopped at the join. Card E405 asked the next question per site: a
missing target is only a defect if a reader would fail, so read the enclosing chain and publish
whether the absence raises, returns a default, or is guarded.

**What is on disk.**

| file | role |
| --- | --- |
| `scripts/e405_dead_read_failure_mode.py` | re-derives every classification from the live AST; selftest 17/17 |
| `results/state_tilt/DEADREAD-2026-11-04.json` + `deadread_latest.json` | the face (population machine-read from E404's `summary.dead_joins`) |
| `smoke_test.py` leg E405 + `scripts/run_e405_smoke_leg.py` | leg exec'd verbatim, 1/1 |
| `Tools/s6_chain_bmb.py` leg `dead_read_failure_mode` | verify wired into the S6 chain |
| `knowledge/METHODOLOGY_ASSETS.md` card E405 | the reusable rules |
| `research/digests/DIGEST-20261104-r1424-e405-dead-read-failure-mode.md` | this note |

**Verdict.**
`readers_and_enumeration_disagree_loud_name_based_consumers_and_a_silent_directory_enumerating_one`
-- 3 sites: `1` write at the join line, `2` module constants, `0` reads. 2 sites refuse loudly, 1
would be silently omitted, 0 ungraded.

**Three findings the E404 face does not contain.**

1. **`in_tree_absent_reads: 3` is not three reads.** `scripts/p2_deepening.py:420` assigns a joined
   path and line 421 opens it with mode `"w"`; the site is a write target whose registration stage
   never ran. E404's companion count `in_tree_absent_writes: 0` is therefore false. The classification
   has to follow a function-local path to its *first later use* -- the join line carries no mode.
2. **Both constants are gated, and the gate is a non-zero exit.** `scripts/trial_labor_w20.py:94/97`
   are read only inside `cmd_judge_prep` / `cmd_intake` after
   `if not os.path.exists(NAME): print("...GATE..."); return 2`. Eleven consumer rows across the two
   constants: 2 writers (`_dump` to the same names), 2 existence gates, 2 gated reads, 2 status-table
   prints, 2 landing-helper passes, 1 other. Absence is a loud pending output.
3. **The only silent mode lives one level above the join.** No source file names
   `COMPOSITE-001.json` as a read. The two corpus readers consume the directory --
   `scripts/aggressive_lab.py:266` (`glob.glob(... "firm","traders","*.json")`) and
   `scripts/monthly_briefing.py:70` (`traders_dir.glob("*.json")`). A trader whose registration never
   ran is silently missing from a roster nobody counts, and no existence gate can see it.

**Instrument rule kept from E389/E207.** A reference this arm cannot grade is published
`not_graded_this_arm_sees_the_reference_not_its_effect` instead of being charged silent: the row is
`tl16.tl6.finalize_already_landed(SCREEN_BATCH, SCREEN_FILE)` (w20 line 1254), whose own gate lives
inside a helper. 1 of 11 consumer rows; charging it would have manufactured a silent mode out of a
landed-check.

**Side effect, stated not hidden.** Two new `.py` files entered the tree this round (the producer and
its leg runner), so E305's `precisiongap` face was re-derived from the live build before commit --
the leg that guards it names the number it re-derives, so a stale face re-reds the suite (the E407
family). No leg threshold was touched.