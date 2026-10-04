# r684 bm-b: inspect the 12 pending contest legs (grammar/params/source refs)
import json, io

doc = json.load(io.open(r'results/contest_p1/entrants.json', encoding='utf-8'))
print('n_entrants', doc.get('n_entrants'), 'by_source', json.dumps(doc.get('n_by_source')))
for e in doc['entrants']:
    if e['source'] in ('REV_CENSUS_POSITIVE', 'LOWAMP_DEEP_EXPLORATION'):
        g = e.get('grammar', {})
        print('---', e['contest_id'], '|', e.get('face_name'), '|', e.get('source'))
        print('  grammar:', json.dumps(g, ensure_ascii=False)[:500])
        print('  ytd_legs:', e.get('ytd_legs'), '| grammar_ref:', e.get('grammar_ref', '')[:120])
