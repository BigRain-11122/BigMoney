# -*- coding: utf-8 -*-
# r1084-continuation bm-c: W265 PRE-FINALIZE six-gate receipt (standing law
# since W217 debt; clone lineage _r1076bmc_w264_sixgate.py pattern, would-be
# 27th consecutive PRE-FINALIZE correct-phase). Burn landed by resident engine
# auto-ignite post-W265 splice a47517f792 (ledger appends self-commit by the
# daemon; finalize not yet run).
# DIFFERENCE vs the W264 receipt: NO post-splice heal section -- the W265
# canon was born CLEAN: the 3-token defect family (un-rolled _set_wave +
# self-check indexes, W264 r1076 H1/H2/H3) was caught PRE-splice in the DST
# (results/_r1084bmc_dst_heal.py, 4 faces, idempotent v2) -- n1 selftest
# passed FIRST-TRY at splice time (N1_ST_RC=0 in the splice window), so
# gate-1 asserts the plain worktree==receipt-post==landed-blob identity
# (CR-normalized for the landed blob, clean-filter face per W263/W264
# precedent).
import hashlib
import io
import json
import os
import re
import subprocess
import sys


def sha16(p):
    return hashlib.sha256(io.open(p, 'rb').read()).hexdigest()[:16]


def crnorm(b):
    return b.replace(b'\r\n', b'\n')


SPLICE = 'a47517f792bf061b046f508f8712680047bd25b4'
fr = json.load(io.open('results/_w265bmc_freeze_receipt.json', encoding='utf-8'))
pf_now = sha16('scripts/perpetual_faces.py')
n1_now = sha16('scripts/perpetual_faces_n1.py')

n1t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = n1t.find('265: {"batch": "PERPETUAL-N1-W265"')
assert i >= 0, 'W265 wave row missing'
seg = n1t[i:i + 9000]
if '266: {' in seg:
    seg = seg[:seg.find('266: {')]
row_faces = {
    'a_seed_base_598301': '598301' in seg,
    'b_exit_seed_base_600301': '600301' in seg,
    'shard_subdir_n1_w265': 'n1_w265' in seg,
    'out_name_n1_w265_results': 'n1_w265_results.json' in seg,
    'engine_owner_bm_c': 'engine_owner": "bm-c"' in seg,
}
f1 = 'base=598301 span=2000'
f2 = 'base=600301 span=200'
fam = {f1: n1t.count(f1), f2: n1t.count(f2)}
m264 = re.search(r'264: \{"batch": "PERPETUAL-N1-W264"', n1t)
w264_seg = n1t[m264.start():m264.start() + 8000] if m264 else ''
if '265: {' in w264_seg:
    w264_seg = w264_seg[:w264_seg.find('265: {')]
boundary = bool(m264) and '596101' in w264_seg and '598101' in w264_seg

sd = 'results/p2cal_ext/n1_w265'
shards = sorted(f for f in os.listdir(sd) if f.startswith('shard-') and f.endswith('.json'))
sizes_ok = all(os.path.getsize(os.path.join(sd, f)) > 100000 for f in shards)

r_banned = subprocess.run([sys.executable, 'Tools/banned_direction_gate.py',
                           '--prereg', 'research/PERPETUAL_N1_W265_PREREG.md'],
                          capture_output=True, text=True)
r_pf = subprocess.run([sys.executable, 'scripts/perpetual_faces.py', 'selftest'],
                     capture_output=True, text=True)
r_n1 = subprocess.run([sys.executable, 'scripts/perpetual_faces_n1.py', 'selftest'],
                      capture_output=True, text=True)
r_git = subprocess.run(['git', 'show', f'{SPLICE}:scripts/perpetual_faces_n1.py'],
                       capture_output=True)
n1_landed = hashlib.sha256(r_git.stdout).hexdigest()[:16]
wt_n1_bytes = io.open('scripts/perpetual_faces_n1.py', 'rb').read()
n1_crnorm_equal = crnorm(wt_n1_bytes) == crnorm(r_git.stdout)
r_git_pf = subprocess.run(['git', 'show', f'{SPLICE}:scripts/perpetual_faces.py'],
                          capture_output=True)
wt_pf_bytes = io.open('scripts/perpetual_faces.py', 'rb').read()
pf_crnorm_equal = crnorm(wt_pf_bytes) == crnorm(r_git_pf.stdout)
r_git_pf_diff = subprocess.run(['git', 'diff', SPLICE, '--',
                                'scripts/perpetual_faces.py'],
                               capture_output=True, text=True)
pf_diff_empty = (len((r_git_pf_diff.stdout or '').strip()) == 0
                 and r_git_pf_diff.returncode == 0)

pre_splice_heal_note = (
    'PRE-SPLICE heal face (W264 r1076 H1/H2/H3 defect family caught one '
    'generation earlier): results/_r1084bmc_dst_heal.py applied 4 faces to '
    'the DST BEFORE the splice (E2 _set_wave 263->265, E3/E4 self-check '
    'WAVE_CONFIGS [264]->[265], E1 receipt wave field) -- canon born clean, '
    'n1 selftest passed FIRST-TRY in the splice window, zero post-splice '
    'heal needed (contrast: W264 required the r1076 post-splice heal with '
    'minimality proof after n1 selftest died "W264 A hits W263").'
)

