# E552 — created item presence in the published artefact (r1591 bm-b, 2026-11-08)

**Question.** E547 published eight created items and measured who *reads* them (nobody outside the producer). It never asked whether the artefact the module writes carries the item at all.

**Answer.** 1 of 8 created items never reach a stored artefact (6 by identity, 1 copied-and-published, 0 only echoed to stdout, 1 absent).

| row | presence | evidence |
|---|---|---|
| scripts/alphagen_beam_w18.py :: cmd_probe | present_through_the_same_object | out is handed to the file channel '_dump' at line 568 |
| scripts/alphagen_beam_w19.py :: cmd_probe | present_through_the_same_object | out is handed to the file channel '_dump' at line 676 |
| scripts/alphagen_beam_w20.py :: cmd_probe | present_through_the_same_object | out is handed to the file channel '_dump' at line 743 |
| scripts/t19_adjust_view.py :: _gate_results | present_as_a_copy_in_a_published_container | rows['_GB_nan_skipped'] is transcribed into gates at line 297 and gates is published at line 298 |
| scripts/t33_attack_wave.py :: cmd_selftest | absent_from_every_published_container | 5 publish channel(s) exist but none names probe or a container carrying it |
| scripts/t73_s2_factor_history.py :: run | present_through_the_same_object | art is handed to the file channel 'write' at line 385 |
| scripts/t73_s2_retail_herding.py :: run | present_through_the_same_object | art is handed to the file channel 'write' at line 238 |
| scripts/t73_s2_reversal_momentum.py :: run | present_through_the_same_object | art is handed to the file channel 'write' at line 205 |

**Why the split matters.** unread and bsent need different repairs: an unread key can gain a reader at zero cost; an absent key cannot be read by anyone until its producer starts publishing it. The one copy row is present but one line away from silent loss.

**Method pit (self-caught this round).** The first draft classed six rows as identity but three of them were evidenced by a print line. Those three actually reach disk through a module-level _flush(art) helper, so the right answer rested on the wrong line. Fixed by binding helper parameters to caller arguments for one hop, and by making stdout its own class (carried_only_to_stdout) rather than a publish channel -- a print can also project a subset ({k: art[k] for k in (...)}) that drops the key again.

**Bounds.** One helper hop; only the store lines the parent named; the cross-module persisted-face channel is not re-run (E547 already settled it as unread).

**Body.** scripts/e552_created_item_presence.py (selftest 13 arms) -> results/state_tilt/CREATEDITEMPRESENCE-2026-11-08.json ; S6 leg created_item_presence rc=0 0.13s.
