# -*- coding: utf-8 -*-
import subprocess
out = subprocess.run(['schtasks', '/query', '/fo', 'csv'],
                     capture_output=True).stdout.decode('gbk', errors='replace')
names = []
for line in out.splitlines():
    if 'Bigmoney' in line or 'HQ-' in line:
        names.append(line.split(',')[0].strip('"'))
print('\n'.join(names))
