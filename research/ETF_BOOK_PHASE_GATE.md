# A gate that cannot say "I cannot tell" is not a gate — and the sibling book it
# admitted only a week ago is refused two phases in five (r1420 bm-c)

r1419 ended on its own next step: *"the yearly gate must be phase-robust before it
adjudicates adoption — a gate that admits a book must also admit that it cannot tell."*
This round builds that word and then re-asks r1418's two questions with it.

## The apparatus

`scripts/candidate_year_gate_phases.py` (selftest 13/13). A book is priced at **five weekly
decision starts** (2020-01-01 … 2020-01-29 = offsets 0/5/10/15/20 bars, exactly one 20-bar
rebalance block), each phase goes through the frozen gate
(`candidate_year_gate.admission_block`, imported; the four lines and the capacity floor are
imported too), and then:

```
v       = the set of per-phase verdicts
m       = median per-phase top-2 share
spread  = max − min of per-phase top-2 share
margin  = |m − 0.70|
if len(v) == 1 and spread <= margin  →  that verdict
else                                 →  UNADJUDICABLE_PHASE
```

The rule was frozen in the file before any number was read and is printed into the receipt.
Bit-identity leg: phase 2020-01-01 reproduces **every published yearly row of r1418 to
max|diff| 0.0** and the same verdict.

## What it says

| book | phase reads of top-2 share | single-phase verdict | adjudication |
|---|---|---|---|
| `nobond_vt08` (adopted) | 71.08 / 79.46 / 79.58 / 79.82 / 79.62 | CONDITIONAL | **CONDITIONAL** — 5/5 agree, spread 8.74pp inside the 9.58pp margin |
| `nobond_base` | 68.98 / 67.98 / **82.07** / **88.80** / **83.25** | ADMIT | **UNADJUDICABLE_PHASE** — ADMIT, CONDITIONAL, REFUSE all appear |
| `nobond_vt08` floor 0.5 | 66.85 / 74.58 / 78.92 / 79.95 / 80.81 | ADMIT | **UNADJUDICABLE_PHASE** — ADMIT vs CONDITIONAL split |

Three readings, in order of how much they change the desk's picture:

1. **r1418's ADMIT of the sibling is a phase artifact.** `nobond_base` read 68.98% on the
   phase r1418 used — 1.02pp under the line — and reads 82.07 / 88.80 / 83.25 the following
   three weeks, one of which is a **REFUSE** (it also breaks Y3: worst year < −15pp). Three
   of five phases are *further* over the line than the adopted book ever is. The published
   reading was the most favourable of five.
2. **The overlay that "pushed the book over the line" is the thing that made it readable.**
   r1418 concluded the 8% vol target cost the book its admission (71.08% vs 68.98%). Across
   phases the ranking inverts: the adopted book is the only arm with a unanimous verdict and
   the smallest spread (8.74pp); its un-overlaid brother swings 20.82pp and cannot be
   judged at all. A de-risking layer that narrows the calendar's phase sensitivity is doing
   the job a gate cares about, even while it raises the concentration statistic on the one
   phase we happened to look at.
3. **r1419's refusal to adopt the floor is confirmed by the repaired gate, not by a 3-of-4
   count.** Floor 0.5 ADMITs at phase 0 and CONDITIONALs at the other four; the honest word
   is "cannot tell", and no production change follows.

## Consequence for the desk

The adopted book stands: it is CONDITIONAL on Y4 and now we know *how* thin that is —
every phase fails Y4, by 3–10pp, with the noise band (8.74pp) as wide as the margin
(9.58pp). It is not "1.08pp away from admission"; it is a book whose calendar
concentration is real and roughly phase-insensitive, which is a much firmer statement
than r1418 could make. Nothing is changed in the production configuration this round.

The gate's own status: `candidate_year_gate` remains the adjudicator for single receipts;
the phase-set wrapper is the adjudicator for **adoption**, and it is now the only form in
which this desk may call a book admissible or inadmissible.

## What was not measured

The phase set is four weeks (one rebalance block); a longer block (60/120 bars) is a
different question not priced here. ETF universe is survivorship-biased. 2026 is an
8.6-month partial year inside every phase. The floor arm only rescales one selection
sequence. Capacity is the 5%-participation figure inherited from r1418, not an AUM claim.

Pos = `scripts/candidate_year_gate_phases.py` (selftest 13/13) +
`results/etf_book_phase_gate.json` + methodology card E424.