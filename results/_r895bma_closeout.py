# r895 bm-a closeout: round report append + state rewrite + heartbeat rewrite.
# Encoding laws: report = UTF-8 append w/ CRLF tail probe (r843/r844); state/heartbeat = JSON int epoch (R170/R178).
import json, time, datetime

NOW = datetime.datetime.now().astimezone()
NOW_ISO = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())
R = 895

# ---- leg 1: round report append (ROOT canonical face per r844 law) ----
row = (
 f"2026-10-09T02:31:00+08:00 | r895 | bm-a | dept:research/engine (perpetual line W191 finalize closeout; dead-tail composite per r844/r888: adopted r895 S0 dead-session e8dddd37c + probe artifacts) | "
 "WM-VERDICT: green (red=false lane healthy; engine ALIVE rc0 idle queue 0; next_pick moneyflow IC claimed=advisory panel-source-blocked) | "
 "当前活: r895 收口 (孤儿面=0·26 py faces; W191 finalize 落账+回填+推送完成·引擎 idle) | "
 "最近实物: results/perpetual_faces/n1_w191_results.json @ origin ecf0d3446 (02:1x; K 418,120·ledger 831,336+2,200=833,536 EXACT·audit bm-a) + research/PERPETUAL_N1_W191_PREREG.md §7/§8 回填 @同 commit | "
 "下个里程碑: CODELY 主件超帽 mini-split (30,922B>30,720B·下轮首件) + W192 五面=bm-c 席在飞 bm-a 让路 (窗 ≤48h) | "
 "did: S0-1 锚定 bm-a+孤儿探针 0 + S0=死会话 e8dddd37c 收编已落 (half-open rebase 解决+pool_core_samples union 2190|2191->2193+saturated history 01:27->01:30 恢复+W191 shard-10/11 verbatim 恢复+01:39 引擎活面吸收·zero-loss asserted) 本窗续尾: S0.5 双扫 0 未回执 (54/191)+DEC/ORD 水位零变化 (83813196/861949ca) + S1 smoke 49/49 + 主产出=W191 finalize 收口: 死会话六门 pre-finalize 探针收编 (G1 Σ2200/G2 half-open tiling/G3 seed continuity A 435004..437003 B 437004..437203/G4 output absent/G5 no live proc/G6 head 831,366) GREEN_FINALIZE_READY → 本窗复核=materializer 02:02 已自动落账 (ledger 块在嵌套 science_gates.ledger r459 面·顶层读 NO block 近失一腿: pit-95+finalize_already_landed 嵌套面源码读核双拦·盲跑未发生) → 账本 831,336+2,200=833,536 EXACT (vs §5 冻结投影 827,528 差 +6,008=bm-b r807 fund_trio 追加式重锚 r518 活链头消费律·§7 披露非改判据) + K=418,120 EXACT + §5 四预键机证全过 (mu gap 0.0030<0.02/sigma +0.0065%<10%/A p95 Δ-0.0019<0.05/K-lift +0.0001≤0.02·line 1.1871→1.1872) → n1 selftest PASS (default wave r522 律) → §7/§8 机器回填 (_r895bma_w191_sec78_backfill.py·六门数字直读断言) → attrition CLEAN (4 ledgers·healed 注记照录) → commit+push ecf0d3446 送达 → S6 39 腿全绿 (r892 driver 滚一代 r895·panel 10-08 cutoff·盘前 no-op 族·bad_legs NONE·205s 量级) → idle_trigger --worked 清零 (idle_rounds 0/agenda_starved false) | "
 "W192 席位让路: bm-c 席 MSG-20261008-2351 已发布 (A 437_204..439_203 staircase FIFTY-SECOND/B 439_204..439_403 own-A W141 leg2·re-derive 已由 bm-c 预席探针兑现 r587 never-transcribe) — 本机 r894 state 'next' 的 W192 seat chain 指针作废·bm-c r787 在飞·bm-a 不碰 (协同反重复铁律) | "
 "实物: ①n1_w191_results.json+prereg §7/§8 @ ecf0d3446 (上面) ②results/_r895bma_s6_chain.json (39 腿 bad NONE) ③results/_r895bma_w191_prefinalize_probe.json (死会话六门探针收编) + _r895bma_w191_sec78_backfill.py + _r895bma_s6_driver.py (r892 滚一代) ④坑律直写 research/pit-engine-finalize.md (materializer 嵌套面判定 1,138B·r666 直写例外=主件超帽) | "
 "验证: smoke 49/49 + n1 selftest PASS + S6 39 腿 bad NONE + attrition CLEAN + 孤儿面=0 (26 py faces) + engine ALIVE idle queue 0 + 四件套绿 (loop pin=8 next-fire 02:28/watchdog next-fire 02:27/双爪 PRESENT LF-norm) + orders unacked=0 (轮首+S7 双扫) + 本地未达 origin commit 数=0 (push 后 fetch+rev-list 自证) + token: L1 零 API | "
 "下轮指针: ①CODELY.md 主件 30,922B>30,720B 超 202B (本窗零 append·前窗他机增量所致) mini-split 候选=下轮首件 ②W192 五面 bm-c 席在飞 (bm-a 让路·只读监控) ③W193 席 chain 待 bm-c W192 落地后 (W193+ 投影: naive A 439_204..441_203/B 439_404..439_603·W192-B-refuses-W193-A staircase FIFTY-THIRD 预告) ④GM bm-b reroute decision watch [via bm-a r895]"
)
with open('round_reports-bm-a.md', 'ab') as f:
    t = open('round_reports-bm-a.md', 'rb').read()
    if t and not t.endswith(b'\r\n') and not t.endswith(b'\n'):
        f.write(b'\r\n')
    f.write(row.encode('utf-8') + b'\r\n')
