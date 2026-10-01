import json, re
d = json.load(open('results/perpetual_faces/n1_w46_results.json', encoding='utf-8'))
print('batch:', d['batch'], '| cutoff:', d.get('evidence_cutoff'))
print('null_pool_cumulative:', d['null_pool_cumulative'])
print('skill_line:', json.dumps(d.get('skill_line_v2_k_lift'), ensure_ascii=False)[:260])
print('shards_consumed:', d['shards_consumed'])
print('audit:', json.dumps(d.get('audit'), ensure_ascii=False)[:200])
print()
src = open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
for m in re.finditer(r'^(def [a-zA-Z_]+|FINALIZE\w*|sub.*finalize|finalize)', src, re.M):
    print('hit:', src[m.start():m.start()+90].split('\n')[0])
i = src.find('finalize')
print('--- around first finalize mention ---')
print(src[max(0,i-300):i+900])
