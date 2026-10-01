import json, os
base = 'K:/Fluxgroup/FluxGroup/quant/bigmoney/results/p2cal_ext/n1_w8'
for n in (8, 9, 10, 11):
    p = os.path.join(base, f'shard-{n}-of-12.json')
    try:
        d = json.load(open(p, encoding='utf-8'))
        keys = list(d.keys())[:8]
        cells = d.get('cells')
        cn = (len(cells) if hasattr(cells, '__len__') else 'n/a')
        print(f'W8 shard-{n}: OK size={os.path.getsize(p)} toplevel={keys} cells_count_field={cn}')
    except Exception as ex:
        print(f'W8 shard-{n}: FAIL {ex}')
