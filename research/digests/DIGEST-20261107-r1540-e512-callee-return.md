# DIGEST — r1540 bm-b · E512: what the callee names when the site's only binding reads a call

**Round**: r1540 (bm-b) · **Face**: `results/state_tilt/CALLEERETURN-2026-11-07.json` (+ `calleereturn_latest.json`)
**Instrument**: `scripts/e512_callee_return.py` (selftest 28/28) · **Card**: E512 · **S6 leg**: `callee_return`

## The question

E511 anatomised the four pair sites E510 could not collapse and left three of them classed as
"one in-scope binding, the value enters through the right-hand side": `asof = tk["priced_bar"] or
"unknown"` where `tk = card_config_ticket(nav=nav)`. That verdict stops one hop short — the
right-hand side is a *call*, so there is a second author. This round reads that author.

## Population (two published faces, nothing re-read from E507's raw pairs)

| arm | sites | source |
|---|---|---|
| `the_sites_own_binding_is_a_call_result` | 5 | E510's published pairs whose single in-scope binding has shape `call_result` |
| `the_sites_value_reads_an_operand_that_is_a_call_result` | 3 | E511's published sites with resolution `operand_read_what_the_right_hand_side_actually_returns` |

## Readings

- 8 sites / 1 distinct callee / 9 return paths examined.
- **3 sites** resolve to `card_config_ticket` (same module, `scripts/etf_book_order.py:688`). Its
  three return paths are `literal_None` ×2 and `dict_literal` ×1 — it *does* branch — and a
  **terminating guard** sits between the call (line 1015) and each site: `if not tk: return 2` at
  1016. So the empty arm cannot arrive, and the surviving dict's `priced_bar` traces
  `sh.get("as_of_bar")` → `sh = doc.get("sheet")` → `doc = _read_card(card_dir)` = **a value read
  from a file**: a data day, not a run clock and not a constant. The `or "unknown"` at the site
  rescues a missing *field*, not a missing return.
- **5 sites** call a builtin coercion (`str(...)`) — no contract, but it fixes the argument's
  shape: 1 traces to an element of a loaded series, 4 to `BT.apply_overlay(...)` = a value built
  by another module (published as such, not followed further — that is E514).
- **0 sites** read whatever arrives. Verdict:
  `every_site_is_answered_by_reading_its_callee_or_its_argument`.

E510/E511's "operand read" bucket **dissolves**: every member is answered by one more hop.

## Three lessons measured, not assumed

1. A bucket named "needs an operand read" has a next question — *read whose* value. Not reading
   the callee treats "undecided" as "unreadable".
2. "The callee branches" ≠ "the site can receive two values". A guard only filters the empty arm
   when it **terminates**; a non-terminating guard shadows nothing (the fixture pair gamma/ beta
   is exactly this contrast).
3. Name tracing must skip the write it has already consumed. `slip = slip[slip.index >= start]`
   pins the walk to itself until the depth cap, and the honest-looking `something_else` was the
   instrument's own scar: fixing it moved 4 sites to `built_by_a_call_into_another_module` with
   **zero verdict changes**.

## Verification

`run` rc0 · `check` problems=[] · `verify` rebuild problems=[] · selftest 28/28 (5 fixtures + 7
doctored arms refused) · S6 leg `callee_return` rc0 0.05s · smoke leg `# E512` 1/1 green standalone
and 1/1 red under `--doctor` with the face byte-restored (sha `78b96c2500d8`).

**Not done and not claimed**: the full smoke suite, the `update_*` collectors, the market/paper
chain, `monitor.build_status`, `daily_scorecard`.