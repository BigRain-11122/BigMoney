# DIGEST 2026-11-07 r1504 bm-b — E476 the payload side of the 47 unowned unread families

**Question.** E473 found 47 of E472's 97 unread vintage families have no write-call evidence in any
source — the paths are composed at runtime, so no python literal names them. Those faces were still
written by something. Does a published payload itself carry a writer channel, and how often?

**Population.** 97 families (E472 `vintageread_latest.json`) minus the families any E473 writer row
names (`producerspill_latest.json`) = **47 unattributed families**, 240 member files seen, 12201
python sources indexed, 372 methodology cards indexed. Face:
`results/state_tilt/PAYLOADWRITER-2026-11-07.json`.

**Channels (frozen before the run).**
1. `payload_names_a_script_on_disk` — a top-level string under a writer-ish key (study/generator/tool/
   script/producer/module/engine/card/...) resolves to a `.py` on disk (exact path, basename or stem).
2. `payload_carries_a_resolvable_card` — a string is a card id `E\d{3,4}` the asset file carries.
3. `payload_carries_a_card_id_the_asset_file_does_not_carry` — same shape, no such card (a channel,
   but a broken one).
4. `payload_carries_only_a_timestamp` — generated/ts/cutoff/evidence_cutoff, no identity.
5. `nothing_in_the_payload_names_a_writer` — parsed payload, no channel.
6. `no_payload_file_was_parsed_so_the_channel_is_unmeasured` — every member was csv/parquet or over
   the read cap.

**Reading.**

| channel | families |
|---|---|
| names a script on disk | 0 |
| resolvable card id | 14 |
| dead card id | 0 |
| timestamp only | 23 |
| parsed payload names nothing | 1 |
| unmeasured (csv-only members) | 9 |

Verdict `some_unowned_families_can_be_attributed_from_their_payload`: **14 of the 47 measured 38**
name a writer, and **all 14 do it through a card id carried in a `study` field** — E224, E231, E232,
E233, E234, E237, E239, E242, E243, E244, E245, E248, E249, E250. Not one family names the script
that wrote it: the only payload channel that works points at the study card, i.e. the readable
knowledge face, never the code that emitted the bytes.

**Why the timestamp class is published separately.** Counting the 23 timestamp-only families as
attribution would make 37 of 47 "have an owner" while a reader still cannot reach a script. The
verdict is computed over writer channels only; the timestamp class says WHEN, not WHO.

**The defect caught in-window.** The first burn classed the 9 csv-only families as
`nothing_in_the_payload_names_a_writer` — a negative result produced without opening a single payload.
They are now `unmeasured`, the verdict is computed over measured families only, and `check` refuses a
"nothing" row with `payload_files_parsed == 0`. Same family as E444/E462: *no candidate is not a
failed candidate*.

**Wiring.** `scripts/e476_payload_writer.py` (run / check problems=0 / verify problems=0 / selftest
29/29); S6 leg `payload_writer` after `producer_spill`; smoke leg "E476 an unowned family's payload
channel is measured, not assumed absent" (holds the tallies re-derive, the unmeasured count re-derives
from the rows, the verdict is decided over measured families, and two doctored copies are refused);
methodology card **E476**; pool E476 closed with result_ref, E469/E466 stale-ready rows corrected.

**How to apply.** When retiring an ownerless face family, ask which level its payload answers:
card level = citable but not fixable at the source; timestamp level = not even citable; unmeasured =
add a reader for the member format before drawing a conclusion.