# -*- coding: utf-8 -*-
# r397 bm-c LOWAMP-DEEP-P1 E1 three-leg detached runner (r324 law)
import subprocess, os, time
REPO = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
PY = r'C:\Users\Dasheng\AppData\Local\Programs\Python\Python313\python.exe'
NW = 0x08000000
LOG = os.path.join(REPO, 'results', '_r397bmc_e1_log.txt')

def log(msg):
    with open(LOG, 'a', encoding='utf-8') as fh:
        fh.write(msg + '\n')
        fh.flush()

log('=== r397 bm-c E1 three-leg start %s ===' % time.strftime('%Y-%m-%d %H:%M:%S'))
t0 = time.time()
r = subprocess.run([PY, '-X', 'utf8', r'results\_r397bmc_e1_three_leg.py'],
                   cwd=REPO, capture_output=True, creationflags=NW)
out = (r.stdout or b'').decode('utf-8', 'replace')
err = (r.stderr or b'').decode('utf-8', 'replace')
log('rc=%d elapsed=%.1fs' % (r.returncode, time.time() - t0))
for ln in out.splitlines():
    log('[out] ' + ln)
for ln in err.splitlines():
    log('[err] ' + ln)
log('=== E1 end ===')
