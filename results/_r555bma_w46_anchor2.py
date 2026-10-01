"""r555 helper: full key dump of W46 finalize product."""
import subprocess, json

d = json.loads(subprocess.check_output(['git', 'show', 'origin/main:results/perpetual_faces/n1_w46_results.json']))
npc = d['null_pool_cumulative']
print('npc ALL keys:', sorted(npc.keys()))
for k in sorted(npc.keys()):
    v = npc[k]
    if not isinstance(v, (list, dict)):
        print('  npc.%s = %s' % (k, v))
print()
fams = d['families']
for fam, fv in fams.items():
    agg = {k: v for k, v in fv.items() if not isinstance(v, list)}
    print('family', fam, '->', json.dumps(agg, ensure_ascii=False))
print()
print('science_gates block:', json.dumps(d.get('science_gates', {}), ensure_ascii=False)[:600])
print('shards_consumed:', json.dumps(d.get('shards_consumed', {}), ensure_ascii=False)[:300])
print('batch:', d.get('batch'), '| generated:', d.get('generated'), '| cutoff:', d.get('evidence_cutoff'))
