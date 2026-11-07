# DIGEST 2026-11-07 r1532 bm-b — E503: the chain's own certifiers (205 read-only legs / 2932 relations)

**Ticket**: `E503-HOW-STALE-IS-THE-EVIDENCE-THE-CHAIN-CERTIFIES` (seeded r1528, burned r1532).
**Product**: `results/state_tilt/CHAINSTALE-2026-11-07.json` + `chainstale_latest.json`.

## What was asked

E501 (r1528) published 8 faces that a producer writes and no consumer reads, and every one of them
was held only by a read-only chain step. That is a statement about the *pinned population*. E503
asks it about the *chain*: for each read-only step, which face does it read, what date does that
payload publish, and does any writing-mode step in the same chain ever write that name?

## Population and classification

`Tools/s6_chain_bmb.py` LEGS folded statically (constants, lists, `os.path.join`; the chain module
is never imported, so nothing runs). 264 legs: **205 read-only** (`verify`/`check`/`selftest`/
`status`/`doctor`/`scan`), **59 writing** (`run`/`probe`/`apply`/… or no subcommand), 1 excluded
(the study's own `chain_stale` leg — the scanner must not measure itself), 0 sources that failed
to parse.

Every read-only leg's script is folded the same way to the faces it names; templates (`%s`, `{…}`,
`<cutoff>`, `*`) are resolved against a **single index** of `results/**.json` and published with
the template text.

## Readings (2026-11-07, cutoff = the round's own date)

| class | relations |
|---|---|
| bounded — a writing-mode leg in this chain names the same face | **1254** |
| widens — no writing-mode leg in this chain names it, age > 0 | **852** |
| dated today, nothing here writes it | **101** |
| no parseable date in the payload (age unpriceable) | **725** |
| named face absent from disk | 0 |
| template matches | 0 |

- Widening population: **409 distinct faces / 71,751,994 B**, age max **46 d**, median **7 d**;
  witness fields: `generated` 236 / `evidence_cutoff` 143 / `date` 19 / `ts` 11.
- Two read-only legs name no face at all (`guard_reach_claw`, `machine_health`) — published as
  `certifies_nothing`, not folded in as zero risk.
- Verdict (recomputed by the gate): `read_only_steps_certify_faces_that_no_writing_mode_leg_in_the_chain_reaches_and_those_gaps_widen_every_round`.
- mtime floor (E453) = 21 days, published beside every age; no age is derived from `st_mtime`.

## Two self-caught measurement bugs (both in this window)

1. **Byte tally summed relation edges, not files.** The first published
   `bytes_certified_while_widening` was 194,476,736 B because a face read by three clean steps was
   counted three times; the distinct-file sum is 71,751,994 B. Face count was already distinct.
   Caught by cross-checking the summary against a hand aggregation — the two numbers in the same
   face disagreed by 2.7x and neither was labelled.
2. **Recursive glob per leg did not finish.** The first draft resolved each name with
   `results/**/<name>` (hundreds of legs × a full recursive walk); a background run was still
   working after minutes and had to be stopped. One index built once is the same measurement.

Two smaller ones: the same face is routinely named twice per script (the folded `os.path.join`
*and* the template constant it is built from), which doubled the relation counts until deduped per
(leg, face); and a `*` inside a literal path was not treated as a template marker at all, so a
glob leg priced zero faces and looked clean.

## Reusable

- **A read-only step is not a validator.** It is a reader that fails loudly. When nothing in the
  same table writes the name, its age grows one day per round *by construction*, and the chain
  keeps printing a green line about evidence that stopped moving weeks ago.
- **"No writing-mode leg names it" ≠ "no writer exists."** The writer may be a hand run, a pool
  card, another machine. The 409 / 68 MB population is an upper bound on chain-attributable
  staleness, and it is published as one.
- **Age must come from the payload, never the filesystem** (E453 floor = 21 d here). 725 relations
  certify a face that publishes no parseable date at all — that bucket is E506's population, and
  it is larger than the priced arm.
- **A tally with two plausible denominators must name its denominator.** Bytes per edge vs bytes
  per file differ by the fan-in, and only one of them is "how much evidence".

## Boundaries

Population is the chain's LEGS table, not every script. Writer reach is judged inside the chain
only. A face is counted for a leg only when the leg's script names it and the file exists. Ages use
the payload's own date field; a face whose only date is prose is `no parseable date`, not stale.
Templates that match nothing are absent, not stale.

## Verification

`scripts/e503_chain_stale.py` — `run` rc0 / `check` problems=[] / `verify` problems=[] (rebuild
identical) / **selftest 23/23**. S6 leg `chain_stale` rc0 0.06 s
(`results/_r1532bmb_s6_chain.json`). Smoke leg `E503 ...` extracted verbatim:
1/1 green, doctored 1/1 red, face restored byte-identically (sha `a1929505ae97`).