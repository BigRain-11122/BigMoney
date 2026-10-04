import json
import io
import time

# S7: state round_no 706 -> 707
sp = 'state-bm-a.json'
s = json.load(io.open(sp, encoding='utf-8'))
old = s.get('round_no', 0)
s['round_no'] = old + 1
s['last_round_ts'] = '2026-10-05T02:15:00+08:00'
with io.open(sp, 'w', encoding='utf-8', newline='') as f:
    json.dump(s, f, ensure_ascii=False, indent=1)
print('round_no:', old, '->', old + 1)

# heartbeat: epoch int + clock_read T-separated
hp = 'fleet/machines/bm-a.json'
h = json.load(io.open(hp, encoding='utf-8'))
h['last_seen'] = '2026-10-05T02:15:00+08:00'
h['current_task'] = 'r707: N2-W15 judge 12-shard crash-loop P0 fix (grammar-key) + shard-0 24/24 burned; S6 chain 38 gates all green'
h['cpu_cores'] = 32
h['free_ram_gb'] = 51.2
h['gpu_free_vram_gb'] = 7.4
h['verdict'] = 'ok'
epoch = int(time.time())
assert isinstance(epoch, int)
h['heartbeat_epoch_utc'] = epoch
h['clock_read'] = '2026-10-05T02:15:00+08:00'
# product-first three lines (P-07 sec.5)
h['now_active'] = 'N2-W15 judge burns resumed fleet-wide post fix (3/12 shards ckpt landed, fuse tombstones auto-clearing)'
h['latest_artifact'] = 'scripts/perpetual_faces_n2.py grammar-key fix (origin 0caf879c6, 02:07) + results/n2_w15/checkpoint/n2_w15_judge_shard_0of12.jsonl (24 judged cells, 02:00)'
h['next_milestone'] = '12/12 judge shards done -> judge-finalize -> W15 wave verdict into 千人题库 supply; ETA in-window tonight (burns ~2min/shard, fleet-parallel)'
with io.open(hp, 'w', encoding='utf-8', newline='') as f:
    json.dump(h, f, ensure_ascii=False, indent=1)
back = json.load(io.open(hp, encoding='utf-8'))
assert isinstance(back['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
print('heartbeat epoch:', back['heartbeat_epoch_utc'], 'int-ok')
print('orders_ack count:', len(h.get('orders_ack', [])))
