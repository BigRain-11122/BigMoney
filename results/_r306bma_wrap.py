# -*- coding: utf-8 -*-
# r306 bm-a S7 wrap: round report line + state 306 + heartbeat update.
import json
import time
from datetime import datetime

NOW = datetime.now().astimezone()
NOW_ISO = NOW.isoformat()
NOW_STR = NOW.strftime("%Y-%m-%d %H:%M:%S")

# --- round report (append one line) ----------------------------------------
REPORT = ("logs/iteration-loop/round_reports-bm-a.md")
line = (
    f"\n{NOW_ISO} | R306 bm-a (dept:工程·舰队+研究供给) | WM first-line verdict: "
    "red=false lane healthy (probe 08:44 py_low_board_clear n=5 avg 0.3% legal: "
    "pool takeable=0 = self-claimed mkneutral burn in flight + board zero open + "
    "bandit 0; supply line ACTIVE = queue #5 burning same round) | did: "
    "(A) 08:40:08 tick LAUNCH VERIFIED: CN-MKTNEUTRAL-P1 claim+fire pid 19684 "
    "(latency 18.9min honest = R305 registration-defect window; workers_plan fix "
    "220be63b held) -- burn completed ~7min vs est 30-120min (vector-width+monthly "
    "rebalance actuals far lighter, honest no-retro-estimate-edit) | "
    "(B) HARVEST full chain r302-law-first: done-flip BEFORE analysis (pool entry+"
    "shard done + result_ref, _r306bma_mkneutral_flip.py) -> judged 4/4 NEGATIVE "
    "(x2 Sharpe 0.4975/0.5577/0.4680/0.4802 vs own-null lines 0.6834/0.6862 "
    "(null_term, mu_null 0.3752>0.3 = s5.1 ENG FLAG FIRED -> post-flag beta/"
    "accounting audit CLEAN: caps both-side binding, fallbacks 2 window-start, "
    "margin peak 14.7-16.8% in budget, NAV identity 42/42 -> drift attribution = "
    "mechanism face, verdict independent of attribution) / 0.5606 (passive_term); "
    "CI95 low -0.107..-0.182 all <=0; DSR <=0.0021; family PBO 0.9286; batch face "
    "cells_ok 4/4 TRUE (ann +4.7-5.9%/OOS both positive/maxDD -21.5..-25.4%/no "
    "crash year) = 'positive returns but does not cross own-null calibrated line' "
    "semantics; D6 vs ew6 <=0.1196 zero reject, intra 0.753-0.942; x1>x2 4/4 "
    "erosion 17-29%; robust sign-flip p 0.098-0.157 ns; virtual starts 2,026 "
    "(bull 416/deep_bear 6 insufficient honest) beat6m 0.41-0.44 <0.5; ledger "
    "204,445+2,004=206,449 exact) -> s7/s8 single-finalization (7-prediction "
    "reconciliation: p2/p3/p6/p7 hit, p1 half+flag, p2b cost-erosion 17-29% vs "
    "30-60% MISS, p4 maxDD vs >=-15% MISS but -30% failure line not hit) -> "
    "row-16 market-neutral judged-closed with REV-TILT standing ('increment "
    "positive != magnitude crossing') -> post_review criteria T-87-CN-MKTNEUTRAL-"
    "P1 24 frozen-value checks (first run NO x3 = my 2-arg json_field vs sectldr "
    "3-arg precedent shape error, caught+fixed same round -> YES=40 NO=0) -> "
    "T-87 ticket CLOSED s1-s4 (queue #1-#5 ALL judged-negative, ZERO survivors "
    "-> T-85 fusion pool ZERO intake, s4 honest zero-supply cross-ref) -> "
    "SCHOOL ledger row + attrition row (runner self-landed 08:42:59, entries "
    "column face r248) | "
    "(C) INFRA: autofill submit contract gate mechanized (r301+r305 trio assert: "
    "submit subcommand runner-on-disk+shards+workers_plan, duplicate-id refuse, "
    "atomic os.replace, no-git single-writer; selftest +S17a-f 6 new legs 48/48 "
    "ALL PASS; live CLI refusal probe exit 2 zero pool write; S17f kenglu in-"
    "family: repo-real runner path makes _runner_alive match the selftest process "
    "itself -> tempdir fixture law) | "
    "(D) S6 30/30 rc=0 (_r306bma_s6_chain.ps1 Copy-Item r305 lineage + difflib "
    "delta=round-face only r298; Sunday legal no-bar, collectors honest no-ops; "
    "ORANGE shadow breadth 0.77; market_clock ORANGE_COOL; audit pool-supply-gap "
    "non-flag; daily_report faces=4 token=1; token L2 legs 0) | "
    "(E) S7: push-collision x1 window (bm-b r311 same-window): 2 UU resolved "
    "union zero-loss (compute_audit history 201+203->204 shared-200 +1/+3; "
    "x2_watch 600+600->606; _r306bma_resolve.py = r311-lineage resolver Copy-Item "
    "whole-file REPO-path-face-only per r298; parse-verify r185 in-resolver; "
    "rebase --continue clean; both pushes landed bc4774b3 + ca587d95); schtasks "
    "alive (loop Running next 08:58 + watchdog Ready 09:20 per R49 schtasks-not-"
    "CIM law); inbox zero unprocessed; S0.5 both-scans 96/96 orders zero unacked "
    "+ decisions zero new rows (D-20260927-04 BigMoney face = self-correct-"
    "maintain standing honored); smoke 25/25; CODELY 9,494B <10KB hard line no "
    "append (submit-gate completion log fails memory gate-4q by design) | "
    "NEXT: R307 = supply-line face after queue exhaustion: external digest "
    "(O-1721 dual-frequency) or PLAN.md P0-P4 lane; watch moneyflow rank-pass "
    "self-heal + ah_panel refresh completion; T-89/T-90 bm-b lanes untouched "
    "(anti-dup standing)")
