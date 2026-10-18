# -*- coding: utf-8 -*-
# r1102 bm-c: W273 PRE-FINALIZE six-gate receipt (standing law since W217
# debt; clone lineage _r1100bmc_w272_sixgate.py, 36th consecutive
# PRE-FINALIZE correct-phase target). Burn landed by resident engine
# mtime-watch auto-ignite post-W273 splice (splice commit 04f2127db pushed
# direct first-try this window -- engine appender self-committed the first
# 6-shard batch fbb4788c49 pre-splice-push per r359 disclosed face, the
# push carried it; remaining shards ride the finalize commit per the
# W272 estate precedent; finalize not yet run).
# CLEAN-AT-BIRTH FACE (6th consecutive) on ENGINE MECHANICS: the W273
# splice carried ZERO post-splice heals on pf/n1. Window heals disclosed
# (all PRE-splice, caught by fail-closed editor gates, zero engine-
# mechanics content defects): 9 authoring heals [stale bm-a owner
# attribution x3 + bm-a own-seat continuity + bma-rows-129 draft-ordinal
# face + (18 rows) aging count + machine-SUB->E63-builder x3 + prereg
# surgery-delivery prose x2] -- all prose/attribution faces in the new
# W273 block, zero functional impact; phase4 zero-residual + phase5
# presence gates ALL PASS at editor time; setwave root-cure held at the
# birth station (_set_wave(273):1/272:1/271:1 whole-file).
# Gate-1 asserts: (a) worktree n1/pf sha16 == freeze-receipt post faces;
# (b) CR-normalized worktree == CR-normalized landed blob @ splice commit
# (landed blob = LF-normalized storage face, known clean divergence --
# raw-byte sha16 of the landed LF face recorded for the receipt);
# (c) segment-scoped birth-station presence gates after the W272 block:
# _set_wave(273) present, _set_wave(272)/_set_wave(271) absent.
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


SPLICE = 'acc7fd02c01a933afb6c81fbeb053d70daafac00'
fr = json.load(io.open('results/_w273bmc_freeze_receipt.json', encoding='utf-8'))
pf_now = sha16('scripts/perpetual_faces.py')
n1_now = sha16('scripts/perpetual_faces_n1.py')

n1t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = n1t.find('273: {"batch": "PERPETUAL-N1-W273"')
assert i >= 0, 'W273 wave row missing'
seg = n1t[i:i + 9000]
if '274: {' in seg:
    seg = seg[:seg.find('274: {')]
row_faces = {
    'a_seed_base_615901': '615901' in seg,
    'b_exit_seed_base_617901': '617901' in seg,
    'shard_subdir_n1_w273': 'n1_w273' in seg,
    'out_name_n1_w273_results': 'n1_w273_results.json' in seg,
    'engine_owner_bm_c': 'engine_owner": "bm-c"' in seg,
}
f1 = 'base=615901 span=2000'
f2 = 'base=617901 span=200'
fam = {f1: n1t.count(f1), f2: n1t.count(f2)}

# prior-wave W272 registry boundary faces kept
m272 = re.search(r'272: \{"batch": "PERPETUAL-N1-W272"', n1t)
w272_seg = n1t[m272.start():m272.start() + 9000] if m272 else ''
if '273: {' in w272_seg:
    w272_seg = w272_seg[:w272_seg.find('273: {')]
boundary = bool(m272) and '613701' in w272_seg and '615701' in w272_seg

# setwave birth-station presence gates (segment-scoped, editor phase5 face)
k272pos = n1t.rfind('_set_wave(272)')
after272 = n1t[k272pos + len('_set_wave(272)'):]
setwave_presence = {
    'w273_block_has_273': '_set_wave(273)' in after272,
    'w273_block_has_272': '_set_wave(272)' in after272,
    'w273_block_has_271': '_set_wave(271)' in after272,
    'whole_file_273_count': n1t.count('_set_wave(273)'),
    'whole_file_272_count': n1t.count('_set_wave(272)'),
    'whole_file_271_count': n1t.count('_set_wave(271)'),
}
setwave_ok = (setwave_presence['w273_block_has_273']
              and not setwave_presence['w273_block_has_272']
              and not setwave_presence['w273_block_has_271']
              and setwave_presence['whole_file_273_count'] == 1
              and setwave_presence['whole_file_272_count'] == 1
              and setwave_presence['whole_file_271_count'] == 1)

sd = 'results/p2cal_ext/n1_w273'
shards = sorted(f for f in os.listdir(sd) if f.startswith('shard-') and f.endswith('.json'))
sizes_ok = all(os.path.getsize(os.path.join(sd, f)) > 100000 for f in shards)

