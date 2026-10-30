# r1372 / E282 — the sweep r1371 named, and the false alarm it found on the way

**Trigger.** r1371 left an explicit debt in its own report: *"any gate that decides 'did my source
move' by mtime is measuring the filesystem, not the data, and this round named the family without
auditing it."* This round is that audit.

**What was found.** Five more places in the same family, all still asking the clock:

| gate | module | old test |
|---|---|---|
| `floor_check` | `etf_book_phase_atlas_arms.py` | any source mtime > face mtime + 1 s |
| `width_check` | same | baseline grid mtime > face mtime + 1 s |
| `live_width_check` | same | any of `{BASE, CAPACITY_FACE, TICKET_LATEST}` newer |
| `readback_check` | same | any of `{FLOOR_OUT, READBACK_FACE, BASE}` newer |
| `check` | `etf_book_rule_null.py` | arms face newer than the null face |

Each fed the same two-state verdict (`stale` = chain pays the declared refresh; `inconsistent` =
stay red, because re-deriving would launder an edit) from a quantity every `git checkout`, clone,
rebase and restore rewrites.

**Fix.** One shared rule, two clock-free signals (`_source_moved`):

1. **Copied leaves.** A leaf that `build()` copies verbatim from a source face (`baseline.audit*`,
   `arms.<n>.audit.*`) differing means the source now says something else → the source was
   regenerated. Copy *agreement* is positive evidence, which the old path never had.
2. **Priced bar.** A source whose own `evidence_cutoff` is later than this face's is a source that
   advanced. Dates cannot be handed out by a checkout.

Both signals are content; neither can be produced by moving bytes around in a working tree.

**The sweep's own finding — a false alarm, live.** The first version of `_cutoff_of` also read
`as_of` / `priced_bar` / `decision_bar`, so the live-width gate compared its own cutoff (the atlas
grid's bar, 2026-10-29) against `results/etf_book_order/latest.json`, whose `as_of` is 2026-10-30 —
**the date the ticket was written**, not the bar its numbers come from. The gate then reported
`live-width face is stale: a source face is priced later than this one
(TICKET-2026-10-30.json(2026-10-30>2026-10-29))` on a face that re-derives to the same bytes. It
was caught by a pre-existing selftest leg (`an edited live-width verdict stays inconsistent`), not
by inspection — and it is the r1292 unit-mix-up in a new place: two dates that look alike and mean
different things.

Narrowed: `_cutoff_of` reads `evidence_cutoff` only (top level, or inside `baseline`), and
`TICKET_LATEST` was dropped from the live-width source list entirely — the ticket's real
contribution (its `k_now`/`beta_target`) is covered by the drift comparison, which is already
content-level. `latest.json` is a pointer, and a pointer's write date is not a bar.

**Selftest.** 102 → 109 legs in the arms module (10 stay green in the null-rule module). The three
new behavioural legs move exactly the class they claim to distinguish, in both directions:

- `L32` an unedited floor still passes with a clock 2 h in the **past**;
- `L33` a hand edit under that old clock stays **inconsistent** — the mtime rule called it stale;
- `L34` a face priced on `2000-01-04` goes **stale** even when it is the newest file on disk —
  the mtime rule called it fresh.

Plus four unit legs pin the reader: `as_of` alone is not a priced bar; `evidence_cutoff` is read
top-level and inside `baseline`; no sources is not staleness; the ticket pointer never stales the
live-width face on its own.

**Gate state after the round** (all five, on the 2026-10-29 bar):

```
--check              rc=0  arms face matches its own sources (10 arm verdicts reprinted)
--floor-check        rc=0  UNREACHABLE_BY_CONSTRUCTION (k required 7.792)
--width-check        rc=0  DIRECTION_NOT_A_SIZE (width required 61.72)
--live-widths-check  rc=0  COIN_FLIP_INSIDE_ENGINE_DISAGREEMENT (paired gap 0.09pp)
--readback-check     rc=0  HOLDS (predicted +0.228, observed +0.260)
rule_null --check    rc=0  REJECT_IS_THE_DEFAULT (seed 20261030, 20000 trials)
```

**Open.** (a) `check()` now routes its stale/inconsistent split through the same `_source_moved`
helper as the four siblings, so there is one implementation of the rule in this module — but the
null-rule module still reads `evidence_cutoff` itself (it imports `_cutoff_of`, not
`_source_moved`), which is the next place the two copies could drift apart. (b) The remaining
mtime users in `scripts/` (`update_fundamental`, `cross_start_robustness`, `exclusion_marginal_scan`,
`automation_line_audit`, `daily_report`) all compare a file against *now* rather than one face
against another — a freshness age, which a checkout cannot forge — so they are not this family, but
they were not audited pair-by-pair either.