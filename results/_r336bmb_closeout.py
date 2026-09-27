# _r336bmb_closeout.py -- S5 round-ledger line + state.json r336 + heartbeat three-face
# self-verification (epoch JSON int / clock_read T-separator / last_seen isoformat).
import datetime
import io
import json
import subprocess

NOW = datetime.datetime.now().astimezone()
ISO = NOW.isoformat(timespec='seconds')          # 2026-09-27T17:5x:xx+08:00
EPOCH = int(NOW.timestamp())
TS = NOW.strftime('%Y-%m-%d %H:%M:%S')

REPORT_LINE = (
    '2026-09-27T17:5x+08:00 | r336 bm-b | dept:工程+舰队 | 水位=绿：red=false@17:30:21 lane healthy'
    '（probe 17:52 py=28.3% py_low_with_work_cands=合法白名单：W2-A census burn 自家 claim 在飞 0of1 keepalive 17:40'
    '+板全闭环 0 open+bandit 空+RAM<4GB 禁新重活 r335 HANDOVER 令 r336 遵守）'
    '| did: (1) **S0 落链使命达成**：machine/bm-b-r335 折链 8 pick 两程 rebase 落 origin/main 21d1ab80'
    '（push#1 拒=轮中 bm-a r340 4837c841 同窗 churn→pull --rebase 二程 4 停点全正典解：'
    'resolver v3=results/_r336bmb_resolve.py UU 门控+UNKNOWN 闸+自 add+bare-CR churn 检——'
    '6 面 r334 重放（CODELY 条目粒度 oa-filter D-09 合规+1 块/archive 直拼/autofill union 48 cap50/'
    'compute 226==|A∪B|/regime asof/x2 858→864 行级零丢失）+15 面 r335 重放（21 take_new 深探 ts 取新+union 226）'
    '+HANDOVER anchor-insert 手解（r210 律：bm-a r340 origin 先落保位+r335 增量插锚前）+3 autofill tick 面 union；'
    '17:48:31 抢 17:50:02 tick fire 前 push 落定=零 tick 竞态零 claw 拦截）'
    '(2) **GC 使命**：machine/bm-b-r334+r335 双支 R323 内容锚核全 PASS（missing=0+7 锚点+cherry 打头阵）'
    '→远端双支已删除'
    '(3) S0.5 orders 96/96 python 名集双向差零未回执（R13 律）+decisions 本机不可达 r334 定谳维持'
    '+bm-a r339/340+bm-c r92 双机代审 D-20260927-01~10 零新动作'
    '(4) S1 smoke 25/25 (5) S2 双板 0 open/93 全 claimed+job_list 空'
    '(6) **CODELY 二十五批当窗整编**：fold 后 13400B>≤10KB 硬线→11 行 verbatim 外迁 archive 二十五批节'
    ' 9872B≤10KB 达线（r334 asof 全文先验 23 批在档再删+r91 短指针字段并核+严格子集去重 r88 先例）'
    '(7) S6 29/29 rc=0 周日族（25 腿 rc=0：audit CLEAN/probe/update_daily cutoff 09-24/regime ORANGE shadow/'
    'scorecard S2A4 best VOLATILITY-CE-01 87.0/market_clock CALL-09-24 ORANGE_COOL 幂等/车道护栏诚实 no-op 8 面/'
    'aggr-alloc-grid 纸盘幂等/astock panel fresh/rev_osc SIG cutoff 幂等/t35_export 再生/daily_report faces=4 token=1'
    '+4 新 bar 腿诚实跳过：live.paper/t35v/t24x2）'
    '(8) S7：tick 17:50 自提交 bd33e67e 收讫+state round_no→336+心跳三面自证+inbox 零未读'
    '| evidence: resolver v3 断言面×4 停点+GC-VERIFY-PASS+CODELY 9872B≤10240 断言+archive verbatim 全查'
    '+S6 25x rc=0+smoke 25/25+orders 双向差空+push 21d1ab80 落定+双支删除回执'
    '| 下轮: 周一 09-28 09:15 T-91 s3 自动点火（SIG/BARS-2026-09-28 到位即重放）+15:30 T-87 astock 首续拉'
    '+新 bar 全链接力（update_daily→live.paper REGIME_GUARD v3 enforce 首跑→t35v→t24×2→aggr 20 账→grid 5 账首拍'
    '→export→scorecard→daily_report）；W2-A census burn 收割 watch（0of1@3.5h·3-6h est·r312 done-flip）；'
    '开发队列 J12 总控v2公司小镇 CEO 点名面恢复；R340 5x HANDOVER bm-b 侧；10-01 月首轮三件套+REGIME_GUARD v3 日期门')

# ---- 1. round report append (EOL mirror) ----
RP = 'logs/iteration-loop/round_reports.md'
rb = open(RP, 'rb').read()
eol = '\r\n' if rb.count(b'\r\n') and rb.count(b'\r\n') >= (rb.count(b'\n') - rb.count(b'\r\n')) else '\n'
assert rb.endswith(eol.encode()), 'report EOL tail expected'
assert 'r336 bm-b' not in rb.decode('utf-8'), 'r336 line already present (double-append guard)'
with io.open(RP, 'ab') as f:
    f.write((REPORT_LINE + eol).encode('utf-8'))

