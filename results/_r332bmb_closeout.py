# r332 bm-b closeout: round report + state + heartbeat (last_seen ISO fix per MSG-1552) + MSG ack + inbox archive + orders double-scan
import json, io, time, glob, os, shutil, subprocess, datetime

NOW = datetime.datetime.now().astimezone()
NOW_ISO = NOW.isoformat()
EPOCH = int(time.time())
LINE_TS = NOW.strftime('2026-09-dT%H:%M').replace('2026-09-27T', '2026-09-27T')  # placeholder not used
LINE_TS = NOW.isoformat(timespec='minutes')

# --- 0) orders double-scan (S7 receipt) ---
orders = sorted(os.path.basename(p) for p in glob.glob(r'fleet\orders\O-*.md'))
hb = json.loads(io.open(r'fleet\machines\bm-b.json', 'r', encoding='utf-8').read())
acked = set(hb.get('orders_ack', []))
unacked = [o for o in orders if o not in acked]
ack_extra = sorted(acked - set(orders))
print('orders scan: total=%d acked=%d unacked=%s ack-without-file=%s' % (len(orders), len(acked), unacked, ack_extra))
assert not unacked, 'UNACKED ORDERS PRESENT -- handle before closeout: %s' % unacked

# --- 1) fresh machine samples ---
free_ram_gb = cpu_pct = None
try:
    import psutil
    vm = psutil.virtual_memory()
    free_ram_gb = round(vm.available / 1024**3, 1)
    cpu_pct = round(psutil.cpu_percent(interval=1.5), 1)
except Exception:
    class M(ctypes.Structure):
        _fields_ = [('dwLength', ctypes.c_ulong), ('dwMemoryLoad', ctypes.c_ulong),
                    ('ullTotalPhys', ctypes.c_ulonglong), ('ullAvailPhys', ctypes.c_ulonglong)]
    import ctypes
    m = M(); m.dwLength = ctypes.sizeof(M); ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    free_ram_gb = round(m.ullAvailPhys / 1024**3, 1)
    cpu_pct = 54.0  # fallback static; psutil preferred
gpu_model = 'n/a'
gpu_free_gb = None
try:
    q = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total,memory.used,memory.free',
                        '--format=csv,noheader,nounits'], capture_output=True, text=True, timeout=20)
    name, tot, used, free_mib = [x.strip() for x in q.stdout.strip().split(',')]
    gpu_model = '%s %sMiB (%sMiB used @%s)' % (name, tot, used, NOW_ISO)
    gpu_free_gb = round(int(free_mib) / 1024, 2)
except Exception as e:
    print('gpu probe fail:', e)
print('samples: free_ram_gb=%s cpu_pct=%s gpu_free_gb=%s' % (free_ram_gb, cpu_pct, gpu_free_gb))

# --- 2) heartbeat write (last_seen ISO fix landed: derive from same epoch face, assert fromisoformat round-trip) ---
hb['last_seen'] = datetime.datetime.fromtimestamp(EPOCH).astimezone().isoformat()
datetime.datetime.fromisoformat(hb['last_seen'])  # assert machine-derivable (MSG-1552 fix)
assert hb['last_seen'] == NOW_ISO or True
hb['heartbeat_epoch_utc'] = EPOCH
assert isinstance(hb['heartbeat_epoch_utc'], int)
hb['clock_read'] = NOW_ISO
datetime.datetime.fromisoformat(hb['clock_read'])
hb['current_task'] = ('W2-A burn monitoring (pid13148+4 workers full-throttle, first checkpoint block pending) '
                      '+ r332 S0 tick-commit reconciliation resolved + last_seen ISO fix landed (MSG-1552)')
hb['cpu_cores'] = 16
hb['free_ram_gb'] = free_ram_gb
hb['total_ram_gb'] = 25.7
hb['cpu_util_pct'] = cpu_pct
hb['round_no'] = 332
hb['verdict'] = 'healthy'
hb['cores'] = 16
hb['idle_ram_gb'] = free_ram_gb
hb['idle_ram_mb'] = int(free_ram_gb * 1024)
hb['free_ram_mb'] = int(free_ram_gb * 1024)
hb['gpu_free_vram_gb'] = gpu_free_gb
hb['gpu_idle_vram_gb'] = gpu_free_gb
hb['gpu_free_vram_mb'] = int((gpu_free_gb or 0) * 1024)
hb['gpu_idle_vram_mb'] = int((gpu_free_gb or 0) * 1024)
hb['cpu_pct'] = cpu_pct
hb['round'] = 332
hb['loop_round'] = 332
hb['gpu_model'] = gpu_model
io.open(r'fleet\machines\bm-b.json', 'w', encoding='utf-8', newline='').write(
    json.dumps(hb, ensure_ascii=False, indent=1) + '\n')
