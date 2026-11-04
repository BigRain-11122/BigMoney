# DIGEST r1430 (bm-b) -- E406: 126 modules read a committed blob and exactly one puts it beside the file

**Face:** `results/state_tilt/BLOBREAD-2026-11-05.json` (+ `blobread_latest.json`)
**Script:** `scripts/e406_blob_vs_tree_readers.py` (run / verify problems=[] / selftest 14/14)
**Card:** `knowledge/METHODOLOGY_ASSETS.md` E406
**Seeded by:** pool card `E406-DOES-A-READER-OF-A-COMMITTED-BLOB-KNOW-IT-CAN-DIFFER-FROM-THE-FILE`

## The question

E401 priced every site the stdlib call table called `other` and found all ten are git-object reads:
`subprocess.run(["git", "show", "HEAD:" + path])` and family, across 4 keys and 63 direct helpers.
A working-tree read and a committed-blob read of the same published face disagree whenever the face
is newer than the last commit -- which it is all day, because a round publishes and then commits.
E401 priced the blind spot; this study prices the *consequence*: which readers exist, which of them
can notice a drift, and how far apart the two readings are right now.

## Result -- 307 attributed call sites, 126 modules, 58 faces named

| measure | value |
|---|---|
| git-object callables (E401 arm, reused) | 66 |
| attributed call sites | **307** |
| modules holding one | **126** |
| call rows that a name alone could not be attributed to | **2,504** |
| face names a blob reader can name | 58 |
| faces with both a blob at HEAD and a file on disk | 25 |
| faces whose blob and file differ right now | **5** |
| faces whose *verdict string* moved | **1** |
| largest top-level key delta | 11 |
| largest headline delta | 4 |
| modules that compare the two arms | **1** |

The single comparing module is `scripts/e365_face_population_pin.py`, and only through one paired
name; the other 125 read a blob and never look at the file beside it.

## The five disagreements, measured at this round

| face | keys moved | headline moved | basis |
|---|---|---|---|
| `results/state_tilt/greenwindow_latest.json` | 11 | 0 | module face literal |
| `results/state_tilt/siblingentry_latest.json` | 6 | 2 | module face literal |
| `results/state_tilt/guardloosen_latest.json` | 4 | 1 | module face literal |
| `results/state_tilt/repairrecord_latest.json` | 4 | 0 | module face literal |
| `results/state_tilt/REPUBLISH-2026-11-03.json` | 3 | 4 | module face literal |

`siblingentry_latest.json` is on that list because this very round republished it before the census
ran: the blob still says the old population (2,466 sources), the file says 2,467. That is the
mechanism, observed rather than argued -- a reader of `HEAD:` would answer with the stale face and
no leg would go red.

## Where the count is honest and where it is not

**The instrument was wrong twice and both errors were mine.** A corpus-wide name match attributed
2,811 sites over 1,729 modules because `_head`, `main`, `raw`, `blob` and `stage` are reused by
unrelated modules (E366's one-name-two-entities); the fix is per-module resolution -- the callee
must be defined as a git-object helper in *this* module, or imported here from the module that
defines it. After that, 2,504 calls still carry a name that no import resolves, and they are
published as `unresolved_name_rows` rather than silently counted; the site total is therefore a
floor, not a census.

**Face names carry a basis, because a helper takes the path as a parameter.** `literal_in_body` and
`literal_at_call_site` are strong; `module_face_literal` means "this module names face X and passes
a path to a blob reader at runtime", which is weaker. Of the 58 names, 32 resolve to no file at all
-- they are fixture names inside a temporary directory or pieces of a formatted name (the E402
family), and they are labelled `name_resolved_to_no_file` instead of being dropped.

## What this does not do

It does not rewrite a reader and it does not write to git: every measurement is one `git show` per
face, read-only. The repair -- a leg that fails when a blob reader's face moved under it -- is a
separate card, and this face is the population it would cover.

## Verdict

`some_module_compares_the_blob_to_the_file_and_the_rest_cannot_notice_a_drift`