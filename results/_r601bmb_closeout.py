import subprocess, sys

def git(args):
    r = subprocess.run(['git'] + args, capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    return r.returncode, r.stdout, r.stderr

rc, out, err = git(['add', '-A', '--',
                    ':(exclude)results/_r603bmb_sens_partial_killed.jsonl',
                    ':(exclude)results/fund_value_p1/cells_VALUE-PB_x2.jsonl'])
print('add', rc, err.strip()[:200]); assert rc == 0, err

rc, out, err = git(['status', '--porcelain'])
staged = [l for l in out.splitlines() if l.strip() and l[0] in 'MADRC']
d = [l for l in staged if 'D' in l[:2]]
print('staged:', len(staged), 'D-in-staged:', len(d))
assert not d, 'D faces in staged set: ' + str(d[:5])
untracked_left = [l for l in out.splitlines() if l.startswith('??')]
print('untracked left:', [l[3:] for l in untracked_left])

msg = ("round 601 closeout (bm-b): S6 34/34 rc0 (dualrun ZERO-DRIFT streak 5, audit CLEAN, Golden Week no-new-bar legs honest no-op); "
       "bookkeeping four (state 601 / heartbeat epoch-int / round report / CODELY lesson: diverged-window invisible keepalive -> stale-claim "
       "takeover -> duplicate-burn face); autofill VALUEPB-X2 burn in flight (checkpoint cells_VALUE-PB_x2.jsonl + killed SENS partial left "
       "untracked by design: in-flight r532 live-write + superseded duplicate awaiting bm-a canonical). Product face of this round already "
       "delivered b1a99c1b3 (quality-family unblock).")
open('.codely-cli/scratch/r601bmb_close.txt', 'w', encoding='utf-8').write(msg)
rc, out, err = git(['commit', '-F', '.codely-cli/scratch/r601bmb_close.txt'])
print('commit', rc, (out + err).strip()[:200]); assert rc == 0, out + err

rc, out, err = git(['push'])
print('push', rc, (out + err).strip()[:250])
assert rc == 0, out + err

# delivery self-check
git(['fetch', 'origin'])
rc, ahead, _ = git(['rev-list', '--count', 'origin/main..HEAD'])
rc2, behind, _ = git(['rev-list', '--count', 'HEAD..origin/main'])
rc3, head, _ = git(['rev-parse', 'HEAD'])
rc4, ohead, _ = git(['rev-parse', 'origin/main'])
print('HEAD', head.strip()[:10], 'origin', ohead.strip()[:10],
      'ahead', ahead.strip(), 'behind', behind.strip())
assert ahead.strip() == '0', 'undelivered commits!'
assert behind.strip() == '0', 'origin advanced during closeout'
print('DELIVERY VERIFIED: N=0')
