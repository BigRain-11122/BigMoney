# -*- coding: utf-8 -*-
# r397 bm-c S0 integration: r589 revoke-FF-reland loop for unpushed r396 closeout.
# Laws: r589 (unpushed commit + origin advanced; live-write faces forbid rebase),
#       r593 (execution-time origin sha, never cached), r570/r600 (jsonl union in
#       bytes space, EOL per incumbent blob, dict-only rows), r595 (no blind D
#       restage), r385 (staged bookkeeping assert), r580 (python argv lists).
import subprocess, os, sys, json

REPO = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
NW = 0x08000000
POOL = 'results/pool_core_samples.jsonl'
MSGF = r'K:\Fluxgroup\FluxGroup\quant\.codely-cli\scratch\r397bmc_commit_msg.txt'
# per-machine faces: any foreign touch appearing as merge blocker here = abort
MY_FACES = {
    'state-bm-c.json', 'round_reports-bm-c.md', 'fleet/machines/bm-c.json',
    'results/autofill_state.bm-c.json', 'results/saturation_engine_state.bm-c.json',
    'results/saturation_engine/face_bm-c.json', 'results/compute_audit.bm-c.json',
}

def git(*args, check=True, binary=False):
    r = subprocess.run(['git'] + list(args), cwd=REPO, capture_output=True, creationflags=NW)
    if check and r.returncode != 0:
        print('GIT_FAIL %s :: %s' % (list(args), (r.stderr or b'').decode('utf-8', 'replace')[:600]))
        sys.exit(2)
    return r.stdout if binary else (r.stdout or b'').decode('utf-8', 'replace')

def fail(msg):
    print('ABORT: ' + msg)
    sys.exit(2)

def blob(rev, path):
    r = subprocess.run(['git', 'show', '%s:%s' % (rev, path)], cwd=REPO,
                       capture_output=True, creationflags=NW)
    if r.returncode != 0:
        fail('blob read %s:%s -> %s' % (rev, path, r.stderr.decode('utf-8', 'replace')[:200]))
    return r.stdout

def norm_lines(b):
    out = []
    for ln in b.split(b'\n'):
        if ln.endswith(b'\r'):
            ln = ln[:-1]
        if ln:
            out.append(ln)
    return out

def assert_dicts(lines, tag):
    for ln in lines:
        try:
            obj = json.loads(ln.decode('utf-8'))
        except Exception as e:
            fail('%s: non-json line: %r (%s)' % (tag, ln[:80], e))
        if not isinstance(obj, dict):
            fail('%s: non-dict row: %r' % (tag, ln[:80]))

