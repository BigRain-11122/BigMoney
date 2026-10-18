# -*- coding: utf-8 -*-
# r1086-continuation bm-c: W266 PRE-FINALIZE six-gate receipt (standing law
# since W217 debt; clone lineage _r1076bmc_w264_sixgate.py heal-face pattern,
# 29th consecutive PRE-FINALIZE correct-phase target). Burn landed by resident
# engine auto-ignite post-W266 splice (splice executed by the dead 09:25-09:50
# window -- 58th-gen absorb estate landed by THIS window's commit
# dc71ecc3f9fef2544ec7c9ef49b6b886a70fed9a; ledger appends self-committed by
# the daemon; finalize not yet run).
# POST-SPLICE HEAL FACE (r1076 W264 precedent, H1 family 3rd recurrence):
# the dead window's editor left the W266 selftest block roll line un-rolled
# (_set_wave(265) inside the W266 section) -- runtime proof: n1 selftest died
# "W266 A hits W265" pre-heal. Healed THIS window PRE-finalize by a single
# same-length token per results/_r1086bmc_w266_selftest_heal.{py,json};
# engine mechanics untouched (the engine already self-burned 12/12 from the
# correct W266 registry rows). Gate-1 asserts: (a) healed worktree sha16 ==
# heal receipt new_sha16; (b) MINIMALITY PROOF -- applying the same single
# token heal to the landed LF blob yields CR-normalized equality with the
# healed worktree (delta == exactly the 1 token). Raw freeze-receipt
# sha16_post (992f2f3b7b380bf6) hashed the PRE-heal CRLF worktree and equals
# the pre-heal landed blob face (recorded in the heal receipt old_sha16_crlf).
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


SPLICE = 'dc71ecc3f9fef2544ec7c9ef49b6b886a70fed9a'
fr = json.load(io.open('results/_w266bmc_freeze_receipt.json', encoding='utf-8'))
heal = json.load(io.open('results/_r1086bmc_w266_selftest_heal.json', encoding='utf-8'))
pf_now = sha16('scripts/perpetual_faces.py')
n1_now = sha16('scripts/perpetual_faces_n1.py')

n1t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = n1t.find('266: {"batch": "PERPETUAL-N1-W266"')
assert i >= 0, 'W266 wave row missing'
seg = n1t[i:i + 9000]
if '267: {' in seg:
    seg = seg[:seg.find('267: {')]
row_faces = {
    'a_seed_base_600501': '600501' in seg,
    'b_exit_seed_base_602501': '602501' in seg,
    'shard_subdir_n1_w266': 'n1_w266' in seg,
    'out_name_n1_w266_results': 'n1_w266_results.json' in seg,
    'engine_owner_bm_c': 'engine_owner": "bm-c"' in seg,
}
f1 = 'base=600501 span=2000'
f2 = 'base=602501 span=200'
fam = {f1: n1t.count(f1), f2: n1t.count(f2)}
m265 = re.search(r'265: \{"batch": "PERPETUAL-N1-W265"', n1t)
w265_seg = n1t[m265.start():m265.start() + 8000] if m265 else ''
if '266: {' in w265_seg:
    w265_seg = w265_seg[:w265_seg.find('266: {')]
boundary = bool(m265) and '598301' in w265_seg and '600301' in w265_seg

sd = 'results/p2cal_ext/n1_w266'
shards = sorted(f for f in os.listdir(sd) if f.startswith('shard-') and f.endswith('.json'))
sizes_ok = all(os.path.getsize(os.path.join(sd, f)) > 100000 for f in shards)

r_banned = subprocess.run([sys.executable, 'Tools/banned_direction_gate.py',
                           '--prereg', 'research/PERPETUAL_N1_W266_PREREG.md'],
                          capture_output=True, text=True)
r_pf = subprocess.run([sys.executable, 'scripts/perpetual_faces.py', 'selftest'],
                     capture_output=True, text=True)
r_n1 = subprocess.run([sys.executable, 'scripts/perpetual_faces_n1.py', 'selftest'],
                      capture_output=True, text=True)
r_git = subprocess.run(['git', 'show', f'{SPLICE}:scripts/perpetual_faces_n1.py'],
                       capture_output=True)
n1_landed = hashlib.sha256(r_git.stdout).hexdigest()[:16]
wt_n1_bytes = io.open('scripts/perpetual_faces_n1.py', 'rb').read()


