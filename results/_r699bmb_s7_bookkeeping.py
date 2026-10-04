# r699 bm-b S7 bookkeeping: state.json + heartbeat + round report append (programmatic, r645 self-verify law)
import json, time, io

ROOT = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
now = time.time()
clock = time.strftime('%Y-%m-%dT%H:%M:%S+08:00', time.localtime(now))

# --- state.json ---
sp = ROOT + r'\state.json'
st = json.load(io.open(sp, encoding='utf-8'))
st['round_no'] = 699
st['note'] = ("r699: holiday maintenance round green across the board: S0 merge origin 2 (bm-c faces, zero intersect); "
              "D-19 orders key flipped (group orders.md new row O-20261004-2300 Xidudu re-acceptance order @Biggame, not involving this company -> watermark updated, zero action); "
              "S1 smoke 48/48; S6 38/38 rc0 (update_lhb min-interval guard re-verify PASS closes r698 pointer-e); "
              "N2-W15 screen 11/12 (my SHARD-2 ready RAM-gated daemon auto-ignite); trio NULLS V/Q/D burning to 10-06/07/08; "
              "W3 judge shards 4/4 done (bm-c finalize seat ETA ~10-05T02:00); CONTEST-RC done; post_review x0 zero red")
st['last_round_at'] = clock
st['ts'] = clock
st['updated'] = clock
st['last_seen'] = clock
st['round_no_label'] = 'round 699 (bm-b)'
st['clock_read'] = clock
st['last_orders_sha'] = '34BCD6B57975DA02E573AAF832F9E2B1255CAB2F'
st['next'] = ("(a) 10-05 morning round: W3 judge finalize landing watch (bm-c seat, ETA ~10-05T02:00, verify chain _r487bmc_w3_judge_verify.py); "
              "(b) N2 SHARD-2 (mine) RAM-gated -> daemon auto-ignite when trio V closes ~10-06T17; "
              "(c) after screen 12/12 + bm-a finalize: N2-W15 sec.9.1 concretize freeze window <=10-08, judge pool burn <=10-12; "
              "(d) MF IC reference batch (next_pick) still source-blocked on bm-a lane (30-min self-heal in flight); "
              "(e) 10-09 post-holiday data-chain check")
json.dump(st, io.open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
chk = json.load(io.open(sp, encoding='utf-8'))
assert chk['round_no'] == 699, 'state round_no verify failed'
print('state.json OK round_no=', chk['round_no'], 'orders_sha=', chk['last_orders_sha'][:12])

# --- heartbeat ---
hp = ROOT + r'\fleet\machines\bm-b.json'
hb = json.load(io.open(hp, encoding='utf-8'))
hb['last_seen'] = clock
hb['heartbeat_epoch_utc'] = int(now)
hb['clock_read'] = clock
hb['round_no'] = 699
hb['round_no_label'] = 'round 699 (bm-b)'
hb['current_task'] = ("r699 closed: holiday maintenance green (S6 38/38, smoke 48/48, D-19 orders key consumed O-20261004-2300 @Biggame zero-action, "
                      "LHB min-interval guard re-verify PASS); trio NULLS V/Q/D burning to 10-06T17/10-07T11/10-08T0x; "
                      "N2-W15 screen 11/12, my SHARD-2 ready RAM-gated daemon auto-ignite; W3 judge finalize bm-c seat ETA ~10-05T02:00")
hb['verdict'] = ("healthy burning (trio NULLS three-family in flight RAM-held + N2 SHARD-2 RAM-gated ready; "
                 "py_low_with_work_cands = legal RAM-gated window per r691 cap law; maintenance round per product law)")
for k in ('ts', 'updated', 'updated_at'):
    hb[k] = clock
json.dump(hb, io.open(hp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
chk2 = json.load(io.open(hp, encoding='utf-8'))
assert isinstance(chk2['heartbeat_epoch_utc'], int), 'epoch must be JSON int (R170/R178)'
assert chk2['round_no'] == 699
print('heartbeat OK epoch_int=', chk2['heartbeat_epoch_utc'], 'clock=', chk2['clock_read'])
