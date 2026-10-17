# -*- coding: utf-8 -*-
# r1067 bm-c: W261 PRE-FINALIZE six-gate receipt (standing law since W217 debt;
# clone lineage _r1065bmc_w260_sixgate.py W260 pattern, 23rd consecutive
# PRE-FINALIZE correct-phase). Burn landed by resident engine auto-ignite
# post-W261 splice 68aad04b6 (batched ledger appends self-committed 12/12:
# ad2aa9322 6 + b88dc8fcd 5 + shard-7 pending engine next batch tick, shard
# files only); finalize not yet run.
# Splice commit 68aad04b6 = worktree bytes directly (zero post-splice heal --
# worktree == receipt post == landed blob triple-identity expected for BOTH pf
# and n1 faces; verified live this window pre-sixgate).
# This window = r1067 57th-gen absorb continuation (dead-r1067 window: editor
# estate build_editor + derive_editor + needle preflight 149 faces +
# freeze_edits bundle; 1 disclosed comment needle heal [W211..W238 legs (28)
# -> W211..W242 legs (32), W257-editor-era stale inherited face, code asserts
# govern]; splice + engine self-burn 12/12 THIS window; this session runs
# sixgate->finalize->fivekeys->sec78->W262 seat->S6(already in flight)->closeout).
import hashlib
import io
import json
import os
import re
import subprocess
import sys


def sha16(p):
    return hashlib.sha256(io.open(p, 'rb').read()).hexdigest()[:16]


fr = json.load(io.open('results/_w261bmc_freeze_receipt.json', encoding='utf-8'))
pf_now = sha16('scripts/perpetual_faces.py')
n1_now = sha16('scripts/perpetual_faces_n1.py')

n1t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = n1t.find('261: {"batch": "PERPETUAL-N1-W261"')
assert i >= 0, 'W261 wave row missing'
seg = n1t[i:i + 9000]
if '262: {' in seg:
    seg = seg[:seg.find('262: {')]
row_faces = {
    'a_seed_base_589501': '589501' in seg,
    'b_exit_seed_base_591501': '591501' in seg,
    'shard_subdir_n1_w261': 'n1_w261' in seg,
    'out_name_n1_w261_results': 'n1_w261_results.json' in seg,
    'engine_owner_bm_c': 'engine_owner": "bm-c"' in seg,
}
f1 = 'base=589501 span=2000'
f2 = 'base=591501 span=200'
fam = {f1: n1t.count(f1), f2: n1t.count(f2)}
m260 = re.search(r'260: \{"batch": "PERPETUAL-N1-W260"', n1t)
w260_seg = n1t[m260.start():m260.start() + 8000] if m260 else ''
if '261: {' in w260_seg:
    w260_seg = w260_seg[:w260_seg.find('261: {')]
boundary = bool(m260) and '587301' in w260_seg and '589301' in w260_seg

sd = 'results/p2cal_ext/n1_w261'
shards = sorted(f for f in os.listdir(sd) if f.startswith('shard-') and f.endswith('.json'))
sizes_ok = all(os.path.getsize(os.path.join(sd, f)) > 100000 for f in shards)

r_banned = subprocess.run([sys.executable, 'Tools/banned_direction_gate.py',
                           '--prereg', 'research/PERPETUAL_N1_W261_PREREG.md'],
                          capture_output=True, text=True)
r_pf = subprocess.run([sys.executable, 'scripts/perpetual_faces.py', 'selftest'],
                      capture_output=True, text=True)
r_n1 = subprocess.run([sys.executable, 'scripts/perpetual_faces_n1.py', 'selftest'],
                      capture_output=True, text=True)
r_git = subprocess.run(['git', 'show', '68aad04b6:scripts/perpetual_faces_n1.py'],
                       capture_output=True)
n1_landed = hashlib.sha256(r_git.stdout).hexdigest()[:16]
r_git_pf = subprocess.run(['git', 'diff', '68aad04b6', '--', 'scripts/perpetual_faces.py'],
                          capture_output=True, text=True)
