# -*- coding: utf-8 -*-
"""r879 adopted-window closeout: state heal + heartbeat + round report append (one-shot)."""
import json, time, datetime, io

NOW = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
EPOCH = int(time.time())

# ---- 1. state-bm-a.json (fresh read-modify-write) ----
P_STATE = r'state-bm-a.json'
st = json.load(io.open(P_STATE, encoding='utf-8'))
prev_round = st.get('round_no')
assert prev_round == 877, prev_round  # sequence: 877 closed -> 878 dead -> 879 dead -> this close 879

notes_add = (" r879: double dead-tail adoption (r844 family first double instance) -- r878 session died post-FREEZE-push"
             " (c5eb9d6dd on origin, 3 churn-absorb commits local, no state/report write); r879 session died post-S6+finalize-face"
             " (13:23 n1_w185_results.json landed, no state/report write); this close = 879 composite per r852/r853 heal precedent,"
             " sequence honest 877->878 dead->879 dead->879-close. marks-lane watch (bm-c r758-761) adjudicated = r480 <5bp redundancy"
             " suppression legal (InvisibleRunner rc real-propagated, 13:35 task run rc=0 = suppressed-not-failed; 13:39:01 healthy"
             " tick landed) -- watch closed, no lane defect.")
st['notes'] = (st.get('notes') or '') + notes_add
st.update({
    'round_no': 879, 'round': 879, 'loop_round': 879,
    'last_round': 879, 'last_round_at': NOW, 'last_round_ts': NOW,
    'last_round_closed': NOW, 'last_seen': NOW, 'updated': NOW, 'ts': NOW, 'last_run': NOW,
    'clock_read': NOW,
    'heartbeat_epoch_utc': EPOCH, 'last_heartbeat_epoch_utc': EPOCH,
    'last_orders_sha': '1ce71b36e8144fce478b806892b0c1ced94ffc75cdf1670dcaca2bd6db3dc298',
    'last_orders_at': NOW,
    'last_decisions_sha': 'ee70cef0f4a5e3b8db4c67936ce2a2aeee222fff8d03f33339b390eac814ac8c',
    'last_decisions_seen': ('r879: DEC ee70cef0 UNCHANGED zero action; ORD d7d3a73e->1ce71b36 consumed'
                            ' (rows 282-289 all BigStream MV lane, zero BigMoney dispatch; mid-window re-delta'
                            ' 157adbd1 re-scanned same verdict); watermark keys moved to consumed tip'),
    'last_orders_seen': ('r879: ORD delta rows 282-289 (12:2x unity-package feed / MV 9th-12th addenda /'
                          ' three-wave merge receipts / D-BS-20261008-10 v2 verdicts / v2 sample delivery) all BigStream'
                          ' MV domain -- zero bm-a lane dispatch; unacked=0; inbox 0'),
    'current_task': 'W185 finalize closure (adopted window) -> next: W186 prereg buildgen chain',
    'now_active': 'W185 closed end-to-end (burn 12/12 + finalize + sec7/8 backfill + push df0e28a8a); engine idle awaiting W186',
    'last_action': 'r879 composite closeout (double dead-tail adoption r844 law): W185 sec7/8 mechanical backfill + rebase storm resolve + delivery',
    'did': ('r879 composite (dead r878 freeze+ignition + dead r879 S6 41/41+finalize adopted): this leg = sec7/8 backfill'
            ' (machine-read asserts) + E42 writer-pause rebase (14 UU: ALL_FACES resolve x6 + twins take-:3 x8 + attrition UNKNOWN'
            ' manual take-new 13:25:16) + push df0e28a8a + reconcile (5 zero-drift, compute_audit observation-phase drift logged)'
            + ' + marks-lane watch adjudicated (r480 <5bp suppression legal) + quartet green + ORD/DEC dual-consumed'),
    'next': ('W186 chain (r874 bloodline): probe projection re-derive (naive-B-inside-naive-A forced re-derive note,'
             ' staircase 46th pending universe recheck) -> prereg buildgen -> freeze five-face insertions -> tick self-ignite;'
             ' post-15:30 new-bar window: live.paper + paper family + REGIME_GUARD v3 enforce + marks settle face;'
             ' VL measured leg = O-1850 arrears still held'),
    'verify': ('sec7/8 backfill asserts PASS (ledger 812,128+2,200=814,328 EXACT / K=404,920 / mu -0.092852 / sigma 0.245090'
               ' / se_mu 0.000385 / K-lift -0.0001 / A p95 0.3066 / audit.finalize_only true / 12 shards)'
               ' + smoke 49/49 + not-at-origin=0 (df0e28a8a) + attrition CLEAN + orphan face=0 + quartet green'),
    'latest_artifact': 'results/perpetual_faces/n1_w185_results.json (W185 finalize, ledger 814,328 / K 404,920 / K-lift -0.0001)',
    'last_artifact': 'results/perpetual_faces/n1_w185_results.json (W185 finalize, ledger 814,328 / K 404,920 / K-lift -0.0001)',
    'idle_rounds': 0, 'agenda_starved': False,
})
io.open(P_STATE, 'w', encoding='utf-8', newline='').write(json.dumps(st, ensure_ascii=False, indent=1))
chk = json.load(io.open(P_STATE, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int) and chk['round_no'] == 879
print('state OK round 879, epoch int', chk['heartbeat_epoch_utc'])

# ---- 2. heartbeat fleet/machines/bm-a.json ----
P_HB = r'fleet\machines\bm-a.json'
hb = json.load(io.open(P_HB, encoding='utf-8'))
hb.update({
    'last_seen': NOW, 'ts': NOW, 'clock_read': NOW,
    'heartbeat_epoch_utc': EPOCH,
    'current_task': 'W185 finalize closed (r879 adopted window); next W186 prereg buildgen',
    'cores': 32, 'free_ram_gb': 59.6, 'total_ram_gb': 93.6, 'gpu_free_vram_mib': 8684,
    'verdict': 'loaded_ok',
    'idle_rounds': 0, 'agenda_starved': False,
    'round_no': 879,
})
io.open(P_HB, 'w', encoding='utf-8', newline='').write(json.dumps(hb, ensure_ascii=False, indent=1))
chk2 = json.load(io.open(P_HB, encoding='utf-8'))
assert isinstance(chk2['heartbeat_epoch_utc'], int)
print('heartbeat OK epoch int', chk2['heartbeat_epoch_utc'])

# ---- 3. round report append (binary append, UTF-8; tail probe CRLF) ----
P_RR = r'round_reports-bm-a.md'
raw = open(P_RR, 'rb').read()
crlf = raw.endswith(b'\r\n')
line = (
NOW + ' | r879 | bm-a | dept:研究-永续线+工程/舰队 | '
'WM-VERDICT: 绿 (red=false lane=healthy; engine ALIVE rc0 idle queue-0 post-W185; next_pick=moneyflow IC claimed=advisory only) | '
'当前活=W185 finalize 收口复合窗 (r844 双死腿收养: r878 死腿=freeze 五面+自燃+3 吸收提交; r879 死腿=S6 41/41 rc0+finalize 落件 13:23; 本腿=§7/§8 机械回填+rebase 风暴解+送达) | '
'最近实物=results/perpetual_faces/n1_w185_results.json (13:23, W185 finalize: 账本 812,128+2,200=814,328 EXACT 零投影差 / K=404,920 / merged mu -0.092852 / sigma 0.245090 / se_mu 0.000385 链面 W182..W185 0.000388→0.000385 / K-lift -0.0001 四预键 4/4 PASS / A p95 0.3066 Δ-0.0128 门过 / canon flip NOT performed) + research/PERPETUAL_N1_W185_PREREG.md §7/§8 回填 (13:3x, W184 血统镜像·机读零手抄·回填窗注记=r879 死会话收养窗非漏补窗) | '
'下个里程碑=W186 prereg buildgen (r875 probe 投影 A 423_804..425_803 / B 424_004..424_203 naive-B-inside-naive-A 强制重 derive 注记+阶梯第 46 例待注册宇宙复核·r874 血统链, 窗≤今晚) + 15:30 后新 bar 窗 live.paper+纸盘族+REGIME_GUARD v3 enforce | '
'did: S0-1 身份锚定 bm-a+孤儿面=0 (28 py faces); S0 push 拒→E42 静窗 (4 写盘任务 pause→残面吸收→rebase 6/7 撞 14 UU→分类器 13 分类+1 UNKNOWN→ALL_FACES resolve 6 面 (compute_audit 18 行 union·regime_state·update_status·lhb·futures·token_usage) +孪生族 8 件 :3 取新 (REPORT/LIVE 四胞胎同侧 13:24:53>13:20:10·fundamental_b_layer 13:24:16>13:19:37·attrition 扫描件 UNKNOWN 手工裁定=取新 13:25:16>13:22:18 双侧同形同判 active_loss=false)→continue 7/7→push df0e28a8a→reconcile 5 面零漂移+compute_audit 观察相漂移照录→4 任务恢复; S0.5 双扫=本地 51 令零未回执+inbox 0; 集团水位 DEC ee70cef0 UNCHANGED 零动作 / ORD d7d3a73e→1ce71b36 消费 (delta 行 282-289 全 BigStream MV 车道零 BigMoney 派单·中窗 157adbd1 再 delta 复扫同谳·水位键取消费 tip); S1 smoke 49/49; S2 板空 (job_list 0+tasks 全 claimed 零开放)+idle --worked 清零; S3 引擎 ALIVE rc0 idle; S6 未重跑 (r879 死腿 13:20 41/41 rc0=15min 前面·白跑律·采集器 pre-15:30 合法 no-op·诚实披露); marks lane 观察 (bm-c r758-761 遗留)定谳=r480 <5bp 冗余抑制门合法抑制 (InvisibleRunner rc 真传播·13:35 任务跑 rc=0=抑制非失败)+13:39:01 健康落行复证=观察闭合; S7 四件套绿 (loop pin=8 no-op / watchdog 13:42 重注 / 双爪 CR-normalized 重装) | '
'验证=commit df0e28a8a (rebase 后) + not-at-origin=0 (push 后 fetch 自证) + §7/§8 机读断言全过 (账本恒等式/K/mu/sigma/se_mu/K-lift/A p95/audit.finalize_only/12 shards 全 assert) + attrition 双侧 CLEAN + 孤儿面=0 + heartbeat epoch-int 自证 | '
'孤儿面=0 | 本地未达 origin commit 数=0 (收尾 push+fetch 自证) | '
'下轮指针: ① W186 prereg buildgen (r874 血统·W185 finalize 锚=814,328/K 404,920/p95 0.3066 键面·naive-B-inside-naive-A 强制重 derive+阶梯第 46 例复核)→freeze 五面插录→tick 自燃 ② 15:30 后新 bar 窗: live.paper+纸盘族+REGIME_GUARD v3 enforce+marks settle 面 ③ VL 实测腿=O-1850 欠账仍挂'
)
with open(P_RR, 'ab') as f:
    if not raw.endswith(b'\n'):
        f.write(b'\r\n')
    f.write(line.encode('utf-8') + (b'\r\n' if crlf else b'\n'))
print('round report appended, line', len(line), 'chars; crlf-tail =', crlf)
