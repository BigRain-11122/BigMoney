# -*- coding: utf-8 -*-
# r653 bm-b closeout writer (r652 lineage recipe; programmatic state/heartbeat writes per r645 law)
import json, time, os, glob, subprocess, datetime
import psutil

NOW_EPOCH = int(time.time())
now = datetime.datetime.fromtimestamp(NOW_EPOCH).astimezone()
ISO = now.strftime('%Y-%m-%dT%H:%M:%S+08:00')
print('clock:', ISO)

# ---------- 0. closeout orders double-scan (S7 second scan, same-scope basename set diff) ----------
hp0 = 'fleet/machines/bm-b.json'
h0 = json.loads(open(hp0, 'rb').read().decode('utf-8'))
ack = set(h0.get('orders_ack') or [])
disk = set(os.path.basename(p) for p in glob.glob('fleet/orders/O-*.md'))
diff = disk - ack
assert not diff, 'NEW ORDERS AT CLOSEOUT: %s' % sorted(diff)
print('closeout orders scan: %d/%d zero-diff' % (len(ack), len(disk)))

# ---------- 1. round report append (mixed-encoding file: utf-8 append, no CRLF translation) ----------
block = f"""{ISO} | round 653 (bm-b, dept:工程/数据+研究): watermark verdict=GREEN (red=false; engine alive rc0 idle; dualrun ZERO-DRIFT streak 45; py 55-87% 三族烧批占用合法)
当前活: FUND 三族 NULLS 烧录健康在飞 Q465/V615/D328 of 2000（readiness 06:49 复跑 60s 双采样：V/Q 实测 1.00/min → ETA V~10-05 05:54/Q~10-05 08:24 早于前估；D 60s 窗 lumpy 零进位 → cross-round fallback 0.27/min → 最坏 ETA ~10-08 20:23 仍落 finalize 窗 10-05..10-09 且早于 10-09 12:00 提速评估线 → 按 r647 既定决策继续 watch 不提速；三烧进程 30208/34396/57116 实活·RAM 4.88GB>4 门；G-SEG GM 裁决 G4 PENDING 等待态一行声明不重扫·r638 insufficient-sample fallback armed）
最近实物: readiness 探针复跑 results/finalize_trio_readiness.json 06:49（Q465/V615/D328 dup_k=0·G1=F·G2/G3=T·G4=PENDING sha 未动·mechanical_ready=false）+ S6 34 腿 rc0 全绿（post_review 官方 run YES=45/NO=0/WAIT=5 零待办 + attrition 4 ledger CLEAN + REPORT-2026-10-04/LIVE-2026-10-04 当日幂等再生〔state=ORANGE cap 50%〕+ dualrun streak 45）
下个里程碑: 三族烧满 2000 → mechanical_ready=true → finalize+E1 判决落窗 10-05..10-09（V 最早 ~10-05 05:54；G-SEG 无裁决走 r638 单读判决）；窗 ≤48h 首查=烧录完成度+G4 裁定面
做了什么: S0 轮首树脏 8 面=本机 daemon treadmill（autofill/satengine/三族 nulls/p1d_gates）→ 与 origin 在途 2 commit〔bm-c r447 收口+r448 closeout〕diff 交集为空 → r437 预对齐净路走 lane absorb 提交→merge origin/main 零 UU 净合→push_verify DELIVERED 三证；S0.5 令双扫 152/152 零差 + D-19 sparse-clone fallback MATCH EB14B510 零消费（K:/C: 集团树双缺席·r641 探针复用·残留 temp 手清后直跑）+ inbox 0；S1 smoke 47/47；S2 板 165 票 0 open·job_list 空；S3 门全绿（WM red=false·engine alive rc0 idle·常设线由在飞三族烧批满足·W14-GENERATE 治理停泊一行声明不重扫·moneyflow IC 批 parked 源阻断自愈域一行声明不重扫）；S6 34 腿 rc0（黄金周周日诚实 no-op 族+车道护栏腿+新 bar 三件套按门不跳〔latest=2026-09-30〕+ t35_paper_export/daily_scorecard/build_status 三面 bm-a 心跳 stale 31min 按 STALE_MIN 律 stale-takeover derive 合法）；S7 attrition CLEAN+四件幂等注册（loop pin=2 no-op·watchdog 在位·precommit/prepush 双爪 match）
验证证据: S6 per-leg 探针清单 34/34 rc=0（evidence _r653bmb_s6_evidence.txt）；smoke 47/47；dualrun ZERO-DRIFT streak 45（366 entries）；readiness 探针 06:49 实跑 JSON（Q465/V615/D328 dup_k=0·elapsed 60.0s·ETA 三族全窗内·BURNPROC pids 30208/34396/57116 活证）；attrition scan CLEAN（evidence results/_attrition_guard_scan.json）；post_review 官方 run YES=45 NO=0；token delta=0（本地腿 0 today）；心跳/state json.loads 双自证 epoch int·clock T 分隔
下轮指针: r654 = 烧录进位 watch+readiness 复跑；mechanical_ready=true 且窗开即执行三族 finalize+E1（G-SEG 无裁决走 r638 fallback）；D lumpy 速率盯防线：ETA>10-09 12:00 即评估合规提速面（禁池面整文件重放陷阱 r630 律·redo-k-lo/hi 分片序 r611）；W14-GENERATE 治理冻结待 GM 裁定不重提
本地未达 origin commit 数=0（以收轮 push_verify 输出为准·失败则 addendum 补记）
"""
p = 'logs/iteration-loop/round_reports.md'
with open(p, 'a', encoding='utf-8', newline='') as f:
    f.write(block)
