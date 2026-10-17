# -*- coding: utf-8 -*-
# r1066 runner: byte-capture the W261 prereg derive stdout/stderr into a UTF-8 log
# (PS5.1 console is GBK; direct console print of CJK gate errors = mojibake)
import subprocess, sys, os
ROOT = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
os.chdir(ROOT)
env = dict(os.environ)
env['PYTHONIOENCODING'] = 'utf-8'
r = subprocess.run([sys.executable, 'results/_w261bmc_prereg_derive.py'],
                   capture_output=True, env=env)
log = ROOT + r'\results\_r1066bmc_derive_run.log'
with open(log, 'wb') as f:
    f.write(('RC=%d\n' % r.returncode).encode('ascii'))
    f.write(b'=== STDOUT ===\n'); f.write(r.stdout)
    f.write(b'\n=== STDERR ===\n'); f.write(r.stderr)
out = (r.stdout or b'').decode('utf-8', 'replace')
err = (r.stderr or b'').decode('utf-8', 'replace')
def safe(s):
    return s.encode('ascii', 'replace').decode('ascii')
print('DERIVE_RC=%d' % r.returncode)
print('--- stdout tail ---')
for ln in out.strip().splitlines()[-15:]:
    print('O|' + safe(ln))
print('--- stderr tail ---')
for ln in err.strip().splitlines()[-15:]:
    print('E|' + safe(ln))
