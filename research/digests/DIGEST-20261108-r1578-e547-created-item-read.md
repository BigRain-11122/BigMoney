# DIGEST 2026-11-08 r1578 bm-b -- E547: the eight created items, and who reads them back

**Study**: `scripts/e547_created_item_read.py` (card E547) · **Face**: `results/state_tilt/CREATEDITEMREAD-2026-11-08.json` (+ `createditemread_latest.json`) · **Pool card**: E547 -> done.

## What the card asked

E544 (r1573) published 13 `(store, later read)` pairs over containers this repo's own interpreter can bind.
Eight of them run the other way: the store **creates** an item the fold never publishes --
`out['verdict']` (three `alphagen_beam_w1x` probes), `rows['_GB_nan_skipped']` (t19),
`probe['params']['report_num_entries']` (t33), `art['trials_N']` (three `t73_s2_*` studies).  E544 named
the divergence and stopped there.  The card asks the consequence: **a consumer that took the fold's container
-- the one without the item -- what does it meet?**  A `KeyError`, a default, or nothing at all?

## What it found

| outcome | rows |
|---|---|
| a consumer that took the fold's container would raise `KeyError` | **8** |
| only ever read through a guard or a default | 0 |
| no read of the item exists anywhere | 0 |

10 unguarded subscript reads, 2 guarded (`.get`, both on t19's own row, where the guard sits on the *second*
store rather than on the reader).  Every row's read is inside the module that creates the item; **0 rows are
read back through a persisted face**.  The three `alphagen_beam_w1x` probes resolve their face path
(`results/alphagen_w1x/probe_latest.json`), and five further modules name that same basename -- but not one of
them binds anything from that file, so they are a name collision and not a channel.

Verdict: `the_created_items_are_read_only_inside_the_module_that_creates_them_and_never_through_a_persisted_face`.

## The expensive lesson: a key name is not a container

`verdict` is named **3,374** times in the corpus, of which **3,257** sit on a *different* container.  Across
the four created key names, 741 modules name at least one of them.  A name census would therefore have
published 741 "consumer modules" for eight items that **nobody outside their producer reads**.  The first
build of this study made exactly that mistake in the other direction -- it reported 8/8 "never read", because
the parent publishes key tokens with their Python quotes attached (`"'verdict'"`), so no site matched at all
until the tokens were unquoted.  The truth is in the middle and only a container-scoped census reaches it.

## The laws this round adds

1. **Same name is not same container.**  `out['verdict']` is three different dicts in three sibling probes.
   A cross-module read of the same key literal belongs in the collision bucket until it is *proved* to come
   from the same object (here: bound from a load of the same face file).
2. **The numerator of a name census must be falsifiable by the container.**  Publish the container with every
   read, then count.  741 versus 0 is invisible without that column.
3. **"Never read" and "read by its own producer" are different risks.**  6/8 reads sit in the creating
   function after the store (a `print`, an accumulator).  Only a read that leaves the module can hurt a
   consumer, so `read_scope` is published beside the outcome rather than folded into it.

## Defects caught before the gate

- The parent's key tokens carry their quotes (`"'verdict'"`), so the first build matched nothing and published
  a clean-looking "nothing reads these" over a population it had silently emptied.  Fixed by unquoting at
  population read; the smoke leg now pins the population to the parent's own eight.
- The first face-channel arm used a bare basename match and invented 16 readers per row -- the three
  `alphagen_beam_w1x` probes reading each other's local `out`.  Replaced with `face_bound_names`: a reader
  must bind a local from a load of the face file, or it is only a module that *names* the file.
- `functions_at` walked `ast.arguments`, which carries no line number; the module path resolver then had to
  be taught `dirname`/`abspath(__file__)`/`join` or every persisted face came back unresolved.  Unresolved
  expressions are now published, not dropped.

## Gates

`selftest 16/16` · `check` `problems=[]` (re-derives every outcome from the row's own read list and the
verdict from the rows) · `verify` two builds identical · smoke leg `# E547` standalone `PASS`, `--doctor`
`FAIL` (a hand-written verdict is refused) · S6 leg `created_item_read rc=0` (20.9 s -- it parses 2,783
modules).

## Limits published with the face

Static AST only; a subscript inside `try/except KeyError` still counts as unguarded because the guard lives at
the caller.  The persisted-face channel resolves literal / `join` / `dirname` / `abspath(__file__)` path
constants only -- anything else is published as unresolved rather than as "unread".  Cross-module analysis is
a key-literal census, not a dataflow; the face channel is the one place where a binding is required.

## Next

E551 asks whether the six `print("wrote", OUT_PATH, ...)` render sites are parsed back by machine code.  The
E547 reading sharpens it: a printed path is not a channel unless something binds it, and in this corpus the
only string that travels between modules is a *name*, which is exactly what cannot be trusted.