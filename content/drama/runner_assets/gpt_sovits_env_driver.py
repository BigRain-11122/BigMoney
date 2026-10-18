"""GPT-SoVITS environment bootstrap driver (drama voice-library lane, ST-005).

Phased, idempotent, detached-carrier install for the ST-003 chosen main engine
(GPT-SoVITS, MIT license, clone already at media/drama-tools/GPT-SoVITS).

Law carriers:
  - pit-spawn: __main__ guard (r324/r699); CREATE_NO_WINDOW children (r700);
    detached ignition with explicit std redirect + close_fds=True (r317);
    python -u + flush=True + incremental log (r680); rc/status face polled only
    after host-exit probe (r748) -- here the driver itself owns the log.
  - astock spawn_detached precedent (scripts/update_astock_daily.py L701).
  - CPU lane per VOICE-PIPELINE-SKELETON-v1 sec.6 (GPU face = ST-002 gate).
  - PyPI default torch on Windows = CPU build; tsinghua mirror carries it, so
    no pytorch.org index needed for the CPU lane (honest note vs install.ps1).

Phases (each idempotent, checkpointed in the status face):
  venv -> torch -> deps -> weights -> extras -> smoke

Commands:
  run        full phased run (detached carrier body)
  status     one-line JSON verdict from the status face
  selftest   offline asserts, no network no installs

Status face: results/drama_env/gpt_sovits_env_status.json (in-repo, small).
Log:         media/drama-tools/.gpt_sovits_env_install.log (gitignored area).
"""
import datetime
import io
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
GRP = r'C:\Fluxgroup\FluxGroup'
REPO = os.path.join(GRP, 'media', 'drama-tools', 'GPT-SoVITS')
VENV = os.path.join(REPO, 'runtime')
VPY = os.path.join(VENV, 'Scripts', 'python.exe')
LOG = os.path.join(GRP, 'media', 'drama-tools', '.gpt_sovits_env_install.log')
STATUS = os.path.join(ROOT, 'results', 'drama_env', 'gpt_sovits_env_status.json')
REQ = os.path.join(REPO, 'requirements.txt')
EXTRA_REQ = os.path.join(REPO, 'extra-req.txt')
FILTERED = os.path.join(REPO, 'requirements.filtered.txt')
DEPS_OK = os.path.join(REPO, '.env-deps-ok')
SMOKE_OK = os.path.join(REPO, '.env-smoke-ok')
PHASES = ['venv', 'torch', 'deps', 'weights', 'extras', 'smoke']
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) fleet-bmb-st005'}
MS_BASE = 'https://www.modelscope.cn/models/XXXXRT/GPT-SoVITS-Pretrained/resolve/master/'
WEIGHTS = [
    (MS_BASE + 'pretrained_models.zip', os.path.join(REPO, 'pretrained_models.zip'),
     os.path.join(REPO, 'GPT_SoVITS'), 'GPT_SoVITS/pretrained_models/sv'),
    (MS_BASE + 'G2PWModel.zip', os.path.join(REPO, 'G2PWModel.zip'),
     os.path.join(REPO, 'GPT_SoVITS', 'text'), 'GPT_SoVITS/text/G2PWModel'),
]
EXTRA_DL = [
    (MS_BASE + 'nltk_data.zip', os.path.join(REPO, 'nltk_data.zip'), 'nltk'),
    (MS_BASE + 'open_jtalk_dic_utf_8-1.11.tar.gz',
     os.path.join(REPO, 'open_jtalk_dic_utf_8-1.11.tar.gz'), 'openjtalk'),
]
_NO_WINDOW = 0x08000000  # CREATE_NO_WINDOW (r700 law)
SUBPROC_TIMEOUT = {'venv': 600, 'pip_common': 900, 'torch': 2400, 'deps': 3600}


def now_iso():
    return datetime.datetime.now().isoformat(timespec='seconds')


