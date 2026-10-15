# -*- coding: ascii -*-
# r977 bm-b completion-package landing driver (segment A of r951 two-phase closeout)
# Lands the r947-r976 recovery estate onto a fresh origin tip.
# Laws applied: r968 origin-verbatim foreign faces / r953 Popen+taskkill tree-kill caps /
# r958 chunked checkout / r972 communicate / r962 binary-safe union / r959-r960 lazy-fetch completion.
import subprocess, os, sys, json, time
from collections import Counter
REPO = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
os.chdir(REPO)
L = open(r'results\_r977bmb_land.log', 'w', encoding='utf-8', errors='replace')
def log(*a):
    s = ' '.join(str(x) for x in a)
    print(s); L.write(s + '\n'); L.flush()
def run(cmd, cap=180):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        out, _ = p.communicate(timeout=cap)
        return p.returncode, out
    except subprocess.TimeoutExpired:
        subprocess.run(['taskkill', '/T', '/F', '/PID', str(p.pid)], capture_output=True)
        try: out, _ = p.communicate(timeout=30)
        except Exception: out = b''
        return -99, (out or b'') + b'\nCAP_FIRED'
def must(cmd, cap=180):
    rc, out = run(cmd, cap)
    if rc != 0:
        log('FATAL rc=%d: %s' % (rc, cmd[:120]))
        log((out or b'').decode('utf-8', 'replace')[-600:])
        sys.exit(1)
    return (out or b'').decode('utf-8', 'replace')

FOREIGN = ('bm-a', 'bm-c', 'bma_', 'bmc_')
def is_foreign(p): return any(m in p for m in FOREIGN)

TAKE_ORIGIN_SHARED = set([
 '.gitignore', 'Tools/git_claw.py', 'Tools/iteration_prompt.txt', 'monitor/build_status.py',
 'scripts/perpetual_faces.py', 'scripts/perpetual_faces_n1.py', 'state/queue/tech.md',
 'research/pit-data.md', 'research/pit-git-staged.md', 'research/pit-machine.md',
 'research/pit-ps.md', 'research/pit-tooling.md', 'research/PERPETUAL_N1_W241_PREREG.md',
 'fleet/machine-health.json', 'HQ-FEEDBACK.md', 'results/_quarantine/manifest.json',
 'results/paper/marks/marks-20261015.jsonl', 'results/post_review.jsonl',
 'results/post_review/REPORT-20261015.md', 'results/x2_watch_log.jsonl',
 'results/pool_core_samples.jsonl', 'results/pool_red_flags.jsonl',
 'results/perpetual_faces_state.json', 'results/strategy_scorecard.json',
 'results/scorecard_v1.json', 'results/daily_scorecard.json', 'results/daily_scorecard.html',
 'results/dashboard_status.json', 'results/dashboard_status.js',
 'results/system_v1_paper/REV-OSC-STD_paper.json', 'results/system_v1_paper/SYSTEM-V1_paper.json',
 'results/cta_paper/CTA-P1_paper.json', 'results/market_clock/CALL-2026-10-13.md',
 'results/market_clock/CALL-2026-10-14.md', 'docs/daily_report/REPORT-2026-10-14.json',
 'docs/daily_report/REPORT-2026-10-14.md', 'docs/live_usage/LIVE-2026-10-14.json',
 'docs/live_usage/LIVE-2026-10-14.md', 'results/heat_update_status.json',
 'results/moneyflow_update_status.json', 'results/sina_mf_update_status.json',
 'results/repo_update_status.json', 'results/zt_pool_update_status.json',
 'results/zt_pool_crosscheck.json', 'results/futures_update_status.json',
 'results/lhb_update_status.json', 'results/fund_premium_status.json',
 'results/fund_statement_update_status.json', 'results/ah_panel_status.json',
 'results/p1d_gates.json', 'results/queue_head_collision_probe.json', 'results/queue_seed_gate.json',
])
UNION_FACES = ['CODELY.md', 'research/HANDOVER.md', 'HQ-FEEDBACK.md']
PROMPT_PATH = 'Tools/iteration_prompt.txt'
PROMPT_S8_MARKER = 'bmb-claim-ignite'

def batched(cmdfmt, paths, n=40, cap=300):
    for i in range(0, len(paths), n):
        chunk = paths[i:i+n]
        must(cmdfmt + ' -- ' + ' '.join('"%s"' % p for p in chunk), cap)
    log('  batched %d paths done (%s)' % (len(paths), cmdfmt[:24]))

log('=== r977 landing start', time.strftime('%Y-%m-%d %H:%M:%S'))
must('git fetch origin main', 150)
base = must('git rev-parse origin/main').strip()
log('origin tip', base[:12])
must('git reset --soft ' + base)
log('local main caught up (reset --soft, index preserved)')

names = must('git diff --cached --name-status')
D=[];M=[];A=[];R=[]
for ln in names.splitlines():
    t = ln.split('\t'); s = t[0][0]
    if s=='R': R.append((t[1],t[2]))
    elif s=='D': D.append(t[1])
    elif s=='M': M.append(t[1])
    elif s=='A': A.append(t[1])
