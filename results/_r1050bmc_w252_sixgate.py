# -*- coding: utf-8 -*-
# r1050 bm-c: W252 PRE-FINALIZE six-gate receipt (standing law since W217 debt;
# clone lineage _r1048bmc_w251_sixgate.py W251 pattern). Burn landed by resident
# engine auto-ignite post-r1050 splice e63561df3 (ledger appends cbf6411bf +
# b3d563f4f self-committed 12/12); finalize not yet run. r1050 window = ZERO
# post-splice heal (splice commit = worktree bytes directly; dead-window authoring
# repaired 5 defect classes PRE-splice via count-asserted gates) -> worktree ==
# receipt post == landed blob triple-identity (verified pre-gate this window).
import hashlib
import io
import json
import os
import re
import subprocess
import sys


def sha16(p):
    return hashlib.sha256(io.open(p, 'rb').read()).hexdigest()[:16]


fr = json.load(io.open('results/_w252bmc_freeze_receipt.json', encoding='utf-8'))
pf_now = sha16('scripts/perpetual_faces.py')
n1_now = sha16('scripts/perpetual_faces_n1.py')

n1t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = n1t.find('252: {"batch": "PERPETUAL-N1-W252"')
assert i >= 0, 'W252 wave row missing'
seg = n1t[i:i + 9000]
if '253: {' in seg:
    seg = seg[:seg.find('253: {')]
row_faces = {
    'a_seed_base_569701': '569701' in seg,
    'b_exit_seed_base_571701': '571701' in seg,
    'shard_subdir_n1_w252': 'n1_w252' in seg,
    'out_name_n1_w252_results': 'n1_w252_results.json' in seg,
    'engine_owner_bm_c': 'engine_owner": "bm-c"' in seg,
}
f1 = 'base=569701 span=2000'
f2 = 'base=571701 span=200'
fam = {f1: n1t.count(f1), f2: n1t.count(f2)}
m251 = re.search(r'251: \{"batch": "PERPETUAL-N1-W251"', n1t)
w251_seg = n1t[m251.start():m251.start() + 8000] if m251 else ''
if '252: {' in w251_seg:
    w251_seg = w251_seg[:w251_seg.find('252: {')]
boundary = bool(m251) and '567501' in w251_seg and '569501' in w251_seg

sd = 'results/p2cal_ext/n1_w252'
shards = sorted(f for f in os.listdir(sd) if f.startswith('shard-') and f.endswith('.json'))
sizes_ok = all(os.path.getsize(os.path.join(sd, f)) > 100000 for f in shards)

r_banned = subprocess.run([sys.executable, 'Tools/banned_direction_gate.py',
                           '--prereg', 'research/PERPETUAL_N1_W252_PREREG.md'],
                          capture_output=True, text=True)
r_pf = subprocess.run([sys.executable, 'scripts/perpetual_faces.py', 'selftest'],
                      capture_output=True, text=True)
r_n1 = subprocess.run([sys.executable, 'scripts/perpetual_faces_n1.py', 'selftest'],
                      capture_output=True, text=True)
r_git = subprocess.run(['git', 'show', 'e63561df3:scripts/perpetual_faces_n1.py'],
                       capture_output=True)
n1_landed = hashlib.sha256(r_git.stdout).hexdigest()[:16]
n1_vs_receipt_note = (
    'r1050 window: ZERO post-splice heal (dead-window splice commit e63561df3 = the worktree '
    'bytes directly; 5 authoring defect classes caught pre-splice by count-asserted gates per '
    'commit msg) -> gate-1 asserts the TRIPLE identity worktree == receipt n1_sha16_post '
    '== landed git blob (verified pre-gate this window; engine self-burn commits touched '
    'shard files only)')
w251_finalize_present = os.path.exists('results/perpetual_faces/n1_w251_results.json')
out = {
 "machine": "bm-c",
 "wave": 252,
 "phase": "PRE-FINALIZE six-gate (r1050 bm-c absorb window; standing law -- engine self-burn 12/12 landed post-r1050 splice e63561df3 via ledger appends cbf6411bf+b3d563f4f, finalize not yet run)",
 "gates": {
  "splice_integrity": {
   "bands_facts_match_freeze_receipt": all(row_faces.values()),
   "pf_sha16_now": pf_now, "n1_sha16_now": n1_now,
   "pf_sha16_freeze_post": fr['pf_sha16_post'],
   "n1_sha16_freeze_post": fr['n1_sha16_post'],
   "n1_sha16_landed_commit": n1_landed,
   "n1_vs_receipt_disclosure": n1_vs_receipt_note,
   "family_seed_faces": fam,
   "prior_wave_251_boundary_kept": boundary,
  },
  "banned": {"rc": r_banned.returncode, "stdout_tail": (r_banned.stdout or '').strip()[-200:]},
  "pf_selftest": {"rc": r_pf.returncode, "stdout_tail": (r_pf.stdout or '').strip()[-120:]},
  "n1_selftest": {"rc": r_n1.returncode, "stdout_tail": (r_n1.stdout or '').strip()[-120:]},
  "shards": {"present": len(shards), "of": 12, "sizes_above_100k": sizes_ok,
             "files": shards},
  "seed_admit": {
   "freeze_gate_lines": fr.get('seed_admit_gate'),
   "note": "freeze-time FREE evidence consumed verbatim from _w252bmc_freeze_receipt.json (both bands); whole-file per-span family faces count-asserted; W252 block uses merged both-bands phrasing (a-msg quote-wrapper rebuilt via repr per commit msg P5e class)",
  },
  "wave_configs_row": {
   "present": True, "engine_owner": "bm-c",
   "a_seed_base": 569701, "b_exit_seed_base": 571701,
   "shard_subdir": "n1_w252", "out_name": "n1_w252_results.json",
   "seed_bases_match_freeze_bands": fr['bands']['A'] == [569701, 571700] and fr['bands']['B'] == [571701, 571900],
   "row_faces_detail": row_faces,
  },
  "w251_finalize_product_present": w251_finalize_present,
 },
 "ledger_pre": {
  "prev_total": 976535, "prev_merged_n": 550120,
  "expect_total": 978735, "expect_merged": 552320,
  "anchor": "W251 finalize (bm-c r1048 absorb window one-pass, 976,535/K=550,120) per freeze receipt w251_upstream face",
 },
}

ok = (all(row_faces.values()) and all(v >= 1 for v in fam.values()) and boundary
      and w251_finalize_present
      and pf_now == fr['pf_sha16_post'] and n1_now == n1_landed
      and n1_now == fr['n1_sha16_post']
      and len(shards) == 12 and sizes_ok
      and r_banned.returncode == 0 and r_pf.returncode == 0 and r_n1.returncode == 0)
out['verdict'] = 'ALL PASS' if ok else 'FAIL'
io.open('results/_r1050bmc_w252_sixgate.json', 'w', encoding='utf-8').write(
    json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps({'verdict': out['verdict'], 'row_faces': row_faces, 'fam': fam,
                  'boundary': boundary, 'shards': len(shards), 'pf': pf_now, 'n1': n1_now,
                  'n1_landed': n1_landed, 'receipt_post': fr['n1_sha16_post'],
                  'w251_finalize_present': w251_finalize_present,
                  'banned_rc': r_banned.returncode, 'pf_rc': r_pf.returncode,
                  'n1_rc': r_n1.returncode}, indent=1))
raise SystemExit(0 if ok else 1)
