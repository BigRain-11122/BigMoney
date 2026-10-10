# -*- coding: utf-8 -*-
# r846 bm-c: dump null_pool_cumulative + skill_line_v2_k_lift + families summary for §7 backfill
import io, json
d = json.load(io.open('results/perpetual_faces/n1_w206_results.json', encoding='utf-8'))
npc = d.get('null_pool_cumulative') or {}
skl = d.get('skill_line_v2_k_lift') or {}
fams = d.get('families') or {}
out = {'null_pool_cumulative': npc, 'skill_line_v2_k_lift': skl}
# families summary: strip runs arrays to stats only
fam_sum = {}
for k, v in fams.items():
    fam_sum[k] = {kk: vv for kk, vv in v.items() if kk != 'runs'}
    fam_sum[k]['n_runs'] = len(v.get('runs') or [])
    # band stats from runs (p95/p99 of 'full' values, mu)
    runs = v.get('runs') or []
    fulls = [r.get('full') for r in runs if isinstance(r.get('full'), (int, float))]
    if fulls:
        import statistics as st
        s = sorted(fulls)
        n = len(s)
        fam_sum[k]['full_mu'] = st.fmean(s)
        fam_sum[k]['full_p95'] = s[max(0, int(round(0.95 * n)) - 1)]
        fam_sum[k]['full_p99'] = s[max(0, int(round(0.99 * n)) - 1)]
out['families_summary'] = fam_sum
io.open('results/_r846bmc_w206_npc_dump.txt', 'w', encoding='utf-8').write(
    json.dumps(out, ensure_ascii=False, indent=1, default=str))
print('npc keys:', list(npc.keys()))
print('skl:', json.dumps(skl, ensure_ascii=False)[:400])
