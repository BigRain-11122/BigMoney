# -*- coding: utf-8 -*-
# r1065 bm-c: W260 PRE-FINALIZE six-gate receipt (standing law since W217 debt;
# clone lineage _r1064bmc_w259_sixgate.py W259 pattern). Burn landed by resident
# engine auto-ignite post-W260 splice e8a9d5d67 (batched ledger appends
# self-committed 12/12, shard files only); finalize not yet run.
# Splice commit e8a9d5d67 = worktree bytes directly (zero post-splice heal --
# worktree == receipt post == landed blob triple-identity expected for BOTH pf
# and n1 faces; verified live this window pre-sixgate).
# This window = r1065 55th-gen absorb continuation (dead-r1065 windows: prereg
# frozen 0f33f9abc + editor pre-built; this window 1 disclosed OUTPUT-GATE
# needle heal [w244_a frozen-verbatim -- builder wrongly rolled +1 AGAIN,
# r1064 same-defect precedent] + splice e8a9d5d67 + engine self-burn 12/12;
# this session runs sixgate->finalize->fivekeys->sec78->W261 seat->S6
# (absorbed dead-window 43/43 10:41)->closeout).
import hashlib
import io
import json
import os
import re
import subprocess
import sys


def sha16(p):
    return hashlib.sha256(io.open(p, 'rb').read()).hexdigest()[:16]


fr = json.load(io.open('results/_w260bmc_freeze_receipt.json', encoding='utf-8'))
pf_now = sha16('scripts/perpetual_faces.py')
n1_now = sha16('scripts/perpetual_faces_n1.py')

n1t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = n1t.find('260: {"batch": "PERPETUAL-N1-W260"')
assert i >= 0, 'W260 wave row missing'
seg = n1t[i:i + 9000]
if '261: {' in seg:
    seg = seg[:seg.find('261: {')]
row_faces = {
    'a_seed_base_587301': '587301' in seg,
    'b_exit_seed_base_589301': '589301' in seg,
    'shard_subdir_n1_w260': 'n1_w260' in seg,
    'out_name_n1_w260_results': 'n1_w260_results.json' in seg,
    'engine_owner_bm_c': 'engine_owner": "bm-c"' in seg,
}
f1 = 'base=587301 span=2000'
f2 = 'base=589301 span=200'
fam = {f1: n1t.count(f1), f2: n1t.count(f2)}
m259 = re.search(r'259: \{"batch": "PERPETUAL-N1-W259"', n1t)
w259_seg = n1t[m259.start():m259.start() + 8000] if m259 else ''
if '260: {' in w259_seg:
    w259_seg = w259_seg[:w259_seg.find('260: {')]
boundary = bool(m259) and '585101' in w259_seg and '587101' in w259_seg

sd = 'results/p2cal_ext/n1_w260'
shards = sorted(f for f in os.listdir(sd) if f.startswith('shard-') and f.endswith('.json'))
sizes_ok = all(os.path.getsize(os.path.join(sd, f)) > 100000 for f in shards)

r_banned = subprocess.run([sys.executable, 'Tools/banned_direction_gate.py',
                           '--prereg', 'research/PERPETUAL_N1_W260_PREREG.md'],
                          capture_output=True, text=True)
r_pf = subprocess.run([sys.executable, 'scripts/perpetual_faces.py', 'selftest'],
                      capture_output=True, text=True)
r_n1 = subprocess.run([sys.executable, 'scripts/perpetual_faces_n1.py', 'selftest'],
                      capture_output=True, text=True)
r_git = subprocess.run(['git', 'show', 'e8a9d5d67:scripts/perpetual_faces_n1.py'],
                       capture_output=True)
n1_landed = hashlib.sha256(r_git.stdout).hexdigest()[:16]
r_git_pf = subprocess.run(['git', 'diff', 'e8a9d5d67', '--', 'scripts/perpetual_faces.py'],
                          capture_output=True, text=True)
pf_diff_empty = (len((r_git_pf.stdout or '').strip()) == 0
                 and r_git_pf.returncode == 0)
n1_vs_receipt_note = (
    'r1065 window: splice commit e8a9d5d67 = worktree bytes directly (zero '
    'post-splice heal) -> gate-1 asserts TRIPLE identity worktree == receipt '
    'n1_sha16_post == landed git blob; engine self-burn commits touch shard '
    'files only'
)
w259_finalize_present = os.path.exists('results/perpetual_faces/n1_w259_results.json')
out = {
 "machine": "bm-c",
 "wave": 260,
 "phase": "PRE-FINALIZE six-gate (r1065 bm-c 55th-gen absorb-continuation window; standing law -- engine self-burn 12/12 landed post-W260 splice e8a9d5d67 via batched ledger appends, finalize not yet run)",
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
   "prior_wave_259_boundary_kept": boundary,
  },
  "banned": {"rc": r_banned.returncode, "stdout_tail": (r_banned.stdout or '').strip()[-200:]},
  "pf_selftest": {"rc": r_pf.returncode, "stdout_tail": (r_pf.stdout or '').strip()[-120:]},
  "n1_selftest": {"rc": r_n1.returncode, "stdout_tail": (r_n1.stdout or '').strip()[-120:]},
  "shards": {"present": len(shards), "of": 12, "sizes_above_100k": sizes_ok,
             "files": shards},
  "seed_admit": {
   "freeze_gate_lines": fr.get('seed_admit_gate'),
   "note": "freeze-time FREE evidence consumed verbatim from _w260bmc_freeze_receipt.json (both bands); whole-file per-span family faces count-asserted",
  },
  "wave_configs_row": {
   "present": True, "engine_owner": "bm-c",
   "a_seed_base": 587301, "b_exit_seed_base": 589301,
   "shard_subdir": "n1_w260", "out_name": "n1_w260_results.json",
   "seed_bases_match_freeze_bands": fr['bands']['A'] == [587301, 589300] and fr['bands']['B'] == [589301, 589500],
   "row_faces_detail": row_faces,
  },
  "w259_finalize_product_present": w259_finalize_present,
 },
 "ledger_pre": {
  "prev_total": 994135, "prev_merged_n": 567720,
  "expect_total": 996335, "expect_merged": 569920,
  "anchor": "W259 finalize (r1064 54th-gen absorb-continuation one-pass 994,135/K=567,720) per freeze receipt w259_upstream face",
 },
}

ok = (all(row_faces.values()) and all(v >= 1 for v in fam.values()) and boundary
      and w259_finalize_present
      and pf_now == fr['pf_sha16_post'] and pf_diff_empty
      and n1_now == n1_landed
      and n1_now == fr['n1_sha16_post']
      and len(shards) == 12 and sizes_ok
      and r_banned.returncode == 0 and r_pf.returncode == 0 and r_n1.returncode == 0)
out['verdict'] = 'ALL PASS' if ok else 'FAIL'
io.open('results/_r1065bmc_w260_sixgate.json', 'w', encoding='utf-8').write(
    json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps({'verdict': out['verdict'], 'row_faces': row_faces, 'fam': fam,
                  'boundary': boundary, 'shards': len(shards), 'pf': pf_now, 'n1': n1_now,
                  'n1_landed': n1_landed, 'receipt_post': fr['n1_sha16_post'],
                  'w259_finalize_present': w259_finalize_present,
                  'banned_rc': r_banned.returncode, 'pf_rc': r_pf.returncode,
                  'n1_rc': r_n1.returncode}, indent=1))
raise SystemExit(0 if ok else 1)
