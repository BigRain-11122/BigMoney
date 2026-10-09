import re, json, os
t = open(r'results/update_status.json', encoding='utf-8-sig').read()
ours = theirs = None
if '<<<<<<<' in t:
    ours = t.split('<<<<<<<')[1].split('=======')[0]
    theirs = t.split('=======')[1].split('>>>>>>>')[0]
def ts_of(s):
    m = re.search(r'"ts"\s*:\s*"([^"]+)"', s)
    if m: return m.group(1)
    m = re.findall(r'"(2026-10-09[^"]*)"', s)
    return m[:2]
print('OURS ts:', ts_of(ours))
print('THEIRS ts:', ts_of(theirs))
print('OURS head:', (ours or '').strip()[:200])
print('THEIRS head:', (theirs or '').strip()[:200])
