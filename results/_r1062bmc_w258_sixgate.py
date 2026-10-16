# -*- coding: utf-8 -*-
# r1062 bm-c: W258 PRE-FINALIZE six-gate receipt (standing law since W217 debt;
# clone lineage _r1060bmc_w257_sixgate.py W257 pattern). Burn landed by resident
# engine auto-ignite post-W258 splice 37ccebffd (ledger appends 122485949 +
# cc72046d7 self-committed 12/12, shard files only); finalize not yet run.
# Splice commit 37ccebffd = worktree bytes directly (zero post-splice heal --
# worktree == receipt post == landed blob triple-identity expected for BOTH pf
# and n1 faces; verified live this window pre-sixgate).
# This window = 52nd-gen absorb continuation (dead r1062 window landed splice
# 37ccebffd + engine self-burn 12/12; this session verifies, then runs
# sixgate->finalize->fivekeys->sec78->W259 seat->S6->closeout).
import hashlib
import io
import json
import os
import re
import subprocess
import sys


def sha16(p):
    return hashlib.sha256(io.open(p, 'rb').read()).hexdigest()[:16]


fr = json.load(io.open('results/_w258bmc_freeze_receipt.json', encoding='utf-8'))
pf_now = sha16('scripts/perpetual_faces.py')
n1_now = sha16('scripts/perpetual_faces_n1.py')

n1t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = n1t.find('258: {"batch": "PERPETUAL-N1-W258"')
assert i >= 0, 'W258 wave row missing'
seg = n1t[i:i + 9000]
if '259: {' in seg:
    seg = seg[:seg.find('259: {')]
row_faces = {
    'a_seed_base_582901': '582901' in seg,
    'b_exit_seed_base_584901': '584901' in seg,
    'shard_subdir_n1_w258': 'n1_w258' in seg,
    'out_name_n1_w258_results': 'n1_w258_results.json' in seg,
    'engine_owner_bm_c': 'engine_owner": "bm-c"' in seg,
}
f1 = 'base=582901 span=2000'
f2 = 'base=584901 span=200'
fam = {f1: n1t.count(f1), f2: n1t.count(f2)}
m257 = re.search(r'257: \{"batch": "PERPETUAL-N1-W257"', n1t)
w257_seg = n1t[m257.start():m257.start() + 8000] if m257 else ''
if '258: {' in w257_seg:
    w257_seg = w257_seg[:w257_seg.find('258: {')]
boundary = bool(m257) and '580701' in w257_seg and '582701' in w257_seg

sd = 'results/p2cal_ext/n1_w258'
shards = sorted(f for f in os.listdir(sd) if f.startswith('shard-') and f.endswith('.json'))
sizes_ok = all(os.path.getsize(os.path.join(sd, f)) > 100000 for f in shards)

r_banned = subprocess.run([sys.executable, 'Tools/banned_direction_gate.py',
                           '--prereg', 'research/PERPETUAL_N1_W258_PREREG.md'],
                          capture_output=True, text=True)
r_pf = subprocess.run([sys.executable, 'scripts/perpetual_faces.py', 'selftest'],
                      capture_output=True, text=True)
r_n1 = subprocess.run([sys.executable, 'scripts/perpetual_faces_n1.py', 'selftest'],
                      capture_output=True, text=True)
r_git = subprocess.run(['git', 'show', '37ccebffd:scripts/perpetual_faces_n1.py'],
                       capture_output=True)
n1_landed = hashlib.sha256(r_git.stdout).hexdigest()[:16]
r_git_pf = subprocess.run(['git', 'diff', '37ccebffd', '--', 'scripts/perpetual_faces.py'],
                          capture_output=True, text=True)
pf_diff_empty = (len((r_git_pf.stdout or '').strip()) == 0
                 and r_git_pf.returncode == 0)
n1_vs_receipt_note = (
    'r1062 window: splice commit 37ccebffd = worktree bytes directly (zero '
    'post-splice heal) -> gate-1 asserts TRIPLE identity worktree == receipt '
    'n1_sha16_post == landed git blob; engine self-burn commits 122485949+'
    'cc72046d7 touched shard files only'
)
w257_finalize_present = os.path.exists('results/perpetual_faces/n1_w257_results.json')
out = {
 "machine": "bm-c",
 "wave": 258,
 "phase": "PRE-FINALIZE six-gate (r1062 bm-c 52nd-gen absorb continuation window; standing law -- engine self-burn 12/12 landed post-W258 splice 37ccebffd via ledger appends 122485949+cc72046d7, finalize not yet run)",
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
   "prior_wave_257_boundary_kept": boundary,
  },
  "banned": {"rc": r_banned.returncode, "stdout_tail": (r_banned.stdout or '').strip()[-200:]},
  "pf_selftest": {"rc": r_pf.returncode, "stdout_tail": (r_pf.stdout or '').strip()[-120:]},
  "n1_selftest": {"rc": r_n1.returncode, "stdout_tail": (r_n1.stdout or '').strip()[-120:]},
  "shards": {"present": len(shards), "of": 12, "sizes_above_100k": sizes_ok,
             "files": shards},
  "seed_admit": {
   "freeze_gate_lines": fr.get('seed_admit_gate'),
   "note": "freeze-time FREE evidence consumed verbatim from _w258bmc_freeze_receipt.json (both bands); whole-file per-span family faces count-asserted",
  },
  "wave_configs_row": {
   "present": True, "engine_owner": "bm-c",
   "a_seed_base": 582901, "b_exit_seed_base": 584901,
   "shard_subdir": "n1_w258", "out_name": "n1_w258_results.json",
   "seed_bases_match_freeze_bands": fr['bands']['A'] == [582901, 584900] and fr['bands']['B'] == [584901, 585100],
   "row_faces_detail": row_faces,
  },
  "w257_finalize_product_present": w257_finalize_present,
 },
 "ledger_pre": {
  "prev_total": 989735, "prev_merged_n": 563320,
  "expect_total": 991935, "expect_merged": 565520,
  "anchor": "W257 finalize (r1060 50th-gen absorb-continuation one-pass 989,735/K=563,320) per freeze receipt w257_upstream face",
 },
}

ok = (all(row_faces.values()) and all(v >= 1 for v in fam.values()) and boundary
      and w257_finalize_present
      and pf_now == fr['pf_sha16_post'] and pf_diff_empty
      and n1_now == n1_landed
      and n1_now == fr['n1_sha16_post']
      and len(shards) == 12 and sizes_ok
      and r_banned.returncode == 0 and r_pf.returncode == 0 and r_n1.returncode == 0)
out['verdict'] = 'ALL PASS' if ok else 'FAIL'
io.open('results/_r1062bmc_w258_sixgate.json', 'w', encoding='utf-8').write(
    json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps({'verdict': out['verdict'], 'row_faces': row_faces, 'fam': fam,
                  'boundary': boundary, 'shards': len(shards), 'pf': pf_now, 'n1': n1_now,
                  'n1_landed': n1_landed, 'receipt_post': fr['n1_sha16_post'],
                  'w257_finalize_present': w257_finalize_present,
                  'banned_rc': r_banned.returncode, 'pf_rc': r_pf.returncode,
                  'n1_rc': r_n1.returncode}, indent=1))
raise SystemExit(0 if ok else 1)
