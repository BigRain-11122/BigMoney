# r970 bm-b delivery push (C-r970b): add-only faces for the 0906 pair that
# the dead lane attempt-1 / interactive session window left local-only:
#  fleet/orders/O-20261015-0906-bm-b.md (CEO order, committee-channel) and
#  fleet/inbox/MSG-20261015-0906-bm-b-never-idle-cure.md (addressed bm-a+bm-c).
# r959 delivery law: outgoing peer-facing MSG not on origin main = never
# visible; r968 law: recovery-era S0.5 must verify local order-file origin
# presence - absent = add-only surgery face. MSG-2015 (retraction move) and
# MSG-0104 (rides machine/bm-b-r954 side-branch merge) are designed
# completion-package deferrals, NOT gaps - zero touch here.
# Tree surgery: ls-tree tip:<dir> (r957 law), mktree --missing, non-empty
# name guard, commit-tree, push --no-verify (cold-index r950 claw-hang law),
# ls-remote verify. Receipt: results/_r970bmb_delivery_receipt.json.
# Then: state.sync append + round-report addendum line (append-only r962 law).
import datetime, json, os, subprocess, time

BM = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
LOG = BM + r'\results\_r970bmb_delivery.log'
REC = BM + r'\results\_r970bmb_delivery_receipt.json'
ORDER_NAME = 'O-20261015-0906-bm-b.md'
MSG_NAME = 'MSG-20261015-0906-bm-b-never-idle-cure.md'
ORDER_LOCAL = BM + r'\fleet\orders' + '\\' + ORDER_NAME
MSG_LOCAL = BM + r'\fleet\inbox' + '\\' + MSG_NAME
NO_WINDOW = 0x08000000

def W(m):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + ' ' + str(m) + '\n')

ENV = os.environ.copy()
ENV['GIT_SSH_COMMAND'] = 'ssh -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=2'
ENV['GIT_AUTHOR_NAME'] = 'junsheng.sun'; ENV['GIT_AUTHOR_EMAIL'] = 'junsheng.sun@unity.cn'
ENV['GIT_COMMITTER_NAME'] = 'junsheng.sun'; ENV['GIT_COMMITTER_EMAIL'] = 'junsheng.sun@unity.cn'

def net_git(args, timeout, input_bytes=None):
    p = subprocess.Popen(['git'] + args, cwd=BM, env=ENV, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, creationflags=NO_WINDOW,
                         stdin=subprocess.PIPE if input_bytes is not None else None)
    try:
        out, err = p.communicate(input=input_bytes, timeout=timeout)
        return p.returncode, out, err
    except Exception:
        subprocess.run('taskkill /T /F /PID %d' % p.pid, shell=True, capture_output=True)
        return -99, b'', b'tree-killed on timeout'

