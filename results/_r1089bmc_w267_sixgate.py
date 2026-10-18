# -*- coding: utf-8 -*-
# r1089 bm-c: W267 PRE-FINALIZE six-gate receipt (standing law since W217
# debt; clone lineage _r1086bmc_w266_sixgate.py, 30th consecutive
# PRE-FINALIZE correct-phase target). Burn landed by resident engine
# mtime-watch auto-ignite post-W267 splice (splice + setwave ROOT CURE +
# self-burn 12/12 landed by r1088 commit 7b9e9377374504ff6e7a524734334d20ff0b3e29;
# ledger appends self-committed by the daemon; finalize not yet run).
# HEAL FACE (r1076-family 4th recurrence, CLOSED AT THE BIRTH STATION per
# CEO defect-birthplace law 2026-10-16): the r1088 splice initially carried
# the 2-stale canon hdr face _set_wave(265) inside the W267 block; root cure
# = birth-station gate added to the derive editor (p3_setwave_rootcure rep +
# phase5 presence gates) + surgical heal of the spliced live n1 L74709 only
# (W265 L73397 / W266 L74051 faces preserved; splice NOT re-run) -- the
# estate commit 7b9e937 carries the HEALED n1 face directly (commit message
# n1=4262450a0e33b2ee). Gate-1 asserts: (a) worktree sha16 == freeze-receipt
# post-heal face == post_splice_heals.setwave_rootcure.n1_sha16_healed;
# (b) CR-normalized worktree == CR-normalized landed blob @ splice commit
# (landed blob = LF-normalized storage face, known clean divergence --
# raw-byte sha16 of the landed LF face recorded for the receipt);
# (c) segment-scoped birth-station presence gates after the W266 block:
# _set_wave(267) present, _set_wave(265)/_set_wave(266) absent.
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


SPLICE = '7b9e9377374504ff6e7a524734334d20ff0b3e29'
fr = json.load(io.open('results/_w267bmc_freeze_receipt.json', encoding='utf-8'))
heal = fr['post_splice_heals']['setwave_rootcure']
pf_now = sha16('scripts/perpetual_faces.py')
n1_now = sha16('scripts/perpetual_faces_n1.py')

n1t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = n1t.find('267: {"batch": "PERPETUAL-N1-W267"')
assert i >= 0, 'W267 wave row missing'
seg = n1t[i:i + 9000]
if '268: {' in seg:
    seg = seg[:seg.find('268: {')]
row_faces = {
    'a_seed_base_602701': '602701' in seg,
    'b_exit_seed_base_604701': '604701' in seg,
    'shard_subdir_n1_w267': 'n1_w267' in seg,
    'out_name_n1_w267_results': 'n1_w267_results.json' in seg,
    'engine_owner_bm_c': 'engine_owner": "bm-c"' in seg,
}
f1 = 'base=602701 span=2000'
f2 = 'base=604701 span=200'
fam = {f1: n1t.count(f1), f2: n1t.count(f2)}

# prior-wave W266 registry boundary faces kept
m266 = re.search(r'266: \{"batch": "PERPETUAL-N1-W266"', n1t)
w266_seg = n1t[m266.start():m266.start() + 9000] if m266 else ''
if '267: {' in w266_seg:
    w266_seg = w266_seg[:w266_seg.find('267: {')]
boundary = bool(m266) and '600501' in w266_seg and '602501' in w266_seg

# setwave birth-station presence gates (segment-scoped, phase5 face)
k266pos = n1t.rfind('_set_wave(266)')
after266 = n1t[k266pos + len('_set_wave(266)'):]
setwave_presence = {
    'w267_block_has_267': '_set_wave(267)' in after266,
    'w267_block_has_265': '_set_wave(265)' in after266,
    'w267_block_has_266': '_set_wave(266)' in after266,
    'whole_file_267_count': n1t.count('_set_wave(267)'),
    'whole_file_265_count': n1t.count('_set_wave(265)'),
}
setwave_ok = (setwave_presence['w267_block_has_267']
              and not setwave_presence['w267_block_has_265']
              and not setwave_presence['w267_block_has_266']
              and setwave_presence['whole_file_267_count'] == 1
              and setwave_presence['whole_file_265_count'] == 1)

sd = 'results/p2cal_ext/n1_w267'
shards = sorted(f for f in os.listdir(sd) if f.startswith('shard-') and f.endswith('.json'))
sizes_ok = all(os.path.getsize(os.path.join(sd, f)) > 100000 for f in shards)

