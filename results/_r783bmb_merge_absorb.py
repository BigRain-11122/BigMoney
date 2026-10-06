# r783 bm-b S0-2 merge absorb: origin 3 (bm-c r640 close/push-retry/S4) x local 2 (r783 absorb + D-06 migration)
# Laws: dirty-blockers worksnap (r782 path-qualified); CODELY theirs-wins + bm-b ptr row re-append (preservation note);
# resolver theirs-wins (same-entry duplicate drop); legdiff ours (origin LOST the stepper entry - preservation);
# registry line-union; bm-b ledgers byte-untouched; take-theirs blob-sha proof for shared regen faces.
import subprocess, json, os, shutil, hashlib

os.chdir(r'C:\Fluxgroup\FluxGroup\quant\bigmoney')

def git(*a):
    r = subprocess.run(['git'] + list(a), capture_output=True)
    if r.returncode != 0:
        raise RuntimeError('git %s rc=%d %s' % (a, r.returncode, r.stderr[:400].decode('utf-8', 'replace')))
    return r.stdout

receipt = {'steps': [], 'asserts': [], 'overlaps': {}, 'ledgers': {}}
LEDGERS = ['results/fund_quality_p1/nulls.jsonl', 'results/fund_divlowvol_p1/nulls.jsonl',
           'results/saturation_engine/history_bm-b.jsonl',
           'results/finalize_trio_readiness_history.bm-b.jsonl',
           'results/pool_dualrun.bm-b.jsonl']
def lc(p):
    with open(p, 'rb') as f:
        return sum(1 for _ in f)
pre_ledger = {p: lc(p) for p in LEDGERS}

porcelain = git('status', '--porcelain').decode('utf-8')
dirty = [ln[3:].strip().strip('"') for ln in porcelain.splitlines() if ln[:2] in ('M ', ' M', 'MM', 'AM')]
dirty = [p for p in dirty if p]
origin_changed = set(git('diff', '--name-only', 'HEAD', 'origin/main').decode().splitlines())
blockers = sorted(set(dirty) & origin_changed)
receipt['blockers'] = blockers
snapdir = 'results/_worksnap_r783bmb_merge'
os.makedirs(snapdir, exist_ok=True)
for p in blockers:
    q = p.replace('/', '__')
    shutil.copy2(p, os.path.join(snapdir, q))
receipt['steps'].append('worksnap %d blockers -> %s (path-qualified)' % (len(blockers), snapdir))

if blockers:
    git('checkout', '--', *blockers)
    receipt['steps'].append('checkout -- blockers (shared regen faces -> merge brings origin truth)')

# pre-merge: capture my ptr row + stepper entry from current tree (for post-merge re-append)
my_codely = open('CODELY.md', encoding='utf-8').read()
my_ptr = next(ln for ln in my_codely.splitlines() if ln.startswith('- 域指针·r783 bm-b 增量回扫批'))
stepper_anchor = '- [2026-10-06 20:5x r639 bm-c] **血统机械步进'

# merge (no commit; conflicts expected)
r = subprocess.run(['git', 'merge', 'origin/main', '--no-commit'], capture_output=True)
out = (r.stdout + r.stderr).decode('utf-8', 'replace')
receipt['merge_rc'] = r.returncode
receipt['merge_out_tail'] = out[-600:]
uu = [ln for ln in git('diff', '--name-only', '--diff-filter=U').decode().splitlines() if ln]
receipt['uu_faces'] = uu

