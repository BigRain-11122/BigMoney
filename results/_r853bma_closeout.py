# _r853bma_closeout.py -- r853 closeout writer: state heal (851->852->853 per r841 precedent),
# round_reports-bm-a.md appends (r852 dead-tail adoption line + r853 line, UTF-8 per r843 law),
# heartbeat nine-fields update (epoch int R170/R178 law, clock_read T-separator R262 law).
import json, io, time, datetime, os, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now_iso = datetime.datetime.now().isoformat(timespec='seconds')
now = now_iso + '+08:00'
epoch = int(time.time())

# ---------- 1. state-bm-a.json heal ----------
SP = os.path.join(REPO, 'state-bm-a.json')
st = json.load(io.open(SP, encoding='utf-8'))
prev_epoch = st.get('heartbeat_epoch_utc')
st.update({
    'current_task': 'r853 closed: OSS ledger S3/S4/S5 scan (10-09 deadline met 1 day early, 15 rows + evidence rc0); W180 engine self-burn in flight (8/12 at closeout, finalize next round)',
    'did': ('r853: dead-tail adoption (r852 session post-push crash 01:02:53 before state/report write; state heal 851->852->853 per r752+r841; report line adopted from origin commits 220a7b305/8cf4fced3/568848aa4) '
            '+ S0 FF origin (2 behind; 13 stale shared faces discarded origin-newer per ts-newer canon; writer-pause E42; unique lane faces absorbed zero loss) '
            '+ S0.5 orders 51/51 unacked=0 + DEC/ORD ee659451/2bb2ee75 identical python-canonical zero-action '
            '+ S1 smoke 48/48 + OSS S3/S4/S5 scan (ledger section 六: S3 funnel 6 / S5 sentiment 5 / S4 knowledge 4; vibe-astock=REGIME-5 candidate#1; 404-cure law appended CODELY 30,606B) '
            '+ S6 38/38 rc0 (dualrun streak 51) + S7 quartet green + attrition CLEAN + idle --worked'),
    'last_action': 'OSS ledger S3/S4/S5 sealed (research/OSS_HARVEST_LEDGER.md 六; vibe-astock REGIME-5 supply candidate #1); W180 burn shard 8/12 engine-owned',
    'latest_artifact': 'research/OSS_HARVEST_LEDGER.md (section 六) + results/oss_eng_scan/s345-20261008.json @2026-10-08T01:2x',
    'last_artifact': 'research/OSS_HARVEST_LEDGER.md (section 六) + results/oss_eng_scan/s345-20261008.json @2026-10-08T01:2x',
    'next': ('r854: W180 12-shard completion -> one-pass finalize (canon single-pass; anchor W179 finalize head 799,705 K 391,720) '
             '+ OSS admission experiment ticket (S5-01 vibe-astock REGIME-5 probe first, then S3-02 PyPortfolioOpt, S3-01 gplearn) '
             '+ 10-08 15:30 market-reopen data chain re-arm (all gates + REGIME_GUARD v3 enforce) '
             '+ O-1850 VL co-residence reading + CEO order files advance (P-audit 10-12 / R-research+REGIME-5 10-14)'),
    'round': 853, 'round_no': 853, 'last_round': 'r853', 'loop_round': 'r853',
    'heartbeat_epoch_utc': epoch, 'last_heartbeat_epoch_utc': prev_epoch,
    'clock_read': now, 'ts': now, 'updated': now, 'last_seen': now, 'last_run': now,
    'last_round_at': now, 'last_round_ts': now, 'last_orders_at': now,
    'verify': ('smoke 48/48; S6 38/38 rc0 streak 51; attrition CLEAN; orders 51/51; quartet 4/4; engine alive W180 8/12; '
               'OSS scan rc0 3-round evidence; DEC/ORD identical zero-action; not-at-origin=0 post-push self-check'),
    'now_active': 'r853 closed (OSS S3/S4/S5 done early; W180 burn in flight); r854 = W180 finalize watch + admission tickets + 15:30 reopen re-arm',
    'notes': st.get('notes', '') + (' r853: state heal 851->852->853 (r852 died post-push before state write; sequence honest per round_reports lines; '
             'S0 13 stale shared faces discarded origin-newer, unique lane faces absorbed). CODELY 404-cure line appended 30,606B line held.'),
})
with io.open(SP, 'w', encoding='utf-8') as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
assert isinstance(json.load(io.open(SP, encoding='utf-8'))['heartbeat_epoch_utc'], int)
print('state healed 851->853, epoch', epoch)

