# -*- coding: utf-8 -*-
# r336 bm-c: paper-ledger divergence dissection -- where do local and origin differ?
import io, sys, os, json, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
R = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'

def git(*a):
    return subprocess.run(['git', '-C', R] + list(a), capture_output=True)

def walk(obj, path=''):
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            out.update(walk(v, path + '/' + str(k)))
        return out
    if isinstance(obj, list):
        if not obj:
            return {path + '/__len__': 0}
        out = {}
        # sample first/last elements to keep output small
        for idx in (0, len(obj) - 1):
            for p, v in walk(obj[idx], path + '[%d]' % idx).items():
                out[p] = v
        out[path + '/__len__'] = len(obj)
        return out
    return {path: obj}

for f in ['results/paper/COMPOSITE-CE-01_paper.json', 'results/paper/NEEDLE-DE-01_paper.json']:
    o = json.loads(git('show', 'HEAD:' + f).stdout.decode('utf-8'))
    l = json.load(open(os.path.join(R, f.replace('/', os.sep)), encoding='utf-8'))
    fo, fl = walk(o), walk(l)
    print('===', f)
    print('top-level keys origin:', sorted(o.keys()) if isinstance(o, dict) else type(o))
    print('top-level keys local :', sorted(l.keys()) if isinstance(l, dict) else type(l))
    diffs = 0
    for k in sorted(set(fo) | set(fl)):
        if fo.get(k, '<ABSENT>') != fl.get(k, '<ABSENT>'):
            print('DIFF', k, '| origin=', str(fo.get(k, '<ABSENT>'))[:90], '| local=', str(fl.get(k, '<ABSENT>'))[:90])
            diffs += 1
            if diffs > 24:
                print('...truncated')
                break
    print('total diff leaf-samples:', diffs)