print('round report appended')

# ---------- 2. heartbeat rewrite (preserve eol style) ----------
hp = 'fleet/machines/bm-b.json'
raw = open(hp, 'rb').read()
eol = b'\r\n' if b'\r\n' in raw else b'\n'
h = json.loads(raw.decode('utf-8'))
vm = psutil.virtual_memory()
avail_gb_dec = round(vm.available / 1e9, 2)
total_gb_dec = round(vm.total / 1e9, 2)
gpu_free_mb = None
try:
    q = subprocess.run(['nvidia-smi', '--query-gpu=memory.free',
                        '--format=csv,noheader,nounits'],
                       capture_output=True, creationflags=0x08000000, timeout=20)
    gpu_free_mb = int(str(q.stdout, 'utf-8', 'replace').strip().splitlines()[0])
except Exception as ex:
    print('gpu sample failed, keep last:', ex)
if not gpu_free_mb:
    gpu_free_mb = int(h.get('gpu_free_vram_mb') or 2314)
h['last_seen'] = ISO
h['heartbeat_epoch_utc'] = NOW_EPOCH
h['clock_read'] = ISO
h['round_no'] = 653
h['round_no_label'] = 'round 653 (bm-b)'
h['current_task'] = ('FUND trio NULLS burn watch (Q465/V615/D328 of 2000 advancing dup_k=0, V/Q ETA ~10-05 05:54/08:24, '
                     'D lumpy worst-case ETA ~10-08 20:23 all in-window 10-05..10-09; finalize fires on mechanical_ready w/ r638 fallback; '
                     'G-SEG GM ruling G4 PENDING; G3 rehearsal fresh ALL-GREEN x3) '
                     '+ r653 watch round: readiness probe re-run 06:49, S6 34 legs rc0, post_review NO=0, attrition CLEAN, '
                     'S0 empty-intersection merge of bm-c r447/r448 wave delivered push_verify DELIVERED')
h['verdict'] = ('GREEN (smoke 47/47; D-19 MATCH zero-consume; orders 152/152; WM red=false; engine alive rc0 idle; '
                'dualrun ZERO-DRIFT streak 45; S6 34 legs rc0; post_review NO=0; attrition CLEAN; W14-GENERATE governance-parked (GM pending) one-line; '
                'trio burns healthy dup_k=0 x3-pids alive)')
