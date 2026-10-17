# -*- coding: utf-8 -*-
# r1039 bm-a: W263 PRE-FINALIZE six-gate receipt (standing law since W217 debt;
# clone lineage _r1068bmc_w262_sixgate.py W262 pattern, 25th consecutive
# PRE-FINALIZE correct-phase). Burn landed by resident engine auto-ignite
# post-W263 splice f499817fa (ledger appends 355c716b7-chain batched 12/12,
# shard files only; finalize not yet run).
# Splice commit f499817fa landed via clean-filter commit (worktree CRLF ->
# blob LF): raw-byte triple identity does NOT hold for this wave; gate-1
# asserts CR-NORMALIZED content identity worktree == landed blob (EOL
# representation delta only, zero content delta) -- disclosed honest.
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


fr = json.load(io.open('results/_w263bma_freeze_receipt.json', encoding='utf-8'))
pf_now = sha16('scripts/perpetual_faces.py')
n1_now = sha16('scripts/perpetual_faces_n1.py')

n1t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = n1t.find('263: {"batch": "PERPETUAL-N1-W263"')
assert i >= 0, 'W263 wave row missing'
seg = n1t[i:i + 9000]
if '264: {' in seg:
    seg = seg[:seg.find('264: {')]
row_faces = {
    'a_seed_base_593901': '593901' in seg,
    'b_exit_seed_base_595901': '595901' in seg,
    'shard_subdir_n1_w263': 'n1_w263' in seg,
    'out_name_n1_w263_results': 'n1_w263_results.json' in seg,
    'engine_owner_bm_a': 'engine_owner": "bm-a"' in seg,
}
f1 = 'base=593901 span=2000'
f2 = 'base=595901 span=200'
fam = {f1: n1t.count(f1), f2: n1t.count(f2)}
m262 = re.search(r'262: \{"batch": "PERPETUAL-N1-W262"', n1t)
w262_seg = n1t[m262.start():m262.start() + 8000] if m262 else ''
if '263: {' in w262_seg:
    w262_seg = w262_seg[:w262_seg.find('263: {')]
boundary = bool(m262) and '591701' in w262_seg and '593701' in w262_seg

sd = 'results/p2cal_ext/n1_w263'
shards = sorted(f for f in os.listdir(sd) if f.startswith('shard-') and f.endswith('.json'))
sizes_ok = all(os.path.getsize(os.path.join(sd, f)) > 100000 for f in shards)

r_banned = subprocess.run([sys.executable, 'Tools/banned_direction_gate.py',
                           '--prereg', 'research/PERPETUAL_N1_W263_PREREG.md'],
                          capture_output=True, text=True)
r_pf = subprocess.run([sys.executable, 'scripts/perpetual_faces.py', 'selftest'],
                      capture_output=True, text=True)
r_n1 = subprocess.run([sys.executable, 'scripts/perpetual_faces_n1.py', 'selftest'],
                      capture_output=True, text=True)
r_git = subprocess.run(['git', 'show', 'f499817fa:scripts/perpetual_faces_n1.py'],
                      capture_output=True)
n1_landed = hashlib.sha256(r_git.stdout).hexdigest()[:16]
wt_n1_bytes = io.open('scripts/perpetual_faces_n1.py', 'rb').read()
n1_crnorm_equal = crnorm(wt_n1_bytes) == crnorm(r_git.stdout)
r_git_pf = subprocess.run(['git', 'show', 'f499817fa:scripts/perpetual_faces.py'],
                          capture_output=True)
wt_pf_bytes = io.open('scripts/perpetual_faces.py', 'rb').read()
pf_crnorm_equal = crnorm(wt_pf_bytes) == crnorm(r_git_pf.stdout)
r_git_pf_diff = subprocess.run(['git', 'diff', 'f499817fa', '--',
                                'scripts/perpetual_faces.py'],
                               capture_output=True, text=True)
pf_diff_empty = (len((r_git_pf_diff.stdout or '').strip()) == 0
                and r_git_pf_diff.returncode == 0)

n1_vs_receipt_note = (
    'r1039 window disclosure: splice commit f499817fa was created through '
    'the clean-filter path (worktree CRLF -> committed blob LF) -- raw-byte '
    'triple identity does NOT hold for W263; gate-1 asserts CR-NORMALIZED '
    'content identity worktree == landed blob (zero content delta, EOL '
    'representation only). Freeze receipt n1/pf sha16_post hashed the CRLF '
    'worktree bytes at freeze time and those raw worktree hashes still '
    'match today (worktree untouched since splice). Engine self-burn '
    'ledger appends touch shard files only.'
)

