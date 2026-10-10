import json, re
d = json.load(open('results/perpetual_faces/n1_w205_results.json', encoding='utf-8'))
s = json.dumps(d, ensure_ascii=False)
for pat in [r'"mu":\s*[0-9.\-]+', r'"sigma":\s*[0-9.\-]+', r'"se_mu[^"]*":\s*[0-9.\-]+',
            r'"full_sharpe_p95":\s*[0-9.\-]+', r'"full_sharpe_p99":\s*[0-9.\-]+',
            r'"n_values[^"]*":\s*[0-9]+', r'"k_merged[^"]*":\s*[0-9]+',
            r'"merged[^"]*":\s*[0-9.\-]+', r'"w_only[^"]*":\s*[0-9.\-]+',
            r'"a_tier[^"]*":\s*[0-9.\-]+', r'"b_tier[^"]*":\s*[0-9.\-]+', r'"shards_consumed":\s*[0-9/]+']:
    print(pat.split('"')[1], '=>', re.findall(pat, s)[:6])
