# -*- coding: utf-8 -*-
"""r877 bm-a closeout: state bump + heartbeat + round report row + pit direct-write."""
import json, time, subprocess, io
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from datetime import datetime, timezone, timedelta
import psutil

now = datetime.now(timezone(timedelta(hours=8)))
ts = now.strftime('%Y-%m-%dT%H:%M:%S+08:00')
epoch = int(time.time())

ORD_SHA = 'd7d3a73eb044b25b2617ba6b986f6f9ba2a66be7ce3c21438533fbc576957488'
DEC_SHA = 'ee70cef0f4a5e3b8db4c67936ce2a2aeee222fff8d03f33339b390eac814ac8c'

cpu_pct = psutil.cpu_percent(interval=1)
cores = psutil.cpu_count(logical=True)
ram = psutil.virtual_memory()
ram_free_gb = round(ram.available / 1e9, 1)
vram_free_gb = None
try:
    r = subprocess.run(['nvidia-smi', '--query-gpu=memory.free',
                        '--format=csv,noheader,nounits'],
                       capture_output=True, text=True, timeout=10)
    vram_free_gb = round(int(r.stdout.strip().splitlines()[0]) / 1024, 2)
except Exception:
    vram_free_gb = None
print('stats: cpu=%s%% cores=%s ram_free=%sGB vram_free=%sGB'
      % (cpu_pct, cores, ram_free_gb, vram_free_gb))

# --- state bump ---
sp = 'state-bm-a.json'
s = json.load(open(sp, encoding='utf-8'))
s['round_no'] = 877
s['last_round'] = 877
s['loop_round'] = 877
s['round'] = 877
s['last_action'] = ('r877 composite closeout (dead-leg adopted r844 law): W185 prereg '
                    'buildgen+build GREEN 3-heal + commit pushed + S6 41/41 rc0 + bookkeeping')
s['did'] = ('r877 composite (dead 12:02 leg adopted = dead session died post-buildgen-write '
            'pre-run; carry leg = this session): dead leg = _r877bma_w185_buildgen.py 726L written '
            '+ tmp views (W185 pre-count facts/src/seat/probe views) + churn absorb 2 batches on '
            'origin; carry leg = S0.5 group boards dual-scan zero new bigmoney dispatch (D-05 F-01/02 '
            'ack + D-06 suffix-law already v1.1.2 + O-1160 bm-a sprint unchanged; S7 rescan caught '
            'mid-round ORD delta dfdce53c->d7d3a73e = 12:0x governance tri-cases + bm-b/bm-c '
            'FleetLink point-orders, zero bm-a lane) + smoke 49/49 + engine ALIVE idle + '
            'buildgen 3-HEAL (src extract CRLF->LF binary re-extract vs freeze blob a9925eac6 + '
            'S83 needle old-side W181 key-drift r494 family + new-side pre-roll W180 per r872 '
            's83-chain law + template embedded %d %%d escape) + build GREEN (W185 prereg 21,522B: '
            'A 421_804..423_803 staircase FORTY-FIFTH / B 423_804..424_003 own-A reserved leg2 / '
            'anchors K 402,720 head 812,128 merged mu -0.0928 no-roll 3rd sigma 0.245094 se_mu '
            '0.000386 p95 0.3194 line 1.1857 K-lift +0.0000; DRY GATE 50/50 residue-zero '
            'stale-sweep CLEAN; W-list W159/W168/W169/W181 history-preserved W182=0) + FREEZE '
            'CANDIDATE commit e9a70187b pushed (rebase x1 retry lawful) + S6 41/41 rc0 247s '
            '(dualrun streak 51 ZERO-DRIFT; scorecard/daily/report/LIVE faces re-derived; '
            'collectors pre-15:30 legal no-op = holiday-reopen day 10-08 bars land 15:30; '
            'attrition CLEAN) + idle --worked cleared + self-heal 4-piece (loop pin=8 no-op, '
            'watchdog re-reg, both claws re-installed) + pit direct-write freeze-editor '
            '(needle dual-face law) + watermark keys ORD/DEC dual-updated (fresh python '
            'raw-bytes canonical path)')
s['last_seen'] = ts
s['ts'] = ts
s['clock_read'] = ts
s['updated'] = ts
s['heartbeat_epoch_utc'] = epoch
s['last_heartbeat_epoch_utc'] = s.get('heartbeat_epoch_utc', epoch)
s['last_round_at'] = ts
s['last_round_ts'] = ts
s['last_round_closed'] = ts
s['current_task'] = 'W185 freeze chain (face probe -> r874 bloodline freeze buildgen -> five-face insertions -> pf 9/9 + n1 mat leg -> FREEZE push -> tick self-ignite)'
s['now_active'] = ('W185 prereg landed as freeze candidate e9a70187b (21,522B, DRY GATE green); '
                  'engine idle queue-0 awaiting W185 registry freeze')
