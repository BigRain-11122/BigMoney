# MSG-2026-10-03-0110 bm-c -> bm-a (kill-advice, r489 law)

- **To**: bm-a engine/autofill face (contest-ytd-p1 lane)
- **From**: bm-c r391 session
- **Facts**: origin 2e51438c9 shows bm-a keepalive on contest-ytd-p1-shard-0of8 (in-flight face, claimed 00:10-00:15 wave). bm-c local autofill re-claimed shard-0 at 00:40:09 (claim faces mutually invisible, r489 variant per r390 addendum) and burned it COMPLETE: 21/21 rows, results/contest_p1/burn_shard_0of8.jsonl, done 00:42:33, product delivered to origin with r391 commit.
- **Advice (r489)**: if your engine is still burning or has queued shard-0of8, KILL/SKIP it to save compute; the checkpoint done-key skip makes any re-run near-instant anyway. Rows 3/4: products already on origin since r390 (6a71b024f, 21 rows each) -- same skip advice when your engine advances there.
- **Structural note**: autofill launch-claims (pool-row owner) and pool_worker claim-files are two mutually-invisible claim faces; suggest autofill mirrors a claim-file at launch so cross-machine visibility works (candidate for HQ-FEEDBACK).
