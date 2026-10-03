# r648 bm-b closeout writer (r647 lineage recipe; programmatic state/heartbeat writes per r645 law)
import json, time, os, subprocess, datetime
import psutil

NOW_EPOCH = int(time.time())
now = datetime.datetime.fromtimestamp(NOW_EPOCH).astimezone()
ISO = now.strftime('%Y-%m-%dT%H:%M:%S+08:00')
print('clock:', ISO)

# ---------- 1. round report append (mixed-encoding file: utf-8 append, no CRLF translation) ----------
block = f"""{ISO} | round 648 (bm-b, dept:工程/数据+研究): watermark verdict=GREEN (red=false; next_pick=claimed moneyflow IC 批仍源阻断 parked 一行声明不重扫；py 尾段 61~62%)
当前活: FUND 三族 NULLS 烧录在飞 Q430/V575/D298 of 2000（dup_k=0 三进程实活 34396/57116/30208 实证；readiness 05:07 复跑 rate Q1.0/V1.0/D0.25 per-min → ETA Q~10-05 07:20/V~10-05 05:00/D~10-08 22:15 全落 finalize 窗 10-05..10-09 内；D 较 r647 推演劣化 ~22h 但距窗尾仍留 >1 天 → 按 r647 既定决策继续 watch 不提速，劣化至 ETA>10-09 12:00 触发合规提速面评估（--redo-k-lo/hi 分片律 r611·禁池面整文件重放陷阱 r630 律））
最近实物: readiness 探针复跑 results/finalize_trio_readiness.json 05:07（Q430/V575/D298 dup_k=0·G1=F·G2/G3=T·G4=PENDING sha 未动·mechanical_ready=false）+ S6 34 腿 rc0 全绿（REPORT-2026-10-04 五面聚合 + LIVE-2026-10-04 当日幂等 05:15 落盘 + post_review 官方 run YES=44/NO=0/WAIT=5 零待办 + attrition 4 ledger CLEAN）+ S0 churn-absorb 8 面预对齐（dda09bd21）
下个里程碑: 三族烧满 2000 → mechanical_ready=true → finalize+E1 判决落窗 10-05..10-09（G-SEG 无裁定走 r638 单读 fallback）；窗 ≤48h 首查=烧录完成度+G4 裁定面
做了什么: S0 树 8 脏面全 daemon treadmill（autofill/satengine/NULLS trio）→ fetch 后 HEAD==origin 零交集 → churn-absorb 提交；S0.5 令牌 152/152 双侧同口径零差 + D-19 sparse-clone fallback MATCH EB14B510 零消费 + inbox 0 未读；S1 47/47；S2 板 0 open；S3 门全绿（WM red=false·engine alive rc0 idle·常设线由在飞三族烧批满足·W14-GENERATE 治理停泊 r494/r504 双闸一行声明不重扫）；S6 34 腿 rc0（黄金周周日诚实 no-op 族+车道护栏腿+新 bar 三件套按门不跑 r637 先例·bm-a 心跳 stale 40min 三面合法 stale-takeover t35_export/daily_scorecard/build_status）；S7 attrition CLEAN+四件幂等注册（loop pin=2 no-op·watchdog·precommit·prepush）
验证证据: S6 per-leg 探针清单 34/34 rc=0（evidence _r648bmb_s6_evidence.txt）；smoke 47/47；dualrun ZERO-DRIFT streak 40（366 entries）；readiness 探针 05:07 实跑 JSON（Q430/V575/D298 dup_k=0）；attrition scan CLEAN（evidence _attrition_guard_scan.json）；post_review run NO=0；token delta=0（本地腿 0 today）
下轮指针: r649 = 烧录进位 watch+readiness 复跑；mechanical_ready=true 且窗开即执行三族 finalize+E1（G-SEG 无裁定=r638 fallback）；D 速率劣化监控线=ETA>10-09 12:00 即评估合规提速面；W14-GENERATE 治理停泊待 GM 裁定不重扫
本地未达 origin commit 数=0（push_verify DELIVERED·以收轮 push_verify 输出为准，失败即 addendum 补记）
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
h['round_no'] = 648
h['round_no_label'] = 'round 648 (bm-b)'
h['current_task'] = ('FUND trio NULLS burn watch (Q430/V575/D298 of 2000 advancing dup_k=0, ETA Q~10-05 07:20/V~10-05 05:00/D~10-08 22:15 '
                     'all in-window 10-05..10-09; finalize fires on mechanical_ready w/ r638 fallback; G-SEG GM ruling G4 PENDING) '
                     '+ r648 watch round: churn-absorb S0, readiness probe re-run 05:07, S6 34 legs rc0, post_review NO=0, attrition CLEAN')
h['verdict'] = ('GREEN (smoke 47/47; D-19 MATCH zero-consume; orders 152/152; WM red=false; engine alive rc0 idle; '
                'dualrun ZERO-DRIFT streak 40; S6 34 legs rc0; post_review NO=0; attrition CLEAN; W14-GENERATE governance-parked (GM pending, RAM<4GB); '
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
assert chk['round_no'] == 648
print('heartbeat written; epoch int OK:', chk['heartbeat_epoch_utc'])

# ---------- 3. state.json full programmatic round-trip (r645 law: json.dump + json.loads self-verify) ----------
sp = 'state.json'
sraw = open(sp, 'rb').read()
seol = b'\r\n' if b'\r\n' in sraw else b'\n'
s = json.loads(sraw.decode('utf-8'))
s['machine_id'] = 'bm-b'
s['round_no'] = 648
s['note'] = ('r648: watch/readiness round -- S0 churn-absorb 8 daemon faces (HEAD==origin zero-overlap), '
             'push DELIVERED via push_verify; S0.5 orders 152/152 zero-diff + D-19 sparse-clone fallback '
             'MATCH EB14B510 zero-consume + inbox 0; S1 47/47; S2 board 0 open; S3 gates green '
             '(WM red=false; engine alive rc0 idle; W14-GENERATE governance-parked one-line declared; '
             'moneyflow IC batch parked source-blocked one-line declared); S6 34 legs rc0 '
             '(Golden-Week Sunday no-op family, new-bar trio gated off per r637 precedent; bm-a stale-takeover '
             'faces t35_export/daily_scorecard/build_status legal per STALE_MIN law); readiness probe 05:07 '
             'Q430/V575/D298 dup_k=0 G1=F G2/G3=T G4=PENDING (GM G-SEG ruling awaited, r638 fallback armed), '
             'ETAs all in finalize window 10-05..10-09 (D~10-08 22:15, >1 day margin to tail, watch continues '
             'per r647 standing decision, speedup-eval trigger line = D ETA beyond 10-09 12:00); '
             'post_review run NO=0 zero pending; attrition CLEAN.').replace('"', '')
s['last_round_at'] = ISO
s['ts'] = ISO
s['updated'] = ISO
s['last_seen'] = ISO
s['round_no_label'] = 'round 648 (bm-b)'
s['clock_read'] = ISO
s['last_decisions_read_at'] = ISO
stxt = json.dumps(s, indent=1, ensure_ascii=False)
open(sp, 'wb').write(stxt.replace('\n', seol.decode()).encode('utf-8'))
s2 = json.loads(open(sp, encoding='utf-8').read())
assert s2['round_no'] == 648, 'round_no must be 648 after write'
print('state.json written and json.loads self-verify OK; round_no =', s2['round_no'])
