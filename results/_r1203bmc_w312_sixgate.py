# -*- coding: utf-8 -*-
# r1203 bm-c: W312 PRE-FINALIZE six-gate receipt (standing law since W217 debt;
# lineage _r1201bmc_w311_sixgate.py, 75th consecutive PRE-FINALIZE correct-phase
# target). Burn landed live by the resident engine mtime-watch auto-ignite post-W312
# splice (12/12 shards, shard-7/9/10 finished 17:22:48-49); finalize not yet run.
import hashlib
import io
import json
import os
import re
import subprocess
import sys

WAVE = 312
PREV = 311
A_BASE, B_BASE = 701701, 703701
PREV_TOTAL, PREV_K = 1108541, 682120


def sha16(p):
    return hashlib.sha256(io.open(p, 'rb').read()).hexdigest()[:16]


def crnorm(b):
    return b.replace(b'\r\n', b'\n')


# live-derived (r1188 heal): a rebased splice commit turns a hardcoded sha into a
# stale face -- derive it from the commit message (zero transcription).
_r = subprocess.run(['git', 'log', '--format=%H', '--grep', 'W312 five-face freeze splice', '-1'],
                    capture_output=True, text=True, encoding='utf-8', errors='replace')
SPLICE = ((_r.stdout or '').strip().splitlines() or [''])[0]
assert re.match(r'^[0-9a-f]{40}$', SPLICE), f'splice commit not resolvable: {SPLICE!r}'
fr = json.load(io.open('results/_w312bmc_freeze_receipt.json', encoding='utf-8'))
pf_now = sha16('scripts/perpetual_faces.py')
n1_now = sha16('scripts/perpetual_faces_n1.py')

n1t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = n1t.find('312: {"batch": "PERPETUAL-N1-W312"')
assert i >= 0, 'W312 wave row missing'
seg = n1t[i:i + 12000]
if '313: {' in seg:   # r1179 heal: cut on the NEXT row
    seg = seg[:seg.find('313: {')]
row_faces = {
    'a_seed_base_701701': '701701' in seg,
    'b_exit_seed_base_703701': '703701' in seg,
    'shard_subdir_n1_w312': 'n1_w312' in seg,
    'out_name_n1_w312_results': 'n1_w312_results.json' in seg,
    'engine_owner_bm_c': 'engine_owner=bm-c' in seg,
}
f1 = 'law sec.4 W312 A: 701_701..703_700'
f2 = 'law sec.4 W312 B: 703_701..703_900'
fam = {f1: n1t.count(f1), f2: n1t.count(f2)}

# prior-wave W311 registry boundary faces kept
m310 = re.search(r'311: \{"batch": "PERPETUAL-N1-W311"', n1t)
w311_seg = n1t[m310.start():m310.start() + 12000] if m310 else ''
if '312: {' in w311_seg:
    w311_seg = w311_seg[:w311_seg.find('312: {')]
boundary = bool(m310) and '699501' in w311_seg and '701501' in w311_seg

# setwave birth-station presence gates (segment-scoped): the W312 block must sit
# after the W311 block's own setwave and carry exactly its own wave pin.
k311pos = n1t.rfind('_set_wave(311)')
after311 = n1t[k311pos + len('_set_wave(311)'):]
setwave_presence = {
    'w312_block_has_312': '_set_wave(312)' in after311,
    'w312_block_has_311': '_set_wave(311)' in after311,
    'w312_block_has_305': '_set_wave(305)' in after311,
    'whole_file_312_count': n1t.count('_set_wave(312)'),
    'whole_file_311_count': n1t.count('_set_wave(311)'),
    'whole_file_305_count': n1t.count('_set_wave(305)'),
}
setwave_ok = (setwave_presence['w312_block_has_312']
              and not setwave_presence['w312_block_has_311']
              and not setwave_presence['w312_block_has_305']
              and setwave_presence['whole_file_312_count'] == 1
              and setwave_presence['whole_file_311_count'] == 1
              and setwave_presence['whole_file_305_count'] == 1)

sd = 'results/p2cal_ext/n1_w312'
shards = sorted(f for f in os.listdir(sd) if f.startswith('shard-') and f.endswith('.json'))
sizes_ok = all(os.path.getsize(os.path.join(sd, f)) > 100000 for f in shards)

r_banned = subprocess.run([sys.executable, 'Tools/banned_direction_gate.py',
                           '--prereg', 'research/PERPETUAL_N1_W312_PREREG.md'],
                          capture_output=True, text=True, encoding='utf-8', errors='replace')
