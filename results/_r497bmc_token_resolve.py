"""r497 bm-c: token_usage.json merge-conflict resolve = take-ours (HEAD)
per probe-proven union (_r497bmc_token_struct.py: 4/5 machine entries
byte-identical, default cumulative-max ours). HEAD blob direct-read per
r656 law (stage2/3 destroyed by add; HEAD:/MERGE_HEAD: canonical).
Zero-loss assertion vs MERGE_HEAD side on identical keys."""
import json
import subprocess

ours = subprocess.run(['git', 'show', 'HEAD:results/token_usage.json'],
                     capture_output=True).stdout
theirs = subprocess.run(
    ['git', 'show', 'MERGE_HEAD:results/token_usage.json'],
    capture_output=True).stdout
o, t = json.loads(ours.decode('utf-8')), json.loads(theirs.decode('utf-8'))
# union proof re-run inside resolve window (state may have moved)
mism = []
for k in set(o['machines']) | set(t['machines']):
    if k in o['machines'] and k in t['machines']:
        if o['machines'][k] != t['machines'][k] and k != 'default':
            mism.append(k)
    elif k not in o['machines']:
        mism.append(k)  # theirs-only machine key would be LOST by take-ours
assert not mism, "take-ours would lose theirs-only/differing keys: %s" % mism
assert o['machines']['default']['report_bytes'] >= \
    t['machines']['default']['report_bytes'], "cumulative regression"
with open('results/token_usage.json', 'wb') as f:
    f.write(ours)
back = json.load(open('results/token_usage.json', encoding='utf-8'))
assert back == o, "reparse mismatch"
print("RESOLVE OK: token_usage.json take-ours (union), machines=%d, "
      "default.report_bytes=%d >= theirs %d, zero theirs-only keys"
      % (len(back['machines']), back['machines']['default']['report_bytes'],
         t['machines']['default']['report_bytes']))
