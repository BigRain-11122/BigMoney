"""R285 bm-a: register post_review claim row T-87-REV-OSC-P1 (r282 harvest).

R282 harvest commit a0425122 landed the REV-OSC-STOCK-P1 judgment
(judged-negative all 7 cells, slot closed per O-20260926-2335 s5) but no
post_review criteria row was registered -- the acceptance leg of the
legislated/effective/reviewed triad was open. This registers the row with
checks anchored ONLY on stable product files (D-20260927-04 law: no
hot-ticket-face anchoring, no git_log_file on per-round-appended files).
Same-round reviewer re-run = the verification path.
"""
import io
import json

PATH = "results/post_review_criteria.json"
c = json.load(io.open(PATH, encoding="utf-8"))

new_row = {
    "id": "T-87-REV-OSC-P1",
    "claim": "T-87 s2 first-priority REV-OSC-STOCK-P1 full arc: prereg "
             "frozen commit a7761433 BEFORE runner build 0182a8cf BEFORE "
             "any run (R99 law) + dual-face sentinel zero-run amendment "
             "4ac879f9 (r251 probe-authoritative) + runner selftest 15/15 "
             "+ real-data gate probe (eligible medians 194 full / 1116 "
             "2010+) -> pool entry -> autofill twin launch crash 00:10/"
             "00:20 (d6_block unpack of load_member_rets tuple, zero "
             "judged products, engineering fix 64d1c15c legal per r253 "
             "deterministic-reexec law) -> relaunch 01:00:07 -> harvest "
             "r282 commit a0425122 (beat-face percent-unit defect found+"
             "fixed+re-derived single-count per r253; judged faces "
             "byte-stable) -> verdict NEGATIVE per frozen prereg s4: "
             "G1'v2 0/7 (best BASE x1 0.3831 vs line 13.5951, n_eff "
             "189859; passive_term 0.5606 alone exceeds best cell = "
             "verdict robust to null-term scale; only BASE_BG bootstrap "
             "CI lower bound +0.002 > 0) + G2 0/7 (DSR 0-0.0125 vs 0.95 "
             "gate; family PBO 0.4 in observe band 0.25<pbo<=0.5) + "
             "drawdown descriptive line 7/7 breached -> REV-OSC-STOCK "
             "judged negative, slot closed (O-20260926-2335 s5 "
             "new-evidence-reopen law), no paper account; N_trials=2014 "
             "booked (ledger 187845+2014=189859, attrition row 50); "
             "CEO-presented +20.30%/59.8% claim does not reproduce under "
             "conservative T+1 open-entry proxy + full costs + 25y "
             "panel; deep-bear segment beat 0.5481-0.6220 (6/7 inside "
             "predicted band, all-segment highest) = segment-conditional "
             "descriptive premium only, full-history beat6m 0.44-0.48 "
             "~ coin flip",
    "claim_source": "research/REV_OSC_STOCK_PREREG.md (frozen a7761433 "
                    "precedes runner build precedes any run; s7/s8 "
                    "backfilled R285 single-finalization) + results/"
                    "rev_osc/p1_results.json product + results/"
                    "_r282bma_revosc_harvest.py (deterministic harvest, "
                    "commit a0425122) + results/gate_attrition.json row "
                    "50 + logs/autofill.log execution trail",
    "status": "closed",
    "checks": [
        {"kind": "file_exists", "args": ["scripts/rev_osc_stock_p1.py"]},
        {"kind": "file_exists",
         "args": ["results/rev_osc/p1_results.json"]},
        {"kind": "file_exists",
         "args": ["results/_r282bma_revosc_harvest.py"]},
        {"kind": "file_exists",
         "args": ["research/REV_OSC_STOCK_PREREG.md"]},
        {"kind": "json_field",
         "args": ["results/rev_osc/p1_results.json",
                  "evidence_cutoff", "2026-09-22"]},
        {"kind": "json_field",
         "args": ["results/rev_osc/p1_results.json",
                  "trials_ledger.total", "189859"]},
        {"kind": "json_field",
         "args": ["results/rev_osc/p1_results.json",
                  "gates.BASE.g1_prime_v2.pass_v2", "False"]},
        {"kind": "json_field",
         "args": ["results/rev_osc/p1_results.json",
                  "gates.BASE.g1_prime_v2.sharpe_full", "0.3831"]},
        {"kind": "json_field",
         "args": ["results/rev_osc/p1_results.json",
                  "gates.BASE_BG.g1_prime_v2.bootstrap_ci.ci95_low",
                  "0.002"]},
        {"kind": "json_field",
         "args": ["results/rev_osc/p1_results.json",
                  "family_pbo.pbo", "0.4"]},
        {"kind": "json_field",
         "args": ["results/rev_osc/p1_results.json",
                  "nulls.coverage.n_values", "2000"]},
        {"kind": "json_field",
         "args": ["results/rev_osc/p1_results.json",
                  "virtual_starts.n_starts", "8466"]},
        {"kind": "file_contains",
         "args": ["research/REV_OSC_STOCK_PREREG.md",
                  "REV_OSC-STOCK 判负收线"]},
        {"kind": "file_contains",
         "args": ["results/gate_attrition.json",
                  "REV_OSC_STOCK_P1"]},
    ],
}
assert not any(x["id"] == new_row["id"] for x in c["items"])
c["items"].append(new_row)

with io.open(PATH, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(c, fh, ensure_ascii=False, indent=1)
print("registered T-87-REV-OSC-P1 claim row (items=%d)" % len(c["items"]))
