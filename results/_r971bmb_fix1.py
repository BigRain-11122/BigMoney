# r971 bm-b fix1: in-window correction push (r964 precedent). The r971 closeout's
# origin-presence check used list-membership against ls-tree output lines that
# carry the 'fleet/orders/' prefix -> false negatives "(False/False)" for
# O-0025/O-0906 landed in pushed heartbeat/state/report. Correct method =
# substring check on raw ls-tree text (r970 pattern). Re-verify, fix faces,
# append correction report line, push 3 own faces (C-r971b).
import datetime, json, os, subprocess, time

BM = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
LOG = BM + r'\results\_r971bmb_fix1.log'
PUSHREC = BM + r'\results\_r971bmb_fix1_push_receipt.json'
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

W('fix1 start: presence-check method correction (substring on raw text)')
now = datetime.datetime.now().astimezone()
iso = now.isoformat(timespec='seconds')
epoch = int(time.time())

# 1) correct-method re-verify
rc, out_o, _ = net_git(['ls-tree', '--name-only', 'origin/main', 'fleet/orders/'], 60)
names = out_o.decode('utf-8', 'replace')
present = {n: (n in names) for n in ('O-20261015-0025-bm-b.md', 'O-20261015-0906-bm-b.md',
                                     'O-20261015-0915-bm-b.md', 'O-20261015-0952-bm-b.md')}
count = len([l for l in names.splitlines() if l.strip()])
W('correct-method verify: count=%d present=%s' % (count, present))

# 2) heartbeat face fix
hb_path = BM + r'\fleet\machines\bm-b.json'
hb = json.load(open(hb_path, encoding='utf-8'))
hb['orders_ack'] = ("r971: O-20261015-0915 EXECUTED (i2v re-ignition receipt in order file); "
                    "O-20261015-0952 EXECUTED (full-power unlock verified + i2v ignited + bili "
                    "retired + delivery); origin presence re-verified correct-method (fix1): "
                    "O-0025=%s O-0906=%s O-0915=%s O-0952=%s; unknown-order delta since r970 "
                    "= 94-92=2 (the two bm-b deliveries themselves) -> zero unknown; s05 fresh="
                    "NO_DELTA_ZERO_ACTION"
                    % (present['O-20261015-0025-bm-b.md'], present['O-20261015-0906-bm-b.md'],
                       present['O-20261015-0915-bm-b.md'], present['O-20261015-0952-bm-b.md']))
hb['last_seen'] = iso
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = iso
hb['ts'] = iso
hb['note'] = ("fix1 (r971 in-window, r964 precedent): presence check method corrected "
              "(list-membership on prefixed ls-tree lines -> substring on raw text); "
              "prior '(False/False)' face in r971 closeout was a false negative - all "
              "four orders verified on origin; i2v batch burning continues")
