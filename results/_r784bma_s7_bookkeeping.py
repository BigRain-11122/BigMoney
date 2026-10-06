# -*- coding: utf-8 -*-
"""r784 bm-a S7 bookkeeping trio: state + heartbeat + round report line.
Bloodline: _r782bma_s7_bookkeeping.py field faces verbatim.
Round number note: state was 782 at window open (dead-r783 tail -- r783 session
died post-commit pre-S7); this round = 784, state jumps 782->784 absorbing the
dead increment, honest note in did/RR line."""
import json
import time
import datetime as dt

# --- state-bm-a.json ---------------------------------------------------------
s = json.load(open('state-bm-a.json', encoding='utf-8'))
s['round_no'] = 784
s['current_task'] = ("W161 freeze window next session (W160 finalize landed; "
                     "never-dry seat/freeze per r781 double-file lineage)")
s['did'] = ("r784: W160 finalize ONE-PASS (ledger 755,212 -> 757,412 +2,200, "
            "K=349,920, skill_line 1.1822 -> 1.1824 K-lift +0.0002; r708 "
            "pre-flight live-probe+file-probe double green; r381 "
            "recovery-first-action law) + W160 prereg sec7/sec8 backfill "
            "same-window + W159 prereg sec7/sec8 overdue backfill closed "
            "(r782 deferred-window honest note) + W160 seat self-ack "
            "inbox->processed (r783 deferral honored) + S6 38/38 rc0 110s + "
            "dead-r783 S7 tail absorbed into state 782->784")
s['last_action'] = ("r784 closeout: W160 finalize + dual prereg backfill + seat "
                    "self-ack + heartbeat + state 784 + RR line")
json.dump(s, open('state-bm-a.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('state round_no ->', s['round_no'])

# --- heartbeat fleet/machines/bm-a.json --------------------------------------
h = json.load(open('fleet/machines/bm-a.json', encoding='utf-8'))
now = dt.datetime.now().astimezone()
epoch = int(time.time())
h['last_seen'] = now.isoformat(timespec='seconds')
h['heartbeat_epoch_utc'] = epoch
h['clock_read'] = now.isoformat(timespec='seconds')
h['ts'] = now.isoformat(timespec='seconds')
h['now_active'] = ("W160 finalize landed; W161 freeze window next session "
                   "(never-dry line; engine idle queue empty)")
h['last_action'] = ("r784: W160 finalize one-pass (ledger 757,412, K=349,920) "
                    "+ W160/W159 prereg sec7/sec8 backfills + W160 seat self-ack")
h['latest_artifact'] = ("results/perpetual_faces/n1_w160_results.json "
                        "(W160 finalize verdict, 2026-10-06T16:3x)")
h['next_milestone'] = ("W161 seat+freeze+ignite (never-dry, window <=24h) + "
                       "10-07 D-06 closeout window")
json.dump(h, open('fleet/machines/bm-a.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
chk = json.load(open('fleet/machines/bm-a.json', encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int (R170/R178 law)'
print('heartbeat epoch int OK:', chk['heartbeat_epoch_utc'])

# --- round report line --------------------------------------------------------
line = ("| 2026-10-06T16:5x | r784 | bm-a | watermark verdict: py_low_board_clear "
        "(red=false lane=healthy; py 0.2% low = legal idle white-list: board "
        "fully closed O-1218 four tickets done + engine queue empty post-burn + "
        "zero runnable candidates, golden-week no-new-bar) | 当前活: W160 "
        "finalize 收口本窗完成（dead-r783 尾巴吸收）; 最近实物: results/perpetual_faces/"
        "n1_w160_results.json（W160 判定·账本 757,412·K=349,920·16:3x）; 下个里程碑: "
        "W161 seat+freeze+点火（never-dry·窗 ≤24h）+ 10-07 D-06 收口窗 | did: "
        "S0.5 orders 双扫零未回执+decisions 水位零动作 | S1 smoke 48/48 | S3 主线=W160 "
        "finalize ONE-PASS（r708 律 pre-flight 活进程探针+文件探针双绿后单跑 rc0；prev "
        "755,212 derive 实读禁手抄+2,200=757,412；merged K=349,920 mu=−0.092931 "
        "sigma=0.245122；skill_line 1.1822→1.1824 K-lift +0.0002；A p95=0.3297 vs "
        "W159 锚 0.3257 差 +0.0040<0.05 门过；se_mu 收窄 0.000416→0.000414；§5 四预测键"
        "全过机证；canon flip NOT performed K2200 同例法；ledger_head=757,412 file="
        "n1_w160_results.json 断言过；selftest PASS default-wave r522 律）| W160 "
        "prereg §7/§8 同窗回填（照 W158 例）| W159 prereg §7/§8 欠账回填收口（r782 "
        "窗回填未至如实注记·本窗补收口 r381 例）| W160 seat self-ack inbox→processed "
        "移位（r783 deferral 兑现·inbox 清零）| S6 38/38 rc0 110s（golden-week 诚实 "
        "no-op 族；dualrun ZERO-DRIFT streak 51；t35 PASS zero-pending）| attrition "
        "guard CLEAN（4 ledgers·healed 注记照录）| S7 四件套绿（loop pin=8 no-op + "
        "watchdog 重注册 16:39 + 双爪 LF 归一重装幂等）| state 782→784 吸收 dead-r783 "
        "S7 尾巴（r783 session died post-commit pre-S7·如实注记）| 心跳 epoch int + "
        "clock T 分隔自证 | orders_ack 167 零未回执双扫 | 下轮指针: (1) W161 席位+冻结"
        "（r781 双件血统·W160-B-refuses-W161-A 阶梯第廿例预注兑现检查）(2) 10-07 D-06 "
        "全线收口窗 (3) 下轮 5x=r789 HANDOVER 核查 | dept:研究 |\n")
with open('round_reports-bm-a.md', 'a', encoding='utf-8') as f:
    f.write(line)
print('RR line appended')