h['ts'] = ISO
h['updated'] = ISO
h['updated_at'] = ISO
h['cpu_util_pct'] = psutil.cpu_percent(interval=0.3)
h['free_ram_gb'] = avail_gb_dec
h['idle_ram_gb'] = avail_gb_dec
h['total_ram_gb'] = total_gb_dec
h['ram_free_gb'] = avail_gb_dec
h['ram_avail_gb'] = avail_gb_dec
h['gpu_idle_vram_gb'] = round(gpu_free_mb / 1024, 2)
h['gpu_idle_vram_mb'] = gpu_free_mb
h['gpu_free_vram_gb'] = round(gpu_free_mb / 1024, 2)
h['gpu_free_vram_mb'] = gpu_free_mb
h['gpu_vram_free'] = gpu_free_mb
h['gpu_free_vram_mib'] = gpu_free_mb
h['ram_gb'] = total_gb_dec
txt = json.dumps(h, indent=1, ensure_ascii=False)
open(hp, 'wb').write(txt.replace('\n', eol.decode()).encode('utf-8'))
chk = json.loads(open(hp, encoding='utf-8').read())
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
assert chk['round_no'] == 653
print('heartbeat written; epoch int OK:', chk['heartbeat_epoch_utc'])

# ---------- 3. state.json full programmatic round-trip (r645 law: json.dump + json.loads self-verify) ----------
sp = 'state.json'
sraw = open(sp, 'rb').read()
seol = b'\r\n' if b'\r\n' in sraw else b'\n'
s = json.loads(sraw.decode('utf-8'))
s['machine_id'] = 'bm-b'
s['round_no'] = 653
s['note'] = ('r653: watch/readiness round -- S0 8 daemon-treadmill faces absorbed (empty intersection vs origin 2-commit bm-c r447/r448 wave), '
             'clean merge zero UU, push_verify DELIVERED; S0.5 orders 152/152 zero-diff both scans + D-19 sparse-clone fallback MATCH EB14B510 '
             'zero-consume + inbox 0; S1 47/47; S2 board 0 open; S3 gates green (WM red=false; engine alive rc0 idle; '
             'W14-GENERATE governance-parked one-line; moneyflow IC batch parked one-line); S6 34 legs rc0 (Golden-Week Sunday no-op family, '
             'conditional trio gated off latest=2026-09-30; t35_paper_export/daily_scorecard/build_status stale-takeover derive per STALE_MIN law); '
             'readiness probe 06:49 Q465/V615/D328 dup_k=0 G1=F G2/G3=T G4=PENDING (GM G-SEG ruling awaited, r638 fallback armed), '
             'V/Q measured 1.00/min ETA ~10-05 05:54/08:24, D lumpy fallback 0.27/min worst-case ETA ~10-08 20:23 all in finalize window '
             '10-05..10-09 and ahead of the 10-09 12:00 speedup line, watch continues per r647 standing decision (burn pids 30208/34396/57116 alive); '
             'post_review YES=45 NO=0; attrition CLEAN; dualrun ZERO-DRIFT streak 45.').replace('"', '')
s['last_round_at'] = ISO
s['ts'] = ISO
s['updated'] = ISO
s['last_seen'] = ISO
s['round_no_label'] = 'round 653 (bm-b)'
s['clock_read'] = ISO
s['last_decisions_read_at'] = ISO
stxt = json.dumps(s, indent=1, ensure_ascii=False)
open(sp, 'wb').write(stxt.replace('\n', seol.decode()).encode('utf-8'))
s2 = json.loads(open(sp, encoding='utf-8').read())
assert s2['round_no'] == 653, 'round_no must be 653 after write'
print('state.json written and json.loads self-verify OK; round_no =', s2['round_no'])
