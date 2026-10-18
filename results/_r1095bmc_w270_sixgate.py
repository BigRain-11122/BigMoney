# -*- coding: utf-8 -*-
# r1095 bm-c: W270 PRE-FINALIZE six-gate receipt (standing law since W217
# debt; clone lineage _r1093bmc_w269_sixgate.py, 33rd consecutive
# PRE-FINALIZE correct-phase target). Burn landed by resident engine
# mtime-watch auto-ignite post-W270 splice (splice commit 1c814343e
# pushed first-try; ledger appends self-committed by the daemon; finalize
# not yet run).
# CLEAN-AT-BIRTH FACE (3rd consecutive): the W270 splice carried ZERO
# surgical heals -- the r1076-family setwave defect was prevented at the
# birth station by the derive editor's p3_setwave_rootcure rep + phase5
# presence gates (r1088 root cure held; 1 same-class gone-list authoring
# heal caught PRE-splice by fail-closed gates, zero content defects).
# Gate-1 asserts: (a) worktree n1/pf sha16 == freeze-receipt post faces;
# (b) CR-normalized worktree == CR-normalized landed blob @ splice commit
# (landed blob = LF-normalized storage face, known clean divergence --
# raw-byte sha16 of the landed LF face recorded for the receipt);
# (c) segment-scoped birth-station presence gates after the W269 block:
# _set_wave(270) present, _set_wave(269)/_set_wave(268) absent.
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


SPLICE = '1c814343ed5decc23d7c95f7ff710c36106ef3c1'
fr = json.load(io.open('results/_w270bmc_freeze_receipt.json', encoding='utf-8'))
pf_now = sha16('scripts/perpetual_faces.py')
n1_now = sha16('scripts/perpetual_faces_n1.py')

n1t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = n1t.find('270: {"batch": "PERPETUAL-N1-W270"')
assert i >= 0, 'W270 wave row missing'
seg = n1t[i:i + 9000]
if '271: {' in seg:
    seg = seg[:seg.find('271: {')]
row_faces = {
    'a_seed_base_609301': '609301' in seg,
    'b_exit_seed_base_611301': '611301' in seg,
    'shard_subdir_n1_w270': 'n1_w270' in seg,
    'out_name_n1_w270_results': 'n1_w270_results.json' in seg,
    'engine_owner_bm_c': 'engine_owner": "bm-c"' in seg,
}
f1 = 'base=609301 span=2000'
f2 = 'base=611301 span=200'
fam = {f1: n1t.count(f1), f2: n1t.count(f2)}

# prior-wave W269 registry boundary faces kept
m269 = re.search(r'269: \{"batch": "PERPETUAL-N1-W269"', n1t)
w269_seg = n1t[m269.start():m269.start() + 9000] if m269 else ''
if '270: {' in w269_seg:
    w269_seg = w269_seg[:w269_seg.find('270: {')]
boundary = bool(m269) and '607101' in w269_seg and '609101' in w269_seg

# setwave birth-station presence gates (segment-scoped, editor phase5 face)
k269pos = n1t.rfind('_set_wave(269)')
after269 = n1t[k269pos + len('_set_wave(269)'):]
setwave_presence = {
    'w270_block_has_270': '_set_wave(270)' in after269,
    'w270_block_has_269': '_set_wave(269)' in after269,
    'w270_block_has_268': '_set_wave(268)' in after269,
    'whole_file_270_count': n1t.count('_set_wave(270)'),
    'whole_file_269_count': n1t.count('_set_wave(269)'),
    'whole_file_268_count': n1t.count('_set_wave(268)'),
}
setwave_ok = (setwave_presence['w270_block_has_270']
              and not setwave_presence['w270_block_has_269']
              and not setwave_presence['w270_block_has_268']
              and setwave_presence['whole_file_270_count'] == 1
              and setwave_presence['whole_file_269_count'] == 1
              and setwave_presence['whole_file_268_count'] == 1)

sd = 'results/p2cal_ext/n1_w270'
shards = sorted(f for f in os.listdir(sd) if f.startswith('shard-') and f.endswith('.json'))
sizes_ok = all(os.path.getsize(os.path.join(sd, f)) > 100000 for f in shards)

