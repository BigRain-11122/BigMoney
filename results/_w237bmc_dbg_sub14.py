# -*- coding: utf-8 -*-
"""Diagnose SUB#14 anchor mismatch: script literal vs template bytes."""
tpl = open(r'C:\Users\Dasheng\.codely-cli\tmp\w236_frozen_tpl.md', encoding='utf-8').read()
src = open('results/_w237bmc_prereg_derive.py', encoding='utf-8').read()

# Execute the SUBS block definitions only (up to the apply section) in a sandbox.
cut = src.find('# ---------- apply ----------')
head = src[:cut]
ns = {}
# stub out the heavy facts section: exec only the SUBS part
i0 = head.find('SUBS = []')
body = head[i0:]
# provide the names referenced in f-strings / asserts
ns = {'ram_free_gb': 0.9, 'mu_s': '-0.09280926', 'wmu_s': '-0.09685532',
      'sigma_s': '0.24508878', 'delta_s': '0.0040', 'a_p95': 0.3139}
exec(body, ns)
SUBS = ns['SUBS']
print('pairs:', len(SUBS))
old14, new14 = SUBS[13]
i = tpl.find(old14)
print('SUB#14 old found in template at:', i)
if i < 0:
    # locate approximate span and byte-diff
    j = tpl.find('_w236bma_freeze_edits')
    seg = tpl[j - 250:j + 350]
    print('template seg repr:')
    print(repr(seg))
    print('SUB#14 old repr:')
    print(repr(old14))
else:
    print('MATCH — apply-side count bug instead')
