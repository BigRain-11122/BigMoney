"""r803 bm-b rebase conflict resolver (pick 3/4 = churn-absorb-1 vs origin bm-a r816 wave).

Canon per bigmoney-conflict-resolve SKILL.md:
- snapshot/doc regen twins -> deep-ts probe (max internal ISO ts per blob), newer side wins, tie->ours(origin)
- rolling-ledger (compute_audit history / regime_state history+transitions) -> row-identity union zero-loss, state fields take newer
- append-log (marks jsonl AA) -> line-level union zero-loss
- rebase stage inversion: stage2=ours=origin/upstream, stage3=theirs=local commit
Receipt: results/_r803bmb_rebase_resolve.json
"""
import subprocess, json, re, sys, os

ROOT = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
os.chdir(ROOT)

def git_bytes(*args):
    r = subprocess.run(['git'] + list(args), capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {args} rc={r.returncode}: {r.stderr.decode('utf-8', 'replace')[:300]}")
    return r.stdout

ISO = re.compile(rb'20\d\d-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:\+08:00)?')

LEDGERS = {
    'results/compute_audit.json': ['history'],
    'results/regime_state.json': ['history', 'transitions'],
}
LINE_UNION = {'results/paper/marks/marks-20261007.jsonl',
              'results/saturation_engine/history_bm-b.jsonl'}

def stage_blobs():
    out = git_bytes('ls-files', '-u').decode('utf-8', 'replace')
    entries = {}
    for line in out.strip().splitlines():
        meta, path = line.split('\t', 1)
        mode, sha, stage = meta.split()
        entries.setdefault(path, {})[int(stage)] = sha
    return entries

def blob(path, sha):
    return git_bytes('cat-file', 'blob', sha)

def ts_max(raw):
    m = ISO.findall(raw)
    if not m:
        return None
    return max(m)

def detect_indent(raw):
    for line in raw.split(b'\n')[1:6]:
        if line.startswith(b'  '):
            return 2
        if line.startswith(b'    '):
            return 4
        if line.startswith(b'\t'):
            return None  # tab
    return 2

receipt = {'round': 'r803', 'pick': 'churn-absorb-1 a226e4b71', 'faces': [], 'asserts': []}

entries = stage_blobs()
conflict_paths = sorted(entries.keys())
print(f"conflict faces: {len(conflict_paths)}")

for path in conflict_paths:
    sha2 = entries[path].get(2)  # ours = origin
    sha3 = entries[path].get(3)  # theirs = local
    b2 = blob(path, sha2) if sha2 else None
    b3 = blob(path, sha3) if sha3 else None
    face = {'path': path}

    if path in LINE_UNION:
        lines2 = [l for l in (b2 or b'').split(b'\n') if l.strip()]
        lines3 = [l for l in (b3 or b'').split(b'\n') if l.strip()]
        set2, set3 = set(lines2), set(lines3)
        union = list(lines2) + [l for l in lines3 if l not in set2]
        # ts-stable: identical trailing lines deduped above; verify zero loss
        assert len(union) == len(set(union)), f"line union dup in {path}"
        assert len(union) >= max(len(lines2), len(lines3)), f"line union loss in {path}"
        raw = b'\n'.join(union) + (b'\n' if (b2 or b3).endswith(b'\n') or True else b'')
        face['recipe'] = 'line-union'
        face['counts'] = [len(lines2), len(lines3), len(union)]
        receipt['asserts'].append(f"{path}: |A|={len(lines2)} |B|={len(lines3)} |A u B|={len(union)} zero-loss")
    elif path in LEDGERS:
        d2 = json.loads(b2.decode('utf-8'))
        d3 = json.loads(b3.decode('utf-8'))
        base = d2  # origin shape as base (newer writer authority)
        merged_keys = 0
        for key in LEDGERS[path]:
            a = base.get(key) or []
            b = d3.get(key) or []
            a_ids = {json.dumps(r, sort_keys=True, ensure_ascii=False) for r in a}
            for row in b:
                rid = json.dumps(row, sort_keys=True, ensure_ascii=False)
                if rid not in a_ids:
                    a.append(row)
                    a_ids.add(rid)
                    merged_keys += 1
            base[key] = a
        # state fields: take from newer-ts side
        t2, t3 = ts_max(b2), ts_max(b3)
        newer = d3 if (t3 and (not t2 or t3 > t2)) else d2
        for k, v in newer.items():
            if k not in LEDGERS[path]:
                base[k] = v
        indent = detect_indent(b2)
        raw = json.dumps(base, ensure_ascii=False, indent=indent).encode('utf-8')
        if b2.endswith(b'\n'):
            raw += b'\n'
        json.loads(raw.decode('utf-8'))  # parse-verify before write
        face['recipe'] = 'ledger-union'
        face['merged_rows_from_local'] = merged_keys
        face['ts'] = [t2.decode() if t2 else None, t3.decode() if t3 else None]
        la = len(d2.get(LEDGERS[path][0]) or []) + len(d3.get(LEDGERS[path][0]) or [])
        lu = len(base[LEDGERS[path][0]])
        receipt['asserts'].append(f"{path}: union rows={lu} (sides {len(d2.get(LEDGERS[path][0]) or [])}/{len(d3.get(LEDGERS[path][0]) or [])}) merged_from_local={merged_keys}")
    else:
        # deep-ts snapshot: newer side wins, tie -> ours(origin)
        t2, t3 = ts_max(b2 or b''), ts_max(b3 or b'')
        if t3 and (not t2 or t3 > t2):
            chosen, side = b3, 'theirs(local)'
        else:
            chosen, side = b2, 'ours(origin)'
        raw = chosen
        if path.endswith('.json'):
            try:
                json.loads(raw.decode('utf-8'))
            except Exception:
                other = b3 if chosen is b2 else b2
                if other:
                    try:
                        json.loads(other.decode('utf-8'))
                        raw = other
                        side += ' (fallback: chosen side unparseable)'
                    except Exception:
                        pass
        face['recipe'] = 'deep-ts-take-new'
        face['ts'] = [t2.decode() if t2 else None, t3.decode() if t3 else None]
        face['took'] = side
    with open(path, 'wb') as f:
        f.write(raw)
    face['bytes_written'] = len(raw)
    receipt['faces'].append(face)
    print(f"  {path}: {face['recipe']} -> {face.get('took', face.get('counts', ''))}")

with open('results/_r803bmb_rebase_resolve2.json', 'w', encoding='utf-8') as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("receipt written; faces resolved:", len(receipt['faces']))