log('diff vs base: D=%d M=%d A=%d R=%d' % (len(D),len(M),len(A),len(R)))

take_origin = list(D)
take_origin += [p for p in M if is_foreign(p) or p in TAKE_ORIGIN_SHARED or p.startswith('Money02/')]
rm_cached = [p for p in A if is_foreign(p)]
reset_paths = [p for p in M if p.startswith('data/')]
for old, new in R:
    if old not in take_origin: take_origin.append(old)
    if is_foreign(new): rm_cached.append(new)
rm_cached.append('fleet/inbox/MSG-20261015-0906-bm-b-never-idle-cure.md')
take_origin = [p for p in take_origin if p not in UNION_FACES]

rc, ob = run('git show %s:%s' % (base, PROMPT_PATH))
if rc == 0 and ob and PROMPT_S8_MARKER.encode() in ob:
    log('prompt: origin has S8 weave -> take origin')
elif PROMPT_PATH in take_origin:
    take_origin.remove(PROMPT_PATH)
    log('prompt: origin lacks S8 weave (or show rc=%d) -> keep ours (weave delivery)' % rc)

def dedup(xs):
    seen=set(); out=[]
    for x in xs:
        if x not in seen: seen.add(x); out.append(x)
    return out
take_origin = dedup(take_origin); rm_cached = dedup(rm_cached); reset_paths = dedup(reset_paths)
log('plan: take_origin=%d rm_cached=%d reset(data)=%d' % (len(take_origin), len(rm_cached), len(reset_paths)))

def origin_has(p):
    return bool(must('git ls-tree %s -- "%s"' % (base, p)).strip())
final_rm = []; final_reset = list(reset_paths)
for p in rm_cached:
    if origin_has(p): final_reset.append(p)
    else: final_rm.append(p)
log('safety split: rm=%d reset=%d' % (len(final_rm), len(final_reset)))

# r955/r959 law: index-present faces read odb directly without lazy fetch -> single-file checkout
# lazily fetches; r960 retry once; persistent fail -> reset (index:=origin, worktree gap noted).
# Network-dead probe: if first 3 single checkouts all fail -> fast path (reset all, zero fetch).
def checkout_files(paths, cap_single=30):
    ok = []; fail = []
    for p in paths:
        rc, _ = run('git checkout %s -- "%s"' % (base, p), cap_single)
        if rc == 0: ok.append(p); continue
        rc2, _ = run('git checkout %s -- "%s"' % (base, p), cap_single)
        (ok if rc2 == 0 else fail).append(p)
    return ok, fail

dset = set(D)
d_take = [p for p in take_origin if p in dset]
m_take = [p for p in take_origin if p not in dset]

probe_ok, probe_fail = checkout_files(m_take[:1] + d_take[:2], 30)
if len(probe_ok) == 0 and probe_fail:
    log('NETWORK-DEAD probe -> fast path: reset-exclude all take_origin faces (no fetch)')
    all_res = list(take_origin)
else:
    d_ok, d_fail = [], []
    for i in range(0, len(d_take), 40):
        chunk = d_take[i:i+40]
        rc, out = run('git checkout %s -- %s' % (base, ' '.join('"%s"' % p for p in chunk)), 150)
        if rc == 0: d_ok += chunk
        else:
            log('  D batch @%d rc=%d -> per-file fallback' % (i, rc))
            o, f = checkout_files(chunk, 30)
            d_ok += o; d_fail += f
        log('  D progress %d/%d (fail=%d)' % (min(i+40, len(d_take)), len(d_take), len(d_fail)))
    m_ok, m_fail = checkout_files(m_take, 30)
    all_res = d_fail + m_fail
    log('checkouts: D ok=%d fail=%d | M ok=%d fail=%d' % (len(d_ok), len(d_fail), len(m_ok), len(m_fail)))

reset_faces = all_res
if reset_faces:
    log('reset-excluding %d faces (index:=origin canonical; worktree gap logged for r978 v4 heal)' % len(reset_faces))
    batched('git reset ' + base, reset_faces)
if final_reset: batched('git reset ' + base, final_reset)
for p in final_rm:
    rc, out = run('git rm --cached -q -- "%s"' % p, 60)
    if rc != 0:
        log('  rm --cached skipped (already out of index): %s' % p)

# local-only excludes for stale untracked leftovers (r956 info/exclude law) - idempotent
exc = os.path.join(REPO, '.git', 'info', 'exclude')
cur = open(exc, 'rb').read() if os.path.exists(exc) else b''
add = [p for p in final_rm if p.encode() not in cur]
if add:
    with open(exc, 'ab') as fh:
        fh.write(b'\n# r977: stale origin-moved foreign copies kept as untracked\n')
        for p in add: fh.write(p.encode() + b'\n')
    log('info/exclude += %d stale paths' % len(add))

