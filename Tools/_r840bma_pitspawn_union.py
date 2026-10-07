# r840 pit-spawn UU union fix: bm-c full file (:2:) + my single E1 entry (correct union)
import subprocess, re

def blob(s):
    r = subprocess.run(['git', 'show', s], capture_output=True)
    return r.stdout.decode('utf-8', errors='replace')

base = blob(':2:research/pit-spawn.md')
src = open('Tools/_r840bma_pit_directwrite.py', encoding='utf-8').read()
m = re.search(r'E1 = """(.*?)"""', src, re.S)
e1 = m.group(1)
if not base.endswith('\n'):
    base += '\n'
merged = base + e1
if not merged.endswith('\n'):
    merged += '\n'
open('research/pit-spawn.md', 'w', encoding='utf-8', newline='\n').write(merged)
n_mine = merged.count('- [2026-10-07 20:1x r840 bm-a]')
n_bmc = merged.count('r700 bm-c] **O-20261008-1300')
print('merged chars:', len(merged), '| my-entry-count:', n_mine, '| bmc-entry-count:', n_bmc)
assert n_mine == 1 and n_bmc == 1, 'union duplication check FAILED'
print('UNION-OK: each entry exactly once')
