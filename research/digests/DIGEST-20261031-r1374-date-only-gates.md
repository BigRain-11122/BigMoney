# DIGEST — r1374 (bm-c, 2026-10-31): the date-only form of the staleness family

**Question.** r1372 swept every gate that asked the *clock* whether its source had moved and
r1373 closed the last one by hashing its source. Both left one shape named but untested: gates
that ask the **date** the same question. A date cannot see a source that was regenerated on the
bar it already carries, nor a control arm that moved under a face while the calendar stood still.
So: sweep the etf_book family for staleness decisions that rest on a date, and say for each one
whether it is actually blind or merely adjacent to the defect.

## What was blind, and what was done about it

**1. `etf_book_buffer_adoption` — the face grades itself against a control arm it recorded.**
The gate compared the face's `evidence_cutoff` with the card's: "priced on 10-29 while the card is
on 10-30" → stale. That is the whole test. Re-derive the card **on the same bar** — a config edit,
a repaired print, a changed cell — and every number the face graded against moves while the two
dates stay equal. The face stays green while quoting a control that no longer exists.

The second half of the question was already answerable with no engine run: the face *records* what
it graded against (`control.published`, `control.published_turnover`) and the card publishes the
cell it came from. The fix is one shared rule, `etf_book_production.control_moved()`, that compares
the recorded numbers with the card on disk.

**2. `etf_book_hysteresis` — identical shape, identical rule.** Imported, not re-written (the r1372
lesson: a copy of a rule is the next defect). Both gates now take the card itself, not just its date.

**3. `etf_book_beta_menu` — a *cache* keyed on the bar.** This one is stronger evidence than the
gates, because its own docstring asserted the invariant it did not enforce: "the answer only moves
when the panel or the ticket does", while the cache file name was the priced bar alone. A flip
repair anywhere in the panel rewrites the worst N-day window without touching today's date, and the
tier `k` can move without the panel moving at all. Replay then hands the reader numbers for a panel
that no longer exists. `stress_inputs_digest()` keys the replay on the bar, the capital, the
windows, the ticket scale and a hash of the panel values; a cache file written before the digest
existed is a **miss**, not a hit.

## The three states, stated once

`control_moved()` returns three answers, and the third is the one that would otherwise be silent:

| return | meaning | gate |
|---|---|---|
| `False` | the numbers are the ones the face was graded against | green |
| `True` | the control moved under the face on the bar they share | **stale** (rc=2, the chain pays the refresh) |
| `None` | card or cell or recorded control absent — nothing to compare | **not clean**: named `[NOTE] control re-read unavailable`, and the gate falls back to the cutoff rule and says so |

A missing input must not read as "no change"; that is the same law E254 applies to lanes, applied
here to a gate's own inputs.

## Swept and *not* changed (with the reason, so the next round does not re-open them)

- `etf_book_production.drawdown_band_*` — the caveat says "band priced on bar X, not this card's
  bar Y". It **re-reads the artifact on every build**, so the band numbers on the card are current
  by construction; only the bar label can be behind. Not the same defect.
- `etf_book_voltarget_lag` — a cutoff mismatch prints a disclosure instead of going red, and its
  docstring says why (the face is re-derived from the live panel every round). Disclosure-only is
  correct only while that stays true; if it ever stops being re-derived, this is the site to reopen.
- `etf_book_order` / `etf_book_ceo_page` — the remaining date comparisons there decide *which*
  ticket or which page row belongs to a bar, not "did my source move".

## Verification

- `etf_book_hysteresis --selftest` 35/35, three new legs (unchanged control green; a same-bar card
  re-derivation red with the reason; an unreadable cell `None`, never clean).
- `etf_book_buffer_adoption --selftest` 37/37, four new legs, including a same-bar turnover move.
- `etf_book_beta_menu --selftest` 27/27 (30 → 32 `chk(` sites), including "a same-bar panel repair
  is recomputed, never replayed" and "the cache file records what it was computed from".
- Both live gates still `OK` on the current bar (10-30) after the change — the new rule finds
  nothing to report today, which is what a correct rule should do on an unchanged world.

**Scope disclosure:** `etf_book_beta_menu` is a bm-a-owned face — running the leg here prints
"machine=bm-c is not the writer (bm-a) -> honest no-op, nothing written". The cache fix is therefore
proven by its selftest on this host and takes effect on bm-a's next run of that leg.

## One false positive worth naming (orphan probe vs a between-legs chain)

`Tools/orphan_face_probe.py` reported `orphans=1` at open: pid 105520, the S6 chain the r1373 window
left running, with parent dead, no hidden-host ancestor and `cpu_delta_20s=0.0`. Its three faces all
said "orphan". It was not: a chain runner **between legs** has no child process and near-zero CPU,
and it printed `chain: 104/104 rc0` at 00:23:30 before exiting on its own. The discriminating
evidence was its own log's growing mtime, not the process table. Passing `--kill` on that reading
would have killed a chain that was 90% done — the same class of error as judging a staleness gate by
a date, applied to a *process*: the cheap proxy (CPU) does not contain the question.

Pos: `scripts/etf_book_production.py` (`control_moved`) / `scripts/etf_book_buffer_adoption.py`
(`check_payload` + 4 legs) / `scripts/etf_book_hysteresis.py` (`check_payload` + 3 legs) /
`scripts/etf_book_beta_menu.py` (`stress_inputs_digest` + 2 legs).