with open(REPORT, "a", encoding="utf-8") as fh:
    fh.write(line)

# --- state file --------------------------------------------------------------
st = json.load(open("state-bm-a.json", encoding="utf-8-sig"))
st["round_no"] = 306
st["last_round"] = 305
st["did"] = ("R306: CN-MKTNEUTRAL-P1 launch verified 08:40:08 + burn ~7min + "
             "HARVEST full chain (done-flip first r302; judged 4/4 NEGATIVE; "
             "row-16 closed with REV-TILT; s5.1 eng flag fired->audit clean; "
             "s7/s8 single-finalization; post_review criteria 24 checks YES; "
             "T-87 CLOSED s1-s4 queue #1-#5 5/5 negative zero survivors->T-85 "
             "zero intake) + autofill submit contract gate (trio assert, S17a-f "
             "selftest 48/48) + S6 30/30 + push-collision 2 UU union zero-loss "
             "(r311-lineage resolver)")
st["verdict"] = "ok"
st["next"] = ("R307: supply-line face (queue exhausted -> external digest "
              "O-1721 or PLAN.md lane); watch moneyflow rank-pass self-heal + "
              "ah_panel refresh; T-89/T-90 bm-b lanes untouched")
st["current_task"] = "R306 done: mkneutral judged closure + T-87 closed + submit gate"
for k in ("ts", "last_round_ts", "updated_at", "last_run", "last_round_at",
          "updated", "last_seen"):
    st[k] = NOW_ISO.replace("+", "+") if k == "ts" else NOW_ISO
st["task"] = "R307: supply-line face (digest O-1721 / PLAN lane)"
with open("state-bm-a.json", "w", encoding="utf-8") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)

# --- heartbeat ---------------------------------------------------------------
import psutil
hb = json.load(open("fleet/machines/bm-a.json", encoding="utf-8-sig"))
hb["last_seen"] = NOW_ISO
hb["clock_read"] = NOW_ISO
hb["heartbeat_epoch_utc"] = int(time.time())
hb["current_task"] = st["current_task"]
hb["task"] = st["task"]
hb["round_no"] = 306
hb["cpu_pct"] = psutil.cpu_percent(interval=1)
hb["free_ram_gb"] = round(psutil.virtual_memory().available / 1e9, 1)
vm = psutil.virtual_memory()
hb["free_ram_mb"] = round(vm.available / 1e6)
hb["idle_ram_gb"] = hb["free_ram_gb"]
hb["verdict"] = "ok"
with open("fleet/machines/bm-a.json", "w", encoding="utf-8") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)

chk = json.load(open("fleet/machines/bm-a.json", encoding="utf-8-sig"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock ISO face"
print("state round_no:", st["round_no"], "| hb epoch:", chk["heartbeat_epoch_utc"],
      "| clock:", chk["clock_read"], "| cpu:", chk["cpu_pct"],
      "| ram free GB:", chk["free_ram_gb"])
