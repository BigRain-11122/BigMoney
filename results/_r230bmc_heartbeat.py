import io, json, time

d = json.load(io.open('fleet/machines/bm-c.json', encoding='utf-8'))
epoch = int(time.time())
clock = time.strftime('%Y-%m-%dT%H:%M:%S') + '+08:00'
assert isinstance(epoch, int)
d['last_seen'] = time.strftime('%Y-%m-%d %H:%M:%S')
d['heartbeat_epoch_utc'] = epoch
d['clock_read'] = clock
d['current_task'] = ("r230 closed: 17-UU rebase canon-resolve (r229 replayed, escape-branch mission fulfilled) + "
                      "5x HANDOVER r230 window (ledger 341,063->343,788) + S6 37/37 yield-closeout; next: W9-JUDGE "
                      "harvest watch (bm-b lane -> W10 adopter freeze window) + A158-TSGATE-P1 finalize watch + "
                      "10-01 month-first trio")
d['cpu_cores'] = 32
d['cpu_util_pct'] = 1.8
d['cpu_pct'] = 1.8
d['free_ram_gb'] = 12.0
d['idle_ram_gb'] = 12.0
d['ram_free_gb'] = 12.0
d['total_ram_gb'] = 25.7
d['gpu_free_vram_mb'] = 9865
d['gpu_free_vram_mib'] = 9865
d['gpu_vram_free_mb'] = 9865
d['verdict'] = ("py_low_board_clear legal idle (board 0 open, bandit 0, pool ready 2 both spoken-for: W9-JUDGE "
                "lane=bm-b + A158-TSGATE-P1 owned bm-a 17:20:09 in-flight; supply_floor 2<3 breach carries honestly "
                "-- W10-GENERATE gated on W9 verdict per funnel discipline, no fabricated ready)")
d['prod_lanes'] = ("BigMoney-compute-node: W9-SCREEN finalized 243 survivors (bm-b r434), W9-JUDGE ready lane=bm-b "
                   "awaiting bm-b claim | A158-TSGATE-P1 B2 supply response in-burn on bm-a (17:20:09, 157 factors x "
                   "314 gates) | W10 MOM candidate PARKED awaiting W9 verdict (adopt window opens on judged lands) | "
                   "09-29 bar sina 9-try zero-row source-lag (catch-up relay next rounds)")
d['round_no'] = 231
d['updated_at'] = clock
with io.open('fleet/machines/bm-c.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=1)

# self-verify epoch int + clock format per F7 law
d2 = json.load(io.open('fleet/machines/bm-c.json', encoding='utf-8'))
ep = d2.get('heartbeat_epoch_utc')
cr = d2.get('clock_read', '')
assert isinstance(ep, int) and not isinstance(ep, bool), f'epoch not int: {type(ep)}'
assert 'T' in cr and '+' in cr, f'clock_read bad: {cr}'
print('heartbeat OK epoch int', ep, 'clock', cr, 'round', d2['round_no'], 'orders_ack', len(d2['orders_ack']))
