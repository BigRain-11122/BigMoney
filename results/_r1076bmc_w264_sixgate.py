# -*- coding: utf-8 -*-
# r1076 bm-c: W264 PRE-FINALIZE six-gate receipt (standing law since W217 debt;
# clone lineage _r1039bma_w263_sixgate.py W263 pattern, 26th consecutive
# PRE-FINALIZE correct-phase). Burn landed by resident engine auto-ignite
# post-W264 splice 216b578b0 (ledger appends 964148797+17dd06323 batched 12/12,
# shard files only; finalize not yet run).
# Splice commit 216b578b0 landed via clean-filter commit (worktree CRLF ->
# blob LF): raw-byte triple identity does NOT hold for this wave; gate-1
# asserts CR-NORMALIZED content identity worktree == landed blob (EOL
# representation delta only, zero content delta) -- disclosed honest
# (W263 r1039 precedent face, absorbed-verified this window:
# blob_lf_to_crlf hash == receipt pre-sha16 both faces EXACT).
# Freeze receipt hashed the CRLF worktree bytes at freeze time; those raw
# worktree hashes still match today (worktree untouched since splice).
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


SPLICE = '216b578b095b653728a5c18d6835d4e0b968b1dc'
fr = json.load(io.open('results/_w264bmc_freeze_receipt.json', encoding='utf-8'))
pf_now = sha16('scripts/perpetual_faces.py')
n1_now = sha16('scripts/perpetual_faces_n1.py')

n1t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = n1t.find('264: {"batch": "PERPETUAL-N1-W264"')
assert i >= 0, 'W264 wave row missing'
seg = n1t[i:i + 9000]
if '265: {' in seg:
    seg = seg[:seg.find('265: {')]
row_faces = {
    'a_seed_base_596101': '596101' in seg,
    'b_exit_seed_base_598101': '598101' in seg,
    'shard_subdir_n1_w264': 'n1_w264' in seg,
    'out_name_n1_w264_results': 'n1_w264_results.json' in seg,
    'engine_owner_bm_c': 'engine_owner": "bm-c"' in seg,
}
f1 = 'base=596101 span=2000'
f2 = 'base=598101 span=200'
fam = {f1: n1t.count(f1), f2: n1t.count(f2)}
m263 = re.search(r'263: \{"batch": "PERPETUAL-N1-W263"', n1t)
w263_seg = n1t[m263.start():m263.start() + 8000] if m263 else ''
if '264: {' in w263_seg:
    w263_seg = w263_seg[:w263_seg.find('264: {')]
boundary = bool(m263) and '593901' in w263_seg and '595901' in w263_seg

sd = 'results/p2cal_ext/n1_w264'
shards = sorted(f for f in os.listdir(sd) if f.startswith('shard-') and f.endswith('.json'))
sizes_ok = all(os.path.getsize(os.path.join(sd, f)) > 100000 for f in shards)

r_banned = subprocess.run([sys.executable, 'Tools/banned_direction_gate.py',
                           '--prereg', 'research/PERPETUAL_N1_W264_PREREG.md'],
                          capture_output=True, text=True)
r_pf = subprocess.run([sys.executable, 'scripts/perpetual_faces.py', 'selftest'],
                     capture_output=True, text=True)
r_n1 = subprocess.run([sys.executable, 'scripts/perpetual_faces_n1.py', 'selftest'],
                      capture_output=True, text=True)
r_git = subprocess.run(['git', 'show', f'{SPLICE}:scripts/perpetual_faces_n1.py'],
                       capture_output=True)
n1_landed = hashlib.sha256(r_git.stdout).hexdigest()[:16]
wt_n1_bytes = io.open('scripts/perpetual_faces_n1.py', 'rb').read()
n1_crnorm_equal = crnorm(wt_n1_bytes) == crnorm(r_git.stdout)


