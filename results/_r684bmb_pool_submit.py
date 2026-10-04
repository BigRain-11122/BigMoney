# r684 bm-b: submit CONTEST-YTD-P1-RC-0OF1 pool entry (r446 落文件律: argv
# built in python, zero PS quoting layers). Contract trio via autofill submit.
import subprocess
import sys

argv = [
    sys.executable, r"Tools\autofill.py", "submit",
    "--id", "CONTEST-YTD-P1-RC-0OF1",
    "--runner", "scripts/contest_ytd_legs.py",
    "--runner-args", "revcensus",
    "--shards", "contest-ytd-p1-rc-0of1",
    "--workers", "4",
    "--wp-priority", "BelowNormal",
    "--wp-note", "census law RAM floor 16GB internal (exit 3 while trio "
                 "NULLS burns hold RAM); ~8GB/worker stock-panel sizing; "
                 "10 cells single shard",
    "--priority", "1",
    "--ticket-ref", "T-2026-10-02-148 slice-3 pending-legs (O-202601002-2150 "
                    "CEO survivor-king contest; O-2155 contest-fuel; 10 "
                    "REV_CENSUS_POSITIVE entrants YTD legs; due before "
                    "10-08 governance day)",
    "--prereg-ref", "results/contest_p1/entrants.json admission face frozen "
                    "slice-1; contest caliber = runner header (today-engine, "
                    "x1, YTD window, census-parity anchors vs published "
                    "shard rows); RAM floor = refine_bench_rev_census "
                    "census law",
    "--consumer-plan", "contest_table.json assembly A1.5 auto-include "
                       "(assembly rerun; CEO winner-selection face by "
                       "10-08; live-entry consideration queue; 10-31 "
                       "monthly exam scoring face)",
    "--host-gates",
    '[{"kind": "dir_nonempty", "path": "Money02/data/cache/p1c_stock"}]',
    "--data-deps",
    '["Money02/data/cache/p1c_stock", "Money02/data/bars", '
    '"Money02/data/index/sse.parquet", "data/fundamental/b_layer_mask.csv"]',
    "--shard-checkpoint", "results/contest_p1/burn_pending_revcensus.jsonl "
                          "JSONL resume (done-key skip, idempotent)",
    "--shard-note", "10 RC faces x YTD backtest (frozen p1c panel, natural "
                    "end 09-22, disclosed); census-stats parity anchors "
                    "abort on drift",
]
r = subprocess.run(argv, capture_output=True, cwd=r".")
print(r.stdout.decode("utf-8", "replace"))
print(r.stderr.decode("utf-8", "replace"))
sys.exit(r.returncode)