# MINIMALITY PROOF machinery (r1076 W264 heal-face precedent, single-token
# variant): apply the same heal to the landed LF blob -> CR-normalized
# equality with the healed worktree (the heal delta is EXACTLY 1 token).
def apply_heals(blob: bytes) -> bytes:
    assert blob.count(b'_set_wave(265)') == 2, 'landed blob face drift (occurrences)'
    pat = b'_set_wave(265)'
    idxs = []
    k = blob.find(pat)
    while k >= 0:
        idxs.append(k)
        k = blob.find(pat, k + 1)
    jj = idxs[1]
    assert b'W138..W206+W211..W265)' in blob[max(0, jj - 2000):jj], \
        'W266-section anchor missing in landed blob'
    return blob[:jj] + b'_set_wave(266)' + blob[jj + len(pat):]


n1_healed_landed = apply_heals(r_git.stdout)
n1_crnorm_equal_healed = crnorm(wt_n1_bytes) == crnorm(n1_healed_landed)
n1_heal_state_ok = (n1_now == heal['new_sha16_crlf'])
n1_preheal_receipt_landed_ok = (heal['old_sha16_crlf'] == fr['n1_sha16_post'])
r_git_pf = subprocess.run(['git', 'show', f'{SPLICE}:scripts/perpetual_faces.py'],
                           capture_output=True)
wt_pf_bytes = io.open('scripts/perpetual_faces.py', 'rb').read()
pf_crnorm_equal = crnorm(wt_pf_bytes) == crnorm(r_git_pf.stdout)
r_git_pf_diff = subprocess.run(['git', 'diff', SPLICE, '--',
                                'scripts/perpetual_faces.py'],
                               capture_output=True, text=True)
pf_diff_empty = (len((r_git_pf_diff.stdout or '').strip()) == 0
                 and r_git_pf_diff.returncode == 0)

n1_vs_receipt_note = (
    'r1086 POST-SPLICE HEAL DISCLOSURE: splice (absorb commit dc71ecc3f9) '
    'carried ONE un-rolled roll token in the NEW W266 selftest section '
    '(H1 _set_wave(265)->(266), W266-section 2nd occurrence; dead '
    '09:25-09:50 splice-window editor authoring defect; r1076 W264 H1 '
    'family 3rd recurrence) -- runtime proof: n1 selftest died "W266 A '
    'hits W265" pre-heal (prereheal FAIL evidence preserved at '
    'results/_r1086bmc_w266_sixgate_prereheal_FAIL.json). Healed THIS '
    'window PRE-finalize by a single same-length token '
    '(results/_r1086bmc_w266_selftest_heal.{py,json}; post-heal selftest '
    'rc=0 live in the heal receipt). Engine mechanics untouched: registry '
    'rows / shard dir / burn arithmetic verified green by the other gates; '
    'the engine already self-burned 12/12 from the correct W266 rows. '
    'Gate-1 asserts healed-worktree == heal-receipt and landed-blob+heal '
    '== healed-worktree (CR-normalized minimality proof).'
)

