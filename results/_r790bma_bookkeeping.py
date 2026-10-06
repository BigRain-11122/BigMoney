# -*- coding: utf-8 -*-
"""r790 bm-a bookkeeping: state/heartbeat/report/HANDOVER/CODELY one-pass fresh write.
Multi-writer files (orders ledgers, CODELY) = single-file fresh read-modify-write law."""
import io, json, time, datetime

NOW = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
EPOCH = int(time.time())
print('clock:', NOW, 'epoch:', EPOCH, type(EPOCH))

# ---------- 1. state-bm-a.json ----------
p = 'state-bm-a.json'
st = json.load(io.open(p, encoding='utf-8'))
st['round_no'] = 790
st['round'] = 788
st['loop_round'] = 790
st['current_task'] = 'W163 finalize landed; next = W164 seat+freeze (never-dry engine line) + 10-07 D-06 closeout'
st['did'] = ('W163 finalize one-pass rc0 (r708 double-probe GREEN preflight, 12/12 shards consumed, K=356,520==prereg projection, '
             'ledger 761,812->764,012, skill 1.1829->1.1831 K-lift +0.0002, s5 4/4 keys pass, s7/s8 backfilled, n1+pf selftest green) '
             '+ O-20261006-1845 tailnet order intake/receipt (bm-a=dasheng already in tailnet, C dual-node probe PASS) + S6 38/38 rc0 + HANDOVER 5x line')
st['last_action'] = 'r790: W163 finalize one-pass (ledger 761,812->764,012, K=356,520) + O-1845 receipt + HANDOVER 5x r761-r790 merged line'
st['last_round'] = 'r790'
st['last_round_at'] = NOW
st['last_round_ts'] = NOW
st['last_seen'] = NOW
st['last_run'] = NOW
st['updated'] = NOW
st['ts'] = NOW
st['heartbeat_epoch_utc'] = EPOCH
st['last_decisions_sha'] = '8fdf1f57ef0cc10b1b5848673da7c49eac76e654bb544117c5001c62a50df58c'
st['last_decisions_at'] = NOW
st['last_decisions_ts'] = '2026-10-06T19:0x'
st['last_decisions_src'] = 'git show origin/main:docs/decisions.md (blob bytes sha256, group tree at C:/Users/sjs20/Desktop/FluxGroup per D-20261004-02 fallback)'
st['last_orders_sha'] = '415bbcea97998f064c6b424f4518d7a2e1145ce847ea2a40c89816e96e9e5ffb'
st['last_orders_at'] = NOW
st['latest_artifact'] = 'results/perpetual_faces/n1_w163_results.json + research/PERPETUAL_N1_W163_PREREG.md s7/s8 @2026-10-06T19:0x'
st['next'] = ('(1) W164 seat+freeze+ignition (staircase 23rd anticipated: naive A 375_404..377_403 refused by W163 B band 375_404..375_603, hops=1 expected; '
              'own-A reservation leg2 for B; naive B 375_604..375_803 lands inside re-derived A window) '
              '(2) 10-07 12:00 D-06 closeout window (3) 5x=r795 HANDOVER check')
st['verify'] = ('ledger_head()=764,012 file=n1_w163_results.json; W163 K=356,520==prereg projection; '
                'decisions 8fdf1f57 consumed (D-04/05 HQ-only zero BigMoney dispatch); orders 415bbcea consumed (zero new bm-a lines)')
st['notes'] = 'O-20261006-1845 receipt: bm-a=dasheng in tailnet since 09-29 (100.110.185.62), physical 10.86.98.91 not 192.168.1.x, C 11434 tailnet PASS 3 models + 35b gen probe OK'
with io.open(p, 'w', encoding='utf-8', newline='') as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
print('state OK')

