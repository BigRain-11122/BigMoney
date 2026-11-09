---
card: E624
round: r1642
machine: bm-b
cutoff: 2026-11-09
dept: research+engineering
face: results/state_tilt/SIBLINGREADOBJECT-2026-11-09.json
script: scripts/e624_sibling_read_object.py
smoke_leg: E624 (smoke_test.py) + scripts/run_e624_smoke_leg.py
s6_leg: sibling_read_object
---

# E624 — the same key is not the same dict

## The question

E623 counted 6 of its 34 live dead face-key lines as `superseded_duplicate_read`: another read of
the same literal key exists on a later line of the same function. E623's own `limits` block states
the hole — *a read counts when it indexes the same literal key, whatever the object*. `got["verdict"]`
and `faces[UP_E350].get("verdict")` are both "a read of the key verdict"; they are not the same
dict, so the second is not a re-read of anything the first produced.

E624 asks that question of every sibling read E623 counted: **is the receiver the same object?**

## How it is decided

Each read's receiver is recovered (`m["k"]` → `m`, `x.get("k")` → `x`) and the two receivers are
compared. Four relations, fixed before the scan:

| relation | meaning |
|---|---|
| `same_receiver_bound_once` | same expression text and no statement between the two lines binds that name (or assigns that attribute path) — the same object, provably |
| `same_receiver_rebound_in_between` | same text, but the name/path is bound in between — an earlier value is not the current one |
| `different_receiver_expression` | the receiver text differs — a different object |
| `receiver_is_a_computed_expression` | a call result, or no nameable base — identity not decidable statically |

The population is E623's published line rows, obtained by **importing** `e623_deadline_key_use`
(its `classify_tree`, `innermost`, `own_scope`, `key_reads`), not by re-implementing the classifier,
with a cross-check that the re-derived rows match the published face **line for line and class for
class** — they do, 34/34, zero differences.

## Readings

34 live dead face-key lines carry **26 sibling reads** (13 lines have any):

- `same_receiver_bound_once` — **19**
- `same_receiver_rebound_in_between` — **0**
- `different_receiver_expression` — **7**
- `receiver_is_a_computed_expression` — **0**

Under object identity **4 of E623's 6 superseded duplicates survive**:

| line | dead receiver | sibling | verdict |
|---|---|---|---|
| `cn_core_ddctl_p1.py:367` | `P` | `P` at 395 | same object |
| `cn_mkneutral_p1.py:507` | `P` | `P` at 589, 593 | same object |
| `e590_cash_silence.py:364` | `r` | `r` at 362, 367, 372, 377 | same object (same loop item) |
| `ew6_portfolio.py:393` | `ports` | `ports` at 414 (plus `sleeves[tid]` ×4) | same object |
| `e382_key_projection_delta.py:332` | `faces[UP_E377]` | `got` at 284, `faces[UP_E350]` at 350 | **another object** |
| `e504_name_compose.py:879` | `face` | `doctored4` at 919 | **another object** (`doctored4 = json.loads(json.dumps(face))`) |

Corrected tally over all 34 lines: **4** same-object superseded / **7** same object only before the
dead line (the loop-carried shape) / **2** another object is read instead / **21** the only read of
that key on that object in the function. The four add to 34.

Verdict (recomputed by the gate from the rows):
`4_of_6_superseded_duplicate_reads_read_the_same_object_as_the_dead_line`.

## What is measured, not assumed

1. **A row can carry both kinds at once.** `ew6_portfolio:393` has one same-object read (`ports` at
   414) and four reads on `sleeves[tid]` — the row survives, but only because the test is `any()`.
   `all()` would have rejected it. Both answers must be printed for the row to be readable.
2. **A copy is a different object.** `json.loads(json.dumps(face))` and `dict(m)` are new dicts;
   treating a copy as the same object would have kept e504's row alive.
3. **A rebinding is decided only inside the interval.** `m = {...}` between the two lines breaks
   identity; a `for` target bound *before* the dead line does not, so a read in the same iteration
   stays the same object. That is what separates the 7 loop-carried rows from the 4 real ones.

## Limits published, not claimed

- **No alias analysis.** `q = P` then `q["days"]` is published as `different_receiver_expression`
  even though both names may hold one dict. Every row carries both receiver texts so the 34-line
  population can be checked by eye.
- **Object identity is not value identity.** `m["k"]` read twice with `m["k"] = ...` in between is
  still "the same object". That gap is E625's population.
- In-place mutation through a function argument (`f(m)`) is invisible.

## Wiring

- `scripts/e624_sibling_read_object.py` — `selftest` **27/27**, `check`/`verify` `problems=[]`.
- `smoke_test.py` leg E624 — re-derives every relation tally and corrected class count from the
  line rows, re-asks the verdict, requires the two superseded halves to add up, refuses a
  `same_object` flag that contradicts its relation, requires the E623 cross-check to still agree,
  and excludes the study from its own population.
- `scripts/run_e624_smoke_leg.py` — extracts the published leg and runs it standalone (1/1 PASS);
  `--doctor` flips the verdict and gets 1/1 red with the face restored byte-identically.
- `Tools/s6_chain_bmb.py` leg `sibling_read_object` — `rc=0 0.05s problems=[]` (no corpus walk).
- POOL: E624 done → **E625 seeded** (whether the value a sibling read returns is the one the dead
  line saw).

## Honest wall note

The full 300-plus-leg smoke suite and the full S6 chain were **not** re-run this window
(`smoke_test.py` has no leg filter, r1499). The new leg and its standalone mirror are green, and
red under `--doctor`. The build walks the corpus (~200s); `verify` is the 0.05s path.