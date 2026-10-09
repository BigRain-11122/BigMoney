import json, time, datetime, psutil

# S7-1: state-bm-c.json round_no 819->820 + live fields
sp = 'state-bm-c.json'
st = json.load(open(sp, encoding='utf-8'))
now = datetime.datetime.now()
iso = now.isoformat(timespec='seconds') + '+08:00'
m = psutil.virtual_memory()
st['round_no'] = 820
st['round_no_label'] = 'r820'
st['last_round'] = 819
st['last_round_at'] = iso
st['last_round_ts'] = iso
st['clock_read'] = iso
st['ts'] = iso
st['updated'] = iso
st['updated_at'] = iso
st['last_seen'] = iso
st['last_seen_at'] = iso
st['heartbeat_epoch_utc'] = int(time.time())
st['ram_free_gb'] = round(m.available / 1e9, 2)
st['free_ram_gb'] = round(m.available / 1e9, 2)
st['idle_rounds'] = 0
st['agenda_starved'] = False
st['last_round_summary'] = 'r819: H3 768P T2V sample delivered to group outbound (gate 7.5/10, video-only) + W17 screen crash-loop root-caused (RAM gate) and unblocked via Ollama pause (0.4->7.1GB free, SHARD-0 ignited 20:50) + S6 full chain rc0'
st['latest_artifact'] = 'K:/Fluxgroup/FluxGroup/cph4/fleet/h3-local-test/outbound/local/bmc-local-768p-t2v-20261009.mp4'
st['next_milestone'] = 'W17 screen 8 shards burned + judge -> pool replenish SLA D-20261009-01(iii) 10-10 00:00 >=10 claimable; Ollama tasks re-enable after screen wave verified'
json.dump(st, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('state round_no ->', st['round_no'])

# S7-2: heartbeat fleet/machines/bm-c.json
hp = 'fleet/machines/bm-c.json'
hb = json.load(open(hp, encoding='utf-8'))
hb['last_seen'] = iso
hb['ts'] = iso
hb['clock_read'] = iso
hb['heartbeat_epoch_utc'] = int(time.time())
hb['verdict'] = 'ok'
hb['idle_rounds'] = 0
hb['agenda_starved'] = False
hb['current_task'] = ('当前活: W17 屏分片烧批在飞(SHARD-0 已点火·RAM 门解除)+Ollama 双任务暂停让路待屏波验收后恢复 | '
                      '最近实物: H3 本地 768P 测试片已交付集团出口 cph4/fleet/h3-local-test/outbound/local/bmc-local-768p-t2v-20261009.mp4(2026-10-09 20:4x·门检 7.5/10·纯画面无音轨·origin 送达自证) | '
                      '下个里程碑: W17 屏 8 分片烧讫+判决链点火·池补给 SLA 10-10 00:00 ≥10 可认领·Ollama 任务恢复(下轮验收后)')
json.dump(hb, open(hp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
ep = hb['heartbeat_epoch_utc']
assert isinstance(ep, int), 'epoch must be int'
print('heartbeat epoch int OK:', ep)

# S7-3: verify epoch type in state too
st2 = json.load(open(sp, encoding='utf-8'))
assert isinstance(st2['heartbeat_epoch_utc'], int)
print('state epoch int OK')
