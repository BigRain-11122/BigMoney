import json, psutil
from datetime import datetime, timezone, timedelta

tz = timezone(timedelta(hours=8))
iso = datetime.now(tz).strftime('%Y-%m-%dT%H:%M:%S+08:00')

hb = json.load(open(r'fleet\machines\bm-b.json', encoding='utf-8'))
vm = psutil.virtual_memory()
hb['free_ram_gb'] = round(vm.available / 1024**3, 1)
hb['idle_ram_gb'] = round(vm.available / 1024**3, 1)
hb['cpu_util_pct'] = round(psutil.cpu_percent(interval=0.5), 1)
import subprocess
try:
    out = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
                          capture_output=True, text=True, timeout=10).stdout.strip().splitlines()
    hb['gpu_free_vram_gb'] = round(float(out[0]) / 1024, 1)
    hb['gpu_idle_vram_gb'] = hb['gpu_free_vram_gb']
except Exception:
    pass
hb['verdict'] = ('healthy: smoke 26/26; r416 W6 CEO report landed (~47h early) + attrition 2 rows + prereg sec.7/8 first backfill '
                 '(W1-W5 drift debt disclosed for follow-up slice); orders 122/122 zero-diff; S6 34 legs rc=0 '
                 '(dualrun real-drift observation streak-reset; comp_audit FLAG:supply_floor = W7 standing-line carrier); S7 trio green')
json.dump(hb, open(r'fleet\machines\bm-b.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('hb resource faces refreshed: ram', hb['free_ram_gb'], 'cpu', hb['cpu_util_pct'], 'gpu', hb.get('gpu_free_vram_gb'))