def log(msg):
    line = '%s %s' % (now_iso(), msg)
    print(line, flush=True)  # -u + flush law (r680)
    try:
        with io.open(LOG, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except Exception:
        pass


def rd_status():
    try:
        with io.open(STATUS, 'r', encoding='utf-8-sig') as f:
            return json.load(f)
    except Exception:
        return {'schema': 'gpt-sovits-env-v1', 'phases_done': [], 'errors': []}


def wr_status(patch):
    st = rd_status()
    st.update(patch)
    st['updated_at'] = now_iso()
    os.makedirs(os.path.dirname(STATUS), exist_ok=True)
    tmp = STATUS + '.tmp'
    with io.open(tmp, 'w', encoding='utf-8') as f:
        json.dump(st, f, ensure_ascii=False, indent=1)
    os.replace(tmp, STATUS)
    return st


def run(cmd, timeout, cwd=None, check=True):
    """Child spawn: CREATE_NO_WINDOW per r700 (never DETACHED for children)."""
    log('RUN ' + ' '.join(cmd[:6]) + (' ...' if len(cmd) > 6 else ''))
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=timeout, cwd=cwd,
                           creationflags=_NO_WINDOW)
    except subprocess.TimeoutExpired:
        log('TIMEOUT after %ss: %s' % (timeout, cmd[:3]))
        return 124, '', 'timeout'
    out = (r.stdout or b'').decode('utf-8', 'replace')
    err = (r.stderr or b'').decode('utf-8', 'replace')
    tail = (out + err).strip().splitlines()
    for l in tail[-40:]:
        log('  | ' + l[:240])
    if check and r.returncode != 0:
        log('RC=%d (fail)' % r.returncode)
    else:
        log('RC=%d' % r.returncode)
    return r.returncode, out, err


