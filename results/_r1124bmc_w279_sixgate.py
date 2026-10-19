# -*- coding: utf-8 -*-
# r1124 bm-c: W279 PRE-FINALIZE six-gate receipt (standing law since W217
# debt; clone lineage _r1118bmc_w278_sixgate.py, 42nd consecutive
# PRE-FINALIZE correct-phase target). Burn landed by resident engine
# mtime-watch auto-ignite post-W279 splice (splice commit 3810f4a7ac landed
# behind=0 at push (authored 61a65dd55d, mid-window rebase per r1123 verify
# face); engine
# appender shards self-commit per the W272 estate precedent (batches
# 498d178d0b six + 332e8e8656 six, both on origin; finalize not yet run).
# CLEAN-AT-BIRTH FACE (12th consecutive) on ENGINE MECHANICS: the W279
# splice carried ZERO heals of any class -- zero post-splice heals on pf/n1,
# zero pre-splice editor heals (E63 23rd-gen editor CLEAN-AT-BIRTH; needle
# preflight FIRST-RUN one disclosed table-heal = push-race- x2 delivery prose
# forms, expectation-table face only, zero canon anomalies; phase4
# zero-residual + phase5 presence gates ALL PASS; setwave root-cure held
# at the birth station (_set_wave(278):1 / _set_wave(277):0 / _set_wave(276):0
# whole-file).
# Gate-1 asserts: (a) worktree n1/pf sha16 == freeze-receipt post faces;
# (b) CR-normalized worktree == CR-normalized landed blob @ splice commit
# (landed blob = LF-normalized storage face, known clean divergence --
# raw-byte sha16 of the landed LF face recorded for the receipt);
# (c) segment-scoped birth-station presence gates after the W278 block:
# _set_wave(279) present, _set_wave(278)/_set_wave(277) absent.
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


SPLICE = '3810f4a7ac2ece994246cac557c901511bab5121'
fr = json.load(io.open('results/_w279bmc_freeze_receipt.json', encoding='utf-8'))
pf_now = sha16('scripts/perpetual_faces.py')
n1_now = sha16('scripts/perpetual_faces_n1.py')

n1t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = n1t.find('279: {"batch": "PERPETUAL-N1-W279"')
assert i >= 0, 'W279 wave row missing'
seg = n1t[i:i + 9000]
if '280: {' in seg:
    seg = seg[:seg.find('280: {')]
row_faces = {
    'a_seed_base_629101': '629101' in seg,
    'b_exit_seed_base_631101': '631101' in seg,
    'shard_subdir_n1_w279': 'n1_w279' in seg,
    'out_name_n1_w279_results': 'n1_w279_results.json' in seg,
    'engine_owner_bm_c': 'engine_owner": "bm-c"' in seg,
}
f1 = 'base=629101 span=2000'
f2 = 'base=631101 span=200'
fam = {f1: n1t.count(f1), f2: n1t.count(f2)}

# prior-wave W278 registry boundary faces kept
m278 = re.search(r'278: \{"batch": "PERPETUAL-N1-W278"', n1t)
w278_seg = n1t[m278.start():m278.start() + 9000] if m278 else ''
if '279: {' in w278_seg:
    w278_seg = w278_seg[:w278_seg.find('279: {')]
boundary = bool(m278) and '626901' in w278_seg and '628901' in w278_seg

# setwave birth-station presence gates (segment-scoped, editor phase5 face)
k278pos = n1t.rfind('_set_wave(278)')
after278 = n1t[k278pos + len('_set_wave(278)'):]
setwave_presence = {
    'w279_block_has_279': '_set_wave(279)' in after278,
    'w279_block_has_278': '_set_wave(278)' in after278,
    'w279_block_has_277': '_set_wave(277)' in after278,
    'whole_file_279_count': n1t.count('_set_wave(279)'),
    'whole_file_278_count': n1t.count('_set_wave(278)'),
    'whole_file_277_count': n1t.count('_set_wave(277)'),
}
setwave_ok = (setwave_presence['w279_block_has_279']
              and not setwave_presence['w279_block_has_278']
              and not setwave_presence['w279_block_has_277']
              and setwave_presence['whole_file_279_count'] == 1
              and setwave_presence['whole_file_278_count'] == 1
              and setwave_presence['whole_file_277_count'] == 1)

