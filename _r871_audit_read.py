import json
ln = None
for line in open('results/_r871bmc_s6_log.txt', encoding='utf-8', errors='replace'):
    if '"audit_version"' in line:
        ln = line.strip()
        break
d = json.loads(ln)
print('flags:', d.get('flags'))
print('zombies:', d.get('zombies_killed', d.get('zombies')))
print('pool_ready_unclaimed:', d.get('pool_ready_unclaimed'))
print('verdict:', d.get('verdict'))