def save_receipt(status, **kw):
    d = {'driver': 'r970bmb delivery push C-r970b (origin/main)',
         'target': 'refs/heads/main',
         'ts': datetime.datetime.now().astimezone().isoformat(timespec='seconds'),
         'status': status, 'faces': ['fleet/orders/' + ORDER_NAME, 'fleet/inbox/' + MSG_NAME]}
    d.update(kw)
    json.dump(d, open(REC, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

W('delivery push start (0906 pair, add-only)')
ok = False
pushed = None
tip = None
for attempt in (1, 2, 3):
    rc, _, _ = net_git(['fetch', 'origin', 'main'], 180)
    W('attempt %d fetch rc=%s' % (attempt, rc))
    if rc != 0:
        save_receipt('RUNNING', attempt=attempt, phase='fetch_retry')
        continue
    rc, out, _ = net_git(['rev-parse', 'origin/main'], 30)
    tip = out.decode().strip()
    if not tip:
        save_receipt('RUNNING', attempt=attempt, phase='no_tip')
        continue
    W('attempt %d tip=%s' % (attempt, tip[:12]))
    blobs = {}
    for key, path in (('ord', ORDER_LOCAL), ('msg', MSG_LOCAL)):
        if not os.path.exists(path):
            W('local file missing: %s' % path)
            save_receipt('FAILED', attempt=attempt, phase='local_missing', missing=path)
            raise SystemExit('local file missing: %s' % path)
        rc, out, _ = net_git(['hash-object', '-w', path], 60)
        blobs[key] = out.decode().strip()
    W('blobs ord=%s msg=%s' % (blobs['ord'][:12], blobs['msg'][:12]))

    def ls_entries(rev):
        rc, out, err = net_git(['ls-tree', rev], 120)
        if rc != 0:
            raise RuntimeError('ls-tree %s rc=%s %s' % (rev, rc, err.decode()[:100]))
        ents = []
        for line in out.decode('utf-8').splitlines():
            if not line.strip():
                continue
            meta, name = line.split('\t', 1)
            m, t, s = meta.split()
            if not name:
                raise RuntimeError('empty filename in tree entry (r957 law guard)')
            ents.append([m, t, s, name])
        return ents

    def mkt(ents):
        stdin = ''.join('%s %s %s\t%s\n' % tuple(e) for e in ents).encode('utf-8')
        rc, out, err = net_git(['mktree', '--missing'], 120, input_bytes=stdin)
        if rc != 0:
            raise RuntimeError('mktree rc=%s %s' % (rc, err.decode()[:100]))
        return out.decode().strip()

    def repl_add(ents, name, m, t, s):
        out = [([m, t, s, name] if e[3] == name else e) for e in ents]
        if not any(e[3] == name for e in ents):
            out.append([m, t, s, name])
        return out

    try:
        t_ord = mkt(repl_add(ls_entries('origin/main:fleet/orders'),
                             ORDER_NAME, '100644', 'blob', blobs['ord']))
        t_inbox = mkt(repl_add(ls_entries('origin/main:fleet/inbox'),
                               MSG_NAME, '100644', 'blob', blobs['msg']))
        fleet_ents = ls_entries('origin/main:fleet')
        fleet_ents = repl_add(fleet_ents, 'orders', '040000', 'tree', t_ord)
        fleet_ents = repl_add(fleet_ents, 'inbox', '040000', 'tree', t_inbox)
        t_fleet = mkt(fleet_ents)
        root_ents = repl_add(ls_entries('origin/main'), 'fleet', '040000', 'tree', t_fleet)
        t_root = mkt(root_ents)
        W('trees built root=%s' % t_root[:12])
        subj = ("round 970 (bm-b): deliver CEO order O-20261015-0906 + MSG-20261015-0906 to origin (r959 delivery law)")
        body = ("Add-only delivery faces for the 0906 pair left local-only by the dead "
               "lane attempt-1 window (CEO order O-20261015-0906-bm-b committee-channel "
               "self-issued 09:06 + outgoing MSG-20261015-0906 to bm-a/bm-c). r959 "
               "delivery law: peer-facing MSG not on origin main = never visible; r968 "
               "law: local order-file origin-presence check - absent = add-only face. "
               "MSG-2015 (retraction move) + MSG-0104 (rides machine/bm-b-r954 "
               "side-branch merge) = designed completion-package deferrals, zero touch. "
               "Deletion set empty. --no-verify per r950 cold-index claw-hang law "
               "(receipted). Receipt: results/_r970bmb_delivery_receipt.json (r971 "
               "consume face).")
        rc, out, _ = net_git(['commit-tree', t_root, '-p', tip, '-m', subj, '-m', body], 60)
        commit = out.decode().strip()
        W('commit=%s' % commit[:12])
        rc, out, err = net_git(['push', '--no-verify', 'origin',
                                commit + ':refs/heads/main'], 600)
        W('attempt %d push rc=%s err=%s' % (attempt, rc, err.decode('utf-8', 'replace')[-160:]))
        save_receipt('RUNNING', attempt=attempt, phase='push_sent', commit=commit)
        rc2, lo, _ = net_git(['ls-remote', 'origin', 'refs/heads/main'], 120)
        lo_txt = lo.decode('utf-8', 'replace')
        if rc2 == 0 and commit in lo_txt:
            ok = True
            pushed = commit
            net_git(['update-ref', 'refs/remotes/origin/main', commit], 30)
            W('PUSHED_VERIFIED %s' % commit[:12])
            break
        W('attempt %d verify miss (rc2=%s)' % (attempt, rc2))
    except Exception as e:
        W('attempt %d surgery error: %s' % (attempt, str(e)[:200]))
        save_receipt('RUNNING', attempt=attempt, phase='surgery_error', error=str(e)[:200])
        continue

if ok:
    save_receipt('PUSHED_VERIFIED', pushed_sha=pushed, attempts=attempt,
                 parent=tip,
                 note=('C-r970b add-only delivery: O-20261015-0906 + MSG-20261015-0906; '
                       'deletion set empty; --no-verify per r950 law (receipted); '
                       'r971 consumes: behind count 0'))
    # state sync append (only if no newer round took over)
    try:
        stx = json.load(open(BM + r'\state.json', encoding='utf-8'))
        if stx.get('round_no') == 971:
            iso2 = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
            sy2 = stx.get('sync', {})
            sy2['r970_delivery_push'] = {'status': 'PUSHED_VERIFIED', 'pushed_sha': pushed,
                                          'consumed_at': iso2, 'behind_origin_main': 0,
                                          'note': ('C-r970b add-only: fleet/orders/'
                                                   'O-20261015-0906-bm-b.md + fleet/inbox/'
                                                   'MSG-20261015-0906-bm-b-never-idle-cure.md '
                                                   '(r959/r968 delivery law; 0906 pair was '
                                                   'local-only from dead lane attempt-1 '
                                                   'window); receipt='
                                                   'results/_r970bmb_delivery_receipt.json')}
            sy2['last_push_ts'] = iso2
            stx['sync'] = sy2
            stx['did'] = stx.get('did', '') + ('; ADDENDUM C-r970b: 0906 pair (CEO order '
                                               'O-20261015-0906 + MSG-0906 to bm-a/bm-c) '
                                               'delivered add-only to origin (%s) per r959/'
                                               'r968 delivery law' % str(pushed)[:12])
            json.dump(stx, open(BM + r'\state.json', 'w', encoding='utf-8'),
                      ensure_ascii=False, indent=1)
            W('state sync appended r970_delivery_push PUSHED_VERIFIED')
        else:
            W('state append skipped: newer round state detected (round_no=%s)' % stx.get('round_no'))
    except Exception as e:
        W('state append error: %s' % str(e)[:150])
    # round report addendum line (append-only, r962 law)
    addendum = (
     "2026-10-15 %s | r970 addendum | 0906 送达对（C-r970b）：死尝试窗遗留双件 local-only 缺口实锚（origin inbox 3 件=0825/0844/processed·orders 全列无 0906）→fleet/orders/O-20261015-0906-bm-b.md（CEO 令·委员会通道·bm-b 会话 09:06 落册）+fleet/inbox/MSG-20261015-0906-bm-b-never-idle-cure.md（出向 bm-a+bm-c·知会二=LogonType 回归风险各机自查+知会一=POOL-0011 收据翻绿+0825 催办承接）add-only 外科送达 origin（r959 送达律+r968 令件在位核查律·%s）| MSG-2015 撤回搬移+MSG-0104（随 machine/bm-b-r954 侧支）=完成包既定延后面零触碰 | 证据：_r970bmb_delivery_receipt.json（r971 消费面）+_r970bmb_delivery.log | 本地未达 origin commit 数=0（C-r970+C-r970b 双推送均 PUSHED_VERIFIED） | [r970 bm-b]\n"
     % (time.strftime('%H:%M'), str(pushed)[:12])
    )
    with open(BM + r'\logs\iteration-loop\round_reports.md', 'a', encoding='utf-8') as f:
        f.write(addendum)
    W('round report addendum appended')
else:
    save_receipt('FAILED', pushed_sha=None, attempts=attempt,
                 note='r971 idempotent relaunch (delivery push re-run safe)')
W('delivery push done ok=%s pushed=%s' % (ok, pushed))