pf_diff_empty = (len((r_git_pf.stdout or '').strip()) == 0
                 and r_git_pf.returncode == 0)
n1_vs_receipt_note = (
    'r1067 window: splice commit 68aad04b6 = worktree bytes directly (zero '
    'post-splice heal) -> gate-1 asserts TRIPLE identity worktree == receipt '
    'n1_sha16_post == landed git blob; engine self-burn commits touch shard '
    'files only (ad2aa9322 6 + b88dc8fcd 5 + shard-7 pending engine next '
    'batched tick, disclosed honest)'
)
w260_finalize_present = os.path.exists('results/perpetual_faces/n1_w260_results.json')
out = {
 "machine": "bm-c",
 "wave": 261,
 "phase": "PRE-FINALIZE six-gate (r1067 bm-c 57th-gen absorb-continuation window, 23rd consecutive correct-phase; standing law -- engine self-burn 12/12 landed post-W261 splice 68aad04b6 via batched ledger appends, finalize not yet run)",
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
   "prior_wave_260_boundary_kept": boundary,
  },
  "banned": {"rc": r_banned.returncode, "stdout_tail": (r_banned.stdout or '').strip()[-200:]},
  "pf_selftest": {"rc": r_pf.returncode, "stdout_tail": (r_pf.stdout or '').strip()[-120:]},
  "n1_selftest": {"rc": r_n1.returncode, "stdout_tail": (r_n1.stdout or '').strip()[-120:]},
  "shards": {"present": len(shards), "of": 12, "sizes_above_100k": sizes_ok,
             "files": shards},
  "seed_admit": {
   "freeze_gate_lines": fr.get('seed_admit_gate'),
   "note": "freeze-time FREE evidence consumed verbatim from _w261bmc_freeze_receipt.json (both bands); whole-file per-span family faces count-asserted",
  },
  "wave_configs_row": {
   "present": True, "engine_owner": "bm-c",
   "a_seed_base": 589501, "b_exit_seed_base": 591501,
   "shard_subdir": "n1_w261", "out_name": "n1_w261_results.json",
   "seed_bases_match_freeze_bands": fr['bands']['A'] == [589501, 591500] and fr['bands']['B'] == [591501, 591700],
   "row_faces_detail": row_faces,
  },
  "w260_finalize_product_present": w260_finalize_present,
 },
 "ledger_pre": {
  "prev_total": 996335, "prev_merged_n": 569920,
  "expect_total": 998535, "expect_merged": 572120,
  "anchor": "W260 finalize (r1065 55th-gen absorb-continuation one-pass 996,335/K=569,920) per freeze receipt w260_upstream face",
 },
}

ok = (all(row_faces.values()) and all(v >= 1 for v in fam.values()) and boundary
      and w260_finalize_present
      and pf_now == fr['pf_sha16_post'] and pf_diff_empty
      and n1_now == n1_landed
      and n1_now == fr['n1_sha16_post']
      and len(shards) == 12 and sizes_ok
      and r_banned.returncode == 0 and r_pf.returncode == 0 and r_n1.returncode == 0)
out['verdict'] = 'ALL PASS' if ok else 'FAIL'
io.open('results/_r1067bmc_w261_sixgate.json', 'w', encoding='utf-8').write(
    json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps({'verdict': out['verdict'], 'row_faces': row_faces, 'fam': fam,
                  'boundary': boundary, 'shards': len(shards), 'pf': pf_now, 'n1': n1_now,
                  'n1_landed': n1_landed, 'receipt_post': fr['n1_sha16_post'],
                  'w260_finalize_present': w260_finalize_present,
                  'banned_rc': r_banned.returncode, 'pf_rc': r_pf.returncode,
                  'n1_rc': r_n1.returncode}, indent=1))
raise SystemExit(0 if ok else 1)
