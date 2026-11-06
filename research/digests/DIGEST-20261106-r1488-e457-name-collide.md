# DIGEST 2026-11-06 r1488 bm-b -- E457: what a name test's vocabulary costs

**Question.** E450's name arm read 26 hits and the single largest block of them (13, all
`Tools/pool_worker.py`) carried zero rows where the receiver was that module's own class. The
suspicion was a module-level function name that is also a method name elsewhere; nobody had
measured how often that happens or whether the colliding module could even be reading the function.

**Answer.** Population = every module-level function in the tree. 3,523 sources, 3,521 indexed,
17,617 module-level functions, 8,477 distinct names, 149 classes, 138 class methods, 2 genuine
parse failures. **17 names (0.2005%)** carry a method of the same name in another module: 17
(name, module) pairs, and **17 of 17 have no import edge to the definition** -- on this tree the
unpriced half is the entire collision surface, and the surface itself is tiny because the repository
defines 149 classes in 3,521 modules.

**The anchor refutes the suspicion it was built from.** `Tools/pool_worker.py` defines 27
module-level functions and one class with two methods (`_Heartbeat.__init__`, `_Heartbeat.run`), and
**0** of its 27 function names collide with a method name anywhere. Whatever produced E450's 13
name hits in that file, it was not a module-level function name -- so the mechanism E457 prices is a
different and much rarer one than the arm that raised the question, which is the useful half of the
result (a name test on this tree is nearly justified by construction).

**Pits.**

* A UTF-8 BOM is an encoding artefact but `ast.parse` rejects it: reading with `utf-8` published
  117 of 3,523 sources as syntax errors and silently deleted 212 functions, 73 names and 2 classes
  from the census. `utf-8-sig` collapses them to the 2 real failures. Any AST census must prove its
  parse-failure count is not its own reader before it publishes one.
* `import a` is not `from a import f`: a module that imports the defining module but not the name
  has no binding for the function and stays on the unpriced side (fixture `mod_f` pins it).
* A class attribute is not a method; the definition's own module is not a collision.

**Wiring.** `scripts/e457_namecollide.py` (run rc0 / check problems=[] / verify problems=[] /
selftest 17/17); faces `results/state_tilt/namecollide_latest.json` +
`NAMECOLLIDE-2026-11-06.json`; S6 leg `name_collide` (runs `check`; the full rebuild parses 3.5k
sources); smoke leg `e457 a name test's unpriced half is the method names no importer writes
(r1488 bm-b)`; card E465; pool E457 done. No charge, no adoption, no upstream face rewritten.

**Bound.** Nothing here reads call sites, so `C` (the collision surface) is an upper bound of what
a name test can see and `N` (no import edge) is an upper bound of its unpriced half. An aliased
from-import counts as importing the function; a module-attribute access does not count as an import
edge and is therefore priced as unpriced -- the conservative direction.
