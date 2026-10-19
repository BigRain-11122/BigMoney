# -*- coding: utf-8 -*-
# r1139 bm-c: W282 PRE-FINALIZE six-gate receipt (standing law since W217
# debt; clone lineage _r1135bmc_w281_sixgate.py, 45th consecutive
# PRE-FINALIZE correct-phase target). Burn landed by resident engine
# mtime-watch auto-ignite post-W282 splice (splice commit 01fe28eec2 landed
# behind=0 at push); engine appender shards self-commit per the W272 estate
# precedent; finalize not yet run.
# Gate-1 asserts: (a) worktree n1/pf sha16 == freeze-receipt post faces;
# (b) CR-normalized worktree == CR-normalized landed blob @ splice commit;
# (c) segment-scoped birth-station presence gates after the W281 block:
# _set_wave(282) present, _set_wave(281)/_set_wave(280) absent.
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


SPLICE = '01fe28eec227d66e8c4fa8d14994d18174602e74'
fr = json.load(io.open('results/_w282bmc_freeze_receipt.json', encoding='utf-8'))
pf_now = sha16('scripts/perpetual_faces.py')
n1_now = sha16('scripts/perpetual_faces_n1.py')

n1t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = n1t.find('282: {"batch": "PERPETUAL-N1-W282"')
assert i >= 0, 'W282 wave row missing'
seg = n1t[i:i + 9000]
if '283: {' in seg:
    seg = seg[:seg.find('283: {')]
row_faces = {
    'a_seed_base_635701': '635701' in seg,
    'b_exit_seed_base_637701': '637701' in seg,
    'shard_subdir_n1_w282': 'n1_w282' in seg,
    'out_name_n1_w282_results': 'n1_w282_results.json' in seg,
    'engine_owner_bm_c': 'engine_owner": "bm-c"' in seg,
}
f1 = 'law sec.4 W282 A: 635_701..637_700'
f2 = 'law sec.4 W282 B: 637_701..637_900'
fam = {f1: n1t.count(f1), f2: n1t.count(f2)}

# prior-wave W281 registry boundary faces kept
m281 = re.search(r'281: \{"batch": "PERPETUAL-N1-W281"', n1t)
w281_seg = n1t[m281.start():m281.start() + 9000] if m281 else ''
if '282: {' in w281_seg:
    w281_seg = w281_seg[:w281_seg.find('282: {')]
boundary = bool(m281) and '633501' in w281_seg and '635501' in w281_seg

# setwave birth-station presence gates (segment-scoped, editor phase5 face)
k281pos = n1t.rfind('_set_wave(281)')
after281 = n1t[k281pos + len('_set_wave(281)'):]
setwave_presence = {
    'w282_block_has_282': '_set_wave(282)' in after281,
    'w282_block_has_281': '_set_wave(281)' in after281,
    'w282_block_has_280': '_set_wave(280)' in after281,
    'whole_file_282_count': n1t.count('_set_wave(282)'),
    'whole_file_281_count': n1t.count('_set_wave(281)'),
    'whole_file_280_count': n1t.count('_set_wave(280)'),
}
setwave_ok = (setwave_presence['w282_block_has_282']
              and not setwave_presence['w282_block_has_281']
              and not setwave_presence['w282_block_has_280']
              and setwave_presence['whole_file_282_count'] == 1
              and setwave_presence['whole_file_281_count'] == 1
              and setwave_presence['whole_file_280_count'] == 1)

sd = 'results/p2cal_ext/n1_w282'
shards = sorted(f for f in os.listdir(sd) if f.startswith('shard-') and f.endswith('.json'))
sizes_ok = all(os.path.getsize(os.path.join(sd, f)) > 100000 for f in shards)

