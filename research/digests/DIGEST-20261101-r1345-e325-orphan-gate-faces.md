# DIGEST 2026-11-01 (r1345 bm-b) -- E325: the gate rows whose face has no writer

**Question (pool card E325, seeded by r1344).** E321..E324 measured a NAME problem -- is there a
producer for a gate leaf, and does it publish a key of that name. All of them took the FACE for
granted. Over the same 196 rows / 51 faces: how many gate rows read a value from a face that no
source in the tree can produce? A face-level defect is not a naming defect: renaming a key or
resolving a decoy on an unreproducible face buys nothing.

**Answer.** It depends on the naming rule, so it is published as a ladder
(`results/state_tilt/ORPHANGATEFACE-2026-10-31.json`):

| rung | who counts as a writer | writer-less rows | writer-less faces |
|---|---|---|---|
| R1 published lookup | E321/E312 `producer_candidates` as published (stem fallback, self-excluding auditors) | 25 (12.76 pct) | 4 |
| R2 every auditor kept | a single-line writer (`open(name,"w")`, a dump onto an open) | 164 (83.67 pct) | 24 |
| R3 + format templates | a face named by `f"F_{c}.json"` / `"X-%s.json"` | 11 (5.61 pct) | 8 |
| R4 + composed paths | a name on an assignment / `os.path.join` / `ROOT / "results" / name` line, module can write | 0 | 0 |

So no face in the population survives as an orphan, and the named-but-unwritten residue is also
0 rows. The published lookup is disclosed as an INSTRUMENT, not a rung: its stem fallback accepts
a bare mention, so it under-reports writer-less rows by 139, while a rule that demands a writer
orphans 20 more faces than it does. The ladder is monotone only from the second rung.

**What the four R1 orphans were.** (1) `results/state_tilt/GATEOPERANDS-2026-10-31.json`, 22 of the
25 rows: written by `scripts/e312_gate_operand_identity.py`, which the published lookup drops from
its own corpus -- the census could never see its instrument's face. (2) two format-template
families: `p1e_nulls_{cls}.json` (`p1e_ic_batch.py`) and `REGIME5-DIAG-{cutoff}.json`
(`regime5_labeler.py`). (3) one composed path: `OUT_JSON = ROOT / "results" /
"etf_book_voltarget_lag.json"`. E322 had already named the same shapes at key level (self-exclusion,
compact dates, composed names) -- the defect class lives in the search, not the repository.

**Pits.** (a) A family credit must not go to a module that SPELLS the face: if the literal
basename is present and unwritten, the module is a reader, and crediting it through any family
prefix it also formats turns readers into producers (R2 moved 157 -> 162 rows and 20 -> 22 faces
before the spelling guard went in). (b) Rows are not faces: one face carried 22 of the 25
first-rung rows, so the row-weighted reading is eight times the face-weighted one in the same tree.
(c) "Not an orphan" is not "reproduced": the mention-only residue is published separately, or
"0 orphans" reads as "every face is reproducible".

**Numbers for the next reader.** 196 rows / 51 faces / 2,280 corpus sources; 30 of 51 faces change
class between R1 and R4; the largest R1 orphan carries 22 rows and the largest R2 orphan 64; the
card r1345 seeded is E326 (which consumers tie a number to an unrepublished template parameter).