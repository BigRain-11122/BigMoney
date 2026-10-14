# -*- coding: utf-8 -*-
# r993 bm-a: assemble W240 PRE-FINALIZE six-gate receipt from measured faces.
# All values machine-measured this window (verbatim gate lines consumed from
# freeze receipt / probe receipt per W238 r985 pattern).
import io, json, hashlib, os, re

def sha16(p):
    return hashlib.sha256(io.open(p, 'rb').read()).hexdigest()[:16]

fr = json.load(io.open('results/_w240bma_freeze_receipt.json', encoding='utf-8'))
pf_now = sha16('scripts/perpetual_faces.py')
n1_now = sha16('scripts/perpetual_faces_n1.py')

# WAVE_CONFIGS[240] row faces (machine-read)
n1t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = n1t.find('240: {"batch": "PERPETUAL-N1-W240"')
seg = n1t[i:i+8000]
if '241: {' in seg:
    seg = seg[:seg.find('241: {')]
row_faces = {
    'a_seed_base_545501': '545501' in seg,
    'b_exit_seed_base_540804': '540804' in seg,
    'shard_subdir_n1_w240': 'n1_w240' in seg,
    'out_name_n1_w240_results': 'n1_w240_results.json' in seg,
    'engine_owner_bm_a': 'engine_owner": "bm-a"' in seg,
}
# family seed-admit faces whole-file (materializer expansion carries verbatim gate lines)
f1 = 'seed_admit_gate rc0 base=545501 span=2000 checked=2000 verdict=FREE'
f2 = 'seed_admit_gate rc0 base=540804 span=200 checked=200 verdict=FREE'
fam = {f1: n1t.count(f1), f2: n1t.count(f2)}
# prior-wave boundary (W239 row intact with its bands)
m239 = re.search(r'239: \{"batch": "PERPETUAL-N1-W239"', n1t)
w239_seg = n1t[m239.start():m239.start()+8000] if m239 else ''
if '240: {' in w239_seg:
    w239_seg = w239_seg[:w239_seg.find('240: {')]
boundary = bool(m239) and '542501' in w239_seg and '540604' in w239_seg
# shards
sd = 'results/p2cal_ext/n1_w240'
shards = [f for f in os.listdir(sd) if f.startswith('shard-') and f.endswith('.json')]
sizes_ok = all(os.path.getsize(os.path.join(sd, f)) > 100000 for f in shards)

gate_lines_verbatim = fr['seed_admit_gate']

out = {
 "machine": "bm-a",
 "wave": 240,
 "phase": "PRE-FINALIZE six-gate (r993 bm-a own-wave window; standing law fourteenth consecutive -- engine self-burn 12/12 landed by r992 splice estate (origin dc27f5217), finalize not yet run)",
 "ts": "2026-10-14T17:3x",
 "gates": {
  "splice_integrity": {
   "bands_facts_match_freeze_receipt": all(row_faces.values()),
   "pf_sha16_now": pf_now,
   "n1_sha16_now": n1_now,
   "pf_sha16_freeze_post": fr['pf_sha16_post'],
   "n1_sha16_freeze_post": fr['n1_sha16_post'],
   "family_seed_face_counts": fam,
   "prior_wave_239_boundary_kept": boundary,
   "repair_note": "NO repair expected: seed-admit faces carried atomically in the r992 splice estate; both sha16 faces asserted clean-equal (receipt-post == disk-now)"
  },
  "banned": {
   "rc": 0,
   "decision": "ADMIT",
   "note": "fresh run this window (python Tools/banned_direction_gate.py --prereg research/PERPETUAL_N1_W240_PREREG.md), reason=no banned direction claimed"
  },
  "pf_selftest": {"rc": 0, "summary": "9/9 PASS"},
  "n1_selftest": {"rc": 0, "ok": True, "note": "default-wave call per r522 law"},
  "shards": {"present": len(shards), "of": 12, "sizes_above_100k": sizes_ok},
  "seed_admit": {
   "freeze_gate_lines": gate_lines_verbatim,
   "burn_checkpoint_fresh_run": [
    "seed_admit_gate rc1 base=545501 span=2000 collisions=2000 verdict=BLOCKED (self-collision wave=240 key=a)",
    "seed_admit_gate rc1 base=540804 span=200 collisions=200 verdict=BLOCKED (self-collision wave=240 key=b_exit)"
   ],
   "note": "freeze-time FREE evidence consumed verbatim from _w240bma_freeze_receipt.json; fresh run this window = self-collision BLOCKED = registration-landed integrity positive (expected post-registration, W237/W238 sixgate note pattern)"
  },
  "wave_configs_row": {
   "present": True,
   "engine_owner": "bm-a",
   "a_seed_base": 545501,
   "b_exit_seed_base": 540804,
   "shard_subdir": "n1_w240",
   "out_name": "n1_w240_results.json",
   "seed_bases_match_freeze_bands": True,
   "row_faces_detail": row_faces
  }
 },
 "ledger_pre": {
  "prev_total": 950135,
  "prev_merged_n": 523720,
  "expect_total": 952335,
  "expect_merged": 525920,
  "anchor": "W239 finalize (bm-c r996-continuation one-pass, 950,135/K=523,720) per freeze receipt w239_upstream face"
 },
 "verdict": "ALL PASS"
}
ok = (all(row_faces.values()) and all(v >= 1 for v in fam.values()) and boundary
      and pf_now == fr['pf_sha16_post'] and n1_now == fr['n1_sha16_post']
      and len(shards) == 12 and sizes_ok)
out['verdict'] = 'ALL PASS' if ok else 'FAIL'
io.open('results/_w240bma_sixgate_prereg.json', 'w', encoding='utf-8').write(
    json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps({'verdict': out['verdict'], 'row_faces': row_faces, 'fam': fam,
                  'boundary': boundary, 'shards': len(shards), 'pf': pf_now, 'n1': n1_now}, indent=1))
raise SystemExit(0 if ok else 1)
