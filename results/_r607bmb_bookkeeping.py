# r607 bm-b S7 bookkeeping -- heartbeat+round-report first, state bump LAST (r610 law);
# isoformat() clock (r603 strftime-H pit), epoch as native int, post-write self-verify.
import json, time, subprocess
from datetime import datetime

ROOT = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
now = datetime.now().astimezone()
clock_read = now.isoformat(timespec='seconds')  # guaranteed T separator + offset
epoch = int(time.time())

# --- resource probes ---
try:
    import psutil
    vm = psutil.virtual_memory()
    ram_avail = round(vm.available / (1024**3), 2)
    cpu_util = round(psutil.cpu_percent(interval=2), 1)
except Exception:
    ram_avail, cpu_util = 0.0, 0.0
try:
    out = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
                          capture_output=True, text=True, encoding='utf-8', errors='replace',
                          creationflags=0x08000000, timeout=20)
    gpu_free_mb = int(out.stdout.strip().splitlines()[0])
except Exception:
    gpu_free_mb = 0
gpu_free_gb = round(gpu_free_mb / 1024, 2)

# --- heartbeat (preserve all existing keys) ---
hp = ROOT + r'\fleet\machines\bm-b.json'
with open(hp, encoding='utf-8') as f:
    hb = json.load(f)