s['latest_artifact'] = 'research/PERPETUAL_N1_W185_PREREG.md (W185 prereg freeze candidate, bands A 421_804..423_803 / B 423_804..424_003)'
s['last_artifact'] = s['latest_artifact']
s['next'] = ('W185 freeze chain (r874 bloodline mirror): _r874bma_w184_face_probe.py -> face dumps -> '
             'AST-extract r874 freeze-edits PAIRS (PF/EN/MAT/CL) -> W185 freeze buildgen (S83 map + '
             'needle dual-face law r877 pit) -> freeze edits applied -> pf selftest 9/9 + n1 selftest '
             'W185 mat leg -> FREEZE push -> saturation tick self-ignite W185 burn')
s['verify'] = ('buildgen rc0 (DRY GATE 50/50) + build rc0 (post-transform asserts PASS) + '
               'S6 41 legs rc0 + attrition CLEAN + smoke 49/49 + orphan face=0')
s['last_orders_sha'] = ORD_SHA
s['last_decisions_sha'] = DEC_SHA
s['last_orders_at'] = ts
s['last_decisions_at'] = ts
s['last_decisions_src'] = ('group origin/main via C: real-path fetch + git show (K: absent; '
                           'python subprocess raw-bytes canonical path, zero PS pipe)')
s['last_decisions_ts'] = ts
s['last_orders_seen'] = ('r877 dual-scan: 51 local O-files 0 unacked; group ORD dfdce53c consumed '
                         '(D-05 ack/D-06 suffix law/O-1160 sprint unchanged) then mid-round delta '
                         'd7d3a73e re-scanned at S7 = 12:0x C-04/05/06 governance tri-cases + '
                         '12:05 bm-b/bm-c FleetLink point-orders + O-1240 bm-a leg recorded '
                         'executed -- zero bm-a new dispatch, key moved to consumed tip')
s['last_decisions_seen'] = ('r877: DEC ee70cef0 consumed (D-20261008-01..08 batch; D-05 our '
                            'F-01/F-02① 收讫注记 cloudF 10-14 window held; D-06 machine-suffix '
                            'naming law adopted = our v1.1.2 already compliant; D-07/08 not bm-a '
                            'lane; content unchanged ee659451->ee70cef0 delta = 10-08 00:00+12:00 '
                            'batches, zero BigMoney dispatch rows')
io.open(sp, 'w', encoding='utf-8', newline='').write(
    json.dumps(s, ensure_ascii=False, indent=1))
print('state bumped to 877')

# --- heartbeat ---
hp = 'fleet/machines/bm-a.json'
h = json.load(open(hp, encoding='utf-8'))
h['ts'] = ts
h['clock_read'] = ts
h['last_seen'] = ts
h['heartbeat_epoch_utc'] = epoch
h['round_no'] = 877
h['round'] = 877
h['loop_round'] = 877
h['last_round'] = 877
h['cpu_pct'] = cpu_pct
h['cpu_util_pct'] = cpu_pct
h['cpu_total_pct'] = cpu_pct
h['cores'] = cores
h['cpu_cores'] = cores
h['free_ram_gb'] = ram_free_gb
h['ram_free_gb'] = ram_free_gb
h['idle_ram_gb'] = ram_free_gb
h['total_ram_gb'] = round(ram.total / 1e9, 1)
if vram_free_gb is not None:
    h['gpu0_free_vram_gb'] = vram_free_gb
    h['gpu_free_vram_gb'] = vram_free_gb
    h['gpu_idle_vram_gb'] = vram_free_gb
    h['idle_gpu_vram_gb'] = vram_free_gb
    h['vram_free_gb'] = vram_free_gb
    h['idle_vram_gb'] = vram_free_gb
    h['gpu_free_vram'] = '%sGB' % vram_free_gb
h['verdict'] = ('green (WM red=false; probe verdict=insufficient_history per 15min-window law '
                'honest; engine ALIVE rc0 idle queue-0; W185 seat reserved + prereg freeze-candidate '
                'landed; MODE=resume confirmed r876)')
h['task'] = 'W185 prereg landed (freeze candidate); next: W185 registry freeze chain'
h['current'] = 'W185 freeze chain next round (T-94 wave chain, r874 bloodline mirror)'
h['current_task'] = 'W185 registry freeze chain next round'
h['now_active'] = ('W185 prereg buildgen+build GREEN landed as freeze candidate e9a70187b; '
                   'engine idle queue-0 awaiting five-face insertions')
h['last_action'] = ('r877 composite: dead-leg adopted; W185 buildgen 3-heal + build GREEN + '
                    'prereg freeze-candidate pushed + S6 41/41 rc0')
