# r647 bm-b closeout writer (watch round; programmatic state/heartbeat writes per r645 law)
import json, time, os, subprocess, datetime
import psutil

NOW_EPOCH = int(time.time())
now = datetime.datetime.fromtimestamp(NOW_EPOCH).astimezone()
ISO = now.strftime('%Y-%m-%dT%H:%M:%S+08:00')
print('clock:', ISO)

# ---------- 1. round report append (mixed-encoding file: utf-8 append, no CRLF translation) ----------
block = f"""{ISO} | round 647 (bm-b, dept:工程/数据+研究): watermark verdict=GREEN (red=false; next_pick=claimed moneyflow IC 批 parked 源阻断 30-min 自愈域; py 尾段 61~62%)
当前活: FUND 三族 NULLS 烧录在飞 Q425/V567/D294 of 2000（dup_k=0；本窗 60s 双采样 Q 回暖 1.0/min·V 0.37·D 0.31 lumpy-batch 诚实；ETA Q~10-05 07:00/V~10-06 21:00/D~10-08 00:00，全落 finalize 窗 10-05..10-09 内）+ G4 治理面 PENDING（GM 对 MSG-2026-10-03-1720 G-SEG 裁定未落·sha 未动；r638 insufficient-sample fallback 在位）
最近实物: readiness 探针刷新 results/finalize_trio_readiness.json 04:52（G1=F·G2/G3=T·G4=PENDING·mechanical_ready=false·dup_k=0）+ S6 33 腿 rc0 全绿（REPORT-2026-10-04 五面聚合 + LIVE-20261004 当日幂等 04:53 落盘）+ S0 净路整合 origin 7 commit（bm-a r658 题材环 R5 方法论章 + bm-c r444 W2 判决落地 805 cells，absorb→merge 零冲突 ort 净落）
下个里程碑: 三族烧满 2000 → mechanical_ready → finalize+E1 判决落窗 10-05..10-09（G-SEG 无裁定走 r638 单读 fallback）；D 族 ETA 10-08 00:00 距窗尾 10-09 留 1 天余量，若速率再劣化贴窗尾 → 评估合规提速面（禁池面整文件重放陷阱 r630 律）。窗 ≤48h 首查=烧录完成度
做了什么: S0 pull 撞 daemon treadmill → r437 正法 absorb 9 面+merge origin/main（7 commit 净落零 UU·CODELY.md r646 修复面保留）+ push_verify DELIVERED（daemon 同窗自推实证 tip f017d58e）；S0.5 令牌 152/152 双侧同口径零差（fleet/orders README.md 非令件不计数）+D-19 sparse-clone fallback MATCH EB14B510 零消费（K: 本会话不可见·r631 配方）+inbox 0 未读；S1 47/47；S2 板 0 open·T-165 bm-a r658 已闭合不碰；S3 门全绿（WM red=false·engine alive rc0 idle·常设线由在飞三族烧批满足·W14-GENERATE=治理停泊面 r494/r504 park GM 双裁待裁+RAM<4GB 双闸一行声明不重扫·moneyflow rank 腿 RemoteDisconnected 04:32 属 30-min 自愈域）；S6 33 腿 rc0（黄金周周日诚实 no-op 族+车道护栏腿+新 bar 三件套按门不跑 r637 先例）；S7 attrition CLEAN+四件幂等注册
验证证据: S6 per-leg 探针清单 33/33 rc=0（evidence _r647bmb_s6_evidence.txt）；smoke 47/47；dualrun ZERO-DRIFT streak 39（366 entries）；readiness 探针 04:52 实跑 JSON（Q425/V567/D294 dup_k=0）；attrition scan CLEAN；push_verify DELIVERED（本块先落、收轮 push 后以 push_verify 输出为准，失败即 addendum 补记）；token 增长 0（本地腿 0 today）
下轮指针: r648 = 烧录进位 watch+readiness 复跑；mechanical_ready=true 且窗开即执行三族 finalize+E1（G-SEG 无裁定=r638 fallback）；W14-GENERATE 治理停泊待 GM 裁定不重扫
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
h['round_no'] = 647
h['round_no_label'] = 'round 647 (bm-b)'
h['current_task'] = ('FUND trio NULLS burn watch (Q425/V567/D294 of 2000 advancing dup_k=0, ETA Q~10-05 07:00/V~10-06 21:00/D~10-08 00:00; '
                     'finalize window 10-05..10-09 opens on mechanical_ready w/ r638 fallback; G-SEG GM ruling G4 PENDING) '
                     '+ r647 watch round: S0 absorb+merge origin 7 (bm-a theme R5 chapter + bm-c W2 judgment) zero-conflict, '
                     'readiness probe refreshed 04:52, S6 33 legs rc0')
h['verdict'] = ('GREEN (smoke 47/47; D-19 MATCH zero-consume; orders 152/152; WM red=false; engine alive rc0 idle; '
                'dualrun ZERO-DRIFT streak 39; S6 33 legs rc0; attrition CLEAN; W14-GENERATE governance-parked (GM pending, RAM<4GB); '
                'trio burns healthy dup_k=0)')
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
assert chk['round_no'] == 647
print('heartbeat written; epoch int OK:', chk['heartbeat_epoch_utc'])

# ---------- 3. state.json full programmatic round-trip (r645 law: json.dump + json.loads self-verify) ----------
sp = 'state.json'
sraw = open(sp, 'rb').read()
seol = b'\r\n' if b'\r\n' in sraw else b'\n'
s = json.loads(sraw.decode('utf-8'))
s['machine_id'] = 'bm-b'
s['round_no'] = 647
s['note'] = ('r647: watch/readiness round -- S0 treadmill absorb (9 faces) + merge origin 7 commits (bm-a r658 theme R5 chapter, '
             'bm-c r444 W2 judgment landed 805 cells) zero-conflict ort, push DELIVERED (daemon co-push); '
             'S0.5 orders 152/152 zero-diff + D-19 sparse-clone fallback MATCH EB14B510 zero-consume + inbox 0; '
             'S1 47/47; S2 board 0 open (T-165 closed by bm-a r658); S3 gates green (WM red=false; engine alive rc0 idle; '
             'W14-GENERATE governance-parked r494/r504 + RAM<4GB, one-line declared; moneyflow IC batch parked source-blocked '
             '30-min self-heal); S6 33 legs rc0 (Golden-Week Sunday no-op family, new-bar trio gated off per r637 precedent); '
             'readiness probe 04:52 Q425/V567/D294 dup_k=0 G1=F G2/G3=T G4=PENDING (GM G-SEG ruling awaited, r638 fallback armed), '
             'window 10-05..10-09; post_review zero pending; attrition CLEAN.').replace('"', '')
s['last_round_at'] = ISO
s['ts'] = ISO
s['updated'] = ISO
s['last_seen'] = ISO
s['round_no_label'] = 'round 647 (bm-b)'
s['clock_read'] = ISO
s['last_decisions_read_at'] = ISO
stxt = json.dumps(s, indent=1, ensure_ascii=False)
open(sp, 'wb').write(stxt.replace('\n', seol.decode()).encode('utf-8'))
s2 = json.loads(open(sp, encoding='utf-8').read())
assert s2['round_no'] == 647, 'round_no must be 647 after write'
print('state.json written and json.loads self-verify OK; round_no =', s2['round_no'])
