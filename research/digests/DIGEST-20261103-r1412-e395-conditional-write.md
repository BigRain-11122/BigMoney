# E395 — the producer that names the key, and the file it actually dumps into

**Card** E395 · **round** r1412 · **date** 2026-11-03 · **lane** cpu-only, static, zero network

## The question E394 left

E394 classified 218 reads that resolve to a real face which does not store their key. 131 of them
landed in one class: some source that *mentions* the face also builds the key structurally (dict
literal / subscript store / `setdefault`). E394 was careful to call that evidence that the producer
*can* write the key, not proof it did on this run.

E395 asks the follow-up: does the producer write the key on **every path**, on a **branch**, or
behind a **condition** — and is that conditionality written down anywhere a reader of the face can
find it?

## What was measured

Two independent readings of every write site, both from the AST:

1. **Path position** — the ancestor chain between the write and the module body.
   `if` / `try` / `for` / `while` / `with` → the write is on a branch. A function body → the write
   happens when the function is called, which one file cannot discharge. Module body with none of
   those → unconditional.
2. **Dump target** — does this object actually reach a dump of *this* face's file? Direct argument
   to `json.dump`, or one name hop (`facts = {...}; json.dump(facts, ...)`).

The second reading is the one that changed the answer. A closeout script writes several documents
from one function, so "this function dumps a file called `state-bm-c.json` **and** builds a dict
with `dec_delta`" is not the claim "that dict is what gets dumped into that face". The weaker test
put 19 pairs in the wrong bucket.

## The readings (39 (key, face) pairs, 131 reads, 31 keys, 22 faces)

| verdict | pairs | what it means |
| --- | --- | --- |
| unconditional, but into **another** document | **19** | attribution failure: the producer is not this face's writer at all |
| mixed (some branch, some inside a callable) | 8 | no single path story |
| every write site on a branch | 6 | the key is genuinely conditional at the write |
| every write site inside a callable | 5 | the condition is the call, not the branch |
| unconditional into **this very** face | **1** | the only pair where the face lacks a key its own writer always sets |
| (no write site found) | 0 | |

Declarations: **4 of 39 pairs** have a producer docstring line naming the key beside an
optionality marker. **15 of 39** faces name the key somewhere in their own prose — so for those the
face does tell a reader the key exists, without telling them it may be absent.

## Verdict

`some_producers_write_the_key_unconditionally_into_this_exact_face_so_the_face_lacks_a_key_its_own_writer_always_sets`

The load-bearing sentence is the 19: **E394's producer class is, for half its pairs, not a
conditionality story at all — it is a co-occurrence artefact one level deeper than the one E394
already rejected.** E394 rejected "the source names the face and contains the literal". E395 shows
that even the structural test needs its dump target: an unconditional dict literal in a closeout
script is evidence about *some* document, and usually not about the face the read opened.

The single same-document pair is a chase, not a defect registry entry:
`logs/iteration-loop/state.json` / `last_tick`, written at module level and dumped into that file by
`results/_r128bmc_resolve_storm.py:37`.

## Refusals kept

- an unconditional module-level write is published as **attribution failure**, never as
  "conditional" — a producer that always writes the key cannot be the producer of a face without it;
- a write inside a function is published as `inside_a_callable`, never as conditional, and the
  study publishes whether that callable is referenced elsewhere in the module (0 = defined and never
  called);
- `setdefault` is classified apart from a plain store;
- a declaration needs the key literal **and** an optionality marker on the same docstring line, and
  the terse published line is the docstring's own text;
- a producer that cannot be parsed is published as `producer_unparsed`, never guessed;
- the study excludes its own source, face, mirror and smoke leg.

## Evidence

- runner `scripts/e395_conditional_write.py` — `run` / `verify problems=[]` / `selftest 20/20`
- face `results/state_tilt/CONDITIONALWRITE-2026-11-03.json` (+ `conditionalwrite_latest.json`)
- smoke leg `# E395:` in `smoke_test.py`, proven verbatim standalone via
  `scripts/run_e395_smoke_leg.py` (1/1 PASS)
- S6 leg `conditional_write` (`python scripts/e395_conditional_write.py verify`, ~0 s; 170 legs,
  0 ghosts)

## Pit

A path position is not a call graph, and a dump target is not a dataflow proof. Both are published
as the weaker readings they are: `inside_a_callable` says "the condition is the call", and
`via_name_to_this_face` says "one assignment hop reaches a dump that names this file". What they are
enough for is the negative claim that carries the verdict — 19 producers demonstrably write their
key into a *different* document, so their presence in the producer class measures co-occurrence, not
conditionality.