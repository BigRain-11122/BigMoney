# DIGEST — r1378 (bm-c, 2026-10-31): the worklist was not work (record only: its original label card E294 was taken by bm-a's atlas card on origin)

**Question.** r1377 closed with one instruction: "the remaining 12 rows of
`results/live_value_cache_audit.json` — start with `etf_book_ceo_page.selftest`". Before working them,
the cheapest question is the one the previous two rounds never asked of the *rows*: does any of these
functions read a value that came off disk at all?

**Answer: two of sixteen, and neither is the defect the list implied.** Reading the 13 "serve with no
digest" rows by hand (three of them line by line) sorts them into three piles that the name-keyed scan
could not tell apart:

| what it really is | rows | example |
|---|---|---|
| an in-memory dict filled and read inside one call | 3 | `member_reinforce_p1.cmd_run` builds `replays = {}` in the loop at 486-507 and reads it back at 509-560 — nothing survives the process |
| an existence/shape check, never a served value | 6 | `p1e_turnover_derive.main` and `t73_mktcap_sidecar.main` load `meta.json` only to `assert len(syms) == meta_cache["shape"]["N"]` and never let it reach a return; `fund_avail_notice.status` counts `os.path.exists` |
| a self-test proving a cache hits | 5 | `etf_book_ceo_page.selftest` is the L51-L53 legs **of** the digest rule (`stress_cache_digest`) — the test of the fix, not a face |

What is left: `alloc_backtest.run_cell_faces` (r1377's fix — digest passed as an argument, still owed
its perturbing leg) and `member_reinforce_p1.finalize`. The second reads its own append ledger's
running total (`old.get("trials_ledger").get("prev_total")` at 352) and hands it to
`SG.append_ledger(..., prev_total=...)`; there is no skip path — every run recomputes all replays — so
it is an accumulator, not a replay. The tool's taint cannot tell those two apart, and it now says so
in `limits` rather than pretending otherwise.

## What changed

**`Tools/live_value_cache_audit.py` — the value question, asked of the value.** A cross-tick cache has
to survive the process, so the scan now asks two things per row instead of one: did the value it reads
come off disk (`_loaded_names`: a literal-keyed read off a `json.load`/`np.load`/`pd.read_*` binding),
and does it reach a `return` (`_read_reaches_output`, one-hop-per-pass taint over the persisted value
only). Each non-face row is filed under a class — `no_stored_value_read`, `persisted_read_not_served`,
`fixture_readback` — kept in the table and out of the headline.

Headline, before → after:

    13 serve on a key with no digest
     2 read a value OFF DISK and serve it with no digest
        (1 of them hands a digest to the reader as an argument)
    14 of 16: 3 memos/existence checks, 6 validation-only reads, 5 fixture read-backs

**The blind spot, measured instead of guessed.** The census is keyed on names and therefore cannot see
a cache whose payload is called `c` under a path called `cache` — which is exactly
`etf_book_beta_menu.tier_stress`, a real persisted cache keyed on `inputs_sha256`. Widening the entrance
to "any function that loads, compares a literal key and returns" admits **151** functions on this host
(66 report readers and 12 digested caches among them), so the gate stays where r1376 put it and the
blind spot is published as a **size** (`blind_spot_persisted_serving: 151`, `blind_spot_digested: 12`)
with a leg that names `tier_stress` and checks its digest key. A count, not a worklist.

Legs 19 → 30. New: `L20/L21` a dict called `cache` filled inside one call is a memo and stays out of
the headline; `L22` a shape read off `meta.json` that never reaches a `return` is a gate; `L23` a
self-test that proves a cache hits is a fixture; `L24` the disk-loaded-and-returned fixture is still
counted as a face (`_FIX_BAD`) — the refinement must not blind the census it was built for; `L25/L26`
the blind spot finds `tier_stress` and reads its digest key; `L27` the blind-spot list is published
with its size, never trimmed to the sample; `L28` the new headline cannot exceed the legacy one;
`L29` the headline recomputes from the rows (never hand-written); `L30` every non-face row carries a
class.

## What this round does not claim

`reads_a_stored_value` is a **named-binding** read: a value loaded by a helper and returned, or handed
in as an argument, is invisible to it (stated in the artifact's `limits`). The census is still
name-keyed, so its 16 rows are "faces someone called cache-ish", not all caches on the host. And the
one remaining face, `member_reinforce_p1.finalize`, is adjudicated here on reading, not by a leg.

## Verify

- `python Tools/live_value_cache_audit.py selftest` → **30/30 legs PASS** (11 new).
- `python Tools/live_value_cache_audit.py run` → deterministic; artifact republished to
  `results/live_value_cache_audit.json` with `evidence_class` / `reads_a_stored_value` /
  `served_to_caller` / `blind_spot` per row, and `summary.faces_serving_a_stored_value` listing the
  two faces by name.
- Hand-read: `member_reinforce_p1.cmd_run` (memo), `fund_avail_notice.status` (existence),
  `p1e_turnover_derive.main` / `t73_mktcap_sidecar.main` (shape gate) — the three piles the classes
  claim to separate.
- smoke: full suite re-run after the edit (see the round report row).

**Next.** r1379: the blind spot is 151 wide and 12 digested — the un-digested ones are a reading list
only if they serve an operator number; ask the same value question of the 139, not of the 16.