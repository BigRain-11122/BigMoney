# -*- coding: utf-8 -*-
# r651 bm-b closeout writer (r648 lineage recipe; programmatic state/heartbeat writes per r645 law)
import json, time, os, subprocess, datetime
import psutil

NOW_EPOCH = int(time.time())
now = datetime.datetime.fromtimestamp(NOW_EPOCH).astimezone()
ISO = now.strftime('%Y-%m-%dT%H:%M:%S+08:00')
print('clock:', ISO)

# ---------- 1. round report append (mixed-encoding file: utf-8 append, no CRLF translation) ----------
block = f"""{ISO} | round 651 (bm-b, dept:工程/数据+研究): watermark verdict=GREEN (red=false; engine alive rc0 idle; dualrun ZERO-DRIFT streak 43; py 51-86% 三族烧批占用合法)
当前活: FUND 三族 NULLS 烧录健康在飞 Q450/V598/D316 of 2000（dup_k=0 三进程实活 34396/57116/30208 实证；readiness 06:07 复跑 60s 双采样 rate Q0.37/V0.42/D0.31 per-min → ETA V~10-06 14:00/Q~10-07 05:00/D~10-07 23:45 全落 finalize 窗 10-05..10-09 且 D 较 r650 回暖 ~23h 远早于 10-09 12:00 提速评估线 → 按 r647 既定决策继续 watch 不提速；G-SEG GM 裁决 G4 PENDING 等待态一行声明不重扫·r638 insufficient-sample fallback armed）
最近实物: readiness 探针复跑 results/finalize_trio_readiness.json 06:07（Q450/V598/D316 dup_k=0·G1=F·G2/G3=T·G4=PENDING sha 未动·mechanical_ready=false）+ S6 34 腿 rc0 全绿（REPORT-2026-10-04 五面聚合当日幂等 + LIVE-2026-10-04 state=ORANGE cap 50% + post_review 官方 run YES=44/NO=0/WAIT=5 零待办 + attrition 4 ledger CLEAN）
下个里程碑: 三族烧满 2000 → mechanical_ready=true → finalize+E1 判决落窗 10-05..10-09（V 最早 ~10-06 14:00；G-SEG 无裁决走 r638 单读判决）；窗 ≤48h 首查=烧录完成度+G4 裁定面
做了什么: S0 fetch 后 HEAD==origin/main 零落后零合并窗（轮首脏面=本机 daemon treadmill 4 面：autofill+三族 nulls.jsonl·轮末随收口提交）；S0.5 令牌 152/152 双侧同口径 basename 集合比对零差（首扫路径口径假警当场证伪：ls-tree 全路径 vs ack 裸名——r646 同口径律兑现面）+ D-19 sparse-clone fallback MATCH EB14B510 零消费（K:/C: 集团树双缺席·r631 配方）+ inbox 0 未读；S1 smoke 47/47；S2 板 165 票 0 open·job_list 空；S3 门全绿（WM red=false·engine alive rc0 idle·常设线由在飞三族烧批满足·W14-GENERATE 治理停泊 r494/r504 双闸一行声明不重扫·moneyflow IC 批 parked 源阻断 30min 自愈域一行声明不重扫）；MSG-1720 Finding B 修复链定谳复验=runner r626d guard 在位+rehearsal 10-04 01:45 复跑 ALL-GREEN x3（VALUE passive leg PASS·span 1994-09-01 披露）→ finalize 前置工程面零阻塞；S6 34 腿 rc0（黄金周周日诚实 no-op 族+车道护栏腿+新 bar 三件套按门不跳 r637 先例·bm-a origin 心跳 8-9min fresh 全 lane-guard 正常跳过零 stale-takeover）；S7 attrition CLEAN+四件幂等注册（loop pin=2 no-op·watchdog·precommit·prepush）
验证证据: S6 per-leg 探针清单 34/34 rc=0（evidence _r651bmb_s6_evidence.txt）；smoke 47/47；dualrun ZERO-DRIFT streak 43（366 entries）；readiness 探针 06:07 实跑 JSON（Q450/V598/D316 dup_k=0·elapsed 60.0s）；attrition scan CLEAN（evidence results/_attrition_guard_scan.json）；post_review 官方 run YES=44 NO=0；token delta=0（本地腿 0 today）；心跳/state json.loads 双自证 epoch int·clock T 分隔
下轮指针: r652 = 烧录进位 watch+readiness 复跑；mechanical_ready=true 且窗开即执行三族 finalize+E1（G-SEG 无裁决走 r638 fallback）；D 速率波动盯防线：ETA>10-09 12:00 即评估合规提速面（禁池面整文件重放陷阱 r630 律·redo-k-lo/hi 分片序 r611）；W14-GENERATE 治理冻结待 GM 裁定不重提
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
h['round_no'] = 651
h['round_no_label'] = 'round 651 (bm-b)'
h['current_task'] = ('FUND trio NULLS burn watch (Q450/V598/D316 of 2000 advancing dup_k=0, ETA V~10-06 14:00/Q~10-07 05:00/D~10-07 23:45 '
                     'all in-window 10-05..10-09; finalize fires on mechanical_ready w/ r638 fallback; G-SEG GM ruling G4 PENDING; '
                     'MSG-1720 Finding B fix verified + rehearsal ALL-GREEN x3) '
                     '+ r651 watch round: readiness probe re-run 06:07, S6 34 legs rc0, post_review NO=0, attrition CLEAN')
h['verdict'] = ('GREEN (smoke 47/47; D-19 MATCH zero-consume; orders 152/152; WM red=false; engine alive rc0 idle; '
                'dualrun ZERO-DRIFT streak 43; S6 34 legs rc0; post_review NO=0; attrition CLEAN; W14-GENERATE governance-parked (GM pending) one-line; '
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
assert chk['round_no'] == 651
print('heartbeat written; epoch int OK:', chk['heartbeat_epoch_utc'])

# ---------- 3. state.json full programmatic round-trip (r645 law: json.dump + json.loads self-verify) ----------
sp = 'state.json'
sraw = open(sp, 'rb').read()
seol = b'\r\n' if b'\r\n' in sraw else b'\n'
s = json.loads(sraw.decode('utf-8'))
s['machine_id'] = 'bm-b'
s['round_no'] = 651
s['note'] = ('r651: watch/readiness round -- S0 HEAD==origin zero-merge-window (4 daemon treadmill faces absorbed at closeout); '
             'S0.5 orders 152/152 zero-diff (basename same-scope; first-scan path-scope false alarm proven on the spot per r646 law) '
             '+ D-19 sparse-clone fallback MATCH EB14B510 zero-consume + inbox 0; S1 47/47; S2 board 0 open; '
             'S3 gates green (WM red=false; engine alive rc0 idle; W14-GENERATE governance-parked one-line; '
             'moneyflow IC batch parked source-blocked one-line); MSG-1720 Finding B chain re-verified (r626d guard in place '
             '+ rehearsal rerun 10-04 01:45 ALL-GREEN x3, VALUE passive leg PASS span 1994-09-01 disclosed) = finalize engineering face zero-blocking; '
             'S6 34 legs rc0 (Golden-Week Sunday no-op family, new-bar trio gated off per r637 precedent; bm-a origin heartbeat fresh, zero stale-takeover); '
             'readiness probe 06:07 Q450/V598/D316 dup_k=0 G1=F G2/G3=T G4=PENDING (GM G-SEG ruling awaited, r638 fallback armed), '
             'ETAs all in finalize window 10-05..10-09 (D~10-07 23:45, improved ~23h vs r650, >1.3 day margin to 10-09 12:00 speedup line, watch continues per r647 standing decision); '
             'post_review run NO=0 zero pending; attrition CLEAN.').replace('"', '')
s['last_round_at'] = ISO
s['ts'] = ISO
s['updated'] = ISO
s['last_seen'] = ISO
s['round_no_label'] = 'round 651 (bm-b)'
s['clock_read'] = ISO
s['last_decisions_read_at'] = ISO
stxt = json.dumps(s, indent=1, ensure_ascii=False)
open(sp, 'wb').write(stxt.replace('\n', seol.decode()).encode('utf-8'))
s2 = json.loads(open(sp, encoding='utf-8').read())
assert s2['round_no'] == 651, 'round_no must be 651 after write'
print('state.json written and json.loads self-verify OK; round_no =', s2['round_no'])
