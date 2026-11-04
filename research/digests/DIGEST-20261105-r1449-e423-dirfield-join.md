# DIGEST 2026-11-05 (r1449 bm-b) -- E423: the leg that never finished, and the gate that red on correct data

**Study.** E423 -- does any consumer join a directory-named field that holds a file path, and how many
published rows would compose a doubled name if one did.

**Face.** `results/state_tilt/DIRFIELD-2026-11-03.json` + `dirfield_latest.json`, re-published from the
live tree (12,861 faces / 3,401 sources): 29 read sites, 44 file-valued directory fields, verdict
`a_consumer_joins_a_directory_named_field_with_a_name_but_no_published_row_could_double`.

**Readings.**
- 12,861 published JSON faces -> 822 directory-named fields -> 44 hold a file path, in 8 faces / 42 rows.
- 3,401 python sources -> 29 reads of such a field: 19 whole-path, 8 republished, 1 prefix join,
  1 NAME join (`scripts/e347_published_number_gate_census.py:372`, `face["dir"].rstrip("/") + "/" + face["name"]`).
- The one name join lands on a listing whose rows hold a real directory: `joins_that_can_double = []`.
- 34 rows carry a name field beside a file-valued directory field (`resolved_directory` 22,
  `parent_dir` 10, `directory_expression` 2) -- the population a future join would double.

**What this window actually had to fix.** r1446 shipped the producer, the face, the smoke leg and the S6
row, but the leg was never re-derived end to end:

1. `read_sites` walked the whole AST once per read node, and tested containment with
   `any(sub is node for sub in ast.walk(outer))`. On `scripts/e39_panel_census.py` (230,290 nodes,
   7,430 reads) the leg and `verify` ran past 5 minutes with no output. Replaced by a parent-index climb
   (testing the node itself first, or the receiver chain `face["dir"].rstrip("/")` drops out of the name
   join), one index of `ast.Name` by identifier, and a bisect interval index for the enclosing definition:
   **36 s for 3,401 sources**. The live class tally is byte-identical to the published one -- that is the
   evidence the change is speed, not reading.
2. `verify` re-implemented the file-path test with a private extension list and raised **18 problems**
   on values the build graded correctly (`.jsonl`, `.json.tmp`, the expression
   `ROOT / "results" / "idle_trigger.bm-c.json"`). The gate now calls `value_class()`, and the smoke leg
   calls the same function instead of keeping a second copy.

**Verification.**
- `python scripts/e423_dirfield_join.py run` -- face re-published from the live tree
  (faces=12861 dir_fields=822 file_valued=44 read_sites=29).
- `python scripts/e423_dirfield_join.py verify` -> `problems=0` (~60 s).
- `python scripts/e423_dirfield_join.py selftest` -> 17/17.
- `python scripts/run_e423_smoke_leg.py` -> 1/1 PASS; `--doctor` -> 1/1 red, face restored byte-identical.
- `python Tools/s6_chain_bmb.py 1449 --only dirfield_join` -> rc 0, 34.6 s, `verify problems=0`.

**Method limits carried by the face.** A read is classified by the expression it sits in, one hop through
a bound name; a value stored on an attribute and joined two functions later is graded whole-path.
The doubling counterfactual is priced at the row, not proven at a call site. Faces larger than 3 MB are
not scanned.

**Card.** `knowledge/METHODOLOGY_ASSETS.md` E423.