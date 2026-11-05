# DIGEST 2026-11-06 r1464 bm-b -- E442: which path composition is never consumed

**Question.** E436 graded 37 sites that name a double-ready fragment and never asked whether the
composed path is consumed later in the scope or simply dropped.

**Population.** Every `os.path.join(...)` call and every `Path(...) / "x"` division in the corpus:
16,611 sites over 3,493 parsed sources in 2,501 files. The walk excludes this study's own files.

**Readings.**

| class | sites |
|---|---|
| consumed at the call site by an opener | 3,153 |
| consumed at the call site by a helper | 2,415 |
| flows into an open/read/write through a bound name | 3,995 |
| flows into a nested scope only | 3,415 |
| flows into another call through a bound name | 530 |
| composed and never used in the scope (dropped) | **85** |
| composed where no name can be followed | 2,001 |
| used some way that is not a consumer | 408 |
| part of a larger composition | 194 |
| stored into a slot or attribute | 67 |
| flows into a return | 221 |
| flows into a dict literal | 127 |

`dropped_sites` = 2,086 (12.56%) is the sum of the last two evidence classes and must be read with
the split above: **85 dead compositions, 2,001 unmeasurable ones**. `sites_reaching_without_a_bound_name`
= 293 (returned or placed in a payload without a name). E436's residue: 30 named, 30 graded here,
3 dropped.

**Two defects found and fixed in the producer, in-window.**

1. The tally guard required a `binding` for `flows_into_a_return` / `flows_into_a_dict_literal` and
   therefore accused 30 legitimate direct-reach rows of "flowing out of a name it never bound"; the
   guard now holds only the three classes that are *defined* as flows of a bound name, and the
   direct-reach shape became a published counter.
2. `ast.get_source_segment` re-splits the source on every call, so a scan that asks for one segment
   per node paid a whole-file split per node: the first build burned 898 s of CPU with no output.
   A per-file splitter (ast's own `_splitlines_no_ff` + byte-offset slicing) brings the build to
   44 s; equivalence was checked over 80 sampled files (8,625 segments, 0 mismatch) rather than
   assumed.

**Evidence.** `scripts/e442_deadpath.py run|verify|check|selftest` -> 26/26 selftest legs,
`verify problems=[]`, `check problems=[]`; face `results/state_tilt/deadpath_latest.json` +
`DEADPATH-2026-11-06.json`; smoke leg `e442 which path composition is never consumed` (extracted
logic 1/1, plus two doctored controls that stay red).

**Method limits, published with the face.** the follow is one name wide (aliasing through a second
name is not followed); the read test is by name inside the scope, not by position; only
`path.join`-tailed calls and Path divisions are in the population; static only, so a path handed to
a function that opens it elsewhere is `flows_into_another_call`, never `consumed`.
