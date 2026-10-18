# r1084-continuation bm-c: byte-identity extractor from group-tree origin/main (raw-bytes law, zero tree touch)
import subprocess

REPO = 'K:/Fluxgroup/FluxGroup'
OUT = 'K:/Fluxgroup/FluxGroup/quant/bigmoney/results/'


def run(*a):
    return subprocess.run(list(a), capture_output=True)


targets = [
    ('cph4/research/R-20261018-memory-control-01.md', '_r1084bmc_memctl_rdoc_v2.md'),
    ('Tools/memory-budget-gate.py', '_r1084bmc_gate_v2.py'),
    ('cph4/fleet/memory-slim/LEDGER.md', '_r1084bmc_ledger_origin.md'),
]

allok = True
for src, dst in targets:
    b = run('git', '-C', REPO, 'show', 'origin/main:' + src).stdout
    p = OUT + dst
    with open(p, 'wb') as f:
        f.write(b)
    want = run('git', '-C', REPO, 'rev-parse', 'origin/main:' + src).stdout.decode().strip()
    got = run('git', '-C', REPO, 'hash-object', '--no-filters', p).stdout.decode().strip()
    ok = (want == got)
    allok = allok and ok
    print(dst, 'bytes=', len(b), 'IDENTITY' if ok else 'MISMATCH want=%s got=%s' % (want, got))

lines = run('git', '-C', REPO, 'show', 'origin/main:docs/orders.md').stdout.decode('utf-8', 'replace').splitlines()
with open(OUT + '_r1084bmc_ordtail2.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines[-10:]))
print('orders total lines=', len(lines), 'tail10 written')

# origin skills listing vs local working tree (agent-library install delta face)
ls_o = run('git', '-C', REPO, 'ls-tree', '--name-only', 'origin/main', 'cph4/skills/').stdout.decode()
print('origin cph4/skills entries:', ls_o.strip().replace('\n', ' | '))
print('ALL-IDENTITY' if allok else 'HAS-MISMATCH')
