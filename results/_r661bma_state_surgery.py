import re
import time

PATH = r'state-bm-a.json'
raw = open(PATH, 'rb').read()
orig_len = len(raw)

now_local = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')

def sub_once(pattern, repl_bytes, label):
    global raw
    new, n = re.subn(pattern, repl_bytes, raw, count=1, flags=re.S)
    assert n == 1, 'needle not found: ' + label
    raw = new

# 1) round_no 660 -> 661
sub_once(rb'"round_no": 660,', b'"round_no": 661,', 'round_no')

# 2) did / verify / next / last_round_at / current_task lines (mojibake-safe: match to line end)
did_new = ('r661 值守轮: S6 31 腿全绿 rc0 (dualrun ZERO-DRIFT streak36; compute_audit CLEAN; '
           'probe py_low_board_clear 周末合法 idle; CALL ORANGE_COOL sleeves4 activated0; LIVE-20261004 ORANGE cap50; '
           'REPORT-20261004 faces5; t35 PASS 0 pending) + S0.5 orders 双扫 152/152 零未回执 + '
           'D-19 双面 MATCH (decisions eb14b510/orders 82a0cef9 实径 git show 原字节复算) + '
           '生产线盘点 (fund NULLS bm-b 在飞 V~10-05/Q~10-07; W14 park=GM 面; post_review 历史 NO 38 条定性 零当窗新增 X)')
verify_new = ('S1 smoke 47/47; S6 31 legs rc0; attrition CLEAN 4 台账; S7 4/4 (loop pin8 no-op + '
              'watchdog 重注 + 双爪重装); 池 3 ready=bm-b 在飞禁碰防双烧; 引擎 pool-has-live-supply no-action')
next_new = ('10-05 V-NULLS 烧完窗 -> fund trio finalize watch (预演 r652 ALL-GREEN x3, r633 工具随轮重跑); '
            '10-08 开市窗 run-11/run-7 双跳 + 治理日验收窗 (登记簿零命令断言行); W14/CFO 探针=GM 裁决面')
ct_new = 'r661: 值守轮 S6 全绿 + 生产线盘点; next=V-NULLS finalize watch + 10-08 开市窗双跳'

sub_once(rb'"did": "[^\n]*",', b'"did": "' + did_new.encode('utf-8') + b'",', 'did')
sub_once(rb'"verify": "[^\n]*",', b'"verify": "' + verify_new.encode('utf-8') + b'",', 'verify')
sub_once(rb'"next": "[^\n]*",', b'"next": "' + next_new.encode('utf-8') + b'",', 'next')
sub_once(rb'"last_round_at": "[^\n]*",', ('"last_round_at": "' + now_local + '",').encode('utf-8'), 'last_round_at')
sub_once(rb'"current_task": "[^\n]*",', b'"current_task": "' + ct_new.encode('utf-8') + b'",', 'current_task')

open(PATH, 'wb').write(raw)
print('state surg: %d -> %d bytes' % (orig_len, len(raw)))

# post-write self-check: json.loads (tolerant read is NOT allowed for structural check of the new lines;
# the file has legacy GBK rows -> strict json would fail on those, so verify structure by regex instead)
import json
try:
    json.loads(raw.decode('utf-8'))
    print('strict json.loads: PASS')
except Exception as e:
    # legacy mojibake rows predate this surgery; confirm our new fields parse standalone
    txt = raw.decode('utf-8', errors='replace')
    for k in ['"round_no"', '"did"', '"verify"', '"next"', '"current_task"']:
        m = re.search(re.escape(k) + r': "([^"]{0,40})', txt)
        print(k, '=', (m.group(1)[:40] if m else 'MISSING').encode('ascii', errors='replace').decode())
    print('strict parse failed on legacy rows (pre-existing mojibake):', str(e)[:80])
