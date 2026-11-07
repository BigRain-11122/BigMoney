# DIGEST 2026-11-07 r1515 bm-b -- E490 write-helper

Card: E490 in `knowledge/METHODOLOGY_ASSETS.md`.

## Question
E489 left 9 same-directory writers whose write call is present but whose path argument never
folds. Those nine are not one class. Is the write done inside a helper that takes the directory as
a parameter (so the module constant is handed in at the call site -- one more hop reaches the
reader's directory), or does the path genuinely come from argv / the environment / a temp
directory (no hop budget will ever place it)?

## Reading (2026-11-07, 9 spellings / 11 write sites)
- one hop reaches the reader's directory: **4** (`bandflipbudget`, `pointerread`, `scaffold`,
  `selfres`) -- reached through a **parameter default** (`write_face(face, root=ROOT)`), the
  caller's own parameter chain (`_write(out, outdir)` inside a function that receives `outdir`),
  and a call site that composes `os.path.join(OUTDIR, ...)` directly
- the directory arrives, the basename is itself a parameter: **1** (`banddraw` --
  `_write(face, outdir or OUTDIR, tag)`, `tag` picks the basename) -> **5/9 need one more hop**
- run-time supply: **3** (`invisibletail`'s `_fx` writes into `tempfile.mkdtemp()`,
  `pininstability`'s `p` from `mkdtemp`, `undated`'s `tmp2` / `wm_tmp`)
- still unfoldable, no call site supplies a folding value: **1** (`stalecutoff` -- `e328`'s site is
  a selftest fixture and every published `e365._write` call site in that module points at a temp
  root)
- parent tally reproduced 9/9

Verdict: `most_unfoldable_writes_are_one_hop_from_the_reader_directory`

## The three lessons
1. **"The argument does not fold" mixes delegation with run-time supply.** Inside the callee both
   look identical -- a name with no binding -- but a helper parameter is one call site away from a
   literal while `argv`/`environ`/`tempfile` is unreachable at any depth. The deciding evidence is
   the value at the **call site**, not the binding shape inside the callee.
2. **A parameter default is a statically reachable hop.** `write_face(face, root=ROOT)` called as
   `write_face(face)` hands the helper `ROOT`; enumerating only explicit arguments reads that as
   "no call site supplies it" and invents an unreachable defect (first version of this face did
   exactly that on `e359` -- 1 of the 9 flipped only after defaults were folded).
3. **Keep the directory position apart from the basename position.** In
   `os.path.join(outdir, name)` the directory can arrive while the name is still a parameter; that
   half-arrival is a third reading. Folded into "reached" it overstates the module, folded into
   "not reached" it hides a real placement -- both would have been wrong for `banddraw`.

## Scale notes
The face follows at most three caller hops and only same-module bare-name call sites; a helper
that forwards its parameter to a second helper is published as one hop, not chased to the end. A
folded value says the composed string equals the reader path -- it does not claim the file exists
or that the branch executes.

## Verification
`scripts/e490_write_helper.py`: run rc0, check `problems=[]`, verify re-builds `problems=[]`,
selftest **24/24** (one-hop helper, loop variable, parameter default, caller parameter chain, argv
supply, no call, six doctored fixtures). Face `results/state_tilt/WRITEHELPER-2026-11-07.json` +
`writehelper_latest.json`. S6 leg `write_helper` rc0 0.07s
(`results/_r1515bmb_s6_chain.json`). Smoke leg *E490 an unfoldable write's directory is a helper
parameter or run-time supply* standalone 1/1 green, three doctored copies 1/1 red.