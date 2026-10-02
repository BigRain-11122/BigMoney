import psutil, json, glob, os

for pid in [35768, 104552]:
    try:
        p = psutil.Process(pid)
        print(pid, '|', p.status(), '|',
              ' '.join(p.info.get('cmdline') or [])[:130])
        p.cmdline()
        print('   full:', ' '.join(p.cmdline())[-160:])
    except Exception as ex:
        print(pid, 'gone:', ex)

for d in sorted(glob.glob('results/pool_claims/FUND-VALUE*')):
    print('claim dir:', os.path.basename(d)[:55])
    for f in sorted(glob.glob(d + '/*')):
        try:
            j = json.load(open(f, encoding='utf-8'))
            print('   ', os.path.basename(f), '->',
                  json.dumps({k: j[k] for k in list(j)[:6]},
                             ensure_ascii=False)[:200])
        except Exception as ex:
            print('   ', os.path.basename(f), 'ERR', ex)

for cell in ['VALUE-PE_x2', 'VALUE-PB_x1', 'VALUE-PB_x2']:
    p = f'results/fund_value_p1/cells_{cell}.jsonl'
    if os.path.exists(p):
        n = sum(1 for _ in open(p, encoding='utf-8'))
        print(f'checkpoint {cell}: {n} cells')
    else:
        print(f'checkpoint {cell}: absent')
print('cont x2 exists:', os.path.exists('results/fund_value_p1/cont_VALUE-PE_x2.json'))