r_pf = subprocess.run([sys.executable, 'scripts/perpetual_faces.py', 'selftest'],
                      capture_output=True, text=True, encoding='utf-8', errors='replace')
r_n1 = subprocess.run([sys.executable, 'scripts/perpetual_faces_n1.py', 'selftest'],
                      capture_output=True, text=True, encoding='utf-8', errors='replace')
r_git_n1 = subprocess.run(['git', 'show', f'{SPLICE}:scripts/perpetual_faces_n1.py'],
                          capture_output=True)
r_git_pf = subprocess.run(['git', 'show', f'{SPLICE}:scripts/perpetual_faces.py'],
                          capture_output=True)
n1_landed = hashlib.sha256(r_git_n1.stdout).hexdigest()[:16]
pf_landed = hashlib.sha256(r_git_pf.stdout).hexdigest()[:16]
wt_n1_bytes = io.open('scripts/perpetual_faces_n1.py', 'rb').read()
wt_pf_bytes = io.open('scripts/perpetual_faces.py', 'rb').read()
n1_crnorm_equal = crnorm(wt_n1_bytes.replace(b'\r\n', b'\n')) == crnorm(r_git_n1.stdout)
pf_crnorm_equal = crnorm(wt_pf_bytes.replace(b'\r\n', b'\n')) == crnorm(r_git_pf.stdout)
r_git_pf_diff = subprocess.run(['git', 'diff', SPLICE, '--',
                               'scripts/perpetual_faces.py'],
                               capture_output=True, text=True, encoding='utf-8', errors='replace')
pf_diff_empty = (len((r_git_pf_diff.stdout or '').strip()) == 0
                 and r_git_pf_diff.returncode == 0)

# clean-state v2 (r1188 heal): CR-normalized worktree vs landed + replay adjudication.
adj_path = 'results/_n1_face_adjudication_w312.json'
adj = json.load(io.open(adj_path, encoding='utf-8')) if os.path.exists(adj_path) else {}
adj_ok = (adj.get('verdict') == 'PASS'
          and adj.get('post_faces_match_receipt') is True
          and not adj.get('unexplained_deltas'))
clean_state_ok = (n1_crnorm_equal and pf_crnorm_equal and adj_ok)
clean_state_detail = {
    'n1_crnorm_worktree_eq_landed': n1_crnorm_equal,
    'pf_crnorm_worktree_eq_landed': pf_crnorm_equal,
    'freeze_face_adjudication': {'path': adj_path, 'verdict': adj.get('verdict'),
                                 'adj_ok': bool(adj_ok),
                                 'replay_lf_eq_landed': adj.get('replay_lf_eq_landed'),
                                 'heal_delta_count': len(adj.get('heal_deltas') or []),
                                 'unexplained_delta_count': len(adj.get('unexplained_deltas') or [])},
    'raw_receipt_face_equality': {'n1': n1_now == fr['n1_sha16_post'],
                                  'pf': pf_now == fr['pf_sha16_post'],
                                  'note': ('raw face equality is EOL-invalid post-commit '
                                           'under autocrlf; kept for disclosure only')},
}
birth_evidence_ok = (os.path.exists('results/_w312bmc_prereg_derive.py')
                     and os.path.exists('Tools/n1_seat_probe.py')
                     and os.path.exists('results/_w312bmc_20261024_probe_receipt.json')
                     and os.path.exists('results/_w312bmc_freeze_edits.py')
                     and os.path.exists('results/_w312bmc_freeze_receipt.json'))

