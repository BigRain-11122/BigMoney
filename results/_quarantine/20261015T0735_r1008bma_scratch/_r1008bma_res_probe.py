import json, io
d = json.load(io.open(r'results\perpetual_faces\n1_w244_results.json', encoding='utf-8'))
out = io.open(r'results\_r1008bma_audit_face.txt', 'w', encoding='utf-8')
def w(s): out.write(s + '\n')
w('audit: ' + json.dumps(d.get('audit'), ensure_ascii=False, indent=1))
w('shards_consumed: ' + json.dumps(d.get('shards_consumed'), ensure_ascii=False)[:800])
w('universe: ' + json.dumps(d.get('universe'), ensure_ascii=False)[:400])
w('generated: ' + json.dumps(d.get('generated'), ensure_ascii=False))
led = [json.loads(l) for l in io.open(r'results\saturation_engine\ledger_bm-a.jsonl', encoding='utf-8').read().splitlines() if l.strip()]
w244 = [e for e in led if e.get('batch') == 'PERPETUAL-N1-W244' and 'done_at' in e]
w(f'w244 burn events: {len(w244)}')
for e in w244[:1] + w244[-1:]:
    w(f"  shard {e.get('shard')}: {e.get('started_at')} -> {e.get('done_at')}")
w(f"last shard index done: {max(e.get('shard', -1) for e in w244)}")
# ledger append face: last 2 lines raw keys
w('ledger last-2 events:')
for l in io.open(r'results\saturation_engine\ledger_bm-a.jsonl', encoding='utf-8').read().splitlines()[-2:]:
    o = json.loads(l)
    w('  ' + json.dumps(o, ensure_ascii=False)[:300])
out.close()
print('done')
