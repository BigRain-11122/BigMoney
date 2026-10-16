# -*- coding: utf-8 -*-
# r1046 bm-c: W250 PRE-FINALIZE six-gate receipt (standing law since W217 debt;
# clone lineage _r1043bmc_w249_sixgate.py W249 pattern). Burn in flight by
# resident engine auto-ignite post-r1046 splice (ledger appends self-commit);
# finalize not yet run. Gates: 1 splice integrity sha16 x2 + 2 wave-row faces
# ==freeze receipt bands + 3 banned ADMIT + 4 pf selftest + 5 n1 selftest
# + 6 shards 12/12 + seed_admit FREE-verbatim + prior-wave boundary kept.
import hashlib
import io
import json
import os
import re
import subprocess
import sys


def sha16(p):
    return hashlib.sha256(io.open(p, 'rb').read()).hexdigest()[:16]


fr = json.load(io.open('results/_w250bmc_freeze_receipt.json', encoding='utf-8'))
pf_now = sha16('scripts/perpetual_faces.py')
n1_now = sha16('scripts/perpetual_faces_n1.py')

n1t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = n1t.find('250: {"batch": "PERPETUAL-N1-W250"')
assert i >= 0, 'W250 wave row missing'
seg = n1t[i:i + 9000]
if '251: {' in seg:
    seg = seg[:seg.find('251: {')]
row_faces = {
    'a_seed_base_565501': '565501' in seg,
    'b_exit_seed_base_545101': '545101' in seg,
    'shard_subdir_n1_w250': 'n1_w250' in seg,
    'out_name_n1_w250_results': 'n1_w250_results.json' in seg,
    'engine_owner_bm_c': 'engine_owner": "bm-c"' in seg,
}
f1 = 'seed_admit_gate rc0 base=565501 span=2000 checked=2000 verdict=FREE'
f2 = 'seed_admit_gate rc0 base=545101 span=200 checked=200 verdict=FREE'
fam = {f1: n1t.count(f1), f2: n1t.count(f2)}
m249 = re.search(r'249: \{"batch": "PERPETUAL-N1-W249"', n1t)
w249_seg = n1t[m249.start():m249.start() + 8000] if m249 else ''
if '250: {' in w249_seg:
    w249_seg = w249_seg[:w249_seg.find('250: {')]
boundary = bool(m249) and '563501' in w249_seg and '544901' in w249_seg

sd = 'results/p2cal_ext/n1_w250'
shards = sorted(f for f in os.listdir(sd) if f.startswith('shard-') and f.endswith('.json'))
sizes_ok = all(os.path.getsize(os.path.join(sd, f)) > 100000 for f in shards)

r_banned = subprocess.run([sys.executable, 'Tools/banned_direction_gate.py',
                           '--prereg', 'research/PERPETUAL_N1_W250_PREREG.md'],
                          capture_output=True, text=True)
r_pf = subprocess.run([sys.executable, 'scripts/perpetual_faces.py', 'selftest'],
                      capture_output=True, text=True)
r_n1 = subprocess.run([sys.executable, 'scripts/perpetual_faces_n1.py', 'selftest'],
                      capture_output=True, text=True)
r_git = subprocess.run(['git', 'show', '29930f489:scripts/perpetual_faces_n1.py'],
                       capture_output=True)
n1_landed = hashlib.sha256(r_git.stdout).hexdigest()[:16]
n1_vs_receipt_note = (
    'receipt n1_sha16_post (050d7e70375727f2) = in-memory pre-heal string n1_t4 hashed at '
    'receipt-write 08:04:23; disclosed post-splice heal (print face rows 68->69, commit '
    '29930f489 message) landed 08:07:43 before commit, so receipt post-sha is a PRE-HEAL '
    'snapshot and cannot equal the healed blob by construction; gate-1 asserts instead '
    'worktree == LANDED git blob (zero drift since splice commit)')
out = {
 "machine": "bm-c",
 "wave": 250,
 "phase": "PRE-FINALIZE six-gate (r1046 bm-c window; standing law -- engine self-burn 12/12 landed post-r1046 splice, finalize not yet run)",
 "gates": {
  "splice_integrity": {
   "bands_facts_match_freeze_receipt": all(row_faces.values()),
   "pf_sha16_now": pf_now, "n1_sha16_now": n1_now,
   "pf_sha16_freeze_post": fr['pf_sha16_post'],
   "n1_sha16_freeze_post": fr['n1_sha16_post'],
   "n1_sha16_landed_commit": n1_landed,
   "n1_vs_receipt_disclosure": n1_vs_receipt_note,
   "family_seed_faces": fam,
   "prior_wave_249_boundary_kept": boundary,
  },
  "banned": {"rc": r_banned.returncode, "stdout_tail": (r_banned.stdout or '').strip()[-200:]},
  "pf_selftest": {"rc": r_pf.returncode, "stdout_tail": (r_pf.stdout or '').strip()[-120:]},
  "n1_selftest": {"rc": r_n1.returncode, "stdout_tail": (r_n1.stdout or '').strip()[-120:]},
  "shards": {"present": len(shards), "of": 12, "sizes_above_100k": sizes_ok,
             "files": shards},
  "seed_admit": {
   "freeze_gate_lines": fr.get('seed_admit_gate'),
   "note": "freeze-time FREE evidence consumed verbatim from _w250bmc_freeze_receipt.json; post-registration self-collision BLOCKED would be the fresh-run positive (W237.. pattern)",
  },
  "wave_configs_row": {
   "present": True, "engine_owner": "bm-c",
   "a_seed_base": 565501, "b_exit_seed_base": 545101,
   "shard_subdir": "n1_w250", "out_name": "n1_w250_results.json",
   "seed_bases_match_freeze_bands": fr['bands']['A'] == [565501, 567500] and fr['bands']['B'] == [545101, 545300],
   "row_faces_detail": row_faces,
  },
 },
 "ledger_pre": {
  "prev_total": 972135, "prev_merged_n": 545720,
  "expect_total": 974335, "expect_merged": 547920,
  "anchor": "W249 finalize (bm-c r1043 absorb one-pass, 972,135/K=545,720) per freeze receipt w249_upstream face",
 },
}

ok = (all(row_faces.values()) and all(v >= 1 for v in fam.values()) and boundary
      and pf_now == fr['pf_sha16_post'] and n1_now == n1_landed
      and len(shards) == 12 and sizes_ok
      and r_banned.returncode == 0 and r_pf.returncode == 0 and r_n1.returncode == 0)
out['verdict'] = 'ALL PASS' if ok else 'FAIL'
io.open('results/_r1046bmc_w250_sixgate.json', 'w', encoding='utf-8').write(
    json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps({'verdict': out['verdict'], 'row_faces': row_faces, 'fam': fam,
                  'boundary': boundary, 'shards': len(shards), 'pf': pf_now, 'n1': n1_now,
                  'n1_landed': n1_landed, 'receipt_pre_heal': fr['n1_sha16_post'],
                  'banned_rc': r_banned.returncode, 'pf_rc': r_pf.returncode,
                  'n1_rc': r_n1.returncode}, indent=1))
raise SystemExit(0 if ok else 1)
