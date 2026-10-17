# -*- coding: utf-8 -*-
import io
t = io.open('results/_w264bmc_freeze_edits.py', encoding='utf-8', newline='').read()
for i, ln in enumerate(t.split('\n')):
    if any(x in ln for x in ['fifty-one legs', 'thirty-three legs', 'eighteen legs',
                             'range(211, 262)', 'legs 51', 'legs 52', 'sixty-nine',
                             'W211..W261', 'W211..W243', 'W244..W261',
                             'range(138, 207)', 'range(244,', 'range(245,',
                             '69 estate', 'full parity span', 'estate segment']):
        print(f'L{i+1}| {ln.strip()[:200]}')
