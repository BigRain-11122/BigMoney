# DIGEST r1401 / E382 -- what moves if the face key projection is fixed

**Study** `E382_key_projection_delta` · card `KEYDELTA-2026-11-03` · 2026-11-03 · bm-b (CPU only,
zero network, GPU parked per C-20261014-01, cloud untouched).

## The question

E381 showed the shared keying is wrong in two named ways: `e347.values_in:133` hands a `join` call's
operands back as SEPARATE values, `e350._face_bindings:139` keys each operand alone (so a
three-component path lands under a bare basename), and both helpers accept only paths ending `.json`
(so a `.jsonl` read is never keyed). The card seeded by that round asks the question a bugfix owes:
**before anyone patches e350, price the republish.**

## The method

Two arms over ONE corpus pass (2,422 sources; this study excluded):

| arm | keying |
|---|---|
| `published_keying` | `e350._face_bindings` unchanged |
| `repaired_keying` | each load's own operands folded into one path; `.jsonl` accepted; per-value rule kept as fallback |

Every headline is published three ways — what the face on disk says, what the published arm
re-derives from today's corpus, and what the repaired arm re-derives from the same corpus — so the
repair's bill (`repaired - published_arm`) is never mixed with corpus drift
(`published_arm - face_on_disk`).

## Readings

| headline | face on disk | published arm | repaired arm | repair Δ | drift |
|---|---|---|---|---|---|
| E350 fields | 2,289 | 2,318 | 2,373 | **+55** | +29 |
| E350 reads | 5,398 | 5,491 | 5,620 | **+129** | +93 |
| E350 fields with no writer | 1,698 | 1,717 | 1,761 | **+44** | +19 |
| E350 guard fields | 230 | 230 | 253 | **+23** | 0 |
| E350 unwritten guard fields | 131 | 131 | **148** | **+17** | 0 |
| E350 face keys | 846 | 857 | 881 | **+24** | +11 |
| E350 fields with unresolved face | 803 | 810 | **758** | **−52** | +7 |
| E353 pairs | 131 | 131 | 148 | **+17** | 0 |
| E377 blind-spot targets | 36 | 36 | 36 | 0 | 0 |
| E377 targets the census keys | 0 | 0 | **2** | **+2** | 0 |
| joined-only faces (E381) | 12 | 12 | **0** | **−12** | 0 |

**10 of 11 headlines move and E350's verdict string flips** (`...131 of them have no writer...` ->
`...148...`). E377's 36 blind-spot faces re-key exactly the 2 E381 named; the 12 joined-only faces go
to zero, so that defect is fully closed by this repair and no other face list shrinks.

The single largest delta is a **decrease** and it is the defect's own signature: 52 fewer fields sit
under a name no path can resolve (810 -> 758), i.e. the repair turns about 6% of the population from
"keyed by a name" into "keyed by its path".

## What the study refused to claim

- It does not re-run E353's classification (its verdict needs each pair's face read on disk); only
  the pair count is repriced, and `not_repriced` says so.
- It does not re-run E377's dump census (its verdict inputs are unchanged by keying); only its face
  list is republished.
- It does not call the repair monotone. The first draft did, and its own selftest killed the draft: a
  folded load drops its basename key, so a key count can fall; every delta's sign is published.
- It does not touch the published faces: E350/E353/E377/E381 are read, never rewritten. Patching them
  is a separate decision, and this face is the bill for that decision.

## Wiring

- `scripts/e382_key_projection_delta.py` — `run` / `verify problems=[]` / `selftest 16/16`
- smoke leg E382 in `smoke_test.py`, exec'd verbatim out of the suite
  (`scripts/run_e382_smoke_leg.py`, 1/1 PASS)
- S6 chain leg `key_projection_delta` in `Tools/s6_chain_bmb.py`
- face `results/state_tilt/KEYDELTA-2026-11-03.json` + `keydelta_latest.json`
- card `knowledge/METHODOLOGY_ASSETS.md` E382

## Pit (carried into the state face)

The first build was launched before the smoke leg was installed in `smoke_test.py` — a corpus member
changed mid-scan. The run was killed and restarted on the final tree rather than published from a
moving corpus; the numbers above are that second snapshot (identical corpus size 2,422 on both runs,
so the restart cost wall time and no reading).