# ---------- 2. heartbeat fleet/machines/bm-a.json ----------
p = 'fleet/machines/bm-a.json'
hb = json.load(io.open(p, encoding='utf-8'))
hb['round_no'] = 790
hb['loop_round'] = 603
hb['clock_read'] = NOW
hb['ts'] = NOW
hb['last_seen'] = NOW
hb['heartbeat_epoch_utc'] = EPOCH
hb['last_round'] = 'r790'
hb['last_action'] = st['last_action']
hb['task'] = 'r789 W163 finalize done; next = W164 seat+freeze + 10-07 D-06 closeout'
hb['current_task'] = hb['task']
hb['now_active'] = 'W163 finalize landed (ledger 764,012; chain W1..W163 fully closed, zero in-flight seats)'
hb['latest_artifact'] = st['latest_artifact']
hb['next_milestone'] = 'W164 seat+freeze (never-dry, window <=24h) + 10-07 D-06 closeout 12:00 + T-173 report due 10-08 noon'
hb['verdict'] = ('r790 W163 finalize landed (bm-a 79th owned, 153rd wave, A 373_404..375_403/B 375_404..375_603, '
                 'ledger 761,812->764,012 K=356,520, skill 1.1829->1.1831, s5 4/4, n1+pf selftest PASS); '
                 'S6 38/38 rc0; smoke 48/48; O-1845 tailnet receipt landed')
if 'O-20261006-1845-bm-c.md' not in hb['orders_ack']:
    hb['orders_ack'].append('O-20261006-1845-bm-c.md')
assert isinstance(hb['heartbeat_epoch_utc'], int), 'epoch must be int'
with io.open(p, 'w', encoding='utf-8', newline='') as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
print('heartbeat OK, acks:', len(hb['orders_ack']))

# ---------- 3. round report line ----------
p = 'logs/iteration-loop/round_reports-bm-a.md'
line = ('2026-10-06T19:0x+08:00 | r790 bm-a (dept:工程+研究) | watermark verdict: 绿 (red=false lane=healthy; py 0.4-0.6% 低位=golden-week 合法 idle 白名单面: '
        '板全闭环 0 open 票 + 引擎 W163 烧毕收口 + 零 active burns) | 当前活: W163 finalize ONE-PASS 本窗落地 + O-20261006-1845 机队组网令回执 '
        '| 最近实物: results/perpetual_faces/n1_w163_results.json + research/PERPETUAL_N1_W163_PREREG.md §7/§8 回填 @2026-10-06T19:0x '
        '| 下个里程碑: W164 席位+冻结+点火 (never-dry 线·窗 ≤24h) + 10-07 12:00 D-06 收口窗 '
        '| did: S0 fetch behind=0 脏树=own r789 收尾面 (preflight 双探针 GREEN _r790bma_w163_preflight.json 后单路 finalize: ledger 761,812→764,012 +2,200==prereg 投影恒等·'
        'K 354,320→356,520==prereg 投影键·skill_line_v2 1.1829→1.1831 K-lift +0.0002·se_mu 0.000412→0.000411·A p95 0.3259 vs W162 键 0.3093 差 +0.0166 正向微扩如实披露·'
        'W163-only mu −0.088982/merged −0.092858 |Δ|=0.0039·§5 四预测键全过机证·canon flip NOT performed·audit.finalize_only=true·'
        'mu_delta_w163_vs_w162ext +0.006616) + §7/§8 同窗回填 (W162 范式镜像+机值零手抄) + 宝藏捕获问本批无新宝藏 (阶梯第 22 例已由 r789 冻结窗 gate 回执 ADMIT 兑现·方法论卡零 append) '
        '+ n1 selftest PASS + pf selftest 9/9; S0.5 O-20261006-1845-bm-c 令执行 (CEO 令 bm-c 转发: bm-a=dasheng 已在 tailnet 100.110.185.62 自 09-29=bm-c 检测漏认已纠正·'
        '物理 IP 10.86.98.91≠192.168.1.0/24 与 C 非同物理 LAN 192.168.1.4 另有其机·C 双节点实测 tailnet 11434 True+三模型在位+qwen3.6-coder:35b 生成探针 OK·'
        '服务面 L2 自决=大文件接收/中转节点候选+Ollama 对外暂不开+LLM-via-C 35b 纳入 L2 候选待 GM 定籍·回执节已落令件) + '
        '决策水位 a44c39e0→8fdf1f57 消费 (D-20261006-04/05 均 HQ 台账即办零 BigMoney 派单=水位更新零动作) + orders 水位 3e8c73e3→415bbcea 消费 (零新本司行) + orders 159/159 双扫零未回执; '
        'S1 smoke 48/48; S3 饱和引擎 status rc0 活 (active_burns=[] W163 已烧完); S6 38/38 rc0 101.3s (_r790bma_s6_chain.py=r788 血统·dualrun ZERO-DRIFT·golden-week no-op 族如实); '
        'S7 attrition guard CLEAN 4 账本 + loop pin=8 在位 + watchdog 在位 + 双爪恒等 + state 789→790 + 心跳 epoch int 自证 + HANDOVER 5x 行 (r761-r790 合并覆盖·r765-r785 死会话截如实注记·产品漂移清单入行) '
        '| verify: ledger_head()=764,012 file=n1_w163_results.json 断言过; orders 159/159; 本地未达 origin commit 数=0 (commit 后 push+fetch+rev-list 复核) '
        '| next: (1) r791=W164 席位+冻结+点火 (naive A 375_404..377_403 将被 W163 B 带 375_404..375_603 拒·阶梯第 23 例 post-W163 宇宙 derive 强制+own-A 预留 leg2; naive B 375_604..375_803 落重 derive A 窗内) '
        '(2) 10-07 12:00 D-06 收口窗 (3) T-173 48h 报告 due 10-08 午 | [r790 bm-a]\n')