r_banned = subprocess.run([sys.executable, 'Tools/banned_direction_gate.py',
                           '--prereg', 'research/PERPETUAL_N1_W282_PREREG.md'],
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
r_git_pf_diff = subprocess.run(['git', 'diff', SPLICE, '--',
                                'scripts/perpetual_faces.py'],
                               capture_output=True, text=True, encoding='utf-8', errors='replace')
pf_diff_empty = (len((r_git_pf_diff.stdout or '').strip()) == 0
                 and r_git_pf_diff.returncode == 0)

clean_state_ok = (n1_now == fr['n1_sha16_post'] and pf_now == fr['pf_sha16_post'])
birth_evidence_ok = (os.path.exists('results/_r1137bmc_prereg_derive_w282.py')
                     ) and (os.path.exists('results/_w282bmc_20261020_probe.py')
                            and os.path.exists('results/_w282bmc_freeze_edits.py')
                            and os.path.exists('results/_w282bmc_freeze_receipt.json'))

n1_vs_receipt_note = (
    'r1139 GATE-1 FACE (45th consecutive PRE-FINALIZE target) on ENGINE '
    'MECHANICS: W282 splice 01fe28eec2 landed at r1138; gate asserts '
    'worktree sha16 == freeze-receipt post faces, CR-normalized worktree == '
    'CR-normalized landed blob @ splice commit, segment-scoped birth-station '
    'presence gates green, derive/probe/freeze-edit evidence files present.'
)

# ledger_pre: machine-read from W281 finalize product (r587 never-transcribe)
w281 = json.load(io.open('results/perpetual_faces/n1_w281_results.json',
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


ledger_w281 = _find_ledger(w281)
assert ledger_w281 is not None, 'W281 ledger face missing'
prev_total = ledger_w281['total']
prev_k = w281['null_pool_cumulative']['merged']['n_values']
expect_total = prev_total + 2200
expect_merged = prev_k + 2200
up = fr['upstream_w281']
upstream_match = (up['ledger_total'] == prev_total and up['merged_n'] == prev_k)

w281_finalize_present = os.path.exists('results/perpetual_faces/n1_w281_results.json')
out = {
 "machine": "bm-c",
 "wave": 282,
 "phase": "PRE-FINALIZE six-gate (r1139 bm-c own-seat window, 45th consecutive correct-phase target; standing law -- engine self-burn 12/12 landed post-W282 splice 01fe28eec2, finalize not yet run)",
 "gates": {
  "splice_integrity": {
   "bands_facts_match_freeze_receipt": all(row_faces.values()),
   "pf_sha16_now": pf_now, "n1_sha16_now": n1_now,
   "pf_sha16_freeze_post": fr['pf_sha16_post'],
   "n1_sha16_freeze_post": fr['n1_sha16_post'],
   "n1_sha16_landed_commit_lf_face": n1_landed,
   "pf_sha16_landed_commit_lf_face": pf_landed,
   "clean_state": {
    "source": "freeze receipt post faces + measured worktree/landed comparison this window",
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
   "n1_vs_receipt_disclosure": n1_vs_receipt_note,
   "family_seed_faces": fam,
   "prior_wave_281_boundary_kept": boundary,
  },
  "banned": {"rc": r_banned.returncode, "stdout_tail": (r_banned.stdout or '').strip()[-200:]},
  "pf_selftest": {"rc": r_pf.returncode, "stdout_tail": (r_pf.stdout or '').strip()[-120:]},
  "n1_selftest": {"rc": r_n1.returncode, "stdout_tail": (r_n1.stdout or '').strip()[-120:]},
  "shards": {"present": len(shards), "of": 12, "sizes_above_100k": sizes_ok,
             "files": shards},
  "seed_admit": {
   "freeze_gate_lines": fr.get('seed_admit_gate'),
   "note": "freeze-time FREE evidence consumed verbatim from _w282bmc_freeze_receipt.json (both bands); whole-file per-span family faces count-asserted",
  },
  "wave_configs_row": {
   "present": True, "engine_owner": "bm-c",
   "a_seed_base": 635701, "b_exit_seed_base": 637701,
   "shard_subdir": "n1_w282", "out_name": "n1_w282_results.json",
   "seed_bases_match_freeze_bands": fr['bands']['A'][0] == 635701 and fr['bands']['B'][0] == 637701,
   "row_faces_detail": row_faces,
  },
  "w281_finalize_product_present": w281_finalize_present,
 },
 "ledger_pre": {
  "prev_total": prev_total, "prev_merged_n": prev_k,
  "expect_total": expect_total, "expect_merged": expect_merged,
  "source": "W281 finalize actuals machine-read from n1_w281_results.json (r587 law)",
  "freeze_receipt_upstream_face_match": upstream_match,
  "anchor": "W281 finalize (bm-c r1135 one-pass 1,042,535/K=616,120) honored per freeze receipt upstream_w281 face",
 },
}

ok = (all(row_faces.values()) and all(v >= 1 for v in fam.values()) and boundary
      and w281_finalize_present
      and pf_now == fr['pf_sha16_post'] and pf_diff_empty and pf_crnorm_equal
      and clean_state_ok and n1_crnorm_equal and birth_evidence_ok and setwave_ok
      and len(shards) == 12 and sizes_ok
      and r_banned.returncode == 0 and r_pf.returncode == 0 and r_n1.returncode == 0
      and upstream_match and prev_total == 1042535 and prev_k == 616120)
out['verdict'] = 'ALL PASS' if ok else 'FAIL'
io.open('results/_r1139bmc_w282_sixgate.json', 'w', encoding='utf-8').write(
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