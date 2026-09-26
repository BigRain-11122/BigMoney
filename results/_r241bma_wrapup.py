# -*- coding: utf-8 -*-
"""R241 S7 wrap-up: state round_no++, heartbeat (epoch int + ack), round report.

Format-mirror laws: state/heartbeat indent=1 + CRLF (r230/r223), heartbeat
epoch_utc MUST be JSON int (R170/R178 double-law), round report append-only
CRLF, orders_ack token = full filename incl .md suffix (r220 law).
"""
import io
import json
import time
from datetime import datetime, timezone, timedelta

NOW = datetime.now()
CST = timezone(timedelta(hours=8))
NOW_ISO = NOW.strftime('%Y-%m-%dT%H:%M:%S+08:00')
NOW_S = NOW.strftime('%Y-%m-%d %H:%M:%S')
EPOCH = int(time.time())

# ---- 1) state-bm-a.json ----
SP = 'state-bm-a.json'
d = json.load(io.open(SP, encoding='utf-8'))
old_round = d['round_no']
d['round_no'] = 241
d['did'] = ('R241: adopted dead R240 mid-rebase wreckage (resolver died between '
            'write and add, 13/14 staged, CODELY UU) -> verified on-disk vs blob '
            'union then completed: 3 rebase waves all canonical (CODELY memory-union '
            'x2, post_review.jsonl 599+33->632 zero-loss, autofill launches-union '
            'cap50 + last_tick dict, compute_audit history union 204, snapshots '
            'take-new, dashboard twins, daily products take-mine+regen) -> main '
            'LANDED db38b1aa after machine/bm-a-r241 fallback; O-0958 acked '
            'cross-ref (bm-b executed T-78 s1-s3); T-70 C-arm batch COMPLETE '
            '10:50:09: C=4/10 vs A 10/10 B 2/10, fix-rounds dist 3/1/6, strict '
            'loop conversion=01 only (05=regen variance honest split), frozen '
            'prereg line fired: 4/10<7/10 -> honest negative (30B not production-'
            'line grade, no purchase card), S5 closeout appended; memory hot-cold '
            'reorg 6 flow lines -> archive zero-loss, root 47.3KB')
d['verdict'] = 'GREEN'
d['next'] = ('T-70 blind-eval axis slice (C products new-mask re-eval per RUBRIC '
             'double-blind) -> B-single-vs-C-loop two-axis summary backfill HQ + '
             'P-08; 09-28 Mon new-bar chain; 10-01 month trio + REGIME_GUARD v3 '
             'date gate; T-70 midterm dossier verdict reading 10-09 GM window')
d['ts'] = NOW_ISO
d['last_round_ts'] = '2026-09-26T10:31:43'
d['updated_at'] = NOW_ISO
d['current_task'] = ('R241 done: T-70 C-arm functional closeout (blind-eval axis '
                     'next); R240 collision saga fully landed main')
d['updated'] = NOW_S
txt = json.dumps(d, ensure_ascii=False, indent=1)
io.open(SP, 'w', encoding='utf-8', newline='').write(txt.replace('\n', '\r\n') + '\r\n')
back = json.load(io.open(SP, encoding='utf-8'))
assert back['round_no'] == 241 and old_round == 240
print(f'state: round_no {old_round} -> 241 OK (parse-verified)')

# ---- 2) heartbeat fleet/machines/bm-a.json ----
HP = 'fleet/machines/bm-a.json'
h = json.load(io.open(HP, encoding='utf-8'))
ack = h.get('orders_ack', '')
tokens = ack.split()
if 'O-20260926-0958-bm-a.md' not in tokens:
    tokens.append('O-20260926-0958-bm-a.md')
h['orders_ack'] = ' '.join(tokens)
h['last_seen'] = NOW_S
h['current_task'] = ('R241: T-70 C-arm functional closeout done (C=4/10, frozen '
                     'negative line fired, no purchase card); blind-eval axis next '
                     'slice; R240 push-collision wreckage adopted+landed main '
                     'db38b1aa; S6 21 legs green, watermark py_low_board_clear')
h['verdict'] = 'idle_ok'
h['heartbeat_epoch_utc'] = EPOCH
h['clock_read'] = NOW_ISO
h['round_no'] = 241
txt = json.dumps(h, ensure_ascii=False, indent=1)
io.open(HP, 'w', encoding='utf-8', newline='').write(txt.replace('\n', '\r\n') + '\r\n')
back = json.load(io.open(HP, encoding='utf-8'))
ep = back['heartbeat_epoch_utc']
assert isinstance(ep, int) and not isinstance(ep, bool), f'epoch must be int, got {type(ep)}'
assert 'O-20260926-0958-bm-a.md' in back['orders_ack'].split()
print(f'heartbeat: epoch={ep} (int OK), ack token added ({len(tokens)} tokens)')

# ---- 3) round report append ----
RP = 'logs/iteration-loop/round_reports-bm-a.md'
line = ('2026-09-26 11:15 | R241 | 死轮残骸收养+T-70 C 臂功能面收口：S0 发现 R240 '
        'push 被拒后 rebase 中途死（resolver2 死于 write/add 之间 13/14, CODELY UU）'
        '→收养正典三波全解（CODELY union 验盘即 add；post_review.jsonl 599+33→632 行级 '
        'union 零丢失；autofill launches union cap50+last_tick 整 dict 取新 10:40:01；'
        'compute_audit history union 204；snapshot 取新 bm-b 10:41 侧；dashboard 双胞胎 '
        '整字节同侧保 JS 包装；daily 产物 take-mine+确定性再生）→push 三拒→machine/'
        'bm-a-r241 fallback→rebase3 落 main db38b1aa（全部 rebase 禁 abort 零丢失）；'
        'S0.5 orders 78/78 差集=O-0958 未回执→bm-b 已执行 T-78 s1-s3 实证（fetch 门+'
        'prereg 冻结 r240+s2/s3 r241）→交叉回执零重复，decisions 新行 D-20260926-01..04 '
        '无 BigMoney 新指令；smoke 25/25；watermark red=false；post_review 2 NO 行'
        '=T-27-VETO-FIELD 09-24 已修史（39 连 YES 至 10:25）零动作；T-70 C 臂批 10:50:09 '
        'COMPLETE：C=4/10（01@2r 严格循环转化+02/03/05@0r，05=B-fail→C-round0=再生方差诚实'
        '分列；A 10/10 B 2/10 同口径）第五列 0/1-3/3 轮未过=3/1/6，冻结解读线 4/10<7/10 '
        '触发→如实定谳「30B 不达产线·购买卡不呈」零再推导，S5 收口段落 prereg（§1-4 冻结面'
        '零触碰），资源面 5012s/30 attempts/96,348 eval tokens/0 OOM/0 让路；S4 记忆一'
        '条（死轮 resolver 半程态收养律）+超 50KB 水位热冷整编 6 流水行迁 research/'
        'memory-archive/202609.md 行级零丢失（root 50.8KB→47.3KB）；S6 21 腿全绿'
        '（audit CLEAN, watermark=py_low_board_clear, 周末 no-op 合法, clock ORANGE_COOL '
        '幂等, moneyflow/AH spawn 节流窗内）；schtasks 双活；inbox 空 | 下轮: T-70 盲评轴'
        '切片（C 产物新 mask 重评双盲）→两轴对照小结回填 HQ+P-08；09-28 新 bar 链；10-01 '
        '月界三件套+REGIME_GUARD v3\r\n')
with io.open(RP, 'a', encoding='utf-8', newline='') as f:
    f.write(line)
print('round report R241 appended')
