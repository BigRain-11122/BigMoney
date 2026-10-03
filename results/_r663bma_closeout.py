# r663 bm-a closeout: state writeback + round report line + heartbeat
# (python json.dump + reparse self-proof; PS5.1 CJK ConvertFrom-Json crash pit r662)
import json, time, subprocess, datetime

NOW = datetime.datetime.now()
TS = NOW.strftime('%Y-%m-%dT%H:%M:%S+08:00')
EPOCH = int(time.time())

# --- CPU/RAM sample via probe-free approach (wmic-free: use psutil if present) ---
cpu_pct, free_ram, gpu_free = 0.0, 0.0, 0.0
try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=1.0), 1)
    free_ram = round(psutil.virtual_memory().available / (1024**3), 1)
except Exception:
    pass

# --- state writeback: round_no 663 -> 664, r663 record ---
state_fp = r'state-bm-a.json'
with open(state_fp, 'r', encoding='utf-8') as f:
    st = json.load(f)
st['round_no'] = 664
st['did'] = ("r663 dead-session estate adopted per r471/r656 + fund-statement collector live-crash fix: "
             "prior r663 session (claimed T-166 06:5x, launched backfill 07:14) died pre-commit 07:2x "
             "(process gone, bookkeeping untouched); products verified (selftest ALL-PASS, probe 6/6, spec, ticket) "
             "and adopted; backfill had crashed at cashflow:20080630 (pd.NaT strftime ValueError, 7/258 "
             "face-periods landed) -- root-caused + fixed in norm_avail_date (NaT->None) + selftest F5 "
             "regression leg + relaunch re-fired at gate throttle expiry 07:44 (checkpoint resume). "
             "S6 37 legs rc0 zero-fail (dualrun ZERO-DRIFT streak39; audit CLEAN; CALL ORANGE_COOL; "
             "LIVE/REPORT/scorecard/dashboard CEO faces refreshed); pool face settled via mlv.sync_face "
             "internal API after r437 checkout replay (r661 precedent); D-19 dual-face MATCH via raw-bytes "
             "probe (PS join-string hash fake-CHANGED caught live = r660 third-family instance); orders "
             "double-scan 152/152 zero-unacked; attrition CLEAN 4 ledgers; inbox zero-unread.")
st['verify'] = ("S1 smoke 48/48 (incl fund-statements selftest row); collector selftest rc0 + py_compile ok "
                "+ NaT regression leg; S6 37/37 rc0 elapsed 81.2s (_r663bma_s6_log.txt); S7 4/4 machinery "
                "(loop pin8 no-op + watchdog re-registered + pre-commit/pre-push claws MATCH); heartbeat "
                "epoch int + clock T self-proof; state strict json.loads PASS")
st['next'] = ("T-166 backfill in-flight watch (251 face-periods remaining, ~2.5s throttle cadence, completion "
              "-> panel complete -> T-166 done-flip); 10-05 V-NULLS burn-done window -> fund trio judged "
              "finalize (rehearsal ALL-GREEN x3 stands); 10-08 market-open window run-11/run-7 dual-jump + "
              "governance-day acceptance; G-SEG ruling window 10-06..09 (no GM ruling -> insufficient-sample)")
st['last_round_at'] = TS
st['current_task'] = ("r663 done: dead-session adoption + fund collector NaT fix + backfill relaunched; "
                      "next=T-166 backfill watch + 10-05 V-NULLS finalize watch")
st['updated'] = NOW.strftime('%Y-%m-%d %H:%M:%S')
st['last_round_ts'] = TS
st['heartbeat_epoch_utc'] = EPOCH
with open(state_fp, 'w', encoding='utf-8') as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
with open(state_fp, 'r', encoding='utf-8') as f:
    json.load(f)

# --- heartbeat writeback ---
hb_fp = r'fleet\machines\bm-a.json'
with open(hb_fp, 'r', encoding='utf-8') as f:
    hb = json.load(f)
hb['last_seen'] = TS
hb['current_task'] = st['current_task']
hb['cpu_pct'] = cpu_pct
hb['free_ram_gb'] = free_ram
hb['heartbeat_epoch_utc'] = EPOCH
hb['clock_read'] = TS
with open(hb_fp, 'w', encoding='utf-8') as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
with open(hb_fp, 'r', encoding='utf-8') as f:
    rhb = json.load(f)