print('report appended', len(row.encode('utf-8')), 'bytes')

# ---- leg 2: state rewrite (preserve untouched fields) ----
SP = 'state-bm-a.json'
s = json.load(open(SP, encoding='utf-8'))
s['round_no'] = R
s['round'] = R
s['loop_round'] = R
s['last_round'] = R
s['last_round_at'] = NOW_ISO
s['last_round_closed'] = NOW_ISO
s['last_round_ts'] = NOW_ISO
s['last_run'] = NOW_ISO
s['last_seen'] = NOW_ISO
s['ts'] = NOW_ISO
s['updated'] = NOW_ISO
s['clock_read'] = NOW_ISO
s['heartbeat_epoch_utc'] = EPOCH
s['last_heartbeat_epoch_utc'] = EPOCH
s['current_task'] = "r895 closed: W191 finalize landed+backfilled+pushed (ecf0d3446); engine idle queue 0; W192 five-face = bm-c seat in-flight (bm-a yields)"
s['did'] = ("r895 dead-tail composite: adopted r895 S0 dead-session (e8dddd37c) + carried finalize closeout: materializer 02:02 auto-finalize discovered via nested science_gates.ledger face (top-level read near-miss, pit-95+source-read double-verified), "
            "ledger 831,336+2,200=833,536 EXACT (delta +6,008 vs freeze projection = bm-b r807 fund_trio reanchor, r518 live-head law, sec7 disclosed), K=418,120 EXACT, sec5 four keys all PASS, "
            "prereg sec7/sec8 machine backfill, n1 selftest PASS (default wave), attrition CLEAN, commit+push ecf0d3446, S6 39-leg full green (r892 driver rolled r895), idle --worked cleared")
s['last_artifact'] = "W191 finalize products on origin ecf0d3446 (n1_w191_results.json K 418,120 ledger 833,536 + prereg sec7/8 backfill)"
s['latest_artifact'] = s['last_artifact']
s['next'] = ("CODELY main 30,922B>30,720B cap mini-split (first item next round; this window zero main-file appends, overage pre-existing from other-machine entries) + W192 five-face = bm-c seat in-flight bm-a yields (W193 chain waits W192 landing; W193+ projection naive A 439_204..441_203 / B 439_404..439_603, staircase FIFTY-THIRD anticipated) + GM bm-b reroute watch")
s['now_active'] = "r895 closed: W191 finalize landed (ledger 833,536, K 418,120); engine idle; perpetual line caught up through W191"
s['verify'] = ("smoke 49/49 + n1 selftest PASS (default wave) + S6 39-leg bad NONE (r895 driver, panel cutoff 10-08) + attrition CLEAN (4 ledgers) + orphan face=0 (26 py faces) + engine ALIVE idle queue 0 + "
               "S7 quartet green (loop pin=8 next-fire 02:28 / watchdog next-fire 02:27 / pre-commit+pre-push claws PRESENT) + orders unacked=0 (double-scan) + DEC/ORD watermarks unchanged (83813196/861949ca) + local-vs-origin 0/0 self-verified")
s['last_orders_seen'] = "r895: ORD 861949ca unchanged both scans (round-first + S7); all 54 files acked (orders_ack 191)"
s['last_decisions_seen'] = "r895: DEC 83813196 unchanged both scans; zero new dispatch rows"
s['last_orders_at'] = NOW_ISO
s['last_decisions_at'] = NOW_ISO
s['last_action'] = "r895 composite closeout: finalize products push ecf0d3446 + state/report/heartbeat writes"
s['idle_rounds'] = 0
s['agenda_starved'] = False
with open(SP, 'w', encoding='utf-8', newline='') as f:
    json.dump(s, f, ensure_ascii=False, indent=1)
print('state rewritten round', R)

# ---- leg 3: heartbeat rewrite (epoch int, T-sep clock) ----
HB = 'fleet/machines/bm-a.json'
h = json.load(open(HB, encoding='utf-8'))
h['last_seen'] = NOW_ISO
h['ts'] = NOW_ISO
h['clock_read'] = NOW_ISO
h['heartbeat_epoch_utc'] = EPOCH
h['last_heartbeat_epoch_utc'] = EPOCH
h['current_task'] = "r895 closed: W191 finalize landed+pushed (K 418,120 ledger 833,536); W192=bm-c seat in-flight"
h['idle_rounds'] = 0
h['agenda_starved'] = False
h['verdict'] = "green"
if 'sync' in h and isinstance(h['sync'], dict):
    h['sync']['last_sync_at'] = NOW_ISO
    h['sync']['behind_origin'] = 0
with open(HB, 'w', encoding='utf-8', newline='') as f:
    json.dump(h, f, ensure_ascii=False, indent=1)
chk = json.load(open(HB, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
assert 'T' in chk['clock_read'] and ' ' not in chk['clock_read'], 'clock_read must be T-separated'
print('heartbeat written; epoch int verified', chk['heartbeat_epoch_utc'])
