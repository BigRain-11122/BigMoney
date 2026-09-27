import subprocess

c = open('CODELY.md', 'rb').read()
print('current CODELY size:', len(c))
o = subprocess.run(['git', 'show', 'origin/main:CODELY.md'], capture_output=True).stdout
print('origin(main@5c5dab93) CODELY size:', len(o))
ct = c.decode('utf-8')
ot = o.decode('utf-8', errors='replace')
ce = [l for l in ct.splitlines() if l.strip().startswith('- [')]
oe = [l for l in ot.splitlines() if l.strip().startswith('- [')]
print('current entries:', len(ce), '| origin entries:', len(oe))
cset = {l.strip()[:55] for l in ce}
oset = {l.strip()[:55] for l in oe}
print('== origin-only (first 55 chars):')
for x in sorted(oset - cset):
    print('  O:', x)
print('== current-only:')
for x in sorted(cset - oset):
    print('  C:', x)
# look for the r332-bmb neighborhood
i = ct.find('r332 bm-b')
print('== r332bm-b region:')
print(ct[max(0, i - 200):i + 500])
