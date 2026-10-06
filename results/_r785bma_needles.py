# -*- coding: utf-8 -*-
import json
r = json.load(open('results/_r785bma_w161_face_probe_receipt.json', encoding='utf-8'))
print('faces:', r['faces'])
print('chain n=', len(r['mat_chain_rows']), r['mat_chain_rows'][:2], '..', r['mat_chain_rows'][-2:])
for k, v in r['needles'].items():
    tot = v['pf_blk'] + v['entry'] + v['mat'] + v['claim']
    print(f"{tot}  pfblk={v['pf_blk']} entry={v['entry']} mat={v['mat']} claim={v['claim']}  {k[:72]}")
