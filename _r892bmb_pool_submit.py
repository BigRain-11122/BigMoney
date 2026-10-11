# -*- coding: utf-8 -*-
"""r892 bm-b: submit N2U3 leg-2 probe pool entry (in-process driver --
PowerShell native-arg quoting strips inner JSON quotes; argv-list call
avoids the whole family). One-shot round driver, safe to re-run only
after editing the id (duplicate-id gate refuses otherwise)."""
import sys

sys.path.insert(0, r"Tools")
import autofill  # noqa: E402

ARGV = [
    "autofill.py", "submit",
    "--id", "N2U3-ALPHAGEN-RL-P1-LEG2-PROBE",
    "--runner", "scripts/alphagen_rl_p1.py",
    "--runner-args", "probe --episodes 256",
    "--shards", "n2u3-leg2-probe",
    "--workers", "8",
    "--lane-owner", "bm-b",
    "--priority", "1",
    "--ticket-ref",
    "N2U3-ALPHAGEN-RL-P1 leg-2 short-window training probe "
    "(freeze commit 8f49d6eea r892; runner multiproc conversion r892: "
    "parallel marginal eval face + L13 bit-exact equivalence leg, "
    "selftest 46/46; F-04 MSG-20261011-1835-bmb declaration)",
    "--prereg-ref",
    "research/N2U3_ALPHAGEN_RL_P1.md FROZEN 2026-10-11 (r892 freeze "
    "commit 8f49d6eea; five-condition gate closed; evidence_cutoff="
    "2026-10-09; seed bands 20625000/20625500/20626000)",
    "--consumer-plan",
    "N2U3 chain: leg-2 probe (pretrain + 256 eps PPO) -> probe_receipt "
    "throughput face sizes leg-3 full-training pool entry -> export-topk "
    "K=32 -> judged face (core48 all-start virtual timepoints "
    "g1_prime_v2/g2_registration_v2) -> N2 U3 channel-1 verdict; "
    "consumers = N2 U3 channel-1 closeout decision + factor material "
    "pool per prereg sec.0.9 item-2; P3 prediction face = RL marginal "
    "gain honest disclosure",
    "--data-deps",
    '["results/alphagen_rg/panel_cache_2026-10-09.npz"]',
    "--host-gates",
    '[{"kind": "dir_nonempty", "path": "results/alphagen_rg"}]',
    "--wp-note",
    "workers=min(worker_cap(),8)=8 per prereg sec.0 workers_plan; "
    "parallel marginal eval ProcessPool (O-20260930-2355 law-1 "
    "conversion); BelowNormal CEO headroom law",
    "--data-gates",
    "fail-closed rc2 freeze gate in-runner (prereg FROZEN + 3 seed "
    "bands required); panel gate = E16 frozen cache 2026-10-09 in "
    "place; universe/eligibility faces read-only",
]

_old = sys.argv
sys.argv = ARGV
try:
    autofill.main()
except SystemExit as exc:
    print("submit_exit_code:", exc.code)
finally:
    sys.argv = _old
