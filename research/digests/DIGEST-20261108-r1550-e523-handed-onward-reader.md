# r1550 / E523 -- who reads the value a site handed onward?

**Question.** E522 published 351 call sites that hand the callee's result onward without reading it
there (342 in production functions, 9 at module level). A hand-on is not an endpoint: the reader is
one hop away, and the published face could not say whether that reader guards the value.

**Method.** Follow one hop, per site, from the AST:
`return value` -> the enclosing function's production call sites (same resolution and guard rules as
E515/E522); `sink(value)` -> resolve the callee through the corpus import maps and ask whether the
receiving parameter is loaded at all and whether the first load sits behind a terminating guard;
`{"k": value}` -> stored (the reader is whoever reads the container);
`Compare/BinOp/JoinedStr/IfExp` -> read inside an expression at the site, which is neither a named
reader nor a guard.

**Readings (351 sites, 2723 sources parsed, 22 unparseable).**

| form | sites |
|---|---|
| stored in a container | 153 |
| consumed inside an expression at the site | 82 |
| passed as an argument to a call | 49 |
| returned from the enclosing function | 42 |
| handed on in a form this scan does not follow | 25 |

| reader | sites |
|---|---|
| every production caller guards it (returned) | 37 |
| a production caller reads it unguarded (returned) | 1 |
| in-repo callee reads the parameter behind a guard | 3 |
| in-repo callee reads the parameter with no guard | 11 |
| in-repo callee never loads the parameter | 0 |
| callee outside the corpus (value left the tree) | 34 |
| returned, no production caller | 4 |
| unresolved | 1 |

**Finding.** 12 sites hand a result to a reader that reads it with no guard: 1 through
`e482_latest_outside.py`'s `read_text -> _source_text` return, and 11 through a parameter --
including `Tools/saturation_engine.py::cmd_status` (`read_machine_id`),
`scripts/compute_audit.py::ignitable_face` (`heartbeat_silence`),
`scripts/py_watermark.py::probe` (`core_count`, `_machine_id`) and
`scripts/supply_alignment.py::build` (`_self_id`).

**Pitfalls measured, not assumed.**
1. A first draft recognised only Return and Call as hand-on forms; that folded 82 expression-site
   reads and 25 other forms into "unresolved" (108), both overstating the residue and hiding a real
   read class. The five-form vocabulary came from looking at the parents.
2. "Read inside an expression here" is not "someone guards it": `SAMPLE_WINDOW_S * cores`,
   `{_machine_id()}` and `'x' in src` carry no terminating guard, so they are published as their own
   class and are excluded from both the guarded and the unguarded-reader numerators.
3. The corpus size is a live-tree snapshot, not a measurement: `sources_read` moved 2722 -> 2723 ->
   2745 across this window because other lanes write into corpus directories. `verify` gates the
   reader classes and prints those two counters instead of failing on them (documented in
   `method_limits`).
4. A summary key named `handed_onward_production_sites_in_upstream` counted 9 module-level sites as
   production; renamed to `handed_onward_sites_in_upstream` with `sites_at_module_level` published
   beside it.

**Wiring.** `scripts/e523_handed_onward_reader.py` (selftest clean, run rc0, check 0, verify 0;
fixture corpus with returned/argument/dropping/blind readers plus six doctored faces refused);
S6 leg `handed_onward_reader` rc0 0.07s; smoke leg `# E523` proven standalone 1/1 with `--doctor`
1/1 red and the face sha restored. Face: `results/state_tilt/HANDEDREAD-2026-11-08.json` +
`handedread_latest.json`. Not run this window and not claimed: the full smoke suite, the rest of the
S6 chain, monitor.build_status, daily_scorecard.
