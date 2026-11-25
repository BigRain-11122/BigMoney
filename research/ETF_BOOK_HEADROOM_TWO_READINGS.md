# One receipt, two headroom numbers

generated 2026-11-25T02:29:38+08:00 | evidence cutoff 2026-11-24 | ticket `TICKET-2026-11-24.json`

## What is on the face

The size in force is **k = 0.435003** on **1,000,000** CNY.

| reading | path | k | headroom to add, pp | CNY |
|---|---|---|---|---|
| printed floor (strictest) | universe | 0.435003 | 0.5 | 5,000 |
| loosest supporter | window | 0.747086 | 31.7083 | 317,083 |

Each row adds the face's own `size_tol` (0.50pp) before subtracting the size in force, because that tolerance is how `keep_allowed` itself is written.

## Which one the verdict used

`TWO_READINGS_DIFFER` -- the printed permitting floor sits 0.50pp above the size in force, while the verdict only stops saying KEEP once k passes 0.752503 (31.75pp higher) -- quoting the floor understates how much more this book may buy, quoting the loosest path overstates how much independent evidence stands behind it

`keep_allowed = any(path >= k_now - tol)` is the branch that decides; `permitted_k = min(paths)` is the number the face prints as *the permitting floor*. Both are true statements about the same table, and they answer different questions.

## Flip point, measured by calling `decide()`

- first k with the size no longer kept: **0.752503** (step 0.0005)
- that is **31.75 pp** above the size in force
- below it the face says KEEP regardless of how much the book adds

## Honest limits

* the r2063 patch (identity leg anchored on `base_bar`) is **not applied on disk** -- the patched cell exists only in memory here (base bar 2026-11-20, k 0.458463422);
* no repricing, no schedule rebuild, no panel read;
* this face does not say which reading *should* govern a size increase -- that is the sizing rule's call, and it is printed, not decided, here;
* k can only fall for reasons outside this face (a new volatility reading), and a falling k never costs the size its permission, so the strict number is a ceiling on ADDING, not a trigger for selling.

