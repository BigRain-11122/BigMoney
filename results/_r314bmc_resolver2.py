import json, sys
repo = 'K:/Fluxgroup/FluxGroup/quant/bigmoney/'
ENV_KEYS = {'ts','generated','elapsed','elapsed_sec','machine','workers','updated_at','generated_at','heartbeat_age_min','asof'}

def blocks(lines):
    h = next(i for i,l in enumerate(lines) if l.startswith('<<<<<<<'))
    b = next(i for i,l in enumerate(lines) if l.startswith('|||||||'))
    s = next(i for i,l in enumerate(lines) if l.strip()=='=======')
    e = next(i for i,l in enumerate(lines) if l.startswith('>>>>>>>'))
    return h,b,s,e

def strip_env(o):
    if isinstance(o, dict):
        return {k: strip_env(v) for k,v in o.items() if k not in ENV_KEYS}
    if isinstance(o, list):
        return [strip_env(x) for x in o]
    return o

def tryload(ls):
    try: return json.loads('\n'.join(ls))
    except Exception: return None

report = []
for path in sys.argv[1:]:
    p = repo + path.replace('\\','/')
    raw = open(p, encoding='utf-8', newline='').read()
    lines = raw.split('\n')
    h,b,s,e = blocks(lines)
    ours_full = lines[:h] + lines[h+1:b] + lines[e+1:]
    theirs_full = lines[:h] + lines[s+1:e] + lines[e+1:]
    if path.endswith('.jsonl'):
        ours = [x for x in lines[h+1:b] if x.strip()]
        theirs = [x for x in lines[s+1:e] if x.strip()]
        seen = set(ours)
        extra = [x for x in theirs if x not in seen]
        out = lines[:h] + ours + extra + lines[e+1:]
        open(p,'w',encoding='utf-8',newline='').write('\n'.join(out))
        report.append(path + ': jsonl-union +%d' % len(extra))
        continue
    if path.endswith('.md') and path != 'CODELY.md':
        # full-rewrite derive/report md -> take ours(origin); disclose
        open(p,'w',encoding='utf-8',newline='').write('\n'.join(ours_full))
        report.append(path + ': md-rewrite -> ours(origin)')
        continue
    if path == 'CODELY.md':
        ours = lines[h+1:b]; base = lines[b+1:s]; theirs = lines[s+1:e]
        uniq = [l for l in theirs if l not in set(ours) and l not in set(base)]
        out = lines[:h] + ours + uniq + lines[e+1:]
        open(p,'w',encoding='utf-8',newline='').write('\n'.join(out))
        report.append(path + ': md-block-union +%d' % len(uniq))
        continue
    oj = tryload(ours_full); tj = tryload(theirs_full)
    if oj is None or tj is None:
        open(p,'w',encoding='utf-8',newline='').write('\n'.join(ours_full))
        report.append(path + ': json-parse-fail -> ours(origin)')
        continue
    if strip_env(oj) == strip_env(tj):
        open(p,'w',encoding='utf-8',newline='').write('\n'.join(ours_full))
        report.append(path + ': AA-equal -> ours(origin)')
        continue
    # payload differs: try list-union on first match of common list-of-dict keys
    LIST_KEYS = ('history','runs','records','entries','findings','lines','items')
    merged_any = False
    if isinstance(oj, dict) and isinstance(tj, dict):
        merged = dict(oj)
        for k in LIST_KEYS:
            if isinstance(oj.get(k), list) and isinstance(tj.get(k), list):
                ov = oj[k]; tv = tj[k]
                okeys = set()
                for el in ov:
                    okeys.add(json.dumps(el, sort_keys=True, ensure_ascii=False))
                add = [el for el in tv if json.dumps(el, sort_keys=True, ensure_ascii=False) not in okeys]
                merged[k] = ov + add
                if add:
                    report.append(path + ': list-union key=%s +%d (origin %d + mine-unique %d)' % (k, len(add), len(ov), len(add)))
                else:
                    report.append(path + ': list-union key=%s no-new (origin superset)' % k)
                merged_any = True
        # also merge top-level scalar 'new' keys? skip
        if merged_any:
            for k in tj:
                if k not in merged and k not in ENV_KEYS:
                    merged[k] = tj[k]
            open(p,'w',encoding='utf-8',newline='').write(json.dumps(merged, ensure_ascii=False, indent=1))
            continue
    open(p,'w',encoding='utf-8',newline='').write('\n'.join(ours_full))
    report.append(path + ': payload-DIFF-no-list -> ours(origin) DISCLOSE')

for r in report: print('RES ' + r)
bad = []
for path in sys.argv[1:]:
    p = repo + path.replace('\\','/')
    txt = open(p, encoding='utf-8', newline='').read()
    if '<<<<<<<' in txt or '>>>>>>>' in txt or '|||||||' in txt: bad.append(path)
if bad:
    print('MARKERS-REMAIN: ' + ', '.join(bad)); sys.exit(1)
print('ALL-RESOLVED-OK')
