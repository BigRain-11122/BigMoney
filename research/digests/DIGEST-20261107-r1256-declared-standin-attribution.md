# DIGEST 2026-11-07 r1256 (bm-a): a declared stand-in that neither reader could see

## What the board said

`results/data_lane_freshness.json` at 11:26 read:

    astock_daily  tail=2026-11-06  verdict=unverifiable
    why: "the envelope does not name the machine whose data it describes"
    lane_host=bm-b  host_alive=false (silent 190.7h)  data_face_machine=bm-a

At that same minute `update_astock_daily.py refresh` (pid 68824, started 09:24) was writing
`data/astock_daily/per/*.csv` on **this** machine, and the envelope carried
`takeover: {owner: bm-b, by: bm-a, reason: "owner bm-b silent 189.9h >= 120min"}`.

So the panel was current, the takeover was legal and disclosed, and the board still told a
reader "cannot certify": a healthy lane labelled as a gap.

## Root cause: the declaration existed in a key nobody reads

Two independent misses on the same row:

1. **Writer shape.** `update_astock_daily` published only the top-level `takeover{}` block.
   Both authority readers (`data_lane_freshness`, `lane_ownership_declaration`) read
   `authority.took_over_by`. This is the r1253 defect (`update_repo`) recurring on a
   second lane — the cure there was `_authority_block()` and it was not transplanted.
2. **Reader attribution.** Even with `took_over_by` present, the authority layer first needs
   `reported_by`, taken from top-level `machine|lane_machine|reporter|writer`. This envelope
   names no machine at the top level, so it landed in `authority=unattributed` and the
   declaration was never consulted.

## Cure (both sides, each in its own name)

* `scripts/update_astock_daily.py`: new `_authority_block(takeover)` publishing
  `lane_owner / writer_machine / data_face_machine / declared_takeover / took_over_by /
  took_over_at / reason`, written on every gate pass (`st["authority"] = ...` right after the
  takeover set/pop, so the no-op branch carries it too). Selftest leg added.
* `scripts/data_lane_freshness.py`: when the top-level reporter keys are absent, attribute
  the envelope to `authority.writer_machine` — the canonical block already answers "who
  wrote this", so this is not a legacy-shape accommodation. New selftest leg L19 (18/18 -> 19/19).
* `smoke_test.py`: new leg `fleet: a lane that declares its stand-in is not uncertified`,
  recomputed from the published rows — any row carrying `declared_takeover_by` must be
  `auditable`.

## Live reading after the cure

    verdict=host_down counts={retired:1, unverifiable:5, in_sync:4} worst=moneyflow
    astock_daily  tail=2026-11-06  verdict=in_sync  authority=declared_takeover  reported_by=bm-a

`unverifiable 6 -> 5`, `in_sync 3 -> 4`. The five remaining uncertified lanes are genuinely
bm-b's (`moneyflow/marks/zt_pool/heat/etf_panel`) and stay uncertified — "cannot certify"
is still not read as green.

## Transferable rule

Card E395: for any takeover/degradation/stand-down state ask three questions — which key
carries the declaration, which readers read which key, and what prerequisite field those
readers need before the declaration can be placed. A declaration that fails any of the three
is a line in a log, not a fact in the board. Assert it on published rows, not on writer intent.