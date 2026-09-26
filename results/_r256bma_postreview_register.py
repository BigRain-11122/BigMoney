"""R256 bm-a: post_review check-rot reconciliation + new claim row.

P0 (reviewer NO row): T-73-CN-REV-TILT-P1 git_log_file check rotted --
sliding -5 window on fleet/tasks/T-2026-09-26-73-P1.json, a hot file
receiving per-round progress appends (R250/251/252/255/256 pushed the
R248 harvest commit d8be0cb8 out of the window). The underlying fact
HOLDS (d8be0cb8 verified in file history this round); the encoding was
defective. Fix = Tools/post_review.py git_log_file optional depth arg
(legacy default 5 preserved, selftest ALL PASS) + row reconciled to
depth 30 + documented note. Zero criteria invented: the reconciled
check verifies the SAME pre-frozen fact (R248 delivery commit exists).

Also registers the R256 claim row T-73-CN-REGIME-POLICY-P1 (R246 law:
same-round registration; checks reference only pre-frozen prereg faces
+ artifact existence/consistency, never post-hoc fabricated).
"""
import io
import json
import time

PATH = "results/post_review_criteria.json"
c = json.load(io.open(PATH, encoding="utf-8"))

row = [x for x in c["items"] if x["id"] == "T-73-CN-REV-TILT-P1"][0]
git_checks = [ck for ck in row["checks"] if ck["kind"] == "git_log_file"]
assert len(git_checks) == 1, "unexpected shape"
ck = git_checks[0]
assert ck["args"][:2] == ["fleet/tasks/T-2026-09-26-73-P1.json",
                          "CN-REV-TILT"]
if len(ck["args"]) == 2:
    ck["args"].append(30)          # durable depth (r256 reconciliation)

c["_reconciled"] = (c.get("_reconciled") or "").rstrip() + (
    f"\n - {time.strftime('%Y-%m-%d %H:%M')} r256 bm-a: T-73-CN-REV-TILT-"
    "P1 git_log_file check reconciled to depth 30 (optional-depth arg "
    "added to Tools/post_review.py git_log_file, legacy default 5 kept, "
    "selftest ALL PASS). Root cause = check-rot: sliding -5 window on a "
    "hot ticket file receiving per-round progress appends (R250/251/252/"
    "255/256 appends pushed the R248 harvest commit d8be0cb8 out of "
    "window). Fact verified true pre-reconciliation (d8be0cb8 in file "
    "history); zero criteria invented, same pre-frozen fact re-encoded "
    "durably. Reviewer re-run same round = the re-derive-to-green path.")

new_row = {
    "id": "T-73-CN-REGIME-POLICY-P1",
    "claim": "T-73 s3 slice-3 CN-REGIME-POLICY full arc: s2-sliceB digest "
             "prior-research obligation -> design decision (scope-down "
             "face: policy axis never an alpha slot, P4B={4,7,10,12} "
             "defensive risk-condition x0.5 only) -> prereg frozen R256 "
             "commit 124b360c BEFORE any run (R99 law) + probe facts "
             "frozen (510300 corpus 3483 bars, v3 full-cover, ADV20 cap "
             "margin 3.8x) -> runner selftest 18/18 -> pool entry ready "
             "16:17:58 -> autofill launch (28.7s, 993 units, zero RNG "
             "exhaustive nulls) -> landed p1_results.json with "
             "trials_ledger (prev 186592 + 993 = 187585) -> deterministic "
             "harvest _r256bma_rp_harvest.py PASS -> verdict NEGATIVE "
             "per frozen prereg: A-face policy-axis-value FALSE (full "
             "Sharpe 0.23 < 0.2998; OOS 0.3547 > 0.348 and maxDD "
             "-0.3195 < -0.3713 pass but the 3-condition AND fails on "
             "full Sharpe), B-face month-set signal FALSE (P4B "
             "improvement -0.0698, one-sided p=0.7798 within 495 "
             "exhaustive, family A range 0.1299..0.4196), C-face 0/3 "
             "G1'v2 (best v3_base 0.2998 < line 0.5691; mu_null 0.2777 "
             "sigma_null 0.0591 n_eff 186595) -> G2 ineligible -> "
             "CN-REGIME-POLICY judged negative, no paper account, "
             "family slot closed (third CN-native negative; "
             "new-evidence-reopen law applies)",
    "claim_source": "research/CN_REGIME_POLICY_PREREG.md (frozen R256 "
                    "commit 124b360c, precedes any run; A/B/C faces "
                    "defined pre-burn in s4) + results/"
                    "cn_regime_policy_probe.json (probe facts frozen at "
                    "freeze commit) + results/_r256bma_rp_harvest.py "
                    "(deterministic harvest gate, exit 0) + results/"
                    "cn_regime_policy/p1_results.json product",
    "status": "closed",
    "checks": [
        {"kind": "file_exists", "args": ["scripts/cn_regime_policy_p1.py"]},
        {"kind": "file_exists",
         "args": ["results/cn_regime_policy/p1_results.json"]},
        {"kind": "file_exists",
         "args": ["results/_r256bma_rp_harvest.py"]},
        {"kind": "file_exists",
         "args": ["research/CN_REGIME_POLICY_PREREG.md"]},
        {"kind": "json_field",
         "args": ["results/cn_regime_policy/p1_results.json",
                  "evidence_cutoff", "2026-09-22"]},
        {"kind": "json_field",
         "args": ["results/cn_regime_policy/p1_results.json",
                  "trials_ledger.total", "187585"]},
        {"kind": "json_field",
         "args": ["results/cn_regime_policy/p1_results.json",
                  "n_trials", "993"]},
        {"kind": "json_field",
         "args": ["results/cn_regime_policy/p1_results.json",
                  "a_face_model_question.policy_axis_value", "False"]},
        {"kind": "json_field",
         "args": ["results/cn_regime_policy/p1_results.json",
                  "b_face_month_set_signal.signal_A", "False"]},
        {"kind": "json_field",
         "args": ["results/cn_regime_policy/p1_results.json",
                  "g1_prime_v2.v3_base.pass_v2", "False"]},
        {"kind": "json_field",
         "args": ["results/cn_regime_policy/p1_results.json",
                  "g1_prime_v2.v3_policy.pass_v2", "False"]},
        {"kind": "json_field",
         "args": ["results/cn_regime_policy/p1_results.json",
                  "g1_prime_v2.policy_only.pass_v2", "False"]},
        {"kind": "file_contains",
         "args": ["results/runnable_pool.json",
                  "R256 bm-a deterministic harvest"]},
    ],
}
assert not any(x["id"] == new_row["id"] for x in c["items"])
c["items"].append(new_row)

with io.open(PATH, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(c, fh, ensure_ascii=False, indent=1)
print("reconciled git_log_file depth + registered "
      "T-73-CN-REGIME-POLICY-P1 claim row")
