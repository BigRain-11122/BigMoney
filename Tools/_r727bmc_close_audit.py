import sys
import io
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
t = open('Tools/_r727bmc_close.py', encoding='utf-8').read()
bad46 = [t[max(0, m.start() - 30):m.start() + 10]
         for m in re.finditer('46', t)
         if 'r464' not in t[max(0, m.start() - 4):m.start() + 6]
         and 'R464' not in t[max(0, m.start() - 4):m.start() + 6]]
print('46 residue (excl r464/R464):', len(bad46), bad46)
print('streak 47 / "47. fragments:', t.count('streak 47'), t.count('"47\u00b7'))
print('verdict block after nxt:', t.find('verdict = verdict.replace') > t.find('nxt = ('))
print('round_no 728:', t.count('728'))
