# -*- coding: utf-8 -*-
# r1036 bm-c: W248 PRE-FINALIZE six-gate receipt (standing law since W217 debt;
# clone lineage _r1022bma_w247_sixgate.py W247 pattern). Burn landed 21:36-21:44
# by resident engine auto-ignite (12/12 shards self-committed d3d87cf11+f90e4db17
# via dead-window absorb); finalize not yet run. Gates: 1 splice integrity sha16 x2
# + 2 wave-row faces==freeze receipt bands + 3 banned ADMIT + 4 pf selftest 9/9
# + 5 n1 selftest + 6 shards 12/12 + seed_admit FREE-verbatim.
import hashlib
import io
import json
import os
import re
import subprocess
import sys


def sha16(p):
    return hashlib.sha256(io.open(p, 'rb').read()).hexdigest()[:16]


fr = json.load(io.open('results/_w248bmc_freeze_receipt.json', encoding='utf-8'))
pf_now = sha16('scripts/perpetual_faces.py')
n1_now = sha16('scripts/perpetual_faces_n1.py')

n1t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = n1t.find('248: {"batch": "PERPETUAL-N1-W248"')
assert i >= 0, 'W248 wave row missing'
seg = n1t[i:i + 9000]
if '249: {' in seg:
    seg = seg[:seg.find('249: {')]
row_faces = {
    'a_seed_base_561501': '561501' in seg,
    'b_exit_seed_base_544701': '544701' in seg,
    'shard_subdir_n1_w248': 'n1_w248' in seg,
    'out_name_n1_w248_results': 'n1_w248_results.json' in seg,
    'engine_owner_bm_c': 'engine_owner": "bm-c"' in seg,
}
f1 = 'seed_admit_gate rc0 base=561501 span=2000 checked=2000 verdict=FREE'
f2 = 'seed_admit_gate rc0 base=544701 span=200 checked=200 verdict=FREE'
fam = {f1: n1t.count(f1), f2: n1t.count(f2)}
m247 = re.search(r'247: \{"batch": "PERPETUAL-N1-W247"', n1t)
w247_seg = n1t[m247.start():m247.start() + 8000] if m247 else ''
if '248: {' in w247_seg:
    w247_seg = w247_seg[:w247_seg.find('248: {')]
boundary = bool(m247) and '559501' in w247_seg and '544501' in w247_seg

sd = 'results/p2cal_ext/n1_w248'
shards = sorted(f for f in os.listdir(sd) if f.startswith('shard-') and f.endswith('.json'))
sizes_ok = all(os.path.getsize(os.path.join(sd, f)) > 100000 for f in shards)

r_banned = subprocess.run([sys.executable, 'Tools/banned_direction_gate.py',
                           '--prereg', 'research/PERPETUAL_N1_W248_PREREG.md'],
                          capture_output=True, text=True)
r_pf = subprocess.run([sys.executable, 'scripts/perpetual_faces.py', 'selftest'],
                      capture_output=True, text=True)
r_n1 = subprocess.run([sys.executable, 'scripts/perpetual_faces_n1.py', 'selftest'],
                      capture_output=True, text=True)

out = {
 "machine": "bm-c",
 "wave": 248,
 "phase": "PRE-FINALIZE six-gate (r1036 bm-c own-wave window; standing law -- engine self-burn 12/12 landed 21:36-21:44 by resident engine auto-ignite, finalize not yet run)",
 "gates": {
  "splice_integrity": {
   "bands_facts_match_freeze_receipt": all(row_faces.values()),
   "pf_sha16_now": pf_now, "n1_sha16_now": n1_now,
   "pf_sha16_freeze_post": fr['pf_sha16_post'],
   "n1_sha16_freeze_post": fr['n1_sha16_post'],
   "family_seed_face_counts": fam,
   "prior_wave_247_boundary_kept": boundary,
  },
  "banned": {"rc": r_banned.returncode, "stdout_tail": (r_banned.stdout or '').strip()[-200:]},
  "pf_selftest": {"rc": r_pf.returncode, "stdout_tail": (r_pf.stdout or '').strip()[-120:]},
  "n1_selftest": {"rc": r_n1.returncode, "stdout_tail": (r_n1.stdout or '').strip()[-120:]},
  "shards": {"present": len(shards), "of": 12, "sizes_above_100k": sizes_ok,
             "files": shards},
  "seed_admit": {
   "freeze_gate_lines": fr.get('seed_admit_gate'),
   "note": "freeze-time FREE evidence consumed verbatim from _w248bmc_freeze_receipt.json; post-registration self-collision BLOCKED would be the fresh-run positive (W237.. pattern)",
  },
  "wave_configs_row": {
   "present": True, "engine_owner": "bm-c",
   "a_seed_base": 561501, "b_exit_seed_base": 544701,
   "shard_subdir": "n1_w248", "out_name": "n1_w248_results.json",
   "seed_bases_match_freeze_bands": fr['bands']['A'] == [561501, 563500] and fr['bands']['B'] == [544701, 544900],
   "row_faces_detail": row_faces,
  },
 },
 "ledger_pre": {
  "prev_total": 967735, "prev_merged_n": 541320,
  "expect_total": 969935, "expect_merged": 543520,
  "anchor": "W247 finalize (bm-a r1022 one-pass, 967,735/K=541,320) per freeze receipt w247_upstream face",
 },
}

ok = (all(row_faces.values()) and all(v >= 1 for v in fam.values()) and boundary
      and pf_now == fr['pf_sha16_post'] and n1_now == fr['n1_sha16_post']
      and len(shards) == 12 and sizes_ok
      and r_banned.returncode == 0 and r_pf.returncode == 0 and r_n1.returncode == 0)
out['verdict'] = 'ALL PASS' if ok else 'FAIL'
io.open('results/_r1036bmc_w248_sixgate.json', 'w', encoding='utf-8').write(
    json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps({'verdict': out['verdict'], 'row_faces': row_faces, 'fam': fam,
                  'boundary': boundary, 'shards': len(shards), 'pf': pf_now, 'n1': n1_now,
                  'banned_rc': r_banned.returncode, 'pf_rc': r_pf.returncode,
                  'n1_rc': r_n1.returncode}, indent=1))
raise SystemExit(0 if ok else 1)