r_banned = subprocess.run([sys.executable, 'Tools/banned_direction_gate.py',
                           '--prereg', 'research/PERPETUAL_N1_W267_PREREG.md'],
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

heal_state_ok = (n1_now == heal['n1_sha16_healed'] == fr['n1_sha16_post'])
heal_evidence_ok = (os.path.exists('results/_r1088bmc_n1_setwave_heal.py')
                    and os.path.exists('results/_r1088bmc_derive_editor_log.txt'))

n1_vs_receipt_note = (
    'r1089 GATE-1 HEAL FACE: W267 splice initially carried the 2-stale canon '
    'hdr face _set_wave(265) in the W267 block (r1076-family 4th recurrence); '
    'ROOT CURE executed at the birth station in the r1088 window per CEO '
    'defect-birthplace law 2026-10-16: derive-editor p3_setwave_rootcure rep + '
    'phase5 presence gates, surgical heal of spliced live n1 L74709 only '
    '(W265 L73397 / W266 L74051 preserved, splice NOT re-run), estate commit '
    '7b9e937 carries the HEALED n1 face directly. Gate asserts worktree == '
    'freeze-receipt post-heal face == post_splice_heals.n1_sha16_healed == '
    '4262450a0e33b2ee, CR-normalized worktree == CR-normalized landed blob '
    '(landed = LF storage face, raw sha16 recorded), segment-scoped presence '
    'gates green, heal evidence files present.'
)

# ledger_pre: machine-read from W266 finalize product (r587 never-transcribe)
w266 = json.load(io.open('results/perpetual_faces/n1_w266_results.json',
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


ledger_w266 = _find_ledger(w266)
assert ledger_w266 is not None, 'W266 ledger face missing'
prev_total = ledger_w266['total']
prev_k = w266['null_pool_cumulative']['merged']['n_values']
expect_total = prev_total + 2200
expect_merged = prev_k + 2200
up = fr['w266_upstream']
upstream_match = (up['ledger_total'] == prev_total and up['merged_n'] == prev_k)

w266_finalize_present = os.path.exists('results/perpetual_faces/n1_w266_results.json')
out = {
 "machine": "bm-c",
 "wave": 267,
 "phase": "PRE-FINALIZE six-gate (r1089 bm-c own-seat window, 30th consecutive correct-phase target; standing law -- engine self-burn 12/12 landed post-W267 splice 7b9e9377 + setwave root cure at the birth station, finalize not yet run)",
 "gates": {
  "splice_integrity": {
   "bands_facts_match_freeze_receipt": all(row_faces.values()),
   "pf_sha16_now": pf_now, "n1_sha16_now": n1_now,
   "pf_sha16_freeze_post": fr['pf_sha16_post'],
   "n1_sha16_freeze_post_postheal": fr['n1_sha16_post'],
   "n1_sha16_landed_commit_lf_face": n1_landed,
   "pf_sha16_landed_commit_lf_face": pf_landed,
   "post_splice_heal": {
    "source": "freeze receipt post_splice_heals.setwave_rootcure (healed at the birth station r1088, estate commit carries healed face)",
    "n1_sha16_now": n1_now,
    "heal_receipt_sha16": heal['n1_sha16_healed'],
    "heal_state_ok": heal_state_ok,
    "crnorm_worktree_eq_landed": n1_crnorm_equal,
    "birth_station_presence_gates": setwave_presence,
    "evidence_files_present": heal_evidence_ok,
    "phase": "post-splice post-burn PRE-finalize (engine mechanics untouched; r1076-family 4th recurrence closed at the birth station)",
   },
   "pf_crnorm_equal_worktree_vs_landed": pf_crnorm_equal,
   "pf_landed_diff_empty": pf_diff_empty,
   "n1_vs_receipt_disclosure": n1_vs_receipt_note,
   "family_seed_faces": fam,
   "prior_wave_266_boundary_kept": boundary,
  },
  "banned": {"rc": r_banned.returncode, "stdout_tail": (r_banned.stdout or '').strip()[-200:]},
  "pf_selftest": {"rc": r_pf.returncode, "stdout_tail": (r_pf.stdout or '').strip()[-120:]},
  "n1_selftest": {"rc": r_n1.returncode, "stdout_tail": (r_n1.stdout or '').strip()[-120:]},
  "shards": {"present": len(shards), "of": 12, "sizes_above_100k": sizes_ok,
             "files": shards},
  "seed_admit": {
   "freeze_gate_lines": fr.get('seed_admit_gate'),
   "note": "freeze-time FREE evidence consumed verbatim from _w267bmc_freeze_receipt.json (both bands); whole-file per-span family faces count-asserted",
  },
  "wave_configs_row": {
   "present": True, "engine_owner": "bm-c",
   "a_seed_base": 602701, "b_exit_seed_base": 604701,
   "shard_subdir": "n1_w267", "out_name": "n1_w267_results.json",
   "seed_bases_match_freeze_bands": fr['bands']['a_lo'] == 602701 and fr['bands']['b_lo'] == 604701,
   "row_faces_detail": row_faces,
  },
  "w266_finalize_product_present": w266_finalize_present,
 },
 "ledger_pre": {
  "prev_total": prev_total, "prev_merged_n": prev_k,
  "expect_total": expect_total, "expect_merged": expect_merged,
  "source": "W266 finalize actuals machine-read from n1_w266_results.json (r587 law)",
  "freeze_receipt_upstream_face_match": upstream_match,
  "anchor": "W266 finalize (bm-c r1086 one-pass 1,009,535/K=583,120) honored per freeze receipt w266_upstream face",
 },
}

ok = (all(row_faces.values()) and all(v >= 1 for v in fam.values()) and boundary
      and w266_finalize_present
      and pf_now == fr['pf_sha16_post'] and pf_diff_empty and pf_crnorm_equal
      and heal_state_ok and n1_crnorm_equal and heal_evidence_ok and setwave_ok
      and len(shards) == 12 and sizes_ok
      and r_banned.returncode == 0 and r_pf.returncode == 0 and r_n1.returncode == 0
      and upstream_match and prev_total == 1009535 and prev_k == 583120)
out['verdict'] = 'ALL PASS' if ok else 'FAIL'
io.open('results/_r1089bmc_w267_sixgate.json', 'w', encoding='utf-8').write(
    json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps({"verdict": out['verdict'],
                  "row_faces": row_faces, "fam": fam, "boundary": boundary,
                  "shards": len(shards), "sizes_ok": sizes_ok,
                  "banned_rc": r_banned.returncode,
                  "pf_selftest_rc": r_pf.returncode,
                  "n1_selftest_rc": r_n1.returncode,
                  "heal_state_ok": heal_state_ok,
                  "crnorm_worktree_eq_landed": n1_crnorm_equal,
                  "pf_crnorm_equal": pf_crnorm_equal,
                  "setwave_presence": setwave_presence,
                  "ledger_pre": out['ledger_pre']}, indent=1))
raise SystemExit(0 if ok else 1)
