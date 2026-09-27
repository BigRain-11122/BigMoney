# -*- coding: utf-8 -*-
"""r83 bm-c dashboard pair fix: .json must be same-side as .js (R209/R148 pair law).
resolve3 ts_hint bug gave both sides an equal hint -> .json took mine while .js took
origin (newer meta.generated_at 13:35:37). Fix: take origin .json whole bytes and
assert js/json generated_at pair equality.
"""
import json, re, subprocess

def blob(rev, p):
    return subprocess.run(['git', 'show', '%s:%s' % (rev, p)],
                          capture_output=True, check=True).stdout

b2 = blob(':2', 'results/dashboard_status.json')
d2 = json.loads(b2.decode('utf-8-sig'))
g2 = d2['meta']['generated_at']
d3 = json.loads(blob(':3', 'results/dashboard_status.json').decode('utf-8-sig'))
g3 = d3['meta']['generated_at']
print('origin .json meta.generated_at:', g2, '| mine:', g3)
assert g2 >= g3, 'origin must be newer'
open('results/dashboard_status.json', 'wb').write(b2)
js = open('results/dashboard_status.js', 'rb').read()
m = re.search(rb'"generated_at":\s*"([^"]+)"', js)
jsgen = m.group(1).decode() if m else None
print('fixed: .json <- origin; js generated_at:', jsgen)
assert jsgen == g2, 'pair still mixed: %r vs %r' % (jsgen, g2)
print('PAIR-CONSISTENT: js+json same origin side (%s)' % g2)
