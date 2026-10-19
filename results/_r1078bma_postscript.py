# -*- coding: utf-8 -*-
# r1078 bm-a postscript: push_verified + sync + notes_r1078 into state face (file channel, inline -c double-quote pit avoided)
import json, subprocess
from datetime import datetime

ts = datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + '+08:00'
tip = subprocess.run(['git', 'rev-parse', 'origin/main'], capture_output=True, text=True).stdout.strip()
note = ('r1078 delivery: push race vs bm-c r1115 + bm-b r1021 (2 origin commits mid-window) -> amend absorb live face (r1028/r1074 recipe) '
 '-> rebase 18-UU resolver results/_r1078bma_uu_resolve.py (r965/r1071/r419 recipes: report/live twins newer-generated same-side, '
 'compute_audit/regime_state history-union, marks line-union 10/17 all-valid, d19wm+receipts newer-ts, dashboard/scorecard host=bm-a operative) '
 '-> continue one-pass clean (7th live-fire of the family, first clean continue) -> post-push fetch behind-0 ahead-0 first-try. '
 'PIT (self, tool-layer): PS here-string python -c strips embedded double quotes in native arg passing -- single-quote-only law for inline python '
 '(chr()-escaping everything also breaks format-string literals; file channel is the reliable path, pit-encoding family)')
pv = {'ts': ts, 'origin_tip': tip, 'behind': 0, 'ahead': 0, 'note': 'r1078 delivered db1b812eff first-try after rebase; behind-0 ahead-0 post-push fetch verified'}

def eol_of(p):
    raw = open(p, 'rb').read(65536)
    return '\r\n' if b'\r\n' in raw else '\n'

def rw(p, fn):
    e = eol_of(p)
    j = json.load(open(p, encoding='utf-8'))
    fn(j)
    with open(p, 'w', encoding='utf-8', newline=e) as f:
        json.dump(j, f, ensure_ascii=False, indent=1)
        f.write(e)
    json.load(open(p, encoding='utf-8'))

def apply(j):
    j['push_verified'] = pv
    j['sync'] = dict(pv)
    j['last_delivery_verified_at'] = ts
    j['notes_r1078'] = note

rw('state-bm-a.json', apply)
print('POSTSCRIPT_OK', ts, tip[:10])