# ---------- 2. round_reports-bm-a.md appends ----------
RP = os.path.join(REPO, 'round_reports-bm-a.md')
rb = io.open(RP, 'rb').read()
rt = rb.decode('utf-8', 'replace')
r852 = ('2026-10-08T01:02:53+08:00 | r852 bm-a (dept:research) | [DEAD-TAIL ADOPTED at r853 per r752 three-gate + r841 heal precedent -- session died post-push before state/report write] '
        'watermark verdict: green | 当前活: W180 FREEZE five-face registry insertions (pf N1_BANDS[180]+n1 WAVE_CONFIGS[180]+W180 materializer+PASS-claim; buildgen r849-bloodline 173 pairs AST-carried; '
        'A 410_804..412_803 staircase 40th / B 412_804..413_003 W141 leg2; seat d3b0737fe pre-freeze r565) + churn absorb + r835 rebase-cure leg + S6 38-leg rc0 (streak 51) '
        '| 最近实物: origin commits 220a7b305/8cf4fced3/568848aa4 | 下个里程碑: W180 engine self-burn -> finalize (carried into r854)\r\n')
r853 = (now + ' | r853 bm-a (dept:research) | watermark verdict: green (red=false lane=healthy; next_pick=claimed moneyflow IC batch parked source-blocked 30-min self-heal -- 等待对象一行声明不重扫) '
        '| 当前活: r852 dead-tail adoption (state heal 851->852->853) + OSS ledger S3/S4/S5 补扫收口 (O-2245 @bm-a 承接·10-09 deadline met 1 day early: S3 awesome-quant funnel 6 rows / S5 情绪因子 5 rows / S4 聚宽掘金知识 4 rows; '
        'vibe-astock=REGIME-5 情绪工具供给候选#1 Apache-2.0 净; 手写库全名 404 三连=search-by-name 实证治愈) + S6 38/38 rc0 (dualrun streak 51) + W180 burn engine-owned monitored (8/12 at closeout) '
        '| 最近实物: research/OSS_HARVEST_LEDGER.md 六 + results/oss_eng_scan/s345-20261008.json (rc0) @01:2x '
        '| 下个里程碑: W180 12-shard finalize r854 (canon one-pass, ≤48h) + 10-08 15:30 开市首 bar 数据链 re-arm (REGIME_GUARD v3 enforce 全门) '
        '| 本地未达 origin commit 数=0 (post-push fetch 自证) | 孤儿面=1 (round-zero probe read-only, no kill) '
        '| orders 51/51 unacked=0; DEC ee659451/ORD 2bb2ee75 双零动作; smoke 48/48; attrition CLEAN; quartet 4/4; idle --worked\r\n')
nt = rt + r852 + r853
with io.open(RP, 'wb') as f:
    f.write(nt.encode('utf-8'))
print('report lines appended:', nt.count('r853 bm-a (dept:research)'), 'r853 lines;')

# ---------- 3. heartbeat fleet/machines/bm-a.json ----------
HP = os.path.join(REPO, 'fleet', 'machines', 'bm-a.json')
hb = json.load(io.open(HP, encoding='utf-8'))
try:
    import psutil
    cpu = psutil.cpu_percent(interval=1)
    ram_free = round(psutil.virtual_memory().available / (1024 ** 3), 1)
except Exception:
    cpu, ram_free = hb.get('cpu_total_pct', 0), hb.get('ram_free_gb', 0)
hb.update({
    'machine_id': 'bm-a', 'round_no': 853, 'round': 853, 'loop_round': 'r853', 'last_round': 'r853',
    'current_task': 'r853 closed: OSS S3/S4/S5 scan sealed; W180 burn in flight (8/12); r854=W180 finalize + admission tickets + 15:30 reopen re-arm',
    'task': 'OSS ledger S3/S4/S5 scan (done) + W180 engine burn monitoring', 'now_active': st['now_active'],
    'last_action': st['last_action'], 'latest_artifact': st['latest_artifact'],
    'next_milestone': 'W180 finalize r854 (≤48h); 10-08 15:30 reopen data-chain re-arm',
    'verdict': 'green', 'idle_rounds': 0, 'agenda_starved': False,
    'heartbeat_epoch_utc': epoch, 'last_heartbeat_epoch_utc': prev_epoch,
    'clock_read': now, 'ts': now, 'last_seen': now, 'last_run': now,
    'cpu_total_pct': cpu, 'ram_free_gb': ram_free, 'health': 'ok',
})
with io.open(HP, 'w', encoding='utf-8') as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
chk = json.load(io.open(HP, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int) and 'T' in chk['clock_read']
print('heartbeat updated: epoch', epoch, 'int OK; clock T-sep OK; cpu', cpu, 'ram_free', ram_free)
