# -*- coding: utf-8 -*-
import io, re

out = io.open(r'results/_r980bma_dbg_out.md', encoding='utf-8').read()

for probe in ['投影 B 落投影 A 窗内', '注册后将', 'ide-naive-A re-derive',
              'W237 B 带 538_204..538_403', 'W238 B 带 540_404..540_603']:
    print('=== probe: %s  hits=%d' % (probe, out.count(probe)))
    for m in re.finditer(re.escape(probe), out):
        s = m.start()
        print('   @%d: %s' % (s, out[max(0, s - 55):s + 75].replace('\n', ' ')))
    print()

# template comparison for the same probes
import subprocess
GIT = r'C:\Program Files\Git\cmd\git.exe'
tpl = subprocess.run([GIT, 'show', 'd311a5439:research/PERPETUAL_N1_W237_PREREG.md'],
                     capture_output=True).stdout.decode('utf-8')
print('##### template side #####')
for probe in ['投影 B 落投影 A 窗内', '注册后将']:
    print('=== probe: %s  hits=%d' % (probe, tpl.count(probe)))
    for m in re.finditer(re.escape(probe), tpl):
        s = m.start()
        print('   @%d: %s' % (s, tpl[max(0, s - 55):s + 75].replace('\n', ' ')))
