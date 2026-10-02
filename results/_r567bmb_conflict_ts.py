import re
t = open('results/compute_audit.json', encoding='utf-8', errors='replace').read()
sides = re.findall(r'(<<<<<<<|=======|>>>>>>>)', t)
print('markers:', len(sides))
if '<<<<<<<' in t:
    ours = t.split('<<<<<<<')[1].split('=======')[0]
    theirs = t.split('=======')[1].split('>>>>>>>')[0]
    m1 = re.search(r'"ts": "([^"]+)"', ours)
    m2 = re.search(r'"ts": "([^"]+)"', theirs)
    print('ours(=origin/bm-a side) ts:', m1.group(1) if m1 else None)
    print('theirs(=my pick) ts:', m2.group(1) if m2 else None)
    print('ours len:', len(ours), 'theirs len:', len(theirs))
else:
    print('no markers (already resolved?)')