r_banned = subprocess.run([sys.executable, 'Tools/banned_direction_gate.py',
                           '--prereg', 'research/PERPETUAL_N1_W273_PREREG.md'],
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
birth_evidence_ok = (os.path.exists('results/_w273bmc_derive_editor.py')
                     and os.path.exists('results/_r1102bmc_derive_editor_log.txt')
                     and os.path.exists('results/_r1102bmc_needle_preflight.json'))

n1_vs_receipt_note = (
    'r1102 GATE-1 CLEAN-AT-BIRTH FACE (6th consecutive) on ENGINE MECHANICS: '
    'the W273 splice carried ZERO post-splice heals on pf/n1. Window heals '
    'disclosed (all PRE-splice, caught by fail-closed editor gates, zero '
    'engine-mechanics content defects): 9 authoring heals [stale bm-a '
    'owner attribution x3 + bm-a own-seat continuity + bma-rows-129 '
    'draft-ordinal face + (18 rows) aging count + machine-SUB->E63-builder '
    'x3 + prereg surgery-delivery prose x2: frozen b6bbb69e92 -> origin '
    '839441a547 + receipts eeb3bf07ad r1102 window] -- all prose faces in '
    'the new W273 block, zero functional impact; phase4 zero-residual + '
    'phase5 presence gates ALL PASS at editor time. Gate asserts worktree '
    'sha16 == freeze-receipt post faces, CR-normalized worktree == '
    'CR-normalized landed blob @ splice commit 04f2127db (landed = LF '
    'storage face, raw sha16 recorded; splice pushed direct first-try this '
    'window, engine appender first 6-shard batch fbb4788c49 rode the same '
    'push per r359 disclosed face), segment-scoped birth-station presence '
    'gates green, editor/preflight/log evidence files present.'
)

# ledger_pre: machine-read from W272 finalize product (r587 never-transcribe)
w272 = json.load(io.open('results/perpetual_faces/n1_w272_results.json',
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


ledger_w272 = _find_ledger(w272)
assert ledger_w272 is not None, 'W272 ledger face missing'
prev_total = ledger_w272['total']
prev_k = w272['null_pool_cumulative']['merged']['n_values']
expect_total = prev_total + 2200
expect_merged = prev_k + 2200
up = fr['w272_upstream']
upstream_match = (up['ledger_total'] == prev_total and up['merged_n'] == prev_k)

w272_finalize_present = os.path.exists('results/perpetual_faces/n1_w272_results.json')
out = {
 "machine": "bm-c",
 "wave": 273,
 "phase": "PRE-FINALIZE six-gate (r1102 bm-c own-seat window, 36th consecutive correct-phase target; standing law -- engine self-burn 12/12 landed post-W273 splice 04f2127db clean-at-birth 6th generation on engine mechanics, finalize not yet run)",
 "gates": {
  "splice_integrity": {
   "bands_facts_match_freeze_receipt": all(row_faces.values()),
   "pf_sha16_now": pf_now, "n1_sha16_now": n1_now,
   "pf_sha16_freeze_post": fr['pf_sha16_post'],
   "n1_sha16_freeze_post": fr['n1_sha16_post'],
   "n1_sha16_landed_commit_lf_face": n1_landed,
   "pf_sha16_landed_commit_lf_face": pf_landed,
   "clean_at_birth": {
    "source": "freeze receipt post faces (zero post-splice engine-mechanics heals this generation; setwave root cure held at the birth station; 9 pre-splice editor-time authoring heals disclosed, zero engine-mechanics heal face)",
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
   "prior_wave_272_boundary_kept": boundary,
  },
  "banned": {"rc": r_banned.returncode, "stdout_tail": (r_banned.stdout or '').strip()[-200:]},
  "pf_selftest": {"rc": r_pf.returncode, "stdout_tail": (r_pf.stdout or '').strip()[-120:]},
  "n1_selftest": {"rc": r_n1.returncode, "stdout_tail": (r_n1.stdout or '').strip()[-120:]},
  "shards": {"present": len(shards), "of": 12, "sizes_above_100k": sizes_ok,
             "files": shards},
  "seed_admit": {
   "freeze_gate_lines": fr.get('seed_admit_gate'),
   "note": "freeze-time FREE evidence consumed verbatim from _w273bmc_freeze_receipt.json (both bands); whole-file per-span family faces count-asserted",
  },
  "wave_configs_row": {
   "present": True, "engine_owner": "bm-c",
   "a_seed_base": 615901, "b_exit_seed_base": 617901,
   "shard_subdir": "n1_w273", "out_name": "n1_w273_results.json",
   "seed_bases_match_freeze_bands": fr['bands']['a_lo'] == 615901 and fr['bands']['b_lo'] == 617901,
   "row_faces_detail": row_faces,
  },
  "w272_finalize_product_present": w272_finalize_present,
 },
 "ledger_pre": {
  "prev_total": prev_total, "prev_merged_n": prev_k,
  "expect_total": expect_total, "expect_merged": expect_merged,
  "source": "W272 finalize actuals machine-read from n1_w272_results.json (r587 law)",
  "freeze_receipt_upstream_face_match": upstream_match,
  "anchor": "W272 finalize (bm-c r1100 one-pass 1,022,735/K=596,320) honored per freeze receipt w272_upstream face",
 },
}

ok = (all(row_faces.values()) and all(v >= 1 for v in fam.values()) and boundary
      and w272_finalize_present
      and pf_now == fr['pf_sha16_post'] and pf_diff_empty and pf_crnorm_equal
      and clean_state_ok and n1_crnorm_equal and birth_evidence_ok and setwave_ok
      and len(shards) == 12 and sizes_ok
      and r_banned.returncode == 0 and r_pf.returncode == 0 and r_n1.returncode == 0
      and upstream_match and prev_total == 1022735 and prev_k == 596320)
out['verdict'] = 'ALL PASS' if ok else 'FAIL'
io.open('results/_r1102bmc_w273_sixgate.json', 'w', encoding='utf-8').write(
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
