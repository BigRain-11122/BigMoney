# DIGEST-20261107-r1537-e511-collision-anatomy

**Round:** r1537 bm-b (dept=research+engineering) · **Study:** E511 · **Face:** `results/state_tilt/collisionanatomy_latest.json`

## Question carried in

E510 (r1537) re-read E507's 42 mixed pairs with a scoped binding table: 13 pair sites, 8 collapsed,
1 needs the module-wide fallback, **4 stay ambiguous** with the label *"the enclosing scope itself
holds more than one origin"*. That label is a verdict about a **name**. A name can be ambiguous in
two structurally different ways: it is written more than once inside the scope (which write reaches
the site is a question of execution order), or it is written exactly once and the **value** enters
from somewhere the line does not name (the ambiguity is one level down and a rename has nothing to
separate). E510 never asked which.

## What was measured

For each of the four surviving sites, every write the site's own scope makes of that symbol was
enumerated (assign / annotated-assign / augmented-assign / `for` target / `with ... as` / walrus /
`except ... as`; comprehension targets excluded the way E507 excludes them, and published as a
separate list). Each write was classified by the **shape of its right-hand side**: a seed literal,
a step that mentions and extends the symbol itself, a replacement that never mentions it (a call, a
subscript of another object, an attribute), a defaulted expression, a branching expression. Then the
site was classed from those shapes plus **structural** evidence: two writes that sit in opposite arms
of the same `if` cannot both execute (`if_line` + `arm`).

## Headline

**4 pair sites / 4 member faces / 2 sources / 2 symbols — and the number of sites a rename would
separate is zero.**

* `scripts/etf_book_cash_ladder.py:575` — `idx`: **3 writes, one meaning built in sequence**.
  `idx = None` (seed) → `idx = s.index if idx is None else idx.union(s.index)` (extends itself) →
  `idx = idx[idx >= WINDOW_START]` (subscripts itself). Which of the three values reaches line 575
  is a dataflow question; no rename separates anything because there is only one thing.
* `scripts/etf_book_order.py:1033 / 1043 / 1059` — `asof`, all three inside `run_card` and sharing
  one write: `asof = tk["priced_bar"] or "unknown"`. The operand is `tk = card_config_ticket(nav=nav)`,
  shape `call_result`. **This is why E510's scoped arm read `mixed` on a name that is bound only
  once** — the ambiguity is not in the name, it is in the call that produced the operand.

Verdict: `every_residual_site_is_resolved_by_neither_a_rename_but_the_values`.

## Three things that would have made this face lie

1. **"The scope holds more than one origin" does not mean "this name is written more than once."**
   3 of the 4 sites are written exactly once. Reading the parent verdict literally would have
   classed three quarters of the population in the wrong bucket; the discriminator has to be the
   **count and shape of bindings**, not the parent's wording.
2. **Mutual exclusion has to be structural, not shape-based.** First version of the selftest stood
   at 22/24 because `if flag: stamp = pick(path) else: stamp = stamp2` has two *replacement* writes
   and was therefore published as "two meanings under one name" — i.e. it claimed a rename could fix
   a branch join. Adding the `if_line`/`arm` marker made it 24/24. A shape-only classifier calls
   every branch a collision.
3. **Following the operand one hop explains the parent instead of contradicting it.** Publishing the
   operand evidence (`symbol`, `line`, `shape`, `count_in_scope`) turns "this site still reads mixed"
   into a checkable sentence: `asof`'s only write reads `tk`, and `tk` is a call result. Without it,
   the residual bucket would have stayed an assertion.

## What this face does not claim

Static, one repository, one scope hop; no dataflow is executed and no separation is performed. The
right-hand-side excerpt is a single-line collapse of a possibly multi-line expression — **the line
number is the authority**. Loops and `try` arms are **not** modelled for mutual exclusion (only
`if` arms are), so a `try`-bound site would be classed by shape alone; that is stated in
`method_limits`, not hidden. The history arm of E507 is not replayed.

## Verification

`scripts/e511_collision_anatomy.py`: `run` rc0, `check` problems=[], `verify` problems=[] on a live
re-derive, **selftest 24/24** (6 of those legs are the gate refusing a doctored face). Deterministic
rebuild differs only in `generated`. S6 leg `collision_anatomy` rc0 0.05s. Smoke leg `E511 ...`
proved standalone 1/1 green, 1/1 red on a doctored anatomy, green again after re-deriving the face.