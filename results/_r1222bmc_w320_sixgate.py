# -*- coding: utf-8 -*-
# r1222 bm-c: W320 PRE-FINALIZE six-gate receipt (83rd consecutive correct-phase
# target). Lineage _r1219bmc_w319_sixgate.py; every wave/band/ledger literal is
# written EXPLICITLY (r1168/r1171/r1184/r1208 family: no cascade, no reuse of the
# clone's previous-wave numerals).
import hashlib
import io
import json
import os
import re
import subprocess
import sys

WAVE = 320
PREVTOTAL_LIT, PREVK_LIT = 1126141, 699720


def sha16(p):
    return hashlib.sha256(io.open(p, 'rb').read()).hexdigest()[:16]


def crnorm(b):
    return b.replace(b'\r\n', b'\n')


_r = subprocess.run(['git', 'log', '--format=%H', '--grep', 'W320 five-face splice', '-1'],
                    capture_output=True, text=True, encoding='utf-8', errors='replace')
SPLICE = ((_r.stdout or '').strip().splitlines() or [''])[0]
assert re.match(r'^[0-9a-f]{40}$', SPLICE), f'splice commit not resolvable: {SPLICE!r}'
fr = json.load(io.open('results/_w320bmc_freeze_receipt.json', encoding='utf-8'))
assert fr['bands']['A'] == [719301, 721300] and fr['bands']['B'] == [721301, 721500], fr['bands']
A_BASE, B_BASE = fr['bands']['A'][0], fr['bands']['B'][0]
pf_now = sha16('scripts/perpetual_faces.py')
n1_now = sha16('scripts/perpetual_faces_n1.py')

n1t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = n1t.find('320: {"batch": "PERPETUAL-N1-W320"')
assert i >= 0, 'W320 wave row missing'
seg = n1t[i:i + 12000]
if '321: {' in seg:   # r1179/r1199 self-reference: cut on the NEXT row
    seg = seg[:seg.find('321: {')]
row_faces = {
    'a_seed_base_719301': '719301' in seg,
    'b_exit_seed_base_721301': '721301' in seg,
    'shard_subdir_n1_w320': 'n1_w320' in seg,
    'out_name_n1_w320_results': 'n1_w320_results.json' in seg,
    'engine_owner_bm_c': 'engine_owner=bm-c' in seg,
}
f1 = 'law sec.4 W320 A: 719_301..721_300'
f2 = 'law sec.4 W320 B: 721_301..721_500'
fam = {f1: n1t.count(f1), f2: n1t.count(f2)}

# prior-wave W319 registry boundary faces kept
m319 = re.search(r'319: \{"batch": "PERPETUAL-N1-W319"', n1t)
w319_seg = n1t[m319.start():m319.start() + 12000] if m319 else ''
if '320: {' in w319_seg:
    w319_seg = w319_seg[:w319_seg.find('320: {')]
boundary = bool(m319) and '717101' in w319_seg and '719101' in w319_seg

# setwave birth-station presence gates (segment-scoped)
k319pos = n1t.rfind('_set_wave(319)')
after319 = n1t[k319pos + len('_set_wave(319)'):]
setwave_presence = {
    'w320_block_has_320': '_set_wave(320)' in after319,
    'w320_block_has_319': '_set_wave(319)' in after319,
    'w320_block_has_308': '_set_wave(308)' in after319,
    'whole_file_320_count': n1t.count('_set_wave(320)'),
    'whole_file_319_count': n1t.count('_set_wave(319)'),
    'whole_file_308_count': n1t.count('_set_wave(308)'),
}
setwave_ok = (setwave_presence['w320_block_has_320']
              and not setwave_presence['w320_block_has_319']
              and not setwave_presence['w320_block_has_308']
              and setwave_presence['whole_file_320_count'] == 1
              and setwave_presence['whole_file_319_count'] == 1
              and setwave_presence['whole_file_308_count'] == 1)

sd = 'results/p2cal_ext/n1_w320'
shards = sorted(f for f in os.listdir(sd) if f.startswith('shard-') and f.endswith('.json'))
sizes_ok = all(os.path.getsize(os.path.join(sd, f)) > 100000 for f in shards)

r_banned = subprocess.run([sys.executable, 'Tools/banned_direction_gate.py',
                           '--prereg', 'research/PERPETUAL_N1_W320_PREREG.md'],
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
n1_crnorm_equal = crnorm(wt_n1_bytes) == crnorm(r_git_n1.stdout)
pf_crnorm_equal = crnorm(wt_pf_bytes) == crnorm(r_git_pf.stdout)
r_git_pf_diff = subprocess.run(['git', 'diff', SPLICE, '--', 'scripts/perpetual_faces.py'],
                               capture_output=True, text=True, encoding='utf-8', errors='replace')
pf_diff_empty = (len((r_git_pf_diff.stdout or '').strip()) == 0
                 and r_git_pf_diff.returncode == 0)

adj_path = 'results/_n1_face_adjudication_w320.json'
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
                                  'note': ('raw face equality is EOL-invalid post-commit and, for '
                                           'n1, pre-heal by construction (r1221 heal after receipt); '
                                           'kept for disclosure only')},
}
birth_evidence_ok = (os.path.exists('results/_w320bmc_prereg_derive.py')
                     and os.path.exists('Tools/n1_seat_probe.py')
                     and os.path.exists('results/_w320bmc_20261025_probe_receipt.json')
                     and os.path.exists('results/_w320bmc_freeze_edits.py')
                     and os.path.exists('results/_w320bmc_freeze_receipt.json'))

