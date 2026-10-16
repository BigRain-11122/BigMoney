# -*- coding: utf-8 -*-
# r1053 bm-c: W253 PRE-FINALIZE six-gate receipt (standing law since W217 debt;
# clone lineage _r1050bmc_w252_sixgate.py W252 pattern). Burn landed by resident
# engine auto-ignite post-W253 splice c9b4fd855 (ledger appends b3caaedc1 +
# bec86607a self-committed 12/12, shard files only); finalize not yet run.
# r1053 window = ZERO post-splice heal on n1 (splice commit = worktree bytes
# directly) -> worktree == receipt post == landed blob triple-identity for n1
# (verified pre-gate this window via _r1053bmc_estate_check.py); pf face =
# worktree == receipt post (CRLF worktree face; committed blob = LF
# normalization of same content, git-diff-empty, receipt eol.pf_crlf=true).
import hashlib
import io
import json
import os
import re
import subprocess
import sys


def sha16(p):
    return hashlib.sha256(io.open(p, 'rb').read()).hexdigest()[:16]


fr = json.load(io.open('results/_w253bmc_freeze_receipt.json', encoding='utf-8'))
pf_now = sha16('scripts/perpetual_faces.py')
n1_now = sha16('scripts/perpetual_faces_n1.py')

n1t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = n1t.find('253: {"batch": "PERPETUAL-N1-W253"')
assert i >= 0, 'W253 wave row missing'
seg = n1t[i:i + 9000]
if '254: {' in seg:
    seg = seg[:seg.find('254: {')]
row_faces = {
    'a_seed_base_571901': '571901' in seg,
    'b_exit_seed_base_573901': '573901' in seg,
    'shard_subdir_n1_w253': 'n1_w253' in seg,
    'out_name_n1_w253_results': 'n1_w253_results.json' in seg,
    'engine_owner_bm_c': 'engine_owner": "bm-c"' in seg,
}
f1 = 'base=571901 span=2000'
f2 = 'base=573901 span=200'
fam = {f1: n1t.count(f1), f2: n1t.count(f2)}
m252 = re.search(r'252: \{"batch": "PERPETUAL-N1-W252"', n1t)
w252_seg = n1t[m252.start():m252.start() + 8000] if m252 else ''
if '253: {' in w252_seg:
    w252_seg = w252_seg[:w252_seg.find('253: {')]
boundary = bool(m252) and '569701' in w252_seg and '571701' in w252_seg

sd = 'results/p2cal_ext/n1_w253'
shards = sorted(f for f in os.listdir(sd) if f.startswith('shard-') and f.endswith('.json'))
sizes_ok = all(os.path.getsize(os.path.join(sd, f)) > 100000 for f in shards)

r_banned = subprocess.run([sys.executable, 'Tools/banned_direction_gate.py',
                           '--prereg', 'research/PERPETUAL_N1_W253_PREREG.md'],
                          capture_output=True, text=True)
r_pf = subprocess.run([sys.executable, 'scripts/perpetual_faces.py', 'selftest'],
                      capture_output=True, text=True)
r_n1 = subprocess.run([sys.executable, 'scripts/perpetual_faces_n1.py', 'selftest'],
                      capture_output=True, text=True)
r_git = subprocess.run(['git', 'show', 'c9b4fd855:scripts/perpetual_faces_n1.py'],
                       capture_output=True)
