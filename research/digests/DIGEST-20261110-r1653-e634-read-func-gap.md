# E634 — the function body is wider than the line, and it still names no key

**Round** r1653 · bm-b · 2026-11-10 · card E634 (`cpu-only`) ·
face `results/state_tilt/READFUNCGAP.json` · script `scripts/e634_read_func_gap.py` (selftest 31/31)

## What E633 left open

E633 priced only the accesses that *start on* the counted read line and published that as its second
limit: `"k" in d`, `del d["k"]`, `d.setdefault("k", …)` or `d.pop("k")` on a neighbouring line belong
to that line's count and are invisible to a line-scoped census. So the counted function could read
its key in a form that produces no read node and nothing published would show it.

## What this round measured

Walk the **whole body of the function that holds the dead line**, in document order, for every one of
the 13 counted read lines; classify every access of that receiver with E633's classifier; split each
unnamed entry read by its side of the dead line (a read *before* cannot explain the dead line, a read
*after* competes with the counted read for the same duplicate denominator; `at_the_dead_line` is
published separately so the two questions never merge).

| reading | count |
|---|---|
| counted read lines | 13 |
| lines resolving to a function body | 13 |
| accesses of those receivers in the bodies | **230** |
| … recognised reads of the key | 44 |
| … different named key | 62 |
| … read below the receiver | 52 |
| … container-level | 42 |
| … computed key at the receiver's own level | 30 |
| **unnamed entry reads of the key** | **0** (0 before / 0 at / 0 after) |

Verdict:
`no_counted_read_line_names_this_key_in_an_unrecognised_form_anywhere_in_the_function_that_holds_it_so_E633_line_scoped_census_and_E632_node_count_both_stand`

## Why the zero is a measurement

A zero count is only worth publishing if the instrument says what it looked at (E444/E207 family:
a classifier that has nothing to hit prints the same zero as a classifier that missed). Here the
walker saw **230** accesses of the very same receivers inside those bodies — 44 of them recognised
reads of the key — so the receiver is present, the scope was entered, and the unnamed class is
genuinely empty rather than unreachable. The face publishes the per-row census
(`accesses_in_the_function_body`, `accesses_by_form`) and the selftest leg
“the walker saw the receivers in the bodies (non-empty census)” pins it.

## The residual this round hands forward

30 **computed-key** reads sit at the receiver's own level (8 before the dead line, 1 on it, 21 after).
They read *some* key and cannot be decided as this one — E633's rule, unchanged, so they are published
as a residual with sides rather than folded into the same-key count. 21 of them after the dead line is
the only place left where a read of the counted key could still hide: **E635** (whether those computed
keys resolve to the counted key by constant propagation inside the function).

## Instrument notes

* Fixture dead lines must be **interior markers**. The first draft marked each function's dead line at
  its `def` line, which makes every body read "after" it by construction — the before/after split then
  cannot fail, and four legs reported a split that the fixture never tested. The fix is a marker line
  inside the body, scoped to the function's own line range (a file-wide `next()` picks the first
  function's identical line).
* `del d["k"]` classifies as `kind == "subscript"` with `ctx == "del"`, not as `kind == "membership"`;
  the assertion that said otherwise was the assertion that was wrong.
* The whole-body walk reuses `e633.access_sites` line by line; sorting the sites by
  `(lineno, col_offset, kind)` is what makes "document order" mean the source order the reader sees.