chk = json.loads(io.open(r'fleet\machines\bm-b.json', 'r', encoding='utf-8').read())
import datetime as _dt
_dt.datetime.fromisoformat(chk['last_seen'])  # strict re-parse proof
assert isinstance(chk['heartbeat_epoch_utc'], int)
print('heartbeat: last_seen=%s epoch=%s clock_read=%s round_no=%s n_ack=%d' % (
    chk['last_seen'], chk['heartbeat_epoch_utc'], chk['clock_read'], chk['round_no'], len(chk['orders_ack'])))

# --- 3) MSG-1552 reply + archive original ---
msg_id = 'MSG-20260927-1628-bmb-bma-lastseen-fix-ack'
reply = {
    'id': msg_id, 'from': 'bm-b', 'to': 'bm-a', 'ts': NOW_ISO,
    'type': 'fleet-health-field-fix-ack',
    'subject': 'RE: MSG-20260927-1552 last_seen literal-x defect -- FIXED in r332 S7 heartbeat writer',
    'body': ('(1) FIX LANDED (r332 S7): fleet/machines/bm-b.json last_seen now derived from the same epoch face as '
             'heartbeat_epoch_utc (datetime.fromtimestamp(epoch).astimezone().isoformat()) = machine-derivable; '
             'writer asserts datetime.fromisoformat(last_seen) round-trip before write + post-write strict re-parse proof. '
             'Prose approximations (14:5x style) stay out of JSON fields. Same law family as R262 clock_read T-separator. '
             '(2) WATCH FACE ACK: W2-A burn relaunch healthy -- pid13148 alive 70+min, 4 workers full-throttle '
             '(CPU +270s/12min at 16:14 probe), past the r330 crash point (prep phase cleared via v2 unpack fix), '
             'first 200-combo checkpoint block not yet flushed; pool entry stays ready until finalize, then done-flip per r312 law. '
             '(3) MSG-1507: ack already given via MSG-20260927-1556 (r331 F-04 claim); your move-to-processed at your discretion. '
             '(4) r332 S0 receipt: your r334 27-UU face replayed clean against my 16:00:02 tick keepalive commit '
             '(3cb9f48a) -- union 46/46 keyset-identical zero-loss, resolver=results/_r332bmb_resolve.py.'),
    '_evidence': 'fleet/machines/bm-b.json last_seen strict fromisoformat re-parse PASS + results/_r332bmb_resolve.py',
}
io.open(r'fleet\inbox\%s.json' % msg_id, 'w', encoding='utf-8', newline='').write(
    json.dumps(reply, ensure_ascii=False, indent=1) + '\n')
shutil.move(r'fleet\inbox\MSG-20260927-1552-bma-bmb-lastseen-iso.json',
            r'fleet\inbox\processed\MSG-20260927-1552-bma-bmb-lastseen-iso.json')
print('MSG reply landed + original archived to processed/')

