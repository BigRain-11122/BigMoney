import subprocess

def show(stage, path):
    return subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True).stdout.decode('utf-8', errors='replace')

o = show(2, 'CODELY.md')   # origin side (bm-c r90)
m = show(3, 'CODELY.md')   # my side (r338)
cur = open('CODELY.md', encoding='utf-8').read()

def entries(t):
    return {l.strip() for l in t.splitlines() if l.strip().startswith('- [')}

eo, em, ec = entries(o), entries(m), entries(cur)
print('origin entries:', len(eo), '| mine entries:', len(em), '| current:', len(ec))
print('== origin entries missing from current (TRUE LOSS CHECK):')
lost = eo - ec
for x in sorted(lost):
    print('  LOST:', x[:150])
print('== mine entries missing from current:')
lostm = em - ec
for x in sorted(lostm):
    print('  LOST-MINE:', x[:150])
print('== current-only (added vs both sides):')
for x in sorted(ec - eo - em):
    print('  NEW:', x[:100])
