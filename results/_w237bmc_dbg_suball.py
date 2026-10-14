# -*- coding: utf-8 -*-
"""Diagnose ALL SUB anchor mismatches: print repr of every old that count=0 in template."""
tpl = open(r'C:\Users\Dasheng\.codely-cli\tmp\w236_frozen_tpl.md', encoding='utf-8').read()
src = open('results/_w237bmc_prereg_derive.py', encoding='utf-8').read()
cut = src.find('# ---------- apply ----------')
body = src[src.find('SUBS = []'):cut]
ns = {'ram_free_gb': 0.9, 'mu_s': '-0.09280926', 'wmu_s': '-0.09685532',
      'sigma_s': '0.24508878', 'delta_s': '0.0040', 'a_p95': 0.3139}
exec(body, ns)
SUBS = ns['SUBS']
out = tpl
for i, (old, new) in enumerate(SUBS, 1):
    n = out.count(old)
    if n != 1:
        print('== SUB#%d count=%d' % (i, n))
        if n == 0:
            # find longest common prefix to locate divergence
            best = 0
            for L in range(min(len(old), 40), 10, -1):
                j = tpl.find(old[:L])
                if j >= 0:
                    best = L
                    break
            print('   old diverges after prefix-len', best)
            if best:
                j = tpl.find(old[:best])
                print('   template:', repr(tpl[j:j + min(len(old) - best + 20, 160)]))
                print('   old     :', repr(old[best:best + 160]))
    else:
        out = out.replace(old, new)
print('--- diagnostic apply done (mutations discarded)')
