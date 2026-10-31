# E312 — a gate is compared with *something*, and that something is rarely the leg's quantity (r1331 bm-b)

**Face:** `results/state_tilt/GATEOPERANDS-2026-10-31.json` (+ `gateoperands_latest.json`)
**Producer:** `scripts/e312_gate_operand_identity.py` (run / verify / selftest 21/21)
**Upstream:** `results/state_tilt/gatetol_latest.json` (E308, r1330)
**Verdict:** `a_gate_is_compared_with_something_and_that_something_is_rarely_the_legs_quantity`

## What was asked

The pool card E312: *"E308's scope test asks whether the producer compares with the gate at all — it
does not ask whether it compares the SAME quantity the leg compares; how many of the rows would
survive an operand-identity reading?"*

## Answer, in two steps

**Step 1 — the scope test was reading the wrong name.** All 30 band rows (11 faces, 12 gates; 31
upstream rows, 1 duplicate collapsed) publish their gate as a *bare constant*:

| face | published as | legacy scope | corrected |
|---|---|---|---|
| band family (`arrival/disagree/exp/flipbudget/floormirror/gapceiling/tight/transfer`) | `TOL` / `GAMMA_TOL` | declared_but_never_compared | compared through the constant |
| `repro_latest` / `REPRO-*` | `MATCH_TOL` | declared_but_never_compared / producer_not_found | compared through the constant |
| `t35_open_fill_verify` | `REL_TOL` | declared_but_never_compared | compared through the constant |

E308 scanned for the *declared key* (`tolerance`, `tol`, `rel_tol`). The comparisons use the
constant the key is bound to — `abs(float(r["b"]) - float(b)) <= TOL`, `repro["abs_diff_a"] <=
MATCH_TOL`, `if rel > REL_TOL`, `if lo >= FROZEN_GAMMA - tol` — or a parameter defaulted from it
(`def verdict_from(gammas, r2s, tol=GAMMA_TOL)`). Result: **29 of the 30 pairs E308 called
"declared but never compared" do have a producer comparison**, and the templated face
`REPRO-%s.json` resolves once the needle stops at the template marker instead of running to
`.json`.

**Step 2 — being compared is not being compared to the leg's number.** Of the 30 rows:

| operand identity | rows |
|---|---|
| operand names disjoint from the leg's keys | 25 |
| the leg names no face key at all (unanswerable at name level) | 4 |
| same named quantity | 1 |

And the two bands swap places:

- **`bandexp` falls.** This was E308's single surviving band. Its gate (`verdict_inputs.tol = 0.1`,
  published as `GAMMA_TOL`) is compared inside `if lo >= FROZEN_GAMMA - tol and hi <=
  FROZEN_GAMMA + tol:` — `FROZEN_GAMMA = 0.5` is E253's *assumption*, and the operands are the
  window edges `lo`/`hi`. That is a test of whether the ladder **can** decide, not a tolerance on
  the fitted gamma the leg compares at 1e-6. The name sets do not intersect.
- **`t35` stands, with a caveat.** E308 rejected this band as declared-only. Its gate compares
  `rel = abs(cost - session_open) / session_open` against `REL_TOL`; the leg compares
  `abs(_px - r["session_open"])` at 1e-9. Same object (`session_open`), different form: the gate is
  **relative**, the leg is **absolute**, so the gate still cannot be transported to the leg's number
  without a scale (`form_caveat` is published on the row).

Headline: **1 band stands after both readings, and it is not the band E308 thought** — in this
class, most legs are tighter than a gate that governs a different number, which is not a defect
for either side.

## Traps, all caught in-round

1. **Prose is not a comparison.** The first version scanned raw text: a docstring line carrying
   "tol" and a ">" harvested `this`, `counts`, `as`, `half`, `agreement` as operands. Comparisons
   are now read from `tokenize` NAME/OP tokens; strings and comments are never operands.
2. **`1e-06` is not the identifier `e`.** The number-literal exponent leaked into the leg's name
   set; identifiers now require a non-digit, non-dot prefix.
3. **"No key" is not "disjoint".** Four leg expressions compare two re-derived locals and name no
   face key (`abs(_re54 - _tgt54) > 1e-06`). Counting them as disjoint would have inflated the
   finding by 4 rows; they get their own partition.
4. **A census that greps for face filenames finds itself** (again — E294/E298/E308 family). The
   study excludes its own source and asserts it never appears as a producer.
5. **`in` on a list is not a substring test.** The self-inclusion identity leg passed with
   `"scripts/e312_gate_operand_identity.py"` in the producer list until it was rewritten with a
   substring scan — a check that cannot fail is not a check.

## Limits, published with the rows

A name-level overlap is a **lower bound** on identity: two code paths can compute the same quantity
under different names (invisible here), and two different quantities can share a short local name
(`r`, `b`). Every row publishes both name sets and every operand's one-hop definition, so the
reading can be re-checked by eye. The band arithmetic of E308 is untouched — this study only
re-scopes it.

## Reproduce

```
python scripts/e312_gate_operand_identity.py run       # rebuild both faces
python scripts/e312_gate_operand_identity.py verify    # 0 problems
python scripts/e312_gate_operand_identity.py selftest  # 21/21
```