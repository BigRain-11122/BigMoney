# -*- coding: utf-8 -*-
# r943 bm-c: clone _r936bmc_s6.py -> _r943bmc_s6.py (standing-leg canon clone, r837/r871/r936 lineage)
import ast

src = open('Tools/_r936bmc_s6.py', encoding='utf-8').read()
new = src.replace('_r936bmc_s6_log', '_r943bmc_s6_log').replace('r936 bm-c S6', 'r943 bm-c S6')
old_doc = '"""r943 bm-c S6 chain driver: standing-leg canon clone (r838 canon lineage; r871 canon clone -- identical leg list, leg count derived at runtime honest count). Full log to results/_r943bmc_s6_log.txt.'
assert old_doc in new, 'doc anchor drift'
new = new.replace(
    old_doc,
    '"""r943 bm-c S6 chain driver: standing-leg canon clone (r838 canon lineage; r871/r936 canon clone -- identical leg list, leg count derived at runtime honest count). Full log to results/_r943bmc_s6_log.txt.')
old_note = ('Monday 18:2x run -- new Monday bars expected on update_daily (r933 verdict: '
            'Monday bars pending); papers chain on bar landing; W224 prereg landed this window, '
            'engine DRY (queue_next empty at derive time); bm-a/bm-b-owned lanes honest no-op '
            'on this machine per R31 lane guards.')
new_note = ('Monday 22:4x run -- Monday 10-12 bars already landed r940 (update_daily cutoff '
            '10-12); W226 five-face freeze landed THIS window + engine ignition live '
            '(burns_active w226 x3); papers chain on any new bar; bm-a/bm-b-owned lanes '
            'honest no-op on this machine per R31 lane guards.')
assert old_note in new, 'window note anchor drift'
new = new.replace(old_note, new_note)
ast.parse(new)
open('Tools/_r943bmc_s6.py', 'w', encoding='utf-8', newline='').write(new)
print('clone OK ->', len(new.splitlines()), 'lines; ast parse OK')
