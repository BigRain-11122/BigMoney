# One schedule, two steps: the k leg that reads a different bar

source: `results/etf_book_k_identity_bar.json` @ 2026-11-24T18:36:52+08:00 | ticket `TICKET-2026-11-24.json`

**IDENTITY_INTACT_LEG_READS_A_DIFFERENT_STEP**

the ticket's k=0.458463 is 2026-11-20 on the schedule and is the last step at or before 2026-11-24; the leg reads 2026-10-23 (k=0.460253) -- one step earlier, 0.1790pp apart. The identity holds and the disagreeing leg is reading a different bar, not catching a break.

## the two rows, from the schedule itself

| bar | k | what it is |
|---|---|---|
| 2026-10-23 | 0.460253 | what the leg reads (`book_decided_at` = 2026-11-11) |
| 2026-11-20 | 0.458463 | what the ticket published as `k_rule`, last step at or before 2026-11-24 |

A ticket of 1,000,000 CNY: the ticket's row sits **0.1790pp / 1790.00 CNY** below the row the leg reads (signed -0.1790pp).

schedule tail (last three steps):

| bar | k | beta |
|---|---|---|
| 2026-09-17 | 0.458808 | 0.435912 |
| 2026-10-23 | 0.460253 | 0.434543 |
| 2026-11-20 | 0.458463 | 0.436240 |

The step between those two rows is not unusual: across 78 steps the median adjacent move is **0.2599pp**, the largest is **6.7573pp**, and **46** of the 77 steps are at least as large as this 0.179pp arc. A leg keyed to the wrong bar is red whenever the two bars straddle any step at all.

## the identity that actually holds

| leg | reads |
|---|---|
| ticket_k_rule_is_a_schedule_point | True |
| that_point_is_unique_on_the_schedule | True |
| that_point_is_the_last_step_at_or_before_the_priced_bar | True |
| the_leg_bar_has_a_step_of_its_own | True |
| both_values_come_from_one_schedule | True |
| the_ticket_row_and_the_leg_row_are_different_steps | True |
| the_two_steps_are_adjacent | True |

The strong form -- *the ticket's k is a distinct point on the schedule, and it is the last one at or before the bar the ticket prices* -- is what makes a size auditable. "Equals the step at whatever bar the reader picked" is not the same statement, and it is the one the red leg asks.

## what is downstream of this leg

| face | verdict | cutoff | why |
|---|---|---|---|
| `etf_book_size_rulers_decision.json` | IDENTITY_BROKEN | 2026-11-24 | a ruler disagrees with a published number (ticket_k_reproduced); the table is not evidence until that is resolved |
| `etf_book_rebalance_permission.json` | UNREADABLE | 2026-11-24 | a reading could not be classified (baseline_published); an unclassified reading is not a vote for the size in force |
| `etf_book_cut_order_gap.json` | UNREADABLE | - | the ticket or the permission is missing k_now/permitted_k/nav |
| `etf_book_k_gap.json` | FLOOR_CUT_THIS_SHEET | 2026-11-20 | - |

`etf_book_rebalance_permission` publishes UNREADABLE because the baseline cell it classifies carries this leg's verdict; `etf_book_cut_order_gap` then publishes UNREADABLE because a null `permitted_k` is not a permission. Both are consequences, not second opinions.

## the patch, in full

```diff
# scripts/etf_book_size_rulers_decision.py, inside run()
-    cells["baseline_published"], k_dec_bar, k_at_dec = baseline_cell(arms["published"], tk)
+    priced_bar = tk.get("base_bar") or tk.get("as_of") or tk.get("book_decided_at")
+    cells["baseline_published"], k_dec_bar, k_at_dec = baseline_cell(
+        arms["published"], dict(tk, book_decided_at=priced_bar))
+    # the leg must then read the step the ticket was priced on, not the roster decision

# why this is the right bar and not a tolerance: k moves only on a schedule step, so the
# step at or before base_bar IS the size in force on base_bar (step_in_force's own rule).
# Widening the leg's tolerance to a whole step (0.1pp) would also turn it green -- and
# would hide a genuine break between two adjacent rows. Fix the bar, keep the tolerance at
# the 6dp storage precision the ticket and the faces share.
```

Widening the leg's tolerance to a whole step (0.1pp) would also turn it green today. It would also hide a genuine break between two adjacent rows. Fix the bar; keep the tolerance at the 6dp storage precision the ticket and the faces share.

## what this does not claim

- it does not fix the leg: the shared science faces are held by another host this round
- it does not re-run the smoke legs: those must speak after the patch lands
- it says nothing about the 5 red legs outside the book family (r2062 counted them)
- adjacency is shown for this ticket only; the drift profile prices how common that arc is across all 78 steps, not how many tickets ever fell into it
