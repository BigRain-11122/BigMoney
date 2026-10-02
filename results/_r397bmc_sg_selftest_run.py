# -*- coding: utf-8 -*-
# r397 bm-c science_gates full selftest detached runner (M3 count edit verification)
import subprocess, os, time
REPO = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
PY = r'C:\Users\Dasheng\AppData\Local\Programs\Python\Python313\python.exe'
NW = 0x08000000
LOG = os.path.join(REPO, 'results', '_r397bmc_sg_selftest_log.txt')


def log(msg):
    with open(LOG, 'a', encoding='utf-8') as fh:
        fh.write(msg + '\n')
        fh.flush()


log('=== r397 bm-c science_gates selftest start %s ===' % time.strftime('%Y-%m-%d %H:%M:%S'))
env = dict(os.environ)
env['PYTHONPATH'] = REPO
t0 = time.time()
r = subprocess.run([PY, '-X', 'utf8', 'scripts\\science_gates.py', 'selftest'],
                   cwd=REPO, capture_output=True, creationflags=NW, env=env)
out = (r.stdout or b'').decode('utf-8', 'replace')
err = (r.stderr or b'').decode('utf-8', 'replace')
log('rc=%d elapsed=%.1fs' % (r.returncode, time.time() - t0))
for ln in out.splitlines()[-80:]:
    log('[out] ' + ln)
for ln in err.splitlines()[-30:]:
    log('[err] ' + ln)
log('=== selftest end ===')
