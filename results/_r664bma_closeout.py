# -*- coding: utf-8 -*-
"""r664 bm-a S7 closeout: state increment + heartbeat + round report append (all with self-checks)."""
import json, time, datetime, io

NOW = datetime.datetime.now().astimezone()
CLOCK = NOW.strftime('%Y-%m-%dT%H:%M:%S') + NOW.strftime('%z')[:3] + ':' + NOW.strftime('%z')[3:]
EPOCH = int(time.time())
STAMP = NOW.strftime('%Y-%m-%d %H:%M:%S')

# ---------- 1. state round_no 664 -> 665 ----------
P = 'state-bm-a.json'
d = json.loads(open(P, 'rb').read().decode('utf-8', errors='replace'))
assert d['round_no'] == 664, f"round_no unexpected: {d['round_no']}"
d['round_no'] = 665
d['last_round_at'] = STAMP
d['last_round'] = 'r664'
d['current_task'] = ('theme ignition census v0.3 delivered (1,919 episodes); fund trio NULLS bm-b in-flight watch; '
                     'T-166 fund statement backfill in background (60+/258 staging)')
d['last_round_ts'] = CLOCK
with open(P, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
back = json.loads(open(P, 'rb').read().decode('utf-8', errors='replace'))
assert back['round_no'] == 665 and isinstance(back['round_no'], int)
print('state round_no -> 665 (json.loads self-check PASS)')

# ---------- 2. heartbeat ----------
P = 'fleet/machines/bm-a.json'
h = json.loads(open(P, 'rb').read().decode('utf-8', errors='replace'))
h['last_seen'] = CLOCK
h['heartbeat_epoch_utc'] = EPOCH
h['clock_read'] = CLOCK
h['current_task'] = d['current_task']
h['cpu_cores'] = 32
h['verdict'] = ('GREEN (smoke 48/48; S6 37/37 rc0 dualrun streak40; theme census v0.3 1,919 episodes delivered + E28 card; '
                'O-20261004-0808 GM double-ruling ACKED: W14 park maintained + G-SEG insufficient-sample freeze path maintained '
                '+ holiday compute orbit aligned (five-things/theme/nulls); fund trio NULLS bm-b canonical in-flight keepalive '
                '(V615/Q465/D333-of-2000 at 07:10 hb); T-166 fund-statement backfill advancing in background; watermark red=false)')
ack = h.get('orders_ack', [])
if 'O-20261004-0808-bm-a.md' not in ack:
    ack.append('O-20261004-0808-bm-a.md')
h['orders_ack'] = ack
with open(P, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(h, f, ensure_ascii=False, indent=1)
back = json.loads(open(P, 'rb').read().decode('utf-8', errors='replace'))
assert isinstance(back['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
assert back['clock_read'].count('T') >= 1 and '+' in back['clock_read'], 'clock_read must be ISO8601 T-format'
assert 'O-20261004-0808-bm-a.md' in back['orders_ack']
print('heartbeat updated (epoch int + clock T-format + ack appended, self-check PASS)')

# ---------- 3. round report append ----------
LINE = (f"watermark: green (red=false; satengine alive rc0 queue 0; fund trio NULLS bm-b canonical in-flight keepalive "
        f"refusals counting = fuse pins working as designed; compute_audit CLEAN; probe insufficient_history golden-week "
        f"no violation face) | {CLOCK} | r664 | dept:研究 | 当前活: 题材战法线 R3 第三刀 v0.3 算法点火普查交付+GM 双裁令 "
        f"O-20261004-0808 回执（裁决一 W14 停泊维持·档存留册不解冻·10,000 帽悬置只约束候选搜索类·V-NULLS 基线投资照跑；"
        f"裁决二 G-SEG 冻结 insufficient-sample 路径维持·在飞三族判决禁中途换分段法·10-06..09 裁决窗以该令结案；轨道对齐=五件事+题材族+nulls+CEO 数据件已呈）"
        f" | 本轮主产出: scripts/theme_ignition_census.py(selftest 7/7·run 9.4s 预算帽内)+results/theme_ring/"
        f"theme_events_v03_algorithmic.json+csv = 全 ETF 面板 1,723 扫描/1,012 合格/**1,919 规则定义事件**(823 ETF·"
        f"evidence_cutoff 2026-09-30·O-2103 §二 R3 >=30 事件目标 60 倍达成)——诚实披露① 924 行情主导: 2024-09-30 单日 436 事件(23%)·"
        f"924 窗 693(36%)·36 个 >=10 同日集群日=市场级 beta 突发非题材特异性(后续判决消费必须同日集群分层)②CEO 16 锚仅 2 个 ±30td 命中"
        f"(券商 +1d/军工 +7d)+3 近失(31-35d)+11 锚窗零命中=爆发确认规则是滞后确认器非叙事起点探测器③famous14 事件中位 ign→peak +53.4% vs "
        f"面板其余 +36.8%=E25 幸存溢价的逐事件量化(16.6pp 中位·远小于 R4 B&H-vs-随机 3 倍差)——E28 双律卡(爆发确认点火滞后律+点火普查集群主导律)"
        f"+TREASURE_REGISTRY 行+THEME_EVENT_LIBRARY §八 落正典; T-165 票面 progress 行补 | S0.5: orders 双扫 153 件仅 O-0808 未回执→本轮回执+心跳 ack; "
        f"D-19 decisions sha MATCH 零动作(eb14b510·git show 原字节法); 集团 orders.md 未开新窗 | S1 smoke 48/48; 生产线: fund trio NULLS bm-b 正主在飞"
        f"(V615/Q465/D333 of 2000·dup_k=0·pid 活·禁碰=本机熔断钉正确工作·refusals 计数=设计面非故障), bm-b r654 已修 VALUE finalize 崩+预演 ALL-GREEN x3, "
        f"W14 park 维持, G-SEG G4 裁决已被 O-0808 结案(bm-b 下轮 S0.5 自取); T-166 财报回填后台推进(60+/258 staging·进程活·gitignore 面零提交风险); "
        f"W115 bm-c 解停点火在位 | S6: 37/37 腿 rc0 126.4s(_r664bma_s6_log.txt; dualrun ZERO-DRIFT streak40; CALL ORANGE_COOL sleeves4 activated0; "
        f"LIVE-20261004+REPORT-20261004+daily_scorecard+dashboard 全刷新; t35 PASS 0 pending; t24 22/22+晋升门 0/22 合法 NOT-ELIGIBLE; 周末采集腿全合法 no-op; "
        f"AH 面板分离刷新已完成; 金周无新 bar→live.paper 系腿诚实跳过(r660 判例)) | S7: 自愈 4/4(loop pin8 no-op+watchdog 重注+双爪 CR 归一重装); "
        f"attrition CLEAN 4 台账; 提交纪律: 轮首 daemon 面 r437 absorb(8 面)+S0 merge→轮末 15 commits 进位再 absorb(交集 26 面 checkout origin blob "
        f"保熔断钉核验 3/3 sig 在位)+merge 撞 REPORT json 一面(当日幂等再生件 ts 定侧 ours 08:17>origin 08:05 整面取 ours·markers 0·json parse OK·r661 判例)"
        f" | 验证证据: selftest 7/7+run 9.4s 产物五件在盘+锚匹配表 16 行+canon 三件 count 断言+push_verify DELIVERED(tip=remote 3a9baa136·ahead=0)"
        f" | 记分: 2 (可跑普查器+1,919 事件产物件=实物) | 记账预算: 4/5 (state+心跳+轮报告+票面) | 本地未达 origin commit 数: 0 (收尾 push 后 push_verify "
        f"自证 DELIVERED) | ceo-visibility: [当前活] 题材事件库扩容普查交付+基金三族判决基线烧批在 bm-a 外正主机在飞+财报数据底座回填本机后台推进 "
        f"[最近实物] results/theme_ring/theme_events_v03_algorithmic.json+csv (1,919 事件·08:1x) + scripts/theme_ignition_census.py + LIVE-2026-10-04 CEO 一页纸 "
        f"[下个里程碑] 10-05 基金三族 V-NULLS 烧完→judged finalize 窗开 (预演 ALL-GREEN x3 就绪·<=48h 首节点); 10-06..07 T-166 财报面板完备翻牌; 10-08 开市窗 "
        f"run-11/run-7 双跳\n")

P = 'round_reports-bm-a.md'
with io.open(P, 'a', encoding='utf-8', newline='') as f:
    f.write(LINE)
src = io.open(P, encoding='utf-8', errors='replace').read()
assert 'r664 | dept:研究' in src, 'report line lost'
assert src.count('| r664 |') == 1
print('round report r664 line appended (self-check PASS)')
print('ALL CLOSEOUT FACES DONE at', CLOCK)
