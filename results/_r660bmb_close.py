# r660 bm-b close: round report append (bytes mode r641 law) + state.json + heartbeat, all programmatic with self-verify
import json, time, subprocess, os

now_iso = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
round_no = 660

# 1) round report append (mixed-encoding history file -> bytes mode, newline='' law)
rr_path = 'logs/iteration-loop/round_reports.md'
line = (
 f"{now_iso}｜round {round_no} (bm-b)｜watermark verdict=GREEN (red=false·engine alive rc0 idle·dualrun streak 51·py 56-86% 三族烧批占用合法)｜"
 f"黄金周值守轮: S0 FF-merge origin bm-c r457 波（QUALITY 池行手术+MSG-0915）零UU（树脏∩origin 交集空·r437 律）｜"
 f"S0.5 令双扫 153/153 零差+D-19 双 MATCH 零消费（subprocess 原字节 decisions=EB14B510/orders=82A0CEF9；PS 管道转码假 CHANGED 8019f543 当场证伪 r641 律→探针假警双面坑律入 CODELY）｜"
 f"S1 smoke 48/48｜S2 板零 open 票·job_list 空｜S3 门全绿（post_review 官方面 ✓45/✗0/🟡5 零活红·next_pick moneyflow IC claimed 他机不碰·常设线由在飞 trio 烧批满足）｜"
 f"MSG-0915 回执：QUALITY burner pid 57116 CIM 实活（10-03 07:26 起）·nulls 513→515 增长·池行 owner=bm-b 复归确认·keepalive 收养=09:21:39 age>10min 门后首 tick 预期落地（下轮首查）｜"
 f"trio readiness 09:18：V674/Q515/D373 of 2000 dup_k=0 全族·ETA Q 72.5h≈10-07 晨（长杆）/V 56h/D 27.1h 全落 finalize 窗 10-05..10-09·mechanical_ready=false·G4 PENDING（sha 未动）｜"
 f"S6 38/38 rc0（audit CLEAN burning-healthy·pool_ready_unclaimed 1→0 手术生效实证·LHB 30min 节流 no-op·REPORT/LIVE-20261004 幂等刷新）｜"
 f"S7 loop pin=2 no-op+watchdog 注册+双爪 installed+attrition 4 ledger CLEAN｜"
 f"证据=_r660bmb_quality_check.py（pid/池行/行数三验）+_r660bmb_d19_verify.py（原字节双 MATCH）+_r660bmb_s6_log.txt（38rc0）+finalize_trio_readiness.json（09:18）+_attrition_guard_scan.json（CLEAN）｜"
 f"下轮指针：trio 烧尽 mechanical_ready→finalize+E1 判决批（窗 10-05..10-09·Q 长杆 ETA~10-07 晨·r638 fallback armed）；下轮首查=QUALITY keepalive 收养 commit（未落地则查 autofill 日志定位，勿重戳池行 r626d ② 律）｜"
 f"本地未达 origin commit 数=0（commit 后 push_verify 自证）｜token 零云端"
)
with open(rr_path, 'ab') as f:
    f.write(b'\n')
    f.write(line.encode('utf-8'))
    f.write(b'\n')

# 2) state.json programmatic write (r645 law)
st_path = 'state.json'
st = json.load(open(st_path, encoding='utf-8'))
st['round_no'] = round_no
st['round_no_label'] = f'round {round_no} (bm-b)'
st['note'] = ("r660: golden-week watch round -- S0 FF-merge bm-c r457 QUALITY pool-surgery wave zero UU; "
              "D-19 double MATCH zero-consume (subprocess raw-bytes; PS-pipe false CHANGED disproven in-round, r660 pitlaw to CODELY); "
              "MSG-0915 receipt: burner pid 57116 CIM-alive (since 10-03 07:26), pool row owner=bm-b restored, nulls 513->515 growing, "
              "keepalive self-adoption expected first tick after 09:21:39 age-gate (first-check next round); "
              "trio readiness 09:18 V674/Q515/D373 dup_k=0, ETA Q 72.5h long-pole all in finalize window 10-05..10-09; "
              "S6 38/38 rc0 (dualrun streak 51, audit CLEAN, pool_ready_unclaimed 1->0); "
              "S7 four-piece green + attrition CLEAN")
