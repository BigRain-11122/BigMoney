# _r316bmc_s0_resolver.py -- r316 S0 integration conflict resolver
# Laws: r481 (AA product adjudication, take origin :2: after envelope-only assertion),
#       r499 (layered: envelope strip -> float 1e-9 rel tol -> exact int/str),
#       r315 (CODELY union v2: stage-aware entry extraction + EOF append + dedupe fail-closed),
#       r498 fail-soft: resolve only the in-present unmerged set, no hardcoded full set.
import subprocess, json, sys, os

REPO = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
ENV_KEYS = {'machine','machine_id','elapsed_sec','elapsed','workers','worker_count','audit',
            'generated','generated_at','ts','timestamp','started_at','finished_at','host',
            'burned_by','owner','runner_sha256','code_sha256','pid','lane_machine'}

def show(rev):
    return subprocess.check_output(['git','-C',REPO,'show',rev])

def unmerged():
    out = subprocess.check_output(['git','-C',REPO,'ls-files','-u']).decode('utf-8')
    return sorted(set(l.split('\t',1)[1] for l in out.strip().splitlines() if l.strip()))

def strip_env(o):
    if isinstance(o, dict):
        return {k: strip_env(v) for k,v in o.items() if k not in ENV_KEYS}
    if isinstance(o, list):
        return [strip_env(x) for x in o]
    return o

def deep_eq(a, b, tol=1e-9):
    if isinstance(a, bool) or isinstance(b, bool):
        return a == b
    if isinstance(a,(int,float)) and isinstance(b,(int,float)):
        if a == b: return True
        denom = max(abs(a),abs(b),1e-12)
        return abs(a-b)/denom <= tol
    if isinstance(a,dict) and isinstance(b,dict):
        return set(a)==set(b) and all(deep_eq(a[k],b[k],tol) for k in a)
    if isinstance(a,list) and isinstance(b,list):
        return len(a)==len(b) and all(deep_eq(x,y,tol) for x,y in zip(a,b))
    return a == b

def canon(o):
    return json.dumps(strip_env(o), sort_keys=True, ensure_ascii=False)

def resolve_jsonl(path):
    b2 = show(':2:'+path); b3 = show(':3:'+path)
    L2 = [json.loads(l) for l in b2.decode('utf-8').splitlines() if l.strip()]
    L3 = [json.loads(l) for l in b3.decode('utf-8').splitlines() if l.strip()]
    ok = len(L2)==len(L3)
    mode = 'exact'
    if ok:
        c2 = sorted(canon(o) for o in L2); c3 = sorted(canon(o) for o in L3)
        ok = c2 == c3
    if not ok and len(L2)==len(L3):
        # r499 tolerance fallback: greedy order-insensitive match
        rem = [strip_env(x) for x in L3]; ok = True
        for x in L2:
            sx = strip_env(x)
            hit = next((i for i,y in enumerate(rem) if deep_eq(sx,y)), None)
            if hit is None: ok = False; break
            rem.pop(hit)
        mode = 'tol1e-9'
    print(('ADJ_OK' if ok else 'ADJ_FAIL'), path, 'lines', len(L2), len(L3), mode)
    if ok:
        with open(os.path.join(REPO,path),'wb') as f: f.write(b2)  # take origin :2: verbatim (r481)
    return ok

def resolve_json(path):
    b2 = show(':2:'+path); b3 = show(':3:'+path)
    j2 = json.loads(b2.decode('utf-8')); j3 = json.loads(b3.decode('utf-8'))
    ok = deep_eq(strip_env(j2), strip_env(j3))
    print(('ADJ_OK' if ok else 'ADJ_FAIL'), path)
    if ok:
        with open(os.path.join(REPO,path),'wb') as f: f.write(b2)
    return ok

def resolve_codely():
    o2 = show(':2:CODELY.md').decode('utf-8'); o3 = show(':3:CODELY.md').decode('utf-8')
    anchor = '- [2026-10-01 13:13:06 r315 bm-c]'
    lines3 = o3.splitlines()
    idx = [i for i,l in enumerate(lines3) if l.startswith(anchor)]
    if not idx:
        print('CODELY_FAIL anchor missing in :3:'); return False
    entry = lines3[idx[0]]
    if entry in o2:
        print('CODELY_DEDUPE_HIT entry already on origin side -> take origin, no append')
        with open(os.path.join(REPO,'CODELY.md'),'wb') as f: f.write(o2.encode('utf-8'))
        return True
    nl = '\r\n' if '\r\n' in o2 else '\n'
    base = o2
    if not base.endswith('\n'): base += nl
    out = base + nl + entry + nl
    with open(os.path.join(REPO,'CODELY.md'),'wb') as f: f.write(out.encode('utf-8'))
    print('CODELY_UNION_OK appended r315 entry, total_len', len(out))
    return True

def main():
    files = unmerged()
    print('UNMERGED:', files)
    ok = True
    for f in files:
        if f == 'CODELY.md': ok &= resolve_codely()
        elif f == 'results/lowamp_p2/cells_LA-EDGE_legacy_x2.jsonl': ok &= resolve_jsonl(f)
        elif f == 'results/lowamp_p2/cont_LA-EDGE_legacy_x2.json': ok &= resolve_json(f)
        else:
            print('UNEXPECTED_CONFLICT', f); ok = False
    if not ok:
        sys.exit(2)
    subprocess.check_call(['git','-C',REPO,'add','--','CODELY.md',
        'results/lowamp_p2/cells_LA-EDGE_legacy_x2.jsonl','results/lowamp_p2/cont_LA-EDGE_legacy_x2.json'])
    print('RESOLVED_ALL_OK')

if __name__ == '__main__':
    main()
