# _r339bma_s7.py -- r339 close: state bump + heartbeat + round report line.
# Format law: state/heartbeat blobs = pure LF, indent=1, NO trailing newline (probed this round);
# round report worktree = CRLF-uniform with trailing newline (append worktree-faithful).
import json
import subprocess
import time
import datetime

NOW = datetime.datetime.now()
TS = NOW.strftime('%Y-%m-%d %H:%M:%S')
TS_T = NOW.isoformat(timespec='seconds')  # T-separated with offset (local tz)
EPOCH = int(time.time())

# ---- machine samples (psutil family; nvidia-smi for VRAM) ----
cpu_pct = 0.0
free_ram = 0.0
try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=0.5), 1)
    free_ram = round(psutil.virtual_memory().available / (1024 ** 3), 2)
except Exception as e:
    print('psutil sample failed:', e)
gpu_free = None
try:
    r = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
                       capture_output=True, text=True, timeout=10)
    if r.returncode == 0 and r.stdout.strip():
        gpu_free = round(float(r.stdout.strip().splitlines()[0]) / 1024, 2)
except Exception:
    pass

CUR_TASK = ('r339: T-91 launch-eve preflight all green (armed, Monday 09-28 first-marks); '
            'S6 33/33 rc=0 Sunday no-op family; CODELY 23rd-batch archival; '
            'idle-legal (pool busy = bm-b W2-A burn in flight 15:10+, board 0 open)')

# ---- 1) state-bm-a.json (LF, indent 1, no trailing NL) ----
sp = 'state-bm-a.json'
s = json.load(open(sp, encoding='utf-8'))
s['round_no'] = 339
s['did'] = ('R339: S0 autofill tick-state targeted commit + pull --rebase UU vs bm-c r91 same-file rewrite '
            'resolved via r91 union canon (launches union cap48 restore-2 + last_tick take-new) -> 79dd44b9 pushed '
            'same-window + orders 96/96 zero-unacked + decisions no-new-past-D-10 + smoke 25/25 + T-91 launch-eve '
            'preflight all green (anchor SIG/BARS-2026-09-24 on disk 09:52 bm-b, harness selftest 12/12, both '
            'accounts armed 1M entries=0 correct, scorecard pending_cohorts=1, ticket progress_r339) + new pitlaw '
            '(blob-side splice byte-count; v1 bare-CR caught in-flight by r338 churn-check law) + 23rd-batch '
            'in-window archival (r91 bmc + r339 bma fulls verbatim to archive, CODELY 10046B<10KB) + S6 33/33 rc=0')
s['verify'] = ('rebase clean 79dd44b9 onto 72bea1dd + pushed; resolver json.loads valid; harness selftest 12/12 '
               'legs PASS; prod run rc=0 idempotent armed; S6 chain 33/33 rc=0; verbatim+pointer asserts x4 PASS; '
               'CODELY/archive churn --stat 3+6 lines minimal')
s['next'] = ('R340+: (1) Mon 09-28 evening T-91 s3 first marks: bm-b exports BARS-2026-09-28 via git after panel '
             'update -> S6 sysv1 leg auto-consumes -> first cohort entries at 09-28 open (SIG-2026-09-24 Top10) -> '
             'marks auto-flow to all three report faces; (2) W2-A burn completion watch on bm-b -> UNC follow-up '
             'batch routing per sec.9.3; (3) 10-01 month trio standing; (4) moneyflow rank spawn + AH EM-mapping '
             'background watch; (5) C-01 council window 09-29 12:00')
s['last_round_at'] = TS
s['current_task'] = CUR_TASK
out = json.dumps(s, ensure_ascii=False, indent=1)
open(sp, 'wb').write(out.encode('utf-8'))
json.load(open(sp, encoding='utf-8'))
print('state written round_no=339')

# ---- 2) heartbeat fleet/machines/bm-a.json (LF, indent 1, no trailing NL) ----
hp = 'fleet/machines/bm-a.json'
h = json.load(open(hp, encoding='utf-8'))
h['last_seen'] = TS
h['current_task'] = CUR_TASK
h['cpu_pct'] = cpu_pct
h['free_ram_gb'] = free_ram
if gpu_free is not None:
    h['gpu_free_vram_gb'] = gpu_free
