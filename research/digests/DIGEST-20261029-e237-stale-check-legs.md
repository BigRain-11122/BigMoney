# E237 digest -- a check-only leg is red on every panel advance, and the three that were red were read as "red" for 1.5h

r1346 bm-c — `Tools/s6_chain_bmc.py` (selftest 5/5, new) — faces re-derived on the
2026-10-29 bar (`results/etf_book_hysteresis.json`, `results/etf_book_buffer_adoption.json`,
`results/etf_book_cagr_reconcile.json`) — card E237.

## The hole

Six chain legs are ENGINE-FREE gates: they re-read a published face and refuse to let it
drift from the card. They are cheap (0.1s) on purpose, and they were written to go **RED**
the moment the production card advances past the bar the face was priced on. That is a
correct assertion and a broken mechanism:

- The panel advanced to 2026-10-29. Three legs went red at 19:27 and were still red at
  20:57 — through two complete chain runs (`results/_r1344bmc_s6_chain.json`,
  `results/_r1343bmc_s6_chain.json`), both of which printed the same line and moved on:

  ```
  NONZERO: etf_book_cagr_reconcile=2, etf_book_hysteresis=2, etf_book_buffer_adoption=2
  ```

- The reason in all three cases was the same sentence: *"face is stale: priced on
  2026-10-28 while the production card is on 2026-10-29"*. Nothing was inconsistent. The
  faces were simply one bar behind, and the only way to fix that was for a human window to
  notice and type three commands.

That is the r1135 shape: **a gate that is permanently red on inherited state**. The
cheapest repair for the next window is to relax the assertion, and then the gate stops
protecting anything. The correct repair is to give the gate a second exit: *stale* means
"re-derive me", *inconsistent* means "something is wrong".

## What was built

A leg may now carry a third element — the refresh command — and the runner pays it **only
when the probe's own output says the face is stale**:

```python
("etf_book_hysteresis", ["python", "scripts/etf_book_hysteresis.py", "--check"],
 ["python", "scripts/etf_book_hysteresis.py", "run"]),
```

After paying it the probe is re-run and the record carries
`"refreshed": {"cmd": [...], "rc": 0, "elapsed_sec": 46.2}` so the round report can show
that a face was re-derived rather than quietly replaced.

Selftest (5 legs) pins the branch that matters, in both directions:

1. a stale probe pays its refresh once and comes back green;
2. an **inconsistent** probe stays red **with its refresh unspent** (the fixture asserts the
   refresh's marker file was never written — a gate that spends its refresh on any failure
   has become a machine for making red go away);
3. a leg without a refresh declared is unaffected;
4. every leg is `(name, cmd[, refresh])` with list commands;
5. the six check-only legs declare a refresh.

## The same change broke two readers, and both were silent

`LEGS` grew from 2-tuples to (optionally) 3-tuples, and every consumer that unpacked
`for n, _c in LEGS` broke:

- `smoke_test.py` — six sites (leg-presence and leg-ordering assertions).
- `scripts/etf_book_registry.py::chain_legs()` — wrapped in `except Exception: return None`.
  A swallowed `ValueError: too many values to unpack` would have reported **"no legs wired"**
  instead of crashing (the r1288 family: an excepted type error fabricating a plausible
  answer). Fixed at the source, with the reason in the docstring, and the live reading is
  now `chain_legs() -> 84`.

## What the refreshed faces say (2026-10-29 bar)

- **hysteresis** — green on the new bar; k=0.50 arm turn 0.702, CAGR 9.66%, Sharpe 0.997,
  maxDD -13.48% (k=0.35: 9.59% / 0.993 / -12.57%).
- **buffer adoption** — verdict REJECT, 60 cells, median ΔCAGR **-0.145pp** against a
  -0.05pp floor (turnover down in 100% of cells, CAGR better in 55%, phase IQR 0.70pp):
  the buffer buys turnover, not return, and the return reading is inside the phase noise.
- **cagr reconcile** — OK on the same bar: card **9.70%**, executable ticket **13.50%**,
  total gap **3.80pp**, interaction **-1.24pp**. The reconcile face had also gone stale for
  a different reason — a source face it reconciles was re-derived to a new headline
  (`capacity_ceiling_pp` 7.28 -> 7.27), which is exactly the dependency the face was built
  to catch; it caught it, and then nobody re-derived it.

## Consequence

A check-only leg without a declared refresh is now a bug, not a design: it can only be
green on the bar its face was priced on, and the round that advances the panel is the round
that turns it red. The 6 legs are wired; the pattern (probe + refresh, refresh paid only on
stale) is what the remaining gates should copy.