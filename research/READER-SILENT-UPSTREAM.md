# A reader must not crash on a state its writer may publish (r2065, bm-c)

Two of the 34 red smoke legs the r2061 triage called EXCEPTION are not two more
defects: they are the same silent upstream the r2062..r2064 root-cause pass traced
(the cut receipt answers `UNREADABLE` with `permitted_k = null`, so it carries no
`gap_k`), showing up in two readers that were written as if the upstream always
answers.

| leg | shape | what it did on 2026-11-25 | what it does after this patch |
|---|---|---|---|
| `etf_book_permission_persistence --check` | a **checker** reading a key a
published state may omit | `KeyError: 'gap_k'` | prints `UPSTREAM_SILENT`, exits 3 |
| `etf_book_cash_roll_today --selftest` | a **selftest** reading the LIVE faces | `KeyError: 'cash_cny'` | fixture-only, offline |

## Why exit 3 and not 1

The value here is *which* state the leg is in. The upstream is allowed to be silent,
so this is not a verdict about the reader: red would be a flag nobody can act on
(r1789) and would teach the reader to loosen the rule (r1135). Green would read as
clean while nothing was compared (r1861). The harness therefore closes the leg
**UNVERIFIED** on rc 3 with the child's own sentence -- the same third state as
r1861 (face moved mid-run) and r1943 (child killed).

The sentence deliberately does **not** say STALE: the chain only pays a rebuild on
that word (r1850), and re-running this face would produce the same silence.

## Why the selftest had to lose its disk legs

`--selftest` used to call `read_inputs()` and then index `live["cash_cny"]`. On a day
the book cannot answer, `build()` correctly returns `NO_INSTRUCTION` -- and the
selftest crashed on the missing key. That means **the market decided whether this
file's own test passes**, and the leg went red on a day nothing was wrong with the
code. Re-deriving the live pair from disk is `--check`'s job and it already does it,
field by field. The selftest now carries both shapes on fixtures: the readable face
(cash == nav - ordered, to the cent) and the silent one (NO_INSTRUCTION, no cash to
index).

## The patch (waiting for a quiet window)

`patches/r2065-reader-silent-upstream.patch` -- four hunks over three files; `git apply --check` accepts
it against this tree. It is **not applied here**: this round ran inside a contention
window (another host was writing shared faces), so only new files were landed.

## Live readings this was priced against

* cut receipt verdict: `UNREADABLE`, `permitted_k = None`
* published `slack_k` on the persistence face: `0.000000`
* published cash-roll verdict: `ROLL_GC007_TODAY`

## Proof

* PASS patch generation is deterministic (two builds byte-identical)
* PASS the patch is four hunks over three files (one per defect + one per guard) -- files=3 hunks=4
* PASS git apply --check accepts the patch against the current tree
* PASS patched scripts/etf_book_permission_persistence.py parses
* PASS patched scripts/etf_book_cash_roll_today.py parses
* PASS patched smoke_test.py parses
* PASS harness: the UNVERIFIED branch precedes the loop's own check() call
* PASS patched --check on a silent receipt exits 3 and says UPSTREAM_SILENT -- rc=3 said='UPSTREAM_SILENT: the cut receipt says UNREADABLE and publishes no gap_k, so this face cannot re-check the trim it was pr'
* PASS that sentence does not contain STALE (the chain must not pay a rebuild for it) -- UPSTREAM_SILENT: the cut receipt says UNREADABLE and publishes no gap_k, so this face cannot re-check the trim it was pr
* PASS with a readable receipt the same code reaches the rebuild (guard is not a mute)
* PASS unpatched --check still raises KeyError 'gap_k' on the same fixture (control) -- KeyError 'gap_k'
* PASS patched --selftest passes with the disk readers poisoned (it is offline now) -- selftest 20/20
* PASS unpatched --selftest still dies with KeyError 'cash_cny' on a silent face (control) -- KeyError 'cash_cny'

Controls are in the same run: the **unpatched** sources are executed on the same
fixtures and must still raise the two KeyErrors -- a green leg above therefore
cannot mean 'the fixture changed'.
