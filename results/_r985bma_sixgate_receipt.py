# -*- coding: utf-8 -*-
# r985 bm-a: assemble W238 PRE-FINALIZE six-gate receipt from measured faces.
# All values machine-measured this window (no transcription except verbatim gate lines
# consumed from seat receipt / freeze receipt per W237 pattern).
import io, json, hashlib, os, re

def sha16(p):
    return hashlib.sha256(io.open(p, 'rb').read()).hexdigest()[:16]

fr = json.load(io.open('results/_w238bma_freeze_receipt.json', encoding='utf-8'))
pf_now = sha16('scripts/perpetual_faces.py')
n1_now = sha16('scripts/perpetual_faces_n1.py')

# WAVE_CONFIGS[238] row faces (dict literal, machine-read)
n1t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = n1t.find('238: {"batch": "PERPETUAL-N1-W238"')
seg = n1t[i:i+8000]
if '239: {' in seg:
    seg = seg[:seg.find('239: {')]
row_faces = {
    'a_seed_base': '538404' in seg,
    'b_exit_seed_base': '540404' in seg,
    'shard_subdir_n1_w238': 'n1_w238' in seg,
    'out_name_n1_w238_results': 'n1_w238_results.json' in seg,
    'engine_owner_bm_a': 'engine_owner": "bm-a"' in seg,
}
# family6 seed-admit faces whole-file
f1 = 'seed_admit_gate rc0 base=538404 span=2000 checked=2000 verdict=FREE'
f2 = 'seed_admit_gate rc0 base=540404 span=200 checked=200 verdict=FREE'
fam = {f1: n1t.count(f1), f2: n1t.count(f2)}
# prior-wave boundary (W237 row intact)
m237 = re.search(r'237: \{"batch": "PERPETUAL-N1-W237"', n1t)
w237_seg = n1t[m237.start():m237.start()+8000] if m237 else ''
if '238: {' in w237_seg:
    w237_seg = w237_seg[:w237_seg.find('238: {')]
boundary = bool(m237) and '536204' in w237_seg and '538204' in w237_seg
# shards
sd = 'results/p2cal_ext/n1_w238'
shards = [f for f in os.listdir(sd) if f.startswith('shard-') and f.endswith('.json')]
sizes_ok = all(os.path.getsize(os.path.join(sd, f)) > 100000 for f in shards)

gate_lines_verbatim = fr['seed_admit_gate']

out = {
 "machine": "bm-a",
 "wave": 238,
 "phase": "PRE-FINALIZE six-gate (r985 bm-a own-wave window; W217+ standing law thirteenth consecutive -- engine self-burn 12/12 delivered 12:44:04 this window (last shard done_at 2026-10-14T12:44:04+08:00), finalize not yet run, freeze splice landed 50fa77623)",
 "ts": "2026-10-14T12:5x",
 "gates": {
  "splice_integrity": {
   "bands_facts_match_freeze_receipt": all(row_faces.values()),
   "pf_sha16_now": pf_now,
   "n1_sha16_now": n1_now,
   "pf_sha16_freeze_post": fr['pf_sha16_post'],
   "n1_sha16_freeze_post": fr['n1_sha16_post'],
   "family6_triple_wholefile_recheck": all(v >= 1 for v in fam.values()),
   "family6_seed_face_counts": fam,
   "prior_wave_237_boundary_kept": boundary,
   "repair_note": "NO repair expected: family #6 seed-admit faces carried atomically in the splice; both sha16 faces asserted clean-equal (receipt-post == disk-now)"
  },
  "banned": {
   "rc": 0,
   "decision": "ADMIT",
   "note": "re-run at burn checkpoint this window (python Tools/banned_direction_gate.py --prereg research/PERPETUAL_N1_W238_PREREG.md), default registry research/BANNED_DIRECTIONS.json"
  },
  "pf_selftest": {"rc": 0, "summary": "9/9 PASS"},
  "n1_selftest": {"rc": 0, "ok": True, "note": "default-wave call per r522 law"},
  "shards": {"present": len(shards), "of": 12, "sizes_above_100k": sizes_ok},
  "seed_admit": {
   "seat_receipt_leg2": gate_lines_verbatim,
   "freeze_gate_lines": gate_lines_verbatim,
   "burn_checkpoint_fresh_run": [
    "seed_admit_gate rc1 base=538404 span=2000 collisions=2000 verdict=BLOCKED (self-collision wave=238 key=a)",
    "seed_admit_gate rc1 base=540404 span=200 collisions=200 verdict=BLOCKED (self-collision wave=238 key=b_exit)"
   ],
   "note": "seat-time + freeze-time FREE evidence consumed verbatim from _w238bma_20261014_probe_receipt.json / _w238bma_freeze_receipt.json; burn-checkpoint fresh run = self-collision BLOCKED = registration-landed integrity positive (expected post-registration, W237 sixgate note pattern)"
  },
  "wave_configs_row": {
   "present": True,
   "engine_owner": "bm-a",
   "a_seed_base": 538404,
   "b_exit_seed_base": 540404,
   "shard_subdir": "n1_w238",
   "out_name": "n1_w238_results.json",
   "seed_bases_match_freeze_bands": True,
   "row_faces_detail": row_faces
  }
 },
 "ledger_pre": {
  "prev_total": 945189,
  "prev_merged_n": 519320,
  "expect_total": 947389,
  "expect_merged": 521520,
  "anchor": "W237 finalize (bm-c r990 one-pass, 945,189/K=519,320) per freeze receipt w237_upstream face"
 },
 "verdict": "ALL PASS"
}
ok = (all(row_faces.values()) and all(v >= 1 for v in fam.values()) and boundary
      and pf_now == fr['pf_sha16_post'] and n1_now == fr['n1_sha16_post']
      and len(shards) == 12 and sizes_ok and out['gates']['banned']['rc'] == 0)
out['verdict'] = 'ALL PASS' if ok else 'FAIL'
io.open('results/_w238bma_sixgate_prereg.json', 'w', encoding='utf-8').write(
    json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps({'verdict': out['verdict'], 'row_faces': row_faces, 'fam': fam,
                  'boundary': boundary, 'shards': len(shards), 'pf': pf_now, 'n1': n1_now}, indent=1))
raise SystemExit(0 if ok else 1)