n1_landed = hashlib.sha256(r_git.stdout).hexdigest()[:16]
n1_vs_receipt_note = (
    'r1053 window: ZERO post-splice heal on n1 (dead-window splice commit c9b4fd855 = the '
    'worktree bytes directly; 4 same-window needle repairs caught PRE-splice per commit msg) '
    '-> gate-1 asserts the TRIPLE identity worktree == receipt n1_sha16_post == landed git '
    'blob (verified pre-gate this window via _r1053bmc_estate_check.py; engine self-burn '
    'commits b3caaedc1+bec86607a touched shard files only); pf face = worktree == receipt '
    'pf_sha16_post (CRLF worktree face, committed blob = LF normalization, git-diff-empty, '
    'receipt eol.pf_crlf=true)'
)
w252_finalize_present = os.path.exists('results/perpetual_faces/n1_w252_results.json')
out = {
 "machine": "bm-c",
 "wave": 253,
 "phase": "PRE-FINALIZE six-gate (r1053 bm-c absorb window; standing law -- engine self-burn 12/12 landed post-W253 splice c9b4fd855 via ledger appends b3caaedc1+bec86607a, finalize not yet run)",
 "gates": {
  "splice_integrity": {
   "bands_facts_match_freeze_receipt": all(row_faces.values()),
   "pf_sha16_now": pf_now, "n1_sha16_now": n1_now,
   "pf_sha16_freeze_post": fr['pf_sha16_post'],
   "n1_sha16_freeze_post": fr['n1_sha16_post'],
   "n1_sha16_landed_commit": n1_landed,
   "n1_vs_receipt_disclosure": n1_vs_receipt_note,
   "family_seed_faces": fam,
   "prior_wave_252_boundary_kept": boundary,
  },
  "banned": {"rc": r_banned.returncode, "stdout_tail": (r_banned.stdout or '').strip()[-200:]},
  "pf_selftest": {"rc": r_pf.returncode, "stdout_tail": (r_pf.stdout or '').strip()[-120:]},
  "n1_selftest": {"rc": r_n1.returncode, "stdout_tail": (r_n1.stdout or '').strip()[-120:]},
  "shards": {"present": len(shards), "of": 12, "sizes_above_100k": sizes_ok,
             "files": shards},
  "seed_admit": {
   "freeze_gate_lines": fr.get('seed_admit_gate'),
   "note": "freeze-time FREE evidence consumed verbatim from _w253bmc_freeze_receipt.json (both bands); whole-file per-span family faces count-asserted",
  },
  "wave_configs_row": {
   "present": True, "engine_owner": "bm-c",
   "a_seed_base": 571901, "b_exit_seed_base": 573901,
   "shard_subdir": "n1_w253", "out_name": "n1_w253_results.json",
   "seed_bases_match_freeze_bands": fr['bands']['A'] == [571901, 573900] and fr['bands']['B'] == [573901, 574100],
   "row_faces_detail": row_faces,
  },
  "w252_finalize_product_present": w252_finalize_present,
 },
 "ledger_pre": {
  "prev_total": 978735, "prev_merged_n": 552320,
  "expect_total": 980935, "expect_merged": 554520,
  "anchor": "W252 finalize (bm-c r1050 absorb window one-pass, 978,735/K=552,320) per freeze receipt w252_upstream face",
 },
}

ok = (all(row_faces.values()) and all(v >= 1 for v in fam.values()) and boundary
      and w252_finalize_present
      and pf_now == fr['pf_sha16_post'] and n1_now == n1_landed
      and n1_now == fr['n1_sha16_post']
      and len(shards) == 12 and sizes_ok
      and r_banned.returncode == 0 and r_pf.returncode == 0 and r_n1.returncode == 0)
out['verdict'] = 'ALL PASS' if ok else 'FAIL'
io.open('results/_r1053bmc_w253_sixgate.json', 'w', encoding='utf-8').write(
    json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps({'verdict': out['verdict'], 'row_faces': row_faces, 'fam': fam,
                  'boundary': boundary, 'shards': len(shards), 'pf': pf_now, 'n1': n1_now,
                  'n1_landed': n1_landed, 'receipt_post': fr['n1_sha16_post'],
                  'w252_finalize_present': w252_finalize_present,
                  'banned_rc': r_banned.returncode, 'pf_rc': r_pf.returncode,
                  'n1_rc': r_n1.returncode}, indent=1))
raise SystemExit(0 if ok else 1)
