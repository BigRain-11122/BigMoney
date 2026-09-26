# -*- coding: utf-8 -*-
"""r294 bm-b S5+S7 wrap: state.json round 294, round report line, heartbeat w/ F7 self-proof."""
import io, json, time, datetime as dt, os, ctypes, re, psutil

now = dt.datetime.now().astimezone()
now_iso = now.isoformat()

# ---------- S5: state.json ----------
sp = 'logs/iteration-loop/state.json'
s = json.load(io.open(sp, encoding='utf-8-sig'))
s['round_no'] = 294
s['did'] = ('S0 fold autofill owned dirt pre-commit r290 law then pull up-to-date; S0.5 orders 91/91 zero unacked '
            '(group direct-scan face unreachable on bm-b per R291, mirror full-coverage); S1 smoke 25/25; '
            'S3 closed loop: r282 helper zombie PID 7828 triaged (0 CPU 3.5h, 0 threads, kill-denied, PEB readable '
            '= stuck termination rundown) its CWD lock blocked migration Gate 0.5 precheck -> self-resolved 03:52:36 '
            'per journal, Bigmoney-tree cwd blocker face cleared; T-87 re-probe 3111/5228=59.5% zero failures; '
            'S6 30/30 legs rc=0 weekend honest no-ops')
s['verdict'] = 'green'
s['next'] = ('T-87 pass-completion re-probe after ETA (gate auto: panel complete flip = bm-a wave-2 unlock); '
             '09-28 Monday new-bar full chain; migration window v2.2 armed to 09-29 12:00 executor domain')
s['current_task'] = 'r294 honest maintenance round (zombie-orphan migration-precheck unblock + T-87 supply watch)'
s['last_round_ts'] = now_iso
s['updated_at'] = now_iso
io.open(sp, 'w', encoding='utf-8', newline='').write(json.dumps(s, ensure_ascii=False, indent=1))

# ---------- S5: round report one-line append ----------
line = (now_iso + ' | r294 bm-b | dept:工程+舰队 | WM-VERDICT: 绿(red=false healthy; probe 03:54:16 '
        'verdict=insufficient_history 窗样本未满非红; 03:43 py_low_with_work_cands 过渡态点名=T-87 采集批 2.5s/股'
        '网络限速结构性低 CPU 非违令+池 54/54 done+板 0 open+bandit 0 合法) | did: S0 autofill 自有脏先行并入 '
        'commit(r290 自提交律 cef5785d)→pull --rebase up-to-date; S0.5 orders 91/91 轮首扫零未回执+集团 '
        'decisions.md/orders.md 直扫面 bm-b 无集团仓不可达如实注记(R291 律·镜面全覆盖); S1 smoke 25/25; S2 板 0 '
        'open+job_list 0+水位绿; S3 闭环=r282 助手孤儿 PID 7828 定性(0 CPU 3.5h·0 线程·Stop-Process/taskkill 双拒'
        '·PEB 可读=rundown 卡死态)其 CWD 锁曾阻迁移 Gate 0.5 预检→03:52:36 rundown 完成自解 journal 定谳=Bigmoney '
        '树 cwd 阻塞面清零(剩 Tuanjie 编辑器用户面+T-87 自清+执行器自行 28696)+T-87 复探 3111/5228=59.5%@03:55 '
        '零失败 attempts 7 隔离·ETA 修订窗 06:40-09:30; S6 30/30 legs rc=0(复用 r292 runner·周末诚实 no-op·regime '
        'ORANGE shadow·fundamental 5.6h skip·T-87 lock-alive no-op·bm-a/bm-c 车道 stdout-only·daily_report 周日面 '
        'faces=4); S4 CODELY +1 坑律(助手孤儿) 8.8KB<10KB | evidence: fluxgroup-migration-journal.log '
        '03:51:35→03:52:36 两行+results/_r294bmb_s6_chain.log 30/30 rc=0+smoke 25/25+results/'
        'astock_daily_update_status.json ts 03:54:42 lock-alive | next: T-87 完成后 pass-completion 复探(gate 自动·'
        'panel complete 翻面=bm-a wave-2 解锁)·09-28 周一开市新 bar 全链接力·迁移窗 v2.2 armed 至 09-29 12:00 '
        '执行器域勿动勿双 arm')
with io.open('logs/iteration-loop/round_reports.md', 'a', encoding='utf-8', newline='') as f:
    f.write('\n' + line + '\n')

# ---------- S7: heartbeat bm-b ----------
class Mem(ctypes.Structure):
    _fields_ = [('dwLength', ctypes.c_ulong), ('dwMemoryLoad', ctypes.c_ulong),
                ('ullTotalPhys', ctypes.c_ulonglong), ('ullAvailPhys', ctypes.c_ulonglong),
                ('ullTotalPageFile', ctypes.c_ulonglong), ('ullAvailPageFile', ctypes.c_ulonglong),
                ('ullTotalVirtual', ctypes.c_ulonglong), ('ullAvailVirtual', ctypes.c_ulonglong),
                ('ullAvailExtendedVirtual', ctypes.c_ulonglong)]
m = Mem()
m.dwLength = ctypes.sizeof(Mem)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))

p = 'fleet/machines/bm-b.json'
d = json.load(io.open(p, encoding='utf-8'))
orders = sorted(f for f in os.listdir('fleet/orders') if re.match(r'^O-.*\.md$', f))
d['machine_id'] = 'bm-b'
d['role'] = 'compute-node'
d['last_seen'] = now_iso
d['heartbeat_epoch_utc'] = int(time.time())
d['clock_read'] = now_iso
d['current_task'] = ('r294 honest maintenance green (smoke 25/25, S6 30/30, orders 91/91, zero P0); '
                     'r282 zombie orphan cwd-hold cleared from migration precheck 03:52:36; '
                     'T-87 supply 59.5% in flight ETA 06:40-09:30')
d['cpu_cores'] = os.cpu_count()
d['free_ram_gb'] = round(m.ullAvailPhys / 1e9, 1)
d['total_ram_gb'] = round(m.ullTotalPhys / 1e9, 1)
d['cpu_util_pct'] = round(psutil.cpu_percent(interval=0.4), 1)
d['round_no'] = 294
d['verdict'] = 'green'
d['orders_ack'] = ' '.join(orders)
io.open(p, 'w', encoding='utf-8', newline='').write(json.dumps(d, ensure_ascii=False, indent=1))

# post-write self-proof (smoke F7 face)
d2 = json.load(io.open(p, encoding='utf-8'))
assert isinstance(d2['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
assert 'T' in d2['clock_read'], 'clock_read must be T-separated'
print('state round_no=294; report appended; heartbeat ok: epoch=', d2['heartbeat_epoch_utc'],
      'clock=', d2['clock_read'], 'orders_ack n=', len(d2['orders_ack'].split()))