h['verdict'] = 'healthy'
h['heartbeat_epoch_utc'] = EPOCH
h['clock_read'] = TS_T
h['round_no'] = 339
assert isinstance(h['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
out = json.dumps(h, ensure_ascii=False, indent=1)
open(hp, 'wb').write(out.encode('utf-8'))
h2 = json.load(open(hp, encoding='utf-8'))
assert isinstance(h2['heartbeat_epoch_utc'], int) and 'T' in h2['clock_read']
print('heartbeat written epoch=%d clock=%s cpu=%s ram=%s gpu=%s' % (EPOCH, TS_T, cpu_pct, free_ram, gpu_free))

# ---- 3) round report append (worktree CRLF, trailing NL) ----
rp = 'logs/iteration-loop/round_reports-bm-a.md'
LINE = (TS + ' | r339 | 水位绿(lane=healthy red=false 17:25 probe py_low_board_clear 28min窗 avg 0.9%=法定idle白名单: '
        'board 0 open + 池 ready=1 但 lane_owner=bm-b W2-A 燃烧在途(15:10 pid13148 起·16:56 keepalive)+bandit '
        'claimed-await-panel) | 做了: S0 脏树=autofill tick no-op state 先定向 commit→pull --rebase 撞 bm-c r91 '
        '同文件整件重写=UU→r91 正典 union resolve(launches 48+2restored cap48+last_tick take-new 17:20 mine)→'
        '79dd44b9 即推占位 | S0.5: orders 96/96 零未回执(全扫差集)+decisions 无 D-10 后新行(D-04/D-09 维持)零新动作 '
        '| S1 smoke 25/25 | S3 主闭环=T-91 launch-eve preflight 全绿: 锚件在位(SIG/BARS-2026-09-24 bm-b 09:52 出)+'
        'harness selftest 12/12+prod rc=0 幂等 armed+双账户 1M entries=0 正确(入场日 bar=BARS-2026-09-28 周一晚 git 落)+'
        'scorecard pending_cohorts=1 armed-pending 披露+三报告面渲染复验→票面 progress_r339 落 | S4 新坑律: 共享 JSON '
        '字节拼接编辑取侧/去尾字节必按 blob 尾态(autocrlf 工作树 CRLF 假象·v1 b[:-2] 留裸 CR+整件假 churn 被 r338 '
        'churn 核验律当场捕获·v2 blob 重建正典)+二十三批当窗整编(r91 bmc stash-pop union 律+r339 bma 两全文入 archive '
        '行级零丢失·CODELY 10330→10046B<10KB) | S6 33/33 rc=0 周日 no-op 族(moneyflow rank spawn 在途/AH EM-mapping '
        'spawn 在途) | 验证: smoke 25/25+selftest 12/12+S6 33/33+json 校验×3+churn --stat 3+6 行+verbatim 断言×4 PASS+'
        'push 79dd44b9 clean | 下轮指针: (1) 周一 09-28 晚 T-91 s3 首批入场=BARS-2026-09-28 bm-b 出口 git 落后 S6 sysv1 '
        '腿消费→首 marks 流三报告面; (2) W2-A bm-b 燃烧完成观察→UNC 后续批 routing sec.9.3; (3) 10-01 月三件套; '
        '(4) moneyflow rank/AH EM-mapping spawn 回查; (5) C-01 council 窗 09-29 12:00')
b = open(rp, 'rb').read()
assert b.endswith(b'\r\n') and b.count(b'\r\n') > 500, 'report worktree expected CRLF-uniform'
b2 = b + LINE.encode('utf-8').replace('\n', '\r\n') + b'\r\n' if '\n' in LINE else b + LINE.encode('utf-8') + b'\r\n'
open(rp, 'wb').write(b2)
print('round report appended, %d -> %d' % (len(b), len(b2)))