with io.open(p, 'a', encoding='utf-8', newline='') as f:
    f.write(line)
print('report OK')

# ---------- 4. HANDOVER 5x line (insert after title line) ----------
p = 'research/HANDOVER.md'
txt = io.open(p, encoding='utf-8').read()
hline = ('> bm-a round 790 五倍数核对（2026-10-06 19:0x·增量窗覆盖如实披露：r760 5x 后 r765/r770/r775/r780/r785 五个 5x 截被死会话窗吃吞未落账'
         '〔r752 dead-tail continuation 轮族+r787 死会话吸收窗实录〕——本行合并覆盖 r761-r790 三十轮）：增量窗 r761-790=bm-a 面像（'
         '**W157..W163 七波全生命周期收口主线（freeze→tick 点火→12/12→finalize→账本）+CEO 令双窗执行+死尾吸收**——'
         'W157 finalize r772〔dead-tail adoption 链头 739,211→741,411〕·W158 finalize r778〔→753,012〕·W159 finalize r782〔→755,212〕·'
         'W160 finalize r784〔→757,412〕·W161 finalize r786〔→759,612〕·W162 finalize r788〔→761,812〕·W163 freeze r789+finalize r790〔→764,012·K=356,520〕'
         '——nulls-deepening 常设线七连收口·skill_line_v2 1.1792→1.1831·K-lift 逐波 +0.0000 量级·se_mu 0.000443→0.000411；'
         'COREBOOK 零烧判定 r777〔链头 750,812 观察窗〕；O-20261006-1207 题材深化批令 r773 承接〔T-173 三面票 opened+claimed·due 10-08 午〕；'
         'O-20261006-1218 综合研判令 r774 承接〔T-174/175/176 三面票·撞号让路 1215→1218 全链留痕〕；'
         'r779 死尾吸收〔T-173 票面注记〕；r787 死会话〔W162 freeze 落地〕r788 吸收；'
         'O-20261006-1410 集团巡检整改〔PT-20261006-01·bm-a 心跳 ts 字段整改 SLA 10-13〕；'
         'O-20261006-1845 机队组网令 r790 执行+回执〔bm-a=dasheng 已在 tailnet 100.110.185.62 自 09-29=bm-c 检测漏认纠正·物理 10.86.98.91 非 192.168.1 段·'
         'C 双节点 11434 实测通三模型+35b 生成探针 OK·服务面 L2 自决留痕〕；'
         'W164+ 投影已披露（阶梯第 23 例 anticipated）。**产品清单漂移**=results/perpetual_faces/n1_w1{57..163}_results.json〔七连 finalize 合并件〕+'
         'research/PERPETUAL_N1_W1{57..163}_PREREG.md〔冻结件族·§7/§8 回填〕+results/p2cal_ext/n1_w1{57..163}/ 分片件族+席位 MSG 族'
         '〔fleet/inbox/processed/〕+band gate/probe/xform 回执族 results/_r7{7,8}*.py/.json+T-173/174/175/176 票面'
         '〔fleet/tasks/〕+O-1845 回执节〔fleet/orders/O-20261006-1845-bm-c.md〕+本行 research/HANDOVER.md〔r790 5x〕；'
         '统一链 **764,012 实读**〔live head=results/perpetual_faces/n1_w163_results.json science_gates.ledger_head() 实测·W163 finalize bm-a r790 已落账〕；'
         'orders 159/159 双扫零未回执全窗维持；smoke 48/48 全窗维持；D-19 双水位消费窗窗清洁〔r790 dec 8fdf1f57/ord 415bbcea〕；'
         '指针：**10-07 12:00 D-06 集团收口窗+T-173 48h 报告 10-08 午+W164 freeze→ignition→finalize（bm-a 车道）+复竞 10-09+月界首考 10-31**；下一 5x=bm-a r795。\n')
