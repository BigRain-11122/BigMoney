# -*- coding: utf-8 -*-
# r1068 bm-c: W262 PRE-FINALIZE six-gate receipt (standing law since W217 debt;
# clone lineage _r1067bmc_w261_sixgate.py W261 pattern, 24th consecutive
# PRE-FINALIZE correct-phase). Burn landed by resident engine auto-ignite
# post-W262 splice e1a94b335 (batched ledger appends self-committed 12/12:
# 06dcd6c23 6 + b83318440 6, shard files only); finalize not yet run.
# Splice commit e1a94b335 = worktree bytes directly (zero post-splice heal --
# worktree == receipt post == landed blob triple-identity expected for BOTH pf
# and n1 faces). Splice push saga disclosed: first push claw-blocked (origin
# advanced to bm-b r990 mid-flight = hot-window race), stash-bridge rebase hit
# the engine-burn n1 file-lock (unable to unlink -> could not detach HEAD,
# partial-checkout worktree damage healed same-window: pf restored from index
# BEFORE remaining shards ignited, splice files restored, burn proceeded
# 12/12 with correct bytes), post-burn rebase 3/3 clean -> push LANDED
# c80525116..b83318440 (splice e1a94b335 rebased + two engine appends).
import hashlib
import io
import json
import os
import re
import subprocess
import sys


def sha16(p):
    return hashlib.sha256(io.open(p, 'rb').read()).hexdigest()[:16]


fr = json.load(io.open('results/_w262bmc_freeze_receipt.json', encoding='utf-8'))
pf_now = sha16('scripts/perpetual_faces.py')
n1_now = sha16('scripts/perpetual_faces_n1.py')

n1t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = n1t.find('262: {"batch": "PERPETUAL-N1-W262"')
assert i >= 0, 'W262 wave row missing'
seg = n1t[i:i + 9000]
if '263: {' in seg:
    seg = seg[:seg.find('263: {')]
row_faces = {
    'a_seed_base_591701': '591701' in seg,
    'b_exit_seed_base_593701': '593701' in seg,
    'shard_subdir_n1_w262': 'n1_w262' in seg,
    'out_name_n1_w262_results': 'n1_w262_results.json' in seg,
    'engine_owner_bm_c': 'engine_owner": "bm-c"' in seg,
}
f1 = 'base=591701 span=2000'
f2 = 'base=593701 span=200'
fam = {f1: n1t.count(f1), f2: n1t.count(f2)}
m261 = re.search(r'261: \{"batch": "PERPETUAL-N1-W261"', n1t)
w261_seg = n1t[m261.start():m261.start() + 8000] if m261 else ''
if '262: {' in w261_seg:
    w261_seg = w261_seg[:w261_seg.find('262: {')]
boundary = bool(m261) and '589501' in w261_seg and '591501' in w261_seg

sd = 'results/p2cal_ext/n1_w262'
shards = sorted(f for f in os.listdir(sd) if f.startswith('shard-') and f.endswith('.json'))
sizes_ok = all(os.path.getsize(os.path.join(sd, f)) > 100000 for f in shards)

r_banned = subprocess.run([sys.executable, 'Tools/banned_direction_gate.py',
                           '--prereg', 'research/PERPETUAL_N1_W262_PREREG.md'],
                          capture_output=True, text=True)
r_pf = subprocess.run([sys.executable, 'scripts/perpetual_faces.py', 'selftest'],
                      capture_output=True, text=True)
r_n1 = subprocess.run([sys.executable, 'scripts/perpetual_faces_n1.py', 'selftest'],
                      capture_output=True, text=True)
r_git = subprocess.run(['git', 'show', 'e1a94b335:scripts/perpetual_faces_n1.py'],
                       capture_output=True)
n1_landed = hashlib.sha256(r_git.stdout).hexdigest()[:16]
r_git_pf = subprocess.run(['git', 'diff', 'e1a94b335', '--', 'scripts/perpetual_faces.py'],
                          capture_output=True, text=True)