def filter_requirements():
    """Drop the '--no-binary=opencc' directive line (source build needs
    MSVC+cmake absent here); wheel route is the Windows fallback. Pure fn."""
    with io.open(REQ, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.read().splitlines()
    kept, dropped = [], []
    for ln in lines:
        s = ln.strip()
        if s.startswith('--no-binary'):
            dropped.append(s)
        else:
            kept.append(ln)
    return kept, dropped


def _pkg_of(line):
    """Bare package name from a requirements line ('pyopenjtalk>=0.4.1' ->
    'pyopenjtalk'); pure fn."""
    s = line.strip()
    for sep in ('>=', '<=', '==', '!=', '~=', '>', '<', ' ', ';', '['):
        i = s.find(sep)
        if i > 0:
            s = s[:i]
    return s.lower()


def failing_pkg(full_text):
    """Build-failure-aware: the failing sdist is the last 'Collecting X' line
    before the first 'subprocess-exited-with-error' block (pip aborts there);
    fallback patterns for resolution failures. Takes FULL pip output."""
    i = full_text.find('subprocess-exited-with-error')
    if i >= 0:
        cands = re.findall(r'Collecting ([A-Za-z0-9_.\-]+)', full_text[:i])
        if cands:
            return cands[-1]
    for pat in (r'satisfies the requirement ([A-Za-z0-9_.\-]{2,40})',
                r'No matching distribution found for ([A-Za-z0-9_.\-]{2,40})',
                r'Failed to build ([A-Za-z0-9_.\-]{2,40})'):
        m = re.search(pat, full_text)
        if m:
            return m.group(1)
    return None


def stream_download(url, dest, tries=2):
    for attempt in range(1, tries + 1):
        try:
            log('DL try%d %s -> %s' % (attempt, url, os.path.basename(dest)))
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as resp:
                total = int(resp.headers.get('Content-Length') or 0)
                got = 0
                with io.open(dest, 'wb') as f:
                    while True:
                        chunk = resp.read(1024 * 1024)
                        if not chunk:
                            break
                        f.write(chunk)
                        got += len(chunk)
                        if got % (64 * 1024 * 1024) < len(chunk):
                            pct = ('%.1f%%' % (100.0 * got / total)) if total else '?'
                            log('  .. %d MB (%s)' % (got // (1024 * 1024), pct))
            log('DL done %d MB' % (got // (1024 * 1024)))
            return True
        except Exception as e:
            log('DL ERROR: %s' % str(e)[:200])
            if attempt >= tries:
                return False
            time.sleep(20)
    return False


def extract_zip(src, dest, marker_dir=None, strip_one=False):
    if marker_dir and os.path.isdir(marker_dir):
        log('  marker present, skip unzip: %s' % marker_dir)
        return True
    os.makedirs(dest, exist_ok=True)
    with zipfile.ZipFile(src) as z:
        names = z.namelist()
        if strip_one:
            for n in names:
                z.extract(n, dest)
        else:
            z.extractall(dest)
    log('  unzipped %d entries -> %s' % (len(names), dest))
    return True


def phase_venv():
    if os.path.exists(VPY):
        log('venv exists, skip')
        return True
    rc, _, _ = run([sys.executable, '-m', 'venv', VENV], SUBPROC_TIMEOUT['venv'])
    return rc == 0 and os.path.exists(VPY)


def phase_torch():
    rc, out, _ = run([VPY, '-c', 'import torch, torchaudio'], 120)
    if rc == 0:
        log('torch already importable, skip')
        return True
    rc, _, _ = run([VPY, '-m', 'pip', 'install', '--disable-pip-version-check',
                    'torch', 'torchaudio'], SUBPROC_TIMEOUT['torch'])
    if rc != 0:
        return False
    rc, out, _ = run([VPY, '-c', 'import torch; print(torch.__version__)'], 120)
    log('torch version: %s' % out.strip()[:60])
    return rc == 0


def phase_deps():
    if os.path.exists(DEPS_OK):
        log('deps marker present, skip')
        return True
    if not os.path.exists(EXTRA_REQ):
        log('extra-req.txt missing (honest skip)')
    else:
        rc, _, _ = run([VPY, '-m', 'pip', 'install', '--disable-pip-version-check',
                        '-r', EXTRA_REQ, '--no-deps'], SUBPROC_TIMEOUT['pip_common'])
        if rc != 0:
            return False
    kept, dropped = filter_requirements()
    if dropped:
        log('requirements directive dropped (source-build needs MSVC): %s' % dropped)
    strips = []
    for attempt in range(5):
        with io.open(FILTERED, 'w', encoding='utf-8') as f:
            f.write('\n'.join(kept) + '\n')
        rc, out, err = run([VPY, '-m', 'pip', 'install', '--disable-pip-version-check',
                            '-r', FILTERED], SUBPROC_TIMEOUT['deps'])
        if rc == 0:
            # fallback leg: if pyopenjtalk was stripped (MSVC-less source
            # build), the maintained fork ships a cp311 win wheel under the
            # same module name (借力: pyopenjtalk-plus). Best-effort, non-fatal.
            rc2, o2, e2 = run([VPY, '-c', 'import pyopenjtalk'], 120)
            if rc2 != 0:
                rc3, _, _ = run([VPY, '-m', 'pip', 'install', '--disable-pip-version-check',
                                 'pyopenjtalk-plus'], SUBPROC_TIMEOUT['pip_common'])
                if rc3 == 0:
                    run([VPY, '-c', 'import pyopenjtalk; print("pyopenjtalk-plus OK")'], 120)
                else:
                    log('pyopenjtalk-plus fallback FAILED (Japanese normalization '
                        'degrades honestly; CJK-first env unaffected)')
            with io.open(DEPS_OK, 'w', encoding='utf-8') as f:
                f.write('ok %s strips=%s\n' % (now_iso(), strips))
            return True
        tail = out + err
        pkg = failing_pkg(tail)
        if not pkg or pkg.lower() in [s.lower() for s in strips]:
            log('deps failed, no further auto-strip (pkg=%s)' % pkg)
            return False
        before = len(kept)
        kept = [l for l in kept if _pkg_of(l) != pkg.lower()]
        if len(kept) == before:
            log('deps failed, cannot strip %s' % pkg)
            return False
        strips.append(pkg)
        log('stripped failing pkg (will note in receipt): %s' % pkg)
    return False


def phase_weights():
    all_ok = True
    for url, zip_path, dest_dir, marker_dir in WEIGHTS:
        if os.path.isdir(marker_dir):
            log('weights marker present, skip %s' % marker_dir)
            continue
        if not os.path.exists(zip_path):
            if not stream_download(url, zip_path):
                all_ok = False
                continue
        # pretrained zip extracts a top-level pretrained_models/ dir into GPT_SoVITS/
        try:
            extract_zip(zip_path, dest_dir)
            os.remove(zip_path)
        except Exception as e:
            log('unzip ERROR %s: %s' % (os.path.basename(zip_path), str(e)[:200]))
            all_ok = False
    return all_ok


def phase_extras():
    ok = True
    for url, dest, kind in EXTRA_DL:
        try:
            if kind == 'nltk':
                target = VENV  # sys.prefix of the venv python == VENV root
                marker = os.path.join(target, 'nltk_data')
                if os.path.isdir(marker):
                    log('nltk_data present, skip')
                    continue
                if not os.path.exists(dest):
                    if not stream_download(url, dest):
                        ok = False
                        continue
                extract_zip(dest, target, marker_dir=marker)
                os.remove(dest)
            else:  # openjtalk dict -- only meaningful if pyopenjtalk importable
                rc, out, _ = run([VPY, '-c', 'import pyopenjtalk, os; print(os.path.dirname(pyopenjtalk.__file__))'], 120)
                if rc != 0:
                    log('pyopenjtalk not importable, skip open_jtalk dict (CJK-first env)')
                    continue
                pkg_dir = out.strip().splitlines()[-1]
                marker = os.path.join(pkg_dir, 'open_jtalk_dic_utf_8-1.11')
                if os.path.isdir(marker):
                    log('open_jtalk dic present, skip')
                    continue
                if not os.path.exists(dest):
                    if not stream_download(url, dest):
                        ok = False
                        continue
                rc, _, _ = run([sys.executable, '-c',
                                'import tarfile,sys; tarfile.open(sys.argv[1]).extractall(sys.argv[2])',
                                dest, pkg_dir], 600)
                if rc == 0:
                    os.remove(dest)
                else:
                    ok = False
        except Exception as e:
            log('extras ERROR %s: %s' % (kind, str(e)[:200]))
            ok = False
    return ok


SMOKE_IMPORTS = ('torch', 'torchaudio', 'librosa', 'funasr', 'transformers',
                 'gradio', 'jieba', 'pypinyin', 'cn2an')


def phase_smoke():
    if os.path.exists(SMOKE_OK):
        log('smoke marker present, skip')
        return True
    code = 'import %s; import torch; print("torch", torch.__version__, "cuda", torch.cuda.is_available())' % ', '.join(SMOKE_IMPORTS)
    rc, out, err = run([VPY, '-c', code], 600)
    if rc != 0:
        log('smoke FAIL (see tail above)')
        return False
    log('smoke tail: %s' % (out + err).strip().splitlines()[-1][:120])
    ff = shutil.which('ffmpeg')
    log('ffmpeg probe: %s' % (ff or 'NOT FOUND (needed by webui/inference)'))
    with io.open(SMOKE_OK, 'w', encoding='utf-8') as f:
        f.write('ok %s ffmpeg=%s\n' % (now_iso(), bool(ff)))
    return True


PHASE_FN = {'venv': phase_venv, 'torch': phase_torch, 'deps': phase_deps,
            'weights': phase_weights, 'extras': phase_extras, 'smoke': phase_smoke}


def do_run():
    prior = rd_status()
    st = wr_status({'schema': 'gpt-sovits-env-v1', 'state': 'running', 'pid': os.getpid(),
                   'started_at': now_iso(), 'phases_done': prior.get('phases_done', []),
                   'errors': prior.get('errors', []), 'log': LOG,
                   'driver': os.path.abspath(__file__)})
    for ph in PHASES:
        if ph in st['phases_done']:
            log('phase %s already done (checkpoint), skip' % ph)
            continue
        wr_status({'phase': ph, 'phase_state': 'running'})
        log('=== PHASE %s ===' % ph)
        try:
            ok = PHASE_FN[ph]()
        except Exception as e:
            log('PHASE %s EXC %s' % (ph, str(e)[:240]))
            ok = False
        if not ok:
            errs = rd_status().get('errors', [])
            errs.append({'phase': ph, 'ts': now_iso()})
            wr_status({'phase': ph, 'phase_state': 'failed', 'state': 'failed',
                       'errors': errs})
            log('DRIVER STOP at phase %s (honest fail; status face carries state)' % ph)
            return 1
        st = wr_status({'phase': ph, 'phase_state': 'done'})
        st['phases_done'].append(ph)
        wr_status({'phases_done': st['phases_done']})
    wr_status({'state': 'done', 'phase': 'all', 'phase_state': 'done',
               'finished_at': now_iso()})
    log('DRIVER DONE all phases')
    return 0


def pid_alive(pid):
    if not pid:
        return False
    try:
        r = subprocess.run(['powershell.exe', '-NoProfile', '-Command',
                            '(Get-Process -Id %d -ErrorAction SilentlyContinue) -ne $null' % int(pid)],
                           capture_output=True, text=True, timeout=30,
                           creationflags=_NO_WINDOW)
        return r.stdout.strip().lower() == 'true'
    except Exception:
        return False


def do_status():
    st = rd_status()
    live = pid_alive(st.get('pid')) and st.get('state') == 'running'
    print(json.dumps({'state': st.get('state'), 'live': live,
                      'phase': st.get('phase'), 'phase_state': st.get('phase_state'),
                      'phases_done': st.get('phases_done', []),
                      'updated_at': st.get('updated_at'),
                      'errors': len(st.get('errors', []))}, ensure_ascii=False))
    return 0


def selftest():
    asserts = []
    kept, dropped = filter_requirements()
    asserts.append(('filter-drops-nobinary', dropped == ['--no-binary=opencc'] and len(kept) > 20))
    asserts.append(('filter-keeps-torchaudio', any('torchaudio' in l for l in kept)))
    assert len(PHASES) == len(set(PHASES))
    asserts.append(('phases-unique', True))
    ok_zip = False
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        zp = os.path.join(td, 't.zip')
        with zipfile.ZipFile(zp, 'w') as z:
            z.writestr('a/b.txt', 'x')
        try:
            extract_zip(zp, os.path.join(td, 'out'))
            ok_zip = os.path.exists(os.path.join(td, 'out', 'a', 'b.txt'))
        except Exception:
            ok_zip = False
    asserts.append(('zip-extract-purefn', ok_zip))
    asserts.append(('failing-pkg-regex', failing_pkg("Could not find a version that satisfies the requirement jieba_fast==0.1") == 'jieba_fast'))
    asserts.append(('pkg-of-versioned', _pkg_of('pyopenjtalk>=0.4.1') == 'pyopenjtalk'))
    asserts.append(('pkg-of-extras', _pkg_of('fastapi[standard]>=0.115.2') == 'fastapi'))
    asserts.append(('pkg-of-plain', _pkg_of('tqdm') == 'tqdm'))
    sample = ('Collecting cn2an (from -r x (line 13))\n'
              'Collecting pyopenjtalk>=0.4.1 (from -r x (line 15))\n'
              'Installing build dependencies: finished\n'
              'error: subprocess-exited-with-error\n'
              'Getting requirements to build wheel did not run successfully.')
    asserts.append(('failing-pkg-buildblock', failing_pkg(sample) == 'pyopenjtalk'))
    asserts.append(('status-face-path-in-repo', STATUS.startswith(ROOT)))
    rc = 0 if all(ok for _, ok in asserts) else 1
    print(json.dumps({'selftest': 'PASS' if rc == 0 else 'FAIL',
                      'asserts': {k: v for k, v in asserts}}, ensure_ascii=False))
    return rc


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'status'
    if cmd == 'run':
        sys.exit(do_run())
    elif cmd == 'status':
        sys.exit(do_status())
    elif cmd == 'selftest':
        sys.exit(selftest())
    else:
        print(json.dumps({'verdict': 'usage', 'cmds': ['run', 'status', 'selftest']}))
        sys.exit(2)
