# -*- coding: utf-8 -*-
"""R248 bm-a: register T-73 s3 slice-1 (CN-REV-TILT-P1) post-review row per
O-2115/R246 law -- claim + claim_source (pre-frozen faces only) + machine
checks (product-field existence/consistency, zero post-hoc criteria)."""
import io
import json

P = "results/post_review_criteria.json"
d = json.load(io.open(P, encoding="utf-8"))
items = d["items"]

if any(it.get("id") == "T-73-CN-REV-TILT-P1" for it in items):
    print("row already present; no-op")
    raise SystemExit(0)

items.append({
    "id": "T-73-CN-REV-TILT-P1",
    "claim": "T-73 s3 slice-1 CN-REVERSAL-TILT full arc: prereg frozen pre-run "
             "(R245/R246 zero runs) -> runner scripts/cn_rev_tilt_p1.py (selftest 30/30) "
             "-> pool batch CN-REV-TILT-P1 landed 13:40:50 (T8792/N5222/cutoff 2026-09-22, "
             "N_trials 54, ledger 185798+54=185852) -> deterministic harvest (r244 law) flipped "
             "pool done + verdict NEGATIVE 4/4 G1'v2 (x1 Sharpe 0.1976/0.4757/0.0104/0.4217 all "
             "< skill line 0.6147) -> G2 not applicable -> model judged negative per prereg s4, "
             "no CN-* paper wiring (correct fail-closed closure); prereg s7/s8 backfilled with "
             "run numbers only; tilt axis falsified per s5.2 pre-registered honest possibility",
    "claim_source": "research/CN_REV_TILT_PREREG.md (frozen R245/R246 pre-run; R99 law: post-run "
                    "s7/s8 backfill only) + T-73 progress_r246 runner contract (frozen) + "
                    "results/_r248bma_cnrev_harvest.py (deterministic harvest gate, exit 0) + "
                    "runner.log finalize line + results/cn_rev_tilt/p1_results.json product",
    "status": "closed",
    "checks": [
        {"kind": "file_exists", "args": ["scripts/cn_rev_tilt_p1.py"]},
        {"kind": "file_exists", "args": ["results/cn_rev_tilt/p1_results.json"]},
        {"kind": "file_exists", "args": ["results/_r248bma_cnrev_harvest.py"]},
        {"kind": "json_field",
         "args": ["results/cn_rev_tilt/p1_results.json", "evidence_cutoff",
                  "2026-09-22"]},
        {"kind": "json_field",
         "args": ["results/cn_rev_tilt/p1_results.json", "ledger.total", "185852"]},
        {"kind": "json_field",
         "args": ["results/cn_rev_tilt/p1_results.json", "n_trials", "54"]},
        {"kind": "json_field",
         "args": ["results/cn_rev_tilt/p1_results.json",
                  "g1_prime_v2.REV60_bare.pass_v2", "False"]},
        {"kind": "file_contains",
         "args": ["results/runnable_pool.json", "R248 bm-a deterministic harvest"]},
        {"kind": "git_log_file",
         "args": ["fleet/tasks/T-2026-09-26-73-P1.json", "CN-REV-TILT"]},
    ],
})

with io.open(P, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(d, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
print("row T-73-CN-REV-TILT-P1 appended; items =", len(items))