# ledger_pre: machine-read from W265 finalize product (r587 never-transcribe)
w265 = json.load(io.open('results/perpetual_faces/n1_w265_results.json',
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


ledger_w265 = _find_ledger(w265)
assert ledger_w265 is not None, 'W265 ledger face missing'
prev_total = ledger_w265['total']
prev_k = w265['null_pool_cumulative']['merged']['n_values']
expect_total = prev_total + 2200
expect_merged = prev_k + 2200
up = fr['w265_upstream']
upstream_match = (up['ledger_total'] == prev_total and up['merged_n'] == prev_k)

w265_finalize_present = os.path.exists('results/perpetual_faces/n1_w265_results.json')
out = {
 "machine": "bm-c",
 "wave": 266,
 "phase": "PRE-FINALIZE six-gate (r1086-continuation bm-c own-seat window, 29th consecutive correct-phase target; standing law -- engine self-burn 12/12 landed post-W266 splice dc71ecc3f9, single-token post-splice heal applied PRE-finalize, finalize not yet run)",
 "gates": {
  "splice_integrity": {
   "bands_facts_match_freeze_receipt": all(row_faces.values()),
   "pf_sha16_now": pf_now, "n1_sha16_now": n1_now,
   "pf_sha16_freeze_post": fr['pf_sha16_post'],
   "n1_sha16_freeze_post": fr['n1_sha16_post'],
   "n1_sha16_landed_commit_lf_clean": n1_landed,
   "post_splice_heal": {
    "receipt": "results/_r1086bmc_w266_selftest_heal.json",
    "n1_sha16_now": n1_now,
    "heal_receipt_new_sha16": heal['new_sha16_crlf'],
    "heal_state_ok": n1_heal_state_ok,
    "minimality_proof_crnorm_healed_landed_eq_worktree": n1_crnorm_equal_healed,
    "preheal_receipt_sha16_post": fr['n1_sha16_post'],
    "preheal_receipt_eq_landed_face": n1_preheal_receipt_landed_ok,
    "tokens": ["H1 _set_wave(265)->(266) (W266 section, 2nd occurrence, same length)"],
    "phase": "post-splice post-burn PRE-finalize (engine mechanics untouched)",
   },
   "pf_crnorm_equal_worktree_vs_landed": pf_crnorm_equal,
   "pf_landed_diff_empty": pf_diff_empty,
   "n1_vs_receipt_disclosure": n1_vs_receipt_note,
   "family_seed_faces": fam,
   "prior_wave_265_boundary_kept": boundary,
  },
  "banned": {"rc": r_banned.returncode, "stdout_tail": (r_banned.stdout or '').strip()[-200:]},
  "pf_selftest": {"rc": r_pf.returncode, "stdout_tail": (r_pf.stdout or '').strip()[-120:]},
  "n1_selftest": {"rc": r_n1.returncode, "stdout_tail": (r_n1.stdout or '').strip()[-120:]},
  "shards": {"present": len(shards), "of": 12, "sizes_above_100k": sizes_ok,
             "files": shards},
  "seed_admit": {
   "freeze_gate_lines": fr.get('seed_admit_gate'),
   "note": "freeze-time FREE evidence consumed verbatim from _w266bmc_freeze_receipt.json (both bands); whole-file per-span family faces count-asserted",
  },
  "wave_configs_row": {
   "present": True, "engine_owner": "bm-c",
   "a_seed_base": 600501, "b_exit_seed_base": 602501,
   "shard_subdir": "n1_w266", "out_name": "n1_w266_results.json",
   "seed_bases_match_freeze_bands": fr['bands']['a_lo'] == 600501 and fr['bands']['b_lo'] == 602501,
   "row_faces_detail": row_faces,
  },
  "w265_finalize_product_present": w265_finalize_present,
 },
 "ledger_pre": {
  "prev_total": prev_total, "prev_merged_n": prev_k,
  "expect_total": expect_total, "expect_merged": expect_merged,
  "source": "W265 finalize actuals machine-read from n1_w265_results.json (r587 law)",
  "freeze_receipt_upstream_face_match": upstream_match,
  "anchor": "W265 finalize (bm-c r1084 one-pass 1,007,335/K=580,920) honored per freeze receipt w265_upstream face",
 },
}

ok = (all(row_faces.values()) and all(v >= 1 for v in fam.values()) and boundary
      and w265_finalize_present
      and pf_now == fr['pf_sha16_post'] and pf_diff_empty and pf_crnorm_equal
      and n1_heal_state_ok and n1_crnorm_equal_healed and n1_preheal_receipt_landed_ok
      and len(shards) == 12 and sizes_ok
      and r_banned.returncode == 0 and r_pf.returncode == 0 and r_n1.returncode == 0
      and upstream_match and prev_total == 1007335 and prev_k == 580920)
out['verdict'] = 'ALL PASS' if ok else 'FAIL'
io.open('results/_r1086bmc_w266_sixgate.json', 'w', encoding='utf-8').write(
    json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps({"verdict": out['verdict'],
                  "row_faces": row_faces, "fam": fam, "boundary": boundary,
                  "shards": len(shards), "sizes_ok": sizes_ok,
                  "banned_rc": r_banned.returncode,
                  "pf_selftest_rc": r_pf.returncode,
                  "n1_selftest_rc": r_n1.returncode,
                  "heal_state_ok": n1_heal_state_ok,
                  "minimality_proof": n1_crnorm_equal_healed,
                  "pf_crnorm_equal": pf_crnorm_equal,
                  "ledger_pre": out['ledger_pre']}, indent=1))
raise SystemExit(0 if ok else 1)