r_banned = subprocess.run([sys.executable, 'Tools/banned_direction_gate.py',
                           '--prereg', 'research/PERPETUAL_N1_W270_PREREG.md'],
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
birth_evidence_ok = (os.path.exists('results/_w270bmc_derive_editor.py')
                      and os.path.exists('results/_r1095bmc_derive_editor_log.txt')
                      and os.path.exists('results/_r1095bmc_needle_preflight.json'))

n1_vs_receipt_note = (
    'r1095 GATE-1 CLEAN-AT-BIRTH FACE (3rd consecutive): the W270 splice '
    'carried ZERO surgical heals -- the r1076-family setwave defect was '
    'PREVENTED at the birth station by the derive editor p3_setwave_rootcure '
    'rep + phase5 presence gates (r1088 root cure held; the 1 same-class '
    'gone-list authoring heal was caught PRE-splice by the fail-closed gate '
    'at editor time, zero content defects). Gate asserts worktree sha16 == '
    'freeze-receipt post faces, CR-normalized worktree == CR-normalized '
    'landed blob @ splice commit 1c814343e (landed = LF storage face, raw '
    'sha16 recorded), segment-scoped birth-station presence gates green, '
    'editor/preflight/log evidence files present.'
)

# ledger_pre: machine-read from W269 finalize product (r587 never-transcribe)
w269 = json.load(io.open('results/perpetual_faces/n1_w269_results.json',
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


ledger_w269 = _find_ledger(w269)
assert ledger_w269 is not None, 'W269 ledger face missing'
prev_total = ledger_w269['total']
prev_k = w269['null_pool_cumulative']['merged']['n_values']
expect_total = prev_total + 2200
expect_merged = prev_k + 2200
up = fr['w269_upstream']
upstream_match = (up['ledger_total'] == prev_total and up['merged_n'] == prev_k)

w269_finalize_present = os.path.exists('results/perpetual_faces/n1_w269_results.json')
out = {
 "machine": "bm-c",
 "wave": 270,
 "phase": "PRE-FINALIZE six-gate (r1095 bm-c own-seat window, 33rd consecutive correct-phase target; standing law -- engine self-burn 12/12 landed post-W270 splice 1c814343e clean-at-birth 3rd generation, finalize not yet run)",
 "gates": {
  "splice_integrity": {
   "bands_facts_match_freeze_receipt": all(row_faces.values()),
   "pf_sha16_now": pf_now, "n1_sha16_now": n1_now,
   "pf_sha16_freeze_post": fr['pf_sha16_post'],
   "n1_sha16_freeze_post": fr['n1_sha16_post'],
   "n1_sha16_landed_commit_lf_face": n1_landed,
   "pf_sha16_landed_commit_lf_face": pf_landed,
   "clean_at_birth": {
    "source": "freeze receipt post faces (zero post-splice heals this generation; setwave root cure held at the birth station)",
    "n1_sha16_now": n1_now,
    "receipt_sha16_post": fr['n1_sha16_post'],
    "clean_state_ok": clean_state_ok,
    "crnorm_worktree_eq_landed": n1_crnorm_equal,
    "birth_station_presence_gates": setwave_presence,
    "evidence_files_present": birth_evidence_ok,
    "phase": "post-splice post-burn PRE-finalize (engine mechanics untouched; r1076-family recurrence prevented at birth, zero heal face)",
   },
   "pf_crnorm_equal_worktree_vs_landed": pf_crnorm_equal,
   "pf_landed_diff_empty": pf_diff_empty,
   "n1_vs_receipt_disclosure": n1_vs_receipt_note,
   "family_seed_faces": fam,
   "prior_wave_269_boundary_kept": boundary,
  },
  "banned": {"rc": r_banned.returncode, "stdout_tail": (r_banned.stdout or '').strip()[-200:]},
  "pf_selftest": {"rc": r_pf.returncode, "stdout_tail": (r_pf.stdout or '').strip()[-120:]},
  "n1_selftest": {"rc": r_n1.returncode, "stdout_tail": (r_n1.stdout or '').strip()[-120:]},
  "shards": {"present": len(shards), "of": 12, "sizes_above_100k": sizes_ok,
             "files": shards},
  "seed_admit": {
   "freeze_gate_lines": fr.get('seed_admit_gate'),
   "note": "freeze-time FREE evidence consumed verbatim from _w270bmc_freeze_receipt.json (both bands); whole-file per-span family faces count-asserted",
  },
  "wave_configs_row": {
   "present": True, "engine_owner": "bm-c",
   "a_seed_base": 609301, "b_exit_seed_base": 611301,
   "shard_subdir": "n1_w270", "out_name": "n1_w270_results.json",
   "seed_bases_match_freeze_bands": fr['bands']['a_lo'] == 609301 and fr['bands']['b_lo'] == 611301,
   "row_faces_detail": row_faces,
  },
  "w269_finalize_product_present": w269_finalize_present,
 },
 "ledger_pre": {
  "prev_total": prev_total, "prev_merged_n": prev_k,
  "expect_total": expect_total, "expect_merged": expect_merged,
  "source": "W269 finalize actuals machine-read from n1_w269_results.json (r587 law)",
  "freeze_receipt_upstream_face_match": upstream_match,
  "anchor": "W269 finalize (bm-c r1093 one-pass 1,016,135/K=589,720) honored per freeze receipt w269_upstream face",
 },
}

ok = (all(row_faces.values()) and all(v >= 1 for v in fam.values()) and boundary
      and w269_finalize_present
      and pf_now == fr['pf_sha16_post'] and pf_diff_empty and pf_crnorm_equal
      and clean_state_ok and n1_crnorm_equal and birth_evidence_ok and setwave_ok
      and len(shards) == 12 and sizes_ok
      and r_banned.returncode == 0 and r_pf.returncode == 0 and r_n1.returncode == 0
      and upstream_match and prev_total == 1016135 and prev_k == 589720)
out['verdict'] = 'ALL PASS' if ok else 'FAIL'
io.open('results/_r1095bmc_w270_sixgate.json', 'w', encoding='utf-8').write(
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
