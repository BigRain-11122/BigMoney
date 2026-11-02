# DIGEST 2026-11-03 r1396 — E374: which of the store's 128 members are load-bearing

**Card**: E374-WHICH-STORED-MEMBERS-ARE-LOAD-BEARING (ready, priority 2, entered r1393)
**Source**: E373 TWOPINS-2026-11-02 (E353 pairs 129 at its own pin, 131 with the publish-day members;
bill 128 members absent from both commits)
**Face**: `results/state_tilt/STORELOAD-2026-11-03.json` (+ `storeload_latest.json`)
**Script**: `scripts/e374_store_load_bearing_members.py` (selftest 8/8)

## What the card asked

E372 paid 128 recovered members to bring E353's `pairs` from 129 to 131.  The card asks: take the two
pairs, name the face/field behind each, walk the store statically for the members that define those
faces or write those fields, and prove with **one** ablation replay that the remaining members change
no published number.  Target: a store whose size a reader can justify.

## Answer in one line

Three members of 128 carry the whole difference; 125 are paid for nothing on this yardstick — and the
difference is not "two pairs added", it is **three pairs gained and one paid back**.

## The four arms (one pin, four scans)

Pin = E369's `CORPUSPIN-AT-COMMIT-daf9a897.json`, 2,251 members read from that tree, not from today's
disk.  Store = `research/corpus_store/PINSTORE-daf9a897.json`, 128 members, 789,753 bytes.

| arm | population | E353 `pairs` |
|---|---|---|
| A pin only | 2,251 | 129 |
| B pin + whole store | 2,379 | **131** |
| D pin + store minus the load-bearing set (125 dropped) | 2,376 | 129 |
| C pin + the load-bearing set only (3 kept) | 2,254 | 131 |

D returns to A's pair set **exactly** (set equality, not just the count) and C returns to B's, so the
three members are both necessary and sufficient for what the store buys.

## The moved pairs

Gained (3):

| face | field | who guards it | line |
|---|---|---|---|
| `bm-b.json` | `heartbeat_epoch_utc` | `Tools/_r1334bmb_closeout.py` | 166 (`assert_guard`) |
| `bm-b.json` | `round` | `Tools/_r1334bmb_closeout.py` | 167 (`assert_guard`) |
| `state-bm-b.json` | `r1334` | `Tools/_r1334bmb_delivery.py` | `assert_guard` |

Lost (1): `results/runnable_pool.json:entries` — `Tools/_r1234bmb_pool.py` writes that field, so a pair
the pin counted as unwritten stops being one once the writer is in the population.

Net +2, which is what 129 → 131 reads as.  The arithmetic in the card hides a swap: the store does not
add two pairs, it adds three and removes one.

## What the store actually buys

Every gained pair is a guard on the **firm's own status faces** (`bm-b.json` heartbeat fields,
`state-bm-b.json` round key) — bookkeeping that the operators maintain by hand, asserted on by closeout
scripts, and never written by a corpus source.  That is a real pair, and it is the one class of pair a
recovered corpus genuinely repairs: the instrument's own operator loop.

None of the gained pairs is on a research face.  So the card's framing ("the rest are paid for
nothing") holds for the yardstick E353 uses, and — per E371 — even for the yardstick E350 uses, where
the store moved only the source count.

## Reusable findings

1. **A count delta is not a change set.** 129 → 131 is compatible with +2, with +3/−1, or with +40/−38.
   Any "the store buys N" sentence has to be published as gained/lost pair lists, never as a net.
   E374 publishes both directions and the net as three fields.
2. **Load-bearing must be earned per member, by a line, not inferred from the total.** Membership here
   is "carries an assert/exit guard on a moved field" or "writes a field whose pair the store removes";
   an unbranched read of the same field earns a row note but not membership, because a read that is not
   a guard creates no pair. Pruning the store by "it changed the count" would have kept all 128.
3. **The ablation is the only thing that settles indirect paths.** The static walk cannot see a member
   that feeds a pair through a helper two calls deep; the D arm can, and it is one replay of the whole
   population, not 128 replays. Cost: one extra scan (~170 s) to replace 128 of them.
4. **"Load-bearing" is a property of the yardstick, not of the member.** E371 already published that the
   same two store_needed members bind and write no field of E350's arm. A store's size is justified per
   instrument; the honest sentence carries the instrument's name.
5. A member that *parses* is not a member that *counts*: the store's own rule ("recovered only when the
   bytes hash to the pin's sha") is what makes the ablation meaningful — the 125 dropped members were
   recoverable, they were simply irrelevant.

## Bound

The load-bearing set is measured for E353's unwritten-guard pairs only; membership is a guard on a moved
field or a writer for a removed pair, so an indirect feeder is caught by the ablation rather than the
walk; the pin is E369's pinned bytes, so a member today's tree has since changed is judged on the bytes
the pin says it had.

## Cost

Four corpus scans (~130–170 s each), one static walk over 128 members (seconds). Nothing executed from
the corpus; only `ast` and `json.load`.