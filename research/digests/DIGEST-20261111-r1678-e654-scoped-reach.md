# DIGEST 2026-11-11 r1678 bm-b -- E654: does a scoped counted-key site subscript the object a read line reads

**Card** E654 (pool head, lane cpu-only, watermark red: pool-batch-runnable-idle-low-cpu).
**Face** `results/state_tilt/SCOPEDREACH.json` (+ `scopedreach_latest.json`), 16 site rows and 13 read-line rows.
**Script** `scripts/e654_scoped_reach.py` (selftest 19/19; build/check/verify problems=[]).
**Wiring** smoke leg E654, S6 leg `scoped_counted_key_reach` (rc=0, 0.47s).

## What was asked

E650 published 383 module-body sites that sit inside a comprehension or a lambda and 16 that address
one of the six counted row keys (`rows` 11 / `x1` 4 / `bar` 1). E650 could only say *where the base
name is bound*: all 16 are `outer_scope_only`, i.e. the name is bound outside the construct. That is
not the interesting part. The question is whether the outer name carries the same object the counted
read line reads — because a matching key on a *different* dict cannot move a counted value, and
E207/E208's lesson is exactly that a name which reads like a measurement is not a measurement.

## What was measured

| reading | value |
|---|---|
| site rows published (one per site x key x base) | 16 |
| source sites in E650's face | 16 |
| counted read lines (E633/E638) | 13 |
| reach class `off_population` | 16 |
| reach class `same_module_other_receiver` | 0 |
| reach class `same_container` | 0 |
| sites sharing a module with a counted read line | 0 |
| sites whose container a counted read line reads | 0 |
| rows a key-name-only test would call a collision | 16 |
| key-name-only false positives | **16 (100%)** |
| container shape on the site side | call_result 5 / empty_then_populated 11 |
| container shape on the read-line side | empty_then_populated 8 / call_result 2 / literal_mapping 2 / runtime_input 1 |
| per-key split (matches E650's own histogram) | bar 1 / rows 11 / x1 4 |

## The reading

The 16 sites live in eight files: seven round scripts (`_r1052bmb_sscombo_report.py`,
`_r1592_etfbk_diag.py`, four `results/_r45*bmc_fundnulls_watch.py`, `results/_r453bmc_bookkeep.py`,
`results/_r486bmc_w3_judge_prefinalize.py`) and one report script
(`scripts/stagestyle_combo_p1_report.py`). The 13 counted read lines live in
`scripts/cn_core_ddctl_p1.py`, `scripts/cn_mkneutral_p1.py`, `scripts/e382_key_projection_delta.py`,
`scripts/e504_name_compose.py`, `scripts/e590_cash_silence.py` and `scripts/ew6_portfolio.py`. The
two module sets are disjoint, so no site can subscript the dict a read line reads.

What the sites actually do is read their own diagnostic JSON: a comprehension over family names
pulling `fam_out[f]["nulls.jsonl"]["rows"]`, a `max(..., key=lambda k: res[k]["x1"]["sharpe"])` over
a round's own result file, `len([b for b in fresh if pub and b > pub[-1]["bar"]])` over a published
bar list. Their containers are `empty_then_populated` (11) — an empty dict the module then fills in
a loop from disk — or a `call_result` (5). None of them reads anything a counted read line reads.

The counterfactual is the number worth publishing: a test that matches on the key name alone would
have called all 16 a collision. That is a 100% false-positive rate on this population, and it is the
same shape E207 measured at 34,058 cells and E208 repaired by pruning the word list by value shape.

## Pitfalls (all hit or priced this round)

1. **A key spelling is not an object.** "Same key" is a string fact; "same container" needs module,
   receiver name and key to line up. Publishing the first as if it were the second is the E207/E208
   family read.
2. **A negative conclusion has to be priced.** "0 of 16 reach the read container" alone reads as if
   the ruler measured nothing; publishing "a key-name-only test would have said 16" beside it turns
   the zero into a quantity.
3. **Module identity is the cheapest necessary condition.** Two files cannot hold the same dict, so
   cross-module sites are `off_population` without evaluating any container — the same move E646's
   write-side arm makes.
4. **A shape must not guess runtime.** An empty dict the module fills inside a loop is published as
   `empty_then_populated` with no value set (the loop keys come off a disk face); calling that a
   `runtime_input` would be a guess dressed as a reading.

## Next

E660 (ready, cpu-only): whether the 58 bare-name loop bounds E659 could not read are assembled in
the module body above the loop or are true runtime inputs.
