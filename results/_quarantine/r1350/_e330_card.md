## E330 -- a decision between two references is only a decision if something asserts it, and only dangerous if the branches already disagree

E329 found one resolver whose order decides which cut a reader gets. E330 asked the mechanical
question behind it: across 2,284 sources and 646k code lines, which constructs pick between two
references to one family, and which of those picks does no assertion name? Four shapes make such a
pick -- the order of an existence chain, an `or` whose left side can be empty, an argparse default
that names a face, and a mutable default argument whose object survives call N-1 into call N. The
tree makes exactly **one** of them: e242's `_face_file`, a pointer-first chain with a pinned
2026-10-29 fallback, and it is unpinned. Zero argparse defaults name a face (39 `add_argument`
lines seen, all numeric or plain paths), and zero functions in the corpus carry a mutable default.

Three measurement rules came out of the work, and each of them found its own bug first:

- **The operator has to be code, the handles have to be quoted.** A handle lives inside quotes by
  construction, so a scanner that greps the raw line counts its own test input as a decision: e329's
  own `handles_in_line('for cand in (...)')` line read as a second fallback chain. Blank the quoted
  spans at unchanged length and ask the *mask* where the `for ... in` and the `or` are.
- **Two branches, or it is not a choice.** Of 35 lines offering an `or` beside a face, 34 carry a
  face on one side only (`os.path.join(outdir or OUTDIR, "x_latest.json")`) and are not a choice
  between two vintages. Rejecting them is a population cut that must be *published* (34 rejected),
  because a silent cut looks exactly like a clean corpus.
- **A chain is one decision but many stems.** Reporting the first stem's vintage beside another
  stem's flag is the same-name-different-quantity mistake: `outcome_today` came from AGGATT while
  `swap_changes_today` came from owncross. Publish `per_stem` and take the row-level reading from
  the first stem where the branches actually disagree.

What a two-line change would cost, measured rather than argued: for 2 of the chain's 4 call-site
stems (owncross, sharediff) the pointer holds 2026-10-30 while the pinned fallback is 2026-10-29, so
swapping the two candidates today returns an older cut with nothing going red; for per_member_gamma
the pinned branch names a cut that is not on disk at all and returns None.

How to apply: when you write a chooser, name it, then assert the choice in a leg -- the name is what
an assertion can cite; and when a census returns zero for a class, publish the lines you rejected,
because zero-with-a-cut and zero-with-a-proof are different facts.

Evidence: scripts/e330_unpinned_choice.py (selftest 30/30, verify problems=[]) ->
results/state_tilt/UNPINNEDCHOICE-2026-11-01.json + unpinnedchoice_latest.json; S6 leg
unpinned_choice (~40s, corpus scan); smoke leg "product: every two-reference decision in the tree is
counted, and the ones no assertion names are separated from the ones whose branches already
disagree"; research/digests/DIGEST-20261101-r1350-e330-unpinned-choice.md