import subprocess

def show(ref, path):
    r = subprocess.run(['git', 'show', f'{ref}:{path}'], capture_output=True)
    assert r.returncode == 0, f'show {ref} failed'
    return r.stdout.decode('utf-8', errors='replace')

o = show('5c5dab93', 'CODELY.md')
m = show('0cf7c5eb', 'CODELY.md')
cur = open('CODELY.md', encoding='utf-8').read()

def entries(t):
    return {l.strip() for l in t.splitlines() if l.strip().startswith('- [')}

eo, em, ec = entries(o), entries(m), entries(cur)
print('origin(5c5dab93):', len(eo), 'entries | mine(0cf7c5eb):', len(em), '| current: %d' % len(ec))

lost_o = eo - ec
lost_m = em - ec
print('== origin entries missing from current:', len(lost_o))
for x in sorted(lost_o):
    print('  LOST-O:', x[:160])
print('== mine entries missing from current:', len(lost_m))
for x in sorted(lost_m):
    print('  LOST-M:', x[:160])
print('== archive zero-loss backstop for any lost full:')
arch = open('research/memory-archive/202609.md', encoding='utf-8', errors='replace').read()
for x in list(lost_o) + list(lost_m):
    # each lost entry: does a distinctive fragment exist in archive?
    frag = x[60:120]
    print('  frag-in-archive [%s...]: %s' % (frag[:30], frag in arch))