st['last_round_at'] = now_iso
st['ts'] = now_iso
st['updated'] = now_iso
st['last_seen'] = now_iso
st['clock_read'] = now_iso
with open(st_path, 'w', encoding='utf-8', newline='') as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# 3) heartbeat (fresh machine sample)
import psutil
cpu_pct = psutil.cpu_percent(interval=1.0)
vm = psutil.virtual_memory()
free_ram = round(vm.available / (1024 ** 3), 2)
py_cpu = 0.0
for p in psutil.process_iter(['name', 'cpu_percent']):
    try:
        if (p.info['name'] or '').lower().startswith('python'):
            py_cpu += p.info['cpu_percent'] or 0.0
    except Exception:
        pass
gpu_free = None
try:
    o = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
                       capture_output=True, text=True, timeout=10)
    gpu_free = round(float(o.stdout.strip().splitlines()[0]) / 1024, 2)
except Exception:
    pass
hb_path = 'fleet/machines/bm-b.json'
hb = json.load(open(hb_path, encoding='utf-8'))
hb['last_seen'] = now_iso
hb['heartbeat_epoch_utc'] = int(time.time())
hb['clock_read'] = now_iso
hb['round_no'] = round_no
hb['round_no_label'] = f'round {round_no} (bm-b)'
hb['current_task'] = ("当前活: FUND trio NULLS 烧录在飞 V674/Q515/D373 of 2000（dup_k=0，烧录进程 CIM 实活；MSG-0915 回执：QUALITY 池行 owner=bm-b 已由 bm-c r457 手术复归 + burner pid 57116 实活验证，keepalive 自收养 09:21:39 age 门后首 tick 预期落地） | "
                      "最近实物: results/finalize_trio_readiness.json 09:18 刷新（三族 ETA 全落 finalize 窗 10-05..10-09，Q 长杆 ~10-07 晨）+ results/_r660bmb_s6_log.txt（S6 38/38 rc0）+ results/_r660bmb_d19_verify.py（D-19 原字节双 MATCH） | "
                      "下个里程碑: trio 烧满 2000 → mechanical_ready → finalize+E1 判决批，窗 10-05..10-09（Q ETA ~10-07 晨，r638 fallback armed）")
hb['verdict'] = ("GREEN (smoke 48/48; orders delta zero 153/153; D-19 double MATCH zero-consume; WM red=false healthy; engine alive rc0 idle; "
                 "post_review official ✓45/✗0/🟡5; S6 38/38 rc0 dualrun streak 51; attrition CLEAN; QUALITY pool-row restore verified + burner alive; "
                 "keepalive adoption watch first-check next round; zero cloud token)")
hb['ts'] = now_iso
hb['updated'] = now_iso
hb['cpu_util_pct'] = cpu_pct
hb['free_ram_gb'] = free_ram
hb['idle_ram_gb'] = free_ram
hb['ram_avail_gb'] = free_ram
hb['ram_free_gb'] = free_ram
if gpu_free is not None:
    hb['gpu_idle_vram_gb'] = gpu_free
    hb['gpu_free_vram_gb'] = gpu_free
    hb['gpu_idle_vram_mb'] = int(gpu_free * 1024)
    hb['gpu_free_vram_mb'] = int(gpu_free * 1024)
    hb['gpu_vram_free'] = int(gpu_free * 1024)
with open(hb_path, 'w', encoding='utf-8', newline='') as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# 4) self-verify (r645 law): json.loads + epoch int + clock T-separator regex
import re
s2 = json.load(open(st_path, encoding='utf-8'))
h2 = json.load(open(hb_path, encoding='utf-8'))
assert s2['round_no'] == 660, 'state round_no'
assert isinstance(h2['heartbeat_epoch_utc'], int), 'epoch int'
assert re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+08:00$', h2['clock_read']), 'clock format'
assert h2['round_no'] == 660, 'hb round_no'
# round report tail check
with open(rr_path, 'rb') as f:
    tail = f.read()[-200:]
assert f'round {round_no} (bm-b)'.encode('utf-8') in tail, 'round report tail'
print('CLOSE OK:', now_iso, '| state round', s2['round_no'], '| hb epoch', h2['heartbeat_epoch_utc'],
      '| cpu', cpu_pct, '| free_ram', free_ram, '| gpu_free', gpu_free)
