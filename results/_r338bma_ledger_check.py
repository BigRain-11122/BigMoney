import json
import re

# 1. count completed runs in autofill log
log = open('logs/autofill_SINA-CONSTRUCT-P1.log', encoding='utf-8', errors='replace').read()
print('log "written" count:', log.count('written'), '| "MAIN: IS ic" count:', log.count('MAIN: IS ic'))
print('log first/last lines:')
ls = log.splitlines()
for l in ls[:4]:
    print('  HEAD:', l[:170])
for l in ls[-4:]:
    print('  TAIL:', l[:170])

# 2. find trials ledger file
import subprocess
sg = open('scripts/science_gates.py', encoding='utf-8').read()
m = re.search(r'def append_ledger.*?(?=\ndef |\Z)', sg, re.S)
print('== append_ledger source:')
print(m.group(0)[:1200] if m else 'NOT FOUND')
