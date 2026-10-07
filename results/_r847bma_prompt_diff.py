import subprocess

for stage, name in ((2, 'theirs'), (3, 'ours')):
    t = subprocess.run(['git', 'show', ':%d:Tools/iteration_prompt.txt' % stage],
                       capture_output=True).stdout.decode('utf-8', errors='replace')
    i = t.find(u'闲置硬触发')
    j = t.find(u'> 修红', i)
    seg = t[i:j] if i >= 0 and j > i else 'SEGMENT NOT FOUND i=%d j=%d' % (i, j)
    with open('results/_r847bma_prompt_%s.txt' % name, 'w', encoding='utf-8') as f:
        f.write(seg)
    print(name, 'segment len:', len(seg))
