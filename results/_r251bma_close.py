# r251 bm-a close: round report line + state + heartbeat (S7)
import json
import time

NOW = time.strftime("%Y-%m-%d %H:%M")
EPOCH = int(time.time())

REPORT = "logs/iteration-loop/round_reports-bm-a.md"
line = (
    f"{NOW} | R251 | [wm:probe py_low_board_clear (14:39 sample py 0.0-0.3%, open=0 bandit=0 no local "
    "batch; pool_ready=2 = supply lane healthy, watchdog fills; audit CLEAN flags=[] pool-supply-gap] | "
    "did: S0 pull-rebase already-up-to-date clean; S0.5 BOTH scans zero-diff (orders 82/82 ack) + "
    "decisions mtime 12:07 unchanged zero new rows; S1 smoke 25/25; S2 job_list 2 jobs both this round "
    "+ fleet board 81 tickets 0 open no collision; S3 MAIN = T-73 s3 slice-2 CN-DIV-LOWVOL-ROT-P1 "
    "FULL WRITE CYCLE: (1) prereg R251 ZERO-RUN AMENDMENT commit af368f8e PRECEDES ANY RUN (R246 "
    "precedent window): T_joint 1861->1862 = probe joint_bars authoritative (mismatch day 2021-10-22 "
    "is 510880-only, ALREADY outside the intersection; freeze draft double-deducted the off-by-one; "
    "live recount intersection=1862) + narrative fix (2021-10-22 = 512890 share-fold SUSPENSION bar "
    "per DLP.SPLIT_EVENTS single source 1.639->0.801 ratio 2.0449, not a data gap) + event-guard leg "
    "(RS/returns/MA200 on DLP._adjust_split post-event face per r239 pit law; ADV20 raw volume x "
    "close fold-continuous) -- criteria values untouched, zero results zero runs at amendment; "
    "(2) runner scripts/cn_div_lowvol_rot_p1.py = intersection loader fail-closed (T==1862 + "
    "A-only-window==['2021-10-22'] + B-only empty + NaN-free + cutoff lockbox) + 4 judged cells "
    "{W63,W252}x{bare,MA200-gate} 21d-rhythm rotation (schedule range(20,T-1,21), argmax RS_W on "
    "adjusted closes, tie->50/50, gate cells per-leg gate on tie halves, warmup cash-honest) + "
    "K=50 random-leg nulls (seeds 20260980+k in-registry at R250 freeze, x2 judged face, W63-bare "
    "warmup) + EW-pair/buy-hold baselines + V2 ADV20-tiered cost faces (judge=x2 side_cost_x2 family "
    "precedent, x1 verbatim/x3 tripled) + 1%-ADV DAY-QUEUED fills (sells before buys, caps from "
    "ADV20(t-1), lot-rounded buys with AFFORDABILITY LOOP -- negative-cash bug caught by F3 first "
    "run, fixed with per-lot step-down; completion = sells done AND (buys within one lot OR cash "
    "cannot buy one lot) -- cash-exhausted terminal caught by F3 second run; re-anchor supersedes "
    "incomplete transitions fill_days=None honest) + fill_days/notional/per-year-cost disclosures + "
    "G1'v2/G2/DSR/CSCV-8 shared library on x2 + D6 (REG6 ew6 canon reject + same-batch + H4 "
    "disclosures: 510880-leg face computed, family C1 x2 series unavailable_in_artifact honest) + "
    "hard-bound triad crisis windows 2020-03/2021-02/2024-09..10 + regime v3 descriptive column "
    "(cn_rev_tilt_p1 imported layer) + npz ckpt (date-drift refusal) + census gate r188 + "
    "append_ledger single-shot + attrition ENTRIES row (r248 law); selftest 34 legs 0 FAIL after "
    "3 real fixture-defect self-catches (F2 lot-rounding bite 1900-not-2000 hand-math, F3 "
    "negative-cash phantom re-sell + terminal-state, F15 NaN-ADV defer) -- pit entry CODELY; LIVE "
    "loader probe all_ok on real corpora (T=1862, fold-boundary adjusted ret -2.26% = real market "
    "move not -51% raw artifact, ADV20 512890 2020 median 2.446M matches probe 2.45M); "
    "(3) POOL-SUBMITTED entry 46 CN-DIV-LOWVOL-ROT-P1 ready/divlowvolrot-0of1 + T-73 progress_r251 "
    "exact resume pointer; commit 43635ace; | S3 SECONDARY = T80 battery lane verification (R250 "
    "pointer item 1): 14:30 tick LAUNCHED (R250 unblock live-verified: weight-sha/canon-census/grid/"
    "passive-agreement gates all PASS, sleeves 28x2 in 11s) then ANCHOR GATE REFUSED fail-closed "
    "(AGGR-CONC-TOP2.w_cur != frozen aggressive_lab.json: got x1 ret 0.040724 vs want 0.043774, "
    "n_days 177==177 -- engineering drift, zero partial products) + 14:40 tick fuse_refused same-sha "
    "relaunch (no crash-loop burn); suspect face = R250 machine-local re-derivations (canon assembly "
    "+ dA re-run, byte-compare vs bm-b originals unavailable -- disclosed R250); actions = pool entry "
    "lane-status note (no other machine burns blind) + inbox MSG-20260926-1500-bm-a to bm-b (T-80 "
    "owner) with 3 adjudication paths (TRANSFER originals / bm-c canon cross-check / re-freeze anchor "
    "vs reproducible basis); bm-a touched ZERO of bm-b's frozen battery faces (anti-dup law); | S6 "
    "25 legs ALL exit 0 (Saturday no-ops: daily 0 rows cutoff 09-24, regime ORANGE d2 shadow #10 "
    "breadth 0.77, clock ORANGE_COOL idempotent regen cell sleeves=2, lhb 30min throttle, heat "
    "weekend, futures/options/sina_mf/ths zero-network, moneyflow spawn-throttle 25.7min, AH spawn "
    "throttle 25min, fp bm-c lane, fundamental 17.2h fresh, blf verdict written, live.paper+t35_fill+"
    "t24_prospect 3 new-bar legs legitimately skipped Saturday, promotion 0/22 legal, aggr marks "
    "idempotent, alloc bm-b lane, grid no-bar, export 09-24 traders=6, scorecard 6, report 4 faces "
    "token=1, build_status 10f/432/6traders milestones 5/7, token L2 1 leg local ~6135) | evidence: "
    "commits af368f8e + 43635ace + selftest 0 FAIL output + live loader probe + pool entry 46 + "
    "autofill log 14:30/14:40 traces + S6 exit codes in transcript | next: (1) 14:50 tick may "
    "launch CN-DIV-LOWVOL-ROT-P1 -> harvest next round per r244 landed-marker law (pool flip + "
    "harvest_note + prereg S7/S8 backfill + verdict readout + post_review row registration per "
    "O-2115); (2) T80 anchor-gate adjudication = bm-b's call (MSG sent, 3 paths); (3) s3 remaining "
    "slices CORE-SATELLITE (supply dependency honest) / REGIME-POLICY (policy-axis s2 research first); "
    "(4) 09-28 Monday new-bar chain; (5) 10-01 month-boundary trio + REGIME_GUARD v3 date gate; "
    "(6) T-70 verdict window 10-09"
)
with open(REPORT, "a", encoding="utf-8", newline="\n") as fh:
    fh.write(line + "\n")

