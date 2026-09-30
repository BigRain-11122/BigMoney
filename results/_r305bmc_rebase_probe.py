# -*- coding: utf-8 -*-
"""r305 bm-c rebase conflict probe: raw-blob stage2/3 structured diff per unmerged path."""
import subprocess, json, hashlib, sys

def blob(stage, path):
    return subprocess.check_output(['git', 'show', f':{stage}:{path}'])

def sha(b):
    return hashlib.sha256(b).hexdigest()[:12]

paths = [
    'CODELY.md',
    'results/paper/COMPOSITE-CE-01_paper.json',
    'results/paper/COMPOSITE-CE-02_paper.json',
    'results/paper/DROUGHT-CE-01_paper.json',
    'results/paper/ENGULF-CE-01_paper.json',
    'results/paper/NEEDLE-DE-01_paper.json',
    'results/paper/VOLATILITY-CE-01_paper.json',
    'results/paper_export/export-2026-09-30.json',
    'results/paper_export/latest.json',
    'results/t35_open_fill_verify.json',
    'results/token_usage.json',
    'results/x2_watch_log.jsonl',
]
out = {}
for p in paths:
    try:
        b2, b3 = blob(2, p), blob(3, p)
    except Exception as e:
        out[p] = {'error': str(e)}
        continue
    rec = {'sha2': sha(b2), 'sha3': sha(b3), 'same': b2 == b3,
           'len2': len(b2), 'len3': len(b3), 'eol': 'CRLF' if b'\r\n' in b2[:400] else 'LF'}
    if b2 != b3 and p.endswith('.json'):
        try:
            j2, j3 = json.loads(b2.decode('utf-8')), json.loads(b3.decode('utf-8'))
            if isinstance(j2, dict) and isinstance(j3, dict):
                keys2, keys3 = set(j2), set(j3)
                rec['keys_only2'] = sorted(keys2 - keys3)[:10]
                rec['keys_only3'] = sorted(keys3 - keys2)[:10]
                diffk = []
                for k in sorted(keys2 & keys3):
                    if j2[k] != j3[k]:
                        v2, v3 = j2[k], j3[k]
                        d = {'key': k, 'type': type(v2).__name__}
                        if isinstance(v2, dict) and isinstance(v3, dict):
                            # top-level differing subkeys
                            sk = [s for s in set(v2) | set(v3) if v2.get(s) != v3.get(s)]
                            d['subkeys'] = sk[:12]
                        elif isinstance(v2, list) and isinstance(v3, list):
                            d['len2'] = len(v2); d['len3'] = len(v3)
                            d['head2'] = v2[:2]; d['head3'] = v3[:2]
                        else:
                            d['v2'] = str(v2)[:80]; d['v3'] = str(v3)[:80]
                        diffk.append(d)
                rec['dict_diffs'] = diffk[:16]
        except Exception as e:
            rec['json_err'] = str(e)
    if p.endswith('.jsonl'):
        L2 = [l for l in b2.decode('utf-8').splitlines() if l.strip()]
        L3 = [l for l in b3.decode('utf-8').splitlines() if l.strip()]
        s2, s3 = set(L2), set(L3)
        rec['lines2'] = len(L2); rec['lines3'] = len(L3)
        rec['only2_ct'] = len(s2 - s3); rec['only3_ct'] = len(s3 - s2)
        rec['only3_head'] = sorted(s3 - s2)[:2]
    out[p] = rec
print(json.dumps(out, ensure_ascii=False, indent=1, default=str))