assert isinstance(rhb['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
assert 'T' in rhb['clock_read'] and ' ' not in rhb['clock_read'], 'clock must be T-separated ISO8601'

# --- round report line ---
line = (
    "watermark: green (red=false; satengine alive rc0 queue 0; pool floor 3/3 no breach -- fund trio NULLS "
    "bm-b canonical in-flight keepalive; compute_audit CLEAN flags=[]; probe insufficient_history golden-week "
    "window no violation face) | " + TS + " | r663 | dept:\u6570\u636e+\u5de5\u7a0b | "
    "\u5f53\u524d\u6d3b: \u6b7b\u4f1a\u8bdd\u9057\u4ea7\u6536\u517b (r471/r656 \u5f8b) + \u8d22\u62a5\u4e09\u9762\u91c7\u96c6\u5668\u5b9e\u5f39\u5d4c\u6b7b\u4fee\u590d "
    "(T-166-P1 fund \u6570\u636e\u817f\u7ebf\u7eed) -- \u524d\u4f1a\u8bdd 06:5x \u8ba4\u9886\u5f00\u5de5 07:14 \u5206\u79bb\u540e\u7ae0\u540e\u7a8f\u6b7b "
    "\u96f6\u63d0\u4ea4 (\u8fdb\u7a0b\u96f6+\u7c3f\u8bb0\u672a\u52a8\u4e09\u8bc1\u63a2\u5b9e) -> \u672c\u8f6e\u6536\u517b: \u9a8c\u8bc1\u5168\u90e8\u4ea7\u54c1 "
    "(selftest ALL-PASS + probe 6/6 + spec + \u7968\u9762) \u540e\u53d1\u73b0 backfill \u5b9e\u5f39\u5d29\u6b7b @cashflow:20080630 "
    "\u300cValueError: NaTType does not support strftime\u300d (pd.NaT \u662f datetime \u5b50\u7c7b -> \u8fdb\u4e86 strftime \u5206\u652f; "
    "7/258 face-periods \u5df2\u843d\u5730 checkpoint \u5b8c\u597d) -> \u5f53\u8f6e\u4fee\u590d norm_avail_date "
    "(NaT->None \u5982\u5b9e\u7f3a\u5e2d) + selftest F5 \u56de\u5f52\u817f (pd.NaT->None \u65ad\u8a00) + \u95f8\u95e8 07:44:11 "
    "\u8fc7\u671f\u540e\u91cd\u53d1 (checkpoint \u7eed\u62c9) | S0: r437 \u51c0\u8def (21 \u4ea4\u96c6\u9762 origin-blob \u9884\u5bf9\u9f50 -> merge "
    "FF \u96f6\u51b2\u7a81) + \u6c60\u9762\u91cd\u653e\u540e mlv.sync_face \u5185\u90e8 API settle (r661 \u5148\u4f8b) ; D-19 \u53cc\u9762 MATCH "
    "eb14b510/82a0cef9 (raw-bytes \u63a2\u9488; PS join \u4e32\u54c8\u5e0c\u5047 CHANGED \u5f53\u573a\u81ea\u6108 = r660 \u5f8b\u7b2c\u56db\u5b9e\u4f8b) | "
    "\u9a8c\u8bc1\u8bc1\u636e: S1 smoke 48/48; collector selftest rc0 + py_compile + NaT \u56de\u5f52\u817f; S6 37/37 "
    "\u817f rc0 81.2s \u96f6\u8d25 (_r663bma_s6_log.txt; dualrun ZERO-DRIFT streak39; CALL ORANGE_COOL "
    "sleeves4 activated0; LIVE-20261004+REPORT-20261004+daily_scorecard+dashboard \u5168\u5237\u65b0; t35 PASS 0 "
    "pending; t24 22/22 \u664b\u5347\u95e8 0/22 \u5408\u6cd5 NOT-ELIGIBLE; \u91d1\u5468\u91c7\u96c6\u817f\u5168\u5408\u6cd5 no-op \u65e5); orders "
    "\u53cc\u626b 152/152 \u96f6\u672a\u56de\u6267; attrition CLEAN 4 \u53f0\u8d26 (healed \u6ce8\u8bb0\u7167\u5f55); inbox \u96f6\u672a\u8bfb; S7 4/4 "
    "(loop pin8 no-op + watchdog \u91cd\u6ce8 + \u53cc\u94a9 CR \u5f52\u4e00 MATCH) | \u8bb0\u5206: 2 (\u53ef\u8dd1\u91c7\u96c6\u5668+\u4fee\u590d+\u91cd\u53d1 "
    "=\u5b9e\u7269\u4ea7\u54c1; \u6536\u517b\u9762\u5982\u5b9e\u7559\u75d5) | \u8bb0\u8d26\u9884\u7b97: 4/5 (state+\u5fc3\u8df3+\u8f6e\u62a5+\u7968\u9762) | "
    "\u672c\u5730\u672a\u8fbe origin commit \u6570: 0 (\u6536\u5c3e commit \u5373\u63a8+\u63a8\u540e fetch+rev-parse \u81ea\u8bc1) | "
    "ceo-visibility: [\u5f53\u524d\u6d3b] \u57fa\u91d1\u9762\u6570\u636e\u5e95\u5ea7\u91c7\u96c6\u5668\u5d4c\u6b7b\u4fee\u590d\u5e76\u91cd\u65b0\u5f00\u8dd1 (\u8d22\u62a5\u4e09\u9762 2005Q1..\u4eca "
    "258 \u671f\u6279\u91cf\u56de\u586b\u5728\u98de) [\u6700\u8fd1\u5b9e\u7269] scripts/update_fund_statements.py "
    "(\u91c7\u96c6\u5668+NaT \u4fee\u590d+selftest) + research/shortline/FUND_STATEMENT_PANEL.md + "
    "data/fund_statement_export/_staging 7 \u671f parquet \u5df2\u843d\u5730 | [\u4e0b\u4e2a\u91cc\u7a0b\u7891] T-166 \u56de\u586b\u8dd1\u5b8c "
    "->\u9762\u677f\u5b8c\u5907\u7ffb\u7968 (10-05..06); 10-05 V-NULLS \u70e7\u5b8c -> fund \u4e09\u65cf judged finalize "
    "(\u9884\u6f14 ALL-GREEN x3 \u5c31\u7eea); 10-08 \u5f00\u5e02\u7a97 run-11/run-7 \u53cc\u8df3"
)
with open(r'round_reports-bm-a.md', 'a', encoding='utf-8', newline='') as f:
    f.write(line + '\n')

print(f'state round_no={st["round_no"]} epoch={EPOCH} cpu={cpu_pct} free_ram={free_ram}')
print('round report line appended; all writes reparse-verified')
