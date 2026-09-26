# r251 bm-a: T-73 progress_r251 insert (slice-2 runner written + pool-submitted;
# prereg R251 zero-run amendment af368f8e precedes any run). Single-writer this round.
import json

P = "fleet/tasks/T-2026-09-26-73-P1.json"
t = json.load(open(P, encoding="utf-8"))
assert "progress_r251" not in t, "already inserted"
t["progress_r251"] = (
    "R251 s3 slice-2 = CN-DIV-LOWVOL-ROT-P1 runner WRITTEN per frozen prereg "
    "(commit af368f8e = R251 ZERO-RUN amendment, precedes any run: T_joint "
    "1861->1862 probe-authoritative count, mismatch day 2021-10-22 = 512890 "
    "share-fold suspension bar per DLP.SPLIT_EVENTS single source, event-guard "
    "leg = DLP._adjust_split post-event price face per r239 pit law; criteria "
    "values untouched). scripts/cn_div_lowvol_rot_p1.py = intersection loader "
    "(T==1862 fail-closed + A-only-window==['2021-10-22'] + B-only empty + "
    "NaN-free) + 4 judged cells {W63,W252}x{bare,MA200-gate} 21d-rhythm "
    "rotation (schedule range(20,T-1,21), argmax RS_W adjusted closes, tie "
    "-> 50/50, gate cells per-leg gate on tie halves, warmup cash-honest) + "
    "K=50 random-leg nulls (seeds 20260980+k in-registry at R250 freeze, x2 "
    "face, W63-bare warmup) + EW-pair/buy-hold baselines (W63-bare anchored) "
    "+ V2 ADV20-tiered cost faces (judge=x2 side_cost_x2 family precedent; "
    "x1 verbatim/x3 tripled disclosure) + 1% ADV DAY-QUEUED fills (sells "
    "before buys, caps from ADV20(t-1), buys lot-rounded with AFFORDABILITY "
    "LOOP (no negative cash -- F3 caught), completion = sells done AND (buys "
    "within one lot OR cash cannot buy one lot), re-anchor supersedes "
    "incomplete transitions fill_days=None honest) + fill_days/notional/"
    "per-year cost disclosures + G1'v2/G2/DSR/CSCV-8 shared library on x2 "
    "+ D6 (REG6 ew6 canon reject face + same-batch + H4 disclosures: "
    "510880-leg face computed, family C1 x2 series unavailable_in_artifact "
    "honest) + hard-bound triad crisis windows 2020-03/2021-02/2024-09..10 "
    "+ regime v3 descriptive column (cn_rev_tilt_p1 imported layer reuse) + "
    "npz checkpoints (date-drift refusal) + finalize census gate (r188) + "
    "append_ledger single-shot + attrition ENTRIES row (r248 law). Selftest "
    "0 FAIL (34 legs; F1 fold-event guard through real DLP path, F2 queue "
    "hand-math incl lot-rounding bite 1900-not-2000 + supersession, F3 "
    "affordability 999k-of-1M + no phantom re-sell, F4 tie/gate-tie, F15 "
    "NaN-ADV conservative defer). LIVE loader probe all_ok on real corpora "
    "(T=1862, fold-boundary adjusted ret -2.26% = real market move not "
    "-51% raw artifact, ADV 2020 median 2.446M matches probe 2.45M). "
    "POOL-SUBMITTED entry 46 CN-DIV-LOWVOL-ROT-P1 ready/divlowvolrot-0of1 "
    "(_r251bma_pool_submit.py). NEXT (harvest round): autofill launches -> "
    "landed marker results/cn_div_lowvol_rot/p1_results.json -> r244 law "
    "pool-flip done + harvest_note + prereg S7/S8 backfill + verdict readout "
    "(4 cells x2 face; prereg s5 predictions reconciliation; bare-vs-EW-pair "
    "zero-increment clause) -> post_review row registration per O-2115/R246 "
    "law -> three-state claim. Remaining s3 slices: CORE-SATELLITE (satellite "
    "leg supply dependency on T-57 survivors = 0/25 honest negative), "
    "REGIME-POLICY (policy-axis s2 research first per research-before-model "
    "law).")
tmp = P + ".tmp"
with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(t, fh, ensure_ascii=False, indent=1)
import os
os.replace(tmp, P)
t2 = json.load(open(P, encoding="utf-8"))
print("progress_r251 inserted, len:", len(t2["progress_r251"]))
