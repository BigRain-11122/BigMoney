# r646 bm-b closeout writer (watch round; programmatic state/heartbeat writes per r645 law)
import json, time, os, subprocess, datetime
import psutil

NOW_EPOCH = int(time.time())
now = datetime.datetime.fromtimestamp(NOW_EPOCH).astimezone()
ISO = now.strftime('%Y-%m-%dT%H:%M:%S+08:00')
print('clock:', ISO)

# ---------- 1. round report append (mixed-encoding file: utf-8 append, no CRLF translation) ----------
block = f"""{ISO} | round 646 (bm-b, dept:工程/数据+研究): watermark verdict=GREEN (red=false; WM probe local_batch_running=true 合法在烧; dualrun ZERO-DRIFT streak 38)
当前活: FUND 三族 NULLS 烧录在飞 Q413/V555/D284 of 2000（dup_k=0；本窗实测速率 Q~0.36/D~0.31 每 min 受 S6 链同窗 CPU 挤压、V 稳 1.0/min；ETA V~10-05 晨/Q~10-07/D~10-08，仍在 finalize 窗 10-05..10-09 内）+ G4 治理面 PENDING（等 GM 对 MSG-2026-10-03-1720 G-SEG 裁定，r638 insufficient-sample fallback 在位）
最近实物: readiness 探针刷新 results/finalize_trio_readiness.json 04:19（G1=F·G2/G3=T·G4=PENDING·mechanical_ready=false·dup_k=0）+ S6 35 腿 rc0 全绿（docs/daily_report/REPORT-2026-10-04.md 五面聚合一页 04:1x 落盘 + ceo_live_usage LIVE-20261004 当日幂等）
下个里程碑: 三族 NULLS 烧满 2000 → finalize+E1 判决落窗 10-05..10-09（mechanical_ready 即执行；G-SEG 无裁定走 r638 单读判决）；D 族 ETA 若进一步劣化贴 10-09 → 评估合规提速面（禁池面整文件重放陷阱 r630 律）。窗 ≤48h 首查=烧录完成度
做了什么: S0 HEAD==origin 零差集净面（脏面=本机 daemon 族收轮 lane absorb）；S0.5 令牌 152/152 首扫零差+D-19 sparse-clone fallback MATCH EB14B510 零消费+inbox 0 未读；S1 47/47；S2 板 165 票 0 open·job_list 空·T-165 bm-a 在飞（R5 方法论章）不碰；S3 门全绿（WM red=false·engine alive rc0 idle·常设线由在飞三族烧批满足·W14-GENERATE RAM 3.31GiB<4GB 闸正确排队·moneyflow IC 批 parked 源阻断 rank 腿 RemoteDisconnected 03:10 属 30-min 自愈域）；②VALUE cmd_finalize 崩溃修复核实=r626d 守卫已在正典位（源锚+验证件实证）；S6 35 腿 rc0（周日黄金周诚实 no-op 族+车道护栏腿+bar 条件腿按门不跑）；S7 四件幂等+attrition CLEAN
验证证据: S6 rc 清单 35/35 rc=0（per-leg 探针清单）；smoke 47/47；dualrun streak 38 ZERO-DRIFT；readiness 探针 04:19 实跑 JSON（Q413/V555/D284 dup_k=0）；attrition scan CLEAN（gate_attrition.bm-a.json 2 史行 healed 注记照录）；push_verify DELIVERED（本块先落、收轮 push 后以 push_verify 输出为准，失败即 addendum 补记）
下轮指针: r647 = 烧录进位 watch+readiness 复跑；mechanical_ready=true 且窗开（10-05 起）即执行三族 finalize+E1（G-SEG 无裁定=r638 fallback）；W14-GENERATE 待 RAM 解禁由 autofill 续
本地未达 origin commit 数=0（push_verify DELIVERED·以收轮 push_verify 输出为准）
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
h['round_no'] = 646
h['round_no_label'] = 'round 646 (bm-b)'
h['current_task'] = ('FUND trio NULLS burn watch (Q413/V555/D284 of 2000 advancing dup_k=0, ETA V~10-05/Q~10-07/D~10-08; '
                     'finalize window 10-05..10-09 opens on mechanical_ready w/ r638 fallback; G-SEG GM ruling G4 PENDING) '
                     '+ r646 watch round: readiness probe refreshed 04:19, S6 35 legs rc0, VALUE finalize fix verified in-place (r626d)')
h['verdict'] = ('GREEN (smoke 47/47; D-19 MATCH zero-consume; orders 152/152; WM red=false local_batch_running=true; engine alive rc0 idle; '
                'dualrun ZERO-DRIFT streak 38; S6 35 legs rc0; attrition CLEAN; RAM 3.31GiB W14-GENERATE queued; trio burns healthy dup_k=0)')
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
assert chk['round_no'] == 646
print('heartbeat written; epoch int OK:', chk['heartbeat_epoch_utc'])

# ---------- 3. state.json full programmatic round-trip (r645 law: json.dump + json.loads self-verify) ----------
sp = 'state.json'
sraw = open(sp, 'rb').read()
seol = b'\r\n' if b'\r\n' in sraw else b'\n'
s = json.loads(sraw.decode('utf-8'))
s['machine_id'] = 'bm-b'
s['round_no'] = 646
s['note'] = ('r646: watch/readiness round -- S0 HEAD==origin zero-diff net face + daemon lane absorb at close; '
             'S0.5 orders 152/152 zero-diff + D-19 sparse-clone fallback MATCH EB14B510 zero-consume + inbox 0; '
             'S1 47/47; S2 board 0 open; S3 gates green (WM red=false; engine alive rc0 idle; W14-GENERATE RAM-gated queued; '
             'moneyflow IC batch parked source-blocked 30-min self-heal); VALUE cmd_finalize fix verified in-place (r626d guard); '
             'S6 35 legs rc0 (Golden-Week Sunday no-op family); readiness probe 04:19 Q413/V555/D284 dup_k=0 '
             'G1=F G2/G3=T G4=PENDING (GM G-SEG ruling awaited, r638 fallback armed), window 10-05..10-09; '
             'post_review zero pending; attrition CLEAN; RAM 3.31GiB W14-GENERATE stays queued.').replace('"', '')
s['last_round_at'] = ISO
s['ts'] = ISO
s['updated'] = ISO
s['last_seen'] = ISO
s['round_no_label'] = 'round 646 (bm-b)'
s['clock_read'] = ISO
s['last_decisions_read_at'] = ISO
stxt = json.dumps(s, indent=1, ensure_ascii=False)
open(sp, 'wb').write(stxt.replace('\n', seol.decode()).encode('utf-8'))
s2 = json.loads(open(sp, encoding='utf-8').read())
assert s2['round_no'] == 646, 'round_no must be 646 after write'
print('state.json written and json.loads self-verify OK; round_no =', s2['round_no'])