# post-splice heal verification (r1076 dead-window splice landed 3 un-rolled
# index tokens in the W264 selftest section; healed THIS window per
# results/_r1076bmc_w264_selftest_heal.py -- runtime proof: selftest died
# "W264 A hits W263" pre-heal). Machine checks:
#   (a) worktree sha16 == heal receipt new_sha16 (healed state)
#   (b) MINIMALITY PROOF: apply the same 3 same-length token heals to the
#       landed LF blob -> CR-normalized equality with the healed worktree
#       (the heal delta is EXACTLY the 3 tokens, nothing else)
def apply_heals(blob: bytes) -> bytes:
    assert blob.count(b'WAVE_CONFIGS[263]["a_seed_base"] == 596101') == 1
    assert blob.count(b'WAVE_CONFIGS[263]["b_exit_seed_base"] == 598101') == 1
    blob = blob.replace(b'WAVE_CONFIGS[263]["a_seed_base"] == 596101',
                        b'WAVE_CONFIGS[264]["a_seed_base"] == 596101')
    blob = blob.replace(b'WAVE_CONFIGS[263]["b_exit_seed_base"] == 598101',
                        b'WAVE_CONFIGS[264]["b_exit_seed_base"] == 598101')
    pat = b'_set_wave(263)'
    idxs = []
    k = blob.find(pat)
    while k >= 0:
        idxs.append(k)
        k = blob.find(pat, k + 1)
    assert len(idxs) == 2, idxs
    jj = idxs[1]
    assert 'W138..W206+W211..W263)'.encode('utf-8') in blob[max(0, jj - 400):jj]
    return blob[:jj] + b'_set_wave(264)' + blob[jj + len(pat):]


heal = json.load(io.open('results/_r1076bmc_w264_selftest_heal.json',
                         encoding='utf-8'))
n1_healed_landed = apply_heals(r_git.stdout)
n1_crnorm_equal_healed = crnorm(wt_n1_bytes) == crnorm(n1_healed_landed)
n1_heal_state_ok = (sha16('scripts/perpetual_faces_n1.py')
                    == heal['new_sha16_crlf'])
n1_preheal_crnorm_holds = (crnorm(io.open('scripts/perpetual_faces_n1.py',
                                 'rb').read())
                           != crnorm(r_git.stdout))
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
    'r1076 POST-SPLICE HEAL DISCLOSURE: splice commit ' + SPLICE[:10] + ' '
    'landed via the clean-filter path (worktree CRLF -> committed blob LF) AND '
    'carried 3 un-rolled index tokens in the NEW W264 selftest section '
    '(H1 _set_wave(263)->264 [2nd occurrence, W264-section anchored]; H2/H3 '
    'band-facts assert WAVE_CONFIGS[263]->[264] with W264 base values '
    '596101/598101) -- runtime proof: n1 selftest died "W264 A hits W263" '
    '(w244_a held W263 bands via the un-rolled _set_wave). Healed THIS window '
    'PRE-finalize (results/_r1076bmc_w264_selftest_heal.{py,json}, 3 '
    'same-length tokens, engine mechanics untouched: registry rows/shard '
    'dir/burn arithmetic all verified green by the other gates; the engine '
    'already self-burned 12/12 from the correct 264 rows). Gate-1 now '
    'asserts: (a) healed worktree sha16 == heal receipt; (b) MINIMALITY '
    'PROOF -- applying the same 3 heals to the landed LF blob yields '
    'CR-normalized equality with the healed worktree (delta == exactly the 3 '
    'tokens). Raw freeze-receipt sha16_post hashed the PRE-heal CRLF worktree '
    '(still recorded in the freeze receipt + heal receipt old_sha16_crlf).'
)

