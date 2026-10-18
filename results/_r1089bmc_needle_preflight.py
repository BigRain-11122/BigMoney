# -*- coding: utf-8 -*-
# r1089 bm-c: W267 chain-tail MEASURED needle preflight (r1077 law) before
# authoring the W267 sixgate/fivekeys/sec78 clones. Read-only; prints + writes
# results/_r1089bmc_needle_preflight.json.
import hashlib
import io
import json
import os
import subprocess

n1 = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
pf = io.open('scripts/perpetual_faces.py', encoding='utf-8').read()

SPLICE = '7b9e9377374504ff6e7a524734334d20ff0b3e29'
fr = json.load(io.open('results/_w267bmc_freeze_receipt.json', encoding='utf-8'))

r_git_n1 = subprocess.run(['git', 'show', f'{SPLICE}:scripts/perpetual_faces_n1.py'],
                          capture_output=True)
r_git_pf = subprocess.run(['git', 'show', f'{SPLICE}:scripts/perpetual_faces.py'],
                          capture_output=True)
r_diff_pf = subprocess.run(['git', 'diff', SPLICE, '--', 'scripts/perpetual_faces.py'],
                           capture_output=True, text=True)

# registry row segment (W267 row -> next row marker or 9000 chars)
i = n1.find('267: {"batch": "PERPETUAL-N1-W267"')
assert i >= 0, 'W267 registry row missing'
seg = n1[i:i + 9000]
if '268: {' in seg:
    seg = seg[:seg.find('268: {')]
row_faces = {
    'a_seed_base_602701': '602701' in seg,
    'b_exit_seed_base_604701': '604701' in seg,
    'shard_subdir_n1_w267': 'n1_w267' in seg,
    'out_name_n1_w267_results': 'n1_w267_results.json' in seg,
    'engine_owner_bm_c': 'engine_owner": "bm-c"' in seg,
}

# prior-wave W266 registry boundary faces
j = n1.find('266: {"batch": "PERPETUAL-N1-W266"')
w266_seg = n1[j:j + 9000] if j >= 0 else ''
if '267: {' in w266_seg:
    w266_seg = w266_seg[:w266_seg.find('267: {')]
boundary = bool(j >= 0) and '600501' in w266_seg and '602501' in w266_seg

# setwave birth-station presence gates (phase5 face, segment after W266 block)
k266 = n1.rfind('_set_wave(266)')
after266 = n1[k266 + len('_set_wave(266)'):]
setwave_gates = {
    'count_set_wave_267_whole_file': n1.count('_set_wave(267)'),
    'count_set_wave_265_whole_file': n1.count('_set_wave(265)'),
    'after_w266_block_contains_267': '_set_wave(267)' in after266,
    'after_w266_block_contains_265': '_set_wave(265)' in after266,
    'after_w266_block_contains_266': '_set_wave(266)' in after266,
}

fam = {
    'base=602701 span=2000': n1.count('base=602701 span=2000'),
    'base=604701 span=200': n1.count('base=604701 span=200'),
}

n1_sha16 = hashlib.sha256(io.open('scripts/perpetual_faces_n1.py', 'rb').read()).hexdigest()[:16]
pf_sha16 = hashlib.sha256(io.open('scripts/perpetual_faces.py', 'rb').read()).hexdigest()[:16]
n1_landed = hashlib.sha256(r_git_n1.stdout).hexdigest()[:16]
pf_landed = hashlib.sha256(r_git_pf.stdout).hexdigest()[:16]

sd = 'results/p2cal_ext/n1_w267'
shards = sorted(f for f in os.listdir(sd) if f.startswith('shard-') and f.endswith('.json'))

prereg_path = 'research/PERPETUAL_N1_W267_PREREG.md'
prereg = io.open(prereg_path, encoding='utf-8', newline='').read()
placeholders = [n for n, ln in enumerate(prereg.splitlines(), 1) if '占位' in ln]

w266 = json.load(io.open('results/perpetual_faces/n1_w266_results.json', encoding='utf-8'))
pool = w266['null_pool_cumulative']
sl = w266['skill_line_v2_k_lift']
famA = w266['families']['A_random_engine_exit']


def _find_ledger(obj):
    if isinstance(obj, dict):
        if 'ledger' in obj and isinstance(obj['ledger'], dict) and 'total' in obj['ledger']:
            return obj['ledger']
        for v in obj.values():
            r = _find_ledger(v)
            if r:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = _find_ledger(v)
            if r:
                return r
    return None


led = _find_ledger(w266)
keys_w266 = {
    'merged_mu': pool['merged']['mu'],
    'merged_sigma': pool['merged']['sigma'],
    'merged_n': pool['merged']['n_values'],
    'w266_only_mu': pool['w266_only']['mu'],
    'w266_only_sigma': pool['w266_only']['sigma'],
    'se_mu_at_k583120': pool['se_mu_at_k583120'],
    'a_p95': famA['full_sharpe_p95'],
    'a_p99': famA['full_sharpe_p99'],
    'line_pre_w266': sl['line_pre_w266'],
    'line_merged_583120': sl['line_merged_583120'],
    'line_delta_k_lift': sl['line_delta_k_lift'],
    'n_eff_held_equal': sl['n_eff_held_equal'],
    'ledger_total': led['total'],
    'ledger_prev_total': led['prev_total'],
    'shards_consumed': w266.get('shards_consumed'),
}

out = {
    'splice': SPLICE,
    'sha16': {'n1_worktree': n1_sha16, 'pf_worktree': pf_sha16,
              'n1_landed': n1_landed, 'pf_landed': pf_landed,
              'fr_pf_post': fr['pf_sha16_post'],
              'fr_n1_post_preheal': fr['n1_sha16_post'],
              'fr_n1_healed': fr['post_splice_heals']['setwave_rootcure']['n1_sha16_healed'],
              'pf_diff_empty': len((r_diff_pf.stdout or '').strip()) == 0 and r_diff_pf.returncode == 0},
    'row_faces': row_faces,
    'boundary_w266_kept': boundary,
    'setwave_gates': setwave_gates,
    'family_seed_faces': fam,
    'shards': {'count': len(shards), 'files': shards,
               'sizes_above_100k': all(os.path.getsize(os.path.join(sd, f)) > 100000 for f in shards)},
    'prereg': {'path': prereg_path, 'bytes': len(prereg.encode("utf-8")),
               'placeholder_lines': placeholders, 'placeholder_count': len(placeholders)},
    'keys_w266_finalize_actuals': keys_w266,
    'heal_evidence_files': {
        'setwave_heal_py': os.path.exists('results/_r1088bmc_n1_setwave_heal.py'),
        'derive_editor_log': os.path.exists('results/_r1088bmc_derive_editor_log.txt'),
    },
}
io.open('results/_r1089bmc_needle_preflight.json', 'w', encoding='utf-8').write(
    json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps(out, indent=1, ensure_ascii=False))
