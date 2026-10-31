# DIGEST — r1322 bm-b · E294 live-universe drift

**Question.** r1314 froze the BAND family's census to its publish-time vintage because four smoke legs
went red on a directory that had grown (E286 32 → 34 faces, E281 27 → 34, E282 55 → 67). The freeze
stopped the drift. It did not answer the question underneath: *was any published verdict a function of
the directory it happened to see?*

**Method.** Every study script in the family is classified by behaviour (does it glob the face
directory, or read named faces only). Each directory-censusing study is then re-derived twice inside
one process — once against the *frozen vintage* (the faces whose own `generated` stamp is no later than
the study's) and once against the *live directory* — and its verdict classified three ways:

| class | meaning |
|---|---|
| `reproduces_and_stable` | frozen == published **and** live == published |
| `reproduces_and_flips` | frozen == published, live ≠ published → the verdict is a function of the universe |
| `does_not_reproduce` | frozen ≠ published → already drifted for another reason; attribution refused |
| `not_measurable` | `build()`/`run()` takes no universe argument, or raised |

Only the universe is varied. Faces loaded **by name** come from the live directory in both readings —
the family's `load(name)` helpers take no `outdir`, so that is fidelity, not a shortcut.

## Findings

1. **The family is 54 study scripts; only 12 census the directory.** The other 42 read named sibling
   faces, which are pinned by name and therefore vintage-stable by construction. Any statement of the
   form "the family is unaffected by the universe" has to carry that split.
2. **Of the 12, nine can be varied and every one prints the same verdict.** The largest exposure is
   `e277_tight_multiplier_floor.py`: its published vintage saw 47 faces where the directory now holds
   81 (34 gained) and its verdict does not move. `e281` (+28), `e282` (+26), `e283` (+24), `e284` (+22),
   `e286` (+18), `e293` (+12), `e287` (+10), `e278` (+32) — all stable.
3. **Three cannot be asked without editing their code** (`e290`, `e291`, `e292`: `build()` takes no
   universe argument). They are named with their reason, not guessed.
4. **Verdict: `no_published_verdict_moves_with_the_universe`.** The drift r1314 fixed was a
   *reproducibility* problem, not a *conclusion* problem. That distinction is the deliverable.

## Traps this face had to survive

1. **Tautology under `extend`.** Four studies own a freeze switch (`build(outdir, extend)`). The first
   build passed them a staged directory while leaving `extend` at its default `False` — i.e. it ran the
   *same frozen computation twice* and manufactured four stable verdicts. Correct branch: vary the
   switch they own (`extend=False` vs `extend=True`). The smoke leg now asserts that no "stable" row
   came from two identical calls (`" vs "` must appear in the row's `varied` text).
2. **In-process hang.** The first attempt ran every study in the parent process; one wedged and took the
   whole census with it (cancelled after 5 minutes of silence). Each study now gets its own child
   process and a wall-clock cap, and a cap that fires is published as `not_measurable` with the reason.
3. **Self-inclusion.** This face is itself `BAND*`, so publishing it would shift the very census it
   measures. Its own two files are excluded and the exclusion is asserted as a leg.
4. **Case-insensitive glob.** The family's census glob is `BAND*.json`, and on this filesystem that also
   matches the `band*_latest.json` mirrors. They were always inside every study's universe; narrowing
   the glob here would silently change all of them, so it is disclosed rather than fixed.
5. **Membership by behaviour, not by path literal.** Filtering candidate studies on the string
   `state_tilt` misses every study that takes `OUTDIR` from a sibling — which is exactly the frozen
   ones. Membership is `globs BAND*.json` OR `imports e_band_family_vintage`.

## Files

* `scripts/e294_live_universe_drift.py` — runner (`run` / `verify` / `selftest` / `measure <script>`);
  selftest **36/36**, `verify` **0 problems**.
* `results/state_tilt/BANDFROZEN-2026-10-29.json` + `bandfrozen_latest.json`.
* `Tools/s6_chain_bmb.py` leg `live_universe_drift` — `rc=0`, 6.3 s through the real driver.
* smoke leg E294 — extracted verbatim and executed standalone: PASS; 4/4 mutations caught (a stable
  row's live verdict changed, self-inclusion, inflated family shape, status counts losing a row).
* `knowledge/METHODOLOGY_ASSETS.md` card **E301**.