prev = json.load(io.open('results/perpetual_faces/n1_w319_results.json', encoding='utf-8'))


def _find_ledger(obj):
    if isinstance(obj, dict):
        if 'ledger' in obj and isinstance(obj['ledger'], dict) and 'total' in obj['ledger']:
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


ledger_prev = _find_ledger(prev)
assert ledger_prev is not None, 'W319 ledger face missing'
prev_total = ledger_prev['total']
prev_k = prev['null_pool_cumulative']['merged']['n_values']
expect_total = prev_total + 2200
expect_merged = prev_k + 2200
up = fr['upstream_w319']
upstream_match = (up['ledger_total'] == prev_total and up['merged_n'] == prev_k)

prev_finalize_present = os.path.exists('results/perpetual_faces/n1_w319_results.json')
out = {
 "machine": "bm-c",
 "wave": WAVE,
 "phase": ("PRE-FINALIZE six-gate (r1222 bm-c own-seat window, 83rd consecutive "
           "correct-phase target; engine self-burn 12/12 landed post-W320 splice "
           f"{SPLICE[:10]}, finalize not yet run)"),
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
               "adjudication (r1188 law: receipt post faces are pre-commit CRLF faces; the n1 "
               "post face is additionally PRE-HEAL, proved by byte-exact reverse application)"),
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
   "prior_wave_319_boundary_kept": boundary,
  },
  "banned": {"rc": r_banned.returncode, "stdout_tail": (r_banned.stdout or '').strip()[-200:]},
  "pf_selftest": {"rc": r_pf.returncode, "stdout_tail": (r_pf.stdout or '').strip()[-120:]},
  "n1_selftest": {"rc": r_n1.returncode, "stdout_tail": (r_n1.stdout or '').strip()[-120:]},
  "shards": {"present": len(shards), "of": 12, "sizes_above_100k": sizes_ok, "files": shards},
  "seed_admit": {
   "freeze_gate_lines": fr.get('seed_admit_gate'),
   "note": ("freeze-time FREE evidence consumed verbatim from _w320bmc_freeze_receipt.json "
            "(both bands); whole-file per-span family faces count-asserted"),
  },
  "wave_configs_row": {
   "present": True, "engine_owner": "bm-c",
   "a_seed_base": A_BASE, "b_exit_seed_base": B_BASE,
   "shard_subdir": "n1_w320", "out_name": "n1_w320_results.json",
   "seed_bases_match_freeze_bands": fr['bands']['A'][0] == A_BASE and fr['bands']['B'][0] == B_BASE,
   "row_faces_detail": row_faces,
  },
  "w319_finalize_product_present": prev_finalize_present,
 },
 "ledger_pre": {
  "prev_total": prev_total, "prev_merged_n": prev_k,
  "expect_total": expect_total, "expect_merged": expect_merged,
  "source": "W319 finalize actuals machine-read from n1_w319_results.json (r587 law)",
  "freeze_receipt_upstream_face_match": upstream_match,
  "anchor": "W319 finalize (bm-c r1219 one-pass 1,126,141/K=699,720) honored per freeze receipt upstream_w319 face",
 },
}

ok = (all(row_faces.values()) and all(v >= 1 for v in fam.values()) and boundary
      and prev_finalize_present
      and pf_diff_empty and pf_crnorm_equal
      and clean_state_ok and n1_crnorm_equal and birth_evidence_ok and setwave_ok
      and len(shards) == 12 and sizes_ok
      and r_banned.returncode == 0 and r_pf.returncode == 0 and r_n1.returncode == 0
      and upstream_match and prev_total == PREVTOTAL_LIT and prev_k == PREVK_LIT)
out['verdict'] = 'ALL PASS' if ok else 'FAIL'
io.open('results/_r1222bmc_w320_sixgate.json', 'w', encoding='utf-8', newline='\n').write(
    json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps({"verdict": out['verdict'],
                  "row_faces": row_faces, "fam": fam, "boundary": boundary,
                  "shards": len(shards), "sizes_ok": sizes_ok,
                  "banned_rc": r_banned.returncode,
                  "pf_selftest_rc": r_pf.returncode,
                  "n1_selftest_rc": r_n1.returncode,
                  "clean_state_ok": clean_state_ok,
                  "setwave_presence": setwave_presence,
                  "ledger_pre": out['ledger_pre']}, indent=1))
raise SystemExit(0 if ok else 1)