def attempt_loop(round_tag):
    head = git('rev-parse', 'HEAD').strip()
    git('fetch', 'origin')
    origin = git('rev-parse', 'origin/main').strip()          # r593 execution-time
    ahead = int(git('rev-list', '--count', '%s..%s' % (origin, head)).strip())
    behind = int(git('rev-list', '--count', '%s..%s' % (head, origin)).strip())
    print('HEAD=%s origin=%s ahead=%d behind=%d' % (head[:9], origin[:9], ahead, behind))
    if ahead == 0 and behind == 0:
        print('ALREADY_INTEGRATED')
        return 'noop'
    if behind == 0:
        print('PURE_AHEAD: push-only path, nothing to re-land')
        return 'noop'
    if ahead != 1:
        fail('ahead=%d (expect exactly 1 unpushed commit)' % ahead)
    myc = head
    base = git('rev-parse', myc + '~1').strip()
    mb = git('merge-base', myc, origin).strip()
    if mb != base:
        fail('parent %s != merge-base %s' % (base[:9], mb[:9]))

    # 1) extract my pool rows (my commit blob vs base blob), bytes space
    base_l = norm_lines(blob(base, POOL))
    mine_l = norm_lines(blob(myc, POOL))
    base_set = set(base_l)
    my_new = [ln for ln in mine_l if ln not in base_set]
    assert_dicts(my_new, 'my_new')
    print('my_new pool rows=%d (base=%d mine=%d)' % (len(my_new), len(base_l), len(mine_l)))

    # 2) revoke unpushed commit (r589 step1)
    git('reset', '--mixed', base)
    print('reset --mixed -> base %s' % base[:9])

    # 3) clear FF blockers: dirty files that are also in merge delta
    st = git('status', '--porcelain')            # r380/r393: no whole-output strip
    dirty = []
    for line in st.splitlines():
        if not line.strip():
            continue
        xy, p = line[:2], line[3:]
        if '->' in p:
            fail('rename in status not handled: %s' % line)
        dirty.append(p)
    delta = [d.strip() for d in git('diff', '--name-only', base, origin).splitlines() if d.strip()]
    delta_set = set(delta)
    blockers = [p for p in dirty if p in delta_set]
    for p in blockers:
        if p in MY_FACES:
            fail('merge delta touches my per-machine face: %s' % p)
    if blockers:
        r = subprocess.run(['git', 'checkout', '--'] + blockers, cwd=REPO,
                           capture_output=True, creationflags=NW)
        if r.returncode != 0:
            fail('checkout blockers: %s' % r.stderr.decode('utf-8', 'replace')[:300])
    print('FF blockers cleared=%d (delta=%d dirty=%d)' % (len(blockers), len(delta), len(dirty)))

    # 4) pure FF to execution-time origin
    git('merge', '--ff-only', origin)
    print('FF -> %s' % origin[:9])

    # 5) union append my rows onto origin verbatim base (r570/r600 bytes law)
    org_b = blob(origin, POOL)
    crlf = org_b.count(b'\r\n')
    lone_lf = org_b.count(b'\n') - crlf
    eol = b'\r\n' if crlf >= lone_lf else b'\n'
    org_l = norm_lines(org_b)
    org_set = set(org_l)
    to_add = [ln for ln in my_new if ln not in org_set]
    # defensive: engine may have appended to working tree post-FF
    wp = os.path.join(REPO, POOL)
    wl = norm_lines(open(wp, 'rb').read())
    eng_new = [ln for ln in wl if ln not in org_set and ln not in to_add]
    if eng_new:
        assert_dicts(eng_new, 'engine_new')
        print('engine appended %d rows mid-surgery (merged too)' % len(eng_new))
        to_add = to_add + eng_new
    if to_add:
        body = org_b
        if body and not body.endswith(eol):
            body += eol
        for ln in to_add:
            body += ln + eol
        with open(wp, 'wb') as fh:
            fh.write(body)
        assert_dicts(norm_lines(open(wp, 'rb').read()), 'post_union')
        print('union: +%d rows -> %d lines (origin had %d)' % (len(to_add), len(org_l) + len(to_add), len(org_l)))

    # 6) stage kept content; r595 blind-D guard; r385 bookkeeping assert
    st2 = git('status', '--porcelain')
    paths = []
    for line in st2.splitlines():
        if not line.strip():
            continue
        xy, p = line[:2], line[3:]
        if 'D' in xy:
            fail('unexpected D row, refusing (r595): %s' % line)
        paths.append(p)
    r = subprocess.run(['git', 'add', '--'] + paths, cwd=REPO, capture_output=True, creationflags=NW)
    if r.returncode != 0:
        fail('git add: %s' % r.stderr.decode('utf-8', 'replace')[:300])
    cached = [x.strip() for x in git('diff', '--cached', '--name-only').splitlines() if x.strip()]
    need = {'state-bm-c.json', 'round_reports-bm-c.md', 'fleet/machines/bm-c.json'}
    if not need <= set(cached):
        fail('bookkeeping face assert failed (r385): missing %s' % (need - set(cached)))
    ns = git('diff', '--cached', '--name-status')
    for line in ns.splitlines():
        if line.startswith('D'):
            fail('staged deletion present: %s' % line)
    print('staged=%d files, zero deletions' % len(cached))

    # 7) commit -F (r375 long-msg law) + push; rejection = next loop attempt
    msg = ('round 397 (bm-c) S0: re-land r396 closeout after pure-FF integration with '
           'bm-a r605 (r589 revoke-FF-reland loop). Unpushed r396 closeout a55b914de met '
           'origin advance 14e4313b6 on shared base 54532b2d0. Loop: reset --mixed; 19 '
           'overlap shared-derive faces taken origin-verbatim (bm-a host derives fresher; '
           'daily_report/live_usage same-day idempotent regen); per-machine faces + '
           'bookkeeping kept verbatim; pool_core_samples.jsonl union-appended %d dict rows '
           '(bytes-space, EOL per incumbent, r570/r600). Engine live-write faces carried '
           'at current values. Zero deletions (claw clean). %s') % (len(to_add), round_tag)
    with open(MSGF, 'w', encoding='utf-8') as fh:
        fh.write(msg)
    git('commit', '-F', MSGF)
    new_head = git('rev-parse', 'HEAD').strip()
    print('committed %s' % new_head[:9])
    pr = subprocess.run(['git', 'push', 'origin', 'main'], cwd=REPO, capture_output=True, creationflags=NW)
    out = (pr.stdout or b'').decode('utf-8', 'replace')
    err = (pr.stderr or b'').decode('utf-8', 'replace')
    print('push rc=%d %s' % (pr.returncode, (out + ' ' + err).strip()[:300]))
    if pr.returncode == 0:
        git('fetch', 'origin')
        remote = git('rev-parse', 'origin/main').strip()
        ok = remote == new_head
        print('DELIVERED' if ok else 'NOT_DELIVERED remote=%s' % remote[:9])
        return 'pushed' if ok else 'retry'
    return 'retry'

def main():
    for i in range(3):
        res = attempt_loop('attempt %d' % (i + 1))
        if res in ('noop', 'pushed'):
            print('S0_INTEGRATE_OK ' + res)
            return 0
        print('--- retrying loop (origin moved or push rejected) ---')
    fail('3 attempts exhausted')
    return 2

if __name__ == '__main__':
    sys.exit(main())
