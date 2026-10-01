"""r534 CODELY union: extract my r534 entry from a7591e630, append to origin's current version (r315 entry-extraction law)."""
import subprocess

def git(*args):
    return subprocess.run(['git'] + list(args), capture_output=True, text=True, encoding='utf-8', errors='replace').stdout

mine = git('show', 'a7591e630:CODELY.md').splitlines()
cur_lines = open(r'CODELY.md', encoding='utf-8').read().splitlines()
cur_set = set(cur_lines)

# extract my unique lines (in a7591e630 but not in current origin version)
new_entries = [l for l in mine if l not in cur_set and l.strip().startswith('- [2026-10-01 20:0x r534 bm-a]')]
print('my unique r534 entries found:', len(new_entries))
assert len(new_entries) == 1, f'expected exactly 1, got {len(new_entries)}'
entry = new_entries[0]
print('entry preview:', entry[:80])

# EOF append (de-facto convention) + dedupe assertion fail-closed
assert entry not in cur_set, 'dedupe: entry already present, abort'
with open(r'CODELY.md', 'a', encoding='utf-8') as f:
    f.write('\n' + entry + '\n')

final = open(r'CODELY.md', encoding='utf-8').read()
assert final.count('r534 bm-a] finalize') == 1, 'dedupe post-check failed'
print('union done: local CODELY now carries r534 entry on top of origin version')