pf_diff_empty = (len((r_git_pf.stdout or '').strip()) == 0
                 and r_git_pf.returncode == 0)
n1_vs_receipt_note = (
    'r1068 window: splice commit e1a94b335 = worktree bytes directly (zero '
    'post-splice heal) -> gate-1 asserts TRIPLE identity worktree == receipt '
    'n1_sha16_post == landed git blob; engine self-burn commits touch shard '
    'files only (06dcd6c23 6 + b83318440 6 = 12/12, both landed origin via '
    'the r1068 push-saga rebase chain, disclosed honest)'
)
w261_finalize_present = os.path.exists('results/perpetual_faces/n1_w261_results.json')
out = {
 "machine": "bm-c",
 "wave": 262,
 "phase": "PRE-FINALIZE six-gate (r1068 bm-c 58th-gen continuation window, 24th consecutive correct-phase; standing law -- engine self-burn 12/12 landed post-W262 splice e1a94b335 via batched ledger appends, finalize not yet run)",
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
   "prior_wave_261_boundary_kept": boundary,
  },
  "banned": {"rc": r_banned.returncode, "stdout_tail": (r_banned.stdout or '').strip()[-200:]},
  "pf_selftest": {"rc": r_pf.returncode, "stdout_tail": (r_pf.stdout or '').strip()[-120:]},
  "n1_selftest": {"rc": r_n1.returncode, "stdout_tail": (r_n1.stdout or '').strip()[-120:]},
  "shards": {"present": len(shards), "of": 12, "sizes_above_100k": sizes_ok,
             "files": shards},
  "seed_admit": {
   "freeze_gate_lines": fr.get('seed_admit_gate'),
   "note": "freeze-time FREE evidence consumed verbatim from _w262bmc_freeze_receipt.json (both bands); whole-file per-span family faces count-asserted",
  },
  "wave_configs_row": {
   "present": True, "engine_owner": "bm-c",
   "a_seed_base": 591701, "b_exit_seed_base": 593701,
   "shard_subdir": "n1_w262", "out_name": "n1_w262_results.json",
   "seed_bases_match_freeze_bands": fr['bands']['A'] == [591701, 593700] and fr['bands']['B'] == [593701, 593900],
   "row_faces_detail": row_faces,
  },
  "w261_finalize_product_present": w261_finalize_present,
 },
 "ledger_pre": {
  "prev_total": 998535, "prev_merged_n": 572120,
  "expect_total": 1000735, "expect_merged": 574320,
  "anchor": "W261 finalize (r1067 57th-gen absorb-continuation one-pass 998,535/K=572,120) per freeze receipt w261_upstream face",
 },
}

ok = (all(row_faces.values()) and all(v >= 1 for v in fam.values()) and boundary
      and w261_finalize_present
      and pf_now == fr['pf_sha16_post'] and pf_diff_empty
      and n1_now == n1_landed
      and n1_now == fr['n1_sha16_post']
      and len(shards) == 12 and sizes_ok
      and r_banned.returncode == 0 and r_pf.returncode == 0 and r_n1.returncode == 0)
out['verdict'] = 'ALL PASS' if ok else 'FAIL'
io.open('results/_r1068bmc_w262_sixgate.json', 'w', encoding='utf-8').write(
    json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps({'verdict': out['verdict'], 'row_faces': row_faces, 'fam': fam,
                  'boundary': boundary, 'shards': len(shards), 'pf': pf_now, 'n1': n1_now,
                  'n1_landed': n1_landed, 'receipt_post': fr['n1_sha16_post'],
                  'w261_finalize_present': w261_finalize_present,
                  'banned_rc': r_banned.returncode, 'pf_rc': r_pf.returncode,
                  'n1_rc': r_n1.returncode}, indent=1))
raise SystemExit(0 if ok else 1)
