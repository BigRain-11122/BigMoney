# r588 helper 2: extract W109 canon row (encoding-safe)
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
law = open('research/PERPETUAL_FACES.md', encoding='utf-8').read()
m = law.find('- N1 \u6ce2109\uff08')
if m < 0:
    m = law.find('- N1 \u6ce2109')
mend = law.find('\n', m)
row = law[m:mend]
open('results/_r588bma_w109_canon_ref.txt', 'w', encoding='utf-8', newline='\n').write(row)
print('canon row chars:', len(row))
print(row[:400])
print('...')
print(row[-260:])
print('== next line ==')
print(law[mend:mend+100])
