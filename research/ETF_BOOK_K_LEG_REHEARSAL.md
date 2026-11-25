# The one-line anchor patch, priced through the two faces it unblocks (r2064)

`with the r2063 one-line anchor patch (baseline cell reads the step at base_bar 2026-11-20, k=0.458463 instead of 2026-10-23, k=0.460253): the permission turns from UNREADABLE into KEEP_SUPPORTED_BY_INDEPENDENT_PATH with a permitting floor of k=0.435003, and the cut/order gap turns from UNREADABLE into ORDER_WITHIN_PERMISSION with CNY 0 to cut on a CNY 434,724 book. A step next to the right one (2026-09-17 k=0.458808) stays unreadable, so the fix is the bar and not the tolerance.`  
`ticket TICKET-2026-11-24.json` · `evidence_cutoff 2026-11-24`


## What is being compared

| run | baseline cell reads | permission | cut/order gap | cut CNY |
|---|---|---|---|---|
| today (on disk) | 2026-10-23 · k=0.460253 | UNREADABLE | UNREADABLE | - |
| the patch | 2026-11-20 · k=0.458463 | KEEP_SUPPORTED_BY_INDEPENDENT_PATH | ORDER_WITHIN_PERMISSION | 0 |
| one step earlier than the right one | 2026-09-17 · k=0.458808 | UNREADABLE | UNREADABLE | - |

## Checks

* `receipts_agree_the_ticket_k_is_the_priced_step` = **OK**
* `on_disk_run_reproduces_todays_two_verdicts` = **OK**
* `patched_run_flips_both_faces` = **OK**
* `neighbour_step_stays_unreadable` = **OK**
* `patch_touches_only_the_baseline_cell` = **OK**

## Why the bar and not the tolerance

with the r2063 one-line anchor patch (baseline cell reads the step at base_bar 2026-11-20, k=0.458463 instead of 2026-10-23, k=0.460253): the permission turns from UNREADABLE into KEEP_SUPPORTED_BY_INDEPENDENT_PATH with a permitting floor of k=0.435003, and the cut/order gap turns from UNREADABLE into ORDER_WITHIN_PERMISSION with CNY 0 to cut on a CNY 434,724 book. A step next to the right one (2026-09-17 k=0.458808) stays unreadable, so the fix is the bar and not the tolerance.

## What this does not claim

* it does not land the patch: the leg, the permission face and the gap face are shared science faces held by another host this round
* it does not re-price the book or rebuild the beta schedule (no panel, no engine)
* the patched beta is derived (target/k), not read from a receipt, and neither face exercised here consumes beta
* the readers/enforcers scan is not re-run: an empty reader list can only make the gap face more pessimistic, never more favourable
* the permission's permitting floor lands exactly on k_now, so the pass has zero margin -- one tick of deterioration in that reading turns it into a real cut

