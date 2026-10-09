import re, os, datetime, subprocess, json

def clean(s):
    return re.sub(r'[^\x20-\x7e]', ' ', s)

p = r'D:\musubi-tuner\outputs\jman_v1_640\train_log.txt'
if os.path.exists(p):
    d = open(p, 'rb').read().decode('utf-8', 'replace')
    cl = re.sub(r'[^\x20-\x7e]', ' ', d)
    words = [w for w in cl.split() if w.strip()]
    print('LOG_LEN', len(d))
    print('MTIME', datetime.datetime.fromtimestamp(os.path.getmtime(p)))
    print('TAIL', ' | '.join(words[-15:]))
else:
    print('LOG ABSENT')

p2 = r'D:\musubi-tuner\outputs\jman_v1_640\TRAIN_EXIT_1.txt'
if os.path.exists(p2):
    print('EXIT1', clean(open(p2, encoding='utf-8', errors='replace').read()).strip()[:200])

p3 = r'K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r824bmc_train_probe.txt'
if os.path.exists(p3):
    print('PROBE', clean(open(p3, encoding='utf-8', errors='replace').read())[:700])

r = subprocess.run(['powershell', '-NoProfile', '-Command',
                    "(Get-CimInstance Win32_Process -Filter 'ProcessId=55208').CommandLine"],
                   capture_output=True, text=True)
print('LAUNCHER', (r.stdout.strip()[:400] if r.stdout.strip() else 'PS55208_GONE'))

r2 = subprocess.run(['powershell', '-NoProfile', '-Command',
                    '[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,1)'],
                    capture_output=True, text=True)
print('FREE_RAM_GB', r2.stdout.strip())

# launcher bat / runner scripts in D:\musubi-tuner root, newest first
for f in sorted(glob if False else [], ): pass
import glob
for f in sorted(glob.glob(r'D:\musubi-tuner\*run*'), key=os.path.getmtime, reverse=True)[:5]:
    print('RUNNER', f, os.path.getmtime(f))
