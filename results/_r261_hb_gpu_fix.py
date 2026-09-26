# -*- coding: utf-8 -*-
# r261 heartbeat GPU-field correction: CIM AdapterRAM 4GB-capped probe -> nvidia-smi truth
import json, subprocess

HP = 'fleet/machines/bm-b.json'
h = json.load(open(HP, encoding='utf-8-sig'))
out = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader'],
                     capture_output=True, text=True)
free_mib = int(out.stdout.strip().split()[0])  # 2233
out2 = subprocess.run(['powershell', '-NoProfile', '-Command',
                        '[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB*1024,0)'],
                       capture_output=True, text=True)
free_mb = int(float(out2.stdout.strip()))
h['gpu_idle_vram_gb'] = round(free_mib / 1024.0, 1)
h['gpu_free_vram_gb'] = round(free_mib / 1024.0, 1)
h['gpu_free_vram_mb'] = free_mib
h['gpu_idle_vram_mb'] = free_mib
h['idle_ram_gb'] = round(free_mb / 1024.0, 1)
h['free_ram_gb'] = round(free_mb / 1024.0, 1)
h['idle_ram_mb'] = free_mb
with open(HP, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(h, f, ensure_ascii=False, indent=2)
    f.write('\n')
chk = json.load(open(HP, encoding='utf-8-sig'))
assert isinstance(chk['heartbeat_epoch_utc'], int)
print('patched: gpu_free_mib=%d idle_ram_mb=%d epoch_int=%s' % (free_mib, free_mb, isinstance(chk['heartbeat_epoch_utc'], int)))
