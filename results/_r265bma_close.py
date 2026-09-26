# -*- coding: utf-8 -*-
"""R265 bm-a closeout: round report line + state bump + heartbeat refresh (three-face self-verified)."""
import json, time, datetime, psutil

REPORT = 'logs/iteration-loop/round_reports-bm-a.md'
STATE = 'state-bm-a.json'
HEART = 'fleet/machines/bm-a.json'

now = datetime.datetime.now().astimezone()
ts_h = now.strftime('%Y-%m-%d %H:%M')
epoch = int(time.time())
clock_read = now.isoformat(timespec='seconds')

REPORT_LINE = (
    '2026-09-26 19:%02d | R265 bm-a | watermark: GREEN (19:13 probe verdict=py_low_board_clear legal-idle: board 0 open + bandit 0 + '
    'pool 49/49 done + zero runnable candidates, 18:50 red face re-answered by real closure state, no fabricated batch per O-1137; '
    'compute_audit CLEAN flags=[] pool_starvation_candidate=true honestly answered=board-clear) | did: S0 pull-rebase Already-up-to-date; '
    'S0.5 orders 83/83 BOTH scans zero diff (canonical tool) + decisions.md zero new BigMoney-action rows (tail D-20260926-01..11 all '
    'prior-gated; D-09/D-10 executor=HQ, D-11 executed R249) + inbox 0 unread; S1 smoke 25/25; S2 job_list empty + board 0 open '
    '(30 active all claimed; T-83 bm-b owner); S3 MAIN = R265 5x HANDOVER 核对更新（round_no 265=5 倍数轮·双轨制 per r250 bm-b 先例）: '
    'line3 最近核对链前插 bm-a round 265 条目+bm-b r260 降级上一次核对+文末增量窗行 append（对账区间=bm-a R256-265+bm-b r261-267 并读; '
    '统一链 186,592→187,845 实读 +1,253 全窗: CN-REGIME-POLICY +993 R256〔r260 bm-b line3 已收讫〕+style_rotation +102 R259+'
    'CN-CORE-SATELLITE +54 R261+CN-CORE-DDCTL +104 R263=五家族判决批全负收口; T-73 s1/s2/s3 FULLY CLOSED 事实入 line3; '
    'post_review 1,038 行 23 YES/0 NO/5 WAIT 零 ✗; orders 83/83; 池 49/49 done）——产物=results/_r265bma_handover.py '
    '（fail-closed 锚定+CJK 尾锚 console-mojibake 面首锚猜错=JSON 实探锚原文律再证+正典术语校对〔判读/六员首检/半档梯三术语首版误写当场自捕回滚重写〕）'
    '+git diff --stat 2+/1- 字段级双门 PASS+写后七点全检 PASS; S6 ~28 legs ALL exit 0（weekend no-ops: audit CLEAN/wm probe n=4 avg 1.1pct/'
    'daily 0 rows cutoff 09-24/regime ORANGE d2 shadow hs300<MA200 breadth 0.77/clock CALL-2026-09-24 ORANGE_COOL sleeves=4 activated=0 '
    'idempotent/lhb 30min throttle/heat weekend/futures+options cutoff no-op/moneyflow rank spawn throttle 10.7min/sina+ths same-day '
    'idempotent/AH spawn throttled 10min<30min/fp bm-c lane honest no-op/fundamental 21.8h fresh skip/blf all_pass/export 09-24 idempotent '
    '6 traders 18 positions/scorecard 6+28+7/daily_report faces=4 token=1/build_status 432combos/token_meter delta=0 L2 1 leg）'
    '+no new bar Saturday（cutoff 09-24·中秋 09-25 源缺 bar）→live.paper/t35v/t24×2/aggr/alloc/grid 条件腿合法跳过; '
    '月度三件套非月首轮（10-01 下窗）; S7 schtasks R49 law: IterationLoop Running + Watchdog Ready 双任务在册 | '
    'evidence: research/HANDOVER.md diff --stat 2+/1- + _r265bma_handover.py checks 7/7 PASS + S6 exit codes 28x0 in transcript + smoke 25/25 | '
    'next: (1) 09-28 Monday new-bar chain（cutoff 09-24·Friday bar source-absent re-attempt; daily→live.paper REGIME_GUARD v3 enforce→'
    't35v→t24×2→aggr 20 账→grid 5 账首拍 marks→export→scorecard→daily_report）; (2) 10-01 monthly trio + REGIME_GUARD v3 date gate; '
    '(3) T-70 C-arm 中期判读 10-09; (4) R270 5x HANDOVER'
) % now.minute