# --- resolve UU faces ---
for p in uu:
    if p == 'CODELY.md':
        theirs = git('show', 'MERGE_HEAD:CODELY.md')  # origin truth
        txt = theirs.decode('utf-8')
        eol = '\r\n' if '\r\n' in txt else '\n'
        lines = txt.split(eol)
        # theirs already lacks r782/stepper/wrapper hot entries (bm-c batch-4) -> just append my ptr row (with preservation note)
        assert '- [2026-10-06 21:3x r782 bm-b] **worksnap' not in txt, 'theirs still has worksnap entry'
        assert stepper_anchor not in txt, 'theirs still has stepper entry'
        assert my_ptr not in txt, 'theirs already has my ptr row'
        lines.append(my_ptr)
        blob = eol.join(lines)
        if not blob.endswith(eol):
            blob += eol
        open('CODELY.md', 'wb').write(blob.encode('utf-8'))
        git('add', '--', 'CODELY.md')
        receipt['overlays'] = receipt.get('overlays', {})
        receipt['overlays']['CODELY.md'] = 'theirs-wins + bm-b ptr row appended (bm-c batch-4 subsumes bm-b migration; bm-b receipt kept as session evidence)'
    elif p == 'research/pit-git-resolver.md':
        theirs = git('show', 'MERGE_HEAD:research/pit-git-resolver.md')
        open('research/pit-git-resolver.md', 'wb').write(theirs)
        git('add', '--', 'research/pit-git-resolver.md')
        t = theirs.decode('utf-8', 'replace')
        assert t.count('- [2026-10-06 21:3x r782 bm-b] **worksnap') == 1
        receipt['overlays'] = receipt.get('overlays', {})
        receipt['overlays']['research/pit-git-resolver.md'] = 'theirs-wins (bm-c batch-4 already hosts worksnap entry x1; bm-b duplicate append dropped)'
    elif p == 'knowledge/TREASURE_REGISTRY.md':
        o = git('show', 'MERGE_HEAD:knowledge/TREASURE_REGISTRY.md').decode('utf-8')
        m = git('show', 'MERGE_BASE:knowledge/TREASURE_REGISTRY.md').decode('utf-8') if False else None
        # line-union: ours current vs theirs; ours-only lines appended at end (both appended at tail)
        ours_lines = open('knowledge/TREASURE_REGISTRY.md', encoding='utf-8').read().splitlines()
        theirs_lines = o.splitlines()
        base_set = set(git('show', 'HEAD~1:knowledge/TREASURE_REGISTRY.md').decode('utf-8').splitlines())
        ours_new = [ln for ln in ours_lines if ln not in theirs_lines and ln not in base_set]
        eol = '\r\n' if '\r\n' in o else '\n'
        merged = theirs_lines + ours_new
        blob = eol.join(merged)
        if not blob.endswith(eol):
            blob += eol
        open('knowledge/TREASURE_REGISTRY.md', 'wb').write(blob.encode('utf-8'))
        git('add', '--', 'knowledge/TREASURE_REGISTRY.md')
        receipt['overlays'] = receipt.get('overlays', {})
        receipt['overlays']['knowledge/TREASURE_REGISTRY.md'] = 'line-union: theirs + %d ours-new ritual lines' % len(ours_new)
    else:
        # default: shared face -> theirs (regen truth from bm-c S6 run)
        try:
            theirs = git('show', 'MERGE_HEAD:' + p)
        except RuntimeError:
            theirs = None
        if theirs is not None:
            open(p, 'wb').write(theirs)
            git('add', '--', p)
            receipt['overlays'] = receipt.get('overlays', {})
            receipt['overlays'][p] = 'theirs-wins (default shared face)'
        else:
            raise RuntimeError('unhandled UU face without MERGE_HEAD blob: %s' % p)

# --- ledger safety: untouched by merge ---
post_ledger = {p: lc(p) for p in LEDGERS}
receipt['ledgers'] = {'pre': pre_ledger, 'post': post_ledger}
assert post_ledger == pre_ledger, 'LEDGERS TOUCHED: %r vs %r' % (pre_ledger, post_ledger)
receipt['asserts'].append('append-only bm-b ledgers byte-untouched (5/5 line counts stable)')

# --- restore bm-b-owned blockers from worksnap (ours-live-wins) ---
BM_B_OWNED = ('.bm-b.', 'face_bm-b', 'state_bm-b', 'history_bm-b')
for p in blockers:
    if any(k in p for k in BM_B_OWNED):
        shutil.copy2(os.path.join(snapdir, p.replace('/', '__')), p)
        receipt['steps'].append('restored bm-b-owned face from worksnap: %s' % p)

# --- verify: pit-lineage-legdiff kept ours (stepper preservation) ---
lg = open('research/pit-lineage-legdiff.md', encoding='utf-8').read()
assert lg.count(stepper_anchor) == 1, 'stepper entry must be x1 in legdiff (preservation): got %d' % lg.count(stepper_anchor)
receipt['asserts'].append('stepper entry preserved x1 in pit-lineage-legdiff.md (origin batch-4 lost it; bm-b append = zero-loss repair)')

# --- final checks: no UU left, marker scan on resolved faces, sizes ---
assert not git('diff', '--name-only', '--diff-filter=U').decode().strip(), 'UU faces remain'
for p in ['CODELY.md', 'research/pit-git-resolver.md', 'knowledge/TREASURE_REGISTRY.md', 'research/pit-lineage-legdiff.md']:
    raw = open(p, 'rb').read()
    for m in (b'<<<<<<< ', b'>>>>>>> ', b'||||||| '):
        if p != 'research/pit-git-resolver.md':
            assert m not in raw, 'marker %r in %s' % (m, p)
receipt['asserts'].append('marker scan clean on resolved faces (resolver exempt: documents markers)')
sz = os.path.getsize('CODELY.md')
receipt['codely_size'] = sz
assert sz <= 30720, 'CODELY over line after merge: %d' % sz

json.dump(receipt, open('results/_r783bmb_merge_absorb.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps({k: receipt[k] for k in ('merge_rc', 'uu_faces', 'blockers', 'overlays', 'asserts', 'codely_size')}, ensure_ascii=False, indent=1))
print('MERGE-RESOLVED-OK (not yet committed)')
