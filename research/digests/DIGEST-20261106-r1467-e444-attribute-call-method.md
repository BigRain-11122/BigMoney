# DIGEST-20261106-r1467-e444-attribute-call-method

**Card** `E444-WHICH-ATTRIBUTE-CALL-NAMES-A-METHOD-OF-A-CLASS-IN-THE-MODULE-IT-WAS-ATTRIBUTED-TO`
**Producer** `scripts/e444_attr_method.py` (selftest 36/36, `run` rc0, `check` problems=[],
`verify` problems=[])
**Face** `results/state_tilt/attrmethod_latest.json` + `ATTRMETHOD-2026-11-04.json`
**Verdict** `no_attribute_call_row_could_name_a_method_because_the_attributed_modules_define_no_class_at_all`
**Chain** S6 leg `attr_call_module_method` (`check`, no corpus walk); smoke leg
`e444 which attribute call names a method of its own module`
**Cutoff** 2026-11-04 (E440's `evidence_cutoff`, inherited: this study re-reads E440's population)

## Question

E440 dropped 24,308 attribute call rows with one sentence -- "the receiver is an object, not a
module wrapper" -- which is a claim about **spelling**. It never asked whether the name is a method
of a class defined in the very module the row was attributed to. If it is, the row *is* evidence
about that module and the reachability drop threw away a real reader.

## Answer

**0 of 24,618 attribute rows name a method of a class in the attributed module** -- and not by a
narrow margin: the six modules those rows were attributed to define **no class at all**.

| reading | value |
|---|---|
| attribute call rows graded | 24,618 (E440's class, re-derived live) |
| modules the rows were attributed to | 6 |
| classes defined across those modules | **0** (0 methods) |
| rows naming a method of a class there | **0** (0.0 %) |
| rows production / test | 18,868 / 5,750 |
| reproduces E440's attribute count | true (24,618 = 24,618) |

By receiver spelling at the row's own line: a name the caller binds **22,746**; a constructor call
in the caller **1,023**; another expression **847**; a name the caller never binds **2**;
`self`/`cls` inside the caller's class **0**; nothing at that line any more **0**.

By wrapper name: `append` 15,464, `write` 4,778, `dump` 2,566, `run` 1,706, `save` 97,
`write_json` 7. Five further wrapper names (`_write_csv`, `_syn_file`, `_judge_lock_acquire`,
`apply_close`, `write_face`) carry no attribute rows at all and are published as
`wrapper_names_with_no_attribute_rows` rather than as graded names with a zero.

Modules behind the rows: `_r1191bmb_closeout.py` (append), `Tools/_r195_rebase_resolve.py` (write),
`Tools/_r1029bmc_close.py` (dump), `scripts/e110_burncontrol_close.py` (run),
`Tools/_r1390_addendum.py` (save), `Tools/_r1164bmb_push.py` (write_json) -- each parsed, each
`class_count = 0`.

## What was actually learned

1. **A zero hit is a census answer, not a null result -- so the face must carry the census.** "0 of
   24,618" alone reads as "we looked and found nothing". The reason it is zero is that the modules
   contain no class to name a method of. The face publishes `classes_defined_across_those_modules`,
   per-module `class_census`, and a verdict that names the mechanism, and the guard refuses any
   face that claims a hit while the census finds no class anywhere.
2. **The population has to be re-derived, not quoted from the card.** The card says 24,308; the
   live tree says 24,618. Both numbers are published and `reproduces_e440_attribute_count` is
   computed from them, then re-derived by the guard from its own two fields -- quoting the card's
   number would have made the reproduction unfalsifiable.
3. **A block that lists only graded names cannot be closed against a count of all names.** The
   first build published `per_name` over all 11 wrappers while `distinct_wrapper_names_graded` was
   6, and its own "per_name covers every wrapper name graded" leg accused the face of a gap it did
   not have. Absent names now have their own field. The lesson generalises: when a face both
   enumerates a population and grades a subset, the subset needs its own count and the complement
   needs its own name.

## Method limits (carried in the face)

* A method counts only when it is a `def` inside a `ClassDef` body in the attributed module; a
  module-level function of the same name is not a method.
* A row matching methods on several classes is counted once in the cells and once in each class
  under `rows_by_class_in_the_attributed_module`, which is therefore not a partition of the total.
* The receiver is read from the caller's live AST at the row's own line; a file edited since the
  row was indexed reports `the_receiver_is_not_at_that_line_in_the_live_file` rather than a guess.
* Bound/unbound is module-wide, so a name bound in a different function reads as bound; receiver
  kind is a spelling fact, not a type.