# -*- coding: utf-8 -*-
# r989 bm-b: POOL-0018/0019 anchor tooling install (whisperX + allin1), CPU-only, background pythonw.
# Card window: 10-18 17:41. venv-isolated per W009 notes; tsinghua mirror; file-log only (pythonw no-console law).
import os, sys, subprocess, datetime

BASE = r'C:\Fluxgroup\FluxGroup\media\drama-tools'
LOG = os.path.join(BASE, 'anchor-tools-install.log')
STATUS = os.path.join(BASE, 'anchor-tools-INSTALL-STATUS.txt')
VENV_W = os.path.join(BASE, 'venvs', 'whisperx')
VENV_A = os.path.join(BASE, 'venvs', 'allin1')
MIRROR = 'https://pypi.tuna.tsinghua.edu.cn/simple'
BASEPY = os.path.join(os.path.dirname(sys.executable), 'python.exe')

def log(msg):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write('%s %s\n' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), msg))

def run(cmd, timeout=5400):
    log('RUN ' + ' '.join(cmd))
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=timeout)
        rc = p.returncode
        outb, erb = p.stdout or b'', p.stderr or b''
    except subprocess.TimeoutExpired as e:
        log('TIMEOUT after %ds' % timeout)
        return 124
    log('RC=%d' % rc)
    for line in outb.decode('utf-8', 'replace').splitlines()[-12:]:
        log('  OUT ' + line[:200])
    for line in erb.decode('utf-8', 'replace').splitlines()[-12:]:
        log('  ERR ' + line[:200])
    return rc

log('INSTALL_START basepy=%s' % BASEPY)
os.makedirs(os.path.join(BASE, 'venvs'), exist_ok=True)

results = {}
for name, venv, pkg in (('whisperx', VENV_W, 'whisperx'), ('allin1', VENV_A, 'allin1')):
    vpy = os.path.join(venv, 'Scripts', 'python.exe')
    if not os.path.exists(vpy):
        rc = run([BASEPY, '-m', 'venv', venv])
        if rc != 0 or not os.path.exists(vpy):
            log('FATAL venv %s create fail rc=%s' % (name, rc))
            results[name] = (-1, -1)
            continue
    rc_i = run([vpy, '-m', 'pip', 'install', '--no-cache-dir', '-i', MIRROR, pkg])
    rc_v = run([vpy, '-c', 'import %s; print("import_ok")' % pkg])
    results[name] = (rc_i, rc_v)
    log('%s install=%d verify=%d' % (name, rc_i, rc_v))

with open(STATUS, 'w', encoding='utf-8') as f:
    for name in ('whisperx', 'allin1'):
        rc_i, rc_v = results.get(name, (-9, -9))
        f.write('%s install_rc=%d verify_rc=%d\n' % (name, rc_i, rc_v))
log('INSTALL_DONE ' + repr(results))
