# r266 bm-b: T-76 progress_r266 append -- five-face probe first (raw bytes from HEAD blob,
# never via PS redirect per R255 law), then mirror exactly. Assert diff gate = field-level.
import json, subprocess

P = "fleet/tasks/T-2026-09-26-76-P1.json"

# --- probe: raw bytes straight from git (subprocess capture, no PS pipe) ---
blob = subprocess.run(["git", "show", "HEAD:" + P], capture_output=True, check=True).stdout
assert not blob.startswith(b"\xef\xbb\xbf"), "BOM face changed"
assert b"\r\n" in blob, "EOL face changed (expected CRLF)"
assert blob.endswith(b"\n"), "tail-newline face changed (expected trailing LF)"
head_txt = blob.decode("utf-8")
d0 = json.loads(head_txt)
# indent face: count leading spaces on the second non-empty line of HEAD blob
lines = head_txt.split("\r\n")
ind = len(lines[1]) - len(lines[1].lstrip(" "))
assert ind == 1, f"indent face = {ind}, expected 1"
assert "\\u" not in head_txt[:400], "ensure_ascii face changed"

# --- append (mirror: no-BOM / CRLF / tail newline / indent=1 / ensure_ascii=False) ---
d = json.loads(head_txt)
d["progress_r266"] = (
    "R266 bm-b wave-10 deep-read candidate #1 CLOSED: arXiv 2609.27051 'Propose, Don't Judge: "
    "Anytime-Valid Referee for LLM Factor-Mining Agents' FULL-TEXT adjudication (abs page + HTML "
    "full text, 37pp, Qu/Chen/Wang). VERDICT: A-grade methodology lead MAINTAINED with details "
    "now verified; for us = evaluation/science-gates existing-family (T-63/T-02 chain) external "
    "empirical reinforcement, zero new family; CONSUMPTION ROUTE FROZEN = science_gates "
    "methodology face, any adoption requires fresh prereg from PREREG_TEMPLATE.md (zero adoption "
    "zero wiring zero engine zero ledger this round per no-chain-adoption law). Core recipe "
    "extracted: (1) e-process daily betting W=prod(1+lambda_s*X_s) on post-submission daily "
    "rank-IC, predictable aGRAPA stakes capped phi=0.8, Ville inequality -> anytime-valid at any "
    "stopping time; wait is information-bounded T~ln(Nv/(k*alpha))*2*sigma^2/mu^2 (delta-edge "
    "factor ~1434 days, no better bettor shortens); (2) AR(1) whitening REQUIRED (raw stream "
    "false-admits 6.0%/15.4% at rho=0.2/0.4 vs nominal 5%, whitened restores 1.8-2.4%); (3) "
    "online e-BH over frozen universe Nv=2000 slots, k-th admission bar Nv/(k*alpha)=40000 first, "
    "FDR<=alpha at every stopping time under arbitrary dependence, admissions never revoked, "
    "near-copy resubmission only spends proposer slots (attacking hidden-retry extracts +0.027 "
    "false admissions/submission ONLY from leaky referees, zero from frozen); (4) e-detector "
    "retirement = daily-restarted counter-betting e-processes sum, ARL guarantee A*=1260, median "
    "delay 204-322d, stake targets design alternative full-decay (fitting healthy drift = linear "
    "M~t climb = all-hands false alarms); (5) delta=2c*TO/kappa with kappa-bar=0.018 market "
    "constant (per-sleeve estimation INVERTS shelving decisions -- first pass shelved 77% vol "
    "sleeves wrongly), family break-evens differ by an ORDER OF MAGNITUDE (value 0.010 vs "
    "short-horizon reversal 0.074) -> single delta=0.015 is a signal-quality floor not economic "
    "threshold (paper's own honesty note = our prereg threshold-design warning); (6) execution "
    "neutrality Prop.2 (book recomputable from append-only log at zero cost). RECEIPTS for our "
    "law stack: frozen referee admits 5-11x fewer false admissions than leaky referees "
    "(peeking/adaptive-threshold/no-gate) and NO proposer closes the gap (synthetic 0.00 vs "
    "0.26-0.85/submission; CSI-500 10y 11.7 vs 86-196/campaign) = external A-grade evidence for "
    "our frozen-criteria/no-peeking/no-tuning-to-pass architecture; Prop.1 four conditions "
    "(predictable lambda / post-submission-only data / frozen universe per epoch / no "
    "foretelling) map one-to-one onto our prereg-freeze-commit / OOS-blind / seed-registry / "
    "no-future-data laws = already satisfied; GAP FACE flagged honestly: our paper-lane "
    "per-round readouts (T-24 monthly hr gate, x2-watch F3 escalation) = high-frequency reads "
    "on frozen windows = anytime-valid upgrade CANDIDATE (not violation: gate values frozen); "
    "horizon lesson 8.7: daily-IC certificate structurally cannot certify slow factors "
    "(momentum IC 0.001@1d -> 0.009@63d) and the bar favors the statistically-strongest-per-day "
    "family with the WORST net economics (reversal) -> certify the horizon that is traded = "
    "third-party validation of our per-family fixed-window G1'v2 design; wait-scaling law "
    "T~2*sigma^2/mu^2 legitimizes our 6-month PROSPECT window at blend-level sigma (much lower "
    "than single-factor daily IC 0.12) but flags structural shortness if a daily-IC-level "
    "pipeline ever opens; LLM role boundary: proposer yield beats script (6/6), matches bandit, "
    "unique add = self-authored diagnostic probes (3/6 families significant, never worse, "
    "probes never enter statistical tests) -> J13 lane boundary verdict: propose+diagnose "
    "faces only, judging forever belongs to frozen science_gates. Leverage-law due diligence: "
    "single market, no held-out beyond walk-forward, LLM arms are replay not guarantee "
    "instances (knowledge-cutoff face paper-disclosed), portfolio layer is instrument not "
    "strategy (alpha t<1 all groups, no borrow fee, kappa-bar in-sample input, DSR understates "
    "search). Future prereg starting points ranked: (a) e-value companion readout column on "
    "paper sleeves (no frozen-gate touch) (b) per-family delta=2c*TO/kappa economic threshold "
    "law (c) e-detector retirement face at factor-sleeve layer. Deliverable = "
    "research/digests/DIGEST-20260926-wave10-referee-deepread-2609-27051.md; funnel: deep-read "
    "1/1 closed, adoption 0, new family 0"
)
out = json.dumps(d, ensure_ascii=False, indent=1)
out = out.replace("\n", "\r\n") + "\n"
raw_new = out.encode("utf-8")
open(P, "wb").write(raw_new)
print("progress_r266 appended; bytes:", len(raw_new))
