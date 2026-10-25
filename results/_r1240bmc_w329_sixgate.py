# -*- coding: utf-8 -*-
# r1240 bm-c: W329 PRE-FINALIZE six-gate receipt (93rd consecutive correct-phase target).
# Lineage results/_r1238bmc_w328_sixgate.py; every wave/band/ledger literal is written
# EXPLICITLY (r1168/r1171/r1184/r1208/r1240 family: no cascade, no reuse of the clone's
# previous-wave numerals). Face classes handled per r1208/r1240 law:
#   token faces   -> written as the TARGET wave (W329 / w329)
#   plain-digit   -> written as the TARGET wave (329) -- never via a token map
#   prior-wave    -> written as the PREVIOUS wave (W328 / 328) which is now the
#                    registered boundary face to prove kept
# This window inherits the r1239 estate (freeze + splice committed 624c3d99a9, engine
# self-burnt 12/12); the cycle closure (adjudication / six-gate / finalize / fivekeys /
# W330 seat) is executed here.
import hashlib
import io
import json
import os
import re
import subprocess
import sys

WAVE = 329
PREVTOTAL_LIT, PREVK_LIT = 1145941, 719520
A_LO, A_HI = 742701, 744700
B_LO, B_HI = 744701, 744900
PRIOR_A, PRIOR_B = 740501, 742501


def sha16(p):
    return hashlib.sha256(io.open(p, 'rb').read()).hexdigest()[:16]


def crnorm(b):
    return b.replace(b'\r\n', b'\n')


_r = subprocess.run(['git', 'log', '--format=%H', '--grep', 'W329 five-face freeze splice', '-1'],
                    capture_output=True, text=True, encoding='utf-8', errors='replace')
SPLICE = ((_r.stdout or '').strip().splitlines() or [''])[0]
assert re.match(r'^[0-9a-f]{40}$', SPLICE), f'splice commit not resolvable: {SPLICE!r}'
fr = json.load(io.open('results/_w329bmc_freeze_receipt.json', encoding='utf-8'))
assert fr['bands']['A'] == [A_LO, A_HI] and fr['bands']['B'] == [B_LO, B_HI], fr['bands']
A_BASE, B_BASE = fr['bands']['A'][0], fr['bands']['B'][0]
pf_now = sha16('scripts/perpetual_faces.py')
n1_now = sha16('scripts/perpetual_faces_n1.py')

n1t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()

# ---- row-scoped faces (W329 is the newest registered row: the row runs to its closing brace) ----
i = n1t.rfind('329: {"batch": "PERPETUAL-N1-W329"')
assert i >= 0, 'W329 wave row missing'
seg = n1t[i:]
_nxt = seg.find('330: {')
if _nxt >= 0:
    seg = seg[:_nxt]
_eo = seg.find('"engine_owner": "bm-c"}')
seg_row = seg[:_eo + len('"engine_owner": "bm-c"}')] if _eo > 0 else seg
row_faces = {
    'a_seed_base_742701': '"a_seed_base": 742701' in seg_row,
    'b_exit_seed_base_744701': '"b_exit_seed_base": 744701' in seg_row,
    'shard_subdir_n1_w329': '"shard_subdir": "n1_w329"' in seg_row,
    'out_name_n1_w329_results': '"out_name": "n1_w329_results.json"' in seg_row,
    'engine_owner_bm_c': '"engine_owner": "bm-c"' in seg_row,
    'band_law_line_A': 'law sec.4 W329 A: 742_701..744_700' in seg_row,
    'band_law_line_B': 'law sec.4 W329 B: 744_701..744_900' in seg_row,
}
# E94 face: the row must carry THIS wave's machine truths, never the prior wave's
# (scoped to the row so the older rows that legitimately carry them are untouched)
e94 = {
    'w328_a_clause_absent_in_row': seg_row.count('law sec.4 W328 A') == 0,
    'w328_b_clause_absent_in_row': seg_row.count('law sec.4 W328 B') == 0,
    'fresh_A_first_clean_clause': seg_row.count('A base == FIRST CLEAN WINDOW 742_701') == 1,
    'fresh_B_empty_seedhop_clause': seg_row.count('EMPTY seed-hop') >= 1,
}

# materializer band-fact asserts live far below the WAVE_CONFIGS row, so they are gated
# on the whole file with exact-literal counts (r1208/r1232 law)
mat_assert = {
    'a_seed_assert_exact': n1t.count('assert WAVE_CONFIGS[329]["a_seed_base"] == 742701,'),
    'a_above_prior_b_assert': n1t.count(
        'assert 742701 > 742700, "W329 A base must sit above the prior-wave B tail"'),
    'b_seed_hop_assert_exact': n1t.count(
        'assert WAVE_CONFIGS[329]["b_exit_seed_base"] == 744701 == 744700 + 1,'),
    'b_above_prior_b_assert': n1t.count('assert 744701 > 742700,'),
}
mat_ok = all(v >= 1 for v in mat_assert.values())
f1 = 'law sec.4 W329 A: 742_701..744_700'
f2 = 'law sec.4 W329 B: 744_701..744_900'
fam = {f1: n1t.count(f1), f2: n1t.count(f2)}

