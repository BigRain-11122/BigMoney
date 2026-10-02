# -*- coding: utf-8 -*-
# r397 bm-c S1 smoke detached runner (r324 law: detached + self-log; absolute
# PY path per r397 finalize pit -- 'python' from a pythonw host can resolve to
# ComfyUI python_embeded which lacks pandas)
import subprocess, os, time
REPO = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
PY = r'C:\Users\Dasheng\AppData\Local\Programs\Python\Python313\python.exe'
NW = 0x08000000
LOG = os.path.join(REPO, 'results', '_r397bmc_smoke_log.txt')


def log(msg):
    with open(LOG, 'a', encoding='utf-8') as fh:
        fh.write(msg + '\n')
        fh.flush()


log('=== r397 bm-c smoke start %s ===' % time.strftime('%Y-%m-%d %H:%M:%S'))
t0 = time.time()
r = subprocess.run([PY, '-X', 'utf8', '-m', 'smoke_test'],
                  cwd=REPO, capture_output=True, creationflags=NW)
out = (r.stdout or b'').decode('utf-8', 'replace')
err = (r.stderr or b'').decode('utf-8', 'replace')
log('rc=%d elapsed=%.1fs' % (r.returncode, time.time() - t0))
for ln in out.splitlines()[-60:]:
    log('[out] ' + ln)
for ln in err.splitlines()[-30:]:
    log('[err] ' + ln)
log('=== smoke end ===')
