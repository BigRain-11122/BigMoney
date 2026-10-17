# -*- coding: utf-8 -*-
# r1064 bm-c: W259 PRE-FINALIZE six-gate receipt (standing law since W217 debt;
# clone lineage _r1062bmc_w258_sixgate.py W258 pattern). Burn landed by resident
# engine auto-ignite post-W259 splice 89aeea31b (batched ledger appends
# self-committed 12/12, shard files only); finalize not yet run.
# Splice commit 89aeea31b = worktree bytes directly (zero post-splice heal --
# worktree == receipt post == landed blob triple-identity expected for BOTH pf
# and n1 faces; verified live this window pre-sixgate).
# This window = r1064 clean continuation (dead-r1063 pre-built editor + this
# window 4 disclosed gate-list needle heals [w244_a frozen-verbatim / r1064
# freeze-window stamp / 248th anti-gate / 247-129-77 anti-gate] + splice +
# engine self-burn 12/12; this session runs sixgate->finalize->fivekeys->
# sec78->W260 seat->S6->closeout).
import hashlib
import io
import json
import os
import re
import subprocess
import sys


def sha16(p):
    return hashlib.sha256(io.open(p, 'rb').read()).hexdigest()[:16]


fr = json.load(io.open('results/_w259bmc_freeze_receipt.json', encoding='utf-8'))
pf_now = sha16('scripts/perpetual_faces.py')
n1_now = sha16('scripts/perpetual_faces_n1.py')

n1t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = n1t.find('259: {"batch": "PERPETUAL-N1-W259"')
assert i >= 0, 'W259 wave row missing'
seg = n1t[i:i + 9000]
if '260: {' in seg:
    seg = seg[:seg.find('260: {')]
row_faces = {
    'a_seed_base_585101': '585101' in seg,
    'b_exit_seed_base_587101': '587101' in seg,
    'shard_subdir_n1_w259': 'n1_w259' in seg,
    'out_name_n1_w259_results': 'n1_w259_results.json' in seg,
    'engine_owner_bm_c': 'engine_owner": "bm-c"' in seg,
}
f1 = 'base=585101 span=2000'
f2 = 'base=587101 span=200'
fam = {f1: n1t.count(f1), f2: n1t.count(f2)}
m258 = re.search(r'258: \{"batch": "PERPETUAL-N1-W258"', n1t)
w258_seg = n1t[m258.start():m258.start() + 8000] if m258 else ''
if '259: {' in w258_seg:
    w258_seg = w258_seg[:w258_seg.find('259: {')]
boundary = bool(m258) and '582901' in w258_seg and '584901' in w258_seg

sd = 'results/p2cal_ext/n1_w259'
shards = sorted(f for f in os.listdir(sd) if f.startswith('shard-') and f.endswith('.json'))
sizes_ok = all(os.path.getsize(os.path.join(sd, f)) > 100000 for f in shards)

r_banned = subprocess.run([sys.executable, 'Tools/banned_direction_gate.py',
                           '--prereg', 'research/PERPETUAL_N1_W259_PREREG.md'],
                          capture_output=True, text=True)
r_pf = subprocess.run([sys.executable, 'scripts/perpetual_faces.py', 'selftest'],
                      capture_output=True, text=True)
r_n1 = subprocess.run([sys.executable, 'scripts/perpetual_faces_n1.py', 'selftest'],
                      capture_output=True, text=True)
r_git = subprocess.run(['git', 'show', '89aeea31b:scripts/perpetual_faces_n1.py'],
                       capture_output=True)
n1_landed = hashlib.sha256(r_git.stdout).hexdigest()[:16]
r_git_pf = subprocess.run(['git', 'diff', '89aeea31b', '--', 'scripts/perpetual_faces.py'],
                          capture_output=True, text=True)
pf_diff_empty = (len((r_git_pf.stdout or '').strip()) == 0
                 and r_git_pf.returncode == 0)
n1_vs_receipt_note = (
    'r1064 window: splice commit 89aeea31b = worktree bytes directly (zero '
    'post-splice heal) -> gate-1 asserts TRIPLE identity worktree == receipt '
    'n1_sha16_post == landed git blob; engine self-burn commits touch shard '
    'files only'
)
w258_finalize_present = os.path.exists('results/perpetual_faces/n1_w258_results.json')
out = {
 "machine": "bm-c",
 "wave": 259,
 "phase": "PRE-FINALIZE six-gate (r1064 bm-c clean continuation window; standing law -- engine self-burn 12/12 landed post-W259 splice 89aeea31b via batched ledger appends, finalize not yet run)",
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
   "prior_wave_258_boundary_kept": boundary,
  },
  "banned": {"rc": r_banned.returncode, "stdout_tail": (r_banned.stdout or '').strip()[-200:]},
  "pf_selftest": {"rc": r_pf.returncode, "stdout_tail": (r_pf.stdout or '').strip()[-120:]},
  "n1_selftest": {"rc": r_n1.returncode, "stdout_tail": (r_n1.stdout or '').strip()[-120:]},
  "shards": {"present": len(shards), "of": 12, "sizes_above_100k": sizes_ok,
             "files": shards},
  "seed_admit": {
   "freeze_gate_lines": fr.get('seed_admit_gate'),
   "note": "freeze-time FREE evidence consumed verbatim from _w259bmc_freeze_receipt.json (both bands); whole-file per-span family faces count-asserted",
  },
  "wave_configs_row": {
   "present": True, "engine_owner": "bm-c",
   "a_seed_base": 585101, "b_exit_seed_base": 587101,
   "shard_subdir": "n1_w259", "out_name": "n1_w259_results.json",
   "seed_bases_match_freeze_bands": fr['bands']['A'] == [585101, 587100] and fr['bands']['B'] == [587101, 587300],
   "row_faces_detail": row_faces,
  },
  "w258_finalize_product_present": w258_finalize_present,
 },
 "ledger_pre": {
  "prev_total": 991935, "prev_merged_n": 565520,
  "expect_total": 994135, "expect_merged": 567720,
  "anchor": "W258 finalize (r1062 52nd-gen absorb-continuation one-pass 991,935/K=565,520) per freeze receipt w258_upstream face",
 },
}

ok = (all(row_faces.values()) and all(v >= 1 for v in fam.values()) and boundary
      and w258_finalize_present
      and pf_now == fr['pf_sha16_post'] and pf_diff_empty
      and n1_now == n1_landed
      and n1_now == fr['n1_sha16_post']
      and len(shards) == 12 and sizes_ok
      and r_banned.returncode == 0 and r_pf.returncode == 0 and r_n1.returncode == 0)
out['verdict'] = 'ALL PASS' if ok else 'FAIL'
io.open('results/_r1064bmc_w259_sixgate.json', 'w', encoding='utf-8').write(
    json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps({'verdict': out['verdict'], 'row_faces': row_faces, 'fam': fam,
                  'boundary': boundary, 'shards': len(shards), 'pf': pf_now, 'n1': n1_now,
                  'n1_landed': n1_landed, 'receipt_post': fr['n1_sha16_post'],
                  'w258_finalize_present': w258_finalize_present,
                  'banned_rc': r_banned.returncode, 'pf_rc': r_pf.returncode,
                  'n1_rc': r_n1.returncode}, indent=1))
raise SystemExit(0 if ok else 1)
