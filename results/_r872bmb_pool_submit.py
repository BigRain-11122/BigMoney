# -*- coding: utf-8 -*-
"""r872 bm-b: pool-submit T-101-V4-A14-PREDFACE (T26 slice-3; r690 file-law:
argv built in python, zero PS quoting layers). autofill submit contract
(r301+r305 trio + O-20260930-2355 multicore gate + D-20260929-02(2)
inbox guard). F-04 declaration landed this window
(fleet/inbox/MSG-20261011-0905-bmb-a14-predface-freeze.md)."""
import subprocess
import sys

argv = [
    sys.executable, r"Tools\autofill.py", "submit",
    "--id", "T-101-V4-A14-PREDFACE",
    "--runner", "scripts/t101_v4_a14_predface.py",
    "--runner-args", "run --shard 0 --shards 1",
    "--shards", "t101-v4-a14-run-0of1",
    "--workers", "4",
    "--wp-priority", "BelowNormal",
    "--wp-note", "30-cell informational predictor batch (3 mask-mean "
                 "features x 5 members x RAW/RESID): per-member "
                 "ProcessPool jobs (A158 157-factor + MP1 89-formula "
                 "build + shift-nulls K=200 x3 segs + block bootstrap "
                 "B=2000 x2 segs) then 15 resid cell jobs; A13 40-cell "
                 "27.8s same-machinery baseline + mp1 factor face "
                 "increment -> est 1-3 min wall on 4 workers; RAM "
                 "trivial (<1GB); runner-internal fail-closed gates "
                 "(five-member anchor rows + tail-date assert + "
                 "G-ANCHOR-MP1 3341/390/149 reproduction + MP1 roster "
                 "identity) every invocation",
    "--priority", "1",
    "--ticket-ref", "tech.md T26 row (r871 bm-b registered+claimed "
                    "commit 1bbd0bdfd; DIGEST-20261011-w21 Q2 "
                    "adjudication: A13-style predictor extension on the "
                    "v4 22-gate library = the only open consumption "
                    "face; A13 sec.8 downstream pointer: f_c2 "
                    "continuous prediction face -> A1/C1 composite "
                    "named input feature (bm-b lane); supply-floor "
                    "response: audit FLAG pool ready=0<3 this chain "
                    "raises the floor 0->1)",
    "--prereg-ref", "research/T-101-V4_A14_PREDFACE_PREREG.md FROZEN v1.0 "
                    "(r872 bm-b freeze commit b22d02a08 five-condition "
                    "chain: selftest 16/16x2 + draft-probe rerun "
                    "byte-identical md5 9af05782500f + banned gate ADMIT "
                    "rc0 + origin pre-write DRAFT check + same-commit "
                    "runner+SEED_REGISTRY 20615500/20616500; 30 cells; "
                    "evidence_cutoff 2026-10-09)",
    "--consumer-plan", "T-101-V4-A14-PREDFACE run shard 0of1 -> "
                       "results/t101_v4_a14/shard_0of1.jsonl "
                       "(append-per-record checkpoint, done-set resume) "
                       "-> finalize (any healthy machine, "
                       "refuse-if-exists + single-shot landed-batch law) "
                       "-> results/t101_v4_a14_predface.json + "
                       "append_ledger(batch_trials=30) + prereg sec.7/"
                       "sec.8 backfill -> FV-PASS/supply-note cells -> "
                       "A1/C1 composite input-feature roster (named "
                       "consumer, composite arm itself gated behind "
                       "BAN-05 + sentiment-family double-negative per "
                       "DIGEST Q3) + T-101 v4 arm-table A14 row + "
                       "gate_attrition row for negative cells; "
                       "trials-ledger batch (marks +0 SEED +0, 30 "
                       "cells counted at finalize)",
    "--data-deps", "[\"data/daily\"]",
    "--shard-checkpoint", "results/t101_v4_a14/shard_0of1.jsonl "
                          "(append-per-record done-set resume; 5 raw "
                          "member records + 15 resid cell records; "
                          "pool-claim handshake "
                          "results/pool_claims/T-101-V4-A14-PREDFACE/"
                          "t101-v4-a14-run-0of1.<machine>.json on "
                          "completion)",
    "--shard-note", "frozen cell order raw(0..14) resid(15..29); "
                    "cell_idx by position = rng streams "
                    "[20615500/20616500, cell_idx] deterministic "
                    "regardless of scheduling; MP1 mask machinery "
                    "import single-source (mp1_tsgate_probe.mp1_factors "
                    "-> t23.evaluate); A158 face via "
                    "a158_tsgate_probe.gate_universe (fv.GATES17); "
                    "RESID phase needs all 5 member records "
                    "(0of1 contract face; multi-shard split defers "
                    "honestly if members incomplete)",
]
r = subprocess.run(argv, capture_output=True, cwd=r".")
out = r.stdout.decode("utf-8", errors="replace")
err = r.stderr.decode("utf-8", errors="replace")
with open("results/_r872bmb_pool_submit_out.txt", "wb") as fh:
    fh.write(b"=== stdout ===\n")
    fh.write(r.stdout)
    fh.write(b"\n=== stderr ===\n")
    fh.write(r.stderr)
    fh.write(("\n=== rc=%d ===\n" % r.returncode).encode("ascii"))
print(out[-800:])
if err.strip():
    print("STDERR:", err[-400:])
sys.exit(r.returncode)
