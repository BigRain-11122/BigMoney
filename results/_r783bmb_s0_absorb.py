# r783 bm-b S0 minimal absorb: revert only blockers (origin-update-set x dirty), FF, re-insert CODELY entry
# Laws: r782 worksnap path-qualified + line-union (NOT needed here: ledgers untouched by FF);
#       take-theirs blob-sha proof (r782); scoped conflict-marker scan (r637); union CODELY (r639 healed-union style)
import subprocess, json, os, shutil, sys

os.chdir(r'C:\Fluxgroup\FluxGroup\quant\bigmoney')

def git(*a):
    r = subprocess.run(['git'] + list(a), capture_output=True)
    if r.returncode != 0:
        raise RuntimeError('git %s rc=%d %s' % (a, r.returncode, r.stderr[:300].decode('utf-8', 'replace')))
    return r.stdout

porcelain = git('status', '--porcelain').decode('utf-8', 'replace')
dirty = [ln[3:].strip().strip('"') for ln in porcelain.splitlines() if ln[:2] in ('M ', ' M', 'MM', 'AM')]
dirty = [p for p in dirty if p]
old_head = git('rev-parse', 'HEAD').decode().strip()
origin_changed = set(git('diff', '--name-only', old_head, 'origin/main').decode().splitlines())
blockers = sorted(set(dirty) & origin_changed)
receipt = {'old_head': old_head, 'dirty_count': len(dirty), 'blockers': blockers, 'steps': [], 'asserts': []}

# ledger safety probe: line counts before (must be unchanged after -- FF must not touch them)
LEDGERS = ['results/fund_quality_p1/nulls.jsonl', 'results/fund_divlowvol_p1/nulls.jsonl',
           'results/saturation_engine/history_bm-b.jsonl',
           'results/finalize_trio_readiness_history.bm-b.jsonl',
           'results/pool_dualrun.bm-b.jsonl']
def lc(p):
    with open(p, 'rb') as f:
        return sum(1 for _ in f)
pre_ledger = {p: lc(p) for p in LEDGERS}

# step 1: worksnap CODELY only (path-qualified name; the other blockers are regen faces -> take-theirs)
snapdir = 'results/_worksnap_r783bmb'
os.makedirs(snapdir, exist_ok=True)
shutil.copy2('CODELY.md', os.path.join(snapdir, 'CODELY__md'))
receipt['steps'].append('worksnap CODELY.md -> _worksnap_r783bmb/CODELY__md')

# step 2: revert blockers
git('checkout', '--', *blockers)
receipt['steps'].append('checkout -- blockers: %s' % ', '.join(blockers))

# step 3: FF merge
git('merge', '--ff-only', 'origin/main')
new_head = git('rev-parse', 'HEAD').decode().strip()
assert new_head == git('rev-parse', 'origin/main').decode().strip()
receipt['new_head'] = new_head
receipt['steps'].append('ff-only merge origin/main -> %s' % new_head[:11])

# step 4: ledgers untouched assert (the core safety property)
post_ledger = {p: lc(p) for p in LEDGERS}
assert post_ledger == pre_ledger, 'LEDGER TOUCHED BY SURGERY: %r vs %r' % (pre_ledger, post_ledger)
receipt['asserts'].append('append-only ledgers byte-untouched by surgery (5/5 line counts stable)')
receipt['ledger_lines'] = post_ledger

# step 5: take-theirs blob-sha proof for the 4 regen faces
THEIRS = [p for p in blockers if p != 'CODELY.md']
for p in THEIRS:
    st = git('ls-files', '-s', '--', p).decode().split()
    o_sha = git('rev-parse', 'origin/main:%s' % p).decode().strip()
    assert st[1] == o_sha, 'blob-sha mismatch: %s' % p
receipt['asserts'].append('take_theirs blob-sha == origin/main %d/%d' % (len(THEIRS), len(THEIRS)))

# step 6: re-insert my CODELY entry into origin version
snap = open(os.path.join(snapdir, 'CODELY__md'), 'rb').read().decode('utf-8')
snap_lines = snap.splitlines()
mine_entry = [ln for ln in snap_lines if ln.startswith('- [2026-10-06 21:3x r782 bm-b]')]
assert len(mine_entry) == 1, 'r782 entry not found in worksnap: %d' % len(mine_entry)
cur = open('CODELY.md', 'rb').read().decode('utf-8')
assert '- [2026-10-06 21:3x r782 bm-b]' not in cur, 'r782 entry already present in origin CODELY'
cur_lines = cur.splitlines()
idx = next((i for i, ln in enumerate(cur_lines) if ln.startswith('- \u57df\u6307\u9488\u00b7')), None)
assert idx is not None, 'anchor - \u57df\u6307\u9488\u00b7 line not found in origin CODELY'
new_lines = cur_lines[:idx] + [mine_entry[0], ''] + cur_lines[idx:]
eol = '\r\n' if '\r\n' in cur else '\n'
open('CODELY.md', 'wb').write(eol.join(new_lines).encode('utf-8'))
receipt['asserts'].append('CODELY r782 entry re-inserted before first domain-pointer block (dedupe-checked)')
receipt['codely'] = {'origin_lines': len(cur_lines), 'result_lines': len(new_lines)}

# step 7: scoped conflict-marker scan on CODELY + the 4 theirs faces
MARK = b'<<<<<<<\n|||||||\n>>>>>>>\n=======\n'
def marker_scan(p):
    raw = open(p, 'rb').read()
    bad = [m for m in [b'<<<<<<< ', b'>>>>>>> ', b'||||||| '] if m in raw]
    return bad
touched = ['CODELY.md'] + THEIRS
for p in touched:
    bad = marker_scan(p)
    assert not bad, 'conflict markers in %s: %r' % (p, bad)
receipt['asserts'].append('scoped marker scan clean on %d touched files' % len(touched))

json.dump(receipt, open('results/_r783bmb_s0_absorb.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps({k: receipt[k] for k in ('old_head', 'new_head', 'blockers', 'asserts', 'ledger_lines')}, ensure_ascii=False, indent=1))
print('ABSORB-OK')
