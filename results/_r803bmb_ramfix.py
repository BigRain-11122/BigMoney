# r803 hotfix: free_ram probe fallback (ctypes GlobalMemoryStatusEx returned 0 = false data, fix before commit)
import json, subprocess
r = subprocess.run(['powershell', '-NoProfile', '-Command',
                    '(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory'],
                   capture_output=True, text=True, timeout=15)
free_kb = int(r.stdout.strip())
free_gb = round(free_kb / (1024**2), 2)
h = json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))
h['free_ram_gb'] = free_gb
json.dump(h, open('fleet/machines/bm-b.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
h2 = json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))
assert h2['free_ram_gb'] > 1.0, 'RAM probe still bad: %s' % h2['free_ram_gb']
print('free_ram_gb fixed =', h2['free_ram_gb'])