lines = txt.split('\n')
lines.insert(1, hline.rstrip('\n'))
with io.open(p, 'w', encoding='utf-8', newline='') as f:
    f.write('\n'.join(lines))
print('HANDOVER OK')

# ---------- 5. CODELY.md execution record (multi-writer file: fresh read-modify-write) ----------
p = 'CODELY.md'
txt = io.open(p, encoding='utf-8').read()
cline = ('- [2026-10-06 19:0x r790 bm-a] O-20261006-1845-bm-c 机队组网令执行记录（CEO 令 bm-c 转发·回执节已落令件 fleet/orders/O-20261006-1845-bm-c.md）：'
         'bm-a=dasheng 已在 tailnet（100.110.185.62·sunjs666@·09-29 入网在册）——bm-c 检测「bm-a 不在 tailnet」实为漏认 dasheng 节点；'
         '物理 IP=10.86.98.91≠192.168.1.0/24 与 bm-c 非同物理 LAN（192.168.1.4 另有其机非 bm-a）；'
         'C 双节点实测 tailnet 100.123.74.104:11434 True+/api/tags 三模型在位（qwen3.6-coder:35b/qwen3.8:27b/glm-4.7-flash:30b）+qwen3.6-coder:35b 最小生成探针 OK；'
         '服务面 L2 自决=①大文件接收/中转节点候选（tailnet 直传待实测后 GM 定籍 TRANSFER.md）②本机 Ollama 对外暂不开放（GPU 常驻引擎/本地 LLM 车道）'
         '③ACE-Step 未驻场如实 ④LLM-via-C 35b 纳入 bm-a L2 候选通道待 GM 定籍（L1 脚本能算照旧禁走 LLM）。'
         '另 W163 finalize 落地（ledger→764,012·K=356,520）+HANDOVER 5x r761-790 合并行+决策水位 8fdf1f57/orders 415bbcea 消费零本司新派单。\n')
assert cline.strip() not in txt, 'dedup guard'
txt = txt.rstrip('\n') + '\n' + cline
with io.open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(txt)
import os
print('CODELY OK, size:', os.path.getsize(p))
print('ALL BOOKKEEPING DONE')
