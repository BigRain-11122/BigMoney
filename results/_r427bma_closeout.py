# r427 bm-a: round report line + state bump + heartbeat update (atomic, UTF-8 no BOM)
import json, time, datetime

# 1) round report line (S5) -- first field set carries WM verdict per S3 law
ts = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S+08:00')
line = (
    ts + ' | R427 bm-a (dept:工程+研究+舰队) | '
    'WM:绿（red=false·py 尾 2.9/0.5/4.4 低位但板清+W8 泊位=bm-b 下轮冻结步的波间合法 idle·audit supply_floor 旗=常设面池 ready 0）| '
    'did: S0 三步抢救律首例全走通——轮首脏树（11:58 崩溃轮 S6 遗产）stash push -u→pull 快进→pop 撞 17 UU=6 ALL_FACES merge_lane_views resolve'
    '（全取 :2: origin 新侧·compute_audit history union 211 行）+11 twin/snapshot take-new origin 新侧（_r427bma_s0salvage_resolve.py 深探针·孪生同侧字节拷）'
    '+reconcile all faces ZERO-DRIFT；W7 双跑收敛核验=checkpoint 逐字节恒等+verdict 唯一差异 generated 戳→stash 全内容已落地或证冗余零丢失 drop；'
    '坑律一百零五批固化+CODELY 水位整编 10,513→9,219B（批 102/103 verbatim 迁 archive 202609.md『r427 bm-a 窗批』节+合并指针行零删改）；'
    'S0.5 零未回执令+MSG-1211 处置（PLAN L222 已由 bm-c r216 补翻在树✓本机零双翻；f9890dfd 在链与其消息自述内容已落 da44b8b11 两面并真=batch-102 律已载非笔误回执）；'
    '集团决策回执 C-20260929-01/02/03（01/02 涉本仓面=api_reason token_meter L75 在树+consumer_plan 池 schema 在树=合规零动作；03 委员会常设化=非本仓执行面零动作）；'
    'S3 小闭环=PLAN L104 smoke_test.py 翻面（交付物在位+本轮 26/26 实证·pit-104 重 derive 范式）；'
    '孤儿 autostash 审计（09-28 16:49 r398 崩溃窗遗留·stash 内 CODELY 行/MSG 删除面均已被后续轮覆盖=建议 GM 裁处删除·依机队惯例保留原位）；'
    '观察行：dashboard/scorecard/LIVE/REPORT 守卫面 12:19-12:20 生成版经 bm-b r423 风暴合并落 origin（生成器归属从本机视角不可辨·bm-b/bm-c 自查其 guard stdout·确定性再 derive 零科学损失）；'
    '11:58/12:08/12:18 三轮死亡窗实录（11:58 轮跑到 S6 后死=本轮抢救其遗产；12:08/12:18 轮疑死于 S0 脏树 pull 拒=S0 三步法防复发） | '
    'verify: smoke 26/26；S6 37 legs rc=0（dualrun ZERO-DRIFT streak 8/3；regime ORANGE breadth 0.83；clock ORANGE_COOL；t35 PASS 零 pending；t24 22/22 drift 0 promo 0/22；'
    'LIVE-0929 ORANGE cap50 COOL；token L2 0；audit FLAG supply_floor）| '
    'next: W8 冻结步 watch（bm-b 泊位·池回填后 supply_floor 自解）；守卫面生成器归属他机自查回执；10-01 月界首轮三轮（science_audit/monthly_briefing/self_review）+REGIME_GUARD v3 日期门自动激活零手改'
)
with open('logs/iteration-loop/round_reports-bm-a.md', 'a', encoding='utf-8', newline='') as f:
    f.write('\n' + line + '\n')

# 2) state bump (S7)
st = json.load(open('state-bm-a.json', encoding='utf-8'))
st['round_no'] = 427
st['did'] = ('r427: S0 storm-7 stash-pop salvage first-fire (17-UU canon-resolved 6 ALL_FACES + 11 twin/snapshot, '
             'reconcile all faces zero-drift; W7 dual-run convergence proven checkpoint-bit-identical + verdict delta=generated-only '
             '-> salvage stash zero-loss dropped) + batch-105 + CODELY waterline 10,513->9,219B (batches 102/103 verbatim to archive) '
             '+ MSG-1211 processed (L222 already flipped by bm-c r216, zero double-flip) + C-20260929-01/02/03 receipts (in-tree compliant) '
             '+ PLAN L104 flip (pit-104 re-derive) + orphan autostash audit')
st['verify'] = ('smoke 26/26; S6 37 legs rc=0; dualrun streak 8/3; regime ORANGE breadth 0.83; clock ORANGE_COOL; '
                't35 PASS zero-pending; t24 22/22 drift 0; token L2 0')
st['next'] = ('r427: W8 freeze-step watch (bm-b berth, pool refill self-heals supply_floor); guarded-face generator attribution '
              'cross-check by bm-b/bm-c; 10-01 month-boundary trio + REGIME_GUARD v3 auto date-gate')
st['last_round_at'] = ts
st['updated'] = ts
json.dump(st, open('state-bm-a.json', 'w', encoding='utf-8', newline=''), ensure_ascii=False, indent=1)

# 3) heartbeat (S7 tail)
hb = json.load(open('fleet/machines/bm-a.json', encoding='utf-8'))
epoch = int(time.time())
hb['last_seen'] = ts
hb['current_task'] = ('r427 closed: S0 storm-7 stash-pop salvage landed (17-UU canon resolve + W7 dual-run convergence proven); '
                      'batch-105 + waterline 9,219B; W8 freeze-step watch (bm-b berth); 10-01 month-first triple next')
hb['cpu_pct'] = 44.0
hb['free_ram_gb'] = 38.6
hb['gpu_free_vram_gb'] = 5.1
hb['verdict'] = ('r427 green: smoke 26/26; S6 37 legs rc=0 (dualrun streak 8/3; regime ORANGE shadow; clock ORANGE_COOL; '
                 't35 PASS; token L2 0); S0 salvage 17-UU zero-loss (W7 dual-run bit-identical checkpoint, stash dropped after harvest); '
                 'WM green (board clear, between-wave legal idle, supply_floor standing flag = W8 freeze imminent bm-b); state 427')
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = ts
hb['round_no'] = 427
assert isinstance(hb['heartbeat_epoch_utc'], int), 'epoch must be int (R170/R178 law)'
assert 'T' in hb['clock_read'], 'clock_read must be ISO 8601 T-separated (R262 law)'
json.dump(hb, open('fleet/machines/bm-a.json', 'w', encoding='utf-8', newline=''), ensure_ascii=False, indent=1)
print('epoch int OK:', epoch, '| clock:', ts, '| report+state+heartbeat written')
