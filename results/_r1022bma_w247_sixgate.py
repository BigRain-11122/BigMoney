# -*- coding: utf-8 -*-
# r1022 bm-a: W247 PRE-FINALIZE six-gate receipt (standing law; clone lineage
# _r1017bma_w246_sixgate.py W246 pattern + one-pass flow). Burn landed 18:40-18:51
# by resident engine auto-ignite (12/12 shards committed via estate absorb); finalize not yet run.
# Gates: 1 splice integrity sha16 x2 + 2 wave-row faces==freeze receipt bands
# + 3 banned ADMIT + 4 pf selftest 9/9 + 5 n1 selftest + 6 shards 12/12 +
# seed_admit FREE-verbatim / BLOCKED-fresh positive.
import hashlib
import io
import json
import os
import re
import subprocess
import sys


def sha16(p):
    return hashlib.sha256(io.open(p, 'rb').read()).hexdigest()[:16]


fr = json.load(io.open('results/_w247bma_freeze_receipt.json', encoding='utf-8'))
pf_now = sha16('scripts/perpetual_faces.py')
n1_now = sha16('scripts/perpetual_faces_n1.py')

n1t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = n1t.find('247: {"batch": "PERPETUAL-N1-W247"')
assert i >= 0, 'W247 wave row missing'
seg = n1t[i:i + 9000]
if '248: {' in seg:
    seg = seg[:seg.find('248: {')]
row_faces = {
    'a_seed_base_559501': '559501' in seg,
    'b_exit_seed_base_544501': '544501' in seg,
    'shard_subdir_n1_w247': 'n1_w247' in seg,
    'out_name_n1_w247_results': 'n1_w247_results.json' in seg,
    'engine_owner_bm_a': 'engine_owner": "bm-a"' in seg,
}
f1 = 'seed_admit_gate rc0 base=559501 span=2000 checked=2000 verdict=FREE'
f2 = 'seed_admit_gate rc0 base=544501 span=200 checked=200 verdict=FREE'
fam = {f1: n1t.count(f1), f2: n1t.count(f2)}
m246 = re.search(r'246: \{"batch": "PERPETUAL-N1-W246"', n1t)
w246_seg = n1t[m246.start():m246.start() + 8000] if m246 else ''
if '247: {' in w246_seg:
    w246_seg = w246_seg[:w246_seg.find('247: {')]
boundary = bool(m246) and '557501' in w246_seg and '542201' in w246_seg

sd = 'results/p2cal_ext/n1_w247'
shards = sorted(f for f in os.listdir(sd) if f.startswith('shard-') and f.endswith('.json'))
sizes_ok = all(os.path.getsize(os.path.join(sd, f)) > 100000 for f in shards)

r_banned = subprocess.run([sys.executable, 'Tools/banned_direction_gate.py',
                           '--prereg', 'research/PERPETUAL_N1_W247_PREREG.md'],
                          capture_output=True, text=True)
r_pf = subprocess.run([sys.executable, 'scripts/perpetual_faces.py', 'selftest'],
                       capture_output=True, text=True)
r_n1 = subprocess.run([sys.executable, 'scripts/perpetual_faces_n1.py', 'selftest'],
                      capture_output=True, text=True)

out = {
 "machine": "bm-a",
 "wave": 247,
 "phase": "PRE-FINALIZE six-gate (r1022 bm-a own-wave window; standing law -- engine self-burn 12/12 landed 18:40-18:51 by resident engine auto-ignite, finalize not yet run)",
 "gates": {
  "splice_integrity": {
   "bands_facts_match_freeze_receipt": all(row_faces.values()),
   "pf_sha16_now": pf_now, "n1_sha16_now": n1_now,
   "pf_sha16_freeze_post": fr['pf_sha16_post'],
   "n1_sha16_freeze_post": fr['n1_sha16_post'],
   "family_seed_face_counts": fam,
   "prior_wave_246_boundary_kept": boundary,
  },
  "banned": {"rc": r_banned.returncode, "stdout_tail": (r_banned.stdout or '').strip()[-200:]},
  "pf_selftest": {"rc": r_pf.returncode, "stdout_tail": (r_pf.stdout or '').strip()[-120:]},
  "n1_selftest": {"rc": r_n1.returncode, "stdout_tail": (r_n1.stdout or '').strip()[-120:]},
  "shards": {"present": len(shards), "of": 12, "sizes_above_100k": sizes_ok,
             "files": shards},
  "seed_admit": {
   "freeze_gate_lines": fr.get('seed_admit_gate'),
   "note": "freeze-time FREE evidence consumed verbatim from _w247bma_freeze_receipt.json; post-registration self-collision BLOCKED would be the fresh-run positive (W237.. pattern)",
  },
  "wave_configs_row": {
   "present": True, "engine_owner": "bm-a",
   "a_seed_base": 559501, "b_exit_seed_base": 544501,
   "shard_subdir": "n1_w247", "out_name": "n1_w247_results.json",
   "seed_bases_match_freeze_bands": fr['bands']['A'] == [559501, 561500] and fr['bands']['B'] == [544501, 544700],
   "row_faces_detail": row_faces,
  },
 },
 "ledger_pre": {
  "prev_total": 965535, "prev_merged_n": 539120,
  "expect_total": 967735, "expect_merged": 541320,
  "anchor": "W246 finalize (bm-a r1018 one-pass, 965,535/K=539,120) per freeze receipt w243_upstream face",
 },
}

ok = (all(row_faces.values()) and all(v >= 1 for v in fam.values()) and boundary
      and pf_now == fr['pf_sha16_post'] and n1_now == fr['n1_sha16_post']
      and len(shards) == 12 and sizes_ok
      and r_banned.returncode == 0 and r_pf.returncode == 0 and r_n1.returncode == 0)
out['verdict'] = 'ALL PASS' if ok else 'FAIL'
io.open('results/_r1022bma_w247_sixgate.json', 'w', encoding='utf-8').write(
    json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps({'verdict': out['verdict'], 'row_faces': row_faces, 'fam': fam,
                  'boundary': boundary, 'shards': len(shards), 'pf': pf_now, 'n1': n1_now,
                  'banned_rc': r_banned.returncode, 'pf_rc': r_pf.returncode,
                  'n1_rc': r_n1.returncode}, indent=1))
raise SystemExit(0 if ok else 1)