# --- 1. round report append (EOL mirrored) ---
raw = open(REPORT, 'rb').read()
crlf = raw.count(b'\r\n') > 0
sep = '\r\n' if crlf else '\n'
if raw.endswith(sep.encode()):
    out = raw + REPORT_LINE.encode('utf-8') + sep.encode()
else:
    out = raw + sep.encode() + REPORT_LINE.encode('utf-8') + sep.encode()
open(REPORT, 'wb').write(out)
print('report appended, crlf=%s' % crlf)

# --- 2. state bump (load -> update -> dump mirrored: indent=1, CRLF, no trailing newline) ---
st = json.loads(open(STATE, 'rb').read().decode('utf-8'))
st_prev_round = st['round_no']
st['round_no'] = 265
st['did'] = ('R265 5x HANDOVER recon round (maintenance face, board clear): line3 anchor chain '
             'bm-a r265 prepend + bm-b r260 demote + end-of-file increment row (bm-a R256-265 + bm-b r261-267 window, '
             'ledger 186,592->187,845 +1,253 read, five-family negative closure chain receipted)')
st['verdict'] = 'R265: 5x HANDOVER dual-track updated field-level; legal idle confirmed (pool 49/49, board clear, probe py_low_board_clear)'
st['next'] = ('(1) 09-28 Monday new-bar chain (cutoff 09-24, Friday bar source-absent re-attempt); (2) 10-01 monthly trio '
              '+ REGIME_GUARD v3 date gate; (3) T-70 C-arm verdict window 10-09; (4) R270 5x HANDOVER')
for k in ('ts', 'last_round_ts', 'updated_at', 'current_task', 'last_run', 'last_round_at', 'updated'):
    st[k] = ts_h if k != 'current_task' else 'R265 closed (5x HANDOVER recon)'
st['last_round'] = 265
txt = json.dumps(st, ensure_ascii=False, indent=1).replace('\n', '\r\n')
open(STATE, 'wb').write(txt.encode('utf-8'))
print('state round_no %d -> 265' % st_prev_round)

# --- 3. heartbeat refresh (epoch INT + T-sep clock_read, three-face self-verified) ---
h = json.loads(open(HEART, 'rb').read().decode('utf-8'))
cpu = psutil.cpu_percent(interval=1.0)
vm = psutil.virtual_memory()
h['last_seen'] = clock_read
h['current_task'] = 'R265 closed: 5x HANDOVER recon (line3+increment row, ledger 186,592->187,845 five-family negative chain receipted)'
h['cpu_pct'] = round(cpu, 1)
h['free_ram_gb'] = round(vm.available / (1024 ** 3), 1)
h['free_ram_mb'] = int(vm.available / (1024 ** 2))
h['idle_ram_gb'] = round(vm.available / (1024 ** 3), 1)
h['verdict'] = ('GREEN R265: 5x HANDOVER dual-track updated (bm-a R256-265 + bm-b r261-267 window, chain 186,592->187,845, '
                'five CN combo families all-negative closure receipted, T-73 science faces fully closed); smoke 25/25; '
                'S6 ~28 legs exit 0 weekend no-ops; probe py_low_board_clear legal idle (pool 49/49, board clear)')
h['heartbeat_epoch_utc'] = epoch
h['clock_read'] = clock_read
h['round_no'] = 265
h['task'] = ('R265 done: 5x HANDOVER recon; next = 09-28 Mon new-bar chain (cutoff 09-24), 10-01 monthly trio + REGIME_GUARD v3, '
             'T-70 C-arm verdict 10-09')
txt = json.dumps(h, ensure_ascii=False, indent=1).replace('\n', '\r\n')
open(HEART, 'wb').write(txt.encode('utf-8'))

# --- self-verification (smoke F7 contract) ---
h2 = json.loads(open(HEART, 'rb').read().decode('utf-8-sig'))
assert isinstance(h2['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
assert 'T' in h2['clock_read'], 'clock_read must be T-separated ISO 8601'
st2 = json.loads(open(STATE, 'rb').read().decode('utf-8-sig'))
assert st2['round_no'] == 265
print('heartbeat self-verified: epoch=%d (int) clock_read=%s' % (h2['heartbeat_epoch_utc'], h2['clock_read']))
print('CLOSE OK')
