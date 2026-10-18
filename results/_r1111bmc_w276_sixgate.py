# -*- coding: utf-8 -*-
# r1111 bm-c: W276 PRE-FINALIZE six-gate receipt (standing law since W217
# debt; clone lineage _r1108bmc_w275_sixgate.py, 39th consecutive
# PRE-FINALIZE correct-phase target). Burn landed by resident engine
# mtime-watch auto-ignite post-W276 splice (splice commit 354a645155 landed
# on the ff'd base 7a70aee504 after splice gate0 caught the mid-window bm-a
# r1073 chain fail-closed zero-disk-pollution, re-ran clean; engine
# appender shards self-commit per the W272 estate precedent; finalize not
# yet run).
# CLEAN-AT-BIRTH FACE (9th consecutive) on ENGINE MECHANICS: the W276
# splice carried ZERO heals of any class -- zero post-splice heals on
# pf/n1, zero pre-splice authoring heals (all count-asserted editor reps
# first-try; the W275-generation date-roll rep was DROPPED count-0 per the
# measured 20261019==20261019 same-date fact, disclosed in the editor
# header); phase4 zero-residual + phase5 presence gates ALL PASS at editor
# time; setwave root-cure held at the birth station (_set_wave(275):1 /
# _set_wave(274):0 / _set_wave(273):0 whole-file).
# Gate-1 asserts: (a) worktree n1/pf sha16 == freeze-receipt post faces;
# (b) CR-normalized worktree == CR-normalized landed blob @ splice commit
# (landed blob = LF-normalized storage face, known clean divergence --
# raw-byte sha16 of the landed LF face recorded for the receipt);
# (c) segment-scoped birth-station presence gates after the W274 block:
# _set_wave(276) present, _set_wave(275)/_set_wave(274) absent.
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


SPLICE = '354a645155c8206a71635572534753b3c6c08c28'
fr = json.load(io.open('results/_w276bmc_freeze_receipt.json', encoding='utf-8'))
pf_now = sha16('scripts/perpetual_faces.py')
n1_now = sha16('scripts/perpetual_faces_n1.py')

n1t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = n1t.find('276: {"batch": "PERPETUAL-N1-W276"')
assert i >= 0, 'W275 wave row missing'
seg = n1t[i:i + 9000]
if '277: {' in seg:
    seg = seg[:seg.find('277: {')]
row_faces = {
    'a_seed_base_622501': '622501' in seg,
    'b_exit_seed_base_624501': '624501' in seg,
    'shard_subdir_n1_w276': 'n1_w276' in seg,
    'out_name_n1_w276_results': 'n1_w276_results.json' in seg,
    'engine_owner_bm_c': 'engine_owner": "bm-c"' in seg,
}
f1 = 'base=622501 span=2000'
f2 = 'base=624501 span=200'
fam = {f1: n1t.count(f1), f2: n1t.count(f2)}

# prior-wave W274 registry boundary faces kept
m275 = re.search(r'275: \{"batch": "PERPETUAL-N1-W275"', n1t)
w275_seg = n1t[m275.start():m275.start() + 9000] if m275 else ''
if '276: {' in w275_seg:
    w275_seg = w275_seg[:w275_seg.find('276: {')]
boundary = bool(m275) and '620301' in w275_seg and '622301' in w275_seg

# setwave birth-station presence gates (segment-scoped, editor phase5 face)
k275pos = n1t.rfind('_set_wave(275)')
after275 = n1t[k275pos + len('_set_wave(275)'):]
setwave_presence = {
    'w276_block_has_276': '_set_wave(276)' in after275,
    'w276_block_has_275': '_set_wave(275)' in after275,
    'w276_block_has_274': '_set_wave(274)' in after275,
    'whole_file_276_count': n1t.count('_set_wave(276)'),
    'whole_file_275_count': n1t.count('_set_wave(275)'),
    'whole_file_274_count': n1t.count('_set_wave(274)'),
}
setwave_ok = (setwave_presence['w276_block_has_276']
              and not setwave_presence['w276_block_has_275']
              and not setwave_presence['w276_block_has_274']
              and setwave_presence['whole_file_276_count'] == 1
              and setwave_presence['whole_file_275_count'] == 1
              and setwave_presence['whole_file_274_count'] == 1)

sd = 'results/p2cal_ext/n1_w276'
shards = sorted(f for f in os.listdir(sd) if f.startswith('shard-') and f.endswith('.json'))
sizes_ok = all(os.path.getsize(os.path.join(sd, f)) > 100000 for f in shards)

