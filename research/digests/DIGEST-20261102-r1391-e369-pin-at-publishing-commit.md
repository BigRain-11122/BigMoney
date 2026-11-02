# Digest r1391 -- E369: the pin is now at the right commit, and the number still does not come back

Face: `results/state_tilt/PUBLISHPIN-2026-11-02.json` (+ `publishpin_latest.json`).
Pin: `results/state_tilt/CORPUSPIN-AT-COMMIT-daf9a897.json`.
Card: `knowledge/METHODOLOGY_ASSETS.md` E369. Study: `scripts/e369_pin_at_publishing_commit.py`.

## What was done

E368 reproduced the verdict number over a pin taken the day after E350's face was published, which
cannot tell stability from provenance. E369 takes the pin at the commit E350's own face records --
the vintage is machine-read from `fieldbranch_latest.json`, never typed into the study -- and reads
the whole population from that tree:

- members from `git ls-tree -r --name-only -z <commit>` filtered by E346's imported corpus rule
  (`scripts/monitor/Tools/firm/live/content` `*.py` + `smoke_test.py`);
- bytes from one `git cat-file --batch` pass, CRLF/CR folded to LF before hashing (so a pin digest
  cannot drift with a checkout's line endings);
- digest over the sorted `(path, sha256)` pairs = `pin_id`.

At the publishing commit the corpus holds **2,251** members, `pin_id`
`7aacd4d5a13d423740432aac1117f121fd765314969d23e94769390de8295c79`.

## What it measured (pin: 2,251 members @ daf9a897, pinned bytes only)

| key | published | at the publishing commit | delta |
|---|---|---|---|
| E350 corpus_sources | 2,343 | 2,251 | **-92** |
| E350 fields | 2,289 | 2,264 | -25 |
| E350 fields_with_no_writer | 1,698 | 1,687 | -11 |
| E350 guard_fields | 230 | 226 | -4 |
| E350 guard_fields_with_no_writer | 131 | **129** | -2 |
| E353 pairs | 131 | 129 | -2 |
| E353 guard_never_fires_on_a_falsy_value | 34 | 34 | 0 |

Verdict: `a_pin_taken_at_the_publishing_commit_does_not_reproduce_the_published_corpus_size_2251_against_2343_so_the_face_was_built_from_a_tree_no_commit_holds_and_the_bill_is_a_pin_plus_a_store_per_vintage`

## The store bill (against E361's publish-day pin, 2,368 members)

| item | count |
|---|---|
| fetched from the commit | 2,240 |
| absent from the commit (must be stored) | **128** |
| present, other bytes (also unreachable as-is) | **6** |

The absent members are the files that were on disk and untracked when the census ran, e.g.
`Tools/_r1071bmb_shard_relaunch.py`, `Tools/_r1096_closeout.py`, `Tools/_r1096_pool.py`.

## The four readings worth keeping

1. **Right vintage, wrong answer.** Provenance does not imply reproduction: with the pin finally at
   the grading face's own commit, `corpus_sources` is 92 short and the guard headline moves by 2.
   The E368 number that came back was a statement about two nearby trees.
2. **A pin cannot hold what no commit ever held.** 128 of the publish-day population never existed
   in any commit; a pin taken at a commit covers only what the commit holds, so the honest unit is
   *one pin per vintage plus one store per population*.
3. **Only one key was invariant.** `guard_never_fires_on_a_falsy_value` = 34 in both populations
   while every count around it moved -- publishing per-key deltas turns "the number comes back"
   into a measurement instead of a claim about the face.
4. **The vintage is a field you read.** A selftest leg greps the study's own source to prove the
   commit hash is not embedded; a rule enforced by memory is not enforced.

## Bound published

The bill is measured against E361's disk pin (2,368 members), which is the same population *family*
as the face but not the face's own member list (the face counted 2,343 sources). "Must be stored" is
therefore a bound on that population, not a reconstruction of the face's exact input; the study's
`bound` field says this in the face itself.

## Wiring

- `scripts/e369_pin_at_publishing_commit.py` -- `run` / `verify` / `selftest` (12/12).
- `smoke_test.py` leg E369 + `scripts/run_e369_smoke_leg.py` (executed verbatim: 1/1 PASS).
- `results/runnable_pool.json`: E369 done with `result_ref`; follow-ups seeded (E372 store the
  unheld members, E373 apply the same reading to E353's own publishing commit).