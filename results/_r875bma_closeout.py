# -*- coding: utf-8 -*-
"""r875 bm-a closeout: state bump + heartbeat + round report row (one pass)."""
import json, time, subprocess, io
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from datetime import datetime, timezone, timedelta
import psutil

now = datetime.now(timezone(timedelta(hours=8)))
ts = now.strftime('%Y-%m-%dT%H:%M:%S+08:00')
epoch = int(time.time())

# --- system stats ---
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
s['round_no'] = 875
s['last_round'] = 875
s['loop_round'] = 875
s['last_action'] = ('W184 finalize one-pass EXACT + S7/8 backfill + '
                    'W185 pre-seat probe ADMIT + seat MSG pushed + S6 41/41 rc0')
s['last_seen'] = ts
s['ts'] = ts
s['clock_read'] = ts
s['updated'] = ts
s['heartbeat_epoch_utc'] = epoch
s['last_heartbeat_epoch_utc'] = s.get('heartbeat_epoch_utc', epoch)
s['last_round_at'] = ts
s['last_round_ts'] = ts
s['last_round_closed'] = ts
s['current_task'] = 'W185 prereg buildgen+freeze (next round); T-94 wave chain continues'
s['now_active'] = 'W185 seat published; engine idle queue-0 awaiting W185 freeze'
s['latest_artifact'] = 'results/perpetual_faces/n1_w184_results.json (W184 finalize, ledger 812,128, K 402,720)'
s['next'] = 'W185 prereg buildgen -> freeze (five-face insertions) -> engine self-ignite W185'
s['verify'] = 'n1 selftest PASS + pf selftest 9/9 PASS + S6 41 legs rc0 + attrition CLEAN'
io.open(sp, 'w', encoding='utf-8', newline='').write(
    json.dumps(s, ensure_ascii=False, indent=1))
print('state bumped to 875')

# --- heartbeat ---
hp = 'fleet/machines/bm-a.json'
h = json.load(open(hp, encoding='utf-8'))
h['ts'] = ts
h['clock_read'] = ts
h['last_seen'] = ts
h['heartbeat_epoch_utc'] = epoch
h['round_no'] = 875
h['round'] = 875
h['loop_round'] = 875
h['last_round'] = 875
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
h['verdict'] = ('green (WM red=false lane healthy; engine ALIVE idle queue-0 post-W184; '
                'W185 seat pushed = supply link landed; MODE=pause CEO-yield -> VL/GPU legs deferred honest)')
h['task'] = 'W184 finalize closed + W185 seat published; next: W185 prereg buildgen+freeze'
h['current'] = 'W185 prereg buildgen+freeze next round (T-94 wave chain)'
h['current_task'] = 'W185 prereg buildgen+freeze next round'
h['now_active'] = 'W184 finalize one-pass EXACT closed same-window (r381); W185 seat published=reserved on origin (r565)'
h['last_action'] = ('W184 finalize + S7/8 backfill + W185 pre-seat probe ADMIT + '
                    'seat MSG pushed + S6 41/41 rc0')
h['last_artifact'] = ('results/perpetual_faces/n1_w184_results.json '
                      '(10:2x, W184 finalize: ledger 812,128 / K 402,720 / four pre-keys PASS)')
h['latest_artifact'] = h['last_artifact']
h['next_milestone'] = ('W185 freeze landed (five-face insertions + engine self-ignite) '
                       '-- target next bm-a round (<=40min); VL 实测 deferred until MODE=pause '
                       'lifts (CEO-yield law outranks O-1850 VL leg)')
h['idle_rounds'] = 0
h['agenda_starved'] = False
h['orphan_faces'] = 0
h['health'] = 'ok'
h['last_run'] = ts
io.open(hp, 'w', encoding='utf-8', newline='').write(
    json.dumps(h, ensure_ascii=False, indent=1))
h2 = json.load(open(hp, encoding='utf-8'))
e = h2.get('heartbeat_epoch_utc')
assert isinstance(e, int) and not isinstance(e, bool), 'epoch must be JSON int'
assert 'T' in h2.get('clock_read', ''), 'clock_read must have T separator'
print('heartbeat written; epoch int check PASS (%s); clock_read %s' % (e, h2['clock_read']))

# --- round report row ---
row = (ts + ' | r875 | bm-a | dept:研究-永续线+工程/舰队 | '
       'WM-VERDICT: 绿 (red=false lane=healthy; engine ALIVE rc0 idle queue-0 post-W184 burn 12/12; '
       'supply link = W185 seat pushed this window; MODE=pause CEO-yield -> VL 实测腿挂起诚实注记) | '
       '当前活=W184 finalize one-pass EXACT 同轮收口 (r381 律) + §7/§8 同窗回填 (r864 三连) + '
       'W185 pre-seat probe 5-legs ADMIT + 席位 MSG published=reserved 推 origin (r565) | '
       '最近实物=results/perpetual_faces/n1_w184_results.json (10:2x, W184 finalize: '
       '账本 809,928+2,200=812,128 EXACT [+1,010 REGIME5 冻结后入链 r518 披露] / K 402,720 EXACT / '
       'merged mu -0.092818 no-roll / A p95 0.3194 Δ+0.0176 门过 / 四预键全 PASS / audit.finalize_only bm-a) + '
       'research/PERPETUAL_N1_W184_PREREG.md §7/§8 回填 + _r875bma_w185_probe_receipt.json '
       '(W185 A 421_804..423_803 阶梯45例/B 423_804..424_003 leg2 预留) + '
       'fleet/inbox/MSG-2026-10-08-1032-bma-w185-seat.md | '
       '验证=n1 selftest PASS (缺省波 r522 律) + pf selftest 9/9 PASS + S6 41/41 rc0 '
       '(dualrun streak 51 零漂移·scorecard/日报/LIVE 面再 derive·采集器 pre-15:30 合法 no-op·lane 守卫诚实跳过) + '
       'attrition CLEAN + 孤儿面=0 + 复审 ✗0 | '
       '下轮指针=W185 prereg buildgen (r872 血统·W184 finalize 锚=812,128/K 402,720/p95 0.3194 键面) -> '
       'W185 freeze 五面插录 -> 引擎自燃 W185; VL 实测腿=MODE=pause 解除后首窗补测 '
       '(CEO 用机让路律优先·O-1850 欠账如实) | 本地未达 origin commit 数=待收尾 push 自证')
with io.open('round_reports-bm-a.md', 'a', encoding='utf-8', newline='') as f:
    f.write(row + chr(10))
print('round report row appended (ROOT canonical)')
