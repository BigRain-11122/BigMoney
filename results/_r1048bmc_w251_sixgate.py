# -*- coding: utf-8 -*-
# r1048 bm-c: W251 PRE-FINALIZE six-gate receipt (standing law since W217 debt;
# clone lineage _r1046bmc_w250_sixgate.py W250 pattern). Burn in flight by
# resident engine auto-ignite post-r1048 splice c813471cd (ledger appends
# self-commit); finalize not yet run. Gates: 1 splice integrity sha16 x2 + 2
# wave-row faces ==freeze receipt bands + 3 banned ADMIT + 4 pf selftest
# + 5 n1 selftest + 6 shards 12/12 + seed_admit FREE-verbatim + prior-wave
# boundary kept. r1048 window = ZERO post-splice heal (splice committed
# directly) -> worktree == receipt post == landed blob triple-identity.
import hashlib
import io
import json
import os
import re
import subprocess
import sys


def sha16(p):
    return hashlib.sha256(io.open(p, 'rb').read()).hexdigest()[:16]


fr = json.load(io.open('results/_w251bmc_freeze_receipt.json', encoding='utf-8'))
pf_now = sha16('scripts/perpetual_faces.py')
n1_now = sha16('scripts/perpetual_faces_n1.py')

n1t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = n1t.find('251: {"batch": "PERPETUAL-N1-W251"')
assert i >= 0, 'W251 wave row missing'
seg = n1t[i:i + 9000]
if '252: {' in seg:
    seg = seg[:seg.find('252: {')]
row_faces = {
    'a_seed_base_567501': '567501' in seg,
    'b_exit_seed_base_569501': '569501' in seg,
    'shard_subdir_n1_w251': 'n1_w251' in seg,
    'out_name_n1_w251_results': 'n1_w251_results.json' in seg,
    'engine_owner_bm_c': 'engine_owner": "bm-c"' in seg,
}
f1 = 'seed_admit_gate rc0 base=567501 span=2000 checked=2000 verdict=FREE'
f2 = 'seed_admit_gate rc0 base=569501 span=200 checked=200 verdict=FREE'
fam = {f1: n1t.count(f1), f2: n1t.count(f2)}
m250 = re.search(r'250: \{"batch": "PERPETUAL-N1-W250"', n1t)
w250_seg = n1t[m250.start():m250.start() + 8000] if m250 else ''
if '251: {' in w250_seg:
    w250_seg = w250_seg[:w250_seg.find('251: {')]
boundary = bool(m250) and '565501' in w250_seg and '545101' in w250_seg

sd = 'results/p2cal_ext/n1_w251'
shards = sorted(f for f in os.listdir(sd) if f.startswith('shard-') and f.endswith('.json'))
sizes_ok = all(os.path.getsize(os.path.join(sd, f)) > 100000 for f in shards)

r_banned = subprocess.run([sys.executable, 'Tools/banned_direction_gate.py',
                           '--prereg', 'research/PERPETUAL_N1_W251_PREREG.md'],
                          capture_output=True, text=True)
r_pf = subprocess.run([sys.executable, 'scripts/perpetual_faces.py', 'selftest'],
                      capture_output=True, text=True)
r_n1 = subprocess.run([sys.executable, 'scripts/perpetual_faces_n1.py', 'selftest'],
                      capture_output=True, text=True)
r_git = subprocess.run(['git', 'show', 'c813471cd:scripts/perpetual_faces_n1.py'],
                       capture_output=True)
n1_landed = hashlib.sha256(r_git.stdout).hexdigest()[:16]
n1_vs_receipt_note = (
    'r1048 window: ZERO post-splice heal (splice commit c813471cd = the worktree bytes '
    'directly) -> gate-1 asserts the TRIPLE identity worktree == receipt n1_sha16_post '
    '== landed git blob (no E70 re-anchor needed this wave)')
out = {
 "machine": "bm-c",
 "wave": 251,
 "phase": "PRE-FINALIZE six-gate (r1048 bm-c window; standing law -- engine self-burn 12/12 landed post-r1048 splice, finalize not yet run)",
 "gates": {
  "splice_integrity": {
   "bands_facts_match_freeze_receipt": all(row_faces.values()),
   "pf_sha16_now": pf_now, "n1_sha16_now": n1_now,
   "pf_sha16_freeze_post": fr['pf_sha16_post'],
   "n1_sha16_freeze_post": fr['n1_sha16_post'],
   "n1_sha16_landed_commit": n1_landed,
   "n1_vs_receipt_disclosure": n1_vs_receipt_note,
   "family_seed_faces": fam,
   "prior_wave_250_boundary_kept": boundary,
  },
  "banned": {"rc": r_banned.returncode, "stdout_tail": (r_banned.stdout or '').strip()[-200:]},
  "pf_selftest": {"rc": r_pf.returncode, "stdout_tail": (r_pf.stdout or '').strip()[-120:]},
  "n1_selftest": {"rc": r_n1.returncode, "stdout_tail": (r_n1.stdout or '').strip()[-120:]},
  "shards": {"present": len(shards), "of": 12, "sizes_above_100k": sizes_ok,
             "files": shards},
  "seed_admit": {
   "freeze_gate_lines": fr.get('seed_admit_gate'),
   "note": "freeze-time FREE evidence consumed verbatim from _w251bmc_freeze_receipt.json; post-registration self-collision BLOCKED would be the fresh-run positive (W237.. pattern)",
  },
  "wave_configs_row": {
   "present": True, "engine_owner": "bm-c",
   "a_seed_base": 567501, "b_exit_seed_base": 569501,
   "shard_subdir": "n1_w251", "out_name": "n1_w251_results.json",
   "seed_bases_match_freeze_bands": fr['bands']['A'] == [567501, 569500] and fr['bands']['B'] == [569501, 569700],
   "row_faces_detail": row_faces,
  },
 },
 "ledger_pre": {
  "prev_total": 974335, "prev_merged_n": 547920,
  "expect_total": 976535, "expect_merged": 550120,
  "anchor": "W250 finalize (bm-c r1046 window one-pass, 974,335/K=547,920) per freeze receipt w250_upstream face",
 },
}

ok = (all(row_faces.values()) and all(v >= 1 for v in fam.values()) and boundary
      and pf_now == fr['pf_sha16_post'] and n1_now == n1_landed
      and n1_now == fr['n1_sha16_post']
      and len(shards) == 12 and sizes_ok
      and r_banned.returncode == 0 and r_pf.returncode == 0 and r_n1.returncode == 0)
out['verdict'] = 'ALL PASS' if ok else 'FAIL'
io.open('results/_r1048bmc_w251_sixgate.json', 'w', encoding='utf-8').write(
    json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps({'verdict': out['verdict'], 'row_faces': row_faces, 'fam': fam,
                  'boundary': boundary, 'shards': len(shards), 'pf': pf_now, 'n1': n1_now,
                  'n1_landed': n1_landed, 'receipt_post': fr['n1_sha16_post'],
                  'banned_rc': r_banned.returncode, 'pf_rc': r_pf.returncode,
                  'n1_rc': r_n1.returncode}, indent=1))
raise SystemExit(0 if ok else 1)