# ---- 2. state.json r336 ----
SP = 'logs/iteration-loop/state.json'
sb = open(SP, 'rb').read()
seol = '\r\n' if sb.count(b'\r\n') and sb.count(b'\r\n') >= (sb.count(b'\n') - sb.count(b'\r\n')) else '\n'
st = json.loads(sb.decode('utf-8'))
assert st['round_no'] == 335, f"expected state at 335, found {st['round_no']}"
st.update({
    'round_no': 336,
    'did': 'S0 fold-landing mission COMPLETE: r335 escape-valve chain (8 picks, two rebase passes) landed onto origin/main 21d1ab80; 4 stops canonical-resolved (resolver v3 UU-gated/UNKNOWN-gate/self-add/bare-CR churn-check; HANDOVER anchor-insert r210); GC machine/bm-b-r334+r335 both content-verified (R323 anchors) and remote-deleted; CODELY 25th-batch in-window archival 13400->9872B<=10KB; S6 29/29 rc=0 Sunday family',
    'verdict': 'green',
    'next': 'Mon 09-28: T-91 s3 auto-fire 09:15 (SIG/BARS-2026-09-28 replay) + T-87 astock first increment 15:30 + new-bar full chain relay (live.paper REGIME_GUARD v3 enforce first run); W2-A census burn harvest watch (r312 done-flip); resume dev queue J12; R340 5x HANDOVER bm-b side; 10-01 monthly trio',
    'last_round_ts': ISO,
    'last_result': 'ok',
    'current_task': 'r336 closed: fold landed + branches GC-ed + CODELY under hard line',
    'updated_at': ISO,
    'last_seen': ISO,
    'ts': TS,
})
with io.open(SP, 'wb') as f:
    f.write(json.dumps(st, ensure_ascii=False, indent=1).replace('\n', seol).encode('utf-8'))

# ---- 3. heartbeat fleet/machines/bm-b.json ----
HP = 'fleet/machines/bm-b.json'
hb = open(HP, 'rb').read()
heol = '\r\n' if hb.count(b'\r\n') and hb.count(b'\r\n') >= (hb.count(b'\n') - hb.count(b'\r\n')) else '\n'
h = json.loads(hb.decode('utf-8'))
try:
    import psutil
    vm = psutil.virtual_memory()
    free_gb = round(vm.available / 1024 ** 3, 1)
    cpu_pct = psutil.cpu_percent(interval=1)
except Exception:
    free_gb, cpu_pct = h.get('free_ram_gb'), h.get('cpu_util_pct')
gpu_free_mb = h.get('gpu_free_vram_mb', 6923)
try:
    q = subprocess.run(['nvidia-smi', '--query-gpu=memory.free,memory.used,name', '--format=csv,noheader,nounits'],
                        capture_output=True, text=True, timeout=10)
    if q.returncode == 0:
        parts = q.stdout.strip().splitlines()[0].split(',')
        gpu_free_mb = int(round(float(parts[0])))
        gpu_used_mb = int(round(float(parts[1])))
        h['gpu_model'] = f"{parts[2].strip()} ({gpu_used_mb}MiB used @{ISO})"
except Exception:
    pass
h.update({
    'last_seen': ISO,
    'heartbeat_epoch_utc': EPOCH,
    'clock_read': ISO,
    'current_task': 'r336 closed: fold landed origin/main 21d1ab80 + GC r334/r335 branches + CODELY 25th-batch 9872B',
    'round_no': 336,
    'loop_round': 336,
    'round': 336,
    'free_ram_gb': free_gb,
    'idle_ram_gb': free_gb,
    'free_ram_mb': int(free_gb * 1024),
    'idle_ram_mb': int(free_gb * 1024),
    'cpu_util_pct': cpu_pct,
    'cpu_pct': cpu_pct,
    'gpu_free_vram_mb': gpu_free_mb,
    'gpu_free_vram_gb': round(gpu_free_mb / 1024, 2),
    'gpu_idle_vram_mb': gpu_free_mb,
    'gpu_idle_vram_gb': round(gpu_free_mb / 1024, 2),
    'verdict': 'healthy',
})
with io.open(HP, 'wb') as f:
    f.write(json.dumps(h, ensure_ascii=False, indent=1).replace('\n', heol).encode('utf-8'))

# ---- 4. three-face self-verification ----
h2 = json.loads(open(HP, 'rb').read().decode('utf-8'))
assert isinstance(h2['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
assert 'T' in h2['clock_read'] and '+' in h2['clock_read'], 'clock_read must be T-separated ISO8601'
datetime.datetime.fromisoformat(h2['last_seen'])
assert h2['round_no'] == 336 and len(h2['orders_ack']) == 96
st2 = json.loads(open(SP, 'rb').read().decode('utf-8'))
assert st2['round_no'] == 336
rp2 = open(RP, 'rb').read().decode('utf-8')
assert 'r336 bm-b' in rp2
print('closeout OK: report-line appended, state r336, heartbeat epoch=%d(int) clock=%s ram_free=%sGB cpu=%s%% gpu_free=%sMB ack=96' % (
    h2['heartbeat_epoch_utc'], h2['clock_read'], free_gb, cpu_pct, gpu_free_mb))
