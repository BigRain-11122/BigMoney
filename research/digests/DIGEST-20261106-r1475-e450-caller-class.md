# DIGEST r1475 (bm-b) — E450: the caller side of E444's attribute rows is empty, and the name test is a coincidence generator

**Verdict:** `some_bound_or_constructor_rows_name_a_method_carried_by_a_class_in_the_callers_module_but_a_name_is_not_a_type`
— 26 of 23,982 rows carry the name, and only 13 of those have the receiver actually bound to the
class. The index did not misattribute a population of readers; it missed 13 rows in two files.

Face: `results/state_tilt/callerclass_latest.json` (+ `CALLERCLASS-2026-11-06.json`).
Producer: `scripts/e450_caller_class.py` (selftest 43/43, check problems=0).

## What E444 left open

E444 graded all 24,618 attribute call rows against the classes of the module each row was
**attributed** to, and found those six modules define zero classes, so no row could name a method
there. That settles the wrapper side and says nothing about the caller side: if the receiver is a
name the caller binds, the class it names a method of is usually defined in the **caller's own**
module, and such a row is a real reader the name index filed under the wrong module.

## Two readings, deliberately not merged

| | rule | rows | share of 23,982 |
|---|---|---|---|
| **N (name)** | the method name is carried by some class defined in the caller's file | 26 | 0.11% |
| **B (binding)** | the receiver *is* that class — assigned a call to a local class (or is the constructor call itself) which carries the name | 13 | 0.05% |

N is a name test and a name is not a type: `other = open(path); other.write(...)` matches any
class in the same file that happens to carry `write`. The 13-row gap is not noise — it is exactly
the whole of `Tools/pool_worker.py`:

| caller module | N | B |
|---|---|---|
| `Tools/pool_worker.py` | 13 | **0** |
| `scripts/etf_book_forward.py` | 11 | 11 |
| `scripts/alphagen_rl_p1.py` | 2 | 2 |

So the single largest name-hit module contributes **zero** real readers, and the two modules that
do contribute are unambiguous: `fwd = Forward(...)` → `fwd.run(...)` (and `f0..f5`), and
`policy = TinyPolicy(...)` → `policy.save(...)`. Spot-read in source, both real.

## Binding, by how the name got its value

| binding | rows |
|---|---|
| assigned a call to a class defined in the caller | 13 |
| assigned a call to something that is not a local class | 6,875 |
| assigned something that is not a call | 11,685 |
| never assigned here (parameter / import / loop target) | 4,375 |
| receiver is not a name (constructor row) | 1,026 |

## The population pin (E455's rule, applied)

The face re-derives E444's population live and pins itself to E444's published receiver
distribution. It is **not** exact equality — the corpus grows every round, so that would be a
one-round purchase (E455). What is asserted: no receiver kind may lose rows, and E444's own
distribution must sum to its published total.

* E444 published 24,618 rows; this window re-derived **24,831 (+213)**.
* The growth is confined: `a_name_the_caller_binds` +210 (22,746 → 22,956),
  `a_constructor_call_in_the_caller` +3 (1,023 → 1,026); the other four kinds are **byte-identical**
  (2 / 847 / 0 / 0). Nothing lost. `growth_only_superset`.
* Evidence that the classifier did not drift: four of six kinds are exactly unchanged, and
  the +213 is entirely new code arriving in an unchanged population.

Measured twice in one window: the first build read 24,823 and the second (nine minutes later)
24,831. The tree grows while you measure it — which is why the pin is a rule, not a number.

## Pit

My first `verify` compared the published summary to a fresh reading with exact equality. That is
the defect E455 was carded for, walked into by the very round after it was fixed. `verify` now
hands both payloads to `scripts/growth_tolerance.py` with the demographic as the row identity and
the claim (`name_hit`, `binding_hit`) as the class, so growth is reported and only a lost cell, a
shrunk count or a flipped claim is a refusal.

## How to apply

A question of the form "does the name index misattribute readers to the wrong module?" must publish
**the name arm and the binding arm separately**, because the name arm is inflated by ordinary
method-name collisions. In this repository the inflation was 100% of one module's hits. Any census
that answers "does X name Y" without asking "is the receiver Y" is a lower bound wearing an
answer's clothes.