# ledger_pre: machine-read from W264 finalize product (r587 never-transcribe)
w264 = json.load(io.open('results/perpetual_faces/n1_w264_results.json',
                         encoding='utf-8'))


def _find_ledger(obj):
    if isinstance(obj, dict):
        if 'ledger' in obj and isinstance(obj['ledger'], dict) \
                and 'total' in obj['ledger']:
            return obj['ledger']
        for v in obj.values():
            r = _find_ledger(v)
            if r:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = _find_ledger(v)
            if r:
                return r
    return None


ledger_w264 = _find_ledger(w264)
assert ledger_w264 is not None, 'W264 ledger face missing'
prev_total = ledger_w264['total']
prev_k = w264['null_pool_cumulative']['merged']['n_values']
expect_total = prev_total + 2200
expect_merged = prev_k + 2200
up = fr['w264_upstream']
upstream_match = (up['ledger_total'] == prev_total and up['merged_n'] == prev_k)

w264_finalize_present = os.path.exists('results/perpetual_faces/n1_w264_results.json')
out = {
 "machine": "bm-c",
 "wave": 265,
 "phase": "PRE-FINALIZE six-gate (r1084-continuation bm-c own-seat window, 27th consecutive correct-phase; standing law -- engine self-burn 12/12 landed post-W265 splice a47517f792, finalize not yet run)",
 "gates": {
  "splice_integrity": {
   "bands_facts_match_freeze_receipt": all(row_faces.values()),
   "pf_sha16_now": pf_now, "n1_sha16_now": n1_now,
   "pf_sha16_freeze_post": fr['pf_sha16_post'],
   "n1_sha16_freeze_post": fr['n1_sha16_post'],
   "n1_sha16_landed_commit": n1_landed,
   "n1_crnorm_equal_worktree_vs_landed": n1_crnorm_equal,
   "pf_crnorm_equal_worktree_vs_landed": pf_crnorm_equal,
   "pf_landed_diff_empty": pf_diff_empty,
   "pre_splice_heal_note": pre_splice_heal_note,
   "family_seed_faces": fam,
   "prior_wave_264_boundary_kept": boundary,
  },
  "banned": {"rc": r_banned.returncode, "stdout_tail": (r_banned.stdout or '').strip()[-200:]},
  "pf_selftest": {"rc": r_pf.returncode, "stdout_tail": (r_pf.stdout or '').strip()[-120:]},
  "n1_selftest": {"rc": r_n1.returncode, "stdout_tail": (r_n1.stdout or '').strip()[-120:]},
  "shards": {"present": len(shards), "of": 12, "sizes_above_100k": sizes_ok,
             "files": shards},
  "seed_admit": {
   "freeze_gate_lines": fr.get('seed_admit_gate'),
   "note": "freeze-time FREE evidence consumed verbatim from _w265bmc_freeze_receipt.json (both bands); whole-file per-span family faces count-asserted",
  },
  "wave_configs_row": {
   "present": True, "engine_owner": "bm-c",
   "a_seed_base": 598301, "b_exit_seed_base": 600301,
   "shard_subdir": "n1_w265", "out_name": "n1_w265_results.json",
   "seed_bases_match_freeze_bands": fr['bands']['a_lo'] == 598301 and fr['bands']['b_lo'] == 600301,
   "row_faces_detail": row_faces,
  },
  "w264_finalize_product_present": w264_finalize_present,
 },
 "ledger_pre": {
  "prev_total": prev_total, "prev_merged_n": prev_k,
  "expect_total": expect_total, "expect_merged": expect_merged,
  "source": "W264 finalize actuals machine-read from n1_w264_results.json (r587 law)",
  "freeze_receipt_upstream_face_match": upstream_match,
  "anchor": "W264 finalize (bm-c r1076/r1077 one-pass 1,005,135/K=578,720) honored per freeze receipt w264_upstream face",
 },
}

ok = (all(row_faces.values()) and all(v >= 1 for v in fam.values()) and boundary
      and w264_finalize_present
      and pf_now == fr['pf_sha16_post'] and n1_now == fr['n1_sha16_post']
      and n1_crnorm_equal and pf_crnorm_equal and pf_diff_empty
      and len(shards) == 12 and sizes_ok
      and r_banned.returncode == 0 and r_pf.returncode == 0 and r_n1.returncode == 0
      and upstream_match and prev_total == 1005135 and prev_k == 578720)
out['verdict'] = 'ALL PASS' if ok else 'FAIL'
io.open('results/_r1084bmc_w265_sixgate.json', 'w', encoding='utf-8').write(
    json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps({"verdict": out['verdict'],
                  "row_faces": row_faces, "fam": fam, "boundary": boundary,
                  "shards": len(shards), "sizes_ok": sizes_ok,
                  "banned_rc": r_banned.returncode,
                  "pf_selftest_rc": r_pf.returncode,
                  "n1_selftest_rc": r_n1.returncode,
                  "n1_crnorm_equal": n1_crnorm_equal,
                  "pf_crnorm_equal": pf_crnorm_equal,
                  "pf_now_eq_receipt": pf_now == fr['pf_sha16_post'],
                  "n1_now_eq_receipt": n1_now == fr['n1_sha16_post'],
                  "ledger_pre": out['ledger_pre']}, indent=1))
raise SystemExit(0 if ok else 1)
