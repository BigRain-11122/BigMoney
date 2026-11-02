# DIGEST 2026-11-03 r1395 bm-b -- E371: what one store_needed member costs (two zeros, neither of them a number)

**Face** `results/state_tilt/STOREMEMBERCOST-2026-11-03.json` (+ `storemembercost_latest.json`)
**Runner** `scripts/e371_store_member_cost.py` (run / verify / selftest 8/8, verify 0 problems)
**Card** E376 · **Pool** E371 closed with `result_ref` · **Pin** `1244ee231290e6ed13979acf474feb14dddd0dd0`

## The question the card asks

E368's seam replay resolved 2,361 members from disk, 6 from the pin's commit and the rest as
`store_needed` -- members the pin recorded but git cannot supply at the pin commit, replayed from
today's disk. E366 had billed the store as the expensive half of a pin; the store_needed member was
a footnote. Bill it: which face fields does it bind or write, does any of them appear in E350's
writes set, and would its absence move any arm's number?

## The bill

The store is **two members**, not one (`Tools/gpu_face.py`, `Tools/s6_chain_bmb.py`) -- the second
became store_needed after the E368 face was published. Both are **footprint-empty** under both byte
arms: 0 reads, 0 writes, 0 json bindings, 0 faces named. Neither is a file the field census can key,
and the replay shows what that costs:

| arm | E350 `corpus_sources` | `sources_parsed` | `fields` | `fields_with_no_writer` | guard fields / unwritten | E353 `pairs` |
|---|---|---|---|---|---|---|
| with store | 2367 | 2351 | 1947 | 1356 | 230 / 131 | 131 |
| store excluded | 2365 | 2350 | 1947 | 1356 | 230 / 131 | 131 |

Dropping both members moves **the source count and nothing else**; E353 moves **not one key**. The
store's entire measurable cost is **one parsed source that contributes no field** -- `sources_parsed`
falls by 1, not 2, because `Tools/s6_chain_bmb.py` was never parsed in the first place.

## The two zeros that are not the same zero

`Tools/s6_chain_bmb.py` starts with a UTF-8 **BOM**. The pin's bytes are read as UTF-8 (not
UTF-8-SIG), so `ast.parse` refuses the text (`invalid non-printable character U+FEFF`) and the member
is recorded as **unparseable**. Strip the BOM and it parses to **nothing**. Those are two different
statements -- "I could not read it" and "I read it and it says nothing" -- and a census that folds
the unparseable into the empty has silently converted a blind spot into a measured zero. Both arms
are published per member (`as_pinned` / `bom_stripped`) and a selftest leg pins the difference.

## Why the footprint is empty at all, and why that is the real cost

Both members do write faces -- `Tools/s6_chain_bmb.py` writes
`results/_r<round>bmb_s6_chain.json`, `gpu_face.py` writes the heartbeat -- but each builds its path
**at run time** (`"results/_r%sbmb_s6_chain.json" % rnd`). The instrument keys a face by a literal or
constant path, so a computed path is a write no census can name. The footprint therefore publishes
the dump-call census beside it: `gpu_face.py` 2 `json.dump` calls / 2 unresolved paths,
`s6_chain_bmb.py` 1 / 1. **Zero fields is not "writes nothing"; it is "writes something the ledger
cannot key"**, and that is what the store is actually paying for.

## The missing-writer question, and how far the answer reaches

For each of the (face, field) pairs E350 calls an *unwritten guard*, ask whether either member's own
text names both the face and the field -- the only question a census that cannot key computed paths
can still answer. **0 of the 40 published rows name a store member.** Bound published with the
answer: the face carries 40 of the 131 counted rows, so **91 are untested**, and `name_reach` ships
`tested / counted / untested` so a residue that was never tested cannot read as a residue cleared.

## What a reader should take away

1. A store member's cost is not "one file" -- it is whatever the instrument cannot see. Here that is
   exactly one parse and no number, which makes the store cheap **on this instrument** and says
   nothing about what the members do at run time.
2. `unparseable` and `empty` must be published apart, or a BOM silently buys a measured zero.
3. A census that keys faces by resolved paths cannot see a formatted path, so "no writer" verdicts
   are "no writer with a nameable path" -- publish the dump-call census beside the footprint.

## Bounds

Name reach is a substring test over two files, so it can show a writer could be a member, never that
it is; the replay compares published numbers to two arms of the same instrument, so a key the
instrument never measures cannot move in either arm; the payload a member writes at run time is
outside this measurement by construction.