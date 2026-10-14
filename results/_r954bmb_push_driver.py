# r954 bm-b detached push driver: deliver local main C3 (r954 products) to origin
# side-branch machine/bm-b-r954. Same fetch-first design as r953 driver (giant-pack
# root-cause fix), tree-kill soft caps (r953 law), per-attempt HEAD snapshot, final
# ls-remote verify -> receipt json (r955 consumption face). Idempotent relaunch.
# ASCII only. Detached via pythonw.
import os, subprocess, time, datetime, json

bm = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
LOG = bm + r'\results\_r954bmb_push_driver.log'
RECEIPT = bm + r'\results\_r954bmb_push_receipt.json'
TARGET = 'refs/heads/machine/bm-b-r954'
NO_WINDOW = 0x08000000

def W(m):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + ' ' + m + '\n')

def git_cmd(args, cap):
    env = os.environ.copy()
    env['GIT_SSH_COMMAND'] = ('ssh -o ConnectTimeout=25 -o ServerAliveInterval=15 '
                             '-o ServerAliveCountMax=4')
    p = subprocess.Popen(['git'] + args, cwd=bm, env=env, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, creationflags=NO_WINDOW)
    try:
        out = p.communicate(timeout=cap)[0].decode('utf-8', 'replace')
        return p.returncode, out
    except subprocess.TimeoutExpired:
        subprocess.run(['taskkill', '/T', '/F', '/PID', str(p.pid)],
                       capture_output=True, creationflags=NO_WINDOW)
        try:
            p.communicate(timeout=30)
        except Exception:
            pass
        return -98, 'SOFTCAP_TREEKILL after %ss' % cap

W('driver start pid=%d' % os.getpid())
settled = None
attempts = 0
fetch_ok_ever = False
last = 'none'
for i in range(1, 13):
    attempts = i
    rc, out = git_cmd(['fetch', 'origin', 'main'], 180)
    W('attempt %d fetch origin main rc=%s out=%s' % (i, rc, out.replace('\n', ' | ')[:160]))
    if rc == 0:
        fetch_ok_ever = True
    else:
        if not fetch_ok_ever:
            W('attempt %d push skipped (no fetch base yet - avoid giant pack)' % i)
            time.sleep(180)
            continue
    rc, head = git_cmd(['rev-parse', 'HEAD'], 30)
    if rc != 0:
        W('attempt %d rev-parse fail' % i)
        time.sleep(180)
        continue
    head = head.strip()
    rc, out = git_cmd(['push', '--no-verify', 'origin', head + ':' + TARGET], 900)
    W('attempt %d push %s rc=%s out=%s' % (i, head[:12], rc, out.replace('\n', ' | ')[:240]))
    if rc == 0:
        rc2, out2 = git_cmd(['ls-remote', 'origin', TARGET], 60)
        ok = (rc2 == 0 and head in out2)
        W('attempt %d verify rc=%s remote_has=%s' % (i, rc2, ok))
        if ok:
            rc3, head2 = git_cmd(['rev-parse', 'HEAD'], 30)
            head2 = head2.strip() if rc3 == 0 else 'unknown'
            if head2 == head:
                settled = head
                last = out2.strip()[:100]
                break
            W('attempt %d pushed %s but HEAD advanced to %s - next attempt' % (i, head[:12], head2[:12]))
    time.sleep(180)

if settled:
    status = 'PUSHED_VERIFIED'
else:
    rc2, out2 = git_cmd(['ls-remote', 'origin', TARGET], 60)
    if rc2 == 0 and out2.strip():
        status = 'REMOTE_HAS_SOME'
        last = out2.strip()[:140]
    else:
        status = 'ATTEMPTS_EXHAUSTED'
        last = out2[:140] if rc2 == 0 else 'ls-remote fail rc=%s' % rc2
rc3, headnow = git_cmd(['rev-parse', 'HEAD'], 30)
receipt = {
    'status': status,
    'pushed_sha': settled,
    'head_at_exit': (headnow.strip()[:12] if rc3 == 0 else 'unknown'),
    'target': TARGET,
    'attempts': attempts,
    'fetch_ever_ok': fetch_ok_ever,
    'last_line': last,
    'ts': datetime.datetime.now().astimezone().isoformat(timespec='seconds'),
    'note': ('detached driver r954; delivers C3 (r954 products: G5 receipt MSG + state/round-report/heartbeat/CODELY '
             '+ blobfill driver artifacts); fetch-first design; --no-verify documented escape (cold-index pre-push claw hang law r950)'),
}
with open(RECEIPT, 'w', encoding='utf-8') as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
W('driver done status=%s attempts=%d' % (status, attempts))