sd = 'results/p2cal_ext/n1_w279'
shards = sorted(f for f in os.listdir(sd) if f.startswith('shard-') and f.endswith('.json'))
sizes_ok = all(os.path.getsize(os.path.join(sd, f)) > 100000 for f in shards)

r_banned = subprocess.run([sys.executable, 'Tools/banned_direction_gate.py',
                           '--prereg', 'research/PERPETUAL_N1_W279_PREREG.md'],
                          capture_output=True, text=True)
r_pf = subprocess.run([sys.executable, 'scripts/perpetual_faces.py', 'selftest'],
                      capture_output=True, text=True)
r_n1 = subprocess.run([sys.executable, 'scripts/perpetual_faces_n1.py', 'selftest'],
                      capture_output=True, text=True)
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
r_git_pf_diff = subprocess.run(['git', 'diff', SPLICE, '--',
                                'scripts/perpetual_faces.py'],
                               capture_output=True, text=True)
pf_diff_empty = (len((r_git_pf_diff.stdout or '').strip()) == 0
                and r_git_pf_diff.returncode == 0)

clean_state_ok = (n1_now == fr['n1_sha16_post'] and pf_now == fr['pf_sha16_post'])
birth_evidence_ok = (os.path.exists('results/_w279bmc_derive_editor.py')
                     and os.path.exists('results/_r1123bmc_derive_editor_log.txt')
                     and os.path.exists('results/_r1123bmc_needle_preflight.json'))

n1_vs_receipt_note = (
    'r1124 GATE-1 CLEAN-AT-BIRTH FACE (12th consecutive) on ENGINE MECHANICS: '
    'the W279 splice carried ZERO heals of any class -- zero post-splice '
    'heals on pf/n1, zero pre-splice editor heals (E63 23rd-gen editor '
    'CLEAN-AT-BIRTH; needle preflight FIRST-RUN one disclosed table-heal '
    '= push-race- x2 delivery prose forms, expectation-table face only, '
    'zero canon anomalies). Phase4 zero-residual + phase5 presence gates '
    'ALL PASS at editor time. Gate asserts worktree sha16 == freeze-receipt '
    'post faces, CR-normalized worktree == CR-normalized landed blob @ '
    'splice commit 3810f4a7ac (landed = LF storage face, raw sha16 '
    'recorded; engine batches 498d178d0b + 332e8e8656 self-committed '
    'post-splice), segment-scoped birth-station presence gates green, '
    'editor/preflight/log evidence files present.'
)