# prior-wave W328 registry boundary faces kept
m328 = re.search(r'328: \{"batch": "PERPETUAL-N1-W328"', n1t)
w328_seg = n1t[m328.start():m328.start() + 12000] if m328 else ''
if '329: {' in w328_seg:
    w328_seg = w328_seg[:w328_seg.find('329: {')]
boundary = bool(m328) and str(PRIOR_A) in w328_seg and str(PRIOR_B) in w328_seg

# setwave birth-station presence gates (segment-scoped, r1208 law)
k328pos = n1t.rfind('_set_wave(328)')
after328 = n1t[k328pos + len('_set_wave(328)'):]
setwave_presence = {
    'w329_block_has_329': '_set_wave(329)' in after328,
    'w329_block_has_328': '_set_wave(328)' in after328,
    'w329_block_has_310': '_set_wave(310)' in after328,
    'whole_file_329_count': n1t.count('_set_wave(329)'),
    'whole_file_328_count': n1t.count('_set_wave(328)'),
    'whole_file_310_count': n1t.count('_set_wave(310)'),
}
setwave_ok = (setwave_presence['w329_block_has_329']
              and not setwave_presence['w329_block_has_328']
              and not setwave_presence['w329_block_has_310']
              and setwave_presence['whole_file_329_count'] == 1
              and setwave_presence['whole_file_328_count'] == 1
              and setwave_presence['whole_file_310_count'] == 1)

sd = 'results/p2cal_ext/n1_w329'
shards = sorted(f for f in os.listdir(sd) if f.startswith('shard-') and f.endswith('.json'))
sizes_ok = all(os.path.getsize(os.path.join(sd, f)) > 100000 for f in shards)