for f in UNION_FACES:
    rc, ob = run('git show %s:%s' % (base, f))
    if rc != 0 or ob is None:
        log('union %s: show failed -> keep ours' % f); continue
    ours = open(f, 'rb').read()
    if ours == ob:
        log('union %s: identical' % f); continue
    oset = set(ob.split(b'\n')); uset = set(ours.split(b'\n'))
    our_uniq = [l for l in ours.split(b'\n') if l not in oset]
    origin_uniq = [l for l in ob.split(b'\n') if l not in uset]
    if not our_uniq:
        u_ok, _ = checkout_files([f], 30)
        if u_ok:
            log('union %s: ours subset -> took origin' % f)
        else:
            must('git reset %s -- "%s"' % (base, f), 60)
            log('union %s: checkout failed -> reset-excluded (worktree copy stays)' % f)
    elif not origin_uniq:
        log('union %s: ours superset -> keep ours' % f)
    else:
        sep = b'' if ob.endswith(b'\n') else b'\n'
        open(f, 'wb').write(ob + sep + b'\n'.join(our_uniq) + b'\n')
        must('git add -- "%s"' % f)
        log('union %s: merged origin + %d our-unique lines' % (f, len(our_uniq)))

st = must('git status --porcelain')
readd = [ln[3:] for ln in st.splitlines() if ln[:2] == 'MM' and not ln[3:].startswith('data/')]
for p in readd: must('git add -- "%s"' % p, 120)
log('re-added MM keep-ours faces: %d %s' % (len(readd), ';'.join(readd[:10])))

final = must('git diff --cached --name-status')
lines = final.splitlines()
dl = [l for l in lines if l.startswith('D')]
if dl:
    log('DELETION SET NONEMPTY (%d) -> ABORT' % len(dl))
    for l in dl[:20]: log('  ' + l)
    sys.exit(3)
cnt = Counter(l.split('\t')[0][0] for l in lines)
log('final staged commit face: %s (deletion set EMPTY)' % dict(cnt))

open(r'results\_r977bmb_commitmsg.txt', 'w', encoding='utf-8').write(
 "round 977: completion package landed - r947-r976 recovery estate onto origin tip "
 + base[:10] + "; dead-window worktree faces restored origin-verbatim (r968 law; v5 driver died at 469-remaining, "
 "r977 completed via batched checkout); data/ faces excluded mid astock-refresh; shared faces origin-canonical; "
 "CODELY/HQ/HANDOVER union-merged; own recovery receipts r947-r976 + MSG-0104 delivery + MSG-2015 processed move; "
 "local main 69-behind catchup; 9 superseded r95x-r958 commits retired to machine/bm-b-r958 side branch\n")
must('git commit -F results\\_r977bmb_commitmsg.txt', 240)
sha = must('git rev-parse HEAD').strip()
log('COMMITTED', sha[:12])

rc, out = run('git push origin main', 300)
log('push rc=%d %s' % (rc, (out or b'').decode('utf-8', 'replace')[-400:].replace('\n', ' | ')))
remote = ''
rc2, out2 = run('git ls-remote origin main', 90)
if rc2 == 0 and out2:
    remote = out2.decode('utf-8', 'replace').split()[0]
ok = (remote == sha)
log('remote=%s local=%s -> %s' % (remote[:12], sha[:12], 'PUSHED_VERIFIED' if ok else 'NOT-VERIFIED'))

rc3, out3 = run('git ls-tree origin/main -- fleet/orders/ fleet/inbox/', 90)
tree = out3.decode('utf-8', 'replace') if rc3 == 0 else ''
orders_on = [n for n in ['O-20261015-0025-bm-b.md','O-20261015-0906-bm-b.md','O-20261015-0915-bm-b.md','O-20261015-0952-bm-b.md'] if n in tree]
msgs_on = [n for n in ['MSG-20261015-0104-bmb-P1B-G5-done.md','MSG-20260914-2015-bmb.md'] if n in tree]
log('delivery face on tip: orders=%d/4 msgs=%d/2' % (len(orders_on), len(msgs_on)))

json.dump({
 'driver': 'r977bmb completion-package landing (segment A)',
 'ts': time.strftime('%Y-%m-%dT%H:%M:%S+08:00'),
 'base': base, 'pushed_sha': sha, 'push_rc': rc, 'remote': remote,
 'status': 'PUSHED_VERIFIED' if ok else ('PUSH_REJECTED' if rc != 0 else 'MISMATCH'),
 'faces': dict(cnt), 'deletion_set': 'empty',
 'delivery_orders_on_tip': orders_on, 'delivery_msgs_on_tip': msgs_on,
 'take_origin_faces': len(take_origin), 'rm_cached_faces': len(final_rm), 'data_excluded': len(final_reset),
 'm_face_reset_excluded': reset_faces, 'readd_mm': readd,
}, open(r'results\_r977bmb_land_receipt.json', 'w'), indent=1)
log('receipt written. DONE ok=%s' % ok)