# ledger_pre: machine-read from W278 finalize product (r587 never-transcribe)
w278 = json.load(io.open('results/perpetual_faces/n1_w278_results.json',
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


ledger_w278 = _find_ledger(w278)
assert ledger_w278 is not None, 'W278 ledger face missing'
prev_total = ledger_w278['total']
prev_k = w278['null_pool_cumulative']['merged']['n_values']
expect_total = prev_total + 2200
expect_merged = prev_k + 2200
up = fr['w278_upstream']
upstream_match = (up['ledger_total'] == prev_total and up['merged_n'] == prev_k)

w278_finalize_present = os.path.exists('results/perpetual_faces/n1_w278_results.json')
out = {
 "machine": "bm-c",
 "wave": 279,
 "phase": "PRE-FINALIZE six-gate (r1124 bm-c own-seat window, 42nd consecutive correct-phase target; standing law -- engine self-burn 12/12 landed post-W279 splice 3810f4a7ac clean-at-birth 12th generation on engine mechanics, finalize not yet run)",
 "gates": {
  "splice_integrity": {
   "bands_facts_match_freeze_receipt": all(row_faces.values()),
   "pf_sha16_now": pf_now, "n1_sha16_now": n1_now,
   "pf_sha16_freeze_post": fr['pf_sha16_post'],
   "n1_sha16_freeze_post": fr['n1_sha16_post'],
   "n1_sha16_landed_commit_lf_face": n1_landed,
   "pf_sha16_landed_commit_lf_face": pf_landed,
   "clean_at_birth": {
    "source": "freeze receipt post faces (zero heals of any class this generation -- zero post-splice engine-mechanics heals, zero pre-splice editor heals (E63 23rd-gen editor CLEAN-AT-BIRTH), needle preflight FIRST-RUN one disclosed table-heal = push-race- x2 delivery prose forms, expectation-table face only; setwave root cure held at the birth station)",
    "n1_sha16_now": n1_now,
    "receipt_sha16_post": fr['n1_sha16_post'],
    "clean_state_ok": clean_state_ok,
    "crnorm_worktree_eq_landed": n1_crnorm_equal,
    "birth_station_presence_gates": setwave_presence,
    "evidence_files_present": birth_evidence_ok,
    "phase": "post-splice post-burn PRE-finalize (engine mechanics untouched; r1076-family recurrence prevented at birth, zero engine-mechanics heal face)",
   },
   "pf_crnorm_equal_worktree_vs_landed": pf_crnorm_equal,
   "pf_landed_diff_empty": pf_diff_empty,
   "n1_vs_receipt_disclosure": n1_vs_receipt_note,
   "family_seed_faces": fam,
   "prior_wave_278_boundary_kept": boundary,
  },
  "banned": {"rc": r_banned.returncode, "stdout_tail": (r_banned.stdout or '').strip()[-200:]},
  "pf_selftest": {"rc": r_pf.returncode, "stdout_tail": (r_pf.stdout or '').strip()[-120:]},
  "n1_selftest": {"rc": r_n1.returncode, "stdout_tail": (r_n1.stdout or '').strip()[-120:]},
  "shards": {"present": len(shards), "of": 12, "sizes_above_100k": sizes_ok,
             "files": shards},
  "seed_admit": {
   "freeze_gate_lines": fr.get('seed_admit_gate'),
   "note": "freeze-time FREE evidence consumed verbatim from _w279bmc_freeze_receipt.json (both bands); whole-file per-span family faces count-asserted",
  },
  "wave_configs_row": {
   "present": True, "engine_owner": "bm-c",
   "a_seed_base": 629101, "b_exit_seed_base": 631101,
   "shard_subdir": "n1_w279", "out_name": "n1_w279_results.json",
   "seed_bases_match_freeze_bands": fr['bands']['a_lo'] == 629101 and fr['bands']['b_lo'] == 631101,
   "row_faces_detail": row_faces,
  },
  "w278_finalize_product_present": w278_finalize_present,
 },
 "ledger_pre": {
  "prev_total": prev_total, "prev_merged_n": prev_k,
  "expect_total": expect_total, "expect_merged": expect_merged,
  "source": "W278 finalize actuals machine-read from n1_w278_results.json (r587 law)",
  "freeze_receipt_upstream_face_match": upstream_match,
  "anchor": "W278 finalize (bm-c r1119 one-pass 1,035,935/K=609,520) honored per freeze receipt w278_upstream face",
 },
}

ok = (all(row_faces.values()) and all(v >= 1 for v in fam.values()) and boundary
      and w278_finalize_present
      and pf_now == fr['pf_sha16_post'] and pf_diff_empty and pf_crnorm_equal
      and clean_state_ok and n1_crnorm_equal and birth_evidence_ok and setwave_ok
      and len(shards) == 12 and sizes_ok
      and r_banned.returncode == 0 and r_pf.returncode == 0 and r_n1.returncode == 0
      and upstream_match and prev_total == 1035935 and prev_k == 609520)
out['verdict'] = 'ALL PASS' if ok else 'FAIL'
io.open('results/_r1124bmc_w279_sixgate.json', 'w', encoding='utf-8').write(
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