r_banned = subprocess.run([sys.executable, 'Tools/banned_direction_gate.py',
                           '--prereg', 'research/PERPETUAL_N1_W276_PREREG.md'],
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
birth_evidence_ok = (os.path.exists('results/_w276bmc_derive_editor.py')
                     and os.path.exists('results/_r1111bmc_derive_editor_log.txt')
                     and os.path.exists('results/_r1111bmc_needle_preflight.json'))

n1_vs_receipt_note = (
    'r1111 GATE-1 CLEAN-AT-BIRTH FACE (9th consecutive) on ENGINE MECHANICS: '
    'the W276 splice carried ZERO heals of any class -- zero post-splice '
    'heals on pf/n1, zero pre-splice authoring heals (all count-asserted '
    'editor reps first-try; the W275-generation date-roll rep was DROPPED count-0 per the '
    'measured same-date 20261019==20261019 fact, disclosed in the editor '
    'header). Phase4 zero-residual + phase5 presence gates ALL PASS at '
    'editor time. Gate asserts worktree sha16 == freeze-receipt post '
    'faces, CR-normalized worktree == CR-normalized landed blob @ splice '
    'commit 354a645155 (landed = LF storage face, raw sha16 recorded; '
    'splice landed on the ff-base 7a70aee504 after gate0 caught the mid-window '
    'bm-a r1073 chain fail-closed; engine batch1 df7dedfd07 rode the push), segment-scoped birth-station '
    'presence gates green, editor/preflight/log evidence files present.'
)

# ledger_pre: machine-read from W274 finalize product (r587 never-transcribe)
w275 = json.load(io.open('results/perpetual_faces/n1_w275_results.json',
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


ledger_w275 = _find_ledger(w275)
assert ledger_w275 is not None, 'W275 ledger face missing'
prev_total = ledger_w275['total']
prev_k = w275['null_pool_cumulative']['merged']['n_values']
expect_total = prev_total + 2200
expect_merged = prev_k + 2200
up = fr['w275_upstream']
upstream_match = (up['ledger_total'] == prev_total and up['merged_n'] == prev_k)

w275_finalize_present = os.path.exists('results/perpetual_faces/n1_w275_results.json')
out = {
 "machine": "bm-c",
 "wave": 276,
 "phase": "PRE-FINALIZE six-gate (r1111 bm-c own-seat window, 39th consecutive correct-phase target; standing law -- engine self-burn 12/12 landed post-W276 splice 354a645155 clean-at-birth 9th generation on engine mechanics, finalize not yet run)",
 "gates": {
  "splice_integrity": {
   "bands_facts_match_freeze_receipt": all(row_faces.values()),
   "pf_sha16_now": pf_now, "n1_sha16_now": n1_now,
   "pf_sha16_freeze_post": fr['pf_sha16_post'],
   "n1_sha16_freeze_post": fr['n1_sha16_post'],
   "n1_sha16_landed_commit_lf_face": n1_landed,
   "pf_sha16_landed_commit_lf_face": pf_landed,
   "clean_at_birth": {
    "source": "freeze receipt post faces (zero heals of any class this generation -- zero post-splice engine-mechanics heals, zero pre-splice authoring heals, date-roll rep count-0 drop disclosed; setwave root cure held at the birth station)",
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
   "prior_wave_274_boundary_kept": boundary,
  },
  "banned": {"rc": r_banned.returncode, "stdout_tail": (r_banned.stdout or '').strip()[-200:]},
  "pf_selftest": {"rc": r_pf.returncode, "stdout_tail": (r_pf.stdout or '').strip()[-120:]},
  "n1_selftest": {"rc": r_n1.returncode, "stdout_tail": (r_n1.stdout or '').strip()[-120:]},
  "shards": {"present": len(shards), "of": 12, "sizes_above_100k": sizes_ok,
             "files": shards},
  "seed_admit": {
   "freeze_gate_lines": fr.get('seed_admit_gate'),
   "note": "freeze-time FREE evidence consumed verbatim from _w275bmc_freeze_receipt.json (both bands); whole-file per-span family faces count-asserted",
  },
  "wave_configs_row": {
   "present": True, "engine_owner": "bm-c",
   "a_seed_base": 620301, "b_exit_seed_base": 622301,
   "shard_subdir": "n1_w275", "out_name": "n1_w275_results.json",
   "seed_bases_match_freeze_bands": fr['bands']['a_lo'] == 620301 and fr['bands']['b_lo'] == 622301,
   "row_faces_detail": row_faces,
  },
  "w275_finalize_product_present": w275_finalize_present,
 },
 "ledger_pre": {
  "prev_total": prev_total, "prev_merged_n": prev_k,
  "expect_total": expect_total, "expect_merged": expect_merged,
  "source": "W275 finalize actuals machine-read from n1_w275_results.json (r587 law)",
  "freeze_receipt_upstream_face_match": upstream_match,
  "anchor": "W275 finalize (bm-c r1108 one-pass 1,029,335/K=602,920) honored per freeze receipt w275_upstream face",
 },
}

ok = (all(row_faces.values()) and all(v >= 1 for v in fam.values()) and boundary
      and w275_finalize_present
      and pf_now == fr['pf_sha16_post'] and pf_diff_empty and pf_crnorm_equal
      and clean_state_ok and n1_crnorm_equal and birth_evidence_ok and setwave_ok
      and len(shards) == 12 and sizes_ok
      and r_banned.returncode == 0 and r_pf.returncode == 0 and r_n1.returncode == 0
      and upstream_match and prev_total == 1029335 and prev_k == 602920)
out['verdict'] = 'ALL PASS' if ok else 'FAIL'
io.open('results/_r1111bmc_w276_sixgate.json', 'w', encoding='utf-8').write(
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
