# r985 bm-a W238 PRE-FINALIZE six-gate probe (splice integrity legs) -- read-only
import io, json, hashlib, re, sys, os
OUT = {}
fr = json.load(io.open('results/_w238bma_freeze_receipt.json', encoding='utf-8'))
bands = fr['bands']
n1 = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
m = re.search(r'WAVE_CONFIGS\[238\][^\n]*\n(?:\s+[^\n]*\n){0,14}', n1)
block = m.group(0) if m else ''
row_ok = ('538404' in block and '540403' in block and '540404' in block and '540603' in block
          and 'n1_w238' in block and 'bm-a' in block)
OUT['wave_configs_row'] = {
    'found': bool(m),
    'bands_seed_a_lo': bands['a_lo'], 'bands_seed_a_hi': bands['a_hi'],
    'bands_seed_b_lo': bands['b_lo'], 'bands_seed_b_hi': bands['b_hi'],
    'engine_owner_bm_a': 'bm-a' in block, 'shard_subdir_n1_w238': 'n1_w238' in block,
    'row_faces_match_freeze_receipt': row_ok,
    'block_head': block.splitlines()[0][:160] if block else '',
}
faces = ['seed_admit_gate rc0 base=538404 span=2000 checked=2000 verdict=FREE',
         'seed_admit_gate rc0 base=540404 span=200 checked=200 verdict=FREE']
fam_counts = {f: n1.count(f) for f in faces}
OUT['family6_seed_faces'] = {
    'seed_face_counts_in_n1_canon': fam_counts,
    'seed_faces_present_at_least_once': all(v >= 1 for v in fam_counts.values()),
}
m237 = re.search(r'WAVE_CONFIGS\[237\][^\n]*\n(?:\s+[^\n]*\n){0,14}', n1)
b237 = m237.group(0) if m237 else ''
OUT['prior_wave_boundary'] = {
    'w237_row_present': bool(m237),
    'w237_bands_intact': ('536204' in b237 and '538204' in b237),
}
def sha16(p):
    return hashlib.sha256(io.open(p, 'rb').read()).hexdigest()[:16]
pf_now, n1_now = sha16('scripts/perpetual_faces.py'), sha16('scripts/perpetual_faces_n1.py')
OUT['sha16_clean_equal'] = {
    'pf_now': pf_now, 'pf_freeze_post': fr['pf_sha16_post'],
    'n1_now': n1_now, 'n1_freeze_post': fr['n1_sha16_post'],
    'pf_equal': pf_now == fr['pf_sha16_post'],
    'n1_equal': n1_now == fr['n1_sha16_post'],
}
sd = 'results/p2cal_ext/n1_w238'
shards = [f for f in os.listdir(sd) if f.startswith('shard-') and f.endswith('.json')]
sizes = {f: os.path.getsize(os.path.join(sd, f)) for f in shards}
OUT['shards'] = {'present': len(shards), 'of': 12,
                 'min_size': min(sizes.values()) if sizes else 0,
                 'all_above_100k': all(v > 100000 for v in sizes.values())}
ok = (row_ok
      and OUT['family6_seed_faces']['seed_faces_present_at_least_once']
      and OUT['prior_wave_boundary']['w237_row_present']
      and OUT['prior_wave_boundary']['w237_bands_intact']
      and OUT['sha16_clean_equal']['pf_equal']
      and OUT['sha16_clean_equal']['n1_equal']
      and OUT['shards']['present'] == 12
      and OUT['shards']['all_above_100k'])
OUT['verdict'] = 'PASS' if ok else 'FAIL'
print(json.dumps(OUT, ensure_ascii=False, indent=1))
sys.exit(0 if ok else 1)
