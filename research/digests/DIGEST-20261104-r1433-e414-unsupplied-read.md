# Digest -- r1433 bm-b: the one unsupplied pointer read is supplied by its callee

**Card.** E414 (pool card `E414-WHAT-DOES-THE-ONE-BARE-BASENAME-READ-RESOLVE-TO`, seeded r1432).

**Question.** E398 published exactly one read of a `*latest.json` pointer with class
`family_not_supplied_anywhere`: `smoke_test.py:7971` opens the bare basename
`replaycensus_latest.json` through `_m298.load(...)`, and nothing at the site names a directory.
E414 asks where that name actually lands, at every surface that runs the leg, and what happens when
the directory does not hold the face.

**Answer (measured, not argued).** The directory is supplied one hop away, by the callee:

- `load(name, outdir=None)` -> `_read(os.path.join(outdir or OUTDIR, name))`;
- `OUTDIR = os.path.join(ROOT, "results", "state_tilt")`, `ROOT = dirname(dirname(abspath(__file__)))`
  -- a constant chain that bottoms out at `__file__`;
- exercised at four cwds (repo root / `scripts/` / `results/state_tilt/` / `docs/`) by importing the
  real module and replacing its `_read` with a recorder: **one** absolute path at all four, and it
  exists (34,575 B, own `evidence_cutoff` 2026-11-01);
- corpus holders: 52 directories hold a `*latest.json` pointer (230 files); exactly **1** holds
  `replaycensus_latest.json`;
- absence behaviour: `except Exception ... check(name, False, ...)` -> the leg goes **red**; it does
  not skip and cannot silently read another family's document.

Verdict: `the_bare_name_resolves_against_the_readers_own_module_directory_so_no_cwd_can_move_it_onto_another_family`.

**Why E398's class was wrong, in one sentence.** The class grades a *site*, but the directory can be
supplied by the *resolver*; E403 had already bought that rule for signature parameters
(`param or DEFAULT`), and this is the same rule one level up (a module constant that derives from
`__file__`).

**Two closed loops that were not the question.** (a) The first run counted 231 pointer files
instead of 230, because the census publishes `unsupplied_latest.json` -- self-inclusion, the
E180/E207 family for the third time; the face now excludes its own two names and publishes
`own_faces_excluded`. (b) The counterfactual surface (`results/state_tilt` itself) is the only place
a cwd-relative reader would also have worked, which is the defect shape this population *could*
still carry -- it is not present here, and the follow-up card asks how many reads are correct only
because the cwd happens to hold the face.

**Evidence.**
- `scripts/e414_unsupplied_read.py` -- run / verify (problems=[]) / selftest (14/14)
- `results/state_tilt/UNSUPPLIED-2026-11-04.json` + `unsupplied_latest.json`
- smoke leg `# E414:` in `smoke_test.py` -- green live, red on a doctored copy (wrong verdict + a
  missing surface), face restored byte-identical (sha256 checked)
- S6 leg `unsupplied_read` -- `python Tools/s6_chain_bmb.py 1433 --only unsupplied_read` rc=0, 0.34 s
- card `knowledge/METHODOLOGY_ASSETS.md` E414

**Not done and not claimed.** The full smoke suite was not re-run this window (only the E414 block
was executed from the shipped source); the rest of the S6 chain did not run; `smoke_test.py:7971`
was not edited.