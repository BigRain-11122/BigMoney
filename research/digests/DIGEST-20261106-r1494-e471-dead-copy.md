# DIGEST — E471: a never-opened pointer target is a second copy or content nobody reads (r1494 bm-b)

**Face.** `results/state_tilt/DEADCOPY-2026-11-06.json` (+ `deadcopy_latest.json`)
**Producer.** `scripts/e471_dead_copy.py` (run rc0 / `check` problems=[] / `verify` identical / selftest 16/16)
**Population source.** `results/state_tilt/targetread_latest.json` (E470 rows with residue
`never_opened_by_any_site_in_the_corpus`, re-read, not re-derived)

## Question

E470 (r1493) published 17 of 24 pointer targets that need a base other than the repo root and are
*never opened by any site in the corpus*. A file no program opens is either cheap or expensive, and
the two look identical on disk: cheap = the same subject (or the same bytes) is also published on a
face that IS read, so the dead edge costs nothing; expensive = the content exists in exactly one
file nothing will ever open.

## Reading

| channel | targets |
|---|---|
| never-opened targets in the population | 17 |
| has a peer (copy or same subject) | 16 |
| **peer is opened by a study that writes neither face (redundant)** | **5** |
| peer opened only by a smoke leg or a one-off round script | 11 |
| peers exist but nothing opens any of them | 0 |
| no second copy where the subject is published (orphan) | 1 |

Peer edges 55 (readable 5), peers measured 21 (5 opened by a study). Channels: 16 by same subject,
3 by exact content. Verdict:
`some_never_opened_targets_are_second_copies_of_a_face_that_is_read_and_others_are_not`.

The redundancy is one pattern repeated: `BANDTRANSFER`, `BLOBREAD`, `FAMILYGLOBREAD`, `OPTINSWITCH`
and `SIBLINGENTRY` are dated vintages whose `_latest` sibling a study does open, so the dead pointer
costs nothing. The other eleven (`WIDTHLADDER-20261029..20261105`, `PHANTOMWHY`, `PINQUEUE`,
`READCAP`, `READRESOLVE`, `FACEPOPPIN`) are vintages that only legs ever open — a published surface
no production reader has ever consumed. `results/e43_tilt_4member/LADDERDROPWHERE-20261027.json` is
the single genuine orphan: no copy, no sibling, no opener.

## What would have made the answer look better

1. **A tree-wide copy census.** 19,096 JSON files (1.8 GB) live in this tree. Running the census
   everywhere would have been a different study at a different cost, so it is scoped to the
   directories that publish these subjects — and the scope is printed in the face rather than left
   implicit. `no_peer` means "no copy where this subject is published", not "no copy anywhere".
2. **A selftest leg that cannot fail.** The first draft asserted a CRLF-folded copy "equals the
   other file or True". That is a rubber stamp: it passes whether or not the folding works. It was
   replaced by three legs with teeth (CRLF twin hashes equal, reordered/whitespace-reformatted file
   hashes equal, a changed value does not).
3. **Assuming a peer is read because it is the `_latest` sibling.** The 11 only-by-leg targets show
   exactly why not: their peers exist under the same subject and are still never opened by a study.
   Peer opened-status goes back through E470's own opener scan.

## Consequence for the corpus

Retiring a dead pointer is not the same decision as retiring a published vintage. Five of these
edges are free to delete. Eleven are a decision about *publishing* — a family of dated vintages no
reader has ever opened, which is a supply question (E4xx supply-floor family), not a pointer
question. One file is content nobody reads at all, and if the study behind it matters the face needs
to be re-published somewhere a reader opens.