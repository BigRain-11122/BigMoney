# r246 bm-c: INNOVATION-QUOTA-SLOT-4 pool flip (ready->done + shard open->done + result_ref)
# surgical line surgery per R32 paradigm; preserves original CRLF/LF and byte-identical rest of file
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
p = r'results\runnable_pool.json'
raw = open(p, 'rb').read().decode('utf-8')
sep = '\r\n' if '\r\n' in raw[:2000] else '\n'
t = raw

anchor_entry = 'Consumer_plan per prereg s0.",' + sep + '      "status": "ready",'
result_ref = ("results/innovation_quota/VOLREGIME-TIMING-P1.json (r246 bm-c flip per SLOT-1/SLOT-2 precedent; "
              "autofill relaunch 01:50:01 pid 37072 dead + receipt complete 01:50:57 + attrition line 01:50:57 entries-face): "
              "judged-negative ALL 3 cells -- SLOW100-V -0.208 / SLOW45-V -0.2734 / SLOW100-UPPER +0.1728 vs line 0.4394 "
              "(passive_term dominant = batch-own passive 0.3394+0.10; null_term 0.2748/0.2632/0.196); CI95 all straddle zero; "
              "DSR 0.0/0.0/2.8e-05; PBO 0.0 register_eligible band but G1 0/3 -> no G2 face, no T-34 intake; "
              "trade KPI UPPER best (47.58%/+23.1bp/1.481) still loses passive full-window (BH 0.3394/+5.20%); "
              "beat_24m 0.043/0.131/0.288 all <0.5; splits SLOW100-V 0.75 <0.80 unstable; "
              "zoo #96 volume_regime_bimodal first volume-native timing face judged-negative, family closed per law s5 + "
              "reopen note (non-HMA volume moments / intraday faces only); ledger +2003 -> 352,021 linear "
              "(prev 350,018, head w11_screen.json live-read); evidence_cutoff 2026-09-22; prereg s7/s8 backfill same commit")
new_entry = ('Consumer_plan per prereg s0.",' + sep + '      "status": "done",' + sep +
             '      "result_ref": ' + chr(34) + result_ref + chr(34) + ',')
assert t.count(anchor_entry) == 1, 'entry anchor not unique: %d' % t.count(anchor_entry)
t = t.replace(anchor_entry, new_entry)

anchor_shard = ('"key": "main",' + sep + '          "status": "open",' + sep +
                '          "checkpoint": "",' + sep +
                '          "note": "single-face judged batch (3 cells + nulls), default shard",')
new_shard = ('"key": "main",' + sep + '          "status": "done",' + sep +
             '          "checkpoint": "burn complete 01:50:57 (attrition line + trials_ledger landed)",' + sep +
             '          "note": "single-face judged batch (3 cells + nulls), default shard",')
assert t.count(anchor_shard) == 1, 'shard anchor not unique: %d' % t.count(anchor_shard)
t = t.replace(anchor_shard, new_shard)

open(p, 'wb').write(t.encode('utf-8'))
import json
d = json.loads(t)
e = [x for x in d['entries'] if x.get('id') == 'INNOVATION-QUOTA-SLOT-4'][0]
assert e['status'] == 'done' and e['shards'][0]['status'] == 'done' and e['result_ref']
ready_ids = [x['id'] for x in d['entries'] if x.get('status') == 'ready']
print('FLIP OK; line_sep=%r; remaining ready entries: %s' % (repr(sep), ready_ids))
