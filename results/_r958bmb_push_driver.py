# r958 bm-b push driver: fetch-first then push C-r958 to machine/bm-b-r958, ls-remote verify.
# r953 laws: fetch-first builds merge-base so side-branch pack shrinks to delta; network git ops
# use Popen + self-managed taskkill /T /F tree-kill soft cap. Receipt = _r958bmb_push_receipt.json
# (r959 verify face). Idempotent: re-run safe.
import datetime, json, os, subprocess, time

BM = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
LOG = BM + r'\results\_r958bmb_push_driver.log'
REC = BM + r'\results\_r958bmb_push_receipt.json'
NO_WINDOW = 0x08000000
BRANCH = 'refs/heads/machine/bm-b-r958'

def W(m):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + ' ' + str(m) + '\n')

def save(status, **kw):
    d = {'driver': 'r958bmb push (machine/bm-b-r958)', 'target': BRANCH,
         'ts': datetime.datetime.now().astimezone().isoformat(timespec='seconds'), 'status': status}
    d.update(kw)
    json.dump(d, open(REC, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

def env():
    e = os.environ.copy()
    e['GIT_SSH_COMMAND'] = 'ssh -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=2'
    e['GIT_AUTHOR_NAME'] = 'junsheng.sun'; e['GIT_AUTHOR_EMAIL'] = 'junsheng.sun@unity.cn'
    e['GIT_COMMITTER_NAME'] = 'junsheng.sun'; e['GIT_COMMITTER_EMAIL'] = 'junsheng.sun@unity.cn'
    return e

def net_git(args, timeout):
    p = subprocess.Popen(['git'] + args, cwd=BM, env=env(),
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=NO_WINDOW)
    try:
        out, err = p.communicate(timeout=timeout)
        return p.returncode, out, err
    except Exception:
        subprocess.run(['taskkill', '/PID', str(p.pid), '/T', '/F'], capture_output=True)
        return -99, b'', b'tree-killed on timeout'

W('driver start pid=%d' % os.getpid())
save('RUNNING', phase='init')

rc, out, _ = net_git(['rev-parse', 'HEAD'], 30)
head = out.decode().strip()
if not head:
    save('FAILED', error='no HEAD'); W('FAIL no HEAD'); raise SystemExit(2)
W('head=%s' % head[:12])

ok = False; attempts = 0; fetch_ever_ok = False; last_line = ''
for attempt in (1, 2):
    attempts = attempt
    rc, _, _ = net_git(['fetch', 'origin', 'main'], 180)
    if rc == 0:
        fetch_ever_ok = True
    W('attempt %d fetch rc=%s' % (attempt, rc))
    rc, out, err = net_git(['push', '--no-verify', 'origin', head + ':' + BRANCH], 600)
    W('attempt %d push rc=%s out=%s err=%s' % (attempt, rc, out.decode('utf-8', 'replace')[-200:], err.decode('utf-8', 'replace')[-200:]))
    rc2, lo, _ = net_git(['ls-remote', 'origin', BRANCH], 120)
    lo_txt = lo.decode('utf-8', 'replace')
    last_line = lo_txt.strip().split('\n')[-1] if lo_txt.strip() else ''
    if rc2 == 0 and head in lo_txt:
        ok = True; break
    W('attempt %d verify miss, sleeping 20' % attempt)
    time.sleep(20)

if ok:
    save('PUSHED_VERIFIED', pushed_sha=head, head_at_exit=head, attempts=attempts,
         fetch_ever_ok=fetch_ever_ok, last_line=last_line,
         note='detached driver r958; delivers C-r958 (restore v3 driver + census + 300 instant restores + '
              'S0.5 NO_DELTA + state/report/heartbeat/CODELY r958 law); fetch-first design; --no-verify '
              'escape per cold-index pre-push claw hang law r950')
    W('PUSHED_VERIFIED %s' % head[:12])
else:
    save('FAILED', pushed_sha=None, head_at_exit=head, attempts=attempts,
         fetch_ever_ok=fetch_ever_ok, last_line=last_line,
         note='r959 relaunch idempotent (push driver re-run safe)')
    W('FAILED after %d attempts' % attempts)
