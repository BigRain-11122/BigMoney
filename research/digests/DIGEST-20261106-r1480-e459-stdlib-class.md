# E459 -- the standard-library classes behind E456's out-of-tree receivers (r1480 bm-b)

**Question.** E456 left 928 rows whose callee module has no file in this repository. The module name
is a handle the instrument can use without a network. Resolve it, look up the class the import form
named, and count the rows that name a method that class carries.

**Answer.** 960 rows on this residue today (growth-only superset of 928, +32). All 960 import. 17 name
a class of the kind the import form named; 4 of those carry the method (all `io.StringIO.write`).

**What the split says.** 943 rows are *attributes that exist and are not classes*:

| module | attribute | rows |
|---|---|---|
| io | open | 804 |
| subprocess | run | 25 |
| numpy | isfinite | 24 |
| numpy | asarray | 13 |
| tempfile | mkdtemp | 13 |
| tempfile | NamedTemporaryFile | 12 |

Zero rows failed to import (0 `find_spec` misses, 0 imports that raised). So "the standard library is
the untraceable part" would have been the wrong sentence: the part method-level instruments cannot
grade is factory functions, and the class-carrying share of the block is 1.8%.

**Form.** module-level import 863 rows / 8 classes / 4 hits; module-level aliased 83 / 7 / 0;
function-level 13 / 1 / 0; function-level aliased 1 / 1 / 0. The form that dominates the count is the
form that carries the least class identity.

**Rules.** (1) A residue is a reading only if it is resolved. (2) Split *absent* from *present but not
a class*. (3) `find_spec` before `import_module` -- two different findings. (4) A class found is not a
method hit.

Face `results/state_tilt/stdlibclass_latest.json` (+ `STDLIBCLASS-<cutoff>.json`,
`stdlibclass_by_module_<cutoff>.csv`). Producer `scripts/e459_stdlib_class.py`
(selftest 15/15, run rc0, verify clean). S6 leg `stdlib_class` rc=0 in 0.05 s.