# ledger_pre: machine-read from W311 finalize product (r587 never-transcribe)
w311 = json.load(io.open('results/perpetual_faces/n1_w311_results.json',
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


ledger_w311 = _find_ledger(w311)
assert ledger_w311 is not None, 'W311 ledger face missing'
prev_total = ledger_w311['total']
prev_k = w311['null_pool_cumulative']['merged']['n_values']
expect_total = prev_total + 2200
expect_merged = prev_k + 2200
up = fr['upstream_w311']
upstream_match = (up['ledger_total'] == prev_total and up['merged_n'] == prev_k)

w311_finalize_present = os.path.exists('results/perpetual_faces/n1_w311_results.json')
out = {
 "machine": "bm-c",
 "wave": WAVE,
 "phase": ("PRE-FINALIZE six-gate (r1203 bm-c own-seat window, 75th consecutive "
           "correct-phase target; standing law -- engine self-burn 12/12 landed "
           f"post-W312 splice {SPLICE[:10]}, finalize not yet run)"),
 "gates": {
  "splice_integrity": {
   "bands_facts_match_freeze_receipt": all(row_faces.values()),
   "pf_sha16_now": pf_now, "n1_sha16_now": n1_now,
   "pf_sha16_freeze_post": fr['pf_sha16_post'],
   "n1_sha16_freeze_post": fr['n1_sha16_post'],
   "n1_sha16_landed_commit_lf_face": n1_landed,
   "pf_sha16_landed_commit_lf_face": pf_landed,
   "clean_state": {
    "source": ("CR-normalized worktree vs landed blob + mechanical freeze-face replay "
               "adjudication (r1188 law: receipt post faces are pre-commit CRLF faces; "
               "r1189 single-stamp replay + receipt-anchored parity-count heal)"),
    "detail": clean_state_detail,
    "n1_sha16_now": n1_now,
    "receipt_sha16_post": fr['n1_sha16_post'],
    "clean_state_ok": clean_state_ok,
    "crnorm_worktree_eq_landed": n1_crnorm_equal,
    "birth_station_presence_gates": setwave_presence,
    "evidence_files_present": birth_evidence_ok,
    "phase": "post-splice post-burn PRE-finalize (engine mechanics untouched)",
   },
   "pf_crnorm_equal_worktree_vs_landed": pf_crnorm_equal,
   "pf_landed_diff_empty": pf_diff_empty,
   "family_seed_faces": fam,
   "prior_wave_311_boundary_kept": boundary,
  },
  "banned": {"rc": r_banned.returncode, "stdout_tail": (r_banned.stdout or '').strip()[-200:]},
  "pf_selftest": {"rc": r_pf.returncode, "stdout_tail": (r_pf.stdout or '').strip()[-120:]},
  "n1_selftest": {"rc": r_n1.returncode, "stdout_tail": (r_n1.stdout or '').strip()[-120:]},
  "shards": {"present": len(shards), "of": 12, "sizes_above_100k": sizes_ok,
             "files": shards},
  "seed_admit": {
   "freeze_gate_lines": fr.get('seed_admit_gate'),
   "note": ("freeze-time FREE evidence consumed verbatim from _w312bmc_freeze_receipt.json "
            "(both bands); whole-file per-span family faces count-asserted"),
  },
  "wave_configs_row": {
   "present": True, "engine_owner": "bm-c",
   "a_seed_base": A_BASE, "b_exit_seed_base": B_BASE,
   "shard_subdir": "n1_w312", "out_name": "n1_w312_results.json",
   "seed_bases_match_freeze_bands": fr['bands']['A'][0] == A_BASE and fr['bands']['B'][0] == B_BASE,
   "row_faces_detail": row_faces,
  },
  "w311_finalize_product_present": w311_finalize_present,
 },
 "ledger_pre": {
  "prev_total": prev_total, "prev_merged_n": prev_k,
  "expect_total": expect_total, "expect_merged": expect_merged,
  "source": "W311 finalize actuals machine-read from n1_w311_results.json (r587 law)",
  "freeze_receipt_upstream_face_match": upstream_match,
  "anchor": "W311 finalize (bm-c r1201 one-pass 1,108,541/K=682,120) honored per freeze receipt upstream_w311 face",
 },
}

ok = (all(row_faces.values()) and all(v >= 1 for v in fam.values()) and boundary
      and w311_finalize_present
      and pf_diff_empty and pf_crnorm_equal
      and clean_state_ok and n1_crnorm_equal and birth_evidence_ok and setwave_ok
      and len(shards) == 12 and sizes_ok
      and r_banned.returncode == 0 and r_pf.returncode == 0 and r_n1.returncode == 0
      and upstream_match and prev_total == PREV_TOTAL and prev_k == PREV_K)
out['verdict'] = 'ALL PASS' if ok else 'FAIL'
io.open('results/_r1203bmc_w312_sixgate.json', 'w', encoding='utf-8', newline='\n').write(
    json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps({"verdict": out['verdict'],
                  "row_faces": row_faces, "fam": fam, "boundary": boundary,
                  "shards": len(shards), "sizes_ok": sizes_ok,
                  "banned_rc": r_banned.returncode,
                  "pf_selftest_rc": r_pf.returncode,
                  "n1_selftest_rc": r_n1.returncode,
                  "clean_state_ok": clean_state_ok,
                  "crnorm_worktree_eq_landed": n1_crnorm_equal,
                  "pf_crnorm_equal": pf_crnorm_equal,
                  "setwave_presence": setwave_presence,
                  "ledger_pre": out['ledger_pre']}, indent=1))
raise SystemExit(0 if ok else 1)