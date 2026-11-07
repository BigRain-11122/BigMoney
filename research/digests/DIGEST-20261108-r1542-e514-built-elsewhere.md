# E514 — "built by another module" is an unfinished sentence (r1542 bm-b)

Card: E514-WHERE-DOES-THE-VALUE-BUILT-BY-ANOTHER-MODULE-ACTUALLY-COME-FROM
Face: `results/state_tilt/BUILTELSEWHERE-2026-11-08.json` + `builtelsewhere_latest.json`
Script: `scripts/e514_built_elsewhere.py` (run / check / verify / selftest)
Verdict: `every_in_repo_builder_answers_its_return_paths_and_the_rest_of_the_bucket_is_not_a_builder_at_all`

## Why this hop

E512 (r1540) answered all eight of its sites, but four of them carried one label and stopped:
`a_value_built_by_a_call_into_another_module`. They are the same expression —
`asof = str(slip.index[-1].date())` — where `slip` comes out of `BT.apply_overlay(...)`, and
`asof` is the date the ticket is filed under. E513 (r1541) published 23 bindings whose population
is "built by a call into another module" and stopped there too. So the as-of day of a published
ticket was, by two independent faces, a value nobody had read the author of.

## Population (27 rows, both arms from published faces)

* 23 = E513 rows whose origin is `the_population_lives_in_another_module_and_stops_there`;
* 4 = E512 sites whose `field_origin` is `a_value_built_by_a_call_into_another_module`.

## Read

| builder class | rows | what it means |
|---|---|---|
| `the_builder_is_a_function_defined_in_an_in_repo_module` | 13 | a real builder |
| `the_value_is_read_at_the_site_itself` | 4 | `io.open(...)` / `_read(...)` — nothing else builds it |
| `the_value_is_a_literal_written_at_the_site` | 1 | `"\n".join([...])` of literals |
| `the_callee_only_constructs_a_name_or_a_path` | 5 | `os.path.join` / `dirname` / `basename` |
| `the_callee_could_not_be_resolved_to_a_definition` | 4 | a key read off a container (`payloads.get`, `src.get`) |

Ten of the 27 rows are not built elsewhere at all: five are path constructors that the published
bucket called "another module", four are read where the site stands, and one is a literal. The
bucket's name was the only evidence they were builders.

Of the 25 return paths of the 13 genuine builders: **file 5 / git store 4 / tree scan 2 /
parameter 4 / literal 10 — the run clock 0**. Six distinct builders:
`load_pin` (json.load), `pinned_corpus` (`git cat-file --batch` through subprocess),
`_sources` (`open(...).read()` in a loop), `_walk_py` (`os.walk`), `producer_map` (a dict filled
from `_walk_py` + `read_text`), `apply_overlay` (three `pd.Series(..., index=idx)` whose `idx`
walks back to its `rp` parameter).

Answers: read-every-path 7 / mixed 2 / hands-back-a-parameter 4 / the rest non-builders.

## The four ticket sites

`rp` is a parameter of `apply_overlay`, and the feed published for it is
`scripts/etf_phase_beta_target.py:rets` handing back *its own* parameter `ser` — at the call site
`rp = BT.rets(ser.reindex(idx))`. Three named hops from the ticket's date to the panel
(`apply_overlay` → `rets` → the caller's series), and none of them is a clock. That is the
answer the card asked for, and it needed a parameter feed to be sayable at all: "the builder
hands back a parameter" alone just moves the question one step.

## Pitfalls measured in-window

1. **Two import shapes, one resolver.** `e512._callee` splits the last dotted segment off, which
   is right for `import a.b as M` but wrong for `from scripts import mod as BT`: the module
   resolves to the package `scripts`, the callee is not found, and the walk falls into the call's
   **arguments** — the four ticket sites were published as built by the same-module `k_schedule`
   (an argument of `apply_overlay`). Fix: try the full dotted name first, then the split.
2. **Decide "read here" before "who built it".** Otherwise `io.open(...)` counts as an
   unresolvable builder and the bucket looks three-quarters unreadable when it is not.
3. **An empty container is a starting point, not an answer.** `out = []` then `out.append(...)`
   in a loop published as `a_literal_written_in_the_builder` ("the value is []"); falling back to
   "unread" lets the fill be the author (`producer_map` flips literal → tree scan).
4. **A method call's argument is not its value.** `marks.shift(1)` traced to the literal `1`.
   Method calls fall back to the receiver; only constructors look at `index=`.
5. **Parameters come from the function, not the module context.** Reading `e507`'s module-level
   `params` map labelled locals (`out`, `row`) as "a parameter the builder hands back" — the
   count went 0 → 8 and back to 0 once `e512.argument_names(func)` was passed in.
6. **Twelve hops of depth is not enough.** `idx → live → applied → marks → dates → rp` is already
   thirteen AST levels, so `apply_overlay` was published as unreadable for a reason that was the
   instrument's, not the code's.

## Wiring

* S6 leg `built_elsewhere` (`Tools/s6_chain_bmb.py`) — `check` rc=0 0.07s, problems=[].
* smoke leg `# E514` in `smoke_test.py`, executed verbatim by `scripts/run_e514_smoke_leg.py`:
  1/1 green; `--doctor` 1/1 red with the face restored byte-identically (sha `9e2408b5bd58`).
* Five doctored arms refused in `selftest` (flipped answer, inflated builder count, path kind
  outside the vocabulary, hand-written verdict, answer that contradicts its own kinds) and four
  in the smoke leg.

## Not claimed

The full 350+-leg smoke suite was not launched this window. No collector, paper or dashboard leg
was re-run. The study follows one hop plus at most one nested builder; a value handed to a third
module is published as `still_no_readable_origin` rather than chased to the end.