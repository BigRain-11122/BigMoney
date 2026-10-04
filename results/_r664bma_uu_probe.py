import subprocess, json, re

raw = open('docs/daily_report/REPORT-2026-10-04.json', 'rb').read().decode('utf-8', errors='replace')
# split conflict: ours (HEAD) vs theirs (origin/main)
m_ours = re.search(r'<<<<<<< HEAD\r?\n(.*?)\r?\n=======\r?\n(.*?)\r?\n>>>>>>> ', raw, re.S)
if m_ours:
    ours, theirs = m_ours.group(1), m_ours.group(2)
else:
    # markers may vary; find them generically
    parts = re.split(r'<<<<<<< HEAD\r?\n|=======\r?\n|>>>>>>> [^\r\n]*\r?\n', raw)
    print('split parts:', len(parts))
    ours, theirs = parts[1], parts[2]

def get_ts(s):
    mm = re.search(r'"generated[^"]*"\s*:\s*"([^"]+)"', s)
    mm2 = re.search(r'"ts"\s*:\s*"([^"]+)"', s)
    return (mm.group(1) if mm else None, mm2.group(1) if mm2 else None)

print('ours ts:', get_ts(ours))
print('theirs ts:', get_ts(theirs))
print('ours bytes:', len(ours), '| theirs bytes:', len(theirs))
# quick structural diff: which keys differ at top level
try:
    o = json.loads(ours); t = json.loads(theirs)
    diff_keys = [k for k in set(list(o) + list(t)) if json.dumps(o.get(k), sort_keys=True) != json.dumps(t.get(k), sort_keys=True)]
    print('top-level diff keys:', diff_keys[:12])
except Exception as e:
    print('json parse fail:', e)
