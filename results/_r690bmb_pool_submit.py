# r690 bm-b: submit PERPETUAL-N2-W15-GENERATE pool entry (r446 file-law:
# argv built in python, zero PS quoting layers). autofill submit contract
# (r301+r305 trio + O-2355 multicore gate + D-20260929-02(2) inbox guard).
# W14-GENERATE same-type precedent; claim declared MSG-2026-10-04-1940-bmb-ALL.
import subprocess
import sys

argv = [
    sys.executable, r"Tools\autofill.py", "submit",
    "--id", "PERPETUAL-N2-W15-GENERATE",
    "--runner", "scripts/perpetual_faces_n2.py",
    "--runner-args", "generate",
    "--shards", "n2-w15-generate-0of1",
    "--workers", "1",
    "--wp-priority", "BelowNormal",
    "--wp-note", "generate leg = single-process draw census (raw 5,000 "
                 "Sobol draws A500/B4500 + scrnull face + T-84s3 fp dedup "
                 "+ tl14 28-source exclusion real-read, r494 smoke 2.6s/6 "
                 "-> est 30-60min); runner-internal RAM gate 4GB floor "
                 "(r354 three-sample, honest refuse + pool retry); "
                 "one-shot refuse-if-exists guard on candidates file",
    "--priority", "1",
    "--ticket-ref", "T-133 s2 standing supply ticket (O-2026-09-30-2340 "
                    "CEO standing-face order, prereg sec.0 authorization "
                    "face, no new signature needed); seat = MSG-2026-10-"
                    "04-1940-bmb-ALL F-04 first-declaration per MSG-2026-"
                    "10-04-1955 bm-c downstream open face; review PASS "
                    "receipt results/_r690bmb_n2_review.json",
    "--prereg-ref", "research/PERPETUAL_N2_W15_PREREG.md (FROZEN 2026-10-"
                    "04 r492 bm-c slice-3 freeze commit; bands 541_500/"
                    "542_000/542_500 width 499 forced-skip disclosed; "
                    "runner slice-2 bm-a r692 da8171889; FREEZE-GATE "
                    "registered=True live)",
    "--consumer-plan", "N2-W15 supply chain: generate -> n2_w15_candidates"
                       ".json (one-shot product) -> screen-prep -> 12-"
                       "shard screen burn (EW48 passive beat6m cheap "
                       "screen, tl2._finalize_math null p95 survival "
                       "line) -> screen-finalize (ledger append PERPETUAL-"
                       "N2-W15-SCREEN) -> survivors -> judge batch (separ"
                       "ately-frozen mass_trial precedent face) -> trial-"
                       "labor topic bank / registered-member supplement "
                       "line -> prereg sec.7/sec.8 backfill",
    "--data-deps", "[\"data/daily\"]",
    "--shard-checkpoint", "results/n2_w15/n2_w15_candidates.json "
                          "(single-shot product = completion marker; "
                          "refuse-if-exists guard active)",
    "--shard-note", "subspace draw: k_active~U{1..14} + uniform subset + "
                    "base-4-axis full domain + active-gate non-none "
                    "domain pinning; grammar sha16 a231bf10940e7878 "
                    "import-face; W15 new-syntax cells legal non-"
                    "exclusion face (selftest L9); evidence_cutoff="
                    "2026-09-22 same-window law",
]
r = subprocess.run(argv, capture_output=True, cwd=r".")
with open("results/_r690bmb_pool_submit_out.txt", "wb") as fh:
    fh.write(b"=== stdout ===\n")
    fh.write(r.stdout)
    fh.write(b"\n=== stderr ===\n")
    fh.write(r.stderr)
    fh.write(("\n=== rc=%d ===\n" % r.returncode).encode("ascii"))
sys.exit(r.returncode)
