# DIGEST 2026-11-01 r1342 bm-b — E322: the refusal was the needle, not the repository

## What E321 said

E321 (r1341) priced the producer side of the gate-naming census and its verdict sentence
published this clause:

> 25 gates have no producer that publishes the key at all, so no reading of the producer can
> name them.

That is a claim about the repository: a gate whose writer does not exist cannot be named from
anywhere. E322 asks that clause one question — is there a writer on disk?

## What is true

The 25 rows are **4 faces**, and **every one of them has a writer on disk**.

| rows | face | writer found via |
|---:|---|---|
| 22 | `results/state_tilt/GATEOPERANDS-2026-10-31.json` | ISO template → `GATEOPERANDS-%s.json` → `scripts/e312_gate_operand_identity.py` |
| 1 | `results/e40_cashleg_drag/CASHLeg-20261027.json` | compact date → `CASHLeg-%s.json` → `scripts/e39_panel_census.py` |
| 1 | `results/shortline/p1e_nulls_M_arc.json` | name prefix → `p1e_nulls_M` → `scripts/p1e_ic_batch.py` |
| 1 | `results/shortline/p1e_nulls_M_close_tr.json` | name prefix → `p1e_nulls_M_close` → `scripts/p1e_ic_batch.py` |

Three mechanical steps account for all of them:

1. **The auditor is excluded from its own corpus.** `e312.sources()` skips `_OWN` (its own file)
   so that a census cannot quote itself. The cost is that any face `e312` writes becomes
   unowned: `GATEOPERANDS`'s producer *is* the module doing the looking. 22 of the 25 rows are
   this one face, counted once per gate row.
2. **The date substitution only knows ISO.** `producer_candidates()` rewrites `YYYY-MM-DD` to
   `%s`. This repo also dates faces compactly — `CASHLeg-20261027` — where the ISO pattern never
   matches, so the template attempt is a no-op and the search falls back to the exact filename,
   which no source spells.
3. **A composed name appears nowhere literally.** `p1e_ic_batch` writes
   `f"p1e_nulls_{cls}.json"`; the class is a variable, so the published filename exists only at
   runtime. A needle built from the concrete name cannot survive that, and the fix is a name
   prefix, not a looser match.

## Why this matters beyond the count

* E321's 10.7% "named by their producer" is a **lower bound measured with a needle that refuses
  four faces outright**. The refused population is small (25 rows) but it is not random: it is
  exactly the shapes a needle is blind to — self-written, compact-dated, composed. Any face with
  one of those shapes reads as unowned regardless of what its writer says.
* The same three gaps are available to every row E321 classified, so the census should be
  re-priced under the wider needle before its share is quoted. That is E323.
* The self-inclusion defect has now been observed in both directions in this family: E204/r1232
  found a scanner that counted *itself* as a reader; E322 finds a scanner that excludes itself
  and thereby loses its own output. Excluding self is right for *reading* and wrong for
  *ownership*, and the two uses need different corpora.

## Instrument

`scripts/e322_residual_refusal_causes.py` — `run|build|verify|selftest`, selftest 17/17, verify
`problems=[]`, wall <1s. Face `results/state_tilt/REFUSALCAUSE-2026-10-31.json` +
`refusalcause_latest.json`; S6 leg `refusal_cause`; smoke leg tied to E321's own row count so the
two faces cannot drift apart.

Verdict: `every_refused_row_has_a_writer_on_disk_so_the_needle_was_the_defect`.

## First-burn defect (recorded, not hidden)

The first burn resolved two faces to `the_name_is_spelled_in_the_writer` with the writer
`scripts/e322_residual_refusal_causes.py` — the scanner matched **itself**, because it names the
filenames it is looking for in its own docstring and legs. Fixed by excluding only this file
(keeping every other auditor), plus leg L12b pinning that this scanner is not in its own corpus.
The r1232 self-inclusion trap fires in both directions.