hb['last_seen'] = clock_read
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = clock_read
hb['round_no'] = 607
hb['round_no_label'] = 'round 607 (bm-b)'
hb['current_task'] = 'FUND-QUALITY-P1 burn phase: x2 in-flight (stale-claim takeover from bm-a, pid 56540) + value NULLS 68/2000 (pid 34396); QUALITY NULLS 2000 + SENS 500 queued; finalize on completion'
hb['verdict'] = 'round 607 done: MAIN PRODUCT = judged cell QUALITY-ROE x1 delivered to origin (cells 401 rows G-CENSUS bit-exact + cont face, commit bb0c81b87) + X2 stale-claim takeover from bm-a executed legit (claim 06:50 age 26min>20min + host dark since 06:36, commit 7c568ee0a, kill-advice MSG-0725-bma) + surgical S0 FF (14 stale derive faces -> origin-fresh, CODELY r606 line preserved +1/-0); S6 34/34 rc0; smoke 47/47; attrition CLEAN; dualrun streak 12; claws+loop pin+watchdog 4/4'
hb['ts'] = clock_read
hb['updated'] = clock_read
hb['updated_at'] = clock_read
hb['cpu_util_pct'] = cpu_util
hb['free_ram_gb'] = ram_avail
hb['idle_ram_gb'] = ram_avail
hb['ram_free_gb'] = ram_avail
hb['ram_avail_gb'] = ram_avail
hb['gpu_idle_vram_gb'] = gpu_free_gb
hb['gpu_idle_vram_mb'] = gpu_free_mb
hb['gpu_free_vram_gb'] = gpu_free_gb
hb['gpu_free_vram_mb'] = gpu_free_mb
hb['gpu_vram_free'] = gpu_free_gb
with open(hp, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(hb, f, indent=1, ensure_ascii=False)

# --- round report line (606 line already in file stays; append 607) ---
rp = ROOT + r'\logs\iteration-loop\round_reports.md'
line = (
    ' | ' + clock_read + ' | round 607 (bm-b) | '
    '水位 verdict=绿（red=false·loaded_ok 非红诚实面）｜当前活：QUALITY-ROE x2 在飞（pid 56540，接管自 bm-a）+ VALUE NULLS 68/2000 烧录中（pid 34396）｜最近实物：cells_QUALITY-ROE_x1.jsonl 401 行+cont 面（07:2x 上 origin，commit bb0c81b87）｜下个里程碑：x2 交付 ~07:45 后续 QUALITY NULLS 2000+SENS 500 点火，全批 finalize 于 NULLS 完成后（窗 ≤48h→10-05 晚） | '
    'S0 外科纯 FF（origin 领先 3：bm-c r400/401+bm-a tick；14 件陈旧 derive 面弃本地取 origin 新鲜面零损失，CODELY r606 坑律行字节保全回补 +1/-0）+ X1 产物交付 + X2 陈旧 claim 合法接管（bm-a claim 06:50:07 龄 26min>20min + 其心跳 06:36 后停+06:50 后零 commit=机器暗面；我 07:16:25 接管 commit 7c568ee0a 已推）+ kill-advice MSG-2026-10-03-0725-bmb-bma（r489③ 处置面） | '
    '验证：smoke 47/47；S6 34/34 rc0 零瞬态；attrition CLEAN；dualrun streak 12 ZERO-DRIFT；双爪字节一致 2/2+loop pin=2 正确+watchdog 在=4/4；token delta +372 report/+164 mandate/+0 state（L1 零 API）；本地未达 origin commit 数=0 | '
    '下轮指针：x2 烧录完成验收（401 行 G-CENSUS 对账+产物同轮推送）+ QUALITY NULLS/SENS 点火监护 + NULLS 进度（~32 行/h，ETA ~10-05）+ finalize 门监护；bm-a 复活时 X2 kill-advice 生效面回访'
)
with open(rp, 'a', encoding='utf-8', newline='\n') as f:
    f.write('\n' + line)

# --- state bump LAST ---
sp = ROOT + r'\state.json'
with open(sp, encoding='utf-8') as f:
    st = json.load(f)
st['round_no'] = 607
st['note'] = ('r607: (1) MAIN PRODUCT: FUND-QUALITY-P1 judged cell QUALITY-ROE x1 DELIVERED to origin '
              '(cells_QUALITY-ROE_x1.jsonl 401 census rows G-CENSUS bit-exact + cont face, commit bb0c81b87; '
              'done-flip was already origin-visible from daemon tick). (2) X2 stale-claim takeover from bm-a '
              'executed: bm-a claim 06:50:07 (0605a1a22) aged 26min>20min STALE_MIN + bm-a heartbeat dark since '
              '06:36:51 + zero bm-a commits after claim -> legit per r489/r601 (dual condition, NOT r603 wedge); '
              'my claim 07:16:25 commit 7c568ee0a pushed; burn pid 56540; kill-advice MSG-2026-10-03-0725-bmb-bma '
              'for bm-a revival (r489 step3). (3) VALUE NULLS burn healthy 68/2000 pid 34396 (~32 rows/h, ETA '
              '~10-05, inside 10-09 CEO window); QUALITY NULLS 2000 + SENS 500 queued behind x2. (4) S0 surgical '
              'pure-FF: 14 stale local derive faces discarded to origin-fresh (bm-c r401 fresher), CODELY r606 '
              'pit line preserved byte-exact via temp-file union (+1/-0 numstat assert). S6 34/34 rc0; smoke '
              '47/47; attrition CLEAN; dualrun streak 12; claws 4/4 + loop pin=2 + watchdog alive; orders '
              '150/150 double-scan zero unacked; D-19 K: absent honest skip (S4U, watermark 937A373D unchanged '
              'r597). Next: x2 delivery verify (~07:45) -> NULLS/SENS ignition watch -> batch finalize on '
              'completion (<=48h).')
st['last_round_at'] = 607
st['last_round_ts'] = clock_read
st['ts'] = clock_read
st['updated'] = clock_read
st['updated_at'] = clock_read
st['last_seen'] = clock_read
st['round_no_label'] = 'round 607 (bm-b)'
with open(sp, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(st, f, indent=1, ensure_ascii=False)

# --- post-write self-verify (r603 clock law + R170/R178 epoch-type law) ---
with open(sp, encoding='utf-8') as f:
    chk = json.load(f)
assert chk['round_no'] == 607, 'state round_no'
assert datetime.fromisoformat(chk['ts']).tzinfo is not None, 'state ts not ISO-parsable'
with open(hp, encoding='utf-8') as f:
    chb = json.load(f)
assert isinstance(chb['heartbeat_epoch_utc'], int), 'epoch must be int'
assert not isinstance(chb['heartbeat_epoch_utc'], bool), 'epoch must not be bool'
assert datetime.fromisoformat(chb['clock_read']) is not None, 'clock_read not ISO-parsable'
assert chb['round_no'] == 607
tail = open(rp, encoding='utf-8').read().rstrip('\n').split('\n')[-1]
assert 'round 607 (bm-b)' in tail, 'report tail line'
print('BOOKKEEPING OK: round=607 clock=' + clock_read + ' epoch=' + str(epoch) +
      ' ram_avail=' + str(ram_avail) + 'GB cpu=' + str(cpu_util) + '% gpu_free=' + str(gpu_free_gb) + 'GB')