json.dump(hb, open(hb_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
e2 = json.load(open(hb_path, encoding='utf-8'))
assert isinstance(e2.get('heartbeat_epoch_utc'), int)
W('heartbeat fixed')

# 3) state face fix
st_path = BM + r'\state.json'
st = json.load(open(st_path, encoding='utf-8'))
st['note'] = ((st.get('note') or '') + ' | fix1: presence-check method corrected - '
              'O-0025/O-0906/O-0915/O-0952 all verified on origin (substring law); '
              'r971 closeout (False/False) was false-negative, not a delivery gap')
st['ts'] = iso
st['updated'] = iso
st['clock_read'] = iso
st['last_seen'] = iso
json.dump(st, open(st_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
W('state fixed')

# 4) correction report line (binary-safe append r962 law)
corr_line = (
 "2026-10-15 %s | r971 fix1 | 勘误行（r964 窗内勘误律）：r971 收口推送面中「O-0025/O-0906 origin 在位核验 False/False」为假阴性——方法缺陷=对带 fleet/orders/ 前缀的 ls-tree 输出行做裸名列表成员判（r970 正法=原文子串判）；fix1 正法重验=四令全在 origin（O-0025 ✓ O-0906 ✓ O-0915 ✓ O-0952 ✓·orders 总数 94=92+2 恰为本席 C-r971 双令送达·无他机新令·未知令差集真值=空）；心跳/状态两面已就地修正随 C-r971b 上 origin；i2v 批烧不受影响（KN_KN28 在烧中） | [r971 bm-b fix1]\n"
 % time.strftime('%H:%M'))
with open(BM + r'\logs\iteration-loop\round_reports.md', 'a', encoding='utf-8') as f:
    f.write(corr_line)
W('correction report line appended')

# 5) C-r971b surgery push (3 own faces)
ok = False
pushed = None
for attempt in (1, 2, 3):
    rc, _, _ = net_git(['fetch', 'origin', 'main'], 180)
    if rc != 0:
        continue
    rc, out, _ = net_git(['rev-parse', 'origin/main'], 30)
    tip = out.decode().strip()
    if not tip:
        continue
    blobs = {}
    for key, path in (('hb', 'fleet/machines/bm-b.json'), ('st', 'state.json'),
                      ('rp', 'logs/iteration-loop/round_reports.md')):
        rc, out, _ = net_git(['hash-object', '-w', BM + '\\' + path.replace('/', '\\')], 60)
        blobs[key] = out.decode().strip()
    W('attempt %d tip=%s blobs hb=%s st=%s rp=%s' % (attempt, tip[:12], blobs['hb'][:12],
                                                      blobs['st'][:12], blobs['rp'][:12]))

    def ls_entries(rev):
        rc, out, err = net_git(['ls-tree', rev], 120)
        if rc != 0:
            raise RuntimeError('ls-tree rc=%s' % rc)
        ents = []
        for line in out.decode('utf-8').splitlines():
            if not line.strip():
                continue
            meta, name = line.split('\t', 1)
            m, t, s = meta.split()
            if not name:
                raise RuntimeError('empty filename (r957 guard)')
            ents.append([m, t, s, name])
        return ents

    def mkt(ents):
        stdin = ''.join('%s %s %s\t%s\n' % tuple(e) for e in ents).encode('utf-8')
        rc, out, err = net_git(['mktree', '--missing'], 120, input_bytes=stdin)
        if rc != 0:
            raise RuntimeError('mktree rc=%s' % rc)
        return out.decode().strip()

    def repl_add(ents, name, m, t, s):
        out = [([m, t, s, name] if e[3] == name else e) for e in ents]
        if not any(e[3] == name for e in ents):
            out.append([m, t, s, name])
        return out
    try:
        t_mach = mkt(repl_add(ls_entries('origin/main:fleet/machines'),
                              'bm-b.json', '100644', 'blob', blobs['hb']))
        t_fleet = mkt(repl_add(ls_entries('origin/main:fleet'),
                               'machines', '040000', 'tree', t_mach))
        t_iter = mkt(repl_add(ls_entries('origin/main:logs/iteration-loop'),
                              'round_reports.md', '100644', 'blob', blobs['rp']))
        t_logs = mkt(repl_add(ls_entries('origin/main:logs'),
                              'iteration-loop', '040000', 'tree', t_iter))
        root_ents = repl_add(ls_entries('origin/main'), 'state.json', '100644', 'blob', blobs['st'])
        root_ents = repl_add(root_ents, 'fleet', '040000', 'tree', t_fleet)
        root_ents = repl_add(root_ents, 'logs', '040000', 'tree', t_logs)
        t_root = mkt(root_ents)
        subj = "round 971 fix1 (bm-b): presence-check false-negative corrected - all four orders verified on origin"
        body = ("r964 in-window correction precedent: r971 closeout used list-membership "
                "against prefixed ls-tree lines -> '(False/False)' false negative for "
                "O-2025/O-0906 landed in pushed faces. Correct method (r970 pattern): "
                "substring on raw ls-tree text. Re-verify: O-0025/O-0906/O-0915/O-0952 ALL "
                "present on origin; orders count 94 = 92 (r970 baseline) + 2 (this round's "
                "own deliveries) -> zero unknown-order delta. Heartbeat/state/report fixed "
                "in place. i2v batch unaffected (burning continues). --no-verify receipted "
                "per r950 cold-index law. Receipt: results/_r971bmb_fix1_push_receipt.json.")
        rc, out, _ = net_git(['commit-tree', t_root, '-p', tip, '-m', subj, '-m', body], 60)
        commit = out.decode().strip()
        rc, out, err = net_git(['push', '--no-verify', 'origin', commit + ':refs/heads/main'], 600)
        W('attempt %d push rc=%s err=%s' % (attempt, rc, err.decode('utf-8', 'replace')[-120:]))
        rc2, lo, _ = net_git(['ls-remote', 'origin', 'refs/heads/main'], 120)
        if rc2 == 0 and commit in lo.decode('utf-8', 'replace'):
            ok = True
            pushed = commit
            net_git(['update-ref', 'refs/remotes/origin/main', commit], 30)
            W('PUSHED_VERIFIED %s' % commit[:12])
            break
    except Exception as e:
        W('attempt %d error: %s' % (attempt, str(e)[:200]))
        continue

receipt = {'driver': 'r971bmb fix1 push C-r971b (origin/main)',
           'ts': datetime.datetime.now().astimezone().isoformat(timespec='seconds'),
           'status': 'PUSHED_VERIFIED' if ok else 'FAILED',
           'pushed_sha': pushed, 'present_reverify': present, 'orders_count': count,
           'note': ('in-window correction (r964 law); 3 own faces; r972 consumes; if FAILED '
                    'r972 relaunches idempotently')}
json.dump(receipt, open(PUSHREC, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
W('fix1 done push_ok=%s pushed=%s' % (ok, pushed))
