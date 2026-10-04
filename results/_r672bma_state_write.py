# r672 bm-a state write-back (programmatic json dump + strict loads self-verify, r645 law)
import json, io, time, datetime

SP = r"state-bm-a.json"
st = json.load(io.open(SP, encoding="utf-8"))

now_local = datetime.datetime.now().astimezone()
now_iso = now_local.strftime("%Y-%m-%dT%H:%M:%S+08:00")
now_short = now_local.strftime("%Y-%m-%d %H:%M:%S")
epoch = int(time.time())

st["round_no"] = 672
st["last_round"] = "r672"
st["last_round_at"] = now_short
st["last_round_ts"] = now_iso
st["last_run"] = now_iso
st["updated"] = now_short
st["heartbeat_epoch_utc"] = epoch

st["did"] = (
    "r672: T-167 THEME-JUDGE-P1 closeout completion (finalize redo-verified idempotent: "
    "attrition single entry 10:26:19 d8004/total 633,981, r259 prev-echo guard live; "
    "TREASURE_REGISTRY judgment-finalize row backfilled = r670 missed closeout leg, "
    "judged_negative family honest closure registered with full readings) + D-19 "
    "decisions/orders both MATCH (per-key sha256 caliber, r458 near-repeat caught by "
    "64-hex length self-evidence; probe _r669bma_d19_check.py + orders diff probes) + "
    "S0.5 orders 153/153 zero-unacked + S0 churn-absorb merge origin 9 commits zero-UU + "
    "S6 37/37 rc0 84.4s (dualrun streak47 ZERO-DRIFT; fund-statement gate live-verified "
    "no-op panel-complete 86x3 after r671 dash-normalize fix; compute_audit flags=[] "
    "CLEAN supply_gap self-resolved; CALL ORANGE_COOL sleeves4; t35 PASS 0 pending; "
    "t24 22/22 promotion 0/22 NOT-ELIGIBLE; golden-week no-op family; live.paper skipped "
    "r660 precedent) + S7 pin8 no-op watchdog re-reg dual claws MATCH attrition CLEAN"
)
st["last_action"] = (
    "r672: THEME-JUDGE-P1 judged_negative closeout completed (treasure row + finalize "
    "idempotent re-verify); round label from round_reports tail (state.last_round was "
    "stale r668 vs reports r670/r671 advanced)"
)
st["current_task"] = (
    "fund trio NULLS bm-b in-flight keepalive (burn-done watch); piece-4 prereg "
    "trio-gated ETA 10-05..09 per DIGEST sec.4; 10-08 market-open run-11/run-7 dual-jump "
    "+ governance day; G-SEG ruling window 10-06..09"
)
st["next"] = (
    "r673: fund trio NULLS burn-done check (10-05 V-NULLS -> trio judged finalize per "
    "rehearsal ALL-GREEN x3, E21 blockers resolved: G-SEG frozen insufficient-sample "
    "path per GM ruling 10-04, VALUE cmd_finalize _passive_window t0 fix owned bm-b); "
    "T-166 panel promotion done-flip verify; 10-06..09 G-SEG ruling window close; "
    "10-08 market-open dual-jump + governance day; W14 GM-parked maintained"
)
st["verify"] = (
    "S1 smoke 48/48; finalize redo idempotent (attrition 1 entry, ledger 633,981); "
    "S6 37/37 rc0 84.4s (_r672bma_s6_log.txt; dualrun streak47); treasure row appended "
    "(TREASURE_REGISTRY tail); D-19 dual MATCH sha256; attrition guard CLEAN 4 ledgers; "
    "state strict json.loads proof + heartbeat epoch int/T-sep proof"
)

with io.open(SP, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
# self-verify (r645 law)
reloaded = json.load(io.open(SP, encoding="utf-8"))
assert reloaded["round_no"] == 672, "round_no write failed"
assert isinstance(reloaded["heartbeat_epoch_utc"], int), "epoch must be int"
print("STATE OK round_no=672 epoch=", reloaded["heartbeat_epoch_utc"],
      "clock=", reloaded["last_round_ts"])
