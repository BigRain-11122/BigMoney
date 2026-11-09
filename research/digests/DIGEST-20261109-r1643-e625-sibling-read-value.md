# DIGEST r1643 bm-b — E625: does the sibling read see the VALUE the dead line saw?

**Face**: `results/state_tilt/SIBLINGREADVALUE-2026-11-09.json` (+ `siblingreadvalue_latest.json`)
**Script**: `scripts/e625_sibling_read_value.py` — selftest 23/23, run/check/verify `problems=[]`
**Lane**: cpu-only, static, no network, no runner, no fixture write

## Question

E624 closed under object identity and wrote its own hole into `limits`: *a mutation of the object is
not a rebinding of the name*, so `m["k"]` read twice with `m["k"] = ...` in between still counts as
the same object. Key (E623) → object (E624) → **value** (this study) are the three tests; this card
prices the third.

## Method

For every sibling read E624 accepted as reading the same object, the AST interval between the dead
line and that read is scanned for a write to that key on that object:

| class | what it means |
|---|---|
| `the_key_is_stored_between_the_two_lines` | `m["k"] = …`, `del m["k"]`, `m["k"] += …`, `m.update({"k": …})`, `m.setdefault("k", …)`, `m.pop("k")` — the read sees a different value |
| `the_object_is_written_without_the_key_being_named` | `m.update(payload)`, `m[k2] = …` with a computed key, other mutating methods — undecided |
| `the_object_is_handed_to_a_call_between_the_two_lines` | `f(m)` — anything could be written — undecided |
| `the_key_is_not_stored_between_the_two_lines` | nothing touches it — same value |

Population is imported from E624 (`object_facts`, `text_of`, `receiver_of`, `SAME`), not
re-implemented; the cross-check reproduces the published E624 face line for line and corrected class
for class (34/34 rows, 4/4 superseded same-object, zero differences).

## Readings

- 19 same-object sibling reads, over **11** of the 34 live dead face-key lines.
- Value test: **18 untouched**, **0 stored (named)**, **0 written unnamed**, **1 handed to a call**.
- E624's 4 same-object duplicate rows: **3 survive** the value test
  (`cn_mkneutral_p1.py:507` `P["slip_exec"]`, `e590_cash_silence.py:364` `r["bar"]`,
  `ew6_portfolio.py:393` `ports["x1"]`), **0 are stored over**, **1 stays undecided**
  (`cn_core_ddctl_p1.py:367` `P["days"]` — `P` is handed to a call twice between 367 and 395).
- Verdict: `3_of_4_same_object_duplicate_reads_sees_the_value_the_dead_line_saw`.

## What the 0 means

No write in this population names the key it is being compared against. So E623/E624's surviving
duplicates are not "lucky": these dicts are genuinely untouched between the two reads. The only
residual uncertainty is the one class where the object leaves the function — and it is published as
undecided rather than guessed either way.

## How to apply

1. Price a "duplicate read" on three levels — key, object, **value** — before calling it a re-read.
2. `m.update(payload)`, `m[k2] = …`, `f(m)`: never report these as "not written". Publish undecided.
3. An undecided row is a product: it names the next question exactly (E626 — does that callee write
   the key on its parameter?).
4. Carry the evidence for every write/handover on the row (line + form), so the denominator can be
   checked by eye.

## Limits published on the face

No alias analysis; a nested def in the interval is flagged but not descended into; `f(m)` leaves the
value undecided; "same value" rests on the interval's write marks, not on a proof about concurrent
writers; self-exclusion keeps E619/E622/E623/E624's sets plus this study's own.