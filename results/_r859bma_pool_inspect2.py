raw = open(r'results/runnable_pool.json', encoding='utf-8', newline='').read()
print('total len:', len(raw))
print(repr(raw[-1500:]))
