# -*- coding: utf-8 -*-
# r1057 bm-c: W255 PRE-FINALIZE six-gate receipt (standing law since W217 debt;
# clone lineage _r1055bmc_w254_sixgate.py W254 pattern). Burn landed by resident
# engine auto-ignite post-W255 splice e166afc6c (ledger appends b1414b81a +
# f931cf102 self-committed 12/12, shard files only); finalize not yet run.
# Splice commit e166afc6c = worktree bytes directly (2 disclosed needle heals +
# 2 blanket-duplication sub heals caught PRE-splice per commit msg) -> worktree ==
# receipt post == landed blob triple-identity expected for BOTH pf and n1 faces.
# This window = 48th-gen absorb continuation (dead r1057 window landed the splice
# + engine self-burned; this session runs sixgate->finalize->fivekeys->sec78->W256 seat).
import hashlib
import io
import json
import os
import re
import subprocess
import sys


def sha16(p):
    return hashlib.sha256(io.open(p, 'rb').read()).hexdigest()[:16]


fr = json.load(io.open('results/_w255bmc_freeze_receipt.json', encoding='utf-8'))
pf_now = sha16('scripts/perpetual_faces.py')
n1_now = sha16('scripts/perpetual_faces_n1.py')

n1t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = n1t.find('255: {"batch": "PERPETUAL-N1-W255"')
assert i >= 0, 'W255 wave row missing'
seg = n1t[i:i + 9000]
if '256: {' in seg:
    seg = seg[:seg.find('256: {')]
row_faces = {
    'a_seed_base_576301': '576301' in seg,
    'b_exit_seed_base_578301': '578301' in seg,
    'shard_subdir_n1_w255': 'n1_w255' in seg,
    'out_name_n1_w255_results': 'n1_w255_results.json' in seg,
    'engine_owner_bm_c': 'engine_owner": "bm-c"' in seg,
}
f1 = 'base=576301 span=2000'
f2 = 'base=578301 span=200'
fam = {f1: n1t.count(f1), f2: n1t.count(f2)}
m254 = re.search(r'254: \{"batch": "PERPETUAL-N1-W254"', n1t)
w254_seg = n1t[m254.start():m254.start() + 8000] if m254 else ''
if '255: {' in w254_seg:
    w254_seg = w254_seg[:w254_seg.find('255: {')]
boundary = bool(m254) and '574101' in w254_seg and '576101' in w254_seg

sd = 'results/p2cal_ext/n1_w255'
shards = sorted(f for f in os.listdir(sd) if f.startswith('shard-') and f.endswith('.json'))
sizes_ok = all(os.path.getsize(os.path.join(sd, f)) > 100000 for f in shards)

r_banned = subprocess.run([sys.executable, 'Tools/banned_direction_gate.py',
                           '--prereg', 'research/PERPETUAL_N1_W255_PREREG.md'],
                          capture_output=True, text=True)
r_pf = subprocess.run([sys.executable, 'scripts/perpetual_faces.py', 'selftest'],
                      capture_output=True, text=True)
r_n1 = subprocess.run([sys.executable, 'scripts/perpetual_faces_n1.py', 'selftest'],
                      capture_output=True, text=True)
r_git = subprocess.run(['git', 'show', 'e166afc6c:scripts/perpetual_faces_n1.py'],
                       capture_output=True)
n1_landed = hashlib.sha256(r_git.stdout).hexdigest()[:16]
r_git_pf = subprocess.run(['git', 'diff', 'e166afc6c', '--', 'scripts/perpetual_faces.py'],
                         capture_output=True, text=True)
pf_diff_empty = (len((r_git_pf.stdout or '').strip()) == 0
                 and r_git_pf.returncode == 0)
n1_vs_receipt_note = (
    'r1057 window: splice commit e166afc6c = healed worktree bytes directly (2 '
    'needle heals + 2 blanket-duplication sub heals caught PRE-splice per commit '
    'msg) -> gate-1 asserts TRIPLE identity worktree == receipt n1_sha16_post == '
    'landed git blob; engine self-burn commits b1414b81a+f931cf102 touched shard '
    'files only'
)
w254_finalize_present = os.path.exists('results/perpetual_faces/n1_w254_results.json')
out = {
 "machine": "bm-c",
 "wave": 255,
 "phase": "PRE-FINALIZE six-gate (r1057 bm-c 48th-gen absorb continuation window; standing law -- engine self-burn 12/12 landed post-W255 splice e166afc6c via ledger appends b1414b81a+f931cf102, finalize not yet run)",
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
   "prior_wave_254_boundary_kept": boundary,
  },
  "banned": {"rc": r_banned.returncode, "stdout_tail": (r_banned.stdout or '').strip()[-200:]},
  "pf_selftest": {"rc": r_pf.returncode, "stdout_tail": (r_pf.stdout or '').strip()[-120:]},
  "n1_selftest": {"rc": r_n1.returncode, "stdout_tail": (r_n1.stdout or '').strip()[-120:]},
  "shards": {"present": len(shards), "of": 12, "sizes_above_100k": sizes_ok,
             "files": shards},
  "seed_admit": {
   "freeze_gate_lines": fr.get('seed_admit_gate'),
   "note": "freeze-time FREE evidence consumed verbatim from _w255bmc_freeze_receipt.json (both bands); whole-file per-span family faces count-asserted",
  },
  "wave_configs_row": {
   "present": True, "engine_owner": "bm-c",
   "a_seed_base": 576301, "b_exit_seed_base": 578301,
   "shard_subdir": "n1_w255", "out_name": "n1_w255_results.json",
   "seed_bases_match_freeze_bands": fr['bands']['A'] == [576301, 578300] and fr['bands']['B'] == [578301, 578500],
   "row_faces_detail": row_faces,
  },
  "w254_finalize_product_present": w254_finalize_present,
 },
 "ledger_pre": {
  "prev_total": 983135, "prev_merged_n": 556720,
  "expect_total": 985335, "expect_merged": 558920,
  "anchor": "W254 finalize (r1055 absorb-continuation one-pass 983,135/K=556,720, estate machine-verified by r1055 absorb) per freeze receipt w254_upstream face",
 },
}

ok = (all(row_faces.values()) and all(v >= 1 for v in fam.values()) and boundary
      and w254_finalize_present
      and pf_now == fr['pf_sha16_post'] and pf_diff_empty
      and n1_now == n1_landed
      and n1_now == fr['n1_sha16_post']
      and len(shards) == 12 and sizes_ok
      and r_banned.returncode == 0 and r_pf.returncode == 0 and r_n1.returncode == 0)
out['verdict'] = 'ALL PASS' if ok else 'FAIL'
io.open('results/_r1057bmc_w255_sixgate.json', 'w', encoding='utf-8').write(
    json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps({'verdict': out['verdict'], 'row_faces': row_faces, 'fam': fam,
                  'boundary': boundary, 'shards': len(shards), 'pf': pf_now, 'n1': n1_now,
                  'n1_landed': n1_landed, 'receipt_post': fr['n1_sha16_post'],
                  'w254_finalize_present': w254_finalize_present,
                  'banned_rc': r_banned.returncode, 'pf_rc': r_pf.returncode,
                  'n1_rc': r_n1.returncode}, indent=1))
raise SystemExit(0 if ok else 1)