r_banned = subprocess.run([sys.executable, 'Tools/banned_direction_gate.py',
                           '--prereg', 'research/PERPETUAL_N1_W329_PREREG.md'],
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
r_git_n1_diff = subprocess.run(['git', 'diff', SPLICE, '--', 'scripts/perpetual_faces_n1.py'],
                               capture_output=True, text=True, encoding='utf-8', errors='replace')
pf_diff_empty = (len((r_git_pf_diff.stdout or '').strip()) == 0
                 and r_git_pf_diff.returncode == 0)
n1_diff_empty = (len((r_git_n1_diff.stdout or '').strip()) == 0
                 and r_git_n1_diff.returncode == 0)

adj_path = 'results/_n1_face_adjudication_w%d.json' % WAVE
adj = json.load(io.open(adj_path, encoding='utf-8')) if os.path.exists(adj_path) else {}
adj_ok = (adj.get('verdict') == 'PASS'
          and adj.get('pre_faces_match_receipt') is True
          and adj.get('post_faces_match_receipt') is True
          and adj.get('replay_lf_eq_landed') is True
          and not adj.get('unexplained_deltas')
          and not adj.get('heal_deltas'))
clean_state_ok = (n1_crnorm_equal and pf_crnorm_equal and adj_ok
                  and n1_diff_empty and pf_diff_empty)
clean_state_detail = {
    'n1_worktree_eq_landed': n1_crnorm_equal,
    'pf_worktree_eq_landed': pf_crnorm_equal,
    'n1_landed_diff_empty': n1_diff_empty,
    'pf_landed_diff_empty': pf_diff_empty,
    'no_heal_this_window': True,
    'freeze_face_adjudication': {'path': adj_path, 'verdict': adj.get('verdict'),
                                 'adj_ok': bool(adj_ok),
                                 'pre_basis': adj.get('pre_match_basis'),
                                 'post_basis': adj.get('post_match_basis'),
                                 'replay_lf_eq_landed': adj.get('replay_lf_eq_landed'),
                                 'heal_delta_count': len(adj.get('heal_deltas') or []),
                                 'unexplained_delta_count': len(adj.get('unexplained_deltas') or [])},
    'raw_receipt_face_equality': {'n1': n1_now == fr['n1_sha16_post'],
                                  'pf': pf_now == fr['pf_sha16_post'],
                                  'note': ('raw face equality holds here because the W329 '
                                           'freeze receipt and this worktree are BOTH LF-basis '
                                           '(receipt eol flags false)')},
}

birth_evidence_ok = (os.path.exists('results/_w329bmc_prereg_derive.py')
                     and os.path.exists('results/_w329bmc_freeze_edits.py')
                     and os.path.exists('results/_w329bmc_freeze_receipt.json')
                     and os.path.exists('results/_w329bmc_20261025_probe_receipt.json')
                     and os.path.exists('fleet/inbox/MSG-20261025-1005-bmc-w329-seat.md'))

prev = json.load(io.open('results/perpetual_faces/n1_w328_results.json', encoding='utf-8'))


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
assert ledger_prev is not None, 'W328 ledger face missing'
prev_total = ledger_prev['total']
prev_k = prev['null_pool_cumulative']['merged']['n_values']
expect_total = prev_total + 2200
expect_merged = prev_k + 2200
up = fr['upstream_w328']
upstream_match = (up['ledger_total'] == prev_total and up['merged_n'] == prev_k)

prev_finalize_present = os.path.exists('results/perpetual_faces/n1_w328_results.json')
out = {
 "machine": "bm-c",
 "wave": WAVE,
 "phase": ("PRE-FINALIZE six-gate (r1240 bm-c continuation window closing the W329 cycle; the "
           f"r1239 window froze+spliced {SPLICE[:10]} and the engine self-burnt 12/12, then the "
           "cycle closure is executed in this window)"),
 "gates": {
  "splice_integrity": {
   "bands_facts_match_freeze_receipt": all(row_faces.values()) and e94['w328_a_clause_absent_in_row'],
   "pf_sha16_now": pf_now, "n1_sha16_now": n1_now,
   "pf_sha16_freeze_post": fr['pf_sha16_post'],
   "n1_sha16_freeze_post": fr['n1_sha16_post'],
   "n1_sha16_landed_commit_lf_face": n1_landed,
   "pf_sha16_landed_commit_lf_face": pf_landed,
   "clean_state": {
    "source": ("CR-normalized worktree vs landed blob + empty landed diff + mechanical "
               "freeze-face replay adjudication on the receipt's DECLARED EOL basis "
               "(r1188/r1236 law)"),
    "detail": clean_state_detail,
    "clean_state_ok": bool(clean_state_ok),
    "birth_station_presence_gates": setwave_presence,
    "evidence_files_present": birth_evidence_ok,
    "phase": "post-splice post-burn PRE-finalize (engine mechanics untouched)",
   },
   "row_faces_detail": row_faces,
   "e94_row_law_face": e94,
   "materializer_band_fact_asserts": {**mat_assert, "ok": bool(mat_ok)},
   "family_seed_faces": fam,
   "prior_wave_328_boundary_kept": boundary,
  },
  "banned": {"rc": r_banned.returncode, "stdout_tail": (r_banned.stdout or '').strip()[-200:]},
  "pf_selftest": {"rc": r_pf.returncode, "stdout_tail": (r_pf.stdout or '').strip()[-120:]},
  "n1_selftest": {"rc": r_n1.returncode, "stdout_tail": (r_n1.stdout or '').strip()[-120:]},
  "shards": {"present": len(shards), "of": 12, "sizes_above_100k": sizes_ok, "files": shards},
  "seed_admit": {
   "freeze_gate_lines": fr.get('seed_admit_gate'),
   "note": ("freeze-time FREE evidence consumed verbatim from _w329bmc_freeze_receipt.json "
            "(both bands); whole-file per-span family faces count-asserted"),
  },
  "wave_configs_row": {
   "present": True, "engine_owner": "bm-c",
   "a_seed_base": A_BASE, "b_exit_seed_base": B_BASE,
   "shard_subdir": "n1_w329", "out_name": "n1_w329_results.json",
   "seed_bases_match_freeze_bands": fr['bands']['A'][0] == A_BASE and fr['bands']['B'][0] == B_BASE,
  },
  "w328_finalize_product_present": prev_finalize_present,
 },
 "ledger_pre": {
  "prev_total": prev_total, "prev_merged_n": prev_k,
  "expect_total": expect_total, "expect_merged": expect_merged,
  "source": "W328 finalize actuals machine-read from n1_w328_results.json (r587 law)",
  "freeze_receipt_upstream_face_match": upstream_match,
  "anchor": "W328 finalize (ledger 1,145,941 / K=719,520) honored per freeze receipt upstream_w328 face",
 },
}

ok = (mat_ok and all(row_faces.values()) and all(v >= 1 for v in fam.values()) and boundary
      and all(e94.values())
      and prev_finalize_present
      and pf_diff_empty and n1_diff_empty and clean_state_ok and birth_evidence_ok and setwave_ok
      and len(shards) == 12 and sizes_ok
      and r_banned.returncode == 0 and r_pf.returncode == 0 and r_n1.returncode == 0
      and upstream_match and prev_total == PREVTOTAL_LIT and prev_k == PREVK_LIT)
out['verdict'] = 'ALL PASS' if ok else 'FAIL'
io.open('results/_r1240bmc_w329_sixgate.json', 'w', encoding='utf-8', newline='\n').write(
    json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps({"verdict": out['verdict'],
                  "row_faces": row_faces, "e94": e94, "fam": fam, "boundary": boundary,
                  "mat_assert": mat_assert,
                  "shards": len(shards), "sizes_ok": sizes_ok,
                  "banned_rc": r_banned.returncode,
                  "pf_selftest_rc": r_pf.returncode,
                  "n1_selftest_rc": r_n1.returncode,
                  "clean_state_ok": clean_state_ok,
                  "n1_diff_empty": n1_diff_empty, "pf_diff_empty": pf_diff_empty,
                  "setwave_presence": setwave_presence,
                  "ledger_pre": out['ledger_pre']}, indent=1))
raise SystemExit(0 if ok else 1)