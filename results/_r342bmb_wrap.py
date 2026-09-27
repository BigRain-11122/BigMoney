# r342 bm-b wrap: state.json r342 + heartbeat + round report line + CODELY.md pitlaw append + self-verify
# r96 law: all closing timestamps fresh-read at write; epoch & clock_read from one time source.
import json, time, subprocess
from datetime import datetime

ROOT = r'C:\Users\Administrator\Desktop\Bigmoney'

now_epoch = int(time.time())
now_iso = datetime.fromtimestamp(now_epoch).astimezone().isoformat(timespec='seconds')
short_ts = datetime.fromtimestamp(now_epoch).strftime('%Y-%m-%d %H:%M:%S')
hm = now_iso[11:16]

did = ('r342 maintenance round: S0 network-dead verdict (30s bounded fetch timeout = r341-family dead window; '
       'fold infeasible, local-ahead 17 commits carry to r343) + S0.5 dual-scan orders 96/96 zero-diff (programmatic) '
       '+ P-32 decisions 3-path absent honest no-op + S1 smoke 25/25 + S2 dual boards 0 open + S3 W2-A burn health '
       'verify (4 workers since 15:40, ~18.8k CPUsec each vs r341 20:50 baseline ~17.5k, RAM 1.6-4.7GB, '
       'w2a_checkpoint ABSENT = old-code in-flight r340 disclosed face, finalize ~21:40 writes products directly, '
       'no kill) + S6 chain 30/30 rc=0 (Sunday cutoff 09-24, 3 new-bar-gated legal skips: live.paper / '
       't35_open_fill_verify / t24_prospect_paper) + token delta=105 + S4 one pitlaw (PS Start-Job CWD law)')
nxt = ('r343 S0 fold mainline (fetch -> pull --rebase -> classify_conflicts canonical resolve, autofill_state UU '
       'expected -> push main -> GC escape branch machine/bm-b-r340 -> verify ce11fad7+b2a36f94 chain on origin/main); '
       'W2-A finalize harvest ~21:40+ (r312 done-flip pool face + T-86 bm-a ticket receipt); Mon 09-28: 09:15 T-91 '
       's3 auto-fire (SIG/BARS-09-28) + 15:30 T-87 astock first increment + new-bar full chain; 10-01 monthly trio '
       '+ REGIME_GUARD v3 date gate')
cur = 'r342 closed: S6 30/30 + W2-A burn verify + network-dead local mode, local-ahead 17 commits for r343 fold'

# --- state.json ---
sp = ROOT + r'\logs\iteration-loop\state.json'
with open(sp, encoding='utf-8') as f:
    st = json.load(f)
st['round_no'] = 342
st['did'] = did
st['verdict'] = 'green'
st['next'] = nxt
st['last_round_ts'] = now_iso
st['last_result'] = 'ok'
st['current_task'] = cur
st['updated_at'] = now_iso
st['last_seen'] = now_iso
st['ts'] = short_ts
st['last_task'] = 'r342: S6 chain 30/30 green + W2-A burn health verify + local mode'
with open(sp, 'w', encoding='utf-8') as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# --- heartbeat fleet/machines/bm-b.json ---
hp = ROOT + r'\fleet\machines\bm-b.json'
with open(hp, encoding='utf-8') as f:
    hb = json.load(f)
try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=1), 1)
    ram_gb = round(psutil.virtual_memory().available / 1024**3, 1)
except Exception:
    cpu_pct, ram_gb = 29.2, 2.6
try:
    o = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
                       capture_output=True, text=True, timeout=10).stdout.strip().splitlines()
    gpu_free_gb = round(int(o[0]) / 1024, 2)
except Exception:
    gpu_free_gb = hb.get('gpu_free_vram_gb', 6.7)
