# DIGEST 2026-11-09 r1457 (bm-c) — the floor has to be remembered between bars

**Round**: r1457 (round_no 1456 at open), product round.
**Product**: `scripts/etf_book_floor_ledger.py` → append-only floor ledger + one per-round
verdict; consumed on the order sheet itself (`etf_book_order.py::floor_ledger_md`).

## The gap this closes

| round | what it published | what it left unsaid |
|---|---|---|
| r1450 | a permission: k ≤ 0.393073 | who remembers it tomorrow |
| r1455 | the sheet prints the trim (445 lots → k 0.392964) | the sheet is regenerated per run |
| r1456 | one up-step (6.76pp) can erase a 6.72pp cut | nothing stores the cut between bars |

The permission receipt is a **current-moment object**: it is regenerated from the
current ticket and read only at the instant a sheet is printed. If the ticket is
repriced, if a round does not run the order, or if a new permit is issued (possibly
higher), the floor disappears without any error.

## What the ledger does

- **Append-only**, keyed on `(decision_date, ticket_file, permitted_k)`: re-issuing the
  same floor adds nothing; a different `permitted_k` is a **new row**, never a rewrite.
  The series therefore keeps the history of how a permission climbed.
- **Four verdicts, because four different actions follow**:

| verdict | condition | action |
|---|---|---|
| `HOLDING` | schedule's last decision bar ≤ floor | a sheet built now inherits obedience |
| `REAPPLY_REQUIRED` | sheet obeys, **path does not** | apply the same trim on the next decision bar |
| `NOT_ENFORCED` | path and sheet both over | nobody is executing the floor |
| `REISSUE_REQUIRED` | permit priced from a superseded ticket | re-issue on the current ticket |

- **Missing input reads as UNKNOWN**, never as compliance; the sentence under UNKNOWN
  may not name an action.

## Live reading (2026-11-09 02:5x)

```
floor            0.393073   (issued 2026-11-11)
schedule last    k=0.460253 (decision bar 2026-10-23)
order             k_order 0.460253 -> k_sheet 0.392964 (445 lots / CNY 67,289)
verdict          REAPPLY_REQUIRED
```

The order sheet now prints that verdict in its permission section, so the desk does not
have to remember a different file.

## Two sizes are printed and never substituted (E293 family)

- `k_order` — what the ticket **asks for**.
- `k_sheet` — what the sheet **executes** (post-trim integer-lot k when a trim exists).

Judging obedience on `k_order` marks every sheet over; judging it on "a trim exists"
launders a mis-computed trim into compliance. A fixture leg builds a trim that lands
**above** the floor and pins it as not-obeying.

## Wiring

- `scripts/etf_book_order.py`: `FLOOR_FACE`, `_floor_face()`, `floor_ledger_md()`;
  printed inside `permission_md()`; selftest 101/101 (leg50a-c are new).
- `Tools/s6_chain_bmc.py`: leg `floor_ledger` (check, 0.2s) after `permission_persistence`,
  before the register (r1329 ordering law).
- `smoke_test.py`: two legs (selftest, check).
- Card: `knowledge/METHODOLOGY_ASSETS.md` **E463**.

## Self-catches during the build

1. First `assess()` judged obedience on the permission's `k_now` (the **ordered** size),
   so the live face read `NOT_ENFORCED` while the sheet was in fact trimmed to 0.392964.
   Caught by the leg that expects `REAPPLY_REQUIRED`; fixed by reading the published gap
   receipt's post-cut k instead.
2. `latest_ticket()` globbed only `results/` top level and returned `None` (tickets live
   in `results/etf_book_order/` and `results/etf_book_order_fresh/`), which would have made
   `ticket_superseded` pass **by absence** — the cheapest kind of false green. Now walks
   the subtree and skips `_quarantine` and `-card` siblings.
3. The gap receipt publishes `k_after_integer_lots` while `trim_legs()` returns `k_after`.
   The reader accepts both by name and names the gap when neither is present.
4. Repaired three eaten carriage returns left in card **E462** by a previous PowerShell
   inline write (`run()` had become `un()`, `→ results/` had split across lines) — the same
   class of accident the config smoke leg guards.

## Not verified

- The full smoke suite in this round is still running at close (87 lines, one slow leg
  `etf_book_forward --selftest` takes ~113s); the three new/changed legs were run
  individually and are green.
- The ledger records what was issued; it does **not** claim the desk re-applies it. The
  forward proof is the next decision-bar sheet showing `HOLDING` or a fresh trim.