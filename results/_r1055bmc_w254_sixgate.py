# -*- coding: utf-8 -*-
# r1055 bm-c: W254 PRE-FINALIZE six-gate receipt (standing law since W217 debt;
# clone lineage _r1053bmc_w253_sixgate.py W253 pattern). Burn landed by resident
# engine auto-ignite post-W254 splice 3eb691575 (ledger appends c211d1269 +
# fa2bc55e5 self-committed 12/12, shard files only); finalize not yet run.
# Splice commit 3eb691575 = healed worktree bytes directly (4 authoring defect
# classes caught PRE-splice per commit msg) -> worktree == receipt post == landed
# blob triple-identity expected for BOTH pf and n1 faces.
import hashlib
import io
import json
import os
import re
import subprocess
import sys


def sha16(p):
    return hashlib.sha256(io.open(p, 'rb').read()).hexdigest()[:16]


fr = json.load(io.open('results/_w254bmc_freeze_receipt.json', encoding='utf-8'))
pf_now = sha16('scripts/perpetual_faces.py')
n1_now = sha16('scripts/perpetual_faces_n1.py')

n1t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = n1t.find('254: {"batch": "PERPETUAL-N1-W254"')
assert i >= 0, 'W254 wave row missing'
seg = n1t[i:i + 9000]
if '255: {' in seg:
    seg = seg[:seg.find('255: {')]
row_faces = {
    'a_seed_base_574101': '574101' in seg,
    'b_exit_seed_base_576101': '576101' in seg,
    'shard_subdir_n1_w254': 'n1_w254' in seg,
    'out_name_n1_w254_results': 'n1_w254_results.json' in seg,
    'engine_owner_bm_c': 'engine_owner": "bm-c"' in seg,
}
f1 = 'base=574101 span=2000'
f2 = 'base=576101 span=200'
fam = {f1: n1t.count(f1), f2: n1t.count(f2)}
m253 = re.search(r'253: \{"batch": "PERPETUAL-N1-W253"', n1t)
w253_seg = n1t[m253.start():m253.start() + 8000] if m253 else ''
if '254: {' in w253_seg:
    w253_seg = w253_seg[:w253_seg.find('254: {')]
boundary = bool(m253) and '571901' in w253_seg and '573901' in w253_seg

sd = 'results/p2cal_ext/n1_w254'
shards = sorted(f for f in os.listdir(sd) if f.startswith('shard-') and f.endswith('.json'))
sizes_ok = all(os.path.getsize(os.path.join(sd, f)) > 100000 for f in shards)

r_banned = subprocess.run([sys.executable, 'Tools/banned_direction_gate.py',
                           '--prereg', 'research/PERPETUAL_N1_W254_PREREG.md'],
                          capture_output=True, text=True)
r_pf = subprocess.run([sys.executable, 'scripts/perpetual_faces.py', 'selftest'],
                      capture_output=True, text=True)
r_n1 = subprocess.run([sys.executable, 'scripts/perpetual_faces_n1.py', 'selftest'],
                      capture_output=True, text=True)
r_git = subprocess.run(['git', 'show', '3eb691575:scripts/perpetual_faces_n1.py'],
                       capture_output=True)
n1_landed = hashlib.sha256(r_git.stdout).hexdigest()[:16]
r_git_pf = subprocess.run(['git', 'diff', '3eb691575', '--', 'scripts/perpetual_faces.py'],
                         capture_output=True, text=True)
pf_diff_empty = (len((r_git_pf.stdout or '').strip()) == 0
                 and r_git_pf.returncode == 0)
n1_vs_receipt_note = (
    'r1055 window: splice commit 3eb691575 = healed worktree bytes directly (4 '
    'authoring defect classes caught PRE-splice per commit msg) -> gate-1 asserts '
    'TRIPLE identity worktree == receipt n1_sha16_post == landed git blob; engine '
    'self-burn commits c211d1269+fa2bc55e5 touched shard files only'
)
w253_finalize_present = os.path.exists('results/perpetual_faces/n1_w253_results.json')
out = {
 "machine": "bm-c",
 "wave": 254,
 "phase": "PRE-FINALIZE six-gate (r1055 bm-c absorb window; standing law -- engine self-burn 12/12 landed post-W254 splice 3eb691575 via ledger appends c211d1269+fa2bc55e5, finalize not yet run)",
 "gates": {
  "splice_integrity": {
   "bands_facts_match_freeze_receipt": all(row_faces.values()),
   "pf_sha16_now": pf_now, "n1_sha16_now": n1_now,
   "pf_sha16_freeze_post": fr['pf_sha16_post'],
   "n1_sha16_freeze_post": fr['n1_sha16_post'],
   "n1_sha16_landed_commit": n1_landed,
   "pf_landed_diff_empty": pf_diff_empty,
   "n1_vs_receipt_disclosure": n1_vs_receipt_note,
   "family_seed_faces": fam,
   "prior_wave_253_boundary_kept": boundary,
  },
  "banned": {"rc": r_banned.returncode, "stdout_tail": (r_banned.stdout or '').strip()[-200:]},
  "pf_selftest": {"rc": r_pf.returncode, "stdout_tail": (r_pf.stdout or '').strip()[-120:]},
  "n1_selftest": {"rc": r_n1.returncode, "stdout_tail": (r_n1.stdout or '').strip()[-120:]},
  "shards": {"present": len(shards), "of": 12, "sizes_above_100k": sizes_ok,
             "files": shards},
  "seed_admit": {
   "freeze_gate_lines": fr.get('seed_admit_gate'),
   "note": "freeze-time FREE evidence consumed verbatim from _w254bmc_freeze_receipt.json (both bands); whole-file per-span family faces count-asserted",
  },
  "wave_configs_row": {
   "present": True, "engine_owner": "bm-c",
   "a_seed_base": 574101, "b_exit_seed_base": 576101,
   "shard_subdir": "n1_w254", "out_name": "n1_w254_results.json",
   "seed_bases_match_freeze_bands": fr['bands']['A'] == [574101, 576100] and fr['bands']['B'] == [576101, 576300],
   "row_faces_detail": row_faces,
  },
  "w253_finalize_product_present": w253_finalize_present,
 },
 "ledger_pre": {
  "prev_total": 980935, "prev_merged_n": 554520,
  "expect_total": 983135, "expect_merged": 556720,
  "anchor": "W253 finalize (dead r1053 window one-pass 980,935/K=554,520, estate machine-verified by r1053 absorb) per freeze receipt w253_upstream face",
 },
}

ok = (all(row_faces.values()) and all(v >= 1 for v in fam.values()) and boundary
      and w253_finalize_present
      and pf_now == fr['pf_sha16_post'] and pf_diff_empty
      and n1_now == n1_landed
      and n1_now == fr['n1_sha16_post']
      and len(shards) == 12 and sizes_ok
      and r_banned.returncode == 0 and r_pf.returncode == 0 and r_n1.returncode == 0)
out['verdict'] = 'ALL PASS' if ok else 'FAIL'
io.open('results/_r1055bmc_w254_sixgate.json', 'w', encoding='utf-8').write(
    json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps({'verdict': out['verdict'], 'row_faces': row_faces, 'fam': fam,
                  'boundary': boundary, 'shards': len(shards), 'pf': pf_now, 'n1': n1_now,
                  'n1_landed': n1_landed, 'receipt_post': fr['n1_sha16_post'],
                  'w253_finalize_present': w253_finalize_present,
                  'banned_rc': r_banned.returncode, 'pf_rc': r_pf.returncode,
                  'n1_rc': r_n1.returncode}, indent=1))
raise SystemExit(0 if ok else 1)
