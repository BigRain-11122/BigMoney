# DIGEST r1634 bm-b -- E609: does a glob sweep reach the faces no literal names?

**Question.** E606 (r1633) published 86 faces whose printed count disagrees with their own rows and
reported that 82 of them carry no reader pair at all, with a limit in its own face: it counted
literal openers, so "no reader" was "no literal opener". This round prices the missing channel.

**Method.** Every `glob`/`iglob`/`rglob`/`Path.glob` call in the corpus is turned into the patterns
it can really use -- literal arguments, `os.path.join` / `Path` composition, f-strings, one hop of
name assignment -- absolutised patterns are made repo-relative, and each candidate is matched per
segment (Python's rule: `*` inside a segment, `**` across segments) against each face path. A
segment NAMES something when letter/digit text survives both the wildcards and a trailing extension
(`*.json` names nothing, `FILEHIT*.json` names the file, `results` names a directory).

**Readings.**
- 1,202 modules mention glob; 1,060 calls; 330 carry at least one naming segment, 18 carry none.
- All 82 faces are landed on by some glob -- 0 unreachable -- but that is not "read".
- 6 faces are reached by a pattern that names their own directory (all under `results/paper`, via
  `results/_r877bmc_badjson_scan.py` plus one W14 probe).
- 76 faces are reached only by patterns naming an ancestor: `results/**/*.json` (304 sites) and
  `*/**/*` (228 sites) land on them while saying nothing about `state_tilt` vs `paper`.

**Three self-caught defects.**
1. `*.json` strips to `.json` and an extension is not a name (E206 family, fourth recurrence): the
   first build graded 82/82 as "names the file". Fixed by requiring alphanumeric text after the
   trailing extension is removed; 28/28 selftest legs pin the rule.
2. Splitting only bounded/unbounded let `results/**/*.json` tie with `results/paper/**/*.json`.
   Added `names_an_ancestor_directory_only`, which turns 82/82 into 6/76 -- the difference between
   landing and naming.
3. An absolute pattern that is not normalised to a repo-relative one matches nothing, which reads
   exactly like "no sweep exists".

**Product.** `scripts/e609_glob_reach.py` (selftest 28/28; run/check/verify `problems=[]`),
`results/state_tilt/GLOBSWEEPREACH.json` (+ `-latest`), `scripts/run_e609_smoke_leg.py`
(PASS; `--doctor` 1/1 red; face restored byte-identical), smoke leg E609, S6 leg `glob_reach`
rc=0 108.0s, methodology card E610, pool E609 done with E611 seeded.

**Population note.** E606 printed 81 faces with no reader; its reader_pairs table holds 6 pairs
across 5 faces, only 4 of which appear among the 86 face rows, so the row-level population here is
82. That one-face difference is E606's own tally and is disclosed rather than repaired silently.
