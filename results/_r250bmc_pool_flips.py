# r250 bm-c: INNOVATION-QUOTA-SLOT-5 + TRIAL-LABOR-W12-GENERATE pool flips (ready->done + result_ref)
# surgical line surgery per R32/r246 paradigm; preserves rest of file byte-identical
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
p = r'results\runnable_pool.json'
raw = open(p, 'rb').read().decode('utf-8')
sep = '\r\n' if '\r\n' in raw[:2000] else '\n'
t = raw

# --- SLOT-5: status flip (status line followed by entered_at = SLOT-5 key order) ---
a1 = ('      "priority": 3,' + sep +
      '      "status": "ready",' + sep +
      '      "entered_at": "2026-09-30 03:17:58",')
r5 = ("results/innovation_quota/ICU-MA-TIMING-P1.json (r250 bm-c flip per SLOT-1/2/4 precedent; autofill burn 03:21:43 pid 37476 "
      "+ verdict commit 3e77f145d + attrition row + trials_ledger landed): judged-negative ALL 3 cells -- ICU-N5 -0.2778 / "
      "ICU-N120 +0.3952 (best, channel-selection prior confirmed but below line) / ICU-N15 -0.2398 vs line 0.4598 "
      "(passive_term dominant = batch-own passive 0.3598+0.10; null_term 0.1944/0.2171/0.2087); CI95 all straddle zero; "
      "DSR 0.0/0.000661/0.0; PBO 0.0429 register_eligible band but G1 0/3 -> no G2 face, no T-34 intake; trade KPI N120 best "
      "(23.44%/+78.4bp/5.4995 payoff, 128 episodes) still loses line + beat_24m 0.444<0.5; splits N5 0.57 segment-unstable; "
      "zoo #86 icu_ma_timing first robust-regression endpoint timing face judged-negative, family closed per law s5 + reopen "
      "note (confirm-construct variants only, single-reading wipe warning realized); ledger +2003 -> 354,024 linear "
      "(prev 352,021; r249 commit msg said 354,021 = typo, canonical JSON face 354,024); evidence_cutoff 2026-09-22; "
      "48h CEO report clock start 2026-09-30 03:24 (due 2026-10-02 03:24); prereg s7/s8 backfill = r251 pointer")
n1 = ('      "priority": 3,' + sep +
      '      "status": "done",' + sep +
      '      "result_ref": ' + chr(34) + r5 + chr(34) + ',' + sep +
      '      "entered_at": "2026-09-30 03:17:58",')
assert t.count(a1) == 1, 'SLOT-5 status anchor not unique: %d' % t.count(a1)
t = t.replace(a1, n1)

# --- SLOT-5: shard flip ---
a2 = ('          "key": "main",' + sep +
      '          "status": "ready",' + sep +
      '          "checkpoint": "",' + sep +
      '          "note": "single-face judged batch (3 cells + 6000 null draws), default shard",')
n2 = ('          "key": "main",' + sep +
      '          "status": "done",' + sep +
      '          "checkpoint": "burn complete 03:21:43-03:22:2x (verdict + attrition + trials_ledger landed, commit 3e77f145d)",' + sep +
      '          "note": "single-face judged batch (3 cells + 6000 null draws), default shard",')
assert t.count(a2) == 1, 'SLOT-5 shard anchor not unique: %d' % t.count(a2)
t = t.replace(a2, n2)

# --- W12-GENERATE: status flip (status followed by "shards" = W12 key order) ---
a3 = ('      "status": "ready",' + sep +
      '      "shards": [')
r12 = ("results/trial_labor_w12/w12_candidates.json (r250 bm-c flip: autofill burn 03:25:01 pid 34160 -> consumed 03:35:28 "
       "per TRIAL_GRAMMAR_LEDGER W12 row; 5000 raw -> 859 dedup candidates verified in-file, grammar sha 67c86c9cf4ef1ca7, "
       "seeds gen=20320500 null=20321000 unc=20321500; W12 = bm-b T-124 lane, flip from bm-c = consumed-here bookkeeping + "
       "autofill relaunch churn stop; SCREEN/JUDGE legs = next pool items per prereg; same-grammar rerun FORBIDDEN sec.4)")
n3 = ('      "status": "done",' + sep +
      '      "result_ref": ' + chr(34) + r12 + chr(34) + ',' + sep +
      '      "shards": [')
assert t.count(a3) == 1, 'W12 status anchor not unique: %d' % t.count(a3)
t = t.replace(a3, n3)

# --- W12-GENERATE: shard flip ---
a4 = ('          "key": "main",' + sep +
      '          "status": "ready",' + sep +
      '          "checkpoint": "",' + sep +
      '          "note": "ladder default shard (single-face batch, r301 family)",')
n4 = ('          "key": "main",' + sep +
      '          "status": "done",' + sep +
      '          "checkpoint": "generate complete 03:35:28 (859 candidates serialized + ledger row + lane attrition)",' + sep +
      '          "note": "ladder default shard (single-face batch, r301 family)",')
assert t.count(a4) == 1, 'W12 shard anchor not unique: %d' % t.count(a4)
t = t.replace(a4, n4)

open(p, 'wb').write(t.encode('utf-8'))
import json
d = json.loads(t)
for eid in ('INNOVATION-QUOTA-SLOT-5', 'TRIAL-LABOR-W12-GENERATE'):
    e = [x for x in d['entries'] if x.get('id') == eid][0]
    assert e['status'] == 'done' and e['shards'][0]['status'] == 'done' and e['result_ref'], eid
ready_ids = [x['id'] for x in d['entries'] if x.get('status') == 'ready']
print('FLIPS OK; remaining ready entries: %s' % (ready_ids or 'NONE - pool drained'))
