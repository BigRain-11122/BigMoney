# DIGEST 2026-11-02 · r1237 bm-a · the gate is only on the way in

**Question.** The book screens every name on a 20-bar median turnover gate of 20,000,000 CNY
(`etf_composite_pf.MIN_AMT`, imported not retyped). That number is read when a name is
**ranked**. No face in this line reads it on the bar the name is **sold**, so the book can sit
holding names it would not be allowed to buy, and the sell becomes a queue rather than a
decision.

**Face.** `scripts/etf_book_exit_liquidity.py` (selftest 23/23, `--check` re-derives the
verdict from the published rows). Production panel through the production engine, declared
arm only (score held one bar back), four decision phases.

**Readings** (evidence_cutoff 2026-10-30, 5,270 bars × 1,504 funds, 168 quote flips repaired):

| phase | start | holds | positions | exit below gate | no bar | deferred | outside cap | share below | mean defer (bars) | drag (pp/yr) |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 2020-01-02 | 82 | 984 | 39 | 0 | 14 | 25 | 3.96% | 10.57 | +0.435 |
| 1 | 2020-01-09 | 82 | 984 | 46 | 0 | 18 | 28 | 4.67% | 6.83 | +0.128 |
| 2 | 2020-01-16 | 82 | 984 | 46 | 0 | 13 | 33 | 4.67% | 7.69 | +0.014 |
| 3 | 2020-01-23 | 81 | 972 | 35 | 0 | 12 | 23 | 3.60% | 10.33 | +0.299 |

**Verdict `MIXED_ACROSS_PHASES`** under the rule frozen before the run (both readings must be
small, or both large, before it names a side):

- **incidence 4.23%** of held positions must be sold on a bar where the name would not pass the
  buy gate — above the 2% "not a constraint" line, below the 5% "real gate" line;
- **price +0.22 pp/yr** mean (range −0.01 .. +0.43), inside ±0.57 in 4/4 phases — the queue is
  real, the money is not in it (names that fell below the gate went *up* while stuck);
- **censored tail 109/3,924 = 2.78%** never found a qualifying bar inside 20 bars. Those are
  forced holds and are reported as `outside_cap`, never scored as a zero return (E346 family:
  a censored entry never reads as 0).

**What it is not.** The deferral is priced as weight × (open[t']/open[exit] − 1), i.e. an
attribution of stuck capital, not a re-priced equity curve. Impact (order size / turnover),
spread, and names that stopped existing inside the hold are out of scope; the death half is
priced as a budget by E352.

**Landed with.** Card E353, `research/ETF_BOOK_EXIT_LIQUIDITY.md`, chain leg
`etf_book_exit_liquidity` (after `etf_book_open_slicing`, bm-c chain), two smoke legs
(selftest + `--check`). Queue row E29, registered and consumed in the same round.

**Note on quoting.** The card block was first appended through a PowerShell `python -c` whose
backticks were eaten by the shell, so every backticked path lost its leading characters; it was
cut and rewritten through a file-based script and re-verified by reading the tail. Same class as
the eaten-path-prefix defect E351 scans for — and this round's own hygiene leg caught the damage
still quoted verbatim in the first version of this note, which is why the damaged strings are
described here rather than reproduced.