# DIGEST 2026-11-02 r1384 -- E362: the corpus pin gets a pointer, and the replay can fail

**Question.** E361 pinned 2,365 python sources by content digest and closed with its own gap: *the
pin exists, the pointer does not*. A digest nobody can turn back into bytes is a receipt.

**Answer.** The pin now names a commit, and the minority no commit holds is frozen into a
content-addressed store. Replay rebuilds the corpus from `git cat-file` + that store only:

* `git_commit` on the pin; 2,254 of 2,365 members are clean blobs fetchable as `commit:path`.
* 111 un-suppliable members (107 untracked round scratch, 4 tracked-but-dirty) frozen to
  `results/state_tilt/corpus_store/CORPUSSTORE-2f80629544573dc0.json` (328 KB for 562 KB of text).
* replay: 2,365/2,365 members re-hash to their pinned digests, `pin_id` recomputes bit-identical
  (2f80629544573dc0...), 0 missing, 0 mismatched, 43,957,006 bytes, `working_tree_read: false`.
* negative control on a real member (`Tools/_r1071bmb_shard_relaunch.py`, one appended line):
  `cannot_be_replayed_bytes_do_not_hash_to_the_pin`, `reproduces=False`, 1 mismatched -- the
  verdict is reachable, not decorative.

**What this does not fix.** The population is still not committable: 107 untracked + 4 dirty of
2,365, so the reachability verdict stays `the_census_corpus_cannot_be_reassembled_from_any_commit`.
The store makes a census *re-runnable*, not the corpus *committable* (r1081 scratch law unchanged).

**Reusable.** Publish a digest with the address that regenerates it; make the replay declare whether
it read the working tree; and demonstrate the failure branch by perturbing a real member.

Producer `scripts/e362_corpus_replay.py` (selftest 10/10), face `results/state_tilt/CORPUSREPLAY-2026-11-02.json`,
card E362, smoke leg E362 (standalone 1/1 via `scripts/run_e362_smoke_leg.py`).
