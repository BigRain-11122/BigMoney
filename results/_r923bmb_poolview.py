import io
for fn in ['results/runnable_pool.bm-b.json', 'results/runnable_pool.json']:
    s = io.open(fn, encoding='utf-8').read()
    i = s.find('N2U3-ALPHAGEN-RL-P1-LEG3-TRAIN')
    j = s.find('"priority"', i)
    print('===', fn, 'idx', i)
    print(s[j:j+900])
