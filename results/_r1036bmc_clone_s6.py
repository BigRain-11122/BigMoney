# -*- coding: utf-8 -*-
import io

src = io.open('Tools/_r1035bmc_s6.py', encoding='utf-8').read()
t = src.replace('r1035 bm-c S6 chain driver', 'r1036 bm-c S6 chain driver')
t = t.replace('_r1035bmc_s6_log.txt', '_r1036bmc_s6_log.txt')
i0 = t.find('"""') + 3
i1 = t.find('"""', 4)
old_doc = t[i0:i1]
new_doc = ('r1036 bm-c S6 chain driver (canon clone of r1035): standing-leg canon clone '
           '(r838 canon lineage; r871/r936/r1035 canon clone -- identical leg list, leg '
           'count derived at runtime honest count). Full log to '
           'results/_r1036bmc_s6_log.txt. MUST run under the SYSTEM python (Python313): '
           'embedded ComfyUI python has no pandas/akshare (r516 lesson). Every leg '
           'subprocess passes CREATE_NO_WINDOW (U060 silence law). Thursday 21:5x run -- '
           'bars 10-15 landed (r1035 window consumed papers full chain 20:49-20:59); '
           'this window = post-landing idempotent re-derive/no-op sweep; bm-a/bm-b-owned '
           'lanes honest no-op on this machine per R31 lane guards.')
t = t.replace(old_doc, new_doc, 1)
io.open('Tools/_r1036bmc_s6.py', 'w', encoding='utf-8', newline='').write(t)
print('driver written', len(t))