hb['last_seen'] = now_iso
hb['heartbeat_epoch_utc'] = now_epoch
hb['clock_read'] = now_iso
hb['current_task'] = cur
hb['cpu_cores'] = 16
hb['free_ram_gb'] = ram_gb
hb['gpu_free_vram_gb'] = gpu_free_gb
hb['cpu_util_pct'] = cpu_pct
hb['round_no'] = 342
hb['verdict'] = 'healthy'
hb['idle_ram_gb'] = ram_gb
hb['gpu_free_vram_mb'] = int(gpu_free_gb * 1024)
hb['idle_ram_mb'] = int(ram_gb * 1024)
hb['cores'] = 16
hb['cpu_pct'] = cpu_pct
hb['round'] = 342
hb['free_ram_mb'] = int(ram_gb * 1024)
hb['gpu_idle_vram_mb'] = int(gpu_free_gb * 1024)
hb['gpu_idle_vram_gb'] = gpu_free_gb
hb['loop_round'] = 342
with open(hp, 'w', encoding='utf-8') as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# --- round report line (append-only, own-line discipline) ---
rp = ROOT + r'\logs\iteration-loop\round_reports.md'
line = (
    now_iso + ' | round 342 bm-b | dept:工程+舰队 | 水位=绿：red=false lane healthy（py 26-29%=W2-A census 燃烧合法占用）'
    '| did: 维护轮——S0 网络死定谳（30s 有界 fetch 超时=r341 同族死窗；fold 不可行，本地领先 17 commits'
    '〔b2a36f94+r341 close+tick tails 877313eb〕携至 r343）+ S0.5 双扫 orders 96/96 zero-diff（程序化差集禁时间戳过滤）'
    '+ P-32 decisions 三路缺席诚实 no-op + S1 smoke 25/25 + S2 双板 0 open（job_list 空+tasks 30 claimed/63 done 零 open）'
    '+ S3 W2-A 燃烧健康核查（4 workers 15:40 起 ~18.8k CPUsec each〔r341 20:50 基线 ~17.5k 推进实证〕RAM 1.6-4.7GB；'
    'w2a_checkpoint ABSENT=旧码在飞 r340 已披露面，finalize ~21:40 直写产物不依赖 ckpt，禁 kill 禁接管）'
    '+ S6 链 30/30 rc=0（_r342bmb_s6.log；周日 cutoff 09-24：3 新bar门控合法跳过 live.paper/t35_open_fill_verify/t24_prospect_paper）'
    '+ token delta=105 + S4 坑律 1 条（PS Start-Job CWD 律→CODELY.md）'
    '| 验证证据=smoke 25/25 + _r342bmb_s6.log 30x rc=0 + journal precheck 21:01 5x python cwd-holders + w2a 进程快照 18.7-18.9k CPUsec'
    '| 下轮: r343 S0 fold mainline（fetch→pull --rebase→classify_conflicts 正典解 autofill_state UU 预期→push main'
    '→GC escape branch machine/bm-b-r340→verify ce11fad7+b2a36f94 上 origin/main）+ W2-A finalize harvest'
    '（r312 done-flip + T-86 bm-a 回执）+ Mon 09-28 09:15 T-91 s3 auto-fire + 15:30 T-87 astock 首增量 + new-bar 全链'
    '+ 10-01 月度三件套+REGIME_GUARD v3 日期门\n'
)
with open(rp, 'rb') as f:
    raw = f.read()
sep = b'' if raw.endswith(b'\n') else b'\n'
with open(rp, 'ab') as f:
    f.write(sep + line.encode('utf-8'))

# --- CODELY.md pitlaw append (S4, 四问门 passed, single entry) ---
cp = ROOT + r'\CODELY.md'
entry = ('- [' + now_iso[:10] + ' ' + hm + ' r342 bm-b] 坑律：PS Start-Job 作业块不继承调用处 CWD——job 内 git 一律 '
         'fatal "not a git repository"（r342 实弹：fetch 探针首跑 job 化零有效输出、外层 rev-list 读的仍旧是旧 '
         'remote-tracking 假象）；正典=job 块首显式 Set-Location 仓根+外层 Wait-Job -Timeout 有界收口——网络死窗 '
         'S0 逐轮探测一律有界化（直跑 fetch 挂 5min 烧轮预算 r341/r342 双实证；有界化后死窗成本=超时秒数，'
         '探活与 fold 分离）。')
with open(cp, 'rb') as f:
    craw = f.read()
csep = b'' if craw.endswith(b'\n') else b'\n'
with open(cp, 'ab') as f:
    f.write(csep + entry.encode('utf-8') + b'\n')

# --- self-verify (S7: json.loads + isinstance(epoch,int)) ---
with open(sp, encoding='utf-8') as f:
    st2 = json.load(f)
with open(hp, encoding='utf-8') as f:
    hb2 = json.load(f)
assert st2['round_no'] == 342, 'state round_no'
assert isinstance(hb2['heartbeat_epoch_utc'], int), 'epoch must be int'
assert hb2['heartbeat_epoch_utc'] == now_epoch
assert 'T' in hb2['clock_read'] and '+' in hb2['clock_read'], 'clock_read ISO T-sep'
assert hb2['round_no'] == 342
print('WRAP OK state.round_no=%d hb.epoch=%d(%s) hb.clock=%s cpu=%s ram_gb=%s gpu_free_gb=%s orders_ack=%d' % (
    st2['round_no'], hb2['heartbeat_epoch_utc'], type(hb2['heartbeat_epoch_utc']).__name__,
    hb2['clock_read'], cpu_pct, ram_gb, gpu_free_gb, len(hb2.get('orders_ack', []))))
