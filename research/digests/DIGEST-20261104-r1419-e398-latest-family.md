# Digest r1419 -- E398: who reads a `latest.json` pointer, and do they know which family wrote last

Face: `results/state_tilt/LATESTFAMILY-2026-11-04.json` (+ `latestfamily_latest.json`).
Card: `knowledge/METHODOLOGY_ASSETS.md` E398. Study: `scripts/e398_latest_family.py` (selftest 23/23).

## What was asked

E385 found that the largest merged published name is `latest.json`, with 28 files under it, and that
the name is a pointer *convention* rather than a face. The open question is a reader question, not a
name question: every call that opens a `latest.json` path is a site, and what matters about a site is
where its **family directory** comes from. A reader that resolves the pointer against a free runtime
base opens whichever family published last and looks perfectly healthy doing it -- the file exists,
it parses, and often the keys it asks for are there.

## What it measured

**Population** (as the tree stands): 28 bare `latest.json` files in 28 distinct family directories,
175 `<family>_latest.json` files, 11 with another `latest` shape. 187 in-repo read sites across 39
files; 59 write sites.

| class | read sites | reading |
|---|---|---|
| `family_stated_at_the_site` | 162 | the site's own literals or a resolvable module constant build the directory (incl. `os.path.join(ROOT, "results", "state_tilt", ...)` and `D.LIVE_DIR / "latest.json"`) |
| `family_required_by_the_signature` | 17 | the family is a parameter of the enclosing function (`os.path.join(outdir, "x_latest.json")`, `d = card_dir or CARD_DIR`); no constant default resolves in-tree |
| `family_from_the_value_the_site_itself_wrote` | 7 | read-after-write of a pointer the same function just dumped |
| `family_not_supplied_anywhere` | **1** | `smoke_test.py:7952` opens the bare name `'replaycensus_latest.json'` in the cwd |

Split by reader tier: **live tooling** (`scripts/`, `Tools/`, `monitor/`, `Money02/`) 36 sites --
16 stated, 17 signature, 3 written, **0 unsupplied**; smoke harness 142 sites (137 / 0 / 4 / 1);
scratch and estate (`results/_r*`, `_tmp_*`) 9 sites, all stated.

**What a wrong landing costs.** The 28 bare pointers carry **27 distinct top-level key signatures**;
of 378 confusable pairs only **1** (0.26%) has the same top-level key set. A reader whose base is a
runtime value and which lands one family off is therefore almost never reading "the same document
with other numbers" -- it is reading a different document, and the only reason it does not crash is
that the file it opened exists.

Write side, for symmetry: 59 pointer writes -- 16 build their directory from literals, 29 dump the
path they just built (`family_from_the_value_the_site_itself_wrote`), 12 take it from a parameter, 2
supply nothing. So the writer almost always *has* the family in hand; the pointer convention simply
does not carry it forward to the reader.

## Verdict

`some_latest_pointer_readers_are_handed_their_family_and_some_take_whatever_the_base_holds_so_the_
pointer_convention_is_safe_only_where_the_caller_is` -- and the live-tooling subset re-derives a
stricter line: `every_latest_pointer_reader_names_its_family_at_the_site_or_in_its_signature_so_a_
wrong_family_needs_a_wrong_caller_not_a_wrong_name`.

The sentence the card asked for: a reader whose base is a free runtime name opens whichever family
last wrote that directory's `latest.json`, so on a night when a different family published last it
reports that family's document under its own heading -- numbers, `evidence_cutoff` and verdict all
change, and nothing in the read can tell, because the file exists and parses.

The one unsupplied site is not in production code: it is a smoke leg that opens a bare relative name
and therefore depends on the cwd it is run from. That is worth stating plainly rather than fixing
here (no reader was edited this round).

## Bounds

Measured: static origin of each read site's family (literal / resolvable module constant / parameter /
read-after-write / nothing), the 28 bare pointers' top-level signatures, and the fan-out each
unsupplied reader could reach (28 families for the one that has none).

Not measured: the **callers** of the 17 signature sites -- whether every caller passes the right
family is a second census and the natural successor card; paths assembled through a name bound in
another module that never resolves in-tree; dynamic `getattr`-style opens. No pointer, reader or face
was edited.

## Pit notes (this build)

1. `os.path.join(ROOT, "results", "state_tilt", "x.json")` names the family as plainly as one literal
   would -- a rule that only accepts a single literal containing a slash reported 136 of 187 sites as
   "unsupplied", i.e. the bug was in the instrument, not the tree (first burn).
2. A one-argument wrapper passes the path through: `read(os.path.join(...))` was classified opaque
   until single-arg calls descended into their argument.
3. `a if cond else os.path.join("results", ..., "x_latest.json")` must be read through the branch
   that carries the pointer, not the first branch.
4. `_local_binds(fnode, line)` re-walked the function per site: `smoke_test.py` took 62 s to scan.
   Precomputing one `[(lineno, name, expr)]` per function took the whole corpus to ~9 s -- the
   measurement was correct both ways, but the slow path made `verify` look hung.
5. A writer's `OUT_DIR = os.path.join(ROOT, "results", "state_tilt")` is a family statement even when
   its root is a runtime name; resolution must accept the trailing literal run.