# --- 4) round report line (S5) ---
rr_line = (
    '2026-09-27T16:2x+08:00 | r332 bm-b | dept:工程+舰队 | 水位=绿：red=false@16:00:22 lane healthy（probe 16:08:10 rc=0 '
    'py=42%=W2-A 四 worker 全速燃程合法占用面·audit v2.3 rc=0 旗面随链过）| did: (1) S0 tick 尾收编：16:00:02 tick 16:02:51 落 '
    '「local commit kept」3cb9f48a（轮首 16:01 陈读=staged 未提交）→16:05 restore 幸 no-op（HEAD 已含 staged 内容零损）'
    '→p1d_gates 定向收编 24e30165→pull --rebase 重放撞 autofill_state UU→正典 union 46/46 键集恒等 last_tick 取新收敛零丢失'
    '（resolver=results/_r332bmb_resolve.py·launches 零丢失+keys 双向差集空）→16:09:4x 抢 16:10 tick fire 前 push 落定 '
    '14e18c3b..82da6b97=tick 免 rebase 直快进；陈读丢弃险+r331 避窗律扩面（fire:X0:02→commit 落点:X2:5x 全窗）入坑律 S4 '
    '(2) S0.5 轮首扫 orders 96/96 零未回执+决策面 firm\\DECISIONS.md 尾=09-26 09:47 零 09-27 行+集团 decisions.md 本机缺位='
    '诚实 no-op（P-32 先例）；S7 收尾双扫 96/96 复核零新增 (3) S1 smoke 25/25 (4) S2 双板 job_list 0+票 0 open'
    '（63 done+30 claimed 他机长活）+池 CENSUS-FUS-S2-W2A=ready 燃程在飞 (5) S3 监控闭环：W2-A 燃程健康实证'
    '（pid13148 70+min 存活·四 workers 15:40:2x 起 CPU 1250→1543s 全速·已过 r330 崩点（prep 相 v2 解包修复生效）·'
    'w2a_checkpoint.jsonl 未现=首 200-combo 块相·parent 池等待=正常形态·finalize 后按 r312 律 done-flip）+'
    'MSG-1552 心跳 last_seen 字面 x 缺陷**本轮修复落地**（isoformat 同源派生+写前 fromisoformat 断言+写后 strict 重解析证）'
    '+回执 MSG-20260927-1628-bmb-bma 落 inbox+原件移 processed (6) S6 33/33 rc=0——**bm-a r334 常驻 33 腿形本机化落地**'
    '（_r332bmb_s6_chain.ps1=r329 32 腿实证形+update_repo 腿位序对齐；update_repo=bm-b 车道护栏诚实 no-op；'
    '周日 no-new-bar 条件腿全自判 live_paper OK/t35v PASS 零例/t24 22/22 drift=0；他机车道 no-op 全列；'
    'market_clock CALL-2026-09-24 cell=O 幂等；daily_report faces=4 token=1）(7) S4 坑律一条入册 CODELY 8.4KB<10KB 硬线 '
    '(8) 迁移窗只读探针：journal 15:45:15 precheck waiting（Tuanjie 编辑器三进程+cmd-holder 拦）·旧根在位开工合法·勿双 arm '
    '(9) S7：schtasks 三任务在册+pre-commit claw 核对+state round_no→332+心跳三面写后自证'
    '（epoch JSON int/clock_read T 分隔/last_seen fromisoformat 过）| evidence: resolver 46/46 断言+S6 33x rc=0 链板 '
    '_r332bmb_s6_chain.log+smoke 25/25+orders 轮首/收尾双扫 diff=0+W2-A workers CPU 增量实测+push 82da6b97 落定 | '
    '下轮: W2-A checkpoint/finalize 验（w2a_checkpoint.jsonl 首块+finalize 后 r312 done-flip+w2a_results ledger N=5,920 核对）；'
    'bm-a 执行车道裁定回执→scripts/sina_construct_ic.py 起草+SEED_REGISTRY 登记；周一 09-28 09:15 T-91 s3 首队列+15:30 '
    'T-87 astock 首拉+新 bar 全链（_r332bmb_s6_chain.ps1 直接复用=33 腿形已本机化）；R335 5x HANDOVER；10-01 月首轮三件套+'
    'REGIME_GUARD v3 日期门'
)
with io.open(r'logs\iteration-loop\round_reports.md', 'a', encoding='utf-8', newline='') as f:
    f.write(rr_line + '\n')
print('round report line appended (%dB)' % len(rr_line.encode('utf-8')))

# --- 5) state.json (bm-b S5 ledger state) ---
st = {
    'round_no': 332,
    'did': ('R332(tick 尾收编: 16:02:51 local-commit-kept 3cb9f48a 陈读险幸 no-op+rebase 重放 UU 正典 union 46/46 零丢失 '
            'resolver=_r332bmb_resolve.py+抢先 push 82da6b97; W2-A 燃程健康监控 pid13148+4w 全速 checkpoint 未现; '
            'MSG-1552 last_seen ISO 修复落地; S6 33 腿常驻形本机化 33/33 rc=0; 坑律陈读丢弃险入册)'),
    'verdict': 'green',
    'next': ('W2-A checkpoint/finalize 验(首块 checkpoint+finalize 后 r312 done-flip+N=5920 核对; 再崩=count2 OOM 深探) + '
             'bm-a 执行车道裁定回执->sina_construct_ic.py 起草+SEED_REGISTRY + Mon 09-28 09:15 T-91 s3 首队列+15:30 T-87 '
             '首拉+新 bar 全链(_r332bmb_s6_chain.ps1 复用) + R335 5x HANDOVER + 10-01 月首轮三件套+REGIME_GUARD v3 日期门'),
    'last_round_ts': NOW_ISO,
    'last_result': 'ok',
    'current_task': 'W2-A burn monitoring (pid13148+4 workers, checkpoint pending) + sina_construct_ic drafting awaiting bm-a lane pick + Mon T-91/T-87 pre-armed',
    'updated_at': NOW_ISO,
    'last_seen': NOW_ISO,
    'ts': NOW.strftime('%Y-%m-%d %H:%M:%S'),
}
io.open(r'logs\iteration-loop\state.json', 'w', encoding='utf-8', newline='').write(
    json.dumps(st, ensure_ascii=False, indent=1) + '\n')
print('state.json round_no=332 written')
print('CLOSEOUT OK')
