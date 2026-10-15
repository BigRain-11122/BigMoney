# -*- coding: utf-8 -*-
# r1043 bm-c: W249 PRE-FINALIZE six-gate receipt (standing law since W217 debt;
# clone lineage _r1036bmc_w248_sixgate.py W248 pattern). Burn landed by resident
# engine auto-ignite after r1042 splice (12/12 shards self-committed 2d0b41383
# + f528ab7ab + dfbb4afa2 via dead-window absorb); finalize not yet run.
# Gates: 1 splice integrity sha16 x2 + 2 wave-row faces==freeze receipt bands
# + 3 banned ADMIT + 4 pf selftest + 5 n1 selftest + 6 shards 12/12
# + seed_admit FREE-verbatim + prior-wave boundary kept.
import hashlib
import io
import json
import os
import re
import subprocess
import sys


def sha16(p):
    return hashlib.sha256(io.open(p, 'rb').read()).hexdigest()[:16]


fr = json.load(io.open('results/_w249bmc_freeze_receipt.json', encoding='utf-8'))
pf_now = sha16('scripts/perpetual_faces.py')
n1_now = sha16('scripts/perpetual_faces_n1.py')

n1t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = n1t.find('249: {"batch": "PERPETUAL-N1-W249"')
assert i >= 0, 'W249 wave row missing'
seg = n1t[i:i + 9000]
if '250: {' in seg:
    seg = seg[:seg.find('250: {')]
row_faces = {
    'a_seed_base_563501': '563501' in seg,
    'b_exit_seed_base_544901': '544901' in seg,
    'shard_subdir_n1_w249': 'n1_w249' in seg,
    'out_name_n1_w249_results': 'n1_w249_results.json' in seg,
    'engine_owner_bm_c': 'engine_owner": "bm-c"' in seg,
}
f1 = 'seed_admit_gate rc0 base=563501 span=2000 checked=2000 verdict=FREE'
f2 = 'seed_admit_gate rc0 base=544901 span=200 checked=200 verdict=FREE'
fam = {f1: n1t.count(f1), f2: n1t.count(f2)}
m248 = re.search(r'248: \{"batch": "PERPETUAL-N1-W248"', n1t)
w248_seg = n1t[m248.start():m248.start() + 8000] if m248 else ''
if '249: {' in w248_seg:
    w248_seg = w248_seg[:w248_seg.find('249: {')]
boundary = bool(m248) and '561501' in w248_seg and '544701' in w248_seg

sd = 'results/p2cal_ext/n1_w249'
shards = sorted(f for f in os.listdir(sd) if f.startswith('shard-') and f.endswith('.json'))
sizes_ok = all(os.path.getsize(os.path.join(sd, f)) > 100000 for f in shards)

r_banned = subprocess.run([sys.executable, 'Tools/banned_direction_gate.py',
                           '--prereg', 'research/PERPETUAL_N1_W249_PREREG.md'],
                          capture_output=True, text=True)
r_pf = subprocess.run([sys.executable, 'scripts/perpetual_faces.py', 'selftest'],
                      capture_output=True, text=True)
r_n1 = subprocess.run([sys.executable, 'scripts/perpetual_faces_n1.py', 'selftest'],
                      capture_output=True, text=True)

out = {
 "machine": "bm-c",
 "wave": 249,
 "phase": "PRE-FINALIZE six-gate (r1043 bm-c absorb window; standing law -- engine self-burn 12/12 landed post-r1042 splice, finalize not yet run)",
 "gates": {
  "splice_integrity": {
   "bands_facts_match_freeze_receipt": all(row_faces.values()),
   "pf_sha16_now": pf_now, "n1_sha16_now": n1_now,
   "pf_sha16_freeze_post": fr['pf_sha16_post'],
   "n1_sha16_freeze_post": fr['n1_sha16_post'],
   "family_seed_faces": fam,
   "prior_wave_248_boundary_kept": boundary,
  },
  "banned": {"rc": r_banned.returncode, "stdout_tail": (r_banned.stdout or '').strip()[-200:]},
  "pf_selftest": {"rc": r_pf.returncode, "stdout_tail": (r_pf.stdout or '').strip()[-120:]},
  "n1_selftest": {"rc": r_n1.returncode, "stdout_tail": (r_n1.stdout or '').strip()[-120:]},
  "shards": {"present": len(shards), "of": 12, "sizes_above_100k": sizes_ok,
             "files": shards},
  "seed_admit": {
   "freeze_gate_lines": fr.get('seed_admit_gate'),
   "note": "freeze-time FREE evidence consumed verbatim from _w249bmc_freeze_receipt.json; post-registration self-collision BLOCKED would be the fresh-run positive (W237.. pattern)",
  },
  "wave_configs_row": {
   "present": True, "engine_owner": "bm-c",
   "a_seed_base": 563501, "b_exit_seed_base": 544901,
   "shard_subdir": "n1_w249", "out_name": "n1_w249_results.json",
   "seed_bases_match_freeze_bands": fr['bands']['A'] == [563501, 565500] and fr['bands']['B'] == [544901, 545100],
   "row_faces_detail": row_faces,
  },
 },
 "ledger_pre": {
  "prev_total": 969935, "prev_merged_n": 543520,
  "expect_total": 972135, "expect_merged": 545720,
  "anchor": "W248 finalize (bm-c r1036 absorb one-pass, 969,935/K=543,520) per freeze receipt w248_upstream face",
 },
}

ok = (all(row_faces.values()) and all(v >= 1 for v in fam.values()) and boundary
      and pf_now == fr['pf_sha16_post'] and n1_now == fr['n1_sha16_post']
      and len(shards) == 12 and sizes_ok
      and r_banned.returncode == 0 and r_pf.returncode == 0 and r_n1.returncode == 0)
out['verdict'] = 'ALL PASS' if ok else 'FAIL'
io.open('results/_r1043bmc_w249_sixgate.json', 'w', encoding='utf-8').write(
    json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps({'verdict': out['verdict'], 'row_faces': row_faces, 'fam': fam,
                  'boundary': boundary, 'shards': len(shards), 'pf': pf_now, 'n1': n1_now,
                  'banned_rc': r_banned.returncode, 'pf_rc': r_pf.returncode,
                  'n1_rc': r_n1.returncode}, indent=1))
raise SystemExit(0 if ok else 1)
