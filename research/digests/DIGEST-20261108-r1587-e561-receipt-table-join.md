# DIGEST 20261108 r1587 bm-b — E561: can a historical receipt still be read against its own round's table?

**Question.** E560 priced the receipt's shape and concluded that it never states the size of the
table it ran. The follow-up a triager actually has to answer is narrower and harder: this receipt
is short — was the table that short, or did the run stop / was it an `--only` subset? Two witnesses
exist and this study prices both.

## Witness 1 — the receipt itself

Only bm-b publishes `legs_total`; bm-a and bm-c publish none at all. bm-b's field is built as
`len(rows)` (`Tools/s6_chain_bmb.py:2282`), i.e. the number of legs that ran, not the size of the
table. A field computed from the thing it sits beside can never disagree with it:

| field | receipts |
|---|---|
| carry `legs_total` | 204 / 320 |
| equal to its own row count | 202 |
| disagree with its own row count | 2 (`_r252bmc`, `_r253bmc`: `legs_total=37`, zero readable rows, shape `dict_with_a_row_count`) |

So "the total checks out" is a tautology, not evidence. The only receipt that carries a field able
to disagree is one that carries no rows to compare against.

## Witness 2 — git, joined on the round in the file name

Join: `_r<N>bm<X>_s6_chain.json` → the commit whose subject is `round <N>:` (last 4000 commits) →
`Tools/s6_chain_bm<X>.py` at that commit → `len(LEGS)`. Blobs are fetched through one
`git cat-file --batch` process (3 blobs in 0.04 s; a promisor clone that does not hold an old blob
answers "missing", which is published as *no witness*, never retried).

| class | receipts |
|---|---|
| covers the table of its own round | 31 |
| **shorter than that table** | **159** |
| longer than the table it is joined to | 0 |
| no runner blob reachable | 122 |
| unparsable | 8 |
| joinable (total) | 190 / 320 |

135 of the 159 short receipts ran exactly one leg. In the file a `--only` single-leg run and a run
that was killed mid-chain are **the same object**: the receipt records neither the filter nor the
table length.

Witness coverage is uneven by machine: joinable 190 = bm-b 181 + bm-c 9 + bm-a 0; no witness 122 =
bm-a 53 + bm-c 35 + bm-b 34. bm-a's rounds are not in this repository's `round <N>:` series, so its
receipts cannot be joined here at all.

## Four reusable lessons

1. **Ask of a self-certifying field whether it can ever disagree.** `legs_total = len(rows)` agrees
   with its neighbour in 202 of 204 receipts; a rate of exactly 1.0 is constructive redundancy, not
   a measurement, and no sample size fixes it.
2. **The join key is the file name, not the field.** 17 receipts write `round` as `r183` / `r848
   bm-a`; joining on the field silently drops them. 8 more carry no round in the name at all
   (`_rrunbmb`, `_rverifybmb`, `_r--allbmc`, …) and can only be published as no-witness.
3. **The write encoding is part of the join.** `_r244bmc_s6_chain.json` starts with a UTF-8 BOM and
   `json.load` raises `Unexpected UTF-8 BOM`; readers must open `utf-8-sig` or that receipt is
   permanently unreadable.
4. **A census inside a live directory must exclude its own writer.** The S6 leg's first run used a
   fake round 9999 and immediately added `_r9999bmb_s6_chain.json`, moving the face (LEGS 311→312
   because the leg itself had joined the table). The fix is to delete the self-made artefact (after
   a treasure-guard prescan, zero hits) and rebuild, and to gate per-file re-derivation with new
   files reported as drift — otherwise the gate turns red because it ran (E180/E207 family).

## Artefacts

* `scripts/e561_receipt_table_join.py` — build / check / verify / selftest (19/19)
* `results/state_tilt/RECEIPTTABLE-2026-11-08.json` + `receipttable_latest.json`
* `smoke_test.py` leg `# E561` + standalone `scripts/run_e561_smoke_leg.py` (green 1/1, `--doctor`
  refused 4 problems)
* `Tools/s6_chain_bmb.py` leg `receipt_table_join` (rc=0, 1.1 s)
* `knowledge/METHODOLOGY_ASSETS.md` card E561
* `results/runnable_pool.json` — E561 done

## Verdict

190 of 320 receipts can be read against their own round's table; 31 cover it, **159 are short, and
135 of those are single-leg runs that are indistinguishable in the file from a chain that died**.
The receipt's own total is the count of rows that ran, so it certifies nothing about the table: the
only witness that survives is the runner blob in git, and it does not reach bm-a at all.

## Fixpoint and the gate's own input (both caught in-window)

* Adding the leg to `Tools/s6_chain_bmb.py` moved bm-b's LEGS table 311 → 312, which turned the
  **E560** leg red (`summary does not re-derive from source`). Rebuilt E560's face (474 legs,
  selftest 21/21) rather than relaxing its gate — the same fixpoint step r1585 took for E559.
* The first gate compared **every** receipt on disk, including `_r1587bmb_s6_chain.json` that this
  round's own chain leg had just rewritten (1 row → 2 rows on the second run). The gate now
  compares only receipts **committed in HEAD** (111 of 320) and publishes the other 209 as
  uncommitted observation: a file the study's own runner rewrites cannot be part of the study's
  gate.