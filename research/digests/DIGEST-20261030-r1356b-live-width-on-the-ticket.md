# r1356b — the width ruler reaches the order sheet (and the label stops being a receipt)

2026-10-30, bm-c. Face: `results/etf_book_order/ORDER-2026-10-29.md` + `TICKET-2026-10-29.json`.
Script: `scripts/etf_book_order.py` (selftest 39 → 52).
Parent digest: `DIGEST-20261030-r1356-live-width-ruler.md` (the measurement itself).

## What was wrong

r1356 answered the question an operator actually holds — *is the 12-vs-5 gap worth reading
as a width effect?* — and published it to `results/etf_book_live_width_ruler.json` and a
research page. The ticket, the one document a person opens to place the order, said nothing
about it. That is the r1275 shape exactly: a difference that only lives in `research/` is a
difference nobody was told about.

## What shipped

`live_width_ruler()` in `etf_book_order.py` reads the face back into the ticket:

* `TICKET-<asof>.json` gains a `live_width_ruler` block (state, paired gap, disagreement,
  share, pairs, cutoff, width-by-width priced-vs-live names/rules).
* `ORDER-<asof>.md` gains a section that puts the numbers in front of the reader:
  today `中位差 +0.09pp（20 个相位，10 上 10 下，区间 -2.05 ~ +2.89）`, the same 5→12 rung
  on the second engine `-1.53pp`, the two engines' disagreement `2.04pp` **with the sign
  flipped**, and the one sentence that makes it usable: the gap is **4.4%** of that
  disagreement, so "how much worse is the ticket than the card" is not readable in this
  window; most of the difference between the two documents is the leverage rule, not the
  name count.
* A non-clean ruler changes what the sheet says and lands a caveat in the payload.

## The verdict is re-derived, not copied

The face publishes a label (`COIN_FLIP_INSIDE_ENGINE_DISAGREEMENT`). The ticket does **not**
copy it: it recomputes `|paired median| < |5→12 rung disagreement|` and the sign split from
the face's own published numbers, and if the two disagree the state is `inconsistent`
(r1266: a verdict that can drift away from the numbers that produced it is a receipt).

Five states, each with its own selftest fixture:

| state | meaning |
|---|---|
| `inside_disagreement` | gap is inside the engines' own disagreement and the signs split |
| `separated` | the paired gap is at least the size of the disagreement |
| `inconsistent` | the published label contradicts the published numbers |
| `widths_moved` | the face priced widths the live faces no longer run |
| `stale` | cutoff more than 10 calendar days behind the priced bar |
| `unavailable` | no face on disk (says so; never silently clean) |

## Pitfall recorded — the two faces spell the same rule differently

The card artefact reports its rule as **`vol`**, the atlas reports the same arm as
**`vol_target`**. The first draft compared rule strings literally, so every read of a healthy
face came back `widths_moved` — a false alarm that would have trained the reader to ignore
the gate. Fix: normalise (`lower().replace("_target","")`) before comparing, and keep the raw
spellings in the block so the mismatch stays visible. Legs 40/40b/40e caught it; without
them the state would have been permanently wrong and only the ticket would have looked odd.

## Still open

The card side (`ORDER-<asof>-card.md`, produced by `etf_book_production.py` / `run_card`) does
not print the ruler yet — the executable face does, the config face does not. Next pointer:
give `card_config_card()` the same block so both documents a reader can hold agree about
which question they are answering.