# ledger_pre: machine-read from W263 finalize product (r587 never-transcribe)
w263 = json.load(io.open('results/perpetual_faces/n1_w263_results.json',
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


ledger_w263 = _find_ledger(w263)
assert ledger_w263 is not None, 'W263 ledger face missing'
prev_total = ledger_w263['total']
prev_k = w263['null_pool_cumulative']['merged']['n_values']
expect_total = prev_total + 2200
expect_merged = prev_k + 2200
# cross-check vs freeze receipt upstream face
up = fr['w263_upstream']
upstream_match = (up['ledger_total'] == prev_total and up['merged_n'] == prev_k)

w263_finalize_present = os.path.exists('results/perpetual_faces/n1_w263_results.json')
out = {
 "machine": "bm-c",
 "wave": 264,
 "phase": "PRE-FINALIZE six-gate (r1076 bm-c absorb-continuation own-seat window, 26th consecutive correct-phase; standing law -- engine self-burn 12/12 landed post-W264 splice 216b578b0 via batched ledger appends 964148797+17dd06323, finalize not yet run)",
 "gates": {
  "splice_integrity": {
   "bands_facts_match_freeze_receipt": all(row_faces.values()),
   "pf_sha16_now": pf_now, "n1_sha16_now": n1_now,
   "pf_sha16_freeze_post": fr['pf_sha16_post'],
   "n1_sha16_freeze_post": fr['n1_sha16_post'],
   "n1_sha16_landed_commit_lf_clean": n1_landed,
   "n1_crnorm_equal_worktree_vs_landed_preheal": n1_crnorm_equal,
   "post_splice_heal": {
    "receipt": "results/_r1076bmc_w264_selftest_heal.json",
    "n1_sha16_now": sha16('scripts/perpetual_faces_n1.py'),
    "heal_receipt_new_sha16": heal['new_sha16_crlf'],
    "heal_state_ok": n1_heal_state_ok,
    "minimality_proof_crnorm_healed_landed_eq_worktree": n1_crnorm_equal_healed,
    "preheal_receipt_sha16_post": fr['n1_sha16_post'],
    "tokens": ["H1 _set_wave(263)->264 (W264 section, 2nd occurrence)",
               "H2 WAVE_CONFIGS[263]->[264] band-facts a_seed_base==596101",
               "H3 WAVE_CONFIGS[263]->[264] band-facts b_exit==598101"],
    "phase": "post-splice post-burn PRE-finalize (engine mechanics untouched)",
   },
   "pf_crnorm_equal_worktree_vs_landed": pf_crnorm_equal,
   "pf_landed_diff_empty": pf_diff_empty,
   "n1_vs_receipt_disclosure": n1_vs_receipt_note,
   "family_seed_faces": fam,
   "prior_wave_263_boundary_kept": boundary,
  },
  "banned": {"rc": r_banned.returncode, "stdout_tail": (r_banned.stdout or '').strip()[-200:]},
  "pf_selftest": {"rc": r_pf.returncode, "stdout_tail": (r_pf.stdout or '').strip()[-120:]},
  "n1_selftest": {"rc": r_n1.returncode, "stdout_tail": (r_n1.stdout or '').strip()[-120:]},
  "shards": {"present": len(shards), "of": 12, "sizes_above_100k": sizes_ok,
             "files": shards},
  "seed_admit": {
   "freeze_gate_lines": fr.get('seed_admit_gate'),
   "note": "freeze-time FREE evidence consumed verbatim from _w264bmc_freeze_receipt.json (both bands); whole-file per-span family faces count-asserted",
  },
  "wave_configs_row": {
   "present": True, "engine_owner": "bm-c",
   "a_seed_base": 596101, "b_exit_seed_base": 598101,
   "shard_subdir": "n1_w264", "out_name": "n1_w264_results.json",
   "seed_bases_match_freeze_bands": fr['bands']['A'] == [596101, 598100] and fr['bands']['B'] == [598101, 598300],
   "row_faces_detail": row_faces,
  },
  "w263_finalize_product_present": w263_finalize_present,
 },
 "ledger_pre": {
  "prev_total": prev_total, "prev_merged_n": prev_k,
  "expect_total": expect_total, "expect_merged": expect_merged,
  "source": "W263 finalize actuals machine-read from n1_w263_results.json (r587 law)",
  "freeze_receipt_upstream_face_match": upstream_match,
  "anchor": "W263 finalize (bm-a r1039 one-pass 1,002,935/K=576,520) honored per freeze receipt w263_upstream face",
 },
}

ok = (all(row_faces.values()) and all(v >= 1 for v in fam.values()) and boundary
      and w263_finalize_present
      and pf_now == fr['pf_sha16_post'] and pf_diff_empty and pf_crnorm_equal
      and n1_heal_state_ok and n1_crnorm_equal_healed and n1_preheal_crnorm_holds
      and len(shards) == 12 and sizes_ok
      and r_banned.returncode == 0 and r_pf.returncode == 0 and r_n1.returncode == 0
      and upstream_match and prev_total == 1002935 and prev_k == 576520)
out['verdict'] = 'ALL PASS' if ok else 'FAIL'
io.open('results/_r1076bmc_w264_sixgate.json', 'w', encoding='utf-8').write(
    json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps({"verdict": out['verdict'],
                  "row_faces": row_faces, "fam": fam, "boundary": boundary,
                  "shards": len(shards), "sizes_ok": sizes_ok,
                  "banned_rc": r_banned.returncode,
                  "pf_selftest_rc": r_pf.returncode,
                  "n1_selftest_rc": r_n1.returncode,
                  "n1_crnorm_equal": n1_crnorm_equal,
                  "pf_crnorm_equal": pf_crnorm_equal,
                  "pf_now_eq_receipt": pf_now == fr['pf_sha16_post'],
                  "n1_now_eq_receipt": n1_now == fr['n1_sha16_post'],
                  "ledger_pre": out['ledger_pre']}, indent=1))
raise SystemExit(0 if ok else 1)