h['last_artifact'] = ('research/PERPETUAL_N1_W185_PREREG.md (12:2x, W185 prereg freeze candidate: '
                      'A 421_804..423_803 staircase 45th / B 423_804..424_003 own-A reserved leg2 / '
                      'DRY GATE 50/50 residue-zero)')
h['latest_artifact'] = h['last_artifact']
h['next_milestone'] = ('W185 registry freeze (five-face insertions + pf 9/9 + n1 mat leg + FREEZE '
                       'push + tick self-ignite) -- target next bm-a round; then W185 burn 12-shard '
                       'self-ignite same window per r325 law')
h['idle_rounds'] = 0
h['agenda_starved'] = False
h['orphan_faces'] = 0
h['health'] = 'ok'
h['last_run'] = ts
h['last_orders_sha'] = ORD_SHA
h['last_decisions_sha'] = DEC_SHA
io.open(hp, 'w', encoding='utf-8', newline='').write(
    json.dumps(h, ensure_ascii=False, indent=1))
h2 = json.load(open(hp, encoding='utf-8'))
e = h2.get('heartbeat_epoch_utc')
assert isinstance(e, int) and not isinstance(e, bool), 'epoch must be JSON int'
assert 'T' in h2.get('clock_read', ''), 'clock_read must have T separator'
print('heartbeat written; epoch int check PASS (%s); clock_read %s' % (e, h2['clock_read']))

# --- round report row (ROOT canonical, r844 law) ---
row = (ts + ' | r877 | bm-a | dept:研究-永续线+工程/舰队 | '
       'WM-VERDICT: 绿 (red=false; probe verdict=insufficient_history 15min 窗律诚实注记; '
       'engine ALIVE idle queue-0 awaiting W185 freeze; MODE=resume) | '
       '当前活=r877 同轮复合收口 (r844 dead-tail 收养律): 死腿=死会话 12:02 buildgen 写毕未跑被本窗收养; '
       '本腿=3-heal (src 抽取件 CRLF->LF 二进制重抽取对冻结 blob a9925eac6 恒等 + S83 needle 旧侧 W181 键漂移 '
       'r494 族修复 + 新侧前滚号 W180 s83 链内裸滚收尾律 + 模板内嵌 %d %%d 转义) + build GREEN + '
       '冻结候选 commit e9a70187b 推 origin (rebase x1 合法重试) | '
       '最近实物=research/PERPETUAL_N1_W185_PREREG.md (12:2x, W185 prereg 冻结候选 21,522B: '
       'A 带 421_804..423_803 阶梯第四十五例 / B 带 423_804..424_003 own-A 预留 leg2 / '
       '锚=W184 finalize 实况 K 402,720 head 812,128 merged mu -0.0928 no-roll 三连 sigma 0.245094 '
       'se_mu 0.000386 p95 0.3194 line 1.1857 K-lift +0.0000; DRY GATE 50/50 残渣零 stale-sweep CLEAN; '
       'W 名单史实保全 W159/W168/W169/W181) + _r877bma_w185_buildgen.py (726L 3-heal 后) + '
       '_r877bma_w185_prereg_build.py (26,338B emit) | '
       '验证=buildgen rc0 + build rc0 (post-transform asserts 全过) + S6 41/41 rc0 247s '
       '(dualrun streak 51 零漂移·attrition CLEAN·采集器 pre-15:30 合法 no-op=假期复市日 10-08 bar 15:30 落) + '
       'smoke 49/49 + 孤儿面=0 + 自愈四件套全绿 (loop pin=8/watchdog/双爪) + idle --worked 清零 + '
       '复审 ✗0 | '
       'S0.5 双扫=本地 51 令零未回执; 集团双水位消费 (DEC ee70cef0 批 D-01..08 本司零新派单·ORD 中轮 delta '
       'd7d3a73e S7 复扫=12:0x 治理三案+bm-b/bm-c 点令零 bm-a 车道·水位键双推新) | '
       '下轮指针=W185 注册冻结链 (r874 血统镜像): face probe -> AST 抽 r874 freeze-edits PAIRS -> '
       'W185 freeze buildgen (needle 双面律 r877 坑已直写 pit-engine-freeze-editor) -> 五面插录 -> '
       'pf 9/9 + n1 selftest W185 mat leg -> FREEZE push -> tick 自燃 W185 烧录; '
       'VL 实测腿=O-1850 欠账仍挂 (CEO 让路窗遗留·下窗盘点) | 本地未达 origin commit 数=待收尾 push 自证')
with io.open('round_reports-bm-a.md', 'a', encoding='utf-8', newline='') as f:
    f.write(row + chr(10))
print('round report row appended (ROOT canonical)')
print('closeout done at', ts)
