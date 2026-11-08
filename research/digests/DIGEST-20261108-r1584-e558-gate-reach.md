# DIGEST — E558: does a `--check` gate leg notice its face going missing? (r1584 bm-b)

**Study**: `scripts/e558_gate_reach.py` (build / check / verify / selftest 28/28)
**Face**: `results/state_tilt/GATEREAD-2026-11-08.json` + `gateread_latest.json`
**Parent**: `results/state_tilt/faceentryreach_latest.json` (E557's five gate-leg rows)
**Verdict**: `some_gated_faces_would_vanish_without_their_gate_noticing`

## The question

E557 closed by saying the three `--check` legs "prove the face is still right but can never
rebuild it". That sentence covers repair. It does not cover **noticing**. A gate can refuse a
deleted face correctly and still leave every process on the machine green, so "there is a gate"
and "the loss would surface" are two measurements, not one.

## Method (static, controlled)

Population read out of E557's own face (`rows[].gate_entry_points`, kind = chain gate): **5
leg×face pairs / 3 distinct legs / 3 writers** (two legs serve two faces each).

For each row the gate verb's own entry path is followed: `main()` → the `add_argument("--check")`
dest (including a renamed `dest`), → that flag's branch body, → every local function it calls,
transitively (all five resolve to `check` → `check_payload` → `verdict_for`). Inside that
function set:

1. **is the face opened?** a load call (`open`, `read_text`, `json.load`) whose argument folds to
   the face path through the module's own constants, including `Path(__file__).resolve().parents[N]`
   and `with open(...) as fh` handles. A write-mode `open(...,"w")` / `write_text` is never a read.
2. **is a missing file refused?** an explicit `if not <face>.exists():` branch (or
   `except FileNotFoundError/OSError`) whose body returns non-zero, raises, or `sys.exit(non-zero)`.
3. an unguarded load is published as its own class — non-zero exit, but by traceback.

Third arm: the chain runner's own exit semantics (does the process carry a failing leg?).

## Readings

- **2 of 5 faces would be refused; 3 would not be noticed at all.**
- By face kind: **machine-readable 2/2 refused** (`results/etf_book_premium_phases.json`,
  `results/etf_book_voltarget_phase.json` — both `if not OUT_JSON.exists(): raise SystemExit(...)`);
  **rendered faces a human reads 0/3 opened by any gate** (`research/ETF_BOOK_BUFFER_ADOPTION.md`,
  `research/ETF_BOOK_PREMIUM_PHASES.md`, `research/ETF_BOOK_VOLTARGET_PHASE.md`).
- The buffer gate *does* refuse a missing file — but the file it refuses is
  `results/etf_book_buffer_adoption.json`, and the row E556 carries for that writer is the `.md`.
- Runner arm: all three chains record each leg's rc, compare it to zero and print `NONZERO`;
  **0/3 process exits carry the failure** (bm-b's `main` returns 0 after the `bad` list; bm-c/bm-a's
  `main` has no return at all, falling off the end → 0).
- Calibration: `raise SystemExit("…")` and `sys.exit(1)` both measured rc=1, so a refusal *is*
  visible on the runner's record face — what is invisible is its effect on the process outcome.

## Four reusable lessons

1. **A refusal is the leg's ability; being noticed is the runner's.** All three runners record
   correctly and still exit 0, so "a gate would refuse" is worth one line in a receipt. Any
   upstream that reads the exit code (scheduled task, watchdog, CI) sees green.
2. **The gate guards the machine face; the copy a human reads is opened by nobody.** Same build,
   two artefacts, `--check` opens only the `.json`. Deleting the `.md` leaves `--check` green.
   "A gate exists" is not "the artefact is guarded" — ask per artefact who opens it.
3. **Follow the flag branch plus its local-function closure; the build path does not count.**
   Guards sit in `check_payload`, not `check`, in all three writers; symmetrically, a load reached
   only from `build()` must not be counted as a gate read (both nailed as fixtures).
4. **Measure a path folder before you reuse it.** E554's folder stops at `Path(...).parents[N]`;
   three of the four writers spell `ROOT` that way. Reusing it as-is reads all five rows as
   "never opened the face" — same tree, same sources, and the finding inflates from
   *2 refused / 3 invisible* to *0 / 5*. (Measured: it folded 1 of 4 module `OUT_JSON`s.)

## Bound (published with the face)

Static only. A run-time path is `unfoldable`, never "unread". A cross-module helper is not
followed, so such a gate reads as "never opens the face" — the control arm is the guard against
that being taken as proof (in `etf_book_hysteresis` the gated JSON must read **refused** and the
`.md` the same module writes must read **invisible**). "Would be noticed" is a statement about the
leg's exit code, not about a human reading the receipt; that is why the runner arm is separate.

## Wiring

- S6 leg `gate_reach` (`python scripts/e558_gate_reach.py check`, 1.9 s rc=0) in `Tools/s6_chain_bmb.py`
- smoke leg `# E558` in `smoke_test.py` — re-derives every class, refuses a hand-written verdict, a
  relabelled outcome, a count that does not re-derive and a runner arm that does not re-derive
- card E558 in `knowledge/METHODOLOGY_ASSETS.md`, row in `knowledge/TREASURE_REGISTRY.md`

## Next

E559 (seeded): now that the JSON faces are refused but nothing carries the rc, ask whether *any*
task definition on any of the three machines reads a chain receipt or a leg rc — the population
being every scheduled task whose action runs a chain runner, plus every source that opens
`results/_r*bm*_s6_chain.json`.