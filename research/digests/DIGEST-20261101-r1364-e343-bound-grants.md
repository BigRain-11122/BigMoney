# DIGEST 2026-11-01 r1364 — E343: where a bound grant actually decides

**Question (from E340).** E340 counted 22 self-reads and called 18 of them *bound*: the producer
loads a permission-shaped key off its own face into a name, and what that name then does is invisible
on the access line. A bound grant is where self-authorization would hide. Follow each bound name to
its first downstream use; name the rows where the bound value is the only authority; state what a
check on one of them would have to look like.

**Answer.**

| reading | n |
|---|---|
| E340 `self_bound` rows | 18 (over 22 faces) |
| …that are stores into the loaded dict, not reads | **10** |
| real reads | **14** (5 producers) |
| first use: `stored` / `passed_to_call` / `inline_use` | 3 / 1 / 10 |
| compared or truth-tested at first use | **0** |
| sole authority (no compare, no test, downstream) | **1** |
| sole authority rows with a frozen literal to check against | 0 |

**Verdict:** `some_bound_grants_are_the_only_authority_for_the_value_they_feed_and_nothing_in_the_producer_could_assert_it_today`

## What changed in the finding's shape

1. **E340's `bound` class is inflated by writes.** `st["expected_cutoff"] = expected` is a store into
   the dict that was loaded, not a read of the key. Nine of the ten write-only rows are the four
   `*_update_status` writers (`update_futures`, `update_etf_daily`, `update_options`, `update_repo`)
   plus one scratch tool. Any census keyed on `name["key"]` must check `ast.Subscript.ctx`; a
   line-shaped classifier cannot see the difference and E340's headline rested on it.
2. **Almost nothing downstream of a real read is a check.** 10 of the 14 reads are `inline_use` (the
   key is read and consumed on one line), 3 are stored and 1 is passed to a call. The only genuinely
   gated one — `permit` in `Tools/oss_import_gate.py` — reaches its comparison through an alias two
   hops from the access line (`p = permit.strip()` then `p in FORBIDDEN`), which is why an
   access-line census cannot see it and why alias following was needed at all.
3. **The single sole-authority row is a report, not a decision.**
   `bl = kin["baselines"]` (`scripts/cross_start_robustness.py:909`) is never compared or tested; all
   three uses land inside an f-string summary. So the honest reading of "where would
   self-authorization hide" on today's tree is: nowhere load-bearing, and the place it would have
   hidden was mostly not a read at all.
4. **Mechanism, computed rather than argued.** The producer already carries a selftest, so the
   mechanism is "assert `bl == recomputed baselines` inside that selftest"; none of the population
   carries a frozen literal, so producers without a selftest fall through to a chain leg
   (`assertable_from=none_available`).

## Defects caught in this study's own drafts (all before publish)

- **Store read as a load** (inherited from E340) — 10 of 18 rows. Fixed by requiring
  `isinstance(node.ctx, ast.Load)`; published as `accesses_excluded_as_writes` and
  `write_only_entries` rather than silently dropped.
- **Duplicate rows: one binding published twice** — grouping walked each function subtree *and* the
  module subtree. Fixed by grouping nodes under their nearest enclosing function.
- **Container read as a store** — `all(isinstance(v, str) for v in (src, permit))` reached a Call
  through a Tuple and was called `stored`. Containers are now transparent; only a container landing
  in an assignment is a store. `AugAssign` (`lines += [...]`) was the same defect one node away.
- **The container bound instead of the value** — `bench["ytd_baselines"] = ytd.get("baselines")`
  published a grant against `bench`. Rows with no bound name are published as such and can never be
  sole authority.
- **Alias blind spot** — the only row that is actually gated (`permit`) looked ungated until
  `p = permit.strip()` was followed.

## Reproduce

```
python scripts/e343_bound_grant_decisions.py selftest   # 21/21
python scripts/e343_bound_grant_decisions.py run        # ~1.7s
python scripts/e343_bound_grant_decisions.py verify      # 0 problems
python Tools/s6_chain_bmb.py 1364 --only bound_grant_decisions
```

Face: `results/state_tilt/BOUNDGRANT-2026-11-01.json` (+ `boundgrant_latest.json`).
Source: `results/state_tilt/ALLOWANCE-2026-11-01.json` (E340).

## Follow-ups this opens (not claimed here)

- Should E340's face be re-published with the write exclusion, or should the correction live only in
  this sibling face? (Today: sibling face, E340 untouched — an evidence face is not silently rewritten.)
- `permit` in `Tools/oss_import_gate.py` is the only load-bearing grant in the population; it is gated
  through an alias, so a "gate exists" count keyed on the access line reads 0 for it.