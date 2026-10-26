# E103 — the gap limit is not identified by the panel: 20 limits, 2 objects, 0 moved cells

- date: 2026-10-27 (bm-b r1168)
- face: `results/e44_midmonth/GAPLIMIT-20261026.json`
- code: `scripts/e39_panel_census.py` mode `gaplimit` (+ `--max-limit`, default 20), selftest 286 -> 299
- question (pool E103): E102 showed gap1/gap2/gap5 publish one identical reading on every
  era-book cell. Walk `gap_limit` 1..20, publish how many symbols/prints/bars change per
  limit, name the first limit that moves a published cell — and if none exists, say so,
  because then three published columns cannot be cited as corroboration.

## The ladder is a two-step frontier, not twenty measurements

| limit | symbols rewritten | prints repaired | bars rewritten | edit-face signature |
|---|---|---|---|---|
| 1 | 74 | 75 | 36,184 | `1af14f0fb4bc` |
| 2 | 74 | 75 | 36,184 | `1af14f0fb4bc` |
| **3** | 74 | **76** | **37,101** | `ded3f7541386` |
| 4..20 | 74 | 76 | 37,101 | `ded3f7541386` |

- **Twenty limits, two distinct repair objects.** Limits 1 and 2 rewrite exactly the same
  36,184 bars; every limit from 3 to 20 rewrites exactly the same 37,101 bars. Equality is
  established on the edit face (every changed `symbol|date` cell), so limits inside one
  group are the same object by construction — their cells cannot disagree.
- **The whole ladder moves exactly once, at limit 3**, and the binding print is named:
  **`sz159901` 2010-11-22**, an integer-like print with a 3-session gap. That single print
  rewrites 917 bars downstream and is the only thing separating the lower group from the
  upper one.

## Why it saturates immediately: the panel's own gap spectrum

| gap_sessions | gapped prints | of which integer-like |
|---|---|---|
| 1 | 28 | 10 |
| 2 | 4 | 0 |
| 3 | 1 | 1 |

`max_gap_sessions = 3`. There is **no** print on the panel with a gap of four or more
sessions, so no limit above 3 can ever bind: the flatness of the ladder is a property of
the data, not an artefact of the walk. A gap-2 print exists but none of the four is
integer-like, which is why limit 2 adds nothing even though it widens the window.

## The cells: no limit in 1..20 moves a published cell

| era | book | gap1 delta | gap3 delta | moves? |
|---|---|---|---|---|
| 2017_2020 | me | -745.9 | -745.9 | no |
| 2017_2020 | mid | 0.0 | 0.0 | no |
| 2021_2023 | me | -1098.3 | -1098.3 | no |
| 2021_2023 | mid | -1117.2 | -1117.2 | no |
| 2024_now | me | 4.9 | 4.9 | no |
| 2024_now | mid | -241.0 | -241.0 | no |

`pre2017` is unmeasurable (no decision ends in the era) and stays `null` — it is not a zero.

Verdict: **`not_identified`**. One extra name and 917 extra repaired bars, and not one
published cell moves by even 0.05bp. So:

- `gap1` and `gap2` are **the same object** (E102 already read their deltas as identical;
  the edit face now says why).
- `gap5` is the *upper* object (limit >= 3), i.e. it differs from `gap1` only by
  `sz159901`'s 2010 print — a name whose prints never reach a published cell.
- Therefore **the three published gap columns are one reading under two objects, and none
  of them corroborates another.** A future "N gap arms agree" sentence is a statement about
  the panel's gap spectrum, not about robustness.

## Control

Every published delta in the measured cells reproduces at this burn's own latest end
(`control_reproduces_published: true`, zero mismatches > 0.05bp): -745.9 / 0.0 / -1098.3 /
-1117.2 / 4.9 / -241.0 all match the E99/E102 published numbers. That is the proof this
leg reads the same cell definition, not a nearby one.

## How to cite this from now on

- Never write "gap1/gap2/gap5 agree, so the repair is limit-insensitive". Write **"the
  panel's gap spectrum ends at 3 sessions and exactly one integer-like print sits there;
  every published gap column is the same reading on either side of it"**.
- Any screen whose parameter is not identified by the edit face carries one reading, not
  N. Publish the edit face (`symbols / prints / bars`) beside the deltas.
- A parameter ladder is a **frontier**, not a recommendation: this leg names no chosen
  limit and `gap1` remains the published control.

## Honest limits

- Descriptive census only: no gate, no verdict on the strategy, no prereg, no trial count,
  no ledger booking.
- Identical edit faces are a proof of object identity for *this* panel; a refreshed panel
  can grow a new gap bucket and turn the flat ladder into a real one — the spectrum is
  published with the ladder for exactly that reason.
- The churn level is a name-level mean over swapped pairs, not a portfolio return: the
  deltas move a reading, not money.
- `E100` (naming the transitions that carry the two large moves) and `E97` (routing the
  charged modes to screened twins) remain open in the pool.