# ledger_pre: machine-read from W262 finalize product (r587 never-transcribe)
w262 = json.load(io.open('results/perpetual_faces/n1_w262_results.json',
                         encoding='utf-8'))
ledger_face = None
for container in (w262.get('science_gates', {}) or {}):
    pass


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


ledger_w262 = _find_ledger(w262)
assert ledger_w262 is not None, 'W262 ledger face missing'
prev_total = ledger_w262['total']
prev_k = w262['null_pool_cumulative']['merged']['n_values']
expect_total = prev_total + 2200
expect_merged = prev_k + 2200
# cross-check vs freeze receipt upstream face
up = fr['w262_upstream']
upstream_match = (up['ledger_total'] == prev_total and up['merged_n'] == prev_k)

w262_finalize_present = os.path.exists('results/perpetual_faces/n1_w262_results.json')
out = {
 "machine": "bm-a",
 "wave": 263,
 "phase": "PRE-FINALIZE six-gate (r1039 bm-a own-seat window, 25th consecutive correct-phase; standing law -- engine self-burn 12/12 landed post-W263 splice f499817fa via batched ledger appends, finalize not yet run)",
 "gates": {
  "splice_integrity": {
   "bands_facts_match_freeze_receipt": all(row_faces.values()),
   "pf_sha16_now": pf_now, "n1_sha16_now": n1_now,
   "pf_sha16_freeze_post": fr['pf_sha16_post'],
   "n1_sha16_freeze_post": fr['n1_sha16_post'],
   "n1_sha16_landed_commit_lf_clean": n1_landed,
   "n1_crnorm_equal_worktree_vs_landed": n1_crnorm_equal,
   "pf_crnorm_equal_worktree_vs_landed": pf_crnorm_equal,
   "pf_landed_diff_empty": pf_diff_empty,
   "n1_vs_receipt_disclosure": n1_vs_receipt_note,
   "family_seed_faces": fam,
   "prior_wave_262_boundary_kept": boundary,
  },
  "banned": {"rc": r_banned.returncode, "stdout_tail": (r_banned.stdout or '').strip()[-200:]},
  "pf_selftest": {"rc": r_pf.returncode, "stdout_tail": (r_pf.stdout or '').strip()[-120:]},
  "n1_selftest": {"rc": r_n1.returncode, "stdout_tail": (r_n1.stdout or '').strip()[-120:]},
  "shards": {"present": len(shards), "of": 12, "sizes_above_100k": sizes_ok,
             "files": shards},
  "seed_admit": {
   "freeze_gate_lines": fr.get('seed_admit_gate'),
   "note": "freeze-time FREE evidence consumed verbatim from _w263bma_freeze_receipt.json (both bands); whole-file per-span family faces count-asserted",
  },
  "wave_configs_row": {
   "present": True, "engine_owner": "bm-a",
   "a_seed_base": 593901, "b_exit_seed_base": 595901,
   "shard_subdir": "n1_w263", "out_name": "n1_w263_results.json",
   "seed_bases_match_freeze_bands": fr['bands']['A'] == [593901, 595900] and fr['bands']['B'] == [595901, 596100],
   "row_faces_detail": row_faces,
  },
  "w262_finalize_product_present": w262_finalize_present,
 },
 "ledger_pre": {
  "prev_total": prev_total, "prev_merged_n": prev_k,
  "expect_total": expect_total, "expect_merged": expect_merged,
  "source": "W262 finalize actuals machine-read from n1_w262_results.json (r587 law)",
  "freeze_receipt_upstream_face_match": upstream_match,
  "anchor": "W262 finalize (bm-c r1068 one-pass 1,000,735/K=574,320) honored per freeze receipt w262_upstream face",
 },
}

ok = (all(row_faces.values()) and all(v >= 1 for v in fam.values()) and boundary
      and w262_finalize_present
      and pf_now == fr['pf_sha16_post'] and pf_diff_empty and pf_crnorm_equal
      and n1_now == fr['n1_sha16_post'] and n1_crnorm_equal
      and len(shards) == 12 and sizes_ok
      and r_banned.returncode == 0 and r_pf.returncode == 0 and r_n1.returncode == 0
      and upstream_match and prev_total == 1000735 and prev_k == 574320)
out['verdict'] = 'ALL PASS' if ok else 'FAIL'
io.open('results/_r1039bma_w263_sixgate.json', 'w', encoding='utf-8').write(
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
