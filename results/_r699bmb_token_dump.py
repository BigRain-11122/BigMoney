# r699 bm-b: dump token_usage machines entry structure
import json, subprocess, io
ROOT = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
wt = json.load(io.open(ROOT+r'\results\token_usage.json', encoding='utf-8'))
mach = wt.get('machines') or {}
for mk in sorted(mach.keys()):
    print('==', mk, '=>', json.dumps(mach[mk], ensure_ascii=False)[:400])
