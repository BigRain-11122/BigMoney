# E384 -- 882 of 883 published keys are opened by a real load or dump; the instrument was the finding

**Round** r1417 bm-b · **Face** `results/state_tilt/NEVEROPENED-2026-11-03.json` ·
**Runner** `scripts/e384_never_opened_key.py` (selftest 24/24, verify problems=[])

## What was asked

E381 published a defect (a face composed only of joined names) and E397 resolved all 884 published
keys against the tree.  Neither asked the reverse: **is the site that named this key a load or a
dump at all?**  A string in a source is not a decision to open a file -- the same literal can feed a
caption, a `print`, a comparison or a `Path` that is never read, and every such literal still enters
the key census E391/E397 price.

## What was measured

| reading | value |
|---|---|
| published keys | 883 |
| sites | 2,969 (1,921 load / 1,038 dump / 10 other) |
| keys opened by a load or dump | 882 |
| keys named only by non-opening sites | 1 |
| keys with no site in the corpus | 0 |
| published census faces scanned | 376 |
| bare keys carried by a published face | 0 |

The single residue is `results/perpetual_faces/n1_w192_results.json`, named at
`Tools/_r789bmc_post_rebase_verify.py:12` inside `json.loads(show(...))` -- a project-local helper
that reads a blob, so it *is* a read, just not one a stdlib call table can recognise.  No published
census face carries it, so **no published count moves**: the key population is not inflated by bare
literals here, and E391/E397 stand.

## The finding is the instrument

The first burn said **793 of 883 keys are never opened** (90%).  The cause is structural rather than
empirical: a key is usually a module constant (`FACE = "WALKAMBIG-%s.json"`) while the helper records
its site where the value is consumed (`json.load(open(FACE))`).  Classifying the face-shaped
literal's own line therefore answers "is this literal inside an open" for the ~10% of keys whose
literal sits at the call, and "no" for every key opened through a constant -- which is most of them.

Fix: map **every line a call covers** to that call's class, then look the site line up in that map.
Pinned by three selftest legs (`a_constant_opened_later_sites_the_call`,
`a_constant_declaration_is_not_a_site`, `write_mode_open_is_a_dump`) plus the `open`-mode leg: read
mode is a LOAD, `"w"`/`"a"`/`"x"` is a DUMP, so the table cannot guess from the callee name alone.

Second instrument law, caught on the second burn: the carrier scan must exclude **this study's own
faces**.  The bare key came back "carried by 2 published faces" -- the two files recording the
finding itself.  Third recurrence of the E180/E207 self-inclusion family; now pinned by
`own_faces_are_skipped_as_carriers` and by a smoke check that refuses a carrier naming an own file.

## Card and wiring

* `knowledge/METHODOLOGY_ASSETS.md` card **E400**.
* S6 leg `never_opened_key` (`python scripts/e384_never_opened_key.py verify`).
* Smoke leg: classes partition the population, the site tally re-adds, every never-opened row's
  sites are OTHER, the carrier count follows from its own list, no own face is a carrier, the gate
  re-derives, and the study's own verify is clean.
* Pool: **E384 done** with `result_ref`; successor **E401** seeded (a project-local reader is
  invisible to a stdlib call table -- enumerate local helpers that open files and re-run the
  classification with them added).