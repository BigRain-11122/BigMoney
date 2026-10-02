# -*- coding: utf-8 -*-
import json, time, psutil

now_iso = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
epoch = int(time.time())

state = json.load(open('state.json', encoding='utf-8'))
state['note'] = ("r567 FULL CLOSE: W65 finalize one-pass LANDED (prev 505,348=W64 bm-a r568 0e21c860f same-window "
                 "unblock + 2,200 = 507,548 NET CHAIN HEAD, K=140,920==prereg projection bitwise, S5 4/4 PASS, "
                 "single-wave delta vs W64-only 0.022446 honest-disclosed as observation item; s7/s8 backfill + "
                 "selftest W2..W67 two-state PASS) + W66 same-window draft YIELDED zero-cost to bm-c r359 (FIX-A "
                 "live-fire first catch, r530 12th cross-validation) + W67 FREEZE delivered 551ced1b1 (A 177_004.."
                 "179_003 / B 50_201..50_400 both arithmetic no-skip, seat MSG-20261002-0945-bmb, burn 10/12 "
                 "self-continuing) + W68 frozen by bm-a r568 (938d8bb54 surgical, next free number=69) + S6 all-green "
                 "(dualrun streak 12/3, audit CLEAN burning-healthy, holiday no-ops) + rebase-conflict resolver "
                 "family lessons (whole-rewrite take-newer / jsonl line-union / rebase-reset product restore r543 "
                 "superset route); next = W67 12/12 burn watch -> W66 finalize = bm-c face (unblocked by W65 "
                 "landing) -> W67 finalize mine after W66 lands (chain W64->W65 landed->W66->W67, r538 one-pass)")
state['last_round_at'] = epoch
state['last_round_ts'] = now_iso
state['ts'] = now_iso
state['updated'] = "r567 bm-b FULL CLOSE: W65 finalize landed (head 507,548) + W67 freeze/burn 10/12; next W69 seat on never-dry"
state['updated_at'] = now_iso
json.dump(state, open('state.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

hb = json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))
hb['last_seen'] = now_iso
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = now_iso
hb['current_task'] = ("W67 burn 10/12 via engine tick (self-continuing, finalize after W66 bm-c lands); r567 full "
                      "close: W65 finalize landed head 507,548 + W67 freeze; next free seat W69 on never-dry")
hb['round_no'] = 567
hb['round_no_label'] = 'r567'
hb['cpu_util_pct'] = psutil.cpu_percent(interval=1)
hb['free_ram_gb'] = round(psutil.virtual_memory().available / (1024**3), 1)
hb['idle_ram_gb'] = hb['free_ram_gb']
hb['ram_free_gb'] = hb['free_ram_gb']
hb['verdict'] = 'loaded_ok'
json.dump(hb, open('fleet/machines/bm-b.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
chk = json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int (R170/R178)'

addendum = (
    f"{now_iso} | r567 addendum | W65 FINALIZE 落账实况补账：bm-a r568 同窗送 W64 finalize（0e21c860f·head 505,348）"
    "解封链序→本窗 W65 finalize one-pass 落地（+2,200=507,548 净链头·K=140,920==prereg 投影逐位·S5 4/4 PASS·单波面 "
    "delta vs W64-only 0.022446 诚实披露=观察项移交 W66-only 对照）→s7/s8 机械回填+selftest 两态全绿→push 送达 "
    "d15140148。同窗 W68=bm-a r568 冻结（938d8bb54 外科干净面）→下个自由号=69。下轮指针：W67 烧毕 12/12 watch→"
    "W66 finalize=bm-c 面（已解锁）→W67 finalize=本机（W66 落账后 one-pass）→W69 席位 never-dry。本地未达 origin "
    "commit 数=0。"
)
with open('logs/iteration-loop/round_reports.md', 'a', encoding='utf-8') as f:
    f.write(addendum + '\n')
print('final bookkeeping done:', now_iso)