# state
S = "state-bm-a.json"
s = json.load(open(S, encoding="utf-8"))
s["round_no"] = 251
s["did"] = ("R251: T-73 s3 slice-2 CN-DIV-LOWVOL-ROT-P1 runner written per frozen prereg "
            "(selftest 0 FAIL/34 legs; prereg R251 zero-run amendment af368f8e T_joint 1862 + "
            "fold-suspension narrative + event-guard precedes run) + pool entry 46 ready; T80 "
            "battery 14:30 launch verified past R250-unblocked gates then ANCHOR GATE refused "
            "(engineering drift, fuse blocks re-burn, MSG to bm-b); S6 25 legs exit 0")
s["verdict"] = "GREEN"
s["next"] = ("watchdog launch -> ROT harvest per r244 (flip+S7/S8 backfill+verdict+post_review); "
             "T80 anchor adjudication bm-b; s3 CORE-SAT/REGIME-POLICY next; 09-28 new-bar chain; "
             "10-01 month trio + v3 date gate; T-70 10-09")
s["ts"] = NOW
s["updated_at"] = NOW
s["current_task"] = ("R251 done: slice-2 runner+selftest+pool-submit (entry 46); T80 anchor-gate "
                     "refusal documented+delegated; next=ROT harvest + remaining s3 slices")
tmp = S + ".tmp"
with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(s, fh, ensure_ascii=False, indent=1)
import os
os.replace(tmp, S)

# heartbeat
H = "fleet/machines/bm-a.json"
h = json.load(open(H, encoding="utf-8-sig"))
h["last_seen"] = NOW
h["current_task"] = s["current_task"]
h["task"] = s["current_task"]
h["verdict"] = "alive"
h["heartbeat_epoch_utc"] = EPOCH
h["clock_read"] = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
h["round_no"] = 251
import psutil
h["cpu_pct"] = round(psutil.cpu_percent(interval=1), 1)
h["free_ram_gb"] = round(psutil.virtual_memory().available / 1e9, 1)
try:
    import torch
    free, _total = torch.cuda.mem_get_info(0)
    h["gpu_free_vram_gb"] = round(free / 1e9, 1)
except Exception:
    pass
tmp = H + ".tmp"
with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(h, fh, ensure_ascii=False, indent=1)
os.replace(tmp, H)

# self-verify epoch is JSON int (R170/R178 law)
h2 = json.load(open(H, encoding="utf-8-sig"))
assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
print("round report + state r251 + heartbeat written; epoch int OK:",
      h2["heartbeat_epoch_utc"], "| cpu", h2["cpu_pct"], "| ram free",
      h2